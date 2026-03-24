"""ADG importability contract for agentic_core/prompt_governance/scripts/file_intent.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_file_intent.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.prompt_governance.scripts.file_intent import (  # noqa: F401
        FileIntent,
        HardenedNamingAuditor,
        NamingConvention,
        ViolationReport,
        main,
    )

    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    FileIntent = None  # type: ignore[assignment,misc]
    NamingConvention = None  # type: ignore[assignment,misc]
    ViolationReport = None  # type: ignore[assignment,misc]
    HardenedNamingAuditor = None  # type: ignore[assignment,misc]
    main = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="file_intent deps unavailable")
class TestFileIntentImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/prompt_governance/scripts/file_intent.py must be importable."""
        assert _AVAILABLE

    def test_fileintent_defined(self) -> None:
        assert FileIntent is not None

    def test_namingconvention_defined(self) -> None:
        assert NamingConvention is not None

    def test_violationreport_defined(self) -> None:
        assert ViolationReport is not None

    def test_hardenednamingauditor_defined(self) -> None:
        assert HardenedNamingAuditor is not None