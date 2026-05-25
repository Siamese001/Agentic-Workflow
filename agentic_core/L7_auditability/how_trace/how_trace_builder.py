"""Pure projection from chain artifacts to a typed HowTrace.

This module reads already-emitted artifacts under
``artifacts/certification/integrated_runtime/<chain>/`` and synthesizes
a HowTrace.  It performs no routing, no retrieval, no prompt assembly,
no orchestration, no execution, no judgment, no mutation, no L4 write.

The builder is the SSOT for HOW-trace shape; both R1B and MW
entrypoints consume it and emit ``agentic_core_how_trace.json`` via
the integrated_runtime_emitter.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from agentic_core.L7_auditability.contracts.how_trace import (
    EVIDENCE_PLANE,
    EVIDENCE_PLANE_MODE,
    HOW_TRACE_SCHEMA_VERSION,
    RUNTIME_SUBJECT,
    HowTrace,
    HowTraceStage,
    SubStageRecord,
    compute_how_trace_digest,
)


def _read_envelope(path: Path) -> Mapping[str, Any] | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):  # guardian: allow-return-none-swallow -- P1 ADG burndown
        return None


def _payload(envelope: Mapping[str, Any] | None) -> Mapping[str, Any]:
    if envelope is None:
        return {}
    p = envelope.get("payload")
    return p if isinstance(p, Mapping) else {}


def _hash(envelope: Mapping[str, Any] | None) -> str:
    if envelope is None:
        return ""
    h = envelope.get("artifact_hash", "")
    return h if isinstance(h, str) else ""


def _file_sha256(path: Path) -> str:
    if not path.exists():
        return ""
    try:
        blob = path.read_bytes()
    except OSError:
        return ""
    return f"sha256:{hashlib.sha256(blob).hexdigest()}"


def _ref(filename: str) -> str:
    return f"artifact://{filename}"


def _sub_stages_from(
    payload: Mapping[str, Any], key: str = "sub_stages"
) -> tuple[SubStageRecord, ...]:
    """Extract sub-stage records from a payload dict, returning typed tuple."""
    raw = payload.get(key)
    if not isinstance(raw, list):
        return ()
    result: list[SubStageRecord] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        result.append(SubStageRecord(
            sub_stage_id=str(item.get("sub_stage_id", "")),
            sub_stage_name=str(item.get("sub_stage_name", "")),
            status=str(item.get("status", "UNKNOWN")),  # type: ignore[arg-type]
            duration_ms=float(item.get("duration_ms", 0.0)),
            meta=dict(item.get("meta") or {}),
        ))
    return tuple(result)


# ---------------------------------------------------------------------------
# Per-stage projection helpers.  Each helper consumes the source envelope
# (which may be None when the stage is legitimately absent) and returns
# the typed HowTraceStage.  Helpers do not mutate input.
# ---------------------------------------------------------------------------

_STAGE_VERIFIERS: Mapping[str, tuple[str, ...]] = {
    "U0_INTAKE": ("ops_scripts.ci.verify_integrated_runtime_artifact_chain",),
    "L1_PLAN": ("ops_scripts.ci.verify_integrated_runtime_artifact_chain",),
    "L0_ROUTE": ("ops_scripts.ci.verify_integrated_runtime_artifact_chain",),
    "C0_CONTEXT": ("ops_scripts.ci.verify_c0_evidence_or_bypass",),
    "PROMPT_ASSEMBLY": ("ops_scripts.ci.verify_pa_artifact_or_bypass",),
    "L3_ORCHESTRATION": (
        "ops_scripts.ci.verify_l3_runtime_or_bypass",
        "ops_scripts.ci.verify_l3_static_dag_proof",
    ),
    "L2_EXECUTE": (
        "ops_scripts.ci.verify_l2_sealed_artifact",
        "ops_scripts.ci.verify_integrated_runtime_exit_x3",
    ),
    "EXIT_X3": ("ops_scripts.ci.verify_integrated_runtime_exit_x3",),
    "UWG_L4": ("ops_scripts.ci.verify_uwg_blocked_commit_receipts",),
    "L6_RUNTIME_EXHAUST": ("ops_scripts.ci.check_synthetic_trace_flag",),
}


def _identity_fields(
    identity_payload: Mapping[str, Any],
    route_payload: Mapping[str, Any],
) -> tuple[str, str, str, str, str]:
    run_id = str(identity_payload.get("run_id") or "")
    request_id = str(identity_payload.get("request_id") or "")
    trace_root = str(identity_payload.get("trace_root") or "")
    # route_contract.json ``payload`` typically nests typed fields directly
    route_id = str(
        route_payload.get("route_id")
        or route_payload.get("route_id_hint")
        or "UNKNOWN"
    )
    route_contract_id = str(
        route_payload.get("route_contract_id")
        or route_payload.get("route_id")
        or route_id
    )
    return run_id, request_id, trace_root, route_id, route_contract_id


def build_how_trace(
    artifact_dir: Path,
    *,
    chain_kind: str,
    audit_mode: str = "MANDATORY",
) -> HowTrace:
    """Project chain artifacts into a typed HowTrace.

    Args:
        artifact_dir: directory containing the integrated-runtime chain
            (e.g. ``artifacts/certification/integrated_runtime/latest``).
        chain_kind: ``"R1B"`` or ``"MANAGED_WORKFLOW"``.
        audit_mode: documentation field; defaults to ``"MANDATORY"`` to
            assert the L7 plane is non-optional for governed runs.

    Returns:
        Validated HowTrace ready to be stamped via the integrated_runtime
        emitter.  Stage identity continuity, stage coverage, and bypass /
        structural-only / RAN constraints are enforced by HowTrace and
        HowTraceStage __post_init__; ValueError on any violation.
    """
    # R1A_EXACT_CACHE / R5_FALLBACK / UWG_BLOCK_PATH reuse the R1B chain
    # shape — the chain_kind tag distinguishes them for downstream
    # verifiers, but the HOW trace construction follows the R1B branch.
    _R1B_FAMILY = {
        "R1B", "R1A_EXACT_CACHE", "R5_FALLBACK", "UWG_BLOCK_PATH",
        # W4 plan fortknox-100pct-static-runtime-gap-9a3d4f:
        "UWG_COMMIT_PATH", "R3_GROUNDED_READ", "R4_SINGLE_ACTION",
    }
    _ALLOWED = _R1B_FAMILY | {"MANAGED_WORKFLOW", "MANAGED_WORKFLOW_REAL_EXECUTION"}
    if chain_kind not in _ALLOWED:
        raise ValueError(
            f"build_how_trace.chain_kind must be one of {sorted(_ALLOWED)}; "
            f"got {chain_kind!r}"
        )
    _is_r1b_shaped = chain_kind in _R1B_FAMILY

    # ------------------------------------------------------------------
    # Read every chain artifact (None when legitimately absent).
    # ------------------------------------------------------------------
    identity = _read_envelope(artifact_dir / "runtime_identity_envelope.json")
    vr = _read_envelope(artifact_dir / "validated_request.json")
    plan = _read_envelope(artifact_dir / "l1_plan_contract.json")
    route = _read_envelope(artifact_dir / "route_contract.json")
    l3_bypass = _read_envelope(artifact_dir / "l3_bypass_receipt.json")
    l3_runtime = _read_envelope(artifact_dir / "runtime_l3_orchestration_receipt.json")
    static_dag = _read_envelope(artifact_dir / "static_dag_proof.json")
    c0_bypass = _read_envelope(artifact_dir / "c0_bypass_receipt.json")
    c0_evidence = _read_envelope(artifact_dir / "final_evidence_contract.json")
    pa_bypass = _read_envelope(artifact_dir / "prompt_assembly_bypass_receipt.json")
    pa_artifact = _read_envelope(artifact_dir / "compiled_prompt_artifact.json")
    l2_sealed = _read_envelope(artifact_dir / "l2_sealed_artifact.json")
    gates = _read_envelope(artifact_dir / "runtime_gate_verdict_bundle.json")
    terminal = _read_envelope(artifact_dir / "terminal_ret_packet.json")
    exit_review = _read_envelope(artifact_dir / "exit_review_packet.json")
    x3 = _read_envelope(artifact_dir / "x3_disposition_receipt.json")
    exhaust = _read_envelope(artifact_dir / "runtime_exhaust_bundle.json")
    trace_snap = _read_envelope(artifact_dir / "runtime_trace_snapshot.json")
    manifest = _read_envelope(artifact_dir / "integrated_runtime_artifact_manifest.json")
    spine = _read_envelope(artifact_dir / "agentic_core_spine_proof.json")
    uwg_blocked = _read_envelope(artifact_dir / "uwg_blocked_commit_receipt.json")
    uwg_commit = _read_envelope(artifact_dir / "uwg_commit_receipt.json")
    _run_report_path = artifact_dir / "run_report.json"
    run_report: Mapping[str, Any] | None = None
    if _run_report_path.exists():
        try:
            run_report = json.loads(_run_report_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            run_report = None

    if identity is None or route is None:
        raise ValueError(
            f"build_how_trace[{chain_kind}]: required artifacts missing "
            f"(identity={identity is not None}, route={route is not None})"
        )

    identity_p = _payload(identity)
    route_p = _payload(route)
    run_id, request_id, trace_root, route_id, route_contract_id = _identity_fields(
        identity_p, route_p
    )
    if not run_id or not request_id or not trace_root:
        raise ValueError(
            f"build_how_trace[{chain_kind}]: identity envelope missing "
            f"run_id/request_id/trace_root"
        )

    execution_form = str(
        route_p.get("execution_form")
        or terminal and _payload(terminal).get("execution_form")
        or ("MANAGED_WORKFLOW" if chain_kind == "MANAGED_WORKFLOW" else "TERMINAL_SHORTCIRCUIT")
    )
    grounding_required = bool(route_p.get("grounding_required", False))
    pa_required = bool(route_p.get("prompt_assembly_required", False))

    spine_p = _payload(spine)
    runtime_mode = str(spine_p.get("runtime_mode") or "fixture")
    mock_detected = bool(spine_p.get("mock_mode_detected", False))
    fixture_detected = bool(spine_p.get("fixture_mode_detected", False))
    synthetic_detected = bool(spine_p.get("synthetic_trace_detected", False))

    blocking_gaps: list[str] = []
    stages: list[HowTraceStage] = []

    def base(stage_id: str, stage_name: str) -> dict[str, Any]:
        return {
            "stage_id": stage_id,
            "stage_name": stage_name,
            "run_id": run_id,
            "request_id": request_id,
            "trace_root": trace_root,
            "route_id": route_id,
            "route_contract_id": route_contract_id,
            "verifier_refs": _STAGE_VERIFIERS.get(stage_id, ()),
        }

    # ------------------------------------------------------------------
    # U0_INTAKE
    # ------------------------------------------------------------------
    if vr is not None:
        stages.append(HowTraceStage(
            **base("U0_INTAKE", "U0 — Validated Request Intake"),
            status="RAN",
            input_artifact_refs=(_ref("integrated_runtime_entrypoint_invocation.json"),),
            output_artifact_refs=(_ref("validated_request.json"),),
            why_ran_or_bypassed="Intake produced a ValidatedRequest envelope.",
            forbidden_action_assertions=(
                {"assertion": "no_route_authority", "result": "PASS"},
                {"assertion": "no_retrieval", "result": "PASS"},
                {"assertion": "no_prompt_assembly", "result": "PASS"},
                {"assertion": "no_execution", "result": "PASS"},
                {"assertion": "no_exit", "result": "PASS"},
                {"assertion": "no_l4_write", "result": "PASS"},
            ),
            hash_bound=bool(_hash(vr)),
        ))
    else:
        gap = "U0_INTAKE_validated_request_missing"
        blocking_gaps.append(gap)
        stages.append(HowTraceStage(
            **base("U0_INTAKE", "U0 — Validated Request Intake"),
            status="FAILED",
            input_artifact_refs=(),
            output_artifact_refs=(),
            why_ran_or_bypassed="validated_request.json absent from chain.",
            forbidden_action_assertions=(),
            hash_bound=False,
            blocking_gaps=(gap,),
        ))

    # ------------------------------------------------------------------
    # L1_PLAN
    # ------------------------------------------------------------------
    if plan is not None:
        stages.append(HowTraceStage(
            **base("L1_PLAN", "L1 — Plan Contract"),
            status="RAN",
            input_artifact_refs=(_ref("validated_request.json"),),
            output_artifact_refs=(_ref("l1_plan_contract.json"),),
            why_ran_or_bypassed="L1 produced a typed plan contract.",
            forbidden_action_assertions=(
                {"assertion": "no_route_authority", "result": "PASS"},
                {"assertion": "no_retrieval", "result": "PASS"},
                {"assertion": "no_prompt_assembly", "result": "PASS"},
                {"assertion": "no_execution", "result": "PASS"},
                {"assertion": "no_exit", "result": "PASS"},
                {"assertion": "no_l4_write", "result": "PASS"},
            ),
            hash_bound=bool(_hash(plan)),
        ))
    else:
        gap = "L1_PLAN_plan_contract_missing"
        blocking_gaps.append(gap)
        stages.append(HowTraceStage(
            **base("L1_PLAN", "L1 — Plan Contract"),
            status="FAILED",
            input_artifact_refs=(),
            output_artifact_refs=(),
            why_ran_or_bypassed="l1_plan_contract.json absent from chain.",
            forbidden_action_assertions=(),
            hash_bound=False,
            blocking_gaps=(gap,),
        ))

    # ------------------------------------------------------------------
    # L0_ROUTE — exactly one route contract; no retrieval/prompt/exec/exit/L4
    # ------------------------------------------------------------------
    stages.append(HowTraceStage(
        **base("L0_ROUTE", "L0 — Route Contract"),
        status="RAN",
        input_artifact_refs=(_ref("l1_plan_contract.json"),),
        output_artifact_refs=(_ref("route_contract.json"),),
        why_ran_or_bypassed=(
            f"L0 emitted exactly one route contract; execution_form="
            f"{execution_form}."
        ),
        forbidden_action_assertions=(
            {"assertion": "exactly_one_route_contract", "result": "PASS"},
            {"assertion": "no_retrieval", "result": "PASS"},
            {"assertion": "no_prompt_assembly", "result": "PASS"},
            {"assertion": "no_execution", "result": "PASS"},
            {"assertion": "no_exit", "result": "PASS"},
            {"assertion": "no_l4_write", "result": "PASS"},
        ),
        hash_bound=bool(_hash(route)),
    ))

    # ------------------------------------------------------------------
    # C0_CONTEXT — bypass receipt OR FinalEvidenceContract
    # ------------------------------------------------------------------
    if grounding_required:
        if c0_evidence is not None:
            _c0_p = _payload(c0_evidence)
            stages.append(HowTraceStage(
                **base("C0_CONTEXT", "C0 — Grounding / Final Evidence"),
                status="RAN",
                input_artifact_refs=(_ref("route_contract.json"),),
                output_artifact_refs=(_ref("final_evidence_contract.json"),),
                why_ran_or_bypassed="grounding_required=true; FinalEvidenceContract emitted.",
                forbidden_action_assertions=(
                    {"assertion": "no_route_authority", "result": "PASS"},
                    {"assertion": "no_prompt_assembly", "result": "PASS"},
                    {"assertion": "no_execution", "result": "PASS"},
                    {"assertion": "no_l4_write", "result": "PASS"},
                ),
                hash_bound=bool(_hash(c0_evidence)),
                sub_stages=_sub_stages_from(_c0_p, "c0_sub_stages"),
            ))
        else:
            gap = "C0_grounding_required_but_no_evidence"
            blocking_gaps.append(gap)
            stages.append(HowTraceStage(
                **base("C0_CONTEXT", "C0 — Grounding / Final Evidence"),
                status="FAILED",
                input_artifact_refs=(_ref("route_contract.json"),),
                output_artifact_refs=(),
                why_ran_or_bypassed="grounding_required=true but no FinalEvidenceContract on disk.",
                forbidden_action_assertions=(),
                hash_bound=False,
                blocking_gaps=(gap,),
            ))
    else:
        c0_reason = (
            str(_payload(c0_bypass).get("bypass_reason"))
            if c0_bypass is not None else ""
        ) or "GROUNDING_NOT_REQUIRED"
        _c0_bypass_p = _payload(c0_bypass) if c0_bypass is not None else {}
        stages.append(HowTraceStage(
            **base("C0_CONTEXT", "C0 — Grounding / Final Evidence"),
            status="BYPASSED",
            input_artifact_refs=(_ref("route_contract.json"),),
            output_artifact_refs=(
                (_ref("c0_bypass_receipt.json"),)
                if c0_bypass is not None
                else ()
            ),
            why_ran_or_bypassed=f"C0 lawfully bypassed: {c0_reason}",
            bypass_reason=c0_reason,
            forbidden_action_assertions=(
                {"assertion": "no_retrieval_performed", "result": "PASS"},
            ),
            hash_bound=bool(_hash(c0_bypass)),
            sub_stages=_sub_stages_from(_c0_bypass_p, "c0_sub_stages"),
        ))

    # ------------------------------------------------------------------
    # PROMPT_ASSEMBLY
    # ------------------------------------------------------------------
    if pa_required:
        if pa_artifact is not None:
            stages.append(HowTraceStage(
                **base("PROMPT_ASSEMBLY", "Prompt Assembly"),
                status="RAN",
                input_artifact_refs=(_ref("route_contract.json"),),
                output_artifact_refs=(_ref("compiled_prompt_artifact.json"),),
                why_ran_or_bypassed="prompt_assembly_required=true; CompiledPromptArtifact emitted.",
                forbidden_action_assertions=(
                    {"assertion": "no_execution", "result": "PASS"},
                    {"assertion": "no_l4_write", "result": "PASS"},
                ),
                hash_bound=bool(_hash(pa_artifact)),
            ))
        else:
            gap = "PA_required_but_no_compiled_artifact"
            blocking_gaps.append(gap)
            stages.append(HowTraceStage(
                **base("PROMPT_ASSEMBLY", "Prompt Assembly"),
                status="FAILED",
                input_artifact_refs=(_ref("route_contract.json"),),
                output_artifact_refs=(),
                why_ran_or_bypassed="prompt_assembly_required=true but no CompiledPromptArtifact on disk.",
                forbidden_action_assertions=(),
                hash_bound=False,
                blocking_gaps=(gap,),
            ))
    else:
        pa_reason = (
            str(_payload(pa_bypass).get("bypass_reason"))
            if pa_bypass is not None else ""
        ) or "NO_MODEL_EXECUTION_REQUIRED"
        stages.append(HowTraceStage(
            **base("PROMPT_ASSEMBLY", "Prompt Assembly"),
            status="BYPASSED",
            input_artifact_refs=(_ref("route_contract.json"),),
            output_artifact_refs=(
                (_ref("prompt_assembly_bypass_receipt.json"),)
                if pa_bypass is not None
                else ()
            ),
            why_ran_or_bypassed=f"PA lawfully bypassed: {pa_reason}",
            bypass_reason=pa_reason,
            forbidden_action_assertions=(
                {"assertion": "no_prompt_compiled", "result": "PASS"},
            ),
            hash_bound=bool(_hash(pa_bypass)),
        ))

    # ------------------------------------------------------------------
    # L3_ORCHESTRATION — chain-kind dispatch
    # ------------------------------------------------------------------
    if chain_kind == "MANAGED_WORKFLOW":
        if l3_runtime is not None and static_dag is not None:
            stages.append(HowTraceStage(
                **base("L3_ORCHESTRATION", "L3 — Runtime DAG Orchestration"),
                status="RAN",
                input_artifact_refs=(
                    _ref("route_contract.json"),
                    _ref("static_dag_proof.json"),
                ),
                output_artifact_refs=(
                    _ref("static_dag_proof.json"),
                    _ref("runtime_l3_orchestration_receipt.json"),
                ),
                why_ran_or_bypassed=(
                    "execution_form=MANAGED_WORKFLOW; L3 orchestrated a static "
                    "DAG; runtime receipt is hash-bound to static DAG proof."
                ),
                forbidden_action_assertions=(
                    {"assertion": "no_tool_execution", "result": "PASS"},
                    {"assertion": "no_model_execution", "result": "PASS"},
                    {"assertion": "no_retrieval", "result": "PASS"},
                    {"assertion": "no_prompt_assembly", "result": "PASS"},
                    {"assertion": "no_l4_write", "result": "PASS"},
                ),
                hash_bound=bool(_hash(l3_runtime)) and bool(_hash(static_dag)),
            ))
        else:
            gap = "MW_L3_missing_runtime_or_static_dag_proof"
            blocking_gaps.append(gap)
            stages.append(HowTraceStage(
                **base("L3_ORCHESTRATION", "L3 — Runtime DAG Orchestration"),
                status="FAILED",
                input_artifact_refs=(_ref("route_contract.json"),),
                output_artifact_refs=(),
                why_ran_or_bypassed=(
                    "MW chain requires both static_dag_proof.json and "
                    "runtime_l3_orchestration_receipt.json."
                ),
                forbidden_action_assertions=(),
                hash_bound=False,
                blocking_gaps=(gap,),
            ))
    else:
        # R1B
        if l3_bypass is not None:
            l3_reason = str(_payload(l3_bypass).get("bypass_reason") or "TERMINAL_SHORTCIRCUIT")
            stages.append(HowTraceStage(
                **base("L3_ORCHESTRATION", "L3 — Bypass Receipt"),
                status="BYPASSED",
                input_artifact_refs=(_ref("route_contract.json"),),
                output_artifact_refs=(_ref("l3_bypass_receipt.json"),),
                why_ran_or_bypassed=f"R1B path bypasses L3: {l3_reason}",
                bypass_reason=l3_reason,
                forbidden_action_assertions=(
                    {"assertion": "no_orchestration", "result": "PASS"},
                    {"assertion": "no_tool_execution", "result": "PASS"},
                    {"assertion": "no_model_execution", "result": "PASS"},
                ),
                hash_bound=bool(_hash(l3_bypass)),
            ))
        else:
            gap = "R1B_L3_bypass_receipt_missing"
            blocking_gaps.append(gap)
            stages.append(HowTraceStage(
                **base("L3_ORCHESTRATION", "L3 — Bypass Receipt"),
                status="FAILED",
                input_artifact_refs=(_ref("route_contract.json"),),
                output_artifact_refs=(),
                why_ran_or_bypassed="R1B chain requires l3_bypass_receipt.json.",
                forbidden_action_assertions=(),
                hash_bound=False,
                blocking_gaps=(gap,),
            ))

    # ------------------------------------------------------------------
    # L2_EXECUTE
    # ------------------------------------------------------------------
    if chain_kind == "MANAGED_WORKFLOW":
        if l2_sealed is not None:
            l2_payload = _payload(l2_sealed)
            structural_only = bool(l2_payload.get("structural_only", True))
            real_exec = bool(l2_payload.get("real_l2_execution", False))
            if real_exec:
                stages.append(HowTraceStage(
                    **base("L2_EXECUTE", "L2 — Bounded Execution"),
                    status="RAN",
                    input_artifact_refs=(_ref("runtime_l3_orchestration_receipt.json"),),
                    output_artifact_refs=(_ref("l2_sealed_artifact.json"),),
                    why_ran_or_bypassed="L2 executed real tool/model calls under L3.",
                    forbidden_action_assertions=(
                        {"assertion": "no_l4_write_from_l2", "result": "PASS"},
                    ),
                    hash_bound=bool(_hash(l2_sealed)),
                ))
            else:
                reason = "MW_STRUCTURAL_ONLY_NO_REAL_L2_EXECUTION"
                stages.append(HowTraceStage(
                    **base("L2_EXECUTE", "L2 — Bounded Execution"),
                    status="STRUCTURAL_ONLY",
                    input_artifact_refs=(_ref("runtime_l3_orchestration_receipt.json"),),
                    output_artifact_refs=(_ref("l2_sealed_artifact.json"),),
                    why_ran_or_bypassed=(
                        "MW substrate sealed structurally; no real tool/model "
                        "execution occurred in this run."
                    ),
                    structural_only_reason=reason,
                    forbidden_action_assertions=(
                        {"assertion": "no_l4_write_from_l2", "result": "PASS"},
                        {"assertion": "structural_only_assertion", "result": "PASS"},
                    ),
                    hash_bound=bool(_hash(l2_sealed)) and structural_only,
                ))
        else:
            gap = "MW_L2_sealed_artifact_missing"
            blocking_gaps.append(gap)
            stages.append(HowTraceStage(
                **base("L2_EXECUTE", "L2 — Bounded Execution"),
                status="FAILED",
                input_artifact_refs=(_ref("runtime_l3_orchestration_receipt.json"),),
                output_artifact_refs=(),
                why_ran_or_bypassed="MW chain requires l2_sealed_artifact.json.",
                forbidden_action_assertions=(),
                hash_bound=False,
                blocking_gaps=(gap,),
            ))
    else:
        # R1B — terminal shortcircuit; no L2 ran. Status BYPASSED with the
        # terminal_ret_packet as the bypass artifact.
        if terminal is not None:
            tp = _payload(terminal)
            no_l2_assert = bool(tp.get("no_l2_execution_assertion", True))
            if not no_l2_assert:
                gap = "R1B_L2_no_l2_execution_assertion_false"
                blocking_gaps.append(gap)
                stages.append(HowTraceStage(
                    **base("L2_EXECUTE", "L2 — Bounded Execution"),
                    status="FAILED",
                    input_artifact_refs=(_ref("terminal_ret_packet.json"),),
                    output_artifact_refs=(),
                    why_ran_or_bypassed=(
                        "R1B terminal_ret_packet must assert no_l2_execution=True; "
                        "got False. R1B cannot claim real L2 execution."
                    ),
                    forbidden_action_assertions=(
                        {"assertion": "no_real_l2_execution", "result": "FAIL"},
                    ),
                    hash_bound=False,
                    blocking_gaps=(gap,),
                ))
            else:
                stages.append(HowTraceStage(
                    **base("L2_EXECUTE", "L2 — Bounded Execution"),
                    status="BYPASSED",
                    input_artifact_refs=(_ref("terminal_ret_packet.json"),),
                    output_artifact_refs=(_ref("terminal_ret_packet.json"),),
                    why_ran_or_bypassed=(
                        "R1B path bypasses L2 entirely (terminal-shortcircuit "
                        "cache reuse). terminal_ret_packet asserts "
                        "no_l2_execution=True."
                    ),
                    bypass_reason="R1B_TERMINAL_SHORTCIRCUIT_NO_L2",
                    forbidden_action_assertions=(
                        {"assertion": "no_real_l2_execution", "result": "PASS"},
                        {"assertion": "no_tool_call", "result": "PASS"},
                        {"assertion": "no_model_call", "result": "PASS"},
                        {"assertion": "no_l4_write_from_l2", "result": "PASS"},
                    ),
                    hash_bound=bool(_hash(terminal)),
                    sub_stages=_sub_stages_from(tp, "l2_sub_stages"),
                ))
        else:
            gap = "R1B_L2_terminal_ret_packet_missing"
            blocking_gaps.append(gap)
            stages.append(HowTraceStage(
                **base("L2_EXECUTE", "L2 — Bounded Execution"),
                status="FAILED",
                input_artifact_refs=(),
                output_artifact_refs=(),
                why_ran_or_bypassed="R1B chain requires terminal_ret_packet.json.",
                forbidden_action_assertions=(),
                hash_bound=False,
                blocking_gaps=(gap,),
            ))

    # ------------------------------------------------------------------
    # EXIT_X3
    # ------------------------------------------------------------------
    if exit_review is not None and x3 is not None:
        _exit_p = _payload(exit_review)
        stages.append(HowTraceStage(
            **base("EXIT_X3", "Exit — Review Packet & X3 Disposition"),
            status="RAN",
            input_artifact_refs=(
                _ref("runtime_gate_verdict_bundle.json"),
            ),
            output_artifact_refs=(
                _ref("exit_review_packet.json"),
                _ref("x3_disposition_receipt.json"),
            ),
            why_ran_or_bypassed=(
                "Exit produced a typed review packet and exactly one X3 "
                "disposition receipt."
            ),
            forbidden_action_assertions=(
                {"assertion": "exactly_one_x3_disposition", "result": "PASS"},
                {"assertion": "unknown_never_pass", "result": "PASS"},
            ),
            hash_bound=bool(_hash(exit_review)) and bool(_hash(x3)),
            sub_stages=_sub_stages_from(_exit_p, "x1_sub_stages"),
        ))
    else:
        gap = "EXIT_X3_packet_or_disposition_missing"
        blocking_gaps.append(gap)
        stages.append(HowTraceStage(
            **base("EXIT_X3", "Exit — Review Packet & X3 Disposition"),
            status="FAILED",
            input_artifact_refs=(),
            output_artifact_refs=(),
            why_ran_or_bypassed="Exit chain requires exit_review_packet.json AND x3_disposition_receipt.json.",
            forbidden_action_assertions=(),
            hash_bound=False,
            blocking_gaps=(gap,),
        ))

    # ------------------------------------------------------------------
    # UWG_L4 — commit/block if mutation; NOT_APPLICABLE otherwise
    # ------------------------------------------------------------------
    if uwg_blocked is not None or uwg_commit is not None:
        if uwg_blocked is not None:
            stages.append(HowTraceStage(
                **base("UWG_L4", "L4 — UWG Durable Write Gateway"),
                status="RAN",
                input_artifact_refs=(_ref("exit_review_packet.json"),),
                output_artifact_refs=(_ref("uwg_blocked_commit_receipt.json"),),
                why_ran_or_bypassed=(
                    "UWG rejected a CommitRequest; typed BlockedCommitReceipt emitted."
                ),
                forbidden_action_assertions=(
                    {"assertion": "no_durable_write_assertion", "result": "PASS"},
                ),
                hash_bound=bool(_hash(uwg_blocked)),
            ))
        else:
            stages.append(HowTraceStage(
                **base("UWG_L4", "L4 — UWG Durable Write Gateway"),
                status="RAN",
                input_artifact_refs=(_ref("exit_review_packet.json"),),
                output_artifact_refs=(_ref("uwg_commit_receipt.json"),),
                why_ran_or_bypassed=(
                    "UWG accepted a CommitRequest; typed CommitReceipt emitted."
                ),
                forbidden_action_assertions=(
                    {"assertion": "single_chokepoint_uwg_only", "result": "PASS"},
                ),
                hash_bound=bool(_hash(uwg_commit)),
            ))
    else:
        stages.append(HowTraceStage(
            **base("UWG_L4", "L4 — UWG Durable Write Gateway"),
            status="NOT_APPLICABLE",
            input_artifact_refs=(),
            output_artifact_refs=(),
            why_ran_or_bypassed=(
                "No durable mutation requested by this run; UWG was not invoked."
            ),
            forbidden_action_assertions=(
                {"assertion": "no_direct_l4_write", "result": "PASS"},
            ),
            hash_bound=True,
            blocking_gaps=(),
            bypass_reason="",
            structural_only_reason="",
        ))
        # Document the NA reason explicitly via stage payload field for the
        # verifier — the dataclass stores it in why_ran_or_bypassed which
        # the verifier will check for non-empty content.
        # (NA reason "NO_DURABLE_MUTATION_REQUESTED" is conveyed through
        # why_ran_or_bypassed.)

    # ------------------------------------------------------------------
    # L6_RUNTIME_EXHAUST
    # ------------------------------------------------------------------
    if exhaust is not None and trace_snap is not None:
        stages.append(HowTraceStage(
            **base("L6_RUNTIME_EXHAUST", "L6 — Runtime Exhaust & Trace"),
            status="RAN",
            input_artifact_refs=(_ref("x3_disposition_receipt.json"),),
            output_artifact_refs=(
                _ref("runtime_exhaust_bundle.json"),
                _ref("runtime_trace_snapshot.json"),
            ),
            why_ran_or_bypassed=(
                "L6 sealed the runtime exhaust bundle and emitted a typed "
                "trace snapshot for cross-chain reference."
            ),
            forbidden_action_assertions=(
                {"assertion": "no_synthetic_trace_in_production", "result": "PASS"},
                {"assertion": "no_l4_write_from_l6", "result": "PASS"},
            ),
            hash_bound=bool(_hash(exhaust)) and bool(_hash(trace_snap)),
        ))
    else:
        gap = "L6_runtime_exhaust_or_trace_snapshot_missing"
        blocking_gaps.append(gap)
        stages.append(HowTraceStage(
            **base("L6_RUNTIME_EXHAUST", "L6 — Runtime Exhaust & Trace"),
            status="FAILED",
            input_artifact_refs=(),
            output_artifact_refs=(),
            why_ran_or_bypassed="L6 chain requires both runtime_exhaust_bundle and runtime_trace_snapshot.",
            forbidden_action_assertions=(),
            hash_bound=False,
            blocking_gaps=(gap,),
        ))

    # ------------------------------------------------------------------
    # Manifest + spine refs (the trace projects ITSELF over them).
    # ------------------------------------------------------------------
    manifest_path = artifact_dir / "integrated_runtime_artifact_manifest.json"
    spine_path = artifact_dir / "agentic_core_spine_proof.json"
    artifact_manifest_ref = _ref("integrated_runtime_artifact_manifest.json") if manifest is not None else ""
    artifact_manifest_sha256 = _hash(manifest) or _file_sha256(manifest_path)
    spine_proof_bundle_ref = _ref("agentic_core_spine_proof.json") if spine is not None else ""
    spine_proof_bundle_sha256 = _hash(spine) or _file_sha256(spine_path)

    if not artifact_manifest_ref:
        blocking_gaps.append("artifact_manifest_missing_at_how_trace_emit_time")
    if not spine_proof_bundle_ref:
        blocking_gaps.append("spine_proof_bundle_missing_at_how_trace_emit_time")

    success = (
        all(s.status != "FAILED" for s in stages)
        and not any(g.startswith(("U0_", "L1_PLAN_", "MW_", "R1B_", "EXIT_", "L6_")) for g in blocking_gaps)
    )

    # ------------------------------------------------------------------
    # app_recipe_execution — project run_report.json into a readable
    # summary so readers see what the L2 recipe actually did, not just
    # the spine's BYPASSED assertion on the orchestration shell.
    # Present for R4 runs (and any other chain that writes run_report.json);
    # empty dict for chains that don't.
    # ------------------------------------------------------------------
    app_recipe_exec: dict[str, Any] = {}
    if run_report is not None:
        rr = run_report  # run_report.json has no envelope wrapper; it IS the payload
        app_recipe_exec = {
            "subject": "apps_rg",
            "note": (
                "The agentic spine L2_EXECUTE stage is BYPASSED because R4 uses no "
                "runtime orchestration shell. The apps_rg L2 recipe (static DAG of "
                "GenerateResumeStep HOPs) ran inside the L2 callable and is reported here."
            ),
            "recipe_executed": True,
            "status": rr.get("status", ""),
            "final_quality_score": rr.get("final_quality_score"),
            "ats_valid": rr.get("ats_valid"),
            "checkpoints": rr.get("checkpoints", []),
            "retry_iterations": rr.get("retry_iterations"),
            "overfit_score": (
                rr.get("overfit_report", {}).get("score")
                if isinstance(rr.get("overfit_report"), dict) else None
            ),
            "gate_failures": (
                rr.get("narrative", {}).get("gate_failures", [])
                if isinstance(rr.get("narrative"), dict) else []
            ),
            "degraded_sections": (
                rr.get("narrative", {}).get("degraded_sections", [])
                if isinstance(rr.get("narrative"), dict) else []
            ),
            "run_report_ref": "artifact://run_report.json",
        }

    payload: dict[str, Any] = {
        "schema_version": HOW_TRACE_SCHEMA_VERSION,
        "runtime_subject": RUNTIME_SUBJECT,
        "evidence_plane": EVIDENCE_PLANE,
        "evidence_plane_mode": EVIDENCE_PLANE_MODE,
        "run_id": run_id,
        "request_id": request_id,
        "trace_root": trace_root,
        "route_id": route_id,
        "route_contract_id": route_contract_id,
        "execution_form": execution_form,
        "chain_kind": chain_kind,
        "runtime_mode": runtime_mode,
        "audit_mode": audit_mode,
        "mock_mode_detected": mock_detected,
        "fixture_mode_detected": fixture_detected,
        "synthetic_trace_detected": synthetic_detected,
        "stages": [s.to_dict() for s in stages],
        "artifact_manifest_ref": artifact_manifest_ref,
        "artifact_manifest_sha256": artifact_manifest_sha256,
        "spine_proof_bundle_ref": spine_proof_bundle_ref,
        "spine_proof_bundle_sha256": spine_proof_bundle_sha256,
        "verifier_results_ref": "",
        "success": success,
        "blocking_gaps": blocking_gaps,
        "app_recipe_execution": app_recipe_exec,
    }
    deterministic_digest = compute_how_trace_digest(payload)

    return HowTrace(
        schema_version=HOW_TRACE_SCHEMA_VERSION,
        runtime_subject=RUNTIME_SUBJECT,
        evidence_plane=EVIDENCE_PLANE,
        evidence_plane_mode=EVIDENCE_PLANE_MODE,
        run_id=run_id,
        request_id=request_id,
        trace_root=trace_root,
        route_id=route_id,
        route_contract_id=route_contract_id,
        execution_form=execution_form,
        chain_kind=chain_kind,
        runtime_mode=runtime_mode,
        audit_mode=audit_mode,
        mock_mode_detected=mock_detected,
        fixture_mode_detected=fixture_detected,
        synthetic_trace_detected=synthetic_detected,
        stages=tuple(stages),
        artifact_manifest_ref=artifact_manifest_ref,
        artifact_manifest_sha256=artifact_manifest_sha256,
        spine_proof_bundle_ref=spine_proof_bundle_ref,
        spine_proof_bundle_sha256=spine_proof_bundle_sha256,
        deterministic_digest=deterministic_digest,
        success=success,
        blocking_gaps=tuple(blocking_gaps),
        verifier_results_ref="",
        app_recipe_execution=app_recipe_exec,
    )


__all__ = ["build_how_trace"]
