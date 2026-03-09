"""
Phase 7 — Wave 1 Tests: ToolCapability, ToolIntent, ToolViolation, L1 block enforcement.
"""

from __future__ import annotations

import pytest

from agentic_core.L2_execution.types.tool_intent_types import (
    ToolCapability,
    ToolIntent,
    ToolViolation,
    assert_l1_tool_allowed,
    build_tool_intent,
    is_l1_cognition_active,
    is_mutating,
    l1_cognition_scope,
)

pytestmark = pytest.mark.unit_min_deps


def _make_intent(**overrides) -> ToolIntent:
    defaults: dict = {
        "schema_version": 1,
        "tool_name": "file_read",
        "capability": ToolCapability.NON_MUTATING,
        "args": {"path": "/tmp/test.txt"},
        "requires_commit": False,
    }
    defaults.update(overrides)
    return ToolIntent(**defaults)


class TestToolCapabilityModel:
    def test_non_mutating_is_not_mutating(self):
        assert is_mutating(ToolCapability.NON_MUTATING) is False

    def test_mutating_external_is_mutating(self):
        assert is_mutating(ToolCapability.MUTATING_EXTERNAL) is True

    def test_mutating_fs_is_mutating(self):
        assert is_mutating(ToolCapability.MUTATING_FS) is True

    def test_mutating_statebus_is_mutating(self):
        assert is_mutating(ToolCapability.MUTATING_STATEBUS) is True

    def test_capability_values(self):
        assert ToolCapability.NON_MUTATING.value == "non_mutating"
        assert ToolCapability.MUTATING_EXTERNAL.value == "mutating_external"
        assert ToolCapability.MUTATING_FS.value == "mutating_fs"
        assert ToolCapability.MUTATING_STATEBUS.value == "mutating_statebus"


class TestL1CognitionScope:
    def test_l1_inactive_by_default(self):
        assert is_l1_cognition_active() is False

    def test_l1_active_inside_scope(self):
        with l1_cognition_scope():
            assert is_l1_cognition_active() is True

    def test_l1_inactive_after_scope(self):
        with l1_cognition_scope():
            pass
        assert is_l1_cognition_active() is False

    def test_l1_restored_on_exception(self):
        with pytest.raises(RuntimeError):
            with l1_cognition_scope():
                raise RuntimeError("boom")
        assert is_l1_cognition_active() is False

    def test_nested_scope_stays_active(self):
        with l1_cognition_scope():
            with l1_cognition_scope():
                assert is_l1_cognition_active() is True
            assert is_l1_cognition_active() is True
        assert is_l1_cognition_active() is False


class TestL1BlocksMutatingToolInvocation:
    def test_l1_blocks_mutating_tool_invocation(self):
        """
        Core Wave 1 guarantee: MUTATING_EXTERNAL tool call inside L1 scope raises ToolViolation.
        """
        with l1_cognition_scope():
            with pytest.raises(ToolViolation) as exc_info:
                assert_l1_tool_allowed(ToolCapability.MUTATING_EXTERNAL, "redis_set")
        assert "L1_TOOL_CALL_BLOCKED" in str(exc_info.value)

    def test_l1_blocks_mutating_fs(self):
        with l1_cognition_scope():
            with pytest.raises(ToolViolation) as exc_info:
                assert_l1_tool_allowed(ToolCapability.MUTATING_FS, "file_write")
        assert exc_info.value.code == "L1_TOOL_CALL_BLOCKED"

    def test_l1_blocks_mutating_statebus(self):
        with l1_cognition_scope():
            with pytest.raises(ToolViolation) as exc_info:
                assert_l1_tool_allowed(ToolCapability.MUTATING_STATEBUS, "event_emit")
        assert exc_info.value.code == "L1_TOOL_CALL_BLOCKED"

    def test_violation_detail_contains_tool_name(self):
        with l1_cognition_scope():
            try:
                assert_l1_tool_allowed(ToolCapability.MUTATING_EXTERNAL, "pinecone_upsert")
                pytest.fail("Expected ToolViolation")
            except ToolViolation as exc:  # guardian: allow-silent-swallower
                assert "pinecone_upsert" in exc.detail

    def test_violation_detail_contains_capability(self):
        with l1_cognition_scope():
            try:
                assert_l1_tool_allowed(ToolCapability.MUTATING_EXTERNAL, "redis_set")
            except ToolViolation as exc:  # guardian: allow-silent-swallower
                assert "mutating_external" in exc.detail

    def test_l1_allows_non_mutating_tool_invocation(self):
        """
        Core Wave 1 guarantee: NON_MUTATING tool is allowed inside L1 scope.
        """
        with l1_cognition_scope():
            assert_l1_tool_allowed(ToolCapability.NON_MUTATING, "file_read")  # must not raise
            assert True  # no-exception contract

    def test_mutating_allowed_outside_l1_scope(self):
        """Outside L1 scope, mutating tools are not blocked by this seam."""
        assert_l1_tool_allowed(ToolCapability.MUTATING_EXTERNAL, "redis_set")  # must not raise
        assert True  # no-exception contract


