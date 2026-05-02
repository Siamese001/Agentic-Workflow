"""Canonical runtime identity contract for the agentic_core spine.

Provides a single typed envelope that carries the identity fields every
artifact in the integrated-runtime W2 chain MUST agree on:

    run_id, request_id, trace_root, replay_key,
    policy_hash, blueprint_hash, registry_digest_set,
    route_contract_id, route_id,
    app_name, caller_surface, entrypoint_command,
    started_at_utc, git_commit, git_dirty,
    schema_version, deterministic_digest

The R1B terminal-shortcircuit path aliases ``run_id == request_id``; this
contract makes that aliasing explicit rather than implicit. A future
multi-pass / replan path can populate ``run_id`` independent of
``request_id`` without changing the envelope shape.

Doctrine alignment:
    - ``ValidatedRequest`` is the authoritative source of ``request_id``
      and ``trace_root`` (see ``agentic_core.L0_routing.intake.validated_request``).
    - ``replay_key`` is computed deterministically from the caller-supplied
      raw_request BEFORE intake (see ``_compute_deterministic_replay_key``
      in the integrated entry point).
    - ``policy_hash`` and ``blueprint_hash`` carry through the route
      contract.

Hostile-verifier invariants enforced here:
    1. ``run_id`` MUST be non-empty.
    2. ``request_id`` MUST be non-empty.
    3. ``trace_root`` MUST be non-empty.
    4. ``replay_key`` MUST be non-empty.
    5. ``schema_version`` MUST equal ``IDENTITY_ENVELOPE_SCHEMA_VERSION``.
    6. ``deterministic_digest`` MUST be reproducible from the stable
       fields only — ``started_at_utc``, ``git_commit``, ``git_dirty``
       are excluded.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Mapping

IDENTITY_ENVELOPE_SCHEMA_VERSION = "1.0"

# Fields that participate in the deterministic_digest. Ordered for
# canonical-JSON stability. Volatile fields (started_at_utc, git_commit,
# git_dirty) are intentionally excluded — they would flip the digest on
# every wallclock or commit change and prevent replay verification.
_DIGEST_STABLE_FIELDS: tuple[str, ...] = (
    "schema_version",
    "run_id",
    "request_id",
    "trace_root",
    "replay_key",
    "policy_hash",
    "blueprint_hash",
    "registry_digest_set",
    "route_contract_id",
    "route_id",
    "app_name",
    "caller_surface",
    "entrypoint_command",
)


def _canonical_json(payload: Any) -> str:
    """Deterministic JSON serialization (sorted keys, no whitespace)."""
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)


@dataclass(frozen=True)
class RuntimeIdentityEnvelope:
    """SSOT identity envelope for one runtime invocation.

    Construct via :func:`build_runtime_identity_envelope` so the
    deterministic_digest is computed from the stable fields only.
    """

    # --- mandatory identity ---
    run_id: str
    request_id: str
    trace_root: str
    replay_key: str
    policy_hash: str
    blueprint_hash: str

    # --- caller / entry-point provenance ---
    caller_surface: str
    entrypoint_command: str

    # --- timing / commit (volatile; excluded from digest) ---
    started_at_utc: str
    git_commit: str
    git_dirty: bool

    # --- schema + bound digest (digest filled by builder) ---
    schema_version: str = IDENTITY_ENVELOPE_SCHEMA_VERSION
    deterministic_digest: str = ""

    # --- optional structural binding ---
    registry_digest_set: Mapping[str, str] = field(default_factory=dict)
    route_contract_id: str = ""
    route_id: str = ""
    app_name: str = ""

    def __post_init__(self) -> None:
        for name in ("run_id", "request_id", "trace_root", "replay_key"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value:
                raise ValueError(
                    f"RuntimeIdentityEnvelope.{name} must be a non-empty string; "
                    f"got {value!r}"
                )
        if self.schema_version != IDENTITY_ENVELOPE_SCHEMA_VERSION:
            raise ValueError(
                f"RuntimeIdentityEnvelope.schema_version must be "
                f"{IDENTITY_ENVELOPE_SCHEMA_VERSION!r}; got {self.schema_version!r}"
            )
        if not isinstance(self.git_dirty, bool):
            raise ValueError(
                f"RuntimeIdentityEnvelope.git_dirty must be bool; "
                f"got {type(self.git_dirty).__name__}"
            )

    def to_dict(self) -> dict[str, Any]:
        """Return JSON-serializable dict suitable for the W2 envelope payload."""
        return {
            "schema_version": self.schema_version,
            "run_id": self.run_id,
            "request_id": self.request_id,
            "trace_root": self.trace_root,
            "replay_key": self.replay_key,
            "policy_hash": self.policy_hash,
            "blueprint_hash": self.blueprint_hash,
            "registry_digest_set": dict(self.registry_digest_set),
            "route_contract_id": self.route_contract_id,
            "route_id": self.route_id,
            "app_name": self.app_name,
            "caller_surface": self.caller_surface,
            "entrypoint_command": self.entrypoint_command,
            "started_at_utc": self.started_at_utc,
            "git_commit": self.git_commit,
            "git_dirty": self.git_dirty,
            "deterministic_digest": self.deterministic_digest,
        }


def compute_identity_deterministic_digest(payload: Mapping[str, Any]) -> str:
    """Compute the deterministic digest from a payload mapping.

    Uses only the stable fields listed in :data:`_DIGEST_STABLE_FIELDS`.
    Returns ``"sha256:<hex>"``.
    """
    stable_view: dict[str, Any] = {}
    for key in _DIGEST_STABLE_FIELDS:
        value = payload.get(key)
        if isinstance(value, Mapping):
            stable_view[key] = {str(k): str(v) for k, v in sorted(value.items())}
        else:
            stable_view[key] = value
    blob = _canonical_json(stable_view).encode("utf-8")
    return f"sha256:{hashlib.sha256(blob).hexdigest()}"


def build_runtime_identity_envelope(
    *,
    run_id: str,
    request_id: str,
    trace_root: str,
    replay_key: str,
    policy_hash: str,
    blueprint_hash: str,
    caller_surface: str,
    entrypoint_command: str,
    started_at_utc: str,
    git_commit: str,
    git_dirty: bool,
    registry_digest_set: Mapping[str, str] | None = None,
    route_contract_id: str = "",
    route_id: str = "",
    app_name: str = "",
) -> RuntimeIdentityEnvelope:
    """Construct an envelope and bind its deterministic_digest in one call."""
    digest_input: dict[str, Any] = {
        "schema_version": IDENTITY_ENVELOPE_SCHEMA_VERSION,
        "run_id": run_id,
        "request_id": request_id,
        "trace_root": trace_root,
        "replay_key": replay_key,
        "policy_hash": policy_hash,
        "blueprint_hash": blueprint_hash,
        "registry_digest_set": dict(registry_digest_set or {}),
        "route_contract_id": route_contract_id,
        "route_id": route_id,
        "app_name": app_name,
        "caller_surface": caller_surface,
        "entrypoint_command": entrypoint_command,
    }
    digest = compute_identity_deterministic_digest(digest_input)
    return RuntimeIdentityEnvelope(
        run_id=run_id,
        request_id=request_id,
        trace_root=trace_root,
        replay_key=replay_key,
        policy_hash=policy_hash,
        blueprint_hash=blueprint_hash,
        caller_surface=caller_surface,
        entrypoint_command=entrypoint_command,
        started_at_utc=started_at_utc,
        git_commit=git_commit,
        git_dirty=bool(git_dirty),
        registry_digest_set=dict(registry_digest_set or {}),
        route_contract_id=route_contract_id,
        route_id=route_id,
        app_name=app_name,
        deterministic_digest=digest,
    )


__all__ = [
    "IDENTITY_ENVELOPE_SCHEMA_VERSION",
    "RuntimeIdentityEnvelope",
    "build_runtime_identity_envelope",
    "compute_identity_deterministic_digest",
]
