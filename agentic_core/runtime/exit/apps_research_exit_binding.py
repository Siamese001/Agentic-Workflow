"""Thin Exit binding adapter for apps_research `company_brief` task class.

W7 Exit binding — apps-research-rich-content-runtime-customization-v2.

Per active plan v2: Thin adapter only — no hardcoded Exit policy.
All Exit behavior is package-driven via U0 runtime customization package refs:
- exit_profile.company_brief.v1.json
- required_exit_gates.company_brief.v1.yaml

apps_research is R3_SIMPLE_GROUNDED_READ — no UWG writes, no L4 state mutation.
Artifacts live under artifacts/ only.

This module is a THIN ADAPTER that:
1. Consumes ExitProfile + RequiredExitGates from U0 package
2. Delegates to generic ExitPackageDrivenBinding
3. Emits ExitReviewPacket, ExitDispositionReceipt, RuntimeExhaustBundle

Does NOT:
- Hardcode Exit policy
- Emit X3 from app code
- Write cache/vector/L4
- Call providers
- Retrieve evidence
- Assemble prompts
- Execute tools
- Allow R1B bypass
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
    if isinstance(brief_dict, dict) and "schema_version" not in brief_dict:
        brief_dict = {
            "schema_version": "apps_research.company_brief_failure.v1",
            "output": brief_dict,
            "execution_status": sealed.execution_status,
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

    # Determine exit_status. Product success requires completed L2 output;
    # synthetic fallback output is not an authorized apps_research artifact.
    if sealed.execution_status == "completed":
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
            "stub_mode": False,
        },
        output_artifact_path=artifact_path_str,
        tenant_id=sealed.tenant_id,
        exit_timestamp=exit_ts,
        schema_version="AG9.Exit.1",
        sealed_l2_digest=sealed.compilation_hash,
        l5_certification_ref=APPS_RESEARCH_EXIT_CERT_REF,
    )


# ── W7 Package-Driven Exit Binding Integration ───────────────────────────────

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agentic_core.runtime.exit.exit_package_driven_binding import (
        ExitPackageDrivenBinding,
        ExitInput,
        ExitPolicy,
    )
    from agentic_core.runtime.gates.gate_profile_resolver import GateProfile


def exit_bind_and_finalize_apps_research(
    *,
    gate_profile: "GateProfile",
    exit_policy: "ExitPolicy",
    exit_input: "ExitInput",
    request_id: str,
    run_id: str,
    trace_root: str,
    route_id: str,
    commit_requested: bool = False,
) -> tuple:
    """W7 Package-Driven Exit binding for apps_research.

    Thin adapter that delegates to generic ExitPackageDrivenBinding.
    All app-specific policy comes from U0 runtime package via GateProfile + ExitPolicy.

    Args:
        gate_profile: Gate profile loaded from apps_research U0 package
        exit_policy: Exit policy loaded from apps_research U0 package
        exit_input: Union of SealedL2Artifact/RETTerminalPacket + GateMeshResult
        request_id/run_id/trace_root/route_id: Provenance identifiers
        commit_requested: True if writeback/commit requested

    Returns:
        (ExitReviewPacket, ExitDispositionReceipt, RuntimeExhaustBundle)

    Raises:
        TypeError: on invalid input types
        RuntimeError: on Exit binding failure

    Example:
        >>> from agentic_core.runtime.exit.exit_package_driven_binding import (
        ...     ExitInput, ExitPolicy, ExitPackageDrivenBinding
        ... )
        >>> from agentic_core.runtime.gates.gate_profile_resolver import GateProfile
        >>> gate_profile = GateProfile.from_yaml("apps_research/config/domain_contract/required_exit_gates.company_brief.v1.yaml")
        >>> exit_policy = ExitPolicy.from_dict({...})
        >>> exit_input = ExitInput(
        ...     sealed_l2_artifact=sealed,
        ...     gate_mesh_result=mesh,
        ... )
        >>> review, receipt, exhaust = exit_bind_and_finalize_apps_research(
        ...     gate_profile=gate_profile,
        ...     exit_policy=exit_policy,
        ...     exit_input=exit_input,
        ...     request_id=req_id,
        ...     run_id=run_id,
        ...     trace_root=trace_root,
        ...     route_id=route_id,
        ... )
    """
    # Import here to avoid circular imports at module load time
    from agentic_core.runtime.exit.exit_package_driven_binding import (
        ExitPackageDrivenBinding,
    )

    binding = ExitPackageDrivenBinding(
        gate_profile=gate_profile,
        exit_policy=exit_policy,
        app_id="apps_research",
        task_class="company_brief",
    )

    return binding.bind_and_evaluate(
        exit_input=exit_input,
        request_id=request_id,
        run_id=run_id,
        trace_root=trace_root,
        route_id=route_id,
        commit_requested=commit_requested,
    )


__all__ = [
    "APPS_RESEARCH_EXIT_CERT_REF",
    "exit_finalize_apps_research",  # Legacy — kept for compatibility
    "exit_bind_and_finalize_apps_research",  # W7 Package-Driven
]
