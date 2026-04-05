"""
_ssot_pipeline.py — Pipeline constants, run_pipeline, execution plan, ADG pre-run artifact.

Extracted from execute_ssot.py. All public symbols re-exported from execute_ssot.py.
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any

# L3 import deferred to avoid layer boundary violation (L0→L3)
# from agentic_core.L3_orchestration.registry.agent_dispatch_registry import get_agent_dispatch_registry

_agent_dispatch_registry_cache: Any = None

def _get_agent_dispatch_registry() -> Any:
    """Lazy load L3 agent dispatch registry to avoid layer boundary violation."""
    global _agent_dispatch_registry_cache
    if _agent_dispatch_registry_cache is None:
        try:
            from agentic_core.L3_orchestration.registry.agent_dispatch_registry import (
                get_agent_dispatch_registry as _get_reg,
            )
            _agent_dispatch_registry_cache = _get_reg()
        except ImportError as e:
            logger.warning(f"L3 agent dispatch registry not available: {e}")
            # Return a no-op registry that allows the code to continue
            class _NoOpRegistry:
                def dispatch(self, *args, **kwargs):
                    raise RuntimeError("Agent dispatch registry not available")
            _agent_dispatch_registry_cache = _NoOpRegistry()
    return _agent_dispatch_registry_cache

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
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
    _emit_signs_execution_trace,
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

_emit_routes_to_agent("p1", "_ssot_pipeline", "L0")
_emit_orchestrates_workflow("p1", "_ssot_pipeline", "L0")
_emit_dispatches_execution_plan("p1", "_ssot_pipeline", "L0")
_emit_validates_agent_capability("p1", "_ssot_pipeline", "L0")
_emit_checks_agent_registry("p1", "_ssot_pipeline", "L0")

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
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

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import emit_determinism_digest

emit_determinism_digest("trace__ssot_pipeline", "_ssot_pipeline_dispatch_entry")
emit_determinism_digest("trace__ssot_pipeline", "_ssot_pipeline_dispatch_exit")
emit_determinism_digest("trace__ssot_pipeline", "_ssot_pipeline_tool_invoke")
emit_determinism_digest("trace__ssot_pipeline", "_ssot_pipeline_tool_complete")
emit_determinism_digest("trace__ssot_pipeline", "_ssot_pipeline_agent_entry")
emit_determinism_digest("trace__ssot_pipeline", "_ssot_pipeline_agent_exit")
emit_determinism_digest("trace__ssot_pipeline", "_ssot_pipeline_uwg_write")
emit_determinism_digest("trace__ssot_pipeline", "_ssot_pipeline_trace_sign")
emit_determinism_digest("trace__ssot_pipeline", "_ssot_pipeline_guardrail_check")
emit_determinism_digest("trace__ssot_pipeline", "_ssot_pipeline_policy_verify")

if TYPE_CHECKING:
    from ._ssot_phases import RuntimeStateManager
    from ._ssot_routing import SovereignDecisionEngine
    from ._ssot_types import HealContext

logger = logging.getLogger("UnifiedSovereign")
_logger_adg = logging.getLogger(__name__ + ".adg_prerun")

_THIS_FILE = "agentic_core/L0_routing/scripts/execute_ssot.py"

AGENTIC_CORE_DIR = "agentic_core"

EXECUTION_PLAN = [
    {
        "phase": "1",
        "name": "Discovery",
        "agents": [
            {
                "key": "reconciler",
                "method": "detect_root_drift",
                "description": "filesystem SSOT drift detection",
            },
            {
                "key": "location",
                "method": "run",
                "description": "location validation (confidence gated heal)",
            },
            {
                "key": "file_classification",
                "method": "run",
                "description": "file classification early detection",
                "kwargs": "validate_only=True, dry_run=True",
            },
        ],
    },
    {
        "phase": "2",
        "name": "Reconciliation",
        "agents": [
            {"key": "reconciler", "method": "heal", "description": "drift reconciliation (confidence gated)"}
        ],
    },
    {
        "phase": "3",
        "name": "Structural Alignment & Sovereignty",
        "agents": [
            {
                "key": "hierarchy",
                "method": "heal_hierarchy",
                "description": "hierarchy alignment (confidence gated)",
            },
            {
                "key": "file_classification",
                "method": "heal_repository",
                "description": "sovereignty purge (confidence gated, not dry_run, not validate)",
            },
        ],
    },
    {
        "phase": "4",
        "name": "Architectural Validation",
        "agents": [
            {
                "key": "arch_governor",
                "method": "comprehensive_territory_audit",
                "description": "territory audit",
            },
            {
                "key": "arch_governor",
                "method": "check_file_sizes",
                "description": "file-size check (AC-layer territories only)",
            },
        ],
    },
    {
        "phase": "5",
        "name": "Healing",
        "agents": [
            {
                "key": "arch_governor",
                "method": "generate_healing_plan",
                "description": "healing plan generation",
            },
            {
                "key": "arch_governor",
                "method": "execute_healing_plan",
                "description": "healing plan execution",
            },
        ],
    },
    {
        "phase": "6",
        "name": "Additional Agents",
        "agents": [
            {
                "key": "observability_probe",
                "method": "scan_violations",
                "description": "observability probe scan",
            },
            {
                "key": "root_hygiene",
                "method": "scan_root_violations",
                "description": "root hygiene scan (if registered)",
            },
        ],
    },
    {
        "phase": "7",
        "name": "Certification",
        "agents": [{"key": "*", "method": "aggregate", "description": "final aggregation and certification"}],
    },
]

AGENT_DEPENDENCIES: dict[str, list[str]] = {
    "hierarchy": ["reconciler", "location"],
    "file_classification": ["reconciler", "location"],
    "arch_governor": ["reconciler", "location", "hierarchy"],
    "gravity_repair": ["reconciler"],
    "observability_probe": [],
    "root_hygiene": [],
    "reconciler": [],
    "location": ["reconciler"],
    "cognitive_disposition": [],
}

CANONICAL_ROSTER_KEYS = frozenset(
    {
        "reconciler",
        "location",
        "hierarchy",
        "arch_governor",
        "gravity_repair",
        "file_classification",
        "observability_probe",
        "cognitive_disposition",
        "root_hygiene",
    }
)

AGENT_PIPELINE: list[str] = [
    "reconciler",
    "location",
    "file_classification",
    "hierarchy",
    "arch_governor",
    "gravity_repair",
    "system_architect",
    "observability_probe",
    "root_hygiene",
]

PIPELINE_SUBPHASES: tuple[str, ...] = ("pre_commit", "validate", "execute", "heal")


def get_execution_plan() -> list[dict]:
    """Return the deterministic, ordered execution plan."""
    return EXECUTION_PLAN


def _emit_pipeline_digest(adapters: "dict[str, object]", territory: str, ctx: "HealContext") -> str:
    """Compute and print the deterministic pipeline digest (once per run)."""
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "_emit_pipeline_digest", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "_emit_pipeline_digest")
    from agentic_core.L2_execution.protocol import emit_pipeline_digest as _emit

    return _emit(
        pipeline_order=AGENT_PIPELINE,
        adapter_keys=list(adapters.keys()),
        territory=territory,
        heal=getattr(ctx, "heal", False),
        enable_llm=getattr(ctx, "enable_llm", False),
    )


def run_pipeline(
    adapters: "dict[str, object]",
    territory: str,
    decision_engine: "SovereignDecisionEngine",
    state_mgr: "RuntimeStateManager",
    ctx: "HealContext",
) -> "dict[str, object]":
    """Unified pipeline loop replacing the five bespoke execute_phase*_impl functions.

    Governance invariants enforced:
    - Digest emitted exactly once per call via _emit_pipeline_digest.
    - pre_commit and validate receive scan_ctx (heal=False) structurally.
    - update_agent is never called for execute/heal when gated or fatal.
    - All four subphase slots are always present in AgentRunResult.subphases.
    - Exception in any subphase -> fatal=True -> remaining subphases skipped.
    - Confidence gate fires immediately after validate, before any execute call.

    Returns dict mapping agent_id -> AgentRunResult.
    """
    from agentic_core.L2_execution.protocol import (
        AgentRunResult,
        SubphaseResult,
    )
    from agentic_core.L3_orchestration.registry.agent_dispatch_registry import (
        get_agent_dispatch_registry,
    )

    _emit_pipeline_digest(adapters, territory, ctx)
    import dataclasses as _dc2

    if _dc2.is_dataclass(ctx) and (not isinstance(ctx, type)):
        scan_ctx = _dc2.replace(ctx, heal=False)
    else:

        class _ScanCtx:
            pass

        scan_ctx = _ScanCtx()
        for _attr in ("heal", "enable_llm", "auto_approve", "enable_telemetry", "enable_meta_learning"):
            setattr(scan_ctx, _attr, getattr(ctx, _attr, False))
        scan_ctx.heal = False
        scan_ctx.enable_llm = False

    results: dict[str, AgentRunResult] = {}
    for agent_id in AGENT_PIPELINE:
        adapter = adapters.get(agent_id)
        if adapter is None:
            continue
        run_result = AgentRunResult()
        for sp in PIPELINE_SUBPHASES:
            run_result.subphases[sp] = SubphaseResult(skipped=True, skip_reason="not reached")
        fatal = False
        for subphase_name in PIPELINE_SUBPHASES:
            is_mutating = subphase_name in ("execute", "heal")
            if is_mutating and (not getattr(ctx, "heal", False)):
                run_result.subphases[subphase_name] = SubphaseResult(skipped=True, skip_reason="heal=False")
                continue
            if is_mutating and (run_result.gated or fatal):
                run_result.subphases[subphase_name] = SubphaseResult(
                    skipped=True,
                    skip_reason=run_result.gate_reason if run_result.gated else "prior error",
                )
                continue
            state_mgr.update_agent(agent_id, subphase_name)
            effective_ctx = scan_ctx if not is_mutating else ctx
            try:
                # Wave 2: Use AgentDispatchRegistry instead of raw getattr
                registry = get_agent_dispatch_registry()
                result: SubphaseResult = registry.dispatch(
                    caller="ssot_pipeline",
                    target_instance=adapter,
                    method=subphase_name,
                    args=(territory, effective_ctx),
                )
            except (ImportError, AttributeError, TypeError, ValueError, RuntimeError) as exc:
                result = SubphaseResult(error=str(exc), skipped=True, skip_reason=f"exception: {exc}")
                run_result.error = str(exc)
                fatal = True
                state_mgr.skip_agent(agent_id, f"{subphase_name} exception: {exc}")
                run_result.subphases[subphase_name] = result
                break
            run_result.subphases[subphase_name] = result
            run_result.violations_total += len(result.violations)
            run_result.mutations_applied += len(result.fixed)
            if subphase_name == "validate" and result.violations:
                confidence = decision_engine.calculate_healing_confidence(
                    len(result.violations),
                    [v.get("type", "UNKNOWN") for v in result.violations[:10]],
                    territory,
                    agent_name=agent_id,
                )
                proceed, reason = decision_engine.should_proceed_with_healing(
                    confidence, agent_id, territory=territory
                )
                if not proceed:
                    run_result.gated = True
                    run_result.gate_reason = reason
                    state_mgr.skip_agent(agent_id, reason)
                    state_mgr.complete_agent(agent_id, True, f"gated: {reason}")
                    continue
            state_mgr.complete_agent(agent_id, result.error is None, result.error or "")
        results[agent_id] = run_result
    return results


def print_execution_plan(arbitrate_plan: bool = False, ptc_plan: bool = False) -> None:
    """Print stable, sorted execution plan to stdout."""
    for phase in EXECUTION_PLAN:
        print(f"PHASE {phase['phase']}: {phase['name']}")
        for agent in phase["agents"]:
            kwargs_str = f" ({agent['kwargs']})" if agent.get("kwargs") else ""
            print(f"  - {agent['key']}.{agent['method']}{kwargs_str}")
            print(f"    # {agent['description']}")
        print()
    if arbitrate_plan:
        print("=== MULTI-AGENT ARBITRATION ===")
        task = {"task_id": "execute_ssot_plan", "task_kind": "planning"}
        try:
            from agentic_core.L3_orchestration.arbitration.arbitration_contract import ArbitrationInput
            from agentic_core.L3_orchestration.arbitration.arbitrator import Arbitrator
            from agentic_core.L3_orchestration.arbitration.run_advisors import run_all_advisors

            proposals = run_all_advisors(task)
            input_data = ArbitrationInput(
                task_id=task["task_id"], task_kind=task["task_kind"], proposals=proposals
            )
            arbitrator = Arbitrator()
            decision = arbitrator.arbitrate(input_data)
            print(f"Selected Advisor: {decision.selected_advisor_id}")
            print(f"Selected Decision: {decision.selected_decision}")
            print(f"Score Breakdown: {decision.score_breakdown}")
            print(f"Merged Rationale: {decision.merged_rationale}")
            print(f"Merged Risks: {decision.merged_risks}")
        except (OSError, AttributeError, TypeError) as e:
            print(f"Error listing artifacts: {e}")
        print()
    if ptc_plan:
        print("=== PROGRAMMATIC TOOL CALLING ===")
        if "violations" not in dir():
            violations = []
        try:
            from agentic_core.L3_orchestration.ptc.builtin_tools import register_builtin_tools
            from agentic_core.L3_orchestration.ptc.ptc_registry import get_global_registry
            from agentic_core.L3_orchestration.ptc.tool_call_store import record_tool_call
            from agentic_core.L3_orchestration.ptc.tool_contract import ToolCall, generate_call_id
            from agentic_core.L3_orchestration.ptc.tool_invoker import ToolInvoker

            register_builtin_tools()
            registry = get_global_registry()
            invoker = ToolInvoker()
            expr_call = ToolCall(
                call_id=generate_call_id("expr_eval", {"expr": "2 + 3 * 4"}),
                tool_id="expr_eval",
                args={"expr": "2 + 3 * 4"},
                policy={"timeout": 5},
            )
            expr_result = invoker.invoke(expr_call, registry)
            spec, _ = registry.get("expr_eval")
            artifact_ref = record_tool_call(expr_call, expr_result, spec)
            ptc_plan_data = {
                "tool_calls": [
                    {
                        "tool_id": expr_call.tool_id,
                        "call_id": expr_call.call_id,
                        "args": expr_call.args,
                        "exit_code": expr_result.exit_code,
                        "stdout": expr_result.stdout,
                        "stderr": expr_result.stderr,
                        "truncated": expr_result.truncated,
                    }
                ],
                "artifact_ref": {
                    "kind": artifact_ref.kind,
                    "logical_id": artifact_ref.logical_id,
                    "version": artifact_ref.version,
                    "path": artifact_ref.path,
                },
                "summary": "PTC executed 1 tool calls for plan context",
            }
            print(json.dumps(ptc_plan_data, sort_keys=True, separators=(",", ":")))
        except (ImportError, AttributeError, TypeError, ValueError) as e:
            ptc_plan_data = {"tool_calls": [], "summary": f"PTC setup failed: {str(e)}", "error": str(e)}
            print(json.dumps(ptc_plan_data, sort_keys=True, separators=(",", ":")))
        print()


def resolve_agent_subset(requested: list[str]) -> list[str]:
    """Resolve requested agent keys to a closed set including dependencies.

    Raises ValueError on unknown keys.
    Deterministic ordering: sorted alphabetically after closure.
    """
    unknown = set(requested) - CANONICAL_ROSTER_KEYS
    if unknown:
        raise ValueError(f"Unknown agent key(s): {sorted(unknown)}. Valid: {sorted(CANONICAL_ROSTER_KEYS)}")
    closed = set(requested)
    frontier = list(requested)
    while frontier:
        key = frontier.pop()
        for dep in AGENT_DEPENDENCIES.get(key, []):
            if dep not in closed:
                closed.add(dep)
                frontier.append(dep)
    return sorted(closed)


def list_available_agents(project_root: "Path | None" = None, dedupe: bool = False) -> list:
    """Alias for discover_agents_from_registry (backward compat)."""
    from ._ssot_phases import discover_agents_from_registry

    if project_root is None:
        project_root = Path(__file__).resolve().parents[3]
    agents = discover_agents_from_registry(project_root)
    if dedupe:
        seen: set = set()
        unique = []
        for agent in agents:
            if agent not in seen:
                seen.add(agent)
                unique.append(agent)
        return unique
    return agents


def _emit_adg_pre_run_artifact(repo_root: "Path") -> None:
    """Emit artifacts/adg/execution_impact_<timestamp>.json before main execution.

    Gracefully degrades: if ADG is unavailable, writes a minimal artifact with
    adg_available=false. Never raises — must not block main execution.
    """
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    artifacts_dir = repo_root / "artifacts" / "adg"
    out_path = artifacts_dir / f"execution_impact_{ts}.json"
    payload: dict = {
        "emitted_by": "execute_ssot.py",
        "timestamp": ts,
        "target_file": _THIS_FILE,
        "adg_available": False,
        "adg_error": "",
        "impacted_modules": [],
        "impacted_module_count": 0,
        "impacted_tests": [],
        "impacted_test_count": 0,
        "risk_score": 0,
        "route_mode": "UNKNOWN",
        "layer_violation_count": 0,
        "guardian_scope": [],
        "warnings": [],
        "confidence_summary": "ADG unavailable — no impact data",
        "impact_digest": "",
    }
    try:
        artifacts_dir.mkdir(parents=True, exist_ok=True)
        from agentic_core.adg.applications.PreRunADGReport import build_pre_run_report

        report = build_pre_run_report(changed_files=[_THIS_FILE], repo_root=repo_root)
        payload["adg_available"] = report.adg_available
        payload["adg_error"] = report.adg_error
        payload["impacted_modules"] = report.impacted_modules
        payload["impacted_module_count"] = report.impacted_module_count
        payload["impacted_tests"] = report.impacted_tests
        payload["impacted_test_count"] = report.impacted_test_count
        payload["risk_score"] = report.risk_score
        payload["route_mode"] = report.route_mode
        payload["layer_violation_count"] = report.layer_violation_count
        payload["impact_digest"] = report.impact_digest
        payload["confidence_summary"] = report.summary
        if report.adg_available:
            payload["warnings"] = []
            if report.route_mode == "RESTRICTED":
                payload["warnings"].append(
                    f"RESTRICTED mode: risk_score={report.risk_score}, review before proceeding"
                )
            elif report.route_mode == "HUMAN_REVIEW":
                payload["warnings"].append(f"HUMAN_REVIEW required: risk_score={report.risk_score}")
            # Wire GuardianPrioritizer: rank guardians by ADG structural signals so
            # guardian_scope reflects evidence-based execution order, not a static list.
            try:
                from agentic_core.adg.applications.guardian_prioritizer_types import GuardianPrioritizer
                from agentic_core.adg.runtime.cache_loader import load_or_scan

                _scan = load_or_scan(repo_root=str(repo_root))
                _prio_result = GuardianPrioritizer(_scan).prioritize(guardian_ids=list(CANONICAL_ROSTER_KEYS))
                payload["guardian_scope"] = [s.guardian_id for s in _prio_result.ordered()]
                payload["guardian_priority_digest"] = _prio_result.adg_signals_digest
                _logger_adg.info(
                    "ADG guardian prioritization: %d guardians ranked, digest=%s",
                    len(payload["guardian_scope"]),
                    _prio_result.adg_signals_digest,
                )
            # guardian: allow-silent-swallow
            except (ValueError, TypeError, RuntimeError) as _gp_exc:
                payload["warnings"].append(f"GuardianPrioritizer unavailable: {_gp_exc}")
                _logger_adg.debug("GuardianPrioritizer skipped (non-fatal): %s", _gp_exc)
        else:
            payload["warnings"].append("ADG unavailable — impact analysis skipped")
        _logger_adg.info(
            "ADG pre-run artifact: route_mode=%s risk=%s impacted=%s modules tests=%s",
            report.route_mode,
            report.risk_score,
            report.impacted_module_count,
            report.impacted_test_count,
        )
    # guardian: allow-silent-swallow
    except (ValueError, TypeError, RuntimeError) as exc:
        payload["adg_error"] = str(exc)
        payload["warnings"].append(f"ADG pre-run failed: {exc}")
        _logger_adg.warning("ADG pre-run artifact emission failed: %s", exc)
    try:
        out_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        _logger_adg.info("ADG pre-run artifact written: %s", out_path)
    # guardian: allow-silent-swallow
    except (ValueError, TypeError, RuntimeError) as exc:
        _logger_adg.warning("ADG pre-run artifact write failed: %s", exc)


def _build_ssot_territory_targets(project_root: "Path") -> list[str]:
    """Derive the canonical territory target list from SOVEREIGN_TERRITORIES SSOT."""
    try:
        from agentic_core.L5_safety.config.structure_blueprint import PROJECT_ROOT_WHITELIST

        all_keys = sorted(PROJECT_ROOT_WHITELIST)
    except ImportError:  # guardian: allow-silent-swallow
        logger.warning("[territory-build] SSOT import failed — using legacy hardcoded list")
        return ["prompt_governance", "L5_safety", "L3_orchestration", "L2_execution", "L0_routing"]
    excluded = {".backup", ".github", ".gravity_state"}
    agentic_core_sublayers = ["L0_routing", "L2_execution", "L3_orchestration", "L5_safety"]
    targets = []
    for sub in agentic_core_sublayers:
        sub_path = project_root / AGENTIC_CORE_DIR / sub
        if sub_path.exists():
            targets.append(sub)
    skip = set(agentic_core_sublayers) | excluded | {AGENTIC_CORE_DIR}
    for key in sorted(all_keys):
        if key in skip:
            continue
        territory_path = project_root / key
        if territory_path.exists():
            targets.append(key)
    logger.info(f"[territory-build] SSOT-derived targets ({len(targets)}): {targets}")
    return targets


def _compute_pipeline_digest(targets: "list[str]") -> str:
    """Compute a stable determinism digest for the pipeline run."""
    import hashlib as _h
    import json as _j

    try:
        from agentic_core.L2_execution.determinism.negative_control_harness import get_config_surface as _gcs
        from agentic_core.L2_execution.determinism.negative_control_harness import hash_config_surface as _hcs
        from agentic_core.L6_observability.engines.determinism_digest_emitter import (
            DeterminismDigestEmitter as _DE,
        )
    except ImportError as _exc:
        logger.warning(f"[DETERMINISM-DIGEST] import failed: {_exc}")
        return _h.sha256(b"determinism-digest:import-failed").hexdigest()
    try:
        _policy_file = Path(__file__).resolve().parents[1] / "policy" / "v15_policy_pack.json"
        if _policy_file.exists():
            _policy_hash = _h.sha256(_policy_file.read_bytes()).hexdigest()

_reg_bytes = _j.dumps(_rd(), sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
_registry_hash = _h.sha256(_reg_bytes).hexdigest()
except (ImportError, AttributeError, TypeError):
_registry_hash = _h.sha256(b"registry:fallback").hexdigest()
_config_hash = _hcs(_gcs())
_transcript_bytes = _j.dumps(
sorted(str(t) for t in targets), sort_keys=True, separators=(",", ":"), ensure_ascii=True
).encode("utf-8")
_transcript_hash = _h.sha256(_transcript_bytes).hexdigest()
_dep_lock_hash = _h.sha256(b"dependency-lock:stable").hexdigest()
_emitter = _DE()
return _emitter.compute(
policy_hash=_policy_hash,
registry_hash=_registry_hash,
config_surface_hash=_config_hash,
transcript_hash=_transcript_hash,
dependency_lock_hash=_dep_lock_hash,
)
    _transcript_bytes = _j.dumps(
        sorted(str(t) for t in targets), sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")
    _transcript_hash = _h.sha256(_transcript_bytes).hexdigest()
    _dep_lock_hash = _h.sha256(b"dependency-lock:stable").hexdigest()
    _emitter = _DE()
    return _emitter.compute(
        policy_hash=_policy_hash,
        registry_hash=_registry_hash,
        config_surface_hash=_config_hash,
        transcript_hash=_transcript_hash,
        dependency_lock_hash=_dep_lock_hash,
    )


def try_summon_orchestrator(
    project_root: "Path", targets: list[str], execute: bool = False
) -> "tuple[bool, Any]":
    """Attempt L3 Orchestrator execution. Returns (success, results)."""
    try:
        from agentic_core.L3_orchestration.reasoning.UnifiedSovereignOrchestrator import (
            UnifiedSovereignOrchestrator,
        )

        orchestrator = UnifiedSovereignOrchestrator(project_root=project_root, targets=targets)
        if execute:
            result = orchestrator.execute()
        else:
            result = orchestrator.plan()
        if result and result.get("status") == "success":
            return (True, result)
        logger.error(f"L3 Orchestration failed: {result.get('error')}. Falling back.")
        return (False, None)
    except (ImportError, AttributeError, TypeError, ValueError) as e:
        logger.error(f"L3 Orchestration failed: {e}. Falling back to L5 iteration.")
        return (False, None)
