"""W2 on-disk artifact gate — full résumé success requires JSON + manifest (apps_rg-local)."""

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
_REL_OUTPUT_MANIFEST = Path("apps_rg_output_manifest.json")


def _fail(reasons: list[str]) -> None:
    raise RuntimeError("FAILED_ARTIFACT_GATE: " + "; ".join(reasons))


def persist_json_product_outputs(
    run_dir: Path,
    *,
    generated_resume: dict[str, Any] | None,
) -> None:
    """Write ``outputs/generated_resume.json`` and a JSON-only output manifest when absent."""
    base = Path(run_dir)
    out_dir = base / "outputs"
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "generated_resume.json"
    if generated_resume is not None and isinstance(generated_resume, dict) and generated_resume:
        if not json_path.is_file():
            json_path.write_text(
                json.dumps(generated_resume, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
    man_path = base / _REL_OUTPUT_MANIFEST
    if man_path.is_file():
        return
    shape_rep = classify_resume_payload(
        json.loads(json_path.read_text(encoding="utf-8"))
        if json_path.is_file()
        else (generated_resume or {}),
    )
    manifest: dict[str, Any] = {
        "schema_version": "apps_rg_output_manifest.v1",
        "generated_resume_json_relpath": _REL_GENERATED_RESUME_JSON.as_posix(),
        "apps_rg_generation_status": shape_rep.generation_status,
        "full_resume_generated": shape_rep.full_resume_generated,
        "resume_shape": shape_rep.resume_shape,
        "docx_output_required": True,
        "required_artifacts": {
            "generated_resume_json": "present",
            "output_manifest": "present",
            "resume_docx": "missing",
            "docx_verified": False,
        },
    }
    man_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def verify_full_resume_artifact_bundle(run_dir: Path) -> ResumeShapeReport:
    """Verify required paths, manifest fields, and REAL_RESUME JSON shape.

    Raises
    ------
    RuntimeError
        With prefix ``FAILED_ARTIFACT_GATE`` when the bundle cannot authorize full success.
    """
    base = Path(run_dir)
    reasons: list[str] = []
    json_path = base / _REL_GENERATED_RESUME_JSON
    man_path = base / _REL_OUTPUT_MANIFEST

    if not json_path.is_file():
        reasons.append(f"missing:{_REL_GENERATED_RESUME_JSON.as_posix()}")
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

    try:
        manifest: dict[str, Any] = json.loads(man_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        _fail([f"invalid_output_manifest:{exc}"])

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
    manifest["docx_output_required"] = True
    manifest["generated_resume_json_relpath"] = _REL_GENERATED_RESUME_JSON.as_posix()
    manifest["required_artifacts"] = {
        "generated_resume_json": "verified",
        "output_manifest": "verified",
        "resume_docx": "verified" if (base / "outputs" / "resume.docx").is_file() else "missing",
        "docx_verified": (base / "outputs" / "resume.docx").is_file(),
    }
    man_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return manifest


__all__ = [
    "merge_manifest_after_artifact_gate",
    "persist_json_product_outputs",
    "verify_full_resume_artifact_bundle",
]
