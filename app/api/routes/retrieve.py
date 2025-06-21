from fastapi import APIRouter, Query
from openai import OpenAI
from app.workflows import retreive 
from app.core import settings

router = APIRouter()

@router.get("/")
def retrieve_endpoint(
    query: str = Query(..., description="User query to search for"),
    top_n: int = Query(5, description="Number of top results to return")
) -> dict:
    """API endpoint to retrieve relevant context chunks for a query.
    
    Args:
        query: User query to search for
        top_n: Number of top results to return
        
    Returns:
        JSON response with retrieval results
    """
    client = OpenAI(api_key=settings.openai_api_key)
    results = retreive(
        query=query,
        client=client,
        model=settings.openai_model,
        question_index_name=settings.question_index_name,
        chunk_index_name=settings.chunk_index_name,
        embedding_model_name=settings.embedding_model,
        top_n=top_n
    )
    return {"results": results}
