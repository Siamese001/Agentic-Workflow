"""L0 routing binding for the apps_rg `resume_generation` task class.

Per plan apps-rg-runtime-wiring-completion-d4e8a1 §6 W3.P3.

L0 is the THIRD stage of the U0 -> L1 -> L0 -> [C0] -> [PA] -> L2 -> Exit
pipeline. Its job is to consume the L1 plan, read the apps_rg declarative
route profile (route_profiles.yaml), and emit a typed RouteContract that
downstream C0/PA/L2 stages consume.

Routing decision for task_class='resume_generation':
- route_id = "rg.resume_generation.default" (single-step path)
- l3_required = False (managed-workflow / L3 DAG path deferred per
  plan §3 non-goal: SINGLE_STEP only this iteration)
- Pass-through of L1 flags: grounding_required, model_generation_required,
  write_authority_present

The route profile YAML lists three allowed_route_ids (default / executive /
short_form). Variant selection (e.g. executive for senior+ levels) is a
future optimization and would consume target_level from the original
payload — that requires either a profile-aware L1 plan or passing the
envelope alongside. Out of scope for W3.P3.
"""
from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path

from agentic_core.runtime.contracts.l1_plan_contract import L1PlanContract
from agentic_core.runtime.contracts.route_contract import RouteContract


APPS_RG_L0_CERT_REF: str = "l0-apps-rg-resume-generation-w3p3"
APPS_RG_DEFAULT_ROUTE_ID: str = "rg.resume_generation.default"
_ROUTE_PROFILE_RELPATH: str = "apps_rg/config/domain_contract/route_profiles.yaml"


def _read_route_profile_digest(repo_root: Path) -> str:
    """Compute sha256 digest of the route profile bytes."""
    profile_path = repo_root / _ROUTE_PROFILE_RELPATH
    if not profile_path.exists():
        return ""
    try:
        return hashlib.sha256(profile_path.read_bytes()).hexdigest()
    except OSError:
        return ""


def _resolve_repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in [here.parent, *here.parents]:
        if (parent / "pyproject.toml").exists():
            return parent
    return here.parents[3]


def _build_reason_codes(l1_plan: L1PlanContract) -> tuple[str, ...]:
    """Build human-readable reason codes for the routing decision."""
    codes: list[str] = [
        f"task_class=resume_generation",
        f"route_id={APPS_RG_DEFAULT_ROUTE_ID}",
        "execution_form=single_step",
        f"l3_required=false (managed_workflow path deferred)",
    ]
    if l1_plan.grounding_required:
        codes.append("grounding_required=true (C0 retrieval will fire)")
    if l1_plan.model_generation_required:
        codes.append("model_generation_required=true (L2 LLM call will fire)")
    if not l1_plan.write_authority_present:
        codes.append("write_authority_present=false (no UWG/learning writes)")
    codes.append(
        f"capabilities_count={len(l1_plan.required_capabilities)}: "
        + ",".join(l1_plan.required_capabilities)
    )
    return tuple(codes)


def l0_route_apps_rg(l1_plan: L1PlanContract) -> RouteContract:
    """Emit a RouteContract from an apps_rg L1 plan.

    Args:
        l1_plan: L1PlanContract output of l1_plan_apps_rg.

    Returns:
        RouteContract with route_id, l3_required, and routing flags.

    Raises:
        TypeError: if l1_plan is not an L1PlanContract.
        ValueError: if l1_plan.app_id != 'apps_rg'.
    """
    if not isinstance(l1_plan, L1PlanContract):
        raise TypeError(
            f"l0_route_apps_rg expected L1PlanContract, got {type(l1_plan).__name__}"
        )

    if l1_plan.app_id != "apps_rg":
        raise ValueError(
            f"l0_route_apps_rg expected app_id='apps_rg', got {l1_plan.app_id!r}"
        )

    # Optional digest binding for tampering detection.
    _ = _read_route_profile_digest(_resolve_repo_root())  # captured for parity

    return RouteContract(
        request_id=l1_plan.request_id,
        run_id=l1_plan.run_id,
        app_id=l1_plan.app_id,
        trace_id=l1_plan.trace_id,
        # W1 P1.2: thread identity quad from L1PlanContract (D6)
        tenant_id=l1_plan.tenant_id,
        route_id=APPS_RG_DEFAULT_ROUTE_ID,
        l3_required=False,
        grounding_required=l1_plan.grounding_required,
        model_generation_required=l1_plan.model_generation_required,
        write_authority_present=l1_plan.write_authority_present,
        # W2 P2.1: capability/sandbox/egress — apps_rg is read-only, single vllm model (D11=default-empty)
        sandbox_required=False,
        egress_policy_ref="egress-policy:vllm-only",
        allowed_models=("Qwen/Qwen2.5-32B-Instruct-AWQ",),
        allowed_tools=(),
        allowed_networks=("localhost:8000",),
        allowed_file_roots=("artifacts/apps_rg/",),
        reason_codes=_build_reason_codes(l1_plan),
        routing_timestamp=datetime.now(timezone.utc).isoformat(),
        route_version="W3.P3",
        l5_certification_ref=APPS_RG_L0_CERT_REF,
    )


__all__ = [
    "APPS_RG_L0_CERT_REF",
    "APPS_RG_DEFAULT_ROUTE_ID",
    "l0_route_apps_rg",
]
