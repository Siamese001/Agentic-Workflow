"""ADG-driven tests for L2_execution/determinism/negative_control_harness.py — fan_in=0."""
from __future__ import annotations

import os

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L2_execution.determinism.negative_control_harness import (
    assert_digest_differs,
    get_config_surface,
    is_tamper_active,
)


class TestIsTamperActive:
    def test_returns_false_by_default(self, monkeypatch):
        monkeypatch.delenv("W_HARDEN_NEGCTRL_TAMPER", raising=False)
        assert is_tamper_active() is False

    def test_returns_true_when_set_to_1(self, monkeypatch):
        monkeypatch.setenv("W_HARDEN_NEGCTRL_TAMPER", "1")
        assert is_tamper_active() is True

    def test_returns_false_for_other_values(self, monkeypatch):
        monkeypatch.setenv("W_HARDEN_NEGCTRL_TAMPER", "true")
        assert is_tamper_active() is False


class TestGetConfigSurface:
    def test_returns_dict(self, monkeypatch):
        monkeypatch.delenv("W_HARDEN_NEGCTRL_TAMPER", raising=False)
        result = get_config_surface()
        assert isinstance(result, dict)


class TestAssertDigestDiffers:
    def test_callable(self):
        assert callable(assert_digest_differs)

    def test_raises_if_same(self):
        with pytest.raises(AssertionError):
            assert_digest_differs("abc", "abc")

    def test_passes_if_different(self):
        assert_digest_differs("abc", "def")
