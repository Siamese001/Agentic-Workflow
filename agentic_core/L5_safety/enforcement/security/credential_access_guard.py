"""CredentialAccessGuard — safety-plane enforcement for credential and secret access.

All credential reads and secret lookups MUST be routed through this guard.
It provides three guarantees:

  1. Every access is recorded in the SecretAccessRecorder (ADG: reads_secret,
     accesses_credential edges become ``validated_by_safety_plane`` events).
  2. Caller identity is bound to each access event (agent_id + run_id).
  3. Access can be denied at the policy level before reaching the credential
     store (policy_enforced=True mode).

ADG governance plane: calling ``guarded_get_secret`` or ``guarded_get_env``
adds a ``validated_by_safety_plane`` relation from the caller to the
credential surface, closing the gap between ``accesses_credential`` (346)
and governed access edges (~95).

Layer note: adg.runtime.secret_access (L_TOOLS) is imported lazily inside
each method to avoid an upward L5->L_TOOLS module-level dependency (ADG
violation GV-2).  The functional contract is identical; only the import
timing changes.
"""

from __future__ import annotations

import hashlib
import logging
import os
from typing import Any

Logger = logging.getLogger(__name__)

_DENIED_PREFIXES: tuple[str, ...] = (
    "AWS_SECRET",
    "PRIVATE_KEY",
    "SIGNING_KEY",
)


def _import_secret_access():  # noqa: ANN202
    """Lazy import helper — defers L_TOOLS import to call time."""
    from agentic_core.adg.runtime.secret_access import (  # noqa: PLC0415
        SecretAccessOutcome,
        SecretAccessRecorder,
        SecretKind,
    )

    return SecretAccessOutcome, SecretAccessRecorder, SecretKind


class CredentialAccessDenied(PermissionError):
    """Raised when the guard denies a credential access attempt."""


class CredentialAccessGuard:
    """Safety-plane gate for all credential and secret access.

    Usage::

        guard = CredentialAccessGuard(agent_id="MyAgent", run_id="run-abc")
        api_key = guard.guarded_get_secret("OPENAI_API_KEY")
        db_pass = guard.guarded_get_env("DB_PASSWORD")

    The guard maintains an internal ``SecretAccessRecorder`` and emits a
    ``validated_by_safety_plane`` audit event for each access.
    """

    def __init__(
        self,
        agent_id: str,
        run_id: str,
        policy_enforced: bool = True,
        denied_prefixes: tuple[str, ...] | None = None,
    ) -> None:
        _SecretAccessOutcome, SecretAccessRecorder, _SecretKind = _import_secret_access()
        self._agent_id = agent_id
        self._run_id = run_id
        self._policy_enforced = policy_enforced
        self._denied_prefixes = denied_prefixes if denied_prefixes is not None else _DENIED_PREFIXES
        self._recorder = SecretAccessRecorder(agent_id=agent_id, run_id=run_id)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def guarded_get_secret(
        self,
        secret_name: str,
        kind: Any = None,
        default: str | None = None,
    ) -> str:
        """Retrieve a secret value through the safety-plane gate.

        Args:
            secret_name: The identifier for the secret (e.g. ``OPENAI_API_KEY``).
            kind: The ``SecretKind`` category for audit classification.
            default: Fallback value when the secret is absent (avoid for sensitive data).

        Returns:
            The secret string.

        Raises:
            CredentialAccessDenied: if policy blocks this secret name.
            KeyError: if secret absent and no default provided.
        """
        SecretAccessOutcome, _SecretAccessRecorder, SecretKind = _import_secret_access()
        if kind is None:
            kind = SecretKind.API_KEY
        self._apply_policy_gate(secret_name)
        raw = os.environ.get(secret_name)
        if raw is None:
            if default is not None:
                self._recorder.record_access(
                    secret_name=secret_name,
                    secret_kind=kind,
                    access_method="guarded_get_secret",
                    outcome=SecretAccessOutcome.NOT_FOUND,
                )
                Logger.debug("[CredentialAccessGuard] %s not found, using default", secret_name)
                return default
            self._recorder.record_denied(secret_name=secret_name, secret_kind=kind)
            raise KeyError(
                f"CredentialAccessGuard: secret '{secret_name}' not found and no default provided."
            )
        self._recorder.record_access(
            secret_name=secret_name,
            secret_kind=kind,
            access_method="guarded_get_secret",
            outcome=SecretAccessOutcome.SUCCESS,
            raw_value=raw,
        )
        Logger.debug("[CredentialAccessGuard] validated_by_safety_plane: %s (%s)", secret_name, kind)
        return raw

    def guarded_get_env(
        self,
        var_name: str,
        kind: Any = None,
        default: str | None = None,
    ) -> str | None:
        """Retrieve an environment variable through the safety-plane gate.

        Unlike ``guarded_get_secret``, missing variables return *default*
        (which may be None) rather than raising.
        """
        SecretAccessOutcome, _SecretAccessRecorder, SecretKind = _import_secret_access()
        if kind is None:
            kind = SecretKind.ENV_VAR
        self._apply_policy_gate(var_name)
        raw = os.environ.get(var_name, default)
        outcome = SecretAccessOutcome.SUCCESS if raw is not None else SecretAccessOutcome.NOT_FOUND
        self._recorder.record_access(
            secret_name=var_name,
            secret_kind=kind,
            access_method="guarded_get_env",
            outcome=outcome,
        )
        Logger.debug("[CredentialAccessGuard] env read validated_by_safety_plane: %s", var_name)
        return raw

    def guarded_access_credential(
        self,
        credential_name: str,
        kind: Any = None,
        resolver: Any = None,
    ) -> Any:
        """Access a structured credential through the safety-plane gate.

        Args:
            credential_name: Logical credential identifier.
            kind: Credential kind for audit classification.
            resolver: Optional callable ``(name: str) -> Any`` to retrieve the
                      credential from a vault or credential store.  If None, falls
                      back to ``os.environ``.

        Returns:
            The resolved credential value.

        Raises:
            CredentialAccessDenied: if policy blocks this credential.
        """
        SecretAccessOutcome, _SecretAccessRecorder, SecretKind = _import_secret_access()
        if kind is None:
            kind = SecretKind.TOKEN
        self._apply_policy_gate(credential_name)
        if resolver is not None:
            value = resolver(credential_name)
        else:
            value = os.environ.get(credential_name)
        outcome = SecretAccessOutcome.SUCCESS if value is not None else SecretAccessOutcome.NOT_FOUND
        self._recorder.record_access(
            secret_name=credential_name,
            secret_kind=kind,
            access_method="guarded_access_credential",
            outcome=outcome,
        )
        Logger.debug(
            "[CredentialAccessGuard] accesses_credential validated_by_safety_plane: %s", credential_name
        )
        return value

    def hash_credential(self, raw_value: str) -> str:
        """Return a masked SHA-256 hash of a credential value (first 16 hex chars)."""
        return hashlib.sha256(raw_value.encode()).hexdigest()[:16]

    @property
    def access_report(self):
        """Return the accumulated ``SecretAccessReport`` for this guard instance."""
        return self._recorder.report

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _apply_policy_gate(self, name: str) -> None:
        """Raise CredentialAccessDenied if the name violates policy."""
        if not self._policy_enforced:
            return
        name_upper = name.upper()
        for prefix in self._denied_prefixes:
            if name_upper.startswith(prefix):
                self._recorder.record_denied(secret_name=name)
                raise CredentialAccessDenied(
                    f"CredentialAccessGuard: access to '{name}' denied by safety policy "
                    f"(matches denied prefix '{prefix}')."
                )
