"""Exit Gate Harness — W8.

W8 plan: apps-rg-zip-based-full-spine-runtime-restoration-a3f7e2

Responsibilities:
- Accept SealedWorkflowPackage + GateMeshResult.
- Require GateMeshResult before emitting any X3 (except X3E_SAFE_ABSTAIN).
- Aggregate gate blockers.
- Block ALLOW_FINISH on hard FAIL or material UNKNOWN.
- Block COMMIT_REQUEST_TO_UWG without G27+G28 satisfied.
- Emit exactly ONE ExitDispositionReceipt with a single x3_code.
- NOT write L4, cache, vector, evidence, or index.
- NOT call providers.
- NOT import quarantined apps_rg runtime modules.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any

from agentic_core.runtime.contracts.sealed_workflow_types import SealedWorkflowPackage
from agentic_core.runtime.exit.exit_disposition import (
    EXIT_DISPOSITION_SCHEMA_VERSION,
    X3A_DENY_REROUTE,
    X3B_ESCALATE_HITL,
    X3C_COMMIT_REQUEST_TO_UWG,
    X3D_ALLOW_FINISH,
    X3E_SAFE_ABSTAIN,
    ExitDispositionReceipt,
    RuntimeExhaustBundle,
)
from agentic_core.runtime.gates.gate_evaluators import DEFAULT_EVALUATORS
from agentic_core.runtime.gates.gate_mesh import evaluate_gate_mesh
from agentic_core.runtime.gates.gate_profile_resolver import (
    GateProfile,
    GateProfileError,
)
from agentic_core.runtime.gates.gate_types import (
    VERDICT_FAIL,
    VERDICT_NOT_APPLICABLE,
    VERDICT_PASS,
    VERDICT_UNKNOWN,
    VERDICT_WARN,
    GateMeshResult,
    GateVerdict,
)


class ExitGateHarnessError(Exception):
    """Raised when the harness cannot proceed safely."""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()



class ExitGateHarness:
    """Core Exit gate harness — generic, no app-specific logic.

    App-specific configuration is injected via GateProfile.
    """

    def __init__(
        self,
        gate_profile: GateProfile,
        app_id: str = "",
        task_class: str = "",
    ) -> None:
        self._profile = gate_profile
        self._app_id = app_id
        self._task_class = task_class

    def evaluate(
        self,
        pkg: SealedWorkflowPackage,
        *,
        evidence: dict[str, Any] | None = None,
        request_id: str = "",
        run_id: str = "",
        trace_root: str = "",
        route_id: str = "",
        commit_requested: bool = False,
    ) -> tuple[ExitDispositionReceipt, GateMeshResult, RuntimeExhaustBundle]:
        """Evaluate the gate mesh and emit exactly one X3.

        Args:
            pkg: SealedWorkflowPackage from L3 workflow runner.
            evidence: optional evaluation evidence dict (rubric scores, etc.)
            request_id/run_id/trace_root: provenance identifiers.
            route_id: route contract identifier.
            commit_requested: True if X3C should be considered.

        Returns:
            (ExitDispositionReceipt, GateMeshResult, RuntimeExhaustBundle)

        Raises:
            ExitGateHarnessError: on unrecoverable structural failures.
        """
        if not isinstance(pkg, SealedWorkflowPackage):
            raise ExitGateHarnessError(
                f"ExitGateHarness.evaluate: expected SealedWorkflowPackage, "
                f"got {type(pkg).__name__}"
            )

        ev = evidence or {}

        # ── Evaluate gate mesh ──────────────────────────────────────────────
        mesh = evaluate_gate_mesh(
            pkg=pkg,
            required_gate_ids=self._profile.required_exit_gates,
            gate_definitions=self._profile.gate_definitions,
            evidence=ev,
            request_id=request_id,
            run_id=run_id,
            trace_root=trace_root,
            route_id=route_id,
            evaluator_registry=DEFAULT_EVALUATORS,
        )

        # ── Count signals ───────────────────────────────────────────────────
        hard_fails = [v for v in mesh.verdicts if v.is_hard_fail]
        unknowns = [v for v in mesh.verdicts if v.is_material_unknown]
        warns = [v for v in mesh.verdicts if v.result == VERDICT_WARN]
        missing = list(mesh.missing_gate_ids)

        # ── Determine X3 ────────────────────────────────────────────────────
        x3_code, decisive_reason, blocker_gate_ids, blocker_codes = self._decide_x3(
            mesh=mesh,
            hard_fails=hard_fails,
            unknowns=unknowns,
            warns=warns,
            missing=missing,
            commit_requested=commit_requested,
        )

        now = _now()
        digest = _sha(
            json.dumps({
                "request_id": request_id,
                "run_id": run_id,
                "x3_code": x3_code,
                "mesh_digest": mesh.deterministic_digest,
            }, sort_keys=True, separators=(",", ":"))
        )

        receipt = ExitDispositionReceipt(
            request_id=request_id,
            run_id=run_id,
            trace_root=trace_root,
            app_id=self._app_id,
            task_class=self._task_class,
            x3_code=x3_code,
            decisive_reason=decisive_reason,
            decisive_blocker_gate_ids=tuple(blocker_gate_ids),
            decisive_blocker_codes=tuple(blocker_codes),
            gate_mesh_result_ref=mesh.deterministic_digest,
            required_gates_passed=mesh.all_required_passed,
            hard_fail_count=len(hard_fails),
            unknown_count=len(unknowns) + len(missing),
            warn_count=len(warns),
            missing_gate_count=len(missing),
            commit_request_ref="commit_requested" if commit_requested else "",
            sealed_workflow_package_ref=pkg.package_id,
            output_artifact_digest=pkg.merged_payload_digest or pkg.merged_content_digest,
            workflow_ref=pkg.workflow_ref,
            exit_profile_ref=self._profile.profile_id,
            deterministic_digest=digest,
            created_at=now,
        )

        exhaust = RuntimeExhaustBundle(
            run_id=run_id,
            trace_root=trace_root,
            route_contract_ref=pkg.route_contract_ref,
            sealed_result_ref=pkg.package_id,
            exit_disposition_ref=digest,
            gate_mesh_result_ref=mesh.deterministic_digest,
            created_after_exit=True,
        )

        return receipt, mesh, exhaust

    def _decide_x3(
        self,
        mesh: GateMeshResult,
        hard_fails: list[GateVerdict],
        unknowns: list[GateVerdict],
        warns: list[GateVerdict],
        missing: list[str],
        commit_requested: bool,
    ) -> tuple[str, str, list[str], list[str]]:
        """Return (x3_code, reason, blocker_gate_ids, blocker_codes)."""

        # Hard FAIL → X3A_DENY_REROUTE
        if hard_fails:
            blocker_ids = [v.gate_id for v in hard_fails]
            blocker_codes = [
                code for v in hard_fails for code in v.reason_codes
            ]
            return (
                X3A_DENY_REROUTE,
                f"Hard gate failures: {blocker_ids}",
                blocker_ids,
                blocker_codes,
            )

        # Material UNKNOWN or missing gates → X3B_ESCALATE_HITL
        if unknowns or missing:
            blocker_ids = [v.gate_id for v in unknowns] + missing
            blocker_codes = [
                code for v in unknowns for code in v.reason_codes
            ] + [f"missing_gate:{gid}" for gid in missing]
            return (
                X3B_ESCALATE_HITL,
                f"Material UNKNOWN or missing gates: {blocker_ids}",
                blocker_ids,
                blocker_codes,
            )

        # Commit path — requires G27 + G28 satisfied
        if commit_requested:
            g27 = mesh.get_verdict("G27")
            g28 = mesh.get_verdict("G28")
            g27_ok = g27 is not None and (g27.is_pass or g27.is_not_applicable)
            g28_ok = g28 is not None and (g28.result in {VERDICT_PASS, VERDICT_WARN, VERDICT_NOT_APPLICABLE})
            if not (g27_ok and g28_ok):
                missing_commit = []
                if not g27_ok:
                    missing_commit.append("G27")
                if not g28_ok:
                    missing_commit.append("G28")
                return (
                    X3B_ESCALATE_HITL,
                    f"COMMIT_REQUEST_TO_UWG blocked: G27/G28 not satisfied: {missing_commit}",
                    missing_commit,
                    [f"commit_blocked_without_{gid}" for gid in missing_commit],
                )
            return (
                X3C_COMMIT_REQUEST_TO_UWG,
                "G27+G28 satisfied; commit request forwarded to UWG",
                [],
                [],
            )

        # All required gates passed → X3D_ALLOW_FINISH
        if mesh.all_required_passed:
            return (
                X3D_ALLOW_FINISH,
                "All required exit gates passed",
                [],
                [],
            )

        # Warn-only: proceed if all required passed (warns don't block by default)
        # Fall through: safe abstain
        return (
            X3E_SAFE_ABSTAIN,
            "Cannot determine safe disposition — safe abstain",
            [],
            ["safe_abstain"],
        )


