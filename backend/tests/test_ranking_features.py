"""
Tests for ranking features: trending scores and category rankings
"""
import pytest
from datetime import datetime, timedelta
from services.ranking import RankingService


class TestTrendingScore:
    """Test trending score calculation"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.ranking = RankingService()
    
    def test_trending_score_basic(self):
        """Test basic trending score calculation"""
        score = self.ranking.compute_trending_score(
            recent_downloads=100,
            recent_views=500,
            recent_bookmarks=50,
            time_window_days=7,
            growth_rate=50.0
        )
        
        assert 0.0 <= score <= 1.0
        assert score > 0.0  # Should have positive score with activity
    
    def test_trending_score_no_activity(self):
        """Test trending score with no activity"""
        score = self.ranking.compute_trending_score(
            recent_downloads=0,
            recent_views=0,
            recent_bookmarks=0,
            time_window_days=7,
            growth_rate=0.0
        )
        
        assert score >= 0.0
        assert score < 0.5  # Should be low with no activity
    
    def test_trending_score_high_activity(self):
        """Test trending score with high activity"""
        score = self.ranking.compute_trending_score(
            recent_downloads=1000,
            recent_views=10000,
            recent_bookmarks=500,
            time_window_days=7,
            growth_rate=200.0
        )
        
        assert 0.0 <= score <= 1.0
        assert score > 0.7  # Should be high with lots of activity
    
    def test_trending_score_negative_growth(self):
        """Test trending score with negative growth"""
        score = self.ranking.compute_trending_score(
            recent_downloads=50,
            recent_views=200,
            recent_bookmarks=20,
            time_window_days=7,
            growth_rate=-30.0
        )
        
        assert 0.0 <= score <= 1.0
        # Should still have some score from absolute activity
    
    def test_trending_score_weights(self):
        """Test that downloads are weighted more than views"""
        score_high_downloads = self.ranking.compute_trending_score(
            recent_downloads=500,
            recent_views=100,
            recent_bookmarks=10,
            growth_rate=0.0
        )
        
        score_high_views = self.ranking.compute_trending_score(
            recent_downloads=100,
            recent_views=500,
            recent_bookmarks=10,
            growth_rate=0.0
        )
        
        # Downloads weighted 40%, views 30%, so downloads should score higher
        assert score_high_downloads > score_high_views


class TestCategoryRankings:
    """Test category ranking calculation"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.ranking = RankingService()
    
    def test_category_rankings_basic(self):
        """Test basic category ranking"""
        resources = [
            {'id': '1', 'type': 'api', 'final_score': 0.9},
            {'id': '2', 'type': 'api', 'final_score': 0.7},
            {'id': '3', 'type': 'model', 'final_score': 0.8},
            {'id': '4', 'type': 'model', 'final_score': 0.6},
        ]
        
        ranked = self.ranking.compute_category_rankings(resources)
        
        # Check all resources have ranks
        assert all('category_rank' in r for r in ranked)
        
        # Check API rankings
        api_resources = [r for r in ranked if r['type'] == 'api']
        assert api_resources[0]['category_rank'] == 1  # Highest score
        assert api_resources[1]['category_rank'] == 2
        
        # Check Model rankings
        model_resources = [r for r in ranked if r['type'] == 'model']
        assert model_resources[0]['category_rank'] == 1
        assert model_resources[1]['category_rank'] == 2
    
    def test_category_rankings_single_category(self):
        """Test ranking with single category"""
        resources = [
            {'id': '1', 'type': 'api', 'final_score': 0.5},
            {'id': '2', 'type': 'api', 'final_score': 0.8},
            {'id': '3', 'type': 'api', 'final_score': 0.3},
        ]
        
        ranked = self.ranking.compute_category_rankings(resources)
        
        # Sort by rank to verify order
        ranked_sorted = sorted(ranked, key=lambda r: r['category_rank'])
        
        assert ranked_sorted[0]['final_score'] == 0.8  # Rank 1
        assert ranked_sorted[1]['final_score'] == 0.5  # Rank 2
        assert ranked_sorted[2]['final_score'] == 0.3  # Rank 3
    
    def test_category_rankings_empty(self):
        """Test ranking with empty list"""
        resources = []
        ranked = self.ranking.compute_category_rankings(resources)
        assert ranked == []
    
    def test_category_rankings_custom_field(self):
        """Test ranking with custom score field"""
        resources = [
            {'id': '1', 'type': 'api', 'trending_score': 0.9},
            {'id': '2', 'type': 'api', 'trending_score': 0.7},
        ]
        
        ranked = self.ranking.compute_category_rankings(
            resources,
            score_field='trending_score'
        )
        
        ranked_sorted = sorted(ranked, key=lambda r: r['category_rank'])
        assert ranked_sorted[0]['trending_score'] == 0.9
        assert ranked_sorted[1]['trending_score'] == 0.7
    
    def test_category_rankings_tie_scores(self):
        """Test ranking with tied scores"""
        resources = [
            {'id': '1', 'type': 'api', 'final_score': 0.8},
            {'id': '2', 'type': 'api', 'final_score': 0.8},
            {'id': '3', 'type': 'api', 'final_score': 0.7},
        ]
        
        ranked = self.ranking.compute_category_rankings(resources)
        
        # Both tied resources should get sequential ranks
        ranks = [r['category_rank'] for r in ranked]
        assert sorted(ranks) == [1, 2, 3]


class TestRankingIntegration:
    """Integration tests for ranking features"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.ranking = RankingService()
    
    def test_full_ranking_pipeline(self):
        """Test complete ranking pipeline"""
        # Simulate resources with activity
        resources = [
            {
                'id': '1',
                'type': 'api',
                'github_stars': 5000,
                'downloads': 10000,
                'active_users': 500,
                'final_score': 0.0
            },
            {
                'id': '2',
                'type': 'api',
                'github_stars': 1000,
                'downloads': 2000,
                'active_users': 100,
                'final_score': 0.0
            },
        ]
        
        # Calculate popularity scores
        for resource in resources:
            popularity = self.ranking.compute_popularity(
                github_stars=resource['github_stars'],
                downloads=resource['downloads'],
                users=resource['active_users']
            )
            
            # Use popularity as final score for this test
            resource['final_score'] = popularity
        
        # Rank by category
        ranked = self.ranking.compute_category_rankings(resources)
        
        # Verify ranking
        ranked_sorted = sorted(ranked, key=lambda r: r['category_rank'])
        assert ranked_sorted[0]['github_stars'] == 5000  # Higher stars = rank 1
        assert ranked_sorted[1]['github_stars'] == 1000  # Lower stars = rank 2
    
    def test_trending_vs_popularity(self):
        """Test that trending and popularity are different metrics"""
        # Old popular resource
        popularity_old = self.ranking.compute_popularity(
            github_stars=10000,
            downloads=50000,
            users=1000
        )
        
        trending_old = self.ranking.compute_trending_score(
            recent_downloads=10,
            recent_views=50,
            recent_bookmarks=5,
            growth_rate=-20.0
        )
        
        # New trending resource
        popularity_new = self.ranking.compute_popularity(
            github_stars=100,
            downloads=500,
            users=50
        )
        
        trending_new = self.ranking.compute_trending_score(
            recent_downloads=200,
            recent_views=1000,
            recent_bookmarks=100,
            growth_rate=300.0
        )
        
        # Old resource should have higher popularity
        assert popularity_old > popularity_new
        
        # New resource should have higher trending score
        assert trending_new > trending_old


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
