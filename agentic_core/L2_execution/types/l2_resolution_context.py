"""L2 Resolution Context — canonical agent/validator binding for E2 ↔ E4.

Maps to: docs/reference/04_L2_Execute/04.5a_L2_Resolution_Context_Invariant.md

Invariant (constitutional / 04.5a INV-RC-1..8):
  For every L2 run that reaches E4 Heal, the deterministic SHA-256 digest of
  the validator-side L2ResolutionContext MUST equal the digest of the
  heal-side L2ResolutionContext, bit-for-bit. Mismatch is a fail-closed event
  surfaced by `agentic_core.L2_execution.orchestration.resolution_consistency_gate`.

This module provides:
  - `RepairAuthorityClass` enum
  - `L2ResolutionContext` frozen dataclass
  - `compute_resolution_digest()` — canonical-JSON SHA-256
  - `ResolutionContextField` enum naming every field for mismatch reporting

Determinism:
  - `digest()` is canonical (RFC-8785-style sort_keys, ensure_ascii=False,
    compact separators). Two contexts with identical field values produce the
    same hex digest across processes, hosts, and Python versions.
  - All fields are frozen at construction. Tuples are normalized so order is
    significant (callers MUST emit `allowed_repair_types` in a stable order).
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any


class RepairAuthorityClass(str, Enum):
    """E4 repair-authority classification — see 04.5a Phase 1.

    LOCAL_SAFE_ONLY    — agent may attempt safe local same-authority repairs.
    ESCALATE_REQUIRED  — agent must escalate to L5 / [5] HITL before any heal.
    NONE               — agent has no repair authority; E4 must not run.
    """

    LOCAL_SAFE_ONLY = "LOCAL_SAFE_ONLY"
    ESCALATE_REQUIRED = "ESCALATE_REQUIRED"
    NONE = "NONE"


class ResolutionContextField(str, Enum):
    """Field names used in mismatch reporting. Names match dataclass fields."""

    REQUEST_ID = "request_id"
    RUN_ID = "run_id"
    TRACE_ID = "trace_id"
    ROUTE_ID = "route_id"
    STEP_ID = "step_id"
    AGENT_ID = "agent_id"
    AGENT_TYPE = "agent_type"
    AGENT_VERSION = "agent_version"
    AGENT_PROFILE_HASH = "agent_profile_hash"
    VALIDATOR_ID = "validator_id"
    VALIDATOR_VERSION = "validator_version"
    CAPABILITY_TOKEN = "capability_token"
    CAPABILITY_SCOPE_HASH = "capability_scope_hash"
    SANDBOX_ENVELOPE_HASH = "sandbox_envelope_hash"
    POLICY_HASH = "policy_hash"
    BLUEPRINT_HASH = "blueprint_hash"
    REPLAY_KEY = "replay_key"
    SNAPSHOT_MANIFEST_HASH = "snapshot_manifest_hash"
    TOOL_REGISTRY_DIGEST = "tool_registry_digest"
    MODEL_REGISTRY_DIGEST = "model_registry_digest"
    PROVIDER_LANE = "provider_lane"
    REPAIR_AUTHORITY_CLASS = "repair_authority_class"
    ALLOWED_REPAIR_TYPES = "allowed_repair_types"
    MAX_REPAIR_COUNT = "max_repair_count"
    FROZEN_EXECUTION_CONTEXT_HASH = "frozen_execution_context_hash"
    RESOLVER_DIGEST = "resolver_digest"


# Order is significant for canonical JSON serialization. Do NOT reorder.
_DIGEST_FIELD_ORDER: tuple[str, ...] = tuple(f.value for f in ResolutionContextField)


@dataclass(frozen=True, slots=True)
class L2ResolutionContext:
    """Canonical resolution context binding validator and heal to one agent.

    Construction is the single chokepoint for all 26 fields. The `digest()`
    method returns a stable SHA-256 hex string suitable for equality checks
    across processes.

    Forbidden patterns (enforced upstream by the consistency gate):
      - Mutating any field after construction (frozen=True, slots=True).
      - Producing a context with `agent_id` empty when E4 is reachable —
        validators MUST surface a sealed REJECTED at E2 if resolver fails.
      - Substituting a generic-fallback agent_id like "default" / "fallback".
        The gate checks `_is_default_agent_fallback()` and rejects.
    """

    request_id: str
    run_id: str
    trace_id: str
    route_id: str
    step_id: str | None

    # Agent identity (the gap closure)
    agent_id: str
    agent_type: str
    agent_version: str
    agent_profile_hash: str

    # Validator identity
    validator_id: str
    validator_version: str

    # Authority / capability surface
    capability_token: str
    capability_scope_hash: str
    sandbox_envelope_hash: str
    policy_hash: str
    blueprint_hash: str
    replay_key: str
    snapshot_manifest_hash: str

    # Registry surface
    tool_registry_digest: str
    model_registry_digest: str
    provider_lane: str

    # Repair authority
    repair_authority_class: RepairAuthorityClass
    allowed_repair_types: tuple[str, ...]
    max_repair_count: int

    # Frozen-context surface
    frozen_execution_context_hash: str
    resolver_digest: str

    def __post_init__(self) -> None:
        # Validate required string fields are non-empty (step_id may be None,
        # allowed_repair_types may be empty for repair_authority_class=NONE).
        required_strings: tuple[tuple[str, str], ...] = (
            ("request_id", self.request_id),
            ("run_id", self.run_id),
            ("trace_id", self.trace_id),
            ("route_id", self.route_id),
            ("agent_id", self.agent_id),
            ("agent_type", self.agent_type),
            ("agent_version", self.agent_version),
            ("agent_profile_hash", self.agent_profile_hash),
            ("validator_id", self.validator_id),
            ("validator_version", self.validator_version),
            ("capability_token", self.capability_token),
            ("capability_scope_hash", self.capability_scope_hash),
            ("sandbox_envelope_hash", self.sandbox_envelope_hash),
            ("policy_hash", self.policy_hash),
            ("blueprint_hash", self.blueprint_hash),
            ("replay_key", self.replay_key),
            ("snapshot_manifest_hash", self.snapshot_manifest_hash),
            ("tool_registry_digest", self.tool_registry_digest),
            ("model_registry_digest", self.model_registry_digest),
            ("provider_lane", self.provider_lane),
            ("frozen_execution_context_hash", self.frozen_execution_context_hash),
            ("resolver_digest", self.resolver_digest),
        )
        for name, value in required_strings:
            if not isinstance(value, str) or value == "":
                raise ValueError(
                    f"L2ResolutionContext.{name} must be a non-empty string; "
                    f"resolver_digest={self.resolver_digest!r}"
                )
        if not isinstance(self.repair_authority_class, RepairAuthorityClass):
            raise TypeError(
                "L2ResolutionContext.repair_authority_class must be a RepairAuthorityClass enum; "
                f"got {type(self.repair_authority_class).__name__}"
            )
        if not isinstance(self.allowed_repair_types, tuple):
            raise TypeError(
                "L2ResolutionContext.allowed_repair_types must be a tuple[str, ...]; "
                f"got {type(self.allowed_repair_types).__name__}"
            )
        for entry in self.allowed_repair_types:
            if not isinstance(entry, str) or entry == "":
                raise ValueError(
                    "L2ResolutionContext.allowed_repair_types must contain only "
                    f"non-empty strings; got {entry!r}"
                )
        if not isinstance(self.max_repair_count, int) or self.max_repair_count < 0:
            raise ValueError(
                "L2ResolutionContext.max_repair_count must be a non-negative int; "
                f"got {self.max_repair_count!r}"
            )

    # ------------------------------------------------------------------ #
    # Canonical serialization + digest
    # ------------------------------------------------------------------ #

    def to_canonical_dict(self) -> dict[str, Any]:
        """Return the deterministic dict used for digest computation.

        Field order is fixed by `_DIGEST_FIELD_ORDER`. Enum values are
        serialized as their `.value` string. Tuple of allowed_repair_types
        is serialized as a list (JSON has no tuple distinction).
        """
        raw = asdict(self)
        canonical: dict[str, Any] = {}
        for name in _DIGEST_FIELD_ORDER:
            value = raw[name]
            if isinstance(value, RepairAuthorityClass):
                canonical[name] = value.value
            elif isinstance(value, tuple):
                canonical[name] = list(value)
            else:
                canonical[name] = value
        # The loop above already coerces every RepairAuthorityClass via
        # ``value.value``. The previous "be defensive" follow-up block
        # was dead code (audit 2026-04-26) and has been removed.
        return canonical

    def digest(self) -> str:
        """Stable SHA-256 hex digest of the canonical representation."""
        return compute_resolution_digest(self)

    def first_mismatched_field(self, other: L2ResolutionContext) -> str:
        """Return the first field name that differs between self and other.

        Returns "" when self and other agree on every field. Field order
        matches `_DIGEST_FIELD_ORDER` so the answer is deterministic.
        """
        a = self.to_canonical_dict()
        b = other.to_canonical_dict()
        for name in _DIGEST_FIELD_ORDER:
            if a[name] != b[name]:
                return name
        return ""


def compute_resolution_digest(ctx: L2ResolutionContext) -> str:
    """Compute the canonical SHA-256 digest of an L2ResolutionContext."""
    canonical = ctx.to_canonical_dict()
    body = json.dumps(
        canonical,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(body).hexdigest()


# Sentinel agent_ids that the gate flags as "default-agent fallback" per
# 04.5a INV-RC-8. Any context whose agent_id matches one of these is
# rejected at the gate before digest comparison.
_DEFAULT_AGENT_FALLBACK_IDS: frozenset[str] = frozenset(
    {
        "default",
        "fallback",
        "default-agent",
        "fallback-agent",
        "generic",
        "unresolved",
        "<default>",
        "<fallback>",
    }
)


def is_default_agent_fallback(ctx: L2ResolutionContext) -> bool:
    """True if `ctx.agent_id` matches any sentinel default-fallback name."""
    return ctx.agent_id.strip().lower() in _DEFAULT_AGENT_FALLBACK_IDS


__all__ = [
    "RepairAuthorityClass",
    "ResolutionContextField",
    "L2ResolutionContext",
    "compute_resolution_digest",
    "is_default_agent_fallback",
]
