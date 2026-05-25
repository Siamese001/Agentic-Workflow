"""W0.2 — reconcile gravity inventory JSON vs architectural_exceptions.yaml."""
from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
INV = REPO / "docs/reports/cursor/l6_w6_gravity_edge_inventory_fresh.json"
YAML = REPO / "config/architectural_exceptions.yaml"


def _yaml_edge_pairs(text: str) -> set[tuple[str, str]]:
    pairs: set[tuple[str, str]] = set()
    src = tgt = None
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("- source:"):
            src = line.split(":", 1)[1].strip()
        elif line.startswith("target:") and src:
            tgt = line.split(":", 1)[1].strip()
            pairs.add((src, tgt))
            src = tgt = None
    return pairs


def main() -> None:
    inv = json.loads(INV.read_text(encoding="utf-8"))
    inv_pairs: set[tuple[str, str]] = set()
    for src, tgts in inv["by_source"].items():
        seen: set[str] = set()
        for t in tgts:
            if t["target"] in seen:
                continue
            seen.add(t["target"])
            inv_pairs.add((src, t["target"]))

    yaml_pairs = _yaml_edge_pairs(YAML.read_text(encoding="utf-8"))
    only_inv = sorted(inv_pairs - yaml_pairs)
    only_yaml = sorted(yaml_pairs - inv_pairs)

    out = {
        "plan_id": "l6-reorg-deferred-followup-f3a9c2",
        "wave": "W0",
        "inventory_distinct_pairs": len(inv_pairs),
        "inventory_raw_rows": inv["distinct_import_edges"],
        "yaml_pairs": len(yaml_pairs),
        "only_in_inventory_count": len(only_inv),
        "only_in_yaml_count": len(only_yaml),
        "reconcile_status": "PASS" if not only_inv and not only_yaml else "DRIFT",
        "only_in_inventory_sample": only_inv[:10],
        "only_in_yaml_sample": only_yaml[:10],
    }
    path = REPO / "docs/reports/cursor/l6_followup_w0_reconcile_20260525.json"
    path.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=2))
    raise SystemExit(0 if out["reconcile_status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
