"""Per-section forensic RCA artifacts for failed apps_rg E2E runs."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SECTION_FAILURE_FORENSICS_DIR = "section_failure_forensics"
E2E_SECTION_FORENSICS_GATE_ID = "E2E_FAIL_WITHOUT_SECTION_FORENSICS"
SECTION_FAILURE_FORENSICS_SCHEMA_VERSION = "apps_rg.section_failure_forensics.v1"

FAILURE_TYPES = frozenset(
    {
        "independent_failure",
        "upstream_cascade",
        "aggregation_downstream",
        "mandatory_output_authorization_block",
    }
)

REQUIRED_RCA_FIELDS = (
    "section_id",
    "failure_type",
    "failed_gate_ids",
    "current_output",
    "last_successful_output",
    "input_hash_comparison",
    "selected_fact_plan_comparison",
    "provider_request_hash_comparison",
    "retry_attempts",
    "retry_outputs",
    "repair_ledger",
    "final_materialized_output",
    "exact_code_surface",
    "why_it_passed_before",
    "why_it_failed_now",
    "required_fix",
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def _load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, TypeError):
        return {}
    return raw if isinstance(raw, dict) else {}


def _load_text(path: Path, *, max_chars: int = 12000) -> str:
    if not path.is_file():
        return ""
    try:
        return path.read_text(encoding="utf-8")[:max_chars]
    except OSError:
        return ""


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _stable_hash(value: Any) -> str:
    try:
        text = json.dumps(value, sort_keys=True, ensure_ascii=False, default=str)
    except TypeError:
        text = str(value)
    return _sha256_text(text)


def _repo_rel(path: Path, repo_root: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def _lane_dir(section: dict[str, Any], repo_root: Path) -> Path | None:
    raw = str(section.get("lane_dir") or "").strip()
    if not raw:
        return None
    path = Path(raw)
    if not path.is_absolute():
        path = repo_root / path
    return path if path.exists() else path


def _display_from_l2(path: Path) -> str:
    l2 = _load_json(path)
    for key in (
        "resume_display_text",
        "headline_line",
        "narrative_sentence",
        "summary_text",
        "display_text",
    ):
        text = str(l2.get(key) or "").strip()
        if text:
            return text
    bullets = l2.get("bullets")
    if isinstance(bullets, list):
        lines = [
            str(row.get("bullet_text") or row.get("text") or "").strip()
            for row in bullets
            if isinstance(row, dict)
        ]
        lines = [line for line in lines if line]
        if lines:
            return "\n".join(f"- {line}" for line in lines)
    competencies = l2.get("competencies")
    if isinstance(competencies, list):
        lines = [
            str(row.get("label") or row.get("category") or "").strip()
            for row in competencies
            if isinstance(row, dict)
        ]
        lines = [line for line in lines if line]
        if lines:
            return "\n".join(lines)
    return ""


def _final_materialized_output(lane_dir: Path | None, section: dict[str, Any]) -> dict[str, Any]:
    if lane_dir is None:
        return {
            "present": False,
            "ref": "",
            "text": "",
            "sha256": "",
            "source": "missing_lane_dir",
        }
    candidates: list[Path] = []
    display_abs = str(section.get("display_txt_path") or "").strip()
    if display_abs:
        candidates.append(Path(display_abs))
    candidates.extend(
        [
            lane_dir / "command_output.txt",
            lane_dir / "resume_display_text.txt",
            lane_dir / f"{section.get('section')}_output.txt",
            lane_dir / "output.txt",
        ]
    )
    candidates.extend(sorted(lane_dir.glob("*_output.txt")))
    seen: set[Path] = set()
    for candidate in candidates:
        try:
            resolved = candidate.resolve()
        except OSError:
            resolved = candidate
        if resolved in seen:
            continue
        seen.add(resolved)
        text = _load_text(candidate).strip()
        if text:
            return {
                "present": True,
                "ref": candidate.name,
                "path": str(candidate),
                "text": text,
                "sha256": _sha256_text(text),
                "source": "display_text_file",
            }
    text = _display_from_l2(lane_dir / "l2_output.json").strip()
    if text:
        return {
            "present": True,
            "ref": "l2_output.json",
            "path": str(lane_dir / "l2_output.json"),
            "text": text,
            "sha256": _sha256_text(text),
            "source": "l2_output",
        }
    return {"present": False, "ref": "", "text": "", "sha256": "", "source": "not_found"}


def _known_artifact(path: Path) -> dict[str, Any]:
    doc = _load_json(path)
    if doc:
        return {"ref": path.name, "path": str(path), "json": doc}
    text = _load_text(path)
    if text:
        return {"ref": path.name, "path": str(path), "text": text}
    return {"ref": path.name, "path": str(path), "missing": True}


def _collect_artifacts(lane_dir: Path | None, names: tuple[str, ...]) -> list[dict[str, Any]]:
    if lane_dir is None:
        return []
    out: list[dict[str, Any]] = []
    for name in names:
        path = lane_dir / name
        if path.is_file():
            out.append(_known_artifact(path))
    return out


def _collect_retry_outputs(lane_dir: Path | None) -> list[dict[str, Any]]:
    if lane_dir is None or not lane_dir.is_dir():
        return []
    names = (
        "employment_bullet_regen.json",
        "competencies_graph_pool_regen.json",
        "judge_remediation_cycles.json",
        "executive_summary_regen_receipt.json",
        "retry_receipt.json",
        "raw_output.txt",
        "raw_model_output.txt",
        "raw_model_output_original.txt",
        "parsed_output.json",
    )
    out = _collect_artifacts(lane_dir, names)
    for path in sorted(lane_dir.glob("*regen*.json")) + sorted(lane_dir.glob("*retry*.json")):
        if not any(str(row.get("path")) == str(path) for row in out):
            out.append(_known_artifact(path))
    return out


def _collect_repair_ledger(lane_dir: Path | None) -> dict[str, Any]:
    rows = _collect_artifacts(
        lane_dir,
        (
            "section_repair_ledger.json",
            "repair_receipt.json",
            "executive_summary_repair_ledger.json",
            "judge_remediation_cycles.json",
        ),
    )
    return {"present": bool(rows), "artifacts": rows}


def _failed_gate_ids(section: dict[str, Any]) -> list[str]:
    out: list[str] = []
    for gate in section.get("failed_gates") or []:
        if isinstance(gate, dict):
            gid = str(gate.get("gate_id") or gate.get("id") or "").strip()
            if gid:
                out.append(gid)
        elif str(gate).strip():
            out.append(str(gate).strip())
    return out


def _section_failure_type(section: dict[str, Any], result: dict[str, Any] | None) -> str:
    section_id = str(section.get("section") or "")
    bucket = str(section.get("status_bucket") or "")
    x3 = str(section.get("x3_code") or "")
    if section_id in {"mandatory_outputs", "whole_run"}:
        return "mandatory_output_authorization_block"
    if section_id == "final_resume_aggregation":
        return "aggregation_downstream"
    if bucket in {"pre_run_blocked", "not_run"} or x3.startswith("PRE_RUN:"):
        return "upstream_cascade"
    fault = str((result or {}).get("fault") or "")
    if fault == E2E_SECTION_FORENSICS_GATE_ID:
        return "mandatory_output_authorization_block"
    return "independent_failure"


def _scenario_identity(run_root: Path) -> dict[str, Any]:
    ingress = _load_json(run_root / "ingress_raw.json")
    inventory = _load_json(run_root / "modular_r4" / "phase1_lane_inventory.json")
    targeting = inventory.get("lane_argv_targeting")
    if not isinstance(targeting, dict):
        targeting = {}
    route = _load_json(run_root / "spine_run_manifest.json").get("route_decision")
    if not isinstance(route, dict):
        route = {}
    identity = {
        "target_company": str(
            ingress.get("target_company")
            or targeting.get("target_company")
            or route.get("target_company")
            or ""
        ).strip(),
        "target_role": str(
            ingress.get("target_role")
            or targeting.get("target_title")
            or targeting.get("target_role")
            or route.get("target_role")
            or ""
        ).strip(),
        "manual_brief": str(
            ingress.get("manual_brief")
            or targeting.get("briefing_ref_used")
            or route.get("delegated_briefing_path")
            or ""
        ).strip(),
        "jd": str(
            ingress.get("jd")
            or ingress.get("job_description_ref")
            or ingress.get("job_description_text")
            or ""
        ).strip(),
        "generation_mode": str(ingress.get("generation_mode") or "").strip(),
    }
    return {
        **identity,
        "scenario_hash": _stable_hash({k: v.lower() for k, v in identity.items()}),
    }


def _is_successful_run(run_dir: Path) -> bool:
    mandatory = _load_json(run_dir / "APPS_RG_MANDATORY_RUN_OUTPUT.json")
    summary = mandatory.get("result_summary") if isinstance(mandatory.get("result_summary"), dict) else {}
    if summary.get("outcome_authorized") is True:
        return True
    final_output = mandatory.get("final_resume_output") if isinstance(mandatory.get("final_resume_output"), dict) else {}
    if final_output.get("status") == "PASS" and str(summary.get("exit_status") or "") == "success":
        return True
    manifest = _load_json(run_dir / "spine_run_manifest.json")
    return manifest.get("outcome_authorized") is True or manifest.get("exit_status") == "success"


def _baseline_confidence(run_dir: Path) -> str:
    candidates = (
        _load_json(run_dir / "APPS_RG_MANDATORY_RUN_OUTPUT.json"),
        _load_json(run_dir / "git_state.json"),
        _load_json(run_dir / "worktree_status.json"),
        _load_json(run_dir / "repo_state.json"),
        _load_json(run_dir / "run_manifest.json"),
    )
    saw_clean = False
    for doc in candidates:
        if not doc:
            continue
        text = json.dumps(doc, sort_keys=True, default=str).lower()
        if "dirty" in text and "true" in text:
            return "dirty"
        for key in (
            "git_dirty",
            "worktree_dirty",
            "dirty_worktree",
            "has_uncommitted_changes",
        ):
            if doc.get(key) is True:
                return "dirty"
            if doc.get(key) is False:
                saw_clean = True
        if doc.get("worktree_clean") is True or doc.get("git_clean") is True:
            saw_clean = True
    return "clean" if saw_clean else "unknown"


def _same_scenario(a: dict[str, Any], b: dict[str, Any]) -> bool:
    if a.get("scenario_hash") == b.get("scenario_hash"):
        return True
    company_a = str(a.get("target_company") or "").strip().lower()
    role_a = str(a.get("target_role") or "").strip().lower()
    company_b = str(b.get("target_company") or "").strip().lower()
    role_b = str(b.get("target_role") or "").strip().lower()
    return bool(company_a and role_a and company_a == company_b and role_a == role_b)


def _find_last_successful_same_scenario(run_root: Path) -> dict[str, Any]:
    current = _scenario_identity(run_root)
    parent = run_root.parent
    if not parent.is_dir():
        return {
            "found": False,
            "baseline_confidence": "not_found",
            "scenario": current,
            "run_dir": "",
        }
    candidates = []
    for child in parent.iterdir():
        if child.resolve() == run_root.resolve() or not child.is_dir():
            continue
        if not _is_successful_run(child):
            continue
        identity = _scenario_identity(child)
        if not _same_scenario(current, identity):
            continue
        try:
            mtime = child.stat().st_mtime
        except OSError:
            mtime = 0.0
        candidates.append((mtime, child, identity))
    if not candidates:
        return {
            "found": False,
            "baseline_confidence": "not_found",
            "scenario": current,
            "run_dir": "",
        }
    _mtime, baseline, identity = sorted(candidates, key=lambda row: row[0], reverse=True)[0]
    return {
        "found": True,
        "baseline_confidence": _baseline_confidence(baseline),
        "scenario": current,
        "baseline_scenario": identity,
        "run_dir": str(baseline),
    }


def _baseline_lane_dir(
    baseline: dict[str, Any],
    section: dict[str, Any],
    repo_root: Path,
) -> Path | None:
    raw = str(baseline.get("run_dir") or "").strip()
    if not raw:
        return None
    run_dir = Path(raw)
    section_id = str(section.get("section") or "")
    candidates = [
        run_dir / "lanes" / section_id,
        run_dir / "modular_r4" / "sections" / section_id,
    ]
    if section_id == "final_resume_aggregation":
        candidates.append(run_dir / "modular_r4" / "final_resume_assembly")
    for candidate in candidates:
        if candidate.is_dir():
            return candidate
    mandatory = _load_json(run_dir / "APPS_RG_MANDATORY_RUN_OUTPUT.json")
    for row in mandatory.get("sections") or []:
        if not isinstance(row, dict) or row.get("section") != section_id:
            continue
        lane_dir = str(row.get("lane_dir") or "")
        if not lane_dir:
            continue
        path = Path(lane_dir)
        if not path.is_absolute():
            path = repo_root / path
        return path
    return None


def _comparison(current_dir: Path | None, baseline_dir: Path | None, filename: str) -> dict[str, Any]:
    current = _load_json(current_dir / filename) if current_dir is not None else {}
    baseline = _load_json(baseline_dir / filename) if baseline_dir is not None else {}
    current_hash = _stable_hash(current) if current else ""
    baseline_hash = _stable_hash(baseline) if baseline else ""
    return {
        "artifact": filename,
        "current_present": bool(current),
        "baseline_present": bool(baseline),
        "current_hash": current_hash,
        "baseline_hash": baseline_hash,
        "match": bool(current_hash and baseline_hash and current_hash == baseline_hash),
    }


def _input_hash_comparison(run_root: Path, baseline: dict[str, Any]) -> dict[str, Any]:
    current = _scenario_identity(run_root)
    baseline_scenario = baseline.get("baseline_scenario") if isinstance(baseline.get("baseline_scenario"), dict) else {}
    return {
        "current_scenario_hash": current.get("scenario_hash", ""),
        "baseline_scenario_hash": baseline_scenario.get("scenario_hash", ""),
        "match": bool(
            baseline_scenario
            and current.get("scenario_hash") == baseline_scenario.get("scenario_hash")
        ),
        "current": current,
        "baseline": baseline_scenario,
    }


def _exact_code_surface(
    section: dict[str, Any],
    lane_dir: Path | None,
    repo_root: Path,
) -> dict[str, Any]:
    section_id = str(section.get("section") or "")
    producer_files = ["apps_rg/runtime/section_failure_forensics.py"]
    if section_id == "executive_summary":
        producer_files.append("apps_rg/runtime/sections/executive_summary_lane.py")
    elif section_id == "headline":
        producer_files.append("apps_rg/runtime/sections/headline_lane.py")
    elif section_id == "final_resume_aggregation":
        producer_files.extend(
            [
                "apps_rg/runtime/internal/final_resume_assembler.py",
                "apps_rg/runtime/assembly/final_resume_x2.py",
            ]
        )
    elif section_id.endswith("_bullets") or section_id.endswith("_narrative"):
        producer_files.append("apps_rg/runtime/sections/role_episode_lane.py")
    elif section_id == "competencies":
        producer_files.append("apps_rg/runtime/sections/competencies_lane_execution.py")
    else:
        producer_files.append("apps_rg/runtime/mandatory_run_outputs.py")
    artifact_refs: list[str] = []
    if lane_dir is not None:
        for name in (
            "x2_gate_outputs.json",
            "x3_disposition.json",
            "l2_output.json",
            "selected_fact_plan.json",
            "provider_request.json",
            "integrated_lane_pre_run_failure.json",
        ):
            path = lane_dir / name
            if path.is_file():
                artifact_refs.append(_repo_rel(path, repo_root))
    return {
        "producer_files": sorted(set(producer_files)),
        "artifact_refs": artifact_refs,
        "lane_dir": str(lane_dir) if lane_dir is not None else "",
    }


def _why_passed_before(baseline: dict[str, Any], baseline_output: dict[str, Any]) -> str:
    confidence = str(baseline.get("baseline_confidence") or "not_found")
    if not baseline.get("found"):
        return "No prior successful same-scenario run was found, so this RCA cannot claim a clean passing baseline."
    if confidence == "dirty":
        return (
            "The latest successful same-scenario baseline existed but was dirty; treat it as behavioral "
            "evidence only, not a clean code baseline."
        )
    if bool(baseline_output.get("present")):
        return (
            "The prior same-scenario run produced a materialized output that was accepted by its run-level "
            "success contract."
        )
    return "The prior same-scenario run was marked successful, but this section's baseline output was not found."


def _why_failed_now(section: dict[str, Any], failure_type: str) -> str:
    failed = ", ".join(_failed_gate_ids(section))
    classification = str(section.get("failure_classification") or "").strip()
    x3 = str(section.get("x3_code") or "").strip()
    if failure_type == "upstream_cascade":
        return (
            "This section did not independently certify because an upstream dependency or pre-run "
            f"blocker prevented normal section authorization: {classification or x3}."
        )
    if failure_type == "aggregation_downstream":
        return (
            "Final aggregation was downstream of section certification and product-output gates; "
            f"it failed on {failed or classification or x3}."
        )
    if failure_type == "mandatory_output_authorization_block":
        return "Mandatory output authorization failed before the run could be treated as explainable."
    return f"The section's final materialized artifact did not pass {failed or classification or x3}."


def _required_fix(section: dict[str, Any], failure_type: str) -> list[str]:
    section_id = str(section.get("section") or "section")
    failed = ", ".join(_failed_gate_ids(section)) or str(section.get("x3_code") or "section gate")
    if failure_type == "upstream_cascade":
        return [
            f"Resolve the upstream blocker before dispatching `{section_id}`.",
            "Write the upstream dependency status into the section pre-run receipt.",
            "Keep the section blocked until its own X1-X3 inputs are present.",
        ]
    if failure_type == "aggregation_downstream":
        return [
            "Require final aggregation to consume only sections with accepted X3 evidence.",
            "Record the exact upstream section or product-output gate that blocked assembly.",
            "Rerun aggregation only after the failed section RCA artifacts are complete.",
        ]
    if failure_type == "mandatory_output_authorization_block":
        return [
            "Generate missing mandatory BCG, run-ledger, and forensic RCA artifacts before exit.",
            "Validate every required forensic RCA field before declaring the E2E failure explainable.",
            "Fail with E2E_FAIL_WITHOUT_SECTION_FORENSICS when any required RCA artifact is missing or incomplete.",
        ]
    return [
        f"Make `{section_id}` gate final displayed output, not intermediate provider output.",
        f"Bind the failed gate evidence (`{failed}`) to the producer/parser contract that emitted the artifact.",
        "Record retry and repair outputs in the lane ledger so repeated LLM variance is explainable.",
    ]


def _build_rca(
    *,
    run_root: Path,
    repo_root: Path,
    section: dict[str, Any],
    result: dict[str, Any] | None,
    baseline: dict[str, Any],
) -> dict[str, Any]:
    section_id = str(section.get("section") or "")
    lane = _lane_dir(section, repo_root)
    baseline_lane = _baseline_lane_dir(baseline, section, repo_root)
    current_output = _final_materialized_output(lane, section)
    baseline_output = _final_materialized_output(baseline_lane, section)
    failure_type = _section_failure_type(section, result)
    return {
        "schema_version": SECTION_FAILURE_FORENSICS_SCHEMA_VERSION,
        "generated_at_utc": _utc_now(),
        "section_id": section_id,
        "failure_type": failure_type,
        "failed_gate_ids": _failed_gate_ids(section),
        "current_output": current_output,
        "last_successful_output": {
            **baseline_output,
            "baseline_run_dir": str(baseline.get("run_dir") or ""),
            "baseline_found": bool(baseline.get("found")),
        },
        "input_hash_comparison": _input_hash_comparison(run_root, baseline),
        "selected_fact_plan_comparison": _comparison(
            lane, baseline_lane, "selected_fact_plan.json"
        ),
        "provider_request_hash_comparison": _comparison(
            lane, baseline_lane, "provider_request.json"
        ),
        "retry_attempts": _collect_artifacts(
            lane,
            (
                "employment_bullet_regen.json",
                "competencies_graph_pool_regen.json",
                "judge_remediation_cycles.json",
                "retry_receipt.json",
            ),
        ),
        "retry_outputs": _collect_retry_outputs(lane),
        "repair_ledger": _collect_repair_ledger(lane),
        "final_materialized_output": current_output,
        "exact_code_surface": _exact_code_surface(section, lane, repo_root),
        "why_it_passed_before": _why_passed_before(baseline, baseline_output),
        "why_it_failed_now": _why_failed_now(section, failure_type),
        "required_fix": _required_fix(section, failure_type),
        "baseline_confidence": str(baseline.get("baseline_confidence") or "not_found"),
        "baseline_run_dir": str(baseline.get("run_dir") or ""),
    }


def validate_section_failure_rca(doc: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for field in REQUIRED_RCA_FIELDS:
        if field not in doc:
            errors.append(f"missing:{field}")
            continue
        value = doc.get(field)
        if value is None:
            errors.append(f"null:{field}")
        elif isinstance(value, str) and not value.strip():
            errors.append(f"empty:{field}")
        elif isinstance(value, dict) and not value:
            errors.append(f"empty:{field}")
    if doc.get("failure_type") not in FAILURE_TYPES:
        errors.append("invalid:failure_type")
    required_fix = doc.get("required_fix")
    if not isinstance(required_fix, list) or not (3 <= len(required_fix) <= 5):
        errors.append("invalid:required_fix")
    code_surface = doc.get("exact_code_surface")
    if not isinstance(code_surface, dict) or not code_surface.get("producer_files"):
        errors.append("invalid:exact_code_surface")
    return errors


def _render_rca_md(doc: dict[str, Any]) -> str:
    fixes = doc.get("required_fix") if isinstance(doc.get("required_fix"), list) else []
    lines = [
        f"# Section Failure Forensics - {doc.get('section_id')}",
        "",
        f"- failure_type: `{doc.get('failure_type')}`",
        f"- baseline_confidence: `{doc.get('baseline_confidence')}`",
        f"- failed_gate_ids: `{', '.join(str(x) for x in doc.get('failed_gate_ids') or []) or '-'}`",
        "",
        "## Why It Passed Before",
        "",
        str(doc.get("why_it_passed_before") or ""),
        "",
        "## Why It Failed Now",
        "",
        str(doc.get("why_it_failed_now") or ""),
        "",
        "## Required Fix",
        "",
    ]
    lines.extend(f"- {item}" for item in fixes)
    lines.extend(
        [
            "",
            "## Artifact Hash Comparisons",
            "",
            f"- input_hash_comparison: `{doc.get('input_hash_comparison', {}).get('match')}`",
            f"- selected_fact_plan_comparison: `{doc.get('selected_fact_plan_comparison', {}).get('match')}`",
            f"- provider_request_hash_comparison: `{doc.get('provider_request_hash_comparison', {}).get('match')}`",
            "",
        ]
    )
    return "\n".join(lines)


def _failed_sections(
    sections: list[dict[str, Any]],
    result: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for section in sections:
        x3 = str(section.get("x3_code") or "")
        bucket = str(section.get("status_bucket") or "")
        failed = bool(section.get("failed_gates"))
        if x3 == "X3_ALLOW" and bucket not in {"pre_run_blocked", "not_run"} and not failed:
            continue
        if not x3 and not bucket and not failed:
            continue
        out.append(section)
    if not out and result and str(result.get("exit_status") or "") == "error":
        out.append(
            {
                "section": "whole_run",
                "status_bucket": "not_run",
                "x3_code": str(result.get("x3_disposition") or "X3_BLOCK"),
                "failed_gates": [],
                "failure_classification": str(result.get("fault") or "whole-run failure"),
            }
        )
    return out


def emit_section_failure_forensics(
    run_root: Path,
    *,
    repo_root: Path,
    sections: list[dict[str, Any]],
    result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    root = Path(run_root).resolve()
    repo = Path(repo_root).resolve()
    failed = _failed_sections(sections, result)
    out_dir = root / SECTION_FAILURE_FORENSICS_DIR
    artifacts: list[dict[str, Any]] = []
    incomplete: list[dict[str, Any]] = []
    baseline = _find_last_successful_same_scenario(root)
    if not failed:
        return {
            "gate_id": E2E_SECTION_FORENSICS_GATE_ID,
            "pass": True,
            "required": False,
            "failed_section_count": 0,
            "artifact_dir": "",
            "artifacts": [],
            "missing_or_incomplete": [],
            "failure_reason": "",
            "baseline_confidence": str(baseline.get("baseline_confidence") or "not_found"),
            "baseline_run_dir": str(baseline.get("run_dir") or ""),
        }
    for section in failed:
        section_id = str(section.get("section") or "unknown_section")
        safe_id = section_id.replace("/", "_").replace("\\", "_")
        doc = _build_rca(
            run_root=root,
            repo_root=repo,
            section=section,
            result=result,
            baseline=baseline,
        )
        errors = validate_section_failure_rca(doc)
        json_path = out_dir / f"{safe_id}.json"
        md_path = out_dir / f"{safe_id}.md"
        _write_json(json_path, doc)
        _write_text(md_path, _render_rca_md(doc))
        row = {
            "section_id": section_id,
            "json_path": _repo_rel(json_path, repo),
            "md_path": _repo_rel(md_path, repo),
            "complete": not errors,
            "errors": errors,
            "failure_type": doc.get("failure_type"),
            "baseline_confidence": doc.get("baseline_confidence"),
        }
        artifacts.append(row)
        if errors:
            incomplete.append(row)
    gate_pass = not incomplete
    gate = {
        "gate_id": E2E_SECTION_FORENSICS_GATE_ID,
        "pass": gate_pass,
        "required": bool(failed),
        "failed_section_count": len(failed),
        "artifact_dir": _repo_rel(out_dir, repo) if failed else "",
        "artifacts": artifacts,
        "missing_or_incomplete": incomplete,
        "failure_reason": "" if gate_pass else E2E_SECTION_FORENSICS_GATE_ID,
        "baseline_confidence": str(baseline.get("baseline_confidence") or "not_found"),
        "baseline_run_dir": str(baseline.get("run_dir") or ""),
    }
    _write_json(out_dir / "index.json", gate)
    _write_text(out_dir / "index.md", _render_forensics_index_md(gate))
    return gate


def _render_forensics_index_md(gate: dict[str, Any]) -> str:
    lines = [
        "# Section Failure Forensics Index",
        "",
        f"- gate_id: `{gate.get('gate_id')}`",
        f"- pass: `{gate.get('pass')}`",
        f"- required: `{gate.get('required')}`",
        f"- failed_section_count: `{gate.get('failed_section_count')}`",
        f"- baseline_confidence: `{gate.get('baseline_confidence')}`",
        "",
        "| Section | Failure type | Complete | JSON | MD |",
        "|---|---|---:|---|---|",
    ]
    for row in gate.get("artifacts") or []:
        if not isinstance(row, dict):
            continue
        lines.append(
            "| "
            f"`{row.get('section_id')}` | "
            f"`{row.get('failure_type')}` | "
            f"`{row.get('complete')}` | "
            f"`{row.get('json_path')}` | "
            f"`{row.get('md_path')}` |"
        )
    return "\n".join(lines)


__all__ = [
    "E2E_SECTION_FORENSICS_GATE_ID",
    "REQUIRED_RCA_FIELDS",
    "SECTION_FAILURE_FORENSICS_DIR",
    "emit_section_failure_forensics",
    "validate_section_failure_rca",
]
