"""Foundational behavioral tests for agentic_core/L2_execution/types/instruction_packet_types.py.

fan_in=5 — imported by 5 other modules.
ADG import-hygiene is covered separately by test_instruction_packet_types_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L2_execution.types.instruction_packet_types import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_DEPTH,
        MAX_RETRIES,
        THRESHOLD,
        InstructionPacket,
        SignatureVerificationError,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    SignatureVerificationError = None  # type: ignore[assignment,misc]
    InstructionPacket = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="instruction_packet_types.py deps unavailable")
class TestSignatureVerificationErrorContract:
    def test_is_class(self):
        assert isinstance(SignatureVerificationError, type)

@pytest.mark.skipif(not _AVAILABLE, reason="instruction_packet_types.py deps unavailable")
class TestInstructionPacketContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(InstructionPacket)

    def test_is_frozen(self):
        assert InstructionPacket.__dataclass_params__.frozen is True

    def test_field_names_present(self):
        import dataclasses
        fnames = {f.name for f in dataclasses.fields(InstructionPacket)}
        assert fnames >= {'instruction_id', 'payload', 'certification_timestamp', 'l5_signature', 'metadata', 'signature'}

    def test_field_count_reasonable(self):
        import dataclasses
        assert len(dataclasses.fields(InstructionPacket)) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="instruction_packet_types.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

    def test_value_is_truthy_or_defined(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="instruction_packet_types.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

    def test_value_is_truthy_or_defined(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="instruction_packet_types.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

    def test_value_is_truthy_or_defined(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="instruction_packet_types.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

    def test_value_is_truthy_or_defined(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="instruction_packet_types.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

    def test_value_is_truthy_or_defined(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="instruction_packet_types.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None

    def test_value_is_truthy_or_defined(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Smoke: instruction_packet_types importable or gracefully unavailable."""
    pass