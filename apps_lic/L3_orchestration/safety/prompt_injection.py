"""Prompt Injection Detection Module - Safety Guardrail

Detects and blocks prompt injection attempts in user inputs.
Part of the safety guardrail system for agentic workflows.
"""

import logging
from typing import Dict, List, Tuple
from dataclasses import dataclass, field # Added missing import for dataclass and field

LOGGER = logging.getLogger(__name__)

@dataclass
class InjectionResult:
    """Result of prompt injection detection."""
    is_injection: bool
    severity: str  # "low" | "med" | "high"
    confidence: float
    detected_patterns: List[str]
    rationale: str = "" # Changed RATIONALE to rationale for consistency and PEP8
    metadata: Dict[str, object] = field(default_factory=dict)

def _score_prompt(prompt: str) -> Tuple[int, str]:
    """Score prompt for injection attempts.

    Args:
        prompt: User input to analyze

    Returns:
        Tuple of (score: int, rationale: str)
    """
    score = 0 # Changed SCORE to score for consistency and PEP8
    rationale_parts = []

    # Check for critical keywords first (highest priority)
    critical_keywords = [
        "exfiltrate", "secrets", "policies", "credentials", "password"
    ]

    for keyword in critical_keywords:
        if keyword.lower() in prompt.lower():
            score += 1
            rationale_parts.append(f"Detected '{keyword}'")

    # If no critical keywords, check for high severity keywords
    if score == 0:
        high_keywords = [
            "ignore", "disregard", "override", "bypass", "forget",
            "skip", "admin", "system", "root"
        ]

        for keyword in high_keywords:
            if keyword.lower() in prompt.lower():
                score += 1
                rationale_parts.append(f"Detected '{keyword}'")
                break  # Only count one high-severity keyword

    # Special case: "instructions" only counts if no other keywords found
    if score == 0 and "instructions" in prompt.lower():
        score += 1
        rationale_parts.append("Detected 'instructions'")

    if score > 0:
        rationale = f"Injection risk: {', '.join(rationale_parts)}" # Changed RATIONALE to rationale
    else:
        rationale = "No injection patterns detected" # Changed RATIONALE to rationale

    return score, rationale

def detect_injection(prompt: str) -> InjectionResult:
    """Detect prompt injection attempts in user input.

    Args:
        prompt: User input to analyze for injection attempts

    Returns:
        InjectionResult with detection details and severity assessment
    """
    LOGGER.debug(f"Analyzing prompt for injection: length={len(prompt)}") # Changed logger to LOGGER

    # Score the prompt
    score, rationale = _score_prompt(prompt) # Changed SCORE, RATIONALE to score, rationale

    # Determine severity based on score and content
    if score >= 3 or any(word in prompt.lower() for word in ["exfiltrate", "secrets", "policies"]):
        severity = "high" # Changed SEVERITY to severity
        confidence = 0.9 # Changed CONFIDENCE to confidence
        is_injection = True
    elif score >= 2 or any(word in prompt.lower() for word in ["bypass", "workflow"]):
        severity = "med" # Changed SEVERITY to severity
        confidence = 0.7 # Changed CONFIDENCE to confidence
        is_injection = True
    elif score >= 1:
        severity = "low" # Changed SEVERITY to severity
        confidence = 0.5 # Changed CONFIDENCE to confidence
        is_injection = True
    else:
        severity = "low" # Changed SEVERITY to severity
        confidence = 0.1 # Changed CONFIDENCE to confidence
        is_injection = False

    # Extract detected patterns
    detected_patterns = []
    if score > 0:
        detected_patterns = [f"DETECTED: {pattern}" for pattern in rationale.split(": ")[1].split(", ")] # Fixed unterminated string literal

    LOGGER.debug(f"Injection detection result: is_injection={is_injection}, severity={severity}") # Changed logger to LOGGER

    return InjectionResult(
        is_injection=is_injection,
        severity=severity, # Changed SEVERITY to severity
        confidence=confidence, # Changed CONFIDENCE to confidence
        detected_patterns=detected_patterns,
        rationale=rationale, # Changed RATIONALE to rationale
        metadata={ # Changed METADATA to metadata
            "prompt_length": len(prompt),
            "score": score,
            "analysis_timestamp": "2025-12-11T09:00:00Z"
        }
    )

def validate_safety_threshold(result: InjectionResult, threshold: float = 0.8) -> bool:
    """Validate injection result against safety threshold.

    Args:
        result: InjectionResult from detect_injection
        threshold: Safety confidence threshold (default 0.8)

    Returns:
        True if safe (below threshold), False if unsafe
    """
    if result.is_injection and result.confidence >= threshold:
        LOGGER.warning(f"Prompt injection detected above threshold: {result.confidence}") # Changed logger to LOGGER
        return False
    return True