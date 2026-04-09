"""Collaborative Intelligence - Multi-agent coordination and knowledge sharing.

This module provides collaborative intelligence capabilities that enable
multiple agents to share architectural insights and coordinate actions.
"""

from __future__ import annotations

import logging
import time
from typing import Any, Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import threading
from concurrent.futures import ThreadPoolExecutor, Future

from ..decision_engine import AgentDecisionEngine, ArchitecturalContext, DecisionResult, RiskLevel
from .contextual_engine import ContextualIntelligenceEngine, AnalysisResult

logger = logging.getLogger(__name__)


class CollaborationMode(Enum):
    """Modes of agent collaboration."""

    INDEPENDENT = "independent"  # Agents work independently
    ADVISORY = "advisory"  # Agents provide advice to each other
    COORDINATED = "coordinated"  # Agents coordinate actions
    CONSENSUS = "consensus"  # Agents require consensus for actions
    HIERARCHICAL = "hierarchical"  # Senior agents oversee junior agents


class MessageType(Enum):
    """Types of collaboration messages."""

    INSIGHT_SHARING = "insight_sharing"
    RISK_ALERT = "risk_alert"
    COORDINATION_REQUEST = "coordination_request"
    KNOWLEDGE_QUERY = "knowledge_query"
    DECISION_SUPPORT = "decision_support"
    CONFLICT_RESOLUTION = "conflict_resolution"


@dataclass
class CollaborationMessage:
    """Message between collaborating agents."""

    sender_id: str
    recipient_id: Optional[str]  # None for broadcast
    message_type: MessageType
    content: Dict[str, Any]
    timestamp: float
    priority: int = 5  # 1-10, 10 being highest
    context: Optional[ArchitecturalContext] = None
    correlation_id: Optional[str] = None


@dataclass
class AgentProfile:
    """Profile of an agent in the collaborative network."""

    agent_id: str
    agent_type: str
    capabilities: List[str]
    experience_level: str  # novice, intermediate, expert
    domain_expertise: Dict[str, float]  # domain -> expertise score
    collaboration_history: List[str] = field(default_factory=list)
    reputation_score: float = 0.5
    availability: bool = True


@dataclass
class CollaborationResult:
    """Result of collaborative analysis."""

    primary_result: AnalysisResult
    collaborative_insights: List[str]
    participating_agents: List[str]
    consensus_reached: bool
    conflicts_detected: List[Dict[str, Any]]
    coordination_actions: List[str]
    confidence_boost: float = 0.0
    execution_time_seconds: float = 0.0


