"""W6 tests for L5 Governance v4 engines."""

from __future__ import annotations

import pytest

from system_learning.engines.governance_v4.capability_token import (
    CapabilityToken,
    CapabilityTokenMinter,
    PrincipalChain,
    SandboxEnvelopeMinter,
)
from system_learning.engines.governance_v4.egress_inspector import (
    EgressInspector,
    EgressVerdict,
    HardConstraintEnforcer,
)
from system_learning.engines.governance_v4.identity_propagator import IdentityPropagator
from system_learning.engines.governance_v4.mcp_connector_registry import (
    DataSensitivity,
    GrantType,
    McpConnectorRegistry,
)
from system_learning.engines.governance_v4.replay_envelope_writer import (
    ForensicReplayVerifier,
    ReplayEnvelopeWriter,
)
from system_learning.engines.governance_v4.risk_tier_classifier import (
    RiskTierBand,
    RiskTierClassifier,
)
from system_learning.engines.v7_kpi_board import UnifiedKPIBoard, V7KPIName


# ---- capability_token ----------------------------------------------------


def _principal():
    return PrincipalChain(
        invoking_user="alice@org",
        agent_id="agent.researcher",
        parent_agent_id=None,
        delegation_depth=0,
        scope="research:read",
    )


def test_mint_capability_token_content_addressed():
    m = CapabilityTokenMinter()
    a = m.mint(
        scope="tool.search",
        principal_chain=_principal(),
        connector_allowlist=("notion", "github"),
        plan_digest="d1",
        permission_ladder=("read", "search"),
        standards_fingerprint="NIST_AI_RMF",
        ttl_seconds=300.0,
        issued_at_epoch=1000.0,
    )
    b = m.mint(
        scope="tool.search",
        principal_chain=_principal(),
        connector_allowlist=("github", "notion"),  # different order
        plan_digest="d1",
        permission_ladder=("read", "search"),
        standards_fingerprint="NIST_AI_RMF",
        ttl_seconds=300.0,
        issued_at_epoch=1000.0,
    )
    # connector_allowlist canonicalized via sort: ids identical
    assert a.token_id == b.token_id
    assert a.expires_at_epoch == 1300.0


def test_mint_rejects_excessive_ttl():
    m = CapabilityTokenMinter()
    with pytest.raises(ValueError, match="ttl_seconds"):
        m.mint(
            scope="x", principal_chain=_principal(),
            connector_allowlist=(), plan_digest="",
            permission_ladder=(), standards_fingerprint="",
            ttl_seconds=10 * 3600.0,
        )


def test_mint_rejects_empty_scope():
    m = CapabilityTokenMinter()
    with pytest.raises(ValueError, match="scope"):
        m.mint(
            scope="", principal_chain=_principal(),
            connector_allowlist=(), plan_digest="",
            permission_ladder=(), standards_fingerprint="",
        )


def test_capability_token_publishes_violation_kpis():
    m = CapabilityTokenMinter()
    board = UnifiedKPIBoard()
    m.mark_ttl_violation()
    m.mark_scope_violation()
    m.mark_scope_violation()
    m.publish_kpi_sample(board)
    ttl = board.latest(V7KPIName.CAPABILITY_TOKEN_TTL_VIOLATIONS)  # type: ignore[arg-type]
    sc = board.latest(V7KPIName.CAPABILITY_TOKEN_SCOPE_VIOLATIONS)  # type: ignore[arg-type]
    assert ttl.value == 1.0 and sc.value == 2.0


def test_sandbox_envelope_pairs_with_token():
    m = CapabilityTokenMinter()
    sm = SandboxEnvelopeMinter()
    token = m.mint(
        scope="x", principal_chain=_principal(),
        connector_allowlist=(), plan_digest="",
        permission_ladder=(), standards_fingerprint="",
    )
    env = sm.mint(token=token, fs_writable_paths=("/tmp/run/",),
                  network_allowlist=("api.example.com",))
    assert env.token_id == token.token_id
    assert env.fs_writable_paths == ("/tmp/run/",)


# ---- identity_propagator -------------------------------------------------


def test_propagate_increments_depth_and_sets_parent():
    p = IdentityPropagator(max_depth=4)
    out = p.propagate(_principal(), new_agent_id="agent.searcher")
    assert out.accepted is True
    assert out.new_chain.delegation_depth == 1
    assert out.new_chain.parent_agent_id == "agent.researcher"
    assert out.new_chain.agent_id == "agent.searcher"


