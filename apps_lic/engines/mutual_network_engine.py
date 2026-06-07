"""apps_lic.engines.mutual_network_engine — D6-P5.

Plan: docs/archive/windsurf/legacy-tree/plans/apps-lic-deferred-scope-followup-d3f9b2.md W4 D6-P5

Extracts and scores mutual network signals from caller-provided connection
data. Returns an immutable MutualNetworkSignal.

Decision-only invariants
------------------------
- External signal source: connection data MUST be passed in by caller —
  engine does NOT read from any database or external API.
- Data contract: connection_items is a list of objects with attributes
  (name, company, role, relationship_type). Embed nothing — declare only.
- No durable writes.
- No provider API calls.
- No subprocess calls.
- Config-gated: disabled when MUTUAL_NETWORK_ENABLED env var is absent/falsy.

Signal strength model
---------------------
  no_connection       — no mutual connections found
  weak_connection     — 1 mutual, low relationship_type weight
  moderate_connection — 1–2 mutuals with meaningful relationship weight
  strong_connection   — 3+ mutuals OR 1 with relationship_type="direct"

Relationship type weights (configurable):
  direct    = 1.0
  colleague = 0.7
  alumni    = 0.5
  network   = 0.3
  unknown   = 0.1
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any, Optional

from apps_shared.contracts.connection_data_contract import (
    MutualConnectionItem as _ContractMutualConnectionItem,
)

_CONFIG_PATH = Path(__file__).parent.parent / "config" / "mutual_network_policy.yaml"

_DEFAULT_WEIGHTS: dict[str, float] = {
    "direct":    1.0,
    "colleague": 0.7,
    "alumni":    0.5,
    "network":   0.3,
    "unknown":   0.1,
}

_STRONG_THRESHOLD = 3
_MODERATE_THRESHOLD = 1
_STRONG_WEIGHT_THRESHOLD = 0.9  # direct connection triggers strong regardless of count

MutualConnectionItem = _ContractMutualConnectionItem
"""Canonical connection item — re-exported from apps_shared.contracts."""


@lru_cache(maxsize=1)
def _load_config() -> dict:
    try:
        import yaml  # type: ignore[import]
        with open(_CONFIG_PATH, "r", encoding="utf-8") as fh:
            return yaml.safe_load(fh) or {}
    except Exception:  # noqa: BLE001
        # guardian: allow-broad-except -- optional config.
        return {}


@dataclass(frozen=True)
class MutualNetworkSignal:
    """Result of mutual network extraction.

    Fields
    ------
    signal_strength     : "no_connection" | "weak" | "moderate" | "strong" | "disabled"
    connection_count    : total mutual connections found.
    weighted_score      : sum of relationship weights for all connections.
    top_connection_name : name of highest-weight connection (empty if none).
    enabled             : False when feature is disabled.
    """

    signal_strength: str
    connection_count: int
    weighted_score: float
    top_connection_name: str
    enabled: bool


class MutualNetworkEngine:
    """Extracts and scores mutual network signals from caller-provided data."""

    def __init__(self, config: dict | None = None) -> None:
        self._config = config if config is not None else _load_config()

    def _weights(self) -> dict[str, float]:
        cfg_weights = self._config.get("relationship_weights", {})
        merged = dict(_DEFAULT_WEIGHTS)
        merged.update({k: float(v) for k, v in cfg_weights.items()})
        return merged

    def _strong_threshold(self) -> int:
        return int(self._config.get("strong_threshold", _STRONG_THRESHOLD))

    def extract(
        self,
        *,
        connection_items: list[MutualConnectionItem] | None = None,
    ) -> MutualNetworkSignal:
        """Score mutual network signal.

        Parameters
        ----------
        connection_items : list of objects with attributes:
                           - name (str)
                           - relationship_type (str): direct|colleague|alumni|network|unknown
                           Caller provides; engine does not read from any store.
        """
        if not os.environ.get("MUTUAL_NETWORK_ENABLED"):
            return MutualNetworkSignal(
                signal_strength="disabled",
                connection_count=0,
                weighted_score=0.0,
                top_connection_name="",
                enabled=False,
            )

        items = connection_items or []
        weights = self._weights()
        strong_t = self._strong_threshold()

        if not items:
            return MutualNetworkSignal(
                signal_strength="no_connection",
                connection_count=0,
                weighted_score=0.0,
                top_connection_name="",
                enabled=True,
            )

        scored = []
        for item in items:
            rtype = str(getattr(item, "relationship_type", "unknown")).lower()
            w = weights.get(rtype, weights["unknown"])
            name = str(getattr(item, "name", ""))
            scored.append((w, name))

        scored.sort(key=lambda x: x[0], reverse=True)
        total_weight = sum(w for w, _ in scored)
        top_name = scored[0][1] if scored else ""
        top_weight = scored[0][0] if scored else 0.0
        count = len(scored)

        if count >= strong_t or top_weight >= _STRONG_WEIGHT_THRESHOLD:
            strength = "strong"
        elif count >= _MODERATE_THRESHOLD and total_weight >= 0.5:
            strength = "moderate"
        elif count >= _MODERATE_THRESHOLD:
            strength = "weak"
        else:
            strength = "no_connection"

        return MutualNetworkSignal(
            signal_strength=strength,
            connection_count=count,
            weighted_score=round(total_weight, 3),
            top_connection_name=top_name,
            enabled=True,
        )


__all__ = ["MutualNetworkEngine", "MutualNetworkSignal", "MutualConnectionItem"]
