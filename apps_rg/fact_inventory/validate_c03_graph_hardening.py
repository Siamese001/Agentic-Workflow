"""Validate C0.3 graph hardening after full overwrite."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from apps_rg.fact_inventory.graph_metric_heterogeneity_policy import (
    POLICY_VERSION,
    diversity_summary,
    validate_metric_heterogeneity,
)
from apps_rg.fact_inventory.master_skills_arsenal_ledger import (
    collect_canonical_graph_issues,
    default_arsenal_ledger_path,
    validate_arsenal_ledger_shape,
)

_ISSUE_COUNT_RE = re.compile(r"(?:^|\s)count=(\d+)(?:\s|$)")


def _issue_record(message: str) -> dict[str, Any]:
    code, separator, detail = str(message).partition(":")
    match = _ISSUE_COUNT_RE.search(detail) if separator else None
    return {
        "code": code.strip() or "GRAPH_VALIDATION_ERROR",
        "count": int(match.group(1)) if match else 1,
        "detail": detail.strip() if separator else str(message).strip(),
    }


def _collect_hardening_issues(
    payload: dict[str, Any],
) -> tuple[list[str], dict[str, Any], dict[str, Any] | None]:
    canonical_issues = collect_canonical_graph_issues(payload)
    marker = (payload.get("metadata") or {}).get("c03_actual_graph_full_zero_loss_overwrite")
    rows = payload.get("skill_rows") or []
    summary = diversity_summary(rows)
    if not isinstance(marker, dict):
        canonical_issues.append("missing metadata.c03_actual_graph_full_zero_loss_overwrite")
    else:
        stored_policy_version = marker.get("metric_heterogeneity_policy_version")
        stored_summary = marker.get("diversity_summary")
        if stored_policy_version != POLICY_VERSION or stored_summary != summary:
            canonical_issues.append(
                "GRAPH_METRIC_HETEROGENEITY_STORED_PARITY: count=1 "
                f"stored_policy_version={stored_policy_version!r} "
                f"computed_policy_version={POLICY_VERSION!r} "
                f"stored_summary_digest={_summary_digest(stored_summary)} "
                f"computed_summary_digest={_summary_digest(summary)}"
            )
    heterogeneity_errors = validate_metric_heterogeneity(rows, strict=True)
    if heterogeneity_errors:
        canonical_issues.append(
            f"GRAPH_METRIC_HETEROGENEITY: count={len(heterogeneity_errors)} "
            + "; ".join(heterogeneity_errors)
        )
    try:
        validate_arsenal_ledger_shape(payload)
    except ValueError as exc:
        canonical_issues.append(f"ARSENAL_LEDGER_SHAPE: count=1 {exc}")

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
        canonical_issues.append(
            "C03_HARDENING_SKILLS_OR_NODES_MISSING: "
            f"count={len(missing_skills) + len(missing_nodes)} "
            f"skills={missing_skills} nodes={missing_nodes}"
        )
    return canonical_issues, summary, marker if isinstance(marker, dict) else None


def build_c03_graph_hardening_receipt(payload: dict[str, Any]) -> dict[str, Any]:
    """Build a structured PASS/NOT_READY receipt without hiding validation issues."""
    issues, summary, marker = _collect_hardening_issues(payload)
    return {
        "schema_version": "apps_rg.c03_graph_hardening_validation.v1",
        "status": "NOT_READY" if issues else "PASS",
        "overwrite_version": marker.get("version") if marker else None,
        "diversity_summary": summary,
        "heterogeneity_warnings": [],
        "issues": [_issue_record(issue) for issue in issues],
    }


def validate_c03_graph_hardening_payload(payload: dict[str, Any]) -> dict[str, Any]:
    receipt = build_c03_graph_hardening_receipt(payload)
    if receipt["issues"]:
        messages = [f"{item['code']}: {item['detail']}" for item in receipt["issues"]]
        raise ValueError("GRAPH_CANONICAL_VALIDATION: " + "; ".join(messages))
    return {
        "status": "PASS",
        "overwrite_version": receipt["overwrite_version"],
        "diversity_summary": receipt["diversity_summary"],
        "heterogeneity_warnings": [],
    }


def _summary_digest(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=None)
    parser.add_argument("--graph-path", default=None)
    parser.add_argument("--output", default=None)
    args = parser.parse_args(argv)
    repo_root = Path(args.repo_root).resolve() if args.repo_root else None
    path = Path(args.graph_path) if args.graph_path else default_arsenal_ledger_path(repo_root)
    if not path.is_absolute():
        path = (repo_root or Path.cwd()) / path
    payload = json.loads(path.read_text(encoding="utf-8"))
    receipt = build_c03_graph_hardening_receipt(payload)
    receipt["graph_path"] = str(path.resolve())
    if args.output:
        out = Path(args.output)
        if not out.is_absolute():
            out = (repo_root or Path.cwd()) / out
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2))
    if receipt["status"] != "PASS":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
