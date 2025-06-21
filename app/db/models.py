from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    func
)
from sqlalchemy.orm import declarative_base, relationship
from typing import List, Optional
from datetime import datetime

Base = declarative_base()


class PdfFile(Base):
    """Model representing a PDF file in the database."""
    
    __tablename__ = 'pdf_files'

    id: int = Column(Integer, primary_key=True)
    filepath: str = Column(String, unique=True, index=True)

    # Processing status flags
    extracted: bool = Column(Boolean, default=False)
    extracted_at: Optional[datetime] = Column(DateTime, nullable=True)

    generated: bool = Column(Boolean, default=False)
    generated_at: Optional[datetime] = Column(DateTime, nullable=True)

    indexed: bool = Column(Boolean, default=False)
    indexed_at: Optional[datetime] = Column(DateTime, nullable=True)

    created_at: datetime = Column(DateTime, default=func.now())

    # Relationships
    pages: List['PdfPages'] = relationship("PdfPages", back_populates="file")
    questions: List['PageQuestions'] = relationship("PageQuestions", back_populates="file")
    tags: List['PageTags'] = relationship("PageTags", back_populates="file")
    chunks: List['PageChunks'] = relationship("PageChunks", back_populates="file")


class PdfPages(Base):
    """Model representing individual pages of a PDF file."""
    
    __tablename__ = 'pdf_pages'

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    file_id: int = Column(Integer, ForeignKey('pdf_files.id'), index=True)
    page_number: int = Column(Integer)
    page_text: str = Column(Text)
    created_at: datetime = Column(DateTime, default=func.now())

    __table_args__ = (
        UniqueConstraint('file_id', 'page_number', name='uq_file_page'),
    )

    # Relationships
    file: PdfFile = relationship("PdfFile", back_populates="pages")
    questions: List['PageQuestions'] = relationship("PageQuestions", back_populates="page")
    tags: List['PageTags'] = relationship("PageTags", back_populates="page")
    chunks: List['PageChunks'] = relationship("PageChunks", back_populates="page")


class PageQuestions(Base):
    """Model representing questions extracted from PDF pages."""
    
    __tablename__ = 'page_questions'
    
    id: int = Column(Integer, primary_key=True)
    page_id: int = Column(Integer, ForeignKey('pdf_pages.id'))
    file_id: int = Column(Integer, ForeignKey('pdf_files.id'))

    question: str = Column(String)
    
    # Relationships
    page: PdfPages = relationship("PdfPages", back_populates="questions")
    file: PdfFile = relationship("PdfFile", back_populates="questions")


class PageTags(Base):
    """Model representing tags extracted from PDF pages."""
    
    __tablename__ = 'page_tags'
    
    id: int = Column(Integer, primary_key=True)
    page_id: int = Column(Integer, ForeignKey('pdf_pages.id'))
    file_id: int = Column(Integer, ForeignKey('pdf_files.id'))

    tag: str = Column(String)
    
    # Relationships
    page: PdfPages = relationship("PdfPages", back_populates="tags")
    file: PdfFile = relationship("PdfFile", back_populates="tags")


class PageChunks(Base):
    """Model representing text chunks extracted from PDF pages."""
    
    __tablename__ = 'page_chunks'
    
    id: int = Column(Integer, primary_key=True)
    page_id: int = Column(Integer, ForeignKey('pdf_pages.id'))
    file_id: int = Column(Integer, ForeignKey('pdf_files.id'))

    chunk: str = Column(String)
    
    # Relationships
    page: PdfPages = relationship("PdfPages", back_populates="chunks")
    file: PdfFile = relationship("PdfFile", back_populates="chunks")


class QueryRetreivals(Base):
    """Model for storing query retrieval history."""
    
    __tablename__ = 'query_retreival'
    
    id: int = Column(Integer, primary_key=True)
    
    query: str = Column(String)
    created_at: datetime = Column(DateTime, default=func.now())


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
#     page = relationship("PdfPages", back_populates="steps")
#     file = relationship("PdfFile", back_populates="processing_steps")