"""Focused tests — C0 Submitted-Document Evidence Sufficiency Gate.

Interview-anchor suite for the narrow slice documented in
``apps_underwriting_ai/docs/EVIDENCE_SUFFICIENCY_GATE_CASE_STUDY.md``. Exercises
``UnderwritingC0Adapter`` (the gate) against the synthetic fixtures under
``apps_underwriting_ai/fixtures/c0_*_documents.yaml`` and the downstream LLM
firewall's deterministic evidence-citation allowlist.

Covered behaviors:
  1.  full packet -> PASS (sufficient, no missing/contradiction flags)
  2.  missing BANK_STATEMENT -> MISSING_DOC flag, not PASS
  3.  missing TAX_RETURN     -> MISSING_DOC flag, not PASS
  4.  income/balance mismatch -> INCOME_BALANCE_MISMATCH
  5.  high score + derogatories -> CREDIT_SCORE_DEROGATORY_MISMATCH
  6.  malformed submitted_documents -> FAIL, never raises
  7.  determinism: same input -> same evidence_contract_id + evidence_ids
  8.  changing a submitted value -> changed evidence_contract_id (auditability)
  9.  falsy values (0 / False) are extracted, not dropped
  10. extracted_span_map contains only submitted (schema) fields, none inferred
  11. open_web_blocked always True (parametrized over all states)
  12. firewall rejects rationale citing a fabricated evidence ID (+ bundle guards)

All data is synthetic (see fixtures). No real PII, no real decisioning.
"""
from __future__ import annotations

import copy
import sys
from pathlib import Path
from typing import Any

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from apps_underwriting_ai.integrations.underwriting_c0_adapter import (  # noqa: E402
    C0_STATE_FAIL,
    C0_STATE_PASS,
    UnderwritingC0Adapter,
)

_FIXTURE_DIR = REPO_ROOT / "apps_underwriting_ai" / "fixtures"
_POLICY_HASH = "sha256-demo-policy-standard-v1-aabbcc"

_adapter = UnderwritingC0Adapter()


def _load_documents(fixture_name: str) -> Any:
    """Load the raw ``submitted_documents`` payload from a C0 fixture.

    Returned verbatim (a list of dicts, or — for the malformed fixture — a list
    containing non-dict junk). The gate must tolerate either.
    """
    path = _FIXTURE_DIR / fixture_name
    with path.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    return data["submitted_documents"]


# ---------------------------------------------------------------------------
# 1 — full packet returns PASS
# ---------------------------------------------------------------------------

def test_full_packet_returns_pass() -> None:
    docs = _load_documents("c0_full_pass_documents.yaml")
    fec = _adapter.run(docs, demo_policy_hash=_POLICY_HASH)

    assert fec.c0_state == C0_STATE_PASS, (
        f"Full packet must be PASS, got {fec.c0_state!r} "
        f"(score={fec.support_score}, missing={fec.missing_evidence_flags}, "
        f"contradictions={fec.contradiction_flags})"
    )
    assert fec.evidence_sufficiency == "sufficient"
    assert fec.open_web_blocked is True
    assert fec.missing_evidence_flags == []
    assert fec.contradiction_flags == []
    assert set(fec.required_classes_present) == {
        "BANK_STATEMENT",
        "TAX_RETURN",
        "CREDIT_REPORT",
    }
    assert len(fec.evidence_ids) > 0
    assert len(fec.extracted_span_map) > 0


# ---------------------------------------------------------------------------
# 2 — missing BANK_STATEMENT
# ---------------------------------------------------------------------------

def test_missing_bank_statement_flags_and_not_pass() -> None:
    docs = _load_documents("c0_missing_bank_statement_documents.yaml")
    fec = _adapter.run(docs, demo_policy_hash=_POLICY_HASH)

    assert fec.c0_state != C0_STATE_PASS
    assert "MISSING_DOC:BANK_STATEMENT" in fec.missing_evidence_flags
    assert "BANK_STATEMENT" not in fec.required_classes_present
    assert fec.open_web_blocked is True


# ---------------------------------------------------------------------------
# 3 — missing TAX_RETURN
# ---------------------------------------------------------------------------

