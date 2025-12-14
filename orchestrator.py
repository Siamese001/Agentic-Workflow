"""
Swarm Orchestrator - Hardened Architecture

Manages the lifecycle of the agent swarm with Canon enforcement
and retry logic for failed executions.
"""

import json
import logging
import time
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, timedelta

from agents.specialists import create_agent, PlannerAgent, CoderAgent, AuditorAgent
from core.connections import SwarmNetwork
from core.exceptions import (
    CanonViolationError,
    AgentExecutionError,
    SwarmInitializationError,
    MemorySyncError
)

logger = logging.getLogger(__name__)


class SwarmOrchestrator:
    """
    Manages the swarm execution lifecycle.
    
    Orchestrates: Planner -> Coder -> Auditor
    Enforces Canon compliance and handles failures with retry logic.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the orchestrator.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        
        # Execution state
        self.max_retries = self.config.get("max_retries", 3)
        self.retry_delay = self.config.get("retry_delay", 1.0)
        self.current_mission: Optional[Dict[str, Any]] = None
        
        # Agent instances
        self.planner: Optional[PlannerAgent] = None
        self.coder: Optional[CoderAgent] = None
        self.auditor: Optional[AuditorAgent] = None
        
        # Execution history
        self.execution_history: List[Dict[str, Any]] = []
        
        # Initialize swarm network
        self.network = SwarmNetwork.get_instance()
        
        logger.info("SwarmOrchestrator initialized")
    
    def initialize(self) -> bool:
        """
        Initialize all agents and verify system readiness.
        
        Returns:
            True if initialization successful
            
        Raises:
            SwarmInitializationError: If initialization fails
        """
        try:
            # Connect to network
            if not self.network.connect():
                raise SwarmInitializationError(
                    "Failed to connect to SwarmNetwork",
                    failed_component="SwarmNetwork"
                )
            
            # Run system sanity check
            self._run_system_sanity_check()
            
            # Initialize agents
            self.planner = create_agent("planner", self.config.get("planner", {}))
            self.coder = create_agent("coder", self.config.get("coder", {}))
            self.auditor = create_agent("auditor", self.config.get("auditor", {}))
            
            logger.info("SwarmOrchestrator fully initialized")
            return True
            
        except Exception as e:
            raise SwarmInitializationError(
                f"Orchestrator initialization failed: {e}",
                failed_component="SwarmOrchestrator"
            )
    
    def _run_system_sanity_check(self):
        """Verify system components are ready."""
        # Check Redis AOF is enabled
        try:
            info = self.network.gatekeeper.redis.info()
            if not info.get("aof_enabled", False):
                logger.warning("Redis AOF is not enabled - data may not persist")
        except Exception as e:
            raise MemorySyncError(
                "Redis health check failed",
                operation="info",
                backend="redis"
            )
        
        # Check Qdrant connectivity
        try:
            collections = self.network.qdrant_cache.client.get_collections()
            logger.debug(f"Qdrant collections: {[c.name for c in collections.collections]}")
        except Exception as e:
            raise MemorySyncError(
                "Qdrant health check failed",
                operation="get_collections",
                backend="qdrant"
            )
        
        logger.info("System sanity check passed")
    
    def run_mission(self, mission: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a complete mission through the swarm.
        
        Args:
            mission: Mission description
            context: Optional mission context
            
        Returns:
            Mission execution results
        """
        self.current_mission = {
            "mission": mission,
            "context": context or {},
            "started_at": datetime.utcnow(),
            "status": "running"
        }
        
        logger.info(f"Starting mission: {mission}")
        
        try:
            # Phase 1: Planning
            plan_result = self._execute_phase(
                "planning",
                self.planner,
                {"objective": mission, "context": context}
            )
            
            # Phase 2: Coding
            code_result = self._execute_phase(
                "coding",
                self.coder,
                {
                    "specification": self._extract_code_spec(plan_result),
                    "language": "python",
                    "requirements": context.get("requirements", [])
                }
            )
            
            # Phase 3: Auditing
            audit_result = self._execute_phase(
                "auditing",
                self.auditor,
                {
                    "code": code_result.get("code", ""),
                    "language": "python",
                    "validation_type": "full"
                }
            )
            
            # Check if audit passed
            if not audit_result["validation_result"]["is_valid"]:
                # Handle audit failure with retry logic
                return self._handle_audit_failure(code_result, audit_result, context)
            
            # Mission completed successfully
            self.current_mission["status"] = "completed"
            self.current_mission["completed_at"] = datetime.utcnow()
            
            result = {
                "mission": mission,
                "status": "success",
                "plan": plan_result,
                "code": code_result,
                "audit": audit_result,
                "completed_at": self.current_mission["completed_at"].isoformat()
            }
            
            self._record_execution(result)
            return result
            
        except Exception as e:
            self.current_mission["status"] = "failed"
            self.current_mission["failed_at"] = datetime.utcnow()
            self.current_mission["error"] = str(e)
            
            logger.error(f"Mission failed: {e}")
            raise
    
    def _execute_phase(
        self,
        phase_name: str,
        agent,
        task: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a single phase with retry logic.
        
        Args:
            phase_name: Name of the phase
            agent: Agent instance to execute
            task: Task specification
            
        Returns:
            Phase execution result
        """
        attempt = 0
        last_error = None
        
        while attempt < self.max_retries:
            try:
                logger.info(f"Executing {phase_name} phase (attempt {attempt + 1})")
                
                # Execute task through agent
                result = agent.execute(task)
                
                # Add phase metadata
                result["phase"] = phase_name
                result["attempt"] = attempt + 1
                result["executed_at"] = datetime.utcnow().isoformat()
                
                logger.info(f"{phase_name} phase completed successfully")
                return result
                
            except CanonViolationError as e:
                # Canon violations are not retriable
                logger.error(f"Canon violation in {phase_name}: {e}")
                raise
            except Exception as e:
                last_error = e
                attempt += 1
                
                if attempt < self.max_retries:
                    logger.warning(f"{phase_name} failed (attempt {attempt}), retrying: {e}")
                    time.sleep(self.retry_delay * attempt)
                else:
                    logger.error(f"{phase_name} failed after {self.max_retries} attempts")
                    raise AgentExecutionError(
                        f"Phase {phase_name} failed: {e}",
                        agent_id=agent.agent_id,
                        task=str(task),
                        retry_count=attempt
                    )
        
        # Should not reach here
        raise last_error
    
    def _handle_audit_failure(
        self,
        code_result: Dict[str, Any],
        audit_result: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Handle audit failure with retry logic.
        
        Args:
            code_result: Result from coder phase
            audit_result: Result from auditor phase
            context: Mission context
            
        Returns:
            Final mission result after retries
        """
        logger.warning("Audit failed, initiating retry logic")
        
        retry_count = 0
        while retry_count < self.max_retries:
            retry_count += 1
            
            # Update coder memory with failure
            if self.coder.current_token and self.coder.current_token.pattern_id:
                self.coder._record_outcome(
                    success=False,
                    error_trace=json.dumps(audit_result["validation_result"]["errors"])
                )
            
            # Wait before retry
            time.sleep(self.retry_delay * retry_count)
            
            # Try coding again with updated memory
            logger.info(f"Retry attempt {retry_count} for coding phase")
            
            try:
                # Add audit feedback to context
                retry_context = context.copy() if context else {}
                retry_context["previous_errors"] = audit_result["validation_result"]["errors"]
                retry_context["retry_attempt"] = retry_count
                
                code_retry = self._execute_phase(
                    "coding_retry",
                    self.coder,
                    {
                        "specification": self._extract_code_spec(self.current_mission.get("plan", {})),
                        "language": "python",
                        "requirements": retry_context.get("requirements", []),
                        "context": retry_context
                    }
                )
                
                # Re-audit the new code
                audit_retry = self._execute_phase(
                    "auditing_retry",
                    self.auditor,
                    {
                        "code": code_retry.get("code", ""),
                        "language": "python",
                        "validation_type": "full"
                    }
                )
                
                if audit_retry["validation_result"]["is_valid"]:
                    logger.info(f"Audit passed on retry {retry_count}")
                    
                    # Mission completed after retries
                    self.current_mission["status"] = "completed_with_retries"
                    self.current_mission["completed_at"] = datetime.utcnow()
                    
                    return {
                        "mission": self.current_mission["mission"],
                        "status": "success",
                        "retry_count": retry_count,
                        "code": code_retry,
                        "audit": audit_retry,
                        "completed_at": self.current_mission["completed_at"].isoformat()
                    }
                
            except Exception as e:
                logger.error(f"Retry {retry_count} failed: {e}")
        
        # All retries exhausted
        logger.error("All retry attempts exhausted")
        
        self.current_mission["status"] = "failed"
        self.current_mission["failed_at"] = datetime.utcnow()
        
        return {
            "mission": self.current_mission["mission"],
            "status": "failed",
            "retry_count": retry_count,
            "final_code": code_result,
            "final_audit": audit_result,
            "failed_at": self.current_mission["failed_at"].isoformat()
        }
    
    def _extract_code_spec(self, plan_result: Dict[str, Any]) -> Dict[str, Any]:
        """Extract code specification from plan result."""
        if not plan_result or "plan" not in plan_result:
            return {"type": "generic", "description": "Generate code based on plan"}
        
        plan = plan_result["plan"]
        
        # Determine code type from plan
        if any("class" in step.get("action", "").lower() for step in plan):
            return {"type": "class", "description": "Implement class structure"}
        elif any("function" in step.get("action", "").lower() for step in plan):
            return {"type": "function", "description": "Implement functions"}
        else:
            return {"type": "module", "description": "Implement module"}
    
    def _record_execution(self, result: Dict[str, Any]):
        """Record execution in history."""
        execution_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "mission": result["mission"],
            "status": result["status"],
            "duration": (
                datetime.utcnow() - self.current_mission["started_at"]
            ).total_seconds()
        }
        
        self.execution_history.append(execution_record)
        
        # Keep only last 100 executions
        if len(self.execution_history) > 100:
            self.execution_history = self.execution_history[-100:]
    
    def get_swarm_metrics(self) -> Dict[str, Any]:
        """Get comprehensive swarm metrics."""
        metrics = {
            "network": self.network.get_metrics(),
            "agents": {},
            "orchestrator": {
                "total_missions": len(self.execution_history),
                "success_rate": self._calculate_success_rate(),
                "current_mission": self.current_mission.get("status") if self.current_mission else None
            }
        }
        
        # Get individual agent metrics
        if self.planner:
            metrics["agents"]["planner"] = self.planner.get_metrics()
        if self.coder:
            metrics["agents"]["coder"] = self.coder.get_metrics()
        if self.auditor:
            metrics["agents"]["auditor"] = self.auditor.get_metrics()
        
        return metrics
    
    def _calculate_success_rate(self) -> float:
        """Calculate mission success rate."""
        if not self.execution_history:
            return 0.0
        
        successful = sum(1 for e in self.execution_history if e["status"] == "success")
        return successful / len(self.execution_history)
    
    def shutdown(self):
        """Shutdown the orchestrator and all agents."""
        logger.info("Shutting down SwarmOrchestrator")
        
        # Disconnect network
        self.network.disconnect()
        
        # Clear agents
        self.planner = None
        self.coder = None
        self.auditor = None
        
        logger.info("SwarmOrchestrator shutdown complete")
