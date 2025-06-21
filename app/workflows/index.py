import pinecone
from typing import List

from app.core import EmbeddingService, PineconeIndexer
from app.hierarchical_rag import HierarchicalIndexing, HierarchicalIndexer, IndexingPipeline
from app.db import Database


def create_embedding_service(model: str) -> EmbeddingService:
    return EmbeddingService(model=model)


def create_pinecone_indexer(client: pinecone.Pinecone, index_name: str, embed_service: EmbeddingService, text_key: str, metadata_keys: List[str]) -> PineconeIndexer:
    index = client.Index(index_name)
    return PineconeIndexer(index=index, embedding_service=embed_service, text_key=text_key, metadata_keys=metadata_keys)


def create_indexing_pipeline(
    db: Database,
    question_index_name: str,
    chunk_index_name: str,
    embedding_model: str
) -> IndexingPipeline:
    
    client = pinecone.Pinecone()
    embed_service = create_embedding_service(embedding_model)

    question_indexer = create_pinecone_indexer(client, question_index_name, embed_service, "question", ["tags", "page_id", "pdf_id"])
    chunk_indexer = create_pinecone_indexer(client, chunk_index_name, embed_service, "chunk", ["tags", "page_id", "pdf_id"])

    index_strategy = HierarchicalIndexing(question_indexer, chunk_indexer)
    hierarchical_indexer = HierarchicalIndexer(index_strategy=index_strategy, db=db)

    return IndexingPipeline(indexer=hierarchical_indexer)


def index(
    db: Database,
    question_index_name: str,
    chunk_index_name: str,
    embedding_model: str
):
    pipeline = create_indexing_pipeline(
        db=db,
        question_index_name=question_index_name,
        chunk_index_name=chunk_index_name,
        embedding_model=embedding_model
    )
    pipeline.run()
