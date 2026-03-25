"""ADG importability contract for agentic_core/L2_execution/enforcement/manifest_hash_validator.py."""
from __future__ import annotations

import agentic_core.L2_execution.enforcement.manifest_hash_validator  # noqa: F401


def test_module_importable():
    """Module manifest_hash_validator must be importable."""
    assert agentic_core.L2_execution.enforcement.manifest_hash_validator is not None
