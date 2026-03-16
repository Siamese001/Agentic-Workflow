"""
Wave 3 Phase 3.2 - Boundary Hardening: Branch Coverage Tests

Branch inventory for analyze_l2_execution:
  validator loop:
    - 'cache' in filename -> skipped (no L2-GAP-VALIDATOR)
    - parse failure -> skipped (no L2-GAP-VALIDATOR)
    - no schema_validator_cache import -> L2-GAP-VALIDATOR HIGH
    - schema_validator_cache imported -> no L2-GAP-VALIDATOR
    - no validator files -> no gaps

Branch inventory for analyze_l3_orchestration:
  orchestrator branch:
    - file exists + parse failure -> early return, no gaps
    - file exists + no plan cache import -> L3-GAP-001 MEDIUM
    - file exists + plan cache imported -> no L3-GAP-001
    - file does NOT exist -> no gaps

Branch inventory for analyze_l4_state:
  blob_storage branch:
    - file exists + parse failure -> early return, no gaps
    - file exists + l4_accesses <= 10 -> no L4-GAP-001
    - file exists + l4_accesses > 10 -> L4-GAP-001 HIGH
    - file does NOT exist -> no gaps

Branch inventory for analyze_l5_safety:
  enforcement loop:
    - 'cache' in filename -> skipped
    - parse failure -> skipped
    - no policy cache import + 'policy' in name -> L5-GAP-POLICY MEDIUM
    - no policy cache import + 'policy' NOT in name -> no gap
    - policy cache imported -> no L5-GAP-POLICY
    - no enforcement files -> no gaps

Branch inventory for analyze_l6_observability:
  telemetry loop:
    - parse failure -> skipped
    - no config_file_cache import -> L6-GAP-CONFIG LOW
    - config_file_cache imported -> no L6-GAP-CONFIG
    - no telemetry files -> no gaps

Branch inventory for analyze_architecture_component_presence:
  per-rule loop:
    - file does NOT exist -> ARCH-COMPONENT-MISSING gap
    - file exists + parse failure -> no gap, recorded as parse failure
    - file exists + signals present -> no gap
    - file exists + no signals -> ARCH-COMPONENT-WEAK gap

_dedupe_gaps:
  - empty input -> empty output
  - duplicate same key -> keep higher-priority (lower rank)
  - non-duplicate -> both retained
  - sorted by priority rank

Real codebase invariants:
  - analyze_l2_execution returns list
  - analyze_l3_orchestration returns list
  - analyze_l4_state returns list
  - analyze_l5_safety returns list
  - analyze_l6_observability returns list
  - analyze_architecture_component_presence returns list
  - L2-GAP-VALIDATOR* priority is HIGH
  - L3-GAP-001 priority is MEDIUM
  - L4-GAP-001 priority is HIGH
  - L5-GAP-POLICY* priority is MEDIUM
  - L6-GAP-CONFIG* priority is LOW
"""

from __future__ import annotations

