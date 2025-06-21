from openai import OpenAI
import pinecone
from typing import List

from app.core.embedding import EmbeddingService
from app.core.prompting import PromptProcessor, PromptRunner
from app.core.retreival import PineconeRetriever

from app.hierarchical_rag.pipelines.retreiver import RetrievalPipeline
from app.hierarchical_rag.modules.retreiver import (
    HierarchicalRetriever,
    PromptBasedExpander,
    PineconeRetrieverAdapter,
    ScoreReranker
)
from app.hierarchical_rag.modules.generator import PromptService
from app.hierarchical_rag.modules.prompts import TEMPLATES


def create_prompt_service(client: OpenAI, model: str) -> PromptService:
    runner = PromptRunner(client=client, model=model)
    processor = PromptProcessor(generator=runner, templates=TEMPLATES)
    return PromptService(processor)


def retreive(
    query: str,
    client: OpenAI,
    model: str,
    question_index_name: str,
    chunk_index_name: str,
    embedding_model_name: str,
    top_n: int = 15
) -> List[dict]:
    
    # Initialize Pinecone indexes
    question_index = pinecone.Index(question_index_name)
    chunk_index = pinecone.Index(chunk_index_name)

    # Embedding and prompt services
    embedding_service = EmbeddingService(model=embedding_model_name)
    prompt_service = create_prompt_service(client, model)

    # Create retrievers
    question_retriever = PineconeRetrieverAdapter(
        PineconeRetriever(index=question_index, embedding_service=embedding_service)
    )
    chunk_retriever = PineconeRetrieverAdapter(
        PineconeRetriever(index=chunk_index, embedding_service=embedding_service)
    )

    # Compose the hierarchical retriever
    retriever = HierarchicalRetriever(
        expander=PromptBasedExpander(prompt_service),
        question_retriever=question_retriever,
        chunk_retriever=chunk_retriever,
        reranker=ScoreReranker()
    )

    # Run the retrieval pipeline
    return RetrievalPipeline(retriever).run(query, top_n=top_n)