def test_missing_tax_return_flags_and_not_pass() -> None:
    docs = [
        {
            "document_class": "BANK_STATEMENT",
            "average_monthly_balance": 8500.0,
            "account_tenure_months": 36,
        },
        {
            "document_class": "CREDIT_REPORT",
            "credit_score": 740,
            "derogatory_mark_count": 0,
        },
    ]
    fec = _adapter.run(docs, demo_policy_hash=_POLICY_HASH)

    assert fec.c0_state != C0_STATE_PASS
    assert "MISSING_DOC:TAX_RETURN" in fec.missing_evidence_flags
    assert fec.open_web_blocked is True


# ---------------------------------------------------------------------------
# 4 — income/balance mismatch
# ---------------------------------------------------------------------------

def test_income_balance_mismatch_contradiction() -> None:
    docs = _load_documents("c0_contradiction_documents.yaml")
    fec = _adapter.run(docs, demo_policy_hash=_POLICY_HASH)

    assert "INCOME_BALANCE_MISMATCH" in fec.contradiction_flags
    assert fec.c0_state != C0_STATE_PASS, "A contradiction must never PASS."


# ---------------------------------------------------------------------------
# 5 — high credit score with too many derogatory marks
# ---------------------------------------------------------------------------

def test_credit_score_derogatory_mismatch_contradiction() -> None:
    docs = _load_documents("c0_contradiction_documents.yaml")
    fec = _adapter.run(docs, demo_policy_hash=_POLICY_HASH)

    assert "CREDIT_SCORE_DEROGATORY_MISMATCH" in fec.contradiction_flags
    assert fec.c0_state != C0_STATE_PASS


# ---------------------------------------------------------------------------
# 6 — malformed input returns FAIL, never raises
# ---------------------------------------------------------------------------

def test_malformed_input_returns_fail_contract_without_raising() -> None:
    docs = _load_documents("c0_malformed_documents.yaml")

    # The call itself is the assertion of fail-closed behavior (no raise).
    fec = _adapter.run(docs, demo_policy_hash=_POLICY_HASH)

    assert fec.c0_state == C0_STATE_FAIL
    assert fec.evidence_sufficiency == "insufficient"
    assert fec.open_web_blocked is True
    assert "C0_ADAPTER_INTERNAL_ERROR" not in fec.contradiction_flags, (
        "Ordinary malformed input must NOT use the internal-error flag."
    )
    # All required classes flagged missing via the structured form.
    for cls in ("BANK_STATEMENT", "TAX_RETURN", "CREDIT_REPORT"):
        assert f"MISSING_DOC:{cls}" in fec.missing_evidence_flags


def test_non_list_input_returns_fail() -> None:
    fec = _adapter.run("not a list", demo_policy_hash=_POLICY_HASH)  # type: ignore[arg-type]
    assert fec.c0_state == C0_STATE_FAIL
    assert fec.evidence_sufficiency == "insufficient"
    assert fec.open_web_blocked is True
    assert "C0_ADAPTER_INTERNAL_ERROR" not in fec.contradiction_flags


def test_non_dict_fields_value_does_not_crash() -> None:
    # `fields` is not a dict; the gate must not crash and must not extract it.
    docs = [
        {
            "document_class": "BANK_STATEMENT",
            "average_monthly_balance": 8500.0,
            "account_tenure_months": 36,
            "fields": "this is not a dict",
        },
        {"document_class": "TAX_RETURN", "annual_gross_income": 95000.0, "tax_year": 2025},
        {"document_class": "CREDIT_REPORT", "credit_score": 740, "derogatory_mark_count": 0},
    ]
    fec = _adapter.run(docs, demo_policy_hash=_POLICY_HASH)
    # BANK_STATEMENT top-level fields still extract fine.
    assert fec.c0_state == C0_STATE_PASS
    assert fec.open_web_blocked is True


# ---------------------------------------------------------------------------
# 7 — determinism: same input -> same contract id + evidence ids
# ---------------------------------------------------------------------------

