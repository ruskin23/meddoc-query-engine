from sqlalchemy.orm import Session
from typing import List, Tuple

from app.db.base import Database
from app.db.models import PdfFile
from app.db.models import PdfPages, PageQuestions, PageTags, PageChunks


from app.core.chunking import ChunkService
from app.hierarchical_rag.generator import PromptService

def insert_questions(session: Session, page_id: int, file_id: int, questions: List[str]):
    for question in questions:
        session.add(
            PageQuestions(
                page_id=page_id,
                file_id=file_id,
                question=question
                )
            )
        
def insert_tags(session: Session, page_id: int, file_id: int, tags: List[str]):
    for tag in tags:
        session.add(
            PageTags(
                page_id=page_id,
                file_id=file_id,
                tag=tag
                )
            )
        
def insert_chunks(session: Session, page_id: int, file_id: int, chunks: List[str]):
    for chunk in chunks:
        session.add(
            PageChunks(
                page_id=page_id,
                file_id=file_id,
                chunk=chunk
                )
            )

def generate(db: Database, prompt_service: PromptService, chunking_service: ChunkService) -> None:
    with db.session() as session:
        files = session.query(PdfFile).filter(PdfFile.extracted == False).all()
        for file in files:
            for page in file.pages:
                try:
                    questions = prompt_service.questions_for_page(page.page_text)
                    insert_questions(session, page.id, file.id, questions)

                    tags = prompt_service.tags_for_page(page.page_text)
                    insert_tags(session, page.id, file.id, tags)

                    chunks = chunking_service.chunks_for_page(page.page_text)
                    insert_chunks(session, page.id, file.id, chunks)

                    print(f"Generated for {file.filepath} page {page.page_number}")

                except Exception as e:
                    print(f"Failed on {file.filepath} page {page.page_number}: {e}")
