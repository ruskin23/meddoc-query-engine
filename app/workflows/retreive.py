from openai import OpenAI
import pinecone
from typing import List, Dict, Any

from app.core import EmbeddingService, PromptProcessor, PromptRunner, PineconeRetriever

from app.hierarchical_rag import (
    RetrievalPipeline,
    HierarchicalRetriever,
    PromptBasedExpander,
    PineconeRetrieverAdapter,
    ScoreReranker,
    PromptService,
    TEMPLATES,
)


def create_prompt_service(client: OpenAI, model: str) -> PromptService:
    """Create a prompt service for query expansion.
    
    Args:
        client: OpenAI client instance
        model: Model name to use for generation
        
    Returns:
        Configured prompt service
    """
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
) -> List[Dict[str, Any]]:
    """Retrieve relevant context chunks for a query using hierarchical retrieval.
    
    Args:
        query: User query to search for
        client: OpenAI client instance
        model: Model name for query expansion
        question_index_name: Name of the question index
        chunk_index_name: Name of the chunk index
        embedding_model_name: Model name for embeddings
        top_n: Number of top results to return
        
    Returns:
        List of relevant context chunks with metadata
    """
    # Initialize Pinecone indexes
    question_index = pinecone.Index(question_index_name)
    chunk_index = pinecone.Index(chunk_index_name)

    # Create embedding and prompt services
    embedding_service = EmbeddingService(model=embedding_model_name)
    prompt_service = create_prompt_service(client, model)

    # Create retrievers with adapters
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
