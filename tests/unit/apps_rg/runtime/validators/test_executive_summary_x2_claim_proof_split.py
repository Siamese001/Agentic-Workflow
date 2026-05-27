"""W2.4 — X2 matches claim_text only; proof_text is ledger provenance, not X2 materialization."""

from __future__ import annotations

import json
from pathlib import Path

from apps_rg.fact_inventory.candidate_fact_ledger import load_master_candidate_fact_ledger
from apps_rg.fact_inventory.claim_proof_split_policy import (
    CLAIM_PROOF_SCHEMA_VERSION,
    validate_claim_proof_row,
)
from apps_rg.runtime.validators import executive_summary_x2 as x2

REPO_ROOT = Path(__file__).resolve().parents[5]
W2_FACT_IDS = ("fact_engineering_platform_001", "fact_quant_hpc_003")


def test_x2_module_never_references_proof_text() -> None:
    source_path = Path(x2.__file__)
    source = source_path.read_text(encoding="utf-8")
    assert "proof_text" not in source


def test_ledger_claim_tokens_use_claim_text_only() -> None:
    tokens = x2._ledger_claim_tokens(
        "Designed and operationalized a governed agentic AI platform for regulated enterprise workflows."
    )
    assert tokens
    assert "graphrag" not in tokens


def test_w2_migrated_facts_pass_claim_proof_audit() -> None:
    payload = load_master_candidate_fact_ledger(repo_root=REPO_ROOT)
    by_id = {
        str(row.get("candidate_fact_id")): row
        for row in (payload.get("candidate_facts") or [])
        if isinstance(row, dict)
    }
    for fid in W2_FACT_IDS:
        row = by_id[fid]
        assert row.get("proof_text"), fid
        assert row.get("claim_proof_split_version") == CLAIM_PROOF_SCHEMA_VERSION
        assert validate_claim_proof_row(row) == []


def test_row_sentence_match_prefers_display_claim_over_fact_claim_text() -> None:
    sentence = "Governed platform delivery with audit-ready execution."
    row = {
        "claim": sentence,
        "claim_text": (
            "Designed and operationalized governed agentic AI platform capabilities for regulated "
            "enterprise workflows, including deterministic routing, multi-agent orchestration."
        ),
        "proof_text": "full provenance body not used by X2",
    }
    assert x2._row_sentence_match_strength(sentence, row) >= 90


def test_srfs_executive_summary_w2_facts_have_split() -> None:
    srfs_path = REPO_ROOT / "artifacts/apps_rg/fact_inventory/selected_role_fact_set_active.json"
    srfs = json.loads(srfs_path.read_text(encoding="utf-8"))
    exec_rows = (srfs.get("selected_facts_by_section") or {}).get("executive_summary") or []
    by_id = {str(r.get("candidate_fact_id")): r for r in exec_rows if isinstance(r, dict)}
    for fid in W2_FACT_IDS:
        row = by_id[fid]
        assert validate_claim_proof_row(row) == [], fid
