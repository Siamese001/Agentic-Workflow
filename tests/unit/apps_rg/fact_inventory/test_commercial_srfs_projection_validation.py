"""Contract: commercial skills SRFS projection validation harness."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from apps_rg.fact_inventory.validate_commercial_srfs_projection import (
    REJECTED_FACT_IDS,
    build_validation_payload,
)

REPO = Path(__file__).resolve().parents[4]
OUT_JSON = REPO / "docs/reports/apps_rg/commercial_skills_srfs_projection_validation.json"


def test_commercial_srfs_projection_validation_passes() -> None:
    payload = build_validation_payload()
    assert payload["status"] == "PASS", payload.get("violations")
    auth = set(payload["authoritative_claim_pool_fact_ids"])
    assert not auth & REJECTED_FACT_IDS
    medium = set(payload["medium_confirmation_queue_fact_ids"])
    claim_reg = set(payload.get("claim_eligible_medium_registry_ids") or [])
    if claim_reg:
        assert "fact_sales_accounts_002" not in medium
        assert payload.get("authoritative_commercial_fact_ids")
    else:
        assert "fact_sales_accounts_002" in medium
    archive = set(payload["composite_projection"]["archive_only_context_skill_ids"])
    assert "skill_customer_nrr_predictive_analytics_20pct" in archive
    assert "skill_customer_satisfaction_nps_25pct" in archive
    assert payload["archive_only_context"]["in_authoritative_fact_pool"] == []


def test_validation_report_on_disk() -> None:
    assert OUT_JSON.is_file()
    on_disk = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    assert on_disk["status"] in ("PASS", "FAIL")
