"""Unit tests for agentic_core.L2_execution.types.capability_token_types.

Wave 6.1 (P2 untested-module coverage) — capability-based access control
artifacts. Covers PERMISSION_CODES mapping, Subject/Constraints/Token/Decision
__post_init__ guards + sorted invariants, deterministic trace_id via the
build_* helpers, canonical JSON, the issue_capability_token permission gate,
and CapabilityEnforcer ALLOW/DENY logic + path prefix matching.
"""

from __future__ import annotations

import json

import pytest

from agentic_core.L0_routing.types.determinism_types import SemanticClockSnapshot
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

_CLOCK = SemanticClockSnapshot(tick=1, vector_clock=(("L2", 1),))


def _token(**overrides: object) -> CapabilityTokenArtifact:
    base: dict = {
        "semantic_clock": _CLOCK,
        "subject": CapabilityTokenSubject(kind="agent", id="A1"),
        "issued_by": "L5",
        "permissions": ("FS:READ", "TOOL:READ"),
        "constraints": CapabilityConstraints(allowed_paths=("repo/src",), max_tool_calls=2),
    }
    base.update(overrides)
    return build_capability_token(**base)  # type: ignore[arg-type]


class TestPermissionCodes:
    def test_codes_map_to_namespaced_values(self) -> None:
        assert PERMISSION_CODES["TOOL_READ"] == "TOOL:READ"
        assert PERMISSION_CODES["GIT_WRITE"] == "GIT:WRITE"

    def test_all_permission_values_matches_mapping(self) -> None:
        assert ALL_PERMISSION_VALUES == frozenset(PERMISSION_CODES.values())


class TestSubjectAndConstraints:
    def test_subject_requires_kind(self) -> None:
        with pytest.raises(ValueError, match="kind is required"):
            CapabilityTokenSubject(kind="", id="x")

    def test_subject_requires_id(self) -> None:
        with pytest.raises(ValueError, match="id is required"):
            CapabilityTokenSubject(kind="agent", id="")

    def test_constraints_negative_calls_raise(self) -> None:
        with pytest.raises(ValueError, match="max_tool_calls must be >= 0"):
            CapabilityConstraints(allowed_paths=(), max_tool_calls=-1)

    def test_constraints_paths_auto_sorted(self) -> None:
        c = CapabilityConstraints(allowed_paths=("b", "a"), max_tool_calls=1)
        assert c.allowed_paths == ("a", "b")


class TestTokenArtifact:
    def test_build_sorts_permissions(self) -> None:
        t = _token(permissions=("TOOL:READ", "FS:READ"))
        assert t.permissions == ("FS:READ", "TOOL:READ")

    def test_trace_id_is_deterministic(self) -> None:
        assert _token().trace_id == _token().trace_id

    def test_trace_id_changes_with_payload(self) -> None:
        assert _token(issued_by="L5").trace_id != _token(issued_by="L3").trace_id

    def test_artifact_type_guard(self) -> None:
        with pytest.raises(ValueError, match="artifact_type must be 'CAPABILITY_TOKEN'"):
            CapabilityTokenArtifact(
                artifact_type="WRONG",  # type: ignore[arg-type]
                semantic_clock=_CLOCK,
                trace_id="t",
                subject=CapabilityTokenSubject(kind="agent", id="A1"),
                issued_by="L5",
                permissions=(),
                constraints=CapabilityConstraints(allowed_paths=(), max_tool_calls=1),
                policy_config_hash=None,
            )

    def test_to_json_is_canonical(self) -> None:
        loaded = json.loads(_token().to_json())
        assert loaded["artifact_type"] == "CAPABILITY_TOKEN"
        assert loaded["permissions"] == ["FS:READ", "TOOL:READ"]


