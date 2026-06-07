"""Guardrail Bank Contract — L5 v4 Wave-A (G-01, G-02, G-08, G-20).

Decomposes the single Policy Validation Chokepoint of v3 into an explicit,
named, two-layer bank with egress inspection and optional guard-model review:

- **G-01** Named guardrail catalog: 11 canonical families (PII, Secrets,
  Jailbreak, Moderation, NSFW, OffTopic, Competitors, Hallucination,
  UrlSafety, Keyword, Custom).
- **G-02** Layered guardrails: `client_universal` rail evaluates FIRST at
  the runtime lane entry; `agent_domain` rail evaluates SECOND with
  domain-specific policy. Order is enforced by the bank.
- **G-08** Egress inspection: every `evaluate_egress` result MUST classify
  the LLM response against PII / Secrets / Hallucination / UrlSafety before
  the response leaves the LLM Gateway boundary.
- **G-20** Guard-model review: an optional SECOND-model review stage on
  HIGH-risk egress; composes with G-08 egress inspection.

Additive: emits result contracts only. Concrete guardrail implementations
live in existing `agentic_core/L5_safety/validators/` and are wired in by
separate waves (not this one). This module defines the SHAPE of results
every guardrail must emit so the policy chokepoint can reason uniformly.

Reference:
  - docs/reference/00_L5_Policy_Plane/guardrail_families.md
  - docs/reference/00_L5_Policy_Plane/Governance & Safety v4.md (Runtime Lane)
Parent plan: docs/archive/windsurf/legacy-tree/plans/l5-governance-best-practice-gap-4615ae.md
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Literal


class GuardrailFamily(str, Enum):
    """G-01: Named guardrail families. Closed set."""

    PII = "pii"
    SECRETS = "secrets"
    JAILBREAK = "jailbreak"
    MODERATION = "moderation"
    NSFW = "nsfw"
    OFF_TOPIC = "off_topic"
    COMPETITORS = "competitors"
    HALLUCINATION = "hallucination"
    URL_SAFETY = "url_safety"
    KEYWORD = "keyword"
    CUSTOM = "custom"


GuardrailLayer = Literal["client_universal", "agent_domain"]
GuardrailStage = Literal["ingress", "egress", "guard_model"]
GuardrailAction = Literal["allow", "remediate", "reject"]


@dataclass(frozen=True)
class GuardrailOutcome:
    """Immutable outcome of a single guardrail family's evaluation.

    `action` determines downstream routing per the Decision Rail:
      - `allow`     → continue through the chokepoint
      - `remediate` → safe-to-remediate; forbidden on hard_constraint=True (G-15)
      - `reject`    → terminate with REJECT; hard constraint violation
    """

    family: GuardrailFamily
    layer: GuardrailLayer
    stage: GuardrailStage
    action: GuardrailAction
    score: float  # 0.0 == clean, 1.0 == certain violation
    evidence: str  # short human-readable reason code
    hard_constraint: bool = False
    policy_id: str = ""
    policy_version: str = ""

    def __post_init__(self) -> None:
        if not 0.0 <= self.score <= 1.0:
            raise ValueError(
                f"GuardrailOutcome: score must be in [0.0, 1.0], got {self.score}",
            )
        if self.action not in ("allow", "remediate", "reject"):
            raise ValueError(
                f"GuardrailOutcome: action must be allow|remediate|reject, got '{self.action}'",
            )
        if self.hard_constraint and self.action == "remediate":
            raise ValueError(
                "GuardrailOutcome: remediate is FORBIDDEN on hard_constraint=True "
                "(G-15 invariant). Use 'reject' instead.",
            )
        if not self.evidence:
            raise ValueError("GuardrailOutcome: evidence required")

    def to_dict(self) -> dict[str, Any]:
        return {
            "action": self.action,
            "evidence": self.evidence,
            "family": self.family.value,
            "hard_constraint": self.hard_constraint,
            "layer": self.layer,
            "policy_id": self.policy_id,
            "policy_version": self.policy_version,
            "score": self.score,
            "stage": self.stage,
        }


@dataclass(frozen=True)
class GuardrailBankVerdict:
    """Aggregate verdict across ALL guardrail families at a given stage.

    The bank resolves the verdict by strict precedence:
      1. Any `reject` → verdict=reject
      2. Any hard-constraint `remediate` → raise ValueError (G-15 violation in input)
      3. Any `remediate` → verdict=remediate
      4. Otherwise → verdict=allow

    `ordered_outcomes` preserves evaluation order so the audit log can
    reconstruct the precise path through the bank.
    """

    stage: GuardrailStage
    verdict: GuardrailAction
    ordered_outcomes: tuple[GuardrailOutcome, ...]
    digest: str

    def __post_init__(self) -> None:
        if not self.digest:
            raise ValueError("GuardrailBankVerdict: digest required")
        if not self.ordered_outcomes:
            # An empty bank at a stage is legal (no rules configured) and
            # must default-allow, but still produce a deterministic digest.
            pass

    def to_dict(self) -> dict[str, Any]:
        return {
            "digest": self.digest,
            "ordered_outcomes": [o.to_dict() for o in self.ordered_outcomes],
            "stage": self.stage,
            "verdict": self.verdict,
        }


def resolve_bank_verdict(
    stage: GuardrailStage,
    outcomes: tuple[GuardrailOutcome, ...],
) -> GuardrailBankVerdict:
    """Resolve a bank of guardrail outcomes into a single verdict.

    Evaluation order (G-02): `client_universal` outcomes FIRST, then
    `agent_domain`. Within each layer, outcomes are evaluated in their
    provided order — callers are responsible for ordering families by
    severity / fan-in.

    Raises ValueError if any outcome violates G-15 (hard_constraint=True
    with action='remediate') — the GuardrailOutcome constructor already
    catches this at construction time; this is a defensive second pass.
    """
    # Enforce layer ordering (client_universal before agent_domain)
    layered = sorted(
        outcomes,
        key=lambda o: 0 if o.layer == "client_universal" else 1,
    )
    ordered = tuple(layered)

    has_reject = any(o.action == "reject" for o in ordered)
    has_hard_remediate = any(o.hard_constraint and o.action == "remediate" for o in ordered)
    has_remediate = any(o.action == "remediate" for o in ordered)

    if has_hard_remediate:
        raise ValueError(
            "resolve_bank_verdict: G-15 violation — hard_constraint with "
            "action=remediate. Use 'reject' instead.",
        )

    if has_reject:
        verdict: GuardrailAction = "reject"
    elif has_remediate:
        verdict = "remediate"
    else:
        verdict = "allow"

    # Deterministic digest over ordered outcomes + stage
    canonical = json.dumps(
        {
            "ordered_outcomes": [o.to_dict() for o in ordered],
            "stage": stage,
            "verdict": verdict,
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    return GuardrailBankVerdict(
        stage=stage,
        verdict=verdict,
        ordered_outcomes=ordered,
        digest=digest,
    )


@dataclass(frozen=True)
class EgressInspectionResult:
    """G-08: Egress-side inspection of an LLM response before it leaves the
    LLM Gateway boundary.

    Composes a G-02 bank verdict with optional G-20 guard-model outcome.
    The LLM Gateway MUST NOT emit the response to downstream callers if
    `final_action != 'allow'`.
    """

    bank_verdict: GuardrailBankVerdict
    guard_model_outcome: GuardrailOutcome | None
    final_action: GuardrailAction

    def __post_init__(self) -> None:
        if self.bank_verdict.stage != "egress":
            raise ValueError(
                "EgressInspectionResult: bank_verdict.stage must be 'egress', "
                f"got '{self.bank_verdict.stage}'",
            )
        if self.guard_model_outcome is not None:
            if self.guard_model_outcome.stage != "guard_model":
                raise ValueError(
                    "EgressInspectionResult: guard_model_outcome.stage must be "
                    f"'guard_model', got '{self.guard_model_outcome.stage}'",
                )
        # final_action must be the most restrictive of (bank, guard_model)
        _ORDER: dict[GuardrailAction, int] = {"allow": 0, "remediate": 1, "reject": 2}
        bank_rank = _ORDER[self.bank_verdict.verdict]
        guard_rank = _ORDER[self.guard_model_outcome.action] if self.guard_model_outcome is not None else 0
        expected_rank = max(bank_rank, guard_rank)
        expected_action = next(a for a, r in _ORDER.items() if r == expected_rank)
        if self.final_action != expected_action:
            raise ValueError(
                f"EgressInspectionResult: final_action must be the most "
                f"restrictive of bank/guard_model. Expected '{expected_action}', "
                f"got '{self.final_action}'",
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "bank_verdict": self.bank_verdict.to_dict(),
            "final_action": self.final_action,
            "guard_model_outcome": (
                self.guard_model_outcome.to_dict() if self.guard_model_outcome is not None else None
            ),
        }


def compose_egress_inspection(
    bank_verdict: GuardrailBankVerdict,
    guard_model_outcome: GuardrailOutcome | None = None,
) -> EgressInspectionResult:
    """Compose bank + optional guard-model into a final egress verdict.

    `final_action` is the strictly more restrictive of the two:
      reject > remediate > allow.
    """
    _ORDER: dict[GuardrailAction, int] = {"allow": 0, "remediate": 1, "reject": 2}
    bank_rank = _ORDER[bank_verdict.verdict]
    guard_rank = _ORDER[guard_model_outcome.action] if guard_model_outcome is not None else 0
    rank = max(bank_rank, guard_rank)
    final_action: GuardrailAction = next(a for a, r in _ORDER.items() if r == rank)
    return EgressInspectionResult(
        bank_verdict=bank_verdict,
        guard_model_outcome=guard_model_outcome,
        final_action=final_action,
    )


__all__ = [
    "EgressInspectionResult",
    "GuardrailAction",
    "GuardrailBankVerdict",
    "GuardrailFamily",
    "GuardrailLayer",
    "GuardrailOutcome",
    "GuardrailStage",
    "compose_egress_inspection",
    "resolve_bank_verdict",
]