def test_propagate_rejects_at_max_depth():
    p = IdentityPropagator(max_depth=2)
    chain = _principal()
    chain1 = p.propagate(chain, new_agent_id="a1").new_chain
    chain2 = p.propagate(chain1, new_agent_id="a2").new_chain
    out = p.propagate(chain2, new_agent_id="a3")
    assert out.accepted is False
    _, _, breaches = p.counters
    assert breaches == 1


def test_propagator_publishes_kpis():
    p = IdentityPropagator(max_depth=2)
    board = UnifiedKPIBoard()
    chain = _principal()
    chain1 = p.propagate(chain, new_agent_id="a1").new_chain
    chain2 = p.propagate(chain1, new_agent_id="a2").new_chain
    p.propagate(chain2, new_agent_id="a3")  # rejected
    p.publish_kpi_sample(board)
    completeness = board.latest(V7KPIName.PRINCIPAL_CHAIN_PROPAGATION_COMPLETENESS)  # type: ignore[arg-type]
    breaches = board.latest(V7KPIName.DELEGATION_DEPTH_BREACHES)  # type: ignore[arg-type]
    assert completeness.value == 1.0  # all 3 calls had full chain
    assert breaches.value == 1.0


# ---- risk_tier_classifier -------------------------------------------------


def test_classifier_low_band_for_minimal_risk():
    c = RiskTierClassifier()
    a = c.classify({"writes_to_canonical_store": False})
    assert a.band is RiskTierBand.LOW


def test_classifier_high_band_for_canonical_writes_plus_egress():
    c = RiskTierClassifier()
    a = c.classify({
        "writes_to_canonical_store": True,
        "external_egress": True,
        "cross_principal_data": True,
        "high_value_user_data": True,
    })
    assert a.band is RiskTierBand.HIGH


def test_classifier_publishes_coverage_kpi():
    c = RiskTierClassifier()
    board = UnifiedKPIBoard()
    for _ in range(5):
        c.classify({})
    c.publish_kpi_sample(board)
    sample = board.latest(V7KPIName.RISK_TIER_BAND_COVERAGE)  # type: ignore[arg-type]
    assert sample.value == 1.0


# ---- egress_inspector ----------------------------------------------------


def test_egress_pass_clean_payload():
    e = EgressInspector()
    f = e.inspect("Hello world, no secrets here.")
    assert f.verdict is EgressVerdict.PASS


def test_egress_block_aws_key():
    e = EgressInspector()
    f = e.inspect("token=AKIAABCDEFGHIJKLMNOP suffix")
    assert f.verdict is EgressVerdict.BLOCK
    assert any("aws_access_key" in t for t in f.triggered)


def test_egress_block_ssn():
    e = EgressInspector()
    f = e.inspect("user SSN 123-45-6789")
    assert f.verdict is EgressVerdict.BLOCK
    assert any("ssn_us" in t for t in f.triggered)


def test_egress_url_allowlist_blocks_unlisted():
    e = EgressInspector(url_allowlist=("example.com",))
    f = e.inspect("see https://evil.example.org/path")
    assert f.verdict is EgressVerdict.BLOCK
    assert any("url_not_allowlisted" in t for t in f.triggered)


def test_egress_url_allowlist_allows_subdomain():
    e = EgressInspector(url_allowlist=("example.com",))
    f = e.inspect("see https://api.example.com/path")
    assert f.verdict is EgressVerdict.PASS


def test_egress_publishes_block_rate_kpi():
    e = EgressInspector()
    board = UnifiedKPIBoard()
    e.inspect("clean")
    e.inspect("clean")
    e.inspect("AKIAABCDEFGHIJKLMNOP")
    e.publish_kpi_sample(board)
    sample = board.latest(V7KPIName.EGRESS_INSPECTOR_BLOCK_RATE)  # type: ignore[arg-type]
    assert sample.value == pytest.approx(1 / 3)


# ---- hard_constraint_enforcer --------------------------------------------


def test_hard_constraint_forces_reject():
    h = HardConstraintEnforcer()
    assert h.enforce(decision="REMEDIATE", breached_rule_id="r1",
                     rule_is_hard_constraint=True) == "REJECT"
    assert h.attempt_count == 1


