import json
import time
from typing import Dict, Any, Optional, List

# --- MOCK TOOL WRAPPERS & UTILITIES ---

def get_current_time(timezone: Optional[str] = None) -> str:
    """Mock for Time MCP: Returns current time or converts timezone."""
    if timezone == "Europe/London":
        return '{"datetime": "2025-12-15T10:45:00+00:00"}'
    return '{"datetime": "2025-12-15T05:45:00-05:00"}'

def convert_time(source_timezone: str, time: str, target_timezone: str) -> str:
    """Mock for Time MCP: Converts time between timezones."""
    return '{"target": {"datetime": "2025-12-15T12:00:00+09:00"}}' # Example conversion

def issues_get_detail(issue_id: str) -> str:
    """Mock for GitKraken MCP: Retrieves details for an issue."""
    return f'{{"file_path": "src/config.js", "description": "High-priority bug {issue_id}"}}'

def browser_navigate(url: str) -> None:
    """Mock for Playwright MCP: Navigate to URL."""
    pass

def browser_type(element: str, ref: str, text: str) -> None:
    """Mock for Playwright MCP: Type text into element."""
    pass

def browser_click(element: str, ref: str) -> None:
    """Mock for Playwright MCP: Click element."""
    pass

def string_get(key: str) -> Optional[str]:
    """Mock for Redis MCP: Get string value."""
    # Simulate Redis cache miss
    return None

def string_set(key: str, value: str) -> None:
    """Mock for Redis MCP: Set string value."""
    pass

def search_nodes(query: str) -> str:
    """Mock for MEMemory MCP: Search knowledge graph."""
    # Return mock user data
    return json.dumps({
        "entityName": "user",
        "skills": ["Python", "JavaScript", "Machine Learning"],
        "projects": ["E-commerce Platform", "ML Pipeline"],
        "experience": "5 years"
    })

def search_records(query: str, index: str, top_k: int = 5) -> str:
    """Mock for Pinecone MCP: Search vector database."""
    # Return mock keywords based on query
    if "keywords" in query.lower():
        mock_keywords = [
            {"keyword": "React", "score": 0.95},
            {"keyword": "TypeScript", "score": 0.90},
            {"keyword": "AWS", "score": 0.85},
            {"keyword": "Docker", "score": 0.80},
            {"keyword": "GraphQL", "score": 0.75}
        ]
        return json.dumps(mock_keywords)
    return json.dumps([{"text": "Default search result"}])

def write_file(path: str, content: str) -> None:
    """Mock for Filesystem MCP: Write file."""
    # Ensure directory exists
    if "drafts/" in path and not hasattr(write_file, 'drafts_created'):
        write_file.drafts_created = True
    elif "reports/" in path and not hasattr(write_file, 'reports_created'):
        write_file.reports_created = True

def add_observations(observations: List[Dict[str, Any]]) -> None:
    """Mock for MEMemory MCP: Add observations."""
    pass

def semantic_score_draft(draft_content: str, job_description: str) -> float:
    """
    CRITICAL Utility: Simulates the LLM's semantic analysis score (L3/L5) 
    by comparing the draft to the JD. Score is between 0.0 and 1.0.
    """
    # Simple mock logic: score improves with each attempt
    if "Iteration 1" in draft_content: 
        return 0.70
    elif "Iteration 2" in draft_content: 
        return 0.85
    elif "Iteration 3" in draft_content: 
        return 0.95
    elif "Iteration 4" in draft_content: 
        return 0.98
    else:
        return 0.60 

def generate_draft_llm(draft_type: str, user_data: Dict, job_desc: str, current_draft: Optional[str] = None, required_keywords: Optional[list] = None) -> str:
    """
    Mock for LLM/Thinking Node: Generates or refines the draft based on input context.
    """
    iteration = current_draft.count("Iteration") + 1 if current_draft else 1
    
    # Build draft content
    draft_lines = [
        f"{draft_type} Draft - Iteration {iteration}",
        f"Generated for job description: {job_desc[:50]}...",
        f"User skills: {', '.join(user_data.get('skills', []))}",
        f"User projects: {', '.join(user_data.get('projects', []))}"
    ]
    
    if required_keywords:
        draft_lines.append(f"Target keywords: {', '.join(required_keywords[:3])}")
    
    return "\n".join(draft_lines)

# --- ERROR HANDLING UTILITIES ---

class MCPError(Exception):
    """Base exception for MCP-related errors."""
    pass

class CircuitBreakerOpenError(MCPError):
    """Raised when circuit breaker is open."""
    pass

def retry_with_backoff(func, max_retries: int = 3, base_delay: float = 1.0):
    """
    Retry decorator for MCP calls with exponential backoff.
    """
    def wrapper(*args, **kwargs):
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                delay = base_delay * (2 ** attempt)
                time.sleep(delay)
        return None
    return wrapper

# --- VALIDATION UTILITIES ---

def validate_email(email: str) -> bool:
    """Simple email validation."""
    return "@" in email and "." in email.split("@")[1]

def validate_url(url: str) -> bool:
    """Simple URL validation."""
    return url.startswith(("http://", "https://"))

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for filesystem operations."""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename
