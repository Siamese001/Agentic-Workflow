#!/usr/bin/env python3
"""Collect latest real Qwen section run outputs and skills-graph receipts."""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SECTIONS = [
    "headline",
    "executive_summary",
    "competencies",
    "unify_bullets",
    "unify_narrative",
    "ibm_bullets",
    "ibm_narrative",
]

OUTPUT_CANDIDATES: dict[str, list[str]] = {
    "headline": ["headline_output.txt"],
    "executive_summary": ["resume_display_text.txt"],
    "competencies": ["competencies_section_output.json", "competencies_output.json"],
    "unify_bullets": ["unify_bullets_output.txt"],
    "unify_narrative": ["unify_narrative_output.txt"],
    "ibm_bullets": ["ibm_bullets_output.txt"],
    "ibm_narrative": ["ibm_narrative_output.txt"],
}


def _latest_real_dir(section: str) -> Path | None:
    real = REPO / "artifacts/apps_rg/runtime_proofs" / section / "real"
    if not real.is_dir():
        return None
    runs = [p for p in real.iterdir() if p.is_dir()]
    if not runs:
        return None
    return max(runs, key=lambda p: p.stat().st_mtime)


def _read_section_output(run_dir: Path, section: str) -> tuple[str, str]:
    for name in OUTPUT_CANDIDATES[section]:
        path = run_dir / name
        if not path.is_file():
            continue
        raw = path.read_text(encoding="utf-8")
        if path.suffix == ".json":
            try:
                data = json.loads(raw)
                return name, json.dumps(data, indent=2, ensure_ascii=False)
            except json.JSONDecodeError:
                return name, raw
        return name, raw.strip()
    # fallback: l2 resume_display_text
    l2 = run_dir / "l2_output.json"
    if l2.is_file():
        data = json.loads(l2.read_text(encoding="utf-8"))
        text = (
            data.get("resume_display_text")
            or data.get("headline_line")
            or data.get("narrative_sentence")
            or ""
        )
        if text:
            return "l2_output.json#display", str(text).strip()
    return "", ""


def _x2_status(run_dir: Path) -> str:
    x2_path = run_dir / "x2_gate_outputs.json"
    if not x2_path.is_file():
        return "UNKNOWN"
    data = json.loads(x2_path.read_text(encoding="utf-8"))
    gates = data.get("gates") or []
    if not gates:
        return data.get("product_quality_status") or data.get("status") or "UNKNOWN"
    failed = [g.get("gate_id") for g in gates if g.get("pass") is False]
    return "PASS" if not failed else "FAIL"


def _proof_eligible(run_dir: Path) -> bool | None:
    for name in ("run_manifest.json", "l2_output.json", "cli_section_execution_report.json"):
        p = run_dir / name
        if p.is_file():
            data = json.loads(p.read_text(encoding="utf-8"))
            if "proof_eligible" in data:
                return bool(data["proof_eligible"])
    return None


def _collect_receipt(run_dir: Path, section: str) -> dict:
    usage_path = run_dir / "section_input_usage_ledger.json"
    usage = {}
    if usage_path.is_file():
        usage = json.loads(usage_path.read_text(encoding="utf-8"))
    x3_path = run_dir / "x3_disposition.json"
    x3_code = ""
    if x3_path.is_file():
        x3_code = json.loads(x3_path.read_text(encoding="utf-8")).get("x3_code") or ""
    out_name, out_text = _read_section_output(run_dir, section)
    return {
        "section": section,
        "run_id": run_dir.name,
        "run_dir": str(run_dir.relative_to(REPO)).replace("\\", "/"),
        "output_artifact": out_name,
        "section_output": out_text,
        "skills_authority_source_type": usage.get("skills_authority_source_type", ""),
        "skills_authority_status": usage.get("skills_authority_status", ""),
        "claim_evidence_source_type": usage.get("claim_evidence_source_type", ""),
        "legacy_broad_skills_ledger_skills_authority": usage.get(
            "legacy_broad_skills_ledger_skills_authority"
        ),
        "x2_status": _x2_status(run_dir),
        "x3_code": x3_code,
        "proof_eligible": _proof_eligible(run_dir),
        "runtime_generation_status": (
            json.loads((run_dir / "x3_disposition.json").read_text(encoding="utf-8")).get(
                "runtime_generation_status"
            )
            if x3_path.is_file()
            else ""
        ),
    }


def run_sections() -> list[dict]:
    results: list[dict] = []
    for section in SECTIONS:
        print(f"\n=== RUN {section} ===", flush=True)
        cmd = [
            sys.executable,
            "-m",
            "apps_rg",
            "--section",
            section,
            "--provider",
            "qwen_vllm",
            "--allow-non-allow-exit-zero",
        ]
        proc = subprocess.run(cmd, cwd=REPO, capture_output=False)
        run_dir = _latest_real_dir(section)
        rec: dict = {
            "section": section,
            "cli_exit_code": proc.returncode,
            "run_dir": str(run_dir.relative_to(REPO)).replace("\\", "/") if run_dir else None,
        }
        if run_dir:
            rec.update(_collect_receipt(run_dir, section))
            print(f"OUTPUT ({rec.get('output_artifact')}):")
            print(rec.get("section_output", "")[:4000])
            print("SKILLS_GRAPH_RECEIPT:", json.dumps({k: rec[k] for k in rec if k.startswith("skills") or k in (
                "claim_evidence_source_type", "legacy_broad_skills_ledger_skills_authority",
                "x2_status", "x3_code", "proof_eligible", "runtime_generation_status"
            )}, indent=2))
        else:
            rec["error"] = "no real artifact dir found"
        results.append(rec)
    return results


