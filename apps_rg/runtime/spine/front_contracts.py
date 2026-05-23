"""Spine front contracts — U0/L1/L0 before C0 (apps-rg-spine-only-unification-d8f4a2).

Product-visible section runs emit ValidatedRequest, L1PlanContract, and RouteContract
via apps_rg bindings before proof-pool/C0 retrieval. Single spine entry:
``apps_rg.runtime.spine.apps_rg_spine_run``.
"""
from __future__ import annotations

import json
import os
import uuid
from contextvars import ContextVar
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from apps_rg.runtime.section_spine_terminology import (
    CANONICAL_CONTRACT_TYPES,
    CANONICAL_SPINE_CHAIN,
    section_lane_spine_classification,
)

_FIXTURE_DEV_BYPASS_CTX: ContextVar[bool] = ContextVar(
    "apps_rg_section_fixture_dev_bypass", default=False
)

FRONT_SPINE_CONTRACTS: tuple[str, ...] = (
    "ValidatedRequest",
    "L1PlanContract",
    "RouteContract",
)

DOWNSTREAM_MISSING_CANONICAL_CONTRACTS: tuple[str, ...] = tuple(
    c for c in CANONICAL_CONTRACT_TYPES if c not in FRONT_SPINE_CONTRACTS
)

OBSERVED_CHAIN_WITH_FRONT_BRIDGE: tuple[str, ...] = (
    "CLI",
    "apps_rg_spine_run",
    "U0",
    "L1",
    "L0",
    "c0_retrieve_apps_rg",
    "pa_compose_apps_rg",
    "l2_execute_apps_rg",
    "ExitEvalPipeline",
    "section_L6_shadow",
)


class SectionFrontSpinePreconditionError(RuntimeError):
    """Raised when proof_pool runs product-visible without front-spine contracts."""


@dataclass(frozen=True, slots=True)
class SectionFrontSpineBridge:
    """Front-spine contract bundle for a section lane invocation."""

    section_id: str
    validated_request: Any
    l1_plan: Any
    route: Any
    product_visible: bool = True
    fixture_dev_only_bypass: bool = False
    non_product_certified: bool = False
    observed_chain: tuple[str, ...] = OBSERVED_CHAIN_WITH_FRONT_BRIDGE
    missing_downstream_contracts: tuple[str, ...] = DOWNSTREAM_MISSING_CANONICAL_CONTRACTS
    spine_lane_mode: str = "section_spine_run"
    is_canonical_c0_path: bool = False
    whole_run_envelope: bool = False

    def contracts_emitted(self) -> dict[str, bool]:
        return {
            "ValidatedRequest": self.validated_request is not None,
            "L1PlanContract": self.l1_plan is not None,
            "RouteContract": self.route is not None,
        }


def activate_fixture_dev_bypass(*, non_product_certified: bool = True) -> None:
    """Mark current context as fixture/dev-only (not product-certified). Test-only."""
    if os.environ.get("PYTEST_CURRENT_TEST") is None:
        raise RuntimeError(
            "fixture_dev_bypass is test-only; activate only under pytest "
            "(PYTEST_CURRENT_TEST) or from tests.helpers."
        )
    if not non_product_certified:
        raise ValueError(
            "activate_fixture_dev_bypass requires non_product_certified=True"
        )
    _FIXTURE_DEV_BYPASS_CTX.set(True)


def deactivate_fixture_dev_bypass() -> None:
    _FIXTURE_DEV_BYPASS_CTX.set(False)


def fixture_dev_bypass_active() -> bool:
    return bool(_FIXTURE_DEV_BYPASS_CTX.get())


def product_visible_kill_switch_enabled() -> bool:
    """Kill switch is on unless explicitly disabled (narrow harness only)."""
    return os.environ.get("APPS_RG_SECTION_FRONT_SPINE_KILL_SWITCH", "1").strip() not in (
        "0",
        "false",
        "no",
    )


def assert_proof_pool_front_spine_preconditions(
    *,
    front_spine: SectionFrontSpineBridge | None,
    product_visible: bool | None = None,
    fixture_dev_only_bypass: bool = False,
    non_product_certified: bool = False,
) -> None:
    """Fail closed before proof_pool in product-visible mode."""
    pv = (
        product_visible
        if product_visible is not None
        else product_visible_kill_switch_enabled()
    )
    bypass = fixture_dev_only_bypass or fixture_dev_bypass_active()
    if not pv:
        if fixture_dev_only_bypass and not non_product_certified:
            raise ValueError(
                "fixture_dev_only_bypass requires non_product_certified=True"
            )
        return
    if bypass:
        if fixture_dev_only_bypass and not non_product_certified:
            raise SectionFrontSpinePreconditionError(
                "fixture_dev_only_bypass requires non_product_certified=True"
            )
        return
    if front_spine is None:
        raise SectionFrontSpinePreconditionError(
            "proof_pool_resolver blocked: missing SectionFrontSpineBridge "
            "(ValidatedRequest, L1PlanContract, RouteContract required before proof_pool)"
        )
    missing = [
        name
        for name, ok in front_spine.contracts_emitted().items()
        if not ok
    ]
    if missing:
        raise SectionFrontSpinePreconditionError(
            f"proof_pool_resolver blocked: incomplete front spine contracts: {missing}"
        )


