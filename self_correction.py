# FILE: self_correction.py
"""
Unified Correction Surface Registry (v10_10) — AUTONOMOUS RECOVERY

This module implements Pillar 5 (Capability Maturity).
It acts as the "Immune System" of the agent, defining explicit rules for
detecting failures and prescribing remediation strategies.

It is PURE DECISION LOGIC. It does not execute the retry (L3 does that).

Responsibilities:
    1. Surface Registration: Define known failure modes (RAG empty, QA fail).
    2. Strategy Mapping: Map failures to actions (Retry, Replan, Escalate).
    3. Parameter Tuning: Modify next-hop config (e.g., "increase temp on retry").
"""

from __future__ import annotations

from typing import Dict, Any, Optional, Callable
from pydantic import BaseModel, Field

from models import (
    CorrectionSignal, 
    CorrectionProposal, 
    SelfCorrectionSurface,
    NodeStatus
)

# =============================================================================
# CONFIGURATION MODELS
# =============================================================================

class RemediationPolicy(BaseModel):
    """Declarative rule for handling a specific failure surface."""
    surface_id: str
    action: str             # retry_node, replan_workflow, escalate
    max_retries: int = 1
    backoff_factor: float = 1.0
    param_modifiers: Dict[str, Any] = Field(default_factory=dict)
    
    # For advanced logic (e.g. "only retry if score > 0.5")
    condition: Optional[str] = None 

# =============================================================================
# CORRECTION REGISTRY
# =============================================================================

class CorrectionSurfaceRegistry:
    """
    Central store for recovery policies.
    """
    
    def __init__(self):
        self._policies: Dict[str, RemediationPolicy] = {}
        self._initialize_golden_surfaces()

    def register(self, policy: RemediationPolicy) -> None:
        self._policies[policy.surface_id] = policy

    def resolve(self, signal: CorrectionSignal, attempt_count: int) -> CorrectionProposal:
        """
        Converts a raw Error Signal into an Actionable Proposal.
        """
        policy = self._policies.get(signal.surface)
        
        # 1. Unknown Surface -> Escalate (Safety First)
        if not policy:
            return CorrectionProposal(
                action="escalate",
                target_node="human_supervisor",
                parameters={"reason": f"Unknown failure surface: {signal.surface}"},
                rationale="No remediation policy defined."
            )

        # 2. Retry Limit Exceeded -> Escalate
        if attempt_count >= policy.max_retries:
            return CorrectionProposal(
                action="escalate",
                target_node="human_supervisor",
                parameters={"reason": "Max retries exceeded"},
                rationale=f"Failed after {attempt_count} attempts."
            )

        # 3. Generate Proposal (The Fix)
        # We inject the context from the signal (e.g. the specific QA error)
        # into the parameters for the next attempt.
        
        params = policy.param_modifiers.copy()
        params["feedback_context"] = signal.context
        
        return CorrectionProposal(
            action=policy.action,
            target_node="current_phase", # Default to retrying same phase
            parameters=params,
            rationale=f"Policy {policy.surface_id} triggered retry."
        )

    def _initialize_golden_surfaces(self) -> None:
        """
        Seeding the registry with v10_10 Standard Recovery Paths.
        """
        
        # SURFACE 1: QA Failure (Accuracy issue)
        # Strategy: Retry L2 execution, but force "Reflexion" reasoning.
        self.register(RemediationPolicy(
            surface_id=SelfCorrectionSurface.QA_RECHECK.value,
            action="retry_node",
            max_retries=2,
            param_modifiers={
                "reasoning_strategy": "reflexion", # Force self-critique
                "temperature": 0.3 # Lower temp for precision
            }
        ))

        # SURFACE 2: RAG Zero Results (Context issue)
        # Strategy: Retry L2, but expand query generation.
        self.register(RemediationPolicy(
            surface_id=SelfCorrectionSurface.RAG_RETRY.value,
            action="retry_node",
            max_retries=1,
            param_modifiers={
                "query_expansion_factor": 2, # Generate more queries
                "hybrid_search": True # Force hybrid if not already
            }
        ))

        # SURFACE 3: Safety Block (Policy issue)
        # Strategy: Replan (Go back to L1) or Escalate.
        # We chose Escalate for high-severity blocks, Replan for minor.
        # This basic policy handles the generic case.
        self.register(RemediationPolicy(
            surface_id=SelfCorrectionSurface.SAFETY_RISK.value,
            action="escalate", # Safety is usually hard block
            max_retries=0
        ))

        # SURFACE 4: Strategy Logic Error (Cognitive issue)
        # Strategy: Replan (Go back to L1 to generate new branches).
        self.register(RemediationPolicy(
            surface_id=SelfCorrectionSurface.STRATEGY_REPLAN.value,
            action="replan_workflow",
            max_retries=1,
            param_modifiers={
                "complexity": "high" # Up the complexity
            }
        ))

# Global Singleton
CORRECTION_ENGINE = CorrectionSurfaceRegistry()