def test_same_input_produces_same_ids_across_runs() -> None:
    docs = _load_documents("c0_full_pass_documents.yaml")

    fec_a = _adapter.run(docs, demo_policy_hash=_POLICY_HASH)
    fec_b = _adapter.run(copy.deepcopy(docs), demo_policy_hash=_POLICY_HASH)

    assert fec_a.evidence_contract_id == fec_b.evidence_contract_id
    assert fec_a.evidence_ids == fec_b.evidence_ids
    assert fec_a.support_score == fec_b.support_score
    assert fec_a.to_dict() == fec_b.to_dict()


# ---------------------------------------------------------------------------
# 8 — changing a submitted value changes evidence_contract_id
# ---------------------------------------------------------------------------

def test_changed_field_value_changes_contract_id() -> None:
    docs = _load_documents("c0_full_pass_documents.yaml")
    fec_original = _adapter.run(docs, demo_policy_hash=_POLICY_HASH)

    mutated = copy.deepcopy(docs)
    for doc in mutated:
        if doc.get("document_class") == "TAX_RETURN":
            doc["annual_gross_income"] = doc["annual_gross_income"] + 12345.0
            break
    fec_mutated = _adapter.run(mutated, demo_policy_hash=_POLICY_HASH)

    assert fec_mutated.evidence_contract_id != fec_original.evidence_contract_id, (
        "Changing a submitted field value MUST change evidence_contract_id "
        "(auditability: the ID binds to the actual submitted evidence)."
    )
    # The evidence_id for the changed span must also change (value-aware IDs).
    assert fec_mutated.evidence_ids != fec_original.evidence_ids


# ---------------------------------------------------------------------------
# 9 — falsy values are extracted, not silently dropped
# ---------------------------------------------------------------------------

def test_falsy_values_are_extracted() -> None:
    docs = [
        {
            "document_class": "BANK_STATEMENT",
            "average_monthly_balance": 8500.0,
            "account_tenure_months": 36,
            "overdraft_count_12m": 0,  # falsy but valid
        },
        {"document_class": "TAX_RETURN", "annual_gross_income": 95000.0, "tax_year": 2025},
        {
            "document_class": "CREDIT_REPORT",
            "credit_score": 740,
            "derogatory_mark_count": 0,  # falsy but valid
        },
        {
            "document_class": "IDENTITY_DOCUMENT",
            "id_type": "passport",
            "id_verified": False,  # falsy but valid
        },
    ]
    fec = _adapter.run(docs, demo_policy_hash=_POLICY_HASH)

    extracted = {
        (s["document_class"], s["field_name"]): s["value"]
        for s in fec.extracted_span_map.values()
    }
    assert extracted.get(("BANK_STATEMENT", "overdraft_count_12m")) == 0
    assert extracted.get(("CREDIT_REPORT", "derogatory_mark_count")) == 0
    assert extracted.get(("IDENTITY_DOCUMENT", "id_verified")) is False


# ---------------------------------------------------------------------------
# 10 — extracted_span_map contains only submitted (schema) fields
# ---------------------------------------------------------------------------

def test_extracted_spans_only_contain_submitted_schema_fields() -> None:
    docs = [
        {
            "document_class": "BANK_STATEMENT",
            "average_monthly_balance": 8500.0,
            "account_tenure_months": 36,
            "invented_external_risk_score": 0.99,  # not in schema -> must be ignored
        },
        {"document_class": "TAX_RETURN", "annual_gross_income": 95000.0, "tax_year": 2025},
        {"document_class": "CREDIT_REPORT", "credit_score": 740, "derogatory_mark_count": 0},
    ]
    fec = _adapter.run(docs, demo_policy_hash=_POLICY_HASH)

    field_names = {s["field_name"] for s in fec.extracted_span_map.values()}
    values = {s["value"] for s in fec.extracted_span_map.values()}
    assert "invented_external_risk_score" not in field_names, (
        "Unknown/inferred fields must never enter the contract."
    )
    assert 0.99 not in values
    # Every span keys back to its own id, and every id is in evidence_ids.
    for ev_id, span in fec.extracted_span_map.items():
        assert span["evidence_id"] == ev_id
        assert ev_id in fec.evidence_ids


