"""Behavioral tests for ``agentic_core.L0_routing.enforcement.routing_contract``.

Covers the P1/L0 Routing Governance Contract (14 required fields, immutable).

- Exception hierarchy: Ungoverned/RoutingContractError/StaleRoutingContractError/
  RoutingContractValidationError are distinct and well-typed.
- RoutingContext.validate(): each required field is individually guarded.
- RoutingContract: frozen (immutable), is_policy_current, is_expired,
  require_valid raises on stale policy / expired tick.
- RoutingProposal frozen dataclass.
- create_and_commit_routing_contract(): produces a contract with all 14 fields;
  deterministic contract id for same inputs; candidate order is normalised
  (sorted) before hashing; policy_hash round-trip; registry stores it;
  proposal is also recorded.
- execute_route(): rejects non-contract values; forwards args to fn.
- reset_contract_registry() clears both contracts and proposals.
"""

from __future__ import annotations

import hashlib
from collections.abc import Generator

import pytest

from agentic_core.L0_routing.enforcement.routing_contract import (
    CONTRACT_VERSION,
    ProposalCommitter,
    RoutingContext,
    RoutingContract,
    RoutingContractValidationError,
    RoutingProposal,
    StaleRoutingContractError,
    UngovernnedRouteError,
    _get_contract_registry,
    commit_proposal,
    create_and_commit_routing_contract,
    execute_route,
    reset_contract_registry,
)


def _ctx(**overrides) -> RoutingContext:
    base = {
        "run_id": "run-1",
        "router_id": "router-A",
        "request_hash": "req-hash",
        "candidate_routes": ["D1", "D2", "D3"],
        "chosen_route": "D3",
        "policy_hash": "policy-hash-abc",
        "policy_version": "v1",
    }
    base.update(overrides)
    return RoutingContext(**base)


@pytest.fixture(autouse=True)
def _reset_registry() -> Generator[None, None, None]:
    reset_contract_registry()
    yield
    reset_contract_registry()


# ---- Exception classes --------------------------------------------------


class TestExceptions:
    def test_ungoverned_is_runtime_error(self) -> None:
        assert issubclass(UngovernnedRouteError, RuntimeError)

    def test_stale_is_runtime_error(self) -> None:
        assert issubclass(StaleRoutingContractError, RuntimeError)

    def test_validation_is_value_error(self) -> None:
        assert issubclass(RoutingContractValidationError, ValueError)


# ---- RoutingContext.validate -------------------------------------------


class TestRoutingContextValidate:
    def test_complete_context_passes(self) -> None:
        _ctx().validate()  # no raise

    @pytest.mark.parametrize(
        "field_name",
        [
            "run_id",
            "router_id",
            "request_hash",
            "chosen_route",
            "policy_hash",
            "policy_version",
        ],
    )
    def test_missing_scalar_field_raises(self, field_name: str) -> None:
        with pytest.raises(RoutingContractValidationError, match=field_name):
            _ctx(**{field_name: ""}).validate()

    def test_missing_candidate_routes_raises(self) -> None:
        with pytest.raises(RoutingContractValidationError, match="candidate_routes"):
            _ctx(candidate_routes=[]).validate()

    def test_all_missing_fields_reported(self) -> None:
        c = RoutingContext(
            run_id="",
            router_id="",
            request_hash="",
            candidate_routes=[],
            chosen_route="",
            policy_hash="",
            policy_version="",
        )
        with pytest.raises(RoutingContractValidationError) as info:
            c.validate()
        msg = str(info.value)
        for f in (
            "run_id",
            "router_id",
            "request_hash",
            "candidate_routes",
            "chosen_route",
            "policy_hash",
            "policy_version",
        ):
            assert f in msg


# ---- RoutingContract (immutable) ----------------------------------------


def _fresh_contract() -> RoutingContract:
    return create_and_commit_routing_contract(_ctx())


class TestRoutingContractImmutable:
    def test_frozen(self) -> None:
        c = _fresh_contract()
        with pytest.raises(AttributeError):
            c.policy_hash = "other"  # type: ignore[misc]

    def test_all_14_fields_populated(self) -> None:
        c = _fresh_contract()
        for fname in (
            "routing_contract_id",
            "run_id",
            "trace_id",
            "router_id",
            "request_hash",
            "candidate_routes_hash",
            "chosen_route_hash",
            "policy_hash",
            "policy_version",
            "replay_key",
            "determinism_digest",
            "contract_version",
            "created_at_tick",
            "expiry_tick",
        ):
            val = getattr(c, fname)
            assert val not in (None, "", 0), f"{fname} must be populated"

    def test_contract_version_matches_constant(self) -> None:
        c = _fresh_contract()
        assert c.contract_version == CONTRACT_VERSION


