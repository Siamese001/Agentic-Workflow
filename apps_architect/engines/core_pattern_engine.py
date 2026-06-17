"""Core layer pattern detector — ADG queries for genetic architecture patterns.

Plan: ``.claude/plans/apps-architect-pattern-hardening-d7e4f9.md`` W2.P4.
"""

from __future__ import annotations

import logging
from typing import Tuple

from apps_architect.engines.adg_client import ADGClient
from apps_architect.types.architect_types import Pattern, PatternType

_log = logging.getLogger(__name__)

_LAYERS = ("L0", "L1", "L2", "L3", "L4", "L5", "L6")


class CorePatternEngine:
    """Detects genetic architecture patterns in agentic_core via ADG queries."""

    def __init__(self, client: ADGClient | None = None) -> None:
        self._client = client or ADGClient()

    @property
    def client(self) -> ADGClient:
        return self._client

    def close(self) -> None:
        self._client.close()

    def detect_layer_separation(self) -> Tuple[Pattern, ...]:
        """Detect cross-layer import patterns (who imports across layer boundaries)."""
        patterns: list[Pattern] = []
        for i, src_layer in enumerate(_LAYERS):
            for dst_layer in _LAYERS[i:]:
                if src_layer == dst_layer:
                    continue
                edges = self._client.cross_layer_edges(src_layer, dst_layer, limit=5)
                if edges:
                    for edge in edges:
                        patterns.append(Pattern.from_source(
                            pattern_type=PatternType.CORE,
                            source_ref=f"adg:edge:{edge.get('id', '')}",
                            content=f"{src_layer}->{dst_layer}: {edge.get('src_name', '')} -> {edge.get('dst_name', '')}",
                            summary=f"Cross-layer: {src_layer}->{dst_layer}",
                            tags=("layer_separation", src_layer.lower(), dst_layer.lower()),
                        ))
        return tuple(patterns)

    def detect_layer_composition(self) -> Tuple[Pattern, ...]:
        """Detect layer node-count patterns."""
        patterns: list[Pattern] = []
        summary = self._client.layer_summary()
        for row in summary:
            layer = row.get("layer", "")
            cnt = row.get("cnt", 0)
            if layer in _LAYERS:
                patterns.append(Pattern.from_source(
                    pattern_type=PatternType.CORE,
                    source_ref=f"adg:layer:{layer}",
                    content=f"node_count={cnt}",
                    summary=f"Layer {layer} composition: {cnt} nodes",
                    tags=(layer.lower(), "composition"),
                ))
        return tuple(patterns)

    def detect_violation_hotspots(self, limit: int = 50) -> Tuple[Pattern, ...]:
        """Detect violation hotspots from centrality MV."""
        patterns: list[Pattern] = []
        rows = self._client.mv_hotspot_centrality(limit=limit)
        for row in rows:
            patterns.append(Pattern.from_source(
                pattern_type=PatternType.ADG_VIOLATION,
                source_ref=f"adg:node:{row.get('node_id')}",
                content=f"fan_in={row.get('fan_in')} fan_out={row.get('fan_out')} centrality={row.get('degree_centrality'):.4f}",
                summary=f"Hotspot: {row.get('adg_name', '')} [{row.get('layer', '')}]",
                tags=("hotspot", str(row.get('layer', '')).lower()),
            ))
        return tuple(patterns)

    def detect_all(self) -> Tuple[Pattern, ...]:
        all_patterns: list[Pattern] = []
        all_patterns.extend(self.detect_layer_separation())
        all_patterns.extend(self.detect_layer_composition())
        all_patterns.extend(self.detect_violation_hotspots())
        return tuple(all_patterns)


__all__ = ["CorePatternEngine"]
