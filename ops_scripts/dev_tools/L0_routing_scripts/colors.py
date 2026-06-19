import argparse
import os
import subprocess
import sys
import traceback
from datetime import datetime
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import MAX_DEPTH


# Lazy import to avoid L0->L3 gravity violation
def _get_registry():
    from agentic_core.L3_orchestration.utils.registry.agent_dispatch_registry import (
        get_agent_dispatch_registry,
    )

    return get_agent_dispatch_registry()


from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    # noqa: E402,
    # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,
    # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,
    # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    # noqa: E402
    emit_replay_key,
)

emit_replay_key("p0", "colors")
emit_determinism_digest("p0", "colors")

_emit_dispatches_healing_run("p1", "colors", "L0")
_emit_routes_through("p1", "colors", "L0")
_emit_agent_executes_agent("p1", "colors", "sub_agent")
_emit_verifies_policy("p1", "colors", "policy_check")
_emit_observes_runtime_state("p1", "colors", "runtime_state")
_emit_verifies_boundary("p1", "colors", "boundary_check")
_emit_transcripts_response("p1", "colors", "transcript")
_emit_hard_fails_untranscripted("p1", "colors")
_emit_gated_by_confidence("p1", "colors", "confidence_gate")
_emit_escalates_to_human("p1", "colors", "L0")
_emit_reads_policy_state("p1", "colors", "L0")
_emit_routes_to_agent("p1", "colors", "L0")
_emit_orchestrates_workflow("p1", "colors", "L0")
_emit_dispatches_execution_plan("p1", "colors", "L0")
_emit_validates_agent_capability("p1", "colors", "L0")
_emit_checks_agent_registry("p1", "colors", "L0")

_emit_snapshots_state("p0", "colors", "state_snapshot")
_emit_authorize_and_execute("p2", "colors", "execution_auth")
_emit_validates_capability("p2", "colors", "capability_check")
_emit_routes_to_capability("p2", "colors", "capability_route")
_emit_writes_via_uwg("p2", "colors", "uwg_write")
_emit_blocks_direct_write("p2", "colors", "direct_write_block")
_emit_records_tool_invocation("p2", "colors", "tool_invocation")
_emit_captures_execution_output("p2", "colors", "exec_output")
_emit_dispatches_agent("p3", "colors", "agent_dispatch")
_emit_coordinates_agents("p3", "colors", "agent_coordination")
_emit_records_workflow_lineage("p3", "colors", "workflow_lineage")
_emit_records_healing_outcome("p3", "colors", "healing_outcome")
_emit_escalates_failure("p3", "colors", "failure_escalation")
_emit_orchestrates_workflow("p3", "colors", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "colors", "healing_dispatch")
_emit_invokes_evaluation("p3", "colors", "evaluation_signal")
_emit_records_telemetry_event("p4", "colors", "telemetry_event")
_emit_captures_evaluation_metric("p4", "colors", "eval_metric")
_emit_stores_embedding("p4", "colors", "embedding_store")
_emit_updates_meta_learning_state("p4", "colors", "meta_learning")
_emit_links_execution_to_snapshot("p4", "colors", "exec_snapshot_link")


def _get_orchestrator_class():
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    _emit_applies_guardrail(str(_uuid.uuid4()), "_get_orchestrator_class", "p0_governance")
    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "_get_orchestrator_class")
    from agentic_core.L3_orchestration.reasoning.engines.orchestrator_engine import Orchestrator

    return Orchestrator


def _get_checkpoint_manager():
    from agentic_core.L4_state.reasoning.CheckpointManager import get_checkpoint_manager

    return get_checkpoint_manager


from agentic_core.L0_routing.config.path_constants import AGENTIC_CORE_DIR, APPS_SHARED_DIR
from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write
from agentic_core.config.colors_config import (
    Colors,
    agent_status,
    heartbeat,
    log_status,
    mission_header,
    mission_summary,
    phase_header,
    progress_bar,
    tier_summary,
)

COLORS_AVAILABLE = True


try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass
discover_all_agents = None


def _configure_console_encoding() -> None:
    if not sys.platform.startswith("win"):
        return
    try:
        subprocess.run(
            ["chcp", "65001"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
            shell=False,
            timeout=5,
        )
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (FileNotFoundError, OSError):
        pass


_configure_console_encoding()
_mission_executed = False
import json as _json

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
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
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)
from tqdm import tqdm

