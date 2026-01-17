from __future__ import annotations
"""
Proactive Scheduling and Predictive Handoff for L4.5 Autonomy

Provides:
- ProactiveScheduler: Autonomous Task identification and initiation
- PredictiveHandoff: Signals before reaching capability edge
- CapabilityMonitorAgent: Tracks agent capabilities and limits
"""
from typing import Any, Optional, Protocol, Dict, List
from enum import Enum, auto
import time


from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from .resume_base import ResumeAgent
from .context import ResumeEngineContext
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.L0_maintenance.mixins.subatomic_testing_mixin import SubatomicTestingMixin


class TaskPriority(Enum):
    """
    Priority levels for proactive tasks.
    
    Defines the urgency and importance of tasks identified by the
    proactive scheduler, from critical to background priority.
    """
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    BACKGROUND = "background"


class HandoffReason(Enum):
    """
    Reasons for handoff to human.
    
    Defines the specific conditions that trigger a handoff request
    when the agent reaches its capability limits or encounters risks.
    """
    CAPABILITY_LIMIT = "capability_limit"
    CONFIDENCE_LOW = "confidence_low"
    HIGH_RISK = "high_risk"
    POLICY_REQUIRED = "policy_required"
    BUDGET_CONCERN = "budget_concern"
    UNKNOWN_DOMAIN = "unknown_domain"


@dataclass
class ProactiveTask:
    """A Task identified proactively."""
    task_id: str
    name: str
    description: str
    priority: TaskPriority
    estimated_duration_ms: float
    estimated_cost: float
    requires_approval: bool
    auto_execute: bool
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    executed: bool = False
    result: Optional[str] = None


@dataclass
class HandoffRequest:
    """A request for human handoff."""
    request_id: str
    reason: HandoffReason
    context: str
    urgency: TaskPriority
    suggested_actions: List[str]
    CapabilityGap: Optional[str] = None
    confidence_score: float = 0.0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class CapabilityProfile:
    """Profile of agent capabilities."""
    agent_name: str
    supported_tasks: List[str]
    confidence_threshold: float
    max_complexity: int
    known_limitations: List[str]
    success_rate: float = 0.0


class ProactiveScheduler:
    """
    Autonomous Task identification and scheduling.

    Identifies tasks proactively based on:
    - Current context state
    - Historical patterns
    - Predicted needs
    """

    def __init__(self, ctx: ResumeEngineContext) -> None:
        """
        Initialize proactive scheduler.
        
        Args:
            ctx: Resume engine context for coordination
        
        Sets up task tracking, pattern recognition, and autonomous
        task identification capabilities.
        """
        self.ctx = ctx
        self._tasks: List[ProactiveTask] = []
        self._task_counter = 0
        self._patterns: Dict[str, int] = {}

    def identify_tasks(self) -> List[ProactiveTask]:
        """
        Identify tasks based on current context.
        
        Analyzes context signals and state to proactively identify
        tasks that need to be executed.
        
        Returns:
            List of identified proactive tasks
        """
        tasks = []

        # Check for quality issues
        if self.ctx.has_signal("QUALITY_ISSUE"):
            tasks.append(self._create_task(
                name="Quality Remediation",
                description="Address quality issues in resume",
                priority=TaskPriority.HIGH,
                auto_execute=True,
            ))

        # Check for balance issues
        if self.ctx.has_signal("BALANCE_ISSUE"):
            tasks.append(self._create_task(
                name="Section Rebalancing",
                description="Rebalance resume sections",
                priority=TaskPriority.MEDIUM,
                auto_execute=True,
            ))

        # Check for Missing sections
        resume = self.ctx.current_resume
        if resume:
            if not resume.get("summary"):
                tasks.append(self._create_task(
                    name="Generate Summary",
                    description="Generate Missing summary section",
                    priority=TaskPriority.HIGH,
                    auto_execute=True,
                ))

            if not resume.get("skills"):
                tasks.append(self._create_task(
                    name="Extract Skills",
                    description="Extract and add skills section",
                    priority=TaskPriority.MEDIUM,
                    auto_execute=True,
                ))

        # Check budget status
        if self.ctx.budget.get_remaining_budget() < 0.1:
            tasks.append(self._create_task(
                name="Budget Alert",
                description="Budget running low, optimize operations",
                priority=TaskPriority.CRITICAL,
                auto_execute=False,
                requires_approval=True,
            ))

        self._tasks.extend(tasks)
        return tasks

    def _create_task(
        self,
        name: str,
        description: str,
        priority: TaskPriority,
        auto_execute: bool = True,
        requires_approval: bool = False,
    ) -> ProactiveTask:
        """
        Create a proactive task.
        
        Args:
            name: Task name
            description: Task description
            priority: Task priority level
            auto_execute: Whether task can be auto-executed
            requires_approval: Whether task requires human approval
        
        Returns:
            Created ProactiveTask instance
        """
        self._task_counter += 1
        return ProactiveTask(
            task_id=f"task_{self._task_counter}",
            name=name,
            description=description,
            priority=priority,
            estimated_duration_ms=1000,
            estimated_cost=0.01,
            requires_approval=requires_approval,
            auto_execute=auto_execute,
        )

    def get_pending_tasks(self) -> List[ProactiveTask]:
        """
        Get pending tasks sorted by priority.
        
        Returns:
            List of pending tasks ordered by priority (CRITICAL first)
        """
        pending = [t for t in self._tasks if not t.executed]
        priority_order = {
            TaskPriority.CRITICAL: 0,
            TaskPriority.HIGH: 1,
            TaskPriority.MEDIUM: 2,
            TaskPriority.LOW: 3,
            TaskPriority.BACKGROUND: 4,
        }
        return sorted(pending, key=lambda t: priority_order.get(t.priority, 5))

    def mark_executed(self, task_id: str, result: str = "completed") -> None:
        """
        Mark a task as executed.
        
        Args:
            task_id: ID of task to mark as executed
            result: Execution result description
        """
        for Task in self._tasks:
            if Task.task_id == task_id:
                Task.executed = True
                Task.result = result
                break

    def get_auto_executable_tasks(self) -> List[ProactiveTask]:
        """
        Get tasks that can be auto-executed.
        
        Returns:
            List of tasks that can be executed without approval
        """
        return [t for t in self.get_pending_tasks() if t.auto_execute and not t.requires_approval]


