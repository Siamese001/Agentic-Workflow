"""Assembly manifest helpers for final resume (filesystem SSOT, no providers)."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from apps_rg.runtime.locked_copy.locked_copy_manifest import find_repo_root


@dataclass
class FinalResumePaths:
    repo_root: Path
    rollup_json: Path
    locked_manifest: Path
    locked_x2: Path
    base_resume: Path
    output_dir: Path

    def rel(self, p: Path) -> str:
        try:
            return p.relative_to(self.repo_root).as_posix()
        except ValueError:
            return p.resolve().as_posix()


DEFAULT_ROLLUP_REL = Path("artifacts/apps_rg/runtime_proofs/generated_lane_rollup/generated_lane_rollup.json")
DEFAULT_LOCKED_REL = Path("artifacts/apps_rg/runtime_proofs/locked_copy")
DEFAULT_OUTPUT_REL = Path("artifacts/apps_rg/runtime_proofs/final_resume_assembly")


def resolve_default_paths(repo: Path | None = None) -> FinalResumePaths:
    root = repo or find_repo_root()
    locked = root / DEFAULT_LOCKED_REL
    return FinalResumePaths(
        repo_root=root,
        rollup_json=root / DEFAULT_ROLLUP_REL,
        locked_manifest=locked / "locked_copy_manifest.json",
        locked_x2=locked / "locked_copy_x2_gate_outputs.json",
        base_resume=root / "apps_rg/resume/base/amit_ayer_base_resume_v1.json",
        output_dir=root / DEFAULT_OUTPUT_REL,
    )


def build_assembly_manifest(
    *,
    paths: FinalResumePaths,
    rollup_id: str,
    rollup_generated_at_utc: str,
    gates_passed: int,
    gates_total: int,
    failed_gate_ids: list[str],
    final_resume_hash: str,
) -> dict[str, Any]:
    return {
        "manifest_id": "final_resume_assembly_manifest_v1",
        "assembled_at_utc": datetime.now(timezone.utc).isoformat(),
        "rollup_id_source": rollup_id,
        "rollup_generated_at_utc_source": rollup_generated_at_utc,
        "inputs": {
            "generated_lane_rollup": paths.rel(paths.rollup_json),
            "locked_copy_manifest": paths.rel(paths.locked_manifest),
            "locked_copy_x2_gate_outputs": paths.rel(paths.locked_x2),
            "canonical_base_resume": paths.rel(paths.base_resume),
        },
        "outputs": {
            "final_resume": paths.rel(paths.output_dir / "final_resume.json"),
            "assembly_manifest": paths.rel(paths.output_dir / "final_resume_manifest.json"),
            "final_resume_x2_gate_outputs": paths.rel(paths.output_dir / "final_resume_x2_gate_outputs.json"),
            "final_resume_receipt": paths.rel(paths.output_dir / "final_resume_receipt.json"),
        },
        "gates": {
            "passed": gates_passed,
            "total": gates_total,
            "failed_gate_ids": failed_gate_ids,
        },
        "final_resume_hash": final_resume_hash,
        "calls": {
            "provider_calls_made": False,
            "qwen_calls_made": False,
            "judge_calls_made": False,
            "docx_rendered": False,
        },
    }
