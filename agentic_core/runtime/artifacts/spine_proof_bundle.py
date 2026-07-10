"""Canonical SpineProofBundle builder for the agentic_core runtime spine.

Emits ``agentic_core_spine_proof.json`` as the LAST artifact of the
integrated-runtime W2 chain. The bundle is the single rollup that
points to every other artifact by sha256 hash, declares spine status,
captures runtime mode + mock/fixture/synthetic detection flags, and
enumerates blocking_gaps[] when refs are missing.

The bundle is itself stamped via the integrated_runtime_emitter so it
inherits the full hash chain + producer-component anti-cheat regex
+ no-harness-stamp invariant.

R1B terminal-shortcircuit semantics:
    - ``runtime_l3_receipt_ref`` MUST be null.
    - ``runtime_l3_bypass_ref`` MUST be present.
    - ``runtime_c0_receipt_ref`` MUST point to the C0 BYPASS receipt
      (FinalEvidenceContract is not produced for cache-reuse).
    - ``runtime_prompt_assembly_ref`` MUST point to the PA BYPASS receipt
      (CompiledPromptArtifact is not produced for cache-reuse).
    - ``static_dag_ref`` MAY be null with ``static_dag_sha256=""`` —
      this pass does not implement static DAG proof.
    - ``runtime_l2_artifact_ref`` MAY be null only if the terminal
      shortcircuit is proven (terminal_ret_packet.no_l2_execution_assertion).
    - ``runtime_exhaust_ref`` MUST be present.
    - ``uwg_commit_or_block_ref`` MAY be null on the cache-reuse path
      (UWG is not invoked because there is no state diff).
    - ``otel_or_runtime_trace_ref`` MAY be null in this pass (OTEL is
      live but no per-run trace artifact is produced yet).

``success`` is False if any required ref is missing.
"""

from __future__ import annotations

import json
import os
import subprocess
import time
from pathlib import Path
from typing import Any, Mapping

from agentic_core.L6_observability.runtime_trace.synthetic_trace_detector import (
    detect_trace_provenance,
)

PROOF_SCHEMA_VERSION = "1.0"
HARNESS_SCHEMA_VERSION = "w2.r1b.1.0"
RUNTIME_SUBJECT = "agentic_core"


def _read_json(path: Path) -> Any:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def git_commit_and_dirty(repo_root: Path | None = None) -> tuple[str, bool]:
    """Best-effort ``(git_commit, git_dirty)``. Subprocess hardened.

    Pure-stdlib, ``shell=False``, 10s timeout, returns empty/False on any
    failure. Public helper so the integrated entry point can stamp the
    same git state into both the RuntimeIdentityEnvelope and the
    SpineProofBundle (continuity).
    """
    if repo_root is None:
        repo_root = Path(__file__).resolve().parents[3]
    commit = ""
    dirty = False
    try:
        commit = subprocess.run(  # noqa: S603 - argv list, shell=False
            ["git", "rev-parse", "HEAD"],
            cwd=str(repo_root), shell=False, check=False, timeout=10,
            capture_output=True, text=True,
        ).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        commit = ""
    try:
        result = subprocess.run(  # noqa: S603 - argv list, shell=False
            ["git", "status", "--porcelain"],
            cwd=str(repo_root), shell=False, check=False, timeout=10,
            capture_output=True, text=True,
        )
        dirty = bool(result.stdout.strip())
    except (OSError, subprocess.SubprocessError):
        dirty = False
    return commit, dirty


# Internal alias kept for the in-file caller; new code should import
# ``git_commit_and_dirty``.
_git_state = git_commit_and_dirty


def _env_bool(name: str, default: bool) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _env_str(name: str, default: str) -> str:
    raw = os.environ.get(name)
    if raw is None or not raw.strip():
        return default
    return raw.strip()


