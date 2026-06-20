#!/usr/bin/env python3
"""Gate G-APPS-SPINE-DELEGATION — assert every apps_*/ package imports the spine.

ADR-078. Plan: .codex/plans/adg-three-bucket-unified-c4f8e2.md (W3 P3.2,
flipped to strict in W5 P5.4).

The invariant: for every ``apps_*/`` top-level package, the ADG snapshot
MUST contain at least one ``imports`` edge whose ``source_file`` starts with
``apps_X/`` and whose destination node resolves to a module under
``agentic_core/L0_routing/``, ``agentic_core/L1_cognition/``, or
``agentic_core/L2_execution/``. Packages declared in
``config/apps_spine_delegation_allowlist.yaml`` are exempt with an auditable
reason + expiry.

Per constitutional §28, this gate reads the latest
``artifacts/adg/adg_indexed_<ts>.sqlite`` directly via sqlite3 — no MCP
round-trip required. Per §22, the query is graph-layer primary
(``edges`` + ``nodes`` join, not text scanning).

Modes:
    APPS_SPINE_DELEGATION_GATE_MODE=strict    (default, W5 P5.1+) exit 1 on violation
    APPS_SPINE_DELEGATION_GATE_MODE=advisory                       exit 0 on violation
Bypass: APPS_SPINE_DELEGATION_GATE_BYPASS=1.

Usage:
    python ops_scripts/ci/check_apps_spine_delegation.py
    python ops_scripts/ci/check_apps_spine_delegation.py --strict
    python ops_scripts/ci/check_apps_spine_delegation.py --snapshot <path>
"""

from __future__ import annotations

# This gate queries the ADG nodes/edges surface directly; it does not
# consume materialized views or P-views — it is an inventory consumer.
__adg_consumer_mode__ = "inventory"

import argparse
import glob
import json
import os
import sqlite3
import sys
from dataclasses import asdict, dataclass, field
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Final

REPO_ROOT: Final[Path] = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

REPORT_PATH: Final[Path] = (
    REPO_ROOT / "docs" / "reports" / "adg" / "apps_spine_delegation_gate_report.json"
)
ALLOWLIST_PATH: Final[Path] = REPO_ROOT / "config" / "apps_spine_delegation_allowlist.yaml"

SPINE_PATH_PREFIXES: Final[tuple[str, ...]] = (
    "agentic_core/L0_routing/",
    "agentic_core/L1_cognition/",
    "agentic_core/L2_execution/",
)
SPINE_ADG_NAME_PREFIXES: Final[tuple[str, ...]] = (
    "agentic_core.L0_routing.",
    "agentic_core.L1_cognition.",
    "agentic_core.L2_execution.",
)


@dataclass
class PackageResult:
    package: str
    spine_imports: int
    total_imports: int
    is_violation: bool
    allowlisted: bool = False
    allowlist_reason: str = ""
    allowlist_expires: str = ""
    allowlist_expired: bool = False


@dataclass
class GateResult:
    gate: str = "G-APPS-SPINE-DELEGATION"
    tier: str = "B"
    timestamp: str = ""
    mode: str = "advisory"
    snapshot: str = ""
    snapshot_mtime_utc: str = ""
    packages_scanned: int = 0
    violations: int = 0
    allowlist_active: int = 0
    allowlist_expired: int = 0
    status: str = "ok"
    per_package: list[dict] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Snapshot discovery
# ---------------------------------------------------------------------------


def find_latest_snapshot(repo_root: Path) -> Path:
    """Return the most recently modified non-sentinel ADG snapshot."""
    pattern = str(repo_root / "artifacts" / "adg" / "adg_indexed_*.sqlite")
    candidates = [
        Path(p) for p in glob.glob(pattern)
        if "99999999" not in os.path.basename(p)
    ]
    if not candidates:
        raise FileNotFoundError(
            f"No non-sentinel ADG snapshot found at {pattern}. "
            "Run `python tools/generate_full_adg.py` first."
        )
    return max(candidates, key=lambda p: p.stat().st_mtime)


# ---------------------------------------------------------------------------
# Allowlist
# ---------------------------------------------------------------------------


