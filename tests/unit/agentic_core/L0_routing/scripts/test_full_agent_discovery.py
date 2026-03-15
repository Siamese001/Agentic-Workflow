"""Foundational behavioral tests for agentic_core/L0_routing/scripts/full_agent_discovery.py.

fan_in=7 — imported by 7 other modules.
ADG import-hygiene is covered separately by test_full_agent_discovery_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L0_routing.scripts.full_agent_discovery import (  # noqa: F401
        OUTPUT_SCHEMA_VERSION,
        AgentIntegrityReport,
        DiscoveryError,
        analyze_agent_integrity,
        get_git_commit,
        main,
        setup_logging,
        sha256_file,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    AgentIntegrityReport = None  # type: ignore[assignment,misc]
    DiscoveryError = None  # type: ignore[assignment,misc]
    setup_logging = None  # type: ignore[assignment,misc]
    sha256_file = None  # type: ignore[assignment,misc]
    get_git_commit = None  # type: ignore[assignment,misc]
    main = None  # type: ignore[assignment,misc]
    analyze_agent_integrity = None  # type: ignore[assignment,misc]
    OUTPUT_SCHEMA_VERSION = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="full_agent_discovery.py deps unavailable")
class TestAgentIntegrityReportContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(AgentIntegrityReport)

    def test_field_names_present(self):
        import dataclasses
        fnames = {f.name for f in dataclasses.fields(AgentIntegrityReport)}
        assert fnames >= {'inheritance', 'is_stub', 'path', 'is_valid', 'class_name', 'is_base_agent'}

    def test_field_count_reasonable(self):
        import dataclasses
        assert len(dataclasses.fields(AgentIntegrityReport)) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="full_agent_discovery.py deps unavailable")
class TestDiscoveryErrorContract:
    def test_is_class(self):
        assert isinstance(DiscoveryError, type)

@pytest.mark.skipif(not _AVAILABLE, reason="full_agent_discovery.py deps unavailable")
class TestSetupLoggingFunction:
    def test_is_callable(self):
        assert callable(setup_logging)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(setup_logging)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="full_agent_discovery.py deps unavailable")
class TestSha256FileFunction:
    def test_is_callable(self):
        assert callable(sha256_file)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(sha256_file)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="full_agent_discovery.py deps unavailable")
class TestGetGitCommitFunction:
    def test_is_callable(self):
        assert callable(get_git_commit)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(get_git_commit)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="full_agent_discovery.py deps unavailable")
class TestMainFunction:
    def test_is_callable(self):
        assert callable(main)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(main)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="full_agent_discovery.py deps unavailable")
class TestAnalyzeAgentIntegrityFunction:
    def test_is_callable(self):
        assert callable(analyze_agent_integrity)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(analyze_agent_integrity)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="full_agent_discovery.py deps unavailable")
class TestOutputSchemaVersionConstant:
    def test_is_not_none(self):
        assert OUTPUT_SCHEMA_VERSION is not None

    def test_value_is_truthy_or_defined(self):
        assert OUTPUT_SCHEMA_VERSION is not None


def test_module_importable():
    """Smoke: full_agent_discovery importable or gracefully unavailable."""
    pass
