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
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from agentic_core.runtime.entrypoints.integrated_r4_deterministic_pipeline_run import (
    run_integrated_r4_deterministic_pipeline,
)

# V6 terminal codes short values (integrated R4); legacy strings retained.
_SUCCESS_X3 = frozenset({"X3C", "X3D", "EXIT_OK", "EXIT_PARTIAL"})
_BRIEF_FETCH_MAX_BYTES = 2_000_000


def _fetch_url_text(url: str, *, max_bytes: int = _BRIEF_FETCH_MAX_BYTES) -> str:
    """Fetch brief content from http(s); bounded read for CLI safety."""
    req = Request(url, headers={"User-Agent": "apps_rg-cli/1"})
    with urlopen(req, timeout=45) as resp:  # noqa: S310 — intentional user-supplied brief URL
        raw = resp.read(max_bytes + 1)
    if len(raw) > max_bytes:
        return ""
    return raw.decode("utf-8", errors="replace")


def _read_optional_brief(path_or_url: str) -> str:
    """Load research brief from local path or http(s) URL."""
    s = str(path_or_url).strip()
    if not s:
        return ""
    if s.startswith(("http://", "https://")):
        try:
            return _fetch_url_text(s)
        except (HTTPError, URLError, OSError, ValueError):
            return ""
    return _read_optional_file(s)


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


def _normalize_jd_text_and_title(
    jd_raw: str,
    *,
    target_role: str,
) -> tuple[str, str]:
    """Return (description text, job posting title for jd_payload).

    If ``jd_raw`` is a JSON object with ``title`` / ``description``, those override
    the generic file-as-text behaviour so interactive CLI can pass structured JD.
    """
    jd_text = jd_raw
    jd_title = str(target_role).strip()

    st = jd_raw.strip()
    if st.startswith("{"):
        try:
            obj = json.loads(st)
            if isinstance(obj, dict):
                if obj.get("title") is not None and str(obj.get("title")).strip():
                    jd_title = str(obj["title"]).strip()
                if "description" in obj and obj.get("description") is not None:
                    jd_text = str(obj["description"])
                elif obj:
                    jd_text = json.dumps(obj, sort_keys=True, separators=(",", ":"))
        except json.JSONDecodeError:
            pass

    if not str(jd_text).strip():
        jd_text = f"{target_role} — resume generation request (canonical CLI)."

    return jd_text, jd_title or str(target_role).strip()


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
    jd_raw = _read_optional_file(jd) if jd else ""
    jd_text, jd_title_effective = _normalize_jd_text_and_title(
        jd_raw,
        target_role=target_role,
    )
    jd_payload = {
        "title": jd_title_effective,
        "description": jd_text,
        "company": target_company,
    }
    brief_text = _read_optional_brief(manual_brief)
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
        # E1 intake allowlist excludes "cli"; local CLI runs are user-driven → "ui".
        "transport": "ui",
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


def _augment_integrated_manifest_with_apps_rg_docx(artifact_dir: Path) -> None:
    """Add DOCX pointer fields when ``outputs/resume.docx`` exists.

    Does not modify ``artifact_filenames`` — SSOT chain enumerations stay stable.
    """
    docx = artifact_dir / "outputs" / "resume.docx"
    manifest_path = artifact_dir / "integrated_runtime_artifact_manifest.json"
    if not docx.is_file() or not manifest_path.is_file():
        return
    try:
        digest = hashlib.sha256(docx.read_bytes()).hexdigest()
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        data["apps_rg_resume_docx_relpath"] = "outputs/resume.docx"
        data["apps_rg_resume_docx_sha256"] = f"sha256:{digest}"
        manifest_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    except (OSError, json.JSONDecodeError, TypeError):
        return


def _augment_r4_run_manifest_for_apps_rg_l2_fault(
    artifact_dir: Path,
    *,
    fault: str,
    x3_disposition: str,
) -> None:
    """Align ``r4_run_manifest.json`` with apps_rg full-résumé product truth when L2 faults.

    Core R4 already coerces ``x3_disposition`` to DENY (X3A) when ``l2_fault`` is set;
    this adds explicit product fields so operators are not misled by envelope-only X3
    history and records missing résumé artifacts.
    """
    if not str(fault).strip():
        return
    path = artifact_dir / "r4_run_manifest.json"
    if not path.is_file():
        return
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, TypeError):
        return

    gen_status = "L2_EXECUTION_FAILED"
    if "BLOCKED_STUB_PROVIDER" in fault:
        gen_status = "BLOCKED_STUB_PROVIDER"
    elif "BLOCKED_PROVIDER_LANE" in fault:
        gen_status = "BLOCKED_PROVIDER_LANE"
    elif "FAILED_PROVIDER" in fault:
        gen_status = "FAILED_PROVIDER"
    elif "FAILED_ARTIFACT_GATE" in fault:
        gen_status = "FAILED_ARTIFACT_GATE"

    data["x3_disposition"] = x3_disposition
    data["apps_rg_terminal_class"] = "failure"
    data["apps_rg_product_outcome_authorized"] = False
    data["apps_rg_generation_status"] = gen_status
    data["apps_rg_full_resume_generated"] = False
    data["apps_rg_required_resume_artifacts"] = {
        "outputs/generated_resume.json": "missing",
        "outputs/resume.docx": "missing",
    }
    try:
        path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    except OSError:
        return


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
    _augment_integrated_manifest_with_apps_rg_docx(art)
    _augment_r4_run_manifest_for_apps_rg_l2_fault(
        art,
        fault=result.fault,
        x3_disposition=result.x3_disposition,
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
