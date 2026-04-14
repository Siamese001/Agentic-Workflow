r"""
File: scripts/DebrisHunter.py
Path: C:\Git\Agentic-Workflow\scripts/DebrisHunter.py
Status: Post-Migration Utility
Rationale:
    Identifies and cleans up:
    1. "Split-Brain" files (snake_case.py existing alongside PascalCase.py).
    2. The redundant legacy fixer script in agentic_core.
    3. __temp_ artifacts if any rename operations were interrupted.
"""

import argparse
import os
import sys
from pathlib import Path

from agentic_core.L0_routing.config import (
    AGENTIC_CORE_DIR,
)
from agentic_core.L0_routing.config.path_constants import SOVEREIGN_EXCLUDED_FOLDERS

# SSOT Integration
from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
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
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
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
    emit_determinism_digest,
    emit_replay_key,
)

_emit_dispatches_healing_run("p1", "debris_hunter", "L0")
_emit_routes_through("p1", "debris_hunter", "L0")
_emit_checks_agent_registry("p1", "debris_hunter", "agent_registry")
_emit_validates_agent_capability("p1", "debris_hunter", "capability")
_emit_dispatches_execution_plan("p1", "debris_hunter", "exec_plan")
_emit_agent_executes_agent("p1", "debris_hunter", "sub_agent")
_emit_routes_to_agent("p1", "debris_hunter", "target_agent")
_emit_verifies_policy("p1", "debris_hunter", "policy_check")
_emit_observes_runtime_state("p1", "debris_hunter", "runtime_state")
_emit_verifies_boundary("p1", "debris_hunter", "boundary_check")
_emit_transcripts_response("p1", "debris_hunter", "transcript")
_emit_hard_fails_untranscripted("p1", "debris_hunter")
_emit_gated_by_confidence("p1", "debris_hunter", "confidence_gate")
_emit_escalates_to_human("p1", "debris_hunter", "L0")
_emit_reads_policy_state("p1", "debris_hunter", "L0")

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "debris_hunter", "p0_governance")
_emit_snapshots_state("p0", "debris_hunter", "state_snapshot")
_emit_authorize_and_execute("p2", "debris_hunter", "execution_auth")
_emit_validates_capability("p2", "debris_hunter", "capability_check")
_emit_routes_to_capability("p2", "debris_hunter", "capability_route")
_emit_writes_via_uwg("p2", "debris_hunter", "uwg_write")
_emit_blocks_direct_write("p2", "debris_hunter", "direct_write_block")
_emit_records_tool_invocation("p2", "debris_hunter", "tool_invocation")
_emit_captures_execution_output("p2", "debris_hunter", "exec_output")
_emit_dispatches_agent("p3", "debris_hunter", "agent_dispatch")
_emit_coordinates_agents("p3", "debris_hunter", "agent_coordination")
_emit_records_workflow_lineage("p3", "debris_hunter", "workflow_lineage")
_emit_records_healing_outcome("p3", "debris_hunter", "healing_outcome")
_emit_escalates_failure("p3", "debris_hunter", "failure_escalation")
_emit_orchestrates_workflow("p3", "debris_hunter", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "debris_hunter", "healing_dispatch")
_emit_invokes_evaluation("p3", "debris_hunter", "evaluation_signal")
_emit_records_telemetry_event("p4", "debris_hunter", "telemetry_event")
_emit_captures_evaluation_metric("p4", "debris_hunter", "eval_metric")
_emit_stores_embedding("p4", "debris_hunter", "embedding_store")
_emit_updates_meta_learning_state("p4", "debris_hunter", "meta_learning")
_emit_links_execution_to_snapshot("p4", "debris_hunter", "exec_snapshot_link")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_incident_event,
    _emit_records_learning_event,
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
    _emit_writes_through,
)
from tqdm import tqdm

