from __future__ import annotations

import re
from dataclasses import dataclass
from typing import NamedTuple, Sequence


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


DEFAULT_PATTERNS: Sequence[InjectionPattern] = [
    InjectionPattern(
        name="IGNORE_INSTRUCTIONS_ATTACK",
        regex=re.compile(
            "(ignore|disregard|override|forget) (all|any|previous|prior) instructions", re.IGNORECASE,
        ),
    ),
    InjectionPattern(
        name="ROLE_PLAY_HIJACK",
        regex=re.compile("you are now an unfiltered|act as an unfiltered", re.IGNORECASE),
    ),
    InjectionPattern(
        name="PROMPT_LEAKING_ATTACK",
        regex=re.compile("repeat the words above starting with|repeat everything above", re.IGNORECASE),
    ),
]


def neutralize_prompt(
    prompt: str, patterns: Sequence[InjectionPattern] = DEFAULT_PATTERNS,
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
            sanitized_prompt = pattern.regex.sub("", sanitized_prompt).strip()
    return NeutralizationResult(
        sanitized_prompt=sanitized_prompt,
        injection_detected=bool(detected_patterns),
        detection_patterns=sorted(detected_patterns),
    )


class AssemblyInjectionNeutralizer:
    """Wrapper class for assembly-level prompt injection neutralization.

    Provides a class-based interface for the neutralize_prompt function,
    allowing it to be instantiated and configured with custom patterns.
    """

    def __init__(
        self, patterns: Sequence[InjectionPattern] | None = None,
    ) -> None:
        """Initialize with optional custom patterns.

        Args:
            patterns: Custom injection patterns. If None, uses DEFAULT_PATTERNS.
        """
        self.patterns = patterns if patterns is not None else DEFAULT_PATTERNS

    def neutralize(self, prompt: str) -> NeutralizationResult:
        """Neutralize a prompt using configured patterns.

        Args:
            prompt: The raw prompt to sanitize.

        Returns:
            NeutralizationResult with sanitized prompt and detection info.
        """
        return neutralize_prompt(prompt, self.patterns)
