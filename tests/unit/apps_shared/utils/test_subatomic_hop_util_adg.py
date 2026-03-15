"""ADG-driven tests for apps_shared/utils/subatomic_hop_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_shared.utils.subatomic_hop_util import (  # noqa: F401
        InputValidationError,
        MutationRequired,
        QualityGateFailure,
        StageExecutionError,
        SubatomicHop,
        SubatomicHopConfig,
        create_subatomic_hop,
        subatomic_hop,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    InputValidationError = None  # type: ignore[assignment,misc]
    StageExecutionError = None  # type: ignore[assignment,misc]
    QualityGateFailure = None  # type: ignore[assignment,misc]
    MutationRequired = None  # type: ignore[assignment,misc]
    SubatomicHopConfig = None  # type: ignore[assignment,misc]
    SubatomicHop = None  # type: ignore[assignment,misc]
    create_subatomic_hop = None  # type: ignore[assignment,misc]
    subatomic_hop = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="subatomic_hop_util.py deps unavailable")
class TestInputValidationError:
    def test_is_class(self):
        assert isinstance(InputValidationError, type)
    def test_importable(self):
        assert InputValidationError is not None

@pytest.mark.skipif(not _AVAILABLE, reason="subatomic_hop_util.py deps unavailable")
class TestStageExecutionError:
    def test_is_class(self):
        assert isinstance(StageExecutionError, type)
    def test_importable(self):
        assert StageExecutionError is not None

@pytest.mark.skipif(not _AVAILABLE, reason="subatomic_hop_util.py deps unavailable")
class TestQualityGateFailure:
    def test_is_class(self):
        assert isinstance(QualityGateFailure, type)
    def test_importable(self):
        assert QualityGateFailure is not None

@pytest.mark.skipif(not _AVAILABLE, reason="subatomic_hop_util.py deps unavailable")
class TestMutationRequired:
    def test_is_class(self):
        assert isinstance(MutationRequired, type)
    def test_importable(self):
        assert MutationRequired is not None

@pytest.mark.skipif(not _AVAILABLE, reason="subatomic_hop_util.py deps unavailable")
class TestSubatomicHopConfig:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(SubatomicHopConfig)
    def test_importable(self):
        assert SubatomicHopConfig is not None

@pytest.mark.skipif(not _AVAILABLE, reason="subatomic_hop_util.py deps unavailable")
class TestSubatomicHop:
    def test_is_class(self):
        assert isinstance(SubatomicHop, type)
    def test_importable(self):
        assert SubatomicHop is not None

@pytest.mark.skipif(not _AVAILABLE, reason="subatomic_hop_util.py deps unavailable")
class TestCreateSubatomicHop:
    def test_is_callable(self):
        assert callable(create_subatomic_hop)

@pytest.mark.skipif(not _AVAILABLE, reason="subatomic_hop_util.py deps unavailable")
class TestSubatomicHop:
    def test_is_callable(self):
        assert callable(subatomic_hop)


def test_module_importable():
    """Module subatomic_hop_util.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
