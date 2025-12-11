"""
Job Analyzer - LLM-powered job description analysis.

Analyzes job descriptions to extract key skills, requirements, and cultural fit indicators.
"""

import json
import logging
from typing import Dict, List, Optional, Any

from runtime.shared.multi_provider_clients import get_client, Provider

logger = logging.getLogger(__name__)


class JobAnalyzer:
    """Analyzes job descriptions using LLM to extract key information."""
    
    def __init__(self, llm_client: Optional[Any] = None, provider: Optional[Provider] = None):
        """
        Initialize JobAnalyzer.
        
        Args:
            llm_client: Optional pre-configured LLM client
            provider: Provider to use if client not supplied (defaults to Google/Gemini)
        """
        self.llm_client = llm_client or get_client(provider or Provider.GOOGLE)
        self.provider = provider or Provider.GOOGLE
        
        if self.llm_client is None:
            raise ValueError(f"Failed to initialize LLM client for provider {self.provider}")
    
    def analyze(self, job_description: str) -> Dict[str, Any]:
        """
        Analyze a job description to extract key information.
        
        Args:
            job_description: Raw job description text
            
        Returns:
            Dictionary containing:
            - hard_skills: List of required hard skills
            - soft_skills: List of required soft skills
            - key_responsibilities: List of main responsibilities
            - experience_level: Required experience level
            - cultural_indicators: List of cultural fit keywords
            - north_star_metric: Key success metric for the role
        """
        prompt = self._build_analysis_prompt(job_description)
        
        try:
            # Generate analysis using Gemini
            if self.provider == Provider.GOOGLE:
                response = self._generate_with_gemini(prompt)
            else:
                # Fallback for other providers
                response = self._generate_with_generic_client(prompt)
            
            # Parse and return structured results
            return self._parse_analysis_response(response)
            
        except Exception as e:
            logger.error(f"Error analyzing job description: {e}")
            # Return fallback structure
            return {
                "hard_skills": [],
                "soft_skills": [],
                "key_responsibilities": [],
                "experience_level": "unknown",
                "cultural_indicators": [],
                "north_star_metric": "unknown",
                "error": str(e)
            }
    
    def _build_analysis_prompt(self, job_description: str) -> str:
        """Build the prompt for job analysis."""
        return f"""Analyze the following job description and extract key information. 

JOB DESCRIPTION:
{job_description}

Please extract and return a JSON object with the following structure:
{{
    "hard_skills": ["skill1", "skill2", "skill3", "skill4", "skill5"],
    "soft_skills": ["skill1", "skill2", "skill3"],
    "key_responsibilities": ["responsibility1", "responsibility2", "responsibility3"],
    "experience_level": "entry|mid|senior|lead|executive",
    "cultural_indicators": ["keyword1", "keyword2", "keyword3"],
    "north_star_metric": "Brief description of the key success metric for this role"
}}

Focus on the most important skills and requirements. Be specific and concise.
Return ONLY the JSON object, no additional text."""
    
    def _generate_with_gemini(self, prompt: str) -> str:
        """Generate response using Google Gemini."""
        import google.generativeai as genai
        
        # Configure model
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Generate response
        response = model.generate_content(prompt)
        return response.text
    
    def _generate_with_generic_client(self, prompt: str) -> str:
        """Generate response using generic client interface."""
        # Fallback for other providers
        if hasattr(self.llm_client, 'generate'):
            response = self.llm_client.generate(prompt)
            return response.text if hasattr(response, 'text') else str(response)
        else:
            # Try completion interface
            response = self.llm_client.complete(prompt)
            return response.text if hasattr(response, 'text') else str(response)
    
    def _parse_analysis_response(self, response: str) -> Dict[str, Any]:
        """Parse the LLM response into structured data."""
        try:
            # Clean response - remove any markdown formatting
            cleaned = response.strip()
            if cleaned.startswith('```json'):
                cleaned = cleaned[7:]
            if cleaned.endswith('```'):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()
            
            # Parse JSON
            parsed = json.loads(cleaned)
            
            # Validate and set defaults
            result = {
                "hard_skills": parsed.get("hard_skills", [])[:5],  # Limit to 5
                "soft_skills": parsed.get("soft_skills", [])[:3],  # Limit to 3
                "key_responsibilities": parsed.get("key_responsibilities", [])[:5],
                "experience_level": parsed.get("experience_level", "unknown"),
                "cultural_indicators": parsed.get("cultural_indicators", [])[:5],
                "north_star_metric": parsed.get("north_star_metric", "unknown")
            }
            
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.debug(f"Response content: {response}")
            # Return fallback structure
            return {
                "hard_skills": [],
                "soft_skills": [],
                "key_responsibilities": [],
                "experience_level": "unknown",
                "cultural_indicators": [],
                "north_star_metric": "unknown",
                "error": f"JSON parsing failed: {e}"
            }
    
    def extract_keywords(self, job_description: str, max_keywords: int = 20) -> List[str]:
        """
        Extract important keywords from job description.
        
        Args:
            job_description: Raw job description text
            max_keywords: Maximum number of keywords to return
            
        Returns:
            List of relevant keywords
        """
        # Simple keyword extraction as fallback
        import re
        
        # Common tech/role keywords to look for
        common_keywords = {
            'python', 'java', 'javascript', 'react', 'node', 'aws', 'azure', 'gcp',
            'sql', 'nosql', 'mongodb', 'postgresql', 'mysql', 'docker', 'kubernetes',
            'microservices', 'api', 'rest', 'graphql', 'machine learning', 'ai',
            'data science', 'analytics', 'leadership', 'agile', 'scrum', 'devops',
            'ci/cd', 'testing', 'unit testing', 'integration', 'frontend', 'backend',
            'full stack', 'mobile', 'ios', 'android', 'web', 'cloud', 'security'
        }
        
        # Find matches in text
        text_lower = job_description.lower()
        found_keywords = []
        
        for keyword in common_keywords:
            if keyword in text_lower:
                found_keywords.append(keyword)
                if len(found_keywords) >= max_keywords:
                    break
        
        return found_keywords
