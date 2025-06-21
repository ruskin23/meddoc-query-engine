from fastapi import APIRouter, Query
from openai import OpenAI
from app.workflows.retreive import retreive 
from app.core.config import settings

router = APIRouter()

@router.get("/")
def retrieve_endpoint(
    query: str = Query(...),
    top_n: int = Query(5)
):
    client = OpenAI(api_key=settings.openai_api_key)
    results = retreive(
        query=query,
        openai_client=client,
        openai_model=settings.openai_model,
        question_index_name=settings.question_index_name,
        chunk_index_name=settings.chunk_index_name,
        embedding_model=settings.embedding_model,
        top_n=top_n
    )
    return {"results": results}
