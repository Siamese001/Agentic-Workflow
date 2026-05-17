"""Resolve apps_rg base resume material from ref, inline text, pointer merge, or default SSOT.

U0 passes through ``source_resume_ref`` / ``source_resume_text`` only; this module performs
file I/O for downstream lanes, R4 raw_request shaping, and optional ingress enrichment helpers
(see :func:`apps_rg.runtime.dispatch.apps_rg_dispatch.enrich_ingress_resume_inline_text`).
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any

# apps_rg package root (directory containing ``runtime/``, ``resume/``, …)
_APPS_RG_ROOT = Path(__file__).resolve().parent.parent
_DEFAULT_RESUME_REL_TO_PKG = Path("resume") / "base" / "amit_ayer_base_resume_v1.json"
_DEFAULT_RESUME_FILE = _APPS_RG_ROOT / _DEFAULT_RESUME_REL_TO_PKG

DEFAULT_RESUME_SSOT_PATH: Path = _DEFAULT_RESUME_FILE
DEFAULT_RESUME_REPO_RELPATH: Path = Path("apps_rg") / _DEFAULT_RESUME_REL_TO_PKG
ALLOWED_RESUME_SUFFIXES: frozenset[str] = frozenset({".json", ".txt", ".md", ".markdown"})


class ResumeSource(StrEnum):
    RUN_SPECIFIC = "RUN_SPECIFIC"
    DEFAULT_SSOT = "DEFAULT_SSOT"


class ResumeResolutionError(RuntimeError):
    """Fail-closed resume load (missing file, empty material, plain text where JSON required)."""


@dataclass(frozen=True, slots=True)
class ResolvedResume:
    """Single resolved resume material for lanes, R4, and digest stamping."""

    resume_source: ResumeSource
    resume_digest: str
    resume_ref_used: str
    resume_payload: dict[str, Any]
    resume_dict: dict[str, Any] | None
    resolved_path: Path
    raw_utf8: str


def _sha256_utf8(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def build_canonical_resume_payload(raw: str) -> dict[str, Any]:
    """Normalize resume material into a deterministic payload dict for digesting."""
    s = str(raw).strip()
    if s.startswith("{"):
        try:
            obj = json.loads(s)
            if isinstance(obj, dict):
                return {"material_kind": "json", "document": obj}
        except json.JSONDecodeError:
            pass
    return {"material_kind": "plain", "text": s}


def canonical_resume_digest(resume_payload: dict[str, Any]) -> str:
    """SHA-256 of canonical JSON for ``resume_payload``."""
    blob = _canonical_json(resume_payload)
    return _sha256_utf8(blob)


def u0_inline_text_from_payload(resume_payload: dict[str, Any]) -> str:
    """Serialization aligned with :func:`canonical_resume_digest` (for U0 ``source_resume_text``)."""
    return _canonical_json(resume_payload)


def _repo_root() -> Path:
    return _APPS_RG_ROOT.parent


def _allowed_suffix(path: Path) -> None:
    suf = path.suffix.lower()
    if suf not in ALLOWED_RESUME_SUFFIXES:
        raise ResumeResolutionError(
            f"resume artifact extension {suf!r} not in allowed set {sorted(ALLOWED_RESUME_SUFFIXES)}"
        )


def _resolve_resume_path(ref: str, *, repo_root: Path) -> Path:
    p = Path(ref)
    if p.is_absolute():
        return p.resolve()
    return (repo_root / ref).resolve()


def _default_path_from_pointer(*, repo_root: Path) -> tuple[Path, str]:
    ptr_path = repo_root / "apps_rg" / "resume" / "base" / "active_base_resume_pointer.json"
    default = repo_root / DEFAULT_RESUME_REPO_RELPATH
    if ptr_path.is_file():
        ref_obj = json.loads(ptr_path.read_text(encoding="utf-8"))
        active = ref_obj.get("active_base_resume")
        active_fp = ""
        if isinstance(active, dict):
            active_fp = str(active.get("file_path") or "").strip()
        ref = str(
            ref_obj.get("active_resume_path")
            or ref_obj.get("base_resume_json_ref")
            or active_fp
            or "apps_rg/resume/base/amit_ayer_base_resume_v1.json",
        )
        return _resolve_resume_path(ref, repo_root=repo_root), ref
    return default.resolve(), "apps_rg/resume/base/amit_ayer_base_resume_v1.json"


def _load_file_body(path: Path) -> tuple[str, str]:
    _allowed_suffix(path)
    if not path.is_file():
        raise ResumeResolutionError(f"resume path does not exist or is not a file: {path}")
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ResumeResolutionError(f"cannot read resume file {path}: {exc}") from exc
    if not str(text).strip():
        raise ResumeResolutionError(f"resume file is empty: {path}")
    return text, str(path.resolve())


def resolve_resume_for_lanes(
    *,
    source_resume_text: str | None = None,
    source_resume_ref: str | None = None,
    require_run_specific: bool = False,
    require_json_document: bool = True,
    repo_root: Path | None = None,
) -> ResolvedResume:
    """Load resume body for modular lanes / R4 / digest.

    Precedence: inline ``source_resume_text`` > ``source_resume_ref`` > pointer merge >
    canonical default JSON under ``apps_rg/resume/base/``.

    Parameters
    ----------
    require_run_specific:
        When True, no pointer/default fallbacks (must have inline or ref).
    require_json_document:
        When True, fail if material is plain text (JSON object required for dict consumers).
    """
    root = repo_root or _repo_root()
    inline = str(source_resume_text or "").strip()
    ref = str(source_resume_ref or "").strip()

    if require_run_specific and not (inline or ref):
        raise ResumeResolutionError(
            "required resume material is empty (source_resume_ref and source_resume_text)"
        )

    raw: str
    ref_used: str
    source: ResumeSource
    path_for_meta: Path

    if inline:
        raw = inline
        ref_used = "inline:source_resume_text"
        source = ResumeSource.RUN_SPECIFIC
        path_for_meta = Path("inline:source_resume_text")
    elif ref:
        path = _resolve_resume_path(ref, repo_root=root)
        raw, ref_used = _load_file_body(path)
        source = ResumeSource.RUN_SPECIFIC
        path_for_meta = path
    elif require_run_specific:
        raise ResumeResolutionError("required resume material is empty (ref-only chain exhausted)")
    else:
        path, ptr_note = _default_path_from_pointer(repo_root=root)
        raw, disk_ref = _load_file_body(path)
        ref_used = f"DEFAULT_SSOT:{ptr_note}:{disk_ref}"
        source = ResumeSource.DEFAULT_SSOT
        path_for_meta = path

    payload = build_canonical_resume_payload(raw)
    digest = canonical_resume_digest(payload)

    doc: dict[str, Any] | None = None
    if payload.get("material_kind") == "json":
        doc = payload["document"]
        if not isinstance(doc, dict):
            raise ResumeResolutionError("resolved JSON resume root must be an object")
    elif require_json_document:
        raise ResumeResolutionError(
            "resume material is plain text; JSON resume document required for this consumer"
        )

    return ResolvedResume(
        resume_source=source,
        resume_digest=digest,
        resume_ref_used=ref_used,
        resume_payload=payload,
        resume_dict=doc,
        resolved_path=path_for_meta,
        raw_utf8=raw,
    )


def load_lane_base_resume_json(
    *,
    source_resume_text: str | None = None,
    source_resume_ref: str | None = None,
    require_run_specific: bool = False,
    repo_root: Path | None = None,
) -> tuple[dict[str, Any], Path, str]:
    """Return ``(resume_dict, resolved_path, canonical_resume_digest)`` for JSON lane consumers."""
    rr = resolve_resume_for_lanes(
        source_resume_text=source_resume_text,
        source_resume_ref=source_resume_ref,
        require_run_specific=require_run_specific,
        require_json_document=True,
        repo_root=repo_root,
    )
    if rr.resume_dict is None:
        raise ResumeResolutionError("internal: JSON resume required for lane base load")
    return rr.resume_dict, rr.resolved_path, rr.resume_digest


__all__ = [
    "ALLOWED_RESUME_SUFFIXES",
    "DEFAULT_RESUME_REPO_RELPATH",
    "DEFAULT_RESUME_SSOT_PATH",
    "ResumeResolutionError",
    "ResumeSource",
    "ResolvedResume",
    "build_canonical_resume_payload",
    "canonical_resume_digest",
    "load_lane_base_resume_json",
    "resolve_resume_for_lanes",
    "u0_inline_text_from_payload",
]
