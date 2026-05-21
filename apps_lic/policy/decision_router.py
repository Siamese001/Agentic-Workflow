"""DecisionRouter — generic engine for declarative policy tables.

A `DecisionRouter` instance loads a YAML policy file at construction time,
validates it against a fixed schema, then resolves an incoming state dict
against the policy's rule rows using first-match semantics. Each resolve
emits a `ROUTER_DECISION:` marker line so the call participates in the
closed-loop router ledger family per constitutional §29.

Policy YAML schema (top-level keys):

    policy_name: str        # logical identity, e.g. "exit_policy"
    layer: str              # one of L0..L6 — used in ROUTER_DECISION marker
    router: str             # short identifier, e.g. "exit_gate"
    inputs: list[str]       # state keys that rules may match against
    outputs: list[str]      # output keys produced when a rule matches
    default: dict           # output values if NO rule matches
    rules: list[Rule]       # ordered; first match wins

Each `Rule`:

    rule_id: str            # stable identifier (used in audit + tests)
    when: dict[str, Any]    # all key→value pairs MUST match input state
                            # value can be: scalar (==), list (in), or
                            # the special string "*" (any) — see _matches_when
    then: dict[str, Any]    # output values for the matched verdict

This module is intentionally tiny (~ one class, two helpers). It does NOT
implement scored-match, multi-policy composition, or runtime hot-reload —
those are deliberate non-goals; the simplicity is the point.
"""
from __future__ import annotations

import logging
import os
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

LOG = logging.getLogger(__name__)


class PolicyLoadError(ValueError):
    """Raised when a policy YAML fails schema validation."""


class NoMatchError(LookupError):
    """Raised when no rule matches and no default is declared."""


@dataclass(frozen=True)
class PolicyMatch:
    """The result of a successful or default-fallback resolve."""

    policy_name: str
    rule_id: str  # "default" if fallback
    inputs_subset: dict[str, Any]
    verdict: dict[str, Any]
    matched: bool  # False iff this is the default branch


_REQUIRED_TOP_KEYS = {"policy_name", "layer", "router", "rules"}


