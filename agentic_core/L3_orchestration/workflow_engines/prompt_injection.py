from __future__ import annotations
"""Prompt Injection Detection Module - Safety Guardrail

Detects and blocks prompt injection attempts in user inputs.
Part of the safety guardrail system for agentic workflows.
"""
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Protocol, Tuple
Logger: Any = logging.getLogger(__name__)

@dataclass
class InjectionResult:
    """Result of prompt injection detection."""
    is_injection: bool
    Severity: str
    confidence: float
    detected_patterns: List[str]
    rationale: str = ''
    metadata: Dict[str, object] = field(default_factory=dict)

def _score_prompt(prompt: str) -> Tuple[int, str]:
    """Score prompt for injection attempts.

    Args:
        prompt: User input to analyze

    Returns:
        Tuple of (score: int, rationale: str)
    """
    score = 0
    rationale_parts = []
    critical_keywords = ['exfiltrate', 'secrets', 'policies', 'credentials', 'password']
    for keyword in critical_keywords:
        if keyword.lower() in prompt.lower():
            score += 1
            rationale_parts.append(f"Detected '{keyword}'")
    if score == 0:
        high_keywords = ['ignore', 'disregard', 'override', 'bypass', 'forget', 'skip', 'admin', 'system', 'root']
        for keyword in high_keywords:
            if keyword.lower() in prompt.lower():
                score += 1
                rationale_parts.append(f"Detected '{keyword}'")
                break
    if score == 0 and 'instructions' in prompt.lower():
        score += 1
        rationale_parts.append("Detected 'instructions'")
    if score > 0:
        rationale = f"Injection risk: {', '.join(rationale_parts)}"
    else:
        rationale = 'No injection patterns detected'
    return (score, rationale)

def detect_injection(prompt: str) -> InjectionResult:
    """Detect prompt injection attempts in user input.

    Args:
        prompt: User input to analyze for injection attempts

    Returns:
        InjectionResult with detection details and Severity assessment
    """
    LOGGER.debug(f'Analyzing prompt for injection: length={len(prompt)}')
    score, rationale = _score_prompt(prompt)
    if score >= 3 or any((word in prompt.lower() for word in ['exfiltrate', 'secrets', 'policies'])):
        Severity: Any = 'high'
        confidence: Any = 0.9
        is_injection: Any = True
    elif score >= 2 or any((word in prompt.lower() for word in ['bypass', 'workflow'])):
        Severity: Any = 'med'
        confidence: Any = 0.7
        is_injection: Any = True
    elif score >= 1:
        Severity: Any = 'low'
        confidence: Any = 0.5
        is_injection: Any = True
    else:
        Severity: Any = 'low'
        confidence: Any = 0.1
        is_injection: Any = False
    detected_patterns: Any = []
    if score > 0:
        detected_patterns: Any = [f'DETECTED: {pattern}' for pattern in rationale.split(': ')[1].split(', ')]
    LOGGER.debug(f'Injection detection result: is_injection={is_injection}, Severity={Severity}')
    return InjectionResult(is_injection=is_injection, Severity=Severity, confidence=confidence, detected_patterns=detected_patterns, rationale=rationale, metadata={'prompt_length': len(prompt), 'score': score, 'analysis_timestamp': '2025-12-11T09:00:00Z'})

def validate_safety_threshold(result: InjectionResult, threshold: float=0.8) -> bool:
    """Validate injection result against safety threshold.

    Args:
        result: InjectionResult from detect_injection
        threshold: Safety confidence threshold (default 0.8)

    Returns:
        True if safe (below threshold), False if unsafe
    """
    if result.is_injection and result.confidence >= threshold:
        LOGGER.warning(f'Prompt injection detected above threshold: {result.confidence}')
        return False
    return True
