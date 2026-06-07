"""C0 submitted-document evidence adapter for apps_underwriting_ai.

Implements the SUBMITTED_DOCUMENT_EVIDENCE_ONLY C0 mode for the synthetic
underwriting demo. Open-web retrieval is permanently blocked. Only synthetic
submitted documents, extracted field spans, fixture docs, and approved demo
policy table refs by hash are allowed as evidence sources.

C0 States:
  PASS             — all required document classes present AND all required
                     fields for those classes extracted; no contradictions;
                     support_score >= PASS_THRESHOLD
  WEAK_WITH_CAVEATS — partial evidence: a required field is missing, a required
                     doc is missing but support_score is moderate, or any
                     contradiction is present
  FAIL             — malformed/non-list input, no usable required evidence, or
                     support_score < WEAK_THRESHOLD

Determinism guarantees:
  - evidence_contract_id is a SHA-256 over a CANONICAL representation of the
    submitted documents (normalized class + sorted field names + values +
    demo_policy_hash). Changing any submitted field VALUE changes the ID.
  - per-span evidence_ids are derived from (normalized class, stable document
    ordinal, field name, field value). Duplicate documents do not collide.
  - no timestamps, trace IDs, random UUIDs, or memory addresses feed any hash.

Blocked sources (enforced in run()):
  - open_web: never attempted
  - broad internet enrichment: never attempted
  - semantic-neighbor packets for verdict reuse: never attempted

Plan: apps-underwriting-ai-spine-hardening-d7f3b2 W2.1 / W2.2 (+ readiness hardening).
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
# Each rule compares two extracted spans that come from DIFFERENT submitted
# documents, so a contradiction means the packet is internally inconsistent —
# something a single-document parser could never catch. Rules are deterministic
# threshold checks (no ML) so an underwriter can re-derive every flag by hand.
_CONTRADICTION_RULES: list[tuple[str, str, str, str]] = [
    (
        "annual_gross_income",      # from TAX_RETURN
        "average_monthly_balance",  # from BANK_STATEMENT
        "INCOME_BALANCE_MISMATCH",
        "Declared annual income exceeds 20x the average monthly bank balance — "
        "high income with near-empty accounts is internally inconsistent.",
    ),
    (
        "credit_score",             # from CREDIT_REPORT
        "derogatory_mark_count",    # from CREDIT_REPORT
        "CREDIT_SCORE_DEROGATORY_MISMATCH",
        "Credit score >= 720 paired with 3+ derogatory marks is internally "
        "inconsistent — a clean-score report should not carry heavy derogatories.",
    ),
    (
        "employment_status",        # from EMPLOYMENT_VERIFICATION
        "annual_gross_income",      # from TAX_RETURN
        "EMPLOYMENT_INCOME_CONFLICT",
        "Employment status UNEMPLOYED with declared annual income > 0 is "
        "contradictory across the employment and tax documents.",
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
      missing_evidence_flags: Structured flags for absent required evidence:
        "MISSING_DOC:<CLASS>" for an absent required document class, and
        "MISSING_FIELD:<CLASS>.<field>" for a present class whose required
        field was not extracted. PASS requires this list to be empty.
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


def _canonical_json(data: Any) -> str:
    """Canonical, deterministic JSON for hashing.

    Sorted keys, no whitespace, ``default=str`` so any stray non-JSON value
    (e.g. a Decimal) serializes to a stable string instead of raising.
    """
    return json.dumps(data, sort_keys=True, separators=(",", ":"), default=str)


def _get_submitted_field_value(
    doc: dict[str, Any], field_name: str
) -> tuple[bool, Any]:
    """Return (present, value) for a submitted field, honoring falsy values.

    A field is "present" when the key exists — even if its value is 0, 0.0,
    "", or False. Those are all valid underwriting values (e.g. zero
    derogatory marks) and must NOT be treated as missing. Looks in the top
    level first, then a nested ``fields`` dict. Never infers a value.
    """
    if field_name in doc:
        return True, doc[field_name]
    fields = doc.get("fields")
    if isinstance(fields, dict) and field_name in fields:
        return True, fields[field_name]
    return False, None


def _canonical_document(doc: dict[str, Any]) -> dict[str, Any]:
    """Canonical form of one submitted document for fingerprinting.

    Captures the normalized class plus every submitted field name->value pair
    (top-level recognized fields and a nested ``fields`` dict if present), so
    that two packets differing only in a field VALUE produce different
    fingerprints. Non-dict junk is represented by a stable malformed marker
    rather than crashing the hash.
    """
    if not isinstance(doc, dict):
        return {"__malformed__": _canonical_json(doc)}
    doc_class = _classify_document(doc)
    field_pairs: dict[str, Any] = {}
    for key, value in doc.items():
        if key in ("document_class", "kind", "fields"):
            continue
        field_pairs[str(key)] = value
    nested = doc.get("fields")
    if isinstance(nested, dict):
        for key, value in nested.items():
            field_pairs.setdefault(str(key), value)
    return {"class": doc_class, "fields": field_pairs}


def _compute_evidence_id(
    document_class: str,
    doc_ordinal: int,
    field_name: str,
    value: Any,
) -> str:
    """Produce a deterministic, value-aware evidence_id for a single span.

    Derived from (normalized class, stable document ordinal, field name,
    field value). The ordinal disambiguates duplicate documents of the same
    class so their spans never overwrite each other; the value binds the ID to
    the actual extracted evidence. No timestamps / UUIDs / trace IDs.
    """
    raw = _canonical_json(
        {"class": document_class, "ord": doc_ordinal, "field": field_name, "value": value}
    )
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:12]
    return f"ev-{document_class[:8].upper()}-{digest}"


def _compute_contract_id(documents: list[dict[str, Any]], policy_hash: str) -> str:
    """Produce a deterministic evidence_contract_id from document VALUES.

    Hashes a canonical representation of every submitted document — normalized
    class, sorted field names, and field values — plus the demo_policy_hash.
    Document order IS preserved (it is part of the submitted packet's
    identity). Same input -> same ID; any changed field value -> changed ID.
    Excludes timestamps, trace IDs, and memory addresses. Never raises on junk
    entries (they become a stable malformed marker).
    """
    if not isinstance(documents, list):
        canonical = {"__non_list__": _canonical_json(documents), "policy": policy_hash}
    else:
        canonical = {
            "documents": [_canonical_document(d) for d in documents],
            "policy": policy_hash,
        }
    raw = _canonical_json(canonical)
    return "fec-" + hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


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
    doc_ordinal: int,
) -> tuple[list[str], dict[str, Any], list[str]]:
    """Extract field spans from a single document dict.

    Returns (evidence_ids, span_entries, extracted_field_names). Only fields in
    the schema are extracted, and only when actually submitted — including
    falsy values like 0 / 0.0 / False (valid underwriting values). Fields not
    in the schema (e.g. an invented external score) are never extracted, so no
    inferred / open-web field can enter the contract.

    ``doc_ordinal`` is the document's stable position among same-class
    documents, used so duplicate documents produce distinct evidence_ids
    instead of overwriting each other.
    """
    schema = _DOCUMENT_FIELD_SCHEMA.get(document_class, [])
    evidence_ids: list[str] = []
    span_entries: dict[str, Any] = {}
    extracted_field_names: list[str] = []

    for field_def in schema:
        field_name = field_def["field"]
        present, value = _get_submitted_field_value(doc, field_name)
        if not present:
            continue  # do NOT infer a missing value
        ev_id = _compute_evidence_id(document_class, doc_ordinal, field_name, value)
        evidence_ids.append(ev_id)
        span_entries[ev_id] = {
            "evidence_id": ev_id,
            "document_class": document_class,
            "field_name": field_name,
            "value": value,
            "confidence": 0.90 if field_def["required"] else 0.75,
            "weight": field_def["weight"],
        }
        extracted_field_names.append(field_name)

    return evidence_ids, span_entries, extracted_field_names


def _required_fields_for_class(document_class: str) -> list[str]:
    """Return the required field names for a document class (schema-driven)."""
    return [
        fd["field"]
        for fd in _DOCUMENT_FIELD_SCHEMA.get(document_class, [])
        if fd["required"]
    ]


# Support-score component weights. Tuned so a complete required-document
# packet with all required fields extracted lands above PASS_THRESHOLD (0.80),
# while a packet missing any required class cannot reach PASS on coverage alone.
_SCORE_WEIGHT_REQUIRED_COVERAGE = 0.60
_SCORE_WEIGHT_OPTIONAL_COVERAGE = 0.20
_SCORE_WEIGHT_SPAN_COVERAGE = 0.20


def _compute_support_score_breakdown(
    document_coverage_map: dict[str, bool],
    extracted_span_map: dict[str, Any],
) -> dict[str, float]:
    """Compute the support score AND its component breakdown.

    The score is a transparent weighted sum of three observable signals — no
    learned model, no hidden state — so an underwriter can re-derive it by hand:

      required_coverage = (required classes present / 3)            -> weight 0.60
      optional_coverage = (optional classes present / 4)            -> weight 0.20
      span_coverage     = (extracted required-field weight / max)   -> weight 0.20

      support_score = required_coverage * 0.60
                    + optional_coverage * 0.20
                    + span_coverage     * 0.20

    Returns a dict with every intermediate term plus the final ``support_score``
    so the value is fully explainable in audit and in interview.
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

    required_coverage = req_present / req_total
    optional_coverage = opt_present / opt_total
    span_coverage = min(span_weight / max_weight, 1.0)

    score = (
        required_coverage * _SCORE_WEIGHT_REQUIRED_COVERAGE
        + optional_coverage * _SCORE_WEIGHT_OPTIONAL_COVERAGE
        + span_coverage * _SCORE_WEIGHT_SPAN_COVERAGE
    )
    return {
        "required_coverage": round(required_coverage, 4),
        "optional_coverage": round(optional_coverage, 4),
        "span_coverage": round(span_coverage, 4),
        "support_score": round(min(score, 1.0), 4),
    }


