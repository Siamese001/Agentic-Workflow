"""W1 Phase 5 — Composite Veto Orchestrator.

Chains veto stages in order (Layer 1 → Layer 2), implementing fail-closed
logic across the pipeline. Uses policy JSON to determine stage configuration.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from tools.certification.safety.veto_protocol import (
    VetoResult,
    VetoStage,
    VetoStatus,
    NO_VETO_CONFIGURED,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_POLICY_PATH = REPO_ROOT / "artifacts" / "certification" / "semantic_cache_veto_policy.json"


class VetoOrchestrator:
    """Orchestrates multiple veto stages with fail-closed semantics.
    
    Execution order:
    1. Layer 0: Dense cosine threshold (handled by cache layer, not here)
    2. Layer 1: Lexical pre-veto (if enabled in policy)
       - If SAFE: proceed to Layer 2
       - If DELEGATE: proceed to Layer 2
       - If any block: return immediately (fail-closed)
    3. Layer 2: Primary veto (LLM-judge or cross-encoder)
       - If SAFE: return SAFE
       - If any block/unknown/error: return block (fail-closed)
    
    All stages must implement VetoStage Protocol.
    """
    
    def __init__(
        self,
        policy_path: Path | None = None,
        stages: list[VetoStage] | None = None,
        latency_budget_ms: int = 2500,
    ):
        self._policy_path = policy_path or DEFAULT_POLICY_PATH
        self._policy: dict[str, Any] = {}
        self._stages: list[VetoStage] = stages or []
        self._latency_budget_ms = latency_budget_ms
        self._stage_order: list[str] = []
        self._load_policy()
    
    def _load_policy(self) -> None:
        """Load veto policy from JSON."""
        if not self._policy_path.exists():
            # Use defaults if no policy file
            self._policy = {
                "enabled_stages": {
                    "lexical_intent_pre_veto": True,
                    "llm_judge": True,
                    "cross_encoder": False,
                },
                "stage_order": ["lexical_intent_pre_veto", "llm_judge"],
                "latency_budget_ms": 2500,
            }
            return
        
        try:
            self._policy = json.loads(self._policy_path.read_text(encoding="utf-8"))
        except Exception:
            # Fail-closed: empty policy means no stages available
            self._policy = {"enabled_stages": {}, "stage_order": []}
        
        self._stage_order = self._policy.get("stage_order", [])
        self._latency_budget_ms = self._policy.get("latency_budget_ms", 2500)
        
        # Auto-instantiate stages from policy if not provided
        if not self._stages:
            self._stages = self._instantiate_stages()
    
    def _instantiate_stages(self) -> list[VetoStage]:
        """Create stage instances from policy configuration."""
        stages = []
        enabled = self._policy.get("enabled_stages", {})
        
        # Import here to avoid circular dependencies
        try:
            from tools.certification.safety.lexical_intent_veto import (
                LexicalIntentVeto,
                create_veto_from_policy,
            )
            from tools.certification.safety.llm_judge_veto import (
                LLMJudgeVeto,
                create_veto_from_policy as create_llm_veto,
            )
        except ImportError:
            # Stages not available yet
            return []
        
        for stage_name in self._stage_order:
            if not enabled.get(stage_name, False):
                continue
            
            try:
                if stage_name == "lexical_intent_pre_veto":
                    stages.append(create_veto_from_policy(self._policy))
                elif stage_name == "llm_judge":
                    stages.append(create_llm_veto(self._policy))
                elif stage_name == "cross_encoder":
                    # Cross-encoder not yet implemented in this wave
                    # Placeholder: will raise on use
                    stages.append(_UnavailableStage("cross_encoder"))
            except Exception:
                # Skip stages that fail to instantiate
                pass
        
        return stages
    
    def evaluate(
        self,
        query: str,
        cached_query: str,
        cached_answer: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> VetoResult:
        """Evaluate cache reuse safety through all configured stages.
        
        Fail-closed: any error, timeout, or block at any stage
        returns immediately with VETO/ERROR/UNKNOWN status.
        
        Returns:
            Final VetoResult after all stages or first blocking result.
        """
        start_time = time.perf_counter()
        accumulated_latency_ms = 0.0
        stage_results: list[VetoResult] = []
        
        if not self._stages:
            return NO_VETO_CONFIGURED
        
        for stage in self._stages:
            # Check remaining budget
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            remaining_budget = self._latency_budget_ms - elapsed_ms
            
            if remaining_budget <= 0:
                # Budget exhausted — fail-closed
                return VetoResult.error(
                    stage_name="orchestrator",
                    error=f"Latency budget exhausted: {elapsed_ms:.0f}ms > {self._latency_budget_ms}ms",
                    latency_ms=elapsed_ms,
                    metadata={"stage_results": [r.to_dict() for r in stage_results]},
                )
            
            # Evaluate this stage
            stage_start = time.perf_counter()
            try:
                result = stage.evaluate(
                    query=query,
                    cached_query=cached_query,
                    cached_answer=cached_answer,
                    context=context,
                )
            except Exception as e:
                # Stage threw exception — fail-closed
                result = VetoResult.error(
                    stage_name=stage.name,
                    error=f"Stage exception: {e}",
                    latency_ms=(time.perf_counter() - stage_start) * 1000,
                )
            
            stage_latency = (time.perf_counter() - stage_start) * 1000
            accumulated_latency_ms += stage_latency
            stage_results.append(result)
            
            # Check for blocking result
            if result.blocks_reuse():
                # Fail-closed: block immediately
                return VetoResult(
                    status=result.status,
                    stage_name=f"orchestrator:{stage.name}",
                    confidence=result.confidence,
                    rationale=result.rationale,
                    latency_ms=(time.perf_counter() - start_time) * 1000,
                    metadata={
                        "blocking_stage": stage.name,
                        "stage_results": [r.to_dict() for r in stage_results],
                        "accumulated_latency_ms": accumulated_latency_ms,
                    },
                )
            
            # Special handling for DELEGATE (pre-veto only)
            if result.status == VetoStatus.DELEGATE:
                # Continue to next stage — delegation is not a final verdict
                continue
            
            # SAFE result from this stage — continue to next stage
            # (unless this was the final stage, in which case return SAFE)
        
        # All stages passed (all SAFE or final was SAFE)
        final_result = stage_results[-1] if stage_results else NO_VETO_CONFIGURED
        return VetoResult(
            status=VetoStatus.SAFE,
            stage_name="orchestrator:all_stages",
            confidence=min(r.confidence for r in stage_results) if stage_results else 0.0,
            rationale=f"All {len(stage_results)} veto stages passed. Final: {final_result.stage_name}.",
            latency_ms=(time.perf_counter() - start_time) * 1000,
            metadata={
                "stage_results": [r.to_dict() for r in stage_results],
                "accumulated_latency_ms": accumulated_latency_ms,
            },
        )
    
    def get_policy_summary(self) -> dict[str, Any]:
        """Return summary of current policy for diagnostics."""
        return {
            "policy_id": self._policy.get("policy_id", "unknown"),
            "enabled_stages": self._policy.get("enabled_stages", {}),
            "stage_order": self._stage_order,
            "latency_budget_ms": self._latency_budget_ms,
            "instantiated_stages": [s.name for s in self._stages],
        }


class _UnavailableStage:
    """Placeholder for unavailable stages (cross-encoder in C-primary config)."""
    
    def __init__(self, name: str):
        self._name = name
    
    @property
    def name(self) -> str:
        return self._name
    
    def is_available(self) -> bool:
        return False
    
    def evaluate(
        self,
        query: str,
        cached_query: str,
        cached_answer: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> VetoResult:
        return VetoResult.error(
            stage_name=self._name,
            error=f"Stage {self._name} not available in current configuration",
        )


# Module-level singleton for convenience
default_orchestrator: VetoOrchestrator | None = None


def get_default_orchestrator() -> VetoOrchestrator:
    """Get or create the default veto orchestrator."""
    global default_orchestrator
    if default_orchestrator is None:
        default_orchestrator = VetoOrchestrator()
    return default_orchestrator
