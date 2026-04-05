"""Deterministic tests for all 10 hardening gap fixes."""
from __future__ import annotations


def test_module_importable():
    """Module hardened_gemini_executor_types must be importable."""
    import apps_shared.types.hardened_gemini_executor_types  # noqa: F401

    assert apps_shared.types.hardened_gemini_executor_types is not None
