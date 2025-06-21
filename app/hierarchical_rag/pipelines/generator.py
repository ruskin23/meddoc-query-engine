from typing import List

from app.core.pipelines import Generate
from app.hierarchical_rag.modules.generator import GenerationTask, PageRepository
from app.db.base import Database
from app.db.models import PdfFile

class GenerationPipeline(Generate):
    def __init__(self, db: Database, tasks: List[GenerationTask]):
        self.db = db
        self.tasks = tasks

    def run(self):
        with self.db.session() as session:
            files = session.query(PdfFile).filter(PdfFile.extracted == False).all()
            repo = PageRepository(session)

            for file in files:
                for page in file.pages:
                    try:
                        for task in self.tasks:
                            task.run(page, file, repo)
                        print(f"Generated: {file.filepath} page {page.page_number}")
                    except Exception as e:
                        print(f"Failed on {file.filepath} page {page.page_number}: {e}")