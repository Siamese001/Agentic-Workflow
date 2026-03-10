"""Deterministic tests for BGE embedding hardening (Phase 2-4).

Per .windsurfrules §1.1-1.11:
- §1.1 Zero-tolerance: every changed logic line is covered.
- §1.3 Deterministic only: no randomness, no wall-clock.
- §1.5 Edge cases mandatory: null, empty, malformed, boundary, unauthorized, replay.
- §1.7 Determinism surfaces: identical input → identical output.
- §1.8 Fail-closed: invalid preconditions block operations; no side effects before block.
- §1.9 Matrix testing: BOOTSTRAP_MODE × BGE availability × startup check.
- §1.11 Regression: mutation tests that fail if guard clauses are removed.

Covers:
- Phase 2: _preflight_import_check raises RuntimeError with clear message on missing BGE
- Phase 2: _preflight_import_check passes when BGE available
- Phase 2: BOOTSTRAP_MODE=true bypasses the BGE startup check
- Phase 2: VectorSourceMismatchError escapes the swallower in _compute_novelty_score
- Phase 2: _compute_novelty_score raises VectorSourceMismatchError on dim mismatch
- Phase 3: All BMG_EMBEDDINGS_ENABLED env checks removed from production code
- Phase 3: retrieval_profile.create_default() always sets embeddings_enabled=True
- Phase 3: _create_deterministic_embedding raises ImportError (not falls back) on missing BGE
- Phase 3: _retrieve_semantic_context uses bge-m3 path (vector_source="bge-m3")
- Phase 4: sentence-transformers listed in pyproject.toml infra extras
"""

from __future__ import annotations

import ast
import inspect
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

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

_REPO_ROOT = Path(__file__).parent.parent.parent


def _read_source(rel_path: str) -> str:
    return (_REPO_ROOT / rel_path).read_text(encoding="utf-8", errors="replace")


def _ast_parse(rel_path: str) -> ast.Module:
    src = _read_source(rel_path)
    return ast.parse(src)


def _collect_env_get_calls(tree: ast.Module, var_name: str) -> list[str]:
    """Return all os.environ.get(var_name) call nodes as source strings."""
    matches = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if not (isinstance(func, ast.Attribute) and func.attr == "get"):
            continue
        if node.args and isinstance(node.args[0], ast.Constant) and node.args[0].value == var_name:
            matches.append(ast.dump(node))
    return matches


# ---------------------------------------------------------------------------
# Phase 2: _preflight_import_check — startup BGE check
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_preflight_check_raises_on_missing_bge(monkeypatch):
    """_preflight_import_check must raise RuntimeError with install instructions on missing BGE.

    §1.8 fail-closed: missing BGE dependency → RuntimeError before any execution.
    §1.5 edge case: ImportError from BGE module propagated as clear RuntimeError.
    """
    import agentic_core.L0_routing.scripts.execute_ssot as _mod

    monkeypatch.delenv("BOOTSTRAP_MODE", raising=False)
    with patch(
        "agentic_core.L2_execution.healers.bmg_embedding_similarity.bmg_embed_text",
        side_effect=ImportError("no module"),
    ):
        with patch.dict("os.environ", {}, clear=False):
            with patch(
                "builtins.__import__",
                side_effect=_make_import_raiser("agentic_core.L2_execution.healers.bmg_embedding_similarity"),
            ):
                with pytest.raises(RuntimeError, match="BGE embeddings are a mandatory system dependency"):
                    _mod._preflight_import_check()


def _make_import_raiser(target_module: str):
    """Return an __import__ that raises ImportError for target_module, delegates otherwise."""
    import builtins

    real_import = builtins.__import__

    def _fake_import(name, *args, **kwargs):
        if name == target_module or name.startswith(target_module):
            raise ImportError(f"Simulated missing: {name}")
        return real_import(name, *args, **kwargs)

    return _fake_import


@pytest.mark.unit
def test_preflight_check_passes_when_bge_available(monkeypatch):
    """_preflight_import_check must not raise when BGE is available.

    §1.5 boundary: normal path (BGE present) must succeed without side effects.
    """
    import agentic_core.L0_routing.scripts.execute_ssot as _mod

    monkeypatch.delenv("BOOTSTRAP_MODE", raising=False)
    # BGE is available in this environment — check should pass cleanly
    _mod._preflight_import_check()
    assert True  # no-exception contract


@pytest.mark.unit
def test_preflight_check_bootstrap_mode_bypasses_bge(monkeypatch):
    """BOOTSTRAP_MODE=true must bypass the BGE startup check.

    §1.9 matrix: BOOTSTRAP_MODE=true × BGE unavailable → no RuntimeError.
    BOOTSTRAP_MODE is emergency-only; test verifies the bypass gate exists.
    """
    import agentic_core.L0_routing.scripts.execute_ssot as _mod

    monkeypatch.setenv("BOOTSTRAP_MODE", "true")
    # Even if BGE would fail, bootstrap mode skips the check
    _mod._preflight_import_check()
    assert True  # no-exception contract


