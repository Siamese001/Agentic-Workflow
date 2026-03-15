"""
Provider Binding Determinism (REQ-413)

Ensures determinism digest includes provider_id, model_id, gateway_version,
and semantic_clock_vector for reproducible LLM interactions.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any

from agentic_core.L0_routing.types.determinism_types import SemanticClockSnapshot
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)


@dataclass(frozen=True)
class ProviderBindingContext:
    """Context for provider binding determinism."""

    provider_id: str
    model_id: str
    gateway_version: str
    semantic_clock_vector: dict[str, int]


def compute_provider_binding_digest(
    provider_id: str,
    model_id: str,
    gateway_version: str,
    semantic_clock: SemanticClockSnapshot,
    additional_context: dict[str, Any] | None = None,
) -> str:
    """Compute deterministic digest for provider binding (REQ-413).

    Args:
        provider_id: LLM provider identifier (e.g., "openai", "anthropic", "google")
        model_id: Model identifier (e.g., "gpt-4", "claude-3-5-sonnet-20241022")
        gateway_version: SovereignLLMGateway version
        semantic_clock: Current semantic clock snapshot
        additional_context: Optional additional context for determinism

    Returns:
        SHA-256 hex digest of provider binding information
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "compute_provider_binding_digest", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "compute_provider_binding_digest", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "compute_provider_binding_digest")
    vector_dict = dict(semantic_clock.vector_clock)
    binding_data = {
        "provider_id": provider_id,
        "model_id": model_id,
        "gateway_version": gateway_version,
        "semantic_clock_vector": vector_dict,
        "semantic_clock_tick": semantic_clock.tick,
    }
    if additional_context:
        binding_data["additional_context"] = additional_context
    canonical_json = json.dumps(binding_data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()


def verify_provider_binding_determinism(
    expected_digest: str,
    provider_id: str,
    model_id: str,
    gateway_version: str,
    semantic_clock: SemanticClockSnapshot,
    additional_context: dict[str, Any] | None = None,
) -> bool:
    """Verify provider binding determinism (REQ-413).

    Args:
        expected_digest: Previously computed digest to verify against
        provider_id: LLM provider identifier
        model_id: Model identifier
        gateway_version: SovereignLLMGateway version
        semantic_clock: Current semantic clock snapshot
        additional_context: Optional additional context

    Returns:
        True if digest matches, False otherwise
    """
    computed_digest = compute_provider_binding_digest(
        provider_id=provider_id,
        model_id=model_id,
        gateway_version=gateway_version,
        semantic_clock=semantic_clock,
        additional_context=additional_context,
    )
    return computed_digest == expected_digest


def extract_provider_context_from_request(request: dict[str, Any]) -> ProviderBindingContext:
    """Extract provider binding context from LLM request.

    Args:
        request: LLM request dictionary

    Returns:
        ProviderBindingContext with extracted information
    """
    provider_id = request.get("provider", "unknown")
    model_id = request.get("model", "unknown")
    import os

    gateway_version = os.getenv("GATEWAY_VERSION", "1.0.0")
    semantic_clock_data = request.get("semantic_clock", {"tick": 0, "vector_clock": {}})
    semantic_clock_vector = semantic_clock_data.get("vector_clock", {})
    return ProviderBindingContext(
        provider_id=provider_id,
        model_id=model_id,
        gateway_version=gateway_version,
        semantic_clock_vector=semantic_clock_vector,
    )
