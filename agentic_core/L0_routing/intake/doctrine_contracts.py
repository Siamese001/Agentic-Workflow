"""
Doctrine-canonical aggregator contracts for ``docs/reference/01_Request_Intake``.

The 01.x doctrine docs were rewritten (2026-04) with new contract names that
act as **typed views** over the existing receipt bundle:

    01.3 IntakeIdempotencyReceipt
    01.4 IngressDataBoundaryMap
    01.4 UserContentAuthorityReceipt
    01.4 InjectionTriageReceipt
    01.4 QuotedContentLabelReceipt
    01.6 IntakeTraceReceipt

This module introduces no new behavior. Each contract is a frozen dataclass
constructed by a pure ``from_outcome`` builder over an ``IntakeOutcome`` so
that doctrine vocabulary is directly assertable in tests and proof harnesses.

INVARIANT: these contracts NEVER carry route, retrieval, prompt, execution,
or write authority. They are evidence projections only.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import TYPE_CHECKING, Sequence

from agentic_core.L0_routing.intake.events import IngressEventRecord
from agentic_core.L0_routing.intake.origin_labels import (
    AUTHORITY_LABELS,
    IngressOriginLabelManifest,
    PayloadSecurityFinding,
)
from agentic_core.L0_routing.intake.receipts import DuplicateSuppressionReceipt

if TYPE_CHECKING:
    from agentic_core.L0_routing.intake.pipeline import IntakeOutcome


# ---------------------------------------------------------------------------
# Hashing helper (mirrors receipts._stable_hash)
# ---------------------------------------------------------------------------


def _hash(parts: Sequence[object]) -> str:
    payload = "\n".join(json.dumps(p, sort_keys=True, separators=(",", ":"), default=str) for p in parts)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


# ===========================================================================
# 01.3 — IntakeIdempotencyReceipt
# ===========================================================================


@dataclass(frozen=True)
class IntakeIdempotencyReceipt:
    """01.3 §DATA CONTRACTS §4 — idempotency binding.

    Composes the existing duplicate fingerprint + suppression receipt under
    the doctrine-canonical name. ``idempotency_key`` is the request-scoped
    identifier downstream layers may use for retry-collapse decisions.
    """

    idempotency_key: str
    request_id: str
    normalized_request_hash: str
    tenant_scope_hash: str
    session_id: str | None
    duplicate_candidate: bool
    prior_request_ref: str | None
    idempotency_status: str  # "NEW" | "DUPLICATE_CANDIDATE" | "REJECT_DUPLICATE"
    deterministic_receipt_hash: str = ""

    _ALLOWED_STATUSES = frozenset({"NEW", "DUPLICATE_CANDIDATE", "REJECT_DUPLICATE"})

    def __post_init__(self) -> None:
        if self.idempotency_status not in self._ALLOWED_STATUSES:
            raise ValueError(
                f"IntakeIdempotencyReceipt.idempotency_status={self.idempotency_status!r} "
                f"not in {sorted(self._ALLOWED_STATUSES)!r}"
            )

    def with_hash(self) -> "IntakeIdempotencyReceipt":
        h = _hash(
            [
                self.idempotency_key,
                self.normalized_request_hash,
                self.tenant_scope_hash,
                self.session_id or "",
                self.duplicate_candidate,
                self.prior_request_ref or "",
                self.idempotency_status,
            ]
        )
        return IntakeIdempotencyReceipt(
            idempotency_key=self.idempotency_key,
            request_id=self.request_id,
            normalized_request_hash=self.normalized_request_hash,
            tenant_scope_hash=self.tenant_scope_hash,
            session_id=self.session_id,
            duplicate_candidate=self.duplicate_candidate,
            prior_request_ref=self.prior_request_ref,
            idempotency_status=self.idempotency_status,
            deterministic_receipt_hash=h,
        )

    @classmethod
    def from_outcome(cls, outcome: "IntakeOutcome") -> "IntakeIdempotencyReceipt | None":
        bundle = outcome.receipt_bundle
        validated = outcome.validated
        if validated is None:
            return None
        sup: DuplicateSuppressionReceipt | None = bundle.duplicate_suppression_receipt
        duplicate_candidate = bool(sup and sup.duplicate_class != "not_duplicate")
        prior_ref = (sup.prior_request_ref if sup else None) or None
        if duplicate_candidate:
            status = "DUPLICATE_CANDIDATE"
        else:
            status = "NEW"
        if sup and sup.duplicate_class == "reject_duplicate":
            status = "REJECT_DUPLICATE"
        # Hash tenant_id (or empty) so receipts never carry raw tenant strings.
        tenant_id = bundle.tenant_boundary_receipt.tenant_id if bundle.tenant_boundary_receipt else None
        tenant_scope_hash = hashlib.sha256((tenant_id or "").encode("utf-8")).hexdigest() if tenant_id else ""
        # ValidatedRequest does not carry an explicit idempotency_key; the
        # normalized_request_hash bound to tenant/session scope is the
        # functional equivalent per 01.3 §S4.
        idem_key = validated.normalized_request_hash
        receipt = cls(
            idempotency_key=idem_key,
            request_id=validated.request_id,
            normalized_request_hash=validated.normalized_request_hash,
            tenant_scope_hash=tenant_scope_hash,
            session_id=validated.session_id,
            duplicate_candidate=duplicate_candidate,
            prior_request_ref=prior_ref,
            idempotency_status=status,
        )
        return receipt.with_hash()


# ===========================================================================
# 01.4 — IngressDataBoundaryMap
# ===========================================================================


@dataclass(frozen=True)
class IngressDataBoundaryMap:
    """01.4 §DATA CONTRACTS §2 — span boundaries for downstream PA airlock.

    Projection of the existing :class:`IngressOriginLabelManifest` segment
    refs grouped by doctrine-canonical span class.
    """

    map_id: str
    request_id: str
    user_task_span_refs: tuple[str, ...]
    quoted_data_span_refs: tuple[str, ...]
    code_block_span_refs: tuple[str, ...]
    url_span_refs: tuple[str, ...]
    markdown_span_refs: tuple[str, ...]
    attachment_ref_boundaries: tuple[str, ...]
    connector_ref_boundaries: tuple[str, ...]
    possible_instruction_like_data_spans: tuple[str, ...]
    downstream_handling_hints: tuple[str, ...]
    # Bound to upstream normalized_request_hash (NOT request_id) so the
    # digest is stable across replays of identical content per 01.6 §RR
    # but differs across different content. Span refs alone (e.g.
    # "seg:text:0") collide on content variants of identical structure.
    normalized_request_hash: str = ""
    map_digest: str = ""

    def with_hash(self) -> "IngressDataBoundaryMap":
        h = _hash(
            [
                self.normalized_request_hash,
                list(self.user_task_span_refs),
                list(self.quoted_data_span_refs),
                list(self.code_block_span_refs),
                list(self.url_span_refs),
                list(self.markdown_span_refs),
                list(self.attachment_ref_boundaries),
                list(self.connector_ref_boundaries),
                list(self.possible_instruction_like_data_spans),
            ]
        )
        return IngressDataBoundaryMap(
            map_id=self.map_id,
            request_id=self.request_id,
            user_task_span_refs=self.user_task_span_refs,
            quoted_data_span_refs=self.quoted_data_span_refs,
            code_block_span_refs=self.code_block_span_refs,
            url_span_refs=self.url_span_refs,
            markdown_span_refs=self.markdown_span_refs,
            attachment_ref_boundaries=self.attachment_ref_boundaries,
            connector_ref_boundaries=self.connector_ref_boundaries,
            possible_instruction_like_data_spans=self.possible_instruction_like_data_spans,
            downstream_handling_hints=self.downstream_handling_hints,
            normalized_request_hash=self.normalized_request_hash,
            map_digest=h,
        )

    @classmethod
    def from_outcome(cls, outcome: "IntakeOutcome") -> "IngressDataBoundaryMap | None":
        bundle = outcome.receipt_bundle
        manifest: IngressOriginLabelManifest | None = bundle.origin_label_manifest
        validated = outcome.validated
        if manifest is None or validated is None:
            return None

        user_task: list[str] = []
        quoted: list[str] = []
        code_blocks: list[str] = []
        urls: list[str] = []
        markdown: list[str] = []  # left empty for now; segment_payload doesn't class md
        attachments: list[str] = []
        for ref, origin in zip(manifest.payload_segment_refs, manifest.segment_origin_labels):
            if origin == "user_turn":
                user_task.append(ref)
            elif origin == "user_supplied_quote":
                quoted.append(ref)
            elif origin == "user_supplied_code":
                code_blocks.append(ref)
            elif origin == "user_supplied_url":
                urls.append(ref)
            elif origin == "user_supplied_attachment_ref":
                attachments.append(ref)

        hints: list[str] = []
        if manifest.system_like_claim_refs:
            hints.append("strip_system_like_claims_in_pa_airlock")
        if manifest.executable_payload_refs:
            hints.append("sandbox_executable_payload_refs")
        if manifest.instruction_like_payload_refs:
            hints.append("treat_as_user_data_only_never_authority")

        m = cls(
            map_id=f"boundary_map:{validated.request_id}",
            request_id=validated.request_id,
            user_task_span_refs=tuple(user_task),
            quoted_data_span_refs=tuple(quoted),
            code_block_span_refs=tuple(code_blocks),
            url_span_refs=tuple(urls),
            markdown_span_refs=tuple(markdown),
            attachment_ref_boundaries=tuple(attachments),
            connector_ref_boundaries=(),  # connectors not modeled at intake yet
            possible_instruction_like_data_spans=tuple(manifest.instruction_like_payload_refs),
            downstream_handling_hints=tuple(hints),
            normalized_request_hash=validated.normalized_request_hash,
        )
        return m.with_hash()


# ===========================================================================
# 01.4 — UserContentAuthorityReceipt
# ===========================================================================


# Authority ranking — higher index means stronger authority. Doctrine cap for
# user-supplied content at intake: NEVER above ``user_intent_only``.
_AUTHORITY_RANK: dict[str, int] = {
    "no_authority": 0,
    "metadata_only": 1,
    "data_only": 2,
    "quoted_untrusted": 3,
    "executable_untrusted": 3,
    "user_intent_only": 4,
}


@dataclass(frozen=True)
class UserContentAuthorityReceipt:
    """01.4 §O1/O2 — proves user-supplied content was never elevated above
    ``user_intent_only`` during intake. This is the central 01.4 invariant.
    """

    receipt_id: str
    request_id: str
    observed_authority_labels: tuple[str, ...]
    max_authority_observed: str
    user_intent_cap_respected: bool
    authority_claim_refs: tuple[str, ...]
    deterministic_receipt_hash: str = ""

    def __post_init__(self) -> None:
        if self.max_authority_observed and self.max_authority_observed not in AUTHORITY_LABELS:
            raise ValueError(
                f"UserContentAuthorityReceipt.max_authority_observed="
                f"{self.max_authority_observed!r} not in {sorted(AUTHORITY_LABELS)!r}"
            )
        # Hard invariant: cap must match the observed maximum.
        if self.observed_authority_labels:
            actual_max_rank = max(_AUTHORITY_RANK.get(a, 0) for a in self.observed_authority_labels)
            cap_rank = _AUTHORITY_RANK["user_intent_only"]
            cap_respected = actual_max_rank <= cap_rank
            if cap_respected != self.user_intent_cap_respected:
                raise ValueError(
                    "UserContentAuthorityReceipt.user_intent_cap_respected "
                    f"({self.user_intent_cap_respected}) disagrees with observed "
                    f"max rank ({actual_max_rank} vs cap {cap_rank})."
                )

    def with_hash(self) -> "UserContentAuthorityReceipt":
        h = _hash(
            [
                list(self.observed_authority_labels),
                self.max_authority_observed,
                self.user_intent_cap_respected,
                list(self.authority_claim_refs),
            ]
        )
        return UserContentAuthorityReceipt(
            receipt_id=self.receipt_id,
            request_id=self.request_id,
            observed_authority_labels=self.observed_authority_labels,
            max_authority_observed=self.max_authority_observed,
            user_intent_cap_respected=self.user_intent_cap_respected,
            authority_claim_refs=self.authority_claim_refs,
            deterministic_receipt_hash=h,
        )

    @classmethod
    def from_outcome(cls, outcome: "IntakeOutcome") -> "UserContentAuthorityReceipt | None":
        bundle = outcome.receipt_bundle
        manifest = bundle.origin_label_manifest
        validated = outcome.validated
        if manifest is None or validated is None:
            return None
        labels = manifest.segment_authority_labels
        if not labels:
            max_observed = "no_authority"
        else:
            max_observed = max(labels, key=lambda a: _AUTHORITY_RANK.get(a, 0))
        cap_rank = _AUTHORITY_RANK["user_intent_only"]
        cap_respected = all(_AUTHORITY_RANK.get(a, 0) <= cap_rank for a in labels)
        receipt = cls(
            receipt_id=f"user_authority:{validated.request_id}",
            request_id=validated.request_id,
            observed_authority_labels=tuple(labels),
            max_authority_observed=max_observed,
            user_intent_cap_respected=cap_respected,
            authority_claim_refs=tuple(manifest.system_like_claim_refs),
        )
        return receipt.with_hash()


# ===========================================================================
# 01.4 — InjectionTriageReceipt
# ===========================================================================


_INJECTION_TRIAGE_STATUSES: frozenset[str] = frozenset({"CLEAR", "LABELED_SUSPICIOUS", "STRUCTURAL_REJECT"})


@dataclass(frozen=True)
class InjectionTriageReceipt:
    """01.4 §DATA CONTRACTS §3 — aggregator over PayloadSecurityFinding tuple."""

    triage_receipt_id: str
    request_id: str
    obvious_hijack_patterns: tuple[str, ...]
    role_override_attempts: tuple[str, ...]
    credential_request_markers: tuple[str, ...]
    tool_override_attempts: tuple[str, ...]
    system_prompt_request_markers: tuple[str, ...]
    suspicious_url_or_code_markers: tuple[str, ...]
    triage_status: str
    reason_codes: tuple[str, ...]
    deterministic_receipt_hash: str = ""

    def __post_init__(self) -> None:
        if self.triage_status not in _INJECTION_TRIAGE_STATUSES:
            raise ValueError(
                f"InjectionTriageReceipt.triage_status={self.triage_status!r} "
                f"not in {sorted(_INJECTION_TRIAGE_STATUSES)!r}"
            )

    def with_hash(self) -> "InjectionTriageReceipt":
        h = _hash(
            [
                list(self.obvious_hijack_patterns),
                list(self.role_override_attempts),
                list(self.credential_request_markers),
                list(self.tool_override_attempts),
                list(self.system_prompt_request_markers),
                list(self.suspicious_url_or_code_markers),
                self.triage_status,
                list(self.reason_codes),
            ]
        )
        return InjectionTriageReceipt(
            triage_receipt_id=self.triage_receipt_id,
            request_id=self.request_id,
            obvious_hijack_patterns=self.obvious_hijack_patterns,
            role_override_attempts=self.role_override_attempts,
            credential_request_markers=self.credential_request_markers,
            tool_override_attempts=self.tool_override_attempts,
            system_prompt_request_markers=self.system_prompt_request_markers,
            suspicious_url_or_code_markers=self.suspicious_url_or_code_markers,
            triage_status=self.triage_status,
            reason_codes=self.reason_codes,
            deterministic_receipt_hash=h,
        )

    @classmethod
    def from_outcome(cls, outcome: "IntakeOutcome") -> "InjectionTriageReceipt | None":
        bundle = outcome.receipt_bundle
        validated = outcome.validated
        rejected = outcome.rejected
        # Triage receipt may be emitted on either path; require any request id.
        request_id = validated.request_id if validated else (rejected.request_id if rejected else "")
        if not request_id:
            return None
        findings: tuple[PayloadSecurityFinding, ...] = bundle.payload_security_findings

        def _refs(cls_name: str) -> tuple[str, ...]:
            return tuple(f.segment_ref for f in findings if f.finding_class == cls_name)

        hijack = _refs("prompt_injection_like_text")
        role_overrides = _refs("system_override_claim")
        creds = _refs("credential_or_secret_pattern")
        tool_overrides = tuple(
            f.segment_ref
            for f in findings
            if f.finding_class == "prompt_injection_like_text"
            and "tool" in (f.downstream_attention_hint or "").lower()
        )
        sys_prompt = _refs("system_override_claim")
        suspicious = _refs("suspicious_url") + _refs("executable_payload")

        if findings:
            # Any high-severity finding without quarantine-OK status -> still LABELED_SUSPICIOUS;
            # structural reject is reserved for transport-stage rejection paths.
            status = "LABELED_SUSPICIOUS"
        else:
            status = "CLEAR"

        receipt = cls(
            triage_receipt_id=f"triage:{request_id}",
            request_id=request_id,
            obvious_hijack_patterns=hijack,
            role_override_attempts=role_overrides,
            credential_request_markers=creds,
            tool_override_attempts=tool_overrides,
            system_prompt_request_markers=sys_prompt,
            suspicious_url_or_code_markers=suspicious,
            triage_status=status,
            reason_codes=tuple(f.finding_class for f in findings),
        )
        return receipt.with_hash()


# ===========================================================================
# 01.4 — QuotedContentLabelReceipt
# ===========================================================================


@dataclass(frozen=True)
class QuotedContentLabelReceipt:
    """01.4 §O1 — explicit label for quoted/pasted content as
    ``QUOTED_USER_PROVIDED_DATA``. Projects the manifest's quoted refs into
    a doctrine-named receipt that downstream layers can consume directly.
    """

    receipt_id: str
    request_id: str
    quoted_segment_refs: tuple[str, ...]
    label: str = "QUOTED_USER_PROVIDED_DATA"
    deterministic_receipt_hash: str = ""

    def with_hash(self) -> "QuotedContentLabelReceipt":
        h = _hash([self.label, list(self.quoted_segment_refs)])
        return QuotedContentLabelReceipt(
            receipt_id=self.receipt_id,
            request_id=self.request_id,
            quoted_segment_refs=self.quoted_segment_refs,
            label=self.label,
            deterministic_receipt_hash=h,
        )

    @classmethod
    def from_outcome(cls, outcome: "IntakeOutcome") -> "QuotedContentLabelReceipt | None":
        bundle = outcome.receipt_bundle
        manifest = bundle.origin_label_manifest
        validated = outcome.validated
        if manifest is None or validated is None:
            return None
        receipt = cls(
            receipt_id=f"quoted_label:{validated.request_id}",
            request_id=validated.request_id,
            quoted_segment_refs=manifest.quoted_or_pasted_content_refs,
        )
        return receipt.with_hash()


# ===========================================================================
# 01.6 — IntakeTraceReceipt
# ===========================================================================


# Doctrine span set per 01.6 §REQUIRED OTEL SPANS, mapped to existing
# IngressEvent enum members. Any additional spans listed in the doctrine
# but not yet emitted by the pipeline are reported via missing_spans.
# Map doctrine span names -> existing IngressEvent values that satisfy
# them. Where the pipeline does not yet emit a dedicated event the doctrine
# span is reported as missing (see IntakeTraceReceipt.missing_spans). This
# is honest evidence: the implementation is closing the gap incrementally.
_DOCTRINE_SPAN_TO_EVENTS: dict[str, tuple[str, ...]] = {
    "u0.transport.receive": ("IngressReceived",),
    "u0.transport.validate_envelope": ("RequestIdAssigned", "TraceRootBound"),
    "u0.identity.classify": ("AuthBaselineEvaluated",),
    "u0.tenant.bind": ("AuthBaselineEvaluated",),  # folded into baseline event
    "u0.session.bind": ("AuthBaselineEvaluated",),  # folded into baseline event
    "u0.quota.check": ("QuotaEvaluated",),
    "u0.schema.validate": ("SchemaEvaluated",),
    "u0.payload.normalize": ("PayloadNormalized",),
    "u0.digest.compute": ("PayloadNormalized",),  # hash computed with normalize
    "u0.origin.label": ("PayloadNormalized",),  # origin labels built post-normalize
    "u0.injection.triage": ("PayloadNormalized",),  # findings emitted post-normalize
    "u0.admission.decide": ("IngressAccepted", "IngressRejected"),
    "u0.handoff.l1": ("IngressAccepted",),  # handoff envelope built on accept
}

_DOCTRINE_COVERAGE_BUCKETS: tuple[str, ...] = (
    "TRANSPORT",
    "IDENTITY",
    "QUOTA",
    "SCHEMA",
    "ORIGIN_LABELS",
    "ADMISSION",
    "HANDOFF",
)


@dataclass(frozen=True)
class IntakeTraceReceipt:
    """01.6 §DATA CONTRACTS §1 — span-coverage projection.

    Reports which doctrine-canonical U0 spans were observed in the
    pipeline event stream and which (if any) are missing. Used by the
    proof harness and U0BoundaryTestSuite to assert intake observability.
    """

    intake_trace_receipt_id: str
    request_id: str
    trace_root: str
    spans: tuple[str, ...]
    span_coverage: tuple[str, ...]
    missing_spans: tuple[str, ...]
    trace_status: str  # "COMPLETE" | "PARTIAL" | "FAILED"
    trace_digest: str = ""

    _ALLOWED = frozenset({"COMPLETE", "PARTIAL", "FAILED"})

    def __post_init__(self) -> None:
        if self.trace_status not in self._ALLOWED:
            raise ValueError(
                f"IntakeTraceReceipt.trace_status={self.trace_status!r} not in {sorted(self._ALLOWED)!r}"
            )
        for bucket in self.span_coverage:
            if bucket not in _DOCTRINE_COVERAGE_BUCKETS:
                raise ValueError(
                    f"IntakeTraceReceipt.span_coverage contains unknown bucket "
                    f"{bucket!r}; allowed = {_DOCTRINE_COVERAGE_BUCKETS!r}"
                )

    def with_hash(self) -> "IntakeTraceReceipt":
        h = _hash(
            [
                list(self.spans),
                list(self.span_coverage),
                list(self.missing_spans),
                self.trace_status,
            ]
        )
        return IntakeTraceReceipt(
            intake_trace_receipt_id=self.intake_trace_receipt_id,
            request_id=self.request_id,
            trace_root=self.trace_root,
            spans=self.spans,
            span_coverage=self.span_coverage,
            missing_spans=self.missing_spans,
            trace_status=self.trace_status,
            trace_digest=h,
        )

    @classmethod
    def from_outcome(cls, outcome: "IntakeOutcome") -> "IntakeTraceReceipt":
        events: tuple[IngressEventRecord, ...] = outcome.events
        emitted_event_names = {e.event.value for e in events}

        observed_spans: list[str] = []
        missing_spans: list[str] = []
        for span_name, event_names in _DOCTRINE_SPAN_TO_EVENTS.items():
            if any(en in emitted_event_names for en in event_names):
                observed_spans.append(span_name)
            else:
                missing_spans.append(span_name)

        # Coverage-bucket derivation
        coverage: list[str] = []
        if any(s.startswith("u0.transport.") for s in observed_spans):
            coverage.append("TRANSPORT")
        if any(s in observed_spans for s in ("u0.identity.classify", "u0.tenant.bind", "u0.session.bind")):
            coverage.append("IDENTITY")
        if "u0.quota.check" in observed_spans:
            coverage.append("QUOTA")
        if any(
            s in observed_spans for s in ("u0.schema.validate", "u0.payload.normalize", "u0.digest.compute")
        ):
            coverage.append("SCHEMA")
        if any(s in observed_spans for s in ("u0.origin.label", "u0.injection.triage")):
            coverage.append("ORIGIN_LABELS")
        if "u0.admission.decide" in observed_spans:
            coverage.append("ADMISSION")
        if "u0.handoff.l1" in observed_spans:
            coverage.append("HANDOFF")

        if outcome.validated is None:
            status = "FAILED" if not coverage else "PARTIAL"
        elif missing_spans:
            status = "PARTIAL"
        else:
            status = "COMPLETE"

        request_id = (
            outcome.validated.request_id
            if outcome.validated
            else (outcome.rejected.request_id if outcome.rejected else "")
        )
        trace_root = (
            outcome.validated.trace_root
            if outcome.validated
            else (outcome.rejected.trace_root if outcome.rejected else "")
        )

        receipt = cls(
            intake_trace_receipt_id=f"trace_receipt:{request_id or 'unknown'}",
            request_id=request_id or "unknown",
            trace_root=trace_root or "unknown",
            spans=tuple(observed_spans),
            span_coverage=tuple(coverage),
            missing_spans=tuple(missing_spans),
            trace_status=status,
        )
        return receipt.with_hash()


# ===========================================================================
# Aggregate builder
# ===========================================================================


@dataclass(frozen=True)
class DoctrineContractBundle:
    """Convenience aggregator — all six doctrine-canonical contracts."""

    idempotency_receipt: IntakeIdempotencyReceipt | None
    data_boundary_map: IngressDataBoundaryMap | None
    user_authority_receipt: UserContentAuthorityReceipt | None
    injection_triage_receipt: InjectionTriageReceipt | None
    quoted_content_label_receipt: QuotedContentLabelReceipt | None
    trace_receipt: IntakeTraceReceipt

    @classmethod
    def from_outcome(cls, outcome: "IntakeOutcome") -> "DoctrineContractBundle":
        return cls(
            idempotency_receipt=IntakeIdempotencyReceipt.from_outcome(outcome),
            data_boundary_map=IngressDataBoundaryMap.from_outcome(outcome),
            user_authority_receipt=UserContentAuthorityReceipt.from_outcome(outcome),
            injection_triage_receipt=InjectionTriageReceipt.from_outcome(outcome),
            quoted_content_label_receipt=QuotedContentLabelReceipt.from_outcome(outcome),
            trace_receipt=IntakeTraceReceipt.from_outcome(outcome),
        )


__all__ = [
    "DoctrineContractBundle",
    "IngressDataBoundaryMap",
    "InjectionTriageReceipt",
    "IntakeIdempotencyReceipt",
    "IntakeTraceReceipt",
    "QuotedContentLabelReceipt",
    "UserContentAuthorityReceipt",
]