class CollaborativeIntelligence:
    """Collaborative intelligence system for multi-agent coordination."""

    def __init__(self, contextual_engine: ContextualIntelligenceEngine):
        """Initialize collaborative intelligence system.

        Args:
            contextual_engine: Contextual intelligence engine for base analysis
        """
        self.contextual_engine = contextual_engine

        # Agent registry
        self.agent_profiles: Dict[str, AgentProfile] = {}
        self.active_sessions: Dict[str, Set[str]] = defaultdict(set)  # session_id -> agent_ids

        # Message system
        self.message_queue: deque[CollaborationMessage] = deque(maxlen=1000)
        self.message_handlers: Dict[MessageType, callable] = {}
        self._message_lock = threading.Lock()

        # Knowledge sharing
        self.shared_insights: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.collaboration_history: List[CollaborationResult] = []

        # Thread pool for parallel collaboration
        self.executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="collab")

        # Initialize message handlers
        self._initialize_message_handlers()

        logger.info("CollaborativeIntelligence initialized")

    def register_agent(self, profile: AgentProfile) -> None:
        """Register an agent in the collaborative network.

        Args:
            profile: Agent profile with capabilities and expertise
        """
        self.agent_profiles[profile.agent_id] = profile
        logger.info(f"Agent {profile.agent_id} registered with capabilities: {profile.capabilities}")

    def analyze_collaboratively(
        self,
        context: ArchitecturalContext,
        requesting_agent: str,
        collaboration_mode: CollaborationMode = CollaborationMode.ADVISORY,
        target_agents: Optional[List[str]] = None,
    ) -> CollaborationResult:
        """Perform collaborative analysis with multiple agents.

        Args:
            context: Architectural context for analysis
            requesting_agent: ID of the requesting agent
            collaboration_mode: Mode of collaboration to use
            target_agents: Specific agents to collaborate with (None for auto-selection)

        Returns:
            CollaborationResult with collaborative insights and coordination
        """
        start_time = time.time()

        logger.info(
            f"Starting collaborative analysis for agent {requesting_agent} in mode {collaboration_mode.value}"
        )

        # Get primary analysis
        primary_result = self.contextual_engine.analyze_with_context(context)

        # Select collaborating agents
        selected_agents = self._select_collaborating_agents(
            context, requesting_agent, collaboration_mode, target_agents
        )

        # Initialize collaboration result
        collab_result = CollaborationResult(
            primary_result=primary_result,
            collaborative_insights=[],
            participating_agents=[requesting_agent] + selected_agents,
            consensus_reached=False,
            conflicts_detected=[],
            coordination_actions=[],
        )

        # Perform collaboration based on mode
        if collaboration_mode == CollaborationMode.INDEPENDENT:
            collab_result.consensus_reached = True
        elif collaboration_mode == CollaborationMode.ADVISORY:
            self._advisory_collaboration(context, requesting_agent, selected_agents, collab_result)
        elif collaboration_mode == CollaborationMode.COORDINATED:
            self._coordinated_collaboration(context, requesting_agent, selected_agents, collab_result)
        elif collaboration_mode == CollaborationMode.CONSENSUS:
            self._consensus_collaboration(context, requesting_agent, selected_agents, collab_result)
        elif collaboration_mode == CollaborationMode.HIERARCHICAL:
            self._hierarchical_collaboration(context, requesting_agent, selected_agents, collab_result)

        # Calculate execution time
        collab_result.execution_time_seconds = time.time() - start_time

        # Calculate confidence boost from collaboration
        collab_result.confidence_boost = self._calculate_confidence_boost(collab_result)

        # Store collaboration history
        self.collaboration_history.append(collab_result)

        # Update agent profiles
        self._update_agent_profiles(requesting_agent, selected_agents, collab_result)

        logger.info(
            f"Collaborative analysis completed in {collab_result.execution_time_seconds:.3f}s "
            f"with {len(selected_agents)} collaborating agents"
        )

        return collab_result

    def _select_collaborating_agents(
        self,
        context: ArchitecturalContext,
        requesting_agent: str,
        mode: CollaborationMode,
        target_agents: Optional[List[str]],
    ) -> List[str]:
        """Select agents for collaboration based on context and capabilities."""
        if target_agents:
            # Validate requested agents are available
            available_targets = [
                agent_id
                for agent_id in target_agents
                if agent_id in self.agent_profiles and self.agent_profiles[agent_id].availability
            ]
            return available_targets

        # Auto-select based on context and capabilities
        candidates = []

        for agent_id, profile in self.agent_profiles.items():
            if agent_id == requesting_agent or not profile.availability:
                continue

            # Score based on domain expertise
            relevance_score = self._calculate_agent_relevance(profile, context)

            # Score based on capabilities
            capability_score = self._calculate_capability_match(profile, context)

            # Combined score
            total_score = (relevance_score * 0.6) + (capability_score * 0.4)

            candidates.append((agent_id, total_score))

        # Sort by score and select top candidates
        candidates.sort(key=lambda x: x[1], reverse=True)

        # Select different numbers based on collaboration mode
        max_agents = {
            CollaborationMode.ADVISORY: 3,
            CollaborationMode.COORDINATED: 2,
            CollaborationMode.CONSENSUS: 4,
            CollaborationMode.HIERARCHICAL: 1,
        }

        selected_count = max_agents.get(mode, 2)
        return [agent_id for agent_id, _ in candidates[:selected_count]]

    def _calculate_agent_relevance(self, profile: AgentProfile, context: ArchitecturalContext) -> float:
        """Calculate agent relevance to the current context."""
        relevance = 0.0

        # Domain expertise relevance
        for module in context.target_modules:
            for domain, expertise in profile.domain_expertise.items():
                if domain.lower() in module.lower():
                    relevance += expertise

        # Experience level relevance
        experience_bonus = {"novice": 0.1, "intermediate": 0.3, "expert": 0.5}
        relevance += experience_bonus.get(profile.experience_level, 0.2)

        # Reputation relevance
        relevance += profile.reputation_score * 0.2

        return min(1.0, relevance)

    def _calculate_capability_match(self, profile: AgentProfile, context: ArchitecturalContext) -> float:
        """Calculate how well agent capabilities match the context."""
        required_capabilities = self._infer_required_capabilities(context)

        if not required_capabilities:
            return 0.5  # Default score

        matches = sum(1 for cap in required_capabilities if cap in profile.capabilities)
        return matches / len(required_capabilities)

    def _infer_required_capabilities(self, context: ArchitecturalContext) -> List[str]:
        """Infer required capabilities from context."""
        capabilities = []

        action_type = context.action_type.lower()
        if "write" in action_type or "create" in action_type:
            capabilities.extend(["code_generation", "architectural_validation"])
        if "read" in action_type or "analyze" in action_type:
            capabilities.extend(["code_analysis", "pattern_recognition"])
        if "refactor" in action_type or "modify" in action_type:
            capabilities.extend(["refactoring", "impact_analysis"])
        if "test" in action_type:
            capabilities.extend(["testing", "validation"])

        return list(set(capabilities))

    def _advisory_collaboration(
        self,
        context: ArchitecturalContext,
        requesting_agent: str,
        selected_agents: List[str],
        result: CollaborationResult,
    ) -> None:
        """Perform advisory collaboration where agents provide advice."""

        # Send advisory requests to selected agents
        futures = []
        for agent_id in selected_agents:
            future = self.executor.submit(
                self._get_advisory_insights, agent_id, context, result.primary_result
            )
            futures.append((agent_id, future))

        # Collect insights
        for agent_id, future in futures:
            try:
                insights = future.result(timeout=5.0)
                result.collaborative_insights.extend(insights)
                result.collaborative_insights.append(f"[{agent_id}] Advisory insights provided")
            except (TimeoutError, ValueError, RuntimeError) as e:
                logger.warning(f"Failed to get insights from agent {agent_id}: {e}")

        result.consensus_reached = True  # Advisory mode doesn't require consensus

    def _coordinated_collaboration(
        self,
        context: ArchitecturalContext,
        requesting_agent: str,
        selected_agents: List[str],
        result: CollaborationResult,
    ) -> None:
        """Perform coordinated collaboration where agents coordinate actions."""

        # Check for potential conflicts
        conflicts = self._detect_coordination_conflicts(context, requesting_agent, selected_agents)
        result.conflicts_detected.extend(conflicts)

        if conflicts:
            # Attempt conflict resolution
            resolution_actions = self._resolve_conflicts(conflicts, selected_agents)
            result.coordination_actions.extend(resolution_actions)

        # Get coordinated insights
        coordinated_insights = self._get_coordinated_insights(context, selected_agents, result.primary_result)
        result.collaborative_insights.extend(coordinated_insights)

        result.consensus_reached = len(conflicts) == 0

    def _consensus_collaboration(
        self,
        context: ArchitecturalContext,
        requesting_agent: str,
        selected_agents: List[str],
        result: CollaborationResult,
    ) -> None:
        """Perform consensus collaboration requiring agreement from all agents."""

        # Get individual agent assessments
        agent_assessments = {}
        for agent_id in selected_agents:
            assessment = self._get_agent_assessment(agent_id, context, result.primary_result)
            agent_assessments[agent_id] = assessment

        # Check for consensus
        consensus_reached = self._check_consensus(agent_assessments)
        result.consensus_reached = consensus_reached

        if not consensus_reached:
            result.conflicts_detected.append(
                {
                    "type": "consensus_failure",
                    "details": f"Agents could not reach consensus: {list(agent_assessments.keys())}",
                }
            )

            # Attempt to build consensus
            consensus_actions = self._build_consensus(agent_assessments, selected_agents)
            result.coordination_actions.extend(consensus_actions)

        # Aggregate insights
        for agent_id, assessment in agent_assessments.items():
            result.collaborative_insights.extend(assessment.get("insights", []))

    def _hierarchical_collaboration(
        self,
        context: ArchitecturalContext,
        requesting_agent: str,
        selected_agents: List[str],
        result: CollaborationResult,
    ) -> None:
        """Perform hierarchical collaboration with senior agent oversight."""

        # Find senior agent (highest experience level)
        senior_agent = max(selected_agents, key=lambda aid: self.agent_profiles[aid].experience_level)

        # Get senior agent oversight
        oversight = self._get_senior_oversight(senior_agent, context, result.primary_result)
        result.collaborative_insights.extend(oversight)

        # Senior agent makes final decision
        final_decision = self._make_hierarchical_decision(senior_agent, context, result.primary_result)
        result.consensus_reached = final_decision.get("approved", False)

        if not result.consensus_reached:
            result.coordination_actions.append(f"Senior agent {senior_agent} rejected action")
        else:
            result.coordination_actions.append(f"Senior agent {senior_agent} approved action")

    def _get_advisory_insights(
        self, agent_id: str, context: ArchitecturalContext, primary_result: AnalysisResult
    ) -> List[str]:
        """Get advisory insights from a specific agent."""
        # This would integrate with the actual agent's analysis capabilities
        # For now, simulate advisory insights
        insights = []

        profile = self.agent_profiles.get(agent_id)
        if not profile:
            return insights

        # Domain-specific insights
        for domain, expertise in profile.domain_expertise.items():
            if expertise > 0.7:
                insights.append(f"[{agent_id}] High expertise in {domain}: additional validation recommended")

        # Experience-based insights
        if profile.experience_level == "expert":
            insights.append(
                f"[{agent_id}] Expert recommendation: consider long-term architectural implications"
            )

        # Risk-based insights
        if primary_result.base_result.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            insights.append(f"[{agent_id}] Risk assessment confirmed: additional safeguards recommended")

        return insights

    def _detect_coordination_conflicts(
        self, context: ArchitecturalContext, requesting_agent: str, selected_agents: List[str]
    ) -> List[Dict[str, Any]]:
        """Detect potential coordination conflicts between agents."""
        conflicts = []

        # Check for simultaneous access to same resources
        resource_access = defaultdict(list)
        for agent_id in [requesting_agent] + selected_agents:
            for module in context.target_modules:
                resource_access[module].append(agent_id)

        for resource, agents in resource_access.items():
            if len(agents) > 1:
                conflicts.append(
                    {
                        "type": "resource_conflict",
                        "resource": resource,
                        "agents": agents,
                        "severity": "medium",
                    }
                )

        return conflicts

    def _resolve_conflicts(self, conflicts: List[Dict[str, Any]], selected_agents: List[str]) -> List[str]:
        """Attempt to resolve detected conflicts."""
        resolution_actions = []

        for conflict in conflicts:
            if conflict["type"] == "resource_conflict":
                resolution_actions.append(f"Implement resource locking for {conflict['resource']}")
                resolution_actions.append("Establish coordination protocol for concurrent access")

        return resolution_actions

    def _get_coordinated_insights(
        self, context: ArchitecturalContext, selected_agents: List[str], primary_result: AnalysisResult
    ) -> List[str]:
        """Get coordinated insights from multiple agents."""
        insights = []

        # Aggregate insights from all agents
        for agent_id in selected_agents:
            agent_insights = self._get_advisory_insights(agent_id, context, primary_result)
            insights.extend(agent_insights)

        # Add coordination-specific insights
        if len(selected_agents) > 1:
            insights.append("Multi-agent coordination: increased validation coverage")
            insights.append("Distributed expertise: comprehensive architectural analysis")

        return insights

    def _get_agent_assessment(
        self, agent_id: str, context: ArchitecturalContext, primary_result: AnalysisResult
    ) -> Dict[str, Any]:
        """Get assessment from a specific agent for consensus building."""
        # This would integrate with the actual agent's assessment capabilities
        profile = self.agent_profiles.get(agent_id)

        # Simulate assessment based on agent profile
        approval_likelihood = 0.5

        # Experience-based approval
        if profile.experience_level == "expert":
            approval_likelihood += 0.2
        elif profile.experience_level == "novice":
            approval_likelihood -= 0.1

        # Risk-based approval
        if primary_result.base_result.risk_level == RiskLevel.CRITICAL:
            approval_likelihood -= 0.3
        elif primary_result.base_result.risk_level == RiskLevel.LOW:
            approval_likelihood += 0.2

        approved = approval_likelihood > 0.5

        return {
            "agent_id": agent_id,
            "approved": approved,
            "confidence": approval_likelihood,
            "insights": [f"[{agent_id}] Assessment based on {profile.experience_level} experience"],
        }

    def _check_consensus(self, agent_assessments: Dict[str, Dict[str, Any]]) -> bool:
        """Check if consensus is reached among agents."""
        if not agent_assessments:
            return True

        approvals = [assessment["approved"] for assessment in agent_assessments.values()]

        # Consensus requires all agents to agree
        return all(approvals) or not any(approvals)

    def _build_consensus(
        self, agent_assessments: Dict[str, Dict[str, Any]], selected_agents: List[str]
    ) -> List[str]:
        """Attempt to build consensus among disagreeing agents."""
        actions = []

        # Find dissenting agents
        dissenting = [
            agent_id for agent_id, assessment in agent_assessments.items() if not assessment["approved"]
        ]

        if dissenting:
            actions.append(f"Initiate consensus building with agents: {dissenting}")
            actions.append("Facilitate discussion to resolve concerns")
            actions.append("Consider compromise solutions")

        return actions

    def _get_senior_oversight(
        self, senior_agent: str, context: ArchitecturalContext, primary_result: AnalysisResult
    ) -> List[str]:
        """Get oversight insights from senior agent."""
        insights = [f"[{senior_agent}] Senior oversight initiated"]

        profile = self.agent_profiles.get(senior_agent)
        if profile and profile.experience_level == "expert":
            insights.append("[senior] Expert review: architectural soundness confirmed")
            insights.append("[senior] Risk assessment within acceptable bounds")

        return insights

    def _make_hierarchical_decision(
        self, senior_agent: str, context: ArchitecturalContext, primary_result: AnalysisResult
    ) -> Dict[str, Any]:
        """Make hierarchical decision based on senior agent input."""
        # Simulate senior agent decision
        approved = True

        # Senior agents are more cautious with high-risk actions
        if primary_result.base_result.risk_level == RiskLevel.CRITICAL:
            approved = False

        return {
            "senior_agent": senior_agent,
            "approved": approved,
            "reasoning": "Hierarchical decision based on senior assessment",
        }

    def _calculate_confidence_boost(self, result: CollaborationResult) -> float:
        """Calculate confidence boost from collaboration."""
        boost = 0.0

        # Boost based on number of participating agents
        agent_boost = min(0.2, len(result.participating_agents) * 0.05)
        boost += agent_boost

        # Boost based on consensus
        if result.consensus_reached:
            boost += 0.1

        # Boost based on lack of conflicts
        if not result.conflicts_detected:
            boost += 0.1

        # Boost based on collaborative insights
        insight_boost = min(0.1, len(result.collaborative_insights) * 0.02)
        boost += insight_boost

        return min(0.5, boost)  # Cap at 0.5

    def _update_agent_profiles(
        self, requesting_agent: str, selected_agents: List[str], result: CollaborationResult
    ) -> None:
        """Update agent profiles based on collaboration outcome."""
        # Update collaboration history
        for agent_id in result.participating_agents:
            if agent_id in self.agent_profiles:
                profile = self.agent_profiles[agent_id]
                profile.collaboration_history.append(str(result))

                # Update reputation based on successful collaboration
                if result.consensus_reached and not result.conflicts_detected:
                    profile.reputation_score = min(1.0, profile.reputation_score + 0.01)
                elif result.conflicts_detected:
                    profile.reputation_score = max(0.0, profile.reputation_score - 0.005)

    def _initialize_message_handlers(self) -> None:
        """Initialize message handlers for different message types."""
        self.message_handlers = {
            MessageType.INSIGHT_SHARING: self._handle_insight_sharing,
            MessageType.RISK_ALERT: self._handle_risk_alert,
            MessageType.COORDINATION_REQUEST: self._handle_coordination_request,
            MessageType.KNOWLEDGE_QUERY: self._handle_knowledge_query,
            MessageType.DECISION_SUPPORT: self._handle_decision_support,
            MessageType.CONFLICT_RESOLUTION: self._handle_conflict_resolution,
        }

    def _handle_insight_sharing(self, message: CollaborationMessage) -> None:
        """Handle insight sharing messages."""
        agent_id = message.sender_id
        insights = message.content.get("insights", [])

        self.shared_insights[agent_id].extend(insights)
        logger.info(f"Received {len(insights)} insights from agent {agent_id}")

    def _handle_risk_alert(self, message: CollaborationMessage) -> None:
        """Handle risk alert messages."""
        logger.warning(f"Risk alert from {message.sender_id}: {message.content}")

        # Broadcast to relevant agents
        self._broadcast_message(message, exclude_sender=True)

    def _handle_coordination_request(self, message: CollaborationMessage) -> None:
        """Handle coordination request messages."""
        logger.info(f"Coordination request from {message.sender_id}")

        # Process coordination request
        # This would integrate with actual coordination logic

    def _handle_knowledge_query(self, message: CollaborationMessage) -> None:
        """Handle knowledge query messages."""
        logger.info(f"Knowledge query from {message.sender_id}")

        # Process knowledge query
        # This would integrate with knowledge base

    def _handle_decision_support(self, message: CollaborationMessage) -> None:
        """Handle decision support messages."""
        logger.info(f"Decision support request from {message.sender_id}")

        # Process decision support request
        # This would integrate with decision support system

    def _handle_conflict_resolution(self, message: CollaborationMessage) -> None:
        """Handle conflict resolution messages."""
        logger.info(f"Conflict resolution from {message.sender_id}")

        # Process conflict resolution
        # This would integrate with conflict resolution system

    def _broadcast_message(self, message: CollaborationMessage, exclude_sender: bool = False) -> None:
        """Broadcast message to all relevant agents."""
        with self._message_lock:
            self.message_queue.append(message)

    def send_message(self, message: CollaborationMessage) -> None:
        """Send a message to another agent or broadcast."""
        with self._message_lock:
            self.message_queue.append(message)

        # Process message immediately if handler exists
        handler = self.message_handlers.get(message.message_type)
        if handler:
            try:
                handler(message)
            except (ValueError, RuntimeError, KeyError) as e:
                logger.error(f"Error handling message {message.message_type}: {e}")

    def get_collaboration_statistics(self) -> Dict[str, Any]:
        """Get collaboration system statistics."""
        return {
            "registered_agents": len(self.agent_profiles),
            "active_sessions": len(self.active_sessions),
            "total_collaborations": len(self.collaboration_history),
            "average_confidence_boost": sum(r.confidence_boost for r in self.collaboration_history)
            / len(self.collaboration_history)
            if self.collaboration_history
            else 0.0,
            "consensus_rate": sum(1 for r in self.collaboration_history if r.consensus_reached)
            / len(self.collaboration_history)
            if self.collaboration_history
            else 0.0,
            "message_queue_size": len(self.message_queue),
            "shared_insights_count": sum(len(insights) for insights in self.shared_insights.values()),
        }
