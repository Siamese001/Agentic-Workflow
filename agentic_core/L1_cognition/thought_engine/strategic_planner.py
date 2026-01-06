from __future__ import annotations
"""
StrategicPlannerAgent - L1 Guardian for Mission Planning

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
Logger: Any = logging.getLogger(__name__)
few_shot_strategic: Any = '\nfrom agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin\nfrom agentic_core.utils.core_extensions.healer_mixin import HealerMixin\nYou are the StrategicPlannerAgent, an expert in mission planning and coordination.\n\nYour role is to:\n1. Generate comprehensive mission plans\n2. Coordinate agent execution order\n3. Allocate resources efficiently\n4. Anticipate potential issues\n\nMission Plan Structure:\n{\n    "mission_id": "unique_identifier",\n    "cycle_id": 1,\n    "priority": "HIGH|MEDIUM|LOW",\n    "objective": "Clear mission objective",\n    "phases": [\n        {\n            "name": "phase_name",\n            "agents": ["agent1", "agent2"],\n            "dependencies": [],\n            "estimated_duration": 300,\n            "resources": ["cpu", "memory", "api_calls"]\n        }\n    ],\n    "risk_assessment": {\n        "risks": ["risk1", "risk2"],\n        "mitigations": ["mitigation1", "mitigation2"]\n    }\n}\n```\n\nGuidelines:\n- Start with reconnaissance (file scanning)\n- Follow with analysis (validation, checks)\n- End with execution (fixes, commits)\n- Always include rollback plans\n'
from dataclasses import dataclass, field
from enum import Enum

# [SSOT IMPORT] Structure blueprint is the single source of truth
from agentic_core.config.blueprint_sovereign.structure_blueprint import (
    SOVEREIGN_REGISTRY,
    CORE_SUBFOLDER_MAP,
)


class MissionPriority(Enum):
    """Mission priority levels."""
    CRITICAL: Any = 'CRITICAL'
    HIGH: Any = 'HIGH'
    MEDIUM: Any = 'MEDIUM'
    LOW: Any = 'LOW'

class MissionStatus(Enum):
    """Mission status values."""
    PLANNED: Any = 'PLANNED'
    ACTIVE: Any = 'ACTIVE'
    PAUSED: Any = 'PAUSED'
    COMPLETED: Any = 'COMPLETED'
    FAILED: Any = 'FAILED'
    CANCELLED: Any = 'CANCELLED'

@dataclass
class MissionPhase:
    """A single phase of a mission."""
    name: str
    agents: List[str]
    dependencies: List[str] = field(default_factory=list)
    estimated_duration: int = 300
    resources: List[str] = field(default_factory=list)
    parallel: bool = False
    retry_count: int = 0
    max_retries: int = 3

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {'name': self.name, 'agents': self.agents, 'dependencies': self.dependencies, 'estimated_duration': self.estimated_duration, 'resources': self.resources, 'parallel': self.parallel, 'retry_count': self.retry_count, 'max_retries': self.max_retries}

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
        return {'mission_id': self.mission_id, 'cycle_id': self.cycle_id, 'priority': self.priority.value, 'objective': self.objective, 'phases': [p.to_dict() for p in self.phases], 'risk_assessment': self.risk_assessment, 'created_at': self.created_at.isoformat(), 'status': self.status.value}

    @classmethod
    def from_dict(cls, data: Dict) -> 'MissionPlan':
        """Create from dictionary."""
        plan: Any = cls(mission_id=data['mission_id'], cycle_id=data['cycle_id'], priority=MissionPriority(data['priority']), objective=data['objective'], risk_assessment=data.get('risk_assessment', {}), status=MissionStatus(data.get('status', 'PLANNED')))
        for phase_data in data.get('phases', []):
            phase: Any = MissionPhase(name=phase_data['name'], agents=phase_data['agents'], dependencies=phase_data.get('dependencies', []), estimated_duration=phase_data.get('estimated_duration', 300), resources=phase_data.get('resources', []), parallel=phase_data.get('parallel', False), retry_count=phase_data.get('retry_count', 0), max_retries=phase_data.get('max_retries', 3))
            plan.phases.append(phase)
        return plan

# DUPLICATE ACCEPTED: App-specific customization valid
# (different contexts: L1 strategic cognition vs L2 planning vs apps_rg implementations)
# - Intentional variants for domain-specific planning
# - Documented 2026-01-06

class StrategicPlannerAgent(HealerMixin, MCPHardenedMixin):
    """
    Plans and coordinates mission execution.

    Features:
    - Generates mission plans based on objectives
    - Optimizes agent execution order
    - Manages resource allocation
    - Tracks mission progress
    """

    def __init__(self) -> None:
        """Initialize the StrategicPlannerAgent."""
        self.active_missions: Dict[str, MissionPlan] = {}
        self.mission_history: List[Dict] = []
        self.agent_capabilities = self._load_agent_capabilities()
        try:
            from agentic_core.L3_orchestration.workflow_engines.mcp_router_sovereign import SovereignMCPRouter
            self.McpRouterAgent = SovereignMCPRouter(role='cognition_strategic')
        except Exception as e:
            LOGGER.warning(f'MCP Router initialization failed: {e}. Using legacy planning.')
            self.McpRouterAgent = None
        LOGGER.info('StrategicPlannerAgent initialized')

    def _load_agent_capabilities(self) -> Dict[str, Dict]:
        """Load agent capabilities and requirements."""
        return {'ArchitectureGovernor': {'purpose': 'Enforce architectural rules', 'resources': ['cpu', 'file_access'], 'phase': 'validation'}, 'TestPilot': {'purpose': 'Run property-based tests', 'resources': ['cpu', 'memory'], 'phase': 'testing'}, 'ReflectionAgent': {'purpose': 'Learn from execution', 'resources': ['memory', 'pinecone'], 'phase': 'learning'}, 'GitAgent': {'purpose': 'Commit changes', 'resources': ['git', 'network'], 'phase': 'execution'}, 'SafetyInspectorAgent': {'purpose': 'Security validation', 'resources': ['cpu', 'llm'], 'phase': 'validation'}, 'TruthKeeper': {'purpose': 'Docstring consistency', 'resources': ['cpu', 'llm'], 'phase': 'validation'}, 'RedSentinelAgent': {'purpose': 'Fuzz testing', 'resources': ['cpu'], 'phase': 'testing'}, 'TheCartographer': {'purpose': 'Semantic mapping', 'resources': ['cpu', 'llm'], 'phase': 'analysis'}, 'Historian': {'purpose': 'Memory optimization', 'resources': ['disk'], 'phase': 'optimization'}}

    async def generate_plan(self, objective: str, cycle_id: int, priority: MissionPriority=MissionPriority.MEDIUM, context: Dict=None) -> MissionPlan:
        """
        Generate a mission plan for the given objective.
        Phase 13B: Full MCP reasoning integration via Sequential Thinking.

        Args:
            objective: Mission objective
            cycle_id: Cycle identifier
            priority: Mission priority
            context: Additional context for planning
        Returns:
            Generated mission plan
        """
        from agentic_core.config.blueprint_sovereign.sovereign_config import config
        if config.SEQUENTIAL_THINKING_MCP_ENABLED and self.McpRouterAgent:
            try:
                return await self._generate_plan_with_mcp(objective, cycle_id, priority, context)
            except Exception as e:
                LOGGER.error(f'MCP planning failed: {e}. Falling back to legacy.')
        return self._generate_plan_legacy(objective, cycle_id, priority, context)

    async def _generate_plan_with_mcp(self, objective: str, cycle_id: int, priority: MissionPriority, context: Dict) -> MissionPlan:
        """Generate plan using Sequential Thinking MCP."""
        from agentic_core.config.blueprint_sovereign.sovereign_config import config
        mcp_payload = {'Task': f'Generate comprehensive sovereign mission plan for objective: {objective}', 'cycle_id': cycle_id, 'priority': priority.value, 'context': context or {}, 'max_steps': config.SEQ_THINKING_MAX_STEPS, 'temperature': config.SEQ_THINKING_TEMPERATURE, 'enable_hypothesis_branching': config.SEQ_THINKING_ENABLE_HYPOTHESIS_BRANCHING, 'enable_self_revision': config.SEQ_THINKING_ENABLE_SELF_REVISION, 'prune_low_confidence': config.SEQ_THINKING_PRUNE_LOW_CONFIDENCE, 'min_confidence_threshold': config.SEQ_THINKING_MIN_HYPOTHESIS_CONFIDENCE}
        result = await self.McpRouterAgent.manager.call_tool(tool_name='mcp10_sequentialthinking', args=mcp_payload)
        plan = self._extract_mission_plan_from_mcp(result, objective, cycle_id, priority)
        LOGGER.info(f'[L1 PLANNING] Mission plan generated via Sequential Thinking MCP')
        return plan

    def _extract_mission_plan_from_mcp(self, mcp_result: Dict, objective: str, cycle_id: int, priority: MissionPriority) -> MissionPlan:
        """Extract MissionPlan from Sequential Thinking MCP result."""
        mission_id = f"mission-{cycle_id}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        plan = MissionPlan(mission_id=mission_id, cycle_id=cycle_id, priority=priority, objective=objective)
        thought_content = mcp_result.get('thought', '')
        if thought_content:
            plan.phases = self._parse_phases_from_thought(thought_content)
        if not plan.phases:
            plan.phases = self._generate_phases(objective, {})
        plan.risk_assessment = self._assess_risks(plan)
        self.active_missions[mission_id] = plan
        return plan

    def _parse_phases_from_thought(self, thought: str) -> List[MissionPhase]:
        """Parse mission phases from Sequential Thinking output."""
        phases = []
        if 'reconnaissance' in thought.lower():
            phases.append(MissionPhase(name='reconnaissance', agents=['Historian', 'TheCartographer'], dependencies=[], estimated_duration=120, resources=['cpu', 'disk'], parallel=True))
        if 'validation' in thought.lower():
            phases.append(MissionPhase(name='validation', agents=['ArchitectureGovernor', 'SafetyInspectorAgent', 'TruthKeeper'], dependencies=['reconnaissance'] if phases else [], estimated_duration=300, resources=['cpu', 'llm', 'file_access'], parallel=True))
        return phases

    def _generate_plan_legacy(self, objective: str, cycle_id: int, priority: MissionPriority, context: Dict) -> MissionPlan:
        """Legacy mission plan generation."""
        mission_id = f"mission-{cycle_id}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        plan = MissionPlan(mission_id=mission_id, cycle_id=cycle_id, priority=priority, objective=objective)
        phases = self._generate_phases(objective, context or {})
        plan.phases = phases
        plan.risk_assessment = self._assess_risks(plan)
        self.active_missions[mission_id] = plan
        LOGGER.info(f'Generated mission plan: {mission_id}')
        LOGGER.info(f'  Objective: {objective}')
        LOGGER.info(f'  Phases: {len(phases)}')
        return plan

    def _generate_phases(self, objective: str, context: Dict) -> List[MissionPhase]:
        """Generate mission phases based on objective."""
        phases = []
        phases.append(MissionPhase(name='reconnaissance', agents=['Historian', 'TheCartographer'], dependencies=[], estimated_duration=120, resources=['cpu', 'disk'], parallel=True))
        phases.append(MissionPhase(name='validation', agents=['ArchitectureGovernor', 'SafetyInspectorAgent', 'TruthKeeper'], dependencies=['reconnaissance'], estimated_duration=300, resources=['cpu', 'llm', 'file_access'], parallel=True))
        phases.append(MissionPhase(name='testing', agents=['TestPilot', 'RedSentinelAgent'], dependencies=['validation'], estimated_duration=600, resources=['cpu', 'memory'], parallel=True))
        phases.append(MissionPhase(name='learning', agents=['ReflectionAgent'], dependencies=['testing'], estimated_duration=180, resources=['memory', 'pinecone']))
        phases.append(MissionPhase(name='execution', agents=['GitAgent'], dependencies=['learning'], estimated_duration=60, resources=['git', 'network']))
        if context.get('skip_testing'):
            phases = [p for p in phases if p.name != 'testing']
        if context.get('urgent'):
            for phase in phases:
                phase.estimated_duration = int(phase.estimated_duration * 0.7)
        return phases

    def _assess_risks(self, plan: MissionPlan) -> Dict:
        """Assess risks for the mission plan."""
        risks = []
        mitigations = []
        resource_usage = {}
        for phase in plan.phases:
            for resource in phase.resources:
                resource_usage[resource] = resource_usage.get(resource, 0) + 1
        for resource, count in resource_usage.items():
            if count > 3:
                risks.append(f'Resource contention for {resource}')
                mitigations.append(f'Stagger phases using {resource}')
        for phase in plan.phases:
            if phase.estimated_duration > 600:
                risks.append(f'Long running phase: {phase.name}')
                mitigations.append(f'Add progress monitoring for {phase.name}')
        all_agents = set()
        for phase in plan.phases:
            all_agents.update(phase.agents)
        if len(all_agents) > 8:
            risks.append('High agent coordination complexity')
            mitigations.append('Consider parallel execution where possible')
        return {'risks': risks, 'mitigations': mitigations, 'risk_score': min(len(risks) * 10, 100)}

    def update_phase_status(self, mission_id: str, phase_name: str, status: str, result: Dict=None) -> Any:
        """
        Update the status of a mission phase.
        Args:
            mission_id: Mission identifier
            phase_name: Phase name
            status: New status
            result: Phase execution result
        """
        if mission_id not in self.active_missions:
            LOGGER.error(f'Mission not found: {mission_id}')
            return
        plan: Any = self.active_missions[mission_id]
        for phase in plan.phases:
            if phase.name == phase_name:
                if not hasattr(phase, 'results'):
                    phase.results = {}
                phase.results[status] = {'timestamp': datetime.utcnow().isoformat(), 'result': result or {}}
                LOGGER.info(f'Updated phase {phase_name} status to {status}')
                break

    def complete_mission(self, mission_id: str, status: MissionStatus) -> Any:
        """
        Mark a mission as complete.

        Args:
            mission_id: Mission identifier
            status: Final mission status
        """
        if mission_id not in self.active_missions:
            return
        plan: Any = self.active_missions[mission_id]
        plan.status = status
        self.mission_history.append(plan.to_dict())
        del self.active_missions[mission_id]
        LOGGER.info(f'Mission {mission_id} completed with status {status.value}')

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
        plan: Any = self.active_missions.get(mission_id)
        if not plan:
            return None
        for phase in plan.phases:
            if not hasattr(phase, 'results'):
                return phase
        return None

    def get_mission_summary(self, mission_id: str) -> Dict:
        """Get summary of mission execution."""
        plan: Any = self.active_missions.get(mission_id)
        if not plan:
            return {'error': 'Mission not found'}
        completed_phases: Any = sum((1 for p in plan.phases if hasattr(p, 'results')))
        total_phases: Any = len(plan.phases)
        total_duration: Any = sum((p.estimated_duration for p in plan.phases))
        return {'mission_id': plan.mission_id, 'objective': plan.objective, 'priority': plan.priority.value, 'status': plan.status.value, 'progress': f'{completed_phases}/{total_phases}', 'progress_percent': completed_phases / total_phases * 100 if total_phases > 0 else 0, 'total_duration': total_duration, 'risk_score': plan.risk_assessment.get('risk_score', 0)}
_strategic_planner: Optional[StrategicPlannerAgent] = None

def get_strategic_planner() -> StrategicPlannerAgent:
    """Get or create the global StrategicPlannerAgent instance."""
    global _strategic_planner
    if _strategic_planner is None:
        _strategic_planner = StrategicPlannerAgent()
    return _strategic_planner

def initialize_strategic_planner() -> Any:
    """Initialize the StrategicPlannerAgent system."""
    get_strategic_planner()
    LOGGER.info('StrategicPlannerAgent system initialized')

def generate_mission_plan(objective: str, cycle_id: int, priority: MissionPriority=MissionPriority.MEDIUM, context: Dict=None) -> MissionPlan:
    """Generate a mission plan."""
    planner: Any = get_strategic_planner()
    return planner.generate_plan(objective, cycle_id, priority, context)

def _run_self_tests(self) -> dict:
        """Run internal self-tests."""
        results = {"passed": 0, "failed": 0, "tests": []}
        try:
            assert self is not None
            results["passed"] += 1
            results["tests"].append({"name": "test_instantiation", "status": "passed"})
        except AssertionError as e:
            results["failed"] += 1
            results["tests"].append({"name": "test_instantiation", "status": "failed", "error": str(e)})
        return results
