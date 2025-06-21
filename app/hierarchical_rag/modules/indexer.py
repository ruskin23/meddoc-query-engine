from typing import List, Dict, Any
from abc import ABC, abstractmethod
import hashlib

from datetime import datetime

from app.core.indexing import BaseIndexer
from app.db import Database, PdfFile, PdfPages

class DocumentProcessor:
    @staticmethod
    def process_page(page: PdfPages, pdf_id: int) -> List[Dict[str, Any]]:
        docs = []
        for question in page.questions:
            question_hash = hashlib.sha256(question.encode()).hexdigest()[:16]
            docs.append({
                "id": f"q-{page.id}-{question_hash}",
                "question": question,
                "tags": page.tags,
                "page_id": page.id,
                "pdf_id": pdf_id
            })
        for chunk in page.chunks:
            chunk_hash = hashlib.sha256(chunk.encode()).hexdigest()[:16]
            docs.append({
                "id": f"c-{page.id}-{chunk_hash}",
                "chunk": chunk,
                "tags": page.tags,
                "page_id": page.id,
                "pdf_id": pdf_id
            })
        return docs

class HierarchicalIndexing:
    def __init__(self, question_indexer: BaseIndexer, chunk_indexer: BaseIndexer):
        self.question_indexer = question_indexer
        self.chunk_indexer = chunk_indexer

    def index(self, documents: List[Dict[str, Any]]):
        questions = [doc for doc in documents if "question" in doc]
        chunks = [doc for doc in documents if "chunk" in doc]

        if questions:
            self.question_indexer.index_documents(questions)
        if chunks:
            self.chunk_indexer.index_documents(chunks)


class HierarchicalIndexer:
    def __init__(self, index_strategy: HierarchicalIndexing, db: Database):
        self.index_strategy = index_strategy
        self.db = db

    def index_all(self):
        with self.db.session() as session:
            # Process files that have been generated but not yet indexed
            pdfs = session.query(PdfFile).filter(
                PdfFile.generated == True,
                PdfFile.indexed == False
            ).all()
            
            for pdf in pdfs:
                try:
                    self.index_pdf(pdf)
                    pdf.indexed = True
                    pdf.indexed_at = datetime.now()
                    session.commit()
                    print(f"Indexed: {pdf.filepath}")
                except Exception as e:
                    print(f"Failed to index {pdf.filepath}: {e}")
                    session.rollback()

    def index_pdf(self, pdf: PdfFile):
        all_docs = []
        for page in pdf.pages:
            all_docs.extend(DocumentProcessor.process_page(page, pdf.id))
        self.index_strategy.index(all_docs)


