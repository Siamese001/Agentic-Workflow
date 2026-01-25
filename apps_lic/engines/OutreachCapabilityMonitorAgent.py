"""LEGACY FILE - Moved to legacy during Terminal Alignment Command
This file has fundamental architectural issues that require complete rewrite.
Status: DEPRECATED - Do not use in production
"""

# LEGACY CODE BELOW - COMMENTED OUT
# from enum import Enum
# from dataclasses import dataclass, field
# from agentic_core.base_agents.subatomic_testing_mixin import SubatomicTestingMixin
# """
# Proactive Scheduling and Predictive Handoff for Outreach Engine L4.5 Autonomy

# Provides:
# - OutreachProactiveScheduler: Autonomous Task identification for campaigns
# - OutreachPredictiveHandoff: Signals before reaching capability edge
# - OutreachCapabilityMonitorAgent: Tracks agent capabilities and limits
# """

# from datetime import datetime

# from .context import OutreachEngineContext


# class OutreachTaskPriority(Enum):
#     """
#     Priority levels for proactive outreach tasks.

#     Defines the urgency and importance of tasks identified by the
#     proactive scheduler for outreach campaigns.
#     """

#     CRITICAL = "critical"
#     HIGH = "high"
#     MEDIUM = "medium"
#     LOW = "low"
#     BACKGROUND = "background"


# class OutreachHandoffReason(Enum):
#     """
#     Reasons for handoff to human in outreach.

#     Defines the specific conditions that trigger a handoff request
#     when the agent reaches capability limits or encounters compliance issues.
#     """

#     CAPABILITY_LIMIT = "capability_limit"
#     CONFIDENCE_LOW = "confidence_low"
#     HIGH_RISK = "high_risk"
#     COMPLIANCE_REQUIRED = "compliance_required"
#     BUDGET_CONCERN = "budget_concern"
#     SENSITIVE_CONTACT = "sensitive_contact"


# @dataclass
# class OutreachProactiveTask:
#     """A proactive outreach Task."""

#     task_id: str
#     name: str
#     description: str
#     priority: OutreachTaskPriority
#     estimated_duration_ms: float
#     estimated_cost: float
#     requires_approval: bool
#     auto_execute: bool
#     created_at: str = field(default_factory=lambda: datetime.now().isoformat())
#     executed: bool = False
#     result: str | None = None


# @dataclass
# class OutreachHandoffRequest:
#     """A request for human handoff in outreach."""

#     request_id: str
#     reason: OutreachHandoffReason
#     context: str
#     urgency: OutreachTaskPriority
#     suggested_actions: list[str]
#     CapabilityGap: str | None = None
#     confidence_score: float = 0.0
#     created_at: str = field(default_factory=lambda: datetime.now().isoformat())


# @dataclass
# class OutreachCapabilityProfile:
#     """Profile of outreach agent capabilities."""

#     agent_name: str
#     supported_tasks: list[str]
#     confidence_threshold: float
#     max_leads_per_batch: int
#     known_limitations: list[str]
#     success_rate: float = 0.0


# class OutreachProactiveScheduler:
#     """
#     Autonomous Task identification for outreach campaigns.

#     Identifies tasks proactively based on:
#     - Campaign state
#     - Lead quality
#     - Message compliance
#     - Historical patterns
#     """

#     def __init__(self, ctx: OutreachEngineContext) -> None:
#         """
#         Initialize outreach proactive scheduler.

#         Args:
#             ctx: Outreach engine context for coordination

#         Sets up task tracking and autonomous task identification
#         for outreach campaigns.
#         """
#         self.ctx = ctx
#         self._tasks: list[OutreachProactiveTask] = []
#         self._task_counter = 0

#     def identify_tasks(self) -> list[OutreachProactiveTask]:
#         """Identify tasks based on current context."""
#         tasks = []

