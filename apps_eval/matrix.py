"""Suite matrix runner for apps_eval."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from apps_eval.contracts import EvalRequest
from apps_eval.registry import load_suites_registry
from apps_eval.runner.core import run_eval


def _stable_matrix_id(payload: dict[str, Any]) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def _render_matrix(summary: dict[str, Any]) -> str:
    lines = [
        f"# apps_eval matrix: {summary['matrix_id']}",
        "",
        f"App filter: `{summary.get('app_id') or 'all'}`",
        f"Split filter: `{summary.get('split') or 'all'}`",
        f"Mode: `{summary['mode']}`",
        f"Verdict: `{summary['verdict']}`",
        "",
        "| Suite | App | Score | Verdict | Block Failures | Record |",
        "|---|---|---:|---|---:|---|",
    ]
    for row in summary["suites"]:
        lines.append(
            "| {suite_id} | {app_id} | {score:.6f} | {verdict} | {block_failures} | `{record_path}` |".format(
                **row
            )
        )
    lines.append("")
    return "\n".join(lines)


def run_matrix(
    *,
    app_id: str = "",
    split: str = "",
    mode: str = "snapshot",
    deterministic_only: bool = True,
    out_dir: str = "artifacts/apps_eval/runs",
) -> dict[str, Any]:
    suites = load_suites_registry()
    selected = [
        suite_id
        for suite_id, suite in sorted(suites.items())
        if suite.get("scenarios")
        and (not app_id or suite.get("app_id") == app_id)
        and (not split or suite.get("split") == split)
    ]
    if not selected:
        raise ValueError("no runnable suites matched the matrix filters")

    seed = {
        "app_id": app_id,
        "split": split,
        "mode": mode,
        "deterministic_only": deterministic_only,
        "suites": selected,
    }
    matrix_id = _stable_matrix_id(seed)
    matrix_dir = Path(out_dir) / "matrix" / matrix_id
    records_dir = matrix_dir / "records"
    rows: list[dict[str, Any]] = []
    for suite_id in selected:
        record = run_eval(
            EvalRequest(
                suite_id=suite_id,
                mode=mode,  # type: ignore[arg-type]
                deterministic_only=deterministic_only,
                out_dir=str(records_dir),
            )
        )
        rows.append(
            {
                "suite_id": suite_id,
                "app_id": record.app_id,
                "score": record.scorecard.score,
                "verdict": record.scorecard.verdict,
                "block_failures": record.scorecard.block_failures,
                "record_path": record.artifact_paths["eval_record"],
            }
        )
    verdict = "pass" if all(row["verdict"] == "pass" for row in rows) else "fail"
    summary = {
        "matrix_id": matrix_id,
        "app_id": app_id,
        "split": split,
        "mode": mode,
        "deterministic_only": deterministic_only,
        "verdict": verdict,
        "suite_count": len(rows),
        "suites": rows,
        "artifact_paths": {},
    }
    matrix_dir.mkdir(parents=True, exist_ok=True)
    summary_path = matrix_dir / "matrix_summary.json"
    report_path = matrix_dir / "matrix_report.md"
    summary["artifact_paths"] = {
        "matrix_summary": summary_path.as_posix(),
        "matrix_report": report_path.as_posix(),
    }
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    report_path.write_text(_render_matrix(summary), encoding="utf-8")
    return summary
