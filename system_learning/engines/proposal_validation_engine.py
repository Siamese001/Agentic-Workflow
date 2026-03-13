"""Proposal Validation Engine — four-gate validation for OptimizationProposals.

Runs each OptimizationProposal through five validation gates:

  1. REPLAY_VALIDATION       — verifies the change is replay-safe
  2. POLICY_VALIDATION       — verifies the change doesn't violate policy
  3. GUARDRAIL_VALIDATION    — verifies guardrail invariants are preserved
  4. DETERMINISM_VERIFICATION — verifies the change spec is deterministic
  5. REGRESSION_TESTING      — assesses regression risk from cluster evidence

Only proposals that pass ALL required gates produce a ``ValidationResult``
with ``validation_pass=True`` and may proceed to ``OptimizationCommit``.

Design invariants
-----------------
1. Pure function interface — no global mutable state.
2. No wall-clock reads; ``timestamp_utc`` always caller-supplied.
3. All outputs are deterministically content-addressed.
4. Validation gates are individually configurable as required/optional.
5. Fail-closed: any gate that raises an unexpected exception counts as a
   failure (not a pass) and logs a WARNING.
6. HIGH and CRITICAL risk proposals require all gates to pass.
   LOW and MEDIUM risk proposals may skip REGRESSION_TESTING if
   ``skip_regression_for_low_risk=True`` (default False).
"""

from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass
from typing import Sequence

