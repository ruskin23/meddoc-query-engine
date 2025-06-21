from fastapi import APIRouter
from app.db import Database, PdfFile
from app.workflows import generate, index
from sqlalchemy import func

from app.core import settings
from openai import OpenAI

router = APIRouter()

@router.get("/status")
def status_endpoint():
    """Get the current status of PDF processing pipeline"""
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
def generate_endpoint():
    """Generate questions, tags, and chunks for extracted PDFs"""
    db = Database(settings.database_url)
    client = OpenAI(api_key=settings.openai_api_key)

    generate(db=db, 
             client=client, 
             model=settings.openai_model)
    
    return {"status": "success", "message": "Content generation completed"}

@router.post("/index")
def index_endpoint():
    """Index generated content into vector database"""
    db = Database(settings.database_url)
    
    index(db=db, 
          question_index_name=settings.question_index_name, 
          chunk_index_name=settings.chunk_index_name, 
          embedding_model=settings.embedding_model)

    return {"status": "success", "message": "Content indexed successfully"}

@router.post("/")
def full_pipeline_endpoint():
    """Run both generation and indexing in sequence"""
    db = Database(settings.database_url)
    client = OpenAI(api_key=settings.openai_api_key)

    # Step 1: Generate content
    generate(db=db, 
             client=client, 
             model=settings.openai_model)
    
    # Step 2: Index content
    index(db=db, 
          question_index_name=settings.question_index_name, 
          chunk_index_name=settings.chunk_index_name, 
          embedding_model=settings.embedding_model)

    return {"status": "success", "message": "Full pipeline completed"}
