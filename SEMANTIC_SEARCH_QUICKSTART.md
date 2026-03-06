# Semantic Search Quick Start

## 🚀 Get Started in 3 Steps

### Step 1: Setup OpenSearch Index
```bash
cd backend
python setup_opensearch_index.py
```

This creates a k-NN enabled index with 1024-dimensional vectors for Titan v2 embeddings.

### Step 2: Test the API
```bash
# Intent search (semantic)
curl -X POST http://localhost:8000/api/v1/search/intent \
  -H "Content-Type: application/json" \
  -d '{
    "query": "I need a free model for understanding Hindi-English mixed text",
    "limit": 5
  }'
```

### Step 3: Use in Frontend
```typescript
// In your React component
const results = await apiService.intentSearch(
  "best payment gateway for India",
  { limit: 5 }
);
```

## 🎯 Key Differences

### Keyword Search (`/api/v1/search`)
- Traditional text matching
- Fast (~50-100ms)
- Good for exact matches
- Example: "GPT-4 API"

### Intent Search (`/api/v1/search/intent`)
- Semantic understanding
- Slower (~300-500ms)
- Better for natural language
- Example: "I need something like ChatGPT but cheaper"

## 🔧 Configuration

### Environment Variables
```bash
AWS_REGION=us-east-1
OPENSEARCH_HOST=your-endpoint.region.es.amazonaws.com
OPENSEARCH_PORT=443
OPENSEARCH_USE_SSL=true
```

### Ranking Weights (Optional)
Edit `backend/services/ranking.py`:
```python
weights = {
    'semantic': 0.40,      # Cosine similarity
    'popularity': 0.30,    # Stars, downloads
    'optimization': 0.20,  # Latency, cost
    'freshness': 0.10      # Last updated
}
```

## 📊 Example Queries

### Natural Language
```json
{
  "query": "What's the best free model for text generation in Hindi?",
  "limit": 5
}
```

### Technical
```json
{
  "query": "low latency image classification API with GPU support",
  "limit": 5
}
```

### Conversational
```json
{
  "query": "I'm building a chatbot for customer support, what should I use?",
  "limit": 5
}
```

## 🎨 Frontend Integration

### Add Search Mode Toggle
```jsx
const [searchMode, setSearchMode] = useState('keyword');

const handleSearch = async (query) => {
  if (searchMode === 'intent') {
    return await apiService.intentSearch(query, { limit: 5 });
  } else {
    return await apiService.search(query, { limit: 20 });
  }
};

// Toggle button
<button onClick={() => setSearchMode(m => m === 'keyword' ? 'intent' : 'keyword')}>
  {searchMode === 'keyword' ? '🔍 Keyword' : '🧠 AI Intent'}
</button>
```

## 🐛 Troubleshooting

### "Index not found"
```bash
python setup_opensearch_index.py
```

### "Bedrock access denied"
Check AWS credentials have `bedrock:InvokeModel` permission.

### Slow performance
- Reduce `k` parameter in k-NN search
- Lower `ef_search` in index settings
- Enable embedding caching

### Poor results
- Verify resources are indexed with embeddings
- Check ranking weights
- Review query formulation

## 📈 Monitoring

### Health Check
```bash
curl http://localhost:8000/api/v1/health
```

### Check Logs
```bash
tail -f backend/logs/app.log | grep "Intent search"
```

## 🎓 Learn More

- Full setup guide: `backend/SEMANTIC_SEARCH_SETUP.md`
- Implementation details: `SEMANTIC_SEARCH_IMPLEMENTATION.md`
- API documentation: `backend/README.md`

## 💡 Tips

1. **Use intent search for**:
   - Natural language queries
   - Exploratory searches
   - When exact keywords unknown

2. **Use keyword search for**:
   - Specific resource names
   - Fast lookups
   - Exact matches

3. **Combine both**:
   - Start with intent search
   - Refine with keyword filters
   - Best of both worlds!
