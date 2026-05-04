"""P12 (W4) — CLI-local identity resolver for apps_rg R4 pipeline.

apps_rg is a CLI-only app that runs in a local developer environment.
There is no SSO token, no session cookie, and no HTTP bearer token — the
"user" is whoever invoked the CLI.  This resolver maps CLI invocations to a
stable, deterministic RuntimeIdentityEnvelope without making any network
calls.

The resolver is pluggable into the U0 intake step of
integrated_r4_deterministic_pipeline_run.py so that the canonical spine
receives a properly-typed identity envelope instead of a raw ``user_id``
string.

Usage
-----
From the R4 entrypoint or any U0-adjacent code::

    from apps_rg.integrations.rg_identity_resolver import resolve_rg_identity

    identity = resolve_rg_identity(
        user_id=args.user_id,
        source_channel="apps_rg_cli",
    )

Plan: apps-rg-canonical-wireup-c8a4f2 W4 P12.
"""
from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass
from typing import Any

# ---------------------------------------------------------------------------
# Stable defaults read from intake_policy.yaml identity_defaults.
# Hardcoded here for zero-dependency use; the entrypoint may override.
# ---------------------------------------------------------------------------
_DEFAULT_TENANT_ID = "local"
_DEFAULT_USER_ID = "u-apps_rg"
_DEFAULT_SOURCE_CHANNEL = "apps_rg_cli"


@dataclass(frozen=True)
class RgIdentity:
    """Lightweight identity record for a single apps_rg CLI run.

    Attributes
    ----------
    tenant_id:
        Always ``"local"`` for CLI runs — no multi-tenant context.
    user_id:
        Stable identifier for the CLI user.  Defaults to ``"u-apps_rg"``;
        can be overridden via ``--user-id`` (not yet wired to argparse —
        deferred to W7 HITL surface).
    source_channel:
        Transport/channel label.  Always ``"apps_rg_cli"`` for local runs.
    principal_hash:
        Deterministic SHA-256 of ``tenant_id:user_id`` — stable across
        runs with the same identity, useful for audit correlation.
    environment:
        ``"local"`` unless the ``APPS_RG_ENV`` environment variable is set
        (e.g. ``"ci"`` during pytest runs).
    """

    tenant_id: str
    user_id: str
    source_channel: str
    principal_hash: str
    environment: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "tenant_id": self.tenant_id,
            "user_id": self.user_id,
            "source_channel": self.source_channel,
            "principal_hash": self.principal_hash,
            "environment": self.environment,
        }


def resolve_rg_identity(
    *,
    user_id: str | None = None,
    source_channel: str | None = None,
    tenant_id: str | None = None,
) -> RgIdentity:
    """Resolve a CLI invocation to a stable RgIdentity.

    Parameters
    ----------
    user_id:
        Override the default user ID.  ``None`` → ``"u-apps_rg"``.
    source_channel:
        Override the default source channel.  ``None`` → ``"apps_rg_cli"``.
    tenant_id:
        Override the default tenant.  ``None`` → ``"local"``.

    Returns
    -------
    RgIdentity
        Frozen, hash-verified identity record.
    """
    tid = tenant_id or _DEFAULT_TENANT_ID
    uid = user_id or _DEFAULT_USER_ID
    channel = source_channel or _DEFAULT_SOURCE_CHANNEL
    env = os.environ.get("APPS_RG_ENV", "local")

    principal_hash = hashlib.sha256(
        f"{tid}:{uid}".encode("utf-8")
    ).hexdigest()[:16]

    return RgIdentity(
        tenant_id=tid,
        user_id=uid,
        source_channel=channel,
        principal_hash=principal_hash,
        environment=env,
    )


def build_raw_request_identity_fields(identity: RgIdentity) -> dict[str, str]:
    """Return the identity fields that belong in a ``raw_request`` dict.

    This is the bridge between ``RgIdentity`` and the ``raw_request`` shape
    expected by ``run_request_intake`` at U0 ingress.

    Returns a dict with keys ``transport``, ``source_channel``, ``user_id``.
    """
    return {
        "transport": "cli",
        "source_channel": identity.source_channel,
        "user_id": identity.user_id,
    }


__all__ = [
    "RgIdentity",
    "resolve_rg_identity",
    "build_raw_request_identity_fields",
]
