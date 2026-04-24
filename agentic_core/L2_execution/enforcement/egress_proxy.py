"""
Egress proxy with domain allowlist — W2-P2.1 (gap plan b7c4e2 G2).

Python-level egress guard modeled on Anthropic's Claude Code sandbox proxy
(https://www.anthropic.com/engineering/claude-code-sandboxing). The existing
``preventative_sandbox.py`` treats network calls as blocked writes; this
module adds the nuance that network calls to **allowlisted** domains are
permitted, while unknown or denylisted domains raise ``EgressDenied`` with
an audit record.

Fail-closed: when no policy is active, all egress is denied. Callers must
explicitly install a policy via ``install_egress_policy`` and enter an
``egress_scope`` context manager for the duration of an L2 step.

This module does NOT patch ``socket`` / ``urllib`` / ``requests`` globally.
It is an opt-in resolver that callers query before making a network call.
Deeper OS-level isolation (bubblewrap / seatbelt) is tracked as a separate
deferred wave in the plan's §12.

Guardian note: catches only its own ``EgressDenied`` exception where
needed. No broad ``except Exception`` introduced.
"""

from __future__ import annotations

import fnmatch
import threading
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Iterable, Iterator
from urllib.parse import urlparse

__all__ = [
    "EgressDecision",
    "EgressPolicy",
    "EgressDenied",
    "install_egress_policy",
    "uninstall_egress_policy",
    "current_policy",
    "check_url",
    "egress_scope",
    "FAIL_CLOSED_POLICY",
]


class EgressDenied(Exception):
    """Raised when an outbound URL does not match the current allowlist."""

    def __init__(self, url: str, reason: str) -> None:
        super().__init__(f"egress denied url={url!r} reason={reason!r}")
        self.url = url
        self.reason = reason


@dataclass(frozen=True, slots=True)
class EgressDecision:
    """Outcome of checking a URL against the active policy."""

    url: str
    allowed: bool
    matched_pattern: str | None
    reason: str
    policy_name: str


@dataclass(frozen=True, slots=True)
class EgressPolicy:
    """Allowlist policy keyed by host glob patterns.

    ``allowed_hosts`` and ``denied_hosts`` accept fnmatch-style globs
    (``*.example.com``, ``api.vendor.io``). Deny takes precedence over allow.

    ``allowed_schemes`` constrains URI schemes (default: https only).

    ``require_policy`` is an invariant: if True and no policy is active at
    check time, ``EgressDenied`` is raised immediately — this is the
    fail-closed contract.
    """

    name: str
    allowed_hosts: frozenset[str] = field(default_factory=frozenset)
    denied_hosts: frozenset[str] = field(default_factory=frozenset)
    allowed_schemes: frozenset[str] = field(default_factory=lambda: frozenset({"https"}))
    reason_prefix: str = ""

    def check(self, url: str) -> EgressDecision:
        """Resolve a URL against this policy."""
        parsed = urlparse(url)
        scheme = (parsed.scheme or "").lower()
        host = (parsed.hostname or "").lower()

        if not host:
            return EgressDecision(
                url=url,
                allowed=False,
                matched_pattern=None,
                reason=f"{self.reason_prefix}invalid url (no host)",
                policy_name=self.name,
            )

        if scheme not in self.allowed_schemes:
            return EgressDecision(
                url=url,
                allowed=False,
                matched_pattern=None,
                reason=f"{self.reason_prefix}scheme {scheme!r} not in {sorted(self.allowed_schemes)}",
                policy_name=self.name,
            )

        for pattern in self.denied_hosts:
            if fnmatch.fnmatchcase(host, pattern):
                return EgressDecision(
                    url=url,
                    allowed=False,
                    matched_pattern=pattern,
                    reason=f"{self.reason_prefix}host matches denylist {pattern!r}",
                    policy_name=self.name,
                )

        for pattern in self.allowed_hosts:
            if fnmatch.fnmatchcase(host, pattern):
                return EgressDecision(
                    url=url,
                    allowed=True,
                    matched_pattern=pattern,
                    reason=f"{self.reason_prefix}host matches allowlist {pattern!r}",
                    policy_name=self.name,
                )

        return EgressDecision(
            url=url,
            allowed=False,
            matched_pattern=None,
            reason=f"{self.reason_prefix}host {host!r} not in allowlist",
            policy_name=self.name,
        )


FAIL_CLOSED_POLICY = EgressPolicy(
    name="fail_closed_default",
    allowed_hosts=frozenset(),
    denied_hosts=frozenset(),
    reason_prefix="fail-closed default: ",
)


_policy_lock = threading.RLock()
_active_policy: EgressPolicy | None = None


def install_egress_policy(policy: EgressPolicy) -> None:
    """Install ``policy`` as the active policy. Thread-safe."""
    global _active_policy  # noqa: PLW0603
    with _policy_lock:
        _active_policy = policy


def uninstall_egress_policy() -> None:
    """Clear the active policy. Subsequent ``check_url`` calls fail closed."""
    global _active_policy  # noqa: PLW0603
    with _policy_lock:
        _active_policy = None


def current_policy() -> EgressPolicy | None:
    """Return the active policy, or None if fail-closed."""
    with _policy_lock:
        return _active_policy


def check_url(url: str, *, raise_on_deny: bool = True) -> EgressDecision:
    """Resolve ``url`` against the active policy.

    If no policy is installed, the decision is denied with
    ``policy_name="fail_closed_default"``. When ``raise_on_deny`` is True
    (the default), a denied decision raises ``EgressDenied``.
    """
    policy = current_policy() or FAIL_CLOSED_POLICY
    decision = policy.check(url)
    if not decision.allowed and raise_on_deny:
        raise EgressDenied(url=url, reason=decision.reason)
    return decision


@contextmanager
def egress_scope(policy: EgressPolicy) -> Iterator[EgressPolicy]:
    """Install ``policy`` for the duration of the context block.

    Restores the prior policy (or fail-closed) on exit. Safe to nest; the
    outer scope's policy is always restored.
    """
    with _policy_lock:
        prior = _active_policy
    install_egress_policy(policy)
    try:
        yield policy
    finally:
        if prior is None:
            uninstall_egress_policy()
        else:
            install_egress_policy(prior)


def build_policy(
    *,
    name: str,
    allowed_hosts: Iterable[str],
    denied_hosts: Iterable[str] = (),
    allowed_schemes: Iterable[str] = ("https",),
) -> EgressPolicy:
    """Convenience factory."""
    return EgressPolicy(
        name=name,
        allowed_hosts=frozenset(allowed_hosts),
        denied_hosts=frozenset(denied_hosts),
        allowed_schemes=frozenset(s.lower() for s in allowed_schemes),
    )