def test_hard_constraint_passthrough_when_not_hard():
    h = HardConstraintEnforcer()
    assert h.enforce(decision="REMEDIATE", breached_rule_id="r1",
                     rule_is_hard_constraint=False) == "REMEDIATE"
    assert h.attempt_count == 0


def test_hard_constraint_publishes_kpi():
    h = HardConstraintEnforcer()
    board = UnifiedKPIBoard()
    h.enforce(decision="REMEDIATE", breached_rule_id="r1",
              rule_is_hard_constraint=True)
    h.enforce(decision="REMEDIATE", breached_rule_id="r2",
              rule_is_hard_constraint=True)
    h.publish_kpi_sample(board)
    sample = board.latest(V7KPIName.HARD_CONSTRAINT_REMEDIATE_ATTEMPTS)  # type: ignore[arg-type]
    assert sample.value == 2.0


# ---- replay_envelope_writer + verifier -----------------------------------


def test_envelope_round_trip():
    w = ReplayEnvelopeWriter()
    v = ForensicReplayVerifier()
    payload = {"k1": "v1", "k2": [1, 2, 3]}
    env = w.write(
        trace_id="t1", run_id="r1",
        policy_hash="ph", prompt_hash="prh", context_hash="ch",
        capability_token_id="tk", sandbox_envelope_id="sb",
        standards_fingerprint="NIST_AI_RMF",
        canonical_payload=payload,
        issued_at_epoch=1000.0,
    )
    ok, _ = v.verify(env, payload)
    assert ok is True


def test_envelope_detects_payload_tamper():
    w = ReplayEnvelopeWriter()
    v = ForensicReplayVerifier()
    env = w.write(
        trace_id="t", run_id="r", policy_hash="", prompt_hash="",
        context_hash="", capability_token_id="", sandbox_envelope_id="",
        standards_fingerprint="", canonical_payload={"k": "v"},
    )
    ok, reason = v.verify(env, {"k": "tampered"})
    assert ok is False and "hash mismatch" in reason


def test_envelope_publishes_reconstruction_kpi():
    w = ReplayEnvelopeWriter()
    v = ForensicReplayVerifier()
    board = UnifiedKPIBoard()
    payload = {"x": 1}
    env = w.write(
        trace_id="", run_id="", policy_hash="", prompt_hash="",
        context_hash="", capability_token_id="", sandbox_envelope_id="",
        standards_fingerprint="", canonical_payload=payload,
    )
    v.verify(env, payload)  # ok
    v.verify(env, {"x": 2})  # fail
    v.publish_kpi_sample(board)
    sample = board.latest(V7KPIName.REPLAY_ENVELOPE_RECONSTRUCTION_SUCCESS_RATE)  # type: ignore[arg-type]
    assert sample.value == 0.5


# ---- mcp_connector_registry ----------------------------------------------


def test_registry_authorizes_registered_permanent():
    r = McpConnectorRegistry()
    r.register(connector_id="notion", grant_type=GrantType.PERMANENT,
               data_sensitivity=DataSensitivity.INTERNAL)
    ok, _ = r.authorize("notion")
    assert ok is True
    ok2, _ = r.authorize("notion")
    assert ok2 is True
    assert r.violation_count == 0


def test_registry_rejects_unregistered():
    r = McpConnectorRegistry()
    ok, reason = r.authorize("ghost_connector")
    assert ok is False and "not in allowlist" in reason
    assert r.violation_count == 1


def test_registry_one_time_grant_consumed():
    r = McpConnectorRegistry()
    r.register(connector_id="onetime", grant_type=GrantType.ONE_TIME,
               data_sensitivity=DataSensitivity.CONFIDENTIAL)
    ok1, _ = r.authorize("onetime")
    assert ok1 is True
    ok2, reason = r.authorize("onetime")
    assert ok2 is False and "already consumed" in reason
    assert r.violation_count == 1


def test_registry_publishes_violations_kpi():
    r = McpConnectorRegistry()
    board = UnifiedKPIBoard()
    r.authorize("ghost1")
    r.authorize("ghost2")
    r.publish_kpi_sample(board)
    sample = board.latest(V7KPIName.MCP_CONNECTOR_ALLOWLIST_VIOLATIONS)  # type: ignore[arg-type]
    assert sample.value == 2.0
