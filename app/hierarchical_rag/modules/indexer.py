from typing import List, Dict, Any
from datetime import datetime
import hashlib

from app.core import BaseIndexer
from app.db import Database, PdfFile, PdfPages

class DocumentProcessor:
    """Processor for converting page content into indexable documents."""
    
    @staticmethod
    def process_page(page: PdfPages, pdf_id: int) -> List[Dict[str, Any]]:
        """Convert a page's content into indexable documents.
        
        Args:
            page: PDF page with questions, tags, and chunks
            pdf_id: ID of the PDF file
            
        Returns:
            List of document dictionaries for indexing
        """
        docs = []
        # Process questions from the page
        for question in page.questions:
            question_hash = hashlib.sha256(question.question.encode()).hexdigest()[:16]
            docs.append({
                "id": f"q-{page.id}-{question_hash}",
                "question": question.question,
                "tags": [tag.tag for tag in page.tags],
                "page_id": page.id,
                "pdf_id": pdf_id
            })
        # Process chunks from the page
        for chunk in page.chunks:
            chunk_hash = hashlib.sha256(chunk.chunk.encode()).hexdigest()[:16]
            docs.append({
                "id": f"c-{page.id}-{chunk_hash}",
                "chunk": chunk.chunk,
                "tags": [tag.tag for tag in page.tags],
                "page_id": page.id,
                "pdf_id": pdf_id
            })
        return docs

class HierarchicalIndexing:
    """Strategy for indexing questions and chunks separately."""
    
    def __init__(self, question_indexer: BaseIndexer, chunk_indexer: BaseIndexer) -> None:
        """Initialize the hierarchical indexing strategy.
        
        Args:
            question_indexer: Indexer for question documents
            chunk_indexer: Indexer for chunk documents
        """
        self.question_indexer = question_indexer
        self.chunk_indexer = chunk_indexer

    def index(self, documents: List[Dict[str, Any]]) -> None:
        """Index documents by separating questions and chunks.
        
        Args:
            documents: List of document dictionaries to index
        """
        questions = [doc for doc in documents if "question" in doc]
        chunks = [doc for doc in documents if "chunk" in doc]

        if questions:
            self.question_indexer.index_documents(questions)
        if chunks:
            self.chunk_indexer.index_documents(chunks)


class HierarchicalIndexer:
    """Main indexer for processing PDF files and their content."""
    
    def __init__(self, index_strategy: HierarchicalIndexing, db: Database) -> None:
        """Initialize the hierarchical indexer.
        
        Args:
            index_strategy: Strategy for indexing documents
            db: Database connection
        """
        self.index_strategy = index_strategy
        self.db = db

    def index_all(self) -> None:
        """Index all PDF files that have been generated but not yet indexed."""
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

    def index_pdf(self, pdf: PdfFile) -> None:
        """Index a single PDF file by processing all its pages.
        
        Args:
            pdf: PDF file to index
        """
        all_docs = []
        for page in pdf.pages:
            all_docs.extend(DocumentProcessor.process_page(page, pdf.id))
        self.index_strategy.index(all_docs)