#         # Check for lead quality issues
#         if self.ctx.has_signal("LEAD_QUALITY_ISSUE"):
#             tasks.append(
#                 self._create_task(
#                     name="Lead Quality Remediation",
#                     description="Address lead quality issues",
#                     priority=OutreachTaskPriority.HIGH,
#                     auto_execute=True,
#                 )
#             )

#         # Check for compliance issues
#         if self.ctx.has_signal("COMPLIANCE_ISSUE"):
#             tasks.append(
#                 self._create_task(
#                     name="Compliance Review",
#                     description="Review and fix compliance issues",
#                     priority=OutreachTaskPriority.CRITICAL,
#                     auto_execute=False,
#                     requires_approval=True,
#                 )
#             )

#         # Check for deliverability issues
#         if self.ctx.has_signal("DELIVERABILITY_ISSUE"):
#             tasks.append(
#                 self._create_task(
#                     name="Deliverability Optimization",
#                     description="Optimize message deliverability",
#                     priority=OutreachTaskPriority.HIGH,
#                     auto_execute=True,
#                 )
#             )

#         # Check campaign state
#         campaign = self.ctx.current_campaign
#         if campaign:
#             if not campaign.get("schedule"):
#                 tasks.append(
#                     self._create_task(
#                         name="Add Schedule",
#                         description="Add send schedule to campaign",
#                         priority=OutreachTaskPriority.MEDIUM,
#                         auto_execute=True,
#                     )
#                 )

#             if not campaign.get("tracking"):
#                 tasks.append(
#                     self._create_task(
#                         name="Enable Tracking",
#                         description="Enable campaign tracking",
#                         priority=OutreachTaskPriority.LOW,
#                         auto_execute=True,
#                     )
#                 )

#         # Check lead count
#         if len(self.ctx.leads) > 100 and not self.ctx.current_campaign.get("segmentation"):
#             tasks.append(
#                 self._create_task(
#                     name="Lead Segmentation",
#                     description="Segment large lead list",
#                     priority=OutreachTaskPriority.MEDIUM,
#                     auto_execute=True,
#                 )
#             )

#         # Check budget
#         if self.ctx.budget.get_remaining() < 0.1:
#             tasks.append(
#                 self._create_task(
#                     name="Budget Alert",
#                     description="Budget running low",
#                     priority=OutreachTaskPriority.CRITICAL,
#                     auto_execute=False,
#                     requires_approval=True,
#                 )
#             )

#         self._tasks.extend(tasks)
#         return tasks

#     def _create_task(
#         self,
#         name: str,
#         description: str,
#         priority: OutreachTaskPriority,
#         auto_execute: bool = True,
#         requires_approval: bool = False,
#     ) -> OutreachProactiveTask:
#         """Create a proactive Task."""
#         self._task_counter += 1
#         return OutreachProactiveTask(
#             task_id=f"outreach_task_{self._task_counter}",
#             name=name,
#             description=description,
#             priority=priority,
#             estimated_duration_ms=500,
#             estimated_cost=0.005,
#             requires_approval=requires_approval,
#             auto_execute=auto_execute,
#         )

#     def get_pending_tasks(self) -> list[OutreachProactiveTask]:
#         """Get pending tasks sorted by priority."""
#         pending = [t for t in self._tasks if not t.executed]
#         priority_order = {
#             OutreachTaskPriority.CRITICAL: 0,
#             OutreachTaskPriority.HIGH: 1,
#             OutreachTaskPriority.MEDIUM: 2,
#             OutreachTaskPriority.LOW: 3,
#             OutreachTaskPriority.BACKGROUND: 4,
#         }
#         return sorted(pending, key=lambda t: priority_order.get(t.priority, 5))

#     def mark_executed(self, task_id: str, result: str = "completed") -> Any:
#         """Mark a Task as executed."""
#         for Task in self._tasks:
#             if Task.task_id == task_id:
#                 Task.executed = True
#                 Task.result = result
#                 break

#     def get_auto_executable_tasks(self) -> list[OutreachProactiveTask]:
#         """Get tasks that can be auto-executed."""
#         return [t for t in self.get_pending_tasks() if t.auto_execute and not t.requires_approval]


