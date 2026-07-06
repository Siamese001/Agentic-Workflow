"""apps_rg L0 routing hardening micro-evals.

apps-test-model: APP CONTRACT
"""

from __future__ import annotations

import copy
import json

import pytest

from agentic_core.runtime.contracts.l1_plan_contract import L1PlanContract
from apps_rg.runtime.bindings import l0_binding
from apps_rg.runtime.bindings.l0_binding import (
    RouteProfileSchemaError,
    l0_route_apps_rg,
    reset_route_profiles_cache,
)
from apps_rg.runtime.bindings.l0_route_evidence import (
    RouteSigningSecretMissingError,
    serialize_l0_route_artifact,
)


def _plan(**overrides: object) -> L1PlanContract:
    data: dict[str, object] = {
        "request_id": "req-l0-hardening",
        "run_id": "run-l0-hardening",
        "app_id": "apps_rg",
        "trace_id": "trace-l0-hardening",
        "task_spec": {"generation_mode": "strategic_tailor"},
        "query_spec": {
            "jd_hash": "j" * 64,
            "resume_hash": "r" * 64,
        },
        "support_expectation": {"min_quality": 0.80},
        "grounding_required": True,
        "model_generation_required": True,
        "write_authority_present": False,
        "tenant_id": "apps_rg",
        "merge_required_hint": True,
        "l5_certification_ref": "test-cert-ref",
        "replay_key": "replay::l0-hardening::v1",
    }
    data.update(overrides)
    return L1PlanContract(**data)


def test_route_profiles_expose_canonical_vocabulary_and_activation_metadata() -> None:
    rows = l0_binding._load_profiles()
    assert rows
    canonical = {row["spine"]["canonical_route_id"] for row in rows}
    assert {
        "R1A_EXACT_CACHE",
        "R1B_SEMANTIC_CACHE",
        "R5_FALLBACK",
        "R3_SIMPLE_GROUNDED_READ",
        "R3R4_MANAGED_WORKFLOW",
    } <= canonical
    for row in rows:
        assert isinstance(row.get("production_enabled"), bool)
        assert isinstance(row.get("test_only"), bool)
        assert isinstance(row.get("required_activation_flags"), list)
        assert row["spine"]["canonical_route_id"] in l0_binding.CANONICAL_L0_ROUTE_IDS
        assert row["spine"]["app_route_id"]
        assert row["spine"]["route_family"] in l0_binding.CANONICAL_L0_ROUTE_IDS


def test_managed_workflow_requires_test_posture_or_explicit_activation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
    monkeypatch.delenv("APPS_RG_ENABLE_MANAGED_WORKFLOW_L0", raising=False)
    monkeypatch.setenv("APPS_RG_ROUTE_HMAC_SECRET", "prod-secret")
    route = l0_route_apps_rg(_plan())
    assert route.route_id == "R3_SIMPLE_GROUNDED_READ"
    assert route.allowed_next_stage == frozenset()

    monkeypatch.setenv("APPS_RG_ENABLE_MANAGED_WORKFLOW_L0", "1")
    route = l0_route_apps_rg(_plan())
    assert route.route_id == "R3R4_MANAGED_WORKFLOW"
    assert route.allowed_next_stage == frozenset({"L3"})


def test_missing_production_hmac_secret_fails_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
    monkeypatch.delenv("APPS_RG_ROUTE_HMAC_SECRET", raising=False)
    monkeypatch.delenv("APPS_RG_ROUTE_SIGNING_POSTURE", raising=False)
    with pytest.raises(RouteSigningSecretMissingError):
        l0_route_apps_rg(_plan())


def test_explicit_unsigned_test_posture_emits_digest_without_signature(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
    monkeypatch.delenv("APPS_RG_ROUTE_HMAC_SECRET", raising=False)
    monkeypatch.setenv("APPS_RG_ROUTE_SIGNING_POSTURE", "unsigned_test")
    route = l0_route_apps_rg(_plan(merge_required_hint=False))
    assert len(route.route_digest) == 64
    assert route.hmac_sig == ""
    assert "route_signing_posture=unsigned_test" in route.reason_codes


def test_required_gate_unknown_blocks_progressing_route() -> None:
    route = l0_route_apps_rg(
        _plan(query_spec={}, support_expectation={}, merge_required_hint=True)
    )
    assert route.route_id == "R3R4_MANAGED_WORKFLOW"
    assert route.allowed_next_stage == frozenset()
    assert "route_gate_status=BLOCKED" in route.reason_codes
    assert any(code.startswith("blocking_gate_ids=") for code in route.reason_codes)


def test_ambiguous_matching_profiles_fail_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    rows = copy.deepcopy(l0_binding._load_profiles())
    managed = next(
        row
        for row in rows
        if row["spine"]["canonical_route_id"] == "R3R4_MANAGED_WORKFLOW"
        and row.get("conditions", {}).get("merge_required_hint") is True
    )
    duplicate = copy.deepcopy(managed)
    duplicate["route_profile_id"] = "arpf::apps_rg::resume_generation::duplicate::v1"
    rows.insert(0, duplicate)
    monkeypatch.setattr(l0_binding, "_PROFILE_CACHE", rows)
    with pytest.raises(RouteProfileSchemaError, match="ambiguous"):
        l0_route_apps_rg(_plan())
    reset_route_profiles_cache()


def test_terminal_r5_packet_has_replayable_evidence() -> None:
    route = l0_route_apps_rg(
        _plan(
            task_spec={
                "l0_terminal_route": "R5_FALLBACK",
                "fallback_receipt_ref": "fallback::abstain::001",
            },
            merge_required_hint=False,
        )
    )
    assert route.route_id == "R5_FALLBACK"
    assert route.r5_fallback_receipt_ref == "fallback::abstain::001"
    assert route.allowed_next_stage == frozenset()
    assert route.route_digest
    assert route.replay_key
    assert any(ref.startswith("policy_hash:") for ref in route.snapshot_refs)


def test_hitl_hint_is_annotation_not_route_authority() -> None:
    route = l0_route_apps_rg(
        _plan(route_hints={"hitl_posture": "required"}, merge_required_hint=False)
    )
    assert route.route_id == "R3_SIMPLE_GROUNDED_READ"
    assert "hitl_posture=required" in route.reason_codes
    assert route.allowed_next_stage == frozenset()


def test_serialized_l0_artifact_round_trips_route_semantics() -> None:
    route = l0_route_apps_rg(_plan())
    artifact = serialize_l0_route_artifact(route)
    encoded = json.dumps(artifact, sort_keys=True)
    decoded = json.loads(encoded)
    assert decoded["route_id"] == route.route_id
    assert decoded["canonical_route_id"] == route.route_id
    assert decoded["route_digest"] == route.route_digest
    assert decoded["signature"]["hmac_sig"] == route.hmac_sig
    assert decoded["route_gate_receipts"]
