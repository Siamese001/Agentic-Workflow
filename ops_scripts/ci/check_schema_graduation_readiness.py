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
    snaps = sorted(ARTIFACTS_DIR.glob("adg_indexed_*.sqlite"))
    return snaps[-1] if snaps else None


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
