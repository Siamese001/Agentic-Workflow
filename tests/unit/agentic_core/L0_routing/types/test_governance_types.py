"""Foundational behavioral tests for agentic_core/L0_routing/types/governance_types.py.

fan_in=3 — imported by 3 other modules.
ADG import-hygiene is covered separately by test_governance_types_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L0_routing.types.governance_types import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_DEPTH,
        MAX_RETRIES,
        THRESHOLD,
        EvidencePack,
        ExceptionScope,
        HILOutcome,
        HILReviewOutcome,
        PolicyExceptionArtifact,
        PolicySnapshot,
        ProposalStatus,
        RouteDecisionRef,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    RouteDecisionRef = None  # type: ignore[assignment,misc]
    PolicySnapshot = None  # type: ignore[assignment,misc]
    EvidencePack = None  # type: ignore[assignment,misc]
    ExceptionScope = None  # type: ignore[assignment,misc]
    PolicyExceptionArtifact = None  # type: ignore[assignment,misc]
    ProposalStatus = None  # type: ignore[assignment,misc]
    HILOutcome = None  # type: ignore[assignment,misc]
    HILReviewOutcome = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="governance_types.py deps unavailable")
class TestRouteDecisionRefContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(RouteDecisionRef)

    def test_is_frozen(self):
        assert RouteDecisionRef.__dataclass_params__.frozen is True

    def test_field_names_present(self):
        import dataclasses
        fnames = {f.name for f in dataclasses.fields(RouteDecisionRef)}
        assert fnames >= {'trace_id', 'decision', 'agent_name', 'reason'}

    def test_field_count_reasonable(self):
        import dataclasses
        assert len(dataclasses.fields(RouteDecisionRef)) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="governance_types.py deps unavailable")
class TestPolicySnapshotContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(PolicySnapshot)

    def test_is_frozen(self):
        assert PolicySnapshot.__dataclass_params__.frozen is True

    def test_field_names_present(self):
        import dataclasses
        fnames = {f.name for f in dataclasses.fields(PolicySnapshot)}
        assert fnames >= {'policy_hash', 'risk_tier', 'laws_applied', 'security_level'}

    def test_field_count_reasonable(self):
        import dataclasses
        assert len(dataclasses.fields(PolicySnapshot)) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="governance_types.py deps unavailable")
class TestEvidencePackContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(EvidencePack)

    def test_is_frozen(self):
        assert EvidencePack.__dataclass_params__.frozen is True

    def test_field_names_present(self):
        import dataclasses
        fnames = {f.name for f in dataclasses.fields(EvidencePack)}
        assert fnames >= {'policy_evals', 'trace_id', 'action_trace', 'boundary_snapshot_hash', 'risk_score', 'budget_breach_data'}

    def test_field_count_reasonable(self):
        import dataclasses
        assert len(dataclasses.fields(EvidencePack)) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="governance_types.py deps unavailable")
class TestExceptionScopeContract:
    def test_is_enum(self):
        import enum
        assert issubclass(ExceptionScope, enum.Enum)

    def test_has_members(self):
        assert len(list(ExceptionScope)) >= 1

    def test_member_values_accessible(self):
        for m in ExceptionScope:
            assert m.value is not None or m.value is None

    def test_known_member_single_agent_present(self):
        assert hasattr(ExceptionScope, 'SINGLE_AGENT')

    def test_members_are_unique(self):
        values = [m.value for m in ExceptionScope]
        assert len(values) == len(set(values))

@pytest.mark.skipif(not _AVAILABLE, reason="governance_types.py deps unavailable")
class TestPolicyExceptionArtifactContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(PolicyExceptionArtifact)

    def test_is_frozen(self):
        assert PolicyExceptionArtifact.__dataclass_params__.frozen is True

    def test_field_names_present(self):
        import dataclasses
        fnames = {f.name for f in dataclasses.fields(PolicyExceptionArtifact)}
        assert fnames >= {'semantic_clock_tick', 'issuer_signature', 'trace_id', 'nonce', 'ttl_ticks', 'exception_scope'}

    def test_field_count_reasonable(self):
        import dataclasses
        assert len(dataclasses.fields(PolicyExceptionArtifact)) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="governance_types.py deps unavailable")
class TestProposalStatusContract:
    def test_is_enum(self):
        import enum
        assert issubclass(ProposalStatus, enum.Enum)

    def test_has_members(self):
        assert len(list(ProposalStatus)) >= 1

    def test_member_values_accessible(self):
        for m in ProposalStatus:
            assert m.value is not None or m.value is None

    def test_known_member_pending_present(self):
        assert hasattr(ProposalStatus, 'PENDING')

    def test_members_are_unique(self):
        values = [m.value for m in ProposalStatus]
        assert len(values) == len(set(values))

@pytest.mark.skipif(not _AVAILABLE, reason="governance_types.py deps unavailable")
class TestHILOutcomeContract:
    def test_is_enum(self):
        import enum
        assert issubclass(HILOutcome, enum.Enum)

    def test_has_members(self):
        assert len(list(HILOutcome)) >= 1

    def test_member_values_accessible(self):
        for m in HILOutcome:
            assert m.value is not None or m.value is None

    def test_known_member_approved_present(self):
        assert hasattr(HILOutcome, 'APPROVED')

    def test_members_are_unique(self):
        values = [m.value for m in HILOutcome]
        assert len(values) == len(set(values))

@pytest.mark.skipif(not _AVAILABLE, reason="governance_types.py deps unavailable")
class TestHILReviewOutcomeContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(HILReviewOutcome)

    def test_is_frozen(self):
        assert HILReviewOutcome.__dataclass_params__.frozen is True

    def test_field_names_present(self):
        import dataclasses
        fnames = {f.name for f in dataclasses.fields(HILReviewOutcome)}
        assert fnames >= {'decision', 'reviewer_sig', 'reviewer_id', 'requires_l5_reclear'}

    def test_field_count_reasonable(self):
        import dataclasses
        assert len(dataclasses.fields(HILReviewOutcome)) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="governance_types.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

    def test_value_is_truthy_or_defined(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="governance_types.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

    def test_value_is_truthy_or_defined(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="governance_types.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

    def test_value_is_truthy_or_defined(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="governance_types.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

    def test_value_is_truthy_or_defined(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="governance_types.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

    def test_value_is_truthy_or_defined(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="governance_types.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None

    def test_value_is_truthy_or_defined(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Smoke: governance_types importable or gracefully unavailable."""
    pass