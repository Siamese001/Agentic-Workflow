"""v12 Fallback-chains & SLO-defaults SSOT loader.

Reads ``config/routing/fallback_chains.yaml`` and exposes:

- ``get_fallback_chain(route_id)`` → ordered tuple of ``FallbackEntry``.
- ``get_slo_default(route_id, cost_tier)`` → ``RouteSLO`` for the given cell.

Cached per-process via ``functools.lru_cache``. Call ``reset_cache()`` from
tests that mutate the YAML.

Override order (highest first):
  1. Explicit kwarg passed by caller.
  2. Environment variable (per-route override is not supported; YAML is SSOT).
  3. This YAML.
  4. Hardcoded fallback below (kept in sync with the YAML).
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

from agentic_core.L0_routing.types.route_contract_v12_extensions import (
    CostTier,
    FallbackEntry,
    RouteId,
    RouteSLO,
    V12RouteContractError,
)

# Hard cap — matches _MAX_FALLBACK_CHAIN_DEPTH in the types module but
# duplicated here to avoid a private-name import. Keep in sync.
_MAX_CHAIN_DEPTH = 8

_REPO_ROOT = Path(__file__).resolve().parents[3]
_YAML_PATH = _REPO_ROOT / "config" / "routing" / "fallback_chains.yaml"


# Hardcoded fallbacks — mirror fallback_chains.yaml. Used only when YAML is
# missing or unparseable (e.g. during early bootstrap, in unit tests that
# stub out the FS, or on install-from-sdist without the config tree).
_HARDCODED_CHAINS: dict[str, list[dict[str, str]]] = {
    "R1B": [
        {"route_id": "R1A", "cost_tier": "TIER_S"},
        {"route_id": "R3_GROUNDED", "cost_tier": "TIER_M"},
        {"route_id": "R5_FALLBACK", "cost_tier": "TIER_S"},
    ],
    "R3_GROUNDED": [
        {"route_id": "R3R4_WORKFLOW", "cost_tier": "TIER_L"},
        {"route_id": "R-CASC", "cost_tier": "TIER_S"},
        {"route_id": "R5_FALLBACK", "cost_tier": "TIER_S"},
    ],
    "R4_ACTION": [
        {"route_id": "R-HITL", "cost_tier": "TIER_M"},
        {"route_id": "R5_FALLBACK", "cost_tier": "TIER_S"},
    ],
    "R3R4_WORKFLOW": [
        {"route_id": "R-LOOP", "cost_tier": "TIER_M"},
        {"route_id": "R5_FALLBACK", "cost_tier": "TIER_S"},
    ],
    "R-CASC": [
        {"route_id": "R3R4_WORKFLOW", "cost_tier": "TIER_L"},
        {"route_id": "R5_FALLBACK", "cost_tier": "TIER_S"},
    ],
    "R-PAR": [
        {"route_id": "R3_GROUNDED", "cost_tier": "TIER_M"},
        {"route_id": "R5_FALLBACK", "cost_tier": "TIER_S"},
    ],
    "R-LOOP": [
        {"route_id": "R3_GROUNDED", "cost_tier": "TIER_M"},
        {"route_id": "R5_FALLBACK", "cost_tier": "TIER_S"},
    ],
    "R-HITL": [
        {"route_id": "R5_FALLBACK", "cost_tier": "TIER_S"},
    ],
}


_HARDCODED_SLO: dict[str, dict[str, Any]] = {
    "R1A": {"latency_budget_ms": 50, "token_budget_in": 0, "token_budget_out": 0, "cost_cap_usd": 0.00},
    "R1B": {"latency_budget_ms": 250, "token_budget_in": 0, "token_budget_out": 0, "cost_cap_usd": 0.00},
    "R3_GROUNDED__TIER_S": {
        "latency_budget_ms": 2000,
        "token_budget_in": 4000,
        "token_budget_out": 800,
        "cost_cap_usd": 0.01,
    },
    "R3_GROUNDED__TIER_M": {
        "latency_budget_ms": 6000,
        "token_budget_in": 12000,
        "token_budget_out": 2000,
        "cost_cap_usd": 0.08,
    },
    "R3_GROUNDED__TIER_L": {
        "latency_budget_ms": 20000,
        "token_budget_in": 32000,
        "token_budget_out": 4000,
        "cost_cap_usd": 0.60,
    },
    "R4_ACTION": {
        "latency_budget_ms": 10000,
        "token_budget_in": 8000,
        "token_budget_out": 1000,
        "cost_cap_usd": 0.10,
    },
    "R3R4_WORKFLOW": {
        "latency_budget_ms": 60000,
        "token_budget_in": 64000,
        "token_budget_out": 8000,
        "cost_cap_usd": 2.00,
    },
    "R5_FALLBACK": {
        "latency_budget_ms": 500,
        "token_budget_in": 0,
        "token_budget_out": 200,
        "cost_cap_usd": 0.00,
    },
}


@lru_cache(maxsize=1)
def _load_yaml() -> dict[str, Any]:
    if not _YAML_PATH.exists():
        return {}
    try:
        import yaml  # lazy
    except ImportError:
        return {}
    try:
        raw = yaml.safe_load(_YAML_PATH.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError):
        return {}
    return raw if isinstance(raw, dict) else {}


def reset_cache() -> None:
    """Drop the YAML cache — intended for tests that mutate the YAML on disk."""
    _load_yaml.cache_clear()


def _chains_raw() -> dict[str, list[dict[str, str]]]:
    doc = _load_yaml()
    yaml_chains = doc.get("chains") if isinstance(doc, dict) else None
    if isinstance(yaml_chains, dict):
        return yaml_chains  # type: ignore[return-value]
    return _HARDCODED_CHAINS


def _slo_raw() -> dict[str, dict[str, Any]]:
    doc = _load_yaml()
    yaml_slo = doc.get("slo_defaults") if isinstance(doc, dict) else None
    if isinstance(yaml_slo, dict):
        return yaml_slo  # type: ignore[return-value]
    return _HARDCODED_SLO


def get_fallback_chain(route_id: RouteId | str) -> tuple[FallbackEntry, ...]:
    """Return the default fallback chain for ``route_id``.

    Terminal routes (R1A, R5_FALLBACK) always return an empty tuple.

    Validates:
    - chain depth does not exceed ``_MAX_CHAIN_DEPTH``
    - no entry points back at the primary ``route_id`` with the same tier
      (self-reference = infinite escalation loop)
    - no duplicate (route_id, cost_tier) pairs within the chain
    - R5_FALLBACK, if present, is the final entry
    """
    if not isinstance(route_id, (RouteId, str)):
        raise V12RouteContractError(
            f"route_id must be RouteId or str, got {type(route_id).__name__}"
        )
    key = route_id.value if isinstance(route_id, RouteId) else str(route_id)
    if key in {"R1A", "R5_FALLBACK"}:
        return ()
    raw = _chains_raw().get(key)
    if not raw:
        return ()
    if not isinstance(raw, list):
        raise V12RouteContractError(
            f"fallback chain for {key} must be a list, got {type(raw).__name__}"
        )
    if len(raw) > _MAX_CHAIN_DEPTH:
        raise V12RouteContractError(
            f"fallback chain for {key} exceeds max depth {_MAX_CHAIN_DEPTH} "
            f"(got {len(raw)})"
        )
    entries: list[FallbackEntry] = []
    seen_pairs: set[tuple[str, str]] = set()
    primary_tier_keys: set[tuple[str, str]] = set()
    for idx, row in enumerate(raw):
        if not isinstance(row, dict):
            raise V12RouteContractError(
                f"fallback chain[{idx}] for {key} must be a dict, got {type(row).__name__}"
            )
        try:
            entry = FallbackEntry(
                route_id=RouteId(row["route_id"]),
                cost_tier=CostTier(row["cost_tier"]),
                provider=row.get("provider"),
            )
        except (KeyError, ValueError, V12RouteContractError) as exc:
            raise V12RouteContractError(
                f"invalid fallback_chain entry for {key}[{idx}]: {row!r}"
            ) from exc
        pair = (entry.route_id.value, entry.cost_tier.value)
        if pair in seen_pairs:
            raise V12RouteContractError(
                f"duplicate fallback entry for {key}: {pair}"
            )
        seen_pairs.add(pair)
        # Detect chain entries that loop back to the primary route at the
        # same (or unspecified) tier. Because this loader doesn't know the
        # primary's tier, we defer the full self-reference check to
        # V12RouteAnnex construction; here we only reject entries whose
        # route_id equals the primary key AND whose tier matches a "likely"
        # primary tier (any single-tier route_id).
        if entry.route_id.value == key:
            primary_tier_keys.add(pair)
        entries.append(entry)
    # Same-route cycle is always a misconfiguration regardless of tier.
    if primary_tier_keys:
        raise V12RouteContractError(
            f"fallback chain for {key} contains entries pointing back at the "
            f"primary route ({sorted(primary_tier_keys)}); this is a cycle"
        )
    # R5 must be last if present.
    r5_positions = [
        i for i, e in enumerate(entries) if e.route_id == RouteId.R5_FALLBACK
    ]
    if r5_positions and r5_positions[-1] != len(entries) - 1:
        raise V12RouteContractError(
            f"R5_FALLBACK must be the last entry in fallback chain for {key}"
        )
    return tuple(entries)


def get_slo_default(route_id: RouteId | str, cost_tier: CostTier | str | None = None) -> RouteSLO:
    """Return the default ``RouteSLO`` for the ``(route_id, cost_tier)`` cell.

    Falls back to the route_id-only entry when no tier-specific default
    exists. Raises ``V12RouteContractError`` if no default is defined anywhere.
    """
    route_key = route_id.value if isinstance(route_id, RouteId) else str(route_id)
    tier_key = (
        cost_tier.value
        if isinstance(cost_tier, CostTier)
        else str(cost_tier)
        if cost_tier is not None
        else None
    )
    slo_map = _slo_raw()
    if tier_key is not None:
        combined = f"{route_key}__{tier_key}"
        if combined in slo_map:
            return _row_to_slo(slo_map[combined])
    if route_key in slo_map:
        return _row_to_slo(slo_map[route_key])
    raise V12RouteContractError(f"no SLO default defined for route={route_key} tier={tier_key}")


def _row_to_slo(row: dict[str, Any]) -> RouteSLO:
    try:
        return RouteSLO(
            latency_budget_ms=int(row["latency_budget_ms"]),
            token_budget_in=int(row["token_budget_in"]),
            token_budget_out=int(row["token_budget_out"]),
            cost_cap_usd=float(row["cost_cap_usd"]),
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise V12RouteContractError(f"invalid SLO row: {row!r}") from exc