# ---------------------------------------------------------------------------
# 11 — open_web_blocked is always true
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "fixture_name",
    [
        "c0_full_pass_documents.yaml",
        "c0_missing_bank_statement_documents.yaml",
        "c0_contradiction_documents.yaml",
        "c0_malformed_documents.yaml",
    ],
)
def test_open_web_blocked_is_always_true(fixture_name: str) -> None:
    docs = _load_documents(fixture_name)
    fec = _adapter.run(docs, demo_policy_hash=_POLICY_HASH)
    assert fec.open_web_blocked is True
    assert fec.c0_mode == "SUBMITTED_DOCUMENT_EVIDENCE_ONLY"


# ---------------------------------------------------------------------------
# 12 — firewall rejects fabricated evidence IDs + bundle guards
# ---------------------------------------------------------------------------

def _firewall():
    from apps_underwriting_ai.integrations.underwriting_llm_firewall import (
        UnderwritingLLMFirewall,
    )

    return UnderwritingLLMFirewall()


def _pass_bundle() -> dict[str, Any]:
    docs = _load_documents("c0_full_pass_documents.yaml")
    return _adapter.run(docs, demo_policy_hash=_POLICY_HASH).to_dict()


def test_firewall_accepts_rationale_citing_known_evidence_id() -> None:
    bundle = _pass_bundle()
    known_id = bundle["evidence_ids"][0]

    def _good_llm(artifact: Any) -> str:
        return f"Approved; supported by evidence {known_id} from the submitted packet."

    result = _firewall().gate(
        verdict="APPROVE",
        reason_codes=["RC001_INCOME_VERIFIED"],
        c0_bundle=bundle,
        deterministic_rationale="Approved on verified income.",
        request_id="req-fw-known",
        llm_callable=_good_llm,
    )
    assert result.firewall_passed is True
    assert result.deterministic_fallback_used is False
    assert known_id in result.rationale


def test_firewall_rejects_rationale_citing_fabricated_evidence_id() -> None:
    bundle = _pass_bundle()
    assert "ev-FAKE-deadbeef99" not in bundle["evidence_ids"]

    def _adversarial_llm(artifact: Any) -> str:
        return "Approved based on evidence ev-FAKE-deadbeef99 that was never submitted."

    result = _firewall().gate(
        verdict="APPROVE",
        reason_codes=["RC001_INCOME_VERIFIED"],
        c0_bundle=bundle,
        deterministic_rationale="Approved on verified income.",
        request_id="req-fw-fab",
        llm_callable=_adversarial_llm,
    )
    assert result.firewall_passed is False
    assert result.deterministic_fallback_used is True
    assert result.failure_reason == "unsupported_evidence_id"
    assert "ev-FAKE-deadbeef99" not in result.rationale
    assert result.rationale == "Approved on verified income."


def test_firewall_falls_back_when_bundle_missing_evidence_ids() -> None:
    bad_bundle = {
        "c0_mode": "SUBMITTED_DOCUMENT_EVIDENCE_ONLY",
        "open_web_blocked": True,
        # no evidence_ids key
    }

    def _llm(artifact: Any) -> str:
        return "some rationale"

    result = _firewall().gate(
        verdict="APPROVE",
        reason_codes=["RC001_INCOME_VERIFIED"],
        c0_bundle=bad_bundle,
        deterministic_rationale="Deterministic fallback.",
        request_id="req-fw-nobundle",
        llm_callable=_llm,
    )
    assert result.firewall_passed is False
    assert result.deterministic_fallback_used is True
    assert result.failure_reason == "invalid_c0_bundle"
    assert result.rationale == "Deterministic fallback."


def test_firewall_falls_back_when_open_web_not_blocked() -> None:
    bundle = _pass_bundle()
    bundle["open_web_blocked"] = False

    def _llm(artifact: Any) -> str:
        return "some rationale"

    result = _firewall().gate(
        verdict="APPROVE",
        reason_codes=["RC001_INCOME_VERIFIED"],
        c0_bundle=bundle,
        deterministic_rationale="Deterministic fallback.",
        request_id="req-fw-openweb",
        llm_callable=_llm,
    )
    assert result.firewall_passed is False
    assert result.deterministic_fallback_used is True
    assert result.failure_reason == "open_web_not_blocked"
    assert result.rationale == "Deterministic fallback."
