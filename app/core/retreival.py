import logging
from typing import List, Dict, Any
from app.core.embedding import EmbeddingService

class PineconeRetriever:
    def __init__(self, index, embedding_service: EmbeddingService):
        self.index = index
        self.embedder = embedding_service

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        filter: Dict[str, Any] = None,
        namespace: str = "",
        include_metadata: bool = True
    ) -> List[Dict[str, Any]]:
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

