from typing import List, Any
from sqlalchemy.orm import Session
from abc import ABC, abstractmethod

from app.core import ChunkService, PromptProcessor, PromptPayload
from app.db import PdfFile, PdfPages, PageQuestions, PageTags, PageChunks

from ..models.models import QAPairs, TagList

class PageRepository:
    """Repository for managing page-related database operations."""
    
    def __init__(self, session: Session) -> None:
        """Initialize the page repository.
        
        Args:
            session: Database session
        """
        self.session = session

    def add_questions(self, page_id: int, file_id: int, questions: List[str]) -> None:
        """Add questions to the database for a specific page.
        
        Args:
            page_id: ID of the page
            file_id: ID of the PDF file
            questions: List of questions to add
        """
        self.session.add_all([
            PageQuestions(page_id=page_id, file_id=file_id, question=q)
            for q in questions
        ])

    def add_tags(self, page_id: int, file_id: int, tags: List[str]) -> None:
        """Add tags to the database for a specific page.
        
        Args:
            page_id: ID of the page
            file_id: ID of the PDF file
            tags: List of tags to add
        """
        self.session.add_all([
            PageTags(page_id=page_id, file_id=file_id, tag=t)
            for t in tags
        ])

    def add_chunks(self, page_id: int, file_id: int, chunks: List[str]) -> None:
        """Add text chunks to the database for a specific page.
        
        Args:
            page_id: ID of the page
            file_id: ID of the PDF file
            chunks: List of text chunks to add
        """
        self.session.add_all([
            PageChunks(page_id=page_id, file_id=file_id, chunk=c)
            for c in chunks
        ])


class PromptService:
    """Service for handling prompt-based content generation."""
    
    def __init__(self, processor: PromptProcessor) -> None:
        """Initialize the prompt service.
        
        Args:
            processor: Prompt processor instance
        """
        self.processor = processor

    def questions_for_page(self, page_text: str) -> Any:
        """Generate questions from page text.
        
        Args:
            page_text: Text content of the page
            
        Returns:
            Generated questions in QAPairs format
        """
        payload = PromptPayload(
            prompt_key="page_questions",
            output_format=QAPairs,
            inputs={"page_text": page_text}
        )
        return self.processor.process(payload)

    def tags_for_page(self, page_text: str) -> Any:
        """Generate tags from page text.
        
        Args:
            page_text: Text content of the page
            
        Returns:
            Generated tags in TagList format
        """
        payload = PromptPayload(
            prompt_key="body_tags_page",
            output_format=TagList,
            inputs={"page_text": page_text}
        )
        return self.processor.process(payload)

    def tags_from_query(self, query: str) -> Any:
        """Generate tags from a user query.
        
        Args:
            query: User query text
            
        Returns:
            Generated tags in TagList format
        """
        payload = PromptPayload(
            prompt_key="body_tags_query",
            output_format=TagList,
            inputs={"query": query}
        )
        return self.processor.process(payload)
    
    def questions_from_query(self, query: str, n_questions: int = 15) -> Any:
        """Generate questions from a user query.
        
        Args:
            query: User query text
            n_questions: Number of questions to generate
            
        Returns:
            Generated questions in TagList format
        """
        payload = PromptPayload(
            prompt_key="questions_query",
            output_format=TagList,
            inputs={"query": query, "n_questions": n_questions}
        )
        return self.processor.process(payload)

    def available_prompts(self) -> List[str]:
        """Get list of available prompt template keys.
        
        Returns:
            List of prompt template names
        """
        return list(self.processor.templates.keys())


class GenerationTask(ABC):
    """Abstract base class for content generation tasks."""
    
    @abstractmethod
    def run(self, page: PdfPages, file: PdfFile, repo: PageRepository) -> None:
        """Run the generation task on a page.
        
        Args:
            page: PDF page to process
            file: PDF file containing the page
            repo: Page repository for database operations
        """
        ...


class QuestionGenerationTask(GenerationTask):
    """Task for generating questions from page content."""
    
    def __init__(self, prompt_service: PromptService) -> None:
        """Initialize the question generation task.
        
        Args:
            prompt_service: Service for prompt-based generation
        """
        self.prompt_service = prompt_service

    def run(self, page: PdfPages, file: PdfFile, repo: PageRepository) -> None:
        """Generate questions for a page and store them.
        
        Args:
            page: PDF page to process
            file: PDF file containing the page
            repo: Page repository for database operations
        """
        questions = self.prompt_service.questions_for_page(page.page_text)
        repo.add_questions(page.id, file.id, questions)


class TagGenerationTask(GenerationTask):
    """Task for generating tags from page content."""
    
    def __init__(self, prompt_service: PromptService) -> None:
        """Initialize the tag generation task.
        
        Args:
            prompt_service: Service for prompt-based generation
        """
        self.prompt_service = prompt_service

    def run(self, page: PdfPages, file: PdfFile, repo: PageRepository) -> None:
        """Generate tags for a page and store them.
        
        Args:
            page: PDF page to process
            file: PDF file containing the page
            repo: Page repository for database operations
        """
        tags = self.prompt_service.tags_for_page(page.page_text)
        repo.add_tags(page.id, file.id, tags)


class ChunkGenerationTask(GenerationTask):
    """Task for generating text chunks from page content."""
    
    def __init__(self, chunk_service: ChunkService) -> None:
        """Initialize the chunk generation task.
        
        Args:
            chunk_service: Service for text chunking
        """
        self.chunk_service = chunk_service

    def run(self, page: PdfPages, file: PdfFile, repo: PageRepository) -> None:
        """Generate chunks for a page and store them.
        
        Args:
            page: PDF page to process
            file: PDF file containing the page
            repo: Page repository for database operations
        """
        chunks = self.chunk_service.chunks_for_page(page.page_text)
        repo.add_chunks(page.id, file.id, chunks)


