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

import dataclasses
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Optional

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


def _find_existing_run_dir(repo_root: Path, run_id: str) -> Path | None:
    """Find an already-created run directory matching run_id (from dispatch stage persistence)."""
    base = repo_root / _ARTIFACT_BASE_DIR_RELPATH
    if not base.exists():
        return None
    safe_id = "".join(c for c in run_id if c.isalnum() or c in "._-")
    for d in base.iterdir():
        if d.is_dir() and safe_id in d.name:
            return d
    return None


def _write_artifact(
    sealed: SealedL2Artifact,
    prompt: CompiledPromptArtifact,
    repo_root: Path,
    timestamp_iso: str,
) -> Path:
    """Write generated_content + run metadata to artifacts/apps_rg/runs/<ts_runid>/.

    Returns the path to generated_resume.json. Side-effect: also writes
    a sibling run_metadata.json with prompt + sealed digests for provenance.

    If dispatch already created a run directory (with stages/ inside),
    reuses that directory to keep all artifacts co-located.
    """
    existing = _find_existing_run_dir(repo_root, sealed.run_id)
    if existing is not None:
        run_dir = existing
    else:
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

    # Semantic cache writeback — two-path:
    #   Path 1: learn() → Redis L1 (hot, 24h TTL)
    #   Path 2: VectorRetrievalService.add_documents() → apps_rg_intent ChromaDB (durable)
    # Both are fail-soft: writeback failure must never block the exit path.
    _sc_intent = sealed.generated_content[:256] if sealed.generated_content else sealed.run_id
    _sc_output = sealed.generated_content[:8192] if sealed.generated_content else ""

    # Path 1 — Redis L1 (ephemeral hot cache)
    try:
        from agentic_core.L4_state.utils.memory.semantic_cache_manager import (  # noqa: PLC0415
            SemanticCacheManager,
        )

        _sc = SemanticCacheManager.get_instance()
        _sc.learn(
            context=_sc_intent,
            namespace="apps_rg",
            result={
                "output": _sc_output,
                "app": "apps_rg",
                "run_id": sealed.run_id,
                "artifact_path": str(artifact_path),
            },
            tenant_id=sealed.tenant_id or "",
        )
    except Exception:  # guardian: allow-broad-exception -- semantic cache writeback is best-effort; infrastructure may be absent in test environments
        pass

    # Path 2 — apps_rg_intent ChromaDB collection (durable, survives Redis TTL)
    try:
        from tools.retrieval.vector_service import VectorRetrievalService  # noqa: PLC0415

        _iv_vrs = VectorRetrievalService()
        if _sc_intent.strip():
            _iv_vrs.add_documents(
                collection_name="apps_rg_intent",
                documents=[_sc_intent],
                metadatas=[
                    {
                        "app": "apps_rg",
                        "run_id": sealed.run_id,
                        "tenant_id": sealed.tenant_id or "",
                        "output_preview": _sc_output[:256],
                        "artifact_path": str(artifact_path),
                    }
                ],
            )
    except Exception:  # guardian: allow-broad-exception -- intent vector writeback is best-effort; ChromaDB may be absent
        pass

    # C0 output chunk writeback — write generated content chunks to apps_rg_c0
    # ChromaDB collection so future C0 retrieval can leverage prior outputs.
    # Fail-soft: never block exit on vector DB unavailability.
    try:
        from tools.retrieval.vector_service import VectorRetrievalService  # noqa: PLC0415

        _content = sealed.generated_content or ""
        if _content.strip():
            _vrs = VectorRetrievalService()
            _coll = "apps_rg_c0"
            try:
                _vrs.create_collection(_coll)
            except Exception:  # guardian: allow-broad-exception -- collection may already exist
                pass
            # Split content into ~1024-char chunks for embedding granularity.
            _chunk_size = 1024
            _chunks = [_content[i : i + _chunk_size] for i in range(0, len(_content), _chunk_size)]
            _chunks = [c for c in _chunks if c.strip()][:16]
            if _chunks:
                _metas = [
                    {
                        "app": "apps_rg",
                        "run_id": sealed.run_id,
                        "tenant_id": sealed.tenant_id or "",
                        "chunk_index": idx,
                        "total_chunks": len(_chunks),
                    }
                    for idx, _ in enumerate(_chunks)
                ]
                _vrs.add_documents(
                    collection_name=_coll,
                    documents=_chunks,
                    metadatas=_metas,
                )
    except Exception:  # guardian: allow-broad-exception -- C0 chunk writeback is best-effort; ChromaDB may be absent
        pass

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


