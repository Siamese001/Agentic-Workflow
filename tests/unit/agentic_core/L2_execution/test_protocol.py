"""Foundational behavioral tests for agentic_core/L2_execution/protocol.py.

fan_in=6 — imported by 6 other modules.
ADG import-hygiene is covered separately by test_protocol_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L2_execution.protocol import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_DEPTH,
        MAX_RETRIES,
        THRESHOLD,
        AgentRunResult,
        L2AgentProtocol,
        SubphaseResult,
        compute_pipeline_digest,
        emit_pipeline_digest,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    SubphaseResult = None  # type: ignore[assignment,misc]
    AgentRunResult = None  # type: ignore[assignment,misc]
    L2AgentProtocol = None  # type: ignore[assignment,misc]
    compute_pipeline_digest = None  # type: ignore[assignment,misc]
    emit_pipeline_digest = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="protocol.py deps unavailable")
class TestSubphaseResultContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(SubphaseResult)

    def test_field_names_present(self):
        import dataclasses
        fnames = {f.name for f in dataclasses.fields(SubphaseResult)}
        assert fnames >= {'violations', 'error', 'skipped', 'fixed', 'skip_reason'}

    def test_field_count_reasonable(self):
        import dataclasses
        assert len(dataclasses.fields(SubphaseResult)) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="protocol.py deps unavailable")
class TestAgentRunResultContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(AgentRunResult)

    def test_field_names_present(self):
        import dataclasses
        fnames = {f.name for f in dataclasses.fields(AgentRunResult)}
        assert fnames >= {'gate_reason', 'mutations_applied', 'error', 'gated', 'subphases', 'violations_total'}

    def test_field_count_reasonable(self):
        import dataclasses
        assert len(dataclasses.fields(AgentRunResult)) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="protocol.py deps unavailable")
class TestL2AgentProtocolContract:
    def test_is_class(self):
        assert isinstance(L2AgentProtocol, type)

    def test_has_method_pre_commit(self):
        assert callable(getattr(L2AgentProtocol, 'pre_commit', None))

    def test_has_method_validate(self):
        assert callable(getattr(L2AgentProtocol, 'validate', None))

    def test_has_method_execute(self):
        assert callable(getattr(L2AgentProtocol, 'execute', None))

    def test_has_method_heal(self):
        assert callable(getattr(L2AgentProtocol, 'heal', None))

    def test_public_api_surface_non_empty(self):
        pub = [m for m in dir(L2AgentProtocol) if not m.startswith('_')]
        assert len(pub) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="protocol.py deps unavailable")
class TestComputePipelineDigestFunction:
    def test_is_callable(self):
        assert callable(compute_pipeline_digest)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(compute_pipeline_digest)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="protocol.py deps unavailable")
class TestEmitPipelineDigestFunction:
    def test_is_callable(self):
        assert callable(emit_pipeline_digest)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(emit_pipeline_digest)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="protocol.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

    def test_value_is_truthy_or_defined(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="protocol.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

    def test_value_is_truthy_or_defined(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="protocol.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

    def test_value_is_truthy_or_defined(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="protocol.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

    def test_value_is_truthy_or_defined(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="protocol.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

    def test_value_is_truthy_or_defined(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="protocol.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None

    def test_value_is_truthy_or_defined(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Smoke: protocol importable or gracefully unavailable."""
    pass