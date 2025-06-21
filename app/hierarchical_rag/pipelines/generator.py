from typing import List

from app.core.pipelines import Generate
from app.hierarchical_rag.modules.generator import GenerationTask, PageRepository
from app.db import Database, PdfFile
from datetime import datetime

class GenerationPipeline(Generate):
    def __init__(self, db: Database, tasks: List[GenerationTask]):
        self.db = db
        self.tasks = tasks

    def run(self):
        with self.db.session() as session:
            # Process files that have been extracted but not yet generated
            files = session.query(PdfFile).filter(
                PdfFile.extracted == True,
                PdfFile.generated == False
            ).all()
            
            repo = PageRepository(session)

            for file in files:
                try:
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