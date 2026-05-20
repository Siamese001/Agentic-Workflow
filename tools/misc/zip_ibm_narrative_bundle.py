#!/usr/bin/env python3
"""One-off bundle: IBM narrative prompt/templates + runtime seam + local runtime_proofs tree."""
from __future__ import annotations

import zipfile
from datetime import UTC, datetime
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "artifacts" / "bundles" / "ibm_narrative_prompt_templates_and_artifacts.zip"

SOURCE_REL = [
    "apps_rg/prompt_assembly/templates/ibm_position_narrative_v1.yaml",
    "apps_rg/prompt_assembly/templates/w7_strategic_tailor_shell_slots.yaml",
    "apps_rg/prompt_assembly/section_prompt_contracts/ibm_narrative.contract.yaml",
    "apps_rg/prompt_assembly/prompt_registry.yaml",
    "apps_rg/prompt_assembly/prompt_bom.yaml",
    "apps_rg/rg_output_schema.json",
    "apps_rg/runtime/sections/ibm_narrative_lane_runtime.py",
    "apps_rg/runtime/dispatch/ibm_narrative_pa.py",
    "apps_rg/runtime/dispatch/unify_ibm_pa_common.py",
    "apps_rg/runtime/dispatch/input_authority_prompt_block.py",
    "apps_rg/runtime/sections/ibm_narrative_lane.py",
    "apps_rg/runtime/validators/ibm_narrative_x2.py",
    "apps_rg/runtime/judges/ibm_narrative_x1d.py",
    "apps_rg/runtime/judges/X1D_PROVIDER_CONFIG.md",
    "apps_rg/runtime/exit/ibm_narrative_x3.py",
    "apps_rg/runtime/shadow/ibm_narrative_l6.py",
    "apps_rg/runtime/ibm_narrative_judge_preflight.py",
    "apps_rg/runtime/ibm_narrative_proof_accounting.py",
    "apps_rg/runtime/cli_section_execution_report.py",
    "tests/_apps_contract/test_ibm_narrative_runtime_slice.py",
    "tests/_apps_contract/test_unify_ibm_pa_compiled_prompt.py",
    "tests/_apps_contract/test_w2c_ibm_prompts.py",
]

ART_ROOT = REPO / "artifacts" / "apps_rg" / "runtime_proofs" / "ibm_narrative"


def main() -> Path:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    manifest = [
        f"Built: {datetime.now(UTC).isoformat()}Z",
        "",
        "Prefixes:",
        "  ibm_narrative_bundle/source/  — repo paths as listed below",
        "  ibm_narrative_bundle/artifacts/runtime_proofs/ibm_narrative/  — local runtime proof runs",
        "",
        "Source manifest:",
        *[f"  {rel}" for rel in SOURCE_REL],
    ]
    skipped: list[str] = []
    with zipfile.ZipFile(OUT, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("ibm_narrative_bundle/README.txt", "\n".join(manifest) + "\n")
        for rel in SOURCE_REL:
            p = REPO / rel
            if not p.is_file():
                skipped.append(rel)
                continue
            arc = f"ibm_narrative_bundle/source/{Path(rel).as_posix()}"
            zf.write(p, arcname=arc)
        if ART_ROOT.is_dir():
            for p in ART_ROOT.rglob("*"):
                if not p.is_file():
                    continue
                if "__pycache__" in p.parts:
                    continue
                arc = "ibm_narrative_bundle/artifacts/runtime_proofs/ibm_narrative/" + p.relative_to(
                    ART_ROOT
                ).as_posix()
                zf.write(p, arcname=arc)
        else:
            zf.writestr(
                "ibm_narrative_bundle/artifacts/MISSING_ibm_narrative_runtime_proofs.txt",
                "artifacts/apps_rg/runtime_proofs/ibm_narrative directory not present\n",
            )
        if skipped:
            zf.writestr(
                "ibm_narrative_bundle/SKIPPED_MISSING_SOURCE.txt",
                "\n".join(skipped) + "\n",
            )
    print(OUT.resolve())
    print(f"size_mb={OUT.stat().st_size / (1024 * 1024):.2f}")
    if skipped:
        print("skipped:", skipped)
    return OUT


if __name__ == "__main__":
    main()
