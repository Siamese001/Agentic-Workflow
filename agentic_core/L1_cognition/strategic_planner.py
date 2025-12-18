"""
StrategicPlanner - L1 Guardian for Mission Planning

Generates MissionPlan at the start of cycles.
Coordinates agent execution and resource allocation.
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any

LOGGER = logging.getLogger(__name__)

# Constants
FEW_SHOT_STRATEGIC = """
You are the StrategicPlanner, an expert in mission planning and coordination.

Your role is to:
1. Generate comprehensive mission plans
2. Coordinate agent execution order
3. Allocate resources efficiently
4. Anticipate potential issues

Mission Plan Structure:
```python
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
}
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
            "resources": self.resources,
            "parallel": self.parallel,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries
        }


@dataclass
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
            "cycle_id": self.cycle_id,
            "priority": self.priority.value,
            "objective": self.objective,
            "phases": [p.to_dict() for p in self.phases],
            "risk_assessment": self.risk_assessment,
            "created_at": self.created_at.isoformat(),
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
        
        # Parse phases
        for phase_data in data.get("phases", []):
            phase = MissionPhase(
                name=phase_data["name"],
                agents=phase_data["agents"],
                dependencies=phase_data.get("dependencies", []),
                estimated_duration=phase_data.get("estimated_duration", 300),
                resources=phase_data.get("resources", []),
                parallel=phase_data.get("parallel", False),
                retry_count=phase_data.get("retry_count", 0),
                max_retries=phase_data.get("max_retries", 3)
            )
            plan.phases.append(phase)
        
        return plan


class StrategicPlanner:
    """
    Plans and coordinates mission execution.
    
    Features:
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
                "purpose": "Docstring consistency",
                "resources": ["cpu", "llm"],
                "phase": "validation"
            },
            "RedSentinel": {
                "purpose": "Fuzz testing",
                "resources": ["cpu"],
                "phase": "testing"
            },
            "TheCartographer": {
                "purpose": "Semantic mapping",
                "resources": ["cpu", "llm"],
                "phase": "analysis"
            },
            "Historian": {
                "purpose": "Memory optimization",
                "resources": ["disk"],
                "phase": "optimization"
            }
        }
    
    def generate_plan(self, objective: str, cycle_id: int, 
                     priority: MissionPriority = MissionPriority.MEDIUM,
                     context: Dict = None) -> MissionPlan:
        """
        Generate a mission plan for the given objective.
        
        Args:
            objective: Mission objective
            cycle_id: Cycle identifier
            priority: Mission priority
            context: Additional context for planning
            
        Returns:
            Generated mission plan
        """
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
        """Generate mission phases based on objective."""
        phases = []
        
        # Phase 1: Reconnaissance
        phases.append(MissionPhase(
            name="reconnaissance",
            agents=["Historian", "TheCartographer"],
            dependencies=[],
            estimated_duration=120,
            resources=["cpu", "disk"],
            parallel=True
        ))
        
        # Phase 2: Validation
        phases.append(MissionPhase(
            name="validation",
            agents=["ArchitectureGovernor", "SafetyInspector", "TruthKeeper"],
            dependencies=["reconnaissance"],
            estimated_duration=300,
            resources=["cpu", "llm", "file_access"],
            parallel=True
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
            resources=["git", "network"]
        ))
        
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
            if count > 3:  # Too many phases using same resource
                risks.append(f"Resource contention for {resource}")
                mitigations.append(f"Stagger phases using {resource}")
        
        # Check for long-running phases
        for phase in plan.phases:
            if phase.estimated_duration > 600:  # > 10 minutes
                risks.append(f"Long running phase: {phase.name}")
                mitigations.append(f"Add progress monitoring for {phase.name}")
        
        # Check agent dependencies
        all_agents = set()
        for phase in plan.phases:
            all_agents.update(phase.agents)
        
        if len(all_agents) > 8:
            risks.append("High agent coordination complexity")
            mitigations.append("Consider parallel execution where possible")
        
        return {
            "risks": risks,
            "mitigations": mitigations,
            "risk_score": min(len(risks) * 10, 100)  # Simple scoring
        }
    
    def update_phase_status(self, mission_id: str, phase_name: str, 
                           status: str, result: Dict = None):
        """
        Update the status of a mission phase.
        
        Args:
            mission_id: Mission identifier
            phase_name: Phase name
            status: New status
            result: Phase execution result
        """
        if mission_id not in self.active_missions:
            LOGGER.error(f"Mission not found: {mission_id}")
            return
        
        plan = self.active_missions[mission_id]
        
        # Find phase
        for phase in plan.phases:
            if phase.name == phase_name:
                # Store result in phase metadata
                if not hasattr(phase, 'results'):
                    phase.results = {}
                phase.results[status] = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "result": result or {}
                }
                
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
    planner = get_strategic_planner()
    LOGGER.info("StrategicPlanner system initialized")


# Convenience functions
def generate_mission_plan(objective: str, cycle_id: int, 
                         priority: MissionPriority = MissionPriority.MEDIUM,
                         context: Dict = None) -> MissionPlan:
    """Generate a mission plan."""
    planner = get_strategic_planner()
    return planner.generate_plan(objective, cycle_id, priority, context)
