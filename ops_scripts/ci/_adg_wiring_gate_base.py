#!/usr/bin/env python3
"""Shared harness for ADG wiring-CI gates (plan W1.1).

All wiring gates answer graph-shape questions against the canonical ADG
SQLite snapshot at ``artifacts/adg/adg_indexed_*.sqlite`` (the latest by
mtime unless overridden). This module provides:

    * ``latest_snapshot()`` — snapshot resolution identical to check_snapshot_has_mvs.py
    * ``WiringGate`` — ABC with a standard run loop, tier (B/R/W/K),
      JSONL violation sink, waiver lookup, baseline ratchet support
    * ``Violation`` / ``GateResult`` dataclasses for uniform output

Tier semantics:
    B — blocking (exit 1 on any violation)
    R — ratchet (exit 1 only if count > baseline; baseline auto-seeds on first run)
    W — warn (exit 0 always; prints + logs)
    K — KPI (report only; never CI-blocking)

Environment overrides (per-gate scripts may read these):
    ADG_SNAPSHOT=<path>              — pin a specific snapshot
    WIRING_GATE_BYPASS=1             — full bypass (logs bypass row, exits 0)

Violation sink: artifacts/governance/wiring_gate_violations.jsonl (one JSON per line,
append-only). Waivers: config/wiring_gate_waivers.yaml.
"""

from __future__ import annotations

import json
import os
import sqlite3
import sys
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore[assignment]

REPO_ROOT = Path(__file__).resolve().parents[2]
ADG_DIR = REPO_ROOT / "artifacts" / "adg"
LOG_DIR = REPO_ROOT / "artifacts" / "governance"
LOG_FILE = LOG_DIR / "wiring_gate_violations.jsonl"
BASELINE_DIR = REPO_ROOT / "ops_scripts" / "ci" / "baselines"
WAIVER_FILE = REPO_ROOT / "config" / "wiring_gate_waivers.yaml"

GATE_SNAPSHOT_REQUIRED_TABLES = (
    "nodes",
    "edges",
    "mv_gateway_bypass_paths",
    "mv_exit_disposition_coverage",
    "mv_replay_surface_gaps",
    "mv_actionable_surface_without_schema",
    "mv_structured_output_gaps",
    "mv_hotspot_centrality",
    "mv_cross_cutting_witness_tiers",
    "mv_handoff_witness_tiers",
)


Tier = Literal["B", "R", "W", "K"]


@dataclass
class Violation:
    """Single wiring-CI violation, shape shared by every gate."""

    gate_id: str
    tier: Tier
    subject: str  # module path, pipeline-stage id, etc.
    rule: str  # short human-readable rule name
    detail: str
    severity: Literal["fail", "warn"] = "fail"
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class GateResult:
    gate_id: str
    tier: Tier
    snapshot: str
    timestamp: str
    status: Literal["pass", "fail", "warn", "bypass"]
    violations: list[Violation]
    baseline_count: int | None = None
    summary: dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Snapshot + waiver helpers
# ---------------------------------------------------------------------------


def latest_snapshot() -> Path:
    """Return the most-recently modified adg_indexed_*.sqlite that has a
    `nodes` base table (skips stub/sentinel snapshots).

    Honors ``ADG_SNAPSHOT`` env override unconditionally — operators who
    explicitly point at a stub for testing get what they ask for.

    Delegates to ``tools.adg.shared_modules.path_resolver.latest_sqlite``
    for canonical snapshot resolution (sentinel filtering by timestamp format).
    """
    override = os.environ.get("ADG_SNAPSHOT", "").strip()
    if override:
        p = Path(override).expanduser().resolve()
        if not p.exists():
            raise FileNotFoundError(f"ADG_SNAPSHOT not found: {p}")
        return p

    # Delegate to canonical resolver with gate materialized-view validation.
    # Failed/deferred generator runs can leave a timestamped SQLite with base
    # nodes/edges but without the mv_* tables CI gates require.
    try:
        from tools.adg.shared_modules.path_resolver import latest_sqlite  # noqa: PLC0415

        snap = latest_sqlite(required_tables=GATE_SNAPSHOT_REQUIRED_TABLES)
    except Exception:  # noqa: BLE001
        snap = None

    if snap is None:
        raise FileNotFoundError(
            f"no adg_indexed_*.sqlite under {ADG_DIR}; regenerate via `python tools/generate_full_adg.py`",
        )
    return snap


