"""L1 cognition binding for the apps_rg `resume_generation` task class.

Per plan apps-rg-runtime-wiring-completion-d4e8a1 §6 W3.P2.

L1 is the SECOND stage of the U0 -> L1 -> L0 -> [C0] -> [PA] -> L2 -> Exit
pipeline. Its job is to consume the U0 ValidatedRequest, read the apps_rg
declarative planning profile (rg_planning_profile.yaml, advisory-only per
AG-RGGOV-6), and emit a typed L1PlanContract that downstream L0/C0/PA/L2
stages consume.

Pattern (matches U0 binding shape):
- Pure function. No state. No I/O beyond reading the profile YAML.
- Profile content is digest-bound — tampering between ingress and core
  consumption is detectable via profile_manifest_digest.
- task_plan / required_capabilities are derived from the profile +
  task_class semantics; the binding owns this mapping.
- grounding_required, model_generation_required, write_authority_present
  flags drive downstream routing decisions (L0 / [C0] / [PA] / L2).

For task_class='resume_generation':
- grounding_required = True  (JD + manual brief feed C0 retrieval)
- model_generation_required = True  (LLM composes the narrative)
- write_authority_present = False  (artifact written to artifacts/ but
  apps_rg never mutates durable state — no UWG/learning writes)
"""
from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path

from agentic_core.runtime.contracts.apps_rg_ingress_payload import ValidatedRequest
from agentic_core.runtime.contracts.l1_plan_contract import L1PlanContract


# L5 certification ref for the L1 binding stage.
APPS_RG_L1_CERT_REF: str = "l1-apps-rg-resume-generation-w3p2"

# Path to the apps_rg planning profile (advisory per AG-RGGOV-6).
# Resolved relative to the repo root at call time.
_PLANNING_PROFILE_RELPATH: str = "apps_rg/profiles/rg_planning_profile.yaml"


# ---------------------------------------------------------------------------
# Task plan / capability derivation for task_class='resume_generation'.
#
# This mapping is the L1 binding's INTERPRETATION of the planning profile.
# It is NOT a runtime directive — it's a declarative description of what
# stages downstream consumers (L0 routing, L2 execution) need to perform
# for this task class. Different task classes (e.g. cover_letter, profile
# review) would have different mappings and live in different bindings.
# ---------------------------------------------------------------------------
_RESUME_GENERATION_TASK_PLAN: tuple[str, ...] = (
    "ingest_inputs",        # JD, manual brief, source resume — already loaded by ingress
    "retrieve_grounding",   # C0: JD chunks + brief evidence anchors
    "compose_prompt",       # PA: assemble system + user prompt from prompt profile
    "generate_narrative",   # L2: LLM call producing structured resume JSON
    "validate_output",      # Exit: schema + style + completeness checks
)

_RESUME_GENERATION_REQUIRED_CAPABILITIES: tuple[str, ...] = (
    "llm.text_generation",       # primary model call
    "retrieval.text_anchor",     # C0 evidence retrieval over JD/brief
    "prompt_assembly.template",  # PA template-driven prompt composition
    "schema_validation.json",    # Exit output validation
)


def _read_profile_digest(repo_root: Path) -> str:
    """Compute sha256 digest of the planning profile bytes for tampering detection.

    Returns hex digest. If the profile file is missing, returns empty string —
    downstream consumers can treat this as the absence of digest binding.
    """
    profile_path = repo_root / _PLANNING_PROFILE_RELPATH
    if not profile_path.exists():
        return ""
    try:
        content_bytes = profile_path.read_bytes()
    except OSError:
        return ""
    return hashlib.sha256(content_bytes).hexdigest()


def _resolve_repo_root() -> Path:
    """Best-effort repo-root resolution.

    Walks up from this file's location to find a directory containing
    `pyproject.toml`. Falls back to four-levels-up if not found.
    """
    here = Path(__file__).resolve()
    for parent in [here.parent, *here.parents]:
        if (parent / "pyproject.toml").exists():
            return parent
    return here.parents[3]


def l1_plan_apps_rg(validated_request: ValidatedRequest) -> L1PlanContract:
    """Emit an L1PlanContract for an apps_rg ValidatedRequest.

    Args:
        validated_request: U0 output carrying the authority-validated payload
                           digest, request/run/trace identity, and task_class.

    Returns:
        L1PlanContract with task_plan, required_capabilities, and routing
        flags (grounding_required / model_generation_required /
        write_authority_present) derived from the apps_rg planning profile
        and the resume_generation task semantics.

    Raises:
        TypeError: if validated_request is not a ValidatedRequest (defensive).
        ValueError: if validated_request.task_class is not 'resume_generation'
                    (this binding only handles that task class — other task
                    classes need their own bindings).
    """
    if not isinstance(validated_request, ValidatedRequest):
        raise TypeError(
            "l1_plan_apps_rg expected ValidatedRequest, got "
            f"{type(validated_request).__name__}"
        )

    if validated_request.task_class != "resume_generation":
        raise ValueError(
            f"l1_plan_apps_rg only handles task_class='resume_generation', got "
            f"{validated_request.task_class!r}. Add a sibling binding for other "
            "task classes (e.g. cover_letter, profile_review)."
        )

    if validated_request.app_id != "apps_rg":
        raise ValueError(
            f"l1_plan_apps_rg expected app_id='apps_rg', got "
            f"{validated_request.app_id!r}"
        )

    profile_digest = _read_profile_digest(_resolve_repo_root())

    return L1PlanContract(
        request_id=validated_request.request_id,
        run_id=validated_request.run_id,
        app_id=validated_request.app_id,
        trace_id=validated_request.trace_id,
        # W1 P1.2: thread identity quad from U0 ValidatedRequest (D6)
        tenant_id=validated_request.tenant_id,
        task_plan=_RESUME_GENERATION_TASK_PLAN,
        required_capabilities=_RESUME_GENERATION_REQUIRED_CAPABILITIES,
        grounding_required=True,
        model_generation_required=True,
        write_authority_present=False,
        profile_manifest_digest=profile_digest,
        planning_timestamp=datetime.now(timezone.utc).isoformat(),
        plan_version="W3.P2",
        l5_certification_ref=APPS_RG_L1_CERT_REF,
    )


__all__ = [
    "APPS_RG_L1_CERT_REF",
    "l1_plan_apps_rg",
]
