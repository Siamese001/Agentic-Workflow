"""Lane hook: emit section_l7_binding_manifest after section-domain receipts exist."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from apps_rg.runtime.section_l7_binding_manifest import build_section_l7_binding_manifest
from apps_rg.runtime.section_evidence_package import (
    discover_integrated_correlation,
    finalize_section_evidence_package,
)


def finalize_section_l7_binding(
    artifact_dir: Path,
    *,
    section_id: str,
    runtime_payload: dict[str, Any],
    repo_root: Path,
    command_surface: str | None = None,
) -> Path:
    """Emit L7 binding manifest + evidence package indexes (refs only; no L7 emit)."""
    run_id = str(runtime_payload.get("run_id") or artifact_dir.name)
    surface = command_surface or f"python -m apps_rg --section {section_id}"
    correlation = discover_integrated_correlation(
        repo_root, artifact_dir, section_id=section_id
    )
    binding_doc = build_section_l7_binding_manifest(
        repo_root=repo_root,
        artifact_dir=artifact_dir,
        section_id=section_id,
        run_id=run_id,
        command_surface=surface,
        correlation=correlation,
    )
    path = artifact_dir / "section_l7_binding_manifest.json"
    path.write_text(json.dumps(binding_doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    corr = runtime_payload.get("correlation_id")
    correlation_id = str(corr).strip() if corr is not None and str(corr).strip() else None
    pkg_summary = finalize_section_evidence_package(
        repo_root=repo_root,
        artifact_dir=artifact_dir,
        section_id=section_id,
        run_id=run_id,
        binding_manifest=binding_doc,
        correlation_id=correlation_id,
        correlation=correlation,
    )
    runtime_payload["section_l7_binding_manifest_ref"] = path.name
    runtime_payload["evidence_package_index_ref"] = pkg_summary[
        "evidence_package_index_path"
    ].name
    runtime_payload["spine_subphase_coverage_index_ref"] = pkg_summary[
        "subphase_coverage_index_path"
    ].name
    return path


__all__ = ["finalize_section_l7_binding"]
