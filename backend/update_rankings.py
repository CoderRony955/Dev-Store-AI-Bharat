"""
Update trending scores and category rankings for all resources.

This script should be run periodically (e.g., hourly or daily) to:
1. Calculate trending scores based on recent activity
2. Update category rankings based on final scores
3. Store results in the database

Usage:
    python update_rankings.py [--time-window DAYS]
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
import argparse

from clients.database import DatabaseClient
from services.ranking import RankingService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RankingUpdater:
    """Updates trending scores and category rankings for resources."""
    
    def __init__(self, db_client: DatabaseClient, ranking_service: RankingService):
        self.db = db_client
        self.ranking = ranking_service
    
    async def get_recent_activity(
        self,
        resource_id: str,
        time_window_days: int = 7
    ) -> Dict[str, int]:
        """
        Get recent activity metrics for a resource.
        
        Args:
            resource_id: Resource UUID
            time_window_days: Number of days to look back
            
        Returns:
            Dictionary with download, view, and bookmark counts
        """
        cutoff_date = datetime.utcnow() - timedelta(days=time_window_days)
        
        query = """
            SELECT 
                action,
                COUNT(*) as count
            FROM resource_usage
            WHERE resource_id = $1
                AND created_at >= $2
            GROUP BY action
        """
        
        rows = await self.db.fetch(query, resource_id, cutoff_date)
        
        activity = {
            'downloads': 0,
            'views': 0,
            'bookmarks': 0
        }
        
        for row in rows:
            action = row['action']
            count = row['count']
            if action == 'download_boilerplate':
                activity['downloads'] = count
            elif action == 'view':
                activity['views'] = count
            elif action == 'bookmark':
                activity['bookmarks'] = count
        
        return activity
    
    async def calculate_growth_rate(
        self,
        resource_id: str,
        time_window_days: int = 7
    ) -> float:
        """
        Calculate growth rate compared to previous period.
        
        Args:
            resource_id: Resource UUID
            time_window_days: Number of days for current period
            
        Returns:
            Growth rate as percentage (e.g., 50.0 for 50% growth)
        """
        current_start = datetime.utcnow() - timedelta(days=time_window_days)
        previous_start = datetime.utcnow() - timedelta(days=time_window_days * 2)
        previous_end = current_start
        
        # Get current period count
        current_query = """
            SELECT COUNT(*) as count
            FROM resource_usage
            WHERE resource_id = $1
                AND created_at >= $2
        """
        current_count = await self.db.fetchval(current_query, resource_id, current_start) or 0
        
        # Get previous period count
        previous_query = """
            SELECT COUNT(*) as count
            FROM resource_usage
            WHERE resource_id = $1
                AND created_at >= $2
                AND created_at < $3
        """
        previous_count = await self.db.fetchval(
            previous_query, resource_id, previous_start, previous_end
        ) or 0
        
        # Calculate growth rate
        if previous_count == 0:
            return 100.0 if current_count > 0 else 0.0
        
        growth_rate = ((current_count - previous_count) / previous_count) * 100.0
        return growth_rate
    
    async def update_trending_scores(self, time_window_days: int = 7):
        """
        Update trending scores for all resources.
        
        Args:
            time_window_days: Time window for recent activity
        """
        logger.info(f"Updating trending scores (time window: {time_window_days} days)")
        
        # Get all resources
        query = "SELECT id FROM resources"
        resources = await self.db.fetch(query)
        
        updated_count = 0
        for resource in resources:
            resource_id = resource['id']
            
            # Get recent activity
            activity = await self.get_recent_activity(resource_id, time_window_days)
            
            # Calculate growth rate
            growth_rate = await self.calculate_growth_rate(resource_id, time_window_days)
            
            # Compute trending score
            trending_score = self.ranking.compute_trending_score(
                recent_downloads=activity['downloads'],
                recent_views=activity['views'],
                recent_bookmarks=activity['bookmarks'],
                time_window_days=time_window_days,
                growth_rate=growth_rate
            )
            
            # Update database
            update_query = """
                UPDATE resources
                SET trending_score = $1,
                    updated_at = NOW()
                WHERE id = $2
            """
            await self.db.execute(update_query, trending_score, resource_id)
            updated_count += 1
            
            if updated_count % 100 == 0:
                logger.info(f"Updated {updated_count} resources...")
        
        logger.info(f"Trending scores updated for {updated_count} resources")
    
    async def update_category_rankings(self):
        """Update category rankings for all resources."""
        logger.info("Updating category rankings")
        
        # Get all resources with their scores
        query = """
            SELECT 
                id,
                type,
                COALESCE(
                    (SELECT final_score 
                     FROM resource_rankings 
                     WHERE resource_id = resources.id 
                     ORDER BY date DESC 
                     LIMIT 1),
                    0.0
                ) as final_score
            FROM resources
            ORDER BY type, final_score DESC
        """
        
        resources = await self.db.fetch(query)
        
        # Convert to list of dicts
        resource_list = [dict(r) for r in resources]
        
        # Compute rankings
        ranked_resources = self.ranking.compute_category_rankings(
            resource_list,
            score_field='final_score'
        )
        
        # Update database
        updated_count = 0
        for resource in ranked_resources:
            update_query = """
                UPDATE resources
                SET category_rank = $1,
                    updated_at = NOW()
                WHERE id = $2
            """
            await self.db.execute(
                update_query,
                resource['category_rank'],
                resource['id']
            )
            updated_count += 1
        
        logger.info(f"Category rankings updated for {updated_count} resources")
    
    async def run(self, time_window_days: int = 7):
        """
        Run the complete ranking update process.
        
        Args:
            time_window_days: Time window for trending calculations
        """
        try:
            await self.db.connect()
            
            # Update trending scores
            await self.update_trending_scores(time_window_days)
            
            # Update category rankings
            await self.update_category_rankings()
            
            logger.info("Ranking update completed successfully")
            
        except Exception as e:
            logger.error(f"Error updating rankings: {e}", exc_info=True)
            raise
        finally:
            await self.db.disconnect()


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Update trending scores and category rankings'
    )
    parser.add_argument(
        '--time-window',
        type=int,
        default=7,
        help='Time window in days for trending calculations (default: 7)'
    )
    
    args = parser.parse_args()
    
    # Initialize services
    db_client = DatabaseClient()
    ranking_service = RankingService()
    updater = RankingUpdater(db_client, ranking_service)
    
    # Run update
    await updater.run(time_window_days=args.time_window)


if __name__ == '__main__':
    asyncio.run(main())
