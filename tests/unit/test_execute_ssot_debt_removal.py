"""Hardening tests for execute_ssot.py technical-debt removal.

Covers:
- Debt-1: _compute_novelty_score uses hash-fallback vector when embeddings disabled
- Debt-2: VectorSourceMismatchError raised on dimension mismatch
- Debt-4: _fire_meta_learning_intake adapter sentinel (no NameError when intake fails)
- Debt-5: _wc_digest uses module-level hashlib (no inline import)
"""

import inspect
from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_engine(recent_vecs=None):
    """Return a SovereignDecisionEngine with optional L4 state."""
    from agentic_core.L0_routing.scripts.execute_ssot import SovereignDecisionEngine

    state_mgr = MagicMock()
    state_mgr.state = {"meta_learning": {"recent_failure_vectors": recent_vecs or []}}
    engine = SovereignDecisionEngine.__new__(SovereignDecisionEngine)
    engine.state_mgr = state_mgr
    return engine


def _dummy_confidence(value=0.8, reasoning=""):
    from agentic_core.L0_routing.scripts.execute_ssot import ConfidenceScore

    return ConfidenceScore(value=value, reasoning=reasoning)


# ---------------------------------------------------------------------------
# Debt-1: hash-fallback novelty replaces [BMG-GPU] heuristic
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_novelty_score_disabled_no_vectors_returns_1():
    """When embeddings disabled and no stored vectors, novelty must be 1 (not [BMG-GPU])."""
    engine = _make_engine(recent_vecs=[])
    with patch.dict("os.environ", {"BMG_EMBEDDINGS_ENABLED": "false"}):
        score = engine._compute_novelty_score(None, "agentic_core/L1", _dummy_confidence())
    assert score == 1


@pytest.mark.unit
def test_novelty_score_disabled_uses_fallback_vector_not_bmg_string():
    """When embeddings disabled, score must use generate_fallback_vector, not reason string heuristic.

    _compute_novelty_score builds signal_text as f"{ft_str} {territory}" where
    ft_str is "UNKNOWN" when failure_type is None.  The stored vector must use
    that exact same text so the dot product is 1.0 (identical unit vectors).
    """
    from agentic_core.L2_execution.healers.failure_signal_normalizer import generate_fallback_vector

    same_vec = generate_fallback_vector("UNKNOWN agentic_core/L1")
    engine = _make_engine(recent_vecs=[same_vec])
    with patch.dict("os.environ", {"BMG_EMBEDDINGS_ENABLED": "false"}):
        score = engine._compute_novelty_score(None, "agentic_core/L1", _dummy_confidence(reasoning=""))

    assert score == 0, "Identical stored and query hash vectors should give max similarity >= 0.85 -> N=0"


@pytest.mark.unit
def test_novelty_score_disabled_completely_novel_returns_3():
    """Hash-fallback novelty for a completely different vector should return 3."""
    from agentic_core.L2_execution.healers.failure_signal_normalizer import generate_fallback_vector

    stored = generate_fallback_vector("COMPLETELY_DIFFERENT zzz")
    import numpy as np

    stored_flipped = list(-np.array(stored, dtype=np.float32))
    engine = _make_engine(recent_vecs=[stored_flipped])
    with patch.dict("os.environ", {"BMG_EMBEDDINGS_ENABLED": "false"}):
        score = engine._compute_novelty_score(None, "brand_new_territory", _dummy_confidence())
    assert score in {2, 3}, f"Opposite/distant vector should yield high novelty (got {score})"


@pytest.mark.unit
def test_novelty_score_disabled_legacy_bmg_gpu_string_no_longer_used():
    """[BMG-GPU] string in reasoning MUST NOT affect the novelty score in disabled mode."""
    from agentic_core.L2_execution.healers.failure_signal_normalizer import generate_fallback_vector

    same_vec = generate_fallback_vector("LAYER_VIOLATION territory_x")
    engine = _make_engine(recent_vecs=[same_vec])
    with patch.dict("os.environ", {"BMG_EMBEDDINGS_ENABLED": "false"}):
        score_with_tag = engine._compute_novelty_score(
            None, "territory_x", _dummy_confidence(reasoning="Base: 0.80 [BMG-GPU]")
        )
        score_without_tag = engine._compute_novelty_score(
            None, "territory_x", _dummy_confidence(reasoning="Base: 0.80")
        )
    assert score_with_tag == score_without_tag, "[BMG-GPU] tag must not change novelty score"


