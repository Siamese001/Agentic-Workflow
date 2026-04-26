"""Stage 02.1 — Intent Frame & Ambiguity Register.

Doctrine: ``docs/reference/02_L1_Reasoning/02.1_Intent_Frame_and_Ambiguity_Register_detailed.md``.

This module wraps the existing v4/v5
:func:`agentic_core.L1_cognition.reasoning.intent_parser.parse_intent` and
:func:`agentic_core.L1_cognition.enforcement.first_safety_reading.first_safety_reading`
into the v6 :class:`ParsedIntentPacket` packet contract.

It adds:

* A typed :class:`RequestDetailInventory` extracted from the raw request
  text via deterministic regex (no retrieval, no model call).
* A :class:`JobClassFrame` projection of the IntentFrame's work_class.
* The :class:`UserIntentAuthoritySeparationReceipt` boolean record.
* A :class:`ParsedRequestReceipt` with deterministic input/output digests.
* The three OTEL spans for stage 02.1.

The function :func:`parse_intent_frame` is the public entrypoint.

L1 invariants preserved: no retrieval, no route, no execution, no write.
"""

from __future__ import annotations

import re
from typing import Any

from agentic_core.L1_cognition.enforcement.first_safety_reading import (
    first_safety_reading,
)
from agentic_core.L1_cognition.reasoning.intent_parser import parse_intent
from agentic_core.L1_cognition.types.intent_frame_types import (
    ActionRequirement,
    ArtifactRequirement,
)
from agentic_core.L1_cognition.planning.contracts import (
    FirstSafetyAuthorityReading,
    IntentFrameSnapshot,
    JobClassFrame,
    L1ContractViolation,
    ParsedIntentPacket,
    ParsedRequestInput,
    ParsedRequestReceipt,
    RequestDetailInventory,
    freeze_intent_frame_snapshot,
)
from agentic_core.L1_cognition.planning.digests import stable_digest
from agentic_core.L1_cognition.planning.otel import SpanSink, emit_stage_spans

__all__ = ["parse_intent_frame"]


# ---------------------------------------------------------------------------
# Detail inventory regex — deterministic, no IO.
# ---------------------------------------------------------------------------


_FILE_RE = re.compile(
    r"\b[\w./-]+\.(?:md|txt|json|yaml|yml|csv|xlsx?|py|js|ts|html?|pdf|docx?|pptx?|sql|sh|toml|ini|cfg|log)\b",
    re.IGNORECASE,
)
_URL_RE = re.compile(r"https?://[^\s<>]+", re.IGNORECASE)
_DATE_ISO_RE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")
_VERSION_RE = re.compile(r"\bv\d+(?:\.\d+){1,2}\b")
_NUMBER_RE = re.compile(r"\b\d+(?:\.\d+)?\b")
_QUOTED_RE = re.compile(r"\"([^\"]+)\"")


def _extract_inventory(text: str, parsed_input: ParsedRequestInput) -> RequestDetailInventory:
    files: list[str] = []
    urls: list[str] = []
    dates: list[str] = []
    versions: list[str] = []
    numbers: list[str] = []
    exact_terms: list[str] = []

    for m in _FILE_RE.finditer(text):
        v = m.group(0)
        if v not in files:
            files.append(v)
    for m in _URL_RE.finditer(text):
        v = m.group(0)
        if v not in urls:
            urls.append(v)
    for m in _DATE_ISO_RE.finditer(text):
        v = m.group(0)
        if v not in dates:
            dates.append(v)
    for m in _VERSION_RE.finditer(text):
        v = m.group(0)
        if v not in versions:
            versions.append(v)
    for m in _NUMBER_RE.finditer(text):
        v = m.group(0)
        if v not in numbers and v not in dates and not any(v in u for u in urls):
            numbers.append(v)
    for m in _QUOTED_RE.finditer(text):
        v = m.group(1).strip()
        if v and v not in exact_terms:
            exact_terms.append(v)

    direct_quote = bool(exact_terms) or "exact span" in text.lower() or "verbatim" in text.lower()
    citation_needed = "cite" in text.lower() or "citation" in text.lower() or "source" in text.lower()
    artifact_output = (
        "file" in text.lower()
        or "report" in text.lower()
        or "deck" in text.lower()
        or "spreadsheet" in text.lower()
        or "diagram" in text.lower()
    )
    external_action = (
        "send" in text.lower()
        or "publish" in text.lower()
        or "deploy" in text.lower()
        or "execute" in text.lower()
    )

    return RequestDetailInventory(
        entities=tuple(),  # entities are caller-classified upstream
        actors=tuple(),
        systems=tuple(),
        files=tuple(files),
        uploaded_objects=tuple(parsed_input.uploaded_object_refs),
        connectors=tuple(),
        urls=tuple(urls),
        dates=tuple(dates),
        versions=tuple(versions),
        exact_terms=tuple(exact_terms),
        numbers=tuple(numbers),
        variables=tuple(),
        locations=tuple(),
        source_names=tuple(parsed_input.source_handles),
        requested_schema_or_table_shape="",
        requested_ascii_or_diagram_shape="",
        direct_quote_needed=direct_quote,
        citation_needed=citation_needed,
        artifact_output_needed=artifact_output,
        external_action_requested=external_action,
    )


