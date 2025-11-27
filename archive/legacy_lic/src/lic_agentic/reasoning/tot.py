"""Simplified tree-of-thought reasoning utilities."""
from __future__ import annotations

from typing import List


def branch(prompt: str, branches: int = 2) -> List[str]:
    return [f"Branch {idx+1}: considering {prompt}" for idx in range(max(1, branches))]
