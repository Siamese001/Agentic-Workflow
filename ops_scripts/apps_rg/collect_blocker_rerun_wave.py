#!/usr/bin/env python3
"""Collect latest real run receipts for blocker rerun wave."""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SECTIONS = ["competencies", "ibm_bullets", "ibm_narrative", "executive_summary"]
OUTPUT_MAP = {
    "competencies": ["competencies_section_output.json", "competencies_output.json"],
    "ibm_bullets": ["ibm_bullets_output.txt"],
    "ibm_narrative": ["ibm_narrative_output.txt"],
    "executive_summary": ["resume_display_text.txt"],
}


def latest_real(section: str) -> Path | None:
    real = REPO / "artifacts/apps_rg/runtime_proofs" / section / "real"
    if not real.is_dir():
        return None
    runs = [p for p in real.iterdir() if p.is_dir()]
    return max(runs, key=lambda p: p.stat().st_mtime) if runs else None


def read_output(run_dir: Path, section: str) -> str:
    for name in OUTPUT_MAP[section]:
        p = run_dir / name
        if p.is_file():
            raw = p.read_text(encoding="utf-8")
            if p.suffix == ".json":
                try:
                    return json.dumps(json.loads(raw), indent=2, ensure_ascii=False)[:8000]
                except json.JSONDecodeError:
                    pass
            return raw.strip()[:8000]
    return ""


def x2_status(run_dir: Path) -> str:
    p = run_dir / "x2_gate_outputs.json"
    if not p.is_file():
        return "UNKNOWN"
    data = json.loads(p.read_text(encoding="utf-8"))
    failed = [g.get("gate_id") for g in data.get("gates") or [] if g.get("pass") is False]
    return "PASS" if not failed else "FAIL"


def collect(section: str) -> dict:
    run_dir = latest_real(section)
    if not run_dir:
        return {"section": section, "error": "no real run dir"}
    usage = {}
    up = run_dir / "section_input_usage_ledger.json"
    if up.is_file():
        usage = json.loads(up.read_text(encoding="utf-8"))
    x3 = {}
    x3p = run_dir / "x3_disposition.json"
    if x3p.is_file():
        x3 = json.loads(x3p.read_text(encoding="utf-8"))
    prov = {}
    pp = run_dir / "provider_response.json"
    if pp.is_file():
        prov = json.loads(pp.read_text(encoding="utf-8"))
    qd = {}
    qp = run_dir / "qwen_transport_diagnostic.json"
    if qp.is_file():
        qd = json.loads(qp.read_text(encoding="utf-8"))
    pe = None
    for name in ("run_manifest.json", "l2_output.json"):
        rp = run_dir / name
        if rp.is_file():
            pe = json.loads(rp.read_text(encoding="utf-8")).get("proof_eligible")
            break
    comps_nonempty = None
    if section == "competencies":
        co = run_dir / "competencies_output.json"
        if co.is_file():
            comps_nonempty = len(json.loads(co.read_text(encoding="utf-8"))) > 0
    return {
        "section": section,
        "run_dir": str(run_dir.relative_to(REPO)).replace("\\", "/"),
        "section_output": read_output(run_dir, section),
        "skills_authority_source_type": usage.get("skills_authority_source_type"),
        "skills_authority_status": usage.get("skills_authority_status"),
        "claim_evidence_source_type": usage.get("claim_evidence_source_type"),
        "legacy_broad_skills_ledger_skills_authority": usage.get("legacy_broad_skills_ledger_skills_authority"),
        "x2_status": x2_status(run_dir),
        "x3_code": x3.get("x3_code"),
        "proof_eligible": pe,
        "runtime_generation_status": x3.get("runtime_generation_status") or prov.get("runtime_generation_status"),
        "provider_available": prov.get("provider_available"),
        "provider_error": prov.get("exact_provider_error"),
        "timeout_seconds": qd.get("timeout_seconds"),
        "competencies_nonempty": comps_nonempty,
    }


def main() -> int:
    results = []
    for section in SECTIONS:
        print(f"\n=== RUN {section} ===", flush=True)
        proc = subprocess.run(
            [
                sys.executable,
                "-m",
                "apps_rg",
                "--section",
                section,
                "--provider",
                "qwen_vllm",
                "--allow-non-allow-exit-zero",
            ],
            cwd=REPO,
        )
        rec = collect(section)
        rec["cli_exit_code"] = proc.returncode
        results.append(rec)
        print(json.dumps({k: rec[k] for k in rec if k != "section_output"}, indent=2))
    out = REPO / "docs/reports/apps_rg/live_qwen_remaining_blockers_closeout.json"
    out.write_text(
        json.dumps(
            {"generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "sections": results},
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"\nWrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
