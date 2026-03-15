"""
PHASE 4 WAVE 2 — VLLMInfrastructureFingerprint: pure-L2 infrastructure fingerprint.

Provides deterministic, canonical serialization and SHA256 hashing of vLLM
infrastructure parameters. No GPU imports. No runtime probing in L2 tests.
Used by Phase 3 telemetry path for deterministic replay sealing.

Fingerprint fields (all strings):
- model_name: e.g., "Qwen2.5-7B-Instruct"
- model_revision_sha: git SHA or model identifier
- vllm_version: vLLM package version
- transformers_version: transformers package version
- torch_version: torch package version
- cuda_version: CUDA runtime version
- driver_version: NVIDIA driver version
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any

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

_emit_dispatches_healing_run("p1", "vllm_infrastructure_fingerprint_types", "L2")
_emit_routes_through("p1", "vllm_infrastructure_fingerprint_types", "L2")
_emit_escalates_to_human("p1", "vllm_infrastructure_fingerprint_types", "L2")
_emit_reads_policy_state("p1", "vllm_infrastructure_fingerprint_types", "L2")


def canonical_json(obj: Any) -> str:
    """
    Deterministic JSON serialization with stable key order and minimal whitespace.

    Args:
        obj: JSON-serializable object.

    Returns:
        Canonical JSON string.
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "canonical_json", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "canonical_json", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "canonical_json")
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def sha256_hex(data: str | bytes) -> str:
    """
    Compute SHA256 hex digest of string or bytes.

    Args:
        data: Input data.

    Returns:
        64-character lowercase hex SHA256 digest.
    """
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()


@dataclass(frozen=True)
class VLLMInfrastructureFingerprint:
    """Pure-L2 infrastructure fingerprint for deterministic replay sealing."""

    model_name: str
    model_revision_sha: str
    vllm_version: str
    transformers_version: str
    torch_version: str
    cuda_version: str
    driver_version: str

    def as_dict(self) -> dict[str, str]:
        """Return fingerprint as plain dict (all strings)."""
        return {
            "model_name": self.model_name,
            "model_revision_sha": self.model_revision_sha,
            "vllm_version": self.vllm_version,
            "transformers_version": self.transformers_version,
            "torch_version": self.torch_version,
            "cuda_version": self.cuda_version,
            "driver_version": self.driver_version,
        }

    def canonical_json(self) -> str:
        """
        Return canonical JSON representation (stable key order, no whitespace).

        Used for deterministic hashing.
        """
        return canonical_json(self.as_dict())

    def fingerprint_hash(self) -> str:
        """
        Compute SHA256 hash of the canonical JSON representation.

        Returns:
            64-character lowercase hex SHA256 digest.
        """
        return sha256_hex(self.canonical_json())

    @classmethod
    def deterministic_test_instance(cls) -> VLLMInfrastructureFingerprint:
        """
        Create a deterministic test instance with known values.

        Used by unit_min_deps tests to avoid runtime probing.
        """
        return cls(
            model_name="Qwen2.5-7B-Instruct",
            model_revision_sha="abc123def456",
            vllm_version="0.6.3",
            transformers_version="4.46.0",
            torch_version="2.5.1",
            cuda_version="12.4",
            driver_version="550.54.14",
        )


__all__ = ["VLLMInfrastructureFingerprint", "canonical_json", "sha256_hex"]
