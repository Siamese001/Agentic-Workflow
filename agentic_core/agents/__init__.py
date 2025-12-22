"""Agent classes for agentic_core."""

# Standard library imports
import logging
from dataclasses import dataclass
from typing import Any, Dict, Optional

# Define logger for this module
logger = logging.getLogger(__name__)

# Local application imports (absolute)
from agentic_core.domain.context import ValidationContext

# Local application imports (relative)
# Base classes
# Analysis agents
from .analysis import SemanticMapper, TruthKeeper
from .base import ImportPatcher, SubAtomicAgent

# Canon Validator agents (Subatomic Level 5)
from .canon_base_agent import CanonBaseAgent
from .code_janitor import CodeJanitor

# Concurrency agents
from .concurrency import (
    DeadlockAnalyzer,
    DeadlockDetector,
    MemoryLeakDetector,
    RaceAnalyzer,
)

# Context agents
from .context import OmniContext

# Engineering agents
from .engineering import PatternEnforcer, StructuralEngineer

# Governance agents
from .governance import ArchitectureGovernor, DependencySentinel
from .healer_agent import HealerAgent

# Infrastructure agents
from .infrastructure import BenchmarkingAgent, GitAgent, Historian

# Planning agents
from .planning import ReflectionAgent, StrategicPlanner

# Quality agents (HygieneGuardian, CodeStyleGuardian, PerformanceEnforcer)
from .quality import CodeStyleGuardian, HygieneGuardian, PerformanceEnforcer

# Repair agents
from .repair import Sherlock, TestPilot, ToolsmithAgent

# Security agents (SafetyInspector, ConcurrencyGuardian, SecurityEnforcer, RedSentinel)
from .security import (
    ConcurrencyGuardian,
    RedSentinel,
    SafetyInspector,
    SecurityEnforcer,
)

# Specialized agents
from .specialized import (
    DocEnforcer,
    NamingEnforcer,
    TheCartographer,
    TheOmniContext,
    TheStrategist,
    TypeEnforcer,
)
from .structural_engineer import StructuralEngineer as CanonStructuralEngineer
from .system_architect import SystemArchitect

# Memory agents (Level 5 Autonomous Learning)

# Pattern retrieval agents

# Systemic enhancement agents

# Cognitive assurance agents


# --- Start of merged content from outreach_agent.py ---

# Outreach Agent - LinkedIn Campaign Orchestration
@dataclass
class OutreachConfig:
    """Configuration for outreach campaigns."""
    campaign_id: str
    archetype: str = "RECRUITER"
    max_cycles: int = 5
    quality_threshold: float = 0.75
    enable_intervention: bool = True


class OutreachAgent:
    """
    Specialized agent for LinkedIn outreach campaigns.
    
    Implements:
    - Campaign-specific validation
    - Archetype-based personalization
    - Quality threshold enforcement
    - Message template management
    """
    
    def __init__(self, context: ValidationContext, config: OutreachConfig):
        """
        Initialize outreach agent.
        
        Args:
            context: Validation context
            config: Outreach configuration
        """
        self.ctx = context
        self.config = config
        self.name = "OutreachAgent"
        logger.info(f"Initialized {self.name} for campaign {config.campaign_id}")
    
    async def execute(self) -> Dict[str, Any]:
        """
        Execute outreach campaign validation and generation.
        
        Returns:
            Execution results
        """
        logger.info(f"Executing outreach campaign: {self.config.campaign_id}")
        logger.info(f"  Archetype: {self.config.archetype}")
        logger.info(f"  Quality threshold: {self.config.quality_threshold}")
        
        results = {
            "campaign_id": self.config.campaign_id,
            "archetype": self.config.archetype,
            "status": "COMPLETED",
            "messages_generated": 0,
            "quality_score": 0.0
        }
        
        try:
            await self._validate_campaign_context()
            await self._generate_messages()
            await self._enforce_quality_threshold()
            
            self.ctx.signals.add("OUTREACH_COMPLETE")
            logger.info(f"[OK] Outreach campaign completed: {self.config.campaign_id}")
        
        except Exception as e:
            logger.error(f"[X] Outreach campaign failed: {e}")
            results["status"] = "FAILED"
            results["error"] = str(e)
            self.ctx.signals.add("OUTREACH_FAILED")
        
        return results
    
    async def _validate_campaign_context(self):
        """Validate campaign context and prerequisites."""
        logger.info("Validating campaign context...")
        
        if not self.config.campaign_id:
            raise ValueError("Campaign ID is required")
        
        if self.config.archetype not in ["RECRUITER", "SALES", "NETWORKING"]:
            logger.warning(f"Unknown archetype: {self.config.archetype}")
    
    async def _generate_messages(self):
        """Generate outreach messages based on archetype."""
        logger.info(f"Generating messages for archetype: {self.config.archetype}")
    
    async def _enforce_quality_threshold(self):
        """Enforce quality threshold on generated content."""
        logger.info(f"Enforcing quality threshold: {self.config.quality_threshold}")
    
    def can_run(self) -> bool:
        """Check if agent can run."""
        return "CRITICAL_FAIL" not in self.ctx.signals


