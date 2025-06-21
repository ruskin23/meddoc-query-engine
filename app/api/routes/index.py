import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.db import Database, PdfFile
from app.workflows import generate, index
from sqlalchemy import func
from openai import OpenAI

from app.core import settings, GenerationError, IndexingError, DatabaseError, ConfigurationError

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()


class StatusResponse(BaseModel):
    """Response model for pipeline status."""
    total_files: int
    extracted_files: int
    generated_files: int
    indexed_files: int
    needs_extraction: int
    needs_generation: int
    needs_indexing: int


class ProcessingResponse(BaseModel):
    """Response model for processing operations."""
    status: str
    message: str
    files_processed: int = 0


@router.get("/status", response_model=StatusResponse)
def status_endpoint() -> StatusResponse:
    """API endpoint to get the current status of the PDF processing pipeline.
    
    Returns:
        JSON response with counts of files in each processing state
        
    Raises:
        HTTPException: If status retrieval fails
    """
    try:
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
            
            return StatusResponse(
                total_files=total_files,
                extracted_files=extracted_files,
                generated_files=generated_files,
                indexed_files=indexed_files,
                needs_extraction=needs_extraction,
                needs_generation=needs_generation,
                needs_indexing=needs_indexing
            )
    
    except DatabaseError as e:
        logger.error(f"Database error during status check: {e}")
        raise HTTPException(status_code=500, detail=f"Database operation failed: {str(e)}")
    
    except Exception as e:
        logger.error(f"Unexpected error during status check: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/generate", response_model=ProcessingResponse)
def generate_endpoint() -> ProcessingResponse:
    """API endpoint to generate questions, tags, and chunks for extracted PDFs.
    
    Returns:
        JSON response with status and message
        
    Raises:
        HTTPException: If generation fails
    """
    try:
        # Validate configuration
        if not settings.openai_api_key:
            raise ConfigurationError("OpenAI API key is not configured")
        
        db = Database(settings.database_url)
        
        # Count files that need generation
        with db.session() as session:
            files_to_process = session.query(PdfFile).filter(
                PdfFile.extracted == True,
                PdfFile.generated == False
            ).count()
        
        if files_to_process == 0:
            logger.info("No files need generation")
            return ProcessingResponse(
                status="success",
                message="No files need generation",
                files_processed=0
            )
        
        client = OpenAI(api_key=settings.openai_api_key)
        generate(db=db, client=client, model=settings.openai_model)
        
        logger.info(f"Successfully generated content for {files_to_process} files")
        return ProcessingResponse(
            status="success",
            message=f"Successfully generated content for {files_to_process} files",
            files_processed=files_to_process
        )
    
    except ConfigurationError as e:
        logger.error(f"Configuration error during generation: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    
    except GenerationError as e:
        logger.error(f"Generation error: {e}")
        raise HTTPException(status_code=422, detail=f"Content generation failed: {str(e)}")
    
    except DatabaseError as e:
        logger.error(f"Database error during generation: {e}")
        raise HTTPException(status_code=500, detail=f"Database operation failed: {str(e)}")
    
    except Exception as e:
        logger.error(f"Unexpected error during generation: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/index", response_model=ProcessingResponse)
def index_endpoint() -> ProcessingResponse:
    """API endpoint to index generated content into the vector database.
    
    Returns:
        JSON response with status and message
        
    Raises:
        HTTPException: If indexing fails
    """
    try:
        # Validate configuration
        if not settings.question_index_name or not settings.chunk_index_name:
            raise ConfigurationError("Pinecone index names are not configured")
        
        db = Database(settings.database_url)
        
        # Count files that need indexing
        with db.session() as session:
            files_to_process = session.query(PdfFile).filter(
                PdfFile.generated == True,
                PdfFile.indexed == False
            ).count()
        
        if files_to_process == 0:
            logger.info("No files need indexing")
            return ProcessingResponse(
                status="success",
                message="No files need indexing",
                files_processed=0
            )
        
        index(
            db=db,
            question_index_name=settings.question_index_name,
            chunk_index_name=settings.chunk_index_name,
            embedding_model=settings.embedding_model
        )
        
        logger.info(f"Successfully indexed content for {files_to_process} files")
        return ProcessingResponse(
            status="success",
            message=f"Successfully indexed content for {files_to_process} files",
            files_processed=files_to_process
        )
    
    except ConfigurationError as e:
        logger.error(f"Configuration error during indexing: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    
    except IndexingError as e:
        logger.error(f"Indexing error: {e}")
        raise HTTPException(status_code=422, detail=f"Content indexing failed: {str(e)}")
    
    except DatabaseError as e:
        logger.error(f"Database error during indexing: {e}")
        raise HTTPException(status_code=500, detail=f"Database operation failed: {str(e)}")
    
    except Exception as e:
        logger.error(f"Unexpected error during indexing: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/", response_model=ProcessingResponse)
def full_pipeline_endpoint() -> ProcessingResponse:
    """API endpoint to run both generation and indexing in sequence.
    
    Returns:
        JSON response with status and message
        
    Raises:
        HTTPException: If pipeline execution fails
    """
    try:
        # Validate configuration
        if not settings.openai_api_key:
            raise ConfigurationError("OpenAI API key is not configured")
        if not settings.question_index_name or not settings.chunk_index_name:
            raise ConfigurationError("Pinecone index names are not configured")
        
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
        
        # Step 1: Generate content
        if files_to_generate > 0:
            generate(db=db, client=client, model=settings.openai_model)
            logger.info(f"Generated content for {files_to_generate} files")
        
        # Step 2: Index content
        index(
            db=db,
            question_index_name=settings.question_index_name,
            chunk_index_name=settings.chunk_index_name,
            embedding_model=settings.embedding_model
        )
        
        logger.info(f"Successfully completed full pipeline for {total_files} files")
        return ProcessingResponse(
            status="success",
            message=f"Successfully completed full pipeline for {total_files} files",
            files_processed=total_files
        )
    
    except ConfigurationError as e:
        logger.error(f"Configuration error during pipeline execution: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    
    except (GenerationError, IndexingError) as e:
        logger.error(f"Processing error during pipeline execution: {e}")
        raise HTTPException(status_code=422, detail=f"Pipeline execution failed: {str(e)}")
    
    except DatabaseError as e:
        logger.error(f"Database error during pipeline execution: {e}")
        raise HTTPException(status_code=500, detail=f"Database operation failed: {str(e)}")
    
    except Exception as e:
        logger.error(f"Unexpected error during pipeline execution: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
