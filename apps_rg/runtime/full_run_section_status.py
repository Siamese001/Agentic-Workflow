"""Mandatory per-section status table for integrated full-resume runs."""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from apps_rg.runtime.internal.generated_lane_rollup import GENERATED_LANES

FULL_RUN_SECTION_STATUS_MD = "FULL_RUN_SECTION_STATUS.md"
FULL_RUN_SECTION_STATUS_JSON = "full_run_section_status.json"

# Human-readable section text (relative to lanes/<lane>/).
LANE_DISPLAY_TXT_CANDIDATES: dict[str, tuple[str, ...]] = {
    "headline": ("headline_output.txt", "command_output.txt"),
    "executive_summary": ("resume_display_text.txt", "command_output.txt"),
    "unify_bullets": ("unify_bullets_output.txt", "command_output.txt"),
    "unify_narrative": ("unify_narrative_output.txt", "command_output.txt"),
    "ibm_bullets": ("ibm_bullets_output.txt", "command_output.txt"),
    "ibm_narrative": ("ibm_narrative_output.txt", "command_output.txt"),
    "insurtech_bullets": ("insurtech_bullets_output.txt", "command_output.txt"),
    "insurtech_narrative": ("insurtech_narrative_output.txt", "command_output.txt"),
    "ey_bullets": ("ey_bullets_output.txt", "command_output.txt"),
    "ey_narrative": ("ey_narrative_output.txt", "command_output.txt"),
    "competencies": ("competencies_display.txt", "command_output.txt"),
}


@dataclass(frozen=True)
class LaneSectionStatusRow:
    lane: str
    lane_dir: str | None
    display_txt_rel: str | None
    display_txt_abs: str | None
    x3_code: str
    product_quality: str
    x2_pass: str
    x2_failed_gate_ids: str
    runtime_generation_status: str
    executed: bool
    judge_summary: str = ""
    aggregation_pass: str = ""
    aggregation_method: str = ""
    mean_normalized_score: str = ""
    model_backed_pass_count: str = ""
    model_backed_total: str = ""
    judge_details: tuple[dict[str, Any], ...] = ()


FINAL_AGGREGATION_LANE = "final_resume_aggregation"


def _load_json(path: Path) -> dict[str, Any]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        return raw if isinstance(raw, dict) else {}
    except (OSError, json.JSONDecodeError, TypeError):
        return {}


