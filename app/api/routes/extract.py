from fastapi import APIRouter
from app.workflows import extract_text
from app.db import Database
from app.core import settings

router = APIRouter()

@router.post("/")
def extract_endpoint() -> dict:
    """API endpoint to extract text from all unprocessed PDF files in the database.
    
    Returns:
        JSON response with status and message
    """
    db = Database(settings.database_url)
    extract_text(db)
    return {"status": "success", "message": "Text extracted"}
