import requests
import json
from typing import Dict, List, Any
import os

class OllamaClient:
    def __init__(self):
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.model = "llama2"  # Default model, can be changed based on requirements

    def _make_request(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make a request to the Ollama API"""
        try:
            response = requests.post(
                f"{self.base_url}/{endpoint}",
                json=data,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error communicating with Ollama: {str(e)}")

    def generate_response(self, prompt: str, system_prompt: str = None) -> str:
        """Generate a response from the LLM"""
        data = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }
        if system_prompt:
            data["system"] = system_prompt

        response = self._make_request("api/generate", data)
        return response.get("response", "")

    def analyze_candidate(self, candidate_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze candidate data and extract relevant information"""
        prompt = f"""
        Analyze the following candidate data and extract key information:
        {json.dumps(candidate_data, indent=2)}
        
        Please provide:
        1. Key skills and expertise
        2. Experience level
        3. Location preferences
        4. Availability
        5. Potential fit score (0-100)
        """

        system_prompt = """
        You are an expert recruiter and talent analyst. Your task is to analyze candidate data
        and extract relevant information for recruitment purposes. Be precise and objective in your analysis.
        """

        response = self.generate_response(prompt, system_prompt)
        return self._parse_analysis(response)

    def _parse_analysis(self, response: str) -> Dict[str, Any]:
        """Parse the LLM response into structured data"""
        # TODO: Implement proper parsing logic
        # This is a placeholder implementation
        return {
            "skills": [],
            "experience_level": "",
            "location": "",
            "availability": "",
            "fit_score": 0
        }

    def generate_screening_questions(self, candidate_data: Dict[str, Any]) -> List[str]:
        """Generate relevant screening questions for a candidate"""
        prompt = f"""
        Based on the following candidate profile, generate 5 relevant technical screening questions:
        {json.dumps(candidate_data, indent=2)}
        
        Focus on their key skills and experience areas.
        """

        system_prompt = """
        You are an expert technical interviewer. Generate relevant and challenging
        questions that will help assess the candidate's expertise in their domain.
        """

        response = self.generate_response(prompt, system_prompt)
        return self._parse_questions(response)

    def _parse_questions(self, response: str) -> List[str]:
        """Parse the LLM response into a list of questions"""
        # TODO: Implement proper parsing logic
        # This is a placeholder implementation
        return response.split("\n") 