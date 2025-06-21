import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.workflows import extract_text
from app.db import Database
from app.core import settings, ExtractionError, DatabaseError

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()


class ExtractionResponse(BaseModel):
    """Response model for text extraction."""
    status: str
    message: str
    files_processed: int = 0


@router.post("/", response_model=ExtractionResponse)
def extract_endpoint() -> ExtractionResponse:
    """API endpoint to extract text from all unprocessed PDF files in the database.
    
    Returns:
        JSON response with status and message
        
    Raises:
        HTTPException: If extraction fails
    """
    try:
        db = Database(settings.database_url)
        
        # Count files that need extraction
        with db.session() as session:
            from app.db import PdfFile
            files_to_process = session.query(PdfFile).filter(PdfFile.extracted == False).count()
        
        if files_to_process == 0:
            logger.info("No files need extraction")
            return ExtractionResponse(
                status="success",
                message="No files need extraction",
                files_processed=0
            )
        
        # Perform extraction
        extract_text(db)
        
        logger.info(f"Successfully extracted text from {files_to_process} files")
        return ExtractionResponse(
            status="success",
            message=f"Successfully extracted text from {files_to_process} files",
            files_processed=files_to_process
        )
        
    except ExtractionError as e:
        logger.error(f"Extraction error: {e}")
        raise HTTPException(status_code=422, detail=f"Text extraction failed: {str(e)}")
    
    except DatabaseError as e:
        logger.error(f"Database error during extraction: {e}")
        raise HTTPException(status_code=500, detail=f"Database operation failed: {str(e)}")
    
    except Exception as e:
        logger.error(f"Unexpected error during extraction: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