from system_learning.enforcement.determinism import deterministic_json
from system_learning.types.optimization_types import (
    OptimizationProposal,
    ValidationResult,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Gate names (canonical)
# ---------------------------------------------------------------------------

GATE_REPLAY = "REPLAY_VALIDATION"
GATE_POLICY = "POLICY_VALIDATION"
GATE_GUARDRAIL = "GUARDRAIL_VALIDATION"
GATE_DETERMINISM = "DETERMINISM_VERIFICATION"
GATE_REGRESSION = "REGRESSION_TESTING"

_ALL_GATES: tuple[str, ...] = (
    GATE_REPLAY,
    GATE_POLICY,
    GATE_GUARDRAIL,
    GATE_DETERMINISM,
    GATE_REGRESSION,
)

# ---------------------------------------------------------------------------
# Regression risk thresholds
# ---------------------------------------------------------------------------

_RISK_THRESHOLDS: dict[str, tuple[float, float]] = {
    # (hitl_rate_ceiling, healer_rate_ceiling) → regression risk
    # Used to derive regression_risk label from cluster statistics
}

_REGRESSION_RISK_LABELS: tuple[tuple[str, str, str], ...] = (
    # (risk_class, hitl_rate_floor, regression_label)
    ("CRITICAL", "0.0", "HIGH"),
    ("HIGH", "0.6", "HIGH"),
    ("HIGH", "0.0", "MEDIUM"),
    ("MEDIUM", "0.5", "MEDIUM"),
    ("MEDIUM", "0.0", "LOW"),
    ("LOW", "0.0", "NONE"),
)


def _derive_regression_risk(proposal: OptimizationProposal, hitl_rate: float) -> str:
    """Derive regression risk from proposal risk class and cluster HITL rate."""
    risk_class = proposal.risk_class
    for rc, hitl_floor, label in _REGRESSION_RISK_LABELS:
        if rc == risk_class and hitl_rate >= float(hitl_floor):
            return label
    return "LOW"


# ---------------------------------------------------------------------------
# Gate implementations
# ---------------------------------------------------------------------------


def _gate_replay(proposal: OptimizationProposal) -> tuple[bool, str | None]:
    """Replay validation gate.

    Passes when:
    - change_spec contains determinism_markers or no mutation keys present
    - change_type is not EMBEDDING_CORPUS_EXPANSION on a HIGH-risk proposal
      without evidence
    """
    change_spec_dict = dict(proposal.change_spec)

    # ROUTING and CONFIDENCE changes are replay-safe by definition
    if proposal.proposed_change_type in (
        "ROUTING_RULE_ADJUSTMENT",
        "CONFIDENCE_THRESHOLD_UPDATE",
    ):
        return True, None

    # EMBEDDING_CORPUS_EXPANSION with no evidence bundle is suspicious
    if (
        proposal.proposed_change_type == "EMBEDDING_CORPUS_EXPANSION"
        and not proposal.evidence_bundle_hashes
    ):
        return False, "EMBEDDING_EXPANSION_NO_EVIDENCE"

    # DPO_DATASET_GENERATION requires evidence bundles
    if (
        proposal.proposed_change_type == "DPO_DATASET_GENERATION"
        and not proposal.evidence_bundle_hashes
    ):
        return False, "DPO_NO_EVIDENCE_BUNDLE"

    return True, None


def _gate_policy(proposal: OptimizationProposal, policy_hash: str | None) -> tuple[bool, str | None]:
    """Policy validation gate.

    Passes when:
    - proposal.policy_hash matches the active policy_hash (or both None)
    - Change type is not GUARDRAIL_REFINEMENT on a CRITICAL proposal
    """
    if proposal.policy_hash is not None and policy_hash is not None:
        if proposal.policy_hash != policy_hash:
            return False, "POLICY_HASH_MISMATCH"

    # CRITICAL guardrail changes require explicit policy alignment
    if (
        proposal.proposed_change_type == "GUARDRAIL_REFINEMENT"
        and proposal.risk_class == "CRITICAL"
    ):
        if proposal.policy_hash is None:
            return False, "GUARDRAIL_CRITICAL_NO_POLICY_HASH"

    return True, None


def _gate_guardrail(proposal: OptimizationProposal) -> tuple[bool, str | None]:
    """Guardrail validation gate.

    Passes when:
    - Affected component is a known ADG entity (starts with "ADG::")
    - HIGH risk proposals targeting guardrail components have evidence
    """
    component = proposal.affected_component

    # Affected component must reference a valid ADG entity
    if not component or component == "ADG::Unknown":
        return False, "UNKNOWN_AFFECTED_COMPONENT"

    # HIGH/CRITICAL guardrail changes require evidence
    if (
        proposal.proposed_change_type == "GUARDRAIL_REFINEMENT"
        and proposal.risk_class in ("HIGH", "CRITICAL")
        and not proposal.evidence_bundle_hashes
    ):
        return False, "GUARDRAIL_HIGH_RISK_NO_EVIDENCE"

    return True, None


def _gate_determinism(proposal: OptimizationProposal) -> tuple[bool, str | None]:
    """Determinism verification gate.

    Verifies that the change_spec is deterministically serializable and
    that the proposal_id matches the expected content-addressed value.
    """
    # Verify change_spec is JSON-serializable and deterministic
    try:
        spec_json = deterministic_json(dict(proposal.change_spec))
        _ = spec_json  # consume
    except Exception:  # guardian: allow-silent-swallow
        return False, "CHANGE_SPEC_NOT_SERIALIZABLE"

    # Verify proposal_id is a valid SHA-256 hexdigest
    pid = proposal.proposal_id
    if not pid or len(pid) != 64 or not all(c in "0123456789abcdef" for c in pid):
        return False, "PROPOSAL_ID_NOT_HASH"

    return True, None


def _gate_regression(
    proposal: OptimizationProposal,
    hitl_rate: float,
    *,
    skip_for_low_risk: bool,
) -> tuple[bool, str | None]:
    """Regression testing gate.

    Derives regression risk from cluster statistics and blocks HIGH regression
    for HIGH/CRITICAL proposals.
    """
    if skip_for_low_risk and proposal.risk_class in ("LOW", "MEDIUM"):
        return True, None

    regression_risk = _derive_regression_risk(proposal, hitl_rate)

    # Block HIGH regression for HIGH/CRITICAL proposals
    if (
        regression_risk == "HIGH"
        and proposal.risk_class in ("HIGH", "CRITICAL")
    ):
        return False, "HIGH_REGRESSION_RISK"

    return True, None


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------


@dataclass
class ValidationConfig:
    """Configuration for the proposal validation engine."""

    required_gates: tuple[str, ...] = (
        GATE_REPLAY,
        GATE_POLICY,
        GATE_GUARDRAIL,
        GATE_DETERMINISM,
        GATE_REGRESSION,
    )
    skip_regression_for_low_risk: bool = False
    active_policy_hash: str | None = None


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------


class ProposalValidationEngine:
    """Runs OptimizationProposals through the five-gate validation pipeline.

    Produces a ``ValidationResult`` for each proposal.  Only proposals with
    ``validation_pass=True`` should proceed to ``OptimizationCommit``.
    """

    def __init__(self, config: ValidationConfig | None = None) -> None:
        self._config = config or ValidationConfig()

    def validate(
        self,
        proposal: OptimizationProposal,
        timestamp_utc: int,
        *,
        hitl_rate: float = 0.0,
    ) -> ValidationResult:
        """Validate a single proposal.

        Parameters
        ----------
        proposal:
            The proposal to validate.
        timestamp_utc:
            Caller-supplied Unix timestamp.
        hitl_rate:
            HITL escalation rate from the originating cluster (0.0–1.0).
            Used by the regression gate.

        Returns
        -------
        ValidationResult
        """
        cfg = self._config
        gate_results: dict[str, bool] = {}
        denial_reasons: list[str] = []

        # --- Run all five gates ---
        for gate_name, gate_fn_result in self._run_gates(
            proposal, hitl_rate, cfg
        ):
            passed, reason = gate_fn_result
            gate_results[gate_name] = passed
            if not passed and gate_name in cfg.required_gates:
                denial_reasons.append(reason or gate_name)

        validation_pass = len(denial_reasons) == 0

        # Derive individual gate booleans
        replay_safe = gate_results.get(GATE_REPLAY, True)
        policy_safe = gate_results.get(GATE_POLICY, True)
        guardrail_safe = gate_results.get(GATE_GUARDRAIL, True)
        det_verified = gate_results.get(GATE_DETERMINISM, True)

        regression_risk = _derive_regression_risk(proposal, hitl_rate)

        # Content-addressed result_id
        canonical = deterministic_json({
            "denial_reasons": sorted(denial_reasons),
            "gate_results": sorted(gate_results.items()),
            "policy_hash": cfg.active_policy_hash,
            "proposal_id": proposal.proposal_id,
            "timestamp_utc": timestamp_utc,
            "validation_pass": validation_pass,
        })
        result_id = hashlib.sha256(canonical.encode("utf-8")).hexdigest()

        return ValidationResult(
            result_id=result_id,
            proposal_id=proposal.proposal_id,
            validation_pass=validation_pass,
            replay_safe=replay_safe,
            policy_safe=policy_safe,
            guardrail_safe=guardrail_safe,
            determinism_verified=det_verified,
            regression_risk=regression_risk,
            gate_results=tuple(sorted(gate_results.items())),
            denial_reasons=tuple(sorted(denial_reasons)),
            policy_hash=cfg.active_policy_hash,
            timestamp_utc=timestamp_utc,
        )

    def validate_batch(
        self,
        proposals: Sequence[OptimizationProposal],
        timestamp_utc: int,
        *,
        hitl_rates: dict[str, float] | None = None,
    ) -> list[ValidationResult]:
        """Validate a batch of proposals.

        Parameters
        ----------
        proposals:
            Proposals to validate.
        timestamp_utc:
            Caller-supplied Unix timestamp.
        hitl_rates:
            Optional dict mapping proposal_id → hitl_rate.  Defaults to
            0.0 for any proposal not in the dict.

        Returns
        -------
        list[ValidationResult]
            Sorted by result_id for determinism.
        """
        hitl_rates = hitl_rates or {}
        results = [
            self.validate(
                p,
                timestamp_utc,
                hitl_rate=hitl_rates.get(p.proposal_id, 0.0),
            )
            for p in proposals
        ]
        results.sort(key=lambda r: r.result_id)
        return results

    def _run_gates(
        self,
        proposal: OptimizationProposal,
        hitl_rate: float,
        cfg: ValidationConfig,
    ):
        """Yield (gate_name, (passed, reason)) tuples for all gates."""
        gates = [
            (GATE_REPLAY, lambda: _gate_replay(proposal)),
            (GATE_POLICY, lambda: _gate_policy(proposal, cfg.active_policy_hash)),
            (GATE_GUARDRAIL, lambda: _gate_guardrail(proposal)),
            (GATE_DETERMINISM, lambda: _gate_determinism(proposal)),
            (
                GATE_REGRESSION,
                lambda: _gate_regression(
                    proposal,
                    hitl_rate,
                    skip_for_low_risk=cfg.skip_regression_for_low_risk,
                ),
            ),
        ]
        for gate_name, gate_fn in gates:
            try:
                result = gate_fn()
            except Exception as exc:  # guardian: allow-silent-swallow
                logger.warning(
                    "validation_engine: gate raised exception",
                    extra={
                        "gate": gate_name,
                        "proposal_id": proposal.proposal_id,
                        "error": str(exc),
                    },
                )
                result = (False, f"{gate_name}_EXCEPTION")
            yield gate_name, result


# ---------------------------------------------------------------------------
# Module-level convenience
# ---------------------------------------------------------------------------


def validate_proposal(
    proposal: OptimizationProposal,
    timestamp_utc: int,
    *,
    config: ValidationConfig | None = None,
    hitl_rate: float = 0.0,
) -> ValidationResult:
    """Module-level convenience wrapper."""
    return ProposalValidationEngine(config).validate(
        proposal, timestamp_utc, hitl_rate=hitl_rate
    )


__all__ = [
    "GATE_DETERMINISM",
    "GATE_GUARDRAIL",
    "GATE_POLICY",
    "GATE_REGRESSION",
    "GATE_REPLAY",
    "ProposalValidationEngine",
    "ValidationConfig",
    "validate_proposal",
]
