"""W0-W8 agentic_core leakage audit scanner.

Run: python tools/analysis/run_leakage_audit.py
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

NEW_CORE_FILES = [
    "agentic_core/runtime/gates/gate_evaluators.py",
    "agentic_core/runtime/gates/gate_profile_resolver.py",
    "agentic_core/runtime/gates/gate_mesh.py",
    "agentic_core/runtime/gates/gate_types.py",
    "agentic_core/runtime/exit/exit_gate_harness.py",
    "agentic_core/runtime/exit/exit_disposition.py",
    "agentic_core/L3_orchestration/managed_workflow_runner.py",
    "agentic_core/L3_orchestration/section_merge_engine.py",
    "agentic_core/L3_orchestration/workflow_registry.py",
    "agentic_core/L2_execution/ensemble_lane.py",
    "agentic_core/L2_execution/candidate_gate_runner.py",
    "agentic_core/L2_execution/judge_jury_runner.py",
    "agentic_core/prompt_governance/managed_workflow_pa_resolver.py",
    "agentic_core/runtime/contracts/sealed_workflow_types.py",
    "agentic_core/runtime/contracts/l3_to_l2_step_contract.py",
    "agentic_core/runtime/contracts/managed_prompt_artifact.py",
    "agentic_core/runtime/contracts/route_contract.py",
    "agentic_core/runtime/contracts/ensemble_types.py",
    "agentic_core/runtime/contracts/judge_types.py",
]

LEAKAGE_PATTERNS = [
    ("apps_rg", "APP_STRING"),
    ("resume_generation", "APP_STRING"),
    ("header_block", "SECTION_NAME"),
    ("professional_summary", "SECTION_NAME"),
    ("skills_block", "SECTION_NAME"),
    ("experience_block", "SECTION_NAME"),
    ("education_block", "SECTION_NAME"),
    ("certifications_block", "SECTION_NAME"),
    ("selected_projects_block", "SECTION_NAME"),
    ("publications_block", "SECTION_NAME"),
    ("factual_grounding", "THRESHOLD_DIM"),
    ("role_alignment", "THRESHOLD_DIM"),
    ("ats_readability", "THRESHOLD_DIM"),
    ("no_fabrication", "THRESHOLD_DIM"),
    ("executive_positioning", "THRESHOLD_DIM"),
    ("format_compliance", "THRESHOLD_DIM"),
    ("route_registry", "PATH_REF"),
    ("workflow_manifest.resume_generation", "PATH_REF"),
    ("exit_profile.resume_generation", "PATH_REF"),
    ("runtime_gate_profile.resume_generation", "PATH_REF"),
    ("Qwen", "PROVIDER"),
    ("Anthropic", "PROVIDER"),
    ("vLLM", "PROVIDER"),
]


def is_comment_or_docstring(line: str) -> bool:
    s = line.strip()
    return s.startswith("#") or s.startswith('"""') or s.startswith("'''")


def scan() -> list[dict]:
    results = []
    for relpath in NEW_CORE_FILES:
        fp = ROOT / relpath
        if not fp.exists():
            continue
        lines = fp.read_text(encoding="utf-8", errors="ignore").splitlines()
        in_docstring = False
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            # track docstring blocks
            if '"""' in stripped or "'''" in stripped:
                in_docstring = not in_docstring
            if in_docstring or is_comment_or_docstring(line):
                continue
            for pat, category in LEAKAGE_PATTERNS:
                if pat.lower() in line.lower():
                    results.append({
                        "category": category,
                        "file": relpath,
                        "line": i,
                        "text": stripped[:120],
                        "pattern": pat,
                    })
                    break  # one hit per line
    return results


if __name__ == "__main__":
    hits = scan()
    out_path = ROOT / "artifacts/apps_rg/audit_leakage_scan.txt"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"{h['category']}|{h['file']}:{h['line']}|{h['pattern']}|{h['text']}" for h in hits]
    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"{len(hits)} hits written to {out_path}")
    # Group by category
    from collections import Counter
    cat_counts = Counter(h["category"] for h in hits)
    for cat, cnt in sorted(cat_counts.items()):
        print(f"  {cat}: {cnt}")
