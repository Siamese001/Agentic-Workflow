"""L1 cognition binding for the apps_rg `resume_generation` task class.

Per plan apps-rg-runtime-wiring-completion-d4e8a1 §6 W3.P2 (initial)
+   plan apps-rg-app-payload-consumption-wiring-b3a449 W2 (AG-2 — app_payload
   consumption wiring).

L1 is the SECOND stage of the U0 -> L1 -> L0 -> [C0] -> [PA] -> L2 -> Exit
pipeline. Its job is to consume the U0 ValidatedRequest, read the apps_rg
declarative planning profile (rg_planning_profile.yaml, advisory-only per
AG-RGGOV-6), and emit a typed L1PlanContract that downstream L0/C0/PA/L2
stages consume.

AG-2 invariant: L1 reads `validated_request.app_payload` (not envelope.payload)
and surfaces five projection mappings on `L1PlanContract`:
    - task_spec — generation_mode + capability_requirements
    - query_spec — jd_hash + resume_hash + target tuple
    - support_expectation — quality thresholds + provenance/fact-check booleans
    - output_expectation — formats + provenance_required + fact_checked_required
    - policy_refs — manifest_digest + 5 ref strings (prompt/hitl/l0/spec/thresholds)

Downstream stages (L0, C0, PA) consume these projections WITHOUT reaching
back to the legacy `AppsRgIngressPayload`.

Pattern (matches U0 binding shape):
- Pure function. No state. No I/O beyond reading the profile YAML.
- Profile content is digest-bound — tampering between ingress and core
  consumption is detectable via profile_manifest_digest.
- task_plan / required_capabilities are derived from the profile +
  task_class semantics; the binding owns this mapping.
- grounding_required, model_generation_required, write_authority_present
  flags drive downstream routing decisions (L0 / [C0] / [PA] / L2).

For task_class='resume_generation':
- grounding_required derived from app_payload generation_mode (true unless
  generation_mode in {generate_scratch, healing_fact_check}).
- model_generation_required = True  (LLM composes the narrative)
- write_authority_present = False  (artifact written to artifacts/ but
  apps_rg never mutates durable state — no UWG/learning writes)
"""
from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from agentic_core.runtime.contracts.apps_rg_ingress_payload import ValidatedRequest
from agentic_core.runtime.contracts.l1_plan_contract import L1PlanContract


# L5 certification ref for the L1 binding stage. Updated for AG-2 to record
# that L1 now consumes app_payload-derived projections.
APPS_RG_L1_CERT_REF: str = "l1-apps-rg-resume-generation-app-payload-b3a449"

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

# AG-2: generation modes that DO NOT require evidence grounding.
# generate_scratch — invents from target_company/target_role only
# healing_fact_check — reads existing resume; no JD ingest
_GENERATION_MODES_WITHOUT_GROUNDING: frozenset[str] = frozenset({
    "generate_scratch",
    "healing_fact_check",
})

# AG-2: required app_payload top-level keys. Missing keys raise ValueError so
# the binding fails closed before producing an under-specified L1PlanContract.
_REQUIRED_APP_PAYLOAD_KEYS: tuple[str, ...] = (
    "transport",
    "target",
    "generation_mode",
    "jd_payload",
    "resume_payload",
    "profile_manifest",
    "quality_thresholds",
    "output_requirements",
    "provenance_requirements",
)


