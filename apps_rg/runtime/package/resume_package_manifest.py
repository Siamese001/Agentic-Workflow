"""Default paths + manifest JSON for resume package X3 aggregator (read-only proofs)."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


def repo_root_default() -> Path:
    """apps_rg/runtime/package -> workspace root."""
    return Path(__file__).resolve().parents[3]


RUNTIME_PROOFS = "artifacts/apps_rg/runtime_proofs"


@dataclass(frozen=True)
class ResumePackageProofPaths:
    """Canonical artifact locations for aggregated resume package proofs."""

    repo_root: Path
    rollup_json: Path
    locked_copy_manifest_json: Path
    locked_copy_x2_json: Path
    final_resume_json: Path
    final_resume_manifest_json: Path
    final_resume_x2_json: Path
    docx_manifest_json: Path
    docx_manifest_x2_json: Path
    docx_render_manifest_json: Path
    docx_render_x2_json: Path
    output_dir: Path

    def package_manifest_json(self) -> Path:
        return self.output_dir / "resume_package_manifest.json"

    def package_x3_json(self) -> Path:
        return self.output_dir / "resume_package_x3_disposition.json"

    def package_receipt_json(self) -> Path:
        return self.output_dir / "resume_package_receipt.json"


def resolve_resume_package_paths(
    *,
    repo_root: Path | None = None,
    output_rel: str | None = None,
) -> ResumePackageProofPaths:
    rr = repo_root.resolve() if repo_root is not None else repo_root_default()
    rp = rr / RUNTIME_PROOFS
    docx_out = rp / "docx"
    out_rel = output_rel or f"{RUNTIME_PROOFS}/resume_package"
    return ResumePackageProofPaths(
        repo_root=rr,
        rollup_json=rr / RUNTIME_PROOFS / "generated_lane_rollup" / "generated_lane_rollup.json",
        locked_copy_manifest_json=rr / RUNTIME_PROOFS / "locked_copy" / "locked_copy_manifest.json",
        locked_copy_x2_json=rr / RUNTIME_PROOFS / "locked_copy" / "locked_copy_x2_gate_outputs.json",
        final_resume_json=rr / RUNTIME_PROOFS / "final_resume_assembly" / "final_resume.json",
        final_resume_manifest_json=rr / RUNTIME_PROOFS / "final_resume_assembly" / "final_resume_manifest.json",
        final_resume_x2_json=rr / RUNTIME_PROOFS / "final_resume_assembly" / "final_resume_x2_gate_outputs.json",
        docx_manifest_json=rr / RUNTIME_PROOFS / "docx_manifest" / "docx_manifest.json",
        docx_manifest_x2_json=rr / RUNTIME_PROOFS / "docx_manifest" / "docx_manifest_x2_gate_outputs.json",
        docx_render_manifest_json=docx_out / "docx_render_manifest.json",
        docx_render_x2_json=docx_out / "docx_render_x2_gate_outputs.json",
        output_dir=(rr / out_rel).resolve(),
    )


def _sha256_file(path: Path) -> str | None:
    if not path.is_file():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _norm_rel(rr: Path, p: Path) -> str:
    try:
        return str(p.relative_to(rr)).replace("\\", "/")
    except ValueError:
        return str(p.resolve()).replace("\\", "/")


def build_resume_package_manifest(
    *,
    paths: ResumePackageProofPaths,
    docx_emit_path_relative: str,
    rollup_blob: Mapping[str, Any],
    extras: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Single proof manifest listing inputs / hashes / output paths (offline)."""
    rr = paths.repo_root
    now = datetime.now(tz=timezone.utc).isoformat()
    rollup_id = rollup_blob.get("rollup_id")
    out: dict[str, Any] = {
        "manifest_id": "resume_package_manifest_v1",
        "constructed_at_utc": now,
        "constructor_module": "apps_rg.runtime.package.resume_package_manifest",
        "rollup_id_observed_in_generated_lane_rollup": rollup_id,
        "sources": {
            "generated_lane_rollup_json": _norm_rel(rr, paths.rollup_json),
            "locked_copy_manifest_json": _norm_rel(rr, paths.locked_copy_manifest_json),
            "locked_copy_x2_gate_outputs_json": _norm_rel(rr, paths.locked_copy_x2_json),
            "final_resume_json": _norm_rel(rr, paths.final_resume_json),
            "final_resume_manifest_json": _norm_rel(rr, paths.final_resume_manifest_json),
            "final_resume_x2_gate_outputs_json": _norm_rel(rr, paths.final_resume_x2_json),
            "docx_manifest_json": _norm_rel(rr, paths.docx_manifest_json),
            "docx_manifest_x2_gate_outputs_json": _norm_rel(rr, paths.docx_manifest_x2_json),
            "docx_render_manifest_json": _norm_rel(rr, paths.docx_render_manifest_json),
            "docx_render_x2_gate_outputs_json": _norm_rel(rr, paths.docx_render_x2_json),
        },
        "source_sha256_hex": {
            "generated_lane_rollup_json": _sha256_file(paths.rollup_json),
            "locked_copy_manifest_json": _sha256_file(paths.locked_copy_manifest_json),
            "locked_copy_x2_gate_outputs_json": _sha256_file(paths.locked_copy_x2_json),
            "final_resume_json": _sha256_file(paths.final_resume_json),
            "final_resume_manifest_json": _sha256_file(paths.final_resume_manifest_json),
            "final_resume_x2_gate_outputs_json": _sha256_file(paths.final_resume_x2_json),
            "docx_manifest_json": _sha256_file(paths.docx_manifest_json),
            "docx_manifest_x2_gate_outputs_json": _sha256_file(paths.docx_manifest_x2_json),
            "docx_render_manifest_json": _sha256_file(paths.docx_render_manifest_json),
            "docx_render_x2_gate_outputs_json": _sha256_file(paths.docx_render_x2_json),
        },
        "aggregated_proof_outputs": {
            "resume_package_manifest_json": _norm_rel(rr, paths.package_manifest_json()),
            "resume_package_x3_disposition_json": _norm_rel(rr, paths.package_x3_json()),
            "resume_package_receipt_json": _norm_rel(rr, paths.package_receipt_json()),
        },
        "docx_emit_path_repo_relative_expected": docx_emit_path_relative,
        "extras": dict(extras) if extras else {},
    }
    return out


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))
