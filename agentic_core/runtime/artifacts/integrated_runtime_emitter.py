"""W2 — Integrated-runtime artifact emitter.

Single SSOT helper for stamping every artifact in the W2 chain with its
provenance envelope:

    {
      "producer_component":         "agentic_core....",
      "producer_module":            "...",
      "producer_function_or_class": "...",
      "emitted_at":                 "<UTC ISO8601>",
      "artifact_hash":              "sha256:<hex>",
      "upstream_artifact_ref":      "sha256:<hex>" | "",
      "payload":                    { ... }
    }

The W2 verifiers consume only this envelope shape; no other emitter
should write into ``artifacts/certification/integrated_runtime/``.

Anti-cheat invariants enforced here, before write:
    1. ``producer_component`` MUST start with ``"agentic_core."``.
    2. ``producer_component`` MUST NOT match harness regex
       (``^tests\\.``, ``^scripts\\.verify_``, contain ``"harness"``).
    3. Payload MUST be JSON-serializable.
    4. Upstream ref, when supplied, MUST be of the form
       ``sha256:<64-hex>`` to keep the chain machine-checkable.
"""

from __future__ import annotations

import hashlib
import json
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# Filename → expected position in the W2 chain. Used by the manifest
# emitter and by the verifiers to assert every declared artifact exists.
#
# 2026-05-01 — extended from 12 to 17 artifacts to close the R1B
# auditability gaps surfaced in the Existence Audit:
#   + runtime_identity_envelope.json     (Phase 1 — canonical identity)
#   + l3_bypass_receipt.json             (Phase 2 — typed L3 bypass)
#   + c0_bypass_receipt.json             (Phase 2 — typed C0 bypass)
#   + prompt_assembly_bypass_receipt.json (Phase 2 — typed PA bypass)
#   + agentic_core_spine_proof.json      (Phase 4 — top-level rollup)
#
# The chain remains linear; each new entry slots in at the position
# that matches its causal point in the run.
W2_ARTIFACT_FILENAMES: tuple[str, ...] = (
    "integrated_runtime_entrypoint_invocation.json",
    "runtime_identity_envelope.json",
    "runtime_certification_binding.json",
    "l5_hitl_reclearance.json",
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
    "agentic_core_spine_proof.json",
)

# Chain order for upstream_artifact_ref linkage. Each entry is
# (filename, upstream_filename_or_None).
W2_CHAIN_LINKAGE: tuple[tuple[str, str | None], ...] = (
    ("integrated_runtime_entrypoint_invocation.json", None),
    ("runtime_identity_envelope.json", "integrated_runtime_entrypoint_invocation.json"),
    ("runtime_certification_binding.json", "runtime_identity_envelope.json"),
    ("l5_hitl_reclearance.json", "runtime_certification_binding.json"),
    ("validated_request.json", "l5_hitl_reclearance.json"),
    ("l1_plan_contract.json", "validated_request.json"),
    ("route_contract.json", "l1_plan_contract.json"),
    ("l3_bypass_receipt.json", "route_contract.json"),
    ("c0_bypass_receipt.json", "l3_bypass_receipt.json"),
    ("prompt_assembly_bypass_receipt.json", "c0_bypass_receipt.json"),
    ("runtime_gate_verdict_bundle.json", "prompt_assembly_bypass_receipt.json"),
    ("semantic_cache_safe_reuse_decision.json", "runtime_gate_verdict_bundle.json"),
    ("terminal_ret_packet.json", "semantic_cache_safe_reuse_decision.json"),
    ("exit_review_packet.json", "terminal_ret_packet.json"),
    ("x3_disposition_receipt.json", "exit_review_packet.json"),
    ("runtime_exhaust_bundle.json", "x3_disposition_receipt.json"),
    ("runtime_trace_snapshot.json", "runtime_exhaust_bundle.json"),
    ("agentic_core_how_trace.json", "runtime_trace_snapshot.json"),
    ("agentic_core_l7_route_family_coverage.json", "agentic_core_how_trace.json"),
    ("integrated_runtime_artifact_manifest.json", "agentic_core_l7_route_family_coverage.json"),
    ("no_harness_stamp_receipt.json", "integrated_runtime_artifact_manifest.json"),
    ("agentic_core_spine_proof.json", "no_harness_stamp_receipt.json"),
)


