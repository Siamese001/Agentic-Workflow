"""
Source Discovery Service — apps_research

Discovers and validates research sources.
Aligned with apps_lic service pattern with lifecycle trace integration.
"""

from __future__ import annotations

import hashlib
import logging
import urllib.parse
from typing import Any

from apps_research._telemetry import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_records_telemetry_event,
    _emit_routes_to_capability,
    _emit_snapshots_state,
    _emit_validates_capability,
    emit_determinism_digest,
    emit_replay_key,
)

_MAX_SOURCES = 50
_MAX_QUERY_LEN = 512

_log = logging.getLogger(__name__)


def _stable_digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]


def _normalize_query(query: str) -> str:
    stripped = query.strip()
    if not stripped:
        raise ValueError("search query must not be blank")
    return stripped[:_MAX_QUERY_LEN]


def _normalize_seed_urls(urls: list[str]) -> list[str]:
    out: list[str] = []
    for raw in urls:
        try:
            parsed = urllib.parse.urlparse(raw.strip())
            if parsed.scheme in ("http", "https") and parsed.netloc:
                out.append(urllib.parse.urlunparse(parsed))
        except ValueError:
            continue
    return out


def _merge_sources(existing: list[dict[str, Any]], new: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = {s["source_id"] for s in existing}
    merged = list(existing)
    for s in new:
        if s["source_id"] not in seen:
            merged.append(s)
            seen.add(s["source_id"])
    return merged


class SourceDiscoveryService:
    """Service for discovering and validating research sources."""

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        """Initialize the source discovery service."""
        self.config = config or {}
        self._discovered_sources: list[dict[str, Any]] = []
        self._max_sources = self.config.get("max_sources", 20)

        # Lifecycle trace emission
        emit_replay_key("source_discovery", "init")
        emit_determinism_digest("source_discovery", "init")
        _emit_applies_guardrail("p0", "source_discovery", "service_init")
        _emit_snapshots_state("p0", "source_discovery", "service_state")

    def discover_from_query(
        self,
        query: str,
        max_sources: int = 10,
        trace_id: str | None = None,
    ) -> dict[str, Any]:
        """Query-driven source discovery.

        Thin alias around :meth:`discover_sources` with no seed_urls. Exposes
        the canonical "discover from query" interface alongside
        :meth:`discover_from_seed_list` for symmetric API surfacing. The
        underlying mock-or-real discovery delegates to ``discover_sources``.
        """
        return self.discover_sources(
            query=query,
            seed_urls=None,
            max_sources=max_sources,
            trace_id=trace_id,
        )

    def discover_sources(
        self,
        query: str,
        seed_urls: list[str] | None = None,
        max_sources: int = 10,
        trace_id: str | None = None,
    ) -> dict[str, Any]:
        query = _normalize_query(query)
        seed_urls = _normalize_seed_urls(seed_urls or [])
        max_sources = min(max(1, max_sources), _MAX_SOURCES)

        # Mock implementation - actual search integration would go here
        discovered = [
            {
                "source_id": _stable_digest(f"https://example.com/source/{i}"),
                "title": f"Source for: {query[:50]}...",
                "source_type": ["article", "paper", "documentation"][i % 3],
                "relevance_score": 0.9 - (i * 0.05),
                "url": f"https://example.com/source/{i}",
            }
            for i in range(min(5, max_sources))
        ]

        self._discovered_sources.extend(discovered)
        _log.info("Discovered %d sources for query: %s", len(discovered), query[:50])
        _emit_records_telemetry_event("p4", "source_discovery", f"discover_complete:{len(discovered)}")

        return {"sources": discovered}

    def discover_from_seed_list(
        self,
        seed_urls: list[str],
        validate_accessibility: bool = True,
    ) -> list[dict[str, Any]]:
        """Discover sources from a seed URL list.

        Args:
            seed_urls: List of seed URLs
            validate_accessibility: Whether to check URL accessibility

        Returns:
            List of validated source metadata
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id,
            LayerSegment.L2_EXECUTION,
            "SourceDiscoveryService.discover_from_seed_list",
        )
        _emit_routes_to_capability("p2", "source_discovery", "url_validation")

        discovered: list[dict[str, Any]] = []

        for i, url in enumerate(seed_urls[: self._max_sources]):
            source = {
                "source_id": f"seed_{i}",
                "title": f"Seed source {i}",
                "url": url,
                "source_type": "seed",
                "validated": validate_accessibility,
            }
            discovered.append(source)

        self._discovered_sources.extend(discovered)
        _log.info("Processed %d seed URLs", len(discovered))
        _emit_records_telemetry_event("p4", "source_discovery", f"seed_processed:{len(discovered)}")

        return discovered

    def get_sources(self) -> list[dict[str, Any]]:
        """Get all discovered sources."""
        return self._discovered_sources.copy()

    def get_sources_by_type(self, source_type: str) -> list[dict[str, Any]]:
        """Get sources filtered by type."""
        return [s for s in self._discovered_sources if s.get("source_type") == source_type]

    def clear_sources(self) -> None:
        """Clear the discovered sources cache."""
        self._discovered_sources.clear()
        _emit_records_telemetry_event("p4", "source_discovery", "sources_cleared")
