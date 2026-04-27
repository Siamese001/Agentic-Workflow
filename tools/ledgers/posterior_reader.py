"""tools.ledgers.posterior_reader — Beta-posterior aggregator over any router ledger.

This is the sanctioned tools-layer adapter for SQL aggregation reads against
the closed-loop router ledgers. Higher layers (e.g.
``agentic_core/L2_execution/healers/cascade_calibrator``) call into this
module instead of importing ``sqlite3`` directly, satisfying the
infrastructure-wiring scan.

Contract:

- Read-only. Opens the ledger DB with ``mode=ro`` URI.
- Stdlib only.
- Fail-soft: every error path returns a structured ``PosteriorAggregate`` with
  ``used=False`` so callers can fall back to a heuristic prior unconditionally.
- The Beta(α, β) prior + observed (k, n-k) yields posterior mean
  ``(α + k) / (α + β + n)``.

The sibling module ``writer.py`` is the only path that mutates a ledger DB.
"""

from __future__ import annotations

import logging
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class PosteriorAggregate:
    """Result of a Beta-posterior aggregation over one routing cell."""

    posterior_mean: float
    n: int
    successes: int
    used: bool
    fallback_reason: str  # "ok" | "n_below_floor" | "ledger_unavailable" | "no_rows" | "error"

    def as_dict(self) -> dict[str, Any]:
        return {
            "posterior_mean": float(self.posterior_mean),
            "n": int(self.n),
            "successes": int(self.successes),
            "used": bool(self.used),
            "fallback_reason": self.fallback_reason,
        }


def aggregate_router_cell(
    *,
    ledger_path: Path | str,
    tier_name: str,
    fingerprint_hex: str,
    n_floor: int,
    alpha: float = 1.0,
    beta: float = 1.0,
    selected_field: str = "tier",
) -> PosteriorAggregate:
    """Read the Beta-posterior over (selected, cell) from a router ledger DB.

    Aggregates ``status='bound'`` rows with ``event_kind='route_decision'``
    where ``prediction_json.<selected_field>`` matches ``tier_name`` and
    ``prediction_json.fingerprint`` matches ``fingerprint_hex``. Returns a
    structured aggregate that callers stamp into telemetry.

    Args:
        ledger_path: Path to the SQLite ledger (typically
            ``artifacts/ledgers/router_<layer>_<router>.sqlite``).
        tier_name: Value to match against the ``selected_field`` JSON path
            (e.g. "HIGH" for L2/cascade or "tier_a" for L1/c0).
        fingerprint_hex: 12-hex SHA-256 prefix identifying the routing cell.
        n_floor: Minimum bound rows required before the result is "used".
            Below this floor the caller should fall back to its heuristic.
        alpha, beta: Beta prior shape parameters (default Beta(1,1) uniform).
        selected_field: JSON field name in ``prediction_json`` carrying the
            chosen action label. Defaults to ``"tier"`` for back-compat with
            L2/cascade; the generic ``RouterClosedLoopHelper`` passes
            ``"selected"`` to match its prediction shape.

    Returns:
        PosteriorAggregate with provenance fields. ``used=False`` whenever the
        cell is cold, the ledger is unavailable, or any SQLite error occurs.
    """
    path = Path(ledger_path)
    prior_mean = alpha / (alpha + beta)

    if not path.exists():
        return PosteriorAggregate(
            posterior_mean=prior_mean,
            n=0,
            successes=0,
            used=False,
            fallback_reason="ledger_unavailable",
        )

    try:
        # Read-only URI — the router ledger surface is canonical-write,
        # callers-read; never mutate from the read path.
        uri = f"file:{path.as_posix()}?mode=ro"
        # Whitelist the JSON field name to keep this query injection-safe
        # despite needing string interpolation (sqlite3 won't parameterize
        # JSON paths, only values).
        if not selected_field.replace("_", "").isalnum():
            raise sqlite3.Error(f"invalid selected_field: {selected_field!r}")
        json_path_selected = f"$.{selected_field}"
        conn = sqlite3.connect(uri, uri=True, timeout=2.0)
        try:
            row = conn.execute(
                f"""
                SELECT
                    COUNT(*) AS n,
                    SUM(CASE WHEN json_extract(outcome_json, '$.success') = 1
                              THEN 1 ELSE 0 END) AS k
                FROM events
                WHERE event_kind = 'route_decision'
                  AND status = 'bound'
                  AND json_extract(prediction_json, '{json_path_selected}') = ?
                  AND json_extract(prediction_json, '$.fingerprint') = ?
                """,
                (tier_name, fingerprint_hex),
            ).fetchone()
        finally:
            conn.close()
    except sqlite3.Error:  # guardian: allow-log-and-swallow -- posterior read is best-effort; callers MUST fall back to heuristic
        _LOGGER.debug("aggregate_router_cell sqlite3 error", exc_info=True)
        return PosteriorAggregate(
            posterior_mean=prior_mean,
            n=0,
            successes=0,
            used=False,
            fallback_reason="error",
        )

    n = int(row[0] or 0)
    k = int(row[1] or 0)
    if n <= 0:
        return PosteriorAggregate(
            posterior_mean=prior_mean,
            n=0,
            successes=0,
            used=False,
            fallback_reason="no_rows",
        )

    posterior_mean = (alpha + k) / (alpha + beta + n)
    used = n >= int(n_floor)
    return PosteriorAggregate(
        posterior_mean=posterior_mean,
        n=n,
        successes=k,
        used=used,
        fallback_reason="ok" if used else "n_below_floor",
    )


__all__ = ["PosteriorAggregate", "aggregate_router_cell"]