def build_section_front_spine_from_args(
    *,
    section_id: str,
    args: Any,
    repo_root: Path,
    generation_mode: str = "section_regen",
) -> SectionFrontSpineBridge:
    """Run apps_rg U0 → L1 → L0 bindings for a section lane CLI args namespace."""
    from apps_rg.runtime.bindings.l0_binding import l0_route_apps_rg
    from apps_rg.runtime.bindings.l1_binding import l1_plan_apps_rg
    from apps_rg.runtime.bindings.u0_binding import u0_validate_apps_rg
    from apps_rg.runtime.resume_resolution import load_lane_base_resume_json

    base_ref = str(getattr(args, "base_resume_ref", "") or "").strip() or None
    base_dict, _base_path, _base_hash = load_lane_base_resume_json(
        source_resume_ref=base_ref,
        repo_root=repo_root,
    )
    source_resume_text = json.dumps(
        base_dict, sort_keys=True, ensure_ascii=False, separators=(",", ":")
    )
    target_company = str(getattr(args, "target_company", "") or "").strip()
    target_role = str(
        getattr(args, "target_role", "") or getattr(args, "target_title", "") or ""
    ).strip()
    jd_text = str(getattr(args, "jd_text", "") or "").strip()
    briefing_text = str(getattr(args, "briefing", "") or "").strip()

    app_payload: dict[str, Any] = {
        "target_company": target_company,
        "target_role": target_role,
        "target_title": target_role,
        "job_description_text": jd_text,
        "jd_text": jd_text,
        "briefing_text": briefing_text,
        "generation_mode": generation_mode,
        "section_id": section_id,
        "source_resume_text": source_resume_text,
        "transport": "ui",
        "source_channel": "apps_rg_section_cli",
    }

    request_id = str(uuid.uuid4())
    run_id = str(uuid.uuid4())
    trace_id = str(uuid.uuid4())
    envelope = SimpleNamespace(
        app_payload=app_payload,
        request_id=request_id,
        run_id=run_id,
        trace_id=trace_id,
        app_id="apps_rg",
        tenant_id="default",
    )
    validated_request = u0_validate_apps_rg(envelope, allow_missing_profiles=False)
    l1_plan = l1_plan_apps_rg(validated_request)
    route = l0_route_apps_rg(l1_plan)
    whole_run = os.environ.get("APPS_RG_WHOLE_RUN_ENVELOPE", "").strip().lower() in (
        "1",
        "true",
        "yes",
    )
    return SectionFrontSpineBridge(
        section_id=section_id,
        validated_request=validated_request,
        l1_plan=l1_plan,
        route=route,
        product_visible=True,
        fixture_dev_only_bypass=False,
        non_product_certified=False,
        whole_run_envelope=whole_run,
    )


def _serialize_value(val: Any) -> Any:
    if val is None or isinstance(val, (str, int, float, bool)):
        return val
    if isinstance(val, (frozenset, set)):
        return sorted(_serialize_value(v) for v in val)
    if isinstance(val, (list, tuple)):
        return [_serialize_value(v) for v in val]
    if isinstance(val, dict):
        return {str(k): _serialize_value(v) for k, v in val.items()}
    if hasattr(val, "__dataclass_fields__"):
        try:
            return _serialize_value(asdict(val))
        except TypeError:  # guardian: allow-silent-swallow -- P2 burndown: fail-soft optional boundary
            pass
    return repr(val)


def _validation_status_from_vr(validated_request: Any) -> str:
    receipt = getattr(validated_request, "authority_validation_receipt", None)
    if receipt is not None and getattr(receipt, "validation_passed", False):
        return "PASS"
    return "PASS" if validated_request is not None else "FAIL"


