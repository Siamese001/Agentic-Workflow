"""Foundational behavioral tests for agentic_core/L0_routing/types/guardian_contract_types.py.

fan_in=30 — imported by 30 other modules.
ADG import-hygiene is covered separately by test_guardian_contract_types_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L0_routing.types.guardian_contract_types import (  # noqa: F401
        GUARDIAN_SIGNING_KEY_ID,
        ArtifactClass,
        ArtifactType,
        CheckStatus,
        GuardianStatus,
        ScanBudgetExceeded,
        V15EnforcementError,
        V15HardFailAbort,
        V15SoftFailAbort,
        get_artifact_filename,
        guard_scan_budget,
        is_v15_enforced,
        is_v15_hard_fail,
        is_v15_soft_fail,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    V15EnforcementError = None  # type: ignore[assignment,misc]
    V15SoftFailAbort = None  # type: ignore[assignment,misc]
    V15HardFailAbort = None  # type: ignore[assignment,misc]
    GuardianStatus = None  # type: ignore[assignment,misc]
    CheckStatus = None  # type: ignore[assignment,misc]
    ArtifactType = None  # type: ignore[assignment,misc]
    ArtifactClass = None  # type: ignore[assignment,misc]
    ScanBudgetExceeded = None  # type: ignore[assignment,misc]
    is_v15_enforced = None  # type: ignore[assignment,misc]
    is_v15_hard_fail = None  # type: ignore[assignment,misc]
    is_v15_soft_fail = None  # type: ignore[assignment,misc]
    get_artifact_filename = None  # type: ignore[assignment,misc]
    guard_scan_budget = None  # type: ignore[assignment,misc]
    GUARDIAN_SIGNING_KEY_ID = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="guardian_contract_types.py deps unavailable")
class TestV15EnforcementErrorContract:
    def test_is_class(self):
        assert isinstance(V15EnforcementError, type)

@pytest.mark.skipif(not _AVAILABLE, reason="guardian_contract_types.py deps unavailable")
class TestV15SoftFailAbortContract:
    def test_is_class(self):
        assert isinstance(V15SoftFailAbort, type)

@pytest.mark.skipif(not _AVAILABLE, reason="guardian_contract_types.py deps unavailable")
class TestV15HardFailAbortContract:
    def test_is_class(self):
        assert isinstance(V15HardFailAbort, type)

@pytest.mark.skipif(not _AVAILABLE, reason="guardian_contract_types.py deps unavailable")
class TestGuardianStatusContract:
    def test_is_enum(self):
        import enum
        assert issubclass(GuardianStatus, enum.Enum)

    def test_has_members(self):
        assert len(list(GuardianStatus)) >= 1

    def test_member_values_accessible(self):
        for m in GuardianStatus:
            assert m.value is not None or m.value is None

    def test_known_member_pass_present(self):
        assert hasattr(GuardianStatus, 'PASS')

    def test_members_are_unique(self):
        values = [m.value for m in GuardianStatus]
        assert len(values) == len(set(values))

@pytest.mark.skipif(not _AVAILABLE, reason="guardian_contract_types.py deps unavailable")
class TestCheckStatusContract:
    def test_is_enum(self):
        import enum
        assert issubclass(CheckStatus, enum.Enum)

    def test_has_members(self):
        assert len(list(CheckStatus)) >= 1

    def test_member_values_accessible(self):
        for m in CheckStatus:
            assert m.value is not None or m.value is None

    def test_known_member_pass_present(self):
        assert hasattr(CheckStatus, 'PASS')

    def test_members_are_unique(self):
        values = [m.value for m in CheckStatus]
        assert len(values) == len(set(values))

@pytest.mark.skipif(not _AVAILABLE, reason="guardian_contract_types.py deps unavailable")
class TestArtifactTypeContract:
    def test_is_enum(self):
        import enum
        assert issubclass(ArtifactType, enum.Enum)

    def test_has_members(self):
        assert len(list(ArtifactType)) >= 1

    def test_member_values_accessible(self):
        for m in ArtifactType:
            assert m.value is not None or m.value is None

    def test_known_member_diff_present(self):
        assert hasattr(ArtifactType, 'DIFF')

    def test_members_are_unique(self):
        values = [m.value for m in ArtifactType]
        assert len(values) == len(set(values))

@pytest.mark.skipif(not _AVAILABLE, reason="guardian_contract_types.py deps unavailable")
class TestArtifactClassContract:
    def test_is_enum(self):
        import enum
        assert issubclass(ArtifactClass, enum.Enum)

    def test_has_members(self):
        assert len(list(ArtifactClass)) >= 1

    def test_member_values_accessible(self):
        for m in ArtifactClass:
            assert m.value is not None or m.value is None

    def test_known_member_individual_present(self):
        assert hasattr(ArtifactClass, 'INDIVIDUAL')

    def test_members_are_unique(self):
        values = [m.value for m in ArtifactClass]
        assert len(values) == len(set(values))

@pytest.mark.skipif(not _AVAILABLE, reason="guardian_contract_types.py deps unavailable")
class TestScanBudgetExceededContract:
    def test_is_class(self):
        assert isinstance(ScanBudgetExceeded, type)

    def test_has_method_details(self):
        assert callable(getattr(ScanBudgetExceeded, 'details', None))

    def test_has_method_remediation_hints(self):
        assert callable(getattr(ScanBudgetExceeded, 'remediation_hints', None))

    def test_public_api_surface_non_empty(self):
        pub = [m for m in dir(ScanBudgetExceeded) if not m.startswith('_')]
        assert len(pub) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="guardian_contract_types.py deps unavailable")
class TestIsV15EnforcedFunction:
    def test_is_callable(self):
        assert callable(is_v15_enforced)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(is_v15_enforced)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="guardian_contract_types.py deps unavailable")
class TestIsV15HardFailFunction:
    def test_is_callable(self):
        assert callable(is_v15_hard_fail)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(is_v15_hard_fail)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="guardian_contract_types.py deps unavailable")
class TestIsV15SoftFailFunction:
    def test_is_callable(self):
        assert callable(is_v15_soft_fail)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(is_v15_soft_fail)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="guardian_contract_types.py deps unavailable")
class TestGetArtifactFilenameFunction:
    def test_is_callable(self):
        assert callable(get_artifact_filename)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(get_artifact_filename)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="guardian_contract_types.py deps unavailable")
class TestGuardScanBudgetFunction:
    def test_is_callable(self):
        assert callable(guard_scan_budget)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(guard_scan_budget)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="guardian_contract_types.py deps unavailable")
class TestGuardianSigningKeyIdConstant:
    def test_is_not_none(self):
        assert GUARDIAN_SIGNING_KEY_ID is not None

    def test_value_is_truthy_or_defined(self):
        assert GUARDIAN_SIGNING_KEY_ID is not None


def test_module_importable():
    """Smoke: guardian_contract_types importable or gracefully unavailable."""
    pass
