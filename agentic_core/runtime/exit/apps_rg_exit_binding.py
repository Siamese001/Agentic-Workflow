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
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Optional

from agentic_core.runtime.exit.hitl_policy_registry import (
    HitlPolicySpec,
    load_hitl_policy_table,
    resolve_hitl_policy,
)

from agentic_core.runtime.contracts.compiled_prompt_artifact import (
    CompiledPromptArtifact,
)
from agentic_core.runtime.contracts.final_evidence_contract import FinalEvidenceContract
from agentic_core.runtime.contracts.sealed_l2_artifact import SealedL2Artifact
from agentic_core.runtime.contracts.x3_disposition import X3Disposition
from apps_rg.exit.apps_rg_exit_evidence_builder import (
    FactualGroundingResult as _FactualGroundingResult,
    HeaderRepairResult as _HeaderRepairResult,
    MissingPerInputHashError as _MissingPerInputHashError,
    build_g24_provenance as _build_g24_provenance,
    compute_factual_grounding as _compute_factual_grounding,
    compute_g22_rubric_scores as _compute_deterministic_dim_scores,
    seal_resume_sections as _seal_resume_sections,
)


APPS_RG_EXIT_CERT_REF: str = "exit-apps-rg-resume-generation-w3p5"
_ARTIFACT_BASE_DIR_RELPATH: str = "artifacts/apps_rg/runs"
_EXIT_LOGGER: logging.Logger = logging.getLogger(__name__)


