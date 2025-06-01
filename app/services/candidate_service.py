from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from ..database.models import Candidate, Screening, Outreach
from ..llm.gemini_client import GeminiClient
import uuid
import json

class CandidateService:
    def __init__(self, db: Session):
        self.db = db
        self.llm = GeminiClient()

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
        
        Provide a JSON response with:
        1. "required_skills": List of required technical skills
        2. "experience_level": Experience level (Junior/Mid/Senior/Lead)
        3. "location": Location preferences
        4. "employment_type": Employment type (Full-time/Contract/Part-time)
        5. "domain": Domain/Industry preferences
        
        Format your response as valid JSON only.
        """
        
        system_prompt = """
        You are an expert recruitment analyst. Parse natural language job requirements 
        into structured search criteria. Be precise and extract only the explicitly mentioned requirements.
        """
        
        response = self.llm.generate_response(prompt, system_prompt)
        
        try:
            # Try to parse JSON response
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass
        
        # Fallback parsing
        return {
            "required_skills": [],
            "experience_level": "Mid",
            "location": "",
            "employment_type": "Full-time",
            "domain": ""
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
                "location": candidate.location,
                "education": candidate.education
            }
            
            # Get LLM analysis
            analysis = self.llm.analyze_candidate(candidate_data)
            
            # Update candidate score
            fit_score = analysis.get("fit_score", 75)
            candidate.score = fit_score
            self.db.commit()
            
            ranked.append({
                "id": candidate.id,
                "name": candidate.name,
                "skills": candidate.skills,
                "experience": candidate.experience,
                "location": candidate.location,
                "score": fit_score,
                "analysis": analysis
            })
        
        # Sort by score
        ranked.sort(key=lambda x: x["score"], reverse=True)
        return ranked

    def get_candidate(self, candidate_id: str) -> Dict[str, Any]:
        """Get detailed candidate information"""
        candidate = self.db.query(Candidate).filter(Candidate.id == candidate_id).first()
        if not candidate:
            raise ValueError(f"Candidate {candidate_id} not found")
        
        return {
            "id": candidate.id,
            "name": candidate.name,
            "email": candidate.email,
            "phone": candidate.phone,
            "location": candidate.location,
            "skills": candidate.skills,
            "experience": candidate.experience,
            "education": candidate.education,
            "resume_url": candidate.resume_url,
            "linkedin_url": candidate.linkedin_url,
            "github_url": candidate.github_url,
            "score": candidate.score,
            "status": candidate.status,
            "created_at": candidate.created_at.isoformat(),
            "updated_at": candidate.updated_at.isoformat()
        }

    def screen_candidate(self, candidate_id: str) -> Dict[str, Any]:
        """Perform AI-powered screening of a candidate"""
        candidate = self.db.query(Candidate).filter(Candidate.id == candidate_id).first()
        if not candidate:
            raise ValueError(f"Candidate {candidate_id} not found")
        
        # Generate screening questions
        questions = self.llm.generate_screening_questions({
            "skills": candidate.skills,
            "experience": candidate.experience,
            "education": candidate.education
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
        
        # Use Gemini to evaluate answers
        evaluation = self.llm.evaluate_screening_answers(screening.questions, answers)
        
        # Update screening record
        screening.answers = answers
        screening.score = evaluation.get("overall_score", 0.0)
        screening.feedback = evaluation.get("feedback", "")
        self.db.commit()
        
        return {
            "screening_id": screening_id,
            "overall_score": screening.score,
            "individual_scores": evaluation.get("individual_scores", []),
            "strengths": evaluation.get("strengths", []),
            "weaknesses": evaluation.get("weaknesses", []),
            "recommendation": evaluation.get("recommendation", ""),
            "feedback": screening.feedback
        } 