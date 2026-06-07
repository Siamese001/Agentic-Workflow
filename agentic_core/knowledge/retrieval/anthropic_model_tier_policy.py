"""Anthropic model-tier selection policy for RAG workflows.

Anthropic's guidance (Choosing the right model docs, 2024) is to use the
CHEAPEST capable model per task and only escalate when the workload requires
it. For RAG pipelines specifically:

    - Contextualization / chunk-summarization      -> Haiku   (cost-critical)
    - Reranking (cross-encoder substitute)         -> Haiku   (cost-critical)
    - Final synthesis of cited answer              -> Sonnet  (quality)
    - Complex reasoning over many documents        -> Opus    (capability)
    - Strict JSON shaping of an existing answer    -> Haiku   (deterministic)

Using Sonnet/Opus for tasks a Haiku call can handle wastes 5-50x the cost
for no measurable quality gain. Using Haiku where Sonnet is needed produces
shallow synthesis that hurts grounded-answer quality. Default policy below
encodes Anthropic's stated tier recommendations so callers get the right
model without having to re-derive the tradeoff per workflow.

Design invariants:
- Pure functions. No I/O, no gateway calls, no environment reads.
- Policy is DATA, not logic — easy to override per workflow without
  subclassing. Callers pass a custom policy dict to `select_model` when the
  default is inappropriate.
- Model names are the canonical Anthropic API identifiers at time of
  writing. Callers should prefer constants (e.g. `HAIKU_4_5`) over hardcoded
  strings so a model-name change is a one-line update.
- Fallback: when a task type is unknown, the policy returns the default
  synthesis model (Sonnet) and logs a debug message. This is safer than
  raising — unknown tasks should still execute, just with a conservative
  tier.

References:
- Anthropic API Docs. Choosing the right model.
  https://docs.anthropic.com/en/docs/about-claude/models/choosing-a-model
- Plan: docs/archive/windsurf/legacy-tree/plans/anthropic-rag-gaps-7f3c2a.md (phase P4.2)
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Literal, Mapping

# Wave B (qwen-adoption-waves-a7f3c2) Phase B1: local-Qwen tier integration.
# Importing the L0 SSOT keeps this module in sync with the Qwen vLLM model
# identifier without duplicating env-var logic.
from agentic_core.L0_routing.config.model_registry import (
    QWEN_LOCAL_MODEL_ID,
)

Logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Canonical model names (stable public identifiers on the Anthropic API)
# ---------------------------------------------------------------------------

HAIKU_4_5 = "claude-haiku-4-5"
SONNET_4_5 = "claude-sonnet-4-5"
SONNET_4_6 = "claude-sonnet-4-6"
OPUS_4_5 = "claude-opus-4-5"

# Wave B Phase B1: local Qwen identifier, sourced from L0 model_registry SSOT.
# Exported alongside Anthropic ids so callers can reference a single constant
# regardless of which tier a task lands in.
QWEN_LOCAL = QWEN_LOCAL_MODEL_ID

# Tier labels (ordered cheapest -> most capable).
# Typed as Literal so mypy accepts them as keys/values in the Mapping[TierName, ...] below.
# ``qwen`` precedes ``haiku`` because local-GPU Qwen is zero-marginal-cost
# and is preferred over Haiku for cost-critical tasks when the local vLLM
# server is available.
TierName = Literal["qwen", "haiku", "sonnet", "opus"]
TIER_QWEN: TierName = "qwen"
TIER_HAIKU: TierName = "haiku"
TIER_SONNET: TierName = "sonnet"
TIER_OPUS: TierName = "opus"

# Tier -> canonical model id. Updating one place updates every task-type
# mapping below that references the tier indirectly.
TIER_MODELS: Mapping[TierName, str] = {
    TIER_QWEN: QWEN_LOCAL,
    TIER_HAIKU: HAIKU_4_5,
    TIER_SONNET: SONNET_4_6,
    TIER_OPUS: OPUS_4_5,
}

# ---------------------------------------------------------------------------
# Task types (string constants — easy to extend without enum churn)
# ---------------------------------------------------------------------------

TASK_CHUNK_CONTEXTUALIZATION = "chunk_contextualization"
TASK_RERANKING = "reranking"
TASK_JSON_SHAPING = "json_shaping"
TASK_SYNTHESIS = "synthesis"
TASK_GROUNDED_ANSWER = "grounded_answer"
TASK_DEEP_REASONING = "deep_reasoning"
TASK_MULTI_AGENT_ORCHESTRATION = "multi_agent_orchestration"
TASK_QUICK_CLASSIFICATION = "quick_classification"

# Default policy — the source of truth for "which tier does what".
DEFAULT_TASK_TIER_POLICY: Mapping[str, TierName] = {
    TASK_CHUNK_CONTEXTUALIZATION: TIER_HAIKU,
    TASK_RERANKING: TIER_HAIKU,
    TASK_JSON_SHAPING: TIER_HAIKU,
    TASK_QUICK_CLASSIFICATION: TIER_HAIKU,
    TASK_SYNTHESIS: TIER_SONNET,
    TASK_GROUNDED_ANSWER: TIER_SONNET,
    TASK_DEEP_REASONING: TIER_OPUS,
    TASK_MULTI_AGENT_ORCHESTRATION: TIER_OPUS,
}

# ---------------------------------------------------------------------------
# Policy decision result
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ModelSelection:
    """Outcome of a model-tier lookup.

    Attributes
    ----------
    model:
        Canonical Anthropic model identifier to pass to the Messages API.
    tier:
        Which tier the task mapped to (haiku / sonnet / opus).
    task_type:
        The task type the caller supplied.
    reason:
        Human-readable rationale — useful in telemetry so cost-tier decisions
        are auditable after the fact.
    """

    model: str
    tier: TierName
    task_type: str
    reason: str


# ---------------------------------------------------------------------------
# Lookup functions
# ---------------------------------------------------------------------------


def select_model(
    task_type: str,
    *,
    policy: Mapping[str, TierName] | None = None,
    tier_models: Mapping[TierName, str] | None = None,
    default_tier: TierName = TIER_SONNET,
) -> ModelSelection:
    """Pick the cheapest capable Anthropic model for a given task type.

    Parameters
    ----------
    task_type:
        One of the ``TASK_*`` constants, or a caller-defined string present
        in ``policy``. Unknown task types fall back to ``default_tier``.
    policy:
        Optional override of the task->tier mapping. Defaults to
        ``DEFAULT_TASK_TIER_POLICY``.
    tier_models:
        Optional override of the tier->model mapping (useful for testing
        with stub model names or pinning to older versions).
    default_tier:
        Tier used when ``task_type`` is unknown to ``policy``. Default is
        Sonnet — conservative middle ground.

    Returns
    -------
    ``ModelSelection`` with model id, tier, and reasoning.
    """
    active_policy = policy if policy is not None else DEFAULT_TASK_TIER_POLICY
    active_tier_models = tier_models if tier_models is not None else TIER_MODELS

    tier = active_policy.get(task_type, default_tier)
    if task_type not in active_policy:
        Logger.debug(
            "Unknown task_type %r; falling back to default tier %r",
            task_type,
            default_tier,
        )
        reason = f"task_type {task_type!r} not in policy; defaulted to tier {tier!r}"
    else:
        reason = f"task_type {task_type!r} maps to tier {tier!r} per policy"

    model = active_tier_models.get(tier)
    if model is None:
        # Tier is in policy but missing from tier_models — misconfiguration.
        # Fall back to the default-tier model; if that also missing, surface
        # a clear error (invariant: at least the default tier MUST be mapped).
        model = active_tier_models.get(default_tier)
        if model is None:
            raise ValueError(f"tier_models is missing both {tier!r} and default {default_tier!r}")
        reason += f" (tier {tier!r} missing a model; used {default_tier!r} fallback)"

    return ModelSelection(model=model, tier=tier, task_type=task_type, reason=reason)


# ---------------------------------------------------------------------------
# Wave B Phase B1: Qwen-preferred policy overlay
# ---------------------------------------------------------------------------
#
# Cost-critical tasks (contextualization, reranking, JSON shaping, quick
# classification) are well within Qwen-2.5-32B-Instruct-AWQ's capability for
# zero marginal cost. The overlay below substitutes ``TIER_QWEN`` for
# ``TIER_HAIKU`` on exactly those tasks while leaving synthesis / reasoning
# tasks pointed at Anthropic Sonnet / Opus.
#
# Synthesis and deep-reasoning stay on Anthropic because Qwen's long-context
# citation fidelity and reasoning depth still lag Sonnet/Opus for production
# RAG answers. This policy is the conservative first step — per-task A/B
# comparisons can lift more tasks into TIER_QWEN later without changing
# any caller code.

QWEN_COST_CRITICAL_TASK_TIER_POLICY: Mapping[str, TierName] = {
    TASK_CHUNK_CONTEXTUALIZATION: TIER_QWEN,
    TASK_RERANKING: TIER_QWEN,
    TASK_JSON_SHAPING: TIER_QWEN,
    TASK_QUICK_CLASSIFICATION: TIER_QWEN,
    TASK_SYNTHESIS: TIER_SONNET,
    TASK_GROUNDED_ANSWER: TIER_SONNET,
    TASK_DEEP_REASONING: TIER_OPUS,
    TASK_MULTI_AGENT_ORCHESTRATION: TIER_OPUS,
}


def get_active_policy() -> Mapping[str, TierName]:
    """Return the task -> tier policy for the current environment.

    Selects ``QWEN_COST_CRITICAL_TASK_TIER_POLICY`` when either:
      * ``USE_QWEN_COST_CRITICAL=1`` is explicitly set, OR
      * ``VLLM_BASE_URL`` is set (local vLLM intent signal) AND
        ``USE_QWEN_COST_CRITICAL`` is not explicitly set to ``0``.

    Otherwise returns the Anthropic-only ``DEFAULT_TASK_TIER_POLICY``.

    This helper lets call-sites opt into Qwen without hardcoding env-var
    checks at every callsite.
    """
    flag = (os.getenv("USE_QWEN_COST_CRITICAL") or "").strip().lower()
    if flag in ("1", "true", "yes", "on"):
        return QWEN_COST_CRITICAL_TASK_TIER_POLICY
    if flag in ("0", "false", "no", "off"):
        return DEFAULT_TASK_TIER_POLICY
    # Unset -> infer from VLLM_BASE_URL presence.
    if os.getenv("VLLM_BASE_URL"):
        return QWEN_COST_CRITICAL_TASK_TIER_POLICY
    return DEFAULT_TASK_TIER_POLICY


def compose_two_pass_models(
    *,
    policy: Mapping[str, TierName] | None = None,
    tier_models: Mapping[TierName, str] | None = None,
) -> tuple[str, str]:
    """Convenience: the (pass1_model, pass2_model) pair for a dual-pass flow.

    Pass 1 is the grounded-answer-with-citations call (Sonnet by default —
    quality matters, citations are being produced). Pass 2 is the JSON
    reshape of that answer (Haiku — deterministic transformation, no new
    reasoning required).

    Returns:
        (pass1_model, pass2_model)
    """
    pass1 = select_model(TASK_GROUNDED_ANSWER, policy=policy, tier_models=tier_models).model
    pass2 = select_model(TASK_JSON_SHAPING, policy=policy, tier_models=tier_models).model
    return pass1, pass2


__all__ = [
    # Model identifiers
    "HAIKU_4_5",
    "SONNET_4_5",
    "SONNET_4_6",
    "OPUS_4_5",
    "QWEN_LOCAL",
    # Tier labels
    "TIER_QWEN",
    "TIER_HAIKU",
    "TIER_SONNET",
    "TIER_OPUS",
    # Task types
    "TASK_CHUNK_CONTEXTUALIZATION",
    "TASK_RERANKING",
    "TASK_JSON_SHAPING",
    "TASK_SYNTHESIS",
    "TASK_GROUNDED_ANSWER",
    "TASK_DEEP_REASONING",
    "TASK_MULTI_AGENT_ORCHESTRATION",
    "TASK_QUICK_CLASSIFICATION",
    # Policy & lookup
    "TIER_MODELS",
    "DEFAULT_TASK_TIER_POLICY",
    "QWEN_COST_CRITICAL_TASK_TIER_POLICY",
    "ModelSelection",
    "select_model",
    "compose_two_pass_models",
    "get_active_policy",
]
