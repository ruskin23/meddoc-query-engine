import logging
from pathlib import Path
from datetime import datetime

from app.db import Database, PdfFile, PdfPages
from app.core import TextExtraction

# Initialize text extraction service
pdf_service = TextExtraction()


def extract_text(db: Database) -> None:
    """Extract text from all PDF files in the database that haven't been processed yet.
    
    Args:
        db: Database connection
    """
    with db.session() as session:
        files = session.query(PdfFile).filter(PdfFile.extracted == False).all()

        for file in files:
            path = Path(file.filepath)
            if not path.exists():
                logging.warning(f"File not found: {file.filepath}")
                continue

            try:
                pages = pdf_service.convert(path)

                # Add each page to the database
                for page_number, page_text in enumerate(pages):
                    session.add(PdfPages(
                        file_id=file.id,
                        page_number=page_number,
                        page_text=page_text
                    ))

                # Mark file as extracted
                file.extracted = True
                file.extracted_at = datetime.now()
                
                logging.info(f"Extracted {len(pages)} pages from {file.filepath}")

            except Exception as e:
                logging.error(f"Failed to extract {file.filepath}: {e}")
