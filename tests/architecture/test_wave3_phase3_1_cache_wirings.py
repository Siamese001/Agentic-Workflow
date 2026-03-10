"""
Wave 3 Phase 3.1 - Cache Wirings + Performance: Branch Coverage Tests

Branch inventory for analyze_l0_routing_gate:
  discovery_py exists branch:
    - file exists + parse failure -> early return, no gaps
    - file exists + cache NOT imported -> L0-GAP-001 HIGH
    - file exists + cache imported via module_hint -> no L0-GAP-001
    - file exists + cache imported via symbol_hint -> no L0-GAP-001
    - file does NOT exist -> no L0-GAP-001
  policy_engine branch:
    - file exists + parse failure -> early return, no gaps after first file
    - file exists + policy cache NOT imported -> L0-GAP-002 MEDIUM
    - file exists + policy cache imported -> no L0-GAP-002
    - file does NOT exist -> no L0-GAP-002

Branch inventory for analyze_l1_cognition:
  cognitive_engine branch:
    - file exists + parse failure -> early return, no gaps
    - file exists + tool cache NOT imported -> L1-GAP-001 HIGH
    - file exists + tool cache imported -> no L1-GAP-001
    - file does NOT exist -> no L1-GAP-001
  prompt_files loop:
    - prompt file ok, no cache import, 'cache' NOT in name -> L1-GAP-PROMPT MEDIUM
    - prompt file ok, no cache import, 'cache' in name -> NO gap (excluded by filename)
    - prompt file ok, cache imported -> no L1-GAP-PROMPT
    - prompt file parse failure -> skipped (no gap)
    - no prompt files found -> no L1-GAP-PROMPT

_analysis_mentions_cache helper:
  - module_hint match -> True
  - symbol_hint match -> True
  - neither match -> False
  - no symbol_hint provided, module_hint absent -> False

Real codebase invariants:
  - analyze_l0_routing_gate returns list
  - analyze_l1_cognition returns list
  - L0-GAP-001 priority is HIGH (if present)
  - L0-GAP-002 priority is MEDIUM (if present)
  - L1-GAP-001 priority is HIGH (if present)
  - L1-GAP-PROMPT-* priority is MEDIUM (if present)
"""

from __future__ import annotations