class TestToolIntentHashStable:
    def test_tool_intent_hash_stable(self):
        """Same inputs produce the same intent_hash."""
        i1 = _make_intent()
        i2 = _make_intent()
        assert i1.intent_hash == i2.intent_hash
        assert len(i1.intent_hash) == 64

    def test_hash_changes_with_tool_name(self):
        i1 = _make_intent(tool_name="file_read")
        i2 = _make_intent(tool_name="ast_parse")
        assert i1.intent_hash != i2.intent_hash

    def test_hash_changes_with_capability(self):
        i1 = _make_intent(capability=ToolCapability.NON_MUTATING, requires_commit=False)
        i2 = _make_intent(
            capability=ToolCapability.MUTATING_EXTERNAL,
            requires_commit=True,
        )
        assert i1.intent_hash != i2.intent_hash

    def test_hash_changes_with_args(self):
        i1 = _make_intent(args={"path": "/tmp/a.txt"})
        i2 = _make_intent(args={"path": "/tmp/b.txt"})
        assert i1.intent_hash != i2.intent_hash

    def test_intent_hash_excluded_from_canonical_bytes(self):
        i = _make_intent()
        assert b"intent_hash" not in i.canonical_bytes()

    def test_canonical_bytes_deterministic(self):
        i1 = _make_intent()
        i2 = _make_intent()
        assert i1.canonical_bytes() == i2.canonical_bytes()

    def test_args_hash_auto_computed(self):
        i = _make_intent(args={"key": "value"})
        assert len(i.args_hash) == 64

    def test_args_hash_stable(self):
        i1 = _make_intent(args={"key": "value"})
        i2 = _make_intent(args={"key": "value"})
        assert i1.args_hash == i2.args_hash

    def test_args_hash_changes_with_args(self):
        i1 = _make_intent(args={"key": "A"})
        i2 = _make_intent(args={"key": "B"})
        assert i1.args_hash != i2.args_hash


class TestToolIntentValidation:
    def test_invalid_schema_version_raises(self):
        with pytest.raises(ValueError, match="schema_version"):
            _make_intent(schema_version=99)

    def test_empty_tool_name_raises(self):
        with pytest.raises(ValueError, match="tool_name"):
            _make_intent(tool_name="")

    def test_non_dict_args_raises(self):
        with pytest.raises(TypeError, match="args"):
            _make_intent(args="not-a-dict")  # type: ignore[arg-type]

    def test_mutating_requires_commit_false_raises(self):
        with pytest.raises(ValueError, match="requires_commit"):
            _make_intent(
                capability=ToolCapability.MUTATING_EXTERNAL,
                requires_commit=False,
            )

    def test_non_mutating_requires_commit_false_ok(self):
        i = _make_intent(capability=ToolCapability.NON_MUTATING, requires_commit=False)
        assert i.requires_commit is False


class TestBuildToolIntentFactory:
    def test_factory_sets_requires_commit_true_for_mutating(self):
        i = build_tool_intent(
            "redis_set",
            ToolCapability.MUTATING_EXTERNAL,
            {"key": "k", "value": "v"},
        )
        assert i.requires_commit is True

    def test_factory_sets_requires_commit_false_for_non_mutating(self):
        i = build_tool_intent(
            "file_read",
            ToolCapability.NON_MUTATING,
            {"path": "/tmp/f.txt"},
        )
        assert i.requires_commit is False

    def test_factory_carries_config_hashes(self):
        i = build_tool_intent(
            "file_read",
            ToolCapability.NON_MUTATING,
            {},
            policy_hash="ph",
            model_hash="mh",
            budget_hash="bh",
            routing_hash="rh",
        )
        assert i.policy_hash == "ph"
        assert i.model_hash == "mh"
        assert i.budget_hash == "bh"
        assert i.routing_hash == "rh"

    def test_to_dict_contains_all_fields(self):
        i = build_tool_intent("file_read", ToolCapability.NON_MUTATING, {})
        d = i.to_dict()
        for key in (
            "schema_version",
            "tool_name",
            "capability",
            "args",
            "args_hash",
            "requires_commit",
            "policy_hash",
            "model_hash",
            "budget_hash",
            "routing_hash",
            "intent_hash",
        ):
            assert key in d