class TestIssueCapabilityToken:
    def test_happy_path(self) -> None:
        t = issue_capability_token(
            semantic_clock=_CLOCK,
            subject_kind="agent",
            subject_id="A1",
            issued_by="L5",
            permissions=["TOOL:READ"],
            allowed_paths=["repo/x"],
            max_tool_calls=3,
        )
        assert isinstance(t, CapabilityTokenArtifact)
        assert t.permissions == ("TOOL:READ",)

    def test_unknown_permission_raises(self) -> None:
        with pytest.raises(ValueError, match="unknown permission"):
            issue_capability_token(
                semantic_clock=_CLOCK,
                subject_kind="agent",
                subject_id="A1",
                issued_by="L5",
                permissions=["BOGUS:PERM"],
                allowed_paths=[],
                max_tool_calls=1,
            )


class TestDecisionArtifact:
    def test_build_decision_deterministic_trace(self) -> None:
        kw = dict(
            semantic_clock=_CLOCK,
            tool_name="t",
            action="execute",
            requested_resource="repo/x",
            decision="ALLOW",
            deny_reason=None,
            capability_trace_id="cap-1",
        )
        a = build_capability_decision(**kw)  # type: ignore[arg-type]
        b = build_capability_decision(**kw)  # type: ignore[arg-type]
        assert a.trace_id == b.trace_id

    def test_invalid_decision_raises(self) -> None:
        with pytest.raises(ValueError, match="decision must be 'ALLOW' or 'DENY'"):
            CapabilityDecisionArtifact(
                artifact_type="CAPABILITY_DECISION",
                semantic_clock=_CLOCK,
                trace_id="t",
                tool_name="tool",
                action="x",
                requested_resource="r",
                decision="MAYBE",  # type: ignore[arg-type]
                deny_reason=None,
                capability_trace_id="c",
            )


class TestEnforcer:
    def test_allow_increments_call_count(self) -> None:
        enf = CapabilityEnforcer(_token())
        dec = enf.check(
            tool_name="t",
            action="execute",
            requested_resource="repo/src/file.py",
            required_permission="FS:READ",
            semantic_clock=_CLOCK,
        )
        assert dec.decision == "ALLOW"
        assert enf.call_count == 1
        assert len(enf.decisions) == 1

    def test_missing_permission_denies(self) -> None:
        enf = CapabilityEnforcer(_token())
        with pytest.raises(PermissionError, match="MISSING_PERMISSION:NET:WRITE"):
            enf.check(
                tool_name="t",
                action="x",
                requested_resource="repo/src",
                required_permission="NET:WRITE",
                semantic_clock=_CLOCK,
            )
        assert enf.call_count == 0

    def test_path_not_allowed_denies(self) -> None:
        enf = CapabilityEnforcer(_token())
        with pytest.raises(PermissionError, match="PATH_NOT_ALLOWED"):
            enf.check(
                tool_name="t",
                action="x",
                requested_resource="other/place",
                required_permission="FS:READ",
                semantic_clock=_CLOCK,
            )

    def test_max_tool_calls_exceeded_denies(self) -> None:
        t = _token(constraints=CapabilityConstraints(allowed_paths=("repo/src",), max_tool_calls=1))
        enf = CapabilityEnforcer(t)
        enf.check(
            tool_name="t",
            action="x",
            requested_resource="repo/src/a",
            required_permission="FS:READ",
            semantic_clock=_CLOCK,
        )
        with pytest.raises(PermissionError, match="MAX_TOOL_CALLS_EXCEEDED"):
            enf.check(
                tool_name="t",
                action="x",
                requested_resource="repo/src/b",
                required_permission="FS:READ",
                semantic_clock=_CLOCK,
            )

    def test_path_matches_prefix_segments(self) -> None:
        assert CapabilityEnforcer._path_matches("a/b/c", ("a/b",)) is True
        assert CapabilityEnforcer._path_matches("a/bc", ("a/b",)) is False
        assert CapabilityEnforcer._path_matches("x/y", ("a",)) is False
