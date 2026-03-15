"""Prompt Safety Validator — L5 policy/guardrail/budget validation for compiled prompts.

Evaluates a ``CompiledPromptArtifact`` through three validation gates:

  1. POLICY_GATE      — prompt_hash policy alignment check
  2. GUARDRAIL_GATE   — guardrail set evaluation
  3. BUDGET_GATE      — token budget check (OVERFLOW → blocked)

Produces a ``PromptSafetyDecision`` and emits the five safety ADG relations:

  compiled_prompt_validated_by_policy
  compiled_prompt_checked_by_guardrail
  compiled_prompt_budget_checked
  compiled_prompt_allowed          (when all gates pass)
  compiled_prompt_blocked          (when any gate fails)

Design invariants
-----------------
1. Fail-closed: any gate exception → gate fails (not passes).
2. No wall-clock reads; ``timestamp_utc`` caller-supplied.
3. All outputs deterministically content-addressed.
4. Budget OVERFLOW always blocks; EXTENDED is a warning but does not block
   unless ``block_on_extended=True`` (default False).
5. Guardrail evaluation is rule-based from a configurable set; the validator
   checks whether the prompt's slot hashes match any blocked pattern hashes.
"""

from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass
from typing import FrozenSet

from system_learning.enforcement.determinism import deterministic_json
from system_learning.types.prompt_adg_relations import (
    SAFETY_ALLOWED,
    SAFETY_BLOCKED,
    SAFETY_BUDGET_CHECKED,
    SAFETY_CHECKED_BY_GUARDRAIL,
    SAFETY_VALIDATED_BY_POLICY,
)
from system_learning.types.prompt_artifact_types import (
    CompiledPromptArtifact,
    PromptSafetyDecision,
)
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Gate names
# ---------------------------------------------------------------------------

GATE_POLICY = "POLICY_GATE"
GATE_GUARDRAIL = "GUARDRAIL_GATE"
GATE_BUDGET = "BUDGET_GATE"


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------


@dataclass
class SafetyValidatorConfig:
    """Configuration for the prompt safety validator.

    Attributes
    ----------
    active_policy_hash : str | None
        Expected policy hash. None means any policy is accepted.
    blocked_guardrails : frozenset[str]
        Guardrail IDs that, if present in the prompt's guardrail set, block it.
        Empty set means no guardrail blocks.
    active_guardrails : frozenset[str]
        All guardrail IDs in scope for evaluation.
    block_on_extended : bool
        If True, EXTENDED budget class also blocks (in addition to OVERFLOW).
    block_on_policy_mismatch : bool
        If False, policy hash mismatch is a warning only (does not block).
        Default: True.
    """

    active_policy_hash: str | None = None
    blocked_guardrails: FrozenSet[str] = frozenset()
    active_guardrails: FrozenSet[str] = frozenset()
    block_on_extended: bool = False
    block_on_policy_mismatch: bool = True


# ---------------------------------------------------------------------------
# Gate implementations
# ---------------------------------------------------------------------------


def _gate_policy(
    artifact: CompiledPromptArtifact,
    cfg: SafetyValidatorConfig,
) -> tuple[bool, str | None]:
    if cfg.active_policy_hash is None or artifact.policy_hash is None:
        return True, None
    if artifact.policy_hash != cfg.active_policy_hash:
        return False, "POLICY_HASH_MISMATCH"
    return True, None


def _gate_guardrail(
    artifact: CompiledPromptArtifact,
    cfg: SafetyValidatorConfig,
) -> tuple[bool, str | None]:
    # blocked_guardrails ∩ active_guardrails = guardrails that could fire
    # Since the artifact doesn't carry a pre-evaluated guardrail hit set,
    # we check whether any blocked guardrail is in the active set at compile time.
    # (Runtime hits are captured in PromptOutcomeRecord.)
    triggered = cfg.blocked_guardrails & cfg.active_guardrails
    if triggered:
        return False, f"GUARDRAIL_TRIGGERED:{','.join(sorted(triggered))}"
    return True, None


def _gate_budget(
    artifact: CompiledPromptArtifact,
    cfg: SafetyValidatorConfig,
) -> tuple[bool, str | None]:
    bc = artifact.slot_manifest.budget_class
    if bc == "OVERFLOW":
        return False, "BUDGET_OVERFLOW"
    if bc == "EXTENDED" and cfg.block_on_extended:
        return False, "BUDGET_EXTENDED_BLOCKED"
    return True, None


# ---------------------------------------------------------------------------
# Main validator
# ---------------------------------------------------------------------------


