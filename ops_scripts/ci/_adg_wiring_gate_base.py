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

Violation sink: artifacts/windsurf/wiring_gate_violations.jsonl (one JSON per line,
append-only). Waivers: config/wiring_gate_waivers.yaml.
"""

from __future__ import annotations

import glob
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
LOG_DIR = REPO_ROOT / "artifacts" / "windsurf"
LOG_FILE = LOG_DIR / "wiring_gate_violations.jsonl"
BASELINE_DIR = REPO_ROOT / "ops_scripts" / "ci" / "baselines"
WAIVER_FILE = REPO_ROOT / "config" / "wiring_gate_waivers.yaml"


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
    """Return the most-recently modified adg_indexed_*.sqlite, or ADG_SNAPSHOT override."""
    override = os.environ.get("ADG_SNAPSHOT", "").strip()
    if override:
        p = Path(override).expanduser().resolve()
        if not p.exists():
            raise FileNotFoundError(f"ADG_SNAPSHOT not found: {p}")
        return p
    pattern = str(ADG_DIR / "adg_indexed_*.sqlite")
    matches = sorted(glob.glob(pattern), key=os.path.getmtime)
    if not matches:
        raise FileNotFoundError(
            f"no adg_indexed_*.sqlite under {ADG_DIR}; regenerate via `python tools/generate_full_adg.py`",
        )
    return Path(matches[-1])


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


def _waiver_matches(waivers: dict[str, Any], gate_id: str, subject: str) -> bool:
    """Return True if an active waiver covers this (gate_id, subject) tuple."""
    today = datetime.now(timezone.utc).date()
    entries = waivers.get("waivers", []) if isinstance(waivers, dict) else []
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        if entry.get("gate") != gate_id:
            continue
        scope = entry.get("scope", "")
        if not (scope == subject or scope == "*" or subject.endswith(scope)):
            continue
        expires = entry.get("expires_on", "")
        try:
            exp_date = datetime.strptime(expires, "%Y-%m-%d").date()
        except (TypeError, ValueError):
            continue
        if exp_date >= today:
            return True
    return False


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
        if self.tier == "B":
            status = "fail" if active else "pass"
        elif self.tier == "R":
            baseline_count = self._baseline_count()
            status = "fail" if len(active) > (baseline_count or 0) else "pass"
        elif self.tier == "W":
            status = "warn" if active else "pass"
        else:  # K
            status = "pass"

        result = GateResult(
            gate_id=self.gate_id,
            tier=self.tier,
            snapshot=self.snapshot.name,
            timestamp=datetime.now(timezone.utc).isoformat(),
            status=status,
            violations=active,
            baseline_count=baseline_count,
            summary={"raw_count": len(raw), "active_count": len(active)},
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
