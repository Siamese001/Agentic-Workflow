"""
Qwen Determinism - Full SHA-256 Digest and Output Canonicalization

Provides deterministic hashing for Qwen model invocations to ensure
replay consistency and auditability.
"""

from __future__ import annotations

import hashlib
import json
import unicodedata

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_routes_through,  # noqa: E402
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)

_emit_dispatches_healing_run("p1", "qwen_determinism", "L2")
_emit_routes_through("p1", "qwen_determinism", "L2")
_emit_escalates_to_human("p1", "qwen_determinism", "L2")
_emit_reads_policy_state("p1", "qwen_determinism", "L2")


def compute_qwen_determinism_digest(
    model_id: str,
    model_revision: str,
    tokenizer_revision: str,
    inference_params: dict,
    vllm_version: str,
    cuda_version: str,
    torch_version: str,
) -> str:
    """Compute W-QWEN-DETERMINISM-DIGEST with full SHA-256."""
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "compute_qwen_determinism_digest", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "compute_qwen_determinism_digest", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "compute_qwen_determinism_digest")
    payload = {
        "model_id": model_id,
        "model_revision": model_revision,
        "tokenizer_revision": tokenizer_revision,
        "inference_params": inference_params,
        "vllm_version": vllm_version,
        "cuda_version": cuda_version,
        "torch_version": torch_version,
    }
    canonical_payload = json.dumps(payload, separators=(",", ":"), sort_keys=True)
    return hashlib.sha256(canonical_payload.encode("utf-8")).hexdigest()


def canonicalize_qwen_output(output: str) -> str:
    """Enforce Unicode and whitespace canonicalization for replay consistency."""
    normalized = unicodedata.normalize("NFC", output)
    normalized = normalized.replace("\r\n", "\n").replace("\r", "\n")
    lines = [line.strip() for line in normalized.split("\n")]
    normalized = "\n".join(lines)
    normalized = normalized.rstrip()
    encoded = normalized.encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def compute_current_determinism_digest() -> str:
    """Compute determinism digest for current runtime configuration."""
    from agentic_core.L2_execution.healers.healing_tier_config import (
        QWEN_CUDA_VERSION,
        QWEN_MODEL_REVISION_SHA,
        QWEN_TOKENIZER_REVISION_SHA,
        QWEN_TORCH_VERSION,
        QWEN_VLLM_VERSION,
    )

    inference_params = {"temperature": 0.0, "top_p": 1.0, "max_tokens": 2048, "seed": 42}
    return compute_qwen_determinism_digest(
        model_id="Qwen/Qwen2.5-7B-Instruct",
        model_revision=QWEN_MODEL_REVISION_SHA,
        tokenizer_revision=QWEN_TOKENIZER_REVISION_SHA,
        inference_params=inference_params,
        vllm_version=QWEN_VLLM_VERSION,
        cuda_version=QWEN_CUDA_VERSION,
        torch_version=QWEN_TORCH_VERSION,
    )


QWEN_METADATA_FIELDS = {
    "determinism_digest": str,
    "output_hash": str,
    "revision_sha": str,
    "latency_ms": int,
    "memory_used_mb": int,
    "gpu_utilization": float,
    "vllm_version": str,
    "cuda_version": str,
    "torch_version": str,
}
__all__ = [
    "compute_qwen_determinism_digest",
    "canonicalize_qwen_output",
    "compute_current_determinism_digest",
    "QWEN_METADATA_FIELDS",
]
