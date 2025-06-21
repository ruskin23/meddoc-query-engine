from pathlib import Path
from typing import Union
from app.db import Database, PdfFile

def ingest_pdfs(db: Database, folder_path: Union[str, Path]) -> None:
    """
    Adds all PDF file paths in a folder to the PdfFile table if not already present.
    """
    folder = Path(folder_path)
    if not folder.exists() or not folder.is_dir():
        raise ValueError(f"Invalid folder path: {folder_path}")

    pdf_files = list(folder.glob("*.pdf"))

    if not pdf_files:
        print("No PDF files found.")
        return

    with db.session() as session:
        for file in pdf_files:
            existing = session.query(PdfFile).filter(PdfFile.filepath == str(file)).first()
            if existing:
                print(f"Already in DB: {file}")
                continue
            pdf_file = PdfFile(filepath=str(file))
            session.add(pdf_file)
            print(f"Added: {file}")
