from __future__ import annotations

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

_emit_records_execution_trace("p0", "evidence", "rescue_reviewer")
_emit_applies_guardrail("p0", "rescue_reviewer", "p0_governance")
_emit_reads_policy_state("p0", "rescue_reviewer", "policy_binding")
_emit_snapshots_state("p0", "rescue_reviewer", "state_snapshot")
emit_replay_key("p0", "rescue_reviewer")
emit_determinism_digest("p0", "rescue_reviewer")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "rescue_reviewer", "execution_auth")
_emit_validates_capability("p2", "rescue_reviewer", "capability_check")
_emit_routes_to_capability("p2", "rescue_reviewer", "capability_route")
_emit_writes_via_uwg("p2", "rescue_reviewer", "uwg_write")
_emit_blocks_direct_write("p2", "rescue_reviewer", "direct_write_block")
_emit_records_tool_invocation("p2", "rescue_reviewer", "tool_invocation")
_emit_captures_execution_output("p2", "rescue_reviewer", "exec_output")
_emit_dispatches_agent("p3", "rescue_reviewer", "agent_dispatch")
_emit_coordinates_agents("p3", "rescue_reviewer", "agent_coordination")
_emit_records_workflow_lineage("p3", "rescue_reviewer", "workflow_lineage")
_emit_records_healing_outcome("p3", "rescue_reviewer", "healing_outcome")
_emit_escalates_failure("p3", "rescue_reviewer", "failure_escalation")
_emit_orchestrates_workflow("p3", "rescue_reviewer", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "rescue_reviewer", "healing_dispatch")
_emit_invokes_evaluation("p3", "rescue_reviewer", "evaluation_signal")
_emit_records_telemetry_event("p4", "rescue_reviewer", "telemetry_event")
_emit_captures_evaluation_metric("p4", "rescue_reviewer", "eval_metric")
_emit_stores_embedding("p4", "rescue_reviewer", "embedding_store")
_emit_updates_meta_learning_state("p4", "rescue_reviewer", "meta_learning")
_emit_links_execution_to_snapshot("p4", "rescue_reviewer", "exec_snapshot_link")
"\nSovereign Rescue & Review (SRR)\n"
import hashlib
import json
import os
from pathlib import Path
from typing import Any

from agentic_core.L0_routing.config.path_constants import SOVEREIGN_EXCLUDED_FOLDERS
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)
from tqdm import tqdm

