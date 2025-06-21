"""Custom exceptions for the medical document query engine."""


class MedDocError(Exception):
    """Base exception for all MedDoc related errors."""
    pass


class DatabaseError(MedDocError):
    """Raised when database operations fail."""
    pass


class PDFProcessingError(MedDocError):
    """Raised when PDF processing operations fail."""
    pass


class ExtractionError(PDFProcessingError):
    """Raised when text extraction from PDFs fails."""
    pass


class GenerationError(MedDocError):
    """Raised when content generation (questions, tags, chunks) fails."""
    pass


class IndexingError(MedDocError):
    """Raised when vector indexing operations fail."""
    pass


class RetrievalError(MedDocError):
    """Raised when retrieval operations fail."""
    pass


class ConfigurationError(MedDocError):
    """Raised when configuration is invalid or missing."""
    pass


class ValidationError(MedDocError):
    """Raised when input validation fails."""
    pass 