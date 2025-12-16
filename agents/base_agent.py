"""
Base Agent - Hardened Swarm Architecture

Abstract base class that enforces Canon consultation
for all agents in the swarm.
"""

import hashlib
import logging
import time
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from core.connections import SwarmNetwork
from core.exceptions import (
    CANON_EXCEPTIONS,
    AgentExecutionError,
    CanonViolationError,
    MemorySyncError,
)

logger = logging.getLogger(__name__)


class CanonToken:
    """
    Token issued after successful Canon verification.

    Represents authorization for an agent to proceed with
    its action based on Canon compliance.
    """

    def __init__(
        self,
        agent_id: str,
        pattern_id: Optional[str],
        verified_at: datetime,
        expires_at: Optional[datetime] = None
    ):
        self.agent_id = agent_id
        self.pattern_id = pattern_id
        self.verified_at = verified_at
        self.expires_at = expires_at or (verified_at + timedelta(minutes=5))
        self.signature = self._generate_signature()

    def _generate_signature(self) -> str:
        """Generate unique token signature."""
        data = f"{self.agent_id}:{self.pattern_id}:{self.verified_at.isoformat()}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]

    def is_valid(self) -> bool:
        """Check if token is still valid."""
        return datetime.utcnow() < self.expires_at

    def to_dict(self) -> Dict[str, Any]:
        """Convert token to dictionary."""
        return {
            "agent_id": self.agent_id,
            "pattern_id": self.pattern_id,
            "verified_at": self.verified_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "signature": self.signature
        }