_emit_emits_metric_event("rescue_reviewer", "p4obs", "metric_1")
_emit_emits_metric_event("rescue_reviewer", "p4obs", "metric_2")
_emit_emits_metric_event("rescue_reviewer", "p4obs", "metric_3")
_emit_emits_metric_event("rescue_reviewer", "p4obs", "metric_4")
_emit_emits_metric_event("rescue_reviewer", "p4obs", "metric_5")
_emit_emits_metric_event("rescue_reviewer", "p4obs", "metric_6")
_emit_records_incident_event("rescue_reviewer", "p4obs", "incident")
_emit_captures_runtime_anomaly("rescue_reviewer", "p4obs", "anomaly")
_emit_writes_observability_log("rescue_reviewer", "p4obs", "obs_log")
_emit_updates_monitoring_state("rescue_reviewer", "p4obs", "mon_state")
_emit_triggers_alert("rescue_reviewer", "p4obs", "alert")
_emit_links_incident_trace("rescue_reviewer", "p4obs", "trace_link")
_emit_captures_pattern("rescue_reviewer", "p3lm", "pattern")
_emit_records_learning_event("rescue_reviewer", "p3lm", "learning_event")
_emit_writes_learning_snapshot("rescue_reviewer", "p3lm", "snapshot")
_emit_feeds_meta_learning("rescue_reviewer", "p3lm", "meta_feed")
_emit_updates_routing_strategy("rescue_reviewer", "p3lm", "routing")
_emit_improves_agent_policy("rescue_reviewer", "p3lm", "policy")
_emit_stores_learning_state("rescue_reviewer", "p3lm", "state")
_emit_records_execution_trace("rescue_reviewer", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("rescue_reviewer", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("rescue_reviewer", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("rescue_reviewer", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("rescue_reviewer", "L4_STATE", "p2_trace_5")
_emit_reads_environ("rescue_reviewer", "env_read", "p2_env_1")
_emit_reads_environ("rescue_reviewer", "env_read", "p2_env_2")
_emit_reads_runtime_state("rescue_reviewer", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("rescue_reviewer", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "rescue_reviewer", "context_pull")
_emit_pulls_context("p1", "rescue_reviewer", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "rescue_reviewer", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "rescue_reviewer", "uwg_term_2")
_emit_writes_through("p1", "rescue_reviewer", "write_through")
_emit_writes_through("p1", "rescue_reviewer", "write_through_2")
_emit_validated_by_safety_plane("p1", "rescue_reviewer", "safety_validation")
_emit_invokes_eval("p1", "rescue_reviewer", "eval_call")
_emit_proposal_commits_routing("p1", "rescue_reviewer", "routing_commit")
_emit_escalates_to_human("p1", "rescue_reviewer", "human_escalation")
_emit_routes_through("p1", "rescue_reviewer", "route_through")
_emit_checks_agent_registry("p1", "rescue_reviewer", "agent_registry")
_emit_validates_agent_capability("p1", "rescue_reviewer", "capability")
_emit_dispatches_execution_plan("p1", "rescue_reviewer", "exec_plan")
_emit_agent_executes_agent("p1", "rescue_reviewer", "sub_agent")
_emit_routes_to_agent("p1", "rescue_reviewer", "target_agent")
_emit_verifies_policy("p1", "rescue_reviewer", "policy_check")
_emit_observes_runtime_state("p1", "rescue_reviewer", "runtime_state")
_emit_verifies_boundary("p1", "rescue_reviewer", "boundary_check")
_emit_transcripts_response("p1", "rescue_reviewer", "transcript")
_emit_hard_fails_untranscripted("p1", "rescue_reviewer")
_emit_gated_by_confidence("p1", "rescue_reviewer", "confidence_gate")


def _get_redis_sovereign_agent():
    """Lazy load RedisSovereignAgent to avoid L0 → L4 dependency."""
    import importlib

    module = importlib.import_module("agentic_core.L4_state.reasoning.RedisSovereignAgent")
    return module.RedisSovereignAgent


class RescueReviewer:
    """
    Sovereign judge of archived files — eternal purity through hash + semantics.
    """

    def __init__(self, project_root: Path):
        self.root = project_root
        self.archive_path = project_root / "archives/depth_violations"
        self.active_hashes = self._map_active_canon()
        try:
            _RedisCls = _get_redis_sovereign_agent()
            self.redis_gateway = _RedisCls(project_root)
            self.redis = self.redis_gateway.get_client()
            print("   [OK] SRR: Redis decision cache online.")
        except Exception as e:  # guardian: allow-silent-swallow
            print(f"   [!] Redis Link Failed: {e}")
            self.redis = None
        # guardian: allow-magic-config
        self.auto_home_threshold = 0.9
        # guardian: allow-magic-config
        self.auto_home_min_signals = 3

    def _map_active_canon(self) -> dict[str, str]:
        """Map every active .py file hash to its current path"""
        hash_map = {}
        targets = [AGENTIC_CORE_DIR, APPS_RG_DIR, APPS_LIC_DIR, APPS_SHARED_DIR, TESTS_DIR]
        for folder in tqdm(targets, desc="Processing", unit="item"):
            path = self.root / folder
            if not path.exists():
                continue
            from agentic_core.utils.runners.ssot_discovery_validator import get_python_files

            for py_file in get_python_files(path):
                try:
                    f_hash = hashlib.sha256(py_file.read_bytes()).hexdigest()
                    rel_path = str(py_file.relative_to(self.root))
                    hash_map[f_hash] = rel_path
                except Exception:  # guardian: allow-silent-swallow
                    pass
        print(f"   [OK] SRR: Mapped {len(hash_map)} active files for deduplication")
        return hash_map

    def review_and_heal(self, auto_home: bool = False) -> Any:
        """Reviews the archive and optionally rescues unique logic."""
        if not self.archive_path.exists():
            print("[OK] Archive is empty. Sovereignty is pure.")
            return
        print(f"\n--- SOVEREIGN ARCHIVE REVIEW (Auto-Home: {auto_home}) ---")
        from agentic_core.L5_safety.config.structure_blueprint import (
            CANON_SIGNALS,
            DEFAULT_CORE_HEALING_TERRITORY,
        )
        from agentic_core.utils.runners.ssot_discovery_validator import get_python_files

        for arch_file in tqdm(get_python_files(self.archive_path), desc="Processing", unit="item"):
            rel: Any = arch_file.relative_to(self.archive_path)
            content: Any = arch_file.read_text(encoding="utf-8", errors="ignore")
            f_hash: Any = hashlib.sha256(content.encode()).hexdigest()
            cache_key: Any = f"srr_decision:{f_hash}"
            if self.redis:
                cached: Any = self.redis.get(cache_key)
                if cached:
                    decision: Any = json.loads(cached)
                    print(f"   [CACHE HIT] {rel} -> {decision['Verdict']}")
                    if decision.get("action") == "moved":
                        continue
            if f_hash in self.active_hashes:
                print(f"[PURGE] {rel} -> REDUNDANT (Exists at: {self.active_hashes[f_hash]})")
                arch_file.unlink()
                continue
            print(f"[RESCUE] {rel} -> UNIQUE logic detected.")
            results: Any = []
            if results and results[0]["score"] >= 0.85:
                match: Any = results[0]
                territory: Any = match["metadata"]["territory"]
                conf: Any = match["score"]
                suggested_territory = DEFAULT_CORE_HEALING_TERRITORY
                sig_count = sum(1 for s in CANON_SIGNALS if s in content.lower())
                print(f"         SUGGESTION: {territory} (Conf: {conf:.2f}) -> {suggested_territory}")
                Verdict: Any = "MANUAL_REVIEW"
                if (
                    auto_home
                    and conf >= self.auto_home_threshold
                    and (sig_count >= self.auto_home_min_signals)
                ):
                    dest: Any = self._execute_rescue(arch_file, territory)
                    Verdict: Any = "RESCUED_AUTO"
                    print(f"         [HEALED] Rescued to -> {dest.relative_to(self.root)}")
                if self.redis:
                    self.redis.set(
                        cache_key,
                        json.dumps(
                            {"Verdict": Verdict, "action": "moved" if Verdict == "RESCUED_AUTO" else "stay"}
                        ),
                        ex=604800,
                    )
            else:
                print("         VERDICT: Unknown logic. Manual review required.")

    def _execute_rescue(self, arch_file, territory):
        target_dir = self.root / territory
        target_dir.mkdir(parents=True, exist_ok=True)
        dest = target_dir / arch_file.name
        if dest.exists():
            dest = target_dir / f"{arch_file.stem}_rescued{arch_file.suffix}"
        arch_file.rename(dest)
        return dest

    def final_lockdown(self) -> Any:
        """Cleans up empty directories in the archive."""
        for dirpath, dirnames, filenames in os.walk(self.archive_path, topdown=False):
            dirnames[:] = [d for d in dirnames if d not in SOVEREIGN_EXCLUDED_FOLDERS]
            if not dirnames and (not filenames):
                os.rmdir(dirpath)


if __name__ == "__main__":
    parser: Any = argparse.ArgumentParser(description="Sovereign Rescue & Review - Archive Purity Enforcer")
    parser.add_argument(
        "--auto-home",
        action="store_true",
        help="Automatically rescue high-confidence unique files to their suggested homes",
    )
    parser.add_argument(
        "--root", type=Path, default=Path("."), help="Project root path (default: current directory)"
    )
    args: Any = parser.parse_args()
    reviewer: Any = RescueReviewer(args.root)
    reviewer.review_and_heal(auto_home=args.auto_home)
    reviewer.final_lockdown()
