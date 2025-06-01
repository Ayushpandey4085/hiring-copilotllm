from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from ..database.models import Candidate, Screening, Outreach
from ..llm.ollama_client import OllamaClient
import uuid
import json

class CandidateService:
    def __init__(self, db: Session):
        self.db = db
        self.llm = OllamaClient()

    def search_candidates(self, query: str, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Search for candidates based on natural language query"""
        # First, use LLM to understand the query and extract search criteria
        search_criteria = self._parse_search_query(query)
        
        # Build database query
        db_query = self.db.query(Candidate)
        
        # Apply filters
        if filters:
            if filters.get("location"):
                db_query = db_query.filter(Candidate.location.ilike(f"%{filters['location']}%"))
            if filters.get("skills"):
                # Assuming skills is stored as JSON array
                for skill in filters["skills"]:
                    db_query = db_query.filter(Candidate.skills.contains(skill))
        
        # Get candidates
        candidates = db_query.all()
        
        # Use LLM to rank and score candidates
        ranked_candidates = self._rank_candidates(candidates, search_criteria)
        
        return ranked_candidates

    def _parse_search_query(self, query: str) -> Dict[str, Any]:
        """Use LLM to parse natural language query into structured search criteria"""
        prompt = f"""
        Parse the following recruitment query into structured search criteria:
        "{query}"
        
        Extract:
        1. Required skills
        2. Experience level
        3. Location preferences
        4. Employment type
        5. Any other relevant criteria
        """
        
        response = self.llm.generate_response(prompt)
        # TODO: Implement proper parsing of LLM response
        return {
            "skills": [],
            "experience_level": "",
            "location": "",
            "employment_type": ""
        }

    def _rank_candidates(self, candidates: List[Candidate], criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Rank candidates based on search criteria using LLM"""
        ranked = []
        for candidate in candidates:
            # Convert candidate to dict for LLM analysis
            candidate_data = {
                "name": candidate.name,
                "skills": candidate.skills,
                "experience": candidate.experience,
                "location": candidate.location
            }
            
            # Get LLM analysis
            analysis = self.llm.analyze_candidate(candidate_data)
            
            # Update candidate score
            candidate.score = analysis["fit_score"]
            self.db.commit()
            
            ranked.append({
                "id": candidate.id,
                "name": candidate.name,
                "skills": candidate.skills,
                "experience": candidate.experience,
                "location": candidate.location,
                "score": candidate.score
            })
        
        # Sort by score
        ranked.sort(key=lambda x: x["score"], reverse=True)
        return ranked

    def screen_candidate(self, candidate_id: str) -> Dict[str, Any]:
        """Perform AI-powered screening of a candidate"""
        candidate = self.db.query(Candidate).filter(Candidate.id == candidate_id).first()
        if not candidate:
            raise ValueError(f"Candidate {candidate_id} not found")
        
        # Generate screening questions
        questions = self.llm.generate_screening_questions({
            "skills": candidate.skills,
            "experience": candidate.experience
        })
        
        # Create screening record
        screening = Screening(
            candidate_id=candidate_id,
            questions=questions,
            answers=[],
            score=0.0
        )
        self.db.add(screening)
        self.db.commit()
        
        return {
            "candidate_id": candidate_id,
            "questions": questions,
            "screening_id": screening.id
        }

    def submit_screening_answers(self, screening_id: int, answers: List[str]) -> Dict[str, Any]:
        """Submit and evaluate screening answers"""
        screening = self.db.query(Screening).filter(Screening.id == screening_id).first()
        if not screening:
            raise ValueError(f"Screening {screening_id} not found")
        
        # Use LLM to evaluate answers
        prompt = f"""
        Evaluate the following screening answers:
        Questions: {json.dumps(screening.questions)}
        Answers: {json.dumps(answers)}
        
        Provide:
        1. Score (0-100)
        2. Detailed feedback
        3. Areas of strength
        4. Areas for improvement
        """
        
        evaluation = self.llm.generate_response(prompt)
        
        # Update screening record
        screening.answers = answers
        screening.score = 0.0  # TODO: Extract score from LLM response
        screening.feedback = evaluation
        self.db.commit()
        
        return {
            "screening_id": screening_id,
            "score": screening.score,
            "feedback": screening.feedback
        } 