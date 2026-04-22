"""Behavioral tests for ``agentic_core.L0_routing.types.p1_routing_protocol``.

Covers the P1Core agent registry:
- register_agent stores capabilities and activates status.
- route_to_agent: False for unknown agent; True for active; False for inactive.
- validate_capability: False for unknown; True for matching; False for missing.
- get_agent_status: None for unknown; status string otherwise.
- P1RoutingProtocol is a Protocol — runtime-checkable via duck typing.
"""

from __future__ import annotations

from agentic_core.L0_routing.types.p1_routing_protocol import P1Core, P1RoutingProtocol


class TestRegisterAndRoute:
    def test_register_adds_active_agent(self) -> None:
        core = P1Core()
        core.register_agent("a1", ["cap-x", "cap-y"])
        assert core.get_agent_status("a1") == "active"

    def test_route_to_known_active_returns_true(self) -> None:
        core = P1Core()
        core.register_agent("a1", [])
        assert core.route_to_agent("a1", context={}) is True

    def test_route_to_unknown_returns_false(self) -> None:
        core = P1Core()
        assert core.route_to_agent("missing", context={}) is False

    def test_route_to_inactive_returns_false(self) -> None:
        core = P1Core()
        core.register_agent("a1", [])
        core._agents["a1"]["status"] = "inactive"  # type: ignore[index]
        assert core.route_to_agent("a1", context={}) is False

    def test_re_register_overwrites(self) -> None:
        core = P1Core()
        core.register_agent("a1", ["old"])
        core.register_agent("a1", ["new"])
        assert core.validate_capability("a1", "new") is True
        assert core.validate_capability("a1", "old") is False


class TestValidateCapability:
    def test_unknown_agent_false(self) -> None:
        core = P1Core()
        assert core.validate_capability("missing", "cap") is False

    def test_matching_capability_true(self) -> None:
        core = P1Core()
        core.register_agent("a1", ["read", "write"])
        assert core.validate_capability("a1", "read") is True
        assert core.validate_capability("a1", "write") is True

    def test_missing_capability_false(self) -> None:
        core = P1Core()
        core.register_agent("a1", ["read"])
        assert core.validate_capability("a1", "write") is False

    def test_empty_capabilities_list(self) -> None:
        core = P1Core()
        core.register_agent("a1", [])
        assert core.validate_capability("a1", "anything") is False


class TestGetAgentStatus:
    def test_unknown_is_none(self) -> None:
        core = P1Core()
        assert core.get_agent_status("missing") is None

    def test_known_returns_status(self) -> None:
        core = P1Core()
        core.register_agent("a1", [])
        assert core.get_agent_status("a1") == "active"


class TestProtocolConformance:
    def test_p1core_satisfies_protocol_by_structure(self) -> None:
        """P1Core duck-types to P1RoutingProtocol (has route_to_agent + validate_capability)."""
        core = P1Core()
        assert hasattr(core, "route_to_agent")
        assert callable(core.route_to_agent)
        assert hasattr(core, "validate_capability")
        assert callable(core.validate_capability)

    def test_protocol_is_a_class(self) -> None:
        # Protocol classes behave like classes
        assert isinstance(P1RoutingProtocol, type)