import pathlib
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_wave3_phase3_2_boundary_hardening")
_emit_applies_guardrail("p0", "test_wave3_phase3_2_boundary_hardening", "p0_governance")
_emit_reads_policy_state("p0", "test_wave3_phase3_2_boundary_hardening", "policy_binding")
_emit_snapshots_state("p0", "test_wave3_phase3_2_boundary_hardening", "state_snapshot")
emit_replay_key("p0", "test_wave3_phase3_2_boundary_hardening")
emit_determinism_digest("p0", "test_wave3_phase3_2_boundary_hardening")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_wave3_phase3_2_boundary_hardening", "execution_auth")
_emit_validates_capability("p2", "test_wave3_phase3_2_boundary_hardening", "capability_check")
_emit_routes_to_capability("p2", "test_wave3_phase3_2_boundary_hardening", "capability_route")
_emit_writes_via_uwg("p2", "test_wave3_phase3_2_boundary_hardening", "uwg_write")
_emit_blocks_direct_write("p2", "test_wave3_phase3_2_boundary_hardening", "direct_write_block")
_emit_records_tool_invocation("p2", "test_wave3_phase3_2_boundary_hardening", "tool_invocation")
_emit_captures_execution_output("p2", "test_wave3_phase3_2_boundary_hardening", "exec_output")
_emit_dispatches_agent("p3", "test_wave3_phase3_2_boundary_hardening", "agent_dispatch")
_emit_coordinates_agents("p3", "test_wave3_phase3_2_boundary_hardening", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_wave3_phase3_2_boundary_hardening", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_wave3_phase3_2_boundary_hardening", "healing_outcome")
_emit_escalates_failure("p3", "test_wave3_phase3_2_boundary_hardening", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_wave3_phase3_2_boundary_hardening", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_wave3_phase3_2_boundary_hardening", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_wave3_phase3_2_boundary_hardening", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_wave3_phase3_2_boundary_hardening", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_wave3_phase3_2_boundary_hardening", "eval_metric")
_emit_stores_embedding("p4", "test_wave3_phase3_2_boundary_hardening", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_wave3_phase3_2_boundary_hardening", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_wave3_phase3_2_boundary_hardening", "exec_snapshot_link")

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
    ARCHITECTURE_COMPONENT_RULES,
    FileAnalysis,
    ParseFailure,
    SemanticGap,
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


def _make_analyzer(
    analyze_map: dict[Path, FileAnalysis],
    file_lists: dict[str, list[Path]] | None = None,
    existing_paths: set[Path] | None = None,
) -> tuple[SemanticGapAnalyzer, dict]:
    """Return a SemanticGapAnalyzer with mocked analyze_file and find_hot_paths.
    file_lists maps a pattern substring to a list of paths to return.
    existing_paths controls which paths report Path.exists() == True.
    """
    analyzer = SemanticGapAnalyzer()

    def _fake_analyze(fp: Path) -> FileAnalysis:
        return analyze_map.get(fp, _ok_analysis(fp))

    _file_lists = file_lists or {}

    def _fake_find(base_dir: Path, pattern: str) -> list[Path]:
        for key, paths in _file_lists.items():
            if key in pattern or key in str(base_dir):
                return paths
        return []

    analyzer.ast_analyzer.analyze_file = _fake_analyze
    analyzer.ast_analyzer.find_hot_paths = _fake_find

    _existing = existing_paths if existing_paths is not None else set(analyze_map.keys())

    def _exists_side_effect(self_path):
        return self_path in _existing

    return analyzer, {"exists_side_effect": _exists_side_effect}


def _make_gap(
    gap_id: str, layer: str, artery: str, priority: str, evidence: list[str] | None = None
) -> SemanticGap:
    return SemanticGap(
        gap_id=gap_id,
        layer=layer,
        artery=artery,
        intent="test intent",
        reality="test reality",
        impact="test impact",
        priority=priority,
        evidence_files=evidence or [f"fake/{gap_id}.py"],
        recommended_fix="test fix",
    )


# ===========================================================================
# 1. analyze_l2_execution
# ===========================================================================


@pytest.mark.architecture
def test_l2_validator_cache_in_name_skipped():
    """L2: validator file with 'cache' in name is excluded from L2-GAP-VALIDATOR."""
    val_path = AGENTIC_CORE / "L2_execution" / "schema_validator_cache.py"
    val_analysis = _ok_analysis(val_path, imported_module_names={"os"}, imported_symbol_names=set())
    analyzer, _ = _make_analyzer(
        {val_path: val_analysis},
        file_lists={"*validator*": [val_path]},
    )
    gaps = analyzer.analyze_l2_execution()
    validator_gaps = [g for g in gaps if "VALIDATOR" in g.gap_id]
    assert not validator_gaps, "Files with 'cache' in name must be excluded"


@pytest.mark.architecture
def test_l2_validator_parse_fail_skipped():
    """L2: validator parse failure -> skipped, no L2-GAP-VALIDATOR."""
    val_path = AGENTIC_CORE / "L2_execution" / "output_validator.py"
    analyzer, _ = _make_analyzer(
        {val_path: _failed_analysis(val_path)},
        file_lists={"*validator*": [val_path]},
    )
    gaps = analyzer.analyze_l2_execution()
    validator_gaps = [g for g in gaps if "VALIDATOR" in g.gap_id]
    assert not validator_gaps


@pytest.mark.architecture
def test_l2_validator_no_cache_import_generates_gap():
    """L2: validator with no schema_validator_cache import -> L2-GAP-VALIDATOR HIGH."""
    val_path = AGENTIC_CORE / "L2_execution" / "output_validator.py"
    val_analysis = _ok_analysis(val_path, imported_module_names={"os"}, imported_symbol_names=set())
    analyzer, _ = _make_analyzer(
        {val_path: val_analysis},
        file_lists={"*validator*": [val_path]},
    )
    gaps = analyzer.analyze_l2_execution()
    validator_gaps = [g for g in gaps if "VALIDATOR" in g.gap_id]
    assert validator_gaps, "Expected L2-GAP-VALIDATOR for validator without cache"
    assert validator_gaps[0].priority == "HIGH"


@pytest.mark.architecture
def test_l2_validator_with_cache_module_no_gap():
    """L2: validator imports schema_validator_cache -> no L2-GAP-VALIDATOR."""
    val_path = AGENTIC_CORE / "L2_execution" / "output_validator.py"
    val_analysis = _ok_analysis(
        val_path,
        imported_module_names={"schema_validator_cache"},
        imported_symbol_names=set(),
    )
    analyzer, _ = _make_analyzer(
        {val_path: val_analysis},
        file_lists={"*validator*": [val_path]},
    )
    gaps = analyzer.analyze_l2_execution()
    validator_gaps = [g for g in gaps if "VALIDATOR" in g.gap_id]
    assert not validator_gaps


@pytest.mark.architecture
def test_l2_validator_with_symbol_cache_no_gap():
    """L2: validator imports SchemaValidatorCache symbol -> no L2-GAP-VALIDATOR."""
    val_path = AGENTIC_CORE / "L2_execution" / "output_validator.py"
    val_analysis = _ok_analysis(
        val_path,
        imported_module_names=set(),
        imported_symbol_names={"SchemaValidatorCache"},
    )
    analyzer, _ = _make_analyzer(
        {val_path: val_analysis},
        file_lists={"*validator*": [val_path]},
    )
    gaps = analyzer.analyze_l2_execution()
    validator_gaps = [g for g in gaps if "VALIDATOR" in g.gap_id]
    assert not validator_gaps


@pytest.mark.architecture
def test_l2_no_validator_files_no_gap():
    """L2: no validator files found -> no L2-GAP-VALIDATOR."""
    analyzer, _ = _make_analyzer({}, file_lists={"*validator*": []})
    gaps = analyzer.analyze_l2_execution()
    assert not gaps


# ===========================================================================
# 2. analyze_l3_orchestration
# ===========================================================================

ORCHESTRATOR = AGENTIC_CORE / "L3_orchestration" / "engines" / "orchestrator_engine.py"


@pytest.mark.architecture
def test_l3_orchestrator_parse_fail_no_gap():
    """L3: orchestrator parse failure -> early return, no L3-GAP-001."""
    analyzer, ctx = _make_analyzer(
        {ORCHESTRATOR: _failed_analysis(ORCHESTRATOR)},
        existing_paths={ORCHESTRATOR},
    )
    with patch.object(pathlib.Path, "exists", ctx["exists_side_effect"]):
        gaps = analyzer.analyze_l3_orchestration()
    assert not any(g.gap_id == "L3-GAP-001" for g in gaps)


@pytest.mark.architecture
def test_l3_orchestrator_no_cache_generates_gap():
    """L3: orchestrator exists + no plan cache import -> L3-GAP-001 MEDIUM."""
    orch_analysis = _ok_analysis(ORCHESTRATOR, imported_module_names={"os"}, imported_symbol_names=set())
    analyzer, ctx = _make_analyzer(
        {ORCHESTRATOR: orch_analysis},
        existing_paths={ORCHESTRATOR},
    )
    with patch.object(pathlib.Path, "exists", ctx["exists_side_effect"]):
        gaps = analyzer.analyze_l3_orchestration()
    assert any(g.gap_id == "L3-GAP-001" for g in gaps)
    gap = next(g for g in gaps if g.gap_id == "L3-GAP-001")
    assert gap.priority == "MEDIUM"


@pytest.mark.architecture
def test_l3_orchestrator_with_cache_module_no_gap():
    """L3: orchestrator imports orchestration_plan_cache -> no L3-GAP-001."""
    orch_analysis = _ok_analysis(
        ORCHESTRATOR,
        imported_module_names={"orchestration_plan_cache"},
        imported_symbol_names=set(),
    )
    analyzer, ctx = _make_analyzer(
        {ORCHESTRATOR: orch_analysis},
        existing_paths={ORCHESTRATOR},
    )
    with patch.object(pathlib.Path, "exists", ctx["exists_side_effect"]):
        gaps = analyzer.analyze_l3_orchestration()
    assert not any(g.gap_id == "L3-GAP-001" for g in gaps)


@pytest.mark.architecture
def test_l3_orchestrator_file_missing_no_gap():
    """L3: orchestrator file does not exist -> no gaps."""
    analyzer, ctx = _make_analyzer({}, existing_paths=set())
    with patch.object(pathlib.Path, "exists", ctx["exists_side_effect"]):
        gaps = analyzer.analyze_l3_orchestration()
    assert not gaps


# ===========================================================================
# 3. analyze_l4_state
# ===========================================================================

BLOB_STORAGE = AGENTIC_CORE / "L4_state" / "memory" / "blob_storage_provider.py"


@pytest.mark.architecture
def test_l4_blob_parse_fail_no_gap():
    """L4: blob_storage parse failure -> early return, no L4-GAP-001."""
    analyzer, ctx = _make_analyzer(
        {BLOB_STORAGE: _failed_analysis(BLOB_STORAGE)},
        existing_paths={BLOB_STORAGE},
    )
    with patch.object(pathlib.Path, "exists", ctx["exists_side_effect"]):
        gaps = analyzer.analyze_l4_state()
    assert not any(g.gap_id == "L4-GAP-001" for g in gaps)


@pytest.mark.architecture
def test_l4_blob_exactly_ten_accesses_no_gap():
    """L4: exactly 10 l4_state_accesses -> boundary: no L4-GAP-001."""
    blob_analysis = _ok_analysis(BLOB_STORAGE, l4_state_accesses=list(range(10)))
    analyzer, ctx = _make_analyzer(
        {BLOB_STORAGE: blob_analysis},
        existing_paths={BLOB_STORAGE},
    )
    with patch.object(pathlib.Path, "exists", ctx["exists_side_effect"]):
        gaps = analyzer.analyze_l4_state()
    assert not any(g.gap_id == "L4-GAP-001" for g in gaps)


@pytest.mark.architecture
def test_l4_blob_eleven_accesses_generates_gap():
    """L4: 11 l4_state_accesses -> boundary: L4-GAP-001 HIGH."""
    blob_analysis = _ok_analysis(BLOB_STORAGE, l4_state_accesses=list(range(11)))
    analyzer, ctx = _make_analyzer(
        {BLOB_STORAGE: blob_analysis},
        existing_paths={BLOB_STORAGE},
    )
    with patch.object(pathlib.Path, "exists", ctx["exists_side_effect"]):
        gaps = analyzer.analyze_l4_state()
    assert any(g.gap_id == "L4-GAP-001" for g in gaps)
    gap = next(g for g in gaps if g.gap_id == "L4-GAP-001")
    assert gap.priority == "HIGH"


@pytest.mark.architecture
def test_l4_blob_file_missing_no_gap():
    """L4: blob_storage file does not exist -> no gaps."""
    analyzer, ctx = _make_analyzer({}, existing_paths=set())
    with patch.object(pathlib.Path, "exists", ctx["exists_side_effect"]):
        gaps = analyzer.analyze_l4_state()
    assert not gaps


# ===========================================================================
# 4. analyze_l5_safety
# ===========================================================================


@pytest.mark.architecture
def test_l5_enforcement_cache_in_name_skipped():
    """L5: enforcement file with 'cache' in name is excluded."""
    enf_path = AGENTIC_CORE / "L5_safety" / "enforcement" / "policy_cache.py"
    enf_analysis = _ok_analysis(enf_path, imported_module_names={"os"}, imported_symbol_names=set())
    analyzer, _ = _make_analyzer(
        {enf_path: enf_analysis},
        file_lists={"enforcement": [enf_path]},
    )
    gaps = analyzer.analyze_l5_safety()
    policy_gaps = [g for g in gaps if "POLICY" in g.gap_id]
    assert not policy_gaps


@pytest.mark.architecture
def test_l5_enforcement_parse_fail_skipped():
    """L5: enforcement parse failure -> skipped, no L5-GAP-POLICY."""
    enf_path = AGENTIC_CORE / "L5_safety" / "enforcement" / "policy_enforcer.py"
    analyzer, _ = _make_analyzer(
        {enf_path: _failed_analysis(enf_path)},
        file_lists={"enforcement": [enf_path]},
    )
    gaps = analyzer.analyze_l5_safety()
    policy_gaps = [g for g in gaps if "POLICY" in g.gap_id]
    assert not policy_gaps


@pytest.mark.architecture
def test_l5_enforcement_policy_in_name_no_cache_generates_gap():
    """L5: 'policy' in name + no cache import -> L5-GAP-POLICY MEDIUM."""
    enf_path = AGENTIC_CORE / "L5_safety" / "enforcement" / "policy_enforcer.py"
    enf_analysis = _ok_analysis(enf_path, imported_module_names={"os"}, imported_symbol_names=set())
    analyzer, _ = _make_analyzer(
        {enf_path: enf_analysis},
        file_lists={"enforcement": [enf_path]},
    )
    gaps = analyzer.analyze_l5_safety()
    policy_gaps = [g for g in gaps if "POLICY" in g.gap_id]
    assert policy_gaps, "Expected L5-GAP-POLICY for policy file without cache"
    assert policy_gaps[0].priority == "MEDIUM"


@pytest.mark.architecture
def test_l5_enforcement_no_policy_in_name_no_gap():
    """L5: 'policy' NOT in name + no cache import -> no L5-GAP-POLICY."""
    enf_path = AGENTIC_CORE / "L5_safety" / "enforcement" / "rate_limiter.py"
    enf_analysis = _ok_analysis(enf_path, imported_module_names={"os"}, imported_symbol_names=set())
    analyzer, _ = _make_analyzer(
        {enf_path: enf_analysis},
        file_lists={"enforcement": [enf_path]},
    )
    gaps = analyzer.analyze_l5_safety()
    policy_gaps = [g for g in gaps if "POLICY" in g.gap_id]
    assert not policy_gaps


@pytest.mark.architecture
def test_l5_enforcement_with_cache_import_no_gap():
    """L5: enforcement imports policy_registry_cache -> no L5-GAP-POLICY."""
    enf_path = AGENTIC_CORE / "L5_safety" / "enforcement" / "policy_enforcer.py"
    enf_analysis = _ok_analysis(
        enf_path,
        imported_module_names={"policy_registry_cache"},
        imported_symbol_names=set(),
    )
    analyzer, _ = _make_analyzer(
        {enf_path: enf_analysis},
        file_lists={"enforcement": [enf_path]},
    )
    gaps = analyzer.analyze_l5_safety()
    policy_gaps = [g for g in gaps if "POLICY" in g.gap_id]
    assert not policy_gaps


@pytest.mark.architecture
def test_l5_no_enforcement_files_no_gap():
    """L5: no enforcement files found -> no gaps."""
    analyzer, _ = _make_analyzer({}, file_lists={"enforcement": []})
    gaps = analyzer.analyze_l5_safety()
    assert not gaps


# ===========================================================================
# 5. analyze_l6_observability
# ===========================================================================


@pytest.mark.architecture
def test_l6_telemetry_parse_fail_skipped():
    """L6: telemetry parse failure -> skipped, no L6-GAP-CONFIG."""
    telem_path = AGENTIC_CORE / "L6_observability" / "telemetry_engine.py"
    analyzer, _ = _make_analyzer(
        {telem_path: _failed_analysis(telem_path)},
        file_lists={"*telemetry*": [telem_path]},
    )
    gaps = analyzer.analyze_l6_observability()
    config_gaps = [g for g in gaps if "CONFIG" in g.gap_id]
    assert not config_gaps


@pytest.mark.architecture
def test_l6_telemetry_no_cache_import_generates_gap():
    """L6: telemetry file with no config_file_cache import -> L6-GAP-CONFIG LOW."""
    telem_path = AGENTIC_CORE / "L6_observability" / "telemetry_engine.py"
    telem_analysis = _ok_analysis(telem_path, imported_module_names={"os"}, imported_symbol_names=set())
    analyzer, _ = _make_analyzer(
        {telem_path: telem_analysis},
        file_lists={"*telemetry*": [telem_path]},
    )
    gaps = analyzer.analyze_l6_observability()
    config_gaps = [g for g in gaps if "CONFIG" in g.gap_id]
    assert config_gaps, "Expected L6-GAP-CONFIG for telemetry without cache"
    assert config_gaps[0].priority == "LOW"


@pytest.mark.architecture
def test_l6_telemetry_with_cache_module_no_gap():
    """L6: telemetry imports config_file_cache -> no L6-GAP-CONFIG."""
    telem_path = AGENTIC_CORE / "L6_observability" / "telemetry_engine.py"
    telem_analysis = _ok_analysis(
        telem_path,
        imported_module_names={"config_file_cache"},
        imported_symbol_names=set(),
    )
    analyzer, _ = _make_analyzer(
        {telem_path: telem_analysis},
        file_lists={"*telemetry*": [telem_path]},
    )
    gaps = analyzer.analyze_l6_observability()
    config_gaps = [g for g in gaps if "CONFIG" in g.gap_id]
    assert not config_gaps


@pytest.mark.architecture
def test_l6_telemetry_with_symbol_cache_no_gap():
    """L6: telemetry imports ConfigFileCache symbol -> no L6-GAP-CONFIG."""
    telem_path = AGENTIC_CORE / "L6_observability" / "telemetry_engine.py"
    telem_analysis = _ok_analysis(
        telem_path,
        imported_module_names=set(),
        imported_symbol_names={"ConfigFileCache"},
    )
    analyzer, _ = _make_analyzer(
        {telem_path: telem_analysis},
        file_lists={"*telemetry*": [telem_path]},
    )
    gaps = analyzer.analyze_l6_observability()
    config_gaps = [g for g in gaps if "CONFIG" in g.gap_id]
    assert not config_gaps


@pytest.mark.architecture
def test_l6_no_telemetry_files_no_gap():
    """L6: no telemetry files found -> no gaps."""
    analyzer, _ = _make_analyzer({}, file_lists={"*telemetry*": []})
    gaps = analyzer.analyze_l6_observability()
    assert not gaps


# ===========================================================================
# 6. analyze_architecture_component_presence
# ===========================================================================


@pytest.mark.architecture
def test_arch_component_missing_file_generates_missing_gap():
    """ARCH: rule file does not exist -> ARCH-COMPONENT-MISSING gap."""
    rule = ARCHITECTURE_COMPONENT_RULES[0]
    target = rule["path"]
    analyzer, ctx = _make_analyzer({}, existing_paths=set())
    with patch.object(pathlib.Path, "exists", ctx["exists_side_effect"]):
        gaps = analyzer.analyze_architecture_component_presence()
    missing_gaps = [g for g in gaps if g.gap_id.startswith("ARCH-COMPONENT-MISSING")]
    assert any(rule["layer"] == g.layer for g in missing_gaps)


@pytest.mark.architecture
def test_arch_component_parse_fail_no_gap():
    """ARCH: rule file exists but parse fails -> no ARCH-COMPONENT gap (recorded as parse failure)."""
    rule = ARCHITECTURE_COMPONENT_RULES[0]
    target = rule["path"]
    analyzer, ctx = _make_analyzer(
        {target: _failed_analysis(target)},
        existing_paths={target},
    )
    with patch.object(pathlib.Path, "exists", ctx["exists_side_effect"]):
        gaps = analyzer.analyze_architecture_component_presence()
    arch_gaps = [g for g in gaps if g.gap_id.startswith("ARCH-COMPONENT") and g.layer == rule["layer"]]
    assert not any(g for g in arch_gaps if rule["artery"] == g.artery)


@pytest.mark.architecture
def test_arch_component_signals_present_no_gap():
    """ARCH: rule file exists + required marker found -> no ARCH-COMPONENT-WEAK gap."""
    rule = ARCHITECTURE_COMPONENT_RULES[0]
    target = rule["path"]
    marker = rule["required_any"][0]
    analysis = _ok_analysis(target, used_names={marker}, imported_symbol_names=set())
    analysis.calls = []
    analyzer, ctx = _make_analyzer(
        {target: analysis},
        existing_paths={target},
    )
    with patch.object(pathlib.Path, "exists", ctx["exists_side_effect"]):
        gaps = analyzer.analyze_architecture_component_presence()
    weak_gaps = [g for g in gaps if g.gap_id.startswith("ARCH-COMPONENT-WEAK") and g.artery == rule["artery"]]
    assert not weak_gaps


@pytest.mark.architecture
def test_arch_component_no_signals_generates_weak_gap():
    """ARCH: rule file exists + no required markers found -> ARCH-COMPONENT-WEAK gap."""
    rule = ARCHITECTURE_COMPONENT_RULES[0]
    target = rule["path"]
    analysis = _ok_analysis(target, used_names={"unrelated_name"}, imported_symbol_names=set())
    analysis.calls = []
    analyzer, ctx = _make_analyzer(
        {target: analysis},
        existing_paths={target},
    )
    with patch.object(pathlib.Path, "exists", ctx["exists_side_effect"]):
        gaps = analyzer.analyze_architecture_component_presence()
    weak_gaps = [g for g in gaps if g.gap_id.startswith("ARCH-COMPONENT-WEAK") and g.artery == rule["artery"]]
    assert weak_gaps


# ===========================================================================
# 7. _dedupe_gaps
# ===========================================================================


@pytest.mark.architecture
def test_dedupe_gaps_empty_input():
    """_dedupe_gaps: empty input -> empty output."""
    analyzer = SemanticGapAnalyzer()
    result = analyzer._dedupe_gaps([])
    assert result == []


@pytest.mark.architecture
def test_dedupe_gaps_no_duplicates_all_retained():
    """_dedupe_gaps: no duplicate keys -> all gaps retained."""
    g1 = _make_gap("G1", "L0", "Artery A", "HIGH", ["file_a.py"])
    g2 = _make_gap("G2", "L1", "Artery B", "MEDIUM", ["file_b.py"])
    analyzer = SemanticGapAnalyzer()
    result = analyzer._dedupe_gaps([g1, g2])
    assert len(result) == 2


@pytest.mark.architecture
def test_dedupe_gaps_duplicate_key_keeps_higher_priority():
    """_dedupe_gaps: two gaps with same key -> higher-priority (lower rank) wins."""
    g_med = _make_gap("G-MED", "L0", "Artery A", "MEDIUM", ["file_a.py"])
    g_high = _make_gap("G-HIGH", "L0", "Artery A", "HIGH", ["file_a.py"])
    analyzer = SemanticGapAnalyzer()
    result = analyzer._dedupe_gaps([g_med, g_high])
    assert len(result) == 1
    assert result[0].priority == "HIGH"


@pytest.mark.architecture
def test_dedupe_gaps_sorted_by_priority():
    """_dedupe_gaps: output sorted by priority rank (HIGH before MEDIUM before LOW)."""
    g_low = _make_gap("G-LOW", "L0", "Artery A", "LOW", ["file_a.py"])
    g_high = _make_gap("G-HIGH", "L1", "Artery B", "HIGH", ["file_b.py"])
    g_med = _make_gap("G-MED", "L2", "Artery C", "MEDIUM", ["file_c.py"])
    analyzer = SemanticGapAnalyzer()
    result = analyzer._dedupe_gaps([g_low, g_high, g_med])
    priorities = [r.priority for r in result]
    assert priorities.index("HIGH") < priorities.index("MEDIUM")
    assert priorities.index("MEDIUM") < priorities.index("LOW")


# ===========================================================================
# 8. Real codebase invariants
# ===========================================================================


@pytest.mark.architecture
def test_analyze_l2_execution_returns_list():
    """Integration: analyze_l2_execution returns a list."""
    assert isinstance(SemanticGapAnalyzer().analyze_l2_execution(), list)


@pytest.mark.architecture
def test_analyze_l3_orchestration_returns_list():
    """Integration: analyze_l3_orchestration returns a list."""
    assert isinstance(SemanticGapAnalyzer().analyze_l3_orchestration(), list)


@pytest.mark.architecture
def test_analyze_l4_state_returns_list():
    """Integration: analyze_l4_state returns a list."""
    assert isinstance(SemanticGapAnalyzer().analyze_l4_state(), list)


@pytest.mark.architecture
def test_analyze_l5_safety_returns_list():
    """Integration: analyze_l5_safety returns a list."""
    assert isinstance(SemanticGapAnalyzer().analyze_l5_safety(), list)


@pytest.mark.architecture
def test_analyze_l6_observability_returns_list():
    """Integration: analyze_l6_observability returns a list."""
    assert isinstance(SemanticGapAnalyzer().analyze_l6_observability(), list)


@pytest.mark.architecture
def test_analyze_architecture_component_presence_returns_list():
    """Integration: analyze_architecture_component_presence returns a list."""
    assert isinstance(SemanticGapAnalyzer().analyze_architecture_component_presence(), list)


@pytest.mark.architecture
def test_l2_validator_gaps_are_high_priority():
    """Contract: all L2-GAP-VALIDATOR-* gaps must be HIGH priority."""
    gaps = SemanticGapAnalyzer().analyze_l2_execution()
    for gap in gaps:
        if "VALIDATOR" in gap.gap_id:
            assert gap.priority == "HIGH", f"L2-GAP-VALIDATOR must be HIGH, got {gap.priority}"


@pytest.mark.architecture
def test_l3_gap001_is_medium_if_present():
    """Contract: L3-GAP-001 must be MEDIUM priority."""
    gaps = SemanticGapAnalyzer().analyze_l3_orchestration()
    for gap in gaps:
        if gap.gap_id == "L3-GAP-001":
            assert gap.priority == "MEDIUM", f"L3-GAP-001 must be MEDIUM, got {gap.priority}"


@pytest.mark.architecture
def test_l4_gap001_is_high_if_present():
    """Contract: L4-GAP-001 must be HIGH priority."""
    gaps = SemanticGapAnalyzer().analyze_l4_state()
    for gap in gaps:
        if gap.gap_id == "L4-GAP-001":
            assert gap.priority == "HIGH", f"L4-GAP-001 must be HIGH, got {gap.priority}"


@pytest.mark.architecture
def test_l5_policy_gaps_are_medium_if_present():
    """Contract: all L5-GAP-POLICY-* gaps must be MEDIUM priority."""
    gaps = SemanticGapAnalyzer().analyze_l5_safety()
    for gap in gaps:
        if "POLICY" in gap.gap_id:
            assert gap.priority == "MEDIUM", f"L5-GAP-POLICY must be MEDIUM, got {gap.priority}"


@pytest.mark.architecture
def test_l6_config_gaps_are_low_if_present():
    """Contract: all L6-GAP-CONFIG-* gaps must be LOW priority."""
    gaps = SemanticGapAnalyzer().analyze_l6_observability()
    for gap in gaps:
        if "CONFIG" in gap.gap_id:
            assert gap.priority == "LOW", f"L6-GAP-CONFIG must be LOW, got {gap.priority}"
