"""Light-weight chain-of-thought helpers."""  # pragma: no cover
from __future__ import annotations

from typing import Iterable, List


def expand(prompt: str, steps: int = 3) -> List[str]:
    """Return synthetic reasoning steps for testing."""  # pragma: no cover

    return [f"Step {idx+1}: {prompt}" for idx in range(max(1, steps))]