_APPS_RG_EXIT_PROFILE_PATH = (
    "apps_rg/config/domain_contract/exit_profile.resume_generation.v1.json"
)
_APPS_RG_RUNTIME_GATE_PROFILE_PATH = (
    "apps_rg/config/domain_contract/runtime_gate_profile.resume_generation.v1.json"
)


def build_apps_rg_exit_harness(
    repo_root: "Path | None" = None,
) -> "ExitGateHarness":
    """Convenience factory for the apps_rg Exit harness.

    Loads the apps_rg gate profile from disk.  Does NOT hardcode any
    gate rules — all rules come from the profile JSON files.
    """
    from agentic_core.runtime.exit.exit_gate_harness import ExitGateHarness
    from agentic_core.runtime.gates.gate_profile_resolver import GateProfileResolver

    root = repo_root or _resolve_repo_root()
    resolver = GateProfileResolver(root)
    profile = resolver.resolve(
        exit_profile_path=_APPS_RG_EXIT_PROFILE_PATH,
        runtime_gate_profile_path=_APPS_RG_RUNTIME_GATE_PROFILE_PATH,
    )
    return ExitGateHarness(
        gate_profile=profile,
    )


# ---------------------------------------------------------------------------
# W5 Exit gate consumers — apps-rg-quarantine-gap-remediation-8f405c W5.P2
#
# Reads provenance_requirements, output_requirements, and profile_manifest
# from ValidatedRequest.app_payload.
#
# Actual field names from contract (apps_rg_ingress_contract_v1.py):
#   ProvenanceRequirementsSection: per_bullet_required (bool), source_quote_required (bool)
#   OutputRequirementsSection: formats (tuple[str]), provenance_required (bool),
#                              fact_checked_required (bool)
#   ProfileManifestSection.hitl_policy_ref — DEFERRED: no HITL consumer at Exit yet.
#     Ref is extracted and logged as policy metadata only; hitl_policy_ref triggers
#     land in future Wave 4 HITL registry (AG-13.b). hitl_policy_ref MUST NOT be
#     evaluated as a gate verdict at Exit.
#
# Fail-soft by default (WARN / NOT_APPLICABLE).
# APPS_RG_PROVENANCE_GATE_FAIL_CLOSED=1 converts WARN into FAIL.
# ---------------------------------------------------------------------------

_PROVENANCE_GATE_FAIL_CLOSED_ENV: str = "APPS_RG_PROVENANCE_GATE_FAIL_CLOSED"

_EXIT_LOGGER = __import__("logging").getLogger(__name__)


@dataclasses.dataclass(frozen=True)
class AppsRGExitGatePolicy:
    """Extracted provenance + output requirements from apps_rg app_payload."""

    per_bullet_required: Optional[bool]
    source_quote_required: Optional[bool]
    output_provenance_required: Optional[bool]
    fact_checked_required: Optional[bool]
    output_formats: Optional[tuple]
    hitl_policy_ref: Optional[str]
    payload_path: str
    fail_closed: bool


