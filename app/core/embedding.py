from typing import List
import openai


class EmbeddingService:
    """Service for generating text embeddings using OpenAI's embedding models."""
    
    def __init__(self, model: str = "text-embedding-3-small") -> None:
        """Initialize the embedding service.
        
        Args:
            model: OpenAI embedding model name
        """
        self.model = model

    def embed(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors (each vector is a list of floats)
        """
        response = openai.Embedding.create(
            input=texts,
            model=self.model
        )
        return [item["embedding"] for item in response["data"]]
