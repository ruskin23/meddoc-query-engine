import uuid
from typing import List, Dict, Any, Iterator

from app.core import EmbeddingService
from abc import ABC, abstractmethod


class BaseIndexer(ABC):
    """Abstract base class for document indexing."""
    
    @abstractmethod
    def index_documents(self, documents: List[Dict[str, Any]]) -> None:
        """Index a list of documents.
        
        Args:
            documents: List of document dictionaries to index
        """
        pass


class PineconeIndexer(BaseIndexer):
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

            print(f"Upserting batch of {len(pinecone_batch)} vectors...")
            self.index.upsert(vectors=pinecone_batch)

