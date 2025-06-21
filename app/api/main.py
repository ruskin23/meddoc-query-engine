"""Main entry point for the Medical Document Query Engine FastAPI application."""

from fastapi import FastAPI
from app.api.routes import ingest, extract, index, retrieve

# Create FastAPI application instance
app = FastAPI(
    title="Medical Document Query Engine",
    description="API for processing and querying medical documents using hierarchical RAG",
    version="1.0.0"
)

# Register API route modules
app.include_router(ingest.router, prefix="/ingest", tags=["ingest"])
app.include_router(extract.router, prefix="/extract", tags=["extract"])
app.include_router(index.router, prefix="/index", tags=["index"])
app.include_router(retrieve.router, prefix="/retrieve", tags=["retrieve"])
