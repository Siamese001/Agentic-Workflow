"""Fail when W9 lanes with examples YAML do not wire E0 hydration at compile."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AUDIT_SCRIPT = ROOT / "ops_scripts" / "apps_rg" / "prompt_assembly_ssot_gap_audit.py"
AUDIT = ROOT / "artifacts" / "apps_rg" / "plans" / "prompt_assembly_ssot_gap_audit.json"
PA_SECTIONS = ROOT / "apps_rg" / "runtime" / "sections"
STALE_DOC_PATHS = (
    "apps_rg/prompt_assembly/rg_prompt_profile.yaml",
    "apps_rg/prompt_assembly/rg_style_profile.yaml",
    "apps_rg/prompt_assembly/rg_evidence_profile.yaml",
)
PA_CONTRACT_DOC = ROOT / "docs" / "guides" / "apps_rg_pa_prompt_contract.md"

REQUIRED_IMPORT = "resolve_e0_for_section"
LANE_MODULES = {
    "executive_summary": "executive_summary_pa.py",
    "competencies": "competencies_pa.py",
    "unify_bullets": "unify_bullets_pa.py",
    "unify_narrative": "unify_narrative_pa.py",
}


def main() -> int:
    failures: list[str] = []

    subprocess.run([sys.executable, str(AUDIT_SCRIPT)], cwd=str(ROOT), check=True)

    for section, mod in LANE_MODULES.items():
        path = PA_SECTIONS / mod
        text = path.read_text(encoding="utf-8")
        if REQUIRED_IMPORT not in text:
            failures.append(f"{mod}: missing {REQUIRED_IMPORT}")
        if 'e0_examples=slots.get("E0")' in text or 'e0_examples=slots["E0"]' in text:
            failures.append(f"{mod}: still uses raw template E0 without resolve_e0_for_section")

    if AUDIT.is_file():
        data = json.loads(AUDIT.read_text(encoding="utf-8"))
        if int(data.get("p0_count") or 0) > 0:
            failures.append(f"audit p0_count={data.get('p0_count')} (expected 0)")
        for lane in data.get("w9_lanes") or []:
            if not lane.get("examples_file"):
                continue
            if lane.get("dual_authority_risk"):
                failures.append(
                    f"{lane.get('section')}: dual_authority_risk still true in audit JSON"
                )
            if not lane.get("examples_wired_at_compile"):
                failures.append(f"{lane.get('section')}: examples_wired_at_compile is false")
    else:
        failures.append(f"missing audit artifact: {AUDIT}")

    if PA_CONTRACT_DOC.is_file():
        doc = PA_CONTRACT_DOC.read_text(encoding="utf-8")
        for rel in STALE_DOC_PATHS:
            if rel in doc and not (ROOT / rel).is_file():
                failures.append(f"PA contract doc still references missing path: {rel}")
    else:
        failures.append(f"missing PA contract doc: {PA_CONTRACT_DOC}")

    proof_script = ROOT / "ops_scripts" / "apps_rg" / "verify_pa_e0_compile_proof.py"
    if proof_script.is_file():
        subprocess.run([sys.executable, str(proof_script)], cwd=str(ROOT), check=True)
    else:
        failures.append(f"missing compile proof script: {proof_script}")

    if failures:
        print("PA-SSOT FAIL:")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("PA-SSOT PASS: E0 hydration wired for examples-backed W9 lanes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
