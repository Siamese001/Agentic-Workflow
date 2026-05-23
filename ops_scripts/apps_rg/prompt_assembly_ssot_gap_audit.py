"""Audit apps_rg prompt_assembly SSOT gaps (BOM vs registry vs examples vs compile path).

Usage:
    python ops_scripts/apps_rg/prompt_assembly_ssot_gap_audit.py
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
PA = ROOT / "apps_rg" / "prompt_assembly"
BOM = PA / "prompt_bom.yaml"
REGISTRY = PA / "prompt_registry.yaml"
EXAMPLES = PA / "examples"

W9_LANES = (
    ("executive_summary", "executive_summary.generate_scratch_v1", "executive_summary_pa"),
    ("headline", "headline_tailor_v1", "headline_pa"),
    ("competencies", "competency_selector_v2", "competencies_pa"),
    ("unify_bullets", "unify_bullet_tailor_v1", "unify_bullets_pa"),
    ("unify_narrative", "unify_position_narrative_v1", "unify_narrative_pa"),
    ("ibm_bullets", "ibm_bullet_tailor_v1", "ibm_bullets_pa"),
    ("ibm_narrative", "ibm_position_narrative_v1", "ibm_narrative_pa"),
)

EXAMPLE_FILES_BY_SECTION = {
    "executive_summary": "executive_summary_examples.yaml",
    "competencies": "competencies_examples.yaml",
    "unify": "unify_examples.yaml",
}


def _load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _template_e0_has_positive_ids(template_path: Path) -> list[str]:
    if not template_path.is_file():
        return []
    raw = template_path.read_text(encoding="utf-8")
    slot = re.search(r"^\s+E0:\s*\|(.*)(?=^\s+[A-Z0-9]+:\s*\||\Z)", raw, re.M | re.S)
    if not slot:
        return []
    body = slot.group(1)
    return re.findall(r'<positive_example id="([^"]+)"', body)


def _examples_yaml_ids(path: Path) -> list[str]:
    if not path.is_file():
        return []
    data = _load(path)
    rows = data.get("examples") or []
    return [str(r.get("id")) for r in rows if isinstance(r, dict) and r.get("id")]


def _pa_uses_slots_get_e0(module_name: str) -> bool:
    pa_path = ROOT / "apps_rg" / "runtime" / "sections" / f"{module_name}.py"
    if not pa_path.is_file():
        return False
    text = pa_path.read_text(encoding="utf-8")
    return 'e0_examples=slots.get("E0")' in text or 'e0_examples=slots["E0"]' in text


def main() -> int:
    bom = _load(BOM)
    reg = _load(REGISTRY)
    templates = reg.get("templates") or {}

    gaps: list[dict] = []
    lanes: list[dict] = []

    bom_e0_required = "E0" in (bom.get("required_slots") or [])
    exec_auth = bom.get("executive_summary_example_authority") or {}

    for section, tid, pa_mod in W9_LANES:
        tmeta = templates.get(tid) or {}
        tpath = PA / str(tmeta.get("path") or "")
        reg_e0_optional = "E0" in (tmeta.get("optional_slots") or [])
        reg_e0_required = "E0" in (tmeta.get("required_slots") or [])
        inline_ids = _template_e0_has_positive_ids(tpath)
        ex_file = EXAMPLE_FILES_BY_SECTION.get(section) or EXAMPLE_FILES_BY_SECTION.get(
            section.split("_")[0], ""
        )
        if section.startswith("unify") or section.startswith("ibm"):
            ex_file = EXAMPLE_FILES_BY_SECTION.get("unify" if "unify" in section else "")
        if section == "competencies":
            ex_file = EXAMPLE_FILES_BY_SECTION["competencies"]
        if section == "executive_summary":
            ex_file = EXAMPLE_FILES_BY_SECTION["executive_summary"]
        if section in ("headline", "ibm_bullets", "ibm_narrative", "unify_bullets", "unify_narrative"):
            ex_file = {
                "headline": "",
                "ibm_bullets": "",
                "ibm_narrative": "",
                "unify_bullets": "unify_examples.yaml",
                "unify_narrative": "unify_examples.yaml",
            }.get(section, ex_file)

        ex_path = EXAMPLES / ex_file if ex_file else None
        yaml_ids = _examples_yaml_ids(ex_path) if ex_path else []
        wired_loader = False
        if section == "executive_summary":
            wired_loader = "load_executive_summary_example_after" in (
                ROOT / "apps_rg" / "runtime" / "sections" / "executive_summary_pa.py"
            ).read_text(encoding="utf-8")
            wired_compile = 'e0_examples=slots.get("E0")' in (
                ROOT / "apps_rg" / "runtime" / "sections" / "executive_summary_pa.py"
            ).read_text(encoding="utf-8")
        else:
            wired_compile = _pa_uses_slots_get_e0(pa_mod)

        drift = bool(ex_path and yaml_ids and inline_ids)
        overlap = sorted(set(inline_ids) & set(yaml_ids)) if yaml_ids else []
        pa_path = ROOT / "apps_rg" / "runtime" / "sections" / f"{pa_mod}.py"
        pa_text = pa_path.read_text(encoding="utf-8") if pa_path.is_file() else ""
        wired = "e0_examples=resolve_e0_for_section" in pa_text
        row = {
            "section": section,
            "template_id": tid,
            "pa_module": pa_mod,
            "template_path": str(tpath.relative_to(ROOT)).replace("\\", "/"),
            "registry_e0_required": reg_e0_required,
            "registry_e0_optional": reg_e0_optional,
            "bom_e0_globally_required": bom_e0_required,
            "examples_file": str(ex_path.relative_to(ROOT)).replace("\\", "/") if ex_path else None,
            "inline_positive_example_ids": inline_ids,
            "examples_yaml_ids_count": len(yaml_ids),
            "shared_ids_inline_and_yaml": overlap,
            "compile_path": "resolve_e0_for_section (e0_examples.py)" if wired else "slots.get(E0) from template only",
            "examples_wired_at_compile": wired and bool(ex_path),
            "dual_authority_risk": bool(ex_path and yaml_ids and not wired),
            "wired_loader_exists_exec_only": wired_loader if section == "executive_summary" else None,
        }
        lanes.append(row)
        if row["dual_authority_risk"]:
            gaps.append(
                {
                    "gap_id": f"PA-E0-DRIFT-{section.upper()}",
                    "severity": "P0" if section == "executive_summary" else "P1",
                    "summary": (
                        f"{section}: examples YAML exists but compile does not call resolve_e0_for_section"
                    ),
                    "section": section,
                }
            )

    examples_backed_optional = [
        l["section"]
        for l in lanes
        if l.get("examples_file") and l.get("registry_e0_optional")
    ]
    if examples_backed_optional:
        gaps.append(
            {
                "gap_id": "PA-BOM-REGISTRY-E0",
                "severity": "P2",
                "summary": (
                    "BOM requires E0 globally but registry marks E0 optional for lanes with "
                    f"examples YAML: {examples_backed_optional}"
                ),
            }
        )

    docs_stale = [
        "apps_rg/prompt_assembly/rg_prompt_profile.yaml",
        "apps_rg/prompt_assembly/rg_style_profile.yaml",
        "apps_rg/prompt_assembly/rg_evidence_profile.yaml",
    ]
    for rel in docs_stale:
        if not (ROOT / rel).is_file():
            gaps.append(
                {
                    "gap_id": "PA-DOCS-STALE-PATH",
                    "severity": "P3",
                    "summary": f"Documented path missing on disk: {rel}",
                }
            )

    dual_contracts = (
        (PA / "section_contracts").is_dir() and (PA / "section_prompt_contracts").is_dir()
    )
    if dual_contracts:
        gaps.append(
            {
                "gap_id": "PA-DUAL-CONTRACT-TREES",
                "severity": "P2",
                "summary": "section_contracts/ (E3) and section_prompt_contracts/ (W9 runtime) coexist",
            }
        )

    out = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "bom_id": bom.get("bom_id"),
        "executive_summary_example_authority": exec_auth,
        "w9_lanes": lanes,
        "gaps": gaps,
        "gap_count": len(gaps),
        "p0_count": sum(1 for g in gaps if g.get("severity") == "P0"),
    }
    artifact = ROOT / "artifacts" / "apps_rg" / "plans" / "prompt_assembly_ssot_gap_audit.json"
    artifact.parent.mkdir(parents=True, exist_ok=True)
    artifact.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps({"artifact": str(artifact), "gap_count": out["gap_count"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
