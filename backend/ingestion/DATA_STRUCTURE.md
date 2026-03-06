# Data Storage Structure

## Output Files

All files are saved to `backend/ingestion/output/`:

### 1. models.json
**Content**: All ML/LLM models (deduplicated)

**Sources**: 
- HuggingFace API (models only)
- OpenRouter API (models only)

**Deduplication Strategy**:
- Uses model name (lowercase) as unique key
- If duplicate found, keeps the one with higher downloads + stars
- Example: If same model exists in both HuggingFace and OpenRouter, keeps the more popular one

**Format**:
```json
[
  {
    "name": "bert-base-uncased",
    "description": "BERT base model",
    "source": "huggingface",
    "source_url": "https://huggingface.co/bert-base-uncased",
    "author": "google",
    "stars": 1234,
    "downloads": 5678900,
    "license": "apache-2.0",
    "tags": ["text-classification", "pytorch"],
    "category": "model",
    "metadata": {...}
  }
]
```

### 2. huggingface_datasets.json
**Content**: Datasets from HuggingFace only

**Source**: HuggingFace API (datasets only)

**Format**:
```json
[
  {
    "name": "squad",
    "description": "Stanford Question Answering Dataset",
    "source": "huggingface",
    "source_url": "https://huggingface.co/datasets/squad",
    "author": "stanford",
    "stars": 500,
    "downloads": 100000,
    "license": "cc-by-4.0",
    "tags": ["question-answering", "english"],
    "category": "dataset",
    "metadata": {...}
  }
]
```

### 3. kaggle_datasets.json
**Content**: Datasets from Kaggle only

**Source**: Kaggle API (datasets only)

**Format**:
```json
[
  {
    "name": "titanic",
    "description": "Titanic: Machine Learning from Disaster",
    "source": "kaggle",
    "source_url": "https://www.kaggle.com/datasets/owner/titanic",
    "author": "owner",
    "stars": 1000,
    "downloads": 50000,
    "license": "Various",
    "tags": ["kaggle", "dataset"],
    "category": "dataset",
    "metadata": {...}
  }
]
```

### 4. github_resources.json
**Content**: Repositories and tools from GitHub

**Source**: GitHub API

**Format**:
```json
[
  {
    "name": "transformers",
    "description": "State-of-the-art ML models",
    "source": "github",
    "source_url": "https://github.com/huggingface/transformers",
    "author": "huggingface",
    "stars": 100000,
    "downloads": 0,
    "license": "Apache-2.0",
    "tags": ["python", "machine-learning"],
    "category": "solution",
    "metadata": {...}
  }
]
```

## Data Flow

```
┌─────────────────┐
│  HuggingFace    │
│      API        │
└────────┬────────┘
         │
         ├─── Models ────────┐
         │                   │
         └─── Datasets ──────┼──> huggingface_datasets.json
                             │
┌─────────────────┐          │
│   OpenRouter    │          │
│      API        │          │
└────────┬────────┘          │
         │                   │
         └─── Models ────────┤
                             │
                             ├──> Deduplicate ──> models.json
                             
┌─────────────────┐
│     Kaggle      │
│      API        │
└────────┬────────┘
         │
         └─── Datasets ──────────> kaggle_datasets.json

┌─────────────────┐
│     GitHub      │
│      API        │
└────────┬────────┘
         │
         └─── Repositories ───────> github_resources.json
```

## Deduplication Logic

### Why Deduplicate?
Some models may exist in both HuggingFace and OpenRouter. We want to avoid duplicates in the final `models.json` file.

### How It Works
1. Collect all models from HuggingFace
2. Collect all models from OpenRouter
3. For each model:
   - Use lowercase model name as unique key
   - If name already exists, compare popularity (downloads + stars)
   - Keep the model with higher popularity score
4. Save deduplicated list to `models.json`

### Example
```python
# Before deduplication:
HuggingFace: "gpt2" (downloads: 1000000, stars: 500)
OpenRouter:  "gpt2" (downloads: 0, stars: 100)

# After deduplication:
models.json: "gpt2" from HuggingFace (higher score: 1000500 vs 100)
```

## File Sizes (Approximate)

| File | Typical Size | Number of Items |
|------|--------------|-----------------|
| models.json | 5-10 MB | 1000-1500 models |
| huggingface_datasets.json | 500 KB | 100 datasets |
| kaggle_datasets.json | 2-3 MB | 500 datasets |
| github_resources.json | 3-5 MB | 900 repositories |

## Usage in Backend

### Loading Models
```python
import json

with open('backend/ingestion/output/models.json', 'r') as f:
    models = json.load(f)

# All models are deduplicated
print(f"Total models: {len(models)}")
```

### Loading Datasets
```python
# HuggingFace datasets
with open('backend/ingestion/output/huggingface_datasets.json', 'r') as f:
    hf_datasets = json.load(f)

# Kaggle datasets
with open('backend/ingestion/output/kaggle_datasets.json', 'r') as f:
    kaggle_datasets = json.load(f)

# Combine if needed
all_datasets = hf_datasets + kaggle_datasets
```

### Loading GitHub Resources
```python
with open('backend/ingestion/output/github_resources.json', 'r') as f:
    repos = json.load(f)
```

## Benefits of This Structure

1. **No Duplicates**: Models are deduplicated automatically
2. **Clear Separation**: Datasets from different sources are in separate files
3. **Easy to Use**: Simple JSON format, easy to load and process
4. **Flexible**: Can combine or use separately as needed
5. **Traceable**: Each item has `source` field to track origin

## Next Steps

1. Load JSON files into your database
2. Generate embeddings for search
3. Index in OpenSearch/Elasticsearch
4. Cache frequently accessed data in Redis
5. Expose via REST API

---

**All data is clean, deduplicated, and ready to use!**
