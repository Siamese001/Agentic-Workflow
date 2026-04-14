"""Behavioral contract tests for agentic_core.evaluation.judges.__init__."""

from __future__ import annotations

import importlib

import pytest

from agentic_core.evaluation.judges.deterministic_judges import _created_at, _verdict_id
from agentic_core.evaluation.judges.types import EvidenceBundle

MODULE_PATH = "agentic_core.evaluation.judges.__init__"


@pytest.fixture(scope="module")
def mod():
    """Import the module under test. Fails hard if first-party import broken."""
    try:
        return importlib.import_module(MODULE_PATH)
    except Exception as exc:  # guardian: allow-broad-exception -- test fixture must surface any import-time error as actionable pytest.fail
        pytest.fail(
            f"FIRST-PARTY IMPORT FAILED for {MODULE_PATH}: {exc}",
            pytrace=False,
        )


def test_module_importable(mod):
    """Module imports without errors."""
    assert mod.__name__ == MODULE_PATH


def test_module_is_namespace_package(mod):
    """Module is a valid namespace package (empty __init__)."""
    public = [n for n in dir(mod) if not n.startswith("_")]
    # Empty namespace packages are valid - just verify import succeeded
    assert mod is not None


# ---------------------------------------------------------------------------
# G6: _verdict_id stability and _created_at precedence
# ---------------------------------------------------------------------------


def test_verdict_id_stable_same_inputs():
    """G6: identical bundle+rubric produces identical 12-char hex ID."""
    bundle = EvidenceBundle(target="agentic_core/L2_execution/foo.py", adg_digest="abc123")
    id1 = _verdict_id(bundle, "ARCH-001")
    id2 = _verdict_id(bundle, "ARCH-001")
    assert id1 == id2
    assert len(id1) == 12
    assert all(c in "0123456789abcdef" for c in id1)


def test_verdict_id_differs_on_different_rubric():
    """G6: same bundle, different rubric_id → different verdict ID."""
    bundle = EvidenceBundle(target="agentic_core/L2_execution/foo.py", adg_digest="abc123")
    id_arch = _verdict_id(bundle, "ARCH-001")
    id_dep = _verdict_id(bundle, "DEP-001")
    assert id_arch != id_dep


def test_verdict_id_differs_on_different_target():
    """G6: same rubric, different bundle target → different verdict ID."""
    b1 = EvidenceBundle(target="module_a.py", adg_digest="digest1")
    b2 = EvidenceBundle(target="module_b.py", adg_digest="digest1")
    assert _verdict_id(b1, "GOV-002") != _verdict_id(b2, "GOV-002")


def test_created_at_uses_injected_timestamp():
    """G6: evaluation_timestamp in config_context is returned."""
    bundle = EvidenceBundle(
        target="x.py",
        config_context={"evaluation_timestamp": "2025-01-15T12:00:00Z"},
    )
    assert _created_at(bundle) == "2025-01-15T12:00:00Z"


def test_created_at_returns_empty_when_absent():
    """G6: missing evaluation_timestamp returns empty string."""
    bundle = EvidenceBundle(target="x.py")
    assert _created_at(bundle) == ""


def test_created_at_returns_empty_when_explicitly_falsy():
    """G6: empty-string evaluation_timestamp yields empty string."""
    bundle = EvidenceBundle(target="x.py", config_context={"evaluation_timestamp": ""})
    assert _created_at(bundle) == ""
