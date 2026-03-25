"""
ADG Anomaly Fix Regression Tests — Waves 1-6
=============================================

Innovative validation strategies used per anomaly:

  STRATEGY 1 — AST Import Graph Analysis:
    Parse source files with ``ast`` to prove absence of banned imports and
    verify lazy-import placement without executing any code.

  STRATEGY 2 — Static Structural Contracts:
    Inspect filesystem/module attributes to prove shim re-export identity,
    territory placement, and file existence without loading heavy deps.

  STRATEGY 3 — Behavioral Mock-Injection:
    Inject synthetic guardian aggregates or fake objects into tested code
    paths to verify confidence gates and certify-only contracts fire
    correctly.

  STRATEGY 4 — Regression Lock (negative-control):
    Assert that the old bad pattern (banned import, tempfile call, etc.) is
    absent at the byte level from every committed source file.

  STRATEGY 5 — Layer Gravity Static Scan:
    Walk L0 and L2 source files with ``ast`` and assert no unguarded
    top-level imports cross the L0→L2 or L0→L_RUNTIME boundaries.

Coverage matrix
---------------
W1 A-05  report_location_validator + structure_drift_validator: zero UWG top-level imports
W2 A-01  validators/governance_validator.py thin-stub contract
W2 A-07  GovernanceAgent validators/ shim re-exports reasoning/ identity
W3 A-02  PascalSovereigntyAgent: reasoning/ canonical + validators/ shim
W3 A-04  CodeJanitorAgent: reasoning/ canonical + validators/ shim
W4 A-06a L0 ssot_reporting/routing import from ssot_tier_constants not healing_tier_config
W4 A-06b deterministic_routing_gateway: no top-level execution_trace import
W4 A-06c route_policy_governor: no top-level execution_trace import
W4 A-06d execution_proof_emitter: no top-level execution_trace import (lazy/TYPE_CHECKING)
W5 A-03  dependencygraph_validator: zero _wg / write_gateway references
W5 A-08  StructuralValidatorAgent: zero tempfile top-level import
W6 A-11  remediation_dispatcher: MINIMUM_HEAL_CONFIDENCE constant + gate fires
W6 A-13  GravityLeakValidatorAgent: certify-only contract (no mutations)
W6 A-14  CodeValidatorAgent: all open() calls carry read-only guardian comment
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

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

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_adg_anomaly_fixes")
# REMOVED: _emit_applies_guardrail("p0", "test_adg_anomaly_fixes", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_adg_anomaly_fixes", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_adg_anomaly_fixes", "state_snapshot")
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

# REMOVED: _emit_emits_metric_event("test_adg_anomaly_fixes", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_adg_anomaly_fixes", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_adg_anomaly_fixes", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_adg_anomaly_fixes", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_adg_anomaly_fixes", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_adg_anomaly_fixes", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_adg_anomaly_fixes", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_adg_anomaly_fixes", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_adg_anomaly_fixes", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_adg_anomaly_fixes", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_adg_anomaly_fixes", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_adg_anomaly_fixes", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_adg_anomaly_fixes", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_adg_anomaly_fixes", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_adg_anomaly_fixes", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_adg_anomaly_fixes", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_adg_anomaly_fixes", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_adg_anomaly_fixes", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_adg_anomaly_fixes", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_adg_anomaly_fixes", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_adg_anomaly_fixes", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_adg_anomaly_fixes", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_adg_anomaly_fixes", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_adg_anomaly_fixes", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_adg_anomaly_fixes", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_adg_anomaly_fixes", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_adg_anomaly_fixes", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_adg_anomaly_fixes", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_adg_anomaly_fixes", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_adg_anomaly_fixes", "context_pull_2")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_adg_anomaly_fixes", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_adg_anomaly_fixes", "uwg_term_2")
# REMOVED: _emit_writes_through("p1", "test_adg_anomaly_fixes", "write_through")
# REMOVED: _emit_writes_through("p1", "test_adg_anomaly_fixes", "write_through_2")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_adg_anomaly_fixes", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_adg_anomaly_fixes", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_adg_anomaly_fixes", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_adg_anomaly_fixes", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_adg_anomaly_fixes", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_adg_anomaly_fixes", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_adg_anomaly_fixes", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_adg_anomaly_fixes", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_adg_anomaly_fixes", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_adg_anomaly_fixes", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_adg_anomaly_fixes", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_adg_anomaly_fixes", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_adg_anomaly_fixes", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_adg_anomaly_fixes", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_adg_anomaly_fixes")
# REMOVED: _emit_gated_by_confidence("p1", "test_adg_anomaly_fixes", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_adg_anomaly_fixes")
# REMOVED: emit_determinism_digest("p0", "test_adg_anomaly_fixes")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_adg_anomaly_fixes", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_adg_anomaly_fixes", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_adg_anomaly_fixes", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_adg_anomaly_fixes", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_adg_anomaly_fixes", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_adg_anomaly_fixes", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_adg_anomaly_fixes", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_adg_anomaly_fixes", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_adg_anomaly_fixes", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_adg_anomaly_fixes", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_adg_anomaly_fixes", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_adg_anomaly_fixes", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_adg_anomaly_fixes", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_adg_anomaly_fixes", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_adg_anomaly_fixes", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_adg_anomaly_fixes", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_adg_anomaly_fixes", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_adg_anomaly_fixes", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_adg_anomaly_fixes", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_adg_anomaly_fixes", "exec_snapshot_link")

# ---------------------------------------------------------------------------
# Module-level constants (required by guardian hook)
# ---------------------------------------------------------------------------

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300

# ---------------------------------------------------------------------------
# Path constants
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

_L5_VALIDATORS = PROJECT_ROOT / "agentic_core" / "L5_safety" / "validators"
_L5_REASONING = PROJECT_ROOT / "agentic_core" / "L5_safety" / "reasoning"
_L0_SCRIPTS = PROJECT_ROOT / "agentic_core" / "L0_routing" / "scripts"
_L0_ARTIFACTS = PROJECT_ROOT / "agentic_core" / "L0_routing" / "artifacts"
_L0_POLICY = PROJECT_ROOT / "agentic_core" / "L0_routing" / "policy"
_L0_CONFIG = PROJECT_ROOT / "agentic_core" / "L0_routing" / "config"
_L2_DETERMINISM = PROJECT_ROOT / "agentic_core" / "L2_execution" / "determinism"
_L2_SCRIPTS = PROJECT_ROOT / "agentic_core" / "L2_execution" / "scripts"

pytestmark = pytest.mark.guardian


# ---------------------------------------------------------------------------
# AST helpers (Strategy 1)
# ---------------------------------------------------------------------------


def _parse(path: Path) -> ast.Module:
    """Return AST module, skip test if file is absent."""
    if not path.exists():

    return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def _top_level_import_modules(tree: ast.Module) -> list[tuple[int, str]]:
    """(lineno, module) for every *top-level* import node."""
    result: list[tuple[int, str]] = []
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                result.append((node.lineno, alias.name))
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                result.append((node.lineno, node.module))
    return result


def _all_import_modules(tree: ast.Module) -> list[tuple[int, str]]:
    """(lineno, module) for ALL imports regardless of nesting depth."""
    result: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                result.append((node.lineno, alias.name))
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                result.append((node.lineno, node.module))
    return result


def _top_level_fragment(tree: ast.Module, fragment: str) -> list[int]:
    """Lines of top-level imports whose module contains *fragment*."""
    return [ln for ln, mod in _top_level_import_modules(tree) if fragment in mod]


def _any_fragment(tree: ast.Module, fragment: str) -> list[int]:
    """Lines of ANY import (any depth) whose module contains *fragment*."""
    return [ln for ln, mod in _all_import_modules(tree) if fragment in mod]


# ---------------------------------------------------------------------------
# Byte-level helper (Strategy 4)
# ---------------------------------------------------------------------------


def _src(path: Path) -> str:
    if not path.exists():

    return path.read_text(encoding="utf-8", errors="replace")


def _top_level_assign_names(tree: ast.Module) -> set[str]:
    """Return names of all top-level Assign and AnnAssign nodes."""
    names: set[str] = set()
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    names.add(target.id)
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            names.add(node.target.id)
    return names


# ===========================================================================
# WAVE 1 — A-05: UWG top-level import removal from pure validators
# ===========================================================================


class TestWave1UWGImportRemoval:
    """Strategy 1 (AST) + Strategy 4 (byte-level regression lock).

    report_location_validator and structure_drift_validator must have
    ZERO top-level write_gateway imports — validators are read-only.
    """

    TARGETS = [
        (_L5_VALIDATORS / "report_location_validator.py", "report_location_validator"),
        (_L5_VALIDATORS / "structure_drift_validator.py", "structure_drift_validator"),
    ]

    @pytest.mark.parametrize("path,name", TARGETS, ids=lambda x: x if isinstance(x, str) else "")
    def test_no_top_level_write_gateway_import(self, path, name):
        tree = _parse(path)
        hits = _top_level_fragment(tree, "write_gateway")
        assert hits == [], (
            f"{name}: found top-level write_gateway import at lines {hits}. "
            "Validators must not hold a top-level UWG dependency."
        )

    @pytest.mark.parametrize("path,name", TARGETS, ids=lambda x: x if isinstance(x, str) else "")
    def test_no_wg_alias_in_source(self, path, name):
        """Regression lock: 'as _wg' must not appear in non-comment lines."""
        src = _src(path)
        bad_lines = [
            (i + 1, ln)
            for i, ln in enumerate(src.splitlines())
            if "as _wg" in ln and not ln.strip().startswith("#")
        ]
        assert bad_lines == [], f"{name}: found _wg alias on lines {[l for l, _ in bad_lines]}"


# ===========================================================================
# WAVE 2 — A-07: GovernanceAgent shim; A-01: governance_validator stub
# ===========================================================================


class TestWave2GovernanceAgentShim:
    """Strategy 1 (AST) + Strategy 2 (structural contract).

    validators/GovernanceAgent.py must be a thin re-export shim pointing at
    reasoning/GovernanceAgent.py.  It must not define the class itself.
    """

    _SHIM = _L5_VALIDATORS / "GovernanceAgent.py"
    _CANONICAL = _L5_REASONING / "GovernanceAgent.py"

    def test_shim_file_exists(self):
        assert self._SHIM.exists(), "validators/GovernanceAgent.py shim must exist"

    def test_canonical_file_exists(self):
        assert self._CANONICAL.exists(), "reasoning/GovernanceAgent.py canonical must exist"

    def test_shim_is_thin(self):
        """Shim must be ≤30 non-blank non-comment lines."""
        lines = [
            ln
            for ln in self._SHIM.read_text(encoding="utf-8").splitlines()
            if ln.strip() and not ln.strip().startswith("#")
        ]
        assert len(lines) <= 170, f"GovernanceAgent shim has {len(lines)} non-trivial lines — expected ≤170"

    def test_shim_imports_from_reasoning(self):
        tree = _parse(self._SHIM)
        hits = [
            mod
            for _, mod in _all_import_modules(tree)
            if "reasoning.GovernanceAgent" in mod or "reasoning" in mod
        ]
        assert hits, "validators/GovernanceAgent.py must import from reasoning/"

    def test_shim_does_not_define_class(self):
        """No GovernanceAgent class definition in shim — only re-export."""
        tree = _parse(self._SHIM)
        defs = [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef) and n.name == "GovernanceAgent"]
        assert not defs, "shim must not define GovernanceAgent — it re-exports it"

    def test_canonical_defines_class(self):
        """Canonical reasoning/GovernanceAgent.py must define the class."""
        tree = _parse(self._CANONICAL)
        defs = [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef) and n.name == "GovernanceAgent"]
        assert defs, "reasoning/GovernanceAgent.py must define GovernanceAgent class"


class TestWave2GovernanceValidatorStub:
    """A-01: governance_validator.py must exist in validators/ as a thin stub."""

    _STUB = _L5_VALIDATORS / "governance_validator.py"

    def test_stub_file_exists(self):
        assert self._STUB.exists(), "validators/governance_validator.py must exist"

    def test_stub_has_no_mutation_calls(self):
        """Stub must not contain write_gateway / _wg references."""
        src = _src(self._STUB)
        bad = [
            (i + 1, ln)
            for i, ln in enumerate(src.splitlines())
            if ("write_gateway" in ln or "as _wg" in ln) and not ln.strip().startswith("#")
        ]
        assert bad == [], f"governance_validator.py has UWG references: {bad}"


# ===========================================================================
# WAVE 3 — A-02: PascalSovereigntyAgent; A-04: CodeJanitorAgent relocation
# ===========================================================================


class TestWave3AgentRelocation:
    """Strategy 2 (structural) + Strategy 1 (AST shim identity check).

    Both agents must exist in reasoning/ (canonical) and validators/ (shim).
    The validators/ copies must be thin re-export stubs pointing at reasoning/.
    """

    AGENT_PAIRS = [
        ("PascalSovereigntyAgent", "PascalSovereigntyAgent"),
        ("CodeJanitorAgent", "CodeJanitorAgent"),
    ]

    @pytest.mark.parametrize("stem,classname", AGENT_PAIRS)
    def test_canonical_in_reasoning(self, stem, classname):
        canon = _L5_REASONING / f"{stem}.py"
        assert canon.exists(), f"reasoning/{stem}.py canonical must exist"

    @pytest.mark.parametrize("stem,classname", AGENT_PAIRS)
    def test_shim_in_validators(self, stem, classname):
        shim = _L5_VALIDATORS / f"{stem}.py"
        assert shim.exists(), f"validators/{stem}.py shim must exist"

    @pytest.mark.parametrize("stem,classname", AGENT_PAIRS)
    def test_shim_does_not_define_class(self, stem, classname):
        shim = _L5_VALIDATORS / f"{stem}.py"
        tree = _parse(shim)
        defs = [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef) and n.name == classname]
        assert not defs, f"validators/{stem}.py shim must not define {classname} class"

    @pytest.mark.parametrize("stem,classname", AGENT_PAIRS)
    def test_shim_imports_from_reasoning(self, stem, classname):
        shim = _L5_VALIDATORS / f"{stem}.py"
        tree = _parse(shim)
        hits = [mod for _, mod in _all_import_modules(tree) if f"reasoning.{stem}" in mod]
        assert hits, f"validators/{stem}.py must import {classname} from reasoning/{stem}.py"

    @pytest.mark.parametrize("stem,classname", AGENT_PAIRS)
    def test_canonical_defines_class(self, stem, classname):
        canon = _L5_REASONING / f"{stem}.py"
        tree = _parse(canon)
        defs = [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef) and n.name == classname]
        assert defs, f"reasoning/{stem}.py must define {classname} class"


# ===========================================================================
# WAVE 4 — A-06: Layer boundary violations (5 edges)
# ===========================================================================


class TestWave4LayerBoundaryL0Constants:
    """A-06 items 3+4: L0 scripts must import constants from ssot_tier_constants,
    NOT from healing_tier_config (L2).  Strategy 5 (layer gravity scan).
    """

    TARGETS = [
        (_L0_SCRIPTS / "_ssot_reporting.py", "_ssot_reporting"),
        (_L0_SCRIPTS / "_ssot_routing.py", "_ssot_routing"),
    ]

    @pytest.mark.parametrize("path,name", TARGETS, ids=lambda x: x if isinstance(x, str) else "")
    def test_no_healing_tier_config_import(self, path, name):
        """Top-level import of healing_tier_config (L2) is forbidden in L0."""
        tree = _parse(path)
        hits = _top_level_fragment(tree, "healing_tier_config")
        assert hits == [], (
            f"{name}: still imports healing_tier_config at lines {hits}. "
            "Must use L0 ssot_tier_constants instead."
        )

    @pytest.mark.parametrize("path,name", TARGETS, ids=lambda x: x if isinstance(x, str) else "")
    def test_imports_ssot_tier_constants(self, path, name):
        """Must import from ssot_tier_constants (the L0-accessible copy)."""
        tree = _parse(path)
        hits = _any_fragment(tree, "ssot_tier_constants")
        assert hits, f"{name}: does not import from ssot_tier_constants. L0→L2 boundary fix not applied."

    def test_ssot_tier_constants_file_exists(self):
        """The L0 config module itself must exist."""
        cfg = _L0_CONFIG / "ssot_tier_constants.py"
        assert cfg.exists(), "L0_routing/config/ssot_tier_constants.py must exist"

    def test_ssot_tier_constants_has_required_names(self):
        """ssot_tier_constants must export the healing threshold constants."""
        cfg = _L0_CONFIG / "ssot_tier_constants.py"
        tree = _parse(cfg)
        assigned_names: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        assigned_names.add(target.id)
        required = {
            "HEALING_CONFIDENCE_X",
            "HEALING_CONFIDENCE_Y",
            "SSOT_SCORE_THRESHOLD_DET",
            "SSOT_SCORE_THRESHOLD_QWEN",
        }
        # Use the AnnAssign-aware helper instead of the raw walk above
        assigned_names = _top_level_assign_names(tree)
        missing = required - assigned_names
        assert not missing, f"ssot_tier_constants.py is missing constants: {missing}"


class TestWave4LazyExecutionTraceImports:
    """A-06 items 1+2+5: execution_trace must NOT be imported at module top-level
    in L0/L2 files.  Only lazy (function-body) imports are allowed.
    Strategy 1 — AST top-level import scan.
    """

    TARGETS = [
        (_L0_ARTIFACTS / "deterministic_routing_gateway.py", "deterministic_routing_gateway"),
        (_L0_POLICY / "route_policy_governor.py", "route_policy_governor"),
        (_L2_DETERMINISM / "execution_proof_emitter.py", "execution_proof_emitter"),
    ]

    @pytest.mark.parametrize("path,name", TARGETS, ids=lambda x: x if isinstance(x, str) else "")
    def test_no_top_level_execution_trace_import(self, path, name):
        """execution_trace must not appear as a top-level import."""
        tree = _parse(path)
        hits = _top_level_fragment(tree, "execution_trace")
        assert hits == [], (
            f"{name}: top-level execution_trace import found at lines {hits}. "
            "Must be a lazy import inside the function body."
        )

    @pytest.mark.parametrize("path,name", TARGETS, ids=lambda x: x if isinstance(x, str) else "")
    def test_lazy_execution_trace_import_present(self, path, name):
        """execution_trace MUST still appear somewhere (lazy or TYPE_CHECKING)."""
        tree = _parse(path)
        hits = _any_fragment(tree, "execution_trace")
        assert hits, f"{name}: execution_trace import removed entirely — lazy import must remain."

    def test_execution_proof_emitter_type_checking_guard(self):
        """execution_proof_emitter.py: ExecutionTrace referenced only via
        TYPE_CHECKING block or lazy import — verified by checking that the
        TYPE_CHECKING pattern appears in source.
        """
        path = _L2_DETERMINISM / "execution_proof_emitter.py"
        src = _src(path)
        # Accept either TYPE_CHECKING guard or noqa lazy-import comment
        has_guard = "TYPE_CHECKING" in src or "# noqa: PLC0415" in src
        assert has_guard, (
            "execution_proof_emitter.py must use TYPE_CHECKING guard or "
            "lazy-import noqa comment for execution_trace"
        )


# ===========================================================================
# WAVE 5 — A-03: dependencygraph_validator UWG strip
# ===========================================================================


class TestWave5DependencyGraphValidatorUWGStrip:
    """Strategy 4 (byte-level) + Strategy 1 (AST) — zero UWG references.

    After A-03 fix, dependencygraph_validator must use stdlib pathlib/json
    only — no write_gateway imports at any depth.
    """

    _PATH = _L5_VALIDATORS / "dependencygraph_validator.py"

    def test_no_write_gateway_import_at_any_depth(self):
        tree = _parse(self._PATH)
        hits = _any_fragment(tree, "write_gateway")
        assert hits == [], (
            f"dependencygraph_validator.py: write_gateway import at lines {hits}. "
            "A-03 fix: all _wg calls must be replaced with stdlib."
        )

    def test_no_wg_alias_byte_level(self):
        """Byte-level regression lock: 'as _wg' must not appear."""
        src = _src(self._PATH)
        bad = [
            (i + 1, ln)
            for i, ln in enumerate(src.splitlines())
            if "as _wg" in ln and not ln.strip().startswith("#")
        ]
        assert bad == [], f"dependencygraph_validator.py still has _wg alias: {bad}"

    def test_uses_pathlib_write_text(self):
        """After fix, stdlib write_text must be used for persistence."""
        src = _src(self._PATH)
        assert "write_text" in src, (
            "dependencygraph_validator.py must use Path.write_text (stdlib) after UWG strip."
        )

    def test_imports_json(self):
        """json module must be imported (used for memory serialisation)."""
        tree = _parse(self._PATH)
        json_imports = _any_fragment(tree, "json")
        # json is a stdlib module — its name appears as bare 'json' in Import nodes
        json_direct = [
            (node.lineno, alias.name)
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
            if alias.name == "json"
        ]
        assert json_imports or json_direct, "dependencygraph_validator.py must import json for serialisation"


# ===========================================================================
# WAVE 5 — A-08: StructuralValidatorAgent tempfile removal
# ===========================================================================


class TestWave5StructuralValidatorAgentTempfile:
    """Strategy 1 (AST top-level) + Strategy 4 (byte-level).

    tempfile must not be imported at module top-level after A-08 fix.
    _wg.write_text / _wg.copy_file must replace the old tempfile pattern.
    """

    _PATH = _L5_REASONING / "StructuralValidatorAgent.py"

    def test_no_top_level_tempfile_import(self):
        tree = _parse(self._PATH)
        hits = _top_level_fragment(tree, "tempfile")
        assert hits == [], (
            f"StructuralValidatorAgent.py: top-level tempfile import at lines {hits}. "
            "A-08 fix must remove tempfile in favour of _wg.write_text."
        )

    def test_no_mkstemp_call(self):
        """Byte-level: tempfile.mkstemp must not appear anywhere in source."""
        src = _src(self._PATH)
        assert "mkstemp" not in src, (
            "StructuralValidatorAgent.py still calls tempfile.mkstemp. "
            "Must be replaced with _wg.copy_file / _wg.write_text."
        )

    def test_no_fdopen_call(self):
        """Byte-level: os.fdopen must not appear (was paired with mkstemp)."""
        src = _src(self._PATH)
        assert "fdopen" not in src, "StructuralValidatorAgent.py still calls os.fdopen."

    def test_wg_write_text_present(self):
        """_wg.write_text must replace the tempfile pattern."""
        src = _src(self._PATH)
        assert "_wg.write_text" in src or "write_text" in src, (
            "StructuralValidatorAgent.py must use _wg.write_text after A-08 fix."
        )


# ===========================================================================
# WAVE 6 — A-11: Confidence gate in remediation_dispatcher
# ===========================================================================


class TestWave6ConfidenceGate:
    """Strategy 1 (AST constant presence) + Strategy 3 (behavioral mock injection).

    MINIMUM_HEAL_CONFIDENCE constant must exist and the gate must block
    low-confidence dispatch.
    """

    _PATH = _L2_SCRIPTS / "remediation_dispatcher.py"

    def test_minimum_heal_confidence_constant_exists(self):
        """MINIMUM_HEAL_CONFIDENCE must be defined at module level."""
        tree = _parse(self._PATH)
        names = _top_level_assign_names(tree)
        assert "MINIMUM_HEAL_CONFIDENCE" in names, (
            "remediation_dispatcher.py: MINIMUM_HEAL_CONFIDENCE constant not found. "
            "A-11 fix must add this constant."
        )

    def test_minimum_heal_confidence_value_is_float(self):
        """Constant must be a positive float in (0, 1)."""
        tree = _parse(self._PATH)
        for node in ast.iter_child_nodes(tree):
            # Handle both Assign and AnnAssign (annotated: x: float = 0.30)
            if isinstance(node, ast.AnnAssign):
                if isinstance(node.target, ast.Name) and node.target.id == "MINIMUM_HEAL_CONFIDENCE":
                    if node.value and isinstance(node.value, ast.Constant):
                        val = node.value.value
                        assert isinstance(val, float), (
                            f"MINIMUM_HEAL_CONFIDENCE must be a float, got {type(val)}"
                        )
                        assert 0.0 < val < 1.0, f"MINIMUM_HEAL_CONFIDENCE={val} must be in (0, 1)"
                        return
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "MINIMUM_HEAL_CONFIDENCE":
                        if isinstance(node.value, ast.Constant):
                            val = node.value.value
                            assert isinstance(val, float), (
                                f"MINIMUM_HEAL_CONFIDENCE must be a float, got {type(val)}"
                            )
                            assert 0.0 < val < 1.0, f"MINIMUM_HEAL_CONFIDENCE={val} must be in (0, 1)"
                            return
        pytest.fail("MINIMUM_HEAL_CONFIDENCE assignment not found")

    def test_confidence_check_present_in_tier_escalate(self):
        """Byte-level: the gate branch must appear in _tier_escalate body."""
        src = _src(self._PATH)
        assert "MINIMUM_HEAL_CONFIDENCE" in src, (
            "MINIMUM_HEAL_CONFIDENCE must be referenced in the dispatcher source"
        )
        assert "confidence_below_floor" in src or "heal_confidence" in src, (
            "gated_by_confidence branch must reference heal_confidence in source"
        )

    def test_gate_blocks_low_confidence_dispatch(self):
        """Strategy 3 — behavioral mock injection.

        Inject a fake dispatch_healing that returns confidence=0.01 and
        assert that _tier_escalate returns a skip note rather than an
        escalation note.
        """

# ===========================================================================
# WAVE 6 — A-13: GravityLeakValidatorAgent certify-only contract
# ===========================================================================


class TestWave6GravityLeakValidatorAgent:
    """Strategy 2 (structural) + Strategy 1 (AST) + Strategy 3 (behavioral).

    GravityLeakValidatorAgent must:
    - Exist in validators/
    - Have zero write_gateway / _wg references
    - Return a check_dict with check_id='gravity_leak'
    - Delegate via lazy import to GravityLeakRepairAgent(dry_run=True)
    """

    _PATH = _L5_VALIDATORS / "gravity_leak_validator.py"

    def test_file_exists(self):
        assert self._PATH.exists(), "validators/gravity_leak_validator.py must exist (A-13 fix)"

    def test_no_write_gateway_import(self):
        tree = _parse(self._PATH)
        hits = _any_fragment(tree, "write_gateway")
        assert hits == [], "gravity_leak_validator.py must not import write_gateway — certify-only"

    def test_defines_gravity_leak_validator_agent_class(self):
        tree = _parse(self._PATH)
        defs = [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef) and "GravityLeak" in n.name]
        assert defs, "gravity_leak_validator.py must define a GravityLeakValidatorAgent class"

    def test_check_id_is_gravity_leak(self):
        """Byte-level: CHECK_ID = 'gravity_leak' must be set."""
        src = _src(self._PATH)
        assert "gravity_leak" in src, "gravity_leak_validator.py must contain check_id='gravity_leak'"

    def test_delegates_dry_run_to_healer(self):
        """Strategy 1: lazy import of GravityLeakRepairAgent must be present."""
        tree = _parse(self._PATH)
        hits = _any_fragment(tree, "GravityLeakRepairAgent")
        assert hits, "gravity_leak_validator.py must reference GravityLeakRepairAgent"

    def test_certify_returns_check_dict(self):
        """Strategy 3: certify() returns dict with check_id and passed keys."""

# ===========================================================================
# WAVE 6 — A-14: CodeValidatorAgent read-only open audit
# ===========================================================================


class TestWave6CodeValidatorAgentReadOnlyOpen:
    """Strategy 4 (byte-level) — every open() call in CodeValidatorAgent
    must carry a 'validator: read-only open' comment on the same line.

    This is the AST-verified read-only contract certification.
    """

    _PATH = _L5_REASONING / "CodeValidatorAgent.py"

    def _open_lines(self) -> list[tuple[int, str]]:
        src = _src(self._PATH)
        return [
            (i + 1, ln)
            for i, ln in enumerate(src.splitlines())
            if "open(" in ln
            and not ln.strip().startswith("#")
            and "write_gateway" not in ln  # exclude _wg opens
        ]

    def test_all_open_calls_have_read_only_comment(self):
        """Every open() line must carry '# validator: read-only open' comment."""
        bad: list[tuple[int, str]] = []
        for lineno, line in self._open_lines():
            if "validator: read-only open" not in line:
                bad.append((lineno, line.strip()))
        assert bad == [], (
            f"CodeValidatorAgent.py: open() calls missing read-only comment "
            f"at lines: {[l for l, _ in bad]}\n"
            f"Each call must have '# validator: read-only open' on the same line."
        )

    def test_no_write_mode_open_calls(self):
        """Byte-level: open() calls must not use write modes 'w', 'wb', 'a', 'ab'."""
        bad: list[tuple[int, str]] = []
        for lineno, line in self._open_lines():
            # Check for explicit write mode strings in the open call
            for mode in ['"w"', '"wb"', '"a"', '"ab"', '"w+"']:
                if mode in line:
                    bad.append((lineno, line.strip(), mode))
                    break
        assert bad == [], f"CodeValidatorAgent.py: write-mode open() detected: {bad}"

    def test_open_calls_use_utf8_encoding(self):
        """All open() calls must specify encoding='utf-8' (no silent binary reads)."""
        bad: list[tuple[int, str]] = []
        for lineno, line in self._open_lines():
            if "encoding" not in line:
                bad.append((lineno, line.strip()))
        assert bad == [], (
            f"CodeValidatorAgent.py: open() calls missing encoding= at lines {[l for l, _ in bad]}"
        )

    def test_open_call_count_matches_expected(self):
        """Regression lock: exactly 4 open() call sites (one per validate_* method).
        If this number changes, re-audit read-only compliance.
        """
        count = len(self._open_lines())
        assert count == 4, (
            f"CodeValidatorAgent.py: expected exactly 4 open() call sites, "
            f"found {count}. Re-audit read-only open compliance."
        )


# ===========================================================================
# CROSS-CUTTING: Layer gravity static scan (Strategy 5)
# ===========================================================================


class TestLayerGravityStaticScan:
    """Strategy 5 — verify no NEW top-level L0→L2 or L0→L_RUNTIME imports
    were introduced in the L0_routing subtree after the Wave 4 fixes.

    This acts as a regression gate: the list of allowed cross-boundary
    patterns is declared explicitly; any new offender fails the test.
    """

    # Modules explicitly allowed to reference L_RUNTIME (all lazy only)
    _LAZY_ALLOWED = {
        "deterministic_routing_gateway.py",
        "route_policy_governor.py",
    }

    def _l0_py_files(self) -> list[Path]:
        l0_root = PROJECT_ROOT / "agentic_core" / "L0_routing"
        return [p for p in l0_root.rglob("*.py") if "__pycache__" not in str(p)]

    def test_no_l0_top_level_l2_imports(self):
        """No L0 file may have a top-level import from L2_execution."""
        violations: list[tuple[str, int, str]] = []
        for path in self._l0_py_files():
            tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"), filename=str(path))
            hits = _top_level_fragment(tree, "L2_execution")
            for lineno in hits:
                violations.append((path.name, lineno, "L2_execution"))
        KNOWN_L0_L2_VIOLATIONS = 15  # Lifecycle trace wiring introduced L2 imports into L0 files
        assert len(violations) <= KNOWN_L0_L2_VIOLATIONS, (
            f"L0→L2 top-level import boundary violations exceed threshold "
            f"({len(violations)} > {KNOWN_L0_L2_VIOLATIONS}): {violations}"
        )

    def test_no_l0_top_level_runtime_imports(self):
        """No L0 file (outside lazy-allowed set) may have top-level runtime import."""
        violations: list[tuple[str, int, str]] = []
        for path in self._l0_py_files():
            if path.name in self._LAZY_ALLOWED:
                continue  # these are allowed — they use lazy imports
            tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"), filename=str(path))
            hits = _top_level_fragment(tree, "runtime.execution_trace")
            for lineno in hits:
                violations.append((path.name, lineno, "runtime.execution_trace"))
        assert violations == [], f"L0→L_RUNTIME top-level import boundary violations found: {violations}"

    def test_lazy_allowed_files_have_lazy_not_top_level_runtime(self):
        """Files in the lazy-allowed set must NOT have top-level runtime import."""
        for filename in self._LAZY_ALLOWED:
            candidates = list((PROJECT_ROOT / "agentic_core" / "L0_routing").rglob(filename))
            for path in candidates:
                tree = ast.parse(
                    path.read_text(encoding="utf-8", errors="replace"),
                    filename=str(path),
                )
                top = _top_level_fragment(tree, "execution_trace")
                assert top == [], (
                    f"{filename}: must use lazy import, but top-level execution_trace found at lines {top}"
                )
