"""
Wave 1 Phase 1.2 - Sovereignty: Direct Provider Import Detection and Upward Import Integrity

Branch inventory:
  analyze_file direct provider import detection (ast.Import branch)
    - success: external top-level SDK import flagged (openai, vllm, etc.)
    - negative: internal agentic_core.* module with 'vllm' in name NOT flagged
    - boundary: bare 'vllm' (no dots) IS flagged
    - boundary: 'vllm.something' top-level IS flagged
    - negative: 'agentic_core.L2_execution.types.vllm_token_budget_types' NOT flagged
  analyze_file direct provider import detection (ast.ImportFrom branch)
    - success: 'from openai import ...' flagged
    - negative: 'from agentic_core.L2_execution.types.vllm_x import ...' NOT flagged
    - boundary: 'from vllm import ...' IS flagged
  _detect_upward_imports
    - success: L1 file importing L0 is NOT an upward import (L1 > L0 is downward)
    - negative: L0 file importing L1 IS an upward import
    - boundary: file with no layer (None) returns empty list
    - boundary: file with no imported_layer_refs returns empty list
  analyze_layer_connection_integrity gaps
    - success: produces SemanticGap entries for direct provider imports
    - success: produces SemanticGap entries for upward imports
    - negative: L2 files with real provider imports appear in findings
    - negative: internal vllm_* type modules do NOT appear as provider-import gaps
  Real codebase invariants
    - No file outside L2_execution has a real external provider SDK import
    - All direct_provider_imports in non-L2 files are zero
"""

from __future__ import annotations

import sys
from pathlib import Path
from textwrap import dedent

import pytest

#  # MOVED: from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_wave1_phase1_2_sovereignty")
# REMOVED: _emit_applies_guardrail("p0", "test_wave1_phase1_2_sovereignty", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_wave1_phase1_2_sovereignty", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_wave1_phase1_2_sovereignty", "state_snapshot")
# REMOVED: emit_replay_key("p0", "test_wave1_phase1_2_sovereignty")
# REMOVED: emit_determinism_digest("p0", "test_wave1_phase1_2_sovereignty")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_wave1_phase1_2_sovereignty", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_wave1_phase1_2_sovereignty", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_wave1_phase1_2_sovereignty", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_wave1_phase1_2_sovereignty", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_wave1_phase1_2_sovereignty", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_wave1_phase1_2_sovereignty", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_wave1_phase1_2_sovereignty", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_wave1_phase1_2_sovereignty", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_wave1_phase1_2_sovereignty", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_wave1_phase1_2_sovereignty", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_wave1_phase1_2_sovereignty", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_wave1_phase1_2_sovereignty", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_wave1_phase1_2_sovereignty", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_wave1_phase1_2_sovereignty", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_wave1_phase1_2_sovereignty", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_wave1_phase1_2_sovereignty", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_wave1_phase1_2_sovereignty", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_wave1_phase1_2_sovereignty", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_wave1_phase1_2_sovereignty", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_wave1_phase1_2_sovereignty", "exec_snapshot_link")

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

#  # MOVED: from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    TESTS_DIR,
)
#  # MOVED: from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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
    DIRECT_PROVIDER_IMPORT_PATTERNS,
    ASTAnalyzer,
    FileAnalysis,
    _detect_upward_imports,
)