def build_spine_proof_payload(
    *,
    artifact_dir: Path,
    artifact_hashes: Mapping[str, str],
    identity_envelope_payload: Mapping[str, Any],
    started_at_utc: str,
    finished_at_utc: str,
    exit_code: int,
    runtime_mode: str | None = None,
    mock_mode_detected: bool | None = None,
    fixture_mode_detected: bool | None = None,
    synthetic_trace_detected: bool | None = None,
    extra_blocking_gaps: list[str] | None = None,
    repo_root: Path | None = None,
    chain_kind: str = "R1B",
) -> dict[str, Any]:
    """Build the SpineProofBundle payload for the R1B terminal-shortcircuit path.

    The caller (the integrated entry point) supplies what it has emitted;
    this builder discovers what's missing on disk and records every
    finding into ``blocking_gaps[]``.

    Environment overrides (test/dev only):
        AGENTIC_CORE_RUNTIME_MODE       — overrides ``runtime_mode``
        AGENTIC_CORE_MOCK_MODE          — overrides ``mock_mode_detected``
        AGENTIC_CORE_FIXTURE_MODE       — overrides ``fixture_mode_detected``
        AGENTIC_CORE_SYNTHETIC_TRACE    — overrides ``synthetic_trace_detected``
    """
    artifact_dir = Path(artifact_dir)
    if repo_root is None:
        repo_root = Path(__file__).resolve().parents[3]

    # Resolve detection flags. Caller value wins over auto-detection
    # only when the caller explicitly passed True. Auto-detection (env
    # vars + manifest inspection + synthetic-seed marker) is delegated
    # to the SSOT detector in
    # ``agentic_core.L6_observability.runtime_trace.synthetic_trace_detector``.
    if runtime_mode is None:
        runtime_mode = _env_str("AGENTIC_CORE_RUNTIME_MODE", "production")

    auto = detect_trace_provenance(artifact_dir)
    if mock_mode_detected is None:
        mock_mode_detected = auto.mock_mode_detected
    else:
        mock_mode_detected = bool(mock_mode_detected) or auto.mock_mode_detected
    if fixture_mode_detected is None:
        fixture_mode_detected = auto.fixture_mode_detected
    else:
        fixture_mode_detected = bool(fixture_mode_detected) or auto.fixture_mode_detected
    if synthetic_trace_detected is None:
        synthetic_trace_detected = auto.synthetic_trace_detected
    else:
        synthetic_trace_detected = bool(synthetic_trace_detected) or auto.synthetic_trace_detected
    trace_provenance_reasons = list(auto.reasons)

    # Continuity rule: prefer the git state already captured into the
    # RuntimeIdentityEnvelope so the two artifacts cannot disagree. Only
    # fall back to subprocess when the envelope didn't carry it (legacy
    # callers, partial runs).
    git_commit = str(identity_envelope_payload.get("git_commit") or "")
    if not git_commit:
        git_commit, _ = git_commit_and_dirty(repo_root)
    git_dirty_raw = identity_envelope_payload.get("git_dirty")
    if isinstance(git_dirty_raw, bool):
        git_dirty = git_dirty_raw
    else:
        _, git_dirty = git_commit_and_dirty(repo_root)

    # --- Required refs per chain kind ---
    if chain_kind == "MANAGED_WORKFLOW":
        REQUIRED_FILES = (
            "integrated_runtime_entrypoint_invocation.json",
            "runtime_identity_envelope.json",
            "validated_request.json",
            "l1_plan_contract.json",
            "route_contract.json",
            "static_dag_proof.json",
            "runtime_l3_orchestration_receipt.json",
            "l2_sealed_artifact.json",
            "c0_bypass_receipt.json",
            "prompt_assembly_bypass_receipt.json",
            "runtime_gate_verdict_bundle.json",
            "exit_review_packet.json",
            "x3_disposition_receipt.json",
            "runtime_exhaust_bundle.json",
            "runtime_trace_snapshot.json",
            "agentic_core_how_trace.json",
            "agentic_core_l7_route_family_coverage.json",
            "integrated_runtime_artifact_manifest.json",
            "no_harness_stamp_receipt.json",
        )
    else:
        # R1B default
        REQUIRED_FILES = (
            "integrated_runtime_entrypoint_invocation.json",
            "runtime_identity_envelope.json",
            "validated_request.json",
            "l1_plan_contract.json",
            "route_contract.json",
            "l3_bypass_receipt.json",
            "c0_bypass_receipt.json",
            "prompt_assembly_bypass_receipt.json",
            "runtime_gate_verdict_bundle.json",
            "semantic_cache_safe_reuse_decision.json",
            "terminal_ret_packet.json",
            "exit_review_packet.json",
            "x3_disposition_receipt.json",
            "runtime_exhaust_bundle.json",
            "runtime_trace_snapshot.json",
            "agentic_core_how_trace.json",
            "agentic_core_l7_route_family_coverage.json",
            "integrated_runtime_artifact_manifest.json",
            "no_harness_stamp_receipt.json",
        )

    blocking: list[str] = []

    def _hash_or_none(filename: str) -> str | None:
        h = artifact_hashes.get(filename)
        if h:
            return h
        # Fallback: read envelope from disk.
        env = _read_json(artifact_dir / filename)
        if isinstance(env, dict):
            recorded = env.get("artifact_hash")
            if isinstance(recorded, str) and recorded:
                return recorded
        return None

    # Identity / intake / plan / route refs.
    runtime_identity_ref = _hash_or_none("runtime_identity_envelope.json")
    runtime_intake_ref = _hash_or_none("validated_request.json")
    runtime_l1_plan_ref = _hash_or_none("l1_plan_contract.json")
    runtime_route_contract_ref = _hash_or_none("route_contract.json")

    # L3: chain-kind dispatch. MW runs emit a runtime receipt; R1B runs
    # emit a bypass. Both are mutually exclusive.
    if chain_kind == "MANAGED_WORKFLOW":
        runtime_l3_receipt_ref = _hash_or_none("runtime_l3_orchestration_receipt.json")
        runtime_l3_bypass_ref: str | None = None
    else:
        runtime_l3_receipt_ref = None
        runtime_l3_bypass_ref = _hash_or_none("l3_bypass_receipt.json")

    # C0 + PA: both bypass for the structural-only paths in this pass.
    runtime_c0_receipt_ref = _hash_or_none("c0_bypass_receipt.json")
    runtime_prompt_assembly_ref = _hash_or_none(
        "prompt_assembly_bypass_receipt.json"
    )

    # L2: R1B terminal shortcircuit doesn't emit a sealed artifact (no
    # L2 ran). MW chain emits a structural-only L2SealedArtifact bound
    # to the L3 step contracts.
    runtime_l2_artifact_ref: str | None = _hash_or_none("l2_sealed_artifact.json")
    terminal_env = _read_json(artifact_dir / "terminal_ret_packet.json")
    if isinstance(terminal_env, dict):
        tp = terminal_env.get("payload", {}) or {}
        if bool(tp.get("l2_recipe_executed")):
            runtime_l2_artifact_ref = _hash_or_none("terminal_ret_packet.json")
        elif not bool(tp.get("no_l2_execution_assertion")) and not runtime_l2_artifact_ref:
            blocking.append(
                "terminal_ret_packet.no_l2_execution_assertion is not True "
                "AND no l2_sealed_artifact.json present; runtime_l2_artifact_ref required"
            )

    # Exit + exhaust.
    runtime_exit_disposition_ref = _hash_or_none("x3_disposition_receipt.json")
    runtime_exhaust_ref = _hash_or_none("runtime_exhaust_bundle.json")

    # UWG: cache-reuse and structural MW do not commit; null is allowed.
    uwg_commit_or_block_ref: str | None = _hash_or_none("blocked_commit_receipt.json")

    # OTEL / runtime trace snapshot — canonical per-run artifact.
    otel_or_runtime_trace_ref: str | None = _hash_or_none(
        "runtime_trace_snapshot.json"
    )

    # Manifest + verifier result refs.
    artifact_manifest_ref = _hash_or_none(
        "integrated_runtime_artifact_manifest.json"
    )
    verifier_result_ref: str | None = None  # populated by record_w2_verifier_results

    # ── L7_AUDITABILITY HOW trace refs ──
    # The HOW trace is mandatory; spine bundle MUST point to it.
    how_trace_ref = _hash_or_none("agentic_core_how_trace.json")
    how_trace_env = _read_json(artifact_dir / "agentic_core_how_trace.json")
    how_trace_status = ""
    if isinstance(how_trace_env, dict):
        ht_payload = how_trace_env.get("payload", {}) or {}
        ht_success = bool(ht_payload.get("success", False))
        how_trace_status = (
            "L7_HOW_TRACE_PROVEN" if ht_success else "L7_HOW_TRACE_BLOCKED"
        )
    if not how_trace_ref:
        blocking.append(
            "agentic_core_how_trace.json missing — L7_AUDITABILITY plane "
            "requires a HOW trace for every governed run"
        )
        how_trace_status = "L7_HOW_TRACE_MISSING"

    # ── L7 route-family coverage matrix refs ──
    # Mandatory honest accounting of route-family L7 coverage.
    rfc_ref = _hash_or_none("agentic_core_l7_route_family_coverage.json")
    rfc_env = _read_json(
        artifact_dir / "agentic_core_l7_route_family_coverage.json"
    )
    rfc_status = ""
    rfc_summary: dict[str, Any] = {}
    if isinstance(rfc_env, dict):
        rfc_payload = rfc_env.get("payload", {}) or {}
        rfc_summary = dict(rfc_payload.get("summary", {}) or {})
        # Status surfaces whether *any* route family is CERTIFIED in this run.
        # If certified>=1, status=PROVEN (the run-family is real-runtime).
        # If structural_only>=1 and certified==0, STRUCTURAL_ONLY.
        # If everything is NOT_CERTIFIED, MISSING.
        cert_n = int(rfc_summary.get("certified", 0) or 0)
        struct_n = int(rfc_summary.get("structural_only", 0) or 0)
        if cert_n >= 1:
            rfc_status = "L7_ROUTE_FAMILY_COVERAGE_PROVEN"
        elif struct_n >= 1:
            rfc_status = "L7_ROUTE_FAMILY_COVERAGE_STRUCTURAL_ONLY"
        else:
            rfc_status = "L7_ROUTE_FAMILY_COVERAGE_MISSING"
    if not rfc_ref:
        blocking.append(
            "agentic_core_l7_route_family_coverage.json missing — "
            "L7_AUDITABILITY plane requires a route-family coverage matrix "
            "for every governed run"
        )
        rfc_status = "L7_ROUTE_FAMILY_COVERAGE_MISSING"

    # --- blocking-gap accumulation ---
    for fn in REQUIRED_FILES:
        h = _hash_or_none(fn)
        if not h:
            blocking.append(f"required artifact missing or hashless: {fn}")

    # Static DAG: populated for MW runs; null for R1B.
    static_dag_ref: str | None = None
    static_dag_sha256 = ""
    if chain_kind == "MANAGED_WORKFLOW":
        static_dag_ref = _hash_or_none("static_dag_proof.json")
        sdp_env = _read_json(artifact_dir / "static_dag_proof.json")
        if isinstance(sdp_env, dict):
            sdp_payload = sdp_env.get("payload", {}) or {}
            static_dag_sha256 = str(sdp_payload.get("dag_sha256", ""))

    # Identity continuity check across artifacts.
    expected_run_id = identity_envelope_payload.get("run_id")
    expected_request_id = identity_envelope_payload.get("request_id")
    expected_trace_root = identity_envelope_payload.get("trace_root")

    continuity_files = (
        "validated_request.json",
        "l1_plan_contract.json",
        "route_contract.json",
        "l3_bypass_receipt.json",
        "runtime_l3_orchestration_receipt.json",
        "c0_bypass_receipt.json",
        "prompt_assembly_bypass_receipt.json",
        "terminal_ret_packet.json",
        "exit_review_packet.json",
    )
    for fn in continuity_files:
        env = _read_json(artifact_dir / fn)
        if not isinstance(env, dict):
            continue
        p = env.get("payload", {}) or {}
        if "request_id" in p and p.get("request_id") not in (
            expected_request_id, "", None,
        ):
            blocking.append(
                f"{fn}: request_id={p.get('request_id')!r} != identity.request_id={expected_request_id!r}"
            )
        if "trace_root" in p and p.get("trace_root") not in (
            expected_trace_root, "", None,
        ):
            blocking.append(
                f"{fn}: trace_root={p.get('trace_root')!r} != identity.trace_root={expected_trace_root!r}"
            )

    if extra_blocking_gaps:
        blocking.extend(extra_blocking_gaps)

    success = (exit_code == 0) and (not blocking)

    # spine_status is a fixed vocabulary so verifiers can match exactly.
    if chain_kind == "MANAGED_WORKFLOW":
        spine_status = (
            "MW_STRUCTURAL_ONLY_PROVEN" if not blocking
            else "MW_STRUCTURAL_ONLY_BLOCKED"
        )
    elif chain_kind == "R1A_EXACT_CACHE":
        spine_status = (
            "R1A_EXACT_CACHE_PROVEN" if not blocking
            else "R1A_EXACT_CACHE_BLOCKED"
        )
    elif chain_kind == "R5_FALLBACK":
        spine_status = (
            "R5_FALLBACK_PROVEN" if not blocking
            else "R5_FALLBACK_BLOCKED"
        )
    elif chain_kind == "UWG_BLOCK_PATH":
        spine_status = (
            "UWG_BLOCK_PATH_PROVEN" if not blocking
            else "UWG_BLOCK_PATH_BLOCKED"
        )
    elif chain_kind == "UWG_COMMIT_PATH":
        spine_status = (
            "UWG_COMMIT_PATH_PROVEN" if not blocking
            else "UWG_COMMIT_PATH_BLOCKED"
        )
    elif chain_kind == "R3_GROUNDED_READ":
        spine_status = (
            "R3_GROUNDED_READ_PROVEN" if not blocking
            else "R3_GROUNDED_READ_BLOCKED"
        )
    elif chain_kind == "R4_SINGLE_ACTION":
        spine_status = (
            "R4_SINGLE_ACTION_PROVEN" if not blocking
            else "R4_SINGLE_ACTION_BLOCKED"
        )
    elif chain_kind == "MANAGED_WORKFLOW_REAL_EXECUTION":
        spine_status = (
            "MW_REAL_EXECUTION_PROVEN" if not blocking
            else "MW_REAL_EXECUTION_BLOCKED"
        )
    else:
        spine_status = (
            "R1B_TERMINAL_SHORTCIRCUIT_PROVEN" if not blocking
            else "R1B_TERMINAL_SHORTCIRCUIT_BLOCKED"
        )

    return {
        "proof_schema_version": PROOF_SCHEMA_VERSION,
        "harness_schema_version": HARNESS_SCHEMA_VERSION,
        "runtime_subject": RUNTIME_SUBJECT,
        "run_id": expected_run_id or "",
        "request_id": expected_request_id or "",
        "trace_root": expected_trace_root or "",
        "started_at_utc": started_at_utc,
        "finished_at_utc": finished_at_utc,
        "exit_code": int(exit_code),
        "git_commit": git_commit,
        "git_dirty": git_dirty,
        "runtime_mode": runtime_mode,
        "mock_mode_detected": bool(mock_mode_detected),
        "fixture_mode_detected": bool(fixture_mode_detected),
        "synthetic_trace_detected": bool(synthetic_trace_detected),
        "success": success,
        "blocking_gaps": list(blocking),
        "agentic_core_spine_status": spine_status,
        "chain_kind": chain_kind,
        "managed_workflow_certified": False,
        "managed_workflow_disclaimer": (
            "MANAGED_WORKFLOW substrate (static DAG proof + runtime L3 "
            "orchestration receipt + MW chain + verifiers) is implemented "
            "this pass as structural-only. Full MANAGED_WORKFLOW "
            "certification (real L2 tool/model execution under L3 "
            "orchestration with bound L2 sealed artifact, UWG commit, "
            "and real OTEL trace capture) remains deferred. The flag is "
            "False until all four are in place."
        ),
        "runtime_identity_ref": runtime_identity_ref,
        "runtime_intake_ref": runtime_intake_ref,
        "runtime_l1_plan_ref": runtime_l1_plan_ref,
        "runtime_route_contract_ref": runtime_route_contract_ref,
        "static_dag_ref": static_dag_ref,
        "static_dag_sha256": static_dag_sha256,
        "runtime_l3_receipt_ref": runtime_l3_receipt_ref,
        "runtime_l3_bypass_ref": runtime_l3_bypass_ref,
        "runtime_c0_receipt_ref": runtime_c0_receipt_ref,
        "runtime_prompt_assembly_ref": runtime_prompt_assembly_ref,
        "runtime_l2_artifact_ref": runtime_l2_artifact_ref,
        "runtime_exit_disposition_ref": runtime_exit_disposition_ref,
        "runtime_exhaust_ref": runtime_exhaust_ref,
        "uwg_commit_or_block_ref": uwg_commit_or_block_ref,
        "otel_or_runtime_trace_ref": otel_or_runtime_trace_ref,
        "artifact_manifest_ref": artifact_manifest_ref,
        "verifier_result_ref": verifier_result_ref,
        "how_trace_ref": how_trace_ref,
        "how_trace_sha256": how_trace_ref or "",
        "how_trace_status": how_trace_status,
        "how_trace_verifier_ref": "ops_scripts.ci.verify_agentic_core_how_trace",
        "l7_route_family_coverage_ref": rfc_ref,
        "l7_route_family_coverage_sha256": rfc_ref or "",
        "l7_route_family_coverage_status": rfc_status,
        "l7_route_family_coverage_summary": rfc_summary,
        "l7_route_family_coverage_verifier_ref": (
            "ops_scripts.ci.verify_agentic_core_l7_route_family_coverage"
        ),
    }


def utc_iso_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


__all__ = [
    "HARNESS_SCHEMA_VERSION",
    "PROOF_SCHEMA_VERSION",
    "RUNTIME_SUBJECT",
    "build_spine_proof_payload",
    "git_commit_and_dirty",
    "utc_iso_now",
]
