"""Headline normalize seam: SRFS fact-ID resolution, pool plan preservation, segment ledger."""

from __future__ import annotations

from apps_rg.runtime.sections.headline_lane import ensure_claim_ledger, normalize_parsed_output

CANONICAL_HL = (
    "SVP Engineering | Agentic AI Platforms | Distributed AI Infrastructure | Governed Enterprise Systems"
)


def test_ensure_claim_ledger_retain_aliases_preserves_bul_for_resolution() -> None:
    parsed = {
        "claim_ledger": [
            {"claim_text": "Governed Agentic Platforms", "source_fact_ids": ["bul_unify_001"]},
            {"claim_text": "Runtime Infrastructure", "source_fact_ids": ["bul_unify_002"]},
            {"claim_text": "Regulated Delivery", "source_fact_ids": ["bul_unify_003"]},
        ],
    }
    allowed = {"fact_engineering_platform_001", "fact_engineering_platform_003", "fact_engineering_platform_005"}
    ensure_claim_ledger(CANONICAL_HL, parsed, allowed, retain_bullet_aliases=True)
    ids = {fid for row in parsed["claim_ledger"] for fid in row["source_fact_ids"]}
    assert "bul_unify_001" in ids


def test_ensure_claim_ledger_coerces_flat_ids_to_xyz_segment_rows() -> None:
    parsed: dict = {"claim_ledger": ["bul_unify_001", "bul_unify_003"]}
    ensure_claim_ledger(CANONICAL_HL, parsed, {"bul_unify_001", "bul_unify_003"})
    ledger = parsed["claim_ledger"]
    assert len(ledger) == 3
    texts = {row["claim_text"] for row in ledger}
    assert "Agentic AI Platforms" in texts
    assert "Distributed AI Infrastructure" in texts
    assert "Governed Enterprise Systems" in texts
    for row in ledger:
        assert set(row["source_fact_ids"]) == {"bul_unify_001", "bul_unify_003"}


def test_normalize_applies_srfs_fact_id_resolution() -> None:
    allowed = {
        "fact_engineering_platform_001",
        "fact_engineering_platform_003",
        "fact_engineering_platform_005",
    }
    runtime_payload = {
        "selected_fact_plan": {
            "section_id": "headline",
            "facts": [{"fact_id": fid} for fid in sorted(allowed)],
            "required_fact_ids": [],
        },
        "proof_pool_metadata": {"proof_pool_type": "augmented_skills_graph"},
    }
    parsed = {
        "headline_line": CANONICAL_HL,
        "claim_ledger": [
            {"claim_text": "Agentic AI Platforms", "source_fact_ids": ["bul_unify_001"]},
            {"claim_text": "Distributed AI Infrastructure", "source_fact_ids": ["bul_unify_002"]},
            {"claim_text": "Governed Enterprise Systems", "source_fact_ids": ["bul_unify_003"]},
        ],
        "jd_alignment": {
            "targeting_only": True,
            "jd_used_as_proof": False,
            "briefing_used_as_proof": False,
        },
    }
    out = normalize_parsed_output(
        parsed,
        runtime_payload,
        allowed,
        CANONICAL_HL,
        proof_pool_metadata=runtime_payload["proof_pool_metadata"],
    )
    assert out is not None
    receipt = out.pop("fact_id_resolution_receipt")
    assert receipt["resolution_status"] == "PASS"
    ids = {
        fid
        for row in out["claim_ledger"]
        for fid in row["source_fact_ids"]
    }
    assert ids <= allowed
    assert ids == allowed


def test_ensure_claim_ledger_records_silent_row_drop() -> None:
    parsed: dict = {
        "claim_ledger": [
            {"claim_text": "theme", "source_fact_ids": ["bul_nope"]},
        ],
    }
    ensure_claim_ledger(CANONICAL_HL, parsed, {"bul_unify_001"})
    assert parsed.get("claim_ledger") == []
    assert parsed.get("_headline_ledger_rows_dropped") == 1


def test_normalize_does_not_expand_word_count_silently() -> None:
    short_hl = "SVP Engineering | Agentic AI Platforms | Distributed AI Infrastructure"
    runtime_payload = {
        "selected_fact_plan": {"section_id": "headline", "facts": [], "required_fact_ids": []},
    }
    parsed = {
        "headline_line": short_hl,
        "claim_ledger": [],
        "jd_alignment": {"targeting_only": True, "jd_used_as_proof": False, "briefing_used_as_proof": False},
    }
    out = normalize_parsed_output(parsed, runtime_payload, set(), short_hl)
    assert out is not None
    assert out["headline_line"] == short_hl
