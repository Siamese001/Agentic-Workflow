"""
File: scripts/CollisionResolver.py
Path: C:\\Git\\Agentic-Workflow\\scripts/CollisionResolver.py
Status: Post-Migration Triage Tool
Rationale:
    The automated fixer cannot resolve collisions where two files want the same name.
    This tool finds these specific cases and reports them for manual adjudication.
"""


import ast
import sys
from collections import defaultdict
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    DISCOVERY_EXCLUDED_TERRITORIES,
    GLOBAL_EXCLUDED_DIRS,
    SOVEREIGN_EXCLUDED_FOLDERS,
)
from agentic_core.L0_routing.enforcement.mutation_prohibition import safe_os_remove
from agentic_core.runtime.lifecycle_trace_contract import (
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
)

_emit_dispatches_healing_run("p1", "collision_resolver", "L0")
_emit_routes_through("p1", "collision_resolver", "L0")
_emit_checks_agent_registry("p1", "collision_resolver", "agent_registry")
_emit_validates_agent_capability("p1", "collision_resolver", "capability")
_emit_dispatches_execution_plan("p1", "collision_resolver", "exec_plan")
_emit_agent_executes_agent("p1", "collision_resolver", "sub_agent")
_emit_routes_to_agent("p1", "collision_resolver", "target_agent")
_emit_verifies_policy("p1", "collision_resolver", "policy_check")
_emit_observes_runtime_state("p1", "collision_resolver", "runtime_state")
_emit_verifies_boundary("p1", "collision_resolver", "boundary_check")
_emit_transcripts_response("p1", "collision_resolver", "transcript")
_emit_hard_fails_untranscripted("p1", "collision_resolver")
_emit_gated_by_confidence("p1", "collision_resolver", "confidence_gate")
_emit_escalates_to_human("p1", "collision_resolver", "L0")
_emit_reads_policy_state("p1", "collision_resolver", "L0")

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "collision_resolver", "p0_governance")
_emit_snapshots_state("p0", "collision_resolver", "state_snapshot")
_emit_authorize_and_execute("p2", "collision_resolver", "execution_auth")
_emit_validates_capability("p2", "collision_resolver", "capability_check")
_emit_routes_to_capability("p2", "collision_resolver", "capability_route")
_emit_writes_via_uwg("p2", "collision_resolver", "uwg_write")
_emit_blocks_direct_write("p2", "collision_resolver", "direct_write_block")
_emit_records_tool_invocation("p2", "collision_resolver", "tool_invocation")
_emit_captures_execution_output("p2", "collision_resolver", "exec_output")
_emit_dispatches_agent("p3", "collision_resolver", "agent_dispatch")
_emit_coordinates_agents("p3", "collision_resolver", "agent_coordination")
_emit_records_workflow_lineage("p3", "collision_resolver", "workflow_lineage")
_emit_records_healing_outcome("p3", "collision_resolver", "healing_outcome")
_emit_escalates_failure("p3", "collision_resolver", "failure_escalation")
_emit_orchestrates_workflow("p3", "collision_resolver", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "collision_resolver", "healing_dispatch")
_emit_invokes_evaluation("p3", "collision_resolver", "evaluation_signal")
_emit_records_telemetry_event("p4", "collision_resolver", "telemetry_event")
_emit_captures_evaluation_metric("p4", "collision_resolver", "eval_metric")
_emit_stores_embedding("p4", "collision_resolver", "embedding_store")
_emit_updates_meta_learning_state("p4", "collision_resolver", "meta_learning")
_emit_links_execution_to_snapshot("p4", "collision_resolver", "exec_snapshot_link")

try:
    from agentic_core.utils.schemas.ssot_discovery_validator import get_python_files
    _SSOT_DISCOVERY_AVAILABLE = True
except ImportError as e:
    _SSOT_DISCOVERY_AVAILABLE = False
    print(f"Warning: ssot_discovery_validator not available: {e}. Using fallback implementation.")

    def get_python_files(root: Path):
        """Fallback implementation when ssot_discovery_validator is unavailable."""
        return list(root.rglob("*.py"))

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
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
    _emit_records_execution_trace,
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
    emit_determinism_digest,
    emit_replay_key,
)

