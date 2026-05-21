"""Unit tests for SRFS executive_summary judge-safe repair (zero-loss arc fixes)."""

from __future__ import annotations

from apps_rg.runtime.sections.exec_summary_srfs_judge_safe import (
    _sentence_s1_s2_capability_redundant,
    _sentence_s3_has_unsupported_embellishment,
    _apply_srfs_judge_safe_repair_core,
    build_fact_tight_s2_sentence,
    build_fact_tight_s3_sentence,
    build_fact_tight_s4_sentence,
)


def _srfs_slice() -> dict[str, object]:
    return {
        "artifact_path_resolved": "artifacts/apps_rg/fact_inventory/test_srfs.json",
        "executive_summary_selected_fact_ids": [
            "fact_engineering_platform_001",
            "fact_engineering_platform_004",
            "fact_engineering_platform_004_metric_06dd515f",
            "fact_governance_003",
            "fact_exec_002",
            "fact_certs_001",
            "fact_quant_hpc_003",
        ],
    }


def _production_like_facts() -> list[dict[str, object]]:
    return [
        {
            "fact_id": "fact_engineering_platform_001",
            "claim_text": (
                "Architected governed agentic AI platforms with deterministic routing, "
                "multi-agent orchestration, GraphRAG retrieval, sandboxed execution, "
                "policy gating, and validation controls."
            ),
        },
        {
            "fact_id": "fact_engineering_platform_004",
            "claim_text": (
                "Leads the full platform lifecycle, converting bespoke delivery into "
                "reusable services adopted across enterprise programs."
            ),
        },
        {
            "fact_id": "fact_engineering_platform_004_metric_06dd515f",
            "claim_text": (
                "Standardized AI lifecycle practices across intake, validation, execution, "
                "monitoring, and remediation, reducing lab-to-production cycle time from "
                "six months to three weeks while preserving auditability and runtime stability."
            ),
            "metric_values": ["6 months to 3 weeks"],
        },
        {
            "fact_id": "fact_governance_003",
            "claim_text": (
                "Implemented Basel III / CCAR data lineage, cataloging, and automated "
                "validation frameworks that cut regulatory reporting errors by 40%."
            ),
        },
        {
            "fact_id": "fact_exec_002",
            "claim_text": (
                "Scaled ML engineering organization from 8 to 28 specialists, including "
                "senior engineers and platform leads."
            ),
        },
        {
            "fact_id": "fact_certs_001",
            "claim_text": "Holds AWS Certified Machine Learning Engineer and FSA credentials.",
        },
        {
            "fact_id": "fact_quant_hpc_003",
            "claim_text": (
                "Built advanced quantitative foundation through derivatives pricing and FSA credential."
            ),
        },
    ]


def test_repair_preserves_platform_004_cycle_metric_in_s4() -> None:
    """Regression: six-month to three-week metric must survive judge-safe repair."""
    facts = _production_like_facts()
    srfs = _srfs_slice()
    slice_ids = frozenset(srfs["executive_summary_selected_fact_ids"])  # type: ignore[index]

    parsed = {
        "resume_display_text": (
            "Engineering executive building governed agentic AI platforms for regulated "
            "enterprise environments. "
            "Designs and operationalizes deterministic routing, multi-agent orchestration, "
            "GraphRAG retrieval, sandboxed execution, policy gating, and validation controls "
            "for regulated enterprise workflows. "
            "Leads platform lifecycle across architecture, operating model, and engineering "
            "scale-out, and implements Basel III and CCAR data lineage, cataloging, and "
            "automated validation frameworks that cut regulatory reporting errors by 40%. "
            "Scaled ML engineering organization from 8 to 28 specialists, including senior "
            "engineers and platform leads. "
            "Brings AWS, Databricks, and FSA credentials together with derivatives pricing "
            "and capital modeling experience to strengthen enterprise risk discipline on "
            "regulated platform programs."
        ),
        "claim_ledger": [
            {"claim_text": "s1", "source_fact_ids": ["fact_engineering_platform_001"]},
            {"claim_text": "s2", "source_fact_ids": ["fact_engineering_platform_001"]},
            {
                "claim_text": "s3",
                "source_fact_ids": ["fact_engineering_platform_001", "fact_governance_003"],
            },
            {"claim_text": "s4", "source_fact_ids": ["fact_exec_002"]},
            {"claim_text": "s5", "source_fact_ids": ["fact_certs_001", "fact_quant_hpc_003"]},
        ],
    }

    out = _apply_srfs_judge_safe_repair_core(parsed, facts, srfs)
    text = out["resume_display_text"].lower()
    assert "six months" in text or "6 months" in text
    assert "three weeks" in text or "3 weeks" in text
    assert "$22m" not in text
    assert "gross margin" not in text
    parts = [p.strip() for p in out["resume_display_text"].split(".") if p.strip()]
    assert len(parts) >= 4
    assert "basel" not in parts[2].lower()

    s4_ids = out["claim_ledger"][3]["source_fact_ids"]
    assert "fact_engineering_platform_004" in s4_ids or any(
        str(x).startswith("fact_engineering_platform_004") for x in s4_ids
    )
    for fid in (out.get("claim_ledger") or []):
        for sid in fid.get("source_fact_ids") or []:
            assert sid in slice_ids or sid.split("_metric_", 1)[0] in slice_ids


