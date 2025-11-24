from __future__ import annotations

"""Reflexion-style self-critique and revision helpers.

These utilities provide a simple interface for critiquing and revising
model outputs. The default implementation is deterministic and does not
call LLMs.
"""

from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class Critique:
    message: str
    severity: str  # e.g. "info", "warning", "error"


def critique_output(output: str) -> List[Critique]:
    """Return deterministic critiques of an output string."""

    output = (output or "").strip()
    if not output:
        return [Critique(message="Output is empty", severity="error")]

    critiques: List[Critique] = []
    if len(output) < 50:
        critiques.append(Critique(message="Output may be too short", severity="warning"))
    if not output.endswith("."):
        critiques.append(Critique(message="Output does not end with a period", severity="info"))
    return critiques


def apply_reflexion(output: str) -> Tuple[str, List[Critique]]:
    """Apply a simple reflexion pass over an output.

    Returns (revised_output, critiques).
    """

    critiques = critique_output(output)
    revised = output.strip()
    if revised and not revised.endswith("."):
        revised = revised + "."
    return revised, critiques