# ─────────────────────────────────────────────────────────────────────────
# Managed-workflow chain (added 2026-05-01).
#
# A separate, parallel chain for runs whose ``RouteContract.execution_form
# == MANAGED_WORKFLOW``. It replaces R1B-specific artifacts with the L3
# substrate (static_dag_proof + runtime_l3_orchestration_receipt) and
# drops the cache-reuse-only artifacts (semantic_cache_safe_reuse_decision,
# terminal_ret_packet).
#
# This is "structural-only" in this pass: real L2 execution under MW is
# deferred. The chain still proves that L3 orchestrated, that the runtime
# receipt is bound to the static DAG by sha256, and that L3 did not
# execute / retrieve / assemble prompts / write L4.
# ─────────────────────────────────────────────────────────────────────────

W2_MW_ARTIFACT_FILENAMES: tuple[str, ...] = (
    "integrated_runtime_entrypoint_invocation.json",
    "runtime_identity_envelope.json",
    "runtime_certification_binding.json",
    "l5_hitl_reclearance.json",
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
    "agentic_core_spine_proof.json",
)

W2_MW_CHAIN_LINKAGE: tuple[tuple[str, str | None], ...] = (
    ("integrated_runtime_entrypoint_invocation.json", None),
    ("runtime_identity_envelope.json", "integrated_runtime_entrypoint_invocation.json"),
    ("runtime_certification_binding.json", "runtime_identity_envelope.json"),
    ("l5_hitl_reclearance.json", "runtime_certification_binding.json"),
    ("validated_request.json", "l5_hitl_reclearance.json"),
    ("l1_plan_contract.json", "validated_request.json"),
    ("route_contract.json", "l1_plan_contract.json"),
    ("static_dag_proof.json", "route_contract.json"),
    ("runtime_l3_orchestration_receipt.json", "static_dag_proof.json"),
    ("l2_sealed_artifact.json", "runtime_l3_orchestration_receipt.json"),
    ("c0_bypass_receipt.json", "l2_sealed_artifact.json"),
    ("prompt_assembly_bypass_receipt.json", "c0_bypass_receipt.json"),
    ("runtime_gate_verdict_bundle.json", "prompt_assembly_bypass_receipt.json"),
    ("exit_review_packet.json", "runtime_gate_verdict_bundle.json"),
    ("x3_disposition_receipt.json", "exit_review_packet.json"),
    ("runtime_exhaust_bundle.json", "x3_disposition_receipt.json"),
    ("runtime_trace_snapshot.json", "runtime_exhaust_bundle.json"),
    ("agentic_core_how_trace.json", "runtime_trace_snapshot.json"),
    ("agentic_core_l7_route_family_coverage.json", "agentic_core_how_trace.json"),
    ("integrated_runtime_artifact_manifest.json", "agentic_core_l7_route_family_coverage.json"),
    ("no_harness_stamp_receipt.json", "integrated_runtime_artifact_manifest.json"),
    ("agentic_core_spine_proof.json", "no_harness_stamp_receipt.json"),
)

# Union of every filename the emitter is allowed to write. emit_artifact
# uses this so a single emitter can serve both R1B and MW entrypoints
# without false positives on legitimate MW filenames.
W2_ALL_ARTIFACT_FILENAMES: frozenset[str] = frozenset(
    set(W2_ARTIFACT_FILENAMES) | set(W2_MW_ARTIFACT_FILENAMES)
)

