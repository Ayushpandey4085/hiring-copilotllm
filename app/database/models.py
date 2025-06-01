from sqlalchemy import Column, Integer, String, Float, JSON, DateTime, create_engine, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create SQLAlchemy base class
Base = declarative_base()

# Database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./peoplegpt.db")

# Create engine and session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone = Column(String)
    location = Column(String, nullable=False)
    skills = Column(JSON, nullable=False)
    experience = Column(String, nullable=False)
    education = Column(JSON)  # List of education entries
    resume_url = Column(String)
    linkedin_url = Column(String)
    github_url = Column(String)
    score = Column(Float, default=0.0)
    status = Column(String, default="new")  # new, screened, contacted, hired
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    candidate_metadata = Column(JSON, nullable=True)

    # Relationships
    screenings = relationship("Screening", back_populates="candidate")
    outreach = relationship("Outreach", back_populates="candidate")

class Screening(Base):
    __tablename__ = "screenings"

    id = Column(Integer, primary_key=True)
    candidate_id = Column(String, ForeignKey("candidates.id"))
    questions = Column(JSON, nullable=False)
    answers = Column(JSON, nullable=True)
    score = Column(Float, default=0.0)
    feedback = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    candidate = relationship("Candidate", back_populates="screenings")

class Outreach(Base):
    __tablename__ = "outreach"

    id = Column(Integer, primary_key=True)
    candidate_id = Column(String, ForeignKey("candidates.id"))
    message = Column(String, nullable=True)
    status = Column(String, nullable=False)  # sent, opened, replied
    response = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    candidate = relationship("Candidate", back_populates="outreach")

# Create all tables
def init_db():
    Base.metadata.drop_all(bind=engine)  # Drop all tables
    Base.metadata.create_all(bind=engine)  # Create all tables

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize database with sample data
def init_sample_data():
    from .init_data import init_sample_data
    db = SessionLocal()
    try:
        init_sample_data(db)
    finally:
        db.close()

# Initialize database and sample data
init_db()
init_sample_data() 