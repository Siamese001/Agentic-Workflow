#!/usr/bin/env python3
"""W0 artefact generator — retired confidence-router inventory."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "artifacts" / "reports" / "confidence_env_dead_keys_report.md"


SECTION = """# Retired confidence routing hygiene report

_Generated_: `{ts}`
_Generator_: `ops_scripts/maintenance/generate_confidence_env_dead_keys_report.py`

This file is **inventory only** — it never edits operator `.env`.

## Current policy

L2 E4 same-authority repair receipts are the kept healing path. Confidence
router env knobs are retired and must not be added back to `.env` files.

## Deprecated / misleading names

- Legacy float aliases were removed from `path_constants.py`.
- Any historic **SOVEREIGN**/**FLASH** tiers referenced in onboarding docs belong to
  different surfaces — see `.env.example` headers for partitioning.

## Router / infra companions (representative — not exhaustive)

| Area | Representative env knobs |
|---|---|
| Cascade fallbacks | retired for app execution |
| Posterior ledger | `ROUTING_POSTERIOR_*` |
| Signal enhancer telemetry | `SIGNAL_*` |

## Operator actions

1. Review private `.env` for retired confidence-router aliases and remove them.
2. Keep app repair work on E4 same-authority receipt paths.
"""


def main() -> int:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).isoformat()
    OUT.write_text(SECTION.format(ts=ts), encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
