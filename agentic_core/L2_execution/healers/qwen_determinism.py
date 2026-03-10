"""
Qwen Determinism - Full SHA-256 Digest and Output Canonicalization

Provides deterministic hashing for Qwen model invocations to ensure
replay consistency and auditability.
"""

from __future__ import annotations

import hashlib
import json
import unicodedata


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

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
    payload = {
        "model_id": model_id,
        "model_revision": model_revision,
        "tokenizer_revision": tokenizer_revision,
        "inference_params": inference_params,
        "vllm_version": vllm_version,
        "cuda_version": cuda_version,
        "torch_version": torch_version,
    }
    # Canonical JSON encoding - sorted keys, no whitespace drift
    canonical_payload = json.dumps(payload, separators=(",", ":"), sort_keys=True)
    return hashlib.sha256(canonical_payload.encode("utf-8")).hexdigest()  # Full 64 chars


def canonicalize_qwen_output(output: str) -> str:
    """Enforce Unicode and whitespace canonicalization for replay consistency."""
    # 1. Normalize Unicode to NFC
    normalized = unicodedata.normalize("NFC", output)
    # 2. Normalize newlines to "\n"
    normalized = normalized.replace("\r\n", "\n").replace("\r", "\n")
    # 3. Strip leading/trailing whitespace per line, then rejoin
    lines = [line.strip() for line in normalized.split("\n")]
    normalized = "\n".join(lines)
    # 4. Strip trailing whitespace/blank lines from the whole output
    normalized = normalized.rstrip()
    # 5. Encode UTF-8 and hash
    encoded = normalized.encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def compute_current_determinism_digest() -> str:
    """Compute determinism digest for current runtime configuration."""
    # Import here to avoid circular dependency
    from agentic_core.L2_execution.healers.healing_tier_config import (
        QWEN_CUDA_VERSION,
        QWEN_MODEL_REVISION_SHA,
        QWEN_TOKENIZER_REVISION_SHA,
        QWEN_TORCH_VERSION,
        QWEN_VLLM_VERSION,
    )

    # Fixed inference parameters for determinism
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


# Required Qwen metadata fields for InvocationRecord
QWEN_METADATA_FIELDS = {
    "determinism_digest": str,  # Full SHA-256
    "output_hash": str,  # Canonicalized output hash
    "revision_sha": str,
    "latency_ms": int,
    "memory_used_mb": int,
    "gpu_utilization": float,
    "vllm_version": str,
    "cuda_version": str,
    "torch_version": str,
}

# Circuit breaker state is operational metadata and MUST NOT be included in determinism_digest
# Circuit breaker state MUST NOT affect replay validation equality


__all__ = [
    "compute_qwen_determinism_digest",
    "canonicalize_qwen_output",
    "compute_current_determinism_digest",
    "QWEN_METADATA_FIELDS",
]
