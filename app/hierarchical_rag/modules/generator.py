from typing import List, Any
from sqlalchemy.orm import Session
from abc import ABC, abstractmethod

from app.core.chunking import ChunkService
from app.db.models import PdfFile, PdfPages
from app.db.models import PageQuestions, PageTags, PageChunks
from app.core.prompting import PromptProcessor, PromptPayload

from ..models.models import QAPairs, TagList

class PageRepository:
    def __init__(self, session: Session):
        self.session = session

    def add_questions(self, page_id: int, file_id: int, questions: List[str]):
        self.session.add_all([
            PageQuestions(page_id=page_id, file_id=file_id, question=q)
            for q in questions
        ])

    def add_tags(self, page_id: int, file_id: int, tags: List[str]):
        self.session.add_all([
            PageTags(page_id=page_id, file_id=file_id, tag=t)
            for t in tags
        ])

    def add_chunks(self, page_id: int, file_id: int, chunks: List[str]):
        self.session.add_all([
            PageChunks(page_id=page_id, file_id=file_id, chunk=c)
            for c in chunks
        ])


class PromptService:
    def __init__(self, processor: PromptProcessor):
        self.processor = processor

    def questions_for_page(self, page_text: str) -> Any:
        payload = PromptPayload(
            prompt_key="page_questions",
            output_format=QAPairs,
            inputs={"page_text": page_text}
        )
        return self.processor.process(payload)

    def tags_for_page(self, page_text: str) -> Any:
        payload = PromptPayload(
            prompt_key="body_tags_page",
            output_format=TagList,
            inputs={"page_text": page_text}
        )
        return self.processor.process(payload)

    def tags_from_query(self, query: str) -> Any:
        payload = PromptPayload(
            prompt_key="body_tags_query",
            output_format=TagList,
            inputs={"query": query}
        )
        return self.processor.process(payload)
    
    def questions_from_query(self, query: str, n_questions:int = 15) -> Any:
        payload = PromptPayload(
            prompt_key="questions_query",
            output_format=TagList,
            inputs={"query": query, "n_questions": n_questions}
        )
        return self.processor.process(payload)
    

    def available_prompts(self) -> list:
        return list(self.processor.templates.keys())



class GenerationTask(ABC):
    @abstractmethod
    def run(self, page: PdfPages, file: PdfFile) -> None:
        ...

class QuestionGenerationTask(GenerationTask):
    def __init__(self, prompt_service: PromptService):
        self.prompt_service = prompt_service

    def run(self, page: PdfPages, file: PdfFile, repo: PageRepository):
        questions = self.prompt_service.questions_for_page(page.page_text)
        repo.add_questions(page.id, file.id, questions)


class TagGenerationTask(GenerationTask):
    def __init__(self, prompt_service: PromptService):
        self.prompt_service = prompt_service

    def run(self, page: PdfPages, file: PdfFile, repo: PageRepository):
        tags = self.prompt_service.tags_for_page(page.page_text)
        repo.add_tags(page.id, file.id, tags)


class ChunkGenerationTask(GenerationTask):
    def __init__(self, chunk_service: ChunkService):
        self.chunk_service = chunk_service

    def run(self, page: PdfPages, file: PdfFile, repo: PageRepository):
        chunks = self.chunk_service.chunks_for_page(page.page_text)
        repo.add_chunks(page.id, file.id, chunks)


