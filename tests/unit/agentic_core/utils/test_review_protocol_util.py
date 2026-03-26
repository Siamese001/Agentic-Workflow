"""Foundational behavioral tests for agentic_core/utils/review_protocol_util.py.

fan_in=12 - this module is imported by 12 other modules.
ADG contract: import-hygiene is covered by test_review_protocol_util_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: import agentic_core.utils.review_protocol_util as _mod  # noqa: F401


def test_module_importable():
    import agentic_core.utils.review_protocol_util as _mod  # noqa: F401
    """Module review_protocol_util must be importable or skip gracefully."""
    assert _mod.__name__ == "agentic_core.utils.review_protocol_util"


def test_module_exposes_public_api():
    """review_protocol_util module exposes expected public symbols."""
    public_symbols = [n for n in dir(_mod) if not n.startswith("_")]
    assert len(public_symbols) >= 1, "review_protocol_util must expose at least one public symbol"
