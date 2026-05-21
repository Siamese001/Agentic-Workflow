"""Unit tests: SRFS emergency executive_summary five-sentence finalizer."""

from __future__ import annotations

from apps_rg.runtime.sections.exec_summary_srfs_emergency_finalizer import (
    apply_srfs_emergency_finalizer,
    build_srfs_five_sentence_finalizer,
    evaluate_finalizer_candidate,
)
from apps_rg.runtime.validators.executive_summary_x2 import (
    _resume_word_count,
    check_source_sensitive_phrases,
    check_srfs_density_word_count,
    check_srfs_sentence_responsibility_shape,
    split_sentences,
)


def _facts() -> list[dict[str, object]]:
    return [
        {
            "fact_id": "fact_engineering_platform_001",
            "claim_text": (
                "Designed and operationalized governed agentic AI platform capabilities for "
                "regulated enterprise workflows, including deterministic routing, multi-agent "
                "orchestration, GraphRAG retrieval, sandboxed execution, policy gating, validation "
                "controls, and replayable execution traces."
            ),
        },
        {
            "fact_id": "fact_engineering_platform_006",
            "claim_text": (
                "Productized agentic AI primitives into reusable platform services, generating "
                "$22M in IP-led revenue, expanding gross margins by 20%, and scaling the ML "
                "engineering organization from 8 to 28 specialists."
            ),
        },
        {
            "fact_id": "fact_governance_003",
            "claim_text": (
                "Implemented Basel III / CCAR data lineage, cataloging, and automated validation "
                "frameworks that cut regulatory reporting errors by 40%."
            ),
        },
        {
            "fact_id": "fact_certs_001",
            "claim_text": (
                "Holds AWS Certified Machine Learning Engineer - Associate, AWS Certified "
                "Solutions Architect - Professional, Databricks Lakehouse Fundamentals, and "
                "Fellow of the Society of Actuaries credentials."
            ),
        },
        {
            "fact_id": "fact_quant_hpc_003",
            "claim_text": (
                "Built advanced quantitative foundation through derivatives pricing, multi-Greek "
                "hedging, capital modeling, and FSA credential across Towers Perrin, ING, and Aetna."
            ),
        },
    ]


def _srfs() -> dict[str, object]:
    ids = [str(f["fact_id"]) for f in _facts()]
    return {
        "artifact_path_resolved": "artifacts/apps_rg/fact_inventory/selected_role_fact_set_active.json",
        "executive_summary_selected_fact_ids": ids,
    }


def _near_fail_parsed() -> dict[str, object]:
    text = (
        "Engineering executive with extensive experience in designing and operationalizing governed "
        "agentic AI platforms for regulated enterprise workflows. Led the full platform lifecycle, from "
        "architecture to commercialization, converting bespoke delivery into reusable services that "
        "generated $22M in IP-led revenue and expanded gross margins by 20%. Implemented robust "
        "governance frameworks, reducing regulatory reporting errors by 40%, and improved reliability "
        "and auditability of autonomous systems. Certified in AWS Machine Learning, Solutions "
        "Architecture, Databricks Lakehouse, and a Fellow of the Society of Actuaries, with advanced "
        "training in causal inference, statistics, and distributed systems engineering."
    )
    return {
        "resume_display_text": text,
        "claim_ledger": [
            {"claim_text": "s1", "source_fact_ids": ["fact_engineering_platform_001"]},
            {"claim_text": "s2", "source_fact_ids": ["fact_engineering_platform_006"]},
            {"claim_text": "s3", "source_fact_ids": ["fact_governance_003"]},
            {"claim_text": "s4", "source_fact_ids": ["fact_certs_001"]},
        ],
    }


def test_finalizer_expands_four_sentences_to_five_and_meets_density() -> None:
    srfs = _srfs()
    out, receipt = apply_srfs_emergency_finalizer(_near_fail_parsed(), srfs, selected_facts=_facts())
    assert receipt is not None
    assert receipt.get("triggered") is True
    assert receipt.get("candidate_accepted") is True
    text = out["resume_display_text"]
    assert len([s for s in split_sentences(text) if s.strip()]) == 5
    assert _resume_word_count(text) >= 95
    assert receipt["pre_word_count"] < 95 or receipt["pre_sentence_count"] == 4


def test_s2_has_no_dollar_after_finalizer() -> None:
    srfs = _srfs()
    out, _ = apply_srfs_emergency_finalizer(_near_fail_parsed(), srfs, selected_facts=_facts())
    s2 = split_sentences(out["resume_display_text"])[1]
    assert "$" not in s2


def test_governance_frameworks_replaced() -> None:
    srfs = _srfs()
    out, receipt = apply_srfs_emergency_finalizer(_near_fail_parsed(), srfs, selected_facts=_facts())
    low = out["resume_display_text"].lower()
    assert "governance frameworks" not in low
    assert "basel iii" in low
    assert receipt and receipt.get("removed_sensitive_phrases")


def test_unsupported_training_phrase_removed() -> None:
    srfs = _srfs()
    out, receipt = apply_srfs_emergency_finalizer(_near_fail_parsed(), srfs, selected_facts=_facts())
    low = out["resume_display_text"].lower()
    assert "causal inference" not in low
    assert "distributed systems engineering" not in low
    assert receipt and receipt.get("unsupported_phrases_removed")


def test_s5_credentials_integrated() -> None:
    srfs = _srfs()
    out, receipt = apply_srfs_emergency_finalizer(_near_fail_parsed(), srfs, selected_facts=_facts())
    s5 = split_sentences(out["resume_display_text"])[-1].lower()
    assert "aws certified" in s5 or "fellow of the society" in s5
    assert receipt and receipt.get("s5_credentials_integrated") is True


def test_finalizer_rejects_out_of_slice_fact_ids() -> None:
    srfs = _srfs()
    sentences, ledger, _ = build_srfs_five_sentence_finalizer(_facts(), srfs)
    assert sentences and ledger
    candidate = {
        "resume_display_text": " ".join(sentences),
        "claim_ledger": ledger,
    }
    ledger[0]["source_fact_ids"] = ["fact_out_of_slice_999"]
    eval_result = evaluate_finalizer_candidate(
        _near_fail_parsed(),
        candidate,
        _facts(),
        srfs,
        trigger_failed_gates=["x2_exec_summary_srfs_density_word_count"],
    )
    assert eval_result["candidate_accepted"] is False
    assert "out_of_slice" in (eval_result.get("rejection_reason") or "")


def test_receipt_records_before_after_and_chosen_source() -> None:
    srfs = _srfs()
    out, receipt = apply_srfs_emergency_finalizer(_near_fail_parsed(), srfs, selected_facts=_facts())
    assert receipt
    assert "pre_word_count" in receipt
    assert "post_word_count" in receipt
    assert receipt["chosen_text_source"] == "finalizer_candidate"
    assert receipt["x2_before"]["failed_gates"]
    assert receipt["x2_after"]["failed_gates"] == []


def test_built_summary_passes_target_x2_gates() -> None:
    srfs = _srfs()
    sentences, ledger, _ = build_srfs_five_sentence_finalizer(_facts(), srfs)
    text = " ".join(sentences)
    parsed = {"resume_display_text": text, "claim_ledger": ledger}
    assert check_srfs_density_word_count(text, parsed, srfs)[0]
    assert check_srfs_sentence_responsibility_shape(text, srfs)[0]
    assert check_source_sensitive_phrases(text, _facts())[0]
