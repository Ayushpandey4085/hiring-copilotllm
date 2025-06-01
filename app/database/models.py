from sqlalchemy import Column, Integer, String, Float, JSON, DateTime, create_engine, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import os
import uuid
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create SQLAlchemy base class
Base = declarative_base()

# Database URL from environment variable (PostgreSQL only)
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required")

# Create engine with PostgreSQL-specific configuration
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Enable connection health checks
    pool_recycle=300,    # Recycle connections every 5 minutes
    echo=False           # Set to True for SQL debugging
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phone = Column(String(50))
    location = Column(String(255), nullable=False)
    skills = Column(JSON, nullable=False)
    experience = Column(Text, nullable=False)  # Use Text for longer content
    education = Column(JSON)  # List of education entries
    resume_url = Column(String(500))
    linkedin_url = Column(String(500))
    github_url = Column(String(500))
    score = Column(Float, default=0.0)
    status = Column(String(50), default="new")  # new, screened, contacted, hired
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    candidate_metadata = Column(JSON, nullable=True)

    # Relationships
    screenings = relationship("Screening", back_populates="candidate", cascade="all, delete-orphan")
    outreach = relationship("Outreach", back_populates="candidate", cascade="all, delete-orphan")

class Screening(Base):
    __tablename__ = "screenings"

    id = Column(Integer, primary_key=True)
    candidate_id = Column(String, ForeignKey("candidates.id", ondelete="CASCADE"))
    questions = Column(JSON, nullable=False)
    answers = Column(JSON, nullable=True)
    score = Column(Float, default=0.0)
    feedback = Column(Text, nullable=True)  # Use Text for longer content
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    candidate = relationship("Candidate", back_populates="screenings")

class Outreach(Base):
    __tablename__ = "outreach"

    id = Column(Integer, primary_key=True)
    candidate_id = Column(String, ForeignKey("candidates.id", ondelete="CASCADE"))
    message = Column(Text, nullable=True)  # Use Text for longer content
    status = Column(String(50), nullable=False)  # sent, opened, replied
    response = Column(Text, nullable=True)  # Use Text for longer content
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    candidate = relationship("Candidate", back_populates="outreach")

# Create all tables
def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)

# Drop and recreate all tables (use with caution!)
def reset_db():
    """Drop and recreate all tables - USE WITH CAUTION!"""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

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

# Initialize database and sample data only if tables don't exist
def setup_database():
    """Setup database - creates tables and adds sample data if needed"""
    init_db()
    
    # Check if we need to add sample data
    db = SessionLocal()
    try:
        candidate_count = db.query(Candidate).count()
        if candidate_count == 0:
            init_sample_data()
    finally:
        db.close()

# Call setup on import
setup_database() 