"""Canonical apps_rg product dispatch — CLI primitives → R4 integrated spine.

``dispatch_apps_rg_run`` in ``agentic_core.runtime.entry.apps_rg_dispatch`` delegates
here so core stays a thin surface and app-owned orchestration holds request shaping.

On success, the R4 entrypoint emits L7 artifacts under ``artifact_dir`` (e.g.
``agentic_core_how_trace.json``).
"""
from __future__ import annotations

import hashlib
import json
import uuid
from pathlib import Path
from typing import Any

from agentic_core.runtime.entrypoints.integrated_r4_deterministic_pipeline_run import (
    run_integrated_r4_deterministic_pipeline,
)

_SUCCESS_X3 = frozenset({"EXIT_OK", "EXIT_PARTIAL"})


def _read_optional_file(path_str: str) -> str:
    if not str(path_str).strip():
        return ""
    p = Path(path_str)
    if p.is_file():
        try:
            return p.read_text(encoding="utf-8")
        except OSError:
            return ""
    return str(path_str)


def _sha16(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def build_raw_request_for_r4(
    *,
    target_company: str,
    target_role: str,
    target_level: str = "",
    jd: str = "",
    manual_brief: str = "",
    resume_path: str = "",
    generation_mode: str = "strategic_tailor",
) -> dict[str, Any]:
    """Shape a raw_request dict for ``run_integrated_r4_deterministic_pipeline``."""
    jd_text = _read_optional_file(jd) if jd else ""
    if not jd_text.strip():
        jd_text = f"{target_role} — resume generation request (canonical CLI)."
    jd_payload = {
        "title": target_role,
        "description": jd_text,
        "company": target_company,
    }
    brief_text = _read_optional_file(manual_brief)
    resume_text = _read_optional_file(resume_path)

    jd_blob = json.dumps(jd_payload, sort_keys=True, separators=(",", ":"))
    jd_hash = hashlib.sha256(jd_blob.encode("utf-8")).hexdigest()
    brief_hash = hashlib.sha256(brief_text.encode("utf-8")).hexdigest() if brief_text else _sha16("no_brief")
    resume_hash = (
        hashlib.sha256(resume_text.encode("utf-8")).hexdigest()
        if resume_text
        else _sha16("no_resume")
    )

    return {
        "transport": "cli",
        "method": "POST",
        "content_type": "application/json",
        "source_channel": "apps_rg_cli",
        "declared_schema": "apps_rg_jd_v1",
        "tenant_id": "default",
        "user_id": "apps_rg_cli_user",
        "target_company": target_company,
        "target_role": target_role,
        "target_level": target_level,
        "manual_brief": manual_brief or "",
        "generation_mode": generation_mode,
        "jd_payload": jd_payload,
        "jd_hash": jd_hash,
        "brief_hash": brief_hash,
        "resume_hash": resume_hash,
        "policy_hash": "policy_v1",
        "blueprint_hash": "blueprint_v1",
        "flow_route": "tailor_existing",
        "body_text": jd_blob,
    }


def _default_artifact_dir(explicit: str) -> Path:
    if str(explicit).strip():
        return Path(explicit)
    here = Path(__file__).resolve()
    for parent in [here, *here.parents]:
        if (parent / "pyproject.toml").exists() or (parent / ".git").exists():
            root = parent
            break
    else:
        root = Path.cwd()
    rid = uuid.uuid4().hex[:12]
    out = root / "artifacts" / "apps_rg" / "runs" / f"cli_{rid}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def run_canonical_apps_rg_from_cli_primitives(
    *,
    target_company: str,
    target_role: str,
    target_level: str = "",
    jd: str = "",
    manual_brief: str = "",
    resume_path: str = "",
    generation_mode: str = "strategic_tailor",
    artifact_dir: str = "",
) -> dict[str, Any]:
    """Run governed R4 spine for apps_rg; return CLI-shaped result dict."""
    raw_request = build_raw_request_for_r4(
        target_company=target_company,
        target_role=target_role,
        target_level=target_level,
        jd=jd,
        manual_brief=manual_brief,
        resume_path=resume_path,
        generation_mode=generation_mode,
    )
    art = _default_artifact_dir(artifact_dir)

    result = run_integrated_r4_deterministic_pipeline(
        raw_request=raw_request,
        app_name="apps_rg",
        artifact_dir=art,
    )

    l7_path = art / "agentic_core_how_trace.json"
    l7_ok = bool(result.fault == "" and l7_path.is_file())
    outcome = (
        result.fault == ""
        and result.x3_disposition in _SUCCESS_X3
    )
    exit_status = "success" if outcome else "error"

    return {
        "exit_status": exit_status,
        "execution_status": "completed" if outcome else "failed",
        "outcome_authorized": outcome,
        "x3_disposition": result.x3_disposition,
        "fault": result.fault,
        "artifact_dir": str(art),
        "run_id": result.run_id,
        "request_id": result.request_id,
        "l7_how_trace_emitted": l7_ok,
        "terminal_r5": result.terminal_r5,
    }


__all__ = [
    "build_raw_request_for_r4",
    "run_canonical_apps_rg_from_cli_primitives",
]
