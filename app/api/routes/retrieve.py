from fastapi import APIRouter, Query
from openai import OpenAI
from app.workflows.retreive import retrieve_context
from app.core.config import settings

router = APIRouter()

@router.get("/")
def retrieve_endpoint(
    query: str = Query(...),
):
    client = OpenAI()
    results = retrieve_context(
        query=query,
        openai_client=client,
        openai_model=settings.openai_model,
        question_index_name=settings.question_index_name,
        chunk_index_name=settings.chunk_index_name,
        embedding_model=settings.embedding_model
    )
    return {"results": results}
