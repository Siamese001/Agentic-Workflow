#!/usr/bin/env python3
"""W0 artefact generator — heal/SIGNAL/router env knob inventory."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "artifacts" / "reports" / "confidence_env_dead_keys_report.md"


SECTION = """# Confidence routing env hygiene report

_Generated_: `{ts}`
_Generator_: `ops_scripts/maintenance/generate_confidence_env_dead_keys_report.py`

This file is **inventory only** — it never edits operator `.env`.

## Canonical heal band knobs

| Knob | SSOT reader |
|---|---|
| `HEALING_CONFIDENCE_HIGH` | `agentic_core/L2_execution/healers/routing_thresholds_ssot.py` |
| `HEALING_CONFIDENCE_MEDIUM` | same |

PRIMARY executor thresholds remain in `confidence_aware_executor.py` (`PRIMARY_*`).

## Deprecated / misleading names

- Legacy floats `HEALING_CONFIDENCE_X` / `HEALING_CONFIDENCE_Y` were removed from
  `path_constants.py`. Use the paired knobs above instead.
- Any historic **SOVEREIGN**/**FLASH** tiers referenced in onboarding docs belong to
  different surfaces — see `.env.example` headers for partitioning.

## Router / infra companions (representative — not exhaustive)

| Area | Representative env knobs |
|---|---|
| Cascade fallbacks | `DISABLE_QWEN_FALLBACK`, `ROUTING_COST_DEMOTE_*` |
| Posterior ledger | `ROUTING_POSTERIOR_*` |
| Signal enhancer telemetry | `SIGNAL_*` (does **not** retarget heal floats) |

## Operator actions

1. Review private `.env` for legacy aliases and remove duplicates.
2. Keep heal bands paired via validated SSOT semantics (ordering + domain checks).
"""


def main() -> int:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).isoformat()
    OUT.write_text(SECTION.format(ts=ts), encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
