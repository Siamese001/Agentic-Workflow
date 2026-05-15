"""W10 — Completed Run Evaluator (Core-Owned)

Evaluates completed run evidence AFTER runtime boundary.
Produces CompletedEvalRecord with learning observations.

Exit owns exactly **one** X3 disposition per run; L6 consumes exhaust **after**
that boundary and never emits X3.

Hard Rules:
- Post-runtime only (after Exit X3)
- Read-only access to runtime artifacts
- No current-run mutation
- All proposals inert
"""
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass

from agentic_core.L6_learning import (
    CompletedEvalRecord,
    ProposalPacket,
    ProposalType,
    ProofType,
)


@dataclass(frozen=True)
class RuntimeExhaustBundle:
    """Bundle of runtime exhaust artifacts.
    
    Passed to L6 as read-only input.
    """
    run_id: str
    trace_root: str
    
    # Runtime outputs (read-only refs)
    exit_disposition_receipt: Dict[str, Any]
    gate_mesh_result: Dict[str, Any]
    x1_checkout_result: Dict[str, Any]
    x2_aggregation_result: Dict[str, Any]
    sealed_l2_artifact: Dict[str, Any]
    final_evidence_contract: Dict[str, Any]
    judge_evidence_results: List[Dict[str, Any]]
    
    # U0 package refs (config, not executable)
    u0_package_refs: Dict[str, str]
    learning_profile_ref: str
    meta_feedback_profile_ref: str


class CompletedRunEvaluator:
    """Evaluates completed run and produces learning observations.
    
    Core owns this evaluation logic. Apps provide learning profiles via config.
    """
    
    def __init__(self, learning_profile: Dict[str, Any]):
        """Initialize with app-owned learning profile config.
        
        Args:
            learning_profile: Loaded from app's U0 package config
        """
        self._profile = learning_profile
    
    def evaluate_completed_run(
        self,
        exhaust_bundle: RuntimeExhaustBundle
    ) -> CompletedEvalRecord:
        """Evaluate completed run and produce learning record.
        
        Args:
            exhaust_bundle: Runtime exhaust artifacts (read-only)
            
        Returns:
            CompletedEvalRecord with learning observations
        """
        run_id = exhaust_bundle.run_id
        
        # Extract learning signals from judge evidence
        entity_alias_obs = self._extract_entity_aliases(
            exhaust_bundle.judge_evidence_results
        )
        source_reliability = self._extract_source_reliability(
            exhaust_bundle.judge_evidence_results
        )
        cache_threshold_hints = self._extract_cache_threshold_hints(
            exhaust_bundle.gate_mesh_result
        )
        judge_calibration = self._extract_judge_calibration_signals(
            exhaust_bundle.judge_evidence_results
        )
        downstream_usefulness = self._extract_downstream_usefulness(
            exhaust_bundle.final_evidence_contract
        )
        
        # Build evidence digest
        evidence_refs = [
            f"l6://completed_eval/{run_id}",
            f"exhaust://{exhaust_bundle.trace_root}",
        ]
        
        return CompletedEvalRecord(
            run_id=run_id,
            trace_root=exhaust_bundle.trace_root,
            runtime_exhaust_bundle_ref=f"exhaust://{run_id}",
            exit_disposition_receipt_ref=f"exit://{run_id}",
            gate_mesh_result_ref=f"gate_mesh://{run_id}",
            x1_checkout_result_ref=f"x1://{run_id}",
            x2_aggregation_result_ref=f"x2://{run_id}",
            sealed_l2_artifact_ref=f"sealed_l2://{run_id}",
            final_evidence_contract_ref=f"evidence://{run_id}",
            judge_evidence_refs=tuple(
                f"judge://{j.get('dimension', 'unknown')}" 
                for j in exhaust_bundle.judge_evidence_results
            ),
            entity_alias_observations=entity_alias_obs,
            source_reliability_signals=source_reliability,
            cache_threshold_proposals=cache_threshold_hints,
            judge_calibration_signals=judge_calibration,
            downstream_usefulness_signals=downstream_usefulness,
            evidence_digest=f"sha256:l6-completed-eval-{run_id}",
        )
    
    def _extract_entity_aliases(
        self,
        judge_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Extract entity alias improvements from judge evidence."""
        # Placeholder: real implementation would analyze entity references
        return {
            "observed_entities": [],
            "alias_candidates": [],
            "confidence": 0.0,
        }
    
    def _extract_source_reliability(
        self,
        judge_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Extract source reliability signals from source authority judge."""
        for result in judge_results:
            if result.get('dimension') == 'source_authority':
                return {
                    "source_scores": result.get('source_scores', {}),
                    "reliability_tier": result.get('reliability_tier', 'unknown'),
                }
        return {"source_scores": {}, "reliability_tier": "unknown"}
    
    def _extract_cache_threshold_hints(
        self,
        gate_mesh_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Extract cache threshold tuning hints from gate results."""
        # Analyze cache-related gate verdicts
        return {
            "hit_rate": gate_mesh_result.get('cache_metrics', {}).get('hit_rate', 0.0),
            "threshold_adjustment_hint": 0.0,
        }
    
    def _extract_judge_calibration_signals(
        self,
        judge_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Extract judge calibration signals."""
        calibration_signals = {}
        for result in judge_results:
            dim = result.get('dimension')
            if dim:
                calibration_signals[dim] = {
                    "score": result.get('score', 0.0),
                    "confidence": result.get('confidence', 0.0),
                    "needs_recalibration": result.get('confidence', 1.0) < 0.7,
                }
        return calibration_signals
    
    def _extract_downstream_usefulness(
        self,
        evidence_contract: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Extract downstream usefulness signals."""
        return {
            "apps_rg_consumed": evidence_contract.get('consumed_by_apps_rg', False),
            "apps_lic_consumed": evidence_contract.get('consumed_by_apps_lic', False),
            "usefulness_score": evidence_contract.get('downstream_usefulness', 0.0),
        }
