"""SC-1 triage CSV builder.

SC-1 = gravity / illegal cross-layer import. Runs the same query as
`tools.generate.validation.gates._query_sc1_gravity` against the latest
ADG snapshot, then classifies each violation into P0/P1/P2 based on the
source layer and incoming fan-in of the source module.

Output: artifacts/reports/sc1_triage_<snapshot>.csv

Classification:
  P0  — src layer L0/L5 (routing/safety) — highest blast radius
  P1  — src layer L3/L4 (orchestration/state) or src fan_in >= 3
  P2  — everything else (L1/L2/L6 with low fan_in)
"""

from __future__ import annotations

import csv
import math
import sqlite3
import sys
from pathlib import Path

from tqdm import tqdm

REPO = Path(__file__).resolve().parents[2]
ARTIFACTS_ADG = REPO / "artifacts" / "adg"
OUT_DIR = REPO / "artifacts" / "reports"

sys.path.insert(0, str(REPO))


def _latest_snapshot() -> Path:
    snaps = sorted(ARTIFACTS_ADG.glob("adg_indexed_*.sqlite"))
    if not snaps:
        raise SystemExit("No ADG snapshot found")
    return snaps[-1]


def _classify(src_layer: str, src_fan_in: int) -> str:
    lay = (src_layer or "").upper()
    if lay in {"L0", "L5"}:
        return "P0"
    if lay in {"L3", "L4"} or src_fan_in >= 3:
        return "P1"
    return "P2"


def _impact(fan_in: int, layer: str) -> float:
    mult = {"L0": 2.0, "L5": 2.0, "L3": 1.75, "L4": 1.75, "L6": 0.75}.get((layer or "").upper(), 1.0)
    return round((1 + math.log10(1 + max(fan_in, 0))) * mult * 1.5, 3)


def main() -> int:
    snap = _latest_snapshot()
    conn = sqlite3.connect(str(snap))
    conn.row_factory = sqlite3.Row

    from tools.generate.validation.gates import _query_sc1_gravity  # type: ignore

    raw = _query_sc1_gravity(conn)
    if not raw:
        print("[sc1_triage] 0 SC-1 violations — already clean!")
        return 0

    # Build fan-in cache for source files
    fan_in_cache: dict[str, int] = {}

    def _fan_in(source_file: str) -> int:
        if source_file in fan_in_cache:
            return fan_in_cache[source_file]
        try:
            cur = conn.execute(
                "SELECT COUNT(DISTINCT e.src_id) FROM edges e "
                "JOIN nodes n ON e.dst_id=n.id "
                "WHERE n.file_path=? AND e.relation_type='imports'",
                (source_file,),
            )
            cnt = int(cur.fetchone()[0] or 0)
        except sqlite3.Error:
            cnt = 0
        fan_in_cache[source_file] = cnt
        return cnt

    enriched: list[dict] = []
    for v in tqdm(raw, desc="Classifying SC-1", unit="violation"):
        src_file = v.get("source_file", "")
        line_no = v.get("line_no", 0)
        evidence = v.get("evidence", "")
        src_layer = evidence.split("->")[0] if "->" in evidence else ""
        dst_layer = evidence.split("->")[1].split(" ")[0] if "->" in evidence else ""
        rel = evidence.split(" via ")[-1] if " via " in evidence else ""
        fi = _fan_in(src_file)
        enriched.append(
            {
                "priority": _classify(src_layer, fi),
                "impact": _impact(fi, src_layer),
                "src_layer": src_layer,
                "dst_layer": dst_layer,
                "relation": rel,
                "fan_in": fi,
                "file_path": src_file,
                "line_no": line_no,
                "evidence": evidence,
            }
        )

    enriched.sort(key=lambda x: (x["priority"], -x["impact"]))

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    snap_tag = snap.stem.replace("adg_indexed_", "")
    out = OUT_DIR / f"sc1_triage_{snap_tag}.csv"
    with out.open("w", newline="", encoding="utf-8") as fp:
        fields = [
            "priority",
            "impact",
            "src_layer",
            "dst_layer",
            "relation",
            "fan_in",
            "file_path",
            "line_no",
            "evidence",
        ]
        writer = csv.DictWriter(fp, fieldnames=fields)
        writer.writeheader()
        for row in enriched:
            writer.writerow({k: row[k] for k in fields})

    counts = {"P0": 0, "P1": 0, "P2": 0}
    for row in enriched:
        counts[row["priority"]] += 1
    print(f"[sc1_triage] rows={len(enriched)} P0={counts['P0']} P1={counts['P1']} P2={counts['P2']}")
    print(f"[sc1_triage] wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
