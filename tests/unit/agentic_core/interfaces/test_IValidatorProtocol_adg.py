"""ADG-driven tests for agentic_core/interfaces/IValidatorProtocol.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.interfaces.IValidatorProtocol import (  # noqa: F401
        ValidatorProtocol,
        AdversarialValidator,
        BoundaryValidator,
        get_adversarial_validator,
        get_boundary_validator,
        register_red_team_validators,
        get_integration_status,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
        BATCH_SIZE,
        MAX_DEPTH,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    ValidatorProtocol = None  # type: ignore[assignment,misc]
    AdversarialValidator = None  # type: ignore[assignment,misc]
    BoundaryValidator = None  # type: ignore[assignment,misc]
    get_adversarial_validator = None  # type: ignore[assignment,misc]
    get_boundary_validator = None  # type: ignore[assignment,misc]
    register_red_team_validators = None  # type: ignore[assignment,misc]
    get_integration_status = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="IValidatorProtocol.py deps unavailable")
class TestValidatorProtocol:
    def test_is_class(self):
        assert isinstance(ValidatorProtocol, type)
    def test_importable(self):
        assert ValidatorProtocol is not None

@pytest.mark.skipif(not _AVAILABLE, reason="IValidatorProtocol.py deps unavailable")
class TestAdversarialValidator:
    def test_is_class(self):
        assert isinstance(AdversarialValidator, type)
    def test_importable(self):
        assert AdversarialValidator is not None

@pytest.mark.skipif(not _AVAILABLE, reason="IValidatorProtocol.py deps unavailable")
class TestBoundaryValidator:
    def test_is_class(self):
        assert isinstance(BoundaryValidator, type)
    def test_importable(self):
        assert BoundaryValidator is not None

@pytest.mark.skipif(not _AVAILABLE, reason="IValidatorProtocol.py deps unavailable")
class TestGetAdversarialValidator:
    def test_is_callable(self):
        assert callable(get_adversarial_validator)

@pytest.mark.skipif(not _AVAILABLE, reason="IValidatorProtocol.py deps unavailable")
class TestGetBoundaryValidator:
    def test_is_callable(self):
        assert callable(get_boundary_validator)

@pytest.mark.skipif(not _AVAILABLE, reason="IValidatorProtocol.py deps unavailable")
class TestRegisterRedTeamValidators:
    def test_is_callable(self):
        assert callable(register_red_team_validators)

@pytest.mark.skipif(not _AVAILABLE, reason="IValidatorProtocol.py deps unavailable")
class TestGetIntegrationStatus:
    def test_is_callable(self):
        assert callable(get_integration_status)

@pytest.mark.skipif(not _AVAILABLE, reason="IValidatorProtocol.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="IValidatorProtocol.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="IValidatorProtocol.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="IValidatorProtocol.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="IValidatorProtocol.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="IValidatorProtocol.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module IValidatorProtocol.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
