"""W10b — R1B UWG receipt governance ref parity."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from apps_rg.cache.r1b_store import R1BSemanticCacheStore
from apps_rg.cache.r1b_uwg_promotion import (
    AppsRgR1BUwgGateway,
    build_r1b_commit_bundle,
    promote_r1b_cache_via_uwg,
)
from apps_rg.cache.r1b_uwg_receipt_contract import (
    build_receipt_field_parity_matrix,
    document_r1b_uwg_core_receipt_gaps,
    validate_commit_request_governance,
)
from tests.unit.apps_rg.test_r1b_uwg_durable_persistence_w10 import (
    _candidate,
)


def _fake_cr_from(cr: object, **overrides: object) -> object:
    class _Fake:
        pass

    fake = _Fake()
    for k, v in cr.__dict__.items():
        setattr(fake, k, v)
    for k, v in overrides.items():
        setattr(fake, k, v)
    return fake


def test_validate_rejects_missing_l5(tmp_path: Path) -> None:
    cand = _candidate(tmp_path)
    cr, _, _, _ = build_r1b_commit_bundle(cand)
    result = validate_commit_request_governance(_fake_cr_from(cr, l5_certification_ref=""))
    assert result.valid is False
    assert "l5_certification_ref" in result.missing_fields


def test_validate_rejects_missing_gate_verdict(tmp_path: Path) -> None:
    cand = _candidate(tmp_path)
    cr, _, _, _ = build_r1b_commit_bundle(cand)
    result = validate_commit_request_governance(_fake_cr_from(cr, gate_verdict_refs=()))
    assert result.valid is False
    assert "gate_verdict_refs" in result.missing_fields


def test_promote_blocked_missing_l5(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from unittest.mock import patch

    monkeypatch.delenv("APPS_RG_R1B_SKIP_UWG", raising=False)
    cand = _candidate(tmp_path)
    cr, sds, rb, rf = build_r1b_commit_bundle(cand)
    with patch(
        "apps_rg.cache.r1b_uwg_promotion.build_r1b_commit_bundle",
        return_value=(_fake_cr_from(cr, l5_certification_ref=""), sds, rb, rf),
    ):
        outcome = promote_r1b_cache_via_uwg(cand, gateway=AppsRgR1BUwgGateway())
    assert outcome.status == "BLOCKED"
    assert "l5_certification_ref" in outcome.missing_contract_fields
    assert outcome.governance_receipt is not None


def test_promote_blocked_missing_gate_before_uwg(tmp_path: Path) -> None:
    from unittest.mock import patch

    cand = _candidate(tmp_path)
    cr, sds, rb, rf = build_r1b_commit_bundle(cand)
    with patch(
        "apps_rg.cache.r1b_uwg_promotion.build_r1b_commit_bundle",
        return_value=(_fake_cr_from(cr, gate_verdict_refs=()), sds, rb, rf),
    ):
        outcome = promote_r1b_cache_via_uwg(cand, gateway=AppsRgR1BUwgGateway())
    assert outcome.status == "BLOCKED"
    assert "gate_verdict_refs" in outcome.missing_contract_fields


def test_admitted_preserves_governance_receipt(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("APPS_RG_R1B_SKIP_UWG", raising=False)
    cand = _candidate(tmp_path)
    outcome = promote_r1b_cache_via_uwg(cand, gateway=AppsRgR1BUwgGateway())
    assert outcome.status == "ADMITTED"
    gov = outcome.governance_receipt or {}
    assert gov.get("l5_certification_ref")
    assert gov.get("gate_verdict_refs")
    assert gov.get("replay_key")
    assert gov.get("policy_hash") == "prompt_profile_w7_v1"
    assert gov.get("blueprint_hash") == "gate_profile_w7_v1"
    assert gov.get("source_surface") == "Exit"
    assert gov.get("core_receipt_l5_present") is True
    assert gov.get("core_receipt_gate_verdict_present") is True
    assert gov.get("core_receipt_policy_hash_present") is True
    assert gov.get("core_receipt_replay_key_present") is True
    assert "l4.apps_rg.r1b_semantic_cache" in (gov.get("affected_state_surfaces") or [])


def test_parity_matrix_and_core_receipt_gap_documented() -> None:
    matrix = build_receipt_field_parity_matrix()
    assert any(r["field"] == "l5_certification_ref" for r in matrix)
    assert all(r["uwg_commit_receipt_core"] is True for r in matrix)
    gaps = document_r1b_uwg_core_receipt_gaps()
    assert gaps["fields_core_cannot_carry"] == []
    assert gaps["fields_promotion_gateway_enriches"] == []
    assert "No active core receipt parity gap" in gaps["core_gap_summary"]


def test_admitted_projection_includes_governance_receipt(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from apps_rg.cache.r1b_uwg_promotion import promote_and_project_r1b_cache

    monkeypatch.delenv("APPS_RG_R1B_SKIP_UWG", raising=False)
    cand = _candidate(tmp_path)
    store = R1BSemanticCacheStore(tmp_path / "store")
    outcome = promote_and_project_r1b_cache(
        candidate=cand,
        projection_root=store.root,
        gateway=AppsRgR1BUwgGateway(),
        mirror_fixture_on_blocked=False,
    )
    assert outcome.status == "ADMITTED"
    intent = store.root / "durable" / "uwg_admitted" / "intents" / f"{cand.record.record_id}.json"
    bundle = json.loads(intent.read_text(encoding="utf-8"))
    assert bundle["governance_receipt"]["l5_certification_ref"]
