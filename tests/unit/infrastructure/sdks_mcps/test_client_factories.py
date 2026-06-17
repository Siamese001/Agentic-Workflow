"""Tests for infrastructure.sdks_mcps factory helpers."""

from __future__ import annotations

import sys
from types import ModuleType

import pytest

from infrastructure.sdks_mcps import (
    create_anthropic_client,
    create_gemini_model,
    create_openai_client,
    create_openai_sync_client,
    create_vertex_client,
)


def _fake_openai_module() -> tuple[ModuleType, type, type]:
    module = ModuleType("openai")

    class AsyncOpenAI:
        def __init__(self, *, api_key: str) -> None:
            self.api_key = api_key

    class OpenAI:
        def __init__(self, *, api_key: str) -> None:
            self.api_key = api_key

    module.AsyncOpenAI = AsyncOpenAI
    module.OpenAI = OpenAI
    return module, AsyncOpenAI, OpenAI


def _fake_anthropic_module() -> tuple[ModuleType, type]:
    module = ModuleType("anthropic")

    class AsyncAnthropic:
        def __init__(self, *, api_key: str) -> None:
            self.api_key = api_key

    module.AsyncAnthropic = AsyncAnthropic
    return module, AsyncAnthropic


def _fake_genai_module() -> tuple[ModuleType, ModuleType, list[str], type]:
    google_pkg = ModuleType("google")
    google_pkg.__path__ = []  # mark as package for import machinery

    genai = ModuleType("google.generativeai")
    configure_calls: list[str] = []

    class GenerativeModel:
        def __init__(self, model_name: str) -> None:
            self.model_name = model_name

    def configure(*, api_key: str) -> None:
        configure_calls.append(api_key)

    genai.configure = configure
    genai.GenerativeModel = GenerativeModel
    google_pkg.generativeai = genai
    return google_pkg, genai, configure_calls, GenerativeModel


def test_create_openai_client_uses_env_and_async_client(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "openai-key")
    module, AsyncOpenAI, _ = _fake_openai_module()
    monkeypatch.setitem(sys.modules, "openai", module)

    client = create_openai_client()

    assert isinstance(client, AsyncOpenAI)
    assert client.api_key == "openai-key"


def test_create_openai_client_raises_without_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    with pytest.raises(ValueError, match="OPENAI_API_KEY missing"):
        create_openai_client()


def test_create_openai_sync_client_uses_env_and_sync_client(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "openai-sync-key")
    module, _, OpenAI = _fake_openai_module()
    monkeypatch.setitem(sys.modules, "openai", module)

    client = create_openai_sync_client()

    assert isinstance(client, OpenAI)
    assert client.api_key == "openai-sync-key"


def test_create_openai_sync_client_raises_without_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    with pytest.raises(ValueError, match="OPENAI_API_KEY missing"):
        create_openai_sync_client()


def test_create_anthropic_client_uses_env_and_async_client(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ANTHROPIC_API_KEY", "anthropic-key")
    module, AsyncAnthropic = _fake_anthropic_module()
    monkeypatch.setitem(sys.modules, "anthropic", module)

    client = create_anthropic_client()

    assert isinstance(client, AsyncAnthropic)
    assert client.api_key == "anthropic-key"


def test_create_anthropic_client_raises_without_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    with pytest.raises(ValueError, match="ANTHROPIC_API_KEY missing"):
        create_anthropic_client()


def test_create_vertex_client_uses_google_api_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("GOOGLE_API_KEY", "google-key")
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    google_pkg, genai, configure_calls, _ = _fake_genai_module()
    monkeypatch.setitem(sys.modules, "google", google_pkg)
    monkeypatch.setitem(sys.modules, "google.generativeai", genai)

    client = create_vertex_client()

    assert client is genai
    assert configure_calls == ["google-key"]


def test_create_vertex_client_raises_without_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    google_pkg, genai, _, _ = _fake_genai_module()
    monkeypatch.setitem(sys.modules, "google", google_pkg)
    monkeypatch.setitem(sys.modules, "google.generativeai", genai)

    with pytest.raises(ValueError, match="GOOGLE_API_KEY missing"):
        create_vertex_client()


def test_create_gemini_model_uses_gemini_api_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("GEMINI_API_KEY", "gemini-key")
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    google_pkg, genai, configure_calls, GenerativeModel = _fake_genai_module()
    monkeypatch.setitem(sys.modules, "google", google_pkg)
    monkeypatch.setitem(sys.modules, "google.generativeai", genai)

    model = create_gemini_model("gemini-2.5-flash")

    assert isinstance(model, GenerativeModel)
    assert model.model_name == "gemini-2.5-flash"
    assert configure_calls == ["gemini-key"]
