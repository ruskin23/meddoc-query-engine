import pinecone
from datetime import datetime

from app.core.embedding import EmbeddingService
from app.core.indexing import PineconeIndexer
from app.db.base import Database
from app.db.models import PdfFile

from app.hierarchical_rag.indexer import IndexDocuments

def get_indexer(client, name, embed):
    index = client.Index(name)
    indexer = PineconeIndexer(index, embed)
    return IndexDocuments(indexer)

def index_pdfs(db: Database, 
               question_index_name: str, 
               chunk_index_name: str, 
               embedding_model: str):
    
    pinecone_client = pinecone.Pinecone()
    embedding_service = EmbeddingService(model=embedding_model)
    
    question_indexer = get_indexer(pinecone_client, question_index_name, embedding_service)
    chunk_indexer = get_indexer(pinecone_client, chunk_index_name, embedding_service)
        
    question_docs = []
    chunk_docs = []

    with db.session() as session:
        pdfs = session.query(PdfFile).filter_by(indexed=False).all()
        
        for pdf in pdfs:
            pages = pdf.pages
            
            for page in pages:
                questions = page.questions
                tags = page.tags
                chunks = page.chunks
                
                for question in questions:
                    question_docs.append({
                        'question': question,
                        'tags': tags,
                        'page_id': page.id,
                        'pdf_id': pdf.id
                    })

                for chunk in chunks:
                    chunk_docs.append({
                        'chunk': chunk,
                        'tags': tags,
                        'page_id': page.id,
                        'pdf_id': pdf.id
                    })

        question_indexer.index_questions(question_docs)
        chunk_indexer.index_chunks(chunk_docs)

        for pdf in pdfs:
            pdf.indexed = True
            pdf.indexed_at = datetime.now(datetime.now())
