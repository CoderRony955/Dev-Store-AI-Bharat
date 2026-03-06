# Multi-Source Data Ingestion and AWS Integration - Code Audit

## Overview
Comprehensive code audit to assess the current system's readiness for multi-source data ingestion (GitHub, HuggingFace, Kaggle) and AWS integration (Bedrock, OpenSearch). This audit will identify gaps between current implementation and requirements for handling diverse JSON formats and semantic search capabilities.

## 1. User Stories

### 1.1 As a DevOps Engineer
I want to understand if the current database schema can store varying metadata structures from GitHub, HuggingFace, and Kaggle so that I can plan any necessary schema migrations.

### 1.2 As a Backend Developer
I want to know if the search service properly integrates with Amazon Bedrock for embeddings and OpenSearch for vector search so that I can implement semantic search features.

### 1.3 As a Frontend Developer
I want to verify that the UI correctly renders source-specific attributes (stars for GitHub, downloads for HuggingFace, usability_rating for Kaggle) so that users see relevant information for each resource type.

### 1.4 As a Product Manager
I want a clear gap analysis report identifying missing functions, parameters, and integrations so that I can prioritize development work.

## 2. Acceptance Criteria

### 2.1 Schema Validation Analysis
- **GIVEN** the current Resource model in `backend/models/domain.py`
- **WHEN** comparing against sample data from GitHub, HuggingFace, and Kaggle
- **THEN** the audit must identify:
  - Whether the `metadata` JSONB field can accommodate all source-specific fields
  - Missing fields in the Resource model (e.g., `language`, `forks`, `private`, `gated`, `usability_rating`)
  - Type mismatches between model and actual data

### 2.2 Intent Search Readiness Analysis
- **GIVEN** the SearchService in `backend/services/search.py`
- **WHEN** examining Bedrock and OpenSearch integration
- **THEN** the audit must verify:
  - Bedrock client properly generates embeddings using Titan
  - OpenSearch client supports KNN vector search
  - Search service orchestrates embedding generation → vector search → ranking
  - Intent extraction uses Bedrock for query understanding

### 2.3 Frontend Data Mapping Analysis
- **GIVEN** the DevStoreDashboard component in `frontend/components/DevStoreDashboard.jsx`
- **WHEN** checking resource rendering logic
- **THEN** the audit must confirm:
  - Component correctly maps `resource_type` or `category` to display icons
  - Source-specific metadata (GitHub stars, HF downloads, Kaggle usability) is rendered
  - Conditional rendering based on data source is implemented

### 2.4 Gap Analysis Report
- **GIVEN** all analysis findings
- **WHEN** compiling the final report
- **THEN** the report must include:
  - Executive summary of readiness status
  - Detailed findings for each area (schema, search, frontend)
  - Specific functions/parameters that need to be added
  - Code examples showing required changes
  - Priority recommendations (critical, high, medium, low)

## 3. Data Sources

### 3.1 GitHub Resources
Sample structure from `backend/github_resources.json`:
```json
{
  "name": "fastapi",
  "stars": 95949,
  "metadata": {
    "language": "Python",
    "forks": 8791,
    "watchers": 95949,
    "open_issues": 145,
    "created_at": "2018-12-08T08:21:47Z",
    "updated_at": "2026-03-06T15:21:51Z"
  }
}
```

### 3.2 HuggingFace Datasets
Sample structure from `backend/huggingface_datasets.json`:
```json
{
  "name": "KakologArchives",
  "downloads": 2005717,
  "stars": 23,
  "metadata": {
    "private": false,
    "gated": false,
    "created_at": "2023-05-12T13:31:56.000Z",
    "last_modified": "2026-03-06T15:56:37.000Z"
  }
}
```

### 3.3 Kaggle Datasets
Sample structure from `backend/kaggle_datasets.json`:
```json
{
  "name": "screen-time-sleep-and-stress-analysis-dataset",
  "metadata": {
    "ref": "amar5693/screen-time-sleep-and-stress-analysis-dataset",
    "usability_rating": 0,
    "last_updated": "None"
  }
}
```

## 4. Technical Constraints

### 4.1 Database
- PostgreSQL with JSONB support for metadata field
- Must maintain backward compatibility with existing data

### 4.2 AWS Services
- Amazon Bedrock (Titan Embeddings, Claude 3)
- OpenSearch with KNN plugin for vector search
- Must handle AWS service failures gracefully

### 4.3 Frontend
- Next.js with React components
- Must support dynamic rendering based on data source

## 5. Out of Scope
- Actual implementation of fixes (this is audit only)
- Performance testing or load testing
- Security audit
- Cost analysis of AWS services
- Migration scripts or data transformation logic

## 6. Success Metrics
- Complete gap analysis report delivered
- All three areas (schema, search, frontend) analyzed
- Specific, actionable recommendations provided
- Code examples included for each gap identified
- Priority levels assigned to each finding