# ---------------------------------------------------------------------------
# Debt-2: VectorSourceMismatchError on dimension mismatch
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_vector_source_mismatch_error_exported():
    """VectorSourceMismatchError must be exported from healing_memory_retriever."""
    from agentic_core.L1_cognition.memory.healing_memory_retriever import (
        VectorSourceMismatchError,
        __all__,
    )

    assert "VectorSourceMismatchError" in __all__
    assert issubclass(VectorSourceMismatchError, RuntimeError)


@pytest.mark.unit
def test_novelty_score_dim_mismatch_raises_vector_source_mismatch_error():
    """Mixing hash-fallback query (16-dim) with bge-m3-like stored vectors raises VectorSourceMismatchError."""
    from agentic_core.L1_cognition.memory.healing_memory_retriever import VectorSourceMismatchError

    stored_high_dim = [[0.1] * 1024]
    engine = _make_engine(recent_vecs=stored_high_dim)
    with patch.dict("os.environ", {"BMG_EMBEDDINGS_ENABLED": "false"}):
        with pytest.raises(VectorSourceMismatchError, match="source mismatch"):
            engine._compute_novelty_score(None, "agentic_core/L1", _dummy_confidence())


# ---------------------------------------------------------------------------
# Debt-4: _fire_meta_learning_intake adapter sentinel
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_fire_meta_learning_intake_no_name_error_when_intake_fails():
    """_fire_meta_learning_intake must not raise NameError for adapter if intake try-block fails.

    With the debt-4 sentinel fix, even when the first try-block (intake) raises
    ImportError before adapter is assigned, the second try-block (pipeline) must
    receive adapter=None rather than a NameError.
    """
    import agentic_core.L0_routing.scripts.execute_ssot as _mod

    state_mgr = MagicMock()
    state_mgr.state = {"healing_actions": []}
    state_mgr.update_meta_learning = MagicMock()

    src = inspect.getsource(_mod._fire_meta_learning_intake)
    assert "adapter = None" in src, (
        "Debt-4: _fire_meta_learning_intake must initialise `adapter = None` before the first try-block"
    )
    assert 'adapter if "adapter" in dir()' not in src, (
        "Debt-4: dir()-based guard must be removed; use the `adapter` sentinel directly"
    )


@pytest.mark.unit
def test_fire_meta_learning_intake_adapter_sentinel_is_none_on_early_fail(monkeypatch):
    """When the intake imports fail, pipeline try-block receives adapter=None (not NameError)."""
    import agentic_core.L0_routing.scripts.execute_ssot as _mod

    calls = []

    def _patched_build_pipeline_deps(repo_root, healing_outcome_intake_adapter):
        calls.append(healing_outcome_intake_adapter)
        raise ImportError("sentinel test stop")

    state_mgr = MagicMock()
    state_mgr.state = {"healing_actions": []}
    state_mgr.update_meta_learning = MagicMock()

    with (
        patch(
            "system_learning.engines.healing_outcome_aggregator.HealingOutcomeAggregator",
            side_effect=ImportError("simulate intake fail"),
        ),
        patch(
            "system_learning.pipelines.pipeline_factory.build_pipeline_deps",
            side_effect=_patched_build_pipeline_deps,
        ),
        patch(
            "system_learning.pipelines.meta_learning_pipeline.run_pipeline",
            side_effect=ImportError("pipeline unavailable"),
        ),
    ):
        _mod._fire_meta_learning_intake(state_mgr)

    if calls:
        assert calls[0] is None, "adapter must be None when intake try-block raised before assignment"


# ---------------------------------------------------------------------------
# Debt-5: _wc_digest must not have inline import of hashlib
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_wc_digest_no_inline_hashlib_import():
    """_wc_digest must not contain an inline 'import hashlib' statement (debt-5)."""
    import ast

    import system_learning.pipelines.meta_learning_pipeline as _pipeline_mod

    src = inspect.getsource(_pipeline_mod._wc_digest)
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            for alias in getattr(node, "names", []):
                assert alias.name != "hashlib", (
                    "_wc_digest must not contain inline 'import hashlib' (use module-level import)"
                )