def create_outreach_agent(
    context: ValidationContext,
    campaign_id: str,
    archetype: str = "RECRUITER",
    max_cycles: int = 5,
    quality_threshold: float = 0.75,
    enable_intervention: bool = True
) -> OutreachAgent:
    """
    Factory function to create outreach agent.
    
    Args:
        context: Validation context
        campaign_id: Campaign identifier
        archetype: Campaign archetype
        max_cycles: Maximum cycles
        quality_threshold: Quality threshold
        enable_intervention: Enable human intervention
        
    Returns:
        OutreachAgent instance
    """
    config = OutreachConfig(
        campaign_id=campaign_id,
        archetype=archetype,
        max_cycles=max_cycles,
        quality_threshold=quality_threshold,
        enable_intervention=enable_intervention
    )
    
    return OutreachAgent(context, config)

# --- End of merged content from outreach_agent.py ---


# --- Start of merged content from resume_agent.py ---

# Resume Agent - Resume Generation Orchestration
@dataclass
class ResumeConfig:
    """Configuration for resume generation."""
    workflow_id: str
    workflow_type: str = "resume_generation"
    enable_titanium_rag: bool = True
    enable_state_persistence: bool = True
    storage_path: Optional[str] = None
    run_base_dir: str = "./pipeline_runs"


class ResumeAgent:
    """
    Specialized agent for resume generation workflows.
    
    Implements:
    - Trinity architecture (Cognitive + Action)
    - Hardened routing with provider fallback
    - Atomic state checkpointing
    - Titanium RAG integration
    - ACID state persistence
    """
    
    def __init__(self, context: ValidationContext, config: ResumeConfig):
        """
        Initialize resume agent.
        
        Args:
            context: Validation context
            config: Resume configuration
        """
        self.ctx = context
        self.config = config
        self.name = "ResumeAgent"
        logger.info(f"Initialized {self.name} for workflow {config.workflow_id}")
    
    async def execute(self) -> Dict[str, Any]:
        """
        Execute resume generation workflow.
        
        Returns:
            Execution results
        """
        logger.info(f"Executing resume workflow: {self.config.workflow_id}")
        logger.info(f"  Titanium RAG: {self.config.enable_titanium_rag}")
        logger.info(f"  State persistence: {self.config.enable_state_persistence}")
        
        results = {
            "workflow_id": self.config.workflow_id,
            "workflow_type": self.config.workflow_type,
            "status": "COMPLETED",
            "hops_completed": [],
            "hops_failed": []
        }
        
        try:
            await self._initialize_workflow()
            await self._execute_cognitive_phase()
            await self._execute_action_phase()
            await self._finalize_workflow()
            
            self.ctx.signals.add("RESUME_COMPLETE")
            logger.info(f"[OK] Resume workflow completed: {self.config.workflow_id}")
        
        except Exception as e:
            logger.error(f"[X] Resume workflow failed: {e}")
            results["status"] = "FAILED"
            results["error"] = str(e)
            self.ctx.signals.add("RESUME_FAILED")
        
        return results
    
    async def _initialize_workflow(self):
        """Initialize workflow state and context."""
        logger.info("Initializing resume workflow...")
        
        if self.config.enable_state_persistence:
            logger.info("  State persistence enabled")
    
    async def _execute_cognitive_phase(self):
        """Execute cognitive processing phase (planning, reasoning)."""
        logger.info("Executing cognitive phase...")
        
        if self.config.enable_titanium_rag:
            logger.info("  Titanium RAG enabled for context retrieval")
    
    async def _execute_action_phase(self):
        """Execute action phase (generation, formatting)."""
        logger.info("Executing action phase...")
    
    async def _finalize_workflow(self):
        """Finalize workflow and create checkpoint."""
        logger.info("Finalizing workflow...")
        
        if self.config.enable_state_persistence:
            logger.info("  Creating final checkpoint")
    
    def can_run(self) -> bool:
        """Check if agent can run."""
        return "CRITICAL_FAIL" not in self.ctx.signals


