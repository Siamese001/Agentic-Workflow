"""Behavioral tests for result_types_adg."""

from __future__ import annotations

import pytest

from agentic_core.result_types_adg import ResultEnvelope


def test_result_envelope_accepts_valid_status():
    assert ResultEnvelope(status="ok").validate().status == "ok"


def test_result_envelope_rejects_blank_status():
    with pytest.raises(ValueError):
        ResultEnvelope(status=" ").validate()
