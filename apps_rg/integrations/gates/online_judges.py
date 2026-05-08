"""Online Judge Contract — Runtime binding for narrative judges.

Implements the Online Judge Runtime Contract per W2:
- JudgeVerdict normalization to GateVerdict
- Required fields: judge_id, judge_version, rubric_version, threshold_profile_id
- Judges evaluate but do not authorize writes

Spec reference: .windsurf/plans/apps-rg-runtime-gate-catalog-c4d7e1.md (W2)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional

from agentic_core.L5_safety.runtime_gates.types import Result
from agentic_core.runtime_gates.definitions import JudgeVerdict as CoreJudgeVerdict, GatePlacement

from apps_eval.engines.narrative_judge_scorer import JudgeVerdict as NarrativeJudgeVerdict


# ----------------------------------------------------------------------------
# Judge versioning constants — W2 Online Judge Runtime Contract
# ----------------------------------------------------------------------------

NARRATIVE_JUDGE_ID: str = "narrative_judge_scorer"
NARRATIVE_JUDGE_VERSION: str = "1.0.0"
DEFAULT_RUBRIC_VERSION: str = "2.0.0"
DEFAULT_THRESHOLD_PROFILE_ID: str = "apps_rg_default"


@dataclass
class JudgeRuntimeContext:
    """Runtime context required for judge verdict normalization.

    Fields:
        section_id: The narrative section being evaluated
        rubric_version: Version of the rubric applied
        threshold_profile_id: Active threshold profile
        gate_id: Runtime gate this judge feeds into
        placement: GatePlacement for this evaluation
    """

    section_id: str
    rubric_version: str = DEFAULT_RUBRIC_VERSION
    threshold_profile_id: str = DEFAULT_THRESHOLD_PROFILE_ID
    gate_id: str = ""
    placement: GatePlacement = GatePlacement.PER_CAND


def normalize_narrative_judge_verdict(
    verdict: NarrativeJudgeVerdict,
    context: JudgeRuntimeContext,
) -> CoreJudgeVerdict:
    """Normalize apps_eval NarrativeJudgeVerdict to core JudgeVerdict.

    This is the bridge between online judges and the RuntimeGateEngine.
    Per W2 contract, judges produce verdicts that are normalized into
    gate verdicts; judges do not authorize writes.

    Args:
        verdict: The narrative judge verdict (from apps_eval)
        context: Runtime context for normalization

    Returns:
        CoreJudgeVerdict with all required W2 contract fields
    """
    # Map accepted status to Result
    if verdict.accepted:
        result = Result.PASS
    elif any(not g.passed for g in verdict.hard_gates):
        result = Result.FAIL
    else:
        # Soft score below threshold
        result = Result.WARN

    # Build reason codes from failed gates
    reason_codes: list[str] = []
    for gate in verdict.hard_gates:
        if not gate.passed:
            reason_codes.append(f"hard_gate_fail:{gate.gate_id}")
            reason_codes.append(gate.gate_id)

    # Evidence refs from section and gates
    evidence_refs: list[str] = [
        f"section:{context.section_id}",
        f"judge:{NARRATIVE_JUDGE_ID}",
    ]
    evidence_refs.extend(reason_codes)

    # Generate deterministic digest for reproducibility
    digest_input = (
        f"{NARRATIVE_JUDGE_ID}:{NARRATIVE_JUDGE_VERSION}:"
        f"{context.section_id}:{context.rubric_version}:"
        f"{verdict.accepted}:{verdict.composite:.4f}"
    )
    import hashlib
    deterministic_digest = hashlib.sha256(digest_input.encode()).hexdigest()[:16]

    return CoreJudgeVerdict(
        judge_id=NARRATIVE_JUDGE_ID,
        judge_version=NARRATIVE_JUDGE_VERSION,
        rubric_version=context.rubric_version,
        threshold_profile_id=context.threshold_profile_id,
        gate_id=context.gate_id or f"{context.section_id}_judge",
        placement=context.placement,
        score=verdict.composite,
        accepted=verdict.accepted,
        result=result,
        reason_codes=tuple(reason_codes),
        evidence_refs=tuple(evidence_refs),
        deterministic_digest=deterministic_digest,
    )


def judge_verdict_to_gate_bundle_entry(
    verdict: CoreJudgeVerdict,
) -> Dict[str, Any]:
    """Convert normalized judge verdict to a gate bundle entry format.

    This is used by the RuntimeGateEngine to aggregate judge verdicts
    into the overall GateBundle.
    """
    return {
        "gate_id": verdict.gate_id,
        "judge_id": verdict.judge_id,
        "judge_version": verdict.judge_version,
        "score": verdict.score,
        "accepted": verdict.accepted,
        "result": verdict.result.value,
        "reason_codes": list(verdict.reason_codes),
        "evidence_refs": list(verdict.evidence_refs),
        "deterministic_digest": verdict.deterministic_digest,
    }


class OnlineJudgeContractValidator:
    """Validates judge verdicts against the Online Judge Runtime Contract.

    Runtime rules enforced:
    1. Judges MUST emit verdicts with all required identifiers
    2. Judges MUST NOT emit write authorization — only evaluation
    3. Malformed verdicts MUST normalize to UNKNOWN GateVerdict
    """

    REQUIRED_FIELDS = {
        "judge_id",
        "judge_version",
        "rubric_version",
        "threshold_profile_id",
        "gate_id",
        "placement",
    }

    @classmethod
    def validate(cls, verdict: CoreJudgeVerdict) -> tuple[bool, list[str]]:
        """Validate a judge verdict. Returns (is_valid, errors)."""
        errors: list[str] = []

        # Check required fields
        for field in cls.REQUIRED_FIELDS:
            value = getattr(verdict, field, None)
            if not value:
                errors.append(f"missing_required_field:{field}")

        # Check score range
        if not 0.0 <= verdict.score <= 1.0:
            errors.append(f"score_out_of_range:{verdict.score}")

        # Check version format (semver-ish)
        for version_field in ("judge_version", "rubric_version"):
            version = getattr(verdict, version_field, "")
            if version and not cls._looks_like_version(version):
                errors.append(f"invalid_version_format:{version_field}={version}")

        return len(errors) == 0, errors

    @staticmethod
    def _looks_like_version(v: str) -> bool:
        """Basic semver check (x.y.z or x.y)."""
        parts = v.split(".")
        return len(parts) >= 2 and all(p.isdigit() for p in parts[:2])

    @classmethod
    def normalize_or_unknown(
        cls,
        raw_verdict: Optional[CoreJudgeVerdict],
        context: JudgeRuntimeContext,
    ) -> CoreJudgeVerdict:
        """Validate verdict; return UNKNOWN if invalid.

        Per W2 contract: malformed judge verdicts block write.
        """
        if raw_verdict is None:
            return cls._unknown_verdict(context, "null_verdict")

        is_valid, errors = cls.validate(raw_verdict)
        if not is_valid:
            return cls._unknown_verdict(context, "|".join(errors))

        return raw_verdict

    @classmethod
    def _unknown_verdict(
        cls,
        context: JudgeRuntimeContext,
        reason: str,
    ) -> CoreJudgeVerdict:
        """Create an UNKNOWN verdict for malformed/missing input."""
        return CoreJudgeVerdict(
            judge_id=NARRATIVE_JUDGE_ID,
            judge_version=NARRATIVE_JUDGE_VERSION,
            rubric_version=context.rubric_version,
            threshold_profile_id=context.threshold_profile_id,
            gate_id=context.gate_id or f"{context.section_id}_judge",
            placement=context.placement,
            score=0.0,
            accepted=False,
            result=Result.UNKNOWN,
            reason_codes=("judge_verdict_malformed", reason),
            evidence_refs=(f"section:{context.section_id}", "result:unknown"),
            deterministic_digest="",
        )


# ----------------------------------------------------------------------------
# Convenience exports
# ----------------------------------------------------------------------------

__all__ = [
    "NARRATIVE_JUDGE_ID",
    "NARRATIVE_JUDGE_VERSION",
    "DEFAULT_RUBRIC_VERSION",
    "DEFAULT_THRESHOLD_PROFILE_ID",
    "JudgeRuntimeContext",
    "normalize_narrative_judge_verdict",
    "judge_verdict_to_gate_bundle_entry",
    "OnlineJudgeContractValidator",
]