class BaseAgent(ABC):
    """
    Abstract base class for all swarm agents.

    Enforces mandatory Canon consultation and outcome recording
    for every agent action.
    """

    def __init__(self, agent_id: str, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the base agent.

        Args:
            agent_id: Unique identifier for this agent
            config: Optional configuration dictionary
        """
        self.agent_id = agent_id
        self.config = config or {}

        # Connect to SwarmNetwork
        self.network = SwarmNetwork.get_instance()
        if not self.network.connect():
            raise AgentExecutionError(
                f"Failed to connect {agent_id} to SwarmNetwork",
                agent_id=agent_id,
                task="initialization"
            )

        # Execution state
        self.current_token: Optional[CanonToken] = None
        self.execution_context: Dict[str, Any] = {}
        self.metrics = {
            "executions": 0,
            "successes": 0,
            "failures": 0,
            "canon_violations": 0,
            "avg_latency_ms": 0
        }

        logger.info(
            f"BaseAgent {agent_id} initialized and connected to SwarmNetwork")

    def _consult_canon(
        self,
        action_description: str,
        code: Optional[str] = None,
        policy_key: Optional[str] = None,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> CanonToken:
        """
        Consult the Canon before executing any action.

        Args:
            action_description: Description of the planned action
            code: Optional code snippet to validate
            policy_key: Specific Canon rule being evaluated
            additional_context: Additional context for consultation

        Returns:
            CanonToken if consultation successful

        Raises:
            CanonViolationError: If Canon rules are violated
        """
        # Generate context vector from action description
        context_vector = self.network.gatekeeper.embed_action(
            action_description)

        # Prepare consultation context
        context = {
            "action": action_description,
            "agent_id": self.agent_id,
            "timestamp": datetime.utcnow().isoformat()
        }

        if code:
            context["code"] = code
        if policy_key:
            context["policy_key"] = policy_key
        if additional_context:
            context.update(additional_context)

        # Consult Canon
        start_time = time.perf_counter()

        try:
            is_safe, pattern = self.network.consult_canon(
                query_vector=context_vector,
                agent_id=self.agent_id,
                context=context
            )

            # Check for immediate violations
            if not is_safe:
                raise CanonViolationError(
                    "Canon consultation returned unsafe",
                    violation_type="unsafe_pattern",
                    agent_id=self.agent_id,
                    pattern_id=str(pattern.id) if pattern else None
                )

            # Create and return token
            token = CanonToken(
                agent_id=self.agent_id,
                pattern_id=str(pattern.id) if pattern else None,
                verified_at=datetime.utcnow()
            )

            # Store pattern in execution context
            if pattern:
                self.execution_context["matched_pattern"] = pattern

            # Track latency
            latency_ms = int((time.perf_counter() - start_time) * 1000)
            self._update_latency(latency_ms)

            logger.info(f"Canon consultation successful for {self.agent_id}")
            return token

        except CANON_EXCEPTIONS:
            self.metrics["canon_violations"] += 1
            raise
        except Exception as e:
            raise MemorySyncError(
                f"Canon consultation failed: {e}",
                operation="consult_canon",
                backend="both",
                context={"agent_id": self.agent_id}
            )

    def _record_outcome(
        self,
        success: bool,
        latency_ms: Optional[int] = None,
        error_trace: Optional[str] = None
    ):
        """
        Record execution outcome for meta-learning.

        Args:
            success: Whether execution was successful
            latency_ms: Execution latency in milliseconds
            error_trace: Error trace if execution failed
        """
        if not self.current_token or not self.current_token.pattern_id:
            logger.warning(f"No pattern to record outcome for {self.agent_id}")
            return

        try:
            self.network.record_outcome(
                pattern_id=self.current_token.pattern_id,
                success=success,
                agent_id=self.agent_id,
                latency_ms=latency_ms,
                error_trace=error_trace
            )

            # Update metrics
            self.metrics["executions"] += 1
            if success:
                self.metrics["successes"] += 1
            else:
                self.metrics["failures"] += 1

            logger.debug(
                f"Recorded outcome for {self.agent_id}: {'SUCCESS' if success else 'FAILURE'}")

        except Exception as e:
            logger.error(f"Failed to record outcome for {self.agent_id}: {e}")

    def _update_latency(self, latency_ms: int):
        """Update average latency metric."""
        current = self.metrics["avg_latency_ms"]
        count = self.metrics["executions"]
        self.metrics["avg_latency_ms"] = (
            (current * count) + latency_ms) / (count + 1)

    def execute(self, task: Dict[str, Any]) -> Any:
        """
        Execute a task with Canon enforcement.

        This method wraps the actual execution with Canon consultation
        and outcome recording.

        Args:
            task: Task specification dictionary

        Returns:
            Execution result

        Raises:
            CanonViolationError: If Canon rules are violated
            AgentExecutionError: If execution fails
        """
        start_time = time.perf_counter()

        try:
            # Step 1: Consult Canon
            self.current_token = self._consult_canon(
                action_description=task.get(
                    "action", f"Execute task for {self.agent_id}"),
                code=task.get("code"),
                policy_key=task.get("policy_key"),
                additional_context=task.get("context", {})
            )

            # Step 2: Execute the actual task
            logger.info(f"Executing task for {self.agent_id}")
            result = self._execute_task(task)

            # Step 3: Record success
            latency_ms = int((time.perf_counter() - start_time) * 1000)
            self._record_outcome(success=True, latency_ms=latency_ms)

            # Add Canon token to result
            if isinstance(result, dict):
                result["canon_token"] = self.current_token.to_dict()

            return result

        except CanonViolationError:
            # Record violation
            self._record_outcome(
                success=False, error_trace=str(CanonViolationError))
            raise
        except Exception as e:
            # Record failure
            latency_ms = int((time.perf_counter() - start_time) * 1000)
            self._record_outcome(
                success=False, latency_ms=latency_ms, error_trace=str(e))

            raise AgentExecutionError(
                f"Task execution failed: {e}",
                agent_id=self.agent_id,
                task=str(task),
                retry_count=task.get("retry_count", 0)
            )
        finally:
            # Clear current token
            self.current_token = None

    @abstractmethod
    def _execute_task(self, task: Dict[str, Any]) -> Any:
        """
        Execute the specific task for this agent.

        Must be implemented by concrete agent classes.

        Args:
            task: Task specification

        Returns:
            Task execution result
        """

    def get_metrics(self) -> Dict[str, Any]:
        """Get agent execution metrics."""
        return {
            "agent_id": self.agent_id,
            "metrics": self.metrics.copy(),
            "network_metrics": self.network.get_metrics(),
            "timestamp": datetime.utcnow().isoformat()
        }

    def reset_metrics(self):
        """Reset all metrics."""
        self.metrics = {
            "executions": 0,
            "successes": 0,
            "failures": 0,
            "canon_violations": 0,
            "avg_latency_ms": 0
        }

    def __repr__(self) -> str:
        return f"<BaseAgent id={self.agent_id} executions={self.metrics['executions']}>"