class TestPolicyAndExpiry:
    def test_is_policy_current_true_on_match(self) -> None:
        c = _fresh_contract()
        assert c.is_policy_current(c.policy_hash) is True

    def test_is_policy_current_false_on_mismatch(self) -> None:
        c = _fresh_contract()
        assert c.is_policy_current("different-hash") is False

    def test_is_expired_before_expiry(self) -> None:
        c = _fresh_contract()
        assert c.is_expired(c.created_at_tick) is False

    def test_is_expired_after_expiry(self) -> None:
        c = _fresh_contract()
        assert c.is_expired(c.expiry_tick + 1) is True

    def test_require_valid_passes_when_fresh(self) -> None:
        c = _fresh_contract()
        c.require_valid(c.policy_hash, c.created_at_tick)  # no raise

    def test_require_valid_raises_on_stale_policy(self) -> None:
        c = _fresh_contract()
        with pytest.raises(StaleRoutingContractError, match="policy mismatch"):
            c.require_valid("new-policy-hash", c.created_at_tick)

    def test_require_valid_raises_on_expired_tick(self) -> None:
        c = _fresh_contract()
        with pytest.raises(StaleRoutingContractError, match="expired"):
            c.require_valid(c.policy_hash, c.expiry_tick + 10)


# ---- RoutingProposal ----------------------------------------------------


class TestRoutingProposal:
    def test_frozen(self) -> None:
        p = RoutingProposal(
            routing_contract_id="rc-1",
            run_id="r",
            router_id="rt",
            chosen_route="D1",
            policy_hash="ph",
            proposal_hash="prop",
        )
        with pytest.raises(AttributeError):
            p.chosen_route = "D2"  # type: ignore[misc]

    def test_proposal_committer_is_class(self) -> None:
        assert isinstance(ProposalCommitter, type)

    def test_commit_proposal_records_in_registry(self) -> None:
        p = RoutingProposal(
            routing_contract_id="rc-x",
            run_id="r",
            router_id="rt",
            chosen_route="D1",
            policy_hash="ph",
            proposal_hash="prop",
        )
        commit_proposal(p)
        assert p in _get_contract_registry().all_proposals()


# ---- create_and_commit_routing_contract --------------------------------


class TestCreateAndCommit:
    def test_stored_in_registry(self) -> None:
        c = create_and_commit_routing_contract(_ctx())
        reg = _get_contract_registry()
        assert reg.get(c.routing_contract_id) is c

    def test_proposal_also_recorded(self) -> None:
        c = create_and_commit_routing_contract(_ctx())
        proposals = _get_contract_registry().all_proposals()
        assert any(p.routing_contract_id == c.routing_contract_id for p in proposals)

    def test_deterministic_contract_id_for_same_inputs(self) -> None:
        c1 = create_and_commit_routing_contract(_ctx(run_id="same"))
        reset_contract_registry()
        c2 = create_and_commit_routing_contract(_ctx(run_id="same"))
        assert c1.routing_contract_id == c2.routing_contract_id

    def test_different_chosen_route_different_id(self) -> None:
        c1 = create_and_commit_routing_contract(_ctx(chosen_route="D1"))
        c2 = create_and_commit_routing_contract(_ctx(chosen_route="D2"))
        assert c1.routing_contract_id != c2.routing_contract_id

    def test_candidate_order_does_not_affect_hash(self) -> None:
        c1 = create_and_commit_routing_contract(_ctx(candidate_routes=["A", "B", "C"]))
        reset_contract_registry()
        c2 = create_and_commit_routing_contract(_ctx(candidate_routes=["C", "B", "A"]))
        # Candidates sorted before hashing → same hash regardless of input order
        assert c1.candidate_routes_hash == c2.candidate_routes_hash

    def test_chosen_route_hash_is_sha256_prefix(self) -> None:
        c = create_and_commit_routing_contract(_ctx(chosen_route="D-42"))
        expected = hashlib.sha256(b"D-42").hexdigest()[:32]
        assert c.chosen_route_hash == expected

    def test_policy_fields_round_trip(self) -> None:
        c = create_and_commit_routing_contract(
            _ctx(policy_hash="POLICY-XYZ", policy_version="v9"),
        )
        assert c.policy_hash == "POLICY-XYZ"
        assert c.policy_version == "v9"

    def test_incomplete_context_rejected(self) -> None:
        with pytest.raises(RoutingContractValidationError):
            create_and_commit_routing_contract(_ctx(chosen_route=""))

    def test_expiry_ticks_respected(self) -> None:
        c = create_and_commit_routing_contract(_ctx(), expiry_ticks=10.0)
        assert c.expiry_tick - c.created_at_tick == pytest.approx(10.0, abs=1.0)


# ---- execute_route -----------------------------------------------------


class TestExecuteRoute:
    def test_forwards_args_on_valid_contract(self) -> None:
        c = _fresh_contract()
        result = execute_route(c, lambda x, y: x + y, 2, 3)
        assert result == 5

    def test_forwards_kwargs(self) -> None:
        c = _fresh_contract()
        result = execute_route(c, lambda **kw: kw["name"], name="cascade")
        assert result == "cascade"

    def test_rejects_non_contract(self) -> None:
        with pytest.raises(UngovernnedRouteError, match="RoutingContract"):
            execute_route("not-a-contract", lambda: None)  # type: ignore[arg-type]

    def test_rejects_none(self) -> None:
        with pytest.raises(UngovernnedRouteError):
            execute_route(None, lambda: None)  # type: ignore[arg-type]


# ---- reset_contract_registry -------------------------------------------


class TestResetRegistry:
    def test_clears_contracts_and_proposals(self) -> None:
        create_and_commit_routing_contract(_ctx())
        reg = _get_contract_registry()
        assert reg.all_contracts()
        assert reg.all_proposals()
        reset_contract_registry()
        new_reg = _get_contract_registry()
        assert new_reg.all_contracts() == []
        assert new_reg.all_proposals() == []
