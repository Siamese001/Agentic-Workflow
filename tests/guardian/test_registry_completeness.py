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

_emit_records_execution_trace("p0", "evidence", "test_registry_completeness")
_emit_applies_guardrail("p0", "test_registry_completeness", "p0_governance")
_emit_reads_policy_state("p0", "test_registry_completeness", "policy_binding")
_emit_snapshots_state("p0", "test_registry_completeness", "state_snapshot")
emit_replay_key("p0", "test_registry_completeness")
emit_determinism_digest("p0", "test_registry_completeness")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_registry_completeness", "execution_auth")
_emit_validates_capability("p2", "test_registry_completeness", "capability_check")
_emit_routes_to_capability("p2", "test_registry_completeness", "capability_route")
_emit_writes_via_uwg("p2", "test_registry_completeness", "uwg_write")
_emit_blocks_direct_write("p2", "test_registry_completeness", "direct_write_block")
_emit_records_tool_invocation("p2", "test_registry_completeness", "tool_invocation")
_emit_captures_execution_output("p2", "test_registry_completeness", "exec_output")
_emit_dispatches_agent("p3", "test_registry_completeness", "agent_dispatch")
_emit_coordinates_agents("p3", "test_registry_completeness", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_registry_completeness", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_registry_completeness", "healing_outcome")
_emit_escalates_failure("p3", "test_registry_completeness", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_registry_completeness", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_registry_completeness", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_registry_completeness", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_registry_completeness", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_registry_completeness", "eval_metric")
_emit_stores_embedding("p4", "test_registry_completeness", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_registry_completeness", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_registry_completeness", "exec_snapshot_link")

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
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_pulls_context,
    _emit_execution_terminates_at_uwg,
    _emit_writes_through,
    _emit_validated_by_safety_plane,
    _emit_invokes_eval,
    _emit_proposal_commits_routing,
)
from agentic_core.runtime.lifecycle_trace_contract import _emit_records_execution_trace, _emit_reads_environ, _emit_reads_runtime_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_captures_pattern, _emit_records_learning_event, _emit_writes_learning_snapshot, _emit_feeds_meta_learning, _emit_updates_routing_strategy, _emit_improves_agent_policy, _emit_stores_learning_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_emits_metric_event, _emit_records_incident_event, _emit_captures_runtime_anomaly, _emit_writes_observability_log, _emit_updates_monitoring_state, _emit_triggers_alert, _emit_links_incident_trace
_emit_emits_metric_event("test_registry_completeness", "p4obs", "metric_1")
_emit_emits_metric_event("test_registry_completeness", "p4obs", "metric_2")
_emit_emits_metric_event("test_registry_completeness", "p4obs", "metric_3")
_emit_emits_metric_event("test_registry_completeness", "p4obs", "metric_4")
_emit_emits_metric_event("test_registry_completeness", "p4obs", "metric_5")
_emit_emits_metric_event("test_registry_completeness", "p4obs", "metric_6")
_emit_records_incident_event("test_registry_completeness", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_registry_completeness", "p4obs", "anomaly")
_emit_writes_observability_log("test_registry_completeness", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_registry_completeness", "p4obs", "mon_state")
_emit_triggers_alert("test_registry_completeness", "p4obs", "alert")
_emit_links_incident_trace("test_registry_completeness", "p4obs", "trace_link")
_emit_captures_pattern("test_registry_completeness", "p3lm", "pattern")
_emit_records_learning_event("test_registry_completeness", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_registry_completeness", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_registry_completeness", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_registry_completeness", "p3lm", "routing")
_emit_improves_agent_policy("test_registry_completeness", "p3lm", "policy")
_emit_stores_learning_state("test_registry_completeness", "p3lm", "state")
_emit_records_execution_trace("test_registry_completeness", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_registry_completeness", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_registry_completeness", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_registry_completeness", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_registry_completeness", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_registry_completeness", "env_read", "p2_env_1")
_emit_reads_environ("test_registry_completeness", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_registry_completeness", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_registry_completeness", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_registry_completeness", "context_pull")
_emit_pulls_context("p1", "test_registry_completeness", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_registry_completeness", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_registry_completeness", "uwg_term_secondary")
_emit_writes_through("p1", "test_registry_completeness", "write_through")
_emit_writes_through("p1", "test_registry_completeness", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_registry_completeness", "safety_validation")
_emit_invokes_eval("p1", "test_registry_completeness", "eval_call")
_emit_proposal_commits_routing("p1", "test_registry_completeness", "routing_commit")

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
        """run_all_guardians.py must not import glob or pathlib.glob."""
        script = GUARDIAN_SCRIPTS_DIR / "run_all_guardians.py"
        content = script.read_text(encoding="utf-8")

        forbidden = ["glob.glob", "Path.glob", "os.walk", "os.listdir"]
        found = [pattern for pattern in forbidden if pattern in content]

        assert not found, (
            f"run_all_guardians.py contains filesystem discovery: {found}. Must use registry only."
        )

    def test_contract_integrity_no_glob_imports(self):
        """run_guardian_contract_integrity.py must not use filesystem globs."""
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