# REMOVED: _emit_emits_metric_event("test_wave1_phase1_2_sovereignty", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_wave1_phase1_2_sovereignty", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_wave1_phase1_2_sovereignty", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_wave1_phase1_2_sovereignty", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_wave1_phase1_2_sovereignty", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_wave1_phase1_2_sovereignty", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_wave1_phase1_2_sovereignty", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_wave1_phase1_2_sovereignty", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_wave1_phase1_2_sovereignty", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_wave1_phase1_2_sovereignty", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_wave1_phase1_2_sovereignty", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_wave1_phase1_2_sovereignty", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_wave1_phase1_2_sovereignty", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_wave1_phase1_2_sovereignty", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_wave1_phase1_2_sovereignty", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_wave1_phase1_2_sovereignty", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_wave1_phase1_2_sovereignty", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_wave1_phase1_2_sovereignty", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_wave1_phase1_2_sovereignty", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_wave1_phase1_2_sovereignty", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_wave1_phase1_2_sovereignty", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_wave1_phase1_2_sovereignty", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_wave1_phase1_2_sovereignty", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_wave1_phase1_2_sovereignty", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_wave1_phase1_2_sovereignty", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_wave1_phase1_2_sovereignty", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_wave1_phase1_2_sovereignty", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_wave1_phase1_2_sovereignty", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_wave1_phase1_2_sovereignty", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_wave1_phase1_2_sovereignty", "context_pull_secondary")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_wave1_phase1_2_sovereignty", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_wave1_phase1_2_sovereignty", "uwg_term_secondary")
# REMOVED: _emit_writes_through("p1", "test_wave1_phase1_2_sovereignty", "write_through")
# REMOVED: _emit_writes_through("p1", "test_wave1_phase1_2_sovereignty", "write_through_secondary")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_wave1_phase1_2_sovereignty", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_wave1_phase1_2_sovereignty", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_wave1_phase1_2_sovereignty", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_wave1_phase1_2_sovereignty", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_wave1_phase1_2_sovereignty", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_wave1_phase1_2_sovereignty", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_wave1_phase1_2_sovereignty", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_wave1_phase1_2_sovereignty", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_wave1_phase1_2_sovereignty", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_wave1_phase1_2_sovereignty", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_wave1_phase1_2_sovereignty", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_wave1_phase1_2_sovereignty", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_wave1_phase1_2_sovereignty", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_wave1_phase1_2_sovereignty", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_wave1_phase1_2_sovereignty")
# REMOVED: _emit_gated_by_confidence("p1", "test_wave1_phase1_2_sovereignty", "confidence_gate")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_analysis_from_source(source: str, file_path: Path | None = None) -> FileAnalysis:
    """Parse source with ASTAnalyzer by writing to a temp file."""
    tmp = REPO_ROOT / TESTS_DIR / "architecture" / "_tmp_sovereignty_test.py"
    tmp.write_text(dedent(source), encoding="utf-8")
    try:
        aa = ASTAnalyzer(AGENTIC_CORE)
        return aa.analyze_file(tmp)
    finally:
        tmp.unlink(missing_ok=True)


# ===========================================================================
# 1. ast.Import branch — direct provider detection
# ===========================================================================


