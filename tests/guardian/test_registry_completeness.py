"""
Phase 1: Registry Completeness Gate (Registry-First Policy).

The SSOT guardian registry is the SOLE AUTHORITY for guardian enumeration.
Filesystem discovery is a diagnostic sanity check only — tests pass even if
the discovery helpers are broken, provided the registry itself is correct.

Invariants:
1. Every registry entry points to an importable callable
2. Every callable returns GuardianResult (annotation check)
3. Guardian IDs are unique; check_ids are unique per guardian
4. Aggregator/integrity checker invoke via registry only (no globs)
5. GUARDIAN_ID in scripts must be a literal string constant (policy)
6. (Diagnostic) Filesystem discovery warns on orphan scripts
"""

from __future__ import annotations

import ast
import importlib
import sys
import warnings
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

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_registry_completeness")
# REMOVED: _emit_applies_guardrail("p0", "test_registry_completeness", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_registry_completeness", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_registry_completeness", "state_snapshot")
# REMOVED: emit_replay_key("p0", "test_registry_completeness")
# REMOVED: emit_determinism_digest("p0", "test_registry_completeness")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_registry_completeness", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_registry_completeness", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_registry_completeness", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_registry_completeness", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_registry_completeness", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_registry_completeness", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_registry_completeness", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_registry_completeness", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_registry_completeness", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_registry_completeness", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_registry_completeness", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_registry_completeness", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_registry_completeness", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_registry_completeness", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_registry_completeness", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_registry_completeness", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_registry_completeness", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_registry_completeness", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_registry_completeness", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_registry_completeness", "exec_snapshot_link")

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agentic_core.L0_routing.config.path_constants import AGENTIC_CORE_DIR
from agentic_core.L0_routing.types.guardian_registry_types import (
    ALL_GUARDIANS,
    GuardianTier,
    get_guardian_specs,
)
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

# REMOVED: _emit_emits_metric_event("test_registry_completeness", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_registry_completeness", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_registry_completeness", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_registry_completeness", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_registry_completeness", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_registry_completeness", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_registry_completeness", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_registry_completeness", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_registry_completeness", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_registry_completeness", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_registry_completeness", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_registry_completeness", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_registry_completeness", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_registry_completeness", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_registry_completeness", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_registry_completeness", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_registry_completeness", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_registry_completeness", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_registry_completeness", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_registry_completeness", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_registry_completeness", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_registry_completeness", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_registry_completeness", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_registry_completeness", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_registry_completeness", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_registry_completeness", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_registry_completeness", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_registry_completeness", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_registry_completeness", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_registry_completeness", "context_pull_secondary")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_registry_completeness", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_registry_completeness", "uwg_term_secondary")
# REMOVED: _emit_writes_through("p1", "test_registry_completeness", "write_through")
# REMOVED: _emit_writes_through("p1", "test_registry_completeness", "write_through_secondary")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_registry_completeness", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_registry_completeness", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_registry_completeness", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_registry_completeness", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_registry_completeness", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_registry_completeness", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_registry_completeness", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_registry_completeness", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_registry_completeness", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_registry_completeness", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_registry_completeness", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_registry_completeness", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_registry_completeness", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_registry_completeness", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_registry_completeness")
# REMOVED: _emit_gated_by_confidence("p1", "test_registry_completeness", "confidence_gate")

pytestmark = pytest.mark.guardian

GUARDIAN_SCRIPTS_DIR = PROJECT_ROOT / AGENTIC_CORE_DIR / "L0_routing" / "scripts"


# ---------------------------------------------------------------------------
# AST helpers (diagnostic only — not on the enforcement path)
# ---------------------------------------------------------------------------


def _extract_guardian_id_from_script(script_path: Path) -> str | None:
    """
    Extract GUARDIAN_ID constant from a guardian script via AST.
    Returns None if not found or parse error.
    """
    try:
        source = script_path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(script_path))

        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "GUARDIAN_ID":
                        if isinstance(node.value, ast.Constant):
                            return node.value.value
        return None
    except (OSError, UnicodeDecodeError, SyntaxError):
        return None


def _discover_guardian_scripts() -> dict[str, Path]:
    """
    Discover all run_guardian_*.py scripts via filesystem.
    Returns dict mapping guardian_id → script_path.
    """
    scripts = GUARDIAN_SCRIPTS_DIR.glob("run_guardian_*.py")
    discovered = {}
    for script in scripts:
        guardian_id = _extract_guardian_id_from_script(script)
        if guardian_id:
            discovered[guardian_id] = script
    return discovered