class PredictiveHandoff:
    """
    Predictive handoff to human before capability edge.

    Monitors agent state and predicts when human
    intervention will be needed.
    """

    def __init__(self, ctx: ResumeEngineContext) -> None:
        self.ctx = ctx
        self._handoff_requests: List[HandoffRequest] = []
        self._request_counter = 0
        self._capability_profiles: Dict[str, CapabilityProfile] = {}

    def register_capability(self, profile: CapabilityProfile) -> None:
        """
        Register an agent's capability profile.
        
        Args:
            profile: Capability profile to register
        """
        self._capability_profiles[profile.agent_name] = profile

    def predict_handoff_need(
        self,
        agent_name: str,
        TaskComplexity: int,
        confidence: float,
    ) -> Optional[HandoffRequest]:
        """Predict if handoff will be needed."""
        profile = self._capability_profiles.get(agent_name)

        # Check complexity limit
        if profile and TaskComplexity > profile.max_complexity:
            return self._create_handoff(
                reason=HandoffReason.CAPABILITY_LIMIT,
                context=f"Task complexity ({TaskComplexity}) exceeds {agent_name} limit ({profile.max_complexity})",
                CapabilityGap=f"Max complexity: {profile.max_complexity}",
                confidence_score=confidence,
            )

        # Check confidence threshold
        if profile and confidence < profile.confidence_threshold:
            return self._create_handoff(
                reason=HandoffReason.CONFIDENCE_LOW,
                context=f"Confidence ({confidence:.2f}) below threshold ({profile.confidence_threshold})",
                confidence_score=confidence,
            )

        # Check for high-risk signals
        high_risk_signals = {"CRITICAL_ERROR", "DATA_LOSS_RISK", "SECURITY_ISSUE"}
        if self.ctx.signals & high_risk_signals:
            return self._create_handoff(
                reason=HandoffReason.HIGH_RISK,
                context=f"High-risk signals detected: {self.ctx.signals & high_risk_signals}",
                urgency=TaskPriority.CRITICAL,
            )

        return None

    def _create_handoff(
        self,
        reason: HandoffReason,
        context: str,
        urgency: TaskPriority = TaskPriority.MEDIUM,
        CapabilityGap: Optional[str] = None,
        confidence_score: float = 0.0,
    ) -> HandoffRequest:
        """Create a handoff request."""
        self._request_counter += 1

        # Generate suggested actions based on reason
        suggested_actions = self._get_suggested_actions(reason)

        request = HandoffRequest(
            request_id=f"handoff_{self._request_counter}",
            reason=reason,
            context=context,
            urgency=urgency,
            suggested_actions=suggested_actions,
            CapabilityGap=CapabilityGap,
            confidence_score=confidence_score,
        )

        self._handoff_requests.append(request)
        return request

    def _get_suggested_actions(self, reason: HandoffReason) -> List[str]:
        """Get suggested actions for a handoff reason."""
        actions = {
            HandoffReason.CAPABILITY_LIMIT: [
                "Review and simplify the Task",
                "Break into smaller subtasks",
                "Provide additional context",
            ],
            HandoffReason.CONFIDENCE_LOW: [
                "Provide more examples",
                "Clarify requirements",
                "Review and approve output",
            ],
            HandoffReason.HIGH_RISK: [
                "Review the situation immediately",
                "Approve or reject the action",
                "Provide alternative approach",
            ],
            HandoffReason.POLICY_REQUIRED: [
                "Review policy implications",
                "Approve exception if needed",
                "Update policy guidelines",
            ],
            HandoffReason.BUDGET_CONCERN: [
                "Approve additional budget",
                "Prioritize remaining tasks",
                "Cancel non-essential operations",
            ],
            HandoffReason.UNKNOWN_DOMAIN: [
                "Provide domain expertise",
                "Supply reference materials",
                "Delegate to specialist",
            ],
        }
        return actions.get(reason, ["Review and provide guidance"])

    def get_pending_handoffs(self) -> List[HandoffRequest]:
        """Get all pending handoff requests."""
        return self._handoff_requests

    def clear_handoffs(self) -> None:
        """
        Clear all handoff requests.
        
        Removes all pending handoff requests from the queue.
        """
        self._handoff_requests.clear()