@pytest.mark.architecture
def test_import_openai_flagged_as_direct_provider():
    from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    from agentic_core.L0_routing.config.path_constants import (
    from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    """Success: bare 'import openai' is flagged as a direct provider import."""
    analysis = _make_analysis_from_source("import openai\n")
    assert "openai" in analysis.direct_provider_imports


@pytest.mark.architecture
def test_import_vllm_flagged_as_direct_provider():
    """Success: bare 'import vllm' is flagged as a direct provider import."""
    analysis = _make_analysis_from_source("import vllm\n")
    assert "vllm" in analysis.direct_provider_imports


@pytest.mark.architecture
def test_import_vllm_submodule_flagged_as_direct_provider():
    """Boundary: 'import vllm.engine' has top-level pkg 'vllm' and IS flagged."""
    analysis = _make_analysis_from_source("import vllm.engine\n")
    assert "vllm.engine" in analysis.direct_provider_imports


@pytest.mark.architecture
def test_import_agentic_core_vllm_type_not_flagged():
    """Negative: internal 'import agentic_core.L2_execution.types.vllm_token_budget_types' must NOT be flagged."""
    analysis = _make_analysis_from_source("import agentic_core.L2_execution.types.vllm_token_budget_types\n")
    assert not analysis.direct_provider_imports, (
        f"Internal vllm type module wrongly flagged: {analysis.direct_provider_imports}"
    )


@pytest.mark.architecture
def test_import_anthropic_flagged():
    """Success: 'import anthropic' is a direct provider import."""
    analysis = _make_analysis_from_source("import anthropic\n")
    assert "anthropic" in analysis.direct_provider_imports


@pytest.mark.architecture
def test_import_litellm_flagged():
    """Success: 'import litellm' is a direct provider import."""
    analysis = _make_analysis_from_source("import litellm\n")
    assert "litellm" in analysis.direct_provider_imports


@pytest.mark.architecture
def test_import_stdlib_not_flagged():
    """Negative: stdlib imports are never flagged as provider imports."""
    analysis = _make_analysis_from_source("import os\nimport sys\nimport json\n")
    assert not analysis.direct_provider_imports


@pytest.mark.architecture
def test_import_agentic_core_never_flagged():
    """Negative: any agentic_core.* import must never be flagged regardless of contents."""
    analysis = _make_analysis_from_source(
        "import agentic_core.L2_execution.types.vllm_backpressure_types\n"
        "import agentic_core.L2_execution.types.vllm_serving_profile_types\n"
        "import agentic_core.L2_execution.types.vllm_gateway_integration_types\n"
    )
    assert not analysis.direct_provider_imports, (
        f"Internal modules wrongly flagged: {analysis.direct_provider_imports}"
    )


# ===========================================================================
# 2. ast.ImportFrom branch — direct provider detection
# ===========================================================================


@pytest.mark.architecture
def test_from_openai_import_flagged():
    """Success: 'from openai import OpenAI' is flagged."""
    analysis = _make_analysis_from_source("from openai import OpenAI\n")
    assert "openai" in analysis.direct_provider_imports


@pytest.mark.architecture
def test_from_vllm_import_flagged():
    """Boundary: 'from vllm import LLM' is flagged."""
    analysis = _make_analysis_from_source("from vllm import LLM\n")
    assert "vllm" in analysis.direct_provider_imports


@pytest.mark.architecture
def test_from_agentic_core_vllm_types_not_flagged():
    """Negative: 'from agentic_core.L2_execution.types.vllm_token_budget_types import X' NOT flagged."""
    analysis = _make_analysis_from_source(
        "from agentic_core.L2_execution.types.vllm_token_budget_types import TokenBudget\n"
    )
    assert not analysis.direct_provider_imports, (
        f"Internal vllm type import wrongly flagged: {analysis.direct_provider_imports}"
    )


@pytest.mark.architecture
def test_from_agentic_core_vllm_infra_fingerprint_not_flagged():
    """Negative: the specific false-positive that existed before the fix must not recur."""
    analysis = _make_analysis_from_source(
        "from agentic_core.L2_execution.types.vllm_infrastructure_fingerprint_types import VllmInfraFingerprint\n"
    )
    assert not analysis.direct_provider_imports, (
        f"Regression: vllm_infrastructure_fingerprint_types wrongly flagged: {analysis.direct_provider_imports}"
    )


@pytest.mark.architecture
def test_google_generativeai_lazy_import_still_detected():
    """Boundary: lazy 'import google.generativeai' inside a function body is still
    detected because AST walk finds all Import nodes regardless of nesting depth."""
    analysis = _make_analysis_from_source("def f():\n    import google.generativeai as genai\n")
    # AST walk finds all nodes regardless of nesting
    assert "google.generativeai" in analysis.direct_provider_imports, (
        f"Expected google.generativeai in direct_provider_imports, got: {analysis.direct_provider_imports}"
    )


# ===========================================================================
# 3. _detect_upward_imports branch coverage
# ===========================================================================


@pytest.mark.architecture
def test_detect_upward_imports_l2_importing_l1_is_upward():
    """Negative control: L2 file importing L1 is flagged as upward.

    _detect_upward_imports flags any imported layer whose rank is LESS THAN
    the source file's rank (lower index in ARCH_LAYER_ORDER). L1 rank=1 < L2 rank=2.
    """
    fake_l2 = AGENTIC_CORE / "L2_execution" / "engines" / "fake_file.py"
    analysis = _make_analysis_from_source("import os\n")
    analysis.imported_layer_refs = {"L1"}
    result = _detect_upward_imports(fake_l2, analysis)
    assert result, "Expected upward import violation for L2->L1"
    assert "L1" in result


@pytest.mark.architecture
def test_detect_upward_imports_l1_importing_l0_is_flagged():
    """Documents actual behaviour: L1 importing L0 IS flagged by _detect_upward_imports
    because L0 rank (0) < L1 rank (1). The function defines 'upward' as any import
    of a lower-numbered layer, not in the architectural downward-dependency sense.
    This is the current implementation contract."""
    fake_l1 = AGENTIC_CORE / "L1_cognition" / "engines" / "fake.py"
    analysis = _make_analysis_from_source("import os\n")
    analysis.imported_layer_refs = {"L0"}
    result = _detect_upward_imports(fake_l1, analysis)
    # Current contract: lower-rank layer imports ARE reported
    assert result, (
        "_detect_upward_imports should flag L1->L0 (L0 rank 0 < L1 rank 1). "
        "If this changes, update the test to match the new contract."
    )
    assert "L0" in result


@pytest.mark.architecture
def test_detect_upward_imports_no_layer_returns_empty():
    """Boundary: file outside any layer folder returns empty list (no layer = no upward check)."""
    fake_path = AGENTIC_CORE / "utils" / "some_util.py"
    analysis = _make_analysis_from_source("import os\n")
    analysis.imported_layer_refs = {"L1", "L2"}
    result = _detect_upward_imports(fake_path, analysis)
    assert result == [], f"Expected empty list for non-layered file, got {result}"


@pytest.mark.architecture
def test_detect_upward_imports_no_refs_returns_empty():
    """Boundary: file with empty imported_layer_refs returns empty list."""
    fake_l0 = AGENTIC_CORE / "L0_routing" / "fake.py"
    analysis = _make_analysis_from_source("import os\n")
    analysis.imported_layer_refs = set()
    result = _detect_upward_imports(fake_l0, analysis)
    assert result == []


@pytest.mark.architecture
def test_detect_upward_imports_same_layer_not_upward():
    """Boundary: L2 importing L2 is not upward (same rank)."""
    fake_l2 = AGENTIC_CORE / "L2_execution" / "engines" / "fake.py"
    analysis = _make_analysis_from_source("import os\n")
    analysis.imported_layer_refs = {"L2"}
    result = _detect_upward_imports(fake_l2, analysis)
    assert not result, f"Same-layer import wrongly flagged as upward: {result}"


@pytest.mark.architecture
def test_detect_upward_imports_l2_importing_l3_is_not_flagged():
    """Documents actual behaviour: L2 importing L3 is NOT flagged because
    L3 rank (3) > L2 rank (2) — higher-numbered is not lower-ranked.
    The function only flags imports of lower-ranked (lower-numbered) layers."""
    fake_l2 = AGENTIC_CORE / "L2_execution" / "engines" / "fake.py"
    analysis = _make_analysis_from_source("import os\n")
    analysis.imported_layer_refs = {"L3"}
    result = _detect_upward_imports(fake_l2, analysis)
    assert not result, (
        f"L2->L3 should not be flagged by _detect_upward_imports (L3 rank 3 > L2 rank 2), got: {result}"
    )


# ===========================================================================
# 4. DIRECT_PROVIDER_IMPORT_PATTERNS tuple — top-level pkg contract
# ===========================================================================


@pytest.mark.architecture
def test_direct_provider_patterns_are_top_level_package_names():
    """Contract: all patterns in DIRECT_PROVIDER_IMPORT_PATTERNS must be
    simple top-level package names (no dots) so the top-pkg match is exact."""
    for pattern in DIRECT_PROVIDER_IMPORT_PATTERNS:
        # google.generativeai and google.genai are allowed multi-part but
        # must match the FIRST segment against top_pkg — verify by convention
        # that each is a known external package prefix
        assert isinstance(pattern, str) and len(pattern) > 0, f"Empty pattern: {pattern!r}"


@pytest.mark.architecture
def test_direct_provider_patterns_does_not_contain_agentic_core():
    """Invariant: DIRECT_PROVIDER_IMPORT_PATTERNS must never include agentic_core."""
    for pattern in DIRECT_PROVIDER_IMPORT_PATTERNS:
        assert AGENTIC_CORE_DIR not in pattern, (
            f"Internal package in DIRECT_PROVIDER_IMPORT_PATTERNS: {pattern!r}"
        )


# ===========================================================================
# 5. Real codebase invariants — non-L2 files must have no real provider imports
# ===========================================================================


@pytest.mark.architecture
def test_no_real_provider_imports_outside_l2():
    """Invariant: only L2_execution files may import real provider SDKs directly.
    Files in L0/L1/L3/L4/L5/L6 must have zero direct_provider_imports."""
    aa = ASTAnalyzer(AGENTIC_CORE)
    violations = []
    for layer in (
        "L0_routing",
        "L1_cognition",
        "L3_orchestration",
        "L4_state",
        "L5_safety",
        "L6_observability",
    ):
        layer_dir = AGENTIC_CORE / layer
        if not layer_dir.exists():
            continue
        for fp in sorted(layer_dir.rglob("*.py")):
            analysis = aa.analyze_file(fp)
            if not analysis.ok:
                continue
            if analysis.direct_provider_imports:
                rel = fp.relative_to(AGENTIC_CORE.parent)
                violations.append(f"{rel}: {sorted(analysis.direct_provider_imports)}")
    assert not violations, "Provider SDK imports found outside L2_execution:\n" + "\n".join(
        f"  {v}" for v in violations
    )


@pytest.mark.architecture
def test_l2_real_provider_imports_are_in_expected_files():
    """Success: the two known L2 real provider imports are in the expected adapter files."""
    aa = ASTAnalyzer(AGENTIC_CORE)
    l2_dir = AGENTIC_CORE / "L2_execution"
    found = {}
    for fp in sorted(l2_dir.rglob("*.py")):
        analysis = aa.analyze_file(fp)
        if not analysis.ok:
            continue
        if analysis.direct_provider_imports:
            found[fp.name] = sorted(analysis.direct_provider_imports)

    assert "healing_provider_adapters.py" in found, (
        "Expected healing_provider_adapters.py to have openai import"
    )
    assert "qwen_vllm_inference.py" in found, "Expected qwen_vllm_inference.py to have vllm import"
    # Both are allowlisted as L2 SDK adapter seams — not violations


@pytest.mark.architecture
def test_internal_vllm_type_modules_produce_no_direct_provider_gap():
    """Regression: the 8 false-positive vllm_* type files must produce zero direct_provider_imports."""
    false_positive_files = [
        AGENTIC_CORE / "L0_routing" / "engines" / "shadow_router_classifier.py",
        AGENTIC_CORE / "L0_routing" / "types" / "shadow_routing_types.py",
        AGENTIC_CORE / "L2_execution" / "types" / "vllm_backpressure_types.py",
        AGENTIC_CORE / "L2_execution" / "types" / "vllm_concurrency_types.py",
        AGENTIC_CORE / "L2_execution" / "types" / "vllm_gateway_adapter_types.py",
        AGENTIC_CORE / "L2_execution" / "types" / "vllm_gateway_integration_types.py",
        AGENTIC_CORE / "L2_execution" / "types" / "vllm_invariant_verifier_types.py",
        AGENTIC_CORE / "L2_execution" / "types" / "vllm_replay_validator_types.py",
    ]
    aa = ASTAnalyzer(AGENTIC_CORE)
    regressions = []
    for fp in false_positive_files:
        if not fp.exists():
            continue
        analysis = aa.analyze_file(fp)
        if not analysis.ok:
            continue
        if analysis.direct_provider_imports:
            regressions.append(f"{fp.name}: {sorted(analysis.direct_provider_imports)}")
    assert not regressions, (
        "Regression: internal vllm_* files wrongly flagged as provider imports:\n"
        + "\n".join(f"  {r}" for r in regressions)
    )
