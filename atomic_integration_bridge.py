"""Bridges OpenAI structure to atomic L1-L5 layers with strict boundaries.

Ensures resume generation follows a clean, maintainable architecture that improves
output consistency and makes it easier to enhance resume quality over time.
"""

from typing import Any, Dict, Optional
from pathlib import Path

# Import concrete implementations to be wrapped
from l3.unified_workflow_orchestrator import UnifiedWorkflowOrchestrator
from l4.state_manager import StateManager
from l5.safety_validator import SafetyValidator

# Import core types and configurations
from core.routing import RoutingPolicy
from config.meta_profile import MetaProfileSnapshot
from runtime.runtime_utils import SandboxConfig

class AtomicWorkflowBridge:
    """Coordinates resume generation across specialized atomic layers.
    
    Ensures each resume section is processed with the right balance of
    planning, execution, and safety checks for optimal job alignment.
    """
    
    def __init__(self, routing_policy: RoutingPolicy, sandbox: SandboxConfig, meta_profile: Optional[MetaProfileSnapshot] = None):
        # Create L4/L5 components for dependency injection
        state_manager = StateManager(Path(sandbox.config.get("state_path", "state.json")))
        safety_validator = SafetyValidator()
        
        # Create L3 orchestrator with injected L4/L5 dependencies and meta_profile
        self.unified_orchestrator = UnifiedWorkflowOrchestrator(
            routing_policy, sandbox, state_manager, safety_validator, meta_profile
        )
    
    def execute_atomic_workflow(self, job: Any, resume: Any, config: Any) -> Dict[str, Any]:
        """Orchestrates the resume generation workflow through atomic layers.
        
        Maintains clean separation of concerns while ensuring all resume sections
        meet quality standards and job requirements.
        """
        return self.unified_orchestrator.orchestrate_full_workflow(job, resume, config)

# Backward compatibility agents that delegate to atomic layers
class AtomicStrategyAgent:
    """Handles strategic planning for resume content organization.
    
    Aligns resume structure with job requirements for maximum impact
    and applicant tracking system (ATS) compatibility.
    """
    
    def __init__(self, routing_policy: RoutingPolicy, sandbox: SandboxConfig, meta_profile: Optional[MetaProfileSnapshot] = None):
        self.bridge = AtomicWorkflowBridge(routing_policy, sandbox, meta_profile)
    
    async def run_strategy(self, strategy_plan: Any, job: Any, resume: Any, config: Any) -> Any:
        """Delegate to atomic workflow - pure orchestration."""
        result = self.bridge.execute_atomic_workflow(job, resume, config)
        return result["strategy"]

class AtomicDraftingAgent:
    """Manages the creation of initial resume drafts.
    
    Ensures content flows naturally while highlighting relevant
    skills and experiences for the target position.
    """
    
    def __init__(self, routing_policy: RoutingPolicy, sandbox: SandboxConfig, meta_profile: Optional[MetaProfileSnapshot] = None):
        self.bridge = AtomicWorkflowBridge(routing_policy, sandbox, meta_profile)
    
    async def run_drafting(self, drafting_plan: Any, job: Any, resume: Any, strategy_result: Any, rag_result: Any, config: Any) -> Any:
        """Delegate to atomic workflow - pure orchestration."""
        result = self.bridge.execute_atomic_workflow(job, resume, config)
        return result["draft"]

class AtomicQAAgent:
    """Validates resume content quality and consistency.
    
    Checks for clarity, relevance, and alignment with job requirements
    to ensure the resume makes a strong first impression.
    """
    
    def __init__(self, routing_policy: RoutingPolicy, sandbox: SandboxConfig, meta_profile: Optional[MetaProfileSnapshot] = None):
        self.bridge = AtomicWorkflowBridge(routing_policy, sandbox, meta_profile)
    
    async def run_qa(self, qa_plan: Any, draft: Any, rag: Any, job: Any, resume: Any, config: Any) -> Any:
        """Delegate to atomic workflow - pure orchestration."""
        result = self.bridge.execute_atomic_workflow(job, resume, config)
        return result["qa"]

class AtomicSafetyAgent:
    """Ensures resume content meets professional and ethical standards.
    
    Validates factual accuracy and prevents misleading claims while
    maintaining a positive, professional tone throughout the resume.
    """
    
    def __init__(self, routing_policy: RoutingPolicy, sandbox: SandboxConfig, meta_profile: Optional[MetaProfileSnapshot] = None):
        self.bridge = AtomicWorkflowBridge(routing_policy, sandbox, meta_profile)
    
    async def run_safety(self, safety_plan: Any, draft: Any, rag: Any, qa: Any, job: Any, resume: Any, config: Any) -> Any:
        """Delegate to atomic workflow - pure orchestration."""
        result = self.bridge.execute_atomic_workflow(job, resume, config)
        return result["safety"]
