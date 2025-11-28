"""
Reflexion self-critique framework for résumé processing workflows.

Provides deterministic output evaluation and revision for comprehensive résumé enhancement.
"""

from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class Critique:
    """
    Represents critique result for résumé processing output evaluation.

    Enables systematic quality assessment for résumé improvement workflows.
    """
    message: str
    severity: str  # e.g. "info", "warning", "error"


def critique_output(output: str) -> List[Critique]:
    """
    Evaluates résumé processing output for quality improvements.

    Identifies areas for enhancement in comprehensive résumé analysis results.
    """

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
    """
    Applies reflexion revision process to résumé processing outputs.

    Ensures quality enhancement through systematic critique and revision.
    """

    critiques = critique_output(output)
    revised = output.strip()
    if revised and not revised.endswith("."):
        revised = revised + "."
    return revised, critiques



