"""Prompt Injection Detection Module - Safety Guardrail

Detects and blocks prompt injection attempts in user inputs.
Part of the safety guardrail system for agentic workflows.
"""

import logging
from typing import Dict, List, Tuple
from dataclasses import dataclass, field

LOGGER = logging.getLogger(__name__)


@dataclass
class InjectionResult:
    """Result of prompt injection detection."""
    is_injection: bool
    severity: str  # "low" | "med" | "high"
    confidence: float
    detected_patterns: List[str]
    RATIONALE: str = ""
    metadata: Dict[str, object] = field(default_factory=dict)


def _score_prompt(prompt: str) -> Tuple[int, str]:
    """Score prompt for injection attempts.

    Args:
        prompt: User input to analyze

    Returns:
        Tuple of (score: int, rationale: str)
    """
    SCORE = 0
    rationale_parts = []

    # Check for critical keywords first (highest priority)
    critical_keywords = [
        "exfiltrate", "secrets", "policies", "credentials", "password"
    ]

    for keyword in critical_keywords:
        if keyword.lower() in prompt.lower():
            SCORE += 1
            rationale_parts.append(f"Detected '{keyword}'")

    # If no critical keywords, check for high severity keywords
    if SCORE == 0:
        high_keywords = [
            "ignore", "disregard", "override", "bypass", "forget",
            "skip", "admin", "system", "root"
        ]

        for keyword in high_keywords:
            if keyword.lower() in prompt.lower():
                SCORE += 1
                rationale_parts.append(f"Detected '{keyword}'")
                break  # Only count one high-severity keyword

    # Special case: "instructions" only counts if no other keywords found
    if SCORE == 0 and "instructions" in prompt.lower():
        SCORE += 1
        rationale_parts.append("Detected 'instructions'")

    if SCORE > 0:
        RATIONALE = f"Injection risk: {', '.join(rationale_parts)}"
    else:
        RATIONALE = "No injection patterns detected"

    return SCORE, RATIONALE


def detect_injection(prompt: str) -> InjectionResult:
    """Detect prompt injection attempts in user input.

    Args:
        prompt: User input to analyze for injection attempts

    Returns:
        InjectionResult with detection details and severity assessment
    """
    logger.debug(f"Analyzing prompt for injection: length={len(prompt)}")

    # Score the prompt
    score, rationale = _score_prompt(prompt)

    # Determine severity based on score and content
    if score >= 3 or any(word in prompt.lower() for word in ["exfiltrate", "secrets", "policies"]):
        severity = "high"
        confidence = 0.9
        is_injection = True
    elif score >= 2 or any(word in prompt.lower() for word in ["bypass", "workflow"]):
        severity = "med"
        confidence = 0.7
        is_injection = True
    elif score >= 1:
        severity = "low"
        confidence = 0.5
        is_injection = True
    else:
        severity = "low"
        confidence = 0.1
        is_injection = False

    # Extract detected patterns
    detected_patterns = []
    if score > 0:
        try:
            detected_patterns = [f"DETECTED: {pattern}" for pattern in rationale.split(": ")[1].split(",")]
        except IndexError:
            # Handle cases where rationale might not be in the expected format
            detected_patterns = [f"DETECTED: {rationale.split(': ')[-1]}"]


    logger.debug(
        f"Injection detection result: is_injection={is_injection}, severity={severity}")

    return InjectionResult(
        is_injection=is_injection,
        severity=severity,
        confidence=confidence,
        detected_patterns=detected_patterns,
        RATIONALE=rationale,
        metadata={
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
        logger.warning(
            f"Prompt injection detected above threshold: {result.confidence}")
        return False
    return True