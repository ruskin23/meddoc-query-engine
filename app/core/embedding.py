from typing import List
from openai import OpenAI


class EmbeddingService:
    """Service for generating text embeddings using OpenAI's embedding models."""
    
    def __init__(self, model: str = "text-embedding-3-small", client: OpenAI = None) -> None:
        """Initialize the embedding service.
        
        Args:
            model: OpenAI embedding model name
            client: OpenAI client instance
        """
        self.model = model
        self.client = client or OpenAI()

    def embed(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors (each vector is a list of floats)
        """
        response = self.client.embeddings.create(
            input=texts,
            model=self.model
        )
        return [item.embedding for item in response.data]
