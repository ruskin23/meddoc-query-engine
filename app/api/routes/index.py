from fastapi import APIRouter
from app.db import Database, PdfFile
from app.workflows import generate, index
from sqlalchemy import func

from app.core import settings
from openai import OpenAI

router = APIRouter()

@router.get("/status")
def status_endpoint() -> dict:
    """API endpoint to get the current status of the PDF processing pipeline.
    
    Returns:
        JSON response with counts of files in each processing state
    """
    db = Database(settings.database_url)
    with db.session() as session:
        # Count files in each state
        total_files = session.query(func.count(PdfFile.id)).scalar()
        extracted_files = session.query(func.count(PdfFile.id)).filter(PdfFile.extracted == True).scalar()
        generated_files = session.query(func.count(PdfFile.id)).filter(PdfFile.generated == True).scalar()
        indexed_files = session.query(func.count(PdfFile.id)).filter(PdfFile.indexed == True).scalar()
        
        # Get files that need processing
        needs_extraction = session.query(func.count(PdfFile.id)).filter(PdfFile.extracted == False).scalar()
        needs_generation = session.query(func.count(PdfFile.id)).filter(
            PdfFile.extracted == True, 
            PdfFile.generated == False
        ).scalar()
        needs_indexing = session.query(func.count(PdfFile.id)).filter(
            PdfFile.generated == True, 
            PdfFile.indexed == False
        ).scalar()
        
        return {
            "total_files": total_files,
            "extracted_files": extracted_files,
            "generated_files": generated_files,
            "indexed_files": indexed_files,
            "needs_extraction": needs_extraction,
            "needs_generation": needs_generation,
            "needs_indexing": needs_indexing
        }

@router.post("/generate")
def generate_endpoint() -> dict:
    """API endpoint to generate questions, tags, and chunks for extracted PDFs.
    
    Returns:
        JSON response with status and message
    """
    db = Database(settings.database_url)
    client = OpenAI(api_key=settings.openai_api_key)
    generate(db=db, client=client, model=settings.openai_model)
    return {"status": "success", "message": "Content generation completed"}

@router.post("/index")
def index_endpoint() -> dict:
    """API endpoint to index generated content into the vector database.
    
    Returns:
        JSON response with status and message
    """
    db = Database(settings.database_url)
    index(
        db=db,
        question_index_name=settings.question_index_name,
        chunk_index_name=settings.chunk_index_name,
        embedding_model=settings.embedding_model
    )
    return {"status": "success", "message": "Content indexed successfully"}

@router.post("/")
def full_pipeline_endpoint() -> dict:
    """API endpoint to run both generation and indexing in sequence.
    
    Returns:
        JSON response with status and message
    """
    db = Database(settings.database_url)
    client = OpenAI(api_key=settings.openai_api_key)
    # Step 1: Generate content
    generate(db=db, client=client, model=settings.openai_model)
    # Step 2: Index content
    index(
        db=db,
        question_index_name=settings.question_index_name,
        chunk_index_name=settings.chunk_index_name,
        embedding_model=settings.embedding_model
    )
    return {"status": "success", "message": "Full pipeline completed"}