# ===================================================================
# CORE TESTS — Registry is SSOT (no filesystem dependency)
# ===================================================================


class TestRegistryIsSSoT:
    """Registry is sole authority. These tests pass without filesystem discovery."""

    def test_no_dead_registry_entries(self):
        """Every registry entry must point to an importable callable."""
        errors = []
        for spec in ALL_GUARDIANS:
            try:
                mod = importlib.import_module(spec.entrypoint_module)
                if not hasattr(mod, spec.entrypoint_fn):
                    errors.append(
                        f"{spec.guardian_id}: function '{spec.entrypoint_fn}' "
                        f"not found in {spec.entrypoint_module}",
                    )
            except ImportError as exc:  # guardian: allow-silent-swallower
                errors.append(f"{spec.guardian_id}: ImportError - {exc}")

        assert not errors, "Dead registry entries:\n" + "\n".join(errors)

    def test_all_entrypoints_return_guardian_result(self):
        """Every callable must return GuardianResult (annotation check)."""
        errors = []
        for spec in ALL_GUARDIANS:
            try:
                mod = importlib.import_module(spec.entrypoint_module)
                fn = getattr(mod, spec.entrypoint_fn)

                if hasattr(fn, "__annotations__"):
                    return_type = fn.__annotations__.get("return")
                    if return_type is not None:
                        type_str = str(return_type)
                        if "GuardianResult" not in type_str:
                            errors.append(
                                f"{spec.guardian_id}: return type is {return_type}, expected GuardianResult",
                            )
            except Exception as exc:  # guardian: allow-silent-swallower
                errors.append(f"{spec.guardian_id}: validation error - {exc}")

        assert not errors, "Invalid return types:\n" + "\n".join(errors)

    def test_all_registered_guardians_have_unique_ids(self):
        """Guardian IDs must be unique in registry."""
        ids = [spec.guardian_id for spec in ALL_GUARDIANS]
        duplicates = [gid for gid in ids if ids.count(gid) > 1]
        assert not duplicates, f"Duplicate guardian_ids in registry: {set(duplicates)}"

    def test_all_check_ids_are_unique_per_guardian(self):
        """Each guardian's check_ids must be unique within that guardian."""
        errors = []
        for spec in ALL_GUARDIANS:
            check_ids = list(spec.check_ids)
            duplicates = [cid for cid in check_ids if check_ids.count(cid) > 1]
            if duplicates:
                errors.append(f"{spec.guardian_id}: duplicate check_ids {set(duplicates)}")

        assert not errors, "Duplicate check_ids:\n" + "\n".join(errors)

    def test_all_check_ids_globally_unique(self):
        """No two guardians may share the same check_id."""
        seen: dict[str, str] = {}  # check_id → guardian_id
        collisions = []
        for spec in ALL_GUARDIANS:
            for cid in spec.check_ids:
                if cid in seen:
                    collisions.append(
                        f"check_id '{cid}' claimed by both '{seen[cid]}' and '{spec.guardian_id}'",
                    )
                else:
                    seen[cid] = spec.guardian_id
        assert not collisions, "Global check_id collisions:\n" + "\n".join(collisions)


# ===================================================================
# POLICY ENFORCEMENT — GUARDIAN_ID must be literal string constant
# ===================================================================


class TestGuardianIdPolicy:
    """GUARDIAN_ID in scripts must be a literal string constant (not computed/imported)."""

    def test_guardian_id_is_literal_in_all_scripts(self):
        """Every run_guardian_*.py must define GUARDIAN_ID as a string literal."""
        errors = []
        for script in sorted(GUARDIAN_SCRIPTS_DIR.glob("run_guardian_*.py")):
            try:
                source = script.read_text(encoding="utf-8")
                tree = ast.parse(source, filename=str(script))

                found_literal = False
                for node in ast.walk(tree):
                    if isinstance(node, ast.Assign):
                        for target in node.targets:
                            if isinstance(target, ast.Name) and target.id == "GUARDIAN_ID":
                                if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                                    found_literal = True
                                else:
                                    errors.append(
                                        f"{script.name}: GUARDIAN_ID is not a string literal "
                                        f"(found {type(node.value).__name__}). "
                                        f"Policy requires literal assignment.",
                                    )

                if not found_literal and not errors:
                    errors.append(f"{script.name}: GUARDIAN_ID constant not found")
            except SyntaxError as exc:  # guardian: allow-silent-swallower
                errors.append(f"{script.name}: SyntaxError at line {exc.lineno}")

        assert not errors, "GUARDIAN_ID policy violations:\n" + "\n".join(errors)