def load_allowlist(path: Path) -> dict[str, dict]:
    """Load allowlist YAML. Returns {package: {reason, expires}}.

    Strict on shape: missing/empty `reason`, malformed `expires`, or unknown
    keys cause the entry to be skipped with a warning printed to stderr — we
    do NOT silently let bad entries pass.
    """
    if not path.is_file():
        return {}
    try:
        import yaml  # noqa: PLC0415 — optional dep, lazy import
    except ImportError:
        print(f"[apps_spine_delegation] WARNING: pyyaml not installed; allowlist ignored", file=sys.stderr)
        return {}
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError) as exc:
        print(f"[apps_spine_delegation] WARNING: allowlist parse failed: {exc}", file=sys.stderr)
        return {}

    out: dict[str, dict] = {}
    for entry in data.get("allowed_packages", []) or []:
        if not isinstance(entry, dict):
            continue
        pkg = entry.get("package", "").strip()
        reason = entry.get("reason", "").strip()
        expires = entry.get("expires", "")
        if not pkg or not reason or not expires:
            print(
                f"[apps_spine_delegation] WARNING: allowlist entry missing required field "
                f"(package/reason/expires): {entry}",
                file=sys.stderr,
            )
            continue
        out[pkg] = {"reason": reason, "expires": str(expires)}
    return out


def _is_expired(expires_str: str) -> bool:
    """Return True iff the ISO date string is strictly in the past."""
    try:
        parsed = date.fromisoformat(str(expires_str))
    except (TypeError, ValueError):
        return True  # malformed = treat as expired (fail closed on bad input)
    return parsed < date.today()


# ---------------------------------------------------------------------------
# Discovery + query
# ---------------------------------------------------------------------------


def discover_apps_packages(repo_root: Path) -> list[str]:
    """Return sorted list of apps_*/ top-level directories."""
    return sorted(
        p.name for p in repo_root.iterdir()
        if p.is_dir() and p.name.startswith("apps_") and not p.name.startswith("apps__")
    )


_SPINE_RESOLVED_PATH_CLAUSE = " OR ".join(
    f"nd.resolved_path LIKE '{p}%'" for p in SPINE_PATH_PREFIXES
)
_SPINE_ADG_NAME_CLAUSE = " OR ".join(
    f"nd.adg_name LIKE '{p}%'" for p in SPINE_ADG_NAME_PREFIXES
)


def count_spine_imports(con: sqlite3.Connection, package: str) -> int:
    """Count `imports` edges from `package/` into agentic_core.L[0-2]_*."""
    cur = con.execute(
        f"""
        SELECT COUNT(*)
        FROM edges e
        JOIN nodes nd ON nd.id = e.dst_id
        WHERE e.relation_type = 'imports'
          AND e.source_file LIKE ?
          AND ({_SPINE_RESOLVED_PATH_CLAUSE} OR {_SPINE_ADG_NAME_CLAUSE})
        """,
        (f"{package}/%",),
    )
    return int(cur.fetchone()[0])


def count_total_imports(con: sqlite3.Connection, package: str) -> int:
    """Count all `imports` edges from `package/`."""
    cur = con.execute(
        "SELECT COUNT(*) FROM edges WHERE relation_type='imports' AND source_file LIKE ?",
        (f"{package}/%",),
    )
    return int(cur.fetchone()[0])


# ---------------------------------------------------------------------------
# Gate evaluation
# ---------------------------------------------------------------------------