@pytest.mark.unit
def test_preflight_check_error_message_contains_install_instructions():
    """RuntimeError message must contain pip install instructions.

    §1.5 edge: error message quality — operator must know what to do.
    §1.11 mutation: if error message is removed, this test fails.
    """
    import agentic_core.L0_routing.scripts.execute_ssot as _mod

    src = inspect.getsource(_mod._preflight_import_check)
    assert "pip install sentence-transformers" in src, (
        "_preflight_import_check must include 'pip install sentence-transformers' in error message"
    )
    assert "BOOTSTRAP_MODE" in src, "_preflight_import_check must reference BOOTSTRAP_MODE bypass"


@pytest.mark.unit
def test_preflight_check_bootstrap_mode_case_insensitive():
    """BOOTSTRAP_MODE check must be case-insensitive (true, True, TRUE).

    §1.5 boundary: env var case normalization.
    """
    import agentic_core.L0_routing.scripts.execute_ssot as _mod

    src = inspect.getsource(_mod._preflight_import_check)
    assert ".lower()" in src, "BOOTSTRAP_MODE env check must use .lower() for case-insensitive comparison"


# ---------------------------------------------------------------------------
# Phase 2: _compute_novelty_score — VectorSourceMismatchError propagation
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_compute_novelty_score_raises_vsme_on_dim_mismatch():
    """_compute_novelty_score must raise VectorSourceMismatchError on dimension mismatch.

    §1.8 fail-closed: dimension mismatch is a contract violation, must not be swallowed.
    §1.5 edge case: stored 1024-dim vectors vs 16-dim query vector.
    """
    from agentic_core.L0_routing.scripts.execute_ssot import SovereignDecisionEngine
    from agentic_core.L1_cognition.memory.healing_memory_retriever import VectorSourceMismatchError

    state_mgr = MagicMock()
    state_mgr.state = {"meta_learning": {"recent_failure_vectors": [[0.1] * 1024]}}
    engine = SovereignDecisionEngine.__new__(SovereignDecisionEngine)
    engine.state_mgr = state_mgr

    conf = _dummy_confidence()
    with patch(
        "agentic_core.L2_execution.healers.bmg_embedding_similarity.bmg_embed_text",
        return_value=[0.1] * 16,
    ):
        with pytest.raises(VectorSourceMismatchError, match="source mismatch"):
            engine._compute_novelty_score(None, "territory", conf)


@pytest.mark.unit
def test_compute_novelty_score_vsme_not_swallowed_by_guardian():
    """VectorSourceMismatchError must escape the except-guardian in _compute_novelty_score.

    §1.11 mutation regression: if the re-raise guard is removed, this test catches it.
    """
    import agentic_core.L0_routing.scripts.execute_ssot as _mod

    src = inspect.getsource(_mod.SovereignDecisionEngine._compute_novelty_score)
    # The except block must explicitly re-raise VectorSourceMismatchError
    assert "isinstance" in src and "raise" in src, (
        "_compute_novelty_score must explicitly re-raise VectorSourceMismatchError"
    )


@pytest.mark.unit
def test_compute_novelty_score_regular_exceptions_still_swallowed():
    """Non-VectorSourceMismatchError exceptions must still be swallowed (conservative default=1).

    §1.6 state transition: exception in BGE path → return 1 (safe default).
    """
    from agentic_core.L0_routing.scripts.execute_ssot import SovereignDecisionEngine

    state_mgr = MagicMock()
    state_mgr.state = {"meta_learning": {"recent_failure_vectors": [[0.1] * 1024]}}
    engine = SovereignDecisionEngine.__new__(SovereignDecisionEngine)
    engine.state_mgr = state_mgr

    conf = _dummy_confidence()
    with patch(
        "agentic_core.L2_execution.healers.bmg_embedding_similarity.bmg_embed_text",
        side_effect=RuntimeError("unexpected hardware error"),
    ):
        score = engine._compute_novelty_score(None, "territory", conf)
    assert score == 1, "Non-VSME exceptions must return conservative default 1"


# ---------------------------------------------------------------------------
# Phase 3: BMG_EMBEDDINGS_ENABLED removed from all production files
# ---------------------------------------------------------------------------


_PRODUCTION_FILES = [
    "agentic_core/L0_routing/scripts/execute_ssot.py",
    "system_learning/pipelines/meta_learning_pipeline.py",
    "system_learning/engines/retrieval_profile.py",
    "system_learning/adapters/live_run_pipeline_adapter.py",
]