def _project_safety(reading_record: Any, request_id: str) -> FirstSafetyAuthorityReading:
    """Project the v4 FirstSafetyReading into the v6 envelope shape."""
    high_impact_domain = bool(reading_record.has_external_side_effects)
    return FirstSafetyAuthorityReading(
        request_id=request_id,
        read_only_request=bool(reading_record.is_read_only),
        reversible_action_request=bool(reading_record.is_reversible_action),
        durable_write_request=bool(reading_record.is_durable_write),
        external_side_effect_request=bool(reading_record.has_external_side_effects),
        high_impact_domain_hint=high_impact_domain,
        authority_override_attempt=bool(reading_record.attempts_authority_override),
        prompt_injection_like_text_present=bool(reading_record.has_prompt_injection_signal),
        retrieved_content_quoted_by_user=False,
        human_or_tool_output_embedded_by_user=False,
        hitl_may_be_needed=bool(reading_record.requires_hitl_later),
        uwg_may_be_needed=bool(reading_record.requires_uwg_later),
        direct_refusal_may_be_needed=bool(reading_record.recommend_refusal),
        safe_direct_response_possible=bool(reading_record.safest_is_direct_conversation),
        risk_notes=tuple(reading_record.triggers),
    )


def parse_intent_frame(
    parsed_input: ParsedRequestInput,
    *,
    span_sink: SpanSink | None = None,
) -> ParsedIntentPacket:
    """02.1 entrypoint — turn a :class:`ParsedRequestInput` into a packet.

    Stages (mirroring the doctrine PHASE 2 contract):

      1. Validate L1 input provenance (already enforced by the dataclass).
      2. Run the existing :func:`parse_intent` to build an IntentFrame.
      3. Run :func:`first_safety_reading` for the FirstSafetyAuthorityReading.
      4. Build the RequestDetailInventory from the raw request text.
      5. Build the JobClassFrame.
      6. Compose the deterministic ParsedRequestReceipt + packet.
      7. Emit OTEL spans for the stage.

    Returns:
        :class:`ParsedIntentPacket`.
    """
    if not isinstance(parsed_input, ParsedRequestInput):
        raise L1ContractViolation(f"parsed_input must be ParsedRequestInput, got {type(parsed_input)}")

    request_text = parsed_input.normalized_user_payload or ""

    # Step 2: existing v4/v5 IntentFrame.
    intent = parse_intent(request_text, request_id=parsed_input.request_id)

    # Step 3: existing FirstSafetyReading (v4/v5) → v6 envelope.
    safety_v4 = first_safety_reading(intent, request_text=request_text)
    safety_v6 = _project_safety(safety_v4, parsed_input.request_id)

    # Step 4: deterministic detail inventory.
    inventory = _extract_inventory(request_text, parsed_input)

    # Step 5: job-class frame.
    is_artifact_or_action = (
        intent.action_requirement
        in (
            ActionRequirement.REVERSIBLE,
            ActionRequirement.WRITE_PROPOSAL,
            ActionRequirement.HIGH_IMPACT,
        )
    ) or (intent.artifact_requirement != ArtifactRequirement.INLINE)
    job_class = JobClassFrame(
        work_class=intent.work_class.value,
        is_artifact_or_action=is_artifact_or_action,
        is_high_risk=intent.high_risk,
    )

    # Snapshot the IntentFrame for hash stability.
    intent_snapshot = freeze_intent_frame_snapshot(intent, intent_frame_id=f"if::{parsed_input.request_id}")

    # Compute deterministic digests.
    input_digest = stable_digest(parsed_input.to_dict(), prefix="l1.02.1.input")
    output_payload = {
        "intent_frame": intent_snapshot.to_dict(),
        "request_detail_inventory": inventory.to_dict(),
        "job_class_frame": job_class.to_dict(),
        "ambiguity_register": intent.ambiguity.to_dict(),
        "first_safety_authority_reading": safety_v6.to_dict(),
    }
    output_digest = stable_digest(output_payload, prefix="l1.02.1.output")

    receipt = ParsedRequestReceipt(
        receipt_id=f"prr::{parsed_input.request_id}",
        request_id=parsed_input.request_id,
        trace_root=parsed_input.trace_root,
        input_digest=input_digest,
        output_digest=output_digest,
    )

    # User intent / authority separation receipt — explicit booleans.
    separation_receipt = {
        "treats_user_text_as_intent_only": True,
        "does_not_grant_authority": True,
        "treats_quoted_content_as_data": True,
        "policy_decision_deferred_to_l5": True,
    }

    packet = ParsedIntentPacket(
        intent_frame=intent_snapshot,
        request_detail_inventory=inventory,
        job_class_frame=job_class,
        ambiguity_register=intent.ambiguity.to_dict(),
        first_safety_authority_reading=safety_v6,
        parsed_request_receipt=receipt,
        user_intent_authority_separation_receipt=separation_receipt,
        policy_hash_observed=parsed_input.policy_hash_observed,
        instruction_hash_observed=parsed_input.instruction_hash_observed,
        source_envelope_id=parsed_input.source_envelope_id,
    )

    # Step 7: emit OTEL spans.
    emit_stage_spans(
        stage="02.1",
        request_id=parsed_input.request_id,
        trace_root=parsed_input.trace_root,
        policy_hash_observed=parsed_input.policy_hash_observed,
        instruction_hash_observed=parsed_input.instruction_hash_observed,
        input_digest=input_digest,
        output_digest=output_digest,
        span_sink=span_sink,
        extra={"work_class": intent.work_class.value},
    )

    return packet
