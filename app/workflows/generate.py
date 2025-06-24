import logging
from openai import OpenAI
from datetime import datetime
from typing import List

from app.core import PromptProcessor, PromptRunner, ChunkService, TEMPLATES, TagList
from app.core.models import Questions
from app.db import Database, PdfFile, PageQuestions, PageTags, PageChunks
from app.core.prompting import PromptPayload


class ContentGenerator:
    """Content generator that handles questions, tags, and chunks for PDF pages."""
    
    def __init__(self, client: OpenAI, model: str):
        """Initialize the content generator.
        
        Args:
            client: OpenAI client for prompt-based generation
            model: Model name to use for generation
        """
        # Create prompt processor for LLM-based generation
        runner = PromptRunner(client=client, model=model)
        self.prompt_processor = PromptProcessor(generator=runner, templates=TEMPLATES)
        
        # Create chunk service for text chunking
        self.chunk_service = ChunkService()
    
    def generate_for_file(self, pdf_file: PdfFile, session) -> None:
        """Generate questions, tags, and chunks for all pages in a PDF file.
        
        Args:
            pdf_file: PDF file to process
            session: Database session for storing results
        """
        for page in pdf_file.pages:
            # Generate questions for the page
            questions = self._generate_questions(page.page_text)
            self._save_questions(page.id, pdf_file.id, questions, session)
            
            # Generate tags for the page
            tags = self._generate_tags(page.page_text)
            self._save_tags(page.id, pdf_file.id, tags, session)
            
            # Generate chunks for the page
            chunks = self._generate_chunks(page.page_text)
            self._save_chunks(page.id, pdf_file.id, chunks, session)
    
    def _generate_questions(self, page_text: str) -> List[str]:
        """Generate questions from page text using LLM."""
        payload = PromptPayload(
            prompt_key="page_questions",
            output_format=Questions,
            inputs={"page_text": page_text}
        )
        result = self.prompt_processor.process(payload)
        # Extract questions from the Questions result
        return result.questions if hasattr(result, 'questions') else []
    
    def _generate_tags(self, page_text: str) -> List[str]:
        """Generate tags from page text using LLM."""
        payload = PromptPayload(
            prompt_key="body_tags_page",
            output_format=TagList,
            inputs={"page_text": page_text}
        )
        result = self.prompt_processor.process(payload)
        return result.tags if hasattr(result, 'tags') else []
    
    def _generate_chunks(self, page_text: str) -> List[str]:
        """Generate text chunks from page text."""
        return self.chunk_service.chunks_for_page(page_text)
    
    def _save_questions(self, page_id: int, file_id: int, questions: List[str], session) -> None:
        """Save generated questions to database."""
        question_objects = [
            PageQuestions(page_id=page_id, file_id=file_id, question=q)
            for q in questions
        ]
        session.add_all(question_objects)
    
    def _save_tags(self, page_id: int, file_id: int, tags: List[str], session) -> None:
        """Save generated tags to database."""
        tag_objects = [
            PageTags(page_id=page_id, file_id=file_id, tag=t)
            for t in tags
        ]
        session.add_all(tag_objects)
    
    def _save_chunks(self, page_id: int, file_id: int, chunks: List[str], session) -> None:
        """Save generated chunks to database."""
        chunk_objects = [
            PageChunks(page_id=page_id, file_id=file_id, chunk=c)
            for c in chunks
        ]
        session.add_all(chunk_objects)


def generate(db: Database, client: OpenAI, model: str) -> None:
    """Generate questions, tags, and chunks for all extracted PDF files.
    
    Args:
        db: Database connection
        client: OpenAI client instance
        model: Model name to use for generation
    """
    generator = ContentGenerator(client, model)
    
    with db.session() as session:
        # Find files that have been extracted but not yet generated
        files = session.query(PdfFile).filter(
            PdfFile.extracted == True,
            PdfFile.generated == False
        ).all()
        
        for file in files:
            try:
                # Generate content for all pages in the file
                generator.generate_for_file(file, session)
                
                # Mark file as generated
                file.generated = True
                file.generated_at = datetime.now()
                
                logging.info(f"Generated content for: {file.filepath}")
                
            except Exception as e:
                logging.error(f"Failed to generate content for {file.filepath}: {e}")
                session.rollback()
