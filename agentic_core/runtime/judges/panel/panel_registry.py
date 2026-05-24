"""Registry of judge panel provider adapters."""

from __future__ import annotations

from agentic_core.runtime.judges.panel.adapter_protocol import JudgeProviderAdapter


class PanelAdapterRegistry:
    def __init__(self) -> None:
        self._adapters: dict[str, JudgeProviderAdapter] = {}

    def register(self, adapter: JudgeProviderAdapter) -> None:
        key = str(adapter.provider_key)
        if not key:
            raise ValueError("adapter.provider_key is required")
        self._adapters[key] = adapter

    def get(self, provider_key: str) -> JudgeProviderAdapter:
        try:
            return self._adapters[provider_key]
        except KeyError as exc:
            raise KeyError(f"no panel adapter registered for {provider_key!r}") from exc

    def keys(self) -> frozenset[str]:
        return frozenset(self._adapters.keys())


__all__ = ["PanelAdapterRegistry"]
