"""QUARANTINE NOTICE — AG-RGGOV-8: QUARANTINE_ALL_RUNTIME_HOPS

This file is QUARANTINED per the declarative ingress-only governance model.
apps_rg may NOT emit lifecycle trace contracts or make provider calls.

Original: apps_rg/integrations\gates\narrative_integration.py
Quarantined: 2026-05-09
Reason: AG-RGGOV-W4-SCOPE — Runtime authority violation

Importing this module raises RuntimeError immediately.
Core L6 Observability owns all trace emission. apps_rg is ingress-only.
"""

raise RuntimeError(
    "QUARANTINE VIOLATION (AG-RGGOV-8): "
    "apps_rg.integrations\gates\narrative_integration is QUARANTINED. "
    "apps_rg may NOT contain runtime authority. "
    "Core L2/L5/L6 owns execution. apps_rg is ingress-only. "
    "See: .windsurf/plans/apps-rg-declarative-ingress-only-spinal-governance-c8b3e1.md §19"
)

# Original code archived to: archives/apps_rg/quarantine_w4_20260509/integrations\gates\narrative_integration.py.ORIGINAL

# QUARANTINED — Original content below for reference only — NOT EXECUTABLE:
# """Narrative Pipeline Gate Integration — RuntimeGateEngine binding for narrative_pass.py.
# 
# Implements the W1 P0 write-boundary fix: integrates RuntimeGateEngine into the
# narrative pipeline to ensure rejected candidates are never written to resume_data.
# 
# Spec reference: .windsurf/plans/apps-rg-runtime-gate-catalog-c4d7e1.md (W1)
# """
# 
# from __future__ import annotations
# 
# import logging
# from dataclasses import dataclass
# from typing import Any, Dict, Optional
# 
# from agentic_core.L5_safety.runtime_gates.types import Result
# from agentic_core.runtime_gates import (
#     GatePlacement,
#     GateVerdict,
#     GateBundle,
#     RuntimeGateEngine,
#     WriteAdmissionGuard,
#     WriteAdmissionReceipt,
# )
# from agentic_core.runtime_gates.builtins.candidate_acceptance_guard import (
#     CandidateAcceptanceGuard,
# )
# from apps_rg.integrations.gates.registry import register_apps_rg_gate_pack
# 
# # W2: Online Judge Contract imports
# from apps_eval.engines.narrative_judge_scorer import JudgeVerdict as NarrativeJudgeVerdict
# from apps_rg.integrations.gates.online_judges import (
#     JudgeRuntimeContext,
#     normalize_narrative_judge_verdict,
#     OnlineJudgeContractValidator,
#     NARRATIVE_JUDGE_ID,
# )
# 
# _log = logging.getLogger("apps_rg.gates.narrative_integration")
# 
# 
# # Singleton engine instance (initialized once per process)
# _engine: Optional[RuntimeGateEngine] = None
# _guard: Optional[WriteAdmissionGuard] = None
# 
# 
# def _get_engine() -> RuntimeGateEngine:
#     """Get or initialize the RuntimeGateEngine singleton."""
#     global _engine
#     if _engine is None:
#         _engine = RuntimeGateEngine()
#         register_apps_rg_gate_pack(_engine)
#         _log.info("[W1] RuntimeGateEngine initialized with apps_rg gate pack")
#     return _engine
# 
# 
# def _get_guard() -> WriteAdmissionGuard:
#     """Get or initialize the WriteAdmissionGuard singleton."""
#     global _guard
#     if _guard is None:
#         gate_defs = _get_engine().get_gate_definitions()
#         _guard = WriteAdmissionGuard(gate_defs)
#     return _guard
# 
# 
# @dataclass
# class AcceptedArtifact:
#     """A candidate artifact that has been accepted and cleared for write.
# 
#     Fields:
#         text: The accepted text content
#         gate_bundle: The GateBundle that authorized this acceptance
#         write_receipt: The WriteAdmissionReceipt with writeable=true
#     """
# 
#     text: str
#     gate_bundle: GateBundle
#     write_receipt: WriteAdmissionReceipt
# 
#     @classmethod
#     def from_candidate(
#         cls,
#         candidate: Any,
#         write_receipt: WriteAdmissionReceipt,
#     ) -> "AcceptedArtifact":
#         """Create AcceptedArtifact from a candidate and its write receipt."""
#         text = getattr(candidate, "text", None)
#         if text is None and isinstance(candidate, dict):
#             text = candidate.get("text", "")
#         return cls(
#             text=str(text),
#             gate_bundle=GateBundle(
#                 app_id="apps_rg",
#                 placement=GatePlacement.POST_ENS,
#                 verdicts=(),  # Will be populated from receipt
#             ),
#             write_receipt=write_receipt,
#         )
# 
# 
# class WriteBlockedError(Exception):
#     """Raised when WriteAdmissionGuard denies write authorization."""
# 
#     def __init__(
#         self,
#         section_id: str,
#         receipt: WriteAdmissionReceipt,
#         candidate_text: str = "",
#     ) -> None:
#         self.section_id = section_id
#         self.receipt = receipt
#         self.candidate_text = candidate_text
#         super().__init__(
#             f"Write blocked for section {section_id}: {receipt.reason} "
#             f"(codes: {receipt.reason_codes})"
#         )
# 
# 
# def evaluate_and_admit(
#     section_id: str,
#     candidate: Any,
#     context: Dict[str, Any],
#     fail_if_rejected: bool = True,
# ) -> AcceptedArtifact:
#     """Evaluate a candidate through RuntimeGateEngine and return AcceptedArtifact.
# 
#     This is the core W1 P0 fix: replaces the direct `resume_data[...] = winner.text`
#     pattern with a gated evaluation that requires WriteAdmissionReceipt.writeable=true.
# 
#     Args:
#         section_id: The narrative section (e.g., "executive_summary")
#         candidate: The ensemble winner (must have .text and .accepted attributes)
#         context: Runtime context with per_cand_results, config, etc.
#         fail_if_rejected: If True, raises WriteBlockedError on rejection
# 
#     Returns:
#         AcceptedArtifact with write_receipt.writeable=True
# 
#     Raises:
#         WriteBlockedError: If candidate rejected and fail_if_rejected=True
#     """
#     engine = _get_engine()
#     guard = _get_guard()
# 
#     # Run POST-ENS gates (including candidate_acceptance_guard)
#     gate_bundle = engine.evaluate(
#         app_id="apps_rg",
#         placement=GatePlacement.POST_ENS,
#         artifact=candidate,
#         context=context,
#     )
# 
#     # Request write admission
#     write_receipt = guard.evaluate(section_id, gate_bundle, context)
# 
#     if not write_receipt.writeable:
#         _log.error(
#             "[W1] Write blocked for %s: %s (codes: %s)",
#             section_id,
#             write_receipt.reason,
#             write_receipt.reason_codes,
#         )
#         if fail_if_rejected:
#             raise WriteBlockedError(
#                 section_id=section_id,
#                 receipt=write_receipt,
#                 candidate_text=getattr(candidate, "text", ""),
#             )
# 
#     # Create accepted artifact
#     accepted = AcceptedArtifact.from_candidate(candidate, write_receipt)
#     _log.info(
#         "[W1] Write authorized for %s: result=%s",
#         section_id,
#         gate_bundle.overall_result.value,
#     )
# 
#     return accepted
# 
# 
# def sealed_failure_packet(
#     section_id: str,
#     receipt: WriteAdmissionReceipt,
#     context: Dict[str, Any],
# ) -> Dict[str, Any]:
#     """Create a sealed failure packet for Exit when write is blocked.
# 
#     This ensures rejected candidates never leak into resume_data, export payloads,
#     cache, or final artifacts.
#     """
#     return {
#         "section_id": section_id,
#         "status": "BLOCKED",
#         "write_receipt": receipt.to_dict(),
#         "context": {
#             "app_id": "apps_rg",
#             "placement": GatePlacement.POST_ENS.value,
#             **{k: str(v) for k, v in context.items() if isinstance(v, (str, int, float, bool))},
#         },
#     }
# 
# 
# def legacy_abort_if_critical(
#     ens_result: Any,
#     strict: bool,
#     section_id: str = "",
# ) -> None:
#     """Legacy compatibility wrapper around _abort_if_critical.
# 
#     This is maintained for backwards compatibility during the W1 migration.
#     New code should use evaluate_and_admit() which integrates the abort check.
#     """
#     if not strict:
#         return
#     if not getattr(ens_result, "accepted", True):
#         from apps_rg.integrations.hops._role_bullet_runner import NarrativeQualityError
#         raise NarrativeQualityError(
#             f"critical section {getattr(ens_result, 'section_id', section_id)} did not pass "
#             f"(reason: {getattr(ens_result, 'fail_reason', 'unknown')})"
#         )
# 
# 
# def evaluate_with_online_judge(
#     section_id: str,
#     judge_verdict: NarrativeJudgeVerdict,
#     candidate: Any,
#     context: Dict[str, Any],
#     rubric_version: str = "2.0.0",
#     threshold_profile_id: str = "apps_rg_default",
# ) -> AcceptedArtifact:
#     """Evaluate using W2 Online Judge Contract — normalize and admit.
# 
#     This function implements the W2 Online Judge Runtime Contract:
#     1. Normalize NarrativeJudgeVerdict to core JudgeVerdict
#     2. Convert to GateVerdict for RuntimeGateEngine aggregation
#     3. Run POST-ENS gates including candidate_acceptance_guard
#     4. Request write admission
# 
#     Args:
#         section_id: The narrative section (e.g., "executive_summary")
#         judge_verdict: The online judge verdict from narrative_judge_scorer
#         candidate: The ensemble winner artifact
#         context: Runtime context
#         rubric_version: Version of rubric applied
#         threshold_profile_id: Active threshold profile
# 
#     Returns:
#         AcceptedArtifact with normalized judge verdict
# 
#     Raises:
#         WriteBlockedError: If judge rejects candidate or malformed verdict
#     """
#     # W2: Normalize online judge verdict to core contract
#     judge_context = JudgeRuntimeContext(
#         section_id=section_id,
#         rubric_version=rubric_version,
#         threshold_profile_id=threshold_profile_id,
#         gate_id=f"{section_id}_judge",
#         placement=GatePlacement.PER_CAND,
#     )
# 
#     # Validate and normalize
#     normalized = normalize_narrative_judge_verdict(judge_verdict, judge_context)
#     validated = OnlineJudgeContractValidator.normalize_or_unknown(
#         normalized, judge_context
#     )
# 
#     # Convert to GateVerdict for engine aggregation
#     gate_verdict = validated.to_gate_verdict()
# 
#     # Update context with per-cand judge results
#     context["per_cand_results"] = context.get("per_cand_results", {})
#     context["per_cand_results"][section_id] = gate_verdict.result
#     context["judge_verdict"] = {
#         "judge_id": validated.judge_id,
#         "judge_version": validated.judge_version,
#         "score": validated.score,
#         "accepted": validated.accepted,
#         "result": validated.result.value,
#     }
# 
#     # Log W2 contract compliance
#     _log.info(
#         "[W2] Judge verdict normalized: section=%s judge=%s v=%s score=%.3f result=%s",
#         section_id,
#         validated.judge_id,
#         validated.judge_version,
#         validated.score,
#         validated.result.value,
#     )
# 
#     # Continue with W1 admission flow
#     return evaluate_and_admit(section_id, candidate, context, fail_if_rejected=True)
# 
# 
# def get_judge_provenance(section_id: str) -> Dict[str, str]:
#     """Get W2 Online Judge Contract provenance for a section.
# 
#     Returns the required identifiers for runtime contract validation.
#     """
#     return {
#         "judge_id": NARRATIVE_JUDGE_ID,
#         "judge_version": "1.0.0",
#         "rubric_version": "2.0.0",
#         "threshold_profile_id": "apps_rg_default",
#         "section_id": section_id,
#         "contract_version": "W2.0",
#     }
# 
# 
# __all__ = [
#     "AcceptedArtifact",
#     "WriteBlockedError",
#     "evaluate_and_admit",
#     "evaluate_with_online_judge",
#     "sealed_failure_packet",
#     "legacy_abort_if_critical",
#     "get_judge_provenance",
# ]
# 