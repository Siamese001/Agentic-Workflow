"""pa_core_law_v1 contract registry — SSOT for shared PA law referenced by section templates."""

from __future__ import annotations

from pathlib import Path

import yaml

from apps_rg.prompt_assembly.pa_core_law import (
    KNOWN_CONTRACT_IDS,
    load_pa_core_law_contract,
    load_pa_core_law_document,
    s0_truth_oath_reference_line,
)

REPO = Path(__file__).resolve().parents[4]
CONTRACT_PATH = REPO / "apps_rg" / "prompt_assembly" / "pa_core_law_v1.yaml"
TEMPLATE = (
    REPO / "apps_rg" / "prompt_assembly" / "templates" / "executive_summary.generate_scratch_v1.yaml"
)


def test_pa_core_law_v1_file_loads_all_contract_ids():
    doc = load_pa_core_law_document()
    assert doc.get("contract_id") == "pa_core_law_v1"
    contracts = doc.get("contracts") or {}
    for cid in KNOWN_CONTRACT_IDS:
        assert cid in contracts
        assert len(str(contracts[cid]).strip()) > 40


def test_load_pa_core_law_contract_roundtrip():
    body = load_pa_core_law_contract("pa_proof_binding_v1")
    assert "claim_ledger" in body
    assert "ALLOWED_SOURCE_FACT_IDS" in body


def test_s0_reference_line_satisfies_dual_validator_tokens():
    line = s0_truth_oath_reference_line()
    assert "NO FABRICATION" in line
    assert "pa_truth_oath_v1" in line


def test_executive_summary_template_references_pa_core_law_not_full_oath():
    raw = TEMPLATE.read_text(encoding="utf-8")
    assert "EXEC_SUMMARY_PROMPT_CORE_LAW_V3" in raw
    assert "pa_core_law_v1.yaml" in raw
    assert "forbidden_slot_body_source: strategic_tailor_v1" in raw
    assert raw.count("<proof_law_v1>") == 1
    i0_start = raw.index("<proof_law_v1>")
    i0_end = raw.index("</proof_law_v1>", i0_start)
    proof_body = raw[i0_start:i0_end]
    assert "pa_proof_binding_v1" in proof_body
    assert "PRODUCT_SHAPE" in proof_body
    assert len(proof_body.splitlines()) <= 12


def test_contract_yaml_parseable():
    data = yaml.safe_load(CONTRACT_PATH.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    assert data.get("schema_version") == "1.0"
