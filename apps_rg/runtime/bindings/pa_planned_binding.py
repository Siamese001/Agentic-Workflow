"""Verified L1-plan boundary for apps_rg prompt assembly.

PA remains prompt-assembly authority. This wrapper verifies the immutable L1
capsule before assembly and requires the emitted prompt artifact to carry the
same planning lineage in its component hashes and slot lineage.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

from agentic_core.runtime.contracts.apps_rg_ingress_payload import ValidatedRequest
from agentic_core.runtime.contracts.compiled_prompt_artifact import CompiledPromptArtifact
from agentic_core.runtime.contracts.final_evidence_contract import FinalEvidenceContract
from agentic_core.runtime.contracts.l1_plan_contract import L1PlanContract
from agentic_core.runtime.contracts.route_contract import RouteContract
from apps_rg.runtime.bindings.l1_planning_capsule import (
    PlanningCapsuleIntegrityError,
    extract_verified_planning_capsule,
)
from apps_rg.runtime.bindings.pa_binding import pa_compose_apps_rg


def _sha256_json(payload: Any) -> str:
    canonical = json.dumps(payload, sort_keys=True, default=str)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def pa_compose_apps_rg_planned(
    route: RouteContract,
    plan: L1PlanContract,
    fec: FinalEvidenceContract,
    validated_request: ValidatedRequest,
) -> CompiledPromptArtifact:
    """Verify L1 planning integrity, assemble PA, and verify plan consumption."""

    capsule, _verification = extract_verified_planning_capsule(plan, required=True)
    artifact = pa_compose_apps_rg(route, plan, fec, validated_request)
    component_hashes = dict(artifact.component_hash_map or {})
    expected = {
        "l1_planning_capsule": _sha256_json(capsule),
        "l1_prompt_plan": _sha256_json(capsule.get("prompt_plan", [])),
        "l1_completion_criteria": _sha256_json(
            capsule.get("completion_criteria", [])
        ),
        "l1_cognition_plan_requested": _sha256_json(
            capsule.get("cognition_plan", [])
        ),
    }
    missing = sorted(key for key in expected if key not in component_hashes)
    mismatched = sorted(
        key
        for key, digest in expected.items()
        if component_hashes.get(key) not in (None, digest)
    )
    if missing or mismatched:
        raise PlanningCapsuleIntegrityError(
            "PA artifact did not preserve verified L1 planning component hashes: "
            f"missing={missing} mismatched={mismatched}"
        )
    lineage = str(
        (artifact.slot_lineage_map or {}).get("l1_planning_capsule") or ""
    )
    if "L1_PLAN_PROJECTIONS" not in lineage:
        raise PlanningCapsuleIntegrityError(
            "PA artifact is missing L1 planning capsule slot lineage"
        )
    return artifact


__all__ = ["pa_compose_apps_rg_planned"]