def _load_waivers() -> dict[str, Any]:
    if not WAIVER_FILE.exists() or yaml is None:
        return {}
    try:
        data = yaml.safe_load(WAIVER_FILE.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError:
        return {}
    if not isinstance(data, dict):
        return {}
    return data


def _entry_active_for(entry: Any, gate_id: str, subject: str, today: Any) -> bool:
    if not isinstance(entry, dict):
        return False
    if entry.get("gate") != gate_id:
        return False
    scope = entry.get("scope", "")
    if not (scope == subject or scope == "*" or subject.endswith(scope)):
        return False
    try:
        exp_date = datetime.strptime(entry.get("expires_on", ""), "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return False
    return bool(exp_date >= today)


def _waiver_matches(waivers: dict[str, Any], gate_id: str, subject: str) -> bool:
    """Return True if an active waiver covers this (gate_id, subject) tuple."""
    today = datetime.now(timezone.utc).date()
    entries = waivers.get("waivers", []) if isinstance(waivers, dict) else []
    return any(_entry_active_for(e, gate_id, subject, today) for e in entries)


# ---------------------------------------------------------------------------
# SQLite access
# ---------------------------------------------------------------------------


def connect_snapshot(snapshot: Path) -> sqlite3.Connection:
    """Open the ADG SQLite snapshot read-only (uri mode)."""
    uri = f"file:{snapshot.as_posix()}?mode=ro"
    return sqlite3.connect(uri, uri=True)


# ---------------------------------------------------------------------------
# Base gate
# ---------------------------------------------------------------------------


class WiringGate(ABC):
    """Subclass must implement ``run()`` returning a list of Violation."""

    gate_id: str
    tier: Tier
    baseline_filename: str | None = None  # for tier R

    def __init__(self, snapshot: Path | None = None) -> None:
        self.snapshot = snapshot or latest_snapshot()
        self.waivers = _load_waivers()

    def _effective_tier(self) -> Tier:
        """Return runtime tier, honouring auto_promoted_tier from baseline JSON.

        Lets a ratchet that previously crossed the zero-run streak threshold
        start blocking on the next run without requiring the source class to
        be edited.
        """
        if self.tier != "R":
            return self.tier
        rec = self._load_baseline_record()
        promoted = rec.get("auto_promoted_tier")
        baseline_count = int(rec.get("count", 0) or 0)
        if promoted == "B" and baseline_count == 0:
            return "B"
        if promoted == "W":
            return "W"
        if promoted == "K":
            return "K"
        return self.tier

    # ---- overridable -----------------------------------------------------
    @abstractmethod
    def run(self, conn: sqlite3.Connection) -> list[Violation]:
        """Return list of (unfiltered) violations."""

    # ---- harness ---------------------------------------------------------
    def execute(self) -> GateResult:
        if os.environ.get("WIRING_GATE_BYPASS", "").strip() == "1":
            return self._bypass_result()

        conn = connect_snapshot(self.snapshot)
        try:
            raw = self.run(conn)
        finally:
            conn.close()

        active = [v for v in raw if not _waiver_matches(self.waivers, self.gate_id, v.subject)]

        baseline_count: int | None = None
        status: Literal["pass", "fail", "warn", "bypass"]
        summary: dict[str, Any] = {"raw_count": len(raw), "active_count": len(active)}
        effective_tier = self._effective_tier()
        if effective_tier != self.tier:
            summary["effective_tier"] = effective_tier
            summary["declared_tier"] = self.tier
        if effective_tier == "B":
            # Severity-aware: blocking tier fails ONLY on `severity=fail`
            # violations. `severity=warn` rows (e.g., deferred-stage
            # informational notices from CanonicalPipelineWiringGate) are
            # tracked but never fail the gate. This matches the per-stage
            # intent already encoded in the gates: a deferred stage is
            # documented as warn-not-fail and must not block CI.
            failing = [v for v in active if v.severity == "fail"]
            warning_only = [v for v in active if v.severity == "warn"]
            if failing:
                status = "fail"
            elif warning_only:
                status = "warn"
            else:
                status = "pass"
        elif effective_tier == "R":
            baseline_count = self._baseline_count()
            status = "fail" if len(active) > (baseline_count or 0) else "pass"
            if status == "pass":
                # W1.1 monotone auto-tighten: shrink baseline on green run
                tightened = self._maybe_tighten_baseline(
                    active_count=len(active),
                    baseline_count=baseline_count or 0,
                )
                if tightened is not None:
                    summary["baseline_tightened_from"] = baseline_count
                    summary["baseline_tightened_to"] = tightened
                    baseline_count = tightened
                # W1.2 R->B auto-promotion after N consecutive zero runs
                promoted = self._maybe_auto_promote_to_block(len(active))
                if promoted:
                    summary["auto_promoted_to_tier"] = "B"
        elif effective_tier == "W":
            status = "warn" if active else "pass"
        else:  # K
            status = "pass"

        result = GateResult(
            gate_id=self.gate_id,
            tier=effective_tier,
            snapshot=self.snapshot.name,
            timestamp=datetime.now(timezone.utc).isoformat(),
            status=status,
            violations=active,
            baseline_count=baseline_count,
            summary=summary,
        )
        self._sink(result)
        return result

    # ---- helpers ---------------------------------------------------------
    def _baseline_count(self) -> int:
        if not self.baseline_filename:
            return 0
        path = BASELINE_DIR / self.baseline_filename
        if not path.exists():
            return 0
        try:
            return int(json.loads(path.read_text(encoding="utf-8")).get("count", 0))
        except (json.JSONDecodeError, ValueError, OSError):
            return 0

    def seed_baseline(self, count: int) -> None:
        if not self.baseline_filename:
            return
        BASELINE_DIR.mkdir(parents=True, exist_ok=True)
        path = BASELINE_DIR / self.baseline_filename
        path.write_text(
            json.dumps(
                {
                    "gate_id": self.gate_id,
                    "count": count,
                    "seeded_at": datetime.now(timezone.utc).isoformat(),
                    "snapshot": self.snapshot.name,
                },
                indent=2,
            ),
            encoding="utf-8",
        )

    # ---- W1.1 monotone ratchet tightening ---------------------------------
    # Default: opt-in per gate via class attr or JSON field. Keep default True
    # so the harness-wide behaviour is "cleanup sticks".
    auto_tighten_baseline: bool = True
    # Default consecutive-zero streak required before promoting R->B.
    auto_promote_to_block_after_zero_runs: int = 3

    def _load_baseline_record(self) -> dict[str, Any]:
        if not self.baseline_filename:
            return {}
        path = BASELINE_DIR / self.baseline_filename
        if not path.exists():
            return {}
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return data if isinstance(data, dict) else {}
        except (json.JSONDecodeError, ValueError, OSError):
            return {}

    def _write_baseline_record(self, rec: dict[str, Any]) -> None:
        if not self.baseline_filename:
            return
        BASELINE_DIR.mkdir(parents=True, exist_ok=True)
        path = BASELINE_DIR / self.baseline_filename
        path.write_text(json.dumps(rec, indent=2), encoding="utf-8")

    def _maybe_tighten_baseline(self, *, active_count: int, baseline_count: int) -> int | None:
        """Rewrite baseline JSON if count shrank below previous baseline.

        Returns the new baseline value on tighten, or None if no change.
        Respects ``auto_tighten_baseline`` class attribute and the JSON
        field ``auto_tighten`` (bool, default True) for per-gate opt-out.
        """
        if not self.baseline_filename:
            return None
        if active_count >= baseline_count:
            return None
        rec = self._load_baseline_record()
        if rec.get("auto_tighten") is False:
            return None
        if not self.auto_tighten_baseline:
            return None
        previous = rec.get("count")
        rec["count"] = active_count
        rec["gate_id"] = rec.get("gate_id", self.gate_id)
        rec["snapshot"] = self.snapshot.name
        rec["tightened_at"] = datetime.now(timezone.utc).isoformat()
        rec.setdefault("seeded_at", datetime.now(timezone.utc).isoformat())
        history = rec.get("tighten_history") or []
        if not isinstance(history, list):
            history = []
        history.append(
            {
                "at": rec["tightened_at"],
                "snapshot": self.snapshot.name,
                "from": previous,
                "to": active_count,
            }
        )
        # Cap history to last 20 entries to keep JSON small.
        rec["tighten_history"] = history[-20:]
        self._write_baseline_record(rec)
        return active_count

    def _maybe_auto_promote_to_block(self, active_count: int) -> bool:
        """Flip ratchet to blocking after N consecutive zero-count runs.

        Increments a zero_run_streak counter on each count=0 pass, resets on
        any non-zero. When the streak hits the threshold, rewrites the JSON
        with ``auto_promoted_tier`` = "B" and emits an event entry.
        Promotion is NOT reflected in ``self.tier`` at runtime (that would
        require reloading the class); subsequent runs read the JSON and
        the harness should honour it. Integration with per-gate tier
        resolution happens in the dashboard + a follow-up tier-resolver.
        """
        if not self.baseline_filename:
            return False
        rec = self._load_baseline_record()
        # Already promoted — nothing to do.
        if rec.get("auto_promoted_tier") == "B":
            return False
        threshold = int(
            rec.get(
                "auto_promote_to_block_after_zero_runs",
                self.auto_promote_to_block_after_zero_runs,
            )
        )
        if threshold <= 0:
            return False
        if active_count == 0:
            streak = int(rec.get("zero_run_streak", 0)) + 1
        else:
            streak = 0
        rec["zero_run_streak"] = streak
        rec["last_run_at"] = datetime.now(timezone.utc).isoformat()
        rec["last_run_snapshot"] = self.snapshot.name
        promoted = False
        if active_count == 0 and streak >= threshold:
            rec["auto_promoted_tier"] = "B"
            rec["auto_promoted_at"] = rec["last_run_at"]
            rec["auto_promoted_after_streak"] = streak
            promoted = True
        self._write_baseline_record(rec)
        return promoted

    def _sink(self, result: GateResult) -> None:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        with LOG_FILE.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(_result_to_dict(result), default=str) + "\n")

    def _bypass_result(self) -> GateResult:
        result = GateResult(
            gate_id=self.gate_id,
            tier=self.tier,
            snapshot=self.snapshot.name,
            timestamp=datetime.now(timezone.utc).isoformat(),
            status="bypass",
            violations=[],
            summary={"reason": "WIRING_GATE_BYPASS=1"},
        )
        self._sink(result)
        return result


def _result_to_dict(result: GateResult) -> dict[str, Any]:
    d = asdict(result)
    return d


# ---------------------------------------------------------------------------
# Exit code helper for CLI scripts
# ---------------------------------------------------------------------------


def cli_exit(result: GateResult) -> int:
    """Print a human summary and return the shell exit code for CI."""
    print(
        f"[{result.gate_id}] tier={result.tier} status={result.status} "
        f"snapshot={result.snapshot} violations={len(result.violations)}"
    )
    for v in result.violations[:50]:
        print(f"  - {v.severity.upper():4s} {v.subject:60s} :: {v.rule} — {v.detail}")
    if len(result.violations) > 50:
        print(f"  ... {len(result.violations) - 50} more (see {LOG_FILE})")
    if result.status == "fail":
        return 1
    if result.status == "warn":
        return 0
    return 0


if __name__ == "__main__":
    sys.stderr.write("This module is a library; import it from a specific gate script.\n")
    sys.exit(2)
