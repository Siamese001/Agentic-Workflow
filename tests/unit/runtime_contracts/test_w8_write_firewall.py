"""W8 tests — write/learning firewall markers on 4 emit contracts (Concern #10).

Covers P8.1: is_uwg_write_authority + is_future_run_only fields on
SealedL2Artifact, X3Disposition, CommitRequest, RuntimeExhaustBundle.
Default is False for both — the gateway (durable_write_gateway) enforces
the actual write discipline; these fields document the contract's intent.
"""
from __future__ import annotations

import pytest


# ---------------------------------------------------------------------------
# Factories
# ---------------------------------------------------------------------------

def _make_sealed():
    from agentic_core.runtime.contracts.sealed_l2_artifact import SealedL2Artifact
    return SealedL2Artifact(
        request_id="r1", run_id="run1", app_id="apps_rg",
        trace_id="t1", execution_status="completed",
        l5_certification_ref="cert-test-ok",
    )


def _make_x3():
    from agentic_core.runtime.contracts.x3_disposition import X3Disposition
    return X3Disposition(
        request_id="r1", run_id="run1", app_id="apps_rg",
        trace_id="t1", exit_status="success",
        l5_certification_ref="cert-test-ok",
    )


def _make_commit():
    from agentic_core.L4_state.contracts.records import CommitRequest
    return CommitRequest(
        commit_request_id="cr1", cleared_exit_review_packet_ref="ep1",
        request_id="r1", run_id="run1", trace_root="t1", tenant_id="tenant1",
        policy_hash="ph1", blueprint_hash="bh1",
        route_contract_ref="rc1", replay_key="rk1",
        rollback_plan_ref="rp1", blast_radius="low",
        l5_certification_ref="cert-test-ok",
    )


def _make_exhaust():
    from agentic_core.L6_observability.runtime_trace.runtime_exhaust_bundle import (
        RuntimeExhaustBundle,
    )
    return RuntimeExhaustBundle(
        raw_evidence_refs=(), lineage_manifest={}, stage_map={},
        artifact_inventory=(), gap_report=(),
        ingest_quality_score=1.0, newest_span_age_seconds=0.0,
        bundle_id="b1", l5_certification_ref="cert-test-ok",
    )


_FIREWALL_CONTRACTS = [
    ("SealedL2Artifact", _make_sealed),
    ("X3Disposition", _make_x3),
    ("CommitRequest", _make_commit),
    ("RuntimeExhaustBundle", _make_exhaust),
]


# ---------------------------------------------------------------------------
# is_uwg_write_authority — presence, type, default
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("name,factory", _FIREWALL_CONTRACTS, ids=[c[0] for c in _FIREWALL_CONTRACTS])
def test_is_uwg_write_authority_exists(name, factory):
    assert hasattr(factory(), "is_uwg_write_authority"), (
        f"{name} missing is_uwg_write_authority"
    )


@pytest.mark.parametrize("name,factory", _FIREWALL_CONTRACTS, ids=[c[0] for c in _FIREWALL_CONTRACTS])
def test_is_uwg_write_authority_is_bool(name, factory):
    val = factory().is_uwg_write_authority
    assert isinstance(val, bool), (
        f"{name}.is_uwg_write_authority should be bool, got {type(val)}"
    )


@pytest.mark.parametrize("name,factory", _FIREWALL_CONTRACTS, ids=[c[0] for c in _FIREWALL_CONTRACTS])
def test_is_uwg_write_authority_default_false(name, factory):
    assert factory().is_uwg_write_authority is False, (
        f"{name}.is_uwg_write_authority default should be False"
    )


# ---------------------------------------------------------------------------
# is_future_run_only — presence, type, default
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("name,factory", _FIREWALL_CONTRACTS, ids=[c[0] for c in _FIREWALL_CONTRACTS])
def test_is_future_run_only_exists(name, factory):
    assert hasattr(factory(), "is_future_run_only"), (
        f"{name} missing is_future_run_only"
    )


@pytest.mark.parametrize("name,factory", _FIREWALL_CONTRACTS, ids=[c[0] for c in _FIREWALL_CONTRACTS])
def test_is_future_run_only_is_bool(name, factory):
    val = factory().is_future_run_only
    assert isinstance(val, bool), (
        f"{name}.is_future_run_only should be bool, got {type(val)}"
    )


@pytest.mark.parametrize("name,factory", _FIREWALL_CONTRACTS, ids=[c[0] for c in _FIREWALL_CONTRACTS])
def test_is_future_run_only_default_false(name, factory):
    assert factory().is_future_run_only is False, (
        f"{name}.is_future_run_only default should be False"
    )


# ---------------------------------------------------------------------------
# Semantic — markers can be set explicitly without breaking frozen invariant
# ---------------------------------------------------------------------------

def test_sealed_with_uwg_write_authority():
    from agentic_core.runtime.contracts.sealed_l2_artifact import SealedL2Artifact
    s = SealedL2Artifact(
        request_id="r1", run_id="run1", app_id="apps_rg",
        trace_id="t1", execution_status="completed",
        is_uwg_write_authority=True,
        l5_certification_ref="cert-test-ok",
    )
    assert s.is_uwg_write_authority is True
    assert s.is_future_run_only is False


def test_x3_with_future_run_only():
    from agentic_core.runtime.contracts.x3_disposition import X3Disposition
    x = X3Disposition(
        request_id="r1", run_id="run1", app_id="apps_rg",
        trace_id="t1", exit_status="success",
        is_future_run_only=True,
        l5_certification_ref="cert-test-ok",
    )
    assert x.is_uwg_write_authority is False
    assert x.is_future_run_only is True


def test_commit_with_both_firewall_markers():
    from agentic_core.L4_state.contracts.records import CommitRequest
    cr = CommitRequest(
        commit_request_id="cr1", cleared_exit_review_packet_ref="ep1",
        request_id="r1", run_id="run1", trace_root="t1", tenant_id="tenant1",
        policy_hash="ph1", blueprint_hash="bh1",
        route_contract_ref="rc1", replay_key="rk1",
        rollback_plan_ref="rp1", blast_radius="low",
        is_uwg_write_authority=True, is_future_run_only=True,
        l5_certification_ref="cert-test-ok",
    )
    assert cr.is_uwg_write_authority is True
    assert cr.is_future_run_only is True


def test_exhaust_bundle_write_authority_always_false_by_convention():
    # L6 is observability terminal — write authority must never be True
    bundle = _make_exhaust()
    assert bundle.is_uwg_write_authority is False
    assert bundle.is_future_run_only is False
