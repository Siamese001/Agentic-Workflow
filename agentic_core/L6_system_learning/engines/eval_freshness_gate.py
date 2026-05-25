"""Eval-freshness write gate — G7 (plan ``system-learning-waves-7b3c91`` C1).

Pre-write hook enforcing the OpenAI "fresh eval per deploy" discipline at the
UWG ink path. Given a proposed change and its gating eval record, the gate
decides whether the eval is fresh enough for the change class (TTL policy
lives in ``config/prompt_governance/eval_freshness_ttl.yaml``).

Consumer pattern (illustrative — no wiring change forced in this phase):

.. code-block:: python

    gate = EvalFreshnessGate.from_repo(repo_root)
    decision = gate.check(
        change_class="prompt",
        eval_record_timestamp=eval_ts,
        now=current_time,
    )
    if decision.blocked:
        raise EvalFreshnessViolation(decision.reason)

The gate is pure (no I/O after construction) so it is safe to call from
inside ``l4_state_writer`` and from tests without mocking clocks.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise ImportError("system_learning.engines.eval_freshness_gate requires PyYAML.") from exc

_DEFAULT_POLICY_REL = "config/prompt_governance/eval_freshness_ttl.yaml"


@dataclass(frozen=True)
class FreshnessDecision:
    """Result of :meth:`EvalFreshnessGate.check`."""

    blocked: bool
    change_class: str
    age_seconds: float | None
    ttl_seconds: float | None
    reason: str


class EvalFreshnessViolation(RuntimeError):
    """Raised by consumers when a ``FreshnessDecision.blocked`` is returned."""


@dataclass(frozen=True)
class FreshnessPolicy:
    """Parsed policy document.

    ``ttl_seconds`` maps change class names to TTL in seconds; ``None`` means
    no TTL requirement. ``default_on_unknown_class`` is one of
    ``{"block", "allow", "warn"}``. ``fail_open`` is an emergency switch.
    """

    ttl_seconds: Mapping[str, float | None]
    default_on_unknown_class: str
    fail_open: bool
    fail_open_adr_ref: str | None
    version: int
    schema: str

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> "FreshnessPolicy":
        ttl = raw.get("ttl_seconds") or {}
        if not isinstance(ttl, dict):
            raise ValueError("'ttl_seconds' must be a mapping")
        normalized: dict[str, float | None] = {}
        for key, value in ttl.items():
            if value is None:
                normalized[str(key)] = None
            else:
                normalized[str(key)] = float(value)
        default = str(raw.get("default_on_unknown_class", "block")).lower()
        if default not in {"block", "allow", "warn"}:
            raise ValueError(f"default_on_unknown_class must be block|allow|warn, got {default!r}")
        return cls(
            ttl_seconds=normalized,
            default_on_unknown_class=default,
            fail_open=bool(raw.get("fail_open", False)),
            fail_open_adr_ref=raw.get("fail_open_adr_ref"),
            version=int(raw.get("version", 1)),
            schema=str(raw.get("schema", "")),
        )


class EvalFreshnessGate:
    """Enforces the eval-freshness TTL policy at L4 write time."""

    def __init__(self, policy: FreshnessPolicy) -> None:
        self._policy = policy
        # v6 KPI counters (EVAL_FRESHNESS_ON_WRITE). Updated on each
        # check() invocation; callers flush to the KPI board via
        # :meth:`publish_kpi_sample`. Counters never raise.
        self._total_writes: int = 0
        self._fresh_writes: int = 0

    @classmethod
    def from_repo(cls, repo_root: str | Path) -> "EvalFreshnessGate":
        path = Path(repo_root) / _DEFAULT_POLICY_REL
        with open(path, encoding="utf-8") as handle:
            data = yaml.safe_load(handle)
        if not isinstance(data, dict):
            raise ValueError(f"Policy file {path} must be a top-level mapping")
        return cls(FreshnessPolicy.from_mapping(data))

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> "EvalFreshnessGate":
        return cls(FreshnessPolicy.from_mapping(raw))

    @property
    def policy(self) -> FreshnessPolicy:
        return self._policy

    def check(
        self,
        *,
        change_class: str,
        eval_record_timestamp: float | None,
        now: float | None = None,
    ) -> FreshnessDecision:
        """Return a :class:`FreshnessDecision` for ``change_class``.

        ``eval_record_timestamp`` is the epoch seconds of the gating eval
        record. ``None`` means "no eval record supplied" — gate blocks unless
        the policy class explicitly has ``null`` TTL (doc-only) or
        ``default_on_unknown_class == "allow"``.

        ``now`` defaults to ``time.time()``.
        """

        now = time.time() if now is None else float(now)
        decision = self._decide(
            change_class=change_class,
            eval_record_timestamp=eval_record_timestamp,
            now=now,
        )
        # v6 KPI accounting: every check is one attempted write; fresh
        # writes are those not blocked by freshness. Guardian-exempt
        # counter update — must never throw in the hot path.
        self._total_writes += 1
        if not decision.blocked:
            self._fresh_writes += 1
        return decision

    def _decide(
        self,
        *,
        change_class: str,
        eval_record_timestamp: float | None,
        now: float,
    ) -> FreshnessDecision:
        # Emergency fail-open: loud warning, not blocked. Audit trail survives.
        if self._policy.fail_open:
            return FreshnessDecision(
                blocked=False,
                change_class=change_class,
                age_seconds=None if eval_record_timestamp is None else max(0.0, now - eval_record_timestamp),
                ttl_seconds=self._policy.ttl_seconds.get(change_class),
                reason=(f"fail_open=true in policy (adr={self._policy.fail_open_adr_ref!r}); write allowed"),
            )

        if change_class not in self._policy.ttl_seconds:
            default = self._policy.default_on_unknown_class
            if default == "allow":
                return FreshnessDecision(
                    blocked=False,
                    change_class=change_class,
                    age_seconds=None,
                    ttl_seconds=None,
                    reason=f"unknown change_class {change_class!r}; default=allow",
                )
            if default == "warn":
                return FreshnessDecision(
                    blocked=False,
                    change_class=change_class,
                    age_seconds=None,
                    ttl_seconds=None,
                    reason=f"unknown change_class {change_class!r}; default=warn (not blocking)",
                )
            return FreshnessDecision(
                blocked=True,
                change_class=change_class,
                age_seconds=None,
                ttl_seconds=None,
                reason=f"unknown change_class {change_class!r}; default=block",
            )

        ttl = self._policy.ttl_seconds[change_class]

        # Null TTL == class is exempt (documentation-only).
        if ttl is None:
            return FreshnessDecision(
                blocked=False,
                change_class=change_class,
                age_seconds=None if eval_record_timestamp is None else max(0.0, now - eval_record_timestamp),
                ttl_seconds=None,
                reason=f"change_class {change_class!r} has null TTL (exempt)",
            )

        if eval_record_timestamp is None:
            return FreshnessDecision(
                blocked=True,
                change_class=change_class,
                age_seconds=None,
                ttl_seconds=ttl,
                reason=(
                    f"change_class {change_class!r} requires an eval record "
                    f"within {ttl:.0f}s but none was supplied"
                ),
            )

        age = now - float(eval_record_timestamp)
        if age < 0:
            # Future-dated eval record — treat as fresh but flag it.
            return FreshnessDecision(
                blocked=False,
                change_class=change_class,
                age_seconds=age,
                ttl_seconds=ttl,
                reason="eval timestamp is in the future; treated as fresh (clock skew?)",
            )
        if age > ttl:
            return FreshnessDecision(
                blocked=True,
                change_class=change_class,
                age_seconds=age,
                ttl_seconds=ttl,
                reason=(
                    f"eval record age {age:.0f}s exceeds TTL {ttl:.0f}s for change_class {change_class!r}"
                ),
            )
        return FreshnessDecision(
            blocked=False,
            change_class=change_class,
            age_seconds=age,
            ttl_seconds=ttl,
            reason=f"fresh ({age:.0f}s <= {ttl:.0f}s)",
        )

    # --- v6 KPI surface -------------------------------------------------

    @property
    def write_counters(self) -> tuple[int, int]:
        """Return ``(fresh_writes, total_writes)`` since construction/reset."""
        return (self._fresh_writes, self._total_writes)

    def reset_counters(self) -> None:
        """Reset the v6 KPI counters. Does not affect policy."""
        self._fresh_writes = 0
        self._total_writes = 0

    def publish_kpi_sample(self, board: Any) -> None:
        """Publish the current EVAL_FRESHNESS_ON_WRITE ratio to ``board``.

        Accepts any object duck-typed as :class:`V6KPIBoard` so this module
        does not depend on the producer helper module at import time.
        The helper never raises — failures are logged via the producer
        module's guardian-exempt logger.
        """
        # Lazy import to avoid import-time cycle with v6_kpi_producers.
        from .v6_kpi_producers import (  # noqa: PLC0415
            record_eval_freshness_on_write,
        )

        record_eval_freshness_on_write(
            board,
            fresh_writes=self._fresh_writes,
            total_writes=self._total_writes,
        )