import pathlib
import sys
from pathlib import Path
from unittest.mock import patch

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

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from tools.semantic_gap_analyzer import (
    AGENTIC_CORE,
    FileAnalysis,
    ParseFailure,
    SemanticGapAnalyzer,
    _analysis_mentions_cache,
    _contains_module_reference,
    _contains_symbol_reference,
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


def _make_analyzer(
    analyze_map: dict[Path, FileAnalysis],
    prompt_files: list[Path] | None = None,
    existing_paths: set[Path] | None = None,
) -> tuple[SemanticGapAnalyzer, dict]:
    """Return a SemanticGapAnalyzer with mocked analyze_file and find_hot_paths.
    existing_paths controls which paths report Path.exists() == True.
    Returns (analyzer, ctx) where ctx['exists_side_effect'] is the side_effect fn.
    """
    analyzer = SemanticGapAnalyzer()

    def _fake_analyze(fp: Path) -> FileAnalysis:
        return analyze_map.get(fp, _ok_analysis(fp))

    def _fake_find(base_dir: Path, pattern: str) -> list[Path]:
        if "*prompt*" in pattern and prompt_files is not None:
            return prompt_files
        return []

    analyzer.ast_analyzer.analyze_file = _fake_analyze
    analyzer.ast_analyzer.find_hot_paths = _fake_find

    _existing = existing_paths if existing_paths is not None else set(analyze_map.keys())

    def _exists_side_effect(self_path):
        return self_path in _existing

    return analyzer, {"exists_side_effect": _exists_side_effect}


# ===========================================================================
# 1. _analysis_mentions_cache helper
# ===========================================================================


@pytest.mark.architecture
def test_analysis_mentions_cache_module_hint_match():
    """_analysis_mentions_cache returns True when module_hint found in imported_module_names."""
    p = AGENTIC_CORE / "utils" / "fake.py"
    analysis = _ok_analysis(p, imported_module_names={"core.discovery_cache"})
    assert _analysis_mentions_cache(analysis, module_hint="discovery_cache")


@pytest.mark.architecture
def test_analysis_mentions_cache_symbol_hint_match():
    """_analysis_mentions_cache returns True when symbol_hint found in imported_symbol_names."""
    p = AGENTIC_CORE / "utils" / "fake.py"
    analysis = _ok_analysis(p, imported_symbol_names={"AgentDiscoveryCache"})
    assert _analysis_mentions_cache(
        analysis, module_hint="discovery_cache", symbol_hint="AgentDiscoveryCache"
    )


@pytest.mark.architecture
def test_analysis_mentions_cache_no_match():
    """_analysis_mentions_cache returns False when neither hint matches."""
    p = AGENTIC_CORE / "utils" / "fake.py"
    analysis = _ok_analysis(p, imported_module_names={"os"}, imported_symbol_names={"Path"})
    assert not _analysis_mentions_cache(
        analysis, module_hint="discovery_cache", symbol_hint="AgentDiscoveryCache"
    )


@pytest.mark.architecture
def test_analysis_mentions_cache_no_symbol_hint_module_absent():
    """_analysis_mentions_cache returns False when no symbol_hint and module absent."""
    p = AGENTIC_CORE / "utils" / "fake.py"
    analysis = _ok_analysis(p, imported_module_names={"os"})
    assert not _analysis_mentions_cache(analysis, module_hint="discovery_cache")


@pytest.mark.architecture
def test_contains_module_reference_substring_match():
    """_contains_module_reference uses substring match on module names."""
    p = AGENTIC_CORE / "utils" / "fake.py"
    analysis = _ok_analysis(p, imported_module_names={"agentic_core.cache.discovery_cache"})
    assert _contains_module_reference(analysis, "discovery_cache")


@pytest.mark.architecture
def test_contains_symbol_reference_substring_match():
    """_contains_symbol_reference uses substring match on symbol names."""
    p = AGENTIC_CORE / "utils" / "fake.py"
    analysis = _ok_analysis(p, imported_symbol_names={"AgentDiscoveryCache", "other_sym"})
    assert _contains_symbol_reference(analysis, "AgentDiscoveryCache")


# ===========================================================================
# 2. analyze_l0_routing_gate — discovery_py branch
# ===========================================================================

DISCOVERY_PY = AGENTIC_CORE / "utils" / "full_agent_discovery.py"
POLICY_ENGINE = AGENTIC_CORE / "L0_routing" / "engines" / "reasoning_policy_engine.py"


@pytest.mark.architecture
def test_discovery_py_parse_fail_no_l0_gap001():
    """L0: discovery_py parse failure -> early return, no L0-GAP-001."""
    analyzer, ctx = _make_analyzer(
        {DISCOVERY_PY: _failed_analysis(DISCOVERY_PY)},
        existing_paths={DISCOVERY_PY},
    )
    with patch.object(pathlib.Path, "exists", ctx["exists_side_effect"]):
        gaps = analyzer.analyze_l0_routing_gate()
    gap_ids = [g.gap_id for g in gaps]
    assert "L0-GAP-001" not in gap_ids


@pytest.mark.architecture
def test_discovery_py_no_cache_generates_l0_gap001():
    """L0: discovery_py exists + no cache import -> L0-GAP-001 HIGH."""
    discovery_analysis = _ok_analysis(
        DISCOVERY_PY,
        imported_module_names={"os", "pathlib"},
        imported_symbol_names=set(),
    )
    policy_analysis = _ok_analysis(
        POLICY_ENGINE,
        imported_module_names={"policy_registry_cache"},
        imported_symbol_names={"PolicyRegistryCache"},
    )
    analyzer, ctx = _make_analyzer(
        {DISCOVERY_PY: discovery_analysis, POLICY_ENGINE: policy_analysis},
        existing_paths={DISCOVERY_PY, POLICY_ENGINE},
    )
    with patch.object(pathlib.Path, "exists", ctx["exists_side_effect"]):
        gaps = analyzer.analyze_l0_routing_gate()

    gap_ids = [g.gap_id for g in gaps]
    assert "L0-GAP-001" in gap_ids
    gap = next(g for g in gaps if g.gap_id == "L0-GAP-001")
    assert gap.priority == "HIGH"


@pytest.mark.architecture
def test_discovery_py_with_module_cache_no_l0_gap001():
    """L0: discovery_py imports discovery_cache module -> no L0-GAP-001."""
    discovery_analysis = _ok_analysis(
        DISCOVERY_PY,
        imported_module_names={"agentic_core.cache.discovery_cache"},
        imported_symbol_names=set(),
    )
    policy_analysis = _ok_analysis(
        POLICY_ENGINE,
        imported_module_names={"policy_registry_cache"},
        imported_symbol_names=set(),
    )
    analyzer, ctx = _make_analyzer(
        {DISCOVERY_PY: discovery_analysis, POLICY_ENGINE: policy_analysis},
        existing_paths={DISCOVERY_PY, POLICY_ENGINE},
    )
    with patch.object(pathlib.Path, "exists", ctx["exists_side_effect"]):
        gaps = analyzer.analyze_l0_routing_gate()

    gap_ids = [g.gap_id for g in gaps]
    assert "L0-GAP-001" not in gap_ids


@pytest.mark.architecture
def test_discovery_py_with_symbol_cache_no_l0_gap001():
    """L0: discovery_py imports AgentDiscoveryCache symbol -> no L0-GAP-001."""
    discovery_analysis = _ok_analysis(
        DISCOVERY_PY,
        imported_module_names=set(),
        imported_symbol_names={"AgentDiscoveryCache"},
    )
    policy_analysis = _ok_analysis(
        POLICY_ENGINE,
        imported_module_names={"policy_registry_cache"},
        imported_symbol_names=set(),
    )
    analyzer, ctx = _make_analyzer(
        {DISCOVERY_PY: discovery_analysis, POLICY_ENGINE: policy_analysis},
        existing_paths={DISCOVERY_PY, POLICY_ENGINE},
    )
    with patch.object(pathlib.Path, "exists", ctx["exists_side_effect"]):
        gaps = analyzer.analyze_l0_routing_gate()

    gap_ids = [g.gap_id for g in gaps]
    assert "L0-GAP-001" not in gap_ids


# ===========================================================================
# 3. analyze_l0_routing_gate — policy_engine branch
# ===========================================================================


@pytest.mark.architecture
def test_policy_engine_parse_fail_no_l0_gap002():
    """L0: policy_engine parse failure -> early return, no L0-GAP-002."""
    discovery_analysis = _ok_analysis(
        DISCOVERY_PY,
        imported_module_names={"discovery_cache"},
        imported_symbol_names=set(),
    )
    analyzer, ctx = _make_analyzer(
        {DISCOVERY_PY: discovery_analysis, POLICY_ENGINE: _failed_analysis(POLICY_ENGINE)},
        existing_paths={DISCOVERY_PY, POLICY_ENGINE},
    )
    with patch.object(pathlib.Path, "exists", ctx["exists_side_effect"]):
        gaps = analyzer.analyze_l0_routing_gate()
    gap_ids = [g.gap_id for g in gaps]
    assert "L0-GAP-002" not in gap_ids


@pytest.mark.architecture
def test_policy_engine_no_cache_generates_l0_gap002():
    """L0: policy_engine exists + no cache import -> L0-GAP-002 MEDIUM."""
    discovery_analysis = _ok_analysis(
        DISCOVERY_PY,
        imported_module_names={"discovery_cache"},
        imported_symbol_names=set(),
    )
    policy_analysis = _ok_analysis(
        POLICY_ENGINE,
        imported_module_names={"os"},
        imported_symbol_names=set(),
    )
    analyzer, ctx = _make_analyzer(
        {DISCOVERY_PY: discovery_analysis, POLICY_ENGINE: policy_analysis},
        existing_paths={DISCOVERY_PY, POLICY_ENGINE},
    )
    with patch.object(pathlib.Path, "exists", ctx["exists_side_effect"]):
        gaps = analyzer.analyze_l0_routing_gate()

    gap_ids = [g.gap_id for g in gaps]
    assert "L0-GAP-002" in gap_ids
    gap = next(g for g in gaps if g.gap_id == "L0-GAP-002")
    assert gap.priority == "MEDIUM"


@pytest.mark.architecture
def test_policy_engine_with_cache_no_l0_gap002():
    """L0: policy_engine imports policy_registry_cache -> no L0-GAP-002."""
    discovery_analysis = _ok_analysis(
        DISCOVERY_PY,
        imported_module_names={"discovery_cache"},
        imported_symbol_names=set(),
    )
    policy_analysis = _ok_analysis(
        POLICY_ENGINE,
        imported_module_names={"policy_registry_cache"},
        imported_symbol_names=set(),
    )
    analyzer, ctx = _make_analyzer(
        {DISCOVERY_PY: discovery_analysis, POLICY_ENGINE: policy_analysis},
        existing_paths={DISCOVERY_PY, POLICY_ENGINE},
    )
    with patch.object(pathlib.Path, "exists", ctx["exists_side_effect"]):
        gaps = analyzer.analyze_l0_routing_gate()

    gap_ids = [g.gap_id for g in gaps]
    assert "L0-GAP-002" not in gap_ids


# ===========================================================================
# 4. analyze_l1_cognition — cognitive_engine branch
# ===========================================================================

COGNITIVE_ENGINE = AGENTIC_CORE / "L1_cognition" / "engines" / "cognitive_engine.py"


@pytest.mark.architecture
def test_cognitive_engine_parse_fail_no_l1_gap001():
    """L1: cognitive_engine parse failure -> early return, no L1-GAP-001."""
    analyzer, ctx = _make_analyzer(
        {COGNITIVE_ENGINE: _failed_analysis(COGNITIVE_ENGINE)},
        prompt_files=[],
        existing_paths={COGNITIVE_ENGINE},
    )
    with patch.object(pathlib.Path, "exists", ctx["exists_side_effect"]):
        gaps = analyzer.analyze_l1_cognition()
    gap_ids = [g.gap_id for g in gaps]
    assert "L1-GAP-001" not in gap_ids


@pytest.mark.architecture
def test_cognitive_engine_no_cache_generates_l1_gap001():
    """L1: cognitive_engine exists + no tool cache import -> L1-GAP-001 HIGH."""
    cog_analysis = _ok_analysis(
        COGNITIVE_ENGINE,
        imported_module_names={"os"},
        imported_symbol_names=set(),
    )
    analyzer, ctx = _make_analyzer(
        {COGNITIVE_ENGINE: cog_analysis},
        prompt_files=[],
        existing_paths={COGNITIVE_ENGINE},
    )
    with patch.object(pathlib.Path, "exists", ctx["exists_side_effect"]):
        gaps = analyzer.analyze_l1_cognition()

    gap_ids = [g.gap_id for g in gaps]
    assert "L1-GAP-001" in gap_ids
    gap = next(g for g in gaps if g.gap_id == "L1-GAP-001")
    assert gap.priority == "HIGH"


@pytest.mark.architecture
def test_cognitive_engine_with_cache_no_l1_gap001():
    """L1: cognitive_engine imports tool_embedding_cache -> no L1-GAP-001."""
    cog_analysis = _ok_analysis(
        COGNITIVE_ENGINE,
        imported_module_names={"agentic_core.cache.tool_embedding_cache"},
        imported_symbol_names=set(),
    )
    analyzer, ctx = _make_analyzer(
        {COGNITIVE_ENGINE: cog_analysis},
        prompt_files=[],
        existing_paths={COGNITIVE_ENGINE},
    )
    with patch.object(pathlib.Path, "exists", ctx["exists_side_effect"]):
        gaps = analyzer.analyze_l1_cognition()

    gap_ids = [g.gap_id for g in gaps]
    assert "L1-GAP-001" not in gap_ids


@pytest.mark.architecture
def test_cognitive_engine_with_symbol_cache_no_l1_gap001():
    """L1: cognitive_engine imports ToolEmbeddingCache symbol -> no L1-GAP-001."""
    cog_analysis = _ok_analysis(
        COGNITIVE_ENGINE,
        imported_module_names=set(),
        imported_symbol_names={"ToolEmbeddingCache"},
    )
    analyzer, ctx = _make_analyzer(
        {COGNITIVE_ENGINE: cog_analysis},
        prompt_files=[],
        existing_paths={COGNITIVE_ENGINE},
    )
    with patch.object(pathlib.Path, "exists", ctx["exists_side_effect"]):
        gaps = analyzer.analyze_l1_cognition()

    gap_ids = [g.gap_id for g in gaps]
    assert "L1-GAP-001" not in gap_ids


# ===========================================================================
# 5. analyze_l1_cognition — prompt_files loop branches
# ===========================================================================


@pytest.mark.architecture
def test_prompt_file_no_cache_generates_l1_gap_prompt():
    """L1 prompt loop: prompt file with no cache import, 'cache' not in name -> L1-GAP-PROMPT."""
    prompt_path = AGENTIC_CORE / "L1_cognition" / "engines" / "prompt_builder.py"
    prompt_analysis = _ok_analysis(
        prompt_path,
        imported_module_names={"os"},
        imported_symbol_names=set(),
    )
    cog_analysis = _ok_analysis(
        COGNITIVE_ENGINE,
        imported_module_names={"tool_embedding_cache"},
        imported_symbol_names=set(),
    )
    analyzer, ctx = _make_analyzer(
        {COGNITIVE_ENGINE: cog_analysis, prompt_path: prompt_analysis},
        prompt_files=[prompt_path],
        existing_paths={COGNITIVE_ENGINE},
    )
    with patch.object(pathlib.Path, "exists", ctx["exists_side_effect"]):
        gaps = analyzer.analyze_l1_cognition()

    prompt_gaps = [g for g in gaps if g.gap_id.startswith("L1-GAP-PROMPT")]
    assert prompt_gaps, "Expected L1-GAP-PROMPT gap for prompt file without cache"
    assert prompt_gaps[0].priority == "MEDIUM"


@pytest.mark.architecture
def test_prompt_file_with_cache_in_name_no_l1_gap_prompt():
    """L1 prompt loop: 'cache' in filename -> excluded from L1-GAP-PROMPT check."""
    prompt_path = AGENTIC_CORE / "L1_cognition" / "engines" / "prompt_artifact_cache.py"
    prompt_analysis = _ok_analysis(
        prompt_path,
        imported_module_names={"os"},
        imported_symbol_names=set(),
    )
    cog_analysis = _ok_analysis(
        COGNITIVE_ENGINE,
        imported_module_names={"tool_embedding_cache"},
        imported_symbol_names=set(),
    )
    analyzer, ctx = _make_analyzer(
        {COGNITIVE_ENGINE: cog_analysis, prompt_path: prompt_analysis},
        prompt_files=[prompt_path],
        existing_paths={COGNITIVE_ENGINE},
    )
    with patch.object(pathlib.Path, "exists", ctx["exists_side_effect"]):
        gaps = analyzer.analyze_l1_cognition()

    prompt_gaps = [g for g in gaps if g.gap_id.startswith("L1-GAP-PROMPT")]
    assert not prompt_gaps, f"'cache' in filename should exclude L1-GAP-PROMPT: {prompt_gaps}"


@pytest.mark.architecture
def test_prompt_file_with_cache_import_no_l1_gap_prompt():
    """L1 prompt loop: prompt file imports prompt_artifact_cache -> no L1-GAP-PROMPT."""
    prompt_path = AGENTIC_CORE / "L1_cognition" / "engines" / "prompt_builder.py"
    prompt_analysis = _ok_analysis(
        prompt_path,
        imported_module_names={"prompt_artifact_cache"},
        imported_symbol_names=set(),
    )
    cog_analysis = _ok_analysis(
        COGNITIVE_ENGINE,
        imported_module_names={"tool_embedding_cache"},
        imported_symbol_names=set(),
    )
    analyzer, ctx = _make_analyzer(
        {COGNITIVE_ENGINE: cog_analysis, prompt_path: prompt_analysis},
        prompt_files=[prompt_path],
        existing_paths={COGNITIVE_ENGINE},
    )
    with patch.object(pathlib.Path, "exists", ctx["exists_side_effect"]):
        gaps = analyzer.analyze_l1_cognition()

    prompt_gaps = [g for g in gaps if g.gap_id.startswith("L1-GAP-PROMPT")]
    assert not prompt_gaps


@pytest.mark.architecture
def test_prompt_file_parse_fail_no_l1_gap_prompt():
    """L1 prompt loop: parse-failed prompt file -> skipped, no L1-GAP-PROMPT."""
    prompt_path = AGENTIC_CORE / "L1_cognition" / "engines" / "prompt_builder.py"
    cog_analysis = _ok_analysis(
        COGNITIVE_ENGINE,
        imported_module_names={"tool_embedding_cache"},
        imported_symbol_names=set(),
    )
    analyzer, ctx = _make_analyzer(
        {COGNITIVE_ENGINE: cog_analysis, prompt_path: _failed_analysis(prompt_path)},
        prompt_files=[prompt_path],
        existing_paths={COGNITIVE_ENGINE},
    )
    with patch.object(pathlib.Path, "exists", ctx["exists_side_effect"]):
        gaps = analyzer.analyze_l1_cognition()

    prompt_gaps = [g for g in gaps if g.gap_id.startswith("L1-GAP-PROMPT")]
    assert not prompt_gaps


@pytest.mark.architecture
def test_no_prompt_files_no_l1_gap_prompt():
    """L1 prompt loop: no prompt files found -> no L1-GAP-PROMPT generated."""
    cog_analysis = _ok_analysis(
        COGNITIVE_ENGINE,
        imported_module_names={"tool_embedding_cache"},
        imported_symbol_names=set(),
    )
    analyzer, ctx = _make_analyzer(
        {COGNITIVE_ENGINE: cog_analysis},
        prompt_files=[],
        existing_paths={COGNITIVE_ENGINE},
    )
    with patch.object(pathlib.Path, "exists", ctx["exists_side_effect"]):
        gaps = analyzer.analyze_l1_cognition()

    prompt_gaps = [g for g in gaps if g.gap_id.startswith("L1-GAP-PROMPT")]
    assert not prompt_gaps


# ===========================================================================
# 6. Real codebase invariants
# ===========================================================================


@pytest.mark.architecture
def test_analyze_l0_routing_gate_returns_list():
    """Integration: analyze_l0_routing_gate returns a list without exception."""
    analyzer = SemanticGapAnalyzer()
    result = analyzer.analyze_l0_routing_gate()
    assert isinstance(result, list)


@pytest.mark.architecture
def test_analyze_l1_cognition_returns_list():
    """Integration: analyze_l1_cognition returns a list without exception."""
    analyzer = SemanticGapAnalyzer()
    result = analyzer.analyze_l1_cognition()
    assert isinstance(result, list)


@pytest.mark.architecture
def test_l0_gap001_is_high_priority_if_present():
    """Contract: L0-GAP-001 must be HIGH priority whenever it appears."""
    analyzer = SemanticGapAnalyzer()
    gaps = analyzer.analyze_l0_routing_gate()
    for gap in gaps:
        if gap.gap_id == "L0-GAP-001":
            assert gap.priority == "HIGH", f"L0-GAP-001 must be HIGH, got {gap.priority}"


@pytest.mark.architecture
def test_l0_gap002_is_medium_priority_if_present():
    """Contract: L0-GAP-002 must be MEDIUM priority whenever it appears."""
    analyzer = SemanticGapAnalyzer()
    gaps = analyzer.analyze_l0_routing_gate()
    for gap in gaps:
        if gap.gap_id == "L0-GAP-002":
            assert gap.priority == "MEDIUM", f"L0-GAP-002 must be MEDIUM, got {gap.priority}"


@pytest.mark.architecture
def test_l1_gap001_is_high_priority_if_present():
    """Contract: L1-GAP-001 must be HIGH priority whenever it appears."""
    analyzer = SemanticGapAnalyzer()
    gaps = analyzer.analyze_l1_cognition()
    for gap in gaps:
        if gap.gap_id == "L1-GAP-001":
            assert gap.priority == "HIGH", f"L1-GAP-001 must be HIGH, got {gap.priority}"


@pytest.mark.architecture
def test_l1_gap_prompt_is_medium_priority_if_present():
    """Contract: all L1-GAP-PROMPT-* gaps must be MEDIUM priority."""
    analyzer = SemanticGapAnalyzer()
    gaps = analyzer.analyze_l1_cognition()
    for gap in gaps:
        if gap.gap_id.startswith("L1-GAP-PROMPT"):
            assert gap.priority == "MEDIUM", f"L1-GAP-PROMPT must be MEDIUM, got {gap.priority}"


@pytest.mark.architecture
def test_all_l0_gaps_have_evidence_files():
    """Contract: all L0 routing gate gaps must have non-empty evidence_files."""
    analyzer = SemanticGapAnalyzer()
    gaps = analyzer.analyze_l0_routing_gate()
    for gap in gaps:
        assert gap.evidence_files, f"L0 gap must have evidence_files: {gap.gap_id}"


@pytest.mark.architecture
def test_all_l1_gaps_have_evidence_files():
    """Contract: all L1 cognition gaps must have non-empty evidence_files."""
    analyzer = SemanticGapAnalyzer()
    gaps = analyzer.analyze_l1_cognition()
    for gap in gaps:
        assert gap.evidence_files, f"L1 gap must have evidence_files: {gap.gap_id}"
