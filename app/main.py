from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
from dotenv import load_dotenv
from sqlalchemy.orm import Session

from .database.models import init_db, get_db
from .services.candidate_service import CandidateService

# Load environment variables
load_dotenv()

# Initialize database
init_db()

app = FastAPI(title="PeopleGPT API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class SearchQuery(BaseModel):
    query: str
    filters: Optional[Dict[str, Any]] = None

class Candidate(BaseModel):
    id: str
    name: str
    skills: List[str]
    experience: str
    location: str
    score: float
    contact_info: Dict[str, Any]

class ScreeningAnswers(BaseModel):
    answers: List[str]

# Routes
@app.get("/")
async def root():
    return {"message": "Welcome to PeopleGPT API"}

@app.post("/search")
async def search_candidates(
    query: SearchQuery,
    db: Session = Depends(get_db)
):
    """
    Search for candidates based on natural language query
    """
    try:
        service = CandidateService(db)
        candidates = service.search_candidates(query.query, query.filters)
        return {
            "candidates": candidates,
            "total": len(candidates),
            "query": query.query
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/candidate/{candidate_id}")
async def get_candidate(
    candidate_id: str,
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific candidate
    """
    try:
        service = CandidateService(db)
        candidate = service.get_candidate(candidate_id)
        return candidate
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/candidate/{candidate_id}/screen")
async def screen_candidate(
    candidate_id: str,
    db: Session = Depends(get_db)
):
    """
    Perform AI-powered screening of a candidate
    """
    try:
        service = CandidateService(db)
        screening = service.screen_candidate(candidate_id)
        return screening
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/screening/{screening_id}/submit")
async def submit_screening_answers(
    screening_id: int,
    answers: ScreeningAnswers,
    db: Session = Depends(get_db)
):
    """
    Submit and evaluate screening answers
    """
    try:
        service = CandidateService(db)
        result = service.submit_screening_answers(screening_id, answers.answers)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 