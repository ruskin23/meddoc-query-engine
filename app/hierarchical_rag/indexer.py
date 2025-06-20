from app.core.indexing import PineconeIndexer

from typing import List, Dict, Any

class IndexDocuments:
    def __init__(self, question_indexer: PineconeIndexer, chunk_indexer: PineconeIndexer):
        self.question_indexer = question_indexer
        self.chunk_indexer = chunk_indexer

    def index_questions(self, documents: List[Dict[str, Any]], batch_size: int = 100):
        self.question_indexer.index_to_pinecone(
            documents,
            text_key="question",
            metadata_keys=["tags", "page_id", "pdf_id"],
            batch_size=batch_size
        )

    def index_chunks(self, documents: List[Dict[str, Any]], batch_size: int = 100):
        self.chunk_indexer.index_to_pinecone(
            documents,
            text_key="chunk",
            metadata_keys=["page_id", "pdf_id"],
            batch_size=batch_size
        )