def extract_apps_rg_exit_gate_policy(validated_request: Any) -> AppsRGExitGatePolicy:
    """Extract provenance_requirements, output_requirements from ValidatedRequest.app_payload.

    Also extracts profile_manifest.hitl_policy_ref as POLICY METADATA only
    (deferred — no HITL consumer at Exit; returned for downstream observability).

    Actual fields consumed:
      provenance_requirements.per_bullet_required (bool)
      provenance_requirements.source_quote_required (bool)
      output_requirements.provenance_required (bool)
      output_requirements.fact_checked_required (bool)
      output_requirements.formats (tuple[str, ...])
      profile_manifest.hitl_policy_ref (str, DEFERRED — metadata only)

    Returns NOT_APPLICABLE policy with None values on any extraction failure.
    Never raises.

    Args:
        validated_request: ValidatedRequest carrying app_payload.

    Returns:
        AppsRGExitGatePolicy with field values or None for absent data.
    """
    fail_closed = os.environ.get(_PROVENANCE_GATE_FAIL_CLOSED_ENV, "").strip() == "1"
    payload_path = (
        "ValidatedRequest.app_payload."
        "{provenance_requirements,output_requirements,profile_manifest.hitl_policy_ref}"
    )

    def _getattr_or_dict(obj: Any, key: str) -> Any:
        if obj is None:
            return None
        if isinstance(obj, dict):
            return obj.get(key)
        return getattr(obj, key, None)

    try:
        app_payload = validated_request.app_payload
        prov_req = _getattr_or_dict(app_payload, "provenance_requirements")
        out_req = _getattr_or_dict(app_payload, "output_requirements")
        prof_manifest = _getattr_or_dict(app_payload, "profile_manifest")

        per_bullet = _getattr_or_dict(prov_req, "per_bullet_required")
        source_quote = _getattr_or_dict(prov_req, "source_quote_required")
        out_provenance = _getattr_or_dict(out_req, "provenance_required")
        fact_checked = _getattr_or_dict(out_req, "fact_checked_required")
        formats_raw = _getattr_or_dict(out_req, "formats")
        output_formats = tuple(formats_raw) if formats_raw is not None else None
        hitl_ref = _getattr_or_dict(prof_manifest, "hitl_policy_ref")

        return AppsRGExitGatePolicy(
            per_bullet_required=per_bullet,
            source_quote_required=source_quote,
            output_provenance_required=out_provenance,
            fact_checked_required=fact_checked,
            output_formats=output_formats,
            hitl_policy_ref=hitl_ref,
            payload_path=payload_path,
            fail_closed=fail_closed,
        )
    except Exception as exc:  # guardian: allow-broad-exception -- policy extraction must never abort Exit; missing policy is WARN not ERROR
        _EXIT_LOGGER.warning("[apps_rg Exit gate] policy extraction failed: %s", exc)
        return AppsRGExitGatePolicy(
            per_bullet_required=None,
            source_quote_required=None,
            output_provenance_required=None,
            fact_checked_required=None,
            output_formats=None,
            hitl_policy_ref=None,
            payload_path=payload_path,
            fail_closed=fail_closed,
        )