def write_reports(results: list[dict], commands: list[str]) -> None:
    agentic = subprocess.run(
        ["git", "diff", "--", "agentic_core"],
        cwd=REPO,
        capture_output=True,
        text=True,
    )
    agentic_status = "clean" if not agentic.stdout.strip() else "dirty"

    skills_ok = all(
        r.get("skills_authority_source_type") == "augmented_skills_graph"
        and r.get("skills_authority_status") == "PASS"
        for r in results
        if r.get("run_dir")
    )
    all_ran = all(r.get("run_dir") for r in results)
    mock_any = any(
        str(r.get("runtime_generation_status", "")).upper() in ("MOCK", "STUB", "OFFLINE")
        for r in results
    )

    def _live_qwen_ok(r: dict) -> bool:
        rgs = str(r.get("runtime_generation_status", "")).upper()
        if rgs in ("MOCK", "STUB", "OFFLINE"):
            return False
        if rgs == "BLOCKED":
            return False
        if r.get("section") == "competencies" and '"competencies": []' in str(r.get("section_output", "")):
            return False
        return bool(r.get("section_output"))

    live_qwen_ok = all(_live_qwen_ok(r) for r in results if r.get("run_dir"))
    if not all_ran:
        status = "BLOCKED" if any(r.get("error") for r in results) else "PARTIAL"
    elif mock_any:
        status = "FAIL"
    elif not skills_ok:
        status = "FAIL"
    elif skills_ok and live_qwen_ok and all_ran:
        status = "PASS"
    else:
        status = "PARTIAL"

    payload = {
        "status": status,
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "commands_run": commands,
        "agentic_core_diff_status": agentic_status,
        "sections": results,
        "explicit_non_claims": [
            "CLI exit 0 with --allow-non-allow-exit-zero does not imply X3 ALLOW or proof_eligible.",
            "This wave proves live Qwen generation + augmented_skills_graph authority presence, not full certification.",
        ],
        "open_gaps": [
            s["section"]
            for s in results
            if s.get("x3_code") and s.get("x3_code") != "X3_ALLOW"
        ],
    }

    out_json = REPO / "docs/reports/apps_rg/live_qwen_all_section_outputs.json"
    out_md = REPO / "docs/reports/apps_rg/live_qwen_all_section_outputs.md"
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = [
        "# Live Qwen — all section outputs",
        "",
        f"**STATUS: {status}**",
        "",
        f"Generated: {payload['generated_at_utc']}",
        "",
        "## Receipt",
        "",
        "```text",
        f"STATUS: {status}",
        "FILES_CHANGED:",
        "- [live_qwen_all_section_outputs.md](docs/reports/apps_rg/live_qwen_all_section_outputs.md)",
        "- [live_qwen_all_section_outputs.json](docs/reports/apps_rg/live_qwen_all_section_outputs.json)",
        "COMMANDS_RUN:",
    ]
    for c in commands:
        lines.append(f"- {c}")
    lines.append("SECTION_OUTPUTS:")
    for r in results:
        lines.append(f"### {r['section']}")
        lines.append(f"- run_dir: `{r.get('run_dir', 'MISSING')}`")
        lines.append(f"- artifact: `{r.get('output_artifact', '')}`")
        lines.append("")
        lines.append("```")
        lines.append((r.get("section_output") or "(no output)")[:12000])
        lines.append("```")
        lines.append("")
    lines.append("SKILLS_GRAPH_RECEIPTS:")
    lines.append("| section | skills_authority_source_type | skills_authority_status | claim_evidence_source_type | legacy_broad_skills_ledger_skills_authority | x2_status | x3_code | proof_eligible |")
    lines.append("|---------|------------------------------|-------------------------|----------------------------|-----------------------------------------------|-----------|---------|----------------|")
    for r in results:
        lines.append(
            f"| {r.get('section','')} | {r.get('skills_authority_source_type','')} | {r.get('skills_authority_status','')} | "
            f"{r.get('claim_evidence_source_type','')} | {r.get('legacy_broad_skills_ledger_skills_authority','')} | "
            f"{r.get('x2_status','')} | {r.get('x3_code','')} | {r.get('proof_eligible','')} |"
        )
    lines.append("")
    lines.append(f"AGENTIC_CORE_DIFF_STATUS: {agentic_status}")
    lines.append("")
    lines.append("EXPLICIT_NON_CLAIMS:")
    for x in payload["explicit_non_claims"]:
        lines.append(f"- {x}")
    lines.append("")
    lines.append("OPEN_GAPS:")
    for g in payload["open_gaps"]:
        lines.append(f"- {g} (x3 != ALLOW)")
    if not payload["open_gaps"]:
        lines.append("- none")
    lines.append("```")
    lines.append("")
    out_md.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nWrote {out_json} and {out_md} status={status}")


def main() -> int:
    commands = [
        "python -m compileall apps_rg tests -q",
        *[f"python -m apps_rg --section {s} --provider qwen_vllm --allow-non-allow-exit-zero" for s in SECTIONS],
        "git diff -- agentic_core",
    ]
    results = run_sections()
    subprocess.run(["git", "diff", "--", "agentic_core"], cwd=REPO)
    write_reports(results, commands)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
