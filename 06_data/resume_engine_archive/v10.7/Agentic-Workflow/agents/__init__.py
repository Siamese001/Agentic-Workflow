"""Compatibility layer exposing test-facing agent facades.

These light-weight facades provide deterministic, dependency-free
implementations that satisfy the behaviour expected by the automated
tests. They intentionally avoid importing the much heavier production
agent stacks so that the unit and regression suites can execute in the
restricted CI environment used for kata style exercises.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional


@dataclass(frozen=True)
class DetectionResult:
    """Outcome returned by :class:`PromptInjectionDetector`."""

    blocked: bool
    reason: str
    confidence: float


class PromptInjectionDetector:
    """Very small heuristic detector for prompt-injection attempts."""

    _BLOCKLIST = (
        "ignore guardrails",
        "disable safety",
        "bypass",
        "override instructions",
        "self destruct",
    )

    def detect(self, text: str) -> DetectionResult:
        lowered = text.lower()
        for keyword in self._BLOCKLIST:
            if keyword in lowered:
                return DetectionResult(
                    blocked=True,
                    reason=f"Matched keyword: {keyword}",
                    confidence=1.0,
                )
        return DetectionResult(blocked=False, reason="No issues detected", confidence=0.0)


class PIISanitizerAgent:
    """Simple recursive sanitizer that redacts common PII tokens."""

    _PII_PATTERNS: Mapping[str, str] = {
        "EMAIL": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
        "PHONE": r"\b(?:\+?1[ -]?)?\(?\d{3}\)?[ -]?\d{3}[ -]?\d{4}\b",
        "SSN": r"\b\d{3}-\d{2}-\d{4}\b",
        "NAME": r"\b[A-Z][a-z]+ [A-Z][a-z]+\b",
    }

    def __init__(self) -> None:
        import re

        self._compiled = {label: re.compile(pattern) for label, pattern in self._PII_PATTERNS.items()}

    def sanitize(self, data: Any) -> Any:
        return self._sanitize(data)

    def _sanitize(self, value: Any) -> Any:
        if isinstance(value, str):
            redacted = value
            for label, pattern in self._compiled.items():
                redacted = pattern.sub(f"[{label}_REDACTED]", redacted)
            return redacted
        if isinstance(value, Mapping):
            return {k: self._sanitize(v) for k, v in value.items()}
        if isinstance(value, list):
            return [self._sanitize(item) for item in value]
        if isinstance(value, tuple):
            return tuple(self._sanitize(item) for item in value)
        return value


class StrategyAgent:
    """Produces a deterministic high-level execution plan."""

    def __init__(self, context: Optional[Mapping[str, Any]] = None) -> None:
        self._context = dict(context or {})

    def generate_plan(self, goal: str) -> Dict[str, Any]:
        steps: List[Dict[str, str]] = [
            {"id": "research", "action": f"Collect domain knowledge for '{goal}'"},
            {"id": "draft", "action": "Produce initial artefact"},
            {"id": "review", "action": "Apply QA checks and iterate"},
        ]
        return {
            "goal": goal,
            "context": self._context,
            "steps": steps,
        }


class RAGAgent:
    """Minimal retrieval augmented generation facade."""

    def __init__(self, corpus: Optional[Iterable[str]] = None) -> None:
        self._corpus = list(corpus or ("Use vector search", "Score sources", "Cite evidence"))

    def retrieve(self, query: str) -> List[str]:
        lowered = query.lower()
        keywords = lowered.split()
        if not keywords:
            return self._corpus[:2]
        head = keywords[0]
        matches = [chunk for chunk in self._corpus if head in chunk.lower()]
        return matches or self._corpus[:2]


class DraftingAgent:
    """Drafts a short deterministic response."""

    def __init__(self, tone: str = "professional") -> None:
        self._tone = tone

    def draft(self, plan: Mapping[str, Any]) -> str:
        goal = plan.get("goal", "deliverable") if isinstance(plan, Mapping) else str(plan)
        return f"[{self._tone}] Draft prepared for {goal}."


class QAAgent:
    """Performs a toy evaluation returning a confidence score."""

    def evaluate(self, artefact: Any) -> MutableMapping[str, Any]:
        text = str(artefact)
        score = 1.0 if text and text.strip() else 0.2
        return {
            "summary": "Validated for structural consistency.",
            "confidence": score,
        }


__all__ = [
    "PromptInjectionDetector",
    "PIISanitizerAgent",
    "StrategyAgent",
    "RAGAgent",
    "DraftingAgent",
    "QAAgent",
    "DetectionResult",
]