def test_s1_s2_not_duplicate_capability_stack_after_repair() -> None:
    facts = _production_like_facts()
    srfs = _srfs_slice()
    s1 = (
        "Engineering executive building governed agentic AI platforms for "
        "regulated enterprise environments."
    )
    s2_bad = (
        "Designs and operationalizes deterministic routing, multi-agent orchestration, "
        "GraphRAG retrieval, sandboxed execution, policy gating, and validation controls "
        "for regulated enterprise workflows."
    )
    assert _sentence_s1_s2_capability_redundant(s1, s2_bad)

    parsed = {
        "resume_display_text": " ".join(
            [
                s1,
                s2_bad,
                "Leads platform lifecycle across architecture, operating model, and engineering "
                "scale-out, and implements Basel III and CCAR frameworks that cut regulatory "
                "reporting errors by 40%.",
                "Standardized AI lifecycle practices, reducing lab-to-production cycle time "
                "from six months to three weeks while preserving auditability.",
                "Brings AWS, Databricks, and FSA credentials to strengthen enterprise risk "
                "discipline on regulated platform programs.",
            ]
        ),
        "claim_ledger": [{"claim_text": f"s{i}", "source_fact_ids": []} for i in range(5)],
    }
    out = _apply_srfs_judge_safe_repair_core(parsed, facts, srfs)
    parts = [p.strip() for p in out["resume_display_text"].split(".") if p.strip()]
    assert len(parts) >= 2
    s2_out = parts[1].lower()
    assert "deterministic routing" not in s2_out or "basel" in s2_out or "ccar" in s2_out
    assert not _sentence_s1_s2_capability_redundant(parts[0], parts[1])


def test_claim_ledger_source_fact_ids_stay_in_srfs_slice() -> None:
    facts = _production_like_facts()
    srfs = _srfs_slice()
    allowed = frozenset(srfs["executive_summary_selected_fact_ids"])  # type: ignore[index]

    parsed = {
        "resume_display_text": (
            "Engineering executive building governed agentic AI platforms for regulated "
            "enterprise environments. Designs governed platform execution. Leads lifecycle. "
            "Delivers six months to three weeks outcomes. Brings AWS and FSA credentials."
        ),
        "claim_ledger": [
            {"claim_text": "a", "source_fact_ids": ["fact_engineering_platform_001"]},
            {"claim_text": "b", "source_fact_ids": ["fact_out_of_slice_999"]},
            {"claim_text": "c", "source_fact_ids": ["fact_engineering_platform_004"]},
            {"claim_text": "d", "source_fact_ids": ["fact_engineering_platform_004_metric_06dd515f"]},
            {"claim_text": "e", "source_fact_ids": ["fact_certs_001"]},
        ],
    }
    out = _apply_srfs_judge_safe_repair_core(parsed, facts, srfs)
    for row in out.get("claim_ledger") or []:
        for fid in row.get("source_fact_ids") or []:
            base = str(fid).split("_metric_", 1)[0]
            assert fid in allowed or base in allowed, (
                f"out-of-slice id emitted: {fid}"
            )


def test_build_fact_tight_s4_prefers_cycle_metric_row() -> None:
    facts = _production_like_facts()
    s4 = build_fact_tight_s4_sentence(facts)
    low = s4.lower()
    assert "six months" in low or "6 months" in low
    assert "three weeks" in low or "3 weeks" in low


def test_s2_preserves_40_percent_governance_metric() -> None:
    facts = _production_like_facts()
    s2 = build_fact_tight_s2_sentence(facts)
    assert "40%" in s2


