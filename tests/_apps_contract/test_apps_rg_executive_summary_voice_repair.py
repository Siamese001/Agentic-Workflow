"""Contract tests for executive_summary deterministic voice repair."""

from __future__ import annotations

from apps_rg.runtime.sections.executive_summary_voice_repair import (
    apply_voice_repair_to_parsed,
    finalize_executive_summary_coherence,
    repair_generic_filler_prose,
)
from apps_rg.runtime.validators.executive_summary_x2 import (
    check_claim_ledger_materialized_or_gap_excused,
)


def test_repair_strips_proven_track_record_opener() -> None:
    text = (
        "An engineering executive with a proven track record in delivering governed "
        "enterprise AI platforms and advanced quantitative foundations."
    )
    repaired, receipt = repair_generic_filler_prose(text)
    assert receipt["repaired"] is True
    assert "proven track record" not in repaired.lower()


def test_repair_clears_bridge_phrase_without_fact_support() -> None:
    text = "Engineering executive delivering platforms with depth in regulated programs."
    repaired, receipt = repair_generic_filler_prose(text, selected_facts=[])
    assert receipt["post_repair_bridge_ok"] is True
    assert "proven track record" not in repaired.lower()


def test_repair_meta_filler_and_sensitive_phrases() -> None:
    text = (
        "An engineering executive with extensive experience in scaling teams for "
        "regulated environments, implementing governance frameworks."
    )
    facts = [
        {
            "claim_text": (
                "Designed governed agentic AI for regulated enterprise workflows "
                "with Basel III/CCAR data lineage frameworks."
            )
        }
    ]
    repaired, receipt = repair_generic_filler_prose(text, selected_facts=facts)
    assert receipt["repaired"] is True
    assert "extensive experience" not in repaired.lower()
    assert "regulated environments" not in repaired.lower()


def test_finalize_excuses_orphan_ledger_after_credential_strip() -> None:
    """Simulate authority strip: 4-sentence display, 5-row ledger with cred tail."""
    display = (
        "Led platform work for regulated enterprises. "
        "Generated $22M IP-led revenue. "
        "Implemented Basel III/CCAR lineage cutting errors by 40%. "
        "Re-architected risk analytics with HPC."
    )
    ledger = [
        {"claim_text": "Led platform work.", "source_fact_ids": ["fact_engineering_platform_001"]},
        {"claim_text": "Generated $22M revenue.", "source_fact_ids": ["fact_engineering_platform_006"]},
        {"claim_text": "Basel lineage cut errors 40%.", "source_fact_ids": ["fact_governance_003"]},
        {"claim_text": "Re-architected risk analytics HPC.", "source_fact_ids": ["fact_quant_hpc_001"]},
        {
            "claim_text": "Holds AWS Certified and Databricks credentials.",
            "source_fact_ids": ["fact_certs_001"],
        },
    ]
    parsed = {
        "resume_display_text": display,
        "claim_ledger": ledger,
        "gap_notes": [],
    }
    out, receipt = finalize_executive_summary_coherence(parsed)
    assert receipt["materialization_pass"] is True
    mat_ok, _ = check_claim_ledger_materialized_or_gap_excused(
        str(out.get("resume_display_text") or ""),
        list(out.get("claim_ledger") or []),
        list(out.get("gap_notes") or []),
    )
    assert mat_ok is True
    assert any("fact_certs_001" in str(g) for g in (out.get("gap_notes") or []))


def test_repair_strips_additionally_opener() -> None:
    text = (
        "Led platform delivery. Built governance controls. "
        "Additionally, re-architected risk analytics with HPC."
    )
    repaired, receipt = repair_generic_filler_prose(text)
    assert "additionally" not in repaired.lower()
    assert receipt["repaired"] is True


def test_apply_voice_repair_to_parsed_updates_display_text() -> None:
    parsed = {
        "resume_display_text": "An engineering executive with a proven track record in delivering AI platforms.",
        "claim_ledger": [],
    }
    out, receipt = apply_voice_repair_to_parsed(parsed)
    assert receipt["repaired"] is True
    assert "proven track record" not in str(out.get("resume_display_text") or "").lower()
