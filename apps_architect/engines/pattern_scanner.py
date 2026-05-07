"""Pattern scanner — orchestrates ADG queries into typed Pattern objects.

Plan: ``.windsurf/plans/apps-architect-pattern-hardening-d7e4f9.md`` W2.P1.
"""

from __future__ import annotations

import logging
from typing import Tuple

from apps_architect.engines.adg_client import ADGClient
from apps_architect.types.architect_types import Pattern, PatternCollection, PatternType

_log = logging.getLogger(__name__)


class PatternScanner:
    """Scans ADG snapshot for structural patterns and returns PatternCollection."""

    def __init__(self, client: ADGClient | None = None) -> None:
        self._client = client or ADGClient()

    @property
    def client(self) -> ADGClient:
        return self._client

    def close(self) -> None:
        self._client.close()

    def scan_centrality(self, limit: int = 50) -> Tuple[Pattern, ...]:
        """Extract patterns from mv_hotspot_centrality."""
        rows = self._client.mv_hotspot_centrality(limit=limit)
        patterns: list[Pattern] = []
        for row in rows:
            content = (
                f"layer={row.get('layer')} fan_in={row.get('fan_in')} "
                f"fan_out={row.get('fan_out')} degree_centrality={row.get('degree_centrality'):.4f}"
            )
            patterns.append(Pattern.from_source(
                pattern_type=PatternType.ADG_VIOLATION,
                source_ref=f"adg:node:{row.get('node_id')}",
                content=content,
                summary=f"Central node: {row.get('adg_name', '')} [{row.get('layer', '')}]",
                tags=("centrality", str(row.get('layer', '')).lower()),
            ))
        return tuple(patterns)

    def scan_layer_violations(self, limit: int = 100) -> Tuple[Pattern, ...]:
        """Extract patterns from P0 critical layer breaks."""
        rows = self._client.p_view_query("v_p0_critical_layer_breaks", limit=limit)
        patterns: list[Pattern] = []
        for row in rows:
            content = str(row)
            patterns.append(Pattern.from_source(
                pattern_type=PatternType.LAYER,
                source_ref=f"adg:violation:{row.get('id', '')}",
                content=content,
                summary=f"Layer violation: {row.get('src_name', '')} -> {row.get('dst_name', '')}",
                tags=("layer_break", "p0"),
            ))
        return tuple(patterns)

    def scan_layer_contracts(self, layers: Tuple[str, ...] = ("L0", "L1", "L2", "L3", "L4", "L5", "L6")) -> Tuple[Pattern, ...]:
        """Extract layer contract patterns (node counts, structure)."""
        patterns: list[Pattern] = []
        summary_rows = self._client.layer_summary()
        for row in summary_rows:
            layer = row.get("layer", "")
            if layer in layers:
                content = f"layer={layer} node_count={row.get('cnt')}"
                patterns.append(Pattern.from_source(
                    pattern_type=PatternType.LAYER,
                    source_ref=f"adg:layer:{layer}",
                    content=content,
                    summary=f"Layer {layer}: {row.get('cnt')} nodes",
                    tags=(layer.lower(), "layer_contract"),
                ))
        return tuple(patterns)

    def scan_all(self) -> PatternCollection:
        """Run all scans and return combined PatternCollection."""
        all_patterns: list[Pattern] = []
        all_patterns.extend(self.scan_centrality())
        all_patterns.extend(self.scan_layer_violations())
        all_patterns.extend(self.scan_layer_contracts())
        return PatternCollection.from_patterns(tuple(all_patterns))


__all__ = ["PatternScanner"]
