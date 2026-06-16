"""EmbeddingServiceFactory device default tests."""

from __future__ import annotations

import sys
from types import SimpleNamespace

from agentic_core.L6_system_learning.engines.embedding_service_factory import EmbeddingServiceFactory


def test_embedding_service_explicit_device_wins(monkeypatch) -> None:
    monkeypatch.setenv("EMBEDDING_DEVICE", "cpu")

    assert EmbeddingServiceFactory._embedding_device() == "cpu"


def test_embedding_service_defaults_to_cuda_when_torch_reports_cuda(monkeypatch) -> None:
    fake_torch = SimpleNamespace(cuda=SimpleNamespace(is_available=lambda: True))

    monkeypatch.delenv("EMBEDDING_DEVICE", raising=False)
    monkeypatch.setitem(sys.modules, "torch", fake_torch)

    assert EmbeddingServiceFactory._embedding_device() == "cuda"


def test_embedding_service_defaults_to_cpu_without_cuda(monkeypatch) -> None:
    fake_torch = SimpleNamespace(cuda=SimpleNamespace(is_available=lambda: False))

    monkeypatch.delenv("EMBEDDING_DEVICE", raising=False)
    monkeypatch.setitem(sys.modules, "torch", fake_torch)

    assert EmbeddingServiceFactory._embedding_device() == "cpu"
