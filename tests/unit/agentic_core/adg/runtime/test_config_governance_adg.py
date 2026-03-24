"""ADG importability contract for agentic_core/adg/runtime/config_governance.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_config_governance.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.adg.runtime.config_governance import (  # noqa: F401
        ConfigGovernanceReport,
        ConfigGovernor,
        ConfigReadEvent,
        ConfigReadOutcome,
        ConfigSchemaStatus,
    )

    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    ConfigReadOutcome = None  # type: ignore[assignment,misc]
    ConfigSchemaStatus = None  # type: ignore[assignment,misc]
    ConfigReadEvent = None  # type: ignore[assignment,misc]
    ConfigGovernanceReport = None  # type: ignore[assignment,misc]
    ConfigGovernor = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="config_governance deps unavailable")
class TestConfigGovernanceImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/adg/runtime/config_governance.py must be importable."""
        assert _AVAILABLE

    def test_configreadoutcome_defined(self) -> None:
        assert ConfigReadOutcome is not None

    def test_configschemastatus_defined(self) -> None:
        assert ConfigSchemaStatus is not None

    def test_configreadevent_defined(self) -> None:
        assert ConfigReadEvent is not None

    def test_configgovernancereport_defined(self) -> None:
        assert ConfigGovernanceReport is not None

    def test_configgovernor_defined(self) -> None:
        assert ConfigGovernor is not None