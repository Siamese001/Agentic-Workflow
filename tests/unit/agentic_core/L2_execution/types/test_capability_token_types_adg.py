"""ADG-driven tests for agentic_core/L2_execution/types/capability_token_types.py — fan_in=4.

Covers: PERMISSION_CODES, CapabilityTokenSubject, CapabilityConstraints,
CapabilityTokenArtifact, CapabilityDecisionArtifact, CapabilityEnforcer,
build_capability_token, build_capability_decision, issue_capability_token.
"""
from __future__ import annotations

import hashlib
import json

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L2_execution.types.capability_token_types import (
    ALL_PERMISSION_VALUES,
    PERMISSION_CODES,
    CapabilityConstraints,
    CapabilityDecisionArtifact,
    CapabilityEnforcer,
    CapabilityTokenArtifact,
    CapabilityTokenSubject,
    build_capability_decision,
    build_capability_token,
    issue_capability_token,
)
from agentic_core.L0_routing.types.determinism_types import SemanticClockSnapshot


def _clock() -> SemanticClockSnapshot:
    return SemanticClockSnapshot(tick=1)


def _subject() -> CapabilityTokenSubject:
    return CapabilityTokenSubject(kind="agent", id="TestAgent")


def _constraints(**kw) -> CapabilityConstraints:
    return CapabilityConstraints(
        allowed_paths=tuple(kw.get("allowed_paths", [])),  # empty = no path restriction
        max_tool_calls=kw.get("max_tool_calls", 10),
    )


def _token(**kw) -> CapabilityTokenArtifact:
    return build_capability_token(
        semantic_clock=_clock(),
        subject=_subject(),
        issued_by=kw.get("issued_by", "TestIssuer"),
        permissions=kw.get("permissions", ["TOOL:READ"]),
        constraints=_constraints(),
    )


class TestAllExports:
    def test_all_exports_present(self):
        import agentic_core.L2_execution.types.capability_token_types as m
        for name in m.__all__:
            assert hasattr(m, name), f"Missing __all__ member: {name}"


class TestPermissionCodes:
    def test_all_expected_codes_present(self):
        expected = {"TOOL_READ", "TOOL_WRITE", "FS_READ", "FS_WRITE", "NET_READ", "NET_WRITE", "GIT_READ", "GIT_WRITE"}
        assert expected == set(PERMISSION_CODES.keys())

    def test_values_use_colon_separator(self):
        for v in PERMISSION_CODES.values():
            assert ":" in v

    def test_all_permission_values_frozenset(self):
        assert isinstance(ALL_PERMISSION_VALUES, frozenset)
        assert set(PERMISSION_CODES.values()) == ALL_PERMISSION_VALUES


class TestCapabilityTokenSubject:
    def test_valid_creation(self):
        s = CapabilityTokenSubject(kind="agent", id="MyAgent")
        assert s.kind == "agent"
        assert s.id == "MyAgent"

    def test_to_dict(self):
        s = CapabilityTokenSubject(kind="agent", id="MyAgent")
        d = s.to_dict()
        assert d == {"kind": "agent", "id": "MyAgent"}

    def test_empty_kind_raises(self):
        with pytest.raises(ValueError, match="kind"):
            CapabilityTokenSubject(kind="", id="x")

    def test_empty_id_raises(self):
        with pytest.raises(ValueError, match="id"):
            CapabilityTokenSubject(kind="agent", id="")

    def test_frozen(self):
        s = CapabilityTokenSubject(kind="agent", id="x")
        with pytest.raises(Exception):
            s.kind = "other"  # type: ignore[misc]


class TestCapabilityConstraints:
    def test_valid_creation(self):
        c = CapabilityConstraints(allowed_paths=("agentic_core/",), max_tool_calls=5)
        assert c.max_tool_calls == 5

    def test_negative_tool_calls_raises(self):
        with pytest.raises(ValueError, match="max_tool_calls"):
            CapabilityConstraints(allowed_paths=(), max_tool_calls=-1)

    def test_to_dict(self):
        c = CapabilityConstraints(allowed_paths=("b/", "a/"), max_tool_calls=3)
        d = c.to_dict()
        assert d["max_tool_calls"] == 3
        assert d["allowed_paths"] == sorted(["b/", "a/"])

    def test_paths_auto_sorted(self):
        c = CapabilityConstraints(allowed_paths=("z/", "a/"), max_tool_calls=1)
        assert c.allowed_paths == ("a/", "z/")


class TestBuildCapabilityToken:
    def test_token_has_correct_artifact_type(self):
        t = _token()
        assert t.artifact_type == "CAPABILITY_TOKEN"

    def test_trace_id_is_deterministic(self):
        t1 = _token()
        t2 = _token()
        assert t1.trace_id == t2.trace_id

    def test_permissions_sorted(self):
        t = _token(permissions=["TOOL:WRITE", "TOOL:READ"])
        assert list(t.permissions) == sorted(t.permissions)

    def test_empty_issued_by_raises(self):
        with pytest.raises(ValueError):
            _token(issued_by="")

    def test_to_json_deterministic(self):
        t1 = _token()
        t2 = _token()
        assert t1.to_json() == t2.to_json()

    def test_to_json_valid_json(self):
        t = _token()
        parsed = json.loads(t.to_json())
        assert parsed["artifact_type"] == "CAPABILITY_TOKEN"


