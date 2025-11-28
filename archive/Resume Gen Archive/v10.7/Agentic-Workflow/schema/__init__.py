"""Lightweight schema helpers used during tests."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class ResumeOutputSchema:
    """Minimal structure validator for resume payloads in tests."""

    candidate: str
    job_title: str
    summary: str
    highlights: List[str] = field(default_factory=list)
    skills: List[str] = field(default_factory=list)
    sections: List[Dict[str, Any]] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.candidate:
            raise ValueError("candidate must be provided")
        if not self.job_title:
            raise ValueError("job_title must be provided")
        if not self.summary:
            raise ValueError("summary must be provided")


__all__ = ["ResumeOutputSchema"]
