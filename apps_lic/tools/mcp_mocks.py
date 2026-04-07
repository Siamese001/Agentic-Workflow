from __future__ import annotations

"\nMCP Mock Tool Wrappers\n\nCluster: Mock implementations for MCP server tools (Time, GitKraken, Playwright, Redis, Brave, Memory, Pinecone, Filesystem, Figma)\nLines: 41-252 from core_utils.py\n"
import json
import logging
from typing import Any

Logger: Any = logging.getLogger("CanonValidator")


def get_current_time(timezone: str | None = None) -> str:
    """Mock for Time MCP: Returns current time or converts timezone."""
    if timezone == "Europe/London":
        return '{"datetime": "2025-12-15T10:45:00+00:00"}'
    return '{"datetime": "2025-12-15T05:45:00-05:00"}'


def convert_time(source_timezone: str, time: str, target_timezone: str) -> str:
    """Mock for Time MCP: Converts time between timezones."""
    return '{"target": {"datetime": "2025-12-15T12:00:00+09:00"}}'


def issues_get_detail(issue_id: str) -> str:
    """Mock for GitKraken MCP: Retrieves details for an issue."""
    return f'{{"file_path": "src/config.js", "description": "High-priority bug {issue_id}"}}'


def browser_navigate(url: str) -> None:
    """Mock for Playwright MCP: Navigate to URL."""


def browser_type(element: str, ref: str, text: str) -> None:
    """Mock for Playwright MCP: Type text into element."""


def browser_click(element: str, ref: str) -> None:
    """Mock for Playwright MCP: Click element."""


def string_get(key: str) -> str | None:
    """Mock for Redis MCP: Get string value."""
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
    current: Any = string_get(key)
    current_val: Any = int(current) if current else 0
    new_val: Any = current_val + 1
    string_set(key, str(new_val))
    return new_val


def get_and_set(key: str, new_value: str) -> str:
    """Mock: Atomically get current value and set new value."""
    current: Any = string_get(key)
    string_set(key, new_value)
    return current or "0"


def brave_search(query: str, count: int = 5) -> str:
    """Mock for Brave Search MCP: Search the web."""
    results: Any = [
        {
            "title": f"Result 1 for {query}",
            "url": "https://example.com/1",
            "snippet": f"Mock snippet about {query}",
        },
        {
            "title": f"Result 2 for {query}",
            "url": "https://example.com/2",
            "snippet": f"Another result about {query}",
        },
        {
            "title": f"Result 3 for {query}",
            "url": "https://example.com/3",
            "snippet": f"Third result about {query}",
        },
    ]
    return json.dumps(results[:count])


def execute_cost_controlled_search(query: str, Logger: Any | None = None) -> str | None:
    """
    Mock for Brave Search wrapper with rate limiting.
    Returns search results 70% of the time to simulate rate limiting.
    """
    import random

    if random.random() < 0.7:
        results: Any = brave_search(query, count=3)
        if Logger:
            Logger.info("Brave Search (Rate-Limited) returned results")
        return results
    else:
        if Logger:
            Logger.info("Brave Search rate limit reached - returning None")
        return None


def get_from_langcache(key: str) -> str | None:
    """Mock: Retrieves final result from LangCache."""
    return None


def set_to_langcache(key: str, value: str, ttl: int = 86400) -> None:
    """Mock: Writes result to LangCache with TTL."""


def search_nodes(query: str) -> str:
    """Mock for MEMemory MCP: Search knowledge graph."""
    return json.dumps(
        {
            "entityName": "user",
            "skills": ["Python", "JavaScript", "Machine Learning"],
            "projects": ["E-commerce Platform", "ML Pipeline"],
            "experience": "5 years",
        },
    )


def add_observations(observations: list[dict[str, Any]]) -> None:
    """Mock for MEMemory MCP: Add observations."""


def search_records(query: str, index: str, top_k: int = 5) -> str:
    """Mock for Pinecone MCP: Search vector database."""
    if "keywords" in query.lower():
        mock_keywords: Any = [
            {"keyword": "React", "score": 0.95},
            {"keyword": "TypeScript", "score": 0.9},
            {"keyword": "AWS", "score": 0.85},
            {"keyword": "Docker", "score": 0.8},
            {"keyword": "GraphQL", "score": 0.75},
        ]
        return json.dumps(mock_keywords)
    return json.dumps([{"text": "Default search result"}])


def write_file(path: str, content: str) -> None:
    """Mock for Filesystem MCP: Write file."""
    if "drafts/" in path and (not hasattr(write_file, "drafts_created")):
        write_file.drafts_created = True
    elif "reports/" in path and (not hasattr(write_file, "reports_created")):
        write_file.reports_created = True


def read_text_file(path: str) -> str:
    """Mock for Filesystem MCP: Read text file."""
    return "function defaultCodeSample() {\n  return 'Default implementation';\n}"


def semantic_score_draft(draft_content: str, JobDescription: str) -> float:
    """
    Simulates semantic analysis score by comparing draft to JD.
    Score is between 0.0 and 1.0.
    """
    if "Iteration 1" in draft_content:
        return 0.7
    elif "Iteration 2" in draft_content:
        return 0.85
    elif "Iteration 3" in draft_content:
        return 0.95
    elif "Iteration 4" in draft_content:
        return 0.98
    else:
        return 0.6


def generate_draft_llm(
    draft_type: str,
    user_data: dict,
    job_desc: str,
    current_draft: str | None = None,
    required_keywords: list | None = None,
) -> str:
    """Mock for LLM/Thinking Node: Generates or refines draft based on input context."""
    iteration: Any = current_draft.count("Iteration") + 1 if current_draft else 1
    draft_lines: Any = [
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
        "Matthew Wallace",
    ]
    if required_keywords:
        draft_lines.insert(6, f"Target keywords: {', '.join(required_keywords[:3])}")
    return "\n".join(draft_lines)


def get_variable_defs(node_id: str, version: str | None = None) -> str:
    """Mock for Figma MCP: Get variable definitions."""
    return json.dumps(
        {
            "colors": {"primary": "#007ACC", "secondary": "#6C757D"},
            "fonts": {"primary": "Arial", "secondary": "Helvetica"},
            "spacing": {"small": "8px", "medium": "16px", "large": "24px"},
            "version": version or "latest",
        },
    )


def get_file_versions(component_id: str) -> str:
    """Mock for Figma MCP: Get file version history."""
    from datetime import datetime, timedelta

    now: Any = datetime.now(timezone.utc)
    versions: Any = [
        {
            "id": "v1.0.0",
            "created_at": (now - timedelta(days=30)).isoformat() + "Z",
            "label": "Stable Release",
        },
        {
            "id": "v1.1.0",
            "created_at": (now - timedelta(days=15)).isoformat() + "Z",
            "label": "Feature Update",
        },
        {
            "id": "v1.2.0-draft",
            "created_at": (now - timedelta(hours=6)).isoformat() + "Z",
            "label": "Draft - In Progress",
        },
    ]
    return json.dumps({"versions": versions})
