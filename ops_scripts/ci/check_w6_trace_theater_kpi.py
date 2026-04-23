#!/usr/bin/env python3
"""KPI E3 — trace-theater growth per layer (plan W6.4).

Ratio per layer of ``_emit_*`` / ``_tracer_*`` / ``_trace_*`` symbol
count vs real production imports. A rising ratio signals trace-
theater (stub modules masquerading as instrumented surfaces).

Tier: K (KPI). Emits one JSONL row per run to
``artifacts/windsurf/kpi_trace_theater.jsonl``.
"""

from __future__ import annotations

import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

from tqdm import tqdm

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ops_scripts.ci._adg_wiring_gate_base import (  # noqa: E402
    LOG_DIR,
    Violation,
    WiringGate,
    cli_exit,
)

KPI_SINK = LOG_DIR / "kpi_trace_theater.jsonl"
PROD_LAYERS = ("L0", "L1", "L2", "L3", "L4", "L5", "L6", "L_APP", "L_PG")


class TraceTheaterKpiGate(WiringGate):
    gate_id = "E3_trace_theater_kpi"
    tier = "K"

    def run(self, conn: sqlite3.Connection) -> list[Violation]:
        layers_list = ",".join(f"'{layer}'" for layer in PROD_LAYERS)
        per_layer: dict[str, dict[str, int]] = {}
        for layer, emit_count in tqdm(
            list(
                conn.execute(
                    f"""
                    SELECT layer, COUNT(*)
                    FROM nodes
                    WHERE entity_type='symbol'
                      AND layer IN ({layers_list})
                      AND (adg_name LIKE '%_emit_%' OR adg_name LIKE '_trace_%' OR adg_name LIKE '_tracer_%')
                    GROUP BY layer
                    """
                )
            ),
            desc="E3_emit_count",
            unit="layer",
        ):
            per_layer.setdefault(layer, {})["emit_count"] = emit_count

        import_rows = list(
            conn.execute(
                f"""
                SELECT src.layer, COUNT(*)
                FROM edges e
                JOIN nodes src ON src.id = e.src_id
                WHERE e.relation_type='imports'
                  AND src.layer IN ({layers_list})
                GROUP BY src.layer
                """
            )
        )
        for layer, import_count in tqdm(import_rows, desc="E3_import_count", unit="layer", leave=False):
            per_layer.setdefault(layer, {})["import_count"] = import_count

        ratios = {}
        for layer, counts in per_layer.items():
            imp = counts.get("import_count", 0)
            emit = counts.get("emit_count", 0)
            ratios[layer] = {
                "emit_count": emit,
                "import_count": imp,
                "ratio": (emit / imp) if imp > 0 else 0.0,
            }

        LOG_DIR.mkdir(parents=True, exist_ok=True)
        with KPI_SINK.open("a", encoding="utf-8") as fh:
            fh.write(
                json.dumps(
                    {
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "per_layer": ratios,
                    }
                )
                + "\n"
            )
        return []  # K-tier


def main() -> int:
    return cli_exit(TraceTheaterKpiGate().execute())


if __name__ == "__main__":
    sys.exit(main())