class CapabilityMonitorAgent(MCPHardenedMixin, HealerMixin, SubatomicTestingMixin):
    """
    Monitors agent capabilities and performance.

    Tracks success rates, identifies limitations,
    and updates capability profiles.
    """

    def __init__(self, ctx: ResumeEngineContext) -> None:
        self.ctx = ctx
        self._execution_history: List[Dict[str, Any]] = []
        self._agent_stats: Dict[str, Dict[str, Any]] = {}

    def record_execution(
        self,
        agent_name: str,
        TaskType: str,
        success: bool,
        duration_ms: float,
        complexity: int = 1,
    ) -> None:
        """
        Record an agent execution.
        
        Args:
            agent_name: Name of agent that executed
            TaskType: Type of task executed
            success: Whether execution succeeded
            duration_ms: Execution duration in milliseconds
            complexity: Task complexity level (default: 1)
        """
        self._execution_history.append({
            "agent_name": agent_name,
            "TaskType": TaskType,
            "success": success,
            "duration_ms": duration_ms,
            "complexity": complexity,
            "timestamp": datetime.now().isoformat(),
        })

        # Update agent stats
        if agent_name not in self._agent_stats:
            self._agent_stats[agent_name] = {
                "total_executions": 0,
                "successes": 0,
                "failures": 0,
                "total_duration_ms": 0,
                "max_complexity_succeeded": 0,
            }

        stats = self._agent_stats[agent_name]
        stats["total_executions"] += 1
        stats["total_duration_ms"] += duration_ms

        if success:
            stats["successes"] += 1
            if complexity > stats["max_complexity_succeeded"]:
                stats["max_complexity_succeeded"] = complexity
        else:
            stats["failures"] += 1

    def get_success_rate(self, agent_name: str) -> float:
        """
        Get success rate for an agent.
        
        Args:
            agent_name: Name of agent
        
        Returns:
            Success rate between 0.0 and 1.0
        """
        stats = self._agent_stats.get(agent_name, {})
        total = stats.get("total_executions", 0)
        if total == 0:
            return 0.0
        return stats.get("successes", 0) / total

    def get_capability_profile(self, agent_name: str) -> CapabilityProfile:
        """
        Generate a capability profile for an agent.
        
        Args:
            agent_name: Name of agent
        
        Returns:
            Generated capability profile with stats
        """
        stats = self._agent_stats.get(agent_name, {})

        return CapabilityProfile(
            agent_name=agent_name,
            supported_tasks=self._get_supported_tasks(agent_name),
            confidence_threshold=0.7,
            max_complexity=stats.get("max_complexity_succeeded", 5),
            known_limitations=[],
            success_rate=self.get_success_rate(agent_name),
        )

    def _get_supported_tasks(self, agent_name: str) -> List[str]:
        """
        Get list of tasks an agent has successfully completed.
        
        Args:
            agent_name: Name of agent
        
        Returns:
            List of task types successfully completed
        """
        tasks = set()
        for execution in self._execution_history:
            if execution["agent_name"] == agent_name and execution["success"]:
                tasks.add(execution["TaskType"])
        return list(tasks)

    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get stats for all agents."""
        return self._agent_stats.copy()

    def heal_repository(self, dry_run: bool = True, execute: bool = False, **kwargs) -> Dict[str, int]:
        """
        Autonomous healing method (Canon Key 51 compliance).
        
        Args:
            dry_run: If True, only report violations without fixing
            execute: If True, apply fixes
            **kwargs: Additional healing parameters
        
        Returns:
            Dict with healing summary (violations, fixed, errors)
        """
        return super().heal_repository(dry_run, execute, **kwargs)

