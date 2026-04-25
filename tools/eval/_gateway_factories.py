"""Gateway factories for ``dueling_llm_synth.py --gateway-mode real``.

These factories wrap the canonical ``SovereignLLMGateway`` so eval-synth
calls go through the same audited, capability-gated path as production
LLM traffic — telemetry ledger, circuit breaker, signature verification.

Selection: pass ``tools.eval._gateway_factories:sovereign_default`` to
``--gateway-factory``. Additional factories can be added here without
modifying the synthesizer.

Secrets: the HMAC secret for ``SovereignLLMGateway`` is read from the
``SOVEREIGN_GATEWAY_HMAC`` environment variable. The factory fails-closed
if the variable is missing — no silent fallback to an empty key.

F4.2: each artifact is HMAC-signed with ``secret_key`` before being sent
to ``gateway.generate``. The signature computation mirrors
``CompiledPromptArtifact._compute_signature`` exactly so a gateway built
with ``verify_signatures=True`` accepts the artifact. This is the
production-hardened default.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
import os
from dataclasses import dataclass, replace
from datetime import UTC, datetime
from typing import Any

logger = logging.getLogger(__name__)


def _compute_artifact_signature(artifact: Any, secret_key: bytes) -> str:
    """Compute the HMAC-SHA256 signature over a CompiledPromptArtifact.

    Mirrors ``CompiledPromptArtifact._compute_signature`` byte-for-byte so a
    gateway constructed with ``verify_signatures=True`` will accept the
    resulting artifact. Isolated here so the test suite can exercise the
    payload contract independently of the artifact class.
    """
    payload = {
        "trace_id": artifact.trace_id,
        "system_version_hash": artifact.system_version_hash,
        "final_system_string": artifact.final_system_string,
        "final_user_string": artifact.final_user_string,
        "allowed_tools_schema": artifact.allowed_tools_schema,
        "tokens": artifact.tokens,
        "slots_used": artifact.slots_used,
        "timestamp": artifact.timestamp,
    }
    payload_bytes = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hmac.new(secret_key, payload_bytes, hashlib.sha256).hexdigest()


def _build_signed_artifact(
    system_prompt: str,
    user_prompt: str,
    seed: int,
    max_tokens: int,
    temperature: float,
    secret_key: bytes,
) -> Any:
    """Construct and sign a CompiledPromptArtifact ready for the gateway."""
    from agentic_core.L2_execution.reasoning.compiled_artifact import (  # noqa: WPS433
        CompiledPromptArtifact,
    )

    timestamp = datetime.now(UTC).isoformat()
    unsigned = CompiledPromptArtifact(
        trace_id=f"eval-synth-{seed}",
        system_version_hash=f"eval-synth-v1-{seed}",
        final_system_string=system_prompt,
        final_user_string=user_prompt,
        allowed_tools_schema=[],
        tokens=0,
        slots_used=["S0", "U0"],
        signature="",  # placeholder for signing pass
        timestamp=timestamp,
        metadata={
            "source": "dueling_llm_synth",
            "temperature": temperature,
            "max_tokens": max_tokens,
        },
    )
    signature = _compute_artifact_signature(unsigned, secret_key)
    # CompiledPromptArtifact is frozen; dataclasses.replace produces a signed copy.
    return replace(unsigned, signature=signature)


@dataclass
class _SovereignAdapter:
    """Adapter that exposes ``GatewayPort.generate`` over SovereignLLMGateway.

    Each call constructs a ``CompiledPromptArtifact``, HMAC-signs it with
    the same ``secret_key`` the underlying gateway was built with, and
    dispatches to ``gateway.generate``. This allows the gateway to run
    with ``verify_signatures=True`` — the production-hardened default.
    """

    gateway: Any
    secret_key: bytes

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        seed: int,
        max_tokens: int = 512,
        temperature: float = 0.0,
    ) -> str:
        artifact = _build_signed_artifact(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            seed=seed,
            max_tokens=max_tokens,
            temperature=temperature,
            secret_key=self.secret_key,
        )
        response = self.gateway.generate(artifact)
        text = getattr(response, "text", None) or getattr(response, "content", None) or str(response)
        return str(text)


def sovereign_default() -> _SovereignAdapter:
    """Build a default SovereignLLMGateway-backed adapter.

    Fails closed if ``SOVEREIGN_GATEWAY_HMAC`` is unset. The gateway is
    constructed with ``verify_signatures=True`` (hardened default); each
    artifact is signed by the adapter before dispatch.
    """
    secret = os.environ.get("SOVEREIGN_GATEWAY_HMAC")
    if not secret:
        raise RuntimeError("SOVEREIGN_GATEWAY_HMAC environment variable is required for real gateway mode")
    from agentic_core.L2_execution.enforcement.SovereignLLMGateway import (  # noqa: WPS433
        SovereignLLMGateway,
    )

    secret_bytes = secret.encode("utf-8")
    gateway = SovereignLLMGateway(
        secret_key=secret_bytes,
        verify_signatures=True,
    )
    logger.info("sovereign_default: gateway constructed (verify_signatures=True)")
    return _SovereignAdapter(gateway=gateway, secret_key=secret_bytes)
