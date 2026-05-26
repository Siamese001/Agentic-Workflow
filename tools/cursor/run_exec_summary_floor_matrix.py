"""Run executive_summary Brown live matrix at judge pass floors 4.0 / 4.2 / 4.4."""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FLOORS = (4.0, 4.2, 4.4)
KEYS = ("gemini_pro", "openai_chatgpt", "anthropic_claude")
RUN_TIMEOUT_S = int(os.environ.get("EXEC_SUMMARY_FLOOR_MATRIX_TIMEOUT_S", "2400"))
CMD = [
    sys.executable,
    "-m",
    "apps_rg",
    "--section",
    "executive_summary",
    "--target-company",
    "Brown & Brown",
    "--target-role",
    "SVP IT Strategy & Innovation",
    "--jd",
    "apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_jd.txt",
    "--manual-brief",
    "apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing.md",
    "--provider",
    "qwen_vllm",
    "--allow-non-allow-exit-zero",
]


def _parse_artifact_dir(stdout: str) -> str | None:
    for line in stdout.splitlines():
        if line.startswith("artifact_dir_workspace="):
            return line.split("=", 1)[1].strip()
    m = re.search(r"exec_summary_\d{8}_\d{6}", stdout)
    if m:
        return f"artifacts/apps_rg/runtime_proofs/executive_summary/real/{m.group(0)}"
    return None


def _regen_attempts_to_pass(cycles_doc: dict | None) -> int | str:
    """First cycle index where all model-backed judges pass; else bounded failure label."""
    if not cycles_doc:
        return 0
    cycles = cycles_doc.get("cycles") or []
    if not cycles:
        return 0
    for c in cycles:
        if isinstance(c, dict) and c.get("all_judges_pass") is True:
            return int(c.get("cycle") or 0)
    used = len(cycles)
    max_c = int(cycles_doc.get("max_cycles") or 3)
    if used >= max_c:
        return f">{max_c}"
    return f">{used}"


def _summarize_run(artifact_rel: str, floor: float) -> dict:
    ad = ROOT / artifact_rel.replace("/", os.sep)
    out: dict = {"floor_minimum": floor, "artifact_dir": artifact_rel}
    x1d_p = ad / "x1d_llm_judge_outputs.json"
    cyc_p = ad / "judge_remediation_cycles.json"
    syn_p = ad / "synthesis_regen_receipt.json"
    x3_p = ad / "x3_disposition.json"
    cli_p = ad / "cli_section_execution_report.json"
    tb_p = ad / "token_budget_receipt.json"

    if tb_p.is_file():
        tb = json.loads(tb_p.read_text(encoding="utf-8"))
        out["token_budget_dispatch"] = tb.get("dispatch_allowed")
        out["token_budget_status"] = tb.get("status")

    if syn_p.is_file():
        syn = json.loads(syn_p.read_text(encoding="utf-8"))
        attempts = syn.get("attempts") or []
        out["synthesis_regen_attempts"] = len(attempts) if syn.get("triggered") else 0

    if x1d_p.is_file():
        x1d = json.loads(x1d_p.read_text(encoding="utf-8"))
        judges = x1d.get("judges") or []
        scores: dict[str, dict] = {}
        for j in judges:
            if j.get("evaluator_mode") != "MODEL_BACKED":
                continue
            pk = str(j.get("provider_key") or "")
            if pk:
                scores[pk] = {
                    "score": j.get("score"),
                    "normalized_score": j.get("normalized_score"),
                    "pass": j.get("pass"),
                    "threshold": j.get("threshold"),
                }
        out["final_judge_scores"] = scores
        mb = [scores[k] for k in KEYS if k in scores]
        out["all_judges_pass_at_floor"] = bool(mb) and all(s.get("pass") is True for s in mb)
        out["min_score_0_to_5"] = (
            min(float(s["score"]) for s in mb if s.get("score") is not None) if mb else None
        )

    cyc_doc = json.loads(cyc_p.read_text(encoding="utf-8")) if cyc_p.is_file() else None
    if cyc_doc:
        out["judge_regen_cycles_schema_version"] = cyc_doc.get("schema_version")
        out["judge_regen_cycles_used"] = len(cyc_doc.get("cycles") or [])
        out["judge_regen_stopped_reason"] = cyc_doc.get("stopped_reason")
        out["judge_regen_max_cycles"] = cyc_doc.get("max_cycles")
        out["regen_outcome"] = cyc_doc.get("regen_outcome")
        out["final_publish_baseline"] = cyc_doc.get("final_publish_baseline")
        out["publish_baseline"] = cyc_doc.get("final_publish_baseline")
        out["published_candidate_digest"] = cyc_doc.get("published_candidate_digest")
        cycles = cyc_doc.get("cycles") or []
        if cycles and isinstance(cycles[-1], dict):
            out["last_cycle_reject_gate"] = cycles[-1].get("reject_gate")
            out["last_cycle_delta_class"] = cycles[-1].get("delta_class")
    out["judge_regen_attempts_to_achieve_floor"] = _regen_attempts_to_pass(cyc_doc)

    if x3_p.is_file():
        x3 = json.loads(x3_p.read_text(encoding="utf-8"))
        out["x3_code"] = x3.get("x3_code")
        out["x3_pass"] = bool(x3.get("pass"))
    if cli_p.is_file():
        cli = json.loads(cli_p.read_text(encoding="utf-8"))
        out["certified"] = bool(cli.get("CERTIFIED") or cli.get("certified"))
        out["operator_status"] = cli.get("OPERATOR_STATUS") or cli.get("operator_status")
    return out


def _print_markdown_table(rows: list[dict]) -> None:
    print(
        "\n| Floor | Regen attempts | Cycles | Publish baseline | Reject gate | Regen outcome | Min score |",
    )
    print("|---:|---|---:|---|---|---|---:|")
    for r in rows:
        floor = r.get("floor_minimum", r.get("floor", ""))
        attempts = r.get("judge_regen_attempts_to_achieve_floor", "—")
        used = r.get("judge_regen_cycles_used", "—")
        baseline = r.get("publish_baseline", r.get("final_publish_baseline", "—"))
        reject_gate = r.get("last_cycle_reject_gate", "—")
        outcome = r.get("regen_outcome", "—")
        mn = r.get("min_score_0_to_5", "—")
        print(f"| {floor} | {attempts} | {used} | {baseline} | {reject_gate} | {outcome} | {mn} |")


def main() -> int:
    rows: list[dict] = []
    for floor in FLOORS:
        env = os.environ.copy()
        env.update(
            {
                "VLLM_MAX_MODEL_LEN": os.environ.get("VLLM_MAX_MODEL_LEN", "32768"),
                "APPS_RG_EXEC_SUMMARY_JUDGE_REGEN": "1",
                "APPS_RG_EXEC_SUMMARY_JUDGE_REGEN_MAX_ATTEMPTS": "3",
                "APPS_RG_QWEN_TIMEOUT_SECONDS": "120",
                "APPS_RG_EXEC_SUMMARY_REGEN_MAX_DELTA_TOKENS": "768",
                "APPS_RG_EXEC_SUMMARY_JUDGE_PASS_FLOOR": str(floor),
            }
        )
        print(f"\n=== FLOOR {floor} (live qwen_vllm) ===", flush=True)
        proc = subprocess.run(
            CMD,
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
            timeout=RUN_TIMEOUT_S,
        )
        combined = (proc.stdout or "") + "\n" + (proc.stderr or "")
        rel = _parse_artifact_dir(combined)
        row: dict = {
            "floor_minimum": floor,
            "exit_code": proc.returncode,
            "artifact_dir": rel,
        }
        if proc.returncode != 0 and not rel:
            row["error_tail"] = "\n".join(combined.splitlines()[-25:])
        if rel:
            row.update(_summarize_run(rel, floor))
        rows.append(row)
        out_path = ROOT / "artifacts/apps_rg/runtime_proofs/executive_summary/real/floor_matrix_latest.json"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps({"runs": rows}, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(row, indent=2), flush=True)

    _print_markdown_table(rows)
    print("\n=== JSON ===", flush=True)
    print(json.dumps({"runs": rows}, indent=2))
    ok = all(
        r.get("token_budget_dispatch") is not False and r.get("artifact_dir")
        for r in rows
    )
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
