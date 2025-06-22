import uuid
import logging
from typing import List, Dict, Any, Iterator, Optional

from app.core.embedding import EmbeddingService


class PineconeIndexer:
    """Indexer for Pinecone vector database."""
    
    def __init__(self, index, embedding_service: EmbeddingService, text_key: str, metadata_keys: List[str]) -> None:
        """Initialize the Pinecone indexer.
        
        Args:
            index: Pinecone index instance
            embedding_service: Service for generating embeddings
            text_key: Key in document dict containing the text to embed
            metadata_keys: Keys to include as metadata
        """
        self.index = index
        self.embedding_service = embedding_service
        self.text_key = text_key
        self.metadata_keys = metadata_keys
        
    def chunked(self, iterable: List[Any], size: int) -> Iterator[List[Any]]:
        """Split iterable into chunks of specified size."""
        for i in range(0, len(iterable), size):
            yield iterable[i:i + size]

    def index_documents(
        self,
        documents: List[Dict[str, Any]],
        batch_size: int = 100
    ) -> None:
        """Index documents in batches to Pinecone.
        
        Args:
            documents: List of document dictionaries to index
            batch_size: Number of documents to process in each batch
        """
        for batch in self.chunked(documents, batch_size):
            texts = [doc[self.text_key] for doc in batch]
            embeddings = self.embedding_service.embed(texts)

            pinecone_batch = []
            for doc, emb in zip(batch, embeddings):
                metadata = {k: doc.get(k) for k in self.metadata_keys if k in doc}
                metadata[self.text_key] = doc[self.text_key]

                pinecone_batch.append({
                    "id": str(uuid.uuid4()),
                    "values": emb,
                    "metadata": metadata
                })

            self.index.upsert(vectors=pinecone_batch)


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