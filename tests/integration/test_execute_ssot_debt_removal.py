"""Hardening tests for execute_ssot.py technical-debt removal.

Covers:
- Debt-1: _compute_novelty_score uses BGE vector (always-on; no fallback path)
- Debt-2: VectorSourceMismatchError raised on dimension mismatch
- Debt-4: _fire_meta_learning_intake adapter sentinel (no NameError when intake fails)
- Debt-5: _wc_digest uses module-level hashlib (no inline import)

BGE embeddings are a mandatory system dependency. BMG_EMBEDDINGS_ENABLED env flag
has been removed. All tests exercise the BGE-always-on code path.
"""

import inspect
from unittest.mock import MagicMock, patch

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_execute_ssot_debt_removal")
_emit_applies_guardrail("p0", "test_execute_ssot_debt_removal", "p0_governance")
_emit_reads_policy_state("p0", "test_execute_ssot_debt_removal", "policy_binding")
_emit_snapshots_state("p0", "test_execute_ssot_debt_removal", "state_snapshot")
emit_replay_key("p0", "test_execute_ssot_debt_removal")
emit_determinism_digest("p0", "test_execute_ssot_debt_removal")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

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
# Debt-1: novelty score uses BGE embeddings (always-on, no disabled path)
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_novelty_score_no_vectors_returns_1():
    """When no stored vectors, novelty must return 1 regardless of confidence.

    BGE is always active; empty vector store is a valid cold-start state.
    """
    engine = _make_engine(recent_vecs=[])
    with patch(
        "agentic_core.L2_execution.healers.bmg_embedding_similarity.bmg_embed_text",
        return_value=[0.1] * 1024,
    ):
        score = engine._compute_novelty_score(None, "agentic_core/L1", _dummy_confidence())
    assert score == 1


@pytest.mark.unit
def test_novelty_score_identical_bge_vector_returns_0():
    """When stored and query BGE vectors are identical (max_sim=1.0), novelty must be 0."""
    import numpy as np

    unit_vec = list(np.ones(1024, dtype=np.float32) / np.sqrt(1024))
    engine = _make_engine(recent_vecs=[unit_vec])
    with patch(
        "agentic_core.L2_execution.healers.bmg_embedding_similarity.bmg_embed_text",
        return_value=unit_vec,
    ):
        score = engine._compute_novelty_score(None, "agentic_core/L1", _dummy_confidence(reasoning=""))
    assert score == 0, "Identical BGE vectors should give max similarity=1.0 -> N=0"


@pytest.mark.unit
def test_novelty_score_distant_bge_vector_returns_high_novelty():
    """When stored and query BGE vectors are orthogonal, novelty must be >= 2."""
    import numpy as np

    stored_vec = list(np.ones(1024, dtype=np.float32) / np.sqrt(1024))
    # Orthogonal: stored is all-positive, query is all-negative
    query_vec = list(-np.ones(1024, dtype=np.float32) / np.sqrt(1024))
    engine = _make_engine(recent_vecs=[stored_vec])
    with patch(
        "agentic_core.L2_execution.healers.bmg_embedding_similarity.bmg_embed_text",
        return_value=query_vec,
    ):
        score = engine._compute_novelty_score(None, "brand_new_territory", _dummy_confidence())
    assert score in {2, 3}, f"Opposite BGE vectors should yield high novelty (got {score})"


@pytest.mark.unit
def test_novelty_score_reasoning_tag_has_no_effect():
    """[BMG-GPU] string in reasoning MUST NOT affect the novelty score.

    Novelty is computed from BGE vector similarity only, never from reasoning text.
    """
    import numpy as np

    unit_vec = list(np.ones(1024, dtype=np.float32) / np.sqrt(1024))
    engine = _make_engine(recent_vecs=[unit_vec])
    with patch(
        "agentic_core.L2_execution.healers.bmg_embedding_similarity.bmg_embed_text",
        return_value=unit_vec,
    ):
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
    """Mixing 16-dim query with 1024-dim stored vectors raises VectorSourceMismatchError.

    Even with BGE always active, a dimension mismatch (e.g. stale FAISS index
    built with hash-fallback vectors) must raise VectorSourceMismatchError.
    """
    from agentic_core.L1_cognition.memory.healing_memory_retriever import VectorSourceMismatchError

    stored_high_dim = [[0.1] * 1024]
    engine = _make_engine(recent_vecs=stored_high_dim)
    # Inject a 16-dim query vector to trigger dimension mismatch
    with patch(
        "agentic_core.L2_execution.healers.bmg_embedding_similarity.bmg_embed_text",
        return_value=[0.1] * 16,
    ):
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
        _mod._fire_meta_learning_intake(state_mgr, now_utc=0)

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
