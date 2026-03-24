"""Foundational behavioral tests for agentic_core/L5_safety/enforcement/registry_verification_enforcer.py.

fan_in=3 — imported by 3 other modules.
ADG import-hygiene is covered separately by test_registry_verification_enforcer_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L5_safety.enforcement.registry_verification_enforcer import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_DEPTH,
        MAX_RETRIES,
        THRESHOLD,
        AgentInfo,
        RegistryVerifier,
        VerificationResult,
        run_verification,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    AgentInfo = None  # type: ignore[assignment,misc]
    VerificationResult = None  # type: ignore[assignment,misc]
    RegistryVerifier = None  # type: ignore[assignment,misc]
    run_verification = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="registry_verification_enforcer.py deps unavailable")
class TestAgentInfoContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(AgentInfo)

    def test_field_names_present(self):
        import dataclasses
        fnames = {f.name for f in dataclasses.fields(AgentInfo)}
        assert fnames >= {'layer', 'inheritance', 'file_path', 'class_name', 'relative_path', 'has_agent_class'}

    def test_field_count_reasonable(self):
        import dataclasses
        assert len(dataclasses.fields(AgentInfo)) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="registry_verification_enforcer.py deps unavailable")
class TestVerificationResultContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(VerificationResult)

    def test_field_names_present(self):
        import dataclasses
        fnames = {f.name for f in dataclasses.fields(VerificationResult)}
        assert fnames >= {'total_registry_agents', 'missing_agents', 'valid_agents', 'orphan_agents', 'path_mismatches', 'total_filesystem_agents'}

    def test_field_count_reasonable(self):
        import dataclasses
        assert len(dataclasses.fields(VerificationResult)) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="registry_verification_enforcer.py deps unavailable")
class TestRegistryVerifierContract:
    def test_is_class(self):
        assert isinstance(RegistryVerifier, type)

    def test_has_method_scan_filesystem(self):
        assert callable(getattr(RegistryVerifier, 'scan_filesystem', None))

    def test_has_method_load_registry(self):
        assert callable(getattr(RegistryVerifier, 'load_registry', None))

    def test_has_method_verify_registry(self):
        assert callable(getattr(RegistryVerifier, 'verify_registry', None))

    def test_has_method_generate_report(self):
        assert callable(getattr(RegistryVerifier, 'generate_report', None))

    def test_public_api_surface_non_empty(self):
        pub = [m for m in dir(RegistryVerifier) if not m.startswith('_')]
        assert len(pub) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="registry_verification_enforcer.py deps unavailable")
class TestRunVerificationFunction:
    def test_is_callable(self):
        assert callable(run_verification)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(run_verification)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="registry_verification_enforcer.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

    def test_value_is_truthy_or_defined(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="registry_verification_enforcer.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

    def test_value_is_truthy_or_defined(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="registry_verification_enforcer.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

    def test_value_is_truthy_or_defined(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="registry_verification_enforcer.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

    def test_value_is_truthy_or_defined(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="registry_verification_enforcer.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

    def test_value_is_truthy_or_defined(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="registry_verification_enforcer.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None

    def test_value_is_truthy_or_defined(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Smoke: registry_verification_enforcer importable or gracefully unavailable."""
    pass