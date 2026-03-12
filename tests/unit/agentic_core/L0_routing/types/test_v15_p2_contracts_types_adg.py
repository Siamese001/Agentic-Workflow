"""ADG contract tests for L0_routing/types/v15_p2_contracts_types.py."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit
from agentic_core.L0_routing.types.v15_p2_contracts_types import (
    ForbiddenInputError, EpisodicMemoryNotQueried, RollbackHashMismatch, WallClockViolation,
    dedupe_sha256, validate_execution_input,
)

class TestCompatExceptions:
    def test_forbidden_input_error_importable(self): assert ForbiddenInputError is not None
    def test_episodic_memory_not_queried_importable(self): assert EpisodicMemoryNotQueried is not None
    def test_rollback_hash_mismatch_importable(self): assert RollbackHashMismatch is not None
    def test_wall_clock_violation_importable(self): assert WallClockViolation is not None

class TestCompatFunctions:
    def test_dedupe_sha256_callable(self): assert callable(dedupe_sha256)
    def test_validate_execution_input_callable(self): assert callable(validate_execution_input)
    def test_dedupe_sha256_produces_hash(self):
        h = dedupe_sha256("test content"); assert isinstance(h, str); assert len(h) == 64
