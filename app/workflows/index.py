import logging
import pinecone
import hashlib
from datetime import datetime
from typing import List, Dict, Any

from app.core import EmbeddingService, PineconeIndexer
from app.db import Database, PdfFile


class DocumentIndexer:
    """Document indexer that handles questions and chunks separately."""
    
    def __init__(self, question_index_name: str, chunk_index_name: str, embedding_model: str):
        """Initialize the document indexer.
        
        Args:
            question_index_name: Name of the question index in Pinecone
            chunk_index_name: Name of the chunk index in Pinecone  
            embedding_model: Model name for generating embeddings
        """
        # Initialize Pinecone and embedding service
        self.client = pinecone.Pinecone()
        self.embedding_service = EmbeddingService(model=embedding_model)
        
        # Create indexers for questions and chunks
        self.question_indexer = PineconeIndexer(
            index=self.client.Index(question_index_name),
            embedding_service=self.embedding_service,
            text_key="question",
            metadata_keys=["tags", "page_id", "pdf_id"]
        )
        
        self.chunk_indexer = PineconeIndexer(
            index=self.client.Index(chunk_index_name),
            embedding_service=self.embedding_service,
            text_key="chunk", 
            metadata_keys=["tags", "page_id", "pdf_id"]
        )
    
    def index_file(self, pdf_file: PdfFile) -> None:
        """Index all content from a PDF file.
        
        Args:
            pdf_file: PDF file to index
        """
        question_docs = []
        chunk_docs = []
        
        # Process each page and collect documents
        for page in pdf_file.pages:
            page_tags = [tag.tag for tag in page.tags]
            
            # Create question documents
            for question in page.questions:
                question_hash = hashlib.sha256(question.question.encode()).hexdigest()[:16]
                question_docs.append({
                    "id": f"q-{page.id}-{question_hash}",
                    "question": question.question,
                    "tags": page_tags,
                    "page_id": page.id,
                    "pdf_id": pdf_file.id
                })
            
            # Create chunk documents
            for chunk in page.chunks:
                chunk_hash = hashlib.sha256(chunk.chunk.encode()).hexdigest()[:16]
                chunk_docs.append({
                    "id": f"c-{page.id}-{chunk_hash}",
                    "chunk": chunk.chunk,
                    "tags": page_tags,
                    "page_id": page.id,
                    "pdf_id": pdf_file.id
                })
        
        # Index documents in their respective indexes
        if question_docs:
            self.question_indexer.index_documents(question_docs)
        if chunk_docs:
            self.chunk_indexer.index_documents(chunk_docs)


def index(
    db: Database,
    question_index_name: str,
    chunk_index_name: str,
    embedding_model: str
) -> None:
    """Index all generated content into vector databases.
    
    Args:
        db: Database connection
        question_index_name: Name of the question index
        chunk_index_name: Name of the chunk index
        embedding_model: Model name for embeddings
    """
    indexer = DocumentIndexer(question_index_name, chunk_index_name, embedding_model)
    
    with db.session() as session:
        # Find files that have been generated but not yet indexed
        files = session.query(PdfFile).filter(
            PdfFile.generated == True,
            PdfFile.indexed == False
        ).all()
        
        for file in files:
            try:
                # Index all content from the file
                indexer.index_file(file)
                
                # Mark file as indexed
                file.indexed = True
                file.indexed_at = datetime.now()
                
                logging.info(f"Indexed: {file.filepath}")
                
            except Exception as e:
                logging.error(f"Failed to index {file.filepath}: {e}")
                session.rollback()
