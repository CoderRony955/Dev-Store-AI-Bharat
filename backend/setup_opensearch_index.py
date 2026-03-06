"""
Setup script for OpenSearch k-NN index

This script creates the OpenSearch index with k-NN vector search support
for semantic search using Bedrock Titan v2 embeddings (1024 dimensions).

Usage:
    python setup_opensearch_index.py
"""
import logging
from clients.opensearch import OpenSearchClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Create OpenSearch index with k-NN support"""
    try:
        logger.info("Initializing OpenSearch client...")
        client = OpenSearchClient()
        
        # Check if index already exists
        index_name = client.index_name
        if client.index_exists(index_name):
            logger.warning(f"Index '{index_name}' already exists")
            response = input(f"Delete and recreate index '{index_name}'? (yes/no): ")
            if response.lower() == 'yes':
                logger.info(f"Deleting existing index '{index_name}'...")
                client.delete_index(index_name)
            else:
                logger.info("Keeping existing index. Exiting.")
                return
        
        # Create k-NN index
        logger.info(f"Creating k-NN index '{index_name}' with 1024-dimensional vectors...")
        success = client.create_knn_index(
            index_name=index_name,
            vector_dimension=1024,
            vector_field="embedding"
        )
        
        if success:
            logger.info(f"✅ Index '{index_name}' created successfully!")
            logger.info("Index configuration:")
            logger.info("  - Vector field: 'embedding'")
            logger.info("  - Dimensions: 1024 (Titan v2)")
            logger.info("  - Algorithm: HNSW")
            logger.info("  - Space type: L2")
        else:
            logger.error(f"❌ Failed to create index '{index_name}'")
    
    except Exception as e:
        logger.error(f"❌ Error setting up OpenSearch index: {e}", exc_info=True)
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
