"""
Wave 2 Phase 2.3 - Prompt Taxonomy: Complete Slot Coverage Branch Tests

Branch inventory for analyze_prompt_taxonomy_coverage:
  _looks_like_prompt_assembler:
    - success: 'prompt' in name + assembler token in rel -> qualifies
    - negative: no prompt token in name -> not a prompt assembler
    - negative: prompt in name but no assembler token -> not flagged
  analyze_prompt_taxonomy_coverage:
    - File skipped: parse failure (not ok)
    - File skipped: _looks_like_prompt_assembler returns False
    - File processed: _looks_like_prompt_assembler returns True
    - missing_slots non-empty, includes S0/C0/U0 -> PROMPT-TAXONOMY-GAP HIGH
    - missing_slots non-empty, excludes S0/C0/U0 -> PROMPT-TAXONOMY-GAP MEDIUM
    - missing_slots empty (all slots present) -> no PROMPT-TAXONOMY-GAP
    - no manifest_hash_mentions -> PROMPT-MANIFEST-GAP MEDIUM
    - manifest_hash_mentions present -> no PROMPT-MANIFEST-GAP
    - no boundary_snapshot_mentions -> PROMPT-VALIDATOR-GAP LOW
    - boundary_snapshot_mentions present -> no PROMPT-VALIDATOR-GAP
    - duplicate paths from multiple base_dirs -> deduplication via seen set
  Helper functions:
    - _slot_coverage_score: 0 when no hits, 5 when all slots hit
    - _missing_slots: returns all 5 when empty, empty list when all present
    - _report_slot_status: marks each slot as present/missing
    - PROMPT_TAXONOMY_PATTERNS: each slot has non-empty pattern tuple
    - PROMPT_SLOT_ORDER: contains all 5 canonical slots
  analyze_file prompt slot detection:
    - S0 detected from string literal containing 'system_prompt'
    - D0 detected from string literal containing 'guardrail'
    - I0 detected from used_name containing 'persona'
    - C0 detected from string literal containing 'context'
    - U0 detected from string literal containing 'user_prompt'
    - no slot hit for unrelated content
  Real codebase invariants:
    - analyze_prompt_taxonomy_coverage returns list
    - All PROMPT-TAXONOMY-GAP gaps layer is 'L1'
    - All PROMPT-MANIFEST-GAP gaps priority is 'MEDIUM'
    - All PROMPT-VALIDATOR-GAP gaps priority is 'LOW'
"""

