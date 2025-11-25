"""Atomic Integration Layer - Bridges OpenAI structure to L1-L5 atomicity.

This module provides the bridge between the OpenAI-style capability folders
and the strict L1-L5 atomic layer enforcement.
"""

from typing import Any, Dict, Optional
from l3.unified_workflow_orchestrator import UnifiedWorkflowOrchestrator
from l4.state_manager import StateManager
from l5.safety_validator import SafetyValidator
from core.routing import RoutingPolicy
from config.meta_profile import MetaProfileSnapshot
from runtime.runtime_utils import SandboxConfig
from pathlib import Path

class AtomicWorkflowBridge:
    """Bridge layer that enforces L1-L5 atomicity within OpenAI structure."""
    
    def __init__(self, routing_policy: RoutingPolicy, sandbox: SandboxConfig, meta_profile: Optional[MetaProfileSnapshot] = None):
        # Create L4/L5 components for dependency injection
        state_manager = StateManager(Path(sandbox.config.get("state_path", "state.json")))
        safety_validator = SafetyValidator()
        
        # Create L3 orchestrator with injected L4/L5 dependencies and meta_profile
        self.unified_orchestrator = UnifiedWorkflowOrchestrator(
            routing_policy, sandbox, state_manager, safety_validator, meta_profile
        )
    
    def execute_atomic_workflow(self, job: Any, resume: Any, config: Any) -> Dict[str, Any]:
        """Execute workflow through strict L1-L5 atomic layers."""
        return self.unified_orchestrator.orchestrate_full_workflow(job, resume, config)

# Backward compatibility agents that delegate to atomic layers
class AtomicStrategyAgent:
    """Strategy agent that delegates to atomic L1-L5 layers."""
    
    def __init__(self, routing_policy: RoutingPolicy, sandbox: SandboxConfig, meta_profile: Optional[MetaProfileSnapshot] = None):
        self.bridge = AtomicWorkflowBridge(routing_policy, sandbox, meta_profile)
    
    async def run_strategy(self, strategy_plan: Any, job: Any, resume: Any, config: Any) -> Any:
        """Delegate to atomic workflow - pure orchestration."""
        result = self.bridge.execute_atomic_workflow(job, resume, config)
        return result["strategy"]

class AtomicDraftingAgent:
    """Drafting agent that delegates to atomic L1-L5 layers."""
    
    def __init__(self, routing_policy: RoutingPolicy, sandbox: SandboxConfig, meta_profile: Optional[MetaProfileSnapshot] = None):
        self.bridge = AtomicWorkflowBridge(routing_policy, sandbox, meta_profile)
    
    async def run_drafting(self, drafting_plan: Any, job: Any, resume: Any, strategy_result: Any, rag_result: Any, config: Any) -> Any:
        """Delegate to atomic workflow - pure orchestration."""
        result = self.bridge.execute_atomic_workflow(job, resume, config)
        return result["draft"]

class AtomicQAAgent:
    """QA agent that delegates to atomic L1-L5 layers."""
    
    def __init__(self, routing_policy: RoutingPolicy, sandbox: SandboxConfig, meta_profile: Optional[MetaProfileSnapshot] = None):
        self.bridge = AtomicWorkflowBridge(routing_policy, sandbox, meta_profile)
    
    async def run_qa(self, qa_plan: Any, draft: Any, rag: Any, job: Any, resume: Any, config: Any) -> Any:
        """Delegate to atomic workflow - pure orchestration."""
        result = self.bridge.execute_atomic_workflow(job, resume, config)
        return result["qa"]

class AtomicSafetyAgent:
    """Safety agent that delegates to atomic L1-L5 layers."""
    
    def __init__(self, routing_policy: RoutingPolicy, sandbox: SandboxConfig, meta_profile: Optional[MetaProfileSnapshot] = None):
        self.bridge = AtomicWorkflowBridge(routing_policy, sandbox, meta_profile)
    
    async def run_safety(self, safety_plan: Any, draft: Any, rag: Any, qa: Any, job: Any, resume: Any, config: Any) -> Any:
        """Delegate to atomic workflow - pure orchestration."""
        result = self.bridge.execute_atomic_workflow(job, resume, config)
        return result["safety"]
