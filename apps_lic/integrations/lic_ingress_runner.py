"""Ingress-wired runner factory for ``apps_lic`` (Life-Insurance / Campaign).

Closes W8.3. See ``agentic_core/runtime/entry/app_ingress_runner.py``.

W5 wiring (plan apps-lic-u0-runtime-package-complete-f8e2a1, P5.1):
The ``parse`` callable now invokes ``u0_validate_apps_lic`` so every request
enters the pipeline as a ``ValidatedRequest`` carrying the full
``runtime_customization_package`` inside ``app_payload``.  Downstream
dispatch (L1 → L0 → C0 → PA → L2 → Exit) receives a typed, validated
contract — not a raw dict.
"""

from __future__ import annotations

from typing import Any, Callable

from agentic_core.L5_safety.enforcement.ingress import IngressEnvelopeCheck
from agentic_core.runtime.contracts.apps_lic_ingress_payload import AppsLicRequestEnvelope
from agentic_core.runtime.contracts.apps_rg_ingress_payload import ValidatedRequest
from agentic_core.runtime.entry.app_ingress_runner import AppIngressRunner
from agentic_core.runtime.entry.u0_apps_lic_binding import u0_validate_apps_lic

LIC_REQUIRED_FIELDS: tuple[str, ...] = ("channel", "audience_segment", "request_type")
"""Minimum payload keys checked by AppIngressRunner before parse is invoked.

These map to the top-level fields on ``AppsLicIngressPayload`` that must be
non-empty strings for the request to be dispatchable.  Missing fields surface
as ``ClarificationRequired`` rather than a hard validation error so the caller
can recover gracefully.
"""


def _parse_lic_envelope(payload: dict[str, Any]) -> ValidatedRequest | None:
    """Convert a raw payload dict → ValidatedRequest via U0.

    Constructs an ``AppsLicRequestEnvelope`` from the dict produced by
    ``AppIngressRunner`` (either from a raw CLI payload or from the
    stamped-envelope path), then delegates to ``u0_validate_apps_lic``.

    Returns None on any construction or adapter error so AppIngressRunner
    surfaces a ``ClarificationRequired`` instead of propagating a hard
    exception to the HTTP/chat caller.
    """
    try:
        from agentic_core.runtime.contracts.apps_lic_ingress_payload import (
            AppsLicIngressPayload,
        )

        ingress = AppsLicIngressPayload(
            app_id=payload.get("app_id", "apps_lic"),
            task_class=payload.get("task_class", "outreach_message"),
            request_type=payload.get("request_type", "outreach_draft"),
            campaign_objective=payload.get("campaign_objective"),
            channel=payload.get("channel", "email"),
            audience_segment=payload.get("audience_segment"),
            action_required=payload.get("action_required", "draft_and_cert"),
            workflow_required=payload.get("workflow_required", "managed_workflow_hop"),
            grounding_required=bool(payload.get("grounding_required", True)),
            side_effect_class=payload.get("side_effect_class", "read_only"),
            lead_profile=payload.get("lead_profile") or {},
            lead_ref=payload.get("lead_ref"),
            sender_profile=payload.get("sender_profile") or {},
            sender_ref=payload.get("sender_ref"),
            company_profile=payload.get("company_profile") or {},
            company_ref=payload.get("company_ref"),
            personalization_inputs=payload.get("personalization_inputs") or {},
            generation_hints=payload.get("generation_hints") or {},
            tone_constraints=payload.get("tone_constraints") or {},
            required_output_format=payload.get("required_output_format") or {},
            research_requirements=payload.get("research_requirements") or {},
            routing_policy=payload.get("routing_policy") or {},
            validation_policy=payload.get("validation_policy") or {},
            gate_decision_policy=payload.get("gate_decision_policy") or {},
            qa_report_requirement=payload.get("qa_report_requirement") or {},
            integration_target=payload.get("integration_target"),
            forbidden_send_modes=tuple(
                payload.get("forbidden_send_modes") or ("send_now", "auto_send", "connector_send")
            ),
            hitl_policy=payload.get("hitl_policy") or {},
            pii_policy=payload.get("pii_policy") or {},
            governance_shield_policy=payload.get("governance_shield_policy") or {},
            antipattern_policy=payload.get("antipattern_policy") or {},
            source_lineage_requirements=payload.get("source_lineage_requirements") or {},
            ab_test_profile=payload.get("ab_test_profile"),
            learning_profile_ref=payload.get("learning_profile_ref"),
            replay_refs=tuple(payload.get("replay_refs") or ()),
            audit_refs=tuple(payload.get("audit_refs") or ()),
            idempotency_key=payload.get("idempotency_key"),
            payload_digest=payload.get("payload_digest") or "",
        )
        envelope = AppsLicRequestEnvelope(
            payload=ingress,
            request_id=payload.get("request_id") or "",
            run_id=payload.get("run_id") or "",
            tenant_id=payload.get("tenant_id") or "apps_lic",
            trace_id=payload.get("trace_id") or "",
            submitted_at=payload.get("submitted_at") or "",
        )
        return u0_validate_apps_lic(envelope)
    except Exception:  # noqa: BLE001  # parse failures surface as ClarificationRequired
        return None


def make_lic_ingress_runner(
    dispatch: Callable[[ValidatedRequest], Any],
    *,
    gate: IngressEnvelopeCheck | None = None,
) -> AppIngressRunner:
    """Create an AppIngressRunner wired for apps_lic outreach_message requests.

    The ``parse`` callable converts a raw payload dict into a ``ValidatedRequest``
    via U0 (``u0_validate_apps_lic``).  The ``runtime_customization_package``
    carried inside ``ValidatedRequest.app_payload`` is therefore available to
    every downstream layer binding (L1 → L0 → C0 → PA → L2 → Exit) without
    any additional extraction step.

    Args:
        dispatch: Callable that receives a ``ValidatedRequest`` and returns the
            domain result.  Typically ``u0_validate_apps_lic``-downstream
            binding chain assembled by apps_lic/__main__.py or a test harness.
        gate: Optional ``IngressEnvelopeCheck`` instance; defaults to a fresh
            one when omitted.
    """
    return AppIngressRunner(
        dispatch=dispatch,
        parse=_parse_lic_envelope,
        required_fields=LIC_REQUIRED_FIELDS,
        gate=gate,
    )


__all__ = ["LIC_REQUIRED_FIELDS", "make_lic_ingress_runner"]


# ----------------------------------------------------------------------
# OTEL coverage — module-load emit per check_apps_otel_coverage.py.
# Phase A of W-OTEL waves: structural wiring at import time.
# Phase B (per-method spans on execute() paths) is tracked separately.
# Pattern matches lifecycle_trace_contract.py and apps_research/engines.
# ----------------------------------------------------------------------
from agentic_core.runtime.contracts.lifecycle_trace_contract import (  # noqa: E402
    _emit_records_telemetry_event,
)

_emit_records_telemetry_event("p4", 'apps_lic.integrations.lic_ingress_runner', "module_loaded")