class DecisionRouter:
    """Resolve a state dict against a YAML policy with first-match semantics.

    Construct once per policy file (cheap; YAML loaded eagerly at __init__).
    Call `resolve(state)` per decision; each call is O(N rules * M when keys)
    and never raises on missing input keys (treated as "key absent" — only
    rules that DO NOT require the key can match).
    """

    def __init__(self, policy_path: str | Path) -> None:
        self.policy_path = Path(policy_path)
        if not self.policy_path.is_file():
            raise PolicyLoadError(f"Policy file not found: {policy_path}")
        try:
            with open(self.policy_path, encoding="utf-8") as f:
                self._policy: dict[str, Any] = yaml.safe_load(f) or {}
        except yaml.YAMLError as exc:
            raise PolicyLoadError(f"Invalid YAML at {policy_path}: {exc}") from exc
        self._validate_policy()
        self.policy_name: str = self._policy["policy_name"]
        self.layer: str = self._policy["layer"]
        self.router: str = self._policy["router"]
        self._rules: list[dict[str, Any]] = list(self._policy["rules"])
        self._default: dict[str, Any] = dict(self._policy.get("default") or {})
        self._inputs: list[str] = list(self._policy.get("inputs") or [])

    def _validate_policy(self) -> None:
        missing = _REQUIRED_TOP_KEYS - set(self._policy.keys())
        if missing:
            raise PolicyLoadError(
                f"Policy {self.policy_path} missing required top-level keys: {sorted(missing)}"
            )
        rules = self._policy.get("rules")
        if not isinstance(rules, list) or not rules:
            raise PolicyLoadError(
                f"Policy {self.policy_path} 'rules' must be a non-empty list"
            )
        for idx, rule in enumerate(rules):
            if not isinstance(rule, dict):
                raise PolicyLoadError(
                    f"Policy {self.policy_path} rule[{idx}] is not a mapping"
                )
            for required in ("rule_id", "when", "then"):
                if required not in rule:
                    raise PolicyLoadError(
                        f"Policy {self.policy_path} rule[{idx}] missing '{required}'"
                    )
            if not isinstance(rule["when"], dict):
                raise PolicyLoadError(
                    f"Policy {self.policy_path} rule[{idx}] 'when' must be a mapping"
                )
            if not isinstance(rule["then"], dict):
                raise PolicyLoadError(
                    f"Policy {self.policy_path} rule[{idx}] 'then' must be a mapping"
                )

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #

    def resolve(
        self,
        state: dict[str, Any],
        *,
        trace_id: str | None = None,
        emit_marker: bool | None = None,
    ) -> PolicyMatch:
        """Match `state` against rules in order; return first match or default.

        Args:
            state: input dict; rule `when` clauses match against these keys.
            trace_id: optional caller-supplied trace id to thread into the
                ROUTER_DECISION marker; auto-generated if omitted.
            emit_marker: override marker emission. Defaults to env var
                ROUTER_ENFORCEMENT_BYPASS unset → True.

        Returns:
            `PolicyMatch` with `matched=True` for a rule hit, `matched=False`
            and `rule_id="default"` for the fallback branch.

        Raises:
            NoMatchError: only if no rule matches AND no `default` was declared
                in the policy YAML.
        """
        if not isinstance(state, dict):
            raise TypeError(f"state must be dict, got {type(state).__name__}")

        do_emit = self._should_emit_marker(emit_marker)
        decision_id = uuid.uuid4().hex
        trace_id = trace_id or decision_id

        for rule in self._rules:
            if _matches_when(rule["when"], state):
                match = PolicyMatch(
                    policy_name=self.policy_name,
                    rule_id=str(rule["rule_id"]),
                    inputs_subset=_subset(state, self._inputs),
                    verdict=dict(rule["then"]),
                    matched=True,
                )
                if do_emit:
                    self._emit_router_decision(match, decision_id, trace_id)
                return match

        if not self._default:
            raise NoMatchError(
                f"Policy {self.policy_name} found no matching rule and "
                f"declared no default; state keys: {sorted(state.keys())}"
            )
        match = PolicyMatch(
            policy_name=self.policy_name,
            rule_id="default",
            inputs_subset=_subset(state, self._inputs),
            verdict=dict(self._default),
            matched=False,
        )
        if do_emit:
            self._emit_router_decision(match, decision_id, trace_id)
        return match

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #

    @staticmethod
    def _should_emit_marker(override: bool | None) -> bool:
        if override is not None:
            return override
        if os.environ.get("ROUTER_ENFORCEMENT_BYPASS") == "1":
            return False
        return True

    def _emit_router_decision(
        self, match: PolicyMatch, decision_id: str, trace_id: str
    ) -> None:
        """Emit the ROUTER_DECISION marker line per constitutional §29.

        Format: `ROUTER_DECISION: layer=<L> router=<r> decision_id=<id> ...`
        Stdout is the canonical sink; this function never raises so that
        marker emission failure does not mask the decision itself.
        """
        try:
            verdict_label = next(iter(match.verdict.values()), "unknown")
            print(
                f"ROUTER_DECISION: layer={self.layer} router={self.router} "
                f"decision_id={decision_id} trace_id={trace_id} "
                f"route_id={self.policy_name} selected={verdict_label} "
                f"rule_id={match.rule_id} matched={match.matched} "
                f"ts={time.time():.3f}",
                flush=True,
            )
        except Exception:  # guardian: allow-log-and-swallow -- marker emission is best-effort  # guardian: allow-broad-exception -- P2 burndown: fail-soft optional boundary
            LOG.debug("ROUTER_DECISION marker emission failed", exc_info=True)


# ---------------------------------------------------------------------- #
# Module-level helpers
# ---------------------------------------------------------------------- #


def _matches_when(when: dict[str, Any], state: dict[str, Any]) -> bool:
    """Test whether every (key, expected) in `when` matches `state[key]`.

    Match semantics:
      - expected == "*"      → key must be present (any value)
      - expected is list     → state[key] must be IN the list
      - expected is scalar   → state[key] == expected

    Missing input key → rule does NOT match.
    """
    for key, expected in when.items():
        if key not in state:
            return False
        actual = state[key]
        if expected == "*":
            continue
        if isinstance(expected, list):
            if actual not in expected:
                return False
        else:
            if actual != expected:
                return False
    return True


def _subset(state: dict[str, Any], keys: list[str]) -> dict[str, Any]:
    """Return state restricted to declared `keys` (for audit hashing)."""
    if not keys:
        return {}
    return {k: state[k] for k in keys if k in state}
