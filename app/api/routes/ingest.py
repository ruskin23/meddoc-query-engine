from fastapi import APIRouter
from app.db import Database
from app.workflows.ingest import ingest_pdfs
from app.core.config import settings

router = APIRouter()

@router.post("/")
def ingest_endpoint(folder_path: str):
    db = Database(settings.database_url)
    ingest_pdfs(db, folder_path)
    return {"status": "success", "message": "PDFs ingested"}
