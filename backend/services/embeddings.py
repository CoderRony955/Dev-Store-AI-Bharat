"""
Embeddings service for DevStore

Provides embedding generation using Amazon Bedrock Titan models.
"""
import logging
from typing import List, Optional, Dict, Any
from functools import lru_cache

logger = logging.getLogger(__name__)


class EmbeddingsService:
    """
    Service for generating embeddings using Amazon Bedrock Titan models.
    
    Supports:
    - Titan Embed Text v1 (1536 dimensions)
    - Titan Embed Text v2 (1024 dimensions) - Default
    - Caching for performance
    """
    
    def __init__(
        self,
        model_version: str = "v2",
        bedrock_client=None
    ):
        """
        Initialize embeddings service.
        
        Args:
            model_version: "v1" (1536-dim) or "v2" (1024-dim, default)
            bedrock_client: Optional BedrockClient instance (auto-created if None)
        """
        self.model_version = model_version
        
        # Set model ID and dimensions based on version
        if model_version == "v1":
            self.model_id = "amazon.titan-embed-text-v1"
            self.dimensions = 1536
        elif model_version == "v2":
            self.model_id = "amazon.titan-embed-text-v2:0"
            self.dimensions = 1024
        else:
            raise ValueError(f"Invalid model_version: {model_version}. Use 'v1' or 'v2'")
        
        # Initialize Bedrock client
        if bedrock_client is None:
            from clients.bedrock import BedrockClient
            self._bedrock = BedrockClient(embedding_model_id=self.model_id)
        else:
            self._bedrock = bedrock_client
        
        logger.info(f"EmbeddingsService initialized (model={self.model_id}, dimensions={self.dimensions})")
    
    def get_embedding(self, text: str) -> List[float]:
        """
        Generate embedding vector for text using Bedrock Titan.
        
        Args:
            text: Input text to embed (max 8192 tokens for v2)
            
        Returns:
            Embedding vector as list of floats
            
        Raises:
            ValueError: If text is empty
            BedrockClientError: If embedding generation fails
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")
        
        # Truncate if too long (rough estimate: 1 token ≈ 4 chars)
        max_chars = 8192 * 4  # ~32k chars for v2
        if len(text) > max_chars:
            logger.warning(f"Text truncated from {len(text)} to {max_chars} chars")
            text = text[:max_chars]
        
        try:
            embedding = self._bedrock.generate_embedding(text)
            
            # Validate dimensions
            if len(embedding) != self.dimensions:
                logger.warning(
                    f"Unexpected embedding dimensions: got {len(embedding)}, expected {self.dimensions}"
                )
            
            return embedding
            
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            raise
    
    def get_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of input texts
            
        Returns:
            List of embedding vectors
            
        Note: Currently processes sequentially. For production, consider
            using async/parallel processing or Bedrock batch APIs.
        """
        embeddings = []
        
        for i, text in enumerate(texts):
            try:
                embedding = self.get_embedding(text)
                embeddings.append(embedding)
            except Exception as e:
                logger.error(f"Failed to generate embedding for text {i}: {e}")
                # Return zero vector as fallback
                embeddings.append([0.0] * self.dimensions)
        
        return embeddings
    
    def get_resource_embedding(self, resource: Dict[str, Any]) -> List[float]:
        """
        Generate embedding for a resource by combining its fields.
        
        Args:
            resource: Resource dictionary with name, description, tags, etc.
            
        Returns:
            Embedding vector for the resource
        """
        # Combine relevant fields for embedding
        parts = []
        
        if resource.get('name'):
            parts.append(f"Name: {resource['name']}")
        
        if resource.get('description'):
            parts.append(f"Description: {resource['description']}")
        
        if resource.get('tags'):
            tags = resource['tags']
            if isinstance(tags, list):
                parts.append(f"Tags: {', '.join(tags)}")
            else:
                parts.append(f"Tags: {tags}")
        
        if resource.get('resource_type'):
            parts.append(f"Type: {resource['resource_type']}")
        
        # Combine into single text
        combined_text = " | ".join(parts)
        
        return self.get_embedding(combined_text)
    
    @property
    def embedding_dimensions(self) -> int:
        """Get the embedding dimensions for this model."""
        return self.dimensions
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on embeddings service.
        
        Returns:
            Health check results
        """
        try:
            # Test with simple text
            test_embedding = self.get_embedding("health check test")
            
            return {
                "status": "healthy",
                "model_id": self.model_id,
                "dimensions": len(test_embedding),
                "expected_dimensions": self.dimensions
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "model_id": self.model_id,
                "error": str(e)
            }


# Cached instance for reuse
_embeddings_service: Optional[EmbeddingsService] = None


def get_embeddings_service(model_version: str = "v2") -> EmbeddingsService:
    """
    Get or create embeddings service instance.
    
    Args:
        model_version: "v1" or "v2" (default)
        
    Returns:
        EmbeddingsService instance
    """
    global _embeddings_service
    
    if _embeddings_service is None or _embeddings_service.model_version != model_version:
        _embeddings_service = EmbeddingsService(model_version=model_version)
    
    return _embeddings_service
