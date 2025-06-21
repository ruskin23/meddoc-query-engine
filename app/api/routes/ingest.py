import logging
from pathlib import Path
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.db import Database
from app.workflows import ingest_pdfs
from app.core import settings

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()


class IngestRequest(BaseModel):
    """Request model for PDF ingestion."""
    directory_path: str


class IngestResponse(BaseModel):
    """Response model for PDF ingestion."""
    status: str
    message: str
    files_processed: int = 0


@router.post("/", response_model=IngestResponse)
def ingest_endpoint(request: IngestRequest) -> IngestResponse:
    """API endpoint to ingest all PDF files from a folder into the database.
    
    Args:
        request: Request containing directory path
        
    Returns:
        JSON response with status and message
        
    Raises:
        HTTPException: If ingestion fails
    """
    try:
        # Validate directory path
        directory_path = Path(request.directory_path)
        if not directory_path.exists():
            raise HTTPException(status_code=400, detail=f"Directory does not exist: {request.directory_path}")
        
        if not directory_path.is_dir():
            raise HTTPException(status_code=400, detail=f"Path is not a directory: {request.directory_path}")

        # Check for PDF files in directory
        pdf_files = list(directory_path.glob("*.pdf"))
        if not pdf_files:
            logger.warning(f"No PDF files found in directory: {request.directory_path}")
            return IngestResponse(
                status="success",
                message="No PDF files found in directory",
                files_processed=0
            )

        # Initialize database and ingest PDFs
        db = Database(settings.database_url)
        ingest_pdfs(db, request.directory_path)
        
        logger.info(f"Successfully ingested {len(pdf_files)} PDF files from {request.directory_path}")
        return IngestResponse(
            status="success",
            message=f"Successfully ingested {len(pdf_files)} PDF files",
            files_processed=len(pdf_files)
        )
        
    except HTTPException:
        # Re-raise HTTPExceptions as-is
        raise
        
    except Exception as e:
        logger.error(f"Error during ingestion: {e}")
        raise HTTPException(status_code=500, detail="PDF ingestion operation failed")
