"""W3.0 — headline fact_id resolution must not duplicate shared typo repair without ledger."""

from __future__ import annotations

from apps_rg.runtime.sections import headline_fact_id_resolution


def test_headline_fact_id_resolution_exposes_apply_helper() -> None:
    assert hasattr(headline_fact_id_resolution, "apply_headline_claim_ledger_fact_id_resolution")