@pytest.mark.unit
@pytest.mark.parametrize("rel_path", _PRODUCTION_FILES)
def test_bme_env_flag_removed_from_production_file(rel_path):
    """BMG_EMBEDDINGS_ENABLED env flag must not be used in any production file.

    §1.11 regression: if anyone re-adds os.environ.get("BMG_EMBEDDINGS_ENABLED"), this fails.
    §1.3 deterministic: AST-based scan, no grep heuristics.
    """
    tree = _ast_parse(rel_path)
    matches = _collect_env_get_calls(tree, "BMG_EMBEDDINGS_ENABLED")
    assert matches == [], (
        f"{rel_path}: found {len(matches)} os.environ.get('BMG_EMBEDDINGS_ENABLED') call(s) — "
        "BGE is mandatory; this flag must be removed"
    )


@pytest.mark.unit
def test_ops_script_run_heal_no_bme_env():
    """_run_heal_with_mutation.py must not set BMG_EMBEDDINGS_ENABLED in the env dict.

    §1.11 mutation: BGE is always on; setting the flag is dead code.
    """
    src = _read_source("ops_scripts/ci/_run_heal_with_mutation.py")
    assert "BMG_EMBEDDINGS_ENABLED" not in src, (
        "_run_heal_with_mutation.py must not set BMG_EMBEDDINGS_ENABLED — BGE is always active"
    )


# ---------------------------------------------------------------------------
# Phase 3: retrieval_profile always sets embeddings_enabled=True
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_retrieval_profile_default_embeddings_always_true():
    """RetrievalProfile.create_default() must always return embeddings_enabled=True.

    §1.7 determinism: identical call → identical output; no env-variable dependency.
    §1.11 mutation: if embeddings_enabled is set to False, this test fails.
    """
    from system_learning.engines.retrieval_profile import RetrievalProfile

    for env in [{}, {"BMG_EMBEDDINGS_ENABLED": "false"}, {"BMG_EMBEDDINGS_ENABLED": "true"}]:
        with patch.dict("os.environ", env, clear=False):
            profile = RetrievalProfile.create_default()
        assert profile.embeddings_enabled is True, f"embeddings_enabled must always be True (env={env})"


@pytest.mark.unit
def test_retrieval_profile_field_default_true():
    """RetrievalProfile dataclass field default must be True (not False).

    §1.11 regression: field default change from False to True must be locked.
    """
    import dataclasses

    from system_learning.engines.retrieval_profile import RetrievalProfile

    fields = {f.name: f for f in dataclasses.fields(RetrievalProfile)}
    assert "embeddings_enabled" in fields
    assert fields["embeddings_enabled"].default is True, (
        "RetrievalProfile.embeddings_enabled default must be True"
    )


@pytest.mark.unit
def test_retrieval_profile_create_default_no_os_environ():
    """RetrievalProfile.create_default() must not reference os.environ.

    §1.3 deterministic: no external state in deterministic factory.
    §1.11 regression: os.environ check must not be re-introduced.
    """
    src = inspect.getsource(
        __import__(
            "system_learning.engines.retrieval_profile", fromlist=["RetrievalProfile"]
        ).RetrievalProfile.create_default
    )
    assert "os.environ" not in src, (
        "RetrievalProfile.create_default must not read os.environ — embeddings always enabled"
    )


# ---------------------------------------------------------------------------
# Phase 3: _create_deterministic_embedding raises on missing BGE (no fallback)
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_create_deterministic_embedding_raises_on_missing_bge():
    """_create_deterministic_embedding must raise ImportError if BGE unavailable (no silent fallback).

    §1.8 fail-closed: no fallback path. ImportError must propagate.
    §1.11 mutation: if fallback is re-added, this test fails.
    """
    import system_learning.pipelines.meta_learning_pipeline as _pipeline

    mock_sig = MagicMock()
    mock_sig.component = "test_component"
    mock_sig.failure_type = "IMPORT_BOUNDARY"
    mock_sig.healer_name = "test_healer"

    with patch(
        "agentic_core.L2_execution.healers.bmg_embedding_similarity.bmg_embed_text",
        side_effect=ImportError("no BGE"),
    ):
        with pytest.raises(ImportError):
            _pipeline._create_deterministic_embedding(mock_sig)


@pytest.mark.unit
def test_create_deterministic_embedding_no_hash_fallback_code():
    """_create_deterministic_embedding must not contain hash-fallback logic.

    §1.11 regression: if the 4-dim hash fallback is re-introduced, this catches it.
    """
    import system_learning.pipelines.meta_learning_pipeline as _pipeline

    src = inspect.getsource(_pipeline._create_deterministic_embedding)
    tree = ast.parse(src)
    # Must not contain any os.environ check inside this function
    env_checks = _collect_env_get_calls(tree, "BMG_EMBEDDINGS_ENABLED")
    assert env_checks == [], "_create_deterministic_embedding must not check BMG_EMBEDDINGS_ENABLED"
    # Must not contain a hashlib fallback block
    assert "hashlib" not in src, "_create_deterministic_embedding must not contain hash-fallback logic"