def _repo_rel(path: Path, repo_root: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def _resolve_lane_display_txt(lane_dir: Path) -> tuple[str | None, Path | None]:
    for name in LANE_DISPLAY_TXT_CANDIDATES.get(lane_dir.name, ("command_output.txt",)):
        candidate = lane_dir / name
        if candidate.is_file() and candidate.stat().st_size > 0:
            return name, candidate
    return None, None


def _x2_summary(lane_dir: Path) -> tuple[str, str]:
    return _x2_summary_doc(_load_json(lane_dir / "x2_gate_outputs.json"))


def _x2_summary_doc(x2: dict[str, Any]) -> tuple[str, str]:
    gates = x2.get("gates")
    if not isinstance(gates, list):
        failed_art = x2.get("failed_gates") or x2.get("x2_failed_gate_ids")
        if isinstance(failed_art, list) and failed_art:
            return "FAIL", ", ".join(str(x) for x in failed_art[:6])
        return "UNKNOWN", ""
    failed = [str(g.get("gate_id")) for g in gates if isinstance(g, dict) and not g.get("pass", True)]
    if failed:
        return "FAIL", ", ".join(failed[:8])
    return "PASS", ""


def _final_assembly_dir(root: Path) -> Path:
    modular = root / "modular_r4" / "final_resume_assembly"
    if modular.is_dir():
        return modular
    return root / "final_resume_assembly"


def _score_text(value: Any) -> str:
    if value is None:
        return "—"
    if isinstance(value, float):
        return f"{value:.2f}".rstrip("0").rstrip(".")
    return str(value)


def _judge_summary(judges: list[dict[str, Any]]) -> str:
    cells: list[str] = []
    for judge in judges:
        provider = str(judge.get("provider_name") or judge.get("provider_key") or "judge")
        model = str(judge.get("model_name") or judge.get("model_actual") or "").strip()
        score = _score_text(judge.get("score"))
        threshold = _score_text(judge.get("threshold"))
        status = "PASS" if judge.get("pass") is True else "FAIL" if judge.get("pass") is False else "UNKNOWN"
        model_suffix = f" `{model}`" if model else ""
        cells.append(f"{provider}{model_suffix}: {score}/5 vs {threshold} {status}")
    return "; ".join(cells)


def _lane_judge_details(lane_dir: Path) -> tuple[dict[str, Any], ...]:
    """Load observed X1D judge rows for a section lane."""
    x1d = _load_json(lane_dir / "x1d_llm_judge_outputs.json")
    raw_judges = x1d.get("judges")
    if not isinstance(raw_judges, list):
        return ()
    rows: list[dict[str, Any]] = []
    for judge in raw_judges:
        if not isinstance(judge, dict):
            continue
        rows.append(
            {
                "judge_id": judge.get("judge_id"),
                "provider_name": judge.get("provider_name"),
                "provider_key": judge.get("provider_key"),
                "model_name": judge.get("model_name") or judge.get("model_actual"),
                "score": judge.get("score"),
                "threshold": judge.get("threshold"),
                "pass": judge.get("pass"),
                "provider_status": judge.get("provider_status") or judge.get("mode"),
                "raw_response_ref": judge.get("raw_response_ref"),
                "decisive_failure": judge.get("decisive_failure"),
                "error": judge.get("error"),
            }
        )
    return tuple(rows)


def _collect_final_aggregation_status(root: Path, repo: Path) -> LaneSectionStatusRow:
    asm = _final_assembly_dir(root)
    display = asm / "final_resume.json"
    if not asm.is_dir():
        return LaneSectionStatusRow(
            lane=FINAL_AGGREGATION_LANE,
            lane_dir=None,
            display_txt_rel=None,
            display_txt_abs=None,
            x3_code="NOT_RUN",
            product_quality="—",
            x2_pass="—",
            x2_failed_gate_ids="",
            runtime_generation_status="—",
            executed=False,
        )

    x2_pass, x2_failed = _x2_summary_doc(_load_json(asm / "final_resume_x2_gate_outputs.json"))
    preflight = _load_json(asm / "aggregation_preflight.json")
    review = _load_json(asm / "full_resume_llm_coherence_review.json")
    x1d = _load_json(asm / "x1d_full_resume_judge_outputs.json")
    aggregation = x1d.get("aggregation") if isinstance(x1d.get("aggregation"), dict) else {}
    judges_raw = x1d.get("judges") or review.get("judge_verdicts") or []
    judges = [j for j in judges_raw if isinstance(j, dict)]
    criteria = review.get("criteria_scores") if isinstance(review.get("criteria_scores"), dict) else {}
    aggregation_pass = aggregation.get("full_resume_coherence_pass")
    if aggregation_pass is None:
        aggregation_pass = review.get("full_resume_coherence_pass")
    if aggregation_pass is None:
        aggregation_pass_text = "UNKNOWN"
    else:
        aggregation_pass_text = "PASS" if bool(aggregation_pass) else "FAIL"
    preflight_pass = preflight.get("all_pass")
    x3_code = "X3_ALLOW" if aggregation_pass_text == "PASS" and x2_pass == "PASS" else "X3_REVIEW_AGGREGATION"
    if preflight_pass is False:
        x3_code = "X3_REVIEW_AGGREGATION_PREFLIGHT"
    product_quality = "PASS" if x3_code == "X3_ALLOW" else aggregation_pass_text
    display_rel = _repo_rel(display, root) if display.is_file() else None
    return LaneSectionStatusRow(
        lane=FINAL_AGGREGATION_LANE,
        lane_dir=_repo_rel(asm, repo),
        display_txt_rel=display_rel,
        display_txt_abs=str(display.resolve()) if display.is_file() else None,
        x3_code=x3_code,
        product_quality=product_quality,
        x2_pass=x2_pass,
        x2_failed_gate_ids=x2_failed,
        runtime_generation_status="ASSEMBLED",
        executed=True,
        judge_summary=_judge_summary(judges),
        aggregation_pass=aggregation_pass_text,
        aggregation_method=str(
            aggregation.get("aggregation_method")
            or review.get("aggregation_method")
            or ""
        ),
        mean_normalized_score=_score_text(criteria.get("mean_normalized_score")),
        model_backed_pass_count=_score_text(
            aggregation.get("model_backed_pass_count")
            or review.get("model_backed_pass_count")
            or criteria.get("model_backed_pass_count")
        ),
        model_backed_total=_score_text(
            aggregation.get("model_backed_total")
            or review.get("model_backed_total")
            or criteria.get("model_backed_total")
        ),
        judge_details=tuple(
            {
                "judge_id": j.get("judge_id"),
                "provider_name": j.get("provider_name"),
                "provider_key": j.get("provider_key"),
                "model_name": j.get("model_name") or j.get("model_actual"),
                "score": j.get("score"),
                "threshold": j.get("threshold"),
                "pass": j.get("pass"),
                "provider_status": j.get("provider_status"),
                "raw_response_ref": j.get("raw_response_ref"),
            }
            for j in judges
        ),
    )


def collect_full_run_section_status(
    run_root: Path,
    *,
    repo_root: Path | None = None,
) -> list[LaneSectionStatusRow]:
    """Inspect ``run_root/lanes/<lane>`` and build one row per generated lane."""
    root = Path(run_root).resolve()
    repo = (repo_root or root).resolve()
    lanes_root = root / "lanes"
    rows: list[LaneSectionStatusRow] = []

    for lane in GENERATED_LANES:
        lane_dir = lanes_root / lane if lanes_root.is_dir() else None
        if lane_dir is None or not lane_dir.is_dir():
            rows.append(
                LaneSectionStatusRow(
                    lane=lane,
                    lane_dir=None,
                    display_txt_rel=None,
                    display_txt_abs=None,
                    x3_code="NOT_RUN",
                    product_quality="—",
                    x2_pass="—",
                    x2_failed_gate_ids="",
                    runtime_generation_status="—",
                    executed=False,
                )
            )
            continue

        pre_fail = _load_json(lane_dir / "integrated_lane_pre_run_failure.json")
        pre_blocker = str(pre_fail.get("blocker") or pre_fail.get("lane_exec_status") or "").strip()

        txt_name, txt_path = _resolve_lane_display_txt(lane_dir)
        txt_rel = f"lanes/{lane}/{txt_name}" if txt_name else None
        x3 = _load_json(lane_dir / "x3_disposition.json")
        x3_code = str(x3.get("x3_code") or x3.get("disposition") or "UNKNOWN")
        if pre_blocker and x3_code == "UNKNOWN" and not txt_name:
            x3_code = f"PRE_RUN:{pre_blocker[:80]}"
        pq = str(x3.get("product_quality_status") or "UNKNOWN")
        x2_pass, x2_failed = _x2_summary(lane_dir)
        manifest = _load_json(lane_dir / "run_manifest.json")
        l2 = _load_json(lane_dir / "l2_output.json")
        rgs = str(
            manifest.get("runtime_generation_status")
            or l2.get("runtime_generation_status")
            or x3.get("runtime_generation_status")
            or "UNKNOWN"
        )
        judge_details = _lane_judge_details(lane_dir)

        rows.append(
            LaneSectionStatusRow(
                lane=lane,
                lane_dir=_repo_rel(lane_dir, repo),
                display_txt_rel=txt_rel,
                display_txt_abs=str(txt_path.resolve()) if txt_path else None,
                x3_code=x3_code,
                product_quality=pq,
                x2_pass=x2_pass,
                x2_failed_gate_ids=x2_failed,
                runtime_generation_status=rgs,
                executed=True,
                judge_summary=_judge_summary(list(judge_details)),
                judge_details=judge_details,
            )
        )
    rows.append(_collect_final_aggregation_status(root, repo))
    return rows


def render_full_run_section_status_markdown(
    rows: list[LaneSectionStatusRow],
    *,
    run_root: Path,
    repo_root: Path | None = None,
) -> str:
    root_name = Path(run_root).name
    lines = [
        "# Full resume — per-section status",
        "",
        f"Run folder: `{root_name}`",
        "",
        "| Section | X3 | X2 | Product quality | Runtime | Judges / score | Display text |",
        "|---|---|---|---|---|---|---|",
    ]
    repo = (repo_root or Path(run_root)).resolve()
    for row in rows:
        if row.display_txt_rel and row.display_txt_abs:
            link = f"[{row.display_txt_rel}]({_repo_rel(Path(row.display_txt_abs), repo)})"
        else:
            link = "— (missing)"
        judges = row.judge_summary or "—"
        lines.append(
            f"| {row.lane} | {row.x3_code} | {row.x2_pass} | {row.product_quality} | "
            f"{row.runtime_generation_status} | {judges} | {link} |"
        )
        if row.x2_failed_gate_ids:
            lines.append(f"| ↳ failed gates | | | | | | `{row.x2_failed_gate_ids}` |")
        if row.x3_code.startswith("PRE_RUN:"):
            lines.append(f"| ↳ pre-run | | | | | | `{row.x3_code}` |")
    lines.append("")
    return "\n".join(lines)


def persist_full_run_section_status(
    run_root: Path,
    *,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    root = Path(run_root).resolve()
    repo = (repo_root or root).resolve()
    rows = collect_full_run_section_status(root, repo_root=repo)
    md = render_full_run_section_status_markdown(rows, run_root=root, repo_root=repo)
    md_path = root / FULL_RUN_SECTION_STATUS_MD
    md_path.write_text(md, encoding="utf-8")
    payload = {
        "schema_version": "apps_rg.full_run_section_status.v1",
        "run_root": _repo_rel(root, repo),
        "lanes": [
            {
                "lane": r.lane,
                "executed": r.executed,
                "lane_dir": r.lane_dir,
                "display_txt_relpath": r.display_txt_rel,
                "display_txt_path": r.display_txt_abs,
                "x3_code": r.x3_code,
                "product_quality_status": r.product_quality,
                "x2_pass": r.x2_pass,
                "x2_failed_gate_ids": r.x2_failed_gate_ids,
                "runtime_generation_status": r.runtime_generation_status,
                "judge_summary": r.judge_summary,
                "aggregation_pass": r.aggregation_pass,
                "aggregation_method": r.aggregation_method,
                "mean_normalized_score": r.mean_normalized_score,
                "model_backed_pass_count": r.model_backed_pass_count,
                "model_backed_total": r.model_backed_total,
                "judges": list(r.judge_details),
            }
            for r in rows
        ],
        "markdown_relpath": FULL_RUN_SECTION_STATUS_MD,
    }
    json_path = root / FULL_RUN_SECTION_STATUS_JSON
    json_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return {"markdown_path": md_path, "json_path": json_path, "payload": payload}


def emit_full_run_section_status(
    run_root: Path,
    *,
    repo_root: Path | None = None,
    print_stdout: bool = True,
) -> dict[str, Any]:
    """Write status artifacts and print the markdown table to stdout (mandatory after full run)."""
    result = persist_full_run_section_status(run_root, repo_root=repo_root)
    if print_stdout:
        text = (result["markdown_path"]).read_text(encoding="utf-8")
        print(text, flush=True)
        sys.stdout.flush()
    return result


__all__ = [
    "FULL_RUN_SECTION_STATUS_JSON",
    "FULL_RUN_SECTION_STATUS_MD",
    "FINAL_AGGREGATION_LANE",
    "LANE_DISPLAY_TXT_CANDIDATES",
    "LaneSectionStatusRow",
    "collect_full_run_section_status",
    "emit_full_run_section_status",
    "persist_full_run_section_status",
    "render_full_run_section_status_markdown",
]
