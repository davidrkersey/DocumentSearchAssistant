from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, Float, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.pool import QueuePool
import os
from datetime import datetime
import time
from contextlib import contextmanager

# Get database URL from environment
DATABASE_URL = os.getenv('DATABASE_URL')
#DATABASE_URL = "postgresql://postgres:password@db:5432/mydatabase"

if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Create database engine with connection pooling and retry settings
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800,  # Recycle connections after 30 minutes
    pool_pre_ping=True  # Enable connection health checks
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    upload_date = Column(DateTime, default=datetime.utcnow)
    page_count = Column(Integer)
    search_results = relationship("SearchResult", back_populates="document")

class SearchResult(Base):
    __tablename__ = "search_results"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    search_term = Column(String, index=True)
    page_number = Column(Integer)
    excerpt = Column(Text)
    summary = Column(Text)
    document = relationship("Document", back_populates="search_results")

# Create all tables
Base.metadata.create_all(bind=engine)

def get_db():
    """Get database session with retry logic"""
    max_retries = 3
    retry_delay = 1  # seconds

    for attempt in range(max_retries):
        try:
            db = SessionLocal()
            # Test the connection with properly formatted SQL
            db.execute(text("SELECT 1"))
            yield db
        except Exception as e:
            if attempt == max_retries - 1:  # Last attempt
                raise Exception(f"Database connection failed after {max_retries} attempts: {str(e)}")
            time.sleep(retry_delay)
            retry_delay *= 2  # Exponential backoff
            continue
        finally:
            db.close()

@contextmanager
def get_db_context():
    """Context manager for database sessions with automatic cleanup"""
    db = next(get_db())
    try:
        yield db
    finally:
        db.close()