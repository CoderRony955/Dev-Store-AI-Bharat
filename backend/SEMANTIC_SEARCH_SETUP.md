# Semantic Search Setup Guide

This guide explains how to set up and use the Bedrock-powered semantic search feature in DevStore.

## Overview

DevStore uses AWS Bedrock Titan v2 embeddings (1024 dimensions) combined with OpenSearch k-NN vector search to provide intelligent, intent-based search capabilities.

## Architecture

```
User Query → Bedrock Titan v2 → Embedding (1024-dim) → OpenSearch k-NN → Ranked Results
```

### Components

1. **Embeddings Service** (`backend/services/embeddings.py`)
   - Generates embeddings using Bedrock Titan v2
   - Supports both v1 (1536-dim) and v2 (1024-dim) models
   - Includes caching and batch processing

2. **OpenSearch Client** (`backend/clients/opensearch.py`)
   - Manages OpenSearch connection
   - Creates k-NN indexes with HNSW algorithm
   - Performs vector similarity search

3. **Search Router** (`backend/routers/search.py`)
   - `/api/v1/search` - Keyword search with intent extraction
   - `/api/v1/search/intent` - Pure semantic search using embeddings

4. **Ranking Service** (`backend/services/ranking.py`)
   - Unified ranking algorithm combining:
     - Semantic relevance (cosine similarity)
     - Popularity (stars, downloads)
     - Optimization (latency, cost, docs quality)
     - Freshness (last updated, health status)

## Setup Instructions

### 1. Prerequisites

Ensure you have:
- AWS credentials configured with Bedrock access
- OpenSearch cluster running and accessible
- Environment variables set in `.env`:
  ```
  AWS_REGION=us-east-1
  OPENSEARCH_HOST=your-opensearch-endpoint
  OPENSEARCH_PORT=443
  OPENSEARCH_USE_SSL=true
  DATABASE_URL=postgresql://...
  ```

### 2. Create OpenSearch k-NN Index

Run the setup script to create the index with proper k-NN configuration:

```bash
cd backend
python setup_opensearch_index.py
```

This creates an index with:
- Vector field: `embedding` (1024 dimensions)
- Algorithm: HNSW (Hierarchical Navigable Small World)
- Space type: L2 (Euclidean distance)
- Additional fields: name, description, resource_type, pricing_type, etc.

### 3. Index Your Resources

To enable semantic search, you need to generate embeddings for your resources and index them in OpenSearch.

Example script:

```python
from services.embeddings import get_embeddings_service
from clients.opensearch import OpenSearchClient
from clients.database import DatabaseClient

# Initialize services
embeddings_service = get_embeddings_service(model_version="v2")
opensearch_client = OpenSearchClient()
db_client = DatabaseClient()

# Get resources from database
resources = db_client.get_all_resources()

# Generate embeddings and index
for resource in resources:
    # Generate embedding
    embedding = embeddings_service.get_resource_embedding({
        'name': resource.name,
        'description': resource.description,
        'tags': resource.tags,
        'resource_type': resource.resource_type
    })
    
    # Index document with embedding
    document = {
        'name': resource.name,
        'description': resource.description,
        'resource_type': resource.resource_type,
        'pricing_type': resource.pricing_type,
        'source': resource.source,
        'github_stars': resource.github_stars,
        'downloads': resource.downloads,
        'last_updated': resource.last_updated.isoformat(),
        'health_status': resource.health_status,
        'embedding': embedding
    }
    
    opensearch_client.index_document(
        document=document,
        doc_id=str(resource.id),
        refresh=True
    )

print(f"Indexed {len(resources)} resources with embeddings")
```

### 4. Test the API

#### Keyword Search (with intent extraction)
```bash
curl -X POST http://localhost:8000/api/v1/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "best free NLP model for text generation",
    "limit": 20
  }'
```

#### Intent Search (pure semantic)
```bash
curl -X POST http://localhost:8000/api/v1/search/intent \
  -H "Content-Type: application/json" \
  -d '{
    "query": "I need a model that can understand Hindi and English mixed text",
    "limit": 5
  }'
```

## Frontend Integration

The frontend can toggle between search modes:

```typescript
// Keyword search
const results = await apiService.search(query, filters);

// Intent search (semantic)
const results = await apiService.intentSearch(query, filters);
```

To add a UI toggle in the frontend:

```jsx
const [searchMode, setSearchMode] = useState('keyword'); // 'keyword' | 'intent'

// In search handler
const handleSearch = async (query) => {
  if (searchMode === 'intent') {
    return await apiService.intentSearch(query);
  } else {
    return await apiService.search(query);
  }
};

// Toggle button
<button onClick={() => setSearchMode(mode => mode === 'keyword' ? 'intent' : 'keyword')}>
  {searchMode === 'keyword' ? '🔍 Keyword' : '🧠 AI Intent'}
</button>
```

## Performance Considerations

### Embedding Generation
- Titan v2 latency: ~100-200ms per request
- Use caching for repeated queries
- Consider batch processing for bulk indexing

### k-NN Search
- HNSW provides O(log n) search complexity
- Adjust `ef_search` parameter for speed/accuracy tradeoff
- Current setting: `ef_search=100` (good balance)

### Ranking
- Unified ranking combines 4 signals
- Weights can be adjusted in `RankingService`
- Current weights:
  - Semantic: 40%
  - Popularity: 30%
  - Optimization: 20%
  - Freshness: 10%

## Monitoring

Check service health:

```bash
# Embeddings service
curl http://localhost:8000/api/v1/health

# OpenSearch
curl http://localhost:8000/api/v1/opensearch/health
```

## Troubleshooting

### "Index not found" error
Run `python setup_opensearch_index.py` to create the index.

### "Bedrock access denied" error
Ensure your AWS credentials have `bedrock:InvokeModel` permission.

### Slow search performance
- Check OpenSearch cluster resources
- Reduce `k` parameter in k-NN search
- Lower `ef_search` value for faster (less accurate) results

### Poor search quality
- Verify embeddings are being generated correctly
- Check if resources are properly indexed with embeddings
- Adjust ranking weights in `RankingService`

## Next Steps

1. Implement incremental indexing (index new resources automatically)
2. Add search analytics and feedback loop
3. Fine-tune ranking weights based on user behavior
4. Implement query expansion and synonym handling
5. Add multi-language support for embeddings
