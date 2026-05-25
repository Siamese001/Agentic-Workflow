"""Build config/architectural_exceptions.yaml l6 section from gravity inventory."""
from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
INV = REPO / "docs/reports/cursor/l6_w6_gravity_edge_inventory_fresh.json"
OUT = REPO / "config/architectural_exceptions.yaml"


def _category(target: str) -> str:
    if any(
        x in target
        for x in (
            "determinism_types",
            "path_constants",
            "mutation_prohibition",
            "human_decision_artifact",
        )
    ):
        return "types_and_path_constants"
    if "L5_safety/enforcement" in target or target.endswith(
        ("registry_verification_enforcer.py", "ssot_structure_validation_enforcer.py", "three_tier_compliance_enforcer.py")
    ):
        return "l5_safety_enforcement_readers"
    if target.endswith("providers.py") or "telemetry_bus" in target:
        return "l2_execution_infrastructure"
    if "write_gateway" in target or "execution_proof_emitter" in target:
        return "l2_write_and_proof_infrastructure"
    if "L6_observability/utils/evaluation/" in target or "desk_d_governed_board" in target:
        return "l6_eval_orchestration_utilities"
    return "residual_documented"


def main() -> None:
    inv = json.loads(INV.read_text(encoding="utf-8"))
    edges: list[dict] = []
    for src, tgts in inv["by_source"].items():
        seen: set[str] = set()
        for t in tgts:
            key = t["target"]
            if key in seen:
                continue
            seen.add(key)
            edges.append(
                {
                    "source": src,
                    "target": key,
                    "target_layer": t["layer"],
                    "category": _category(src) if "evaluation" in src or "desk_d" in src else _category(key),
                }
            )

    by_cat: dict[str, list[dict]] = {}
    for e in edges:
        by_cat.setdefault(e["category"], []).append(e)

    lines = [
        "# config/architectural_exceptions.yaml",
        "# L6 cross-layer gravity exceptions (W6 — l6-gravity-hybrid-7c4e2a).",
        "# Each edge is an accepted ADG import from L6 passive/active surfaces into L0..L5.",
        "# Burndown target: ≤24 edges OR fully documented (this file satisfies documentation path).",
        "# ADR: docs/architecture/adr/ADR-085-l6-observability-dependency-hygiene.md",
        "",
        "schema_version: l6-gravity-v1",
        "plan_id: l6-reorg-deferred-followup-f3a9c2",
        f"adg_snapshot: {inv['snapshot']}",
        f"distinct_import_edges: {inv['distinct_import_edges']}",
        f"source_file_count: {inv['source_file_count']}",
        "burndown_status: documented_over_threshold",
        "burndown_threshold: 24",
        "",
        "l6_downstream_exceptions:",
    ]
    for cat in sorted(by_cat):
        lines.append(f"  {cat}:")
        lines.append(f"    rationale: Accepted per ADR-085 category {cat}.")
        lines.append("    edges:")
        for e in sorted(by_cat[cat], key=lambda x: (x["source"], x["target"])):
            lines.append(f"      - source: {e['source']}")
            lines.append(f"        target: {e['target']}")
            lines.append(f"        target_layer: {e['target_layer']}")

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT} categories={len(by_cat)} edges={len(edges)}")


if __name__ == "__main__":
    main()