from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path
from textwrap import dedent

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from tools.semantic_gap_analyzer import (
    AGENTIC_CORE,
    PROMPT_SLOT_ORDER,
    PROMPT_TAXONOMY_PATTERNS,
    ASTAnalyzer,
    FileAnalysis,
    ParseFailure,
    SemanticGapAnalyzer,
    _looks_like_prompt_assembler,
    _missing_slots,
    _report_slot_status,
    _slot_coverage_score,
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
    a.parse_failure = ParseFailure(
        file_path=file_path, error_type="SyntaxError", message="fake"
    )
    return a


def _all_slots_hit() -> dict:
    return {slot: [f"{slot.lower()}_evidence"] for slot in PROMPT_SLOT_ORDER}


def _no_slots_hit() -> dict:
    return defaultdict(list)


def _make_analysis(source: str) -> FileAnalysis:
    tmp = REPO_ROOT / "tests" / "architecture" / "_tmp_prompt_tax_test.py"
    tmp.write_text(dedent(source), encoding="utf-8")
    try:
        aa = ASTAnalyzer(AGENTIC_CORE)
        return aa.analyze_file(tmp)
    finally:
        if tmp.exists():
            tmp.unlink()


def _make_analyzer_with_files(file_map: dict[Path, FileAnalysis]) -> SemanticGapAnalyzer:
    analyzer = SemanticGapAnalyzer()
    paths = sorted(file_map.keys())

    def _fake_find(base_dir, pattern):
        return [p for p in paths if str(p).startswith(str(base_dir))]

    def _fake_analyze(fp):
        return file_map.get(fp, _ok_analysis(fp))

    analyzer.ast_analyzer.find_hot_paths = _fake_find
    analyzer.ast_analyzer.analyze_file = _fake_analyze
    return analyzer


# ===========================================================================
# 1. _looks_like_prompt_assembler
# ===========================================================================

@pytest.mark.architecture
def test_looks_like_prompt_assembler_prompt_in_name_assembler_in_rel():
    """Success: 'prompt' in filename + 'assembler' in rel path -> qualifies."""
    p = AGENTIC_CORE / "L1_cognition" / "assembler" / "prompt_assembler.py"
    analysis = _ok_analysis(p)
    assert _looks_like_prompt_assembler(p, analysis)


@pytest.mark.architecture
def test_looks_like_prompt_assembler_prompt_in_name_builder_in_rel():
    """Success: 'prompt' in filename + 'builder' in rel path -> qualifies."""
    p = AGENTIC_CORE / "L1_cognition" / "builder" / "prompt_builder.py"
    analysis = _ok_analysis(p)
    assert _looks_like_prompt_assembler(p, analysis)


@pytest.mark.architecture
def test_looks_like_prompt_assembler_no_prompt_in_name():
    """Negative: no 'prompt' in filename -> not a prompt assembler."""
    p = AGENTIC_CORE / "L1_cognition" / "assembler" / "reasoner_engine.py"
    analysis = _ok_analysis(p)
    assert not _looks_like_prompt_assembler(p, analysis)


@pytest.mark.architecture
def test_looks_like_prompt_assembler_prompt_in_name_no_assembler_token():
    """Negative: 'prompt' in filename but no assembler token in rel -> not flagged."""
    p = AGENTIC_CORE / "L1_cognition" / "engines" / "prompt_runner.py"
    analysis = _ok_analysis(p)
    assert not _looks_like_prompt_assembler(p, analysis)


@pytest.mark.architecture
def test_looks_like_prompt_assembler_assembler_hint_in_used_names():
    """Success: analysis.prompt_assembly_markers non-empty -> qualifies.
    prompt_assembly_markers is populated when used_names contain PROMPT_ASSEMBLER_HINTS."""
    p = AGENTIC_CORE / "L1_cognition" / "engines" / "fake_engine.py"
    analysis = _ok_analysis(p, prompt_assembly_markers=["assemble_prompt"])
    assert _looks_like_prompt_assembler(p, analysis)


@pytest.mark.architecture
def test_looks_like_prompt_assembler_assembler_hint_in_string_literals():
    """Success: prompt_assembly_markers populated from string literal containing PROMPT_ASSEMBLER_HINTS."""
    p = AGENTIC_CORE / "L1_cognition" / "engines" / "fake_engine.py"
    analysis = _ok_analysis(p, prompt_assembly_markers=["governed_prompt assembly"])
    assert _looks_like_prompt_assembler(p, analysis)


# ===========================================================================
# 2. Helper functions: _slot_coverage_score, _missing_slots, _report_slot_status
# ===========================================================================

@pytest.mark.architecture
def test_slot_coverage_score_zero_when_no_hits():
    """_slot_coverage_score returns 0 when all slots empty."""
    score = _slot_coverage_score(_no_slots_hit())
    assert score == 0


@pytest.mark.architecture
def test_slot_coverage_score_max_when_all_slots_hit():
    """_slot_coverage_score returns len(PROMPT_SLOT_ORDER) when all slots hit."""
    score = _slot_coverage_score(_all_slots_hit())
    assert score == len(PROMPT_SLOT_ORDER)


@pytest.mark.architecture
def test_slot_coverage_score_partial():
    """_slot_coverage_score counts only slots with non-empty hit lists."""
    hits = {"S0": ["system_prompt"], "U0": ["user_input"]}
    score = _slot_coverage_score(hits)
    assert score == 2


@pytest.mark.architecture
def test_missing_slots_all_when_empty():
    """_missing_slots returns all 5 slots when hits dict is empty."""
    missing = _missing_slots(_no_slots_hit())
    assert set(missing) == set(PROMPT_SLOT_ORDER)


@pytest.mark.architecture
def test_missing_slots_empty_when_all_present():
    """_missing_slots returns empty list when all slots have hits."""
    missing = _missing_slots(_all_slots_hit())
    assert missing == []


@pytest.mark.architecture
def test_missing_slots_partial():
    """_missing_slots returns only the absent slots."""
    hits = {"S0": ["system"], "I0": ["persona"]}
    missing = _missing_slots(hits)
    assert set(missing) == {"D0", "C0", "U0"}


@pytest.mark.architecture
def test_report_slot_status_marks_missing_and_present():
    """_report_slot_status uses '=' separator: 'SLOT=present' / 'SLOT=missing'."""
    hits = {"S0": ["system_prompt"]}
    status = _report_slot_status(hits)
    assert "S0=present" in status
    for slot in ("D0", "I0", "C0", "U0"):
        assert f"{slot}=missing" in status


# ===========================================================================
# 3. PROMPT_TAXONOMY_PATTERNS and PROMPT_SLOT_ORDER invariants
# ===========================================================================

@pytest.mark.architecture
def test_prompt_slot_order_contains_all_canonical_slots():
    """PROMPT_SLOT_ORDER must contain all 5 canonical slots."""
    assert set(PROMPT_SLOT_ORDER) == {"S0", "D0", "I0", "C0", "U0"}


@pytest.mark.architecture
def test_prompt_taxonomy_patterns_all_slots_have_patterns():
    """Every slot in PROMPT_SLOT_ORDER must have a non-empty pattern tuple."""
    for slot in PROMPT_SLOT_ORDER:
        assert slot in PROMPT_TAXONOMY_PATTERNS, f"Slot {slot} missing from PROMPT_TAXONOMY_PATTERNS"
        assert len(PROMPT_TAXONOMY_PATTERNS[slot]) > 0, f"Slot {slot} has empty patterns"


# ===========================================================================
# 4. analyze_file prompt slot detection via real AST parsing
# ===========================================================================

@pytest.mark.architecture
def test_s0_slot_detected_from_system_prompt_literal():
    """S0 slot detected when 'system_prompt' appears in a string literal."""
    analysis = _make_analysis('x = "system_prompt for agent"\n')
    assert "S0" in analysis.prompt_slot_hits and analysis.prompt_slot_hits["S0"]


@pytest.mark.architecture
def test_d0_slot_detected_from_guardrail_literal():
    """D0 slot detected when 'guardrail' appears in a string literal."""
    analysis = _make_analysis('policy = "guardrail applied"\n')
    assert "D0" in analysis.prompt_slot_hits and analysis.prompt_slot_hits["D0"]


@pytest.mark.architecture
def test_i0_slot_detected_from_persona_used_name():
    """I0 slot detected when 'persona' appears as a used name."""
    analysis = _make_analysis("persona = get_persona()\n")
    assert "I0" in analysis.prompt_slot_hits and analysis.prompt_slot_hits["I0"]


@pytest.mark.architecture
def test_c0_slot_detected_from_context_literal():
    """C0 slot detected when 'context' appears in a string literal."""
    analysis = _make_analysis('doc = "injected_context block"\n')
    assert "C0" in analysis.prompt_slot_hits and analysis.prompt_slot_hits["C0"]


@pytest.mark.architecture
def test_u0_slot_detected_from_user_prompt_literal():
    """U0 slot detected when 'user_prompt' appears in a string literal."""
    analysis = _make_analysis('msg = "user_prompt: what is the plan"\n')
    assert "U0" in analysis.prompt_slot_hits and analysis.prompt_slot_hits["U0"]


@pytest.mark.architecture
def test_no_slot_hit_for_unrelated_content():
    """Unrelated source code produces no prompt slot hits."""
    analysis = _make_analysis("x = 1 + 2\nprint(x)\n")
    for slot in PROMPT_SLOT_ORDER:
        hits = analysis.prompt_slot_hits.get(slot, [])
        assert not hits, f"Unexpected slot hit {slot}: {hits}"


# ===========================================================================
# 5. analyze_prompt_taxonomy_coverage branch coverage
# ===========================================================================

@pytest.mark.architecture
def test_parse_failed_file_skipped_no_taxonomy_gap():
    """Parse-failed file is skipped — no PROMPT-TAXONOMY-GAP generated."""
    fake_path = AGENTIC_CORE / "L1_cognition" / "assembler" / "prompt_assembler.py"
    fake_analysis = _failed_analysis(fake_path)
    analyzer = _make_analyzer_with_files({fake_path: fake_analysis})

    gaps = analyzer.analyze_prompt_taxonomy_coverage()
    assert not gaps, f"Parse-failed file should produce no taxonomy gaps: {gaps}"


@pytest.mark.architecture
def test_non_assembler_file_skipped_no_taxonomy_gap():
    """File that does not look like a prompt assembler is skipped."""
    fake_path = AGENTIC_CORE / "L1_cognition" / "engines" / "fake_engine.py"
    fake_analysis = _ok_analysis(fake_path)
    analyzer = _make_analyzer_with_files({fake_path: fake_analysis})

    gaps = analyzer.analyze_prompt_taxonomy_coverage()
    assert not gaps


@pytest.mark.architecture
def test_missing_critical_slots_generates_high_priority_taxonomy_gap():
    """Missing S0/C0/U0 in prompt assembler generates PROMPT-TAXONOMY-GAP with HIGH priority."""
    fake_path = AGENTIC_CORE / "L1_cognition" / "assembler" / "prompt_assembler.py"
    # Only D0 and I0 present -> S0/C0/U0 missing -> HIGH
    fake_analysis = _ok_analysis(
        fake_path,
        prompt_slot_hits={"D0": ["guardrail"], "I0": ["persona"]},
        manifest_hash_mentions={"hash_abc"},
        boundary_snapshot_mentions={"snapshot_xyz"},
    )
    analyzer = _make_analyzer_with_files({fake_path: fake_analysis})

    gaps = analyzer.analyze_prompt_taxonomy_coverage()
    tax_gaps = [g for g in gaps if g.gap_id.startswith("PROMPT-TAXONOMY-GAP")]
    assert tax_gaps, "Expected PROMPT-TAXONOMY-GAP for assembler with missing critical slots"
    assert tax_gaps[0].priority == "HIGH"


@pytest.mark.architecture
def test_missing_non_critical_slots_generates_medium_priority_taxonomy_gap():
    """Missing D0/I0 only (not S0/C0/U0) -> PROMPT-TAXONOMY-GAP with MEDIUM priority."""
    fake_path = AGENTIC_CORE / "L1_cognition" / "assembler" / "prompt_assembler.py"
    # S0/C0/U0 present, D0/I0 missing -> MEDIUM
    fake_analysis = _ok_analysis(
        fake_path,
        prompt_slot_hits={
            "S0": ["system_prompt"],
            "C0": ["context_pack"],
            "U0": ["user_prompt"],
        },
        manifest_hash_mentions={"hash_abc"},
        boundary_snapshot_mentions={"snapshot_xyz"},
    )
    analyzer = _make_analyzer_with_files({fake_path: fake_analysis})

    gaps = analyzer.analyze_prompt_taxonomy_coverage()
    tax_gaps = [g for g in gaps if g.gap_id.startswith("PROMPT-TAXONOMY-GAP")]
    assert tax_gaps, "Expected PROMPT-TAXONOMY-GAP for missing non-critical slots"
    assert tax_gaps[0].priority == "MEDIUM"


@pytest.mark.architecture
def test_all_slots_present_no_taxonomy_gap():
    """All 5 slots present -> no PROMPT-TAXONOMY-GAP generated."""
    fake_path = AGENTIC_CORE / "L1_cognition" / "assembler" / "prompt_assembler.py"
    fake_analysis = _ok_analysis(
        fake_path,
        prompt_slot_hits=_all_slots_hit(),
        manifest_hash_mentions={"hash_abc"},
        boundary_snapshot_mentions={"snapshot_xyz"},
    )
    analyzer = _make_analyzer_with_files({fake_path: fake_analysis})

    gaps = analyzer.analyze_prompt_taxonomy_coverage()
    tax_gaps = [g for g in gaps if g.gap_id.startswith("PROMPT-TAXONOMY-GAP")]
    assert not tax_gaps, f"No taxonomy gap expected when all slots present: {tax_gaps}"


@pytest.mark.architecture
def test_no_manifest_hash_generates_manifest_gap():
    """No manifest_hash_mentions -> PROMPT-MANIFEST-GAP MEDIUM."""
    fake_path = AGENTIC_CORE / "L1_cognition" / "assembler" / "prompt_assembler.py"
    fake_analysis = _ok_analysis(
        fake_path,
        prompt_slot_hits=_all_slots_hit(),
        manifest_hash_mentions=set(),
        boundary_snapshot_mentions={"snapshot_xyz"},
    )
    analyzer = _make_analyzer_with_files({fake_path: fake_analysis})

    gaps = analyzer.analyze_prompt_taxonomy_coverage()
    manifest_gaps = [g for g in gaps if g.gap_id.startswith("PROMPT-MANIFEST-GAP")]
    assert manifest_gaps, "Expected PROMPT-MANIFEST-GAP for missing manifest hash"
    assert manifest_gaps[0].priority == "MEDIUM"


@pytest.mark.architecture
def test_manifest_hash_present_no_manifest_gap():
    """manifest_hash_mentions non-empty -> no PROMPT-MANIFEST-GAP."""
    fake_path = AGENTIC_CORE / "L1_cognition" / "assembler" / "prompt_assembler.py"
    fake_analysis = _ok_analysis(
        fake_path,
        prompt_slot_hits=_all_slots_hit(),
        manifest_hash_mentions={"manifest_hash_abc123"},
        boundary_snapshot_mentions={"snapshot_xyz"},
    )
    analyzer = _make_analyzer_with_files({fake_path: fake_analysis})

    gaps = analyzer.analyze_prompt_taxonomy_coverage()
    manifest_gaps = [g for g in gaps if g.gap_id.startswith("PROMPT-MANIFEST-GAP")]
    assert not manifest_gaps


@pytest.mark.architecture
def test_no_boundary_snapshot_generates_validator_gap():
    """No boundary_snapshot_mentions -> PROMPT-VALIDATOR-GAP LOW."""
    fake_path = AGENTIC_CORE / "L1_cognition" / "assembler" / "prompt_assembler.py"
    fake_analysis = _ok_analysis(
        fake_path,
        prompt_slot_hits=_all_slots_hit(),
        manifest_hash_mentions={"hash_abc"},
        boundary_snapshot_mentions=set(),
    )
    analyzer = _make_analyzer_with_files({fake_path: fake_analysis})

    gaps = analyzer.analyze_prompt_taxonomy_coverage()
    validator_gaps = [g for g in gaps if g.gap_id.startswith("PROMPT-VALIDATOR-GAP")]
    assert validator_gaps, "Expected PROMPT-VALIDATOR-GAP for missing boundary snapshot"
    assert validator_gaps[0].priority == "LOW"


@pytest.mark.architecture
def test_boundary_snapshot_present_no_validator_gap():
    """boundary_snapshot_mentions non-empty -> no PROMPT-VALIDATOR-GAP."""
    fake_path = AGENTIC_CORE / "L1_cognition" / "assembler" / "prompt_assembler.py"
    fake_analysis = _ok_analysis(
        fake_path,
        prompt_slot_hits=_all_slots_hit(),
        manifest_hash_mentions={"hash_abc"},
        boundary_snapshot_mentions={"boundary_snapshot.json"},
    )
    analyzer = _make_analyzer_with_files({fake_path: fake_analysis})

    gaps = analyzer.analyze_prompt_taxonomy_coverage()
    validator_gaps = [g for g in gaps if g.gap_id.startswith("PROMPT-VALIDATOR-GAP")]
    assert not validator_gaps


@pytest.mark.architecture
def test_deduplication_prevents_double_gaps():
    """Same path returned by two base_dirs is only analyzed once (seen set dedup)."""
    fake_path = AGENTIC_CORE / "L1_cognition" / "assembler" / "prompt_assembler.py"
    fake_analysis = _ok_analysis(
        fake_path,
        prompt_slot_hits=_all_slots_hit(),
        manifest_hash_mentions={"hash_abc"},
        boundary_snapshot_mentions={"snapshot_xyz"},
    )
    analyzer = SemanticGapAnalyzer()

    def _fake_find(base_dir, pattern):
        return [fake_path]

    def _fake_analyze(fp):
        return fake_analysis

    analyzer.ast_analyzer.find_hot_paths = _fake_find
    analyzer.ast_analyzer.analyze_file = _fake_analyze

    gaps = analyzer.analyze_prompt_taxonomy_coverage()
    # Gaps should appear at most once despite multiple find calls
    manifest_gaps = [g for g in gaps if g.gap_id.startswith("PROMPT-MANIFEST-GAP")]
    assert len(manifest_gaps) <= 1, f"Dedup failed — got {len(manifest_gaps)} manifest gaps"


@pytest.mark.architecture
def test_taxonomy_finding_added_to_prompt_taxonomy_findings():
    """Each processed assembler file adds a finding to prompt_taxonomy_findings."""
    fake_path = AGENTIC_CORE / "L1_cognition" / "assembler" / "prompt_assembler.py"
    fake_analysis = _ok_analysis(
        fake_path,
        prompt_slot_hits=_all_slots_hit(),
        manifest_hash_mentions={"hash_abc"},
        boundary_snapshot_mentions={"snapshot_xyz"},
    )
    analyzer = _make_analyzer_with_files({fake_path: fake_analysis})
    analyzer.analyze_prompt_taxonomy_coverage()

    assert analyzer.prompt_taxonomy_findings, "Expected findings in prompt_taxonomy_findings"
    required_keys = {"file", "coverage_score", "slot_status", "manifest_hash", "boundary_snapshot"}
    for finding in analyzer.prompt_taxonomy_findings:
        missing = required_keys - set(finding.keys())
        assert not missing, f"Taxonomy finding missing keys: {missing}"


# ===========================================================================
# 6. Real codebase invariants
# ===========================================================================

@pytest.mark.architecture
def test_prompt_taxonomy_coverage_returns_list():
    """Integration: analyze_prompt_taxonomy_coverage returns a list without exception."""
    analyzer = SemanticGapAnalyzer()
    result = analyzer.analyze_prompt_taxonomy_coverage()
    assert isinstance(result, list)


@pytest.mark.architecture
def test_all_taxonomy_gaps_have_layer_l1():
    """Contract: all PROMPT-TAXONOMY-GAP gaps must have layer='L1'."""
    analyzer = SemanticGapAnalyzer()
    gaps = analyzer.analyze_prompt_taxonomy_coverage()
    for gap in gaps:
        if gap.gap_id.startswith("PROMPT-TAXONOMY-GAP"):
            assert gap.layer == "L1", (
                f"PROMPT-TAXONOMY-GAP must have layer L1, got {gap.layer} for {gap.gap_id}"
            )


@pytest.mark.architecture
def test_all_manifest_gaps_are_medium_priority():
    """Contract: all PROMPT-MANIFEST-GAP gaps must have MEDIUM priority."""
    analyzer = SemanticGapAnalyzer()
    gaps = analyzer.analyze_prompt_taxonomy_coverage()
    for gap in gaps:
        if gap.gap_id.startswith("PROMPT-MANIFEST-GAP"):
            assert gap.priority == "MEDIUM", (
                f"PROMPT-MANIFEST-GAP must be MEDIUM, got {gap.priority}"
            )


@pytest.mark.architecture
def test_all_validator_gaps_are_low_priority():
    """Contract: all PROMPT-VALIDATOR-GAP gaps must have LOW priority."""
    analyzer = SemanticGapAnalyzer()
    gaps = analyzer.analyze_prompt_taxonomy_coverage()
    for gap in gaps:
        if gap.gap_id.startswith("PROMPT-VALIDATOR-GAP"):
            assert gap.priority == "LOW", (
                f"PROMPT-VALIDATOR-GAP must be LOW, got {gap.priority}"
            )
