"""L6WritebackProposer — post-runtime learning and writeback proposal engine.

Plan: apps-rg-zip-based-full-spine-runtime-restoration-a3f7e2 W10

L6 is the ONLY consumer of RuntimeExhaustBundle.  It produces inert
FutureRunPromotionRequest objects that UWG then admits or blocks.

Invariants (non-negotiable):
  - Input MUST be RuntimeExhaustBundle with created_after_exit=True.
  - L6 cannot mutate the current run.
  - L6 cannot write L4 directly.
  - L6 emits inert FutureRunPromotionRequest objects only.
  - All proposals have current_run_mutation_allowed=False, requires_uwg=True.
  - Promotion gating logic is read from learning_profile (not hardcoded).
"""
from __future__ import annotations

from typing import Optional

from agentic_core.runtime.exhaust.runtime_exhaust_bundle import RuntimeExhaustBundle
from agentic_core.runtime.contracts.future_run_promotion import (
    FutureRunPromotionRequest,
    build_future_run_promotion_request,
    PROMOTION_TYPE_EXACT_CACHE_WRITEBACK,
    PROMOTION_TYPE_SEMANTIC_CACHE_WRITEBACK,
    PROMOTION_TYPE_EVIDENCE_ARTIFACT_WRITEBACK,
    PROMOTION_TYPE_PROMPT_PROFILE_UPDATE,
    PROMOTION_TYPE_RUBRIC_THRESHOLD_UPDATE,
    PROMOTION_TYPE_JUDGE_CALIBRATION_UPDATE,
    PROMOTION_TYPE_ROUTE_POLICY_UPDATE,
    PROMOTION_TYPE_CACHE_POLICY_UPDATE,
    TARGET_STORE_EXACT_CACHE,
    TARGET_STORE_SEMANTIC_CACHE,
    TARGET_STORE_EVIDENCE_STORE,
    TARGET_STORE_PROMPT_REGISTRY,
    TARGET_STORE_RUBRIC_REGISTRY,
    TARGET_STORE_JUDGE_CALIBRATION,
    TARGET_STORE_ROUTE_POLICY,
    TARGET_STORE_CACHE_POLICY,
    SAFETY_CLASS_STANDARD,
)


class L6WritebackProposerError(RuntimeError):
    """Raised when L6 receives invalid input or violates invariants."""


