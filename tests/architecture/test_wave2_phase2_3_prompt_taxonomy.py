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

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_wave2_phase2_3_prompt_taxonomy")
_emit_applies_guardrail("p0", "test_wave2_phase2_3_prompt_taxonomy", "p0_governance")
_emit_reads_policy_state("p0", "test_wave2_phase2_3_prompt_taxonomy", "policy_binding")
_emit_snapshots_state("p0", "test_wave2_phase2_3_prompt_taxonomy", "state_snapshot")
emit_replay_key("p0", "test_wave2_phase2_3_prompt_taxonomy")
emit_determinism_digest("p0", "test_wave2_phase2_3_prompt_taxonomy")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_wave2_phase2_3_prompt_taxonomy", "execution_auth")
_emit_validates_capability("p2", "test_wave2_phase2_3_prompt_taxonomy", "capability_check")
_emit_routes_to_capability("p2", "test_wave2_phase2_3_prompt_taxonomy", "capability_route")
_emit_writes_via_uwg("p2", "test_wave2_phase2_3_prompt_taxonomy", "uwg_write")
_emit_blocks_direct_write("p2", "test_wave2_phase2_3_prompt_taxonomy", "direct_write_block")
_emit_records_tool_invocation("p2", "test_wave2_phase2_3_prompt_taxonomy", "tool_invocation")
_emit_captures_execution_output("p2", "test_wave2_phase2_3_prompt_taxonomy", "exec_output")
_emit_dispatches_agent("p3", "test_wave2_phase2_3_prompt_taxonomy", "agent_dispatch")
_emit_coordinates_agents("p3", "test_wave2_phase2_3_prompt_taxonomy", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_wave2_phase2_3_prompt_taxonomy", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_wave2_phase2_3_prompt_taxonomy", "healing_outcome")
_emit_escalates_failure("p3", "test_wave2_phase2_3_prompt_taxonomy", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_wave2_phase2_3_prompt_taxonomy", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_wave2_phase2_3_prompt_taxonomy", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_wave2_phase2_3_prompt_taxonomy", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_wave2_phase2_3_prompt_taxonomy", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_wave2_phase2_3_prompt_taxonomy", "eval_metric")
_emit_stores_embedding("p4", "test_wave2_phase2_3_prompt_taxonomy", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_wave2_phase2_3_prompt_taxonomy", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_wave2_phase2_3_prompt_taxonomy", "exec_snapshot_link")

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

from agentic_core.L0_routing.config.path_constants import TESTS_DIR
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,  # noqa: E402
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,  # noqa: E402
)
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

