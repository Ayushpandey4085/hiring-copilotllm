from sqlalchemy.orm import Session
from .models import Candidate, Screening, Outreach
import json

def init_sample_data(db: Session):
    """Initialize database with sample data"""
    # Sample candidates
    candidates = [
        {
            "id": "1",
            "name": "John Doe",
            "email": "john.doe@example.com",
            "phone": "+1-555-0123",
            "location": "New York, NY",
            "skills": ["Python", "FastAPI", "React", "AWS"],
            "experience": "Senior Full Stack Developer with 5 years of experience",
            "education": [
                {
                    "degree": "Bachelor of Science in Computer Science",
                    "institution": "New York University",
                    "year": 2018
                }
            ],
            "resume_url": "https://example.com/resumes/john-doe.pdf",
            "linkedin_url": "https://linkedin.com/in/johndoe",
            "github_url": "https://github.com/johndoe",
            "score": 0.0,
            "status": "new"
        },
        {
            "id": "2",
            "name": "Jane Smith",
            "email": "jane.smith@example.com",
            "phone": "+1-555-0124",
            "location": "San Francisco, CA",
            "skills": ["Java", "Spring Boot", "Kubernetes", "Docker"],
            "experience": "Backend Developer with 3 years of experience",
            "education": [
                {
                    "degree": "Master of Science in Software Engineering",
                    "institution": "Stanford University",
                    "year": 2020
                }
            ],
            "resume_url": "https://example.com/resumes/jane-smith.pdf",
            "linkedin_url": "https://linkedin.com/in/janesmith",
            "github_url": "https://github.com/janesmith",
            "score": 0.0,
            "status": "new"
        },
        {
            "id": "3",
            "name": "Mike Johnson",
            "email": "mike.johnson@example.com",
            "phone": "+1-555-0125",
            "location": "Seattle, WA",
            "skills": ["JavaScript", "React", "Node.js", "MongoDB"],
            "experience": "Frontend Developer with 4 years of experience",
            "education": [
                {
                    "degree": "Bachelor of Science in Information Technology",
                    "institution": "University of Washington",
                    "year": 2019
                }
            ],
            "resume_url": "https://example.com/resumes/mike-johnson.pdf",
            "linkedin_url": "https://linkedin.com/in/mikejohnson",
            "github_url": "https://github.com/mikejohnson",
            "score": 0.0,
            "status": "new"
        }
    ]

    # Add candidates to database
    for candidate_data in candidates:
        candidate = Candidate(**candidate_data)
        db.add(candidate)

    # Commit changes
    db.commit() 