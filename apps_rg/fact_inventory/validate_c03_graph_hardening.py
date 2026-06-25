"""Validate C0.3 graph hardening after full overwrite."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from apps_rg.fact_inventory.graph_metric_heterogeneity_policy import diversity_summary, validate_metric_heterogeneity
from apps_rg.fact_inventory.master_skills_arsenal_ledger import default_arsenal_ledger_path, validate_arsenal_ledger_shape


def validate_c03_graph_hardening_payload(payload: dict[str, Any]) -> dict[str, Any]:
    validate_arsenal_ledger_shape(payload)
    marker = (payload.get("metadata") or {}).get("c03_actual_graph_full_zero_loss_overwrite")
    if not isinstance(marker, dict):
        raise ValueError("missing metadata.c03_actual_graph_full_zero_loss_overwrite")
    rows = payload.get("skill_rows") or []
    summary = diversity_summary(rows)
    heterogeneity_errors = validate_metric_heterogeneity(rows)
    hardening_skill_ids = {
        "skill_c03_metric_heterogeneity_selection",
        "skill_c03_reverse_traversal_receipts",
        "skill_c03_sibling_skill_rejection_reasoning",
    }
    row_ids = {str(r.get("skill_id")) for r in rows if isinstance(r, dict)}
    missing_skills = sorted(hardening_skill_ids - row_ids)
    node_ids = {str(n.get("node_id")) for n in payload.get("graph_nodes") or [] if isinstance(n, dict)}
    missing_nodes = sorted(hardening_skill_ids - node_ids)
    if missing_skills or missing_nodes:
        raise ValueError(f"missing C0.3 hardening skills={missing_skills} nodes={missing_nodes}")
    return {
        "status": "PASS",
        "overwrite_version": marker.get("version"),
        "diversity_summary": summary,
        "heterogeneity_warnings": heterogeneity_errors,
    }


def main() -> None:
    path = default_arsenal_ledger_path()
    payload = json.loads(path.read_text(encoding="utf-8"))
    receipt = validate_c03_graph_hardening_payload(payload)
    out = Path("docs/reports/apps_rg/c03_actual_graph_full_zero_loss_overwrite_validation.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