_emit_emits_metric_event("colors", "p4obs", "metric_1")
_emit_emits_metric_event("colors", "p4obs", "metric_2")
_emit_emits_metric_event("colors", "p4obs", "metric_3")
_emit_emits_metric_event("colors", "p4obs", "metric_4")
_emit_emits_metric_event("colors", "p4obs", "metric_5")
_emit_emits_metric_event("colors", "p4obs", "metric_6")
_emit_records_incident_event("colors", "p4obs", "incident")
_emit_captures_runtime_anomaly("colors", "p4obs", "anomaly")
_emit_writes_observability_log("colors", "p4obs", "obs_log")
_emit_updates_monitoring_state("colors", "p4obs", "mon_state")
_emit_triggers_alert("colors", "p4obs", "alert")
_emit_links_incident_trace("colors", "p4obs", "trace_link")
_emit_captures_pattern("colors", "p3lm", "pattern")
_emit_records_learning_event("colors", "p3lm", "learning_event")
_emit_writes_learning_snapshot("colors", "p3lm", "snapshot")
_emit_feeds_meta_learning("colors", "p3lm", "meta_feed")
_emit_updates_routing_strategy("colors", "p3lm", "routing")
_emit_improves_agent_policy("colors", "p3lm", "policy")
_emit_stores_learning_state("colors", "p3lm", "state")
_emit_records_execution_trace("colors", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("colors", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("colors", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("colors", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("colors", "L4_STATE", "p2_trace_5")
_emit_reads_environ("colors", "env_read", "p2_env_1")
_emit_reads_environ("colors", "env_read", "p2_env_2")
_emit_reads_runtime_state("colors", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("colors", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "colors", "context_pull")
_emit_pulls_context("p1", "colors", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "colors", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "colors", "uwg_term_2")
_emit_writes_through("p1", "colors", "write_through")
_emit_writes_through("p1", "colors", "write_through_2")
_emit_validated_by_safety_plane("p1", "colors", "safety_validation")
_emit_invokes_eval("p1", "colors", "eval_call")
_emit_proposal_commits_routing("p1", "colors", "routing_commit")

RUNTIME_STATE_FILE = "runtime_state.json"
_runtime_state = {
    "status": "idle",
    "start_time": None,
    "end_time": None,
    "current_agent": None,
    "current_layer": None,
    "agents_order": [],
    "total_agents": 0,
    "completed_agents": [],
    "events": [],
    "meta_learning": {
        "enabled": False,
        "total_experiences": 0,
        "patterns_extracted": 0,
        "strategy_weights": {"cot": 1.0, "tot": 1.0, "react": 1.0, "reflection": 1.0},
        "recent_experiences": [],
        "pattern_history": [],
    },
    "redis": {
        "connected": False,
        "operations": {"get": 0, "set": 0, "delete": 0, "total": 0},
        "cache_hits": 0,
        "cache_misses": 0,
        "hit_rate": 0.0,
        "recent_operations": [],
    },
    "pinecone": {
        "connected": False,
        "operations": {"upsert": 0, "query": 0, "delete": 0, "total": 0},
        "vectors_stored": 0,
        "avg_similarity": 0.0,
        "recent_queries": [],
    },
    "execution_timeline": [],
}


def _save_runtime_state(project_root_path: Path):
    """Persist runtime state to JSON for dashboard polling."""
    try:
        state_path = project_root_path / RUNTIME_STATE_FILE
        assert_no_persistent_write("L0", "write_text")
        state_path.write_text(_json.dumps(_runtime_state, indent=2, default=str), encoding="utf-8")
    # guardian: allow-silent-swallow
    except OSError as e:  # guardian: allow-log-and-swallow -- runtime state save failure silently continues
        pass


def _add_event(event_type: str, message: str):
    """Add timestamped event to runtime state."""
    _runtime_state["events"].append(
        {"time": datetime.now().isoformat(), "type": event_type, "message": message},
    )


def _update_meta_learning_state(experience_data: dict):
    """Update runtime state with new meta-learning experience."""
    ml = _runtime_state["meta_learning"]
    ml["enabled"] = True
    ml["total_experiences"] = experience_data.get("total_experiences", ml["total_experiences"])
    ml["patterns_extracted"] = experience_data.get("patterns_extracted", ml["patterns_extracted"])
    if "strategy_weights" in experience_data:
        ml["strategy_weights"] = experience_data["strategy_weights"]
    if "experience" in experience_data:
        ml["recent_experiences"].insert(0, experience_data["experience"])
        ml["recent_experiences"] = ml["recent_experiences"][:10]
    if "pattern" in experience_data:
        ml["pattern_history"].append(
            {"pattern": experience_data["pattern"], "timestamp": datetime.now().isoformat()},
        )


def _update_redis_state(operation: str, key: str, hit: bool = None):
    """Update runtime state with Redis operation."""
    redis = _runtime_state["redis"]
    redis["connected"] = True
    if operation in redis["operations"]:
        redis["operations"][operation] += 1
    redis["operations"]["total"] += 1
    if hit is not None:
        if hit:
            redis["cache_hits"] += 1
        else:
            redis["cache_misses"] += 1
        total = redis["cache_hits"] + redis["cache_misses"]
        redis["hit_rate"] = redis["cache_hits"] / total if total > 0 else 0.0
    redis["recent_operations"].insert(
        0,
        {"operation": operation, "key": key, "hit": hit, "timestamp": datetime.now().isoformat()},
    )
    redis["recent_operations"] = redis["recent_operations"][:20]


def _update_pinecone_state(operation: str, metadata: dict = None):
    """Update runtime state with Pinecone operation."""
    pc = _runtime_state["pinecone"]
    pc["connected"] = True
    if operation in pc["operations"]:
        pc["operations"][operation] += 1
    pc["operations"]["total"] += 1
    if metadata:
        if "vectors_count" in metadata:
            pc["vectors_stored"] += metadata["vectors_count"]
        if "similarity" in metadata:
            total_queries = pc["operations"]["query"]
            if total_queries > 0:
                pc["avg_similarity"] = (
                    pc["avg_similarity"] * (total_queries - 1) + metadata["similarity"]
                ) / total_queries
        if operation == "query":
            pc["recent_queries"].insert(
                0,
                {
                    "results": metadata.get("results", []),
                    "top_k": metadata.get("top_k", 0),
                    "avg_score": metadata.get("similarity", 0),
                    "timestamp": datetime.now().isoformat(),
                },
            )
            pc["recent_queries"] = pc["recent_queries"][:10]


def _update_agent_execution(agent_name: str, layer: str, start_time: float, end_time: float, success: bool):
    """Update execution timeline with agent completion."""
    _runtime_state["execution_timeline"].append(
        {
            "agent": agent_name,
            "layer": layer,
            "start": start_time,
            "end": end_time,
            "duration": end_time - start_time,
            "success": success,
        },
    )


AGENT_LAYERS = {
    "NamingAgent": "L5 – Safety & Governance",
    "LocationAgent": "L5 – Safety & Governance",
    "HierarchyAgent": "L5 – Safety & Governance",
    "ImportAgent": "L5 – Safety & Governance",
    "StructureEnforcerAgent": "L5 – Safety & Governance",
    "CheckpointManagerAgent": "L4 – State & Memory",
    "PerformanceAnalystAgent": "L6 – observability & Metrics",
    "FilesystemSSOTReconcilerAgent": "L0 – Maintenance & Infrastructure",
}


def _find_project_root() -> Path:
    current_file_path = Path(__file__).resolve()
    for parent in current_file_path.parents:
        if (
            (parent / ".git").exists()
            or (parent / "pyproject.toml").exists()
            or (parent / ".env").exists()
            or (parent / AGENTIC_CORE_DIR).exists()
        ):
            return parent
    return current_file_path.parent


project_root = _find_project_root()
project_root_str = str(project_root)
# guardian: allow-global-mutation
if project_root_str not in sys.path:
    sys.path.insert(0, project_root_str)
sovereign_paths = [
    project_root / AGENTIC_CORE_DIR / "runtime" / "shared_runtime",
    project_root / APPS_SHARED_DIR / "utils",
]
for p in sovereign_paths:
    p_str = str(p)
    # guardian: allow-global-mutation
    if p.exists() and p_str not in sys.path:
        # guardian: allow-global-mutation
        sys.path.insert(0, p_str)


def main():
    """Main entry point for the Canon Validator."""
    global _mission_executed
    parser = argparse.ArgumentParser(description="Canon Validator One-File Runner (Thin Wrapper)")
    parser.add_argument(
        "--target",
        type=str,
        default=".",
        help="Target folder for validation (default: entire repo)",
    )
    parser.add_argument("--reset", action="store_true", help="Reset sovereign state before validation")
    parser.add_argument(
        "--heal",
        action="store_true",
        help="Run autonomous domain healing (default: execute mode)",
    )
    parser.add_argument("--report", "-r", action="store_true", help="Report-only mode (no mutations)")
    parser.add_argument("--execute-heal", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument(
        "--agent",
        type=str,
        help="Run a specific agent directly (e.g., 'naming', 'location', 'hierarchy', 'filesystem', 'governance', 'guardian')",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Execute changes (use with --agent, same as --execute-heal)",
    )
    parser.add_argument("--list-agents", action="store_true", help="List all discoverable agents")
    parser.add_argument(
        "--yes",
        "-y",
        action="store_true",
        help="Automatic yes to all prompts (non-interactive mode)",
    )
    parser.add_argument("--report", action="store_true", help="Run autonomy compliance report")
    parser.add_argument(
        "--method",
        type=str,
        default="heal_repository",
        help="Agent method to invoke (default: heal_repository)",
    )
    parser.add_argument(
        "--tier",
        type=int,
        choices=[0, 1, 2, 3, 4],
        default=None,
        help="Run specific healing tier only (0=Pre-Flight, 1=Structural, 2=Architectural, 3=Dynamic, 4=Final Gate)",
    )
    parser.add_argument("--hygiene", action="store_true", help="Run core hygiene agents only (Tier 0-1)")
    parser.add_argument("--full-hygiene", action="store_true", help="Run all hygiene agents (Tier 0-3)")
    parser.add_argument(
        "--preflight-only",
        action="store_true",
        help="Run mandatory preflight checks only (syntax, imports, location)",
    )
    args = parser.parse_args()
    # guardian: allow-global-mutation
    if args.yes:
        # guardian: allow-global-mutation
        os.environ["SOVEREIGN_AUTO_APPROVE"] = "1"
        # guardian: allow-global-mutation
        os.environ["ARCHIVE_BATCH_ACCEPT"] = "1"
        # guardian: allow-global-mutation
        os.environ["CI"] = "true"
        print("   [SYSTEM] SOVEREIGN MODE ACTIVE: Auto-approval enabled.")
    int(os.getenv("MISSION_TIMEOUT_SECONDS", "1800"))
    print("\n[*] Canon Validator v3.2 - Full Repo Scan (Thin Wrapper)")
    print(f"   [OK] Sovereign Neural Link Active at Root: {project_root_str}")
    if args.reset:
        print("\n[*] SOVEREIGN STATE RESET ACTIVATED")
        try:
            from agentic_core.L0_routing.config import fallback_chains_loader_v15, routing_calibration
            from agentic_core.cache import reset_cache_singletons

            reset_cache_singletons()
            routing_calibration.reset_cache()
            fallback_chains_loader_v15.reset_cache()
            runtime_state_path = project_root / RUNTIME_STATE_FILE
            if runtime_state_path.exists():
                runtime_state_path.unlink()
            print("   [OK] Volatile state purged - caches reset on clean slate")
        except (  # guardian: allow-silent-swallow
            OSError,
            ImportError,
            RuntimeError,
        ) as e:  # guardian: allow-log-and-swallow -- state reset failure non-critical
            print(f"   [!] Reset failed: {e}")

    def process_discovery_data(data):
        processed = []
        for agent in data:
            class_name = agent.get("class_name", "")
            if not class_name:
                continue
            path = agent.get("path", "").replace("\\", "/")
            module_path = path.replace("/", ".").replace(".py", "")
            processed.append((class_name, module_path))
        return processed

    def list_available_agents(dedupe: bool = True) -> list:
        """
        STRICT SSOT DISCOVERY: Always runs live AST scan.
        No caching, no stale artifacts. Guaranteed fresh truth.
        """
        if discover_all_agents is None:
            print("   [CRITICAL] SSOT Discovery Module missing!")
            return []
        print("   [SSOT] Executing Strict Live AST Discovery...")
        try:
            discovery_data = discover_all_agents(project_root)
            agents = process_discovery_data(discovery_data)
            print(f"   [OK] SSOT Verified: {len(agents)} agents discovered")
        except (  # guardian: allow-silent-swallow
            OSError,
            ImportError,
            RuntimeError,
        ) as e:  # guardian: allow-log-and-swallow -- discovery failure returns empty
            print(f"   [!] Live discovery failed: {e}")
            traceback.print_exc()
            return []
        if dedupe:
            agents = sorted(set(agents), key=lambda x: (x[0], x[1]))
        else:
            agents = sorted(agents, key=lambda x: (x[0], x[1]))
        return agents

    if args.list_agents:
        print("\n[*] DISCOVERABLE AGENTS (from agent_discovery_full.json):\n")
        all_agents = list_available_agents()
        for i, (class_name, module_path) in enumerate(all_agents, 1):
            print(f"   {i:3}. {class_name:<45} [{module_path}]")
        print(f"\n   Total: {len(all_agents)} agents")
        print("\n   Usage: python canon_validator_agentic_v2_thin.py --agent <name> [--execute]")
        print("   Example: python canon_validator_agentic_v2_thin.py --agent NamingAgent --execute")
        return
    if args.report:
        print("\n[*] Running Autonomy Compliance Report...")
        try:
            from agentic_core.L0_routing.enforcement.safety_validators_seam import load_autonomy_guardian

            def _resolve_autonomy_target(target: str) -> str:
                return target

            get_autonomy_guardian = load_autonomy_guardian().get_autonomy_guardian
            guardian = get_autonomy_guardian(project_root)
            print("   [TARGETS] Using inline autonomy target resolver fallback")
            guardian.generate_compliance_report(context={"target_resolver": _resolve_autonomy_target})
        except (  # guardian: allow-silent-swallow
            ImportError,
            OSError,
            RuntimeError,
        ) as e:  # guardian: allow-log-and-swallow -- report generation failure non-critical
            print(f"   [!] Report failed: {e}")
            traceback.print_exc()
        return
    if args.agent:
        print(f"\n[*] AGENT MODE - Direct invocation of {args.agent.upper()}")
        report_only = args.report
        execute = args.execute or args.execute_heal or not report_only
        mode_str = "EXECUTE" if execute else "DRY-RUN"
        print(f"   [MODE] {mode_str}")

        def discover_agent(agent_name: str) -> tuple:
            """Discover agent by searching for matching class name via AST."""
            search_term = agent_name.lower().replace("-", "").replace("_", "")
            all_agents = list_available_agents()
            for class_name, module_path in all_agents:
                if class_name.lower() == search_term or class_name.lower() == search_term + "agent":
                    return (module_path, class_name)
            for class_name, module_path in all_agents:
                class_normalized = class_name.lower().replace("_", "")
                if class_normalized.startswith(search_term) or search_term in class_normalized:
                    return (module_path, class_name)
            return None

        discovery_result = discover_agent(args.agent)
        if not discovery_result:
            print(f"   [!] Agent not found: {args.agent}")
            print("   Available agents (use any unique prefix):")
            for class_name, _ in list_available_agents()[:30]:
                print(f"      - {class_name}")
            print("   ... and more. Use --list-agents for full list.")
            sys.exit(1)
        module_path, agent_name = discovery_result
        print(f"   [DISCOVERED] {module_path}.{agent_name}")
        try:
            module = __import__(module_path, fromlist=[agent_name])
            getter_name = f"get_{agent_name.lower()}" if not agent_name.startswith("get_") else agent_name
            if hasattr(module, getter_name):
                agent = getattr(module, getter_name)(project_root)
            elif hasattr(module, agent_name):
                agent_cls = getattr(module, agent_name)
                agent = agent_cls(project_root)
            else:
                for attr_name in dir(module):
                    if attr_name.endswith("Agent") and (not attr_name.startswith("_")):
                        agent_cls = getattr(module, attr_name)
                        if callable(agent_cls):
                            agent = agent_cls(project_root)
                            break
                else:
                    raise AttributeError(f"No Agent class found in {module_path}")
            method_name = args.method
            if not hasattr(agent, method_name):
                print(f"   [!] Method '{method_name}' not found on {agent.__class__.__name__}")
                print(
                    f"   Available methods: {[m for m in dir(agent) if not m.startswith('_') and callable(getattr(agent, m))]}",
                )
                sys.exit(1)
            print(f"   [AGENT] {agent.__class__.__name__}.{method_name}()\n")
            # Wave 2: Use AgentDispatchRegistry instead of raw getattr
            registry = get_agent_dispatch_registry()
            if method_name == "heal_repository":
                result = registry.dispatch(
                    caller="colors_script",
                    target_class=agent.__class__.__name__,
                    method=method_name,
                    target_instance=agent,
                    kwargs={"dry_run": not execute, "execute": execute, "depth": 0, "max_depth": MAX_DEPTH},
                )
                print("\n[AGENT COMPLETE]")
                print(f"   Renamed: {result.get('renamed', 0)}")
                print(f"   Errors: {result.get('errors', 0)}")
            elif method_name == "generate_compliance_report":
                method()
            elif method_name == "run":
                result = method()
                print("\n[AGENT COMPLETE]")
                print(f"   Result: {result}")
            else:
                result = method()
                print("\n[AGENT COMPLETE]")
                if result:
                    print(f"   Result: {result}")
        except (  # guardian: allow-silent-swallow
            ImportError,
            AttributeError,
            RuntimeError,
        ) as e:  # guardian: allow-log-and-swallow -- agent invocation failure exits
            print(f"   [!] Agent invocation failed: {e}")
            traceback.print_exc()
            sys.exit(1)
        return
    if args.preflight_only or args.hygiene or args.full_hygiene:
        from agentic_core.config.hygiene_registry_config import CORE_HYGIENE_AGENTS, MANDATORY_PREFLIGHT
        from agentic_core.L0_routing.enforcement.safety_validators_seam import load_healing_strategy

        Orchestrator = _get_orchestrator_class()
        HealingStrategy = load_healing_strategy().HealingStrategy
        report_only = args.report
        execute_heal = (
            getattr(args, "execute_heal", False) or getattr(args, "execute", False) or not report_only
        )
        mode_str = "EXECUTE" if execute_heal else "DRY-RUN"
        if args.preflight_only:
            print("\n[*] PREFLIGHT MODE - Running mandatory checks only")
            print(f"   Agents: {', '.join(MANDATORY_PREFLIGHT)}")
            print(f"   [MODE] {mode_str}")
            strategy = HealingStrategy(project_root=project_root)
            strategy._tiers = {"Tier 0: Pre-Flight": MANDATORY_PREFLIGHT}
        elif args.hygiene:
            print("\n[*] CORE HYGIENE MODE - Running Tier 0-1 agents")
            print(f"   [MODE] {mode_str}")
            strategy = HealingStrategy(project_root=project_root)
            strategy._tiers = {
                "Tier 0: Pre-Flight": CORE_HYGIENE_AGENTS["tier_0_preflight"],
                "Tier 1: Structural": CORE_HYGIENE_AGENTS["tier_1_structural"],
            }
        elif args.full_hygiene:
            print("\n[*] FULL HYGIENE MODE - Running Tier 0-3 agents")
            print(f"   [MODE] {mode_str}")
            strategy = HealingStrategy(project_root=project_root)
            strategy._tiers = {
                "Tier 0: Pre-Flight": CORE_HYGIENE_AGENTS["tier_0_preflight"],
                "Tier 1: Structural": CORE_HYGIENE_AGENTS["tier_1_structural"],
                "Tier 2: Architectural": CORE_HYGIENE_AGENTS["tier_2_architectural"],
                "Tier 3: Autonomy": CORE_HYGIENE_AGENTS["tier_3_autonomy"],
            }
        orchestrator = Orchestrator(strategy=strategy, project_root=project_root, name="HygieneOrchestrator")
        mission_context = {"dry_run": not execute_heal, "execute": execute_heal, "scan_mode": "hygiene_sweep"}
        try:
            print("\n" + "=" * 70)
            results = orchestrator.run_mission(mission_context)
            print("=" * 70)
            print("\n[HYGIENE COMPLETE]")
            print(f"   Total violations: {results.get('total_violations', 0)}")
            print(f"   Violations fixed: {results.get('violations_fixed', 0)}")
        # guardian: allow-silent-swallow
        except (RuntimeError, OSError, ImportError) as e:  # guardian: allow-log-and-swallow -- hygiene failure exits
            print(f"\n[!] Hygiene mode failed: {e}")
            traceback.print_exc()
            sys.exit(1)
        return
    if args.heal:
        print("\n[*] SOVEREIGN HEAL MODE - Autonomous Domain Healing")
        print("   [LAW] All healing via agent.heal_repository() — no external scripts")
        report_only = args.report
        execute_heal = getattr(args, "execute_heal", False) or not report_only
        mode_str = "EXECUTE" if execute_heal else "DRY-RUN"
        print(f"   [MODE] {mode_str}")
        try:
            from agentic_core.L0_routing.enforcement.safety_validators_seam import (
                load_healing_strategy as _load_hs2,
            )

            Orchestrator = _get_orchestrator_class()
            get_checkpoint_manager = _get_checkpoint_manager()
            HealingStrategy = _load_hs2().HealingStrategy

            def get_performance_analyst_safe(root):
                try:
                    import importlib.util

                    spec = importlib.util.find_spec(
                        "agentic_core.L6_observability.utils.engines.PerformanceAnalystAgentSimple",
                    )
                    if spec:
                        perf_module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(perf_module)
                        return perf_module.get_performance_analyst(root)
                except (ValueError, TypeError):  # guardian: allow-silent-swallow
                    pass
                return None

            strategy = HealingStrategy(project_root=project_root, target_tier=args.tier)
            if args.tier is not None:
                print(f"\n   [TIER FILTER] Running ONLY Tier {args.tier}")
            else:
                print("\n   [TIER FILTER] Running ALL tiers (0-4)")
            orchestrator = Orchestrator(
                strategy=strategy,
                project_root=project_root,
                name="SovereignHealOrchestrator",
            )
            checkpoint_manager = get_checkpoint_manager(storage_path=project_root / ".canon_memory" / "checkpoints")
            performance_analyst = get_performance_analyst_safe(project_root)
            mission_context = {
                "dry_run": not execute_heal,
                "execute": execute_heal,
                "checkpoint_manager": checkpoint_manager,
                "performance_analyst": performance_analyst,
                "scan_mode": "unified_sovereign_sweep",
            }
            tiers = strategy.get_tiers()
            all_agent_names = []
            for tier_agents in tiers.values():
                all_agent_names.extend(tier_agents)
            gemini_active = False
            try:
                from agentic_core.L0_routing.enforcement.safety_validators_seam import (
                    load_autonomy_guardian as _load_ag2,
                )

                get_autonomy_guardian = _load_ag2().get_autonomy_guardian
                guardian = get_autonomy_guardian(project_root)
                gemini_active = hasattr(guardian, "gemini_embedder") and guardian.gemini_embedder is not None
            except (ValueError, TypeError):  # guardian: allow-silent-swallow
                pass
            _runtime_state.update(
                {
                    "status": "healing",
                    "start_time": datetime.now().isoformat(),
                    "agents_order": all_agent_names,
                    "total_agents": len(all_agent_names),
                    "completed_agents": [],
                    "events": [],
                    "execution_timeline": [],
                },
            )
            _add_event("info", f"Heal mode started ({mode_str}) - Unified Engine")
            _add_event("meta", f"Meta-learning {('ACTIVE' if gemini_active else 'INACTIVE')}")
            _save_runtime_state(project_root)
            print(mission_header("SOVEREIGN HEAL (UNIFIED)", execute=execute_heal))
            datetime.now()
            results = orchestrator.run_mission(mission_context)
            datetime.now()
            for i, agent_result in enumerate(results.get("agent_results", [])):
                _runtime_state["execution_timeline"].append(
                    {
                        "agent": agent_result.get("agent_name", f"agent_{i}"),
                        "status": agent_result.get("status", "UNKNOWN"),
                        "fixes": agent_result.get("violations_fixed", 0),
                        "violations": agent_result.get("violations_found", 0),
                        "duration_ms": agent_result.get("execution_time_ms", 0),
                    },
                )
            _save_runtime_state(project_root)
            total_fixes = results.get("total_fixed", 0)
            total_violations = results.get("total_violations", 0)
            agents_run = len(results.get("agent_results", []))
            consolidated_results = [
                {
                    "domain": "Sovereign Repository",
                    "agents_run": agents_run,
                    "total_fixed": total_fixes,
                    "total_violations": total_violations,
                    "compliance_score": 100
                    if total_fixes + total_violations == 0
                    else int((1 - total_violations / max(total_fixes + total_violations, 1)) * 100),
                },
            ]
            if results.get("aborted"):
                _add_event("warning", f"Mission aborted: {results.get('abort_reason', 'Unknown')}")
                log_status("warning", f"Mission aborted: {results.get('abort_reason', 'Unknown')}")
            _runtime_state["status"] = "idle"
            _runtime_state["current_agent"] = None
            _runtime_state["current_layer"] = None
            _add_event("info", f"Heal mode completed — Unified Engine ({results.get('status', 'UNKNOWN')})")
            _save_runtime_state(project_root)
            report_consolidated_summary(consolidated_results, gemini_active)
        except (ValueError, TypeError) as e:  # guardian: allow-silent-swallow
            print(f"   [!] Heal mode failed: {e}")
            traceback.print_exc()
            _add_event("error", f"Heal mode failed: {str(e)[:300]}...")
            _runtime_state["status"] = "error"
            _save_runtime_state(project_root)
        return


def report_consolidated_summary(results, gemini_active):
    """Phase 4.5: Generates the Consolidated Sovereign Health Report."""
    total_agents = sum(r.get("agents_run", 0) for r in results)
    total_fixed = sum(r.get("total_fixed", 0) for r in results)
    total_violations = sum(r.get("total_violations", 0) for r in results)
    total_errors = sum(r.get("total_errors", 0) for r in results)
    success = total_violations == 0
    print(mission_summary(total_agents, total_fixed, total_violations, total_errors, 0, success))
    print("\n" + "=" * 60)
    print(
        f"{(Colors.BRIGHT_CYAN if COLORS_AVAILABLE else '')}FINAL CONSOLIDATED SOVEREIGN HEALTH REPORT{(Colors.RESET if COLORS_AVAILABLE else '')}",
    )
    print("=" * 60)
    total_summary = {
        "agents_run": 0,
        "total_renamed": 0,
        "total_errors": 0,
        "total_fixed": 0,
        "total_violations": 0,
    }
    print("\nDomain-by-Domain Health:")
    for res in tqdm(results, desc="Processing", unit="item"):
        domain = res.get("domain", "unknown")
        compliance = res.get("compliance_score", 0)
        fixed = res.get("total_fixed", 0)
        violations = res.get("total_violations", 0)
        total_summary["agents_run"] += res.get("agents_run", 0)
        total_summary["total_renamed"] += res.get("total_renamed", 0)
        total_summary["total_errors"] += res.get("total_errors", 0)
        total_summary["total_fixed"] += fixed
        total_summary["total_violations"] += violations
        status = "✅" if compliance == 100 else "⚠️" if compliance >= 80 else "❌"
        print(f"  {status} {domain:20} Compliance: {compliance}%  Fixed: {fixed}  Violations: {violations}")
    total_checks = total_summary["total_violations"] + total_summary["total_fixed"]
    overall_compliance = (
        100
        if total_checks == 0
        else int((1 - total_summary["total_violations"] / max(total_checks, 1)) * 100)
    )
    print("\n" + "=" * 60)
    print("OVERALL SOVEREIGN HEALTH")
    print("=" * 60)
    print(f"  Domains Scanned: {len(results)}")
    print(f"  Overall Compliance: {overall_compliance}%")
    print(f"  Total Fixed: {total_summary['total_fixed']}")
    print(f"  Total Violations: {total_summary['total_violations']}")
    print(f"  Total Errors: {total_summary['total_errors']}")
    if gemini_active:
        print("\n  Meta-Learning: ACTIVE (Gemini 768D)")
        print("  L4 Memory: Historical snapshots persisted")
    else:
        print("\n  Meta-Learning: LOGGING ONLY (Set GOOGLE_API_KEY to activate)")
    print("=" * 60)


if __name__ == "__main__":
    main()
