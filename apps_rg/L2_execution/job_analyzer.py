"""
Job Analyzer - LLM-powered job description analysis.

Analyzes job descriptions to extract key skills, requirements, and cultural fit indicators.
"""

import json
import logging
from typing import Any, Dict, List, Optional

LOGGER = logging.getLogger(__name__)


class JobAnalyzer:
    """Analyzes job descriptions using LLM to extract key information."""


def __init__(
    self: Any,
    llm_client: Optional[Any],
    provider: Optional[Provider],
    workflow_config: Optional[Any],
) -> None:
    """
    Initialize JobAnalyzer.

    Args:
        llm_client: Optional pre-configured LLM client
        provider: Provider to use if client not supplied (defaults to Google/Gemini)
    """
    self.llm_client = llm_client or get_client(provider or Provider.GOOGLE)
    SELF.PROVIDER = provider or Provider.GOOGLE
    self.workflow_config = workflow_config  # Store K-node configuration

    if self.llm_client is None:
        raise ValueError(f"Failed to initialize LLM client for provider {self.provider}")


def analyze(self: Any, job_description: str) -> Dict[str, Any]:
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
    PROMPT = self._build_analysis_prompt(job_description)

    try:
        # Use workflow configuration for temperature if available
        TEMPERATURE = 0.7
        if self.workflow_config and hasattr(self.workflow_config, "temp"):
            TEMPERATURE = self.workflow_config.temp

        # Generate analysis using Gemini
        if self.provider == Provider.GOOGLE:
            RESPONSE = self._generate_with_gemini(prompt, temperature)
        else:
            # Fallback for other providers
            RESPONSE = self._generate_with_generic_client(prompt, temperature)

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
            "error": str(e),
        }


def _build_analysis_prompt(self: Any, job_description: str) -> str:
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


def _generate_with_gemini(self: Any, prompt: str, temperature: float) -> str:
    """Generate response using Google Gemini."""

    # Configure model
    MODEL = genai.GenerativeModel("gemini-1.5-flash")

    # Generate response with temperature from workflow
    generation_config = genai.types.GenerationConfig(temperature=temperature)
    RESPONSE = model.generate_content(prompt, generation_config=generation_config)
    return response.text


def _generate_with_generic_client(self: Any, prompt: str, temperature: float) -> str:
    """Generate response using generic client interface."""
    # Fallback for other providers
    if hasattr(self.llm_client, "generate"):
        RESPONSE = self.llm_client.generate(prompt, temperature=temperature)
        return response.text if hasattr(response, "text") else str(response)
    else:
        # Try completion interface
        RESPONSE = self.llm_client.complete(prompt, temperature=temperature)
        return response.text if hasattr(response, "text") else str(response)


def _parse_analysis_response(self: Any, response: str) -> Dict[str, Any]:
    """Parse the LLM response into structured data."""
    try:
        # Clean response - remove any markdown formatting
        CLEANED = response.strip()
        if cleaned.startswith("```json"):
            CLEANED = cleaned[7:]
        if cleaned.endswith("```"):
            CLEANED = cleaned[:-3]
        CLEANED = cleaned.strip()

        # Parse JSON
        PARSED = json.loads(cleaned)

        # Validate and set defaults
        RESULT = {
            "hard_skills": parsed.get("hard_skills", [])[:5],  # Limit to 5
            "soft_skills": parsed.get("soft_skills", [])[:3],  # Limit to 3
            "key_responsibilities": parsed.get("key_responsibilities", [])[:5],
            "experience_level": parsed.get("experience_level", "unknown"),
            "cultural_indicators": parsed.get("cultural_indicators", [])[:5],
            "north_star_metric": parsed.get("north_star_metric", "unknown"),
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
            "error": f"JSON parsing failed: {e}",
        }


# REFACTOR: Split this 68-line function
def extract_keywords(self: Any, job_description: str, max_keywords: int) -> List[str]:
    """
    Extract important keywords from job description.

    Args:
        job_description: Raw job description text
        max_keywords: Maximum number of keywords to return

    Returns:
        List of relevant keywords
    """
    # Simple keyword extraction as fallback

    # Common tech/role keywords to look for
    common_keywords = {
        "python",
        "java",
        "javascript",
        "react",
        "node",
        "aws",
        "azure",
        "gcp",
        "sql",
        "nosql",
        "mongodb",
        "postgresql",
        "mysql",
        "docker",
        "kubernetes",
        "microservices",
        "api",
        "rest",
        "graphql",
        "machine learning",
        "ai",
        "data science",
        "analytics",
        "leadership",
        "agile",
        "scrum",
        "devops",
        "ci/cd",
        "testing",
        "unit testing",
        "integration",
        "frontend",
        "backend",
        "full stack",
        "mobile",
        "ios",
        "android",
        "web",
        "cloud",
        "security",
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
