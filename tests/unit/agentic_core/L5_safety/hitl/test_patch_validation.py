"""Addendum 6.1: HITL Patch Validator tests."""

from __future__ import annotations

import pytest

from agentic_core.L5_safety.hitl.patch_validator import ValidatedPatch, validate_patch
from agentic_core.L5_safety.types.hardening_errors import HumanPatchValidationError


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

class TestValidatePatch:
    def _valid_patch(self) -> dict:
        return {
            "original_plan_hash": "abc123",
            "structured_patch_schema": {"type": "MODIFY_DIFF", "file": "foo.py"},
            "reviewer_signature": "reviewer@example.com",
        }

    def test_valid_patch_returns_validated(self):
        result = validate_patch(self._valid_patch())
        assert isinstance(result, ValidatedPatch)
        assert result.reviewer_signature == "reviewer@example.com"
        assert result.original_plan_hash == "abc123"
        assert result.patch_hash  # non-empty SHA256

    def test_patch_hash_is_64_chars(self):
        result = validate_patch(self._valid_patch())
        assert len(result.patch_hash) == 64

    def test_missing_reviewer_signature_raises(self):
        patch = self._valid_patch()
        del patch["reviewer_signature"]
        with pytest.raises(HumanPatchValidationError, match="reviewer_signature"):
            validate_patch(patch)

    def test_missing_plan_hash_raises(self):
        patch = self._valid_patch()
        del patch["original_plan_hash"]
        with pytest.raises(HumanPatchValidationError, match="original_plan_hash"):
            validate_patch(patch)

    def test_missing_patch_schema_raises(self):
        patch = self._valid_patch()
        del patch["structured_patch_schema"]
        with pytest.raises(HumanPatchValidationError, match="structured_patch_schema"):
            validate_patch(patch)

    def test_empty_reviewer_signature_raises(self):
        patch = self._valid_patch()
        patch["reviewer_signature"] = ""
        with pytest.raises(HumanPatchValidationError, match="reviewer_signature"):
            validate_patch(patch)

    def test_empty_dict_raises(self):
        with pytest.raises(HumanPatchValidationError):
            validate_patch({})

    def test_different_patches_different_hashes(self):
        p1 = self._valid_patch()
        p2 = dict(self._valid_patch())
        p2["reviewer_signature"] = "other@example.com"
        r1 = validate_patch(p1)
        r2 = validate_patch(p2)
        assert r1.patch_hash != r2.patch_hash

    def test_negative_complete_patch_never_raises(self):
        """Negative control: all fields present must never raise."""
        raised = False
        try:
            validate_patch(self._valid_patch())
        except HumanPatchValidationError:  # guardian: allow-silent-swallower
            raised = True
        assert not raised
