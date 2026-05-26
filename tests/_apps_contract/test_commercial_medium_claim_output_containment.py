"""Contract: claim_eligible MEDIUM commercial facts do not overclaim in bullet/narrative lanes."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from apps_rg.fact_inventory.validate_commercial_medium_claim_output_containment import (
    BULLET_NARRATIVE_SECTIONS,
    OUT_JSON,
    build_containment_payload,
)
from apps_rg.runtime.proof_pool_resolver import PROOF_SOURCE_AUGMENTED_SKILLS_GRAPH

REPO = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="module")
def containment() -> dict:
    return build_containment_payload()


def test_containment_status_pass(containment: dict) -> None:
    assert containment["status"] == "PASS", containment.get("violations")


@pytest.mark.parametrize("section_id", BULLET_NARRATIVE_SECTIONS)
def test_section_proof_pool_fixture_output(containment: dict, section_id: str) -> None:
    pool = containment["section_proof_pool_fixture_output"][section_id]
    assert pool["proof_source"] == PROOF_SOURCE_AUGMENTED_SKILLS_GRAPH
    assert pool["fact_count"] >= 1
    for row in pool["fixture_claim_texts"]:
        if row["confidence"] == "MEDIUM":
            assert row["source_trace_archive_relpaths"]


def test_report_json_on_disk() -> None:
    assert OUT_JSON.is_file()
    doc = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    assert doc["status"] == "PASS"
