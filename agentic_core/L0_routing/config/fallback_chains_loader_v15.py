"""v15 fallback-chains SSOT loader (plan l0-routing-v15-only-cutover W1.2)."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

from agentic_core.L0_routing.types.route_contract_v15 import (
    CostTierV15,
    FallbackEntryV15,
    RouteIdV15,
    V15RouteContractError,
)

_MAX_CHAIN_DEPTH = 8
_REPO_ROOT = Path(__file__).resolve().parents[3]
_YAML_PATH = _REPO_ROOT / "config" / "routing" / "fallback_chains_v15.yaml"

_HARDCODED: dict[str, list[dict[str, str]]] = {
    "R3_SIMPLE_GROUNDED_READ": [
        {"route_id": "R3_SIMPLE_GROUNDED_READ", "cost_tier": "TIER_L"},
        {"route_id": "R5_FALLBACK", "cost_tier": "TIER_S"},
    ],
    "R4_SINGLE_ACTION": [
        {"route_id": "R3R4_MANAGED_WORKFLOW", "cost_tier": "TIER_HITL"},
        {"route_id": "R5_FALLBACK", "cost_tier": "TIER_S"},
    ],
    "R3R4_MANAGED_WORKFLOW": [
        {"route_id": "R3_SIMPLE_GROUNDED_READ", "cost_tier": "TIER_M"},
        {"route_id": "R5_FALLBACK", "cost_tier": "TIER_S"},
    ],
}


def reset_cache() -> None:
    _load_yaml.cache_clear()
    get_fallback_chain_v15.cache_clear()


@lru_cache(maxsize=1)
def _load_yaml() -> dict[str, list[dict[str, str]]]:
    if not _YAML_PATH.is_file():
        return dict(_HARDCODED)
    try:
        import yaml

        raw = yaml.safe_load(_YAML_PATH.read_text(encoding="utf-8"))
        chains = raw.get("chains") if isinstance(raw, dict) else None
        if not isinstance(chains, dict):
            return dict(_HARDCODED)
        out: dict[str, list[dict[str, str]]] = {}
        for key, entries in chains.items():
            if isinstance(entries, list):
                out[str(key)] = [dict(e) for e in entries if isinstance(e, dict)]
        return out or dict(_HARDCODED)
    except Exception as exc:  # guardian: allow-broad-exception -- bootstrap fallback
        raise V15RouteContractError(f"fallback_chains_v15.yaml unreadable: {exc}") from exc


def _parse_entry(row: dict[str, Any]) -> FallbackEntryV15:
    rid = RouteIdV15(str(row["route_id"]))
    tier = CostTierV15(str(row["cost_tier"]))
    return FallbackEntryV15(rid, tier)


@lru_cache(maxsize=32)
def get_fallback_chain_v15(route_id: RouteIdV15 | str) -> tuple[FallbackEntryV15, ...]:
    key = route_id.value if isinstance(route_id, RouteIdV15) else str(route_id)
    chains = _load_yaml()
    rows = chains.get(key, [])
    if not rows:
        return ()
    entries = tuple(_parse_entry(r) for r in rows)
    if len(entries) > _MAX_CHAIN_DEPTH:
        raise V15RouteContractError(f"chain depth {len(entries)} > {_MAX_CHAIN_DEPTH}")
    if entries and entries[-1].route_id != RouteIdV15.R5_FALLBACK:
        raise V15RouteContractError(f"{key}: terminal entry must be R5_FALLBACK")
    return entries


__all__ = ["get_fallback_chain_v15", "reset_cache"]