def evaluate(
    snapshot: Path,
    repo_root: Path,
    allowlist_path: Path,
) -> GateResult:
    allowlist = load_allowlist(allowlist_path)
    apps = discover_apps_packages(repo_root)
    con = sqlite3.connect(f"file:{snapshot.as_posix()}?mode=ro&immutable=1", uri=True)
    try:
        per_pkg: list[PackageResult] = []
        for pkg in apps:
            spine = count_spine_imports(con, pkg)
            total = count_total_imports(con, pkg)
            allow_entry = allowlist.get(pkg)
            allow = allow_entry is not None
            expired = bool(allow_entry and _is_expired(allow_entry["expires"]))
            # A package with zero spine imports is a violation UNLESS allowlisted
            # by an entry that hasn't expired.
            is_viol = spine == 0 and not (allow and not expired)
            per_pkg.append(
                PackageResult(
                    package=pkg,
                    spine_imports=spine,
                    total_imports=total,
                    is_violation=is_viol,
                    allowlisted=allow,
                    allowlist_reason=allow_entry["reason"] if allow_entry else "",
                    allowlist_expires=allow_entry["expires"] if allow_entry else "",
                    allowlist_expired=expired,
                )
            )
    finally:
        con.close()

    violations = sum(1 for r in per_pkg if r.is_violation)
    allow_active = sum(1 for r in per_pkg if r.allowlisted and not r.allowlist_expired)
    allow_expired = sum(1 for r in per_pkg if r.allowlisted and r.allowlist_expired)

    snap_mtime = datetime.fromtimestamp(snapshot.stat().st_mtime, tz=timezone.utc).isoformat()

    return GateResult(
        timestamp=datetime.now(timezone.utc).isoformat(),
        snapshot=str(snapshot.relative_to(repo_root)) if snapshot.is_relative_to(repo_root) else str(snapshot),
        snapshot_mtime_utc=snap_mtime,
        packages_scanned=len(per_pkg),
        violations=violations,
        allowlist_active=allow_active,
        allowlist_expired=allow_expired,
        status="ok" if violations == 0 else "violations_present",
        per_package=[asdict(r) for r in per_pkg],
    )


def write_report(result: GateResult, report_path: Path) -> None:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        json.dumps(asdict(result), indent=2, default=str), encoding="utf-8"
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--snapshot",
        type=Path,
        default=None,
        help="Path to ADG snapshot (defaults to latest non-sentinel adg_indexed_*.sqlite)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Force strict mode (override APPS_SPINE_DELEGATION_GATE_MODE)",
    )
    parser.add_argument(
        "--report-path",
        type=Path,
        default=None,
        help="Override default report path (mainly for test isolation)",
    )
    parser.add_argument(
        "--allowlist-path",
        type=Path,
        default=None,
        help="Override default allowlist path (mainly for test isolation)",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=None,
        help="Override repo root (mainly for testing with synthetic apps_* tree)",
    )
    args = parser.parse_args(argv)

    if os.environ.get("APPS_SPINE_DELEGATION_GATE_BYPASS") == "1":
        print("[apps_spine_delegation] bypass active (APPS_SPINE_DELEGATION_GATE_BYPASS=1)")
        return 0

    # W5 P5.1 of plan adg-three-bucket-unified-c4f8e2 (2026-04-30): strict
    # mode is now the default. Set APPS_SPINE_DELEGATION_GATE_MODE=advisory
    # to revert to the pre-P5.1 advisory behavior (exit 0 on violation, JSON
    # report only). Explicit --strict flag still forces strict. Bypass
    # remains APPS_SPINE_DELEGATION_GATE_BYPASS=1.
    mode_env = os.environ.get("APPS_SPINE_DELEGATION_GATE_MODE", "strict").strip().lower()
    strict = args.strict or mode_env == "strict"

    repo_root = args.repo_root or REPO_ROOT
    snapshot = args.snapshot or find_latest_snapshot(repo_root)
    allowlist_path = args.allowlist_path or ALLOWLIST_PATH
    report_path = args.report_path or REPORT_PATH

    result = evaluate(snapshot=snapshot, repo_root=repo_root, allowlist_path=allowlist_path)
    result.mode = "strict" if strict else "advisory"
    write_report(result, report_path)

    print(
        f"[apps_spine_delegation] mode={result.mode} "
        f"snapshot={os.path.basename(result.snapshot)} "
        f"packages={result.packages_scanned} violations={result.violations} "
        f"allowlist_active={result.allowlist_active} "
        f"allowlist_expired={result.allowlist_expired}"
    )
    if result.violations:
        for r in result.per_package:
            if r["is_violation"]:
                print(
                    f"  - VIOLATION {r['package']}: "
                    f"spine_imports={r['spine_imports']} total_imports={r['total_imports']}"
                )
    if result.allowlist_expired:
        for r in result.per_package:
            if r["allowlisted"] and r["allowlist_expired"]:
                print(
                    f"  - EXPIRED ALLOWLIST {r['package']}: "
                    f"expires={r['allowlist_expires']} reason={r['allowlist_reason']}"
                )

    if result.violations == 0:
        return 0
    return 1 if strict else 0


if __name__ == "__main__":
    sys.exit(main())
