"""W2 on-disk artifact gate — full résumé success requires JSON + DOCX + manifest (apps_rg-local)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from apps_rg.l2_recipe.resume_output_shape import (
    ResumeShapeReport,
    STUB_RECEIPT,
    classify_resume_payload,
    is_real_resume_shape_report,
)

_REL_GENERATED_RESUME_JSON = Path("outputs") / "generated_resume.json"
_REL_RESUME_DOCX = Path("outputs") / "resume.docx"
_REL_OUTPUT_MANIFEST = Path("apps_rg_output_manifest.json")


def _fail(reasons: list[str]) -> None:
    raise RuntimeError("FAILED_ARTIFACT_GATE: " + "; ".join(reasons))


def verify_full_resume_artifact_bundle(run_dir: Path) -> ResumeShapeReport:
    """Verify required paths, manifest ``docx_verified``, and REAL_RESUME JSON shape.

    Raises
    ------
    RuntimeError
        With prefix ``FAILED_ARTIFACT_GATE`` when the bundle cannot authorize full success.
    """
    base = Path(run_dir)
    reasons: list[str] = []
    json_path = base / _REL_GENERATED_RESUME_JSON
    docx_path = base / _REL_RESUME_DOCX
    man_path = base / _REL_OUTPUT_MANIFEST

    if not json_path.is_file():
        reasons.append(f"missing:{_REL_GENERATED_RESUME_JSON.as_posix()}")
    if not docx_path.is_file():
        reasons.append(f"missing:{_REL_RESUME_DOCX.as_posix()}")
    if not man_path.is_file():
        reasons.append(f"missing:{_REL_OUTPUT_MANIFEST.as_posix()}")
    if reasons:
        _fail(reasons)

    raw = json_path.read_text(encoding="utf-8").strip()
    if not raw:
        _fail([f"empty_json:{_REL_GENERATED_RESUME_JSON.as_posix()}"])
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        _fail([f"invalid_json:{_REL_GENERATED_RESUME_JSON.as_posix()}:{exc}"])
    if not isinstance(data, dict) or len(data) == 0:
        _fail([f"non_object_or_empty:{_REL_GENERATED_RESUME_JSON.as_posix()}"])

    if docx_path.stat().st_size <= 0:
        _fail([f"empty_docx:{_REL_RESUME_DOCX.as_posix()}"])

    try:
        manifest: dict[str, Any] = json.loads(man_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        _fail([f"invalid_output_manifest:{exc}"])

    docx_ok = manifest.get("docx_verified")
    if docx_ok is not True:
        _fail([f"docx_verified_not_true(got={docx_ok!r})"])

    rep = classify_resume_payload(data)
    if rep.generation_status == STUB_RECEIPT or rep.resume_shape == STUB_RECEIPT:
        _fail(["stub_receipt_payload_not_eligible_for_full_resume_bundle"])
    if not is_real_resume_shape_report(rep):
        _fail(
            [
                "resume_shape_not_real_resume: "
                f"generation_status={rep.generation_status!r} "
                f"resume_shape={rep.resume_shape!r} "
                f"full_resume_generated={rep.full_resume_generated!r}",
            ]
        )

    return rep


def merge_manifest_after_artifact_gate(
    run_dir: Path,
    *,
    shape_rep: ResumeShapeReport,
) -> dict[str, Any]:
    """Attach W2 product fields and ``required_artifacts``; rewrite manifest atomically."""
    base = Path(run_dir)
    man_path = base / _REL_OUTPUT_MANIFEST
    manifest = json.loads(man_path.read_text(encoding="utf-8"))
    manifest["apps_rg_generation_status"] = shape_rep.generation_status
    manifest["full_resume_generated"] = shape_rep.full_resume_generated
    manifest["resume_shape"] = shape_rep.resume_shape
    manifest["required_artifacts"] = {
        "generated_resume_json": "verified",
        "resume_docx": "verified",
        "output_manifest": "verified",
        "docx_verified": True,
    }
    man_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return manifest


__all__ = [
    "merge_manifest_after_artifact_gate",
    "verify_full_resume_artifact_bundle",
]