# class OutreachPredictiveHandoff:
#     """
#     Predictive handoff for outreach operations.

#     Monitors agent state and predicts when human
#     intervention will be needed.
#     """

#     def __init__(self, ctx: OutreachEngineContext) -> None:
#         self.ctx = ctx
#         self._handoff_requests: list[OutreachHandoffRequest] = []
#         self._request_counter = 0
#         self._capability_profiles: dict[str, OutreachCapabilityProfile] = {}

#     def register_capability(self, profile: OutreachCapabilityProfile) -> Any:
#         """Register an agent's capability profile."""
#         self._capability_profiles[profile.agent_name] = profile

#     def predict_handoff_need(
#         self,
#         agent_name: str,
#         lead_count: int,
#         confidence: float,
#     ) -> OutreachHandoffRequest | None:
#         """Predict if handoff will be needed."""
#         profile = self._capability_profiles.get(agent_name)

#         # Check lead count limit
#         if profile and lead_count > profile.max_leads_per_batch:
#             return self._create_handoff(
#                 reason=OutreachHandoffReason.CAPABILITY_LIMIT,
#                 context=f"Lead count ({lead_count}) exceeds batch limit ({profile.max_leads_per_batch})",
#                 CapabilityGap=f"Max leads: {profile.max_leads_per_batch}",
#                 confidence_score=confidence,
#             )

#         # Check confidence threshold
#         if profile and confidence < profile.confidence_threshold:
#             return self._create_handoff(
#                 reason=OutreachHandoffReason.CONFIDENCE_LOW,
#                 context=f"Confidence ({confidence:.2f}) below threshold ({profile.confidence_threshold})",
#                 confidence_score=confidence,
#             )

#         # Check for compliance signals
#         if self.ctx.has_signal("COMPLIANCE_ISSUE"):
#             return self._create_handoff(
#                 reason=OutreachHandoffReason.COMPLIANCE_REQUIRED,
#                 context="Compliance review required before sending",
#                 urgency=OutreachTaskPriority.CRITICAL,
#             )

#         # Check for sensitive contacts
#         sensitive_titles = ["CEO", "CFO", "CTO", "Board", "Director"]
#         for contact in self.ctx.contacts:
#             title = contact.get("title", "")
#             if any(s in title for s in sensitive_titles):
#                 return self._create_handoff(
#                     reason=OutreachHandoffReason.SENSITIVE_CONTACT,
#                     context=f"Sensitive contact detected: {title}",
#                     urgency=OutreachTaskPriority.HIGH,
#                 )

#         return None

#     def _create_handoff(
#         self,
#         reason: OutreachHandoffReason,
#         context: str,
#         urgency: OutreachTaskPriority = OutreachTaskPriority.MEDIUM,
#         CapabilityGap: str | None = None,
#         confidence_score: float = 0.0,
#     ) -> OutreachHandoffRequest:
#         """Create a handoff request."""
#         self._request_counter += 1

#         suggested_actions = self._get_suggested_actions(reason)

#         request = OutreachHandoffRequest(
#             request_id=f"outreach_handoff_{self._request_counter}",
#             reason=reason,
#             context=context,
#             urgency=urgency,
#             suggested_actions=suggested_actions,
#             CapabilityGap=CapabilityGap,
#             confidence_score=confidence_score,
#         )

#         self._handoff_requests.append(request)
#         return request

