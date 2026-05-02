"""Prompt-Assembly bypass receipt — typed proof that PA lawfully did NOT run.

Emitted when ``RouteContract.prompt_assembly_required == False`` (or
equivalently when the route has no model execution leg). The receipt
proves three things:

    1. Prompt assembly was not required for the route.
    2. Model execution was not required for the route.
    3. The bypass had a permitted reason.

The receipt does NOT imply PA ran. It does NOT carry slot manifests,
template resolution, or signed compiled prompts. Any of those would
belong to a ``CompiledPromptArtifact`` (see
``agentic_core.L2_execution.reasoning.compiled_artifact``).
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Mapping

PA_BYPASS_RECEIPT_SCHEMA_VERSION = "1.0"

ALLOWED_PA_BYPASS_REASONS: frozenset[str] = frozenset({
    "NO_MODEL_EXECUTION_REQUIRED",
    "TERMINAL_SHORTCIRCUIT_NO_PROMPT",
    "CACHE_REUSE_NO_PROMPT",
    "FALLBACK_NO_PROMPT",
})

_DIGEST_STABLE_FIELDS: tuple[str, ...] = (
    "schema_version",
    "run_id",
    "request_id",
    "trace_root",
    "route_contract_id",
    "route_id",
    "prompt_assembly_required",
    "model_execution_required",
    "prompt_assembly_bypass_reason",
)


def _canonical_json(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)


@dataclass(frozen=True)
class PromptAssemblyBypassReceipt:
    """Typed receipt proving Prompt Assembly lawfully did not execute."""

    run_id: str
    request_id: str
    trace_root: str
    route_contract_id: str
    route_id: str
    prompt_assembly_bypass_reason: str
    prompt_assembly_required: bool = False
    model_execution_required: bool = False
    schema_version: str = PA_BYPASS_RECEIPT_SCHEMA_VERSION
    deterministic_digest: str = ""

    def __post_init__(self) -> None:
        for name in ("run_id", "request_id", "trace_root", "route_id"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value:
                raise ValueError(
                    f"PromptAssemblyBypassReceipt.{name} must be a non-empty string; "
                    f"got {value!r}"
                )
        if self.prompt_assembly_required is not False:
            raise ValueError(
                "PromptAssemblyBypassReceipt.prompt_assembly_required must be False; "
                "use CompiledPromptArtifact when PA actually ran"
            )
        if self.model_execution_required is not False:
            raise ValueError(
                "PromptAssemblyBypassReceipt.model_execution_required must be False"
            )
        if self.prompt_assembly_bypass_reason not in ALLOWED_PA_BYPASS_REASONS:
            raise ValueError(
                f"PromptAssemblyBypassReceipt.prompt_assembly_bypass_reason must be one of "
                f"{sorted(ALLOWED_PA_BYPASS_REASONS)}; "
                f"got {self.prompt_assembly_bypass_reason!r}"
            )
        if self.schema_version != PA_BYPASS_RECEIPT_SCHEMA_VERSION:
            raise ValueError(
                f"PromptAssemblyBypassReceipt.schema_version must be "
                f"{PA_BYPASS_RECEIPT_SCHEMA_VERSION!r}; got {self.schema_version!r}"
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "run_id": self.run_id,
            "request_id": self.request_id,
            "trace_root": self.trace_root,
            "route_contract_id": self.route_contract_id,
            "route_id": self.route_id,
            "prompt_assembly_required": self.prompt_assembly_required,
            "model_execution_required": self.model_execution_required,
            "prompt_assembly_bypass_reason": self.prompt_assembly_bypass_reason,
            "deterministic_digest": self.deterministic_digest,
        }


def compute_pa_bypass_digest(payload: Mapping[str, Any]) -> str:
    stable: dict[str, Any] = {k: payload.get(k) for k in _DIGEST_STABLE_FIELDS}
    blob = _canonical_json(stable).encode("utf-8")
    return f"sha256:{hashlib.sha256(blob).hexdigest()}"


def build_prompt_assembly_bypass_receipt(
    *,
    run_id: str,
    request_id: str,
    trace_root: str,
    route_contract_id: str,
    route_id: str,
    prompt_assembly_bypass_reason: str,
) -> PromptAssemblyBypassReceipt:
    digest_input: dict[str, Any] = {
        "schema_version": PA_BYPASS_RECEIPT_SCHEMA_VERSION,
        "run_id": run_id,
        "request_id": request_id,
        "trace_root": trace_root,
        "route_contract_id": route_contract_id,
        "route_id": route_id,
        "prompt_assembly_required": False,
        "model_execution_required": False,
        "prompt_assembly_bypass_reason": prompt_assembly_bypass_reason,
    }
    digest = compute_pa_bypass_digest(digest_input)
    return PromptAssemblyBypassReceipt(
        run_id=run_id,
        request_id=request_id,
        trace_root=trace_root,
        route_contract_id=route_contract_id,
        route_id=route_id,
        prompt_assembly_bypass_reason=prompt_assembly_bypass_reason,
        prompt_assembly_required=False,
        model_execution_required=False,
        deterministic_digest=digest,
    )


__all__ = [
    "ALLOWED_PA_BYPASS_REASONS",
    "PromptAssemblyBypassReceipt",
    "PA_BYPASS_RECEIPT_SCHEMA_VERSION",
    "build_prompt_assembly_bypass_receipt",
    "compute_pa_bypass_digest",
]
