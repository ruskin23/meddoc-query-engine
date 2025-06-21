from typing import List

from app.core import Generate
from app.hierarchical_rag import GenerationTask, PageRepository
from app.db import Database, PdfFile
from datetime import datetime


class GenerationPipeline(Generate):
    """Pipeline for generating questions, tags, and chunks from extracted PDF content."""
    
    def __init__(self, db: Database, tasks: List[GenerationTask]) -> None:
        """Initialize the generation pipeline.
        
        Args:
            db: Database connection
            tasks: List of generation tasks to run on each page
        """
        self.db = db
        self.tasks = tasks

    def run(self) -> None:
        """Run the generation pipeline on all extracted but ungenerated PDF files."""
        with self.db.session() as session:
            # Process files that have been extracted but not yet generated
            files = session.query(PdfFile).filter(
                PdfFile.extracted == True,
                PdfFile.generated == False
            ).all()
            
            repo = PageRepository(session)

            for file in files:
                try:
                    # Process each page with all generation tasks
                    for page in file.pages:
                        for task in self.tasks:
                            task.run(page, file, repo)
                    
                    # Mark file as generated after successful processing
                    file.generated = True
                    file.generated_at = datetime.now()
                    session.commit()
                    
                    print(f"Generated content for: {file.filepath}")
                    
                except Exception as e:
                    print(f"Failed to generate content for {file.filepath}: {e}")
                    session.rollback()