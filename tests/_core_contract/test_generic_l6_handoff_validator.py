"""Generic L6 handoff manifest validator (minimal)."""

from __future__ import annotations

from agentic_core.runtime.bindings.generic_l6_handoff_validator import (
    validate_generic_l6_handoff_manifest,
)


def test_handoff_manifest_validator_empty_ok() -> None:
    assert validate_generic_l6_handoff_manifest({}) == []