def evaluate_apps_rg_exit_provenance_gate(
    policy: AppsRGExitGatePolicy,
    sealed_artifact: Any = None,
) -> dict[str, Any]:
    """Evaluate provenance and output requirement gates at Exit.

    Checks:
      - output_requirements.provenance_required: if True and per_bullet_required
        is also True, both flags are verified as consistent (PASS), else WARN.
      - provenance_requirements.per_bullet_required / source_quote_required:
        emitted as policy metadata for future per-bullet gate (AG-9.b).
      - output_requirements.fact_checked_required: emitted as policy metadata
        (fact-check engine restoration deferred; gap category #61).
      - output_requirements.formats: emitted as policy metadata.
      - profile_manifest.hitl_policy_ref: extracted as DEFERRED metadata only.
        NEVER evaluated as a gate verdict at Exit — HITL registry (AG-13.b) not
        yet wired; evaluating before the registry lands would produce false FAILs.

    Fail-soft: no live gate produces FAIL in fail_closed=False mode for
    currently un-evaluable checks (e.g. per-bullet provenance enforcement
    requires output artifact scanner, not available at Exit yet).

    Args:
        policy: Extracted exit gate policy.
        sealed_artifact: Optional SealedL2Artifact (reserved; not consumed yet).

    Returns:
        Gate result dict with verdict, per-field verdicts, and policy metadata.
    """
    results: dict[str, Any] = {
        "gate": "EXIT_PROVENANCE_GATE",
        "plan": "apps-rg-quarantine-gap-remediation-8f405c",
        "wave": "W5.P2",
        "policy": {
            "per_bullet_required": policy.per_bullet_required,
            "source_quote_required": policy.source_quote_required,
            "output_provenance_required": policy.output_provenance_required,
            "fact_checked_required": policy.fact_checked_required,
            "output_formats": list(policy.output_formats) if policy.output_formats else None,
            "hitl_policy_ref": policy.hitl_policy_ref,
            "fail_closed": policy.fail_closed,
        },
        "field_verdicts": {},
        "policy_metadata": {},
        "deferred": {},
    }

    checks: list[str] = []

    # provenance_required + per_bullet_required consistency check
    if policy.output_provenance_required is not None:
        if policy.output_provenance_required:
            if policy.per_bullet_required is True:
                results["field_verdicts"]["provenance_consistency"] = "PASS"
                checks.append("PASS")
            elif policy.per_bullet_required is False:
                verdict = "FAIL" if policy.fail_closed else "WARN"
                results["field_verdicts"]["provenance_consistency"] = verdict
                results["policy_metadata"]["provenance_inconsistency_note"] = (
                    "output_requirements.provenance_required=True but "
                    "provenance_requirements.per_bullet_required=False; flags are inconsistent"
                )
                checks.append(verdict)
            else:
                results["field_verdicts"]["provenance_consistency"] = "NOT_APPLICABLE"
                results["policy_metadata"]["per_bullet_required_note"] = (
                    "per_bullet_required absent; provenance consistency check skipped"
                )
                checks.append("NOT_APPLICABLE")
        else:
            results["field_verdicts"]["provenance_required"] = "PASS"
            checks.append("PASS")

    # per_bullet_required — emitted as deferred metadata (gate enforcement
    # requires per-bullet scanner; deferred to AG-9.b W2 gate registry)
    if policy.per_bullet_required is not None:
        results["deferred"]["per_bullet_required"] = {
            "value": policy.per_bullet_required,
            "status": "DEFERRED",
            "reason": (
                "per-bullet provenance scanner lands at W2 gate registry (AG-9.b); "
                "Exit carries this flag as deferred metadata only"
            ),
        }

    # source_quote_required — deferred to W5 RunReport provenance manifest emitter
    if policy.source_quote_required is not None:
        results["deferred"]["source_quote_required"] = {
            "value": policy.source_quote_required,
            "status": "DEFERRED",
            "reason": (
                "source-quote evidence emitter lands with Exit-stage callback at W5 (AG-14.a)"
            ),
        }

    # fact_checked_required — deferred to gap category #61 (fact-check engine restoration)
    if policy.fact_checked_required is not None:
        results["deferred"]["fact_checked_required"] = {
            "value": policy.fact_checked_required,
            "status": "DEFERRED",
            "reason": (
                "fact_check_engine restoration is gap category #61; "
                "gate registry invokes when engine lands (AG-9.b)"
            ),
        }

    # output formats — carried as policy metadata; callback registry deferred to W5
    if policy.output_formats is not None:
        results["policy_metadata"]["output_formats"] = list(policy.output_formats)
        results["deferred"]["output_formats"] = {
            "value": list(policy.output_formats),
            "status": "DEFERRED",
            "reason": (
                "DOCX/RunReport callbacks register against output_formats at W5 (AG-14.a)"
            ),
        }

    # hitl_policy_ref — DEFERRED, extracted as metadata only.
    # AG-13.b HITL registry does not exist at Exit yet. Evaluating this field
    # here would produce false results. We carry it for audit/observability only.
    if policy.hitl_policy_ref:
        results["deferred"]["hitl_policy_ref"] = {
            "value": policy.hitl_policy_ref,
            "status": "DEFERRED",
            "reason": (
                "hitl_registry not yet wired at Exit; HITL triggers land in "
                "future Wave 4 HITL registry (AG-13.b). "
                "hitl_policy_ref carried as audit metadata only."
            ),
        }

    if not checks:
        results["verdict"] = "NOT_APPLICABLE"
        results["reason"] = (
            "no evaluable provenance/output requirements found in payload; "
            "deferred fields extracted as metadata"
        )
    elif "FAIL" in checks:
        results["verdict"] = "FAIL"
    elif "WARN" in checks:
        results["verdict"] = "WARN"
    elif all(c == "NOT_APPLICABLE" for c in checks):
        results["verdict"] = "NOT_APPLICABLE"
    else:
        results["verdict"] = "PASS"

    return results


__all__ = [
    "APPS_RG_EXIT_CERT_REF",
    "AppsRGExitGatePolicy",
    "extract_apps_rg_exit_gate_policy",
    "evaluate_apps_rg_exit_provenance_gate",
    "exit_finalize_apps_rg",
    "build_apps_rg_exit_harness",
]
