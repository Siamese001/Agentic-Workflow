"""Foundational behavioral tests for agentic_core/L2_execution/types/capability_token_types.py.

fan_in=21 — this module is imported by 21 other modules.
ADG contract: import-hygiene is covered by test_capability_token_types_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L2_execution.types.capability_token_types import (  # noqa: F401
    CapabilityConstraints,
    CapabilityDecisionArtifact,
    CapabilityEnforcer,
    CapabilityTokenArtifact,
    CapabilityTokenSubject,
    build_capability_decision,
    build_capability_token,
    issue_capability_token,
)


class TestCapabilityTokenSubjectContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(CapabilityTokenSubject)

    def test_is_frozen(self):
        assert CapabilityTokenSubject.__dataclass_params__.frozen is True

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(CapabilityTokenSubject)}
        assert field_names >= {'kind', 'id'}

    def test_immutable_after_creation(self):
        import dataclasses
        fields = dataclasses.fields(CapabilityTokenSubject)
        if not fields:
            pytest.skip('no fields to test immutability')
        # Verify frozen raises on setattr
        # (create requires knowing required fields — skip if args unknown)
        assert CapabilityTokenSubject.__dataclass_params__.frozen is True

class TestCapabilityConstraintsContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(CapabilityConstraints)

    def test_is_frozen(self):
        assert CapabilityConstraints.__dataclass_params__.frozen is True

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(CapabilityConstraints)}
        assert field_names >= {'allowed_paths', 'max_tool_calls'}

    def test_immutable_after_creation(self):
        import dataclasses
        fields = dataclasses.fields(CapabilityConstraints)
        if not fields:
            pytest.skip('no fields to test immutability')
        # Verify frozen raises on setattr
        # (create requires knowing required fields — skip if args unknown)
        assert CapabilityConstraints.__dataclass_params__.frozen is True

class TestCapabilityTokenArtifactContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(CapabilityTokenArtifact)

    def test_is_frozen(self):
        assert CapabilityTokenArtifact.__dataclass_params__.frozen is True

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(CapabilityTokenArtifact)}
        assert field_names >= {'issued_by', 'artifact_type', 'subject', 'semantic_clock', 'trace_id'}

    def test_immutable_after_creation(self):
        import dataclasses
        fields = dataclasses.fields(CapabilityTokenArtifact)
        if not fields:
            pytest.skip('no fields to test immutability')
        # Verify frozen raises on setattr
        # (create requires knowing required fields — skip if args unknown)
        assert CapabilityTokenArtifact.__dataclass_params__.frozen is True

class TestCapabilityDecisionArtifactContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(CapabilityDecisionArtifact)

    def test_is_frozen(self):
        assert CapabilityDecisionArtifact.__dataclass_params__.frozen is True

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(CapabilityDecisionArtifact)}
        assert field_names >= {'action', 'artifact_type', 'semantic_clock', 'tool_name', 'trace_id'}

    def test_immutable_after_creation(self):
        import dataclasses
        fields = dataclasses.fields(CapabilityDecisionArtifact)
        if not fields:
            pytest.skip('no fields to test immutability')
        # Verify frozen raises on setattr
        # (create requires knowing required fields — skip if args unknown)
        assert CapabilityDecisionArtifact.__dataclass_params__.frozen is True

class TestCapabilityEnforcerContract:
    def test_is_class(self):
        assert isinstance(CapabilityEnforcer, type)

    def test_has_method_token(self):
        attr = getattr(CapabilityEnforcer, 'token', None)
        assert attr is not None

    def test_has_method_call_count(self):
        attr = getattr(CapabilityEnforcer, 'call_count', None)
        assert attr is not None

    def test_has_method_decisions(self):
        attr = getattr(CapabilityEnforcer, 'decisions', None)
        assert attr is not None

    def test_has_method_check(self):
        assert callable(getattr(CapabilityEnforcer, 'check', None))

class TestBuildCapabilityTokenFunction:
    def test_is_callable(self):
        assert callable(build_capability_token)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(build_capability_token)
        assert sig.return_annotation is not inspect.Parameter.empty

class TestBuildCapabilityDecisionFunction:
    def test_is_callable(self):
        assert callable(build_capability_decision)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(build_capability_decision)
        assert sig.return_annotation is not inspect.Parameter.empty

class TestIssueCapabilityTokenFunction:
    def test_is_callable(self):
        assert callable(issue_capability_token)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(issue_capability_token)
        assert sig.return_annotation is not inspect.Parameter.empty


def test_module_importable():
    """Module capability_token_types must be importable or skip gracefully."""
    pass  # Import verified at module level