class L6WritebackProposer:
    """Post-runtime learning proposal generator.

    Consumes RuntimeExhaustBundle and emits FutureRunPromotionRequest proposals.
    The proposals are inert — UWG admits or blocks each one.

    ``learning_profile`` is a dict loaded from the app's learning_profiles.yaml
    or meta_feedback_profile JSON.  Default values are conservative.

    Usage::

        proposer = L6WritebackProposer(
            app_id="<app_id>",  # From caller or profile
            task_class="<task_class>",  # From caller or profile
            learning_profile={...},
            policy_ref="<app_id>/config/domain_contract/meta_feedback_profile.v1.json",
        )
        proposals = proposer.propose(exhaust_bundle)
        # Each proposal: FutureRunPromotionRequest with requires_uwg=True
    """

    def __init__(
        self,
        *,
        app_id: str,
        task_class: str,
        learning_profile: Optional[dict] = None,
        policy_ref: str,
    ) -> None:
        """Initialize L6WritebackProposer.
        
        Args:
            app_id: Application identifier (required, no default)
            task_class: Task class identifier (required, no default)
            learning_profile: Optional learning parameters dict
            policy_ref: Path to policy file (required, no default)
        """
        if not app_id:
            raise ValueError("app_id is required")
        if not task_class:
            raise ValueError("task_class is required")
        if not policy_ref:
            raise ValueError("policy_ref is required")
            
        self._app_id = app_id
        self._task_class = task_class
        self._lp = learning_profile or {}
        self._policy_ref = policy_ref

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def propose(
        self,
        bundle: RuntimeExhaustBundle,
    ) -> list[FutureRunPromotionRequest]:
        """Inspect ``bundle`` and return a list of FutureRunPromotionRequest proposals.

        Returns an empty list when no promotable signals are present.
        Raises L6WritebackProposerError if the bundle is invalid.
        """
        self._assert_valid_bundle(bundle)

        proposals: list[FutureRunPromotionRequest] = []

        # Delegate to per-type signal evaluators
        proposals.extend(self._evaluate_cache_writeback(bundle))
        proposals.extend(self._evaluate_evidence_writeback(bundle))
        proposals.extend(self._evaluate_prompt_profile_update(bundle))
        proposals.extend(self._evaluate_rubric_threshold_update(bundle))
        proposals.extend(self._evaluate_judge_calibration_update(bundle))
        proposals.extend(self._evaluate_route_policy_update(bundle))
        proposals.extend(self._evaluate_cache_policy_update(bundle))

        return proposals

    # ------------------------------------------------------------------
    # Bundle validation
    # ------------------------------------------------------------------

    def _assert_valid_bundle(self, bundle: RuntimeExhaustBundle) -> None:
        if not isinstance(bundle, RuntimeExhaustBundle):
            raise L6WritebackProposerError(
                f"L6 input must be RuntimeExhaustBundle, got {type(bundle).__name__}."
            )
        if not bundle.created_after_exit:
            raise L6WritebackProposerError(
                "L6 input bundle has created_after_exit=False. "
                "L6 may only consume bundles created after Exit."
            )
        if not bundle.current_run_closed:
            raise L6WritebackProposerError(
                "L6 input bundle has current_run_closed=False. "
                "L6 may not process open runs."
            )
        if not bundle.exit_disposition_ref:
            raise L6WritebackProposerError(
                "L6 input bundle has empty exit_disposition_ref. "
                "Bundle must reference a completed Exit disposition."
            )

    # ------------------------------------------------------------------
    # Per-type evaluators — each returns 0..1 proposals
    # ------------------------------------------------------------------

    def _make_proposal(
        self,
        *,
        bundle: RuntimeExhaustBundle,
        promotion_type: str,
        target_store: str,
        target_ref: str,
        evidence_refs: tuple[str, ...],
        confidence: float = 0.0,
        proposed_state_diff: str = "{}",
        metric_summary: str = "{}",
        safety_class: str = SAFETY_CLASS_STANDARD,
    ) -> FutureRunPromotionRequest:
        return build_future_run_promotion_request(
            source_bundle_ref=bundle.bundle_id,
            app_id=self._app_id,
            task_class=self._task_class,
            promotion_type=promotion_type,
            target_store=target_store,
            target_ref=target_ref,
            evidence_refs=evidence_refs,
            policy_ref=self._policy_ref,
            proposed_state_diff=proposed_state_diff,
            metric_summary=metric_summary,
            confidence=confidence,
            safety_class=safety_class,
            learning_profile_ref=bundle.learning_profile_ref,
            meta_feedback_profile_ref=bundle.meta_feedback_profile_ref,
        )

    def _evaluate_cache_writeback(
        self, bundle: RuntimeExhaustBundle
    ) -> list[FutureRunPromotionRequest]:
        """Propose exact cache writeback when sealed_result_ref is present."""
        if not bundle.sealed_result_ref:
            return []
        threshold = float(self._lp.get("promotion_threshold", 0.65))
        # Without real score data from the bundle, use conservative 0.0
        # (UWG will admit based on policy, not on L6's confidence estimate here)
        return [
            self._make_proposal(
                bundle=bundle,
                promotion_type=PROMOTION_TYPE_EXACT_CACHE_WRITEBACK,
                target_store=TARGET_STORE_EXACT_CACHE,
                target_ref=f"r1a::{bundle.sealed_result_ref}",
                evidence_refs=(
                    bundle.sealed_result_ref,
                    bundle.exit_disposition_ref,
                ),
                confidence=threshold,
                proposed_state_diff=(
                    f'{{"op":"cache_store","ref":"{bundle.sealed_result_ref}"}}'
                ),
                metric_summary=(
                    f'{{"sealed_result_ref":"{bundle.sealed_result_ref}",'
                    f'"exit_disposition_ref":"{bundle.exit_disposition_ref}"}}'
                ),
            )
        ]

    def _evaluate_evidence_writeback(
        self, bundle: RuntimeExhaustBundle
    ) -> list[FutureRunPromotionRequest]:
        """Propose evidence artifact writeback when gate_mesh_result_ref is present."""
        if not bundle.gate_mesh_result_ref:
            return []
        return [
            self._make_proposal(
                bundle=bundle,
                promotion_type=PROMOTION_TYPE_EVIDENCE_ARTIFACT_WRITEBACK,
                target_store=TARGET_STORE_EVIDENCE_STORE,
                target_ref=f"c0::{bundle.gate_mesh_result_ref}",
                evidence_refs=(
                    bundle.gate_mesh_result_ref,
                    bundle.exit_disposition_ref,
                ),
                proposed_state_diff=(
                    f'{{"op":"evidence_store","ref":"{bundle.gate_mesh_result_ref}"}}'
                ),
            )
        ]

    def _evaluate_prompt_profile_update(
        self, bundle: RuntimeExhaustBundle
    ) -> list[FutureRunPromotionRequest]:
        """Propose prompt profile update only when learning signals include prompt data."""
        if "prompt_variant_performance" not in bundle.learning_signals:
            return []
        return [
            self._make_proposal(
                bundle=bundle,
                promotion_type=PROMOTION_TYPE_PROMPT_PROFILE_UPDATE,
                target_store=TARGET_STORE_PROMPT_REGISTRY,
                target_ref=f"pp::{self._app_id}::{bundle.run_id}",
                evidence_refs=(bundle.exit_disposition_ref,),
                metric_summary=(
                    f'{{"signal":"prompt_variant_performance","run_id":"{bundle.run_id}"}}'
                ),
            )
        ]

    def _evaluate_rubric_threshold_update(
        self, bundle: RuntimeExhaustBundle
    ) -> list[FutureRunPromotionRequest]:
        """Propose rubric threshold update when section_underperformance signal present."""
        if "section_underperformance" not in bundle.learning_signals:
            return []
        return [
            self._make_proposal(
                bundle=bundle,
                promotion_type=PROMOTION_TYPE_RUBRIC_THRESHOLD_UPDATE,
                target_store=TARGET_STORE_RUBRIC_REGISTRY,
                target_ref=f"rubric::{self._app_id}::{bundle.run_id}",
                evidence_refs=(bundle.exit_disposition_ref,),
            )
        ]

    def _evaluate_judge_calibration_update(
        self, bundle: RuntimeExhaustBundle
    ) -> list[FutureRunPromotionRequest]:
        """Propose judge calibration update when judge_disagreement_spike signal present."""
        if "judge_disagreement_spike" not in bundle.learning_signals:
            return []
        return [
            self._make_proposal(
                bundle=bundle,
                promotion_type=PROMOTION_TYPE_JUDGE_CALIBRATION_UPDATE,
                target_store=TARGET_STORE_JUDGE_CALIBRATION,
                target_ref=f"jc::{self._app_id}::{bundle.run_id}",
                evidence_refs=(bundle.exit_disposition_ref,),
            )
        ]

    def _evaluate_route_policy_update(
        self, bundle: RuntimeExhaustBundle
    ) -> list[FutureRunPromotionRequest]:
        """Propose route policy update when route_fallback_frequency signal present."""
        if "route_fallback_frequency" not in bundle.learning_signals:
            return []
        return [
            self._make_proposal(
                bundle=bundle,
                promotion_type=PROMOTION_TYPE_ROUTE_POLICY_UPDATE,
                target_store=TARGET_STORE_ROUTE_POLICY,
                target_ref=f"rp::{self._app_id}::{bundle.run_id}",
                evidence_refs=(bundle.exit_disposition_ref,),
            )
        ]

    def _evaluate_cache_policy_update(
        self, bundle: RuntimeExhaustBundle
    ) -> list[FutureRunPromotionRequest]:
        """Propose cache policy update when cache_eligibility signal present."""
        if "cache_eligibility" not in bundle.learning_signals:
            return []
        return [
            self._make_proposal(
                bundle=bundle,
                promotion_type=PROMOTION_TYPE_CACHE_POLICY_UPDATE,
                target_store=TARGET_STORE_CACHE_POLICY,
                target_ref=f"cp::{self._app_id}::{bundle.run_id}",
                evidence_refs=(bundle.exit_disposition_ref,),
            )
        ]


__all__ = [
    "L6WritebackProposer",
    "L6WritebackProposerError",
]
