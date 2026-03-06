# Quick Gap Analysis: Multi-Source Data Ingestion

## Status Summary

| Component | Status | Critical Issues |
|-----------|--------|-----------------|
| Schema | ⚠️ 60% | Missing `source` field |
| Search | ✅ 85% | Fully functional, minor tweaks |
| Frontend | ⚠️ 40% | No source differentiation |

## Critical Findings

### ✅ What Works
- Metadata JSONB field CAN store all GitHub/HuggingFace/Kaggle structures
- Bedrock (Titan + Claude) fully functional
- OpenSearch KNN search working
- Complete semantic search pipeline exists

### ❌ Critical Gaps (Must Fix)
1. **Missing `source` field** - Can't identify if resource is from GitHub/HF/Kaggle
2. **No source-specific UI** - All resources look the same regardless of origin
3. **Conflated metrics** - Stars and downloads mixed up

## Required Changes

### 1. Backend Schema (`backend/models/domain.py`)
```python
class Resource(BaseModel):
    # ADD THIS:
    source: str = Field(..., description="github | huggingface | kaggle")
    language: Optional[str] = None  # For GitHub
    private: Optional[bool] = None  # For HuggingFace
```

### 2. Frontend (`frontend/components/DevStoreDashboard.jsx`)
```javascript
// ADD THIS:
const SOURCE_META = {
  github: { icon: "🐙", color: "#333" },
  huggingface: { icon: "🤗", color: "#FFD21E" },
  kaggle: { icon: "📊", color: "#20BEFF" },
};

// FIX THIS:
function mapResource(r) {
  return {
    source: r.source || 'github',
    github_stars: r.github_stars || 0,  // Don't mix with downloads
    downloads: r.downloads || 0,         // Keep separate
  };
}
```

### 3. Database Migration
```sql
ALTER TABLE resources ADD COLUMN source VARCHAR(50) NOT NULL DEFAULT 'github';
ALTER TABLE resources ADD COLUMN language VARCHAR(100);
ALTER TABLE resources ADD COLUMN private BOOLEAN;
CREATE INDEX idx_resources_source ON resources(source);
```

## Implementation (4 hours)
1. Add `source` field to Resource model (1h)
2. Create database migration (1h)
3. Add source icons to frontend (1h)
4. Fix metrics conflation (1h)

## Verdict
**Metadata JSONB is equipped** ✅ - Can store all source-specific data
**Search is ready** ✅ - Bedrock + OpenSearch working
**Need schema + frontend fixes** ⚠️ - Add source field and UI differentiation
