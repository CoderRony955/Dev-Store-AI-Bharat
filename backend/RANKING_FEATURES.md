# Ranking and Trending Features

This document describes the ranking and trending features implemented for the Dev-Store platform.

## Overview

Three key metrics have been added to track resource performance and popularity:

1. **boilerplate_download_count** - Tracks successful boilerplate code downloads
2. **trending_score** - Calculated score for trending resources based on recent activity
3. **category_rank** - Position within resource type (e.g., #1 in Models)

## Database Schema

### New Fields in `resources` Table

```sql
-- Track boilerplate downloads separately from general downloads
boilerplate_download_count INTEGER DEFAULT 0

-- Trending score based on recent activity (0-1 scale)
trending_score FLOAT DEFAULT 0.0

-- Rank position within category (1 = top ranked)
category_rank INTEGER DEFAULT NULL
```

### New Fields in `resource_rankings` Table

Historical tracking of trending scores and category ranks:

```sql
trending_score FLOAT DEFAULT 0.0
category_rank INTEGER DEFAULT NULL
```

## Features

### 1. Boilerplate Download Tracking

Automatically tracks when users download boilerplate code for resources.

**Implementation:**
- Increments `boilerplate_download_count` in the `resources` table
- Logs download action in `resource_usage` table with metadata
- Tracks language and configuration options

**Location:** `backend/routers/boilerplate.py`

**Usage:**
```python
POST /boilerplate/generate
{
    "resource_ids": ["uuid1", "uuid2"],
    "language": "python",
    "include_tests": true
}
```

### 2. Trending Score Calculation

Calculates a trending score based on recent activity and growth velocity.

**Algorithm:**
- Recent downloads: 40%
- Recent views: 30%
- Recent bookmarks: 20%
- Growth rate: 10%

**Features:**
- Uses logarithmic scaling for better distribution
- Compares current period to previous period for growth
- Normalized to 0-1 scale
- Configurable time window (default: 7 days)

**Implementation:** `backend/services/ranking.py`

**Method:**
```python
def compute_trending_score(
    recent_downloads: int,
    recent_views: int,
    recent_bookmarks: int,
    time_window_days: int = 7,
    growth_rate: float = 0.0
) -> float
```

### 3. Category Rankings

Ranks resources within their category (API, Model, Dataset) based on final scores.

**Features:**
- Separate rankings for each resource type
- Based on final composite score
- Rank 1 = highest scoring resource in category
- Automatically updated when scores change

**Implementation:** `backend/services/ranking.py`

**Method:**
```python
def compute_category_rankings(
    resources: List[Dict[str, Any]],
    score_field: str = 'final_score'
) -> List[Dict[str, Any]]
```

## Automated Updates

### Update Script

Run `update_rankings.py` to recalculate all trending scores and category rankings.

**Usage:**
```bash
# Update with default 7-day window
python update_rankings.py

# Update with custom time window
python update_rankings.py --time-window 14
```

**What it does:**
1. Fetches recent activity from `resource_usage` table
2. Calculates growth rates by comparing periods
3. Computes trending scores for all resources
4. Updates category rankings based on final scores
5. Stores results in database

**Recommended Schedule:**
- Trending scores: Update hourly or daily
- Category rankings: Update daily

### Automation Options

**Option 1: Cron Job (Linux/Mac)**
```bash
# Add to crontab (runs daily at 2 AM)
0 2 * * * cd /path/to/backend && python update_rankings.py
```

**Option 2: Windows Task Scheduler**
- Create scheduled task to run `update_rankings.py` daily

**Option 3: AWS Lambda**
- Deploy as Lambda function
- Trigger with CloudWatch Events (EventBridge)
- Run on schedule (e.g., every hour)

**Option 4: Background Worker**
- Use Celery or similar task queue
- Schedule periodic tasks
- Better for high-frequency updates

## API Integration

### Querying Trending Resources

```python
# Get top trending resources
query = """
    SELECT * FROM resources
    WHERE trending_score > 0.5
    ORDER BY trending_score DESC
    LIMIT 10
"""
```

### Querying by Category Rank

```python
# Get top 5 models
query = """
    SELECT * FROM resources
    WHERE type = 'model'
    ORDER BY category_rank ASC
    LIMIT 5
"""
```

### Combined Queries

```python
# Get trending APIs ranked by category
query = """
    SELECT 
        id,
        name,
        trending_score,
        category_rank
    FROM resources
    WHERE type = 'api'
        AND trending_score > 0.3
    ORDER BY category_rank ASC
    LIMIT 20
"""
```

## Domain Model Updates

The `Resource` model in `backend/models/domain.py` now includes:

```python
class Resource(BaseModel):
    # ... existing fields ...
    boilerplate_download_count: Optional[int] = Field(None, ge=0)
    trending_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    category_rank: Optional[int] = Field(None, ge=1)
```

## Performance Considerations

### Indexes

The following indexes optimize query performance:

```sql
-- Trending queries
CREATE INDEX idx_resources_trending ON resources(trending_score DESC);

-- Category ranking queries
CREATE INDEX idx_resources_category_rank ON resources(type, category_rank);

-- Boilerplate download queries
CREATE INDEX idx_resources_boilerplate_downloads ON resources(boilerplate_download_count DESC);
```

### Caching

Consider caching:
- Top trending resources (TTL: 1 hour)
- Category rankings (TTL: 24 hours)
- Resource details with ranks (TTL: 1 hour)

## Monitoring

### Key Metrics to Track

1. **Trending Score Distribution**
   - How many resources have trending_score > 0.5?
   - Average trending score across all resources

2. **Download Patterns**
   - Boilerplate downloads per day
   - Most downloaded resources

3. **Category Balance**
   - Distribution of resources across categories
   - Top resources in each category

### Logging

The ranking service logs:
- Trending score calculations
- Category ranking updates
- Download tracking events
- Errors and warnings

Check logs at: `backend/logs/ranking.log`

## Future Enhancements

1. **Personalized Trending**
   - User-specific trending based on preferences
   - Tech stack-based trending

2. **Time-based Rankings**
   - Weekly/monthly trending charts
   - Historical rank tracking

3. **Advanced Metrics**
   - Engagement rate (views to downloads)
   - Retention rate (repeat usage)
   - Community sentiment

4. **Real-time Updates**
   - WebSocket notifications for rank changes
   - Live trending dashboard

## Troubleshooting

### Trending Scores Not Updating

1. Check if `update_rankings.py` is running
2. Verify database connectivity
3. Check for errors in logs
4. Ensure `resource_usage` table has data

### Category Ranks Missing

1. Verify resources have `final_score` in `resource_rankings`
2. Run `update_rankings.py` manually
3. Check for NULL values in scores

### Download Count Not Incrementing

1. Verify boilerplate endpoint is being called
2. Check database permissions
3. Review error logs in boilerplate router

## Migration

To apply the new schema changes:

```bash
# Run the migration
python run_migrations.py

# Or manually apply
psql -d devstore -f migrations/008_add_trending_and_ranking_fields.sql
```

## Testing

Test the new features:

```bash
# Run ranking tests
pytest tests/test_ranking.py -v

# Test boilerplate tracking
pytest tests/test_boilerplate.py -v
```

## References

- Database Schema: `DATABASE_SCHEMA.md`
- Ranking Algorithm: `backend/services/ranking.py`
- Domain Models: `backend/models/domain.py`
- Migration: `backend/migrations/008_add_trending_and_ranking_fields.sql`
