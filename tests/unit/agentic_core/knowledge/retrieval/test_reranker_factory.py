"""Unit tests for the reranker_factory (Wave D).

Verifies the env-driven reranker selection contract:
    * Default behavior is heuristic (no deployment regression).
    * Explicit modes map to the correct concrete class.
    * Unknown modes log + degrade (don't crash).
    * "none"/"off" returns None so callers can skip rerank.
    * Singletons per mode so cold init cost pays once.
    * Public API exports are wired at package level.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[5]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from agentic_core.knowledge.retrieval.cross_encoder_reranker import CrossEncoderReranker
from agentic_core.knowledge.retrieval.reranker_factory import (
    get_reranker,
    reset_for_testing,
)
from agentic_core.knowledge.retrieval.senior_librarian_reranker import (
    SeniorLibrarianReranker,
)


@pytest.fixture(autouse=True)
def _reset_singletons():
    reset_for_testing()
    yield
    reset_for_testing()


# ---------------------------------------------------------------------------
# Mode resolution
# ---------------------------------------------------------------------------


def test_default_mode_returns_heuristic(monkeypatch):
    """Unset RERANKER => heuristic, matching the historical default so no
    existing call site changes behavior until the operator opts in."""
    monkeypatch.delenv("RERANKER", raising=False)
    reranker = get_reranker()
    assert isinstance(reranker, SeniorLibrarianReranker)


def test_auto_is_equivalent_to_default(monkeypatch):
    monkeypatch.setenv("RERANKER", "auto")
    reranker = get_reranker()
    assert isinstance(reranker, SeniorLibrarianReranker)


def test_explicit_heuristic_mode(monkeypatch):
    monkeypatch.setenv("RERANKER", "heuristic")
    reranker = get_reranker()
    assert isinstance(reranker, SeniorLibrarianReranker)


def test_cross_encoder_mode_returns_cross_encoder(monkeypatch):
    """RERANKER=cross_encoder instantiates the two-stage chain. Does NOT
    require CrossEncoder weights to be downloaded because adapter load is
    deferred until the first rerank() call."""
    monkeypatch.setenv("RERANKER", "cross_encoder")
    reranker = get_reranker()
    assert isinstance(reranker, CrossEncoderReranker)


@pytest.mark.parametrize("disable_val", ["none", "off", "NONE", "Off"])
def test_disable_modes_return_none(monkeypatch, disable_val):
    """RERANKER=none|off => caller skips rerank entirely. Case-insensitive."""
    monkeypatch.setenv("RERANKER", disable_val)
    assert get_reranker() is None


def test_unknown_mode_falls_back_to_heuristic_without_crashing(monkeypatch, caplog):
    """Typos and unsupported values log a warning and degrade gracefully."""
    monkeypatch.setenv("RERANKER", "mythical_future_reranker")
    with caplog.at_level("WARNING"):
        reranker = get_reranker()
    assert isinstance(reranker, SeniorLibrarianReranker)
    # Warning message contains the bad value so operators can see what happened.
    assert any("mythical_future_reranker" in rec.message for rec in caplog.records)


def test_whitespace_in_env_var_is_stripped(monkeypatch):
    """Common shell quoting accidents like RERANKER=' cross_encoder ' must
    still resolve correctly."""
    monkeypatch.setenv("RERANKER", "  cross_encoder  ")
    reranker = get_reranker()
    assert isinstance(reranker, CrossEncoderReranker)


# ---------------------------------------------------------------------------
# Singleton discipline
# ---------------------------------------------------------------------------


def test_heuristic_is_singleton_per_process(monkeypatch):
    """Two get_reranker() calls with heuristic mode return the same instance
    — init cost pays once, state is shared, no thread fight."""
    monkeypatch.setenv("RERANKER", "heuristic")
    a = get_reranker()
    b = get_reranker()
    assert a is b


def test_cross_encoder_is_singleton_per_process(monkeypatch):
    monkeypatch.setenv("RERANKER", "cross_encoder")
    a = get_reranker()
    b = get_reranker()
    assert a is b


def test_reset_for_testing_clears_both_singletons(monkeypatch):
    """Sanity check on the test-only reset helper so other test files can
    rely on clean state between cases."""
    monkeypatch.setenv("RERANKER", "heuristic")
    first = get_reranker()
    reset_for_testing()
    monkeypatch.setenv("RERANKER", "heuristic")
    second = get_reranker()
    assert first is not second


# ---------------------------------------------------------------------------
# Public API exports
# ---------------------------------------------------------------------------


def test_get_reranker_is_exported_at_package_level():
    """Call sites import from the package, not the submodule; make sure the
    factory is reachable via that path to prevent import churn later."""
    from agentic_core.knowledge.retrieval import get_reranker as exported

    assert exported is get_reranker


def test_cross_encoder_reranker_is_exported_at_package_level():
    from agentic_core.knowledge.retrieval import CrossEncoderReranker as exported

    assert exported is CrossEncoderReranker
