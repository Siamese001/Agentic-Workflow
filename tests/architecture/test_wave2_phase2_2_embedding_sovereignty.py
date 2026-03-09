"""
Wave 2 Phase 2.2 - Embedding Sovereignty: Factory Seam Branch Coverage

Branch inventory for analyze_rag_embedding_sovereignty:
  File with no embedding_mentions -> skipped entirely (no gap)
  File with embedding_mentions, path in allowed tokens -> no gap
    - allowed tokens: 'embedding', 'rag', 'faiss', 'memory', 'factory', 'seed'
  File with embedding_mentions, layer in {L1, L4} -> no gap (allowed layers)
  File with embedding_mentions, path NOT in allowed tokens, layer NOT in {L1, L4}
    -> EMBEDDING-PLACEMENT-GAP generated (HIGH priority)
  Parse-failed file -> skipped (no gap)
  Boundary: allowed token in path but layer is L0 -> still no gap (path token wins)
  Boundary: layer is L4 but path has no allowed token -> no gap (layer wins)
  Boundary: multiple embedding mentions, all paths allowed -> no gap
  Real codebase invariants:
    - EMBEDDING-PLACEMENT-GAP count is non-negative integer
    - All EMBEDDING-PLACEMENT-GAP gaps have HIGH priority
    - All gaps have non-empty evidence_files
    - L1 and L4 files never appear in EMBEDDING-PLACEMENT-GAP
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from tools.semantic_gap_analyzer import (
    AGENTIC_CORE,
    EMBEDDING_HINT_PATTERNS,
    FileAnalysis,
    ParseFailure,
    SemanticGapAnalyzer,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _ok_analysis(file_path: Path, **kwargs) -> FileAnalysis:
    a = FileAnalysis(file_path=file_path)
    for k, v in kwargs.items():
        setattr(a, k, v)
    return a


def _failed_analysis(file_path: Path) -> FileAnalysis:
    a = FileAnalysis(file_path=file_path)
    a.parse_failure = ParseFailure(file_path=file_path, error_type="SyntaxError", message="fake")
    return a


def _make_analyzer_with_files(file_map: dict[Path, FileAnalysis]) -> SemanticGapAnalyzer:
    analyzer = SemanticGapAnalyzer()
    paths = sorted(file_map.keys())

    def _fake_find(root_or_dir, pattern):
        return [p for p in paths if str(p).startswith(str(AGENTIC_CORE))]

    def _fake_analyze(fp):
        return file_map.get(fp, _ok_analysis(fp))

    analyzer.ast_analyzer.find_hot_paths = _fake_find
    analyzer.ast_analyzer.analyze_file = _fake_analyze
    return analyzer


# ===========================================================================
# 1. No embedding_mentions -> file skipped
# ===========================================================================


@pytest.mark.architecture
def test_no_embedding_mentions_produces_no_gap():
    """File with empty embedding_mentions is skipped — no EMBEDDING-PLACEMENT-GAP."""
    fake_path = AGENTIC_CORE / "L0_routing" / "engines" / "fake_router.py"
    fake_analysis = _ok_analysis(fake_path, embedding_mentions=set())
    analyzer = _make_analyzer_with_files({fake_path: fake_analysis})

    gaps = analyzer.analyze_rag_embedding_sovereignty()
    assert not gaps, f"Expected no gaps for file with no embedding mentions: {gaps}"


# ===========================================================================
# 2. Allowed path tokens -> no gap regardless of layer
# ===========================================================================


@pytest.mark.architecture
def test_embedding_in_path_name_no_gap():
    """Allowed token 'embedding' in path -> no EMBEDDING-PLACEMENT-GAP."""
    fake_path = AGENTIC_CORE / "L0_routing" / "embedding" / "fake_embedder.py"
    fake_analysis = _ok_analysis(fake_path, embedding_mentions={"text-embedding-3-large"})
    analyzer = _make_analyzer_with_files({fake_path: fake_analysis})

    gaps = analyzer.analyze_rag_embedding_sovereignty()
    emb_gaps = [g for g in gaps if g.gap_id.startswith("EMBEDDING-PLACEMENT-GAP")]
    assert not emb_gaps, f"'embedding' in path should suppress gap: {emb_gaps}"


@pytest.mark.architecture
def test_rag_in_path_name_no_gap():
    """Allowed token 'rag' in path -> no EMBEDDING-PLACEMENT-GAP."""
    fake_path = AGENTIC_CORE / "L0_routing" / "rag_pipeline" / "fake_rag.py"
    fake_analysis = _ok_analysis(fake_path, embedding_mentions={"faiss"})
    analyzer = _make_analyzer_with_files({fake_path: fake_analysis})

    gaps = analyzer.analyze_rag_embedding_sovereignty()
    emb_gaps = [g for g in gaps if g.gap_id.startswith("EMBEDDING-PLACEMENT-GAP")]
    assert not emb_gaps, f"'rag' in path should suppress gap: {emb_gaps}"


@pytest.mark.architecture
def test_factory_in_path_name_no_gap():
    """Allowed token 'factory' in path -> no EMBEDDING-PLACEMENT-GAP."""
    fake_path = AGENTIC_CORE / "L3_orchestration" / "factories" / "fake_factory.py"
    fake_analysis = _ok_analysis(fake_path, embedding_mentions={"embedder"})
    analyzer = _make_analyzer_with_files({fake_path: fake_analysis})

    gaps = analyzer.analyze_rag_embedding_sovereignty()
    emb_gaps = [g for g in gaps if g.gap_id.startswith("EMBEDDING-PLACEMENT-GAP")]
    assert not emb_gaps


@pytest.mark.architecture
def test_memory_in_path_name_no_gap():
    """Allowed token 'memory' in path -> no EMBEDDING-PLACEMENT-GAP."""
    fake_path = AGENTIC_CORE / "L0_routing" / "memory" / "fake_store.py"
    fake_analysis = _ok_analysis(fake_path, embedding_mentions={"bge"})
    analyzer = _make_analyzer_with_files({fake_path: fake_analysis})

    gaps = analyzer.analyze_rag_embedding_sovereignty()
    emb_gaps = [g for g in gaps if g.gap_id.startswith("EMBEDDING-PLACEMENT-GAP")]
    assert not emb_gaps


@pytest.mark.architecture
def test_seed_in_path_name_no_gap():
    """Allowed token 'seed' in path -> no EMBEDDING-PLACEMENT-GAP."""
    fake_path = AGENTIC_CORE / "L0_routing" / "seed_data" / "fake_seeder.py"
    fake_analysis = _ok_analysis(fake_path, embedding_mentions={"embedding"})
    analyzer = _make_analyzer_with_files({fake_path: fake_analysis})

    gaps = analyzer.analyze_rag_embedding_sovereignty()
    emb_gaps = [g for g in gaps if g.gap_id.startswith("EMBEDDING-PLACEMENT-GAP")]
    assert not emb_gaps


# ===========================================================================
# 3. Allowed layers -> no gap
# ===========================================================================


@pytest.mark.architecture
def test_l1_layer_file_with_embedding_no_gap():
    """L1 is an allowed layer for embedding — no EMBEDDING-PLACEMENT-GAP."""
    fake_path = AGENTIC_CORE / "L1_cognition" / "engines" / "fake_reasoner.py"
    fake_analysis = _ok_analysis(fake_path, embedding_mentions={"bge", "faiss"})
    analyzer = _make_analyzer_with_files({fake_path: fake_analysis})

    gaps = analyzer.analyze_rag_embedding_sovereignty()
    emb_gaps = [g for g in gaps if g.gap_id.startswith("EMBEDDING-PLACEMENT-GAP")]
    assert not emb_gaps, f"L1 is allowed for embedding, got: {emb_gaps}"


@pytest.mark.architecture
def test_l4_layer_file_with_embedding_no_gap():
    """L4 is an allowed layer for embedding — no EMBEDDING-PLACEMENT-GAP."""
    fake_path = AGENTIC_CORE / "L4_state" / "engines" / "fake_memory_engine.py"
    fake_analysis = _ok_analysis(fake_path, embedding_mentions={"text-embedding-3-large"})
    analyzer = _make_analyzer_with_files({fake_path: fake_analysis})

    gaps = analyzer.analyze_rag_embedding_sovereignty()
    emb_gaps = [g for g in gaps if g.gap_id.startswith("EMBEDDING-PLACEMENT-GAP")]
    assert not emb_gaps, f"L4 is allowed for embedding, got: {emb_gaps}"


# ===========================================================================
# 4. Disallowed placement -> EMBEDDING-PLACEMENT-GAP generated
# ===========================================================================


@pytest.mark.architecture
def test_l0_file_no_allowed_token_generates_embedding_gap():
    """L0 file with embedding mentions and no allowed path token -> EMBEDDING-PLACEMENT-GAP."""
    fake_path = AGENTIC_CORE / "L0_routing" / "engines" / "fake_router.py"
    fake_analysis = _ok_analysis(fake_path, embedding_mentions={"bge"})
    analyzer = _make_analyzer_with_files({fake_path: fake_analysis})

    gaps = analyzer.analyze_rag_embedding_sovereignty()
    emb_gaps = [g for g in gaps if g.gap_id.startswith("EMBEDDING-PLACEMENT-GAP")]
    assert emb_gaps, "Expected EMBEDDING-PLACEMENT-GAP for L0 file with embedding outside allowed paths"
    assert emb_gaps[0].priority == "HIGH"


@pytest.mark.architecture
def test_l2_file_no_allowed_token_generates_embedding_gap():
    """L2 file with embedding mentions and no allowed token -> EMBEDDING-PLACEMENT-GAP."""
    fake_path = AGENTIC_CORE / "L2_execution" / "engines" / "fake_exec.py"
    fake_analysis = _ok_analysis(fake_path, embedding_mentions={"faiss_index"})
    analyzer = _make_analyzer_with_files({fake_path: fake_analysis})

    gaps = analyzer.analyze_rag_embedding_sovereignty()
    emb_gaps = [g for g in gaps if g.gap_id.startswith("EMBEDDING-PLACEMENT-GAP")]
    assert emb_gaps, "Expected EMBEDDING-PLACEMENT-GAP for L2 file with embedding outside allowed paths"


@pytest.mark.architecture
def test_l3_file_no_allowed_token_generates_embedding_gap():
    """L3 file with embedding mentions and no allowed token -> EMBEDDING-PLACEMENT-GAP."""
    fake_path = AGENTIC_CORE / "L3_orchestration" / "engines" / "fake_orch.py"
    fake_analysis = _ok_analysis(fake_path, embedding_mentions={"embedder"})
    analyzer = _make_analyzer_with_files({fake_path: fake_analysis})

    gaps = analyzer.analyze_rag_embedding_sovereignty()
    emb_gaps = [g for g in gaps if g.gap_id.startswith("EMBEDDING-PLACEMENT-GAP")]
    assert emb_gaps, "Expected EMBEDDING-PLACEMENT-GAP for L3 file outside allowed surfaces"


@pytest.mark.architecture
def test_unknown_layer_file_no_allowed_token_generates_embedding_gap():
    """UNKNOWN layer file (outside L0-L6) with embedding mentions -> gap if no allowed token."""
    fake_path = AGENTIC_CORE / "utils" / "fake_helper.py"
    fake_analysis = _ok_analysis(fake_path, embedding_mentions={"bge"})
    analyzer = _make_analyzer_with_files({fake_path: fake_analysis})

    gaps = analyzer.analyze_rag_embedding_sovereignty()
    emb_gaps = [g for g in gaps if g.gap_id.startswith("EMBEDDING-PLACEMENT-GAP")]
    assert emb_gaps, "Expected EMBEDDING-PLACEMENT-GAP for UNKNOWN-layer file with embedding"


# ===========================================================================
# 5. Parse failure -> skipped
# ===========================================================================


@pytest.mark.architecture
def test_parse_failed_file_skipped_no_embedding_gap():
    """Parse-failed file with embedding context is skipped — no EMBEDDING-PLACEMENT-GAP."""
    fake_path = AGENTIC_CORE / "L3_orchestration" / "engines" / "broken_orch.py"
    fake_analysis = _failed_analysis(fake_path)
    analyzer = _make_analyzer_with_files({fake_path: fake_analysis})

    gaps = analyzer.analyze_rag_embedding_sovereignty()
    assert not gaps, f"Parse-failed file should produce no embedding gaps: {gaps}"


# ===========================================================================
# 6. Boundary conditions
# ===========================================================================


@pytest.mark.architecture
def test_allowed_token_in_path_overrides_bad_layer():
    """Boundary: L0 file with 'embedding' in path -> allowed despite bad layer."""
    fake_path = AGENTIC_CORE / "L0_routing" / "embedding_cache" / "fake_cache.py"
    fake_analysis = _ok_analysis(fake_path, embedding_mentions={"bge", "faiss"})
    analyzer = _make_analyzer_with_files({fake_path: fake_analysis})

    gaps = analyzer.analyze_rag_embedding_sovereignty()
    emb_gaps = [g for g in gaps if g.gap_id.startswith("EMBEDDING-PLACEMENT-GAP")]
    assert not emb_gaps, f"Allowed token 'embedding' in path must suppress gap even for L0: {emb_gaps}"


@pytest.mark.architecture
def test_l4_layer_without_allowed_token_still_no_gap():
    """Boundary: L4 file with no allowed token in path -> still no gap (layer exemption)."""
    fake_path = AGENTIC_CORE / "L4_state" / "engines" / "fake_state_engine.py"
    fake_analysis = _ok_analysis(fake_path, embedding_mentions={"bge"})
    analyzer = _make_analyzer_with_files({fake_path: fake_analysis})

    gaps = analyzer.analyze_rag_embedding_sovereignty()
    emb_gaps = [g for g in gaps if g.gap_id.startswith("EMBEDDING-PLACEMENT-GAP")]
    assert not emb_gaps, f"L4 layer exemption should suppress gap regardless of path token: {emb_gaps}"


# ===========================================================================
# 7. EMBEDDING_HINT_PATTERNS invariants
# ===========================================================================


@pytest.mark.architecture
def test_embedding_hint_patterns_non_empty():
    """Invariant: EMBEDDING_HINT_PATTERNS must be non-empty tuple of strings."""
    assert len(EMBEDDING_HINT_PATTERNS) > 0
    for hint in EMBEDDING_HINT_PATTERNS:
        assert isinstance(hint, str) and len(hint) > 0


@pytest.mark.architecture
def test_embedding_hint_patterns_contains_expected_entries():
    """Contract: EMBEDDING_HINT_PATTERNS must contain at least 'embedding', 'bge', 'faiss'."""
    lower_patterns = [p.lower() for p in EMBEDDING_HINT_PATTERNS]
    for required in ("embedding", "bge", "faiss"):
        assert any(required in p for p in lower_patterns), (
            f"EMBEDDING_HINT_PATTERNS missing expected hint: {required!r}"
        )


# ===========================================================================
# 8. Real codebase invariants
# ===========================================================================


@pytest.mark.architecture
def test_embedding_sovereignty_returns_list():
    """Integration: analyze_rag_embedding_sovereignty returns a list without exception."""
    analyzer = SemanticGapAnalyzer()
    result = analyzer.analyze_rag_embedding_sovereignty()
    assert isinstance(result, list)


@pytest.mark.architecture
def test_all_embedding_gaps_are_high_priority():
    """Contract: all EMBEDDING-PLACEMENT-GAP gaps must have HIGH priority."""
    analyzer = SemanticGapAnalyzer()
    gaps = analyzer.analyze_rag_embedding_sovereignty()
    for gap in gaps:
        assert gap.priority == "HIGH", (
            f"EMBEDDING-PLACEMENT-GAP must be HIGH, got {gap.priority} for {gap.gap_id}"
        )


@pytest.mark.architecture
def test_all_embedding_gaps_have_evidence_files():
    """Contract: every EMBEDDING-PLACEMENT-GAP must have non-empty evidence_files."""
    analyzer = SemanticGapAnalyzer()
    gaps = analyzer.analyze_rag_embedding_sovereignty()
    for gap in gaps:
        assert gap.evidence_files, f"EMBEDDING-PLACEMENT-GAP must have evidence_files: {gap.gap_id}"


@pytest.mark.architecture
def test_l1_files_not_in_embedding_gaps():
    """Invariant: no L1 files appear in EMBEDDING-PLACEMENT-GAP evidence_files."""
    analyzer = SemanticGapAnalyzer()
    gaps = analyzer.analyze_rag_embedding_sovereignty()
    for gap in gaps:
        for ef in gap.evidence_files:
            assert "L1_cognition" not in ef, f"L1 file should never be in EMBEDDING-PLACEMENT-GAP: {ef}"


@pytest.mark.architecture
def test_l4_files_not_in_embedding_gaps():
    """Invariant: no L4 files appear in EMBEDDING-PLACEMENT-GAP evidence_files."""
    analyzer = SemanticGapAnalyzer()
    gaps = analyzer.analyze_rag_embedding_sovereignty()
    for gap in gaps:
        for ef in gap.evidence_files:
            assert "L4_state" not in ef, f"L4 file should never be in EMBEDDING-PLACEMENT-GAP: {ef}"