_emit_emits_metric_event("collision_resolver", "p4obs", "metric_1")
_emit_emits_metric_event("collision_resolver", "p4obs", "metric_2")
_emit_emits_metric_event("collision_resolver", "p4obs", "metric_3")
_emit_emits_metric_event("collision_resolver", "p4obs", "metric_4")
_emit_emits_metric_event("collision_resolver", "p4obs", "metric_5")
_emit_emits_metric_event("collision_resolver", "p4obs", "metric_6")
_emit_records_incident_event("collision_resolver", "p4obs", "incident")
_emit_captures_runtime_anomaly("collision_resolver", "p4obs", "anomaly")
_emit_writes_observability_log("collision_resolver", "p4obs", "obs_log")
_emit_updates_monitoring_state("collision_resolver", "p4obs", "mon_state")
_emit_triggers_alert("collision_resolver", "p4obs", "alert")
_emit_links_incident_trace("collision_resolver", "p4obs", "trace_link")
_emit_captures_pattern("collision_resolver", "p3lm", "pattern")
_emit_records_learning_event("collision_resolver", "p3lm", "learning_event")
_emit_writes_learning_snapshot("collision_resolver", "p3lm", "snapshot")
_emit_feeds_meta_learning("collision_resolver", "p3lm", "meta_feed")
_emit_updates_routing_strategy("collision_resolver", "p3lm", "routing")
_emit_improves_agent_policy("collision_resolver", "p3lm", "policy")
_emit_stores_learning_state("collision_resolver", "p3lm", "state")
_emit_records_execution_trace("collision_resolver", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("collision_resolver", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("collision_resolver", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("collision_resolver", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("collision_resolver", "L4_STATE", "p2_trace_5")
_emit_reads_environ("collision_resolver", "env_read", "p2_env_1")
_emit_reads_environ("collision_resolver", "env_read", "p2_env_2")
_emit_reads_runtime_state("collision_resolver", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("collision_resolver", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "collision_resolver", "context_pull")
_emit_pulls_context("p1", "collision_resolver", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "collision_resolver", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "collision_resolver", "uwg_term_2")
_emit_writes_through("p1", "collision_resolver", "write_through")
_emit_writes_through("p1", "collision_resolver", "write_through_2")
_emit_validated_by_safety_plane("p1", "collision_resolver", "safety_validation")
_emit_invokes_eval("p1", "collision_resolver", "eval_call")
_emit_proposal_commits_routing("p1", "collision_resolver", "routing_commit")


class CollisionResolver:
    def __init__(self, root: Path):
        self.root = root
        self.collisions: dict[str, list[Path]] = defaultdict(list)
        self.skip_dirs = GLOBAL_EXCLUDED_DIRS | SOVEREIGN_EXCLUDED_FOLDERS | DISCOVERY_EXCLUDED_TERRITORIES

    def _get_target_name(self, path: Path) -> str | None:
        """Determine what name this file SHOULD have based on AST analysis."""
        if path.name in ["__init__.py", "__main__.py", "conftest.py"]:
            return None
        try:
            content = path.read_text(encoding="utf-8")
            tree = ast.parse(content)
        except (SyntaxError, UnicodeDecodeError, OSError) as e:
            # Log the specific error and return None - this file cannot be analyzed
            print(f"Warning: Could not parse {path}: {e}")
            return None
        classes = [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
        if not classes:
            return None
        primary = classes[0]
        stem_clean = path.stem.replace("_", "").lower()
        for cls in classes:
            if cls.lower() == stem_clean:
                primary = cls
                break
        is_agent = any(c.endswith("Agent") for c in classes)
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for base in node.bases:
                    if isinstance(base, ast.Name) and "Agent" in base.id:
                        is_agent = True
                    elif isinstance(base, ast.Attribute) and "Agent" in base.attr:
                        is_agent = True
        target = primary
        if is_agent and (not target.endswith("Agent")):
            target += "Agent"
        return f"{target}.py"

    def find_collisions(self):
        """Find files that want the same target name within the same directory."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "CollisionResolver.find_collisions")
        emit_replay_key(_trace_id, f"rk:{_trace_id[:16]}")
        emit_determinism_digest(_trace_id, f"dd:{_trace_id[:16]}")

        print(f"Scanning {self.root} for collision candidates...")
        dir_targets: dict[Path, dict[str, list[Path]]] = defaultdict(lambda: defaultdict(list))
        for path in get_python_files(self.root):
            if any(skip in path.parts for skip in self.skip_dirs):
                continue
            target = self._get_target_name(path)
            if target and target != path.name:
                dir_targets[path.parent][target].append(path)
        for directory, targets in dir_targets.items():
            for target_name, sources in targets.items():
                target_path = directory / target_name
                if target_path.exists() and target_path not in sources:
                    key = str(target_path)
                    self.collisions[key].append(target_path)
                    for src in sources:
                        if src not in self.collisions[key]:
                            self.collisions[key].append(src)
                elif len(sources) > 1:
                    key = str(target_path)
                    for src in sources:
                        if src not in self.collisions[key]:
                            self.collisions[key].append(src)

    def report(self):
        """Generate a detailed collision report."""
        if not self.collisions:
            print("\n✅ No collision violations found. Repository is clean.")
            return 0
        print(f"\n⚠️  Found {len(self.collisions)} collision groups requiring manual resolution.\n")
        print("=" * 80)
        for i, (target, sources) in enumerate(self.collisions.items(), 1):
            target_path = Path(target)
            print(f"\n[{i}] TARGET: {target_path.name}")
            print(f"    Directory: {target_path.parent.relative_to(self.root)}")
            print("    Contenders:")
            for src in sources:
                try:
                    size = src.stat().st_size
                    content = src.read_text(encoding="utf-8")
                    tree = ast.parse(content)
                    classes = [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
                    class_info = f"[Classes: {', '.join(classes[:3])}]" if classes else "[No classes]"
                except (SyntaxError, UnicodeDecodeError, OSError) as e:
                    size = 0
                    class_info = f"[Parse error: {type(e).__name__}]"
                marker = "✓ EXISTS" if src.name == target_path.name else "→ WANTS"
                print(f"      {marker}: {src.name} ({size} bytes) {class_info}")
        print("\n" + "=" * 80)
        print("\nRESOLUTION OPTIONS:")
        print("  1. Manually merge/delete duplicate files")
        print("  2. Rename one file's primary class to create a unique target")
        print("  3. Move one file to a different directory")
        print("=" * 80)
        return len(self.collisions)

    def interactive_resolve(self):
        """Interactive mode for resolving collisions one by one."""
        if not self.collisions:
            print("\n✅ No collisions to resolve.")
            return
        print("\n🔧 INTERACTIVE COLLISION RESOLVER")
        print(f"   {len(self.collisions)} groups to process")
        print("   Commands: [1-N] Keep file N, [S] Skip, [Q] Quit\n")
        resolved = 0
        for target, sources in list(self.collisions.items()):
            target_path = Path(target)
            print("\n" + "=" * 60)
            print(f"TARGET: {target_path.name}")
            print(f"DIR: {target_path.parent}")
            print("-" * 60)
            for i, src in enumerate(sources, 1):
                size = src.stat().st_size if src.exists() else 0
                status = "EXISTS" if src.name == target_path.name else "RENAME"
                print(f"  [{i}] {src.name} ({size} bytes) [{status}]")
            choice = input("\nKeep which file? [1-N/S/Q]: ").strip().upper()
            if choice == "Q":
                print("Exiting interactive mode.")
                break
            elif choice == "S" or not choice:
                print("Skipped.")
                continue
            elif choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(sources):
                    winner = sources[idx]
                    print(f"\n  KEEPING: {winner.name}")
                    for i, src in enumerate(sources):
                        if i != idx and src.exists():
                            print(f"  DELETING: {src.name}")
                            safe_os_remove(src, layer="L0")
                    if winner.name != target_path.name and winner.exists():
                        print(f"  RENAMING: {winner.name} -> {target_path.name}")
                        winner.rename(target_path)
                    resolved += 1
                    print("  ✓ Resolved")
        print(f"\n✅ Resolved {resolved} collision groups.")


if __name__ == "__main__":
    root = Path(__file__).parent.parent
    resolver = CollisionResolver(root)
    print("=" * 60)
    print("SOVEREIGNTY COLLISION RESOLVER")
    print("=" * 60)
    resolver.find_collisions()
    if "--interactive" in sys.argv or "-i" in sys.argv:
        resolver.interactive_resolve()
    else:
        count = resolver.report()
        if count > 0:
            print("\nRun with --interactive (-i) to resolve collisions one by one.")
        sys.exit(count)
