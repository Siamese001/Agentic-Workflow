import os
import json
import logging
import hashlib
import time
import subprocess
from typing import Dict, Any, Optional, List, Optional, Tuple

# Configure logging
logger = logging.getLogger("CanonValidator")

def validate_python_syntax(file_path: str) -> Tuple[bool, Optional[str]]:
    """
    Parses a Python file to check for syntax errors without executing it.
    
    Args:
        file_path (str): The path to the file to check.
        
    Returns:
        Tuple[bool, Optional[str]]: (True, None) if valid. 
                                    (False, error_message) if invalid.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
        
        # Parse the source code into an AST node. 
        # This will raise SyntaxError if the code is invalid.
        ast.parse(source)
        return True, None
        
    except SyntaxError as e:
        error_msg = f"SyntaxError in {file_path}: {e.msg} at line {e.lineno}"
        logger.error(error_msg)
        return False, error_msg
    except Exception as e:
        error_msg = f"Unexpected error validating {file_path}: {str(e)}"
        logger.error(error_msg)
        return False, error_msg

# --- MOCK TOOL WRAPPERS & UTILITIES ---


def get_current_time(timezone: Optional[str] = None) -> str:
    """Mock for Time MCP: Returns current time or converts timezone."""
    if timezone == "Europe/London":
        return '{"datetime": "2025-12-15T10:45:00+00:00"}'
    return '{"datetime": "2025-12-15T05:45:00-05:00"}'


def convert_time(source_timezone: str, time: str, target_timezone: str) -> str:
    """Mock for Time MCP: Converts time between timezones."""
    return '{"target": {"datetime": "2025-12-15T12:00:00+09:00"}}'  # Example conversion


def issues_get_detail(issue_id: str) -> str:
    """Mock for GitKraken MCP: Retrieves details for an issue."""
    return f'{{"file_path": "src/config.js", "description": "High-priority bug {issue_id}"}}'


def browser_navigate(url: str) -> None:
    """Mock for Playwright MCP: Navigate to URL."""


def browser_type(element: str, ref: str, text: str) -> None:
    """Mock for Playwright MCP: Type text into element."""


def browser_click(element: str, ref: str) -> None:
    """Mock for Playwright MCP: Click element."""


def string_get(key: str) -> Optional[str]:
    """Mock for Redis MCP: Get string value."""
    # Simulate Redis cache miss
    return None


def string_set(key: str, value: str) -> None:
    """Mock for Redis MCP: Set string value."""


def start_transaction() -> None:
    """Mock for Redis MCP: Start a transaction."""


def watch_key(key: str) -> None:
    """Mock for Redis MCP: Watch a key for transaction."""


def transaction_set_with_ttl(key: str, value: str, ttl: int) -> None:
    """Mock for Redis MCP: Set value with TTL in transaction."""


def commit_transaction() -> None:
    """Mock for Redis MCP: Commit transaction."""


def incr(key: str) -> int:
    """Mock for Redis MCP: Atomically increment counter."""
    current = string_get(key)
    current_val = int(current) if current else 0
    new_val = current_val + 1
    string_set(key, str(new_val))
    return new_val


def brave_search(query: str, count: int = 5) -> str:
    """Mock for Brave Search MCP: Search the web."""
    # Return mock search results
    results = [
        {"title": f"Result 1 for {query}", "url": "https://example.com/1",
            "snippet": f"Mock snippet about {query}"},
        {"title": f"Result 2 for {query}", "url": "https://example.com/2",
            "snippet": f"Another result about {query}"},
        {"title": f"Result 3 for {query}", "url": "https://example.com/3",
            "snippet": f"Third result about {query}"}
    ]
    return json.dumps(results[:count])


def execute_cost_controlled_search(query: str, logger: Optional[Any] = None) -> Optional[str]:
    """
    Mock for Brave Search wrapper with rate limiting (L1/L3).
    Returns search results 70% of the time to simulate rate limiting.
    """
    import random
    if random.random() < 0.7:
        # Simulate successful search with rate-limited results
        results = brave_search(query, count=3)
        if logger:
            logger.info("Brave Search (Rate-Limited) returned results")
        return results
    else:
        # Simulate rate limit hit
        if logger:
            logger.info("Brave Search rate limit reached - returning None")
        return None

# LangCache Mock Functions (L4 specialized cache for LLM results)


def get_from_langcache(key: str) -> Optional[str]:
    """Mock: Retrieves final result from LangCache."""
    # Simulate a cache miss for demonstration
    return None


def set_to_langcache(key: str, value: str, ttl: int = 86400) -> None:
    """Mock: Writes result to LangCache with TTL."""
    # In a real system, this interacts with the LangCache API

# Atomic Redis Operations for Budget Control


def get_and_set(key: str, new_value: str) -> str:
    """Mock: Atomically get current value and set new value."""
    current = string_get(key)
    string_set(key, new_value)
    return current or "0"


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


def read_text_file(path: str) -> str:
    """Mock for Filesystem MCP: Read text file."""
    # Return default code artifact
    return "function defaultCodeSample() {\n  return 'Default implementation';\n}"


def add_observations(observations: List[Dict[str, Any]]) -> None:
    """Mock for MEMemory MCP: Add observations."""


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

    # Build draft content with proper skills section for testing
    draft_lines = [
        f"{draft_type} Draft - Iteration {iteration}",
        "",
        "Dear Hiring Manager,",
        "",
        f"Generated for job description: {job_desc[:50]}...",
        "",
        "Skills: Python, AWS, Docker, Kubernetes",
        "",
        f"User projects: {', '.join(user_data.get('projects', []))}",
        "",
        "Sincerely,",
        "Matthew Wallace"
    ]

    if required_keywords:
        draft_lines.insert(6, f"Target keywords: {', '.join(required_keywords[:3])}")

    return "\n".join(draft_lines)

# --- ERROR HANDLING UTILITIES ---


class MCPError(Exception):
    """Base exception for MCP-related errors."""


class CircuitBreakerOpenError(MCPError):
    """Raised when circuit breaker is open."""


def retry_with_backoff(func, max_retries: int = 3, base_delay: float = 1.0):
    """
    Retry decorator for MCP calls with exponential backoff.
    """
    def wrapper(*args, **kwargs):
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except Exception:
                pass
            
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


def get_variable_defs(node_id: str, version: Optional[str] = None) -> str:
    """Mock for Figma MCP: Get variable definitions."""
    # Return mock design variables
    return json.dumps({
        "colors": {"primary": "#007ACC", "secondary": "#6C757D"},
        "fonts": {"primary": "Arial", "secondary": "Helvetica"},
        "spacing": {"small": "8px", "medium": "16px", "large": "24px"},
        "version": version or "latest"
    })


def get_file_versions(component_id: str) -> str:
    """Mock for Figma MCP: Get file version history."""
    # Return mock version history with timestamps
    from datetime import datetime, timedelta
    now = datetime.utcnow()

    versions = [
        {
            "id": "v1.0.0",
            "created_at": (now - timedelta(days=30)).isoformat() + "Z",
            "label": "Stable Release"
        },
        {
            "id": "v1.1.0",
            "created_at": (now - timedelta(days=15)).isoformat() + "Z",
            "label": "Feature Update"
        },
        {
            "id": "v1.2.0-draft",
            "created_at": (now - timedelta(hours=6)).isoformat() + "Z",
            "label": "Draft - In Progress"
        }
    ]

    return json.dumps({"versions": versions})


def register_process(pid_file_path: str = "run/agent.pid"):
    """Writes the current process ID to the PID file."""
    import logging
    try:
        os.makedirs(os.path.dirname(pid_file_path), exist_ok=True)
        with open(pid_file_path, 'w') as f:
            f.write(str(os.getpid()))
        logging.info(f"Process registered. PID: {os.getpid()}")
    except Exception as e:
        logging.error(f"Failed to register PID: {e}")


def log_action(action_name: str, details: str, log_file: str = "logs/agent_actions.log"):
    """
    Logs an operational action for the Watchdog to see.
    Keyword 'ACTION_EXECUTED' is mandatory for the trigger.
    """
    import logging
    import time
    try:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        with open(log_file, 'a') as f:
            f.write(f"[{timestamp}] ACTION_EXECUTED: {action_name} - {details}\n")
    except Exception as e:
        logging.error(f"Failed to log action: {e}")

