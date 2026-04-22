"""Behavioral tests for ``agentic_core.L5_safety.validators.canonical_truth_validator``.

Covers the canonical-truth registry and L0-L6 layer directory used by
CanonicalTruthValidator consumers.
"""

from __future__ import annotations

import pytest

from agentic_core.L5_safety.validators import canonical_truth_validator as mod
from agentic_core.L5_safety.validators.canonical_truth_validator import (
    CanonicalTruthValidator,
    canonical_truth,
    get_canonical_layer,
    validate_canonical_truth,
)


# ---- CanonicalTruthValidator ----------------------------------------

class TestCanonicalTruthValidator:
    def test_register_and_get(self) -> None:
        v = CanonicalTruthValidator()
        v.register_truth("k", 123)
        assert v.get_truth("k") == 123

    def test_get_unknown_returns_none(self) -> None:
        v = CanonicalTruthValidator()
        assert v.get_truth("missing") is None

    def test_validate_unregistered_key_allows(self) -> None:
        v = CanonicalTruthValidator()
        assert v.validate("unset", "anything") is True

    def test_validate_match(self) -> None:
        v = CanonicalTruthValidator()
        v.register_truth("k", "expected")
        assert v.validate("k", "expected") is True

    def test_validate_mismatch(self) -> None:
        v = CanonicalTruthValidator()
        v.register_truth("k", "expected")
        assert v.validate("k", "wrong") is False

    def test_register_overwrites(self) -> None:
        v = CanonicalTruthValidator()
        v.register_truth("k", 1)
        v.register_truth("k", 2)
        assert v.get_truth("k") == 2

    def test_independent_instances(self) -> None:
        a = CanonicalTruthValidator()
        b = CanonicalTruthValidator()
        a.register_truth("k", 1)
        assert b.get_truth("k") is None


# ---- validate_canonical_truth / canonical_truth ---------------------

class TestValidateCanonicalTruth:
    def test_always_allows_unregistered_via_fresh_validator(self) -> None:
        # Each call creates a fresh validator, so no truth is registered
        assert validate_canonical_truth("anything", 1) is True

    def test_alias_delegates(self) -> None:
        assert canonical_truth("x", 1) is validate_canonical_truth("x", 1)


# ---- get_canonical_layer --------------------------------------------

class TestGetCanonicalLayer:
    @pytest.mark.parametrize("layer_id,expected_name", [
        ("L0", "Routing"),
        ("L1", "Cognition"),
        ("L2", "Execution"),
        ("L3", "Orchestration"),
        ("L4", "State"),
        ("L5", "Safety"),
        ("L6", "Observability"),
    ])
    def test_known_layer(self, layer_id: str, expected_name: str) -> None:
        layer = get_canonical_layer(layer_id)
        assert layer is not None
        assert layer["name"] == expected_name
        assert "responsibilities" in layer
        assert isinstance(layer["responsibilities"], list)

    def test_unknown_layer_returns_none(self) -> None:
        assert get_canonical_layer("L99") is None

    def test_empty_string_returns_none(self) -> None:
        assert get_canonical_layer("") is None


# ---- Public surface -------------------------------------------------

class TestPublicSurface:
    @pytest.mark.parametrize("name", [
        "CanonicalTruthValidator", "validate_canonical_truth",
        "get_canonical_layer", "canonical_truth",
    ])
    def test_symbol_present(self, name: str) -> None:
        assert hasattr(mod, name)

    def test_all_lists_full_surface(self) -> None:
        assert set(mod.__all__) == {
            "CanonicalTruthValidator", "validate_canonical_truth",
            "get_canonical_layer", "canonical_truth",
        }


# ---- Package __init__ exports (validators/) ------------------------

class TestPackageInit:
    def test_canonical_truth_singleton_accessible(self) -> None:
        from agentic_core.L5_safety.validators import canonical_truth as singleton
        assert isinstance(singleton, CanonicalTruthValidator)

    def test_package_all_exports(self) -> None:
        import agentic_core.L5_safety.validators as pkg
        assert "CanonicalTruthValidator" in pkg.__all__
        assert "canonical_truth" in pkg.__all__
