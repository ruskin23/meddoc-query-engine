from openai import OpenAI

from app.core import PromptProcessor, PromptRunner, ChunkService
from app.db import Database
from app.hierarchical_rag import (
    PromptService,
    TEMPLATES,
    QuestionGenerationTask,
    TagGenerationTask,
    ChunkGenerationTask,
    GenerationPipeline,
)


def create_prompt_service(client: OpenAI, model: str) -> PromptService:
    """Create a prompt service for content generation.
    
    Args:
        client: OpenAI client instance
        model: Model name to use for generation
        
    Returns:
        Configured prompt service
    """
    runner = PromptRunner(client=client, model=model)
    processor = PromptProcessor(generator=runner, templates=TEMPLATES)
    return PromptService(processor)


def create_generation_tasks(prompt_service: PromptService, chunk_service: ChunkService) -> list:
    """Create a list of generation tasks for processing PDF pages.
    
    Args:
        prompt_service: Service for prompt-based generation
        chunk_service: Service for text chunking
        
    Returns:
        List of generation tasks
    """
    return [
        QuestionGenerationTask(prompt_service),
        TagGenerationTask(prompt_service),
        ChunkGenerationTask(chunk_service)
    ]


def generate(db: Database, client: OpenAI, model: str) -> None:
    """Generate questions, tags, and chunks for all extracted PDF files.
    
    Args:
        db: Database connection
        client: OpenAI client instance
        model: Model name to use for generation
    """
    prompt_service = create_prompt_service(client, model)
    chunk_service = ChunkService()
    tasks = create_generation_tasks(prompt_service, chunk_service)
    pipeline = GenerationPipeline(db=db, tasks=tasks)
    pipeline.run()