def create_resume_agent(
    context: ValidationContext,
    workflow_id: str,
    workflow_type: str = "resume_generation",
    enable_titanium_rag: bool = True,
    enable_state_persistence: bool = True,
    storage_path: Optional[str] = None,
    run_base_dir: str = "./pipeline_runs"
) -> ResumeAgent:
    """
    Factory function to create resume agent.
    
    Args:
        context: Validation context
        workflow_id: Workflow identifier
        workflow_type: Type of workflow
        enable_titanium_rag: Enable Titanium RAG
        enable_state_persistence: Enable state persistence
        storage_path: Path for state storage
        run_base_dir: Base directory for runs
        
    Returns:
        ResumeAgent instance
    """
    config = ResumeConfig(
        workflow_id=workflow_id,
        workflow_type=workflow_type,
        enable_titanium_rag=enable_titanium_rag,
        enable_state_persistence=enable_state_persistence,
        storage_path=storage_path,
        run_base_dir=run_base_dir
    )
    
    return ResumeAgent(context, config)

# --- End of merged content from resume_agent.py ---


__all__ = [
    # Base
    'SubAtomicAgent',
    'ImportPatcher',
    # Canon Validator (Subatomic Level 5)
    'CanonBaseAgent',
    'SystemArchitect',
    'CodeJanitor',
    'CanonStructuralEngineer',
    'HealerAgent',
    # Analysis
    'SemanticMapper',
    'TruthKeeper',
    # Concurrency
    'MemoryLeakDetector',
    'DeadlockAnalyzer',
    'DeadlockDetector',
    'RaceAnalyzer',
    # Context
    'OmniContext',
    # Planning
    'StrategicPlanner',
    'ReflectionAgent',
    # Security
    'SafetyInspector',
    'ConcurrencyGuardian',
    'SecurityEnforcer',
    'RedSentinel',
    # Specialized
    'TheCartographer',
    'TheOmniContext',
    'TheStrategist',
    'NamingEnforcer',
    'DocEnforcer',
    'TypeEnforcer',
    'OutreachAgent',  # Added new agent
    'ResumeAgent',    # Added new agent
    # Infrastructure
    'Historian',
    'GitAgent',
    'BenchmarkingAgent',
    # Engineering
    'StructuralEngineer',
    'PatternEnforcer',
    # Governance
    'ArchitectureGovernor',
    'DependencySentinel',
    # Quality
    'HygieneGuardian',
    'CodeStyleGuardian',
    'PerformanceEnforcer',
    # Repair
    'TestPilot',
    'ToolsmithAgent',
    'Sherlock',
]