#     def _get_suggested_actions(self, reason: OutreachHandoffReason) -> list[str]:
#         """Get suggested actions for a handoff reason."""
#         actions = {
#             OutreachHandoffReason.CAPABILITY_LIMIT: [
#                 "Split into smaller batches",
#                 "Prioritize high-value leads",
#                 "Approve batch processing",
#             ],
#             OutreachHandoffReason.CONFIDENCE_LOW: [
#                 "Review message templates",
#                 "Provide more context",
#                 "Approve with modifications",
#             ],
#             OutreachHandoffReason.HIGH_RISK: [
#                 "Review immediately",
#                 "Approve or reject",
#                 "Provide alternative approach",
#             ],
#             OutreachHandoffReason.COMPLIANCE_REQUIRED: [
#                 "Review compliance issues",
#                 "Update message content",
#                 "Approve after review",
#             ],
#             OutreachHandoffReason.BUDGET_CONCERN: [
#                 "Approve additional budget",
#                 "Reduce campaign scope",
#                 "Prioritize leads",
#             ],
#             OutreachHandoffReason.SENSITIVE_CONTACT: [
#                 "Review personalized message",
#                 "Approve outreach",
#                 "Delegate to senior team member",
#             ],
#         }
#         return actions.get(reason, ["Review and provide guidance"])

#     def get_pending_handoffs(self) -> list[OutreachHandoffRequest]:
#         """Get all pending handoff requests."""
#         return self._handoff_requests

#     def clear_handoffs(self) -> Any:
#         """Clear all handoff requests."""
#         self._handoff_requests.clear()


# class OutreachCapabilityMonitorAgent(SovereignBaseAgent):
#     """
#     Monitors outreach agent capabilities and performance.
#     """

#     def __init__(self, ctx: OutreachEngineContext) -> None:
#         self.ctx = ctx
#         self._execution_history: list[dict[str, Any]] = []
#         self._agent_stats: dict[str, dict[str, Any]] = {}

#     def record_execution(
#         self,
#         agent_name: str,
#         TaskType: str,
#         success: bool,
#         duration_ms: float,
#         leads_processed: int = 0,
#     ) -> Any:
#         """Record an agent execution."""
#         self._execution_history.append(
#             {
#                 "agent_name": agent_name,
#                 "TaskType": TaskType,
#                 "success": success,
#                 "duration_ms": duration_ms,
#                 "leads_processed": leads_processed,
#                 "timestamp": datetime.now().isoformat(),
#             }
#         )

#         if agent_name not in self._agent_stats:
#             self._agent_stats[agent_name] = {
#                 "total_executions": 0,
#                 "successes": 0,
#                 "failures": 0,
#                 "total_leads_processed": 0,
#                 "total_duration_ms": 0,
#             }

#         stats = self._agent_stats[agent_name]
#         stats["total_executions"] += 1
#         stats["total_duration_ms"] += duration_ms
#         stats["total_leads_processed"] += leads_processed

#         if success:
#             stats["successes"] += 1
#         else:
#             stats["failures"] += 1

#     def get_success_rate(self, agent_name: str) -> float:
#         """Get success rate for an agent."""
#         stats = self._agent_stats.get(agent_name, {})
#         total = stats.get("total_executions", 0)
#         if total == 0:
#             return 0.0
#         return stats.get("successes", 0) / total

#     def get_capability_profile(self, agent_name: str) -> OutreachCapabilityProfile:
#         """Generate a capability profile for an agent."""
#         self._agent_stats.get(agent_name, {})

#         return OutreachCapabilityProfile(
#             agent_name=agent_name,
#             supported_tasks=self._get_supported_tasks(agent_name),
#             confidence_threshold=0.7,
#             max_leads_per_batch=100,
#             known_limitations=[],
#             success_rate=self.get_success_rate(agent_name),
#         )

#     def _get_supported_tasks(self, agent_name: str) -> list[str]:
#         """Get list of tasks an agent has successfully completed."""
#         tasks = set()
#         for execution in self._execution_history:
#             if execution["agent_name"] == agent_name and execution["success"]:
#                 tasks.add(execution["TaskType"])
#         return list(tasks)

#     def get_all_stats(self) -> dict[str, dict[str, Any]]:
#         """Get stats for all agents."""
#         return self._agent_stats.copy()

#     def heal_repository(self) -> dict:
#         """Invoke healing chain via super()."""
#         return super().heal_repository()
