"""Adapter: CompiledPromptArtifact -> provider request.

Renders a provider-specific request from a compiled prompt artifact.
This adapter may ONLY render from the compiled artifact.
It MUST NOT add new instructions, mutate slots, or add hidden context.
"""

from __future__ import annotations

import logging
from typing import Any

_log = logging.getLogger(__name__)


def artifact_to_provider_request(
    artifact: "AppsRgCompiledPromptArtifact",
) -> dict[str, Any]:
    """Convert a compiled prompt artifact to a provider request dict.

    The returned dict contains the fields a provider gateway expects:
      - messages: list of role/content dicts (from artifact)
      - model: symbolic model ID or provider lane
      - metadata: prompt identity, hashes, replay key
      - output_schema_ref: expected output schema

    Args:
        artifact: A compiled prompt artifact with PA_L2_HANDOFF_READY status.

    Returns:
        Provider request dict.

    Raises:
        RuntimeError: If artifact is not ready for handoff.
    """
    from apps_rg.prompt_assembly.contracts import PACompileStatus

    if artifact.compile_status != PACompileStatus.PA_L2_HANDOFF_READY.value:
        raise RuntimeError(
            f"PA_GUARD_FAILED: artifact not ready for provider handoff "
            f"(status={artifact.compile_status})"
        )

    if not artifact.provider_specific_messages:
        raise RuntimeError(
            "PA_GUARD_FAILED: artifact has no provider_specific_messages"
        )

    provider_request = {
        "messages": artifact.provider_specific_messages,
        "model": artifact.symbolic_model_id or artifact.provider_lane,
        "metadata": {
            "artifact_id": artifact.artifact_id,
            "prompt_id": artifact.prompt_id,
            "prompt_hash": artifact.prompt_hash,
            "prompt_template_hash": artifact.prompt_template_hash,
            "prompt_bom_hash": artifact.prompt_bom_hash,
            "policy_hash": artifact.policy_hash,
            "blueprint_hash": artifact.blueprint_hash,
            "replay_key": artifact.replay_key,
            "provider_lane": artifact.provider_lane,
            "output_schema_ref": artifact.output_schema_ref,
            "output_schema_hash": artifact.output_schema_hash,
            "source_refs": artifact.source_refs,
            "run_id": artifact.run_id,
            "trace_id": artifact.trace_id,
        },
        "output_schema_ref": artifact.output_schema_ref,
    }

    _log.info(
        "[provider_request] Built request: prompt_id=%s, artifact_id=%s",
        artifact.prompt_id,
        artifact.artifact_id,
    )
    return provider_request


__all__ = ["artifact_to_provider_request"]
