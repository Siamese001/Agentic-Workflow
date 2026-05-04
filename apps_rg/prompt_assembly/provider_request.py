"""Adapter: CompiledPromptArtifact -> provider request.

Renders a provider-specific request from a compiled prompt artifact.
This adapter may ONLY render from the compiled artifact.
It MUST NOT add new instructions, mutate slots, or add hidden context.
"""

from __future__ import annotations

import logging
from typing import Any

_log = logging.getLogger(__name__)

_REQUIRED_HASH_FIELDS = (
    "prompt_bom_hash",
    "prompt_registry_hash",
    "prompt_template_hash",
    "prompt_hash",
    "manifest_hash",
    "canonical_slot_bytes_hash",
    "artifact_hash",
)


def artifact_to_provider_request(
    artifact_dict: dict[str, Any],
) -> dict[str, Any]:
    """Convert a compiled prompt artifact dict to a provider request dict.

    Args:
        artifact_dict: The compiled artifact as a JSON-safe dict.

    Returns:
        A dict ready to pass to the provider SDK.

    Raises:
        RuntimeError: If artifact is not ready or messages are missing.
    """
    status = artifact_dict.get("compile_status", "")
    if status != "PA_L2_HANDOFF_READY":
        raise RuntimeError(
            f"PA_PROVIDER_REQUEST_BLOCKED: artifact not ready "
            f"(status={status}). Compiled prompt artifact required."
        )

    messages = artifact_dict.get("provider_specific_messages", [])
    if not messages:
        raise RuntimeError(
            "PA_PROVIDER_REQUEST_BLOCKED: no provider_specific_messages in artifact."
        )

    missing_hashes = [f for f in _REQUIRED_HASH_FIELDS if not artifact_dict.get(f)]
    if missing_hashes:
        raise RuntimeError(
            f"PA_PROVIDER_REQUEST_BLOCKED: missing required hash fields: {missing_hashes}"
        )

    provider_request = {
        "messages": messages,
        "model": artifact_dict.get("symbolic_model_id", ""),
        "prompt_id": artifact_dict.get("prompt_id", ""),
        "template_id": artifact_dict.get("template_id", ""),
        "template_version": artifact_dict.get("template_version", ""),
        "prompt_hash": artifact_dict.get("prompt_hash", ""),
        "prompt_template_hash": artifact_dict.get("prompt_template_hash", ""),
        "prompt_bom_hash": artifact_dict.get("prompt_bom_hash", ""),
        "prompt_registry_hash": artifact_dict.get("prompt_registry_hash", ""),
        "manifest_hash": artifact_dict.get("manifest_hash", ""),
        "canonical_slot_bytes_hash": artifact_dict.get("canonical_slot_bytes_hash", ""),
        "artifact_hash": artifact_dict.get("artifact_hash", ""),
        "policy_hash": artifact_dict.get("policy_hash", ""),
        "blueprint_hash": artifact_dict.get("blueprint_hash", ""),
        "replay_key": artifact_dict.get("replay_key", ""),
        "provider_lane": artifact_dict.get("provider_lane", ""),
        "output_schema_ref": artifact_dict.get("output_schema_ref", ""),
        "output_schema_hash": artifact_dict.get("output_schema_hash", ""),
        "source_refs": artifact_dict.get("source_refs", {}),
        "origin_label_map": artifact_dict.get("origin_label_map", {}),
        "local_evidence_contract_ref": artifact_dict.get("local_evidence_contract_ref", ""),
        "artifact_id": artifact_dict.get("artifact_id", ""),
        "request_id": artifact_dict.get("request_id", ""),
        "run_id": artifact_dict.get("run_id", ""),
        "trace_id": artifact_dict.get("trace_id", ""),
    }

    _log.info(
        "[provider_request] Built request: prompt_id=%s, artifact_id=%s",
        artifact_dict.get("prompt_id", ""),
        artifact_dict.get("artifact_id", ""),
    )
    return provider_request


__all__ = ["artifact_to_provider_request"]
