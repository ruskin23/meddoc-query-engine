import logging
import time
from typing import List
from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel, Field
from openai import OpenAI
from app.workflows import retrieve 
from app.core import settings

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()


class RetrievalResult(BaseModel):
    """Individual retrieval result."""
    chunk: str
    score: float
    page_id: int
    file_id: int
    metadata: dict = Field(default_factory=dict)


class RetrievalResponse(BaseModel):
    """Response model for retrieval operations."""
    query: str
    results: List[RetrievalResult]
    total_results: int
    processing_time_ms: float = 0.0


@router.get("/", response_model=RetrievalResponse)
def retrieve_endpoint(
    query: str = Query(..., description="User query to search for", min_length=1),
    top_n: int = Query(5, description="Number of top results to return", ge=1, le=50)
) -> RetrievalResponse:
    """API endpoint to retrieve relevant context chunks for a query.
    
    Args:
        query: User query to search for
        top_n: Number of top results to return
        
    Returns:
        JSON response with retrieval results
        
    Raises:
        HTTPException: If retrieval fails
    """
    start_time = time.time()
    
    try:
        # Basic validation
        if not query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        # Execute retrieval
        client = OpenAI(api_key=settings.openai_api_key)
        results = retrieve(
            query=query,
            client=client,
            model=settings.openai_model,
            question_index_name=settings.question_index_name,
            chunk_index_name=settings.chunk_index_name,
            embedding_model_name=settings.embedding_model,
            top_n=top_n
        )
        
        # Format response
        retrieval_results = [
            RetrievalResult(
                chunk=result.get('chunk', ''),
                score=result.get('score', 0.0),
                page_id=result.get('page_id', 0),
                file_id=result.get('file_id', 0),
                metadata=result.get('metadata', {})
            )
            for result in results or []
        ]
        
        processing_time = (time.time() - start_time) * 1000
        logger.info(f"Retrieved {len(retrieval_results)} results for query: '{query}' in {processing_time:.2f}ms")
        
        return RetrievalResponse(
            query=query,
            results=retrieval_results,
            total_results=len(retrieval_results),
            processing_time_ms=processing_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during retrieval: {e}")
        raise HTTPException(status_code=500, detail="Retrieval operation failed")