def test_s3_tight_to_srfs_without_embellishment_or_cycle_metric() -> None:
    facts = _production_like_facts()
    blob = " ".join(str(f.get("claim_text") or "") for f in facts).lower()
    s3 = build_fact_tight_s3_sentence(facts)
    low = s3.lower()
    assert "operating model scale-out" not in low or "operating model scale-out" in blob
    assert not _sentence_s3_has_unsupported_embellishment(s3, blob)
    assert "six months" not in low and "three weeks" not in low
    assert (
        "lifecycle" in low
        or "regulated enterprise workflows" in low
        or "leads the full platform lifecycle" in low
    )


def test_repair_splits_combined_platform_004_across_s3_and_s4() -> None:
    """Live SRFS shape: platform_004 claim_text carries both lifecycle and cycle metric."""
    facts = _production_like_facts()
    for row in facts:
        if row["fact_id"] == "fact_engineering_platform_004":
            row["claim_text"] = (
                "Standardized AI lifecycle practices across intake, validation, execution, "
                "monitoring, and remediation, reducing lab-to-production cycle time from "
                "six months to three weeks while preserving auditability and runtime stability."
            )
            break
    srfs = _srfs_slice()
    parsed = {
        "resume_display_text": (
            "Engineering executive building governed agentic AI platforms for regulated "
            "enterprise environments. "
            "Implements Basel III and CCAR data lineage, cataloging, and automated validation "
            "frameworks that cut regulatory reporting errors and strengthen auditability. "
            "Leads the full platform lifecycle, converting bespoke delivery into reusable "
            "services adopted across enterprise programs, through operating model scale-out "
            "and enterprise program adoption. "
            "Standardized AI lifecycle practices across intake, validation, execution, "
            "monitoring, and remediation, reducing lab-to-production cycle time from six "
            "months to three weeks while preserving auditability and runtime stability. "
            "Brings AWS, Databricks, and FSA credentials to strengthen enterprise risk "
            "discipline on regulated platform programs."
        ),
        "claim_ledger": [{"claim_text": f"s{i}", "source_fact_ids": []} for i in range(5)],
    }
    out = _apply_srfs_judge_safe_repair_core(parsed, facts, srfs)
    parts = [p.strip() for p in out["resume_display_text"].split(".") if p.strip()]
    assert len(parts) >= 4
    assert "40%" in parts[1]
    assert "integrating identity controls" not in parts[1].lower()
    s3_low = parts[2].lower()
    assert "six months" not in s3_low and "three weeks" not in s3_low
    assert "operating model scale-out" not in s3_low
    assert (
        "regulated enterprise workflows" in s3_low
        or "lifecycle" in s3_low
        or "8 to 28" in s3_low
        or "28 specialists" in s3_low
    )
    s4_low = parts[3].lower()
    assert "six months" in s4_low or "6 months" in s4_low
    assert "three weeks" in s4_low or "3 weeks" in s4_low


def test_four_sentence_srfs_s3_and_s4_use_distinct_indices() -> None:
    """Regression: len==4 must not alias s3_idx and s4_idx (duplicate lifecycle lines)."""
    facts = _production_like_facts()
    srfs = _srfs_slice()
    parsed = {
        "resume_display_text": (
            "Engineering executive building governed agentic AI platforms for regulated "
            "enterprise environments. "
            "Implemented Basel III / CCAR data lineage, cataloging, and automated validation "
            "frameworks that cut regulatory reporting errors by 40%. "
            "Standardized AI lifecycle practices across intake, validation, execution, "
            "monitoring, and remediation, reducing lab-to-production cycle time from six "
            "months to three weeks while preserving auditability and runtime stability. "
            "Brings AWS, Databricks, and FSA credentials to strengthen enterprise risk "
            "discipline on regulated platform programs."
        ),
        "claim_ledger": [{"claim_text": f"s{i}", "source_fact_ids": []} for i in range(4)],
    }
    out = _apply_srfs_judge_safe_repair_core(parsed, facts, srfs)
    parts = [p.strip() for p in out["resume_display_text"].split(".") if p.strip()]
    assert len(parts) == 4
    s3_low, s4_low = parts[2].lower(), parts[3].lower()
    assert "six months" not in s3_low and "three weeks" not in s3_low
    assert "six months" in s4_low or "6 months" in s4_low
    assert "three weeks" in s4_low or "3 weeks" in s4_low
    assert "reducing lab-to-production" in s4_low or "six months" in s4_low
    if "standardized ai lifecycle" in s3_low and "standardized ai lifecycle" in s4_low:
        assert s4_low.startswith("reducing") or "six months" in s4_low
    assert "standardized ai lifecycle" in s3_low or "intake" in s3_low
    assert "standardized ai lifecycle" in s4_low or "reducing lab-to-production" in s4_low
