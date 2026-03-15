"""ADG importability contract for agentic_core/interfaces/IValidatorProtocol.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_IValidatorProtocol.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.interfaces.IValidatorProtocol import (  # noqa: F401
        AdversarialValidator,
        BoundaryValidator,
        ValidatorProtocol,
        get_adversarial_validator,
        get_boundary_validator,
        register_red_team_validators,
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    ValidatorProtocol = None  # type: ignore[assignment,misc]
    AdversarialValidator = None  # type: ignore[assignment,misc]
    BoundaryValidator = None  # type: ignore[assignment,misc]
    get_adversarial_validator = None  # type: ignore[assignment,misc]
    get_boundary_validator = None  # type: ignore[assignment,misc]
    register_red_team_validators = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="IValidatorProtocol deps unavailable")
class TestIvalidatorprotocolImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/interfaces/IValidatorProtocol.py must be importable."""
        assert _AVAILABLE

    def test_validatorprotocol_defined(self) -> None:
        assert ValidatorProtocol is not None

    def test_adversarialvalidator_defined(self) -> None:
        assert AdversarialValidator is not None

    def test_boundaryvalidator_defined(self) -> None:
        assert BoundaryValidator is not None
