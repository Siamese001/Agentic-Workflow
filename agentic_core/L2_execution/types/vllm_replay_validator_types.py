"""
PHASE 4 WAVE 3 — VLLMReplayValidator: deterministic replay sealing.

Provides canonical hashing utilities and replay validation for vLLM gateway
calls. Ensures identical inputs produce identical hashes and detects tampering.

Replay components (canonical, sorted keys):
- prompt_hash: SHA256 of canonical prompt representation
- local_request_hash: SHA256 of shaped local_request dict
- fingerprint_hash: SHA256 of infrastructure fingerprint canonical JSON
- response_hash: SHA256 of structured response artifact / telemetry decision record

replay_hash = SHA256(prompt_hash + local_request_hash + fingerprint_hash + response_hash)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

def canonical_prompt_hash(prompt: str) -> str:
    """
    Compute SHA256 hash of canonical prompt representation.

    Args:
        prompt: Input prompt string.

    Returns:
        64-character lowercase hex SHA256 digest.
    """
    # Function-scoped imports to avoid lazy seam violations
    from agentic_core.L2_execution.types.vllm_infrastructure_fingerprint_types import (
        canonical_json,
        sha256_hex,
    )

    # Use canonical JSON to ensure stable representation
    return sha256_hex(canonical_json({"prompt": prompt}))


def canonical_local_request_hash(request: VLLMLocalRequest) -> str:
    """
    Compute SHA256 hash of shaped local request dict.

    Args:
        request: VLLMLocalRequest instance.

    Returns:
        64-character lowercase hex SHA256 digest.
    """
    # Function-scoped imports to avoid lazy seam violations
    from agentic_core.L2_execution.types.vllm_infrastructure_fingerprint_types import (
        canonical_json,
        sha256_hex,
    )

    # Convert to dict and canonicalize
    request_dict = {
        "prompt": request.prompt,
        "max_tokens": request.max_tokens,
        "temperature": request.temperature,
        "top_p": request.top_p,
        "seed": request.seed,
        "task_class": request.task_class,
        "profile_name": request.profile_name,
        "max_model_len": request.max_model_len,
    }
    return sha256_hex(canonical_json(request_dict))


def canonical_response_hash(result: VLLMGatewayCallResult) -> str:
    """
    Compute SHA256 hash of structured response artifact / telemetry decision record.

    PHASE 6: Includes invariant violations in canonical form for replay integrity.

    Args:
        result: VLLMGatewayCallResult instance.

    Returns:
        64-character lowercase hex SHA256 digest.
    """
    # Function-scoped imports to avoid lazy seam violations
    from agentic_core.L2_execution.types.vllm_infrastructure_fingerprint_types import (
        canonical_json,
        sha256_hex,
    )

    # Use telemetry as the canonical response artifact
    telemetry_dict = result.telemetry.as_dict()

    # PHASE 6: Include invariant violations in canonical form
    # Violations are already sorted by (invariant_id, severity) in verifier
    if result.invariant_violations:
        violations_canonical = [v.as_dict() for v in result.invariant_violations]
        telemetry_dict["invariant_violations"] = violations_canonical

    return sha256_hex(canonical_json(telemetry_dict))


def compute_replay_hash(
    prompt: str,
    request: VLLMLocalRequest | None,
    fingerprint: VLLMInfrastructureFingerprint,
    result: VLLMGatewayCallResult,
) -> str:
    """
    Compute deterministic replay hash from all components.

    replay_hash = SHA256(prompt_hash + local_request_hash + fingerprint_hash + response_hash)

    Args:
        prompt: Input prompt string.
        request: Shaped local request (None if routed to Gemini).
        fingerprint: Infrastructure fingerprint.
        result: Gateway call result.

    Returns:
        64-character lowercase hex SHA256 digest.
    """
    # Function-scoped imports to avoid lazy seam violations
    from agentic_core.L2_execution.types.vllm_infrastructure_fingerprint_types import (
        canonical_json,
        sha256_hex,
    )

    prompt_hash = canonical_prompt_hash(prompt)

    # For Gemini fallback, use empty dict for local request hash
    if request is None:
        local_request_hash = sha256_hex(canonical_json({}))
    else:
        local_request_hash = canonical_local_request_hash(request)

    fingerprint_hash = fingerprint.fingerprint_hash()
    response_hash = canonical_response_hash(result)

    # Explicit concatenation rule: join with no delimiter
    combined = prompt_hash + local_request_hash + fingerprint_hash + response_hash
    return sha256_hex(combined)


@dataclass(frozen=True)
class VLLMReplayArtifact:
    """Immutable artifact for deterministic replay validation.

    Contains all components needed to recompute and verify replay_hash.
    """

    prompt: str
    local_request: VLLMLocalRequest | None
    fingerprint: VLLMInfrastructureFingerprint
    result: VLLMGatewayCallResult
    prompt_hash: str = field(init=False)
    local_request_hash: str = field(init=False)
    fingerprint_hash: str = field(init=False)
    response_hash: str = field(init=False)
    replay_hash: str = field(init=False)

    def __post_init__(self) -> None:
        # Function-scoped imports to avoid lazy seam violations
        from agentic_core.L2_execution.types.vllm_infrastructure_fingerprint_types import (
            canonical_json,
            sha256_hex,
        )

        # Compute all hashes immutably after construction
        object.__setattr__(self, "prompt_hash", canonical_prompt_hash(self.prompt))

        if self.local_request is None:
            object.__setattr__(self, "local_request_hash", sha256_hex(canonical_json({})))
        else:
            object.__setattr__(self, "local_request_hash", canonical_local_request_hash(self.local_request))

        object.__setattr__(self, "fingerprint_hash", self.fingerprint.fingerprint_hash())
        object.__setattr__(self, "response_hash", canonical_response_hash(self.result))

        combined = self.prompt_hash + self.local_request_hash + self.fingerprint_hash + self.response_hash
        object.__setattr__(self, "replay_hash", sha256_hex(combined))

    def canonical_payload_hash(self) -> str:
        """
        Get the canonical payload hash derived from the exact bytes used for replay_hash computation.

        This reflects the combined canonical payload (prompt_hash + local_request_hash +
        fingerprint_hash + response_hash) before the final SHA-256.

        Returns:
            64-character lowercase hex SHA256 digest of the canonical payload.
        """
        # Function-scoped imports to avoid lazy seam violations
        from agentic_core.L2_execution.types.vllm_infrastructure_fingerprint_types import (
            sha256_hex,
        )

        # Recreate the exact combined payload used for replay_hash
        combined = self.prompt_hash + self.local_request_hash + self.fingerprint_hash + self.response_hash
        return sha256_hex(combined)

    def verify(self) -> bool:
        """
        Verify that stored hashes match recomputed hashes.

        Returns:
            True if all hashes match (artifact is untampered), False otherwise.
        """
        # Recompute replay hash from current state
        current_replay_hash = compute_replay_hash(
            prompt=self.prompt,
            request=self.local_request,
            fingerprint=self.fingerprint,
            result=self.result,
        )
        return current_replay_hash == self.replay_hash


@dataclass(frozen=True)
class VLLMReplayValidator:
    """Minimal replay validator for tamper detection."""

    def validate(self, artifact: VLLMReplayArtifact) -> bool:
        """
        Validate a replay artifact.

        Args:
            artifact: VLLMReplayArtifact to validate.

        Returns:
            True if artifact is valid (untampered), False otherwise.
        """
        return artifact.verify()

    def validate_and_report(self, artifact: VLLMReplayArtifact) -> dict[str, Any]:
        """
        Validate artifact and return detailed report.

        Args:
            artifact: VLLMReplayArtifact to validate.

        Returns:
            Dict with validation result and hash details.
        """
        is_valid = self.validate(artifact)

        # Recompute for comparison if invalid
        if not is_valid:
            current_replay_hash = compute_replay_hash(
                prompt=artifact.prompt,
                request=artifact.local_request,
                fingerprint=artifact.fingerprint,
                result=artifact.result,
            )
        else:
            current_replay_hash = artifact.replay_hash

        return {
            "valid": is_valid,
            "stored_replay_hash": artifact.replay_hash,
            "computed_replay_hash": current_replay_hash,
            "prompt_hash": artifact.prompt_hash,
            "local_request_hash": artifact.local_request_hash,
            "fingerprint_hash": artifact.fingerprint_hash,
            "response_hash": artifact.response_hash,
        }


# ---------------------------------------------------------------------------
# Exported symbols
# ---------------------------------------------------------------------------

__all__ = [
    "VLLMReplayArtifact",
    "VLLMReplayValidator",
    "canonical_prompt_hash",
    "canonical_local_request_hash",
    "canonical_response_hash",
    "compute_replay_hash",
]
