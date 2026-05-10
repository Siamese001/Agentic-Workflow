"""Exit binding for apps_rg `resume_generation` task class.

Per plan apps-rg-runtime-wiring-completion-d4e8a1 §6 W3.P5.

Exit is the SEVENTH and FINAL stage. Its job is to:
1. Write the generated resume JSON to artifacts/apps_rg/runs/<ts>/.
2. Build a typed X3Disposition with exit_status='success',
   outcome_authorized=True, and output_artifact_path pointing at the
   written artifact.
3. Bind the disposition to the upstream SealedL2Artifact for provenance.

W3.P5 SCOPE: real artifact write to disk. Per plan §3 (non-goal: durable
state mutation), the artifact lives under artifacts/ — apps_rg never
writes to UWG / learning ledgers / production state.

When L2 returns execution_status='completed_stub' (W3.P5 stub), the
disposition still finalizes as success because the pipeline reachability
is the W3.P5 acceptance criterion. W5 replaces the stub with a real
LLM call; the artifact path stays the same.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from agentic_core.runtime.contracts.compiled_prompt_artifact import (
    CompiledPromptArtifact,
)
from agentic_core.runtime.contracts.sealed_l2_artifact import SealedL2Artifact
from agentic_core.runtime.contracts.x3_disposition import X3Disposition


APPS_RG_EXIT_CERT_REF: str = "exit-apps-rg-resume-generation-w3p5"
_ARTIFACT_BASE_DIR_RELPATH: str = "artifacts/apps_rg/runs"


def _resolve_repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in [here.parent, *here.parents]:
        if (parent / "pyproject.toml").exists():
            return parent
    return here.parents[3]


def _safe_run_dirname(run_id: str, timestamp_iso: str) -> str:
    """Produce a filesystem-safe directory name for the run artifact.

    Combines an ISO-compact timestamp with the run_id for sortability and
    cross-run uniqueness.
    """
    compact_ts = (
        timestamp_iso
        .replace(":", "")
        .replace("-", "")
        .replace(".", "")
        .replace("+", "_")
        .replace("T", "_")
    )
    safe_run_id = "".join(c for c in run_id if c.isalnum() or c in "._-")
    return f"{compact_ts}_{safe_run_id}"


def _write_artifact(
    sealed: SealedL2Artifact,
    prompt: CompiledPromptArtifact,
    repo_root: Path,
    timestamp_iso: str,
) -> Path:
    """Write generated_content + run metadata to artifacts/apps_rg/runs/<ts_runid>/.

    Returns the path to generated_resume.json. Side-effect: also writes
    a sibling run_metadata.json with prompt + sealed digests for provenance.
    """
    run_dir = (
        repo_root
        / _ARTIFACT_BASE_DIR_RELPATH
        / _safe_run_dirname(sealed.run_id, timestamp_iso)
    )
    run_dir.mkdir(parents=True, exist_ok=True)

    artifact_path = run_dir / "generated_resume.json"
    artifact_path.write_text(sealed.generated_content, encoding="utf-8")

    metadata = {
        "schema_version": "1.0",
        "request_id": sealed.request_id,
        "run_id": sealed.run_id,
        "trace_id": sealed.trace_id,
        "tenant_id": sealed.tenant_id,
        "app_id": sealed.app_id,
        "exit_finalized_at": timestamp_iso,
        "execution_status": sealed.execution_status,
        "execution_duration_ms": sealed.execution_duration_ms,
        "execution_timestamp": sealed.execution_timestamp,
        "sovereign_execution_receipt": sealed.sovereign_execution_receipt,
        "prompt_artifact": {
            "compilation_hash": prompt.compilation_hash,
            "evidence_digest": prompt.evidence_digest,
            "target_model": prompt.target_model,
            "target_provider": prompt.target_provider,
            "blocks_count": len(prompt.prompt_blocks),
            "max_tokens": prompt.max_tokens,
            "temperature": prompt.temperature,
            "schema_version": prompt.schema_version,
        },
        "sealed_l2_artifact": {
            "compilation_hash": sealed.compilation_hash,
            "prompt_artifact_digest": sealed.prompt_artifact_digest,
            "schema_version": sealed.schema_version,
            "state_diff_authorized": sealed.state_diff_authorized,
        },
        "stub_mode": sealed.execution_status in ("completed_stub", "completed_stub_fallback"),
    }
    (run_dir / "run_metadata.json").write_text(
        json.dumps(metadata, indent=2), encoding="utf-8"
    )
    return artifact_path


def exit_finalize_apps_rg(
    sealed: SealedL2Artifact,
    prompt: CompiledPromptArtifact,
) -> X3Disposition:
    """Finalize the apps_rg pipeline by writing the artifact and producing
    the canonical X3Disposition.

    Args:
        sealed: L2 output carrying generated_content + proposed_state_diff.
        prompt: PA output (for provenance metadata in run_metadata.json).

    Returns:
        X3Disposition with exit_status='success' and output_artifact_path
        pointing at the on-disk artifact under artifacts/apps_rg/runs/.

    Raises:
        TypeError: if either argument has the wrong shape.
        OSError: propagated from artifact write failures (caught by dispatch).
    """
    if not isinstance(sealed, SealedL2Artifact):
        raise TypeError(
            f"exit_finalize_apps_rg expected SealedL2Artifact, got {type(sealed).__name__}"
        )
    if not isinstance(prompt, CompiledPromptArtifact):
        raise TypeError(
            f"exit_finalize_apps_rg expected CompiledPromptArtifact, got {type(prompt).__name__}"
        )

    timestamp_iso = datetime.now(timezone.utc).isoformat()
    repo_root = _resolve_repo_root()

    artifact_path = _write_artifact(sealed, prompt, repo_root, timestamp_iso)

    # Final output for chat surface — small summary, not the full resume body.
    final_output = {
        "stage": "EXIT_SUCCESS",
        "execution_status": sealed.execution_status,
        "generated_content_len": len(sealed.generated_content),
        "artifact_relpath": str(artifact_path.relative_to(repo_root)).replace("\\", "/"),
        "artifact_paths": [str(artifact_path.relative_to(repo_root)).replace("\\", "/")],
        "run_id": sealed.run_id,
        "stub_mode": sealed.execution_status in ("completed_stub", "completed_stub_fallback"),
        "sealed_compilation_hash": sealed.compilation_hash,
        "prompt_compilation_hash": prompt.compilation_hash,
        "evidence_digest": prompt.evidence_digest,
        "tenant_id": sealed.tenant_id,
    }

    return X3Disposition(
        request_id=sealed.request_id,
        run_id=sealed.run_id,
        app_id=sealed.app_id,
        trace_id=sealed.trace_id,
        tenant_id=sealed.tenant_id,
        exit_status="success",
        outcome_authorized=True,
        final_output=final_output,
        output_artifact_path=str(artifact_path),
        eval_score=None,
        eval_threshold_met=False,  # eval not run in W3.P5 path
        hitl_required=False,
        exit_timestamp=timestamp_iso,
        sealed_l2_digest=sealed.compilation_hash,
        l5_certification_ref=APPS_RG_EXIT_CERT_REF,
    )


__all__ = [
    "APPS_RG_EXIT_CERT_REF",
    "exit_finalize_apps_rg",
]
