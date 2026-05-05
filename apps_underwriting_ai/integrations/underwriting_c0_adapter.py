"""C0 submitted-document evidence adapter for apps_underwriting_ai.

Implements the SUBMITTED_DOCUMENT_EVIDENCE_ONLY C0 mode for the synthetic
underwriting demo. Open-web retrieval is permanently blocked. Only synthetic
submitted documents, extracted field spans, fixture docs, and approved demo
policy table refs by hash are allowed as evidence sources.

C0 States:
  PASS             — all required document classes present; no contradictions;
                     support_score >= PASS_THRESHOLD
  WEAK_WITH_CAVEATS — partial evidence; missing optional fields or
                     soft contradictions; support_score >= WEAK_THRESHOLD
  FAIL             — required document classes absent; hard contradictions;
                     support_score < WEAK_THRESHOLD

Blocked sources (enforced in run()):
  - open_web: never attempted
  - broad internet enrichment: never attempted
  - semantic-neighbor packets for verdict reuse: never attempted

Plan: apps-underwriting-ai-spine-hardening-d7f3b2 W2.1 / W2.2.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any

C0_MODE = "SUBMITTED_DOCUMENT_EVIDENCE_ONLY"
OPEN_WEB_BLOCKED = True

C0_STATE_PASS = "PASS"
C0_STATE_WEAK = "WEAK_WITH_CAVEATS"
C0_STATE_FAIL = "FAIL"

PASS_THRESHOLD = 0.80
WEAK_THRESHOLD = 0.40

# Required document classes for a full underwriting decision packet.
REQUIRED_DOCUMENT_CLASSES = frozenset({
    "BANK_STATEMENT",
    "TAX_RETURN",
    "CREDIT_REPORT",
})

# Optional document classes — absence lowers score but does not trigger FAIL.
OPTIONAL_DOCUMENT_CLASSES = frozenset({
    "EMPLOYMENT_VERIFICATION",
    "PROPERTY_APPRAISAL",
    "BUSINESS_FINANCIALS",
    "IDENTITY_DOCUMENT",
})

# Field definitions per document class — what fields to extract and their weight.
_DOCUMENT_FIELD_SCHEMA: dict[str, list[dict[str, Any]]] = {
    "BANK_STATEMENT": [
        {"field": "average_monthly_balance", "required": True, "weight": 0.30},
        {"field": "account_tenure_months", "required": True, "weight": 0.20},
        {"field": "overdraft_count_12m", "required": False, "weight": 0.10},
        {"field": "deposit_consistency_score", "required": False, "weight": 0.10},
    ],
    "TAX_RETURN": [
        {"field": "annual_gross_income", "required": True, "weight": 0.35},
        {"field": "tax_year", "required": True, "weight": 0.10},
        {"field": "filing_status", "required": False, "weight": 0.05},
    ],
    "CREDIT_REPORT": [
        {"field": "credit_score", "required": True, "weight": 0.35},
        {"field": "derogatory_mark_count", "required": True, "weight": 0.20},
        {"field": "utilization_rate", "required": False, "weight": 0.10},
        {"field": "inquiry_count_12m", "required": False, "weight": 0.05},
    ],
    "EMPLOYMENT_VERIFICATION": [
        {"field": "employer_name", "required": False, "weight": 0.10},
        {"field": "employment_status", "required": False, "weight": 0.15},
        {"field": "tenure_months", "required": False, "weight": 0.10},
    ],
    "PROPERTY_APPRAISAL": [
        {"field": "appraised_value", "required": False, "weight": 0.20},
        {"field": "appraisal_date", "required": False, "weight": 0.05},
        {"field": "ltv_ratio", "required": False, "weight": 0.15},
    ],
    "BUSINESS_FINANCIALS": [
        {"field": "annual_revenue", "required": False, "weight": 0.25},
        {"field": "net_profit_margin", "required": False, "weight": 0.15},
        {"field": "years_in_operation", "required": False, "weight": 0.10},
    ],
    "IDENTITY_DOCUMENT": [
        {"field": "id_type", "required": False, "weight": 0.05},
        {"field": "id_verified", "required": False, "weight": 0.10},
    ],
}

# Cross-field contradiction rules: (field_a, field_b, rule_id, description).
_CONTRADICTION_RULES: list[tuple[str, str, str, str]] = [
    (
        "annual_gross_income",
        "average_monthly_balance",
        "INCOME_BALANCE_MISMATCH",
        "Declared annual income inconsistent with average monthly balance (ratio > 20x)",
    ),
    (
        "credit_score",
        "derogatory_mark_count",
        "CREDIT_SCORE_DEROGATORY_MISMATCH",
        "Credit score above 720 with 3+ derogatory marks is internally inconsistent",
    ),
    (
        "employment_status",
        "annual_gross_income",
        "EMPLOYMENT_INCOME_CONFLICT",
        "Employment status UNEMPLOYED with declared income > 0 is contradictory",
    ),
]


@dataclass
class FinalEvidenceContract:
    """Output contract for the underwriting C0 evidence pass.

    All fields required by the PA compiler (slot C0) and the Exit FEC producer.
    The contract is immutable once emitted — downstream stages must not modify it.

    Fields:
      c0_mode: Always SUBMITTED_DOCUMENT_EVIDENCE_ONLY.
      c0_state: PASS | WEAK_WITH_CAVEATS | FAIL.
      open_web_blocked: Always True — enforced invariant.
      evidence_contract_id: Deterministic SHA-256 ID from document fingerprints.
      evidence_ids: List of per-span evidence IDs (e.g. "ev-BANK_STATEMENT-0001").
      document_coverage_map: {document_class: bool} — presence of each class.
      extracted_span_map: {evidence_id: {field, value, document_class, confidence}}.
      contradiction_flags: List of CONTRADICTION_RULE_IDs triggered.
      missing_evidence_flags: Required document classes absent from submission.
      support_score: Float [0.0, 1.0] — weighted field coverage score.
      evidence_sufficiency: "sufficient" | "partial" | "insufficient".
      demo_policy_hash: Hash of the demo policy profile bound to this evidence.
      document_count: Number of submitted documents processed.
      required_classes_present: Subset of REQUIRED_DOCUMENT_CLASSES found.
      optional_classes_present: Subset of OPTIONAL_DOCUMENT_CLASSES found.
    """

    c0_mode: str = C0_MODE
    c0_state: str = C0_STATE_FAIL
    open_web_blocked: bool = True
    evidence_contract_id: str = ""
    evidence_ids: list[str] = field(default_factory=list)
    document_coverage_map: dict[str, bool] = field(default_factory=dict)
    extracted_span_map: dict[str, Any] = field(default_factory=dict)
    contradiction_flags: list[str] = field(default_factory=list)
    missing_evidence_flags: list[str] = field(default_factory=list)
    support_score: float = 0.0
    evidence_sufficiency: str = "insufficient"
    demo_policy_hash: str = ""
    document_count: int = 0
    required_classes_present: list[str] = field(default_factory=list)
    optional_classes_present: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "c0_mode": self.c0_mode,
            "c0_state": self.c0_state,
            "open_web_blocked": self.open_web_blocked,
            "evidence_contract_id": self.evidence_contract_id,
            "evidence_ids": self.evidence_ids,
            "document_coverage_map": self.document_coverage_map,
            "extracted_span_map": self.extracted_span_map,
            "contradiction_flags": self.contradiction_flags,
            "missing_evidence_flags": self.missing_evidence_flags,
            "support_score": self.support_score,
            "evidence_sufficiency": self.evidence_sufficiency,
            "demo_policy_hash": self.demo_policy_hash,
            "document_count": self.document_count,
            "required_classes_present": self.required_classes_present,
            "optional_classes_present": self.optional_classes_present,
        }


def _compute_evidence_id(document_class: str, field_name: str, index: int) -> str:
    """Produce a deterministic evidence_id for a single extracted span."""
    raw = f"{document_class}:{field_name}:{index:04d}"
    digest = hashlib.sha256(raw.encode()).hexdigest()[:12]
    return f"ev-{document_class[:8].upper()}-{digest}"


def _compute_contract_id(documents: list[dict[str, Any]], policy_hash: str) -> str:
    """Produce a deterministic evidence_contract_id from document fingerprints."""
    fingerprint = json.dumps(
        [{"kind": d.get("kind", ""), "class": d.get("document_class", "")} for d in documents],
        sort_keys=True,
    )
    raw = f"{fingerprint}:{policy_hash}"
    return "fec-" + hashlib.sha256(raw.encode()).hexdigest()[:16]


def _classify_document(doc: dict[str, Any]) -> str:
    """Map a submitted document dict to a normalized document class string."""
    kind = (doc.get("document_class") or doc.get("kind") or "").upper()
    aliases: dict[str, str] = {
        "TAX_RETURN": "TAX_RETURN",
        "TAX": "TAX_RETURN",
        "BANK_STATEMENT": "BANK_STATEMENT",
        "BANK": "BANK_STATEMENT",
        "CREDIT_REPORT": "CREDIT_REPORT",
        "CREDIT": "CREDIT_REPORT",
        "EMPLOYMENT_VERIFICATION": "EMPLOYMENT_VERIFICATION",
        "EMPLOYMENT": "EMPLOYMENT_VERIFICATION",
        "PROPERTY_APPRAISAL": "PROPERTY_APPRAISAL",
        "APPRAISAL": "PROPERTY_APPRAISAL",
        "BUSINESS_FINANCIALS": "BUSINESS_FINANCIALS",
        "BUSINESS": "BUSINESS_FINANCIALS",
        "IDENTITY_DOCUMENT": "IDENTITY_DOCUMENT",
        "IDENTITY": "IDENTITY_DOCUMENT",
        "ID": "IDENTITY_DOCUMENT",
    }
    return aliases.get(kind, kind)


def _extract_spans(
    doc: dict[str, Any],
    document_class: str,
    span_index: int,
) -> tuple[list[str], dict[str, Any]]:
    """Extract field spans from a document dict.

    Returns (evidence_ids, span_entries) for all recognized fields.
    Fields not in the schema are silently ignored — no open-web inference.
    """
    schema = _DOCUMENT_FIELD_SCHEMA.get(document_class, [])
    evidence_ids: list[str] = []
    span_entries: dict[str, Any] = {}

    for field_def in schema:
        field_name = field_def["field"]
        value = doc.get(field_name) or doc.get("fields", {}).get(field_name)
        if value is None:
            continue
        ev_id = _compute_evidence_id(document_class, field_name, span_index)
        evidence_ids.append(ev_id)
        span_entries[ev_id] = {
            "evidence_id": ev_id,
            "document_class": document_class,
            "field_name": field_name,
            "value": value,
            "confidence": 0.90 if field_def["required"] else 0.75,
            "weight": field_def["weight"],
        }
        span_index += 1

    return evidence_ids, span_entries


def _compute_support_score(
    document_coverage_map: dict[str, bool],
    extracted_span_map: dict[str, Any],
) -> float:
    """Compute a weighted support score from coverage and extracted spans.

    Score = (required_classes_present / total_required) * 0.60
            + (optional_classes_present / total_optional) * 0.20
            + (span_weight_sum / max_possible_weight) * 0.20
    """
    req_present = sum(
        1 for cls in REQUIRED_DOCUMENT_CLASSES if document_coverage_map.get(cls, False)
    )
    req_total = len(REQUIRED_DOCUMENT_CLASSES)
    opt_present = sum(
        1 for cls in OPTIONAL_DOCUMENT_CLASSES if document_coverage_map.get(cls, False)
    )
    opt_total = len(OPTIONAL_DOCUMENT_CLASSES) or 1

    span_weight = sum(s.get("weight", 0.0) for s in extracted_span_map.values())
    max_weight = sum(
        fd["weight"]
        for fields in _DOCUMENT_FIELD_SCHEMA.values()
        for fd in fields
        if fd["required"]
    )
    max_weight = max_weight or 1.0

    score = (
        (req_present / req_total) * 0.60
        + (opt_present / opt_total) * 0.20
        + min(span_weight / max_weight, 1.0) * 0.20
    )
    return round(min(score, 1.0), 4)


def _detect_contradictions(extracted_span_map: dict[str, Any]) -> list[str]:
    """Detect cross-field contradictions in extracted spans.

    Returns list of triggered CONTRADICTION_RULE_IDs.
    """
    field_values: dict[str, Any] = {
        span["field_name"]: span["value"]
        for span in extracted_span_map.values()
    }
    flags: list[str] = []

    for field_a, field_b, rule_id, _ in _CONTRADICTION_RULES:
        val_a = field_values.get(field_a)
        val_b = field_values.get(field_b)
        if val_a is None or val_b is None:
            continue

        if rule_id == "INCOME_BALANCE_MISMATCH":
            try:
                income = float(val_a)
                balance = float(val_b)
                if income > 0 and balance > 0 and income / balance > 20:
                    flags.append(rule_id)
            except (TypeError, ValueError, ZeroDivisionError):
                pass

        elif rule_id == "CREDIT_SCORE_DEROGATORY_MISMATCH":
            try:
                score = float(val_a)
                derog = int(val_b)
                if score >= 720 and derog >= 3:
                    flags.append(rule_id)
            except (TypeError, ValueError):
                pass

        elif rule_id == "EMPLOYMENT_INCOME_CONFLICT":
            try:
                status = str(val_a).upper()
                income = float(val_b)
                if status == "UNEMPLOYED" and income > 0:
                    flags.append(rule_id)
            except (TypeError, ValueError):
                pass

    return flags


class UnderwritingC0Adapter:
    """Adapter that runs C0 retrieval in SUBMITTED_DOCUMENT_EVIDENCE_ONLY mode.

    Invariants:
    - open_web retrieval is NEVER attempted (OPEN_WEB_BLOCKED = True always)
    - Only submitted-document fields and fixture policy refs by hash are sourced
    - Output is always a FinalEvidenceContract; never raises on bad input
    - c0_state is determined by support_score thresholds and missing required classes
    - All field values come from submitted_documents dicts — no inference, no retrieval
    """

    def run(
        self,
        submitted_documents: list[dict[str, Any]],
        demo_policy_hash: str = "",
        trace_id: str = "",
    ) -> FinalEvidenceContract:
        """Run C0 evidence extraction on submitted documents.

        Open-web retrieval is blocked. Extracts fields from submitted_documents
        dicts only. Computes coverage, contradiction flags, and support score.
        Determines c0_state from thresholds.

        Args:
            submitted_documents: List of synthetic submitted document dicts.
                Each dict should carry a 'document_class' or 'kind' key plus
                field key-value pairs matching _DOCUMENT_FIELD_SCHEMA.
            demo_policy_hash: Hash of the demo policy table to bind evidence to.
                Binds the FinalEvidenceContract to a specific policy fixture.
            trace_id: Optional trace identifier for observability.

        Returns:
            FinalEvidenceContract with evidence extraction results.
            Never raises — returns FAIL contract on any malformed input.
        """
        try:
            return self._run_safe(submitted_documents, demo_policy_hash, trace_id)
        except Exception:  # noqa: BLE001
            # guardian: allow-broad-except -- C0 adapter is fail-soft;
            # any unexpected error returns a FAIL contract rather than raising
            return FinalEvidenceContract(
                c0_mode=C0_MODE,
                c0_state=C0_STATE_FAIL,
                open_web_blocked=True,
                evidence_contract_id="fec-error-fallback",
                evidence_ids=[],
                document_coverage_map={},
                extracted_span_map={},
                contradiction_flags=["C0_ADAPTER_INTERNAL_ERROR"],
                missing_evidence_flags=list(REQUIRED_DOCUMENT_CLASSES),
                support_score=0.0,
                evidence_sufficiency="insufficient",
                demo_policy_hash=demo_policy_hash,
                document_count=0,
                required_classes_present=[],
                optional_classes_present=[],
            )

    def _run_safe(
        self,
        submitted_documents: list[dict[str, Any]],
        demo_policy_hash: str,
        trace_id: str,
    ) -> FinalEvidenceContract:
        """Internal implementation — called by run() with exception guard."""
        if not isinstance(submitted_documents, list):
            submitted_documents = []

        evidence_contract_id = _compute_contract_id(submitted_documents, demo_policy_hash)

        # Step 1: classify documents and build coverage map.
        document_coverage_map: dict[str, bool] = {}
        class_to_docs: dict[str, list[dict[str, Any]]] = {}
        for doc in submitted_documents:
            if not isinstance(doc, dict):
                continue
            doc_class = _classify_document(doc)
            if not doc_class:
                continue
            document_coverage_map[doc_class] = True
            class_to_docs.setdefault(doc_class, []).append(doc)

        # Step 2: extract spans from all recognized documents.
        all_evidence_ids: list[str] = []
        all_span_map: dict[str, Any] = {}
        span_index = 0
        for doc_class, docs in class_to_docs.items():
            for doc in docs:
                ids, spans = _extract_spans(doc, doc_class, span_index)
                all_evidence_ids.extend(ids)
                all_span_map.update(spans)
                span_index += len(ids)

        # Step 3: required/optional class presence.
        required_present = sorted(
            cls for cls in REQUIRED_DOCUMENT_CLASSES if document_coverage_map.get(cls, False)
        )
        optional_present = sorted(
            cls for cls in OPTIONAL_DOCUMENT_CLASSES if document_coverage_map.get(cls, False)
        )
        missing_required = sorted(
            cls for cls in REQUIRED_DOCUMENT_CLASSES if not document_coverage_map.get(cls, False)
        )

        # Step 4: contradiction detection.
        contradiction_flags = _detect_contradictions(all_span_map)

        # Step 5: support score.
        support_score = _compute_support_score(document_coverage_map, all_span_map)

        # Step 6: determine c0_state.
        has_hard_contradiction = len(contradiction_flags) > 0
        has_missing_required = len(missing_required) > 0

        if has_missing_required and support_score < WEAK_THRESHOLD:
            c0_state = C0_STATE_FAIL
            evidence_sufficiency = "insufficient"
        elif has_hard_contradiction or (has_missing_required and support_score < PASS_THRESHOLD):
            c0_state = C0_STATE_WEAK
            evidence_sufficiency = "partial"
        elif support_score >= PASS_THRESHOLD and not has_hard_contradiction:
            c0_state = C0_STATE_PASS
            evidence_sufficiency = "sufficient"
        else:
            c0_state = C0_STATE_WEAK
            evidence_sufficiency = "partial"

        return FinalEvidenceContract(
            c0_mode=C0_MODE,
            c0_state=c0_state,
            open_web_blocked=True,
            evidence_contract_id=evidence_contract_id,
            evidence_ids=all_evidence_ids,
            document_coverage_map=document_coverage_map,
            extracted_span_map=all_span_map,
            contradiction_flags=contradiction_flags,
            missing_evidence_flags=missing_required,
            support_score=support_score,
            evidence_sufficiency=evidence_sufficiency,
            demo_policy_hash=demo_policy_hash,
            document_count=len(submitted_documents),
            required_classes_present=required_present,
            optional_classes_present=optional_present,
        )