# ===================================================================
# NO FILESYSTEM FALLBACK — aggregator + integrity use registry only
# ===================================================================


class TestNoFilesystemFallback:
    """Aggregator and integrity checker must use registry only, no filesystem globs."""

    def test_run_all_guardians_no_glob_imports(self):
    """Test run_all_guardians_no_glob_imports runtime behavior."""
    # Arrange
    # TODO: Set up execution parameters
    input_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute run_all_guardians_no_glob_imports
    result = None  # Replace with actual execution

    # Assert
    assert result is not None, f"{function_name} should return a result"
    assert isinstance(result, (dict, list, str, int, float, bool)), "Result should be a common type"
    # TODO: Add specific execution assertions
        script = GUARDIAN_SCRIPTS_DIR / "run_guardian_contract_integrity.py"
        content = script.read_text(encoding="utf-8")

        forbidden = ["glob.glob", "Path.glob", "GUARDIAN_SCRIPT_PATTERN"]
        found = [pattern for pattern in forbidden if pattern in content]

        assert not found, (
            f"run_guardian_contract_integrity.py contains filesystem discovery: {found}. "
            f"Must use registry only."
        )


# ===================================================================
# DIAGNOSTIC SANITY CHECK — filesystem discovery (warning, not enforcement)
# ===================================================================


class TestFilesystemDiagnostic:
    """Filesystem discovery is a sanity check. Orphans emit warnings, not failures."""

    def test_no_orphan_scripts_diagnostic(self):
        """Warn (not fail) if filesystem has scripts not in registry."""
        discovered = _discover_guardian_scripts()
        registered = {spec.guardian_id for spec in ALL_GUARDIANS}

        orphans = set(discovered.keys()) - registered
        if orphans:
            warnings.warn(
                f"Diagnostic: unregistered guardian scripts found: {orphans}. "
                f"Add them to guardian_registry.py or remove the scripts.",
                stacklevel=1,
            )
        # Always passes — registry is SSOT, not filesystem

    def test_registry_covers_discovered_scripts(self):
        """Warn if registry has entries not found on filesystem."""
        discovered = _discover_guardian_scripts()
        registered = {spec.guardian_id for spec in ALL_GUARDIANS}

        missing_on_disk = registered - set(discovered.keys())
        if missing_on_disk:
            warnings.warn(
                f"Diagnostic: registry entries without matching script: {missing_on_disk}. "
                f"Scripts may have been renamed or moved.",
                stacklevel=1,
            )
        # Always passes — registry is SSOT

    def test_discovery_count_matches_registry(self):
        """Diagnostic: count comparison between registry and filesystem."""
        discovered = _discover_guardian_scripts()
        registered = {spec.guardian_id for spec in ALL_GUARDIANS}

        if len(registered) != len(discovered):
            warnings.warn(
                f"Diagnostic: registry count ({len(registered)}) != "
                f"discovered count ({len(discovered)}). "
                f"Registered: {sorted(registered)}, "
                f"Discovered: {sorted(discovered.keys())}",
                stacklevel=1,
            )


# ===================================================================
# TIER FILTERING — get_guardian_specs(tier=...) returns correct subset
# ===================================================================


class TestTierFiltering:
    """get_guardian_specs must correctly filter by GuardianTier."""

    def test_fast_tier_returns_only_fast(self):
        """All specs returned for FAST tier must have tier == 'fast'."""
        fast_specs = get_guardian_specs(tier=GuardianTier.FAST)
        assert all(s.tier == GuardianTier.FAST.value for s in fast_specs), (
            f"Non-FAST specs returned: {[s.guardian_id for s in fast_specs if s.tier != GuardianTier.FAST.value]}"
        )

    def test_slow_tier_returns_only_slow(self):
        """All specs returned for SLOW tier must have tier == 'slow'."""
        slow_specs = get_guardian_specs(tier=GuardianTier.SLOW)
        assert all(s.tier == GuardianTier.SLOW.value for s in slow_specs), (
            f"Non-SLOW specs returned: {[s.guardian_id for s in slow_specs if s.tier != GuardianTier.SLOW.value]}"
        )

    def test_tier_filter_is_exhaustive(self):
        """FAST + SLOW must cover all registered guardians."""
        fast = {s.guardian_id for s in get_guardian_specs(tier=GuardianTier.FAST)}
        slow = {s.guardian_id for s in get_guardian_specs(tier=GuardianTier.SLOW)}
        all_ids = {s.guardian_id for s in ALL_GUARDIANS}
        assert fast | slow == all_ids, f"Tier filter gap: {all_ids - fast - slow} not in FAST or SLOW"
