from contextlib import contextmanager
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session


class Database:
    """Database connection manager for SQLAlchemy."""
    
    def __init__(self, db_url: str) -> None:
        """Initialize database connection.
        
        Args:
            db_url: Database connection URL
        """
        self.engine = create_engine(db_url, future=True)
        self.SessionLocal = sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            future=True
        )

    @contextmanager
    def session(self) -> Generator[Session, None, None]:
        """Context manager for database sessions.
        
        Yields:
            Database session instance
            
        Raises:
            Exception: Any exception that occurs during session usage
        """
        db = self.SessionLocal()
        try:
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()
