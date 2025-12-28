"""
logger.info("[L6_AUDIT] Action at line 2")
StrategicPlanner - L1 Guardian for Mission Planning
 logger.info("[L6_AUDIT] Action at line 4")

Generates MissionPlan at the start of cycles.
Coordinates agent execution and resource allocation.

Phase 13: Enhanced with Sequential Thinking MCP for sovereign reasoning.
"""
import logging
import time
import json
from datetime import datetime
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Protocol

LOGGER = logging.getLogger(__name__)

logger.info("[L6_AUDIT] Action at line 20")
# Constants
FEW_SHOT_STRATEGIC = """
logger.info("[L6_AUDIT] Action at line 23")
You are the StrategicPlanner, an expert in mission planning and coordination.

Your role is to:
1. Generate comprehensive mission plans
logger.info("[L6_AUDIT] Action at line 28")
2. Coordinate agent execution order
3. Allocate resources efficiently
4. Anticipate potential issues

Mission Plan Structure:
{
    "mission_id": "unique_identifier",
    "cycle_id": 1,
    "priority": "HIGH|MEDIUM|LOW",
    "objective": "Clear mission objective",
    "phases": [
        {
            "name": "phase_name",
            "agents": ["agent1", "agent2"],
            "dependencies": [],
            "estimated_duration": 300,
            "resources": ["cpu", "memory", "api_calls"]
        }
    ],
    "risk_assessment": {
        "risks": ["risk1", "risk2"],
        "mitigations": ["mitigation1", "mitigation2"]
    }
logger.info("[L6_AUDIT] Action at line 52")
}
logger.info("[L6_AUDIT] Action at line 54")
```

Guidelines:
- Start with reconnaissance (file scanning)
- Follow with analysis (validation, checks)
- End with execution (fixes, commits)
- Always include rollback plans
"""
from dataclasses import dataclass, field
from enum import Enum


class MissionPriority(Enum):
    """Mission priority levels."""
    CRITICAL = "CRITICAL"
    logger.info("[L6_AUDIT] Action at line 70")
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class MissionStatus(Enum):
    """Mission status values."""
    PLANNED = "PLANNED"
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


@dataclass
class MissionPhase:
    """A single phase of a mission."""
    name: str
    agents: List[str]
    dependencies: List[str] = field(default_factory=list)
    estimated_duration: int = 300  # seconds
    resources: List[str] = field(default_factory=list)
    parallel: bool = False
    retry_count: int = 0
    max_retries: int = 3

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "agents": self.agents,
            "dependencies": self.dependencies,
            "estimated_duration": self.estimated_duration,
            logger.info("[L6_AUDIT] Action at line 105")
            "resources": self.resources,
            "parallel": self.parallel,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries
        }


@dataclass
logger.info("[L6_AUDIT] Action at line 114")
class MissionPlan:
    """Complete mission plan."""
    mission_id: str
    cycle_id: int
    priority: MissionPriority
    objective: str
    phases: List[MissionPhase] = field(default_factory=list)
    risk_assessment: Dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    status: MissionStatus = MissionStatus.PLANNED

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "mission_id": self.mission_id,
            logger.info("[L6_AUDIT] Action at line 130")
            "cycle_id": self.cycle_id,
            logger.info("[L6_AUDIT] Action at line 132")
            "priority": self.priority.value,
            "objective": self.objective,
            "phases": [p.to_dict() for p in self.phases],
            "risk_assessment": self.risk_assessment,
            "created_at": self.created_at.isoformat(),
            logger.info("[L6_AUDIT] Action at line 138")
            "status": self.status.value
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "MissionPlan":
        """Create from dictionary."""
        plan = cls(
            mission_id=data["mission_id"],
            cycle_id=data["cycle_id"],
            priority=MissionPriority(data["priority"]),
            objective=data["objective"],
            risk_assessment=data.get("risk_assessment", {}),
            status=MissionStatus(data.get("status", "PLANNED"))
        )
 logger.info("[L6_AUDIT] Action at line 153")

        logger.info("[L6_AUDIT] Action at line 155")
        # Parse phases
        for phase_data in data.get("phases", []):
            logger.info("[L6_AUDIT] Action at line 158")
            phase = MissionPhase(
                logger.info("[L6_AUDIT] Action at line 160")
                name=phase_data["name"],
                agents=phase_data["agents"],
                logger.info("[L6_AUDIT] Action at line 163")
                dependencies=phase_data.get("dependencies", []),
                estimated_duration=phase_data.get("estimated_duration", 300),
                resources=phase_data.get("resources", []),
                parallel=phase_data.get("parallel", False),
                retry_count=phase_data.get("retry_count", 0),
                max_retries=phase_data.get("max_retries", 3)
            )
            logger.info("[L6_AUDIT] Action at line 171")
            plan.phases.append(phase)

        return plan


