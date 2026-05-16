"""Reasoning transport capability declaration (generic, provider-agnostic).

Providers may expose which keyword arguments they forward to the outbound
inference request via ``reasoning_transport_kw_forwarded`` returning a frozenset
of names. Sovereign gateway uses this to classify APPLIED vs IGNORED entries.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class TransportCapabilities:
    """Keyword names the active provider forwards to outbound transport."""

    forwarded_kw_names: frozenset[str]

    @staticmethod
    def from_provider(provider_impl: Any) -> TransportCapabilities:
        getter = getattr(provider_impl, "reasoning_transport_kw_forwarded", None)
        if callable(getter):
            names = getter()
            if isinstance(names, frozenset):
                return TransportCapabilities(forwarded_kw_names=names)
            if isinstance(names, (set, list, tuple)):
                return TransportCapabilities(forwarded_kw_names=frozenset(str(x) for x in names))
        return TransportCapabilities(frozenset())


__all__ = ["TransportCapabilities"]
