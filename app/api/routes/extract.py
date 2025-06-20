from fastapi import APIRouter
from app.workflows.extract import extract_text
from app.db.base import Database
from app.core.config import settings

router = APIRouter()

@router.post("/")
def extract_endpoint():
    db = Database(settings.database_url)
    extract_text()
    return {"status": "success", "message": "Text extracted"}
