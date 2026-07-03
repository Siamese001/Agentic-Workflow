"""Mandatory final resume text/DOCX product outputs for apps_rg runs."""

from __future__ import annotations

import hashlib
import html
import json
import re
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from xml.etree import ElementTree

from apps_rg.runtime.assembly.full_resume_text import (
    ENGINEERING_PLATFORM_COMPETENCIES_HEADING,
    base_role_header_lines_from_final_resume,
    base_role_headers_from_final_resume,
    flatten_final_resume_to_text,
    format_cert,
    format_edu,
    rendered_resume_section_order,
)
from apps_rg.runtime.full_run_section_status import (
    LANE_DISPLAY_TXT_CANDIDATES,
    collect_full_run_section_status,
)
from apps_rg.runtime.run_output_contract import (
    FINAL_RESUME_ASSEMBLY_JSON_RELPATH,
    FINAL_RESUME_DOCX_RELPATH,
    FINAL_RESUME_OUTPUT_JSON,
    FINAL_RESUME_OUTPUT_TXT,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
BASE_RESUME_RELPATH = Path("apps_rg/resume/base/amit_ayer_base_resume_v1.json")
GENERATED_SECTION_IDS: tuple[str, ...] = (
    "headline",
    "executive_summary",
    "competencies",
    "unify_bullets",
    "unify_narrative",
    "ibm_bullets",
    "ibm_narrative",
    "insurtech_bullets",
    "insurtech_narrative",
    "ey_bullets",
    "ey_narrative",
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _repo_rel(path: Path, repo: Path) -> str:
    try:
        return path.resolve().relative_to(repo.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def _run_rel(path: Path, run_root: Path) -> str:
    try:
        return path.resolve().relative_to(run_root.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def _sha256_file(path: Path) -> str | None:
    if not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, TypeError):
        return {}
    return raw if isinstance(raw, dict) else {}


def _load_text(path: Path) -> str:
    if not path.is_file():
        return ""
    try:
        return path.read_text(encoding="utf-8").strip()
    except OSError:
        return ""


def _base_resume_path(repo_root: Path | None) -> Path:
    candidates: list[Path] = []
    if repo_root is not None:
        candidates.append(Path(repo_root).resolve() / BASE_RESUME_RELPATH)
    candidates.append(REPO_ROOT / BASE_RESUME_RELPATH)
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return candidates[-1]


def _load_base_resume(repo_root: Path | None) -> dict[str, Any]:
    return _load_json(_base_resume_path(repo_root))


def _json_dumps(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def _display_text_for_lane(run_root: Path, lane: str) -> str:
    for row in collect_full_run_section_status(run_root, repo_root=REPO_ROOT):
        if row.lane != lane or not row.display_txt_abs:
            continue
        text = _load_text(Path(row.display_txt_abs))
        if text:
            return text
    for rel in LANE_DISPLAY_TXT_CANDIDATES.get(lane, ("command_output.txt",)):
        for base in (run_root / "lanes" / lane, run_root / "modular_r4" / "sections" / lane):
            text = _load_text(base / rel)
            if text:
                return text
    return ""


def _lane_l2_snapshot(run_root: Path, lane: str) -> dict[str, Any]:
    for row in collect_full_run_section_status(run_root, repo_root=REPO_ROOT):
        if row.lane != lane or not row.lane_dir:
            continue
        lane_dir = Path(row.lane_dir)
        if not lane_dir.is_absolute():
            lane_dir = REPO_ROOT / lane_dir
        l2 = _load_json(lane_dir / "l2_output.json")
        if l2:
            return l2
    for base in (run_root / "lanes" / lane, run_root / "modular_r4" / "sections" / lane):
        l2 = _load_json(base / "l2_output.json")
        if l2:
            return l2
    return {}


def _bullet_rows(text: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for line in text.splitlines():
        cleaned = line.strip().lstrip("-*•").strip()
        if cleaned:
            rows.append({"bullet_text": cleaned})
    return rows


def _snapshot_from_lane_artifacts(run_root: Path, lane: str) -> dict[str, Any]:
    l2 = _lane_l2_snapshot(run_root, lane)
    if l2:
        return l2
    text = _display_text_for_lane(run_root, lane)
    if not text:
        return {}
    if lane == "headline":
        return {"headline_line": text}
    if lane == "executive_summary":
        return {"resume_display_text": text}
    if lane == "competencies":
        return {"resume_display_text": text}
    if lane.endswith("_bullets"):
        return {"bullets": _bullet_rows(text)}
    if lane.endswith("_narrative"):
        return {"narrative_sentence": text}
    return {"resume_display_text": text}


def _generated_section(order: int, section_id: str, snapshot: dict[str, Any]) -> dict[str, Any]:
    return {
        "assemble_order": order,
        "section_id": section_id,
        "section_kind": "generated_lane",
        "l2_output_snapshot": snapshot,
        "generated_content_observed": bool(snapshot),
        "source_artifact_refs": {},
        "disposition_refs": {},
    }


def _fallback_final_resume_blob(run_root: Path, repo_root: Path | None) -> dict[str, Any]:
    base = _load_base_resume(repo_root)
    facts = base.get("facts") if isinstance(base.get("facts"), dict) else {}
    employment = [row for row in facts.get("employment") or [] if isinstance(row, dict)]
    education = [row for row in facts.get("education") or [] if isinstance(row, dict)]
    certifications = [row for row in facts.get("certifications") or [] if isinstance(row, dict)]
    header = base.get("header") if isinstance(base.get("header"), dict) else {}

    generated_sections = [
        _generated_section(idx, section_id, _snapshot_from_lane_artifacts(run_root, section_id))
        for idx, section_id in enumerate(GENERATED_SECTION_IDS)
    ]
    early = employment[4] if len(employment) > 4 else {}
    locked_sections = [
        {
            "assemble_order": 11,
            "section_id": "early_career",
            "section_kind": "locked_copy_inline",
            "copied_text_exact": _json_dumps(early),
        },
        {
            "assemble_order": 12,
            "section_id": "education",
            "section_kind": "locked_copy_inline",
            "copied_text_exact": _json_dumps(education),
        },
        {
            "assemble_order": 13,
            "section_id": "certifications",
            "section_kind": "locked_copy_inline",
            "copied_text_exact": _json_dumps(certifications),
        },
    ]
    dates = [
        {
            "start_date": row.get("start_date"),
            "end_date": row.get("end_date"),
            "is_current": row.get("is_current"),
        }
        for row in employment
    ]
    return {
        "schema_version": "apps_rg.final_resume_assembly.v1",
        "assembly_mode": "mandatory_fallback_from_base_resume_and_run_artifacts",
        "generated_at_utc": _utc_now(),
        "candidate_identity": {
            "candidate_name": header.get("name") or base.get("candidate_name") or "Candidate",
            "header_contact": {
                key: header.get(key)
                for key in ("phone", "email", "linkedin", "github", "location")
                if header.get(key)
            },
        },
        "sections": generated_sections + locked_sections,
        "locked_copy_invariants": {
            "company_names": {
                "copied_text_exact": _json_dumps([row.get("employer") for row in employment])
            },
            "titles": {
                "copied_text_exact": _json_dumps([row.get("title") for row in employment])
            },
            "locations": {
                "copied_text_exact": _json_dumps([row.get("location") for row in employment])
            },
            "dates": {"copied_text_exact": _json_dumps(dates)},
        },
        "source_base_resume": str(_base_resume_path(repo_root)),
        "generated_content_source": "run_artifacts_when_present_else_NOT_GENERATED_BY_RUN_markers",
    }


def _ensure_fallback_final_resume_json(
    run_root: Path,
    *,
    repo_root: Path | None,
) -> Path:
    path = run_root / FINAL_RESUME_ASSEMBLY_JSON_RELPATH
    path.parent.mkdir(parents=True, exist_ok=True)
    blob = _fallback_final_resume_blob(run_root, repo_root)
    path.write_text(json.dumps(blob, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def _safe_rel_manifest_value(value: Any) -> str:
    raw = str(value or "").strip().replace("\\", "/")
    if not raw or raw.startswith(("/", "\\")) or (len(raw) > 1 and raw[1] == ":"):
        return ""
    if ".." in raw.split("/"):
        return ""
    return raw


def _resolve_final_resume_json(run_root: Path) -> Path | None:
    preferred = run_root / FINAL_RESUME_ASSEMBLY_JSON_RELPATH
    if preferred.is_file():
        return preferred
    manifest = _load_json(run_root / "apps_rg_output_manifest.json")
    for key in (
        "canonical_final_resume_json_relpath",
        "final_resume_json_relpath",
        "final_resume_json",
    ):
        rel = _safe_rel_manifest_value(manifest.get(key))
        if rel:
            candidate = run_root / rel
            if candidate.is_file():
                return candidate
    candidates = sorted(run_root.rglob("final_resume.json"))
    spine = [p for p in candidates if _is_spine_shaped(_load_json(p))]
    if not spine:
        return None
    for p in spine:
        if p.parent.name == "final_resume_assembly":
            return p
    return spine[0]


def _is_spine_shaped(blob: dict[str, Any]) -> bool:
    return isinstance(blob.get("candidate_identity"), dict) and isinstance(blob.get("sections"), list)


def _docx_text(path: Path) -> str:
    if not path.is_file():
        return ""
    try:
        with zipfile.ZipFile(path) as zf:
            xml = zf.read("word/document.xml")
    except (OSError, KeyError, zipfile.BadZipFile):
        return ""
    try:
        root = ElementTree.fromstring(xml)
    except ElementTree.ParseError:
        return html.unescape(re.sub(r"<[^>]+>", "", xml.decode("utf-8", "replace")))
    texts: list[str] = []
    for node in root.iter():
        if node.tag.endswith("}t") and node.text:
            texts.append(node.text)
    return "\n".join(texts)


def _artifact(path: Path, run_root: Path) -> dict[str, Any]:
    return {
        "relpath": _run_rel(path, run_root),
        "exists": path.is_file(),
        "bytes": path.stat().st_size if path.is_file() else 0,
        "sha256": _sha256_file(path),
    }


def _gate(gate_id: str, ok: bool, observed: Any, threshold: Any = None, reason: str = "") -> dict[str, Any]:
    return {
        "gate_id": gate_id,
        "pass": bool(ok),
        "observed_value": observed,
        "threshold": threshold,
        "failure_reason": "" if ok else reason,
    }


def _positions(text: str, needles: list[str]) -> dict[str, int]:
    return {needle: text.find(needle) for needle in needles}


def _order_gate(text: str) -> tuple[bool, dict[str, int]]:
    needles = [
        "EXECUTIVE SUMMARY",
        ENGINEERING_PLATFORM_COMPETENCIES_HEADING,
        "PROFESSIONAL EXPERIENCE",
        "EDUCATION",
        "CERTIFICATIONS",
    ]
    positions = _positions(text, needles)
    values = [positions[n] for n in needles]
    ok = all(v >= 0 for v in values) and values == sorted(values)
    return ok, positions


def _base_header_gate(text: str, final_resume: dict[str, Any]) -> tuple[bool, dict[str, Any]]:
    expected = base_role_header_lines_from_final_resume(final_resume)
    observed: dict[str, Any] = {"role_headers": {}, "positions": {}}
    if set(expected) != {"unify", "ibm", "insurtech", "ey", "early_career"}:
        observed["role_headers"] = expected
        return False, observed
    last = -1
    for role_key in ("unify", "ibm", "insurtech", "ey", "early_career"):
        lines = expected.get(role_key) or []
        role_ok = True
        role_positions: list[int] = []
        for line in lines:
            pos = text.find(line)
            role_positions.append(pos)
            if pos < 0 or pos < last:
                role_ok = False
        if role_positions:
            last = max(last, max(role_positions))
        observed["role_headers"][role_key] = lines
        observed["positions"][role_key] = role_positions
        if not role_ok:
            return False, observed
    return True, observed


def _base_header_facts(final_resume: dict[str, Any]) -> list[dict[str, Any]]:
    headers = base_role_headers_from_final_resume(final_resume)
    rows: list[dict[str, Any]] = []
    for role_key in ("unify", "ibm", "insurtech", "ey", "early_career"):
        hdr = headers.get(role_key) or {}
        rows.append(
            {
                "role_key": role_key,
                "employer": hdr.get("employer"),
                "title": hdr.get("title"),
                "location": hdr.get("location"),
                "start_date": hdr.get("start_date"),
                "end_date": hdr.get("end_date"),
                "is_current": hdr.get("is_current"),
            }
        )
    return rows


def _section_by_id(final_resume: dict[str, Any], section_id: str) -> dict[str, Any]:
    for section in final_resume.get("sections") or []:
        if isinstance(section, dict) and section.get("section_id") == section_id:
            return section
    return {}


def _locked_lines(final_resume: dict[str, Any], section_id: str) -> list[str]:
    section = _section_by_id(final_resume, section_id)
    copied = section.get("copied_text_exact")
    if not isinstance(copied, str) or not copied.strip():
        return []
    try:
        rows = json.loads(copied)
    except json.JSONDecodeError:
        return []
    if not isinstance(rows, list):
        return []
    lines: list[str] = []
    formatter = format_edu if section_id == "education" else format_cert
    for row in rows:
        if isinstance(row, dict):
            line = formatter(row)
            if line:
                lines.append(line)
    return lines


def _locked_lines_gate(text: str, final_resume: dict[str, Any], section_id: str) -> tuple[bool, dict[str, Any]]:
    expected = _locked_lines(final_resume, section_id)
    observed = {"section_id": section_id, "expected_lines": expected, "positions": {}}
    if not expected:
        return False, observed
    ok = True
    for line in expected:
        pos = text.find(line)
        observed["positions"][line] = pos
        if pos < 0:
            ok = False
    return ok, observed


def _write_output_manifest(
    run_root: Path,
    *,
    final_resume_path: Path | None,
    contract: dict[str, Any],
) -> None:
    manifest_path = run_root / "apps_rg_output_manifest.json"
    manifest = _load_json(manifest_path)
    if not manifest:
        manifest = {"schema_version": "apps_rg_output_manifest.v1"}
    if final_resume_path is not None:
        manifest["canonical_final_resume_json_relpath"] = _run_rel(final_resume_path, run_root)
    manifest["rendered_resume_text_relpath"] = FINAL_RESUME_OUTPUT_TXT
    manifest["final_resume_output_json_relpath"] = FINAL_RESUME_OUTPUT_JSON
    manifest["resume_docx_relpath"] = FINAL_RESUME_DOCX_RELPATH
    output_required = bool(contract.get("required"))
    manifest["docx_output_required"] = output_required
    manifest["docx_verified"] = contract.get("status") == "PASS"
    required = manifest.get("required_artifacts")
    if not isinstance(required, dict):
        required = {}
    required.update(
        {
            "canonical_final_resume_json": "verified"
            if contract.get("final_resume_json", {}).get("exists")
            else "missing" if output_required else "not_required",
            "rendered_resume_text": "verified"
            if contract.get("rendered_resume_text", {}).get("exists")
            else "missing" if output_required else "not_required",
            "resume_docx": "verified"
            if contract.get("resume_docx", {}).get("exists")
            else "missing" if output_required else "not_required",
            "final_resume_output_json": "verified",
            "docx_verified": contract.get("status") == "PASS",
        }
    )
    manifest["required_artifacts"] = required
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def build_final_resume_output_contract(
    run_root: Path,
    *,
    repo_root: Path | None = None,
    required: bool = True,
) -> dict[str, Any]:
    root = Path(run_root).resolve()
    repo = (repo_root or root).resolve()
    final_resume_path = _resolve_final_resume_json(root)
    text_path = root / FINAL_RESUME_OUTPUT_TXT
    docx_path = root / FINAL_RESUME_DOCX_RELPATH
    final_resume = _load_json(final_resume_path) if final_resume_path is not None else {}
    text = text_path.read_text(encoding="utf-8") if text_path.is_file() else ""
    docx_text = _docx_text(docx_path)

    spine_ok = final_resume_path is not None and _is_spine_shaped(final_resume)
    text_ok = bool(text.strip())
    docx_ok = docx_path.is_file() and docx_path.stat().st_size > 0 and bool(docx_text.strip())
    text_order_ok, text_order_obs = _order_gate(text)
    docx_order_ok, docx_order_obs = _order_gate(docx_text.upper())
    text_headers_ok, text_headers_obs = (
        _base_header_gate(text, final_resume) if spine_ok else (False, {})
    )
    docx_headers_ok, docx_headers_obs = (
        _base_header_gate(docx_text, final_resume) if spine_ok else (False, {})
    )
    text_education_ok, text_education_obs = (
        _locked_lines_gate(text, final_resume, "education") if spine_ok else (False, {})
    )
    docx_education_ok, docx_education_obs = (
        _locked_lines_gate(docx_text, final_resume, "education") if spine_ok else (False, {})
    )
    text_certifications_ok, text_certifications_obs = (
        _locked_lines_gate(text, final_resume, "certifications") if spine_ok else (False, {})
    )
    docx_certifications_ok, docx_certifications_obs = (
        _locked_lines_gate(docx_text, final_resume, "certifications") if spine_ok else (False, {})
    )
    no_gaps_ok = "[NOT COMPLETED:" not in text and "[NOT_GENERATED_BY_RUN:" not in text

    gates = [
        _gate(
            "final_resume_json_spine_present",
            spine_ok,
            _repo_rel(final_resume_path, repo) if final_resume_path is not None else None,
            FINAL_RESUME_ASSEMBLY_JSON_RELPATH,
            "missing spine-shaped final_resume.json",
        ),
        _gate(
            "final_resume_rendered_text_present",
            text_ok,
            _artifact(text_path, root),
            "nonempty text output",
            "FINAL_RESUME_OUTPUT.txt missing or empty",
        ),
        _gate(
            "final_resume_docx_present_nonempty",
            docx_ok,
            _artifact(docx_path, root),
            "nonempty DOCX output",
            "outputs/resume.docx missing, empty, or unreadable",
        ),
        _gate(
            "final_resume_rendered_order_valid",
            text_order_ok,
            text_order_obs,
            list(rendered_resume_section_order()),
            "rendered resume text order is invalid",
        ),
        _gate(
            "final_resume_docx_order_valid",
            docx_order_ok,
            docx_order_obs,
            list(rendered_resume_section_order()),
            "DOCX resume order is invalid",
        ),
        _gate(
            "final_resume_base_role_headers_preserved",
            text_headers_ok,
            text_headers_obs,
            "base resume employer/title/location/date headers in order",
            "rendered text does not preserve base resume role headers",
        ),
        _gate(
            "final_resume_docx_base_role_headers_preserved",
            docx_headers_ok,
            docx_headers_obs,
            "base resume employer/title/location/date headers in order",
            "DOCX does not preserve base resume role headers",
        ),
        _gate(
            "final_resume_education_copied_from_base",
            text_education_ok,
            text_education_obs,
            "base resume education lines",
            "rendered text does not contain locked base resume education",
        ),
        _gate(
            "final_resume_docx_education_copied_from_base",
            docx_education_ok,
            docx_education_obs,
            "base resume education lines",
            "DOCX does not contain locked base resume education",
        ),
        _gate(
            "final_resume_certifications_copied_from_base",
            text_certifications_ok,
            text_certifications_obs,
            "base resume certification lines",
            "rendered text does not contain locked base resume certifications",
        ),
        _gate(
            "final_resume_docx_certifications_copied_from_base",
            docx_certifications_ok,
            docx_certifications_obs,
            "base resume certification lines",
            "DOCX does not contain locked base resume certifications",
        ),
        _gate(
            "final_resume_no_gap_markers",
            no_gaps_ok,
            {
                "not_completed": "[NOT COMPLETED:" in text,
                "not_generated_by_run": "[NOT_GENERATED_BY_RUN:" in text,
            },
            False,
            "rendered resume contains generated-content gap markers",
        ),
    ]
    failed = [g["gate_id"] for g in gates if not g["pass"]]
    status = "PASS" if not failed else ("FAIL" if required else "SKIPPED")
    return {
        "schema_version": "apps_rg.final_resume_output.v1",
        "generated_at_utc": _utc_now(),
        "required": bool(required),
        "status": status,
        "failed_gate_ids": failed,
        "run_root": _repo_rel(root, repo),
        "final_resume_json": _artifact(final_resume_path, root) if final_resume_path is not None else {
            "relpath": FINAL_RESUME_ASSEMBLY_JSON_RELPATH,
            "exists": False,
            "bytes": 0,
            "sha256": None,
        },
        "rendered_resume_text": _artifact(text_path, root),
        "resume_docx": _artifact(docx_path, root),
        "rendered_order": list(rendered_resume_section_order()),
        "base_resume_role_facts": _base_header_facts(final_resume) if spine_ok else [],
        "content_sources": {
            "identity_contact_source": "base_resume_locked_profile",
            "role_header_source": "final_resume.locked_copy_invariants",
            "generated_content_source": "final_resume.sections[].l2_output_snapshot",
            "education_certification_source": "final_resume.sections[].copied_text_exact",
            "locked_copy_source": "final_resume.sections[].copied_text_exact",
        },
        "gates": gates,
    }


def emit_final_resume_product_outputs(
    run_root: Path,
    *,
    repo_root: Path | None = None,
    required: bool = True,
) -> dict[str, Any]:
    root = Path(run_root).resolve()
    final_resume_path = _resolve_final_resume_json(root)
    if final_resume_path is None and required:
        final_resume_path = _ensure_fallback_final_resume_json(root, repo_root=repo_root)
    if final_resume_path is not None:
        final_resume = _load_json(final_resume_path)
        if _is_spine_shaped(final_resume):
            text = flatten_final_resume_to_text(final_resume)
            (root / FINAL_RESUME_OUTPUT_TXT).write_text(text, encoding="utf-8")
            docx_path = root / FINAL_RESUME_DOCX_RELPATH
            docx_path.parent.mkdir(parents=True, exist_ok=True)
            from ops_scripts.apps_rg.export_final_resume_docx import export

            export(final_resume_path, docx_path)

    contract = build_final_resume_output_contract(root, repo_root=repo_root, required=required)
    _write_output_manifest(root, final_resume_path=final_resume_path, contract=contract)
    contract_path = root / FINAL_RESUME_OUTPUT_JSON
    contract_path.write_text(json.dumps(contract, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return contract


__all__ = [
    "build_final_resume_output_contract",
    "emit_final_resume_product_outputs",
]
