import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.db import Database, PdfFile
from app.workflows import generate, index
from openai import OpenAI

from app.core import settings

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()


class ProcessingResponse(BaseModel):
    """Response model for processing operations."""
    status: str
    message: str
    files_processed: int = 0


@router.post("/index", response_model=ProcessingResponse)
def index_endpoint() -> ProcessingResponse:
    """API endpoint to run both generation and indexing in sequence.
    
    This endpoint processes files in two steps:
    1. Generates content (questions, tags, chunks) for extracted files that haven't been generated
    2. Indexes generated content into the vector database for files that haven't been indexed
    
    Returns:
        JSON response with status and message
        
    Raises:
        HTTPException: If pipeline execution fails
    """
    try:
        # Validate configuration
        if not settings.openai_api_key:
            raise HTTPException(status_code=400, detail="OpenAI API key is not configured")
        if not settings.question_index_name or not settings.chunk_index_name:
            raise HTTPException(status_code=400, detail="Pinecone index names are not configured")
        
        db = Database(settings.database_url)
        
        # Count files that need processing
        with db.session() as session:
            files_to_generate = session.query(PdfFile).filter(
                PdfFile.extracted == True,
                PdfFile.generated == False
            ).count()
            files_to_index = session.query(PdfFile).filter(
                PdfFile.generated == True,
                PdfFile.indexed == False
            ).count()
        
        total_files = files_to_generate + files_to_index
        
        if total_files == 0:
            logger.info("No files need processing")
            return ProcessingResponse(
                status="success",
                message="No files need processing",
                files_processed=0
            )
        
        client = OpenAI(api_key=settings.openai_api_key)
        
        # Step 1: Generate content for files that need generation
        if files_to_generate > 0:
            generate(db=db, client=client, model=settings.openai_model)
            logger.info(f"Generated content for {files_to_generate} files")
        
        # Step 2: Index content for all files that need indexing
        index(
            db=db,
            question_index_name=settings.question_index_name,
            chunk_index_name=settings.chunk_index_name,
            embedding_model=settings.embedding_model
        )
        
        logger.info(f"Successfully completed processing for {total_files} files")
        return ProcessingResponse(
            status="success",
            message=f"Successfully completed processing for {total_files} files (generated: {files_to_generate}, indexed: {files_to_index})",
            files_processed=total_files
        )
    
    except HTTPException:
        # Re-raise HTTPExceptions as-is
        raise
    
    except Exception as e:
        logger.error(f"Error during processing: {e}")
        raise HTTPException(status_code=500, detail="Processing operation failed")