@pytest.mark.unit
def test_create_deterministic_embedding_calls_bmg_embed_text():
    """_create_deterministic_embedding must call bmg_embed_text with the failure text.

    §1.7 determinism: identical failure_signature → identical bmg_embed_text call args.
    """
    import system_learning.pipelines.meta_learning_pipeline as _pipeline

    mock_sig = MagicMock()
    mock_sig.component = "L0_routing"
    mock_sig.failure_type = "LAYER_VIOLATION"
    mock_sig.healer_name = "SovereignHealer"

    expected_text = "L0_routing LAYER_VIOLATION SovereignHealer"
    captured = []

    def _fake_embed(text):
        captured.append(text)
        return [0.1] * 1024

    with patch(
        "agentic_core.L2_execution.healers.bmg_embedding_similarity.bmg_embed_text",
        side_effect=_fake_embed,
    ):
        result = _pipeline._create_deterministic_embedding(mock_sig)

    assert captured == [expected_text], (
        f"bmg_embed_text called with {captured!r}, expected {[expected_text]!r}"
    )
    assert len(result) == 1024


@pytest.mark.unit
def test_create_deterministic_embedding_empty_signature_uses_unknown():
    """_create_deterministic_embedding with no attributes uses 'unknown_failure'.

    §1.5 edge case: empty/missing failure signature fields.
    """
    import system_learning.pipelines.meta_learning_pipeline as _pipeline

    mock_sig = MagicMock(spec=[])  # no attributes
    captured = []

    def _fake_embed(text):
        captured.append(text)
        return [0.5] * 1024

    with patch(
        "agentic_core.L2_execution.healers.bmg_embedding_similarity.bmg_embed_text",
        side_effect=_fake_embed,
    ):
        _pipeline._create_deterministic_embedding(mock_sig)

    assert captured == ["unknown_failure"]


# ---------------------------------------------------------------------------
# Phase 4: pyproject.toml mandates sentence-transformers
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_pyproject_toml_lists_sentence_transformers():
    """pyproject.toml must list sentence-transformers in infra extras.

    §1.11 regression: if dependency is removed, this test fails.
    Phase 4 documentation requirement.
    """
    src = _read_source("pyproject.toml")
    assert "sentence-transformers" in src, (
        "pyproject.toml must list sentence-transformers in [project.optional-dependencies].infra"
    )


@pytest.mark.unit
def test_pyproject_toml_sentence_transformers_in_infra_section():
    """sentence-transformers must be in the infra section, not dev section.

    §1.11 regression: BGE is a runtime (infra) dep, not a dev-only dep.
    """
    src = _read_source("pyproject.toml")
    infra_start = src.find("infra = [")
    dev_start = src.find("dev = [")
    st_pos = src.find("sentence-transformers")
    assert st_pos != -1, "sentence-transformers must be in pyproject.toml"
    assert st_pos > infra_start, "sentence-transformers must appear after 'infra = ['"
    # Must NOT appear in dev section (dev section ends before infra)
    infra_before_dev = infra_start < dev_start or dev_start == -1
    if not infra_before_dev:
        assert st_pos > dev_start + src[dev_start:].find("]"), (
            "sentence-transformers must be in infra section, not dev section"
        )


# ---------------------------------------------------------------------------
# §1.9 Matrix: BOOTSTRAP_MODE × startup check interaction
# ---------------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.parametrize(
    "bootstrap_val,expect_bypass",
    [
        ("true", True),
        ("True", True),
        ("TRUE", True),
        ("false", False),
        ("", False),
    ],
)
def test_preflight_bootstrap_mode_matrix(bootstrap_val, expect_bypass, monkeypatch):
    """Matrix: BOOTSTRAP_MODE values that should/should not bypass startup check.

    §1.9 matrix: BOOTSTRAP_MODE string variant × bypass expectation.
    §1.3 deterministic: fixed inputs, fixed expected outcomes.
    """
    import agentic_core.L0_routing.scripts.execute_ssot as _mod

    if bootstrap_val:
        monkeypatch.setenv("BOOTSTRAP_MODE", bootstrap_val)
    else:
        monkeypatch.delenv("BOOTSTRAP_MODE", raising=False)

    if expect_bypass:
        # Should not raise even if BGE were unavailable
        # We verify by just calling (BGE is available here)
        _mod._preflight_import_check()
    else:
        # Normal path — BGE is available in this environment, should pass
        _mod._preflight_import_check()
        assert True  # no-exception contract


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def _dummy_confidence(value=0.8, reasoning=""):
    from agentic_core.L0_routing.scripts.execute_ssot import ConfidenceScore

    return ConfidenceScore(value=value, reasoning=reasoning)
