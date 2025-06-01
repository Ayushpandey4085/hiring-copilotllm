import google.generativeai as genai
import json
import re
from typing import Dict, List, Any
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class GeminiClient:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is required")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        
        # Use Gemini Flash model (updated model name)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Generation config for better responses
        self.generation_config = {
            'temperature': 0.7,
            'top_p': 0.8,
            'top_k': 40,
            'max_output_tokens': 2048,
        }

    def generate_response(self, prompt: str, system_prompt: str = None) -> str:
        """Generate a response from Gemini"""
        try:
            # Combine system prompt with user prompt if provided
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"
            
            response = self.model.generate_content(
                full_prompt,
                generation_config=self.generation_config
            )
            
            return response.text if response.text else ""
        
        except Exception as e:
            raise Exception(f"Error communicating with Gemini: {str(e)}")

    def analyze_candidate(self, candidate_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze candidate data and extract relevant information"""
        prompt = f"""
        Analyze the following candidate data and extract key information:
        {json.dumps(candidate_data, indent=2)}
        
        Please provide a JSON response with:
        1. "skills": List of key skills and expertise
        2. "experience_level": Experience level (Junior/Mid/Senior/Lead)
        3. "location": Location or location preference
        4. "availability": Availability status
        5. "fit_score": Potential fit score (0-100)
        6. "summary": Brief summary of the candidate
        
        Format your response as valid JSON only.
        """

        system_prompt = """
        You are an expert recruiter and talent analyst. Your task is to analyze candidate data
        and extract relevant information for recruitment purposes. Be precise and objective in your analysis.
        Always respond with valid JSON format.
        """

        response = self.generate_response(prompt, system_prompt)
        return self._parse_analysis(response)

    def _parse_analysis(self, response: str) -> Dict[str, Any]:
        """Parse the Gemini response into structured data"""
        try:
            # Try to extract JSON from the response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                return json.loads(json_str)
        except (json.JSONDecodeError, AttributeError):
            pass
        
        # Fallback if JSON parsing fails
        return {
            "skills": self._extract_list_from_text(response, "skills"),
            "experience_level": "Mid",
            "location": "Remote",
            "availability": "Available",
            "fit_score": 75,
            "summary": response[:200] + "..." if len(response) > 200 else response
        }

    def generate_screening_questions(self, candidate_data: Dict[str, Any]) -> List[str]:
        """Generate relevant screening questions for a candidate"""
        prompt = f"""
        Based on the following candidate profile, generate 5 relevant technical screening questions:
        {json.dumps(candidate_data, indent=2)}
        
        Focus on their key skills and experience areas.
        
        Format: Return each question on a new line, numbered 1-5.
        Make questions specific to their expertise and challenging but fair.
        """

        system_prompt = """
        You are an expert technical interviewer. Generate relevant and challenging
        questions that will help assess the candidate's expertise in their domain.
        Focus on practical knowledge and problem-solving abilities.
        """

        response = self.generate_response(prompt, system_prompt)
        return self._parse_questions(response)

    def _parse_questions(self, response: str) -> List[str]:
        """Parse the Gemini response into a list of questions"""
        # Split by lines and filter out empty lines
        lines = [line.strip() for line in response.split('\n') if line.strip()]
        
        questions = []
        for line in lines:
            # Remove numbering if present (1., 2., etc.)
            cleaned_line = re.sub(r'^\d+\.?\s*', '', line)
            if cleaned_line and len(cleaned_line) > 10:  # Ensure it's a substantial question
                questions.append(cleaned_line)
        
        # Return up to 5 questions
        return questions[:5] if questions else [
            "Tell me about your experience with the technologies mentioned in your profile.",
            "Describe a challenging project you've worked on recently.",
            "How do you approach problem-solving in your field?",
            "What are your preferred tools and methodologies?",
            "Where do you see yourself growing in the next 2-3 years?"
        ]

    def _extract_list_from_text(self, text: str, key: str) -> List[str]:
        """Helper method to extract lists from text responses"""
        # Simple extraction for skills, can be enhanced
        if "skills" in key.lower():
            # Look for common skill patterns
            skills = []
            words = text.split()
            tech_keywords = ['Python', 'JavaScript', 'Java', 'React', 'Node.js', 'AWS', 'Docker', 'Kubernetes']
            for word in words:
                if word in tech_keywords:
                    skills.append(word)
            return skills[:10]  # Limit to 10 skills
        return []

    def evaluate_screening_answers(self, questions: List[str], answers: List[str]) -> Dict[str, Any]:
        """Evaluate screening answers and provide feedback"""
        prompt = f"""
        Evaluate the following screening interview:
        
        Questions and Answers:
        {chr(10).join([f"Q{i+1}: {q}{chr(10)}A{i+1}: {a}{chr(10)}" for i, (q, a) in enumerate(zip(questions, answers))])}
        
        Please provide a JSON response with:
        1. "overall_score": Overall score (0-100)
        2. "individual_scores": List of scores for each question (0-100)
        3. "strengths": List of candidate's strengths
        4. "weaknesses": List of areas for improvement
        5. "recommendation": Hiring recommendation (Hire/Maybe/Pass)
        6. "feedback": Detailed feedback summary
        
        Format your response as valid JSON only.
        """

        system_prompt = """
        You are an expert technical interviewer evaluating candidate responses.
        Be fair, objective, and constructive in your evaluation.
        Consider technical accuracy, communication skills, and problem-solving approach.
        """

        response = self.generate_response(prompt, system_prompt)
        
        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass
        
        # Fallback response
        return {
            "overall_score": 75,
            "individual_scores": [75] * len(questions),
            "strengths": ["Good communication", "Technical knowledge"],
            "weaknesses": ["Could provide more specific examples"],
            "recommendation": "Maybe",
            "feedback": "Candidate shows promise but needs further evaluation."
        } 