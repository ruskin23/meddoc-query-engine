import uuid
from typing import List, Dict, Any

from app.core.embedding import EmbeddingService

class PineconeIndexer:
    def __init__(self, index, embedding_service: EmbeddingService):
        self.index = index
        self.embedder = embedding_service

    def chunked(self, iterable, size: int):
        for i in range(0, len(iterable), size):
            yield iterable[i:i + size]

    def index_to_pinecone(
        self,
        documents: List[Dict[str, Any]],
        text_key: str,
        metadata_keys: List[str],
        batch_size: int = 100,
        include_text_in_metadata: bool = True
    ):
        for batch in self.chunked(documents, batch_size):
            texts = [doc[text_key] for doc in batch]
            embeddings = self.embedder.embed(texts)

            pinecone_batch = []
            for doc, emb in zip(batch, embeddings):
                metadata = {k: doc.get(k) for k in metadata_keys if k in doc}
                if include_text_in_metadata:
                    metadata[text_key] = doc[text_key]

                pinecone_batch.append({
                    "id": str(uuid.uuid4()),
                    "values": emb,
                    "metadata": metadata
                })

            print(f"Upserting batch of {len(pinecone_batch)} vectors...")
            self.index.upsert(vectors=pinecone_batch)