def _compute_support_score(
    document_coverage_map: dict[str, bool],
    extracted_span_map: dict[str, Any],
) -> float:
    """Compute the weighted support score (see _compute_support_score_breakdown)."""
    return _compute_support_score_breakdown(
        document_coverage_map, extracted_span_map
    )["support_score"]


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
            # guardian: allow-broad-except -- C0 adapter is fail-soft; only a
            # TRULY unexpected error reaches here (the normal malformed-input
            # paths are handled deterministically inside _run_safe). Returns a
            # FAIL contract rather than raising. The C0_ADAPTER_INTERNAL_ERROR
            # contradiction flag distinguishes this from ordinary missing/weak
            # evidence so on-call can tell a bug from a thin packet.
            return FinalEvidenceContract(
                c0_mode=C0_MODE,
                c0_state=C0_STATE_FAIL,
                open_web_blocked=True,
                evidence_contract_id="fec-error-fallback",
                evidence_ids=[],
                document_coverage_map={},
                extracted_span_map={},
                contradiction_flags=["C0_ADAPTER_INTERNAL_ERROR"],
                missing_evidence_flags=[
                    f"MISSING_DOC:{cls}" for cls in sorted(REQUIRED_DOCUMENT_CLASSES)
                ],
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
        """Internal implementation — called by run() with exception guard.

        Handles malformed input deterministically (does NOT rely on the
        run() exception guard): a non-list payload yields a FAIL contract, and
        junk entries inside a list (non-dicts, dicts with no recognizable
        document_class) are skipped deterministically.
        """
        # Non-list input -> deterministic FAIL (never the internal-error path).
        if not isinstance(submitted_documents, list):
            return self._fail_closed_contract(
                submitted_documents, demo_policy_hash, document_count=0
            )

        # Contract ID is value-aware over the WHOLE submitted payload (incl.
        # junk, captured via a stable malformed marker) so it stays stable and
        # changes whenever any submitted value changes.
        evidence_contract_id = _compute_contract_id(submitted_documents, demo_policy_hash)

        # Step 1: classify documents and build coverage map. Junk entries are
        # skipped deterministically; they still counted in document_count.
        document_coverage_map: dict[str, bool] = {}
        class_to_docs: dict[str, list[dict[str, Any]]] = {}
        for doc in submitted_documents:
            if not isinstance(doc, dict):
                continue
            doc_class = _classify_document(doc)
            if not doc_class:
                continue  # dict without a recognizable document_class/kind
            document_coverage_map[doc_class] = True
            class_to_docs.setdefault(doc_class, []).append(doc)

        # Step 2: extract spans. Each same-class document gets a stable ordinal
        # so duplicates do not collide.
        all_evidence_ids: list[str] = []
        all_span_map: dict[str, Any] = {}
        extracted_fields_by_class: dict[str, set[str]] = {}
        for doc_class, docs in class_to_docs.items():
            for ordinal, doc in enumerate(docs):
                ids, spans, field_names = _extract_spans(doc, doc_class, ordinal)
                all_evidence_ids.extend(ids)
                all_span_map.update(spans)
                extracted_fields_by_class.setdefault(doc_class, set()).update(field_names)

        # Step 3: required/optional class presence.
        required_present = sorted(
            cls for cls in REQUIRED_DOCUMENT_CLASSES if document_coverage_map.get(cls, False)
        )
        optional_present = sorted(
            cls for cls in OPTIONAL_DOCUMENT_CLASSES if document_coverage_map.get(cls, False)
        )

        # Step 3b: build structured missing-evidence flags.
        #   MISSING_DOC:<CLASS>            — required class absent entirely
        #   MISSING_FIELD:<CLASS>.<field>  — required class present but a
        #                                    required field was not extracted
        missing_evidence_flags: list[str] = []
        missing_required_docs: list[str] = []
        missing_required_fields: list[str] = []
        for cls in sorted(REQUIRED_DOCUMENT_CLASSES):
            if not document_coverage_map.get(cls, False):
                missing_required_docs.append(cls)
                missing_evidence_flags.append(f"MISSING_DOC:{cls}")
                continue
            extracted = extracted_fields_by_class.get(cls, set())
            for field_name in _required_fields_for_class(cls):
                if field_name not in extracted:
                    missing_required_fields.append(f"{cls}.{field_name}")
                    missing_evidence_flags.append(f"MISSING_FIELD:{cls}.{field_name}")

        # Step 4: contradiction detection.
        contradiction_flags = _detect_contradictions(all_span_map)

        # Step 5: support score.
        support_score = _compute_support_score(document_coverage_map, all_span_map)

        # Step 6: determine c0_state.
        #   PASS  : all required classes present AND all required fields
        #           extracted AND no contradictions AND score >= PASS_THRESHOLD
        #   FAIL  : a required class missing AND score < WEAK_THRESHOLD
        #   WEAK  : everything in between (missing required field, missing doc
        #           with moderate score, or any contradiction)
        has_contradiction = len(contradiction_flags) > 0
        has_missing_required_doc = len(missing_required_docs) > 0
        has_missing_required_field = len(missing_required_fields) > 0

        if has_missing_required_doc and support_score < WEAK_THRESHOLD:
            c0_state = C0_STATE_FAIL
            evidence_sufficiency = "insufficient"
        elif (
            not has_missing_required_doc
            and not has_missing_required_field
            and not has_contradiction
            and support_score >= PASS_THRESHOLD
        ):
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
            missing_evidence_flags=missing_evidence_flags,
            support_score=support_score,
            evidence_sufficiency=evidence_sufficiency,
            demo_policy_hash=demo_policy_hash,
            document_count=len(submitted_documents),
            required_classes_present=required_present,
            optional_classes_present=optional_present,
        )

    @staticmethod
    def _fail_closed_contract(
        submitted_documents: Any,
        demo_policy_hash: str,
        document_count: int,
    ) -> FinalEvidenceContract:
        """Deterministic FAIL contract for malformed (e.g. non-list) input.

        Unlike the run() exception guard, this is NOT an internal error — it is
        the expected, documented response to an unusable payload. No
        C0_ADAPTER_INTERNAL_ERROR flag is set.
        """
        return FinalEvidenceContract(
            c0_mode=C0_MODE,
            c0_state=C0_STATE_FAIL,
            open_web_blocked=True,
            evidence_contract_id=_compute_contract_id(submitted_documents, demo_policy_hash),
            evidence_ids=[],
            document_coverage_map={},
            extracted_span_map={},
            contradiction_flags=[],
            missing_evidence_flags=[
                f"MISSING_DOC:{cls}" for cls in sorted(REQUIRED_DOCUMENT_CLASSES)
            ],
            support_score=0.0,
            evidence_sufficiency="insufficient",
            demo_policy_hash=demo_policy_hash,
            document_count=document_count,
            required_classes_present=[],
            optional_classes_present=[],
        )
