"""Narrow live adapter for apps_rg.

The snapshot fixtures expose normalized app output. The live adapter must do
the same: preflight the runtime inputs and path budget, then translate product
artifacts back into the eval snapshot contract.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from apps_eval.contracts import AppOutputSnapshot

_REPO_ROOT = Path(__file__).resolve().parents[2]
_DEFAULT_BRIEF = _REPO_ROOT / "apps_rg" / "config" / "default_targeting_briefing.txt"
_DEFAULT_RESUME = _REPO_ROOT / "apps_rg" / "resume" / "base" / "amit_ayer_base_resume_v1.json"
_MAX_WINDOWS_PATH = 240
_LONGEST_EXPECTED_LANE_REL = Path(
    "modular_r4/sections/insurtech_narrative/real/"
    "insurtech_narrative_99999999_999999/section_repair_ledger.json"
)

_X3_CANONICAL = {
    "X3A": "X3A_DENY",
    "X3B": "X3B_ESCALATE_HITL",
    "X3C": "X3C_COMMIT_REQUEST_TO_UWG",
    "X3D": "X3D_ALLOW_FINISH",
    "X3E": "X3E_SAFE_ABSTAIN",
}


def _as_text(value: Any) -> str:
    return str(value or "").strip()


def _json_object(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, TypeError):
        return {}
    return data if isinstance(data, dict) else {}


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _path_budget_errors(artifact_dir: Path) -> list[str]:
    worst = (artifact_dir / _LONGEST_EXPECTED_LANE_REL).resolve()
    n_chars = len(str(worst))
    if n_chars <= _MAX_WINDOWS_PATH:
        return []
    return [
        (
            f"windows_path_budget_exceeded: estimated longest live apps_rg path "
            f"is {n_chars} chars, limit {_MAX_WINDOWS_PATH}: {worst}"
        )
    ]


def _resolve_live_inputs(payload: dict[str, Any], artifact_dir: Path) -> tuple[dict[str, str], list[str]]:
    resolved = {
        "target_company": _as_text(payload.get("target_company")),
        "target_role": _as_text(payload.get("target_role")),
        "target_level": _as_text(payload.get("target_level")),
        "jd": _as_text(payload.get("jd")),
        "manual_brief": _as_text(payload.get("manual_brief")),
        "resume_path": _as_text(payload.get("resume_path")),
        "generation_mode": _as_text(payload.get("generation_mode")) or "strategic_tailor",
        "artifact_dir": str(artifact_dir),
    }
    if not resolved["manual_brief"] and _DEFAULT_BRIEF.is_file():
        resolved["manual_brief"] = str(_DEFAULT_BRIEF)
    if not resolved["resume_path"] and _DEFAULT_RESUME.is_file():
        resolved["resume_path"] = str(_DEFAULT_RESUME)

    missing = [
        key
        for key in ("target_company", "target_role", "jd", "manual_brief", "resume_path", "artifact_dir")
        if not resolved[key]
    ]
    errors = [f"missing_required_input:{key}" for key in missing]
    errors.extend(_path_budget_errors(artifact_dir))
    return resolved, errors


def _preflight_failure_snapshot(
    *,
    scenario_id: str,
    artifact_dir: Path,
    resolved: dict[str, str],
    errors: list[str],
) -> AppOutputSnapshot:
    preflight = {
        "status": "failed",
        "errors": list(errors),
        "resolved_inputs": {
            key: value
            for key, value in resolved.items()
            if key not in {"manual_brief", "resume_path"}
        },
        "manual_brief_resolved": bool(resolved.get("manual_brief")),
        "resume_path_resolved": bool(resolved.get("resume_path")),
    }
    if not any(err.startswith("windows_path_budget_exceeded") for err in errors):
        _write_json(artifact_dir / "apps_rg_live_preflight.json", preflight)
    return AppOutputSnapshot(
        app_id="apps_rg",
        scenario_id=scenario_id,
        x3_disposition="PRECHECK_FAILED",
        output={"preflight": preflight},
        artifacts=["apps_rg_live_preflight.json"] if (artifact_dir / "apps_rg_live_preflight.json").is_file() else [],
        provenance={
            "entrypoint": "apps_eval.adapters.apps_rg:run_apps_rg_live",
            "preflight": "failed",
        },
        side_effects={"product_state_mutated": False, "writes": []},
    )


def _read_receipt_x3(artifact_dir: Path) -> str:
    receipt = _json_object(artifact_dir / "x3_disposition_receipt.json")
    payload = receipt.get("payload") if isinstance(receipt.get("payload"), dict) else receipt
    return _as_text(payload.get("disposition") or payload.get("x3_code"))


def _canonical_x3(raw: str) -> str:
    value = _as_text(raw)
    return _X3_CANONICAL.get(value, value)


def _result_x3(result: dict[str, Any], artifact_dir: Path) -> str:
    raw = (
        _as_text(result.get("x3_disposition"))
        or _as_text(result.get("x3_code"))
        or _read_receipt_x3(artifact_dir)
        or _as_text(result.get("exit_status"))
        or "UNKNOWN"
    )
    return _canonical_x3(raw)


def _generated_resume_path(artifact_dir: Path) -> Path | None:
    candidates = [
        artifact_dir / "outputs" / "generated_resume.json",
        artifact_dir / "modular_r4" / "outputs" / "generated_resume.json",
        artifact_dir / "modular_r4" / "outputs" / "final_resume.json",
    ]
    for path in candidates:
        if path.is_file():
            return path
    return None


def _stringify_section(value: Any) -> str:
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, dict):
        if isinstance(value.get("text"), str):
            return value["text"].strip()
        return " ".join(_stringify_section(v) for v in value.values()).strip()
    if isinstance(value, list):
        return " ".join(_stringify_section(v) for v in value).strip()
    return _as_text(value)


def _normalize_sections(generated_resume: dict[str, Any]) -> dict[str, str]:
    raw_sections = generated_resume.get("sections")
    sections = raw_sections if isinstance(raw_sections, dict) else {}
    executive_summary = _stringify_section(
        sections.get("executive_summary")
        or sections.get("summary")
        or generated_resume.get("executive_summary")
        or generated_resume.get("summary")
    )
    experience = _stringify_section(sections.get("experience") or generated_resume.get("experience"))
    skills = _stringify_section(sections.get("skills") or generated_resume.get("skills"))
    normalized = {
        "executive_summary": executive_summary,
        "experience": experience,
        "skills": skills,
    }
    return {key: value for key, value in normalized.items() if value}


def _collect_source_ids(value: Any) -> list[str]:
    refs: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            if key in {"source_id", "source_ref", "evidence_ref"} and isinstance(child, str) and child.strip():
                refs.append(child.strip())
            elif key in {"source_ids", "source_refs", "evidence_refs"} and isinstance(child, list):
                refs.extend(str(item).strip() for item in child if str(item).strip())
            else:
                refs.extend(_collect_source_ids(child))
    elif isinstance(value, list):
        for child in value:
            refs.extend(_collect_source_ids(child))
    return refs


def _claims_from_resume(generated_resume: dict[str, Any]) -> list[dict[str, Any]]:
    refs = sorted(set(_collect_source_ids(generated_resume)))
    return [
        {
            "id": f"apps_rg_live_claim_{idx + 1}",
            "source_ids": [ref],
            "support_status": "UNKNOWN",
            "text": ref,
        }
        for idx, ref in enumerate(refs)
    ]


def _artifact_names(artifact_dir: Path) -> list[str]:
    names: set[str] = set()
    if (artifact_dir / "outputs" / "resume.md").is_file() or (artifact_dir / "resume.md").is_file():
        names.add("resume.md")
    if _generated_resume_path(artifact_dir) is not None:
        names.add("generated_resume.json")
    if (artifact_dir / "outputs" / "resume.docx").is_file():
        names.add("resume.docx")
    return sorted(names)


def _normalize_live_snapshot(
    *,
    scenario_id: str,
    result: dict[str, Any],
    artifact_dir: Path,
    preflight: dict[str, Any],
) -> AppOutputSnapshot:
    resume_path = _generated_resume_path(artifact_dir)
    generated_resume = _json_object(resume_path) if resume_path is not None else {}
    sections = _normalize_sections(generated_resume) if generated_resume else {}
    claims = _claims_from_resume(generated_resume)
    evidence_refs = sorted({ref for claim in claims for ref in claim.get("source_ids", [])})
    output: dict[str, Any] = {
        "runtime": {
            "exit_status": _as_text(result.get("exit_status")),
            "execution_status": _as_text(result.get("execution_status")),
            "outcome_authorized": bool(result.get("outcome_authorized", False)),
            "fault": _as_text(result.get("fault")),
        }
    }
    if sections:
        output["sections"] = sections
    return AppOutputSnapshot(
        app_id="apps_rg",
        scenario_id=scenario_id,
        x3_disposition=_result_x3(result, artifact_dir),
        output=output,
        claims=claims,
        artifacts=_artifact_names(artifact_dir),
        provenance={
            "entrypoint": "agentic_core.runtime.entry.apps_rg_dispatch:dispatch_apps_rg_run",
            "preflight": "passed",
            "preflight_ref": "apps_rg_live_preflight.json",
            "generated_resume_ref": str(resume_path.relative_to(artifact_dir)).replace("\\", "/") if resume_path else "",
            "evidence_refs": evidence_refs,
            "resolved_inputs": preflight.get("resolved_inputs", {}),
            "side_effect_receipt_status": "MISSING",
        },
        side_effects={"product_state_mutated": "UNKNOWN", "writes": [], "receipt_status": "MISSING"},
    )


def run_apps_rg_live(scenario_id: str, payload: dict[str, Any], artifact_dir: Path) -> AppOutputSnapshot:
    from agentic_core.runtime.entry.apps_rg_dispatch import dispatch_apps_rg_run

    resolved, errors = _resolve_live_inputs(payload, artifact_dir)
    if errors:
        return _preflight_failure_snapshot(
            scenario_id=scenario_id,
            artifact_dir=artifact_dir,
            resolved=resolved,
            errors=errors,
        )
    preflight = {
        "status": "passed",
        "errors": [],
        "resolved_inputs": {
            "target_company": resolved["target_company"],
            "target_role": resolved["target_role"],
            "target_level": resolved["target_level"],
            "jd_present": bool(resolved["jd"]),
            "manual_brief_ref": resolved["manual_brief"],
            "resume_path_ref": resolved["resume_path"],
            "generation_mode": resolved["generation_mode"],
            "artifact_dir": resolved["artifact_dir"],
        },
    }
    _write_json(artifact_dir / "apps_rg_live_preflight.json", preflight)
    result = dispatch_apps_rg_run(
        target_company=resolved["target_company"],
        target_role=resolved["target_role"],
        target_level=resolved["target_level"],
        jd=resolved["jd"],
        manual_brief=resolved["manual_brief"],
        resume_path=resolved["resume_path"],
        generation_mode=resolved["generation_mode"],
        artifact_dir=resolved["artifact_dir"],
    )
    return _normalize_live_snapshot(
        scenario_id=scenario_id,
        result=result,
        artifact_dir=artifact_dir,
        preflight=preflight,
    )
