"""Root conftest.py — pytest sandbox isolation.

Redirects tmp_path to .pytest_tmp inside the repo root so that
.gitignore can cover it on every platform.
"""

from __future__ import annotations

from pathlib import Path

_BASETEMP = Path(__file__).resolve().parent / ".pytest_tmp"


def pytest_configure(config: object) -> None:
    """Set basetemp early, before tmp_path fixtures are created."""
    if getattr(config, "option", None) and getattr(config.option, "basetemp", None) is None:
        config.option.basetemp = str(_BASETEMP)  # type: ignore[union-attr]
