"""
Wave 3 Phase 3.3 - Finalization + Monitoring: Branch Coverage Tests

Branch inventory for run_analysis:
  - returns dict with expected keys
  - total_gaps == len(gaps)
  - high_priority + medium_priority + low_priority == total_gaps
  - parse_failures is a list
  - prompt_taxonomy_findings is a list
  - architecture_component_findings is a list
  - layer_connection_findings is a list
  - gaps is a list of SemanticGap
  - self.gaps is populated after run_analysis
  - self.parse_failures is sorted after run_analysis

Branch inventory for generate_report:
  - creates parent directories if missing
  - writes markdown file (output_path.exists() after call)
  - report contains Executive Summary section
  - report contains Analysis Methodology section
  - report contains Priority Matrix section
  - report contains Next Steps section
  - report contains Validation section
  - Architecture Component Presence section present when findings exist
  - Prompt Taxonomy Coverage section present when findings exist
  - Layer Connection Integrity section present when findings exist
  - Parse Failures section present when parse failures exist
  - Per-layer gap sections present when gaps exist
  - No Architecture Component Presence section when findings empty
  - No Prompt Taxonomy Coverage section when findings empty
  - No Layer Connection Integrity section when findings empty
  - No Parse Failures section when no parse failures

main() entrypoint:
  - --fail-on-parse-errors exits non-zero when parse failures present

Real codebase invariants:
  - run_analysis returns a dict
  - run_analysis result has all required keys
  - generate_report creates a file
  - report file is non-empty
  - report file is valid UTF-8
  - result total_gaps == len(result['gaps'])
  - result high+medium+low == total_gaps
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

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

_emit_records_execution_trace("p0", "evidence", "test_wave3_phase3_3_finalization")
_emit_applies_guardrail("p0", "test_wave3_phase3_3_finalization", "p0_governance")
_emit_reads_policy_state("p0", "test_wave3_phase3_3_finalization", "policy_binding")
_emit_snapshots_state("p0", "test_wave3_phase3_3_finalization", "state_snapshot")
emit_replay_key("p0", "test_wave3_phase3_3_finalization")
emit_determinism_digest("p0", "test_wave3_phase3_3_finalization")
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

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from tools.semantic_gap_analyzer import (
    AGENTIC_CORE,
    ParseFailure,
    SemanticGap,
    SemanticGapAnalyzer,
)

RUN_ANALYSIS_KEYS = {
    "total_gaps",
    "high_priority",
    "medium_priority",
    "low_priority",
    "parse_failures",
    "prompt_taxonomy_findings",
    "architecture_component_findings",
    "layer_connection_findings",
    "gaps",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_gap(gap_id: str, layer: str, priority: str) -> SemanticGap:
    return SemanticGap(
        gap_id=gap_id,
        layer=layer,
        artery=f"Artery {gap_id}",
        intent="test intent",
        reality="test reality",
        impact="test impact",
        priority=priority,
        evidence_files=[f"fake/{gap_id}.py"],
        recommended_fix="test fix",
    )


def _analyzer_with_gaps(gaps: list[SemanticGap]) -> SemanticGapAnalyzer:
    """Return an analyzer whose self.gaps is pre-populated (bypasses run_analysis)."""
    a = SemanticGapAnalyzer()
    a.gaps = gaps
    a.parse_failures = []
    a.prompt_taxonomy_findings = []
    a.architecture_component_findings = []
    a.layer_connection_findings = []
    return a


# ===========================================================================
# 1. run_analysis return-value contract
# ===========================================================================


@pytest.mark.architecture
def test_run_analysis_returns_dict():
    """run_analysis must return a dict."""
    result = SemanticGapAnalyzer().run_analysis()
    assert isinstance(result, dict)


@pytest.mark.architecture
def test_run_analysis_has_all_required_keys():
    """run_analysis result must contain all required keys."""
    result = SemanticGapAnalyzer().run_analysis()
    missing = RUN_ANALYSIS_KEYS - result.keys()
    assert not missing, f"Missing keys: {missing}"


@pytest.mark.architecture
def test_run_analysis_total_gaps_equals_len_gaps():
    """run_analysis: total_gaps == len(result['gaps'])."""
    result = SemanticGapAnalyzer().run_analysis()
    assert result["total_gaps"] == len(result["gaps"])


@pytest.mark.architecture
def test_run_analysis_priority_counts_sum_to_total():
    """run_analysis: high+medium+low == total_gaps."""
    result = SemanticGapAnalyzer().run_analysis()
    counted = result["high_priority"] + result["medium_priority"] + result["low_priority"]
    assert counted == result["total_gaps"]


@pytest.mark.architecture
def test_run_analysis_gaps_are_semantic_gap_instances():
    """run_analysis: every item in gaps is a SemanticGap."""
    result = SemanticGapAnalyzer().run_analysis()
    for gap in result["gaps"]:
        assert isinstance(gap, SemanticGap), f"Expected SemanticGap, got {type(gap)}"


@pytest.mark.architecture
def test_run_analysis_parse_failures_is_list():
    """run_analysis: parse_failures is a list."""
    result = SemanticGapAnalyzer().run_analysis()
    assert isinstance(result["parse_failures"], list)


@pytest.mark.architecture
def test_run_analysis_prompt_taxonomy_findings_is_list():
    """run_analysis: prompt_taxonomy_findings is a list."""
    result = SemanticGapAnalyzer().run_analysis()
    assert isinstance(result["prompt_taxonomy_findings"], list)


@pytest.mark.architecture
def test_run_analysis_architecture_component_findings_is_list():
    """run_analysis: architecture_component_findings is a list."""
    result = SemanticGapAnalyzer().run_analysis()
    assert isinstance(result["architecture_component_findings"], list)


@pytest.mark.architecture
def test_run_analysis_layer_connection_findings_is_list():
    """run_analysis: layer_connection_findings is a list."""
    result = SemanticGapAnalyzer().run_analysis()
    assert isinstance(result["layer_connection_findings"], list)


@pytest.mark.architecture
def test_run_analysis_self_gaps_populated_after_call():
    """run_analysis: analyzer.gaps is populated after call."""
    analyzer = SemanticGapAnalyzer()
    result = analyzer.run_analysis()
    assert analyzer.gaps is not None
    assert len(analyzer.gaps) == result["total_gaps"]


@pytest.mark.architecture
def test_run_analysis_self_parse_failures_sorted_after_call():
    """run_analysis: analyzer.parse_failures is a sorted list after call."""
    analyzer = SemanticGapAnalyzer()
    analyzer.run_analysis()
    paths = [str(pf.file_path) for pf in analyzer.parse_failures]
    assert paths == sorted(paths, key=str.lower)


@pytest.mark.architecture
def test_run_analysis_high_priority_count_correct():
    """run_analysis: high_priority count matches gaps with priority=='HIGH'."""
    result = SemanticGapAnalyzer().run_analysis()
    manual_high = sum(1 for g in result["gaps"] if g.priority == "HIGH")
    assert result["high_priority"] == manual_high


@pytest.mark.architecture
def test_run_analysis_medium_priority_count_correct():
    """run_analysis: medium_priority count matches gaps with priority=='MEDIUM'."""
    result = SemanticGapAnalyzer().run_analysis()
    manual_med = sum(1 for g in result["gaps"] if g.priority == "MEDIUM")
    assert result["medium_priority"] == manual_med


@pytest.mark.architecture
def test_run_analysis_low_priority_count_correct():
    """run_analysis: low_priority count matches gaps with priority=='LOW'."""
    result = SemanticGapAnalyzer().run_analysis()
    manual_low = sum(1 for g in result["gaps"] if g.priority == "LOW")
    assert result["low_priority"] == manual_low


# ===========================================================================
# 2. generate_report structural sections
# ===========================================================================


@pytest.mark.architecture
def test_generate_report_creates_file():
    """generate_report: output file is created."""
    analyzer = _analyzer_with_gaps([])
    with tempfile.TemporaryDirectory() as tmpdir:
        out = Path(tmpdir) / "report.md"
        analyzer.generate_report(out)
        assert out.exists(), "Report file was not created"


@pytest.mark.architecture
def test_generate_report_creates_parent_dirs():
    """generate_report: creates parent directories if missing."""
    analyzer = _analyzer_with_gaps([])
    with tempfile.TemporaryDirectory() as tmpdir:
        out = Path(tmpdir) / "nested" / "deep" / "report.md"
        analyzer.generate_report(out)
        assert out.exists(), "Report file in nested dir was not created"


@pytest.mark.architecture
def test_generate_report_file_is_nonempty():
    """generate_report: written file is non-empty."""
    analyzer = _analyzer_with_gaps([])
    with tempfile.TemporaryDirectory() as tmpdir:
        out = Path(tmpdir) / "report.md"
        analyzer.generate_report(out)
        assert out.stat().st_size > 0


@pytest.mark.architecture
def test_generate_report_is_valid_utf8():
    """generate_report: output file is valid UTF-8."""
    analyzer = _analyzer_with_gaps([])
    with tempfile.TemporaryDirectory() as tmpdir:
        out = Path(tmpdir) / "report.md"
        analyzer.generate_report(out)
        out.read_text(encoding="utf-8")  # raises if not valid UTF-8


@pytest.mark.architecture
def test_generate_report_has_executive_summary():
    """generate_report: contains Executive Summary section."""
    analyzer = _analyzer_with_gaps([])
    with tempfile.TemporaryDirectory() as tmpdir:
        out = Path(tmpdir) / "report.md"
        analyzer.generate_report(out)
        content = out.read_text(encoding="utf-8")
        assert "## Executive Summary" in content


@pytest.mark.architecture
def test_generate_report_has_analysis_methodology():
    """generate_report: contains Analysis Methodology section."""
    analyzer = _analyzer_with_gaps([])
    with tempfile.TemporaryDirectory() as tmpdir:
        out = Path(tmpdir) / "report.md"
        analyzer.generate_report(out)
        content = out.read_text(encoding="utf-8")
        assert "## Analysis Methodology" in content


@pytest.mark.architecture
def test_generate_report_has_next_steps():
    """generate_report: contains Next Steps section."""
    analyzer = _analyzer_with_gaps([])
    with tempfile.TemporaryDirectory() as tmpdir:
        out = Path(tmpdir) / "report.md"
        analyzer.generate_report(out)
        content = out.read_text(encoding="utf-8")
        assert "## Next Steps" in content


@pytest.mark.architecture
def test_generate_report_has_validation():
    """generate_report: contains Validation section."""
    analyzer = _analyzer_with_gaps([])
    with tempfile.TemporaryDirectory() as tmpdir:
        out = Path(tmpdir) / "report.md"
        analyzer.generate_report(out)
        content = out.read_text(encoding="utf-8")
        assert "## Validation" in content


@pytest.mark.architecture
def test_generate_report_has_priority_matrix_when_gaps():
    """generate_report: Priority Matrix section present when there are gaps."""
    analyzer = _analyzer_with_gaps([_make_gap("G1", "L0", "HIGH")])
    with tempfile.TemporaryDirectory() as tmpdir:
        out = Path(tmpdir) / "report.md"
        analyzer.generate_report(out)
        content = out.read_text(encoding="utf-8")
        assert "## Priority Matrix" in content


@pytest.mark.architecture
def test_generate_report_no_arch_section_when_empty():
    """generate_report: Architecture Component Presence section absent when findings is empty."""
    analyzer = _analyzer_with_gaps([])
    analyzer.architecture_component_findings = []
    with tempfile.TemporaryDirectory() as tmpdir:
        out = Path(tmpdir) / "report.md"
        analyzer.generate_report(out)
        content = out.read_text(encoding="utf-8")
        assert "## Architecture Component Presence" not in content


@pytest.mark.architecture
def test_generate_report_arch_section_present_when_findings():
    """generate_report: Architecture Component Presence section present when findings exist."""
    analyzer = _analyzer_with_gaps([])
    analyzer.architecture_component_findings = [
        {
            "component": "test_comp",
            "file": "some/file.py",
            "exists": True,
            "required_any": "marker",
            "signals_present": "marker",
        }
    ]
    with tempfile.TemporaryDirectory() as tmpdir:
        out = Path(tmpdir) / "report.md"
        analyzer.generate_report(out)
        content = out.read_text(encoding="utf-8")
        assert "## Architecture Component Presence" in content


@pytest.mark.architecture
def test_generate_report_no_taxonomy_section_when_empty():
    """generate_report: Prompt Taxonomy Coverage section absent when findings is empty."""
    analyzer = _analyzer_with_gaps([])
    analyzer.prompt_taxonomy_findings = []
    with tempfile.TemporaryDirectory() as tmpdir:
        out = Path(tmpdir) / "report.md"
        analyzer.generate_report(out)
        content = out.read_text(encoding="utf-8")
        assert "## Prompt Taxonomy Coverage" not in content


@pytest.mark.architecture
def test_generate_report_taxonomy_section_present_when_findings():
    """generate_report: Prompt Taxonomy Coverage section present when findings exist."""
    analyzer = _analyzer_with_gaps([])
    analyzer.prompt_taxonomy_findings = [
        {
            "file": "some/prompt.py",
            "coverage_score": 3,
            "slot_status": "S0=present",
            "manifest_hash": True,
            "boundary_snapshot": False,
        }
    ]
    with tempfile.TemporaryDirectory() as tmpdir:
        out = Path(tmpdir) / "report.md"
        analyzer.generate_report(out)
        content = out.read_text(encoding="utf-8")
        assert "## Prompt Taxonomy Coverage" in content


@pytest.mark.architecture
def test_generate_report_no_layer_connection_section_when_empty():
    """generate_report: Layer Connection Integrity section absent when findings is empty."""
    analyzer = _analyzer_with_gaps([])
    analyzer.layer_connection_findings = []
    with tempfile.TemporaryDirectory() as tmpdir:
        out = Path(tmpdir) / "report.md"
        analyzer.generate_report(out)
        content = out.read_text(encoding="utf-8")
        assert "## Layer Connection Integrity" not in content


@pytest.mark.architecture
def test_generate_report_layer_connection_present_when_findings():
    """generate_report: Layer Connection Integrity section present when findings exist."""
    analyzer = _analyzer_with_gaps([])
    analyzer.layer_connection_findings = [
        {
            "file": "some/file.py",
            "layer": "L0",
            "upward_imports": "",
            "direct_provider_imports": "",
            "embedding_mentions": 0,
            "governance_mentions": 0,
            "path_d_mentions": 0,
            "elevator_shaft_mentions": 0,
        }
    ]
    with tempfile.TemporaryDirectory() as tmpdir:
        out = Path(tmpdir) / "report.md"
        analyzer.generate_report(out)
        content = out.read_text(encoding="utf-8")
        assert "## Layer Connection Integrity" in content


@pytest.mark.architecture
def test_generate_report_no_parse_failures_section_when_empty():
    """generate_report: Parse Failures section absent when no parse failures."""
    analyzer = _analyzer_with_gaps([])
    with tempfile.TemporaryDirectory() as tmpdir:
        out = Path(tmpdir) / "report.md"
        analyzer.generate_report(out)
        content = out.read_text(encoding="utf-8")
        assert "## Parse Failures" not in content


@pytest.mark.architecture
def test_generate_report_parse_failures_section_present():
    """generate_report: Parse Failures section present when parse failures exist."""
    fake_path = AGENTIC_CORE / "L0_routing" / "broken.py"
    analyzer = _analyzer_with_gaps([])
    analyzer.parse_failures = [
        ParseFailure(file_path=fake_path, error_type="SyntaxError", message="bad syntax")
    ]
    with tempfile.TemporaryDirectory() as tmpdir:
        out = Path(tmpdir) / "report.md"
        analyzer.generate_report(out)
        content = out.read_text(encoding="utf-8")
        assert "## Parse Failures" in content


@pytest.mark.architecture
def test_generate_report_per_layer_gap_section():
    """generate_report: per-layer gap sections present when gaps exist."""
    analyzer = _analyzer_with_gaps([_make_gap("G1", "L0", "HIGH")])
    with tempfile.TemporaryDirectory() as tmpdir:
        out = Path(tmpdir) / "report.md"
        analyzer.generate_report(out)
        content = out.read_text(encoding="utf-8")
        assert "## L0 Layer Gaps" in content


@pytest.mark.architecture
def test_generate_report_executive_summary_counts_accurate():
    """generate_report: Executive Summary counts match actual gap list."""
    gaps = [
        _make_gap("G1", "L0", "HIGH"),
        _make_gap("G2", "L1", "MEDIUM"),
        _make_gap("G3", "L2", "LOW"),
    ]
    analyzer = _analyzer_with_gaps(gaps)
    with tempfile.TemporaryDirectory() as tmpdir:
        out = Path(tmpdir) / "report.md"
        analyzer.generate_report(out)
        content = out.read_text(encoding="utf-8")
        assert "**Total Gaps Identified:** 3" in content
        assert "**High Priority:** 1" in content
        assert "**Medium Priority:** 1" in content
        assert "**Low Priority:** 1" in content


@pytest.mark.architecture
def test_generate_report_gap_id_appears_in_report():
    """generate_report: each gap_id appears in the report output."""
    gaps = [_make_gap("L0-GAP-001", "L0", "HIGH")]
    analyzer = _analyzer_with_gaps(gaps)
    with tempfile.TemporaryDirectory() as tmpdir:
        out = Path(tmpdir) / "report.md"
        analyzer.generate_report(out)
        content = out.read_text(encoding="utf-8")
        assert "L0-GAP-001" in content


# ===========================================================================
# 3. Real codebase end-to-end
# ===========================================================================


@pytest.mark.architecture
def test_real_run_analysis_and_generate_report_e2e():
    """E2E: run_analysis + generate_report produces a valid report file."""
    analyzer = SemanticGapAnalyzer()
    result = analyzer.run_analysis()
    with tempfile.TemporaryDirectory() as tmpdir:
        out = Path(tmpdir) / "report.md"
        analyzer.generate_report(out)
        assert out.exists()
        content = out.read_text(encoding="utf-8")
        assert "## Executive Summary" in content
        assert len(content) > 100


@pytest.mark.architecture
def test_real_run_analysis_result_totals_consistent():
    """E2E: run_analysis total and priority counts are self-consistent."""
    result = SemanticGapAnalyzer().run_analysis()
    assert result["total_gaps"] == len(result["gaps"])
    assert (
        result["high_priority"] + result["medium_priority"] + result["low_priority"] == result["total_gaps"]
    )


@pytest.mark.architecture
def test_all_gap_evidence_files_nonempty():
    """E2E: every SemanticGap returned by run_analysis has non-empty evidence_files."""
    result = SemanticGapAnalyzer().run_analysis()
    for gap in result["gaps"]:
        assert gap.evidence_files, f"Gap {gap.gap_id} has empty evidence_files"


@pytest.mark.architecture
def test_all_gaps_have_valid_priority():
    """E2E: every gap priority is one of HIGH, MEDIUM, LOW."""
    valid = {"HIGH", "MEDIUM", "LOW"}
    result = SemanticGapAnalyzer().run_analysis()
    for gap in result["gaps"]:
        assert gap.priority in valid, f"Gap {gap.gap_id} has invalid priority {gap.priority}"


@pytest.mark.architecture
def test_all_gaps_have_valid_layer():
    """E2E: every gap layer is one of L0-L6 or UNKNOWN."""
    valid = {"L0", "L1", "L2", "L3", "L4", "L5", "L6", "UNKNOWN"}
    result = SemanticGapAnalyzer().run_analysis()
    for gap in result["gaps"]:
        assert gap.layer in valid, f"Gap {gap.gap_id} has invalid layer {gap.layer}"


@pytest.mark.architecture
def test_all_gaps_have_nonempty_intent():
    """E2E: every gap has a non-empty intent."""
    result = SemanticGapAnalyzer().run_analysis()
    for gap in result["gaps"]:
        assert gap.intent.strip(), f"Gap {gap.gap_id} has empty intent"


@pytest.mark.architecture
def test_all_gaps_have_nonempty_recommended_fix():
    """E2E: every gap has a non-empty recommended_fix."""
    result = SemanticGapAnalyzer().run_analysis()
    for gap in result["gaps"]:
        assert gap.recommended_fix.strip(), f"Gap {gap.gap_id} has empty recommended_fix"