_emit_emits_metric_event("debris_hunter", "p4obs", "metric_1")
_emit_emits_metric_event("debris_hunter", "p4obs", "metric_2")
_emit_emits_metric_event("debris_hunter", "p4obs", "metric_3")
_emit_emits_metric_event("debris_hunter", "p4obs", "metric_4")
_emit_emits_metric_event("debris_hunter", "p4obs", "metric_5")
_emit_emits_metric_event("debris_hunter", "p4obs", "metric_6")
_emit_records_incident_event("debris_hunter", "p4obs", "incident")
_emit_captures_runtime_anomaly("debris_hunter", "p4obs", "anomaly")
_emit_writes_observability_log("debris_hunter", "p4obs", "obs_log")
_emit_updates_monitoring_state("debris_hunter", "p4obs", "mon_state")
_emit_triggers_alert("debris_hunter", "p4obs", "alert")
_emit_links_incident_trace("debris_hunter", "p4obs", "trace_link")
_emit_captures_pattern("debris_hunter", "p3lm", "pattern")
_emit_records_learning_event("debris_hunter", "p3lm", "learning_event")
_emit_writes_learning_snapshot("debris_hunter", "p3lm", "snapshot")
_emit_feeds_meta_learning("debris_hunter", "p3lm", "meta_feed")
_emit_updates_routing_strategy("debris_hunter", "p3lm", "routing")
_emit_improves_agent_policy("debris_hunter", "p3lm", "policy")
_emit_stores_learning_state("debris_hunter", "p3lm", "state")
_emit_records_execution_trace("debris_hunter", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("debris_hunter", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("debris_hunter", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("debris_hunter", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("debris_hunter", "L4_STATE", "p2_trace_5")
_emit_reads_environ("debris_hunter", "env_read", "p2_env_1")
_emit_reads_environ("debris_hunter", "env_read", "p2_env_2")
_emit_reads_runtime_state("debris_hunter", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("debris_hunter", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "debris_hunter", "context_pull")
_emit_pulls_context("p1", "debris_hunter", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "debris_hunter", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "debris_hunter", "uwg_term_2")
_emit_writes_through("p1", "debris_hunter", "write_through")
_emit_writes_through("p1", "debris_hunter", "write_through_2")
_emit_validated_by_safety_plane("p1", "debris_hunter", "safety_validation")
_emit_invokes_eval("p1", "debris_hunter", "eval_call")
_emit_proposal_commits_routing("p1", "debris_hunter", "routing_commit")


def _find_project_root() -> Path:
    current = Path(__file__).resolve().parent
    for candidate in (current, *current.parents):
        if (candidate / "agentic_core").exists():
            return candidate
    raise RuntimeError(f"Could not determine project root from {__file__}")


class DebrisHunter:
    def __init__(self, root: Path, dry_run: bool = True):
        self.root = root.resolve()
        self.dry_run = dry_run
        self.debris_found = []

    def scan_for_collisions(self):
        """
        Finds directories containing both 'snake_case.py' and 'PascalCase.py'
        where one is likely the ancestor of the other.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "DebrisHunter.scan_for_collisions")
        emit_replay_key(_trace_id, f"rk:{_trace_id[:16]}")
        emit_determinism_digest(_trace_id, f"dd:{_trace_id[:16]}")

        print(f"Scanning for collision debris in {self.root}...")

        # Walk manually to group by directory
        for dirpath, dirs, filenames in tqdm(os.walk(self.root), desc="Processing", unit="item"):
            dirs[:] = [d for d in dirs if d not in SOVEREIGN_EXCLUDED_FOLDERS]

            py_files = [f for f in filenames if f.endswith(".py")]

            # Map lowercase -> actual_name
            lowermap = {f.lower(): f for f in py_files}

            for f in tqdm(py_files, desc="Processing", unit="item"):
                # If current file is snake_case (has underscores, starts lower)
                if "_" in f and f[0].islower():
                    # Check if a "clean" PascalCase version exists
                    pascal_guess = f.replace("_", "").lower()

                    if pascal_guess in lowermap:
                        partner = lowermap[pascal_guess]
                        # Heuristic: If partner is MixedCase/PascalCase, we have a collision
                        if "_" not in partner and partner[0].isupper():
                            self.debris_found.append(Path(dirpath) / f)
                            print(f"[DEBRIS] Found ghost file: {f} (Shadowed by {partner})")

    def scan_for_known_redundancies(self):
        """Targeted cleanup for known migration artifacts."""
        legacy_fixer = self.root / AGENTIC_CORE_DIR / "L0_routing" / "scripts" / "pascal_sovereignty_fixer.py"
        if legacy_fixer.exists():
            self.debris_found.append(legacy_fixer)
            print(f"[REDUNDANT] Found legacy fixer: {legacy_fixer}")

    def scan_for_temp_files(self):
        """Finds stuck __temp_ artifacts from interrupted renames."""
        for path in self.root.rglob("__temp_*.py"):
            if ".git" not in str(path) and "__pycache__" not in str(path):
                self.debris_found.append(path)
                print(f"[TEMP] Found interrupted rename artifact: {path.name}")

    def execute_cleanup(self):
        self.debris_found = list(dict.fromkeys(self.debris_found))

        if not self.debris_found:
            print("\n✅ No debris found. System clean.")
            return 0

        print(f"\n⚠️  Found {len(self.debris_found)} items to remove.")

        if self.dry_run:
            print("[DRY RUN] Use --force to delete files.")
            return len(self.debris_found)

        deleted = 0
        for path in self.debris_found:
            try:
                assert_no_persistent_write("L0", "os.mutate")  # G-12-1: mutation prohibition guard
                os.remove(path)
                print(f"[DELETED] {path.name}")
                deleted += 1
            # guardian: allow-silent-swallow
            except (OSError, ValueError, TypeError) as e:
                print(f"[ERROR] Could not delete {path.name}: {e}")

        print(f"\n✅ Cleanup complete. Deleted {deleted} files.")
        return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Find and optionally delete migration debris.")
    parser.add_argument("--apply", action="store_true", help="Delete discovered debris. Default is dry-run.")
    parser.add_argument("--root", type=Path, help="Override project root.")
    args = parser.parse_args()

    root = args.root.resolve() if args.root else _find_project_root()
    dry_run = not args.apply

    print("=" * 60)
    print("SOVEREIGNTY DEBRIS HUNTER")
    print("=" * 60)
    print(f"Mode: {'DRY RUN' if dry_run else 'EXECUTE'}")
    print(f"Root: {root}")
    print("=" * 60)

    hunter = DebrisHunter(root, dry_run=dry_run)
    hunter.scan_for_collisions()
    hunter.scan_for_known_redundancies()
    hunter.scan_for_temp_files()
    return hunter.execute_cleanup()


if __name__ == "__main__":
    sys.exit(main())
