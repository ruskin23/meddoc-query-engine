import logging
from typing import List, Dict, Any, Optional
from app.core import EmbeddingService


class PineconeRetriever:
    """Retriever for querying Pinecone vector database."""
    
    def __init__(self, index, embedding_service: EmbeddingService) -> None:
        """Initialize the Pinecone retriever.
        
        Args:
            index: Pinecone index instance
            embedding_service: Service for generating query embeddings
        """
        self.index = index
        self.embedder = embedding_service

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        filter: Optional[Dict[str, Any]] = None,
        namespace: str = "",
        include_metadata: bool = True
    ) -> List[Dict[str, Any]]:
        """Retrieve similar documents from Pinecone.
        
        Args:
            query: Search query text
            top_k: Number of top results to return
            filter: Optional metadata filter
            namespace: Pinecone namespace
            include_metadata: Whether to include metadata in results
            
        Returns:
            List of matching documents with scores and metadata
        """
        embedding = self.embedder.embed([query])[0]

        try:
            response = self.index.query(
                vector=embedding,
                top_k=top_k,
                filter=filter,
                namespace=namespace,
                include_metadata=include_metadata
            )

            return response.get("matches", [])
        except Exception as e:
            logging.error(f"Pinecone query failed: {e}")
            return []

