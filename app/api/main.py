"""Main entry point for the Medical Document Query Engine FastAPI application."""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import ingest, extract, index, retrieve

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('meddoc.log')
    ]
)

logger = logging.getLogger(__name__)

# Create FastAPI application instance
app = FastAPI(
    title="Medical Document Query Engine",
    description="API for processing and querying medical documents using hierarchical RAG",
    version="1.0.0"
)

# Add CORS middleware for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API route modules
app.include_router(ingest.router, prefix="/ingest", tags=["ingest"])
app.include_router(extract.router, prefix="/extract", tags=["extract"])
app.include_router(index.router, prefix="/index", tags=["index"])
app.include_router(retrieve.router, prefix="/retrieve", tags=["retrieve"])

