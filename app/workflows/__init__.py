"""Workflow functions for the medical document processing pipeline."""

from .ingest import ingest_pdfs
from .extract import extract_text
from .generate import generate
from .index import index
from .retrieve import retrieve

__all__ = [
    "ingest_pdfs",
    "extract_text", 
    "generate",
    "index",
    "retrieve",
]