class TestBuildCapabilityDecision:
    def test_allow_decision(self):
        d = build_capability_decision(
            semantic_clock=_clock(),
            tool_name="write_gateway",
            action="write",
            requested_resource="agentic_core/foo.py",
            decision="ALLOW",
            deny_reason=None,
            capability_trace_id="abc123",
        )
        assert d.decision == "ALLOW"
        assert d.deny_reason is None

    def test_deny_decision(self):
        d = build_capability_decision(
            semantic_clock=_clock(),
            tool_name="write_gateway",
            action="write",
            requested_resource="/etc/passwd",
            decision="DENY",
            deny_reason="PATH_NOT_ALLOWED:/etc/passwd",
            capability_trace_id="abc123",
        )
        assert d.decision == "DENY"
        assert "PATH_NOT_ALLOWED" in d.deny_reason

    def test_trace_id_deterministic(self):
        kwargs = dict(
            semantic_clock=_clock(),
            tool_name="t",
            action="a",
            requested_resource="r",
            decision="ALLOW",
            deny_reason=None,
            capability_trace_id="cap1",
        )
        d1 = build_capability_decision(**kwargs)
        d2 = build_capability_decision(**kwargs)
        assert d1.trace_id == d2.trace_id

    def test_invalid_decision_raises(self):
        with pytest.raises(ValueError):
            CapabilityDecisionArtifact(
                artifact_type="CAPABILITY_DECISION",
                semantic_clock=_clock(),
                trace_id="t",
                tool_name="x",
                action="a",
                requested_resource="r",
                decision="MAYBE",  # type: ignore[arg-type]
                deny_reason=None,
                capability_trace_id="c",
            )


class TestCapabilityEnforcer:
    def test_allow_within_limit(self):
        t = _token()  # no path restriction (empty allowed_paths)
        enforcer = CapabilityEnforcer(t)
        decision = enforcer.check(
            tool_name="write_gateway",
            action="read",
            requested_resource="agentic_core/foo.py",
            required_permission="TOOL:READ",
            semantic_clock=_clock(),
        )
        assert decision.decision == "ALLOW"
        assert enforcer.call_count == 1

    def test_deny_missing_permission(self):
        t = _token(permissions=["TOOL:READ"])
        enforcer = CapabilityEnforcer(t)
        with pytest.raises(PermissionError):
            enforcer.check(
                tool_name="write_gateway",
                action="write",
                requested_resource="agentic_core/foo.py",
                required_permission="TOOL:WRITE",
                semantic_clock=_clock(),
            )
        assert enforcer.call_count == 0

    def test_deny_path_not_allowed(self):
        t = build_capability_token(
            semantic_clock=_clock(),
            subject=_subject(),
            issued_by="issuer",
            permissions=["TOOL:WRITE"],
            constraints=CapabilityConstraints(allowed_paths=("agentic_core",), max_tool_calls=10),
        )
        enforcer = CapabilityEnforcer(t)
        with pytest.raises(PermissionError, match="PATH_NOT_ALLOWED"):
            enforcer.check(
                tool_name="t",
                action="a",
                requested_resource="system/etc/passwd",
                required_permission="TOOL:WRITE",
                semantic_clock=_clock(),
            )

    def test_deny_max_tool_calls_exceeded(self):
        t = build_capability_token(
            semantic_clock=_clock(),
            subject=_subject(),
            issued_by="issuer",
            permissions=["TOOL:READ"],
            constraints=CapabilityConstraints(allowed_paths=(), max_tool_calls=1),
        )
        enforcer = CapabilityEnforcer(t)
        enforcer.check(
            tool_name="t", action="a", requested_resource="agentic_core/x",
            required_permission="TOOL:READ", semantic_clock=_clock(),
        )
        with pytest.raises(PermissionError, match="MAX_TOOL_CALLS_EXCEEDED"):
            enforcer.check(
                tool_name="t", action="a", requested_resource="agentic_core/x",
                required_permission="TOOL:READ", semantic_clock=_clock(),
            )

    def test_decisions_recorded(self):
        t = _token()  # empty allowed_paths
        enforcer = CapabilityEnforcer(t)
        enforcer.check(
            tool_name="t", action="a", requested_resource="agentic_core/x",
            required_permission="TOOL:READ", semantic_clock=_clock(),
        )
        assert len(enforcer.decisions) == 1


class TestIssueCapabilityToken:
    def test_valid_token_issued(self):
        t = issue_capability_token(
            semantic_clock=_clock(),
            subject_kind="agent",
            subject_id="TestAgent",
            issued_by="Governor",
            permissions=["TOOL:READ"],
            allowed_paths=["agentic_core/"],
            max_tool_calls=5,
        )
        assert t.artifact_type == "CAPABILITY_TOKEN"
        assert "TOOL:READ" in t.permissions

    def test_unknown_permission_raises(self):
        with pytest.raises(ValueError, match="unknown permission"):
            issue_capability_token(
                semantic_clock=_clock(),
                subject_kind="agent",
                subject_id="x",
                issued_by="y",
                permissions=["INVALID:PERM"],
                allowed_paths=[],
                max_tool_calls=1,
            )

    def test_permissions_sorted(self):
        t = issue_capability_token(
            semantic_clock=_clock(),
            subject_kind="agent",
            subject_id="x",
            issued_by="y",
            permissions=["TOOL:WRITE", "TOOL:READ"],
            allowed_paths=[],
            max_tool_calls=5,
        )
        assert list(t.permissions) == sorted(t.permissions)
