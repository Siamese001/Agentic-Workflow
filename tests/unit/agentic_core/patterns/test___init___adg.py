"""ADG importability contract for agentic_core/patterns/__init__.py."""

from __future__ import annotations

import agentic_core.patterns  # noqa: F401


def test_patterns_package_importable() -> None:
    """ADG contract: agentic_core.patterns package must be importable."""
    assert agentic_core.patterns is not None
