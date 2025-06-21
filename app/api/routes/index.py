from fastapi import APIRouter
from app.db.base import Database
from app.workflows.generate import generate
from app.workflows.index import index

from app.core.config import settings
from openai import OpenAI

router = APIRouter()

@router.post("/")
def index_endpoint():
    db = Database(settings.database_url)
    client = OpenAI()

    generate(db=db, 
             client=client, 
             model=settings.openai_model)
    
    index(db=db, 
          question_index_name=settings.question_index_name, 
          chunk_index_name=settings.chunk_index_name, 
          embedding_model=settings.embedding_model)

    return {"status": "success", "message": "Content generated and indexed"}