# Anti-cheat: any of these substrings/prefixes in producer_component is
# treated as harness-stamping by the verifier and the emitter.
_HARNESS_FORBIDDEN_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"^tests\."),
    re.compile(r"^scripts\.verify_"),
    re.compile(r"^ops_scripts\.ci\.verify_"),
    re.compile(r"\bharness\b"),
)

_SHA256_REF_RE = re.compile(r"^sha256:[0-9a-f]{64}$")


@dataclass(frozen=True)
class ProvenanceStamp:
    producer_component: str
    producer_module: str
    producer_function_or_class: str

    def __post_init__(self) -> None:
        if not self.producer_component.startswith("agentic_core."):
            raise ValueError(
                f"ProvenanceStamp.producer_component must be agentic_core.*; "
                f"got {self.producer_component!r}"
            )
        for pat in _HARNESS_FORBIDDEN_PATTERNS:
            if pat.search(self.producer_component):
                raise ValueError(
                    f"ProvenanceStamp.producer_component matches harness "
                    f"pattern {pat.pattern!r}: {self.producer_component!r}"
                )


def _canonical_json(payload: Any) -> str:
    """Deterministic JSON serialization (sorted keys, no whitespace)."""
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)


def compute_artifact_hash(payload: Any) -> str:
    """Return ``sha256:<hex>`` of canonical-JSON serialization of ``payload``."""
    blob = _canonical_json(payload).encode("utf-8")
    return f"sha256:{hashlib.sha256(blob).hexdigest()}"


def emit_artifact(
    artifact_dir: Path,
    filename: str,
    payload: Any,
    *,
    stamp: ProvenanceStamp,
    upstream_artifact_ref: str = "",
) -> tuple[Path, str]:
    """Stamp ``payload`` and write to ``artifact_dir/filename``.

    Returns ``(written_path, artifact_hash)``.

    Raises:
        ValueError: producer_component is harness-shaped, or
            upstream_artifact_ref is non-empty but malformed.
    """
    if filename not in W2_ALL_ARTIFACT_FILENAMES:
        raise ValueError(
            f"emit_artifact: filename {filename!r} not in any W2 chain manifest. "
            f"All emitted artifacts must be in W2_ARTIFACT_FILENAMES (R1B chain) "
            f"or W2_MW_ARTIFACT_FILENAMES (MANAGED_WORKFLOW chain)."
        )
    if upstream_artifact_ref and not _SHA256_REF_RE.match(upstream_artifact_ref):
        raise ValueError(
            f"emit_artifact: upstream_artifact_ref {upstream_artifact_ref!r} "
            "must be of form 'sha256:<64-hex>' or empty."
        )

    artifact_hash = compute_artifact_hash(payload)
    envelope: dict[str, Any] = {
        "producer_component": stamp.producer_component,
        "producer_module": stamp.producer_module,
        "producer_function_or_class": stamp.producer_function_or_class,
        "emitted_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "artifact_hash": artifact_hash,
        "upstream_artifact_ref": upstream_artifact_ref,
        "payload": payload,
    }

    artifact_dir.mkdir(parents=True, exist_ok=True)
    out = artifact_dir / filename
    out.write_text(
        json.dumps(envelope, indent=2, sort_keys=True, default=str),
        encoding="utf-8",
    )
    return out, artifact_hash


def is_harness_stamp(producer_component: str) -> bool:
    """Return True if ``producer_component`` matches any harness pattern."""
    for pat in _HARNESS_FORBIDDEN_PATTERNS:
        if pat.search(producer_component):
            return True
    return False


__all__ = [
    "ProvenanceStamp",
    "W2_ALL_ARTIFACT_FILENAMES",
    "W2_ARTIFACT_FILENAMES",
    "W2_CHAIN_LINKAGE",
    "W2_MW_ARTIFACT_FILENAMES",
    "W2_MW_CHAIN_LINKAGE",
    "compute_artifact_hash",
    "emit_artifact",
    "is_harness_stamp",
]
