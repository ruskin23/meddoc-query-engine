from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    Index,
    func
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class PdfFile(Base):
    __tablename__ = 'pdf_files'

    id = Column(Integer, primary_key=True)
    filepath = Column(String, unique=True, index=True)

    extracted = Column(Boolean, default=False)
    extracted_at = Column(DateTime, nullable=True)

    indexed = Column(Boolean, default=False)
    indexed_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=func.now())

    # Relationships
    pages = relationship("PdfPage", back_populates="file")
    questions = relationship("PageQuestions", back_populates="file")
    tags = relationship("PageTags", back_populates="file")
    chunks = relationship("PageChunks", back_populates="file")


class PdfPages(Base):
    __tablename__ = 'pdf_pages'

    id = Column(Integer, primary_key=True, autoincrement=True)
    file_id = Column(Integer, ForeignKey('pdf_files.id'), index=True)
    page_number = Column(Integer)
    page_text = Column(Text)
    created_at = Column(DateTime, default=func.now())

    __table_args__ = (
        UniqueConstraint('file_id', 'page_number', name='uq_file_page'),
    )

    # Relationships
    file = relationship("PdfFile", back_populates="page")
    questions = relationship("PageQuestions", back_populates="page")
    tags = relationship("PageTags", back_populates="page")
    chunks = relationship("PageChunks", back_populates="page")

class PageQuestions(Base):
    __tablename__ = 'page_questions'
    
    id = Column(Integer, primary_key=True)
    page_id = Column(Integer, ForeignKey('pdf_pages.id'))
    file_id = Column(Integer, ForeignKey('pdf_files.id'))

    question = Column(String)
    
    # Relationships
    page = relationship("PdfPage", back_populates="questions")
    file = relationship("PdfFile", back_populates="questions")


class PageTags(Base):
    __tablename__ = 'page_tags'
    
    id = Column(Integer, primary_key=True)
    page_id = Column(Integer, ForeignKey('pdf_pages.id'))
    file_id = Column(Integer, ForeignKey('pdf_files.id'))

    tag = Column(String)
    
    # Relationships
    page = relationship("PdfPage", back_populates="tags")
    file = relationship("PdfFile", back_populates="tags")

class PageChunks(Base):
    __tablename__ = 'page_chunks'
    
    id = Column(Integer, primary_key=True)
    page_id = Column(Integer, ForeignKey('pdf_pages.id'))
    file_id = Column(Integer, ForeignKey('pdf_files.id'))

    chunk = Column(String)
    
    # Relationships
    page = relationship("PdfPage", back_populates="chunks")
    file = relationship("PdfFile", back_populates="chunks")


class PageChunks(Base):
    __tablename__ = 'page_chunks'
    
    id = Column(Integer, primary_key=True)
    page_id = Column(Integer, ForeignKey('pdf_pages.id'))
    file_id = Column(Integer, ForeignKey('pdf_files.id'))

    chunk = Column(String)
    
    # Relationships
    page = relationship("PdfPage", back_populates="chunks")
    file = relationship("PdfFile", back_populates="chunks")

class QueryRetreivals(Base):
    __tablename__ = 'query_retreival'
    
    id = Column(Integer, primary_key=True)
    
    query = Column(String)
    created_at = Column(DateTime, default=func.now())


# class ProcessingStep(Base):
#     __tablename__ = 'processing_steps'

#     id = Column(Integer, primary_key=True)
#     page_id = Column(Integer, ForeignKey('pdf_pages.id'))
#     file_id = Column(Integer, ForeignKey('pdf_files.id'))

#     step_name = Column(String)      # e.g., 'chunking', 'qa', 'tagging'
#     status = Column(String)         # e.g., 'pending', 'complete', 'failed'
#     error_message = Column(Text, nullable=True)

#     created_at = Column(DateTime, default=func.now())
#     completed_at = Column(DateTime, nullable=True)

#     __table_args__ = (
#         Index('ix_page_step', 'page_id', 'step_name'),
#     )

#     # Relationships
#     page = relationship("PdfPage", back_populates="steps")
#     file = relationship("PdfFile", back_populates="processing_steps")