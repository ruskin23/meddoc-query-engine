from openai import OpenAI

from app.core.prompting import PromptProcessor, PromptRunner
from app.db.base import Database
from app.hierarchical_rag.modules.generator import PromptService
from app.hierarchical_rag.modules.prompts import TEMPLATES

from app.hierarchical_rag.modules.generator import (
    QuestionGenerationTask,
    TagGenerationTask,
    ChunkGenerationTask
)

from app.hierarchical_rag.pipelines.generator import GenerationPipeline

def create_prompt_service(client: OpenAI, model: str) -> PromptService:
    runner = PromptRunner(client=client, model=model)
    processor = PromptProcessor(generator=runner, templates=TEMPLATES)
    return PromptService(processor)

def create_generation_tasks(prompt_service: PromptService):
    return [
        QuestionGenerationTask(prompt_service),
        TagGenerationTask(prompt_service),
        ChunkGenerationTask(prompt_service)
    ]


def generate(db: Database, client: OpenAI, model: str) -> None:
    prompt_service = create_prompt_service(client, model)
    tasks = create_generation_tasks(prompt_service)
    pipeline = GenerationPipeline(db=db, tasks=tasks)
    pipeline.run()
