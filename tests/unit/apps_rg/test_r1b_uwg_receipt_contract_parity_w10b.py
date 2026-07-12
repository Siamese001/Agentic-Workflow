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
from tests.unit.apps_rg.test_r1b_uwg_durable_persistence_w10 import _candidate


def _fake_cr_from(cr: object, **overrides: object) -> object:
    class _Fake:
        pass

    fake = _Fake()
    for key, value in cr.__dict__.items():
        setattr(fake, key, value)
    for key, value in overrides.items():
        setattr(fake, key, value)
    return fake


def test_validate_rejects_missing_l5(tmp_path: Path) -> None:
    candidate = _candidate(tmp_path)
    commit_request, _, _, _ = build_r1b_commit_bundle(candidate)
    result = validate_commit_request_governance(
        _fake_cr_from(commit_request, l5_certification_ref="")
    )
    assert result.valid is False
    assert "l5_certification_ref" in result.missing_fields


def test_validate_rejects_missing_packet_verification(tmp_path: Path) -> None:
    candidate = _candidate(tmp_path)
    commit_request, _, _, _ = build_r1b_commit_bundle(candidate)
    refs = tuple(
        ref
        for ref in commit_request.l5_certification_refs
        if not str(ref).startswith("verification_digest=")
    )
    result = validate_commit_request_governance(
        _fake_cr_from(commit_request, l5_certification_refs=refs)
    )
    assert result.valid is False
    assert "l5_certification_refs.verification_digest" in result.missing_fields


def test_validate_rejects_missing_gate_verdict(tmp_path: Path) -> None:
    candidate = _candidate(tmp_path)
    commit_request, _, _, _ = build_r1b_commit_bundle(candidate)
    result = validate_commit_request_governance(
        _fake_cr_from(commit_request, gate_verdict_refs=())
    )
    assert result.valid is False
    assert "gate_verdict_refs" in result.missing_fields


def test_promote_blocked_missing_l5(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from unittest.mock import patch

    monkeypatch.delenv("APPS_RG_R1B_SKIP_UWG", raising=False)
    candidate = _candidate(tmp_path)
    commit_request, state_diffs, rollback, refresh = build_r1b_commit_bundle(candidate)
    with patch(
        "apps_rg.cache.r1b_uwg_promotion.build_r1b_commit_bundle",
        return_value=(
            _fake_cr_from(commit_request, l5_certification_ref=""),
            state_diffs,
            rollback,
            refresh,
        ),
    ):
        outcome = promote_r1b_cache_via_uwg(candidate, gateway=AppsRgR1BUwgGateway())
    assert outcome.status == "BLOCKED"
    assert "l5_certification_ref" in outcome.missing_contract_fields
    assert outcome.governance_receipt is not None


def test_promote_blocked_missing_gate_before_uwg(tmp_path: Path) -> None:
    from unittest.mock import patch

    candidate = _candidate(tmp_path)
    commit_request, state_diffs, rollback, refresh = build_r1b_commit_bundle(candidate)
    with patch(
        "apps_rg.cache.r1b_uwg_promotion.build_r1b_commit_bundle",
        return_value=(
            _fake_cr_from(commit_request, gate_verdict_refs=()),
            state_diffs,
            rollback,
            refresh,
        ),
    ):
        outcome = promote_r1b_cache_via_uwg(candidate, gateway=AppsRgR1BUwgGateway())
    assert outcome.status == "BLOCKED"
    assert "gate_verdict_refs" in outcome.missing_contract_fields


def test_admitted_preserves_governance_receipt(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("APPS_RG_R1B_SKIP_UWG", raising=False)
    candidate = _candidate(tmp_path)
    outcome = promote_r1b_cache_via_uwg(candidate, gateway=AppsRgR1BUwgGateway())
    assert outcome.status == "ADMITTED"
    governance = outcome.governance_receipt or {}
    assert governance.get("l5_certification_ref")
    assert governance.get("l5_certification_packet_digest")
    assert governance.get("l5_certification_verified") is True
    assert governance.get("l5_certification_verification_digest")
    assert governance.get("gate_verdict_refs")
    assert governance.get("replay_key")
    assert governance.get("policy_hash") == "prompt_profile_w7_v1"
    assert governance.get("blueprint_hash") == "gate_profile_w7_v1"
    assert governance.get("source_surface") == "Exit"
    assert governance.get("core_receipt_l5_present") is True
    assert governance.get("core_receipt_gate_verdict_present") is True
    assert governance.get("core_receipt_policy_hash_present") is True
    assert governance.get("core_receipt_replay_key_present") is True
    assert "l4.apps_rg.r1b_semantic_cache" in (
        governance.get("affected_state_surfaces") or []
    )


def test_parity_matrix_and_core_receipt_gap_documented() -> None:
    matrix = build_receipt_field_parity_matrix()
    assert any(row["field"] == "l5_certification_ref" for row in matrix)
    assert all(row["uwg_commit_receipt_core"] is True for row in matrix)
    gaps = document_r1b_uwg_core_receipt_gaps()
    assert gaps["fields_core_cannot_carry"] == []
    assert "l5_certification_packet_digest" in gaps["fields_promotion_gateway_enriches"]
    assert "No active core receipt parity gap" in gaps["core_gap_summary"]


def test_admitted_projection_includes_governance_receipt(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from apps_rg.cache.r1b_uwg_promotion import promote_and_project_r1b_cache

    monkeypatch.delenv("APPS_RG_R1B_SKIP_UWG", raising=False)
    candidate = _candidate(tmp_path)
    store = R1BSemanticCacheStore(tmp_path / "store")
    outcome = promote_and_project_r1b_cache(
        candidate=candidate,
        projection_root=store.root,
        gateway=AppsRgR1BUwgGateway(),
        mirror_fixture_on_blocked=False,
    )
    assert outcome.status == "ADMITTED"
    intent = (
        store.root
        / "durable"
        / "uwg_admitted"
        / "intents"
        / f"{candidate.record.record_id}.json"
    )
    bundle = json.loads(intent.read_text(encoding="utf-8"))
    assert bundle["governance_receipt"]["l5_certification_ref"]
    assert bundle["governance_receipt"]["l5_certification_verified"] is True
