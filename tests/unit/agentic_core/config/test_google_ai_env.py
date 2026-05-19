"""Canonical Google AI env resolution."""

from __future__ import annotations

import os

import pytest

from agentic_core.config.google_ai_env import (
    GOOGLE_AI_MODEL,
    GOOGLE_AI_PRO_MODEL,
    GOOGLE_API_KEY,
    google_ai_flash_model_id,
    google_ai_pro_model_id,
    google_api_key,
)


def test_google_api_key_prefers_canonical(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(GOOGLE_API_KEY, "canonical-key")
    monkeypatch.setenv("GEMINI_API_KEY", "legacy-key")
    key, source = google_api_key()
    assert key == "canonical-key"
    assert source == GOOGLE_API_KEY


def test_google_ai_flash_model_prefers_canonical(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(GOOGLE_AI_MODEL, "gemini-2.5-flash")
    monkeypatch.setenv("GEMINI_MODEL", "gemini-3-flash-preview")
    model, source = google_ai_flash_model_id()
    assert model == "gemini-2.5-flash"
    assert source == GOOGLE_AI_MODEL


def test_google_ai_pro_model_prefers_canonical(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(GOOGLE_AI_PRO_MODEL, "gemini-2.5-pro")
    monkeypatch.setenv("GEMINI_PRO_MODEL", "gemini-3.1-pro-preview")
    model, source = google_ai_pro_model_id()
    assert model == "gemini-2.5-pro"
    assert source == GOOGLE_AI_PRO_MODEL
