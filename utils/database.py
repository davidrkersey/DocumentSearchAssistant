from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import os
from datetime import datetime

# Get database URL from environment
DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Create database engine
engine = create_engine(DATABASE_URL)
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
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