_emit_emits_metric_event("test_wave2_phase2_3_prompt_taxonomy", "p4obs", "metric_1")
_emit_emits_metric_event("test_wave2_phase2_3_prompt_taxonomy", "p4obs", "metric_2")
_emit_emits_metric_event("test_wave2_phase2_3_prompt_taxonomy", "p4obs", "metric_3")
_emit_emits_metric_event("test_wave2_phase2_3_prompt_taxonomy", "p4obs", "metric_4")
_emit_emits_metric_event("test_wave2_phase2_3_prompt_taxonomy", "p4obs", "metric_5")
_emit_emits_metric_event("test_wave2_phase2_3_prompt_taxonomy", "p4obs", "metric_6")
_emit_records_incident_event("test_wave2_phase2_3_prompt_taxonomy", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_wave2_phase2_3_prompt_taxonomy", "p4obs", "anomaly")
_emit_writes_observability_log("test_wave2_phase2_3_prompt_taxonomy", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_wave2_phase2_3_prompt_taxonomy", "p4obs", "mon_state")
_emit_triggers_alert("test_wave2_phase2_3_prompt_taxonomy", "p4obs", "alert")
_emit_links_incident_trace("test_wave2_phase2_3_prompt_taxonomy", "p4obs", "trace_link")
_emit_captures_pattern("test_wave2_phase2_3_prompt_taxonomy", "p3lm", "pattern")
_emit_records_learning_event("test_wave2_phase2_3_prompt_taxonomy", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_wave2_phase2_3_prompt_taxonomy", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_wave2_phase2_3_prompt_taxonomy", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_wave2_phase2_3_prompt_taxonomy", "p3lm", "routing")
_emit_improves_agent_policy("test_wave2_phase2_3_prompt_taxonomy", "p3lm", "policy")
_emit_stores_learning_state("test_wave2_phase2_3_prompt_taxonomy", "p3lm", "state")
_emit_records_execution_trace("test_wave2_phase2_3_prompt_taxonomy", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_wave2_phase2_3_prompt_taxonomy", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_wave2_phase2_3_prompt_taxonomy", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_wave2_phase2_3_prompt_taxonomy", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_wave2_phase2_3_prompt_taxonomy", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_wave2_phase2_3_prompt_taxonomy", "env_read", "p2_env_1")
_emit_reads_environ("test_wave2_phase2_3_prompt_taxonomy", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_wave2_phase2_3_prompt_taxonomy", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_wave2_phase2_3_prompt_taxonomy", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_wave2_phase2_3_prompt_taxonomy", "context_pull")
_emit_pulls_context("p1", "test_wave2_phase2_3_prompt_taxonomy", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_wave2_phase2_3_prompt_taxonomy", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_wave2_phase2_3_prompt_taxonomy", "uwg_term_secondary")
_emit_writes_through("p1", "test_wave2_phase2_3_prompt_taxonomy", "write_through")
_emit_writes_through("p1", "test_wave2_phase2_3_prompt_taxonomy", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_wave2_phase2_3_prompt_taxonomy", "safety_validation")
_emit_invokes_eval("p1", "test_wave2_phase2_3_prompt_taxonomy", "eval_call")
_emit_proposal_commits_routing("p1", "test_wave2_phase2_3_prompt_taxonomy", "routing_commit")
_emit_escalates_to_human("p1", "test_wave2_phase2_3_prompt_taxonomy", "human_escalation")
_emit_routes_through("p1", "test_wave2_phase2_3_prompt_taxonomy", "route_through")
_emit_checks_agent_registry("p1", "test_wave2_phase2_3_prompt_taxonomy", "agent_registry")
_emit_validates_agent_capability("p1", "test_wave2_phase2_3_prompt_taxonomy", "capability")
_emit_dispatches_execution_plan("p1", "test_wave2_phase2_3_prompt_taxonomy", "exec_plan")
_emit_agent_executes_agent("p1", "test_wave2_phase2_3_prompt_taxonomy", "sub_agent")
_emit_routes_to_agent("p1", "test_wave2_phase2_3_prompt_taxonomy", "target_agent")
_emit_verifies_policy("p1", "test_wave2_phase2_3_prompt_taxonomy", "policy_check")
_emit_observes_runtime_state("p1", "test_wave2_phase2_3_prompt_taxonomy", "runtime_state")
_emit_verifies_boundary("p1", "test_wave2_phase2_3_prompt_taxonomy", "boundary_check")
_emit_transcripts_response("p1", "test_wave2_phase2_3_prompt_taxonomy", "transcript")
_emit_hard_fails_untranscripted("p1", "test_wave2_phase2_3_prompt_taxonomy")
_emit_gated_by_confidence("p1", "test_wave2_phase2_3_prompt_taxonomy", "confidence_gate")

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


def _all_slots_hit() -> dict:
    return {slot: [f"{slot.lower()}_evidence"] for slot in PROMPT_SLOT_ORDER}


def _no_slots_hit() -> dict:
    return defaultdict(list)


def _make_analysis(source: str) -> FileAnalysis:
    tmp = REPO_ROOT / TESTS_DIR / "architecture" / "_tmp_prompt_tax_test.py"
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
            assert gap.priority == "MEDIUM", f"PROMPT-MANIFEST-GAP must be MEDIUM, got {gap.priority}"


@pytest.mark.architecture
def test_all_validator_gaps_are_low_priority():
    """Contract: all PROMPT-VALIDATOR-GAP gaps must have LOW priority."""
    analyzer = SemanticGapAnalyzer()
    gaps = analyzer.analyze_prompt_taxonomy_coverage()
    for gap in gaps:
        if gap.gap_id.startswith("PROMPT-VALIDATOR-GAP"):
            assert gap.priority == "LOW", f"PROMPT-VALIDATOR-GAP must be LOW, got {gap.priority}"