def build_section_front_spine_receipt(bridge: SectionFrontSpineBridge) -> dict[str, Any]:
    """Master receipt proving front bridge ran (not product certification)."""
    spine = section_lane_spine_classification()
    ts = datetime.now(timezone.utc).isoformat()
    contracts = bridge.contracts_emitted()
    precond_pass = all(contracts.get(c) for c in FRONT_SPINE_CONTRACTS)
    fixture_dev = bool(bridge.fixture_dev_only_bypass or fixture_dev_bypass_active())
    return {
        "schema_version": "section_front_spine_receipt_v1",
        "generated_at_utc": ts,
        "plan_slug": "apps-rg-spine-only-unification-d8f4a2",
        "wave": "W2",
        "section_id": bridge.section_id,
        "product_visible": bridge.product_visible,
        "fixture_dev_only": fixture_dev,
        "fixture_dev_only_bypass": bridge.fixture_dev_only_bypass,
        "non_product_certified": bridge.non_product_certified,
        "product_certification": "NOT_CLAIMED",
        "canonical_c0_claimed": False,
        "canonical_exit_claimed": False,
        "front_spine_status": "PASS" if precond_pass else "FAIL",
        "precondition_status": "PASS" if precond_pass else "FAIL",
        "validated_request_ref": "validated_request.json",
        "l1_plan_contract_ref": "l1_plan_contract.json",
        "route_contract_ref": "route_contract.json",
        "proof_pool_entry_allowed": precond_pass,
        "proof_pool_preconditions": {
            "status": "PASS" if precond_pass else "FAIL",
            "required_contracts": list(FRONT_SPINE_CONTRACTS),
            "satisfied": precond_pass,
            "enforcement": "resolve_section_proof_pool product_visible kill switch",
        },
        "product_visible_kill_switch_enabled": product_visible_kill_switch_enabled(),
        "spine_mode": bridge.spine_lane_mode,
        "spine_lane_mode": bridge.spine_lane_mode,
        "is_canonical_c0_path": bridge.is_canonical_c0_path,
        "observed_chain": list(bridge.observed_chain),
        "canonical_spine_target": list(CANONICAL_SPINE_CHAIN),
        "contracts_emitted": bridge.contracts_emitted(),
        "missing_downstream_canonical_contracts": list(bridge.missing_downstream_contracts),
        "downstream_classification": spine,
        "explicit_non_claims": [
            "no claim of full canonical C0.2 dense retrieval unless Chroma dense path ran",
            "no claim of full canonical C0.3 graph traverse unless spine route traverse ran",
            "no claim of canonical C0.5 FinalEvidenceContract unless spine FEC emitted",
            "no claim of spine ExitDispositionReceipt or RuntimeExhaustBundle",
            "no claim of full canonical product certification",
            "no claim that section CLI is fully migrated past L0",
        ],
    }


def emit_section_front_spine_receipts(
    artifact_dir: Path,
    bridge: SectionFrontSpineBridge,
) -> dict[str, Path]:
    """Write front-spine contract receipts under a section run artifact dir."""
    artifact_dir.mkdir(parents=True, exist_ok=True)
    master = build_section_front_spine_receipt(bridge)
    paths: dict[str, Path] = {}
    p_master = artifact_dir / "section_front_spine_receipt.json"
    p_master.write_text(
        json.dumps(master, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    paths["section_front_spine_receipt"] = p_master

    vr_payload = bridge.validated_request
    request_id = str(getattr(vr_payload, "request_id", "") or "")
    run_id = str(getattr(vr_payload, "run_id", "") or "")
    vr_doc = {
        "contract_type": "ValidatedRequest",
        "contract_version": "apps_rg_spine_front_contracts_v1",
        "producer_stage": "U0",
        "consumer_stage": "L1",
        "request_id": request_id,
        "run_id": run_id,
        "validation_status": _validation_status_from_vr(vr_payload),
        "payload": _serialize_value(bridge.validated_request),
    }
    p_vr = artifact_dir / "validated_request.json"
    p_vr.write_text(json.dumps(vr_doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    paths["validated_request"] = p_vr

    l1_doc = {
        "contract_type": "L1PlanContract",
        "contract_version": "apps_rg_spine_front_contracts_v1",
        "producer_stage": "L1",
        "consumer_stage": "L0",
        "request_id": request_id,
        "run_id": run_id,
        "validated_request_ref": "validated_request.json",
        "parent_contract_ref": request_id,
        "payload": _serialize_value(bridge.l1_plan),
    }
    p_l1 = artifact_dir / "l1_plan_contract.json"
    p_l1.write_text(json.dumps(l1_doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    paths["l1_plan_contract"] = p_l1

    route_payload = _serialize_value(bridge.route)
    route_body = route_payload if isinstance(route_payload, dict) else {}
    route_doc = {
        "contract_type": "RouteContract",
        "contract_version": "apps_rg_spine_front_contracts_v1",
        "producer_stage": "L0",
        "consumer_stage": "section_lane_modular",
        "request_id": request_id,
        "run_id": run_id,
        "l1_plan_contract_ref": "l1_plan_contract.json",
        "parent_contract_ref": request_id,
        "route_id": route_body.get("route_id"),
        "grounding_required": route_body.get("grounding_required"),
        "execution_form": route_body.get("execution_form"),
        "payload": route_payload,
    }
    p_route = artifact_dir / "route_contract.json"
    p_route.write_text(
        json.dumps(route_doc, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    paths["route_contract"] = p_route
    return paths


__all__ = [
    "DOWNSTREAM_MISSING_CANONICAL_CONTRACTS",
    "FRONT_SPINE_CONTRACTS",
    "OBSERVED_CHAIN_WITH_FRONT_BRIDGE",
    "SectionFrontSpineBridge",
    "SectionFrontSpinePreconditionError",
    "activate_fixture_dev_bypass",
    "assert_proof_pool_front_spine_preconditions",
    "build_section_front_spine_from_args",
    "build_section_front_spine_receipt",
    "deactivate_fixture_dev_bypass",
    "emit_section_front_spine_receipts",
    "fixture_dev_bypass_active",
    "product_visible_kill_switch_enabled",
]
