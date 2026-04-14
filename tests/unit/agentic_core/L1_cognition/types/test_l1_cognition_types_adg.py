"""Behavioral tests for l1_cognition_types_adg."""

from __future__ import annotations

import pytest

from agentic_core.l1_cognition_types_adg import L1CognitionSnapshot


def test_l1_cognition_snapshot_accepts_valid_shape():
    assert L1CognitionSnapshot(stage="reason", grounded=True).validate().grounded is True


def test_l1_cognition_snapshot_rejects_blank_stage():
    with pytest.raises(ValueError):
        L1CognitionSnapshot(stage="", grounded=True).validate()