def _build_app_payload_projections(
    app_payload: "Mapping[str, Any]",
) -> tuple[
    "Mapping[str, Any]",  # task_spec
    "Mapping[str, Any]",  # query_spec
    "Mapping[str, Any]",  # support_expectation
    "Mapping[str, Any]",  # output_expectation
    "Mapping[str, str]",  # policy_refs
    bool,                  # grounding_required (derived from generation_mode)
]:
    """Project ValidatedRequest.app_payload into the five L1PlanContract
    projections + the derived grounding_required flag.

    AG-2 (apps-rg-app-payload-consumption-wiring-b3a449 W2). All projections
    are read-only views of app_payload — L1 NEVER mutates app_payload.

    Raises:
        ValueError: when a required app_payload key is missing or empty;
            this is the fail-closed signal preventing L1 from producing an
            under-specified plan.
    """

    missing = [k for k in _REQUIRED_APP_PAYLOAD_KEYS if k not in app_payload]
    if missing:
        raise ValueError(
            f"l1_plan_apps_rg: app_payload missing required keys: {missing}. "
            "AG-2 invariant requires the U0 reflection harness to populate "
            "the full apps_rg ingress contract — was apps_rg_u0_adapt skipped?"
        )

    target = app_payload["target"]
    jd = app_payload["jd_payload"]
    resume = app_payload["resume_payload"]
    manifest = app_payload["profile_manifest"]
    thresholds = app_payload["quality_thresholds"]
    output_req = app_payload["output_requirements"]
    prov_req = app_payload["provenance_requirements"]
    # Pydantic may carry generation_mode as a GenerationMode enum; coerce to
    # its string value so the projection is JSON-serialisable and downstream
    # consumers don't need to import the enum to compare.
    generation_mode_raw = app_payload["generation_mode"]
    generation_mode = (
        generation_mode_raw.value
        if hasattr(generation_mode_raw, "value")
        else str(generation_mode_raw)
    )
    capability_requirements = tuple(app_payload.get("capability_requirements", ()))

    task_spec: dict[str, Any] = {
        "generation_mode": generation_mode,
        "capability_requirements": capability_requirements,
        "task_class": app_payload["transport"]["task_class"],
    }
    query_spec: dict[str, Any] = {
        "jd_hash": jd.get("jd_hash", ""),
        "resume_hash": resume.get("resume_hash", ""),
        "target": {
            "company": target.get("company", ""),
            "role": target.get("role", ""),
            "level": target.get("level", ""),
        },
    }
    support_expectation: dict[str, Any] = {
        "min_quality": thresholds.get("min_quality", 0.0),
        "min_ats": thresholds.get("min_ats", 0),
        "word_min": thresholds.get("word_min", 0),
        "word_max": thresholds.get("word_max", 0),
        "provenance_required": bool(output_req.get("provenance_required", False)),
        "fact_checked_required": bool(output_req.get("fact_checked_required", False)),
        "per_bullet_required": bool(prov_req.get("per_bullet_required", False)),
        "source_quote_required": bool(prov_req.get("source_quote_required", False)),
    }
    # output_requirements.formats is a tuple in the contract; preserve its order.
    formats = output_req.get("formats", ())
    if not isinstance(formats, (list, tuple)):
        formats = (formats,) if formats else ()
    output_expectation: dict[str, Any] = {
        "formats": tuple(formats),
        "provenance_required": bool(output_req.get("provenance_required", False)),
        "fact_checked_required": bool(output_req.get("fact_checked_required", False)),
    }
    policy_refs: dict[str, str] = {
        "manifest_digest": str(manifest.get("manifest_digest", "")),
        "prompt_registry_ref": str(manifest.get("prompt_registry_ref", "")),
        "hitl_policy_ref": str(manifest.get("hitl_policy_ref", "")),
        "l0_policy_ref": str(manifest.get("l0_policy_ref", "")),
        "agent_spec_ref": str(manifest.get("agent_spec_ref", "")),
        "thresholds_ref": str(manifest.get("thresholds_ref", "")),
    }

    grounding_required = generation_mode not in _GENERATION_MODES_WITHOUT_GROUNDING

    return (
        task_spec,
        query_spec,
        support_expectation,
        output_expectation,
        policy_refs,
        grounding_required,
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

    # AG-2: read app_payload (populated by U0 reflection harness) and build
    # the five projections that downstream stages (L0/C0/PA) consume.
    # Failure to read app_payload raises ValueError BEFORE we construct the
    # L1PlanContract — no under-specified plan can leak past L1.
    (
        task_spec,
        query_spec,
        support_expectation,
        output_expectation,
        policy_refs,
        grounding_required_from_payload,
    ) = _build_app_payload_projections(validated_request.app_payload)

    return L1PlanContract(
        request_id=validated_request.request_id,
        run_id=validated_request.run_id,
        app_id=validated_request.app_id,
        trace_id=validated_request.trace_id,
        # W1 P1.2: thread identity quad from U0 ValidatedRequest (D6)
        tenant_id=validated_request.tenant_id,
        # W2: thread target_level for L0 variant routing (DS-3)
        target_level=validated_request.target_level,
        task_plan=_RESUME_GENERATION_TASK_PLAN,
        required_capabilities=_RESUME_GENERATION_REQUIRED_CAPABILITIES,
        # AG-2: grounding_required is now driven by app_payload generation_mode,
        # not hard-coded. generate_scratch + healing_fact_check skip C0.
        grounding_required=grounding_required_from_payload,
        model_generation_required=True,
        write_authority_present=False,
        profile_manifest_digest=profile_digest,
        # AG-2: surface the five projections so L0/C0/PA can consume them
        # without ever touching the legacy AppsRgIngressPayload.
        task_spec=task_spec,
        query_spec=query_spec,
        support_expectation=support_expectation,
        output_expectation=output_expectation,
        policy_refs=policy_refs,
        # AG-2: thread the U0 replay_key forward so the L1 plan is replay-bound.
        replay_key=validated_request.replay_key,
        planning_timestamp=datetime.now(timezone.utc).isoformat(),
        schema_version="AG-2.b3a449",
        l5_certification_ref=APPS_RG_L1_CERT_REF,
    )


__all__ = [
    "APPS_RG_L1_CERT_REF",
    "l1_plan_apps_rg",
]
