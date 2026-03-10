from __future__ import annotations

import re
from dataclasses import dataclass
from typing import NamedTuple, Sequence


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

class NeutralizationResult(NamedTuple):
    """The result of a prompt injection neutralization operation."""

    sanitized_prompt: str
    injection_detected: bool
    detection_patterns: list[str]


@dataclass(frozen=True)
class InjectionPattern:
    """A single pattern for detecting prompt injection attacks."""

    name: str
    regex: re.Pattern


# This is an explicit, curated list of detection patterns.
# In a real system, this would be managed under strict governance.
DEFAULT_PATTERNS: Sequence[InjectionPattern] = [
    InjectionPattern(
        name="IGNORE_INSTRUCTIONS_ATTACK",
        regex=re.compile(
            r"(ignore|disregard|override|forget) (all|any|previous|prior) instructions",
            re.IGNORECASE,
        ),
    ),
    InjectionPattern(
        name="ROLE_PLAY_HIJACK",
        regex=re.compile(r"you are now an unfiltered|act as an unfiltered", re.IGNORECASE),
    ),
    InjectionPattern(
        name="PROMPT_LEAKING_ATTACK",
        regex=re.compile(r"repeat the words above starting with|repeat everything above", re.IGNORECASE),
    ),
]


def neutralize_prompt(
    prompt: str, patterns: Sequence[InjectionPattern] = DEFAULT_PATTERNS
) -> NeutralizationResult:
    """
    Detects and neutralizes prompt injection attacks in a given prompt string.

    This function enforces Guarantee #13 by scanning for known attack vectors
    before the prompt is finalized and sent to a model. It performs a canonical,
    safe reconstruction by removing detected malicious instructions.

    This must be executed in the Assembly Stage before the final payload is constructed.

    Args:
        prompt: The raw prompt string to be sanitized.
        patterns: A sequence of InjectionPattern objects to use for detection.

    Returns:
        A NeutralizationResult containing the sanitized prompt and detection details.
    """
    sanitized_prompt = prompt
    detected_patterns: list[str] = []

    for pattern in patterns:
        if pattern.regex.search(sanitized_prompt):
            detected_patterns.append(pattern.name)
            # Perform a canonical, safe reconstruction by removing the malicious part.
            # This is a simple substitution; a real system might use more advanced
            # AST-like parsing of the prompt structure if it's complex.
            sanitized_prompt = pattern.regex.sub("", sanitized_prompt).strip()

    # The digest contribution would include the injection_detected flag and pattern names.
    # digest_material = {
    #     "injection_detected": bool(detected_patterns),
    #     "detection_patterns": sorted(detected_patterns),
    # }

    return NeutralizationResult(
        sanitized_prompt=sanitized_prompt,
        injection_detected=bool(detected_patterns),
        detection_patterns=sorted(detected_patterns),
    )
