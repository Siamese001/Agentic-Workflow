"""L5 Guardrail Family Registry (G9 closure).

Curated SSOT for the 18 named guardrail families F-01..F-18 from
``guardrail_families.md``. Surfacing the family taxonomy as typed
``GuardrailFamilyRecord`` instances lets callers reference families by ID
(rather than free-form strings inside ``governance_reports``).

Hard-constraint families per `guardrail_families.md` §5: F-01 (Moderation
CSAM class), F-02, F-04, F-05, F-17, F-18 — REMEDIATE forbidden on breach.
"""

from __future__ import annotations

from typing import Mapping

from agentic_core.L5_safety.v5.contracts import GuardrailFamilyRecord
from agentic_core.L5_safety.v5.types import (
    EvaluatorKind,
    GuardrailBank,
    GuardrailFamilyId,
    GuardrailStage,
)


def _activation(low: bool, mod: bool, high: bool) -> Mapping[str, bool]:
    return {"LOW": low, "MODERATE": mod, "HIGH": high}


# Threshold defaults are placeholders; real values are owned by the
# Calibration Plane (`config/judges/`). The registry pins the *structure*.
_DEFAULT_THRESHOLD = 0.5


_FAMILIES: dict[GuardrailFamilyId, GuardrailFamilyRecord] = {
    GuardrailFamilyId.F01_MODERATION: GuardrailFamilyRecord(
        id=GuardrailFamilyId.F01_MODERATION,
        name="Moderation",
        stage=GuardrailStage.INGRESS,
        bank=GuardrailBank.CLIENT_UNIVERSAL,
        evaluator_kind=EvaluatorKind.CLASSIFIER,
        risk_tier_activation=_activation(True, True, True),
        hard_constraint=True,  # CSAM class
        remediable_when_false=False,
        owner="L5 governance",
        eval_dataset_ref="data/eval/golden/moderation",
        version="1.0",
        threshold=_DEFAULT_THRESHOLD,
    ),
    GuardrailFamilyId.F02_SECRET_KEYS: GuardrailFamilyRecord(
        id=GuardrailFamilyId.F02_SECRET_KEYS,
        name="Secret Keys",
        stage=GuardrailStage.INGRESS,
        bank=GuardrailBank.CLIENT_UNIVERSAL,
        evaluator_kind=EvaluatorKind.REGEX,
        risk_tier_activation=_activation(True, True, True),
        hard_constraint=True,
        remediable_when_false=False,
        owner="L5 governance",
        eval_dataset_ref="data/eval/golden/secrets",
        version="1.0",
        threshold=_DEFAULT_THRESHOLD,
    ),
    GuardrailFamilyId.F03_CONTAINS_PII: GuardrailFamilyRecord(
        id=GuardrailFamilyId.F03_CONTAINS_PII,
        name="Contains PII",
        stage=GuardrailStage.INGRESS,
        bank=GuardrailBank.AGENT_DOMAIN,
        evaluator_kind=EvaluatorKind.CLASSIFIER,
        risk_tier_activation=_activation(False, True, True),
        hard_constraint=False,
        remediable_when_false=True,
        owner="L5 governance",
        eval_dataset_ref="data/eval/golden/pii",
        version="1.0",
        threshold=_DEFAULT_THRESHOLD,
    ),
    GuardrailFamilyId.F04_JAILBREAK: GuardrailFamilyRecord(
        id=GuardrailFamilyId.F04_JAILBREAK,
        name="Jailbreak",
        stage=GuardrailStage.INGRESS,
        bank=GuardrailBank.CLIENT_UNIVERSAL,
        evaluator_kind=EvaluatorKind.CLASSIFIER,
        risk_tier_activation=_activation(True, True, True),
        hard_constraint=True,
        remediable_when_false=False,
        owner="L5 governance",
        eval_dataset_ref="data/eval/adversarial/jailbreak",
        version="1.0",
        threshold=_DEFAULT_THRESHOLD,
    ),
    GuardrailFamilyId.F05_PROMPT_INJECTION: GuardrailFamilyRecord(
        id=GuardrailFamilyId.F05_PROMPT_INJECTION,
        name="Prompt Injection Detection",
        stage=GuardrailStage.INGRESS,
        bank=GuardrailBank.CLIENT_UNIVERSAL,
        evaluator_kind=EvaluatorKind.CLASSIFIER,
        risk_tier_activation=_activation(True, True, True),
        hard_constraint=True,
        remediable_when_false=False,
        owner="L5 governance",
        eval_dataset_ref="data/eval/adversarial/prompt_injection",
        version="1.0",
        threshold=_DEFAULT_THRESHOLD,
    ),
    GuardrailFamilyId.F06_NSFW: GuardrailFamilyRecord(
        id=GuardrailFamilyId.F06_NSFW,
        name="NSFW Text",
        stage=GuardrailStage.INGRESS,
        bank=GuardrailBank.CLIENT_UNIVERSAL,
        evaluator_kind=EvaluatorKind.CLASSIFIER,
        risk_tier_activation=_activation(False, True, True),
        hard_constraint=False,
        remediable_when_false=True,
        owner="L5 governance",
        eval_dataset_ref="data/eval/golden/nsfw",
        version="1.0",
        threshold=_DEFAULT_THRESHOLD,
    ),
    GuardrailFamilyId.F07_URL_FILTER: GuardrailFamilyRecord(
        id=GuardrailFamilyId.F07_URL_FILTER,
        name="URL Filter",
        stage=GuardrailStage.EGRESS,
        bank=GuardrailBank.EGRESS_INSPECTION,
        evaluator_kind=EvaluatorKind.REGEX,
        risk_tier_activation=_activation(False, True, True),
        hard_constraint=False,
        remediable_when_false=True,
        owner="L5 governance",
        eval_dataset_ref="data/eval/golden/urls",
        version="1.0",
        threshold=_DEFAULT_THRESHOLD,
    ),
    GuardrailFamilyId.F08_HALLUCINATION: GuardrailFamilyRecord(
        id=GuardrailFamilyId.F08_HALLUCINATION,
        name="Hallucination Detection",
        stage=GuardrailStage.EGRESS,
        bank=GuardrailBank.EGRESS_INSPECTION,
        evaluator_kind=EvaluatorKind.LLM_JUDGE,
        risk_tier_activation=_activation(False, False, True),
        hard_constraint=False,
        remediable_when_false=True,
        owner="L5 governance",
        eval_dataset_ref="data/eval/golden/groundedness",
        version="1.0",
        threshold=_DEFAULT_THRESHOLD,
    ),
    GuardrailFamilyId.F09_OFF_TOPIC: GuardrailFamilyRecord(
        id=GuardrailFamilyId.F09_OFF_TOPIC,
        name="Off-Topic Prompts",
        stage=GuardrailStage.INGRESS,
        bank=GuardrailBank.AGENT_DOMAIN,
        evaluator_kind=EvaluatorKind.CLASSIFIER,
        risk_tier_activation=_activation(False, True, True),
        hard_constraint=False,
        remediable_when_false=True,
        owner="agent owner",
        eval_dataset_ref="data/eval/golden/off_topic",
        version="1.0",
        threshold=_DEFAULT_THRESHOLD,
    ),
    GuardrailFamilyId.F10_COMPETITORS: GuardrailFamilyRecord(
        id=GuardrailFamilyId.F10_COMPETITORS,
        name="Competitors",
        stage=GuardrailStage.EGRESS,
        bank=GuardrailBank.EGRESS_INSPECTION,
        evaluator_kind=EvaluatorKind.REGEX,
        risk_tier_activation=_activation(False, False, True),
        hard_constraint=False,
        remediable_when_false=True,
        owner="agent owner",
        eval_dataset_ref="data/eval/golden/competitors",
        version="1.0",
        threshold=_DEFAULT_THRESHOLD,
    ),
    GuardrailFamilyId.F11_KEYWORD_FILTER: GuardrailFamilyRecord(
        id=GuardrailFamilyId.F11_KEYWORD_FILTER,
        name="Keyword Filter",
        stage=GuardrailStage.INGRESS,
        bank=GuardrailBank.CLIENT_UNIVERSAL,
        evaluator_kind=EvaluatorKind.REGEX,
        risk_tier_activation=_activation(False, True, True),
        hard_constraint=False,
        remediable_when_false=True,
        owner="L5 governance",
        eval_dataset_ref="data/eval/golden/keyword",
        version="1.0",
        threshold=_DEFAULT_THRESHOLD,
    ),
    GuardrailFamilyId.F12_CUSTOM_PROMPT_CHECK: GuardrailFamilyRecord(
        id=GuardrailFamilyId.F12_CUSTOM_PROMPT_CHECK,
        name="Custom Prompt Check",
        stage=GuardrailStage.INGRESS,
        bank=GuardrailBank.AGENT_DOMAIN,
        evaluator_kind=EvaluatorKind.LLM_JUDGE,
        risk_tier_activation=_activation(False, True, True),
        hard_constraint=False,
        remediable_when_false=True,
        owner="agent owner",
        eval_dataset_ref="data/eval/golden/custom",
        version="1.0",
        threshold=_DEFAULT_THRESHOLD,
    ),
    GuardrailFamilyId.F13_SENSITIVE_DATA: GuardrailFamilyRecord(
        id=GuardrailFamilyId.F13_SENSITIVE_DATA,
        name="Sensitive-Data Classifier",
        stage=GuardrailStage.EGRESS,
        bank=GuardrailBank.EGRESS_INSPECTION,
        evaluator_kind=EvaluatorKind.CLASSIFIER,
        risk_tier_activation=_activation(False, False, True),
        hard_constraint=False,
        remediable_when_false=True,
        owner="L5 governance",
        eval_dataset_ref="data/eval/golden/sensitive",
        version="1.0",
        threshold=_DEFAULT_THRESHOLD,
    ),
    GuardrailFamilyId.F14_GUARD_MODEL_REVIEW: GuardrailFamilyRecord(
        id=GuardrailFamilyId.F14_GUARD_MODEL_REVIEW,
        name="Guard-Model Review",
        stage=GuardrailStage.EGRESS,
        bank=GuardrailBank.EGRESS_INSPECTION,
        evaluator_kind=EvaluatorKind.GUARD_MODEL,
        risk_tier_activation=_activation(False, False, True),
        hard_constraint=False,
        remediable_when_false=True,
        owner="L5 governance",
        eval_dataset_ref="data/eval/adversarial/guard_model",
        version="1.0",
        threshold=_DEFAULT_THRESHOLD,
    ),
    GuardrailFamilyId.F15_HANDOFF_VALIDITY: GuardrailFamilyRecord(
        id=GuardrailFamilyId.F15_HANDOFF_VALIDITY,
        name="Handoff Validity",
        stage=GuardrailStage.HANDOFF,
        bank=GuardrailBank.CLIENT_UNIVERSAL,
        evaluator_kind=EvaluatorKind.DIGEST_MATCH,
        risk_tier_activation=_activation(True, True, True),
        hard_constraint=False,
        remediable_when_false=True,
        owner="L5 governance",
        eval_dataset_ref="data/eval/golden/handoff",
        version="1.0",
        threshold=_DEFAULT_THRESHOLD,
    ),
    GuardrailFamilyId.F16_CONTEXT_BLEED: GuardrailFamilyRecord(
        id=GuardrailFamilyId.F16_CONTEXT_BLEED,
        name="Context Bleed Detector",
        stage=GuardrailStage.CONTEXT,
        bank=GuardrailBank.CLIENT_UNIVERSAL,
        evaluator_kind=EvaluatorKind.CLASSIFIER,
        risk_tier_activation=_activation(False, True, True),
        hard_constraint=False,
        remediable_when_false=True,
        owner="L5 governance",
        eval_dataset_ref="data/eval/adversarial/context_bleed",
        version="1.0",
        threshold=_DEFAULT_THRESHOLD,
    ),
    GuardrailFamilyId.F17_SUPPLY_CHAIN_DIGEST: GuardrailFamilyRecord(
        id=GuardrailFamilyId.F17_SUPPLY_CHAIN_DIGEST,
        name="Supply-Chain Digest",
        stage=GuardrailStage.SUPPLY_CHAIN,
        bank=GuardrailBank.CLIENT_UNIVERSAL,
        evaluator_kind=EvaluatorKind.DIGEST_MATCH,
        risk_tier_activation=_activation(True, True, True),
        hard_constraint=True,
        remediable_when_false=False,
        owner="L5 governance",
        eval_dataset_ref="data/eval/golden/supply_chain",
        version="1.0",
        threshold=_DEFAULT_THRESHOLD,
    ),
    GuardrailFamilyId.F18_THREAT_INTEL_SIGNATURE: GuardrailFamilyRecord(
        id=GuardrailFamilyId.F18_THREAT_INTEL_SIGNATURE,
        name="Threat-Intel Signature",
        stage=GuardrailStage.INGRESS,
        bank=GuardrailBank.CLIENT_UNIVERSAL,
        evaluator_kind=EvaluatorKind.DIGEST_MATCH,
        risk_tier_activation=_activation(True, True, True),
        hard_constraint=True,
        remediable_when_false=False,
        owner="L5 governance",
        eval_dataset_ref="data/eval/adversarial/threat_intel",
        version="1.0",
        threshold=_DEFAULT_THRESHOLD,
    ),
}


def get_family(family_id: GuardrailFamilyId) -> GuardrailFamilyRecord:
    """Return the curated record for a family ID."""
    if family_id not in _FAMILIES:
        raise ValueError(f"get_family: unknown family {family_id!r}")
    return _FAMILIES[family_id]


def all_families() -> tuple[GuardrailFamilyRecord, ...]:
    """Return all 18 family records, ordered by ID."""
    return tuple(_FAMILIES[fid] for fid in sorted(_FAMILIES, key=lambda f: f.value))


def hard_constraint_family_ids() -> tuple[GuardrailFamilyId, ...]:
    """Return the IDs of families with `hard_constraint=True`."""
    return tuple(
        sorted(
            (fid for fid, rec in _FAMILIES.items() if rec.hard_constraint),
            key=lambda f: f.value,
        )
    )


__all__ = [
    "all_families",
    "get_family",
    "hard_constraint_family_ids",
]