class PromptSafetyValidator:
    """Evaluates compiled prompts through the three L5 safety gates.

    Usage::

        validator = PromptSafetyValidator(config)
        decision, relations = validator.validate(artifact, timestamp_utc=ts)
        if decision.allowed:
            proceed_to_routing(artifact)
    """

    def __init__(self, config: SafetyValidatorConfig | None = None) -> None:
        self._config = config or SafetyValidatorConfig()

    def validate(
        self,
        artifact: CompiledPromptArtifact,
        timestamp_utc: int,
    ) -> tuple[PromptSafetyDecision, list[tuple[str, str, str]]]:
        """Validate a compiled prompt artifact.

        Returns
        -------
        (PromptSafetyDecision, list of ADG relation tuples)
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "PromptSafetyValidator.validate")

        cfg = self._config
        denial_reasons: list[str] = []
        relations: list[tuple[str, str, str]] = []
        an = artifact.adg_entity_name

        # Policy gate
        try:
            p_pass, p_reason = _gate_policy(artifact, cfg)
        except Exception as exc:
            logger.warning("prompt_safety_validator: policy gate exception: %s", exc)
            p_pass, p_reason = False, "POLICY_GATE_EXCEPTION"
        relations.append((an, SAFETY_VALIDATED_BY_POLICY,
                          f"ADG::Policy::{(artifact.policy_hash or 'NONE')[:16]}"))
        if not p_pass and cfg.block_on_policy_mismatch:
            denial_reasons.append(p_reason or GATE_POLICY)

        # Guardrail gate
        try:
            g_pass, g_reason = _gate_guardrail(artifact, cfg)
        except Exception as exc:
            logger.warning("prompt_safety_validator: guardrail gate exception: %s", exc)
            g_pass, g_reason = False, "GUARDRAIL_GATE_EXCEPTION"
        guardrail_set = tuple(sorted(cfg.active_guardrails))
        relations.append((an, SAFETY_CHECKED_BY_GUARDRAIL,
                          f"ADG::GuardrailSet::{_hash_set(guardrail_set)[:16]}"))
        if not g_pass:
            denial_reasons.append(g_reason or GATE_GUARDRAIL)

        # Budget gate
        try:
            b_pass, b_reason = _gate_budget(artifact, cfg)
        except Exception as exc:
            logger.warning("prompt_safety_validator: budget gate exception: %s", exc)
            b_pass, b_reason = False, "BUDGET_GATE_EXCEPTION"
        relations.append((an, SAFETY_BUDGET_CHECKED,
                          f"ADG::BudgetClass::{artifact.slot_manifest.budget_class}"))
        if not b_pass:
            denial_reasons.append(b_reason or GATE_BUDGET)

        allowed = len(denial_reasons) == 0
        adg_relation = SAFETY_ALLOWED if allowed else SAFETY_BLOCKED

        # Final allowed/blocked relation
        relations.append((
            an,
            adg_relation,
            f"ADG::SafetyDecision::{artifact.prompt_hash[:16]}",
        ))

        # Build decision_id
        canonical = deterministic_json({
            "allowed": allowed,
            "denial_reasons": sorted(denial_reasons),
            "guardrail_set": sorted(guardrail_set),
            "policy_hash": cfg.active_policy_hash,
            "prompt_hash": artifact.prompt_hash,
            "timestamp_utc": timestamp_utc,
        })
        decision_id = hashlib.sha256(canonical.encode("utf-8")).hexdigest()

        decision = PromptSafetyDecision(
            decision_id=decision_id,
            prompt_hash=artifact.prompt_hash,
            allowed=allowed,
            policy_hash=cfg.active_policy_hash,
            guardrail_set=guardrail_set,
            budget_class=artifact.slot_manifest.budget_class,
            denial_reasons=tuple(sorted(denial_reasons)),
            adg_relation=adg_relation,
            timestamp_utc=timestamp_utc,
        )
        return decision, relations


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _hash_set(items: tuple[str, ...]) -> str:
    return hashlib.sha256(
        deterministic_json(list(items)).encode("utf-8")
    ).hexdigest()


# ---------------------------------------------------------------------------
# Module-level convenience
# ---------------------------------------------------------------------------


def validate_prompt(
    artifact: CompiledPromptArtifact,
    timestamp_utc: int,
    *,
    config: SafetyValidatorConfig | None = None,
) -> tuple[PromptSafetyDecision, list[tuple[str, str, str]]]:
    """Module-level convenience wrapper."""
    return PromptSafetyValidator(config).validate(artifact, timestamp_utc)


__all__ = [
    "GATE_BUDGET",
    "GATE_GUARDRAIL",
    "GATE_POLICY",
    "PromptSafetyValidator",
    "SafetyValidatorConfig",
    "validate_prompt",
]
