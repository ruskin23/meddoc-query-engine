from openai import OpenAI
import pinecone

from app.core.embedding import EmbeddingService
from app.core.prompting import PromptProcessor, PromptRunner
from app.core.retreival import PineconeRetriever

from app.hierarchical_rag.prompts import TEMPLATES
from app.hierarchical_rag.generator import PromptService
from app.hierarchical_rag.retreiver import HierarchicalRetriever

def get_prompt_service(openai_client, openai_model) -> PromptService:
    generator = PromptRunner(client=openai_client, model=openai_model)
    processor = PromptProcessor(generator=generator, templates=TEMPLATES)
    return PromptService(processor=processor)


def initialize_indices(question_index_name: str, chunk_index_name: str):
    question_index = pinecone.Index(question_index_name)
    chunk_index = pinecone.Index(chunk_index_name)
    return question_index, chunk_index


def initialize_services_and_retrievers(
    openai_client: OpenAI,
    openai_model: str,
    embedding_model: str,
    question_index,
    chunk_index
):
    embedding_service = EmbeddingService(model=embedding_model)

    question_retriever = PineconeRetriever(index=question_index, embedding_service=embedding_service)
    chunk_retriever = PineconeRetriever(index=chunk_index, embedding_service=embedding_service)

    prompt_service = get_prompt_service(openai_client, openai_model)

    return HierarchicalRetriever(
        prompt_service=prompt_service,
        question_retriever=question_retriever,
        chunk_retriever=chunk_retriever
    )


def retrieve_context(
    query: str,
    openai_client: OpenAI,
    openai_model: str,
    question_index_name: str,
    chunk_index_name: str,
    embedding_model: str
):
    question_index, chunk_index = initialize_indices(question_index_name, chunk_index_name)
    retriever = initialize_services_and_retrievers(
        openai_client, openai_model, embedding_model, question_index, chunk_index
    )
    return retriever.get_context_chunks(query)

