import uuid
from typing import List, Dict, Any

from app.core.embedding import EmbeddingService
from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseIndexer(ABC):
    @abstractmethod
    def index_documents(self, documents: List[Dict[str, Any]]) -> None:
        pass

class PineconeIndexer(BaseIndexer):
    def __init__(self, index, embedding_service: EmbeddingService, text_key: str, metadata_keys: List[str]):
        self.index = index
        self.embedding_service = embedding_service
        self.text_key = text_key
        self.metadata_keys = metadata_keys
        
    def chunked(self, iterable, size: int):
        for i in range(0, len(iterable), size):
            yield iterable[i:i + size]

    def index_documents(
        self,
        documents: List[Dict[str, Any]],
        batch_size: int = 100
    ):
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

