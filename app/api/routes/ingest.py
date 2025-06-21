from fastapi import APIRouter
from app.db import Database
from app.workflows import ingest_pdfs
from app.core import settings

router = APIRouter()

@router.post("/")
def ingest_endpoint(folder_path: str) -> dict:
    """API endpoint to ingest all PDF files from a folder into the database.
    
    Args:
        folder_path: Path to the folder containing PDF files
        
    Returns:
        JSON response with status and message
    """
    db = Database(settings.database_url)
    ingest_pdfs(db, folder_path)
    return {"status": "success", "message": "PDFs ingested"}
