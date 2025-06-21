from app.db import Database, PdfFile, PdfPages
from app.core.extracting import TextExtraction

from pathlib import Path
from datetime import datetime

pdf_service = TextExtraction()

def extract_text(db: Database) -> None:
    """
    Extract text from all PDF files in the DB that haven't been processed yet.
    """
    with db.session() as session:
        files = session.query(PdfFile).filter(PdfFile.extracted == False).all()

        for file in files:
            path = Path(file.filepath)
            if not path.exists():
                print(f"File missing: {file.filepath}")
                continue

            try:
                pages = pdf_service.convert(path)

                for page_number, page_text in enumerate(pages):
                    session.add(PdfPages(
                        file_id=file.id,
                        page_number=page_number,
                        page_text=page_text
                    ))

                file.extracted = True
                file.extracted_at = datetime.now(datetime.now())
                
                print(f"Extracted {len(pages)} pages from {file.filepath}")

            except Exception as e:
                print(f"Failed to extract {file.filepath}: {e}")
