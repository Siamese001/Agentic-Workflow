"""G-SCHEMA-GRADUATION-READINESS — advisory gate reporting whether the
schema is ready for NOT NULL graduation (W7 of plan
three-bucket-gap-remediation-069806).

This gate is **advisory by default** because graduation is a one-way
schema migration that should only be triggered after a 4-week green
window of the upstream gates (3B1..3B4). It surfaces:

  * remaining NULL counts on the closed-enum columns
  * how many columns are already graduated
  * blockers preventing graduation

Strict mode (``SCHEMA_GRADUATION_READINESS_STRICT=1`` / ``--strict``)
fails when ANY blockers remain — useful for projects that have
backfilled all rows and want CI to insist on graduation before the
next regen.
"""

from __future__ import annotations

# Consumes the snapshot via direct SQLite; no MV queries.
__adg_consumer_mode__ = "inventory"

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Final

REPO_ROOT: Final[Path] = Path(__file__).resolve().parents[2]
ARTIFACTS_DIR: Final[Path] = REPO_ROOT / "artifacts" / "adg"
GATE_REPORT_PATH: Final[Path] = (
    REPO_ROOT / "docs" / "reports" / "adg" / "schema_graduation_readiness_gate.json"
)


def _latest_snapshot() -> Path | None:
    """Resolve the latest valid ADG snapshot.

    Delegates to the canonical ``tools.adg.shared_modules.path_resolver.latest_sqlite``
    which validates ``%m%d%Y_%H%M`` timestamps and picks by mtime. This rejects
    the legacy sentinel ``adg_indexed_99999999_9999.sqlite`` (month 99 is
    invalid) — without this delegation, the previous naive
    ``sorted(glob())[-1]`` would shadow the real snapshot with any sentinel
    that test code or archiver cleanup left behind.

    Regression precedent (2026-04-30): a sentinel at
    ``artifacts/adg/adg_indexed_99999999_9999.sqlite`` was shadowing the
    real snapshot and this gate reported 4 columns "not present" against the
    empty 24KB stub. Fix is to use the canonical resolver everywhere.
    """
    try:
        from tools.adg.shared_modules.path_resolver import latest_sqlite  # noqa: PLC0415
    except ImportError:
        # Fallback only when the shared module is genuinely unimportable
        # (e.g. tests that don't have tools/ on sys.path). Filter sentinels
        # manually in that case.
        files = list(ARTIFACTS_DIR.glob("adg_indexed_*.sqlite"))
        from datetime import datetime as _dt  # noqa: PLC0415
        def _valid(p: Path) -> bool:
            try:
                _dt.strptime(p.stem.replace("adg_indexed_", ""), "%m%d%Y_%H%M")
                return True
            except ValueError:
                return False
        valid = [p for p in files if _valid(p)]
        return max(valid, key=lambda p: p.stat().st_mtime) if valid else None
    return latest_sqlite()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", type=Path, default=None)
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Force strict mode (override SCHEMA_GRADUATION_READINESS_STRICT)",
    )
    args = parser.parse_args(argv)

    if os.environ.get("SCHEMA_GRADUATION_READINESS_BYPASS") == "1":
        print("[schema_graduation] bypass active (SCHEMA_GRADUATION_READINESS_BYPASS=1)")
        return 0

    # Advisory by default — graduation is a one-way migration.
    _env = os.environ.get("SCHEMA_GRADUATION_READINESS_STRICT", "0")
    strict = args.strict or _env == "1"

    snapshot = args.snapshot or _latest_snapshot()
    if snapshot is None or not snapshot.exists():
        print("[schema_graduation] FAIL: no snapshot found")
        return 1 if strict else 0

    sys.path.insert(0, str(REPO_ROOT))
    from tools.adg.graduate_schema_not_null import assess  # noqa: PLC0415

    stats = assess(snapshot)

    GATE_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    GATE_REPORT_PATH.write_text(
        json.dumps(
            {
                "gate": "G-SCHEMA-GRADUATION-READINESS",
                "tier": "B",
                "advisory_mode": not strict,
                "snapshot": stats.snapshot,
                "status": stats.status,
                "needs_graduation": stats.needs_graduation,
                "already_graduated": stats.already_graduated,
                "null_counts": stats.null_counts,
                "blockers": stats.blockers,
                "timestamp": stats.timestamp,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    print(
        f"[schema_graduation] status={stats.status} "
        f"already={len(stats.already_graduated)} "
        f"needs={len(stats.needs_graduation)} "
        f"blockers={len(stats.blockers)} "
        f"strict={strict}"
    )
    if stats.blockers:
        print(f"[schema_graduation] details: {GATE_REPORT_PATH.relative_to(REPO_ROOT)}")
        for b in stats.blockers[:5]:
            print(f"  - {b}")

    if stats.status == "blocked" and strict:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