def _safe_build_g24_provenance(
    sealed: SealedL2Artifact,
    prompt: CompiledPromptArtifact,
    pkg: Any,
) -> dict[str, Any]:
    """Wrap build_g24_provenance with honest-fail semantics.

    When pkg is absent or any required per-input hash is missing from
    component_hash_map, returns {} so G24 evaluates UNKNOWN rather than
    falsely PASS on a fallback aggregate hash.
    """
    if pkg is None:
        return {}
    try:
        return _build_g24_provenance(sealed, prompt, pkg)
    except _MissingPerInputHashError as exc:
        _EXIT_LOGGER.warning(
            "G24 provenance omitted — %s",
            exc,
        )
        return {}


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
    fec: Optional[FinalEvidenceContract] = None,
) -> X3Disposition:
    """Finalize the apps_rg pipeline by writing the artifact and producing
    the canonical X3Disposition.

    Args:
        sealed: L2 output carrying generated_content + proposed_state_diff.
        prompt: PA output (for provenance metadata in run_metadata.json).
        fec: Optional FinalEvidenceContract from C0.  When present (grounded
             runs), factual_grounding is computed and added to g22_rubric_scores
             evidence for G22.  When None (generate_scratch), factual_grounding
             remains absent and G22 stays UNKNOWN on that dimension.

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

    # ── Exit gate evaluation ──────────────────────────────────────────────────
    # Two-pass approach for G28 post-mesh audit:
    #   Pass 1 — evaluate G21/G22/G23/G24/G26 + first-pass G28 with
    #             sealed_workflow_package_ref already known.
    #   Pass 2 — evaluate G28 again with gate_mesh_result_ref and
    #             decisive_reason from Pass-1 receipt (Option 1).
    # Fail-soft: harness evaluation failure must never block artifact delivery.
    _gate_receipt = None
    _mesh_result = None
    _exhaust = None
    _g28_post_mesh_verdict = None
    _gate_verdict_refs: tuple[str, ...] = ()
    _outcome_authorized: bool = False
    _hitl_required: bool = False
    _exit_status_from_harness: str = "blocked"
    _header_repair = _HeaderRepairResult(repaired=False, header_dict={}, source_evidence_ref="")

    try:
        # Parse generated content for G22 dim scoring (None if unparseable).
        _parsed: dict[str, Any] | None = None
        try:
            _parsed = json.loads(sealed.generated_content) if sealed.generated_content else None
        except (json.JSONDecodeError, TypeError):
            pass

        # Seal L2 resume sections into canonical SealedSectionArtifact objects.
        # seal_resume_sections maps L2 flat keys → canonical section IDs.
        # When header absent from LLM output and fec contains source resume,
        # deterministic repair extracts header fields from source resume evidence.
        # header_block is NEVER synthesised from target_company/target_role/target_level.
        _sealed_sections, _header_repair = _seal_resume_sections(_parsed, sealed.run_id, fec)
        _merged_content: str = sealed.generated_content or ""

        # Build SealedWorkflowPackage with real sections and merged content.
        # Import lazily to avoid circular-import risk.
        try:
            from agentic_core.runtime.contracts.sealed_workflow_types import (  # noqa: PLC0415
                SealedWorkflowPackage,
            )
            _pkg = SealedWorkflowPackage(
                package_id=f"pkg::apps_rg::{sealed.run_id}",
                run_id=sealed.run_id,
                trace_root=sealed.trace_id,
                route_contract_ref="rcr::apps_rg::resume_generation::v1",
                workflow_ref="wfm::apps_rg::resume_generation::v1",
                workflow_manifest_ref="wfm::apps_rg::resume_generation::v1",
                sealed_sections=_sealed_sections,
                section_count=len(_sealed_sections),
                merged_content=_merged_content,
                merged_content_digest=sealed.compilation_hash,
                merged_payload_digest=prompt.compilation_hash,
                replay_manifest=sealed.compilation_hash,
            )
        except Exception:  # guardian: allow-broad-exception -- pkg construction is best-effort
            _pkg = None  # type: ignore[assignment]

        # Pass 1: supply sealed_workflow_package_ref (available now).
        # gate_mesh_result_ref and decisive_reason are not yet known — G28
        # will return UNKNOWN on this pass; corrected by post-mesh Pass 2.
        # Merge deterministic dim scores with factual_grounding when FEC is available.
        _dim_scores = _compute_deterministic_dim_scores(_parsed, sealed)
        _fg_result: _FactualGroundingResult | None = None
        if fec is not None:
            _fg_result = _compute_factual_grounding(_parsed, fec)
            if _fg_result is not None:
                _dim_scores["factual_grounding"] = _fg_result.score
                # Recompute overall_pass_threshold with factual_grounding included.
                _all_dims = [v for k, v in _dim_scores.items()
                             if k != "overall_pass_threshold" and isinstance(v, float)]
                if _all_dims:
                    _dim_scores["overall_pass_threshold"] = round(
                        len(_all_dims) / sum(1.0 / max(d, 1e-9) for d in _all_dims), 4
                    )

        evidence: dict[str, Any] = {
            "g22_rubric_scores": _dim_scores,
            "g24_provenance": _safe_build_g24_provenance(sealed, prompt, _pkg),
            "g28": {
                "output_artifact_path": str(artifact_path),
                "sealed_compilation_hash": sealed.compilation_hash,
                "audit_refs": {
                    "sealed_workflow_package_ref": _pkg.package_id if _pkg else "",
                },
            },
        }

        _harness = build_apps_rg_exit_harness(repo_root=repo_root)
        _gate_receipt, _mesh_result, _exhaust = _harness.evaluate(
            _pkg,
            evidence=evidence,
            request_id=sealed.request_id,
            run_id=sealed.run_id,
            trace_root=sealed.trace_id,
        )

        # ── Persist Pass-1 mesh result + optional exhaust (NOT the receipt yet) ──
        # 07_gate_receipt.json is written AFTER Pass-2 so it contains both
        # g28_initial_verdict and g28_post_mesh_verdict (Patch B).
        _run_dir = artifact_path.parent
        try:
            _run_dir.mkdir(parents=True, exist_ok=True)
            (_run_dir / "07_gate_mesh_result.json").write_text(
                _mesh_result.as_json(), encoding="utf-8"
            )
            if _exhaust is not None:
                try:
                    (_run_dir / "07_runtime_exhaust.json").write_text(
                        _exhaust.as_json(), encoding="utf-8"
                    )
                except Exception:  # guardian: allow-broad-exception -- exhaust serialization is optional
                    pass
        except Exception:  # guardian: allow-broad-exception -- proof artifact write is fail-soft
            pass

        # ── Persist G22 factual_grounding diagnostics artifact (Patch A) ─────
        # Written independently of gate verdict — diagnostics never change pass/fail.
        if _fg_result is not None:
            try:
                _fg_diag_payload: dict[str, Any] = {
                    "schema_version": "1.0",
                    "gate_id": "G22",
                    "dimension": "factual_grounding",
                    "run_id": sealed.run_id,
                    "score": _fg_result.score,
                    "supported_token_samples": _fg_result.supported_token_samples,
                    "unsupported_token_samples": _fg_result.unsupported_token_samples,
                    "source_evidence_refs": _fg_result.source_evidence_refs,
                    "decisive_reason": _fg_result.decisive_reason,
                }
                (_run_dir / "07_g22_factual_grounding_diagnostics.json").write_text(
                    json.dumps(_fg_diag_payload, indent=2, ensure_ascii=False),
                    encoding="utf-8",
                )
            except Exception:  # guardian: allow-broad-exception -- diagnostics write is fail-soft
                pass

        # ── Pass 2: post-mesh G28 audit with real gate_mesh_result_ref ───────
        # Re-evaluate G28 only, using the receipt fields now known from Pass 1.
        _g28_initial_verdict_dict: dict[str, Any] | None = None
        try:
            from agentic_core.runtime.gates.gate_evaluators import (  # noqa: PLC0415
                evaluate_g28,
            )
            # Capture Pass-1 G28 verdict for dual-verdict receipt.
            _pass1_g28 = next(
                (v for v in _mesh_result.verdicts if v.gate_id == "G28"), None
            )
            if _pass1_g28 is not None:
                try:
                    _g28_initial_verdict_dict = json.loads(_pass1_g28.as_json())
                except Exception:  # guardian: allow-broad-exception -- serialization is optional
                    pass

            _g28_gate_def = _harness._profile.gate_definitions.get("G28", {})  # noqa: SLF001
            _g28_post_mesh_evidence: dict[str, Any] = {
                "g28": {
                    "output_artifact_path": str(artifact_path),
                    "sealed_compilation_hash": sealed.compilation_hash,
                    "audit_refs": {
                        "sealed_workflow_package_ref": _pkg.package_id if _pkg else "",
                        "gate_mesh_result_ref": _gate_receipt.gate_mesh_result_ref,
                        "decisive_reason": _gate_receipt.decisive_reason,
                    },
                },
            }
            _g28_post_mesh_verdict = evaluate_g28(
                "G28",
                _g28_gate_def,
                _pkg,
                _g28_post_mesh_evidence,
                request_id=sealed.request_id,
                run_id=sealed.run_id,
                trace_root=sealed.trace_id,
            )
            try:
                (_run_dir / "07_g28_post_mesh_verdict.json").write_text(
                    _g28_post_mesh_verdict.as_json(), encoding="utf-8"
                )
            except Exception:  # guardian: allow-broad-exception -- verdict write is fail-soft
                pass
        except Exception:  # guardian: allow-broad-exception -- post-mesh G28 evaluation is fail-soft
            _g28_post_mesh_verdict = None

        # ── Persist 07_gate_receipt.json AFTER Pass-2 (Patch B) ──────────────
        # Includes both g28_initial_verdict and g28_post_mesh_verdict so the
        # receipt clearly shows the two-pass audit chain.
        # When Pass-1 was blocked solely by the circular G28 dependency and
        # post-mesh G28 is PASS/WARN, the on-disk receipt is updated to reflect
        # the authorized outcome so it stays consistent with 07_Exit_disposition.json.
        _pass1_blocked_only_by_g28_for_receipt = (
            not _gate_receipt.allows_finish
            and set(_gate_receipt.decisive_blocker_gate_ids) == {"G28"}
        )
        _g28_post_ok_for_receipt = (
            _g28_post_mesh_verdict is not None
            and _g28_post_mesh_verdict.result in ("PASS", "WARN")
        )
        try:
            from agentic_core.runtime.exit.exit_disposition import X3D_ALLOW_FINISH as _X3D  # noqa: PLC0415
            _receipt_dict: dict[str, Any] = json.loads(_gate_receipt.as_json())
            # If post-mesh G28 authorized the run, update Pass-1 fields that
            # were set based on the circular G28 failure.  Initial verdict is
            # preserved in g28_audit_chain.g28_initial_verdict.
            if _pass1_blocked_only_by_g28_for_receipt and _g28_post_ok_for_receipt:
                _receipt_dict["x3_code"] = _X3D
                _receipt_dict["decisive_reason"] = (
                    f"post_mesh_g28_{_g28_post_mesh_verdict.result.lower()}: "
                    "all material audit refs satisfied after mesh"
                )
                _receipt_dict["decisive_blocker_gate_ids"] = []
                _receipt_dict["decisive_blocker_codes"] = []
                _receipt_dict["required_gates_passed"] = True
                _receipt_dict["hard_fail_count"] = 0
                _receipt_dict["post_mesh_authorization"] = {
                    "authorized": True,
                    "reason": "pass1_blocked_only_by_circular_g28_dependency",
                    "post_mesh_g28_result": _g28_post_mesh_verdict.result,
                    "post_mesh_g28_digest": _g28_post_mesh_verdict.deterministic_digest,
                }
            # Attach dual G28 verdict fields under app-owned diagnostics key.
            _receipt_dict["g28_audit_chain"] = {
                "g28_initial_verdict": _g28_initial_verdict_dict,
                "g28_post_mesh_verdict": (
                    json.loads(_g28_post_mesh_verdict.as_json())
                    if _g28_post_mesh_verdict is not None
                    else None
                ),
                "factual_grounding_diagnostics_ref": (
                    "07_g22_factual_grounding_diagnostics.json"
                    if _fg_result is not None
                    else None
                ),
            }
            # Record deterministic header repair audit field.
            _receipt_dict["deterministic_header_repair"] = {
                "repaired": _header_repair.repaired,
                "source_evidence_ref": _header_repair.source_evidence_ref,
            }
            (_run_dir / "07_gate_receipt.json").write_text(
                json.dumps(_receipt_dict, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
        except Exception:  # guardian: allow-broad-exception -- receipt write is fail-soft
            # Fallback: write the plain receipt without the dual-verdict extension.
            try:
                (_run_dir / "07_gate_receipt.json").write_text(
                    _gate_receipt.as_json(), encoding="utf-8"
                )
            except Exception:  # guardian: allow-broad-exception -- fallback receipt write is fail-soft
                pass

        # ── Build gate_verdict_refs from Pass-1 mesh + post-mesh G28 ─────────
        _verdict_map: dict[str, Any] = {
            v.gate_id: v for v in _mesh_result.verdicts
        }
        # Substitute post-mesh G28 verdict if it improved on UNKNOWN
        if _g28_post_mesh_verdict is not None:
            _verdict_map["G28"] = _g28_post_mesh_verdict

        _gate_verdict_refs = tuple(
            f"{v.gate_id}::{v.result}::{v.deterministic_digest}"
            for v in _verdict_map.values()
        )

        # ── Determine final authorization from harness + post-mesh G28 ───────
        # Pass-1 receipt x3_code reflects G21/G22/G23/G24/G26 plus first-pass G28.
        # Post-mesh G28 may upgrade or block.
        from agentic_core.runtime.exit.exit_disposition import (  # noqa: PLC0415
            X3A_DENY_REROUTE,
            X3B_ESCALATE_HITL,
            X3D_ALLOW_FINISH,
        )
        _pass1_allows = _gate_receipt.x3_code == X3D_ALLOW_FINISH
        _pass1_blocked_only_by_g28 = (
            not _gate_receipt.allows_finish
            and set(_gate_receipt.decisive_blocker_gate_ids) == {"G28"}
        )
        _g28_post_ok = (
            _g28_post_mesh_verdict is not None
            and _g28_post_mesh_verdict.result in ("PASS", "WARN")
        )

        if _pass1_allows:
            # All gates including first-pass G28 passed — final authorization.
            _outcome_authorized = True
            _hitl_required = False
            _exit_status_from_harness = "success"
        elif _pass1_blocked_only_by_g28 and _g28_post_ok:
            # Pass-1 was blocked solely because G28 lacked post-mesh refs.
            # Post-mesh G28 now passes/warns — authorize.
            _outcome_authorized = True
            _hitl_required = False
            _exit_status_from_harness = "success"
        else:
            # Hard fail or UNKNOWN in G21/G22/G23/G24/G26, or G28 post-mesh
            # still fails/unknown — do not authorize.
            _outcome_authorized = False
            _hitl_required = _gate_receipt.x3_code == X3B_ESCALATE_HITL
            _exit_status_from_harness = (
                "blocked_hitl" if _hitl_required else "blocked_denied"
            )

    except Exception:  # guardian: allow-broad-exception -- gate evaluation is advisory; must not block exit artifact delivery
        # Fall back to conservative values — do not authorize when harness fails.
        _outcome_authorized = False
        _gate_verdict_refs = ()
        _exit_status_from_harness = "blocked"

    # Final output for chat surface — small summary, not the full resume body.
    final_output = {
        "stage": "EXIT_SUCCESS" if _outcome_authorized else "EXIT_BLOCKED",
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
        exit_status=_exit_status_from_harness,
        outcome_authorized=_outcome_authorized,
        final_output=final_output,
        output_artifact_path=str(artifact_path),
        eval_score=None,
        eval_threshold_met=False,  # eval not run in W3.P5 path
        hitl_required=_hitl_required,
        exit_timestamp=timestamp_iso,
        sealed_l2_digest=sealed.compilation_hash,
        gate_verdict_refs=_gate_verdict_refs,
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
        app_id="apps_rg",
        task_class="resume_generation",
    )


# ---------------------------------------------------------------------------
# Exit gate consumers — wired across two plans:
#   W5 fields:  apps-rg-quarantine-gap-remediation-8f405c W5.P2
#   DF-1/2/3:  apps-rg-deferred-follow-ons-b3e9f1 W1-W3
#
# Reads provenance_requirements, output_requirements, and profile_manifest
# from ValidatedRequest.app_payload.
#
# Actual field names from contract (apps_rg_ingress_contract_v1.py):
#   ProvenanceRequirementsSection: per_bullet_required (bool), source_quote_required (bool)
#   OutputRequirementsSection: formats (tuple[str]), provenance_required (bool),
#                              fact_checked_required (bool)
#   ProfileManifestSection.hitl_policy_ref — WIRED (DF-1): resolved via
#     hitl_policy_registry.resolve_hitl_policy() → HitlPolicySpec; requires_hitl
#     flag propagated to gate result for HITL routing agent.
#   fact_checked_required — WIRED (DF-2): blocking gate (fail-closed default);
#     APPS_RG_FACT_CHECK_FAIL_CLOSED=0 to soften.
#   formats — WIRED (DF-3): DOCX renderer dispatched when "docx" in formats.
#
# Fail-soft by default (WARN / NOT_APPLICABLE).
# APPS_RG_PROVENANCE_GATE_FAIL_CLOSED=1 converts provenance WARN into FAIL.
# APPS_RG_FACT_CHECK_FAIL_CLOSED defaults to 1 (fail-closed for fact-check).
# APPS_RG_HITL_REGISTRY_FAIL_CLOSED=1 treats unknown HITL refs as requires_hitl=True.
# ---------------------------------------------------------------------------

_PROVENANCE_GATE_FAIL_CLOSED_ENV: str = "APPS_RG_PROVENANCE_GATE_FAIL_CLOSED"
_FACT_CHECK_FAIL_CLOSED_ENV: str = "APPS_RG_FACT_CHECK_FAIL_CLOSED"
_HITL_REGISTRY_FAIL_CLOSED_ENV: str = "APPS_RG_HITL_REGISTRY_FAIL_CLOSED"

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
    hitl_policy_spec: Optional[HitlPolicySpec]
    payload_path: str
    fail_closed: bool
    fact_check_fail_closed: bool


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
    fact_check_fail_closed = os.environ.get(_FACT_CHECK_FAIL_CLOSED_ENV, "1").strip() == "1"
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
        _hitl_table = load_hitl_policy_table(
            "apps_rg/config/domain_contract/hitl_policies.resume_generation.v1.yaml"
        )
        hitl_spec = resolve_hitl_policy(hitl_ref, policy_table=_hitl_table)

        return AppsRGExitGatePolicy(
            per_bullet_required=per_bullet,
            source_quote_required=source_quote,
            output_provenance_required=out_provenance,
            fact_checked_required=fact_checked,
            output_formats=output_formats,
            hitl_policy_ref=hitl_ref,
            hitl_policy_spec=hitl_spec,
            payload_path=payload_path,
            fail_closed=fail_closed,
            fact_check_fail_closed=fact_check_fail_closed,
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
            hitl_policy_spec=None,
            payload_path=payload_path,
            fail_closed=fail_closed,
            fact_check_fail_closed=fact_check_fail_closed,
        )


def _dispatch_docx_renderer(sealed_artifact: Any) -> dict[str, Any]:
    """Invoke tools/apps_rg/resume_docx_renderer.render() for the run artifact.

    Fail-soft: any error returns {status: 'error', error: <msg>}.
    Requires python-docx; absent in CI lightweight environments is handled
    gracefully (skipped, not a gate FAIL).

    Args:
        sealed_artifact: SealedL2Artifact or None. If None the artifact path
                         is resolved from the most recent run directory.

    Returns:
        {status: 'ok', path: <docx_path>} on success,
        {status: 'error', error: <msg>} on any failure.
    """
    try:
        repo_root = _resolve_repo_root()
        run_id = getattr(sealed_artifact, "run_id", None) if sealed_artifact else None
        run_dir: Path | None = None
        if run_id:
            run_dir = _find_existing_run_dir(repo_root, run_id)
        if run_dir is None:
            # Fallback: most recent run directory
            base = repo_root / _ARTIFACT_BASE_DIR_RELPATH
            if base.exists():
                candidates = sorted(
                    [d for d in base.iterdir() if d.is_dir()], key=lambda d: d.name, reverse=True
                )
                run_dir = candidates[0] if candidates else None
        if run_dir is None:
            return {"status": "error", "error": "no run directory found for DOCX render"}

        json_path = run_dir / "generated_resume.json"
        if not json_path.exists():
            return {"status": "error", "error": f"generated_resume.json not found at {json_path}"}

        docx_path = run_dir / "generated_resume.docx"

        try:
            import json as _json  # noqa: PLC0415
            from tools.apps_rg.resume_docx_renderer import render  # noqa: PLC0415

            with open(json_path, encoding="utf-8") as _fh:
                resume_data = _json.load(_fh)

            default_template = Path(r"C:\Users\amita\Documents\Resumes\SVP Engineering Resume_Ayer.docx")
            if not default_template.exists():
                return {"status": "error", "error": f"DOCX template not found at {default_template}; skipped"}

            render(resume_data, docx_path, default_template)
            return {"status": "ok", "path": str(docx_path)}

        except ImportError as ie:
            return {"status": "error", "error": f"python-docx not available: {ie}"}

    except Exception as exc:  # guardian: allow-broad-exception -- DOCX renderer dispatch is fail-soft; renderer failure must not block Exit
        return {"status": "error", "error": str(exc)}


def evaluate_apps_rg_exit_provenance_gate(
    policy: AppsRGExitGatePolicy,
    sealed_artifact: Any = None,
    run_context: Any = None,
) -> dict[str, Any]:
    """Evaluate provenance and output requirement gates at Exit.

    Checks (as of apps-rg-deferred-follow-ons-b3e9f1):
      - output_requirements.provenance_required: consistency check with
        per_bullet_required (PASS/WARN/FAIL).
      - profile_manifest.hitl_policy_ref: resolved via hitl_policy_registry
        (AG-13.b) to HitlPolicySpec; requires_hitl=True emits hitl_required
        flag in gate result (not a blocking FAIL — HITL routing agent acts on it).
      - output_requirements.fact_checked_required: if True, checks
        run_context.fact_check_receipt is non-null; missing receipt → FAIL
        (fail-closed default, APPS_RG_FACT_CHECK_FAIL_CLOSED=0 to soften).
      - output_requirements.formats: dispatches DOCX renderer after gate pass
        when 'docx' is present; other formats logged as metadata.

    Args:
        policy: Extracted exit gate policy.
        sealed_artifact: Optional SealedL2Artifact (reserved).
        run_context: Optional object/dict with fact_check_receipt field.

    Returns:
        Gate result dict with verdict, per-field verdicts, hitl_required flag,
        and renderer_dispatched list.
    """
    results: dict[str, Any] = {
        "gate": "EXIT_PROVENANCE_GATE",
        "plan": "apps-rg-deferred-follow-ons-b3e9f1",
        "wave": "W1-W3",
        "policy": {
            "per_bullet_required": policy.per_bullet_required,
            "source_quote_required": policy.source_quote_required,
            "output_provenance_required": policy.output_provenance_required,
            "fact_checked_required": policy.fact_checked_required,
            "output_formats": list(policy.output_formats) if policy.output_formats else None,
            "hitl_policy_ref": policy.hitl_policy_ref,
            "fail_closed": policy.fail_closed,
            "fact_check_fail_closed": policy.fact_check_fail_closed,
        },
        "field_verdicts": {},
        "policy_metadata": {},
        "deferred": {},
        "hitl_required": False,
        "hitl_policy_spec": None,
        "renderer_dispatched": [],
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

    # fact_checked_required — DF-2: blocking gate (fail-closed by default)
    if policy.fact_checked_required is not None:
        if policy.fact_checked_required:
            fact_check_receipt = None
            if run_context is not None:
                if isinstance(run_context, dict):
                    fact_check_receipt = run_context.get("fact_check_receipt")
                else:
                    fact_check_receipt = getattr(run_context, "fact_check_receipt", None)
            if fact_check_receipt is not None:
                results["field_verdicts"]["fact_checked_required"] = "PASS"
                results["policy_metadata"]["fact_check_receipt"] = str(fact_check_receipt)
                checks.append("PASS")
            else:
                verdict = "FAIL" if policy.fact_check_fail_closed else "WARN"
                results["field_verdicts"]["fact_checked_required"] = verdict
                results["policy_metadata"]["fact_check_missing_note"] = (
                    "fact_checked_required=True but run_context.fact_check_receipt is absent; "
                    f"gate verdict={verdict} (APPS_RG_FACT_CHECK_FAIL_CLOSED={'1' if policy.fact_check_fail_closed else '0'})"
                )
                checks.append(verdict)
        else:
            results["field_verdicts"]["fact_checked_required"] = "PASS"
            checks.append("PASS")

    # output formats — DF-3: dispatch renderer callbacks (DOCX wired; others metadata)
    if policy.output_formats is not None:
        results["policy_metadata"]["output_formats"] = list(policy.output_formats)
        dispatched: list[str] = []
        skipped: list[str] = []
        for fmt in policy.output_formats:
            fmt_lower = str(fmt).strip().lower()
            if fmt_lower == "json":
                dispatched.append("json")  # natively produced
            elif fmt_lower == "docx":
                _docx_result = _dispatch_docx_renderer(sealed_artifact)
                if _docx_result.get("status") == "ok":
                    dispatched.append("docx")
                    results["policy_metadata"]["docx_artifact_path"] = _docx_result.get("path", "")
                else:
                    skipped.append(f"docx:{_docx_result.get('error', 'unknown')}")
            else:
                skipped.append(fmt_lower)
        results["renderer_dispatched"] = dispatched
        if skipped:
            results["policy_metadata"]["formats_skipped"] = skipped
        if dispatched:
            results["field_verdicts"]["output_formats"] = "PASS"
            checks.append("PASS")

    # hitl_policy_ref — resolved via AG-13.b HITL registry (DF-1 wired)
    if policy.hitl_policy_ref is not None:
        spec = policy.hitl_policy_spec
        if spec is not None and spec.resolved:
            results["field_verdicts"]["hitl_policy_ref"] = "PASS"
            results["hitl_required"] = spec.requires_hitl
            results["hitl_policy_spec"] = {
                "policy_ref": spec.policy_ref,
                "trigger_kind": spec.trigger_kind,
                "requires_hitl": spec.requires_hitl,
                "trigger_threshold": spec.trigger_threshold,
                "operator_id": spec.operator_id,
                "policy_version": spec.policy_version,
                "resolved": spec.resolved,
            }
            checks.append("PASS")
        else:
            results["field_verdicts"]["hitl_policy_ref"] = "WARN"
            results["policy_metadata"]["hitl_policy_ref_note"] = (
                f"hitl_policy_ref={policy.hitl_policy_ref!r} unrecognised in registry; "
                "treated as no-HITL (fail-soft)"
            )
            results["hitl_required"] = False
            results["hitl_policy_spec"] = {
                "policy_ref": policy.hitl_policy_ref,
                "trigger_kind": "UNKNOWN",
                "requires_hitl": False,
                "resolved": False,
            }
            checks.append("WARN")

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
    "_dispatch_docx_renderer",
]
