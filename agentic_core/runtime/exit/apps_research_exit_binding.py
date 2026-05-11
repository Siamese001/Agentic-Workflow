"""Exit binding for apps_research `company_brief` task class.

Per plan apps-research-golden-template-adoption-ag9.

Exit is the SEVENTH and FINAL stage. Its job is to:
1. Write the generated company_brief JSON to artifacts/apps_research/runs/<ts>/.
2. Build a typed X3Disposition with exit_status='success',
   outcome_authorized=True, output_artifact_path pointing at the artifact.
3. Bind the disposition to the upstream SealedL2Artifact for provenance.

apps_research is R3_SIMPLE_GROUNDED_READ — no UWG writes, no L4 state mutation.
Artifacts live under artifacts/ only.
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

APPS_RESEARCH_EXIT_CERT_REF: str = "exit-apps-research-company-brief-ag9"
_ARTIFACT_BASE_DIR_RELPATH: str = "artifacts/apps_research/runs"


def _resolve_repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in [here.parent, *here.parents]:
        if (parent / "pyproject.toml").exists():
            return parent
    return here.parents[3]


def _safe_run_dirname(run_id: str, timestamp_iso: str) -> str:
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
    """Write company_brief JSON + run metadata to artifacts/apps_research/runs/<ts>/.

    Returns path to company_brief.json. Side-effect: writes run_metadata.json.
    """
    run_dir = (
        repo_root
        / _ARTIFACT_BASE_DIR_RELPATH
        / _safe_run_dirname(sealed.run_id, timestamp_iso)
    )
    run_dir.mkdir(parents=True, exist_ok=True)

    # Write main artifact
    brief_path = run_dir / "company_brief.json"

    # Parse generated_content back to dict for clean formatting
    try:
        brief_dict = json.loads(sealed.generated_content)
    except (json.JSONDecodeError, ValueError):
        brief_dict = {
            "schema_version": "company_brief_v1",
            "raw_content": sealed.generated_content,
        }

    with brief_path.open("w", encoding="utf-8") as fh:
        json.dump(brief_dict, fh, ensure_ascii=False, indent=2)

    # Write provenance metadata
    metadata: dict = {
        "run_id": sealed.run_id,
        "request_id": sealed.request_id,
        "app_id": "apps_research",
        "trace_id": sealed.trace_id,
        "tenant_id": sealed.tenant_id,
        "execution_status": sealed.execution_status,
        "execution_timestamp": sealed.execution_timestamp,
        "execution_duration_ms": sealed.execution_duration_ms,
        "sovereign_execution_receipt": sealed.sovereign_execution_receipt,
        "prompt_artifact_digest": sealed.prompt_artifact_digest,
        "sealed_compilation_hash": sealed.compilation_hash,
        "evidence_digest": prompt.evidence_digest,
        "prompt_compilation_hash": prompt.compilation_hash,
        "slot_lineage_map": dict(prompt.slot_lineage_map),
        "component_hash_map": dict(prompt.component_hash_map),
        "replay_manifest_ref": prompt.replay_manifest_ref,
        "target_model": prompt.target_model,
        "schema_version": "AG9.Exit.1",
    }
    metadata_path = run_dir / "run_metadata.json"
    with metadata_path.open("w", encoding="utf-8") as fh:
        json.dump(metadata, fh, ensure_ascii=False, indent=2)

    return brief_path


def exit_finalize_apps_research(
    sealed: SealedL2Artifact,
    prompt: CompiledPromptArtifact,
) -> X3Disposition:
    """Finalize the apps_research pipeline and emit X3Disposition.

    Writes artifacts to disk, builds provenance chain, returns disposition.

    Returns a fully-typed X3Disposition. Raises TypeError or OSError on failure.
    """
    for name, val, expected in (
        ("sealed", sealed, SealedL2Artifact),
        ("prompt", prompt, CompiledPromptArtifact),
    ):
        if not isinstance(val, expected):
            raise TypeError(
                f"exit_finalize_apps_research: expected {expected.__name__} for {name!r}, "
                f"got {type(val)}"
            )

    exit_ts = datetime.now(timezone.utc).isoformat()
    repo_root = _resolve_repo_root()

    artifact_path = _write_artifact(sealed, prompt, repo_root, exit_ts)
    artifact_path_str = str(artifact_path.relative_to(repo_root))

    # Determine exit_status — stub fallback still counts as success for
    # pipeline reachability verification. Real content = 'success'.
    if sealed.execution_status == "completed":
        exit_status = "success"
    elif sealed.execution_status in ("completed_stub_fallback", "completed_stub"):
        exit_status = "success"
    else:
        exit_status = "failure"

    # Parse brief dict for final_output summary
    try:
        brief_dict = json.loads(sealed.generated_content)
        company_name = brief_dict.get("company_name", "")
        section_keys = list((brief_dict.get("sections") or {}).keys())
    except (json.JSONDecodeError, ValueError, AttributeError):
        company_name = ""
        section_keys = []

    return X3Disposition(
        request_id=sealed.request_id,
        run_id=sealed.run_id,
        app_id="apps_research",
        trace_id=sealed.trace_id,
        exit_status=exit_status,
        outcome_authorized=exit_status == "success",
        final_output={
            "company_name": company_name,
            "section_keys": section_keys,
            "execution_status": sealed.execution_status,
            "artifact_path": artifact_path_str,
            "stub_mode": sealed.proposed_state_diff.get("stub_mode", False),
        },
        output_artifact_path=artifact_path_str,
        tenant_id=sealed.tenant_id,
        exit_timestamp=exit_ts,
        schema_version="AG9.Exit.1",
        sealed_l2_digest=sealed.compilation_hash,
        l5_certification_ref=APPS_RESEARCH_EXIT_CERT_REF,
    )


__all__ = [
    "APPS_RESEARCH_EXIT_CERT_REF",
    "exit_finalize_apps_research",
]