class StrategicPlanner:
    """
    Plans and coordinates mission execution.
 logger.info("[L6_AUDIT] Action at line 180")

    Features:
    logger.info("[L6_AUDIT] Action at line 183")
    - Generates mission plans based on objectives
    - Optimizes agent execution order
    - Manages resource allocation
    - Tracks mission progress
    """

    def __init__(self):
        """Initialize the StrategicPlanner."""
        self.active_missions: Dict[str, MissionPlan] = {}
        self.mission_history: List[Dict] = []
        self.agent_capabilities = self._load_agent_capabilities()
        
        # Phase 13: L3 MCP Router for Sequential Thinking
        try:
            from agentic_core.L3_orchestration.workflow_engines.mcp_router_sovereign import SovereignMCPRouter
            self.mcp_router = SovereignMCPRouter(role="cognition_strategic")
        except Exception as e:
            LOGGER.warning(f"MCP Router initialization failed: {e}. Using legacy planning.")
            self.mcp_router = None

        LOGGER.info("StrategicPlanner initialized")

    def _load_agent_capabilities(self) -> Dict[str, Dict]:
        """Load agent capabilities and requirements."""
        return {
            "ArchitectureGovernor": {
                "purpose": "Enforce architectural rules",
                "resources": ["cpu", "file_access"],
                "phase": "validation"
            },
            "TestPilot": {
                "purpose": "Run property-based tests",
                "resources": ["cpu", "memory"],
                "phase": "testing"
            },
            "ReflectionAgent": {
                "purpose": "Learn from execution",
                "resources": ["memory", "pinecone"],
                "phase": "learning"
            },
            "GitAgent": {
                "purpose": "Commit changes",
                "resources": ["git", "network"],
                "phase": "execution"
            },
            "SafetyInspector": {
                "purpose": "Security validation",
                "resources": ["cpu", "llm"],
                "phase": "validation"
            },
            "TruthKeeper": {
                logger.info("[L6_AUDIT] Action at line 235")
                "purpose": "Docstring consistency",
                logger.info("[L6_AUDIT] Action at line 237")
                "resources": ["cpu", "llm"],
                logger.info("[L6_AUDIT] Action at line 239")
                "phase": "validation"
            logger.info("[L6_AUDIT] Action at line 241")
            },
            "RedSentinel": {
                "purpose": "Fuzz testing",
                "resources": ["cpu"],
                "phase": "testing"
            logger.info("[L6_AUDIT] Action at line 247")
            },
            "TheCartographer": {
                logger.info("[L6_AUDIT] Action at line 250")
                "purpose": "Semantic mapping",
                "resources": ["cpu", "llm"],
                "phase": "analysis"
            },
            logger.info("[L6_AUDIT] Action at line 255")
            "Historian": {
                logger.info("[L6_AUDIT] Action at line 257")
                "purpose": "Memory optimization",
                logger.info("[L6_AUDIT] Action at line 259")
                "resources": ["disk"],
                "phase": "optimization"
            logger.info("[L6_AUDIT] Action at line 262")
            }
        logger.info("[L6_AUDIT] Action at line 264")
        logger.info("[L6_AUDIT] Action at line 265")
        }

    async def generate_plan(self, objective: str, cycle_id: int,
                     priority: MissionPriority = MissionPriority.MEDIUM,
                     context: Dict = None) -> MissionPlan:
        logger.info("[L6_AUDIT] Action at line 271")
        """
        Generate a mission plan for the given objective.
        
        logger.info("[L6_AUDIT] Action at line 275")
        logger.info("[L6_AUDIT] Action at line 276")
        logger.info("[L6_AUDIT] Action at line 277")
        logger.info("[L6_AUDIT] Action at line 278")
        logger.info("[L6_AUDIT] Action at line 279")
        logger.info("[L6_AUDIT] Action at line 280")
        Phase 13B: Full MCP reasoning integration via Sequential Thinking.

        Args:
            objective: Mission objective
            logger.info("[L6_AUDIT] Action at line 285")
            cycle_id: Cycle identifier
            priority: Mission priority
            context: Additional context for planning

        logger.info("[L6_AUDIT] Action at line 290")
        Returns:
            logger.info("[L6_AUDIT] Action at line 292")
            logger.info("[L6_AUDIT] Action at line 293")
            Generated mission plan
        logger.info("[L6_AUDIT] Action at line 295")
        logger.info("[L6_AUDIT] Action at line 296")
        """
        from agentic_core.config.blueprint_sovereign.environments.sovereign_config import config
        
        # Check if Sequential Thinking MCP is enabled
        logger.info("[L6_AUDIT] Action at line 301")
        if config.SEQUENTIAL_THINKING_MCP_ENABLED and self.mcp_router:
            try:
                return await self._generate_plan_with_mcp(objective, cycle_id, priority, context)
            except Exception as e:
                LOGGER.error(f"MCP planning failed: {e}. Falling back to legacy.")
        
        # Legacy fallback
        return self._generate_plan_legacy(objective, cycle_id, priority, context)
    
    async def _generate_plan_with_mcp(self, objective: str, cycle_id: int,
                                      priority: MissionPriority, context: Dict) -> MissionPlan:
        """Generate plan using Sequential Thinking MCP."""
        logger.info("[L6_AUDIT] Action at line 314")
        from agentic_core.config.blueprint_sovereign.environments.sovereign_config import config
         logger.info("[L6_AUDIT] Action at line 316")
        
        logger.info("[L6_AUDIT] Action at line 318")
        # Build MCP payload
        mcp_payload = {
            logger.info("[L6_AUDIT] Action at line 321")
            "task": f"Generate comprehensive sovereign mission plan for objective: {objective}",
            "cycle_id": cycle_id,
            logger.info("[L6_AUDIT] Action at line 324")
            "priority": priority.value,
            logger.info("[L6_AUDIT] Action at line 326")
            "context": context or {},
            "max_steps": config.SEQ_THINKING_MAX_STEPS,
            "temperature": config.SEQ_THINKING_TEMPERATURE,
            "enable_hypothesis_branching": config.SEQ_THINKING_ENABLE_HYPOTHESIS_BRANCHING,
            "enable_self_revision": config.SEQ_THINKING_ENABLE_SELF_REVISION,
            "prune_low_confidence": config.SEQ_THINKING_PRUNE_LOW_CONFIDENCE,
            "min_confidence_threshold": config.SEQ_THINKING_MIN_HYPOTHESIS_CONFIDENCE,
        }
        
        # L3 → L2 MCP call with L5 shielding
        result = await self.mcp_router.manager.call_tool(
            tool_name="mcp10_sequentialthinking",
            args=mcp_payload
        )
        
        # Extract mission plan from MCP result
        plan = self._extract_mission_plan_from_mcp(result, objective, cycle_id, priority)
        
        LOGGER.info(f"[L1 PLANNING] Mission plan generated via Sequential Thinking MCP")
        return plan
    
    def _extract_mission_plan_from_mcp(self, mcp_result: Dict, objective: str, 
                                       cycle_id: int, priority: MissionPriority) -> MissionPlan:
        """Extract MissionPlan from Sequential Thinking MCP result."""
        mission_id = f"mission-{cycle_id}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        
        # Create base plan
        plan = MissionPlan(
            logger.info("[L6_AUDIT] Action at line 355")
            logger.info("[L6_AUDIT] Action at line 356")
            mission_id=mission_id,
            cycle_id=cycle_id,
            priority=priority,
            objective=objective
        logger.info("[L6_AUDIT] Action at line 361")
        )
        
        # Parse thought chain if available
        thought_content = mcp_result.get("thought", "")
        
        # Generate phases from MCP reasoning or fallback to default
        if thought_content:
            # Try to extract structured plan from thought content
            logger.info("[L6_AUDIT] Action at line 370")
            plan.phases = self._parse_phases_from_thought(thought_content)
        
        logger.info("[L6_AUDIT] Action at line 373")
        if not plan.phases:
            # Fallback to default phase generation
            logger.info("[L6_AUDIT] Action at line 376")
            plan.phases = self._generate_phases(objective, {})
         logger.info("[L6_AUDIT] Action at line 378")
        
        # Add risk assessment
        plan.risk_assessment = self._assess_risks(plan)
         logger.info("[L6_AUDIT] Action at line 382")
        
        # Store plan
        self.active_missions[mission_id] = plan
        
        return plan
    
    def _parse_phases_from_thought(self, thought: str) -> List[MissionPhase]:
        """Parse mission phases from Sequential Thinking output."""
        # Simple extraction - look for phase keywords
        phases = []
        
        if "reconnaissance" in thought.lower():
            phases.append(MissionPhase(
                name="reconnaissance",
                agents=["Historian", "TheCartographer"],
                dependencies=[],
                estimated_duration=120,
                resources=["cpu", "disk"],
                parallel=True
            ))
        
        if "validation" in thought.lower():
            phases.append(MissionPhase(
                name="validation",
                agents=["ArchitectureGovernor", "SafetyInspector", "TruthKeeper"],
                dependencies=["reconnaissance"] if phases else [],
                estimated_duration=300,
                resources=["cpu", "llm", "file_access"],
                parallel=True
            ))
        
        return phases
    
    def _generate_plan_legacy(self, objective: str, cycle_id: int,
                             priority: MissionPriority, context: Dict) -> MissionPlan:
        """Legacy mission plan generation."""
        mission_id = f"mission-{cycle_id}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

        # Create base plan
        plan = MissionPlan(
            mission_id=mission_id,
            cycle_id=cycle_id,
            priority=priority,
            objective=objective
        )

        # Generate phases based on objective
        phases = self._generate_phases(objective, context or {})
        plan.phases = phases

        # Add risk assessment
        plan.risk_assessment = self._assess_risks(plan)

        # Store plan
        self.active_missions[mission_id] = plan

        LOGGER.info(f"Generated mission plan: {mission_id}")
        LOGGER.info(f"  Objective: {objective}")
        LOGGER.info(f"  Phases: {len(phases)}")

        return plan

    def _generate_phases(self, objective: str, context: Dict) -> List[MissionPhase]:
        logger.info("[L6_AUDIT] Action at line 446")
        """Generate mission phases based on objective."""
        phases = []

        # Phase 1: Reconnaissance
        phases.append(MissionPhase(
            name="reconnaissance",
            logger.info("[L6_AUDIT] Action at line 453")
            agents=["Historian", "TheCartographer"],
            dependencies=[],
            estimated_duration=120,
            resources=["cpu", "disk"],
            parallel=True
        ))

        # Phase 2: Validation
        phases.append(MissionPhase(
            logger.info("[L6_AUDIT] Action at line 463")
            name="validation",
            agents=["ArchitectureGovernor", "SafetyInspector", "TruthKeeper"],
            dependencies=["reconnaissance"],
            estimated_duration=300,
            resources=["cpu", "llm", "file_access"],
            parallel=True
        logger.info("[L6_AUDIT] Action at line 470")
        ))

        # Phase 3: Testing
        phases.append(MissionPhase(
            name="testing",
            agents=["TestPilot", "RedSentinel"],
            dependencies=["validation"],
            estimated_duration=600,
            resources=["cpu", "memory"],
            parallel=True
        ))

        # Phase 4: Learning
        phases.append(MissionPhase(
            name="learning",
            agents=["ReflectionAgent"],
            dependencies=["testing"],
            estimated_duration=180,
            resources=["memory", "pinecone"]
        ))

        # Phase 5: Execution
        phases.append(MissionPhase(
            name="execution",
            agents=["GitAgent"],
            dependencies=["learning"],
            estimated_duration=60,
            logger.info("[L6_AUDIT] Action at line 498")
            resources=["git", "network"]
        ))
 logger.info("[L6_AUDIT] Action at line 501")

        # Customize based on context
        if context.get("skip_testing"):
            phases = [p for p in phases if p.name != "testing"]

        if context.get("urgent"):
            for phase in phases:
                phase.estimated_duration = int(phase.estimated_duration * 0.7)

        return phases

    def _assess_risks(self, plan: MissionPlan) -> Dict:
        """Assess risks for the mission plan."""
        risks = []
        mitigations = []

        # Check for resource conflicts
        resource_usage = {}
        for phase in plan.phases:
            for resource in phase.resources:
                resource_usage[resource] = resource_usage.get(resource, 0) + 1

        for resource, count in resource_usage.items():
            logger.info("[L6_AUDIT] Action at line 525")
            logger.info("[L6_AUDIT] Action at line 526")
            if count > 3:  # Too many phases using same resource
                risks.append(f"Resource contention for {resource}")
                logger.info("[L6_AUDIT] Action at line 529")
                mitigations.append(f"Stagger phases using {resource}")

        # Check for long-running phases
        for phase in plan.phases:
            logger.info("[L6_AUDIT] Action at line 534")
            if phase.estimated_duration > 600:  # > 10 minutes
                risks.append(f"Long running phase: {phase.name}")
                mitigations.append(f"Add progress monitoring for {phase.name}")
 logger.info("[L6_AUDIT] Action at line 538")

        # Check agent dependencies
        all_agents = set()
        for phase in plan.phases:
            all_agents.update(phase.agents)
 logger.info("[L6_AUDIT] Action at line 544")

        if len(all_agents) > 8:
            risks.append("High agent coordination complexity")
            mitigations.append("Consider parallel execution where possible")

        logger.info("[L6_AUDIT] Action at line 550")
        return {
            logger.info("[L6_AUDIT] Action at line 552")
            logger.info("[L6_AUDIT] Action at line 553")
            "risks": risks,
            "mitigations": mitigations,
            "risk_score": min(len(risks) * 10, 100)  # Simple scoring
        logger.info("[L6_AUDIT] Action at line 557")
        }

    def update_phase_status(self, mission_id: str, phase_name: str,
                           status: str, result: Dict = None):
        """
        Update the status of a mission phase.

        logger.info("[L6_AUDIT] Action at line 565")
        logger.info("[L6_AUDIT] Action at line 566")
        Args:
            mission_id: Mission identifier
            logger.info("[L6_AUDIT] Action at line 569")
            logger.info("[L6_AUDIT] Action at line 570")
            logger.info("[L6_AUDIT] Action at line 571")
            phase_name: Phase name
            status: New status
            logger.info("[L6_AUDIT] Action at line 574")
            logger.info("[L6_AUDIT] Action at line 575")
            logger.info("[L6_AUDIT] Action at line 576")
            logger.info("[L6_AUDIT] Action at line 577")
            result: Phase execution result
        """
        if mission_id not in self.active_missions:
            logger.info("[L6_AUDIT] Action at line 581")
            LOGGER.error(f"Mission not found: {mission_id}")
            return

        plan = self.active_missions[mission_id]
 logger.info("[L6_AUDIT] Action at line 586")

        # Find phase
        logger.info("[L6_AUDIT] Action at line 589")
        for phase in plan.phases:
            logger.info("[L6_AUDIT] Action at line 591")
            logger.info("[L6_AUDIT] Action at line 592")
            logger.info("[L6_AUDIT] Action at line 593")
            logger.info("[L6_AUDIT] Action at line 594")
            if phase.name == phase_name:
                # Store result in phase metadata
                logger.info("[L6_AUDIT] Action at line 597")
                if not hasattr(phase, 'results'):
                    logger.info("[L6_AUDIT] Action at line 599")
                    logger.info("[L6_AUDIT] Action at line 600")
                    phase.results = {}
                phase.results[status] = {
                    "timestamp": datetime.utcnow().isoformat(),
                    logger.info("[L6_AUDIT] Action at line 604")
                    "result": result or {}
                logger.info("[L6_AUDIT] Action at line 606")
                }
 logger.info("[L6_AUDIT] Action at line 608")
 logger.info("[L6_AUDIT] Action at line 609")

                LOGGER.info(f"Updated phase {phase_name} status to {status}")
                break

    def complete_mission(self, mission_id: str, status: MissionStatus):
        """
        Mark a mission as complete.

        Args:
            mission_id: Mission identifier
            status: Final mission status
        """
        if mission_id not in self.active_missions:
            return

        plan = self.active_missions[mission_id]
        plan.status = status

        # Move to history
        self.mission_history.append(plan.to_dict())
        del self.active_missions[mission_id]

        LOGGER.info(f"Mission {mission_id} completed with status {status.value}")

    def get_mission_plan(self, mission_id: str) -> Optional[MissionPlan]:
        """Get a mission plan by ID."""
        return self.active_missions.get(mission_id)

    def get_active_missions(self) -> List[MissionPlan]:
        """Get all active missions."""
        return list(self.active_missions.values())

    def get_next_phase(self, mission_id: str) -> Optional[MissionPhase]:
        """
        Get the next phase to execute for a mission.

        Args:
            mission_id: Mission identifier

        Returns:
            Next phase to execute, or None if complete
        """
        plan = self.active_missions.get(mission_id)
        if not plan:
            return None

        # Find first phase without results
        for phase in plan.phases:
            if not hasattr(phase, 'results'):
                return phase

        return None

    def get_mission_summary(self, mission_id: str) -> Dict:
        """Get summary of mission execution."""
        plan = self.active_missions.get(mission_id)
        if not plan:
            return {"error": "Mission not found"}

        completed_phases = sum(1 for p in plan.phases if hasattr(p, 'results'))
        total_phases = len(plan.phases)
        total_duration = sum(p.estimated_duration for p in plan.phases)

        return {
            "mission_id": plan.mission_id,
            "objective": plan.objective,
            "priority": plan.priority.value,
            "status": plan.status.value,
            "progress": f"{completed_phases}/{total_phases}",
            "progress_percent": (completed_phases / total_phases * 100) if total_phases > 0 else 0,
            "total_duration": total_duration,
            "risk_score": plan.risk_assessment.get("risk_score", 0)
        }


# Global instance
_strategic_planner: Optional[StrategicPlanner] = None


def get_strategic_planner() -> StrategicPlanner:
    """Get or create the global StrategicPlanner instance."""
    global _strategic_planner
    if _strategic_planner is None:
        _strategic_planner = StrategicPlanner()
    return _strategic_planner


def initialize_strategic_planner():
    """Initialize the StrategicPlanner system."""
    get_strategic_planner()
    LOGGER.info("StrategicPlanner system initialized")


# Convenience functions
def generate_mission_plan(objective: str, cycle_id: int,
                         priority: MissionPriority = MissionPriority.MEDIUM,
                         context: Dict = None) -> MissionPlan:
    """Generate a mission plan."""
    planner = get_strategic_planner()
    return planner.generate_plan(objective, cycle_id, priority, context)
