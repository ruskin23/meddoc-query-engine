from typing import List, Tuple
import fitz


class TextExtraction:
    """Service for extracting text content from PDF files."""
    
    def __init__(self) -> None:
        """Initialize the text extraction service."""
        pass

    def convert(self, filepath: str) -> List[str]:
        """Extract text from all pages of a PDF file.
        
        Args:
            filepath: Path to the PDF file
            
        Returns:
            List of text content from each page
        """
        doc = fitz.open(filepath)
        return [page.get_text() for page in doc]
