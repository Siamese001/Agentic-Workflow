"""
Integration example for HardenedRedisInspector with MCP Executor.

This file demonstrates how to:
1. Register the Redis Inspector with MCP executor
2. Use it for workflow debugging and monitoring
3. Implement safe memory inspection patterns
4. Monitor system state and queue status
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional

from .hardened_redis_inspector import (
    HardenedRedisInspector,
    create_redis_inspector_config,
    RedisCommand
)
# from .hardened_mcp_executor import HardenedMCPExecutor
# from .hardened_cache_client import HardenedCacheClient

logger = logging.getLogger(__name__)


class RedisInspectorIntegration:
    """
    Integration layer for Redis Inspector with agent orchestration.
    
    Provides high-level methods for common inspection patterns
    and ensures safe usage within the agent ecosystem.
    """
    
    def __init__(self, cache_client, mcp_executor):
        """Initialize the integration.
        
        Args:
            cache_client: HardenedCacheClient instance
            mcp_executor: HardenedMCPExecutor instance
        """
        self.cache_client = cache_client
        self.mcp_executor = mcp_executor
        self.inspector = HardenedRedisInspector(cache_client)
        
        # Register with MCP executor
        self._register_with_mcp()
        
        self.logger = logging.getLogger("RedisInspectorIntegration")
    
    def _register_with_mcp(self) -> None:
        """Register the inspector tool with MCP executor."""
        config = create_redis_inspector_config(self.cache_client)
        self.mcp_executor.register_tool(config)
        self.logger.info("Redis Inspector registered with MCP executor")
    
    async def check_workflow_health(self, workflow_id: str) -> Dict[str, Any]:
        """
        Comprehensive workflow health check.
        
        Args:
            workflow_id: ID of the workflow to check
            
        Returns:
            Health status and diagnostics
        """
        health_report = {
            "workflow_id": workflow_id,
            "status": "unknown",
            "checks": {},
            "recommendations": []
        }
        
        try:
            # Check if workflow exists
            exists = await self.mcp_executor.execute_tool(
                "inspect_memory",
                command="EXISTS",
                key=f"workflow:{workflow_id}"
            )
            
            if not exists.get("value"):
                health_report["status"] = "not_found"
                health_report["recommendations"].append("Workflow not initialized")
                return health_report
            
            health_report["status"] = "found"
            
            # Check workflow data
            workflow_data = await self.mcp_executor.execute_tool(
                "inspect_memory",
                command="HGETALL",
                key=f"workflow:{workflow_id}"
            )
            health_report["checks"]["workflow_data"] = workflow_data
            
            # Check current step
            current_step = await self.mcp_executor.execute_tool(
                "inspect_memory",
                command="GET",
                key=f"workflow:{workflow_id}:current_step"
            )
            health_report["checks"]["current_step"] = current_step
            
            # Check for stuck state
            if current_step.get("value"):
                # Check if step has been running too long
                step_start = await self.mcp_executor.execute_tool(
                    "inspect_memory",
                    command="GET",
                    key=f"workflow:{workflow_id}:step_start_time"
                )
                
                if step_start.get("value"):
                    import time
                    start_time = float(step_start["value"])
                    if time.time() - start_time > 300:  # 5 minutes
                        health_report["status"] = "stuck"
                        health_report["recommendations"].append(
                            "Workflow step appears to be stuck"
                        )
            
            # Check error state
            errors = await self.mcp_executor.execute_tool(
                "inspect_memory",
                command="LLEN",
                key=f"workflow:{workflow_id}:errors"
            )
            
            if errors.get("value", 0) > 0:
                health_report["status"] = "error"
                health_report["checks"]["error_count"] = errors
                health_report["recommendations"].append(
                    f"Workflow has {errors['value']} errors"
                )
            
            return health_report
            
        except Exception as e:
            self.logger.error(f"Workflow health check failed: {e}")
            health_report["status"] = "error"
            health_report["error"] = str(e)
            return health_report
    
    async def monitor_queue_performance(self) -> Dict[str, Any]:
        """
        Monitor queue performance and bottlenecks.
        
        Returns:
            Queue performance metrics
        """
        performance_report = {
            "timestamp": asyncio.get_event_loop().time(),
            "queues": {},
            "alerts": []
        }
        
        # Check different queue priorities
        queue_priorities = ["high_priority", "normal", "low_priority", "batch"]
        
        for priority in queue_priorities:
            queue_key = f"queue:{priority}"
            
            try:
                # Get queue depth
                depth = await self.mcp_executor.execute_tool(
                    "inspect_memory",
                    command="LLEN",
                    key=queue_key
                )
                
                # Get processing count
                processing = await self.mcp_executor.execute_tool(
                    "inspect_memory",
                    command="LLEN",
                    key=f"{queue_key}:processing"
                )
                
                # Calculate metrics
                queue_metrics = {
                    "depth": depth.get("value", 0),
                    "processing": processing.get("value", 0),
                    "utilization": 0.0
                }
                
                # Calculate utilization (assuming max 100 items)
                queue_metrics["utilization"] = min(
                    queue_metrics["depth"] / 100.0,
                    1.0
                )
                
                performance_report["queues"][priority] = queue_metrics
                
                # Check for alerts
                if queue_metrics["depth"] > 50:
                    performance_report["alerts"].append(
                        f"Queue {priority} has high backlog: {queue_metrics['depth']} items"
                    )
                
                if queue_metrics["processing"] > 10:
                    performance_report["alerts"].append(
                        f"Queue {priority} has many processing items: {queue_metrics['processing']}"
                    )
                
            except Exception as e:
                self.logger.error(f"Failed to monitor queue {priority}: {e}")
                performance_report["queues"][priority] = {"error": str(e)}
        
        return performance_report
    
    async def debug_memory_leaks(self) -> Dict[str, Any]:
        """
        Debug potential memory leaks in Redis.
        
        Returns:
            Memory analysis and recommendations
        """
        leak_report = {
            "analysis": {},
            "suspicious_keys": [],
            "recommendations": []
        }
        
        try:
            # Check large objects
            suspicious_patterns = [
                "temp:",
                "cache:",
                "session:",
                "workflow:"
            ]
            
            for pattern in suspicious_patterns:
                # This would require SCAN command which is not whitelisted
                # For now, we check known large keys
                known_large_keys = [
                    f"{pattern}large_data",
                    f"{pattern}bulk_import",
                    f"{pattern}temp_buffer"
                ]
                
                for key in known_large_keys:
                    try:
                        key_type = await self.mcp_executor.execute_tool(
                            "inspect_memory",
                            command="TYPE",
                            key=key
                        )
                        
                        if key_type.get("value") and key_type["value"] != "none":
                            # Check size based on type
                            if key_type["value"] == "list":
                                size = await self.mcp_executor.execute_tool(
                                    "inspect_memory",
                                    command="LLEN",
                                    key=key
                                )
                            elif key_type["value"] == "hash":
                                size = await self.mcp_executor.execute_tool(
                                    "inspect_memory",
                                    command="HGETALL",
                                    key=key
                                )
                                size = {"value": len(size.get("value", {}))}
                            elif key_type["value"] == "set":
                                size = await self.mcp_executor.execute_tool(
                                    "inspect_memory",
                                    command="SCARD",
                                    key=key
                                )
                            else:
                                size = {"value": "unknown"}
                            
                            leak_report["analysis"][key] = {
                                "type": key_type["value"],
                                "size": size["value"]
                            }
                            
                            # Flag suspicious sizes
                            if isinstance(size["value"], int) and size["value"] > 1000:
                                leak_report["suspicious_keys"].append({
                                    "key": key,
                                    "type": key_type["value"],
                                    "size": size["value"]
                                })
                    
                    except Exception:
                        # Key doesn't exist or access denied
                        pass
            
            # Generate recommendations
            if leak_report["suspicious_keys"]:
                leak_report["recommendations"].append(
                    "Consider implementing TTL for large temporary keys"
                )
                leak_report["recommendations"].append(
                    "Review memory usage patterns and optimize data structures"
                )
            
            return leak_report
            
        except Exception as e:
            self.logger.error(f"Memory leak analysis failed: {e}")
            leak_report["error"] = str(e)
            return leak_report
    
    async def validate_system_state(self) -> Dict[str, Any]:
        """
        Validate overall system state and health.
        
        Returns:
            System validation report
        """
        validation_report = {
            "timestamp": asyncio.get_event_loop().time(),
            "status": "healthy",
            "checks": {},
            "issues": []
        }
        
        # Check critical system keys
        critical_checks = [
            ("metrics:system", "System metrics"),
            ("cache:stats", "Cache statistics"),
            ("state:global", "Global state")
        ]
        
        for key, description in critical_checks:
            try:
                exists = await self.mcp_executor.execute_tool(
                    "inspect_memory",
                    command="EXISTS",
                    key=key
                )
                
                validation_report["checks"][description] = {
                    "key": key,
                    "exists": exists.get("value", False)
                }
                
                if not exists.get("value"):
                    validation_report["status"] = "degraded"
                    validation_report["issues"].append(
                        f"Missing critical key: {key}"
                    )
            
            except Exception as e:
                validation_report["checks"][description] = {
                    "key": key,
                    "error": str(e)
                }
                validation_report["status"] = "error"
                validation_report["issues"].append(
                    f"Error checking {key}: {e}"
                )
        
        return validation_report
    
    def get_inspector_stats(self) -> Dict[str, Any]:
        """Get Redis Inspector statistics."""
        return self.inspector.get_stats()


# Example usage in orchestrator
class TitaniumOrchestratorMemoryHelper:
    """
    Helper class for Titanium Orchestrator to use Redis Inspector effectively.
    
    Provides canned queries for common orchestrator needs.
    """
    
    def __init__(self, mcp_executor):
        """Initialize with MCP executor."""
        self.mcp_executor = mcp_executor
        self.logger = logging.getLogger("OrchestratorMemoryHelper")
    
    async def should_dispatch_new_job(self, queue: str = "high_priority") -> bool:
        """Check if system can handle new job dispatch.
        
        Args:
            queue: Queue name to check
            
        Returns:
            True if system can handle new jobs
        """
        try:
            # Check queue depth
            depth = await self.mcp_executor.execute_tool(
                "inspect_memory",
                command="LLEN",
                key=f"queue:{queue}"
            )
            
            # Check processing capacity
            processing = await self.mcp_executor.execute_tool(
                "inspect_memory",
                command="LLEN",
                key=f"queue:{queue}:processing"
            )
            
            # Decision logic
            queue_depth = depth.get("value", 0)
            processing_count = processing.get("value", 0)
            
            # If queue has more than 5 items, switch to batch mode
            if queue_depth > 5:
                self.logger.info(f"Queue depth high ({queue_depth}), switching to batch mode")
                return False
            
            # If processing is at capacity, wait
            if processing_count >= 10:
                self.logger.info(f"Processing at capacity ({processing_count}), waiting")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to check dispatch capacity: {e}")
            # Conservative approach: don't dispatch if we can't check
            return False
    
    async def verify_prerequisites(self, workflow_id: str, step_name: str) -> bool:
        """Verify that prerequisites are met for workflow step.
        
        Args:
            workflow_id: Workflow ID
            step_name: Step to verify
            
        Returns:
            True if prerequisites are met
        """
        try:
            # Check previous step output
            prev_step_key = f"workflow:{workflow_id}:step_{step_name}_output"
            exists = await self.mcp_executor.execute_tool(
                "inspect_memory",
                command="EXISTS",
                key=prev_step_key
            )
            
            if not exists.get("value"):
                self.logger.warning(f"Prerequisite not met: {prev_step_key} missing")
                return False
            
            # Check for errors in previous step
            error_key = f"workflow:{workflow_id}:errors"
            error_count = await self.mcp_executor.execute_tool(
                "inspect_memory",
                command="LLEN",
                key=error_key
            )
            
            if error_count.get("value", 0) > 0:
                self.logger.warning(f"Workflow has errors, cannot proceed")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to verify prerequisites: {e}")
            return False
    
    async def diagnose_stalled_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Diagnose why a workflow might be stalled.
        
        Args:
            workflow_id: Workflow ID to diagnose
            
        Returns:
            Diagnosis report
        """
        diagnosis = {
            "workflow_id": workflow_id,
            "issues": [],
            "recommendations": []
        }
        
        try:
            # Check current step
            current = await self.mcp_executor.execute_tool(
                "inspect_memory",
                command="GET",
                key=f"workflow:{workflow_id}:current_step"
            )
            
            if not current.get("value"):
                diagnosis["issues"].append("No current step set")
                diagnosis["recommendations"].append("Initialize workflow step")
                return diagnosis
            
            # Check step start time
            start_time = await self.mcp_executor.execute_tool(
                "inspect_memory",
                command="GET",
                key=f"workflow:{workflow_id}:step_start_time"
            )
            
            if start_time.get("value"):
                import time
                elapsed = time.time() - float(start_time["value"])
                
                if elapsed > 300:  # 5 minutes
                    diagnosis["issues"].append(f"Step running for {elapsed:.0f} seconds")
                    diagnosis["recommendations"].append("Check for deadlocked resources")
                    diagnosis["recommendations"].append("Consider step timeout and retry")
            
            # Check for resource locks
            locks = await self.mcp_executor.execute_tool(
                "inspect_memory",
                command="SMEMBERS",
                key=f"locks:workflow:{workflow_id}"
            )
            
            if locks.get("value"):
                diagnosis["issues"].append(f"Workflow has {len(locks['value'])} active locks")
                diagnosis["recommendations"].append("Verify lock holders are alive")
            
            return diagnosis
            
        except Exception as e:
            diagnosis["error"] = str(e)
            return diagnosis


# Example usage
async def main():
    """Example of Redis Inspector integration usage."""
    from .hardened_mcp_executor import HardenedMCPExecutor
    from .hardened_cache_client import HardenedCacheClient
    
    # Initialize components
    cache_client = HardenedCacheClient()
    mcp_executor = HardenedMCPExecutor()
    
    # Create integration
    integration = RedisInspectorIntegration(cache_client, mcp_executor)
    
    # Monitor queue performance
    queue_report = await integration.monitor_queue_performance()
    print(f"\n=== Queue Performance ===")
    for queue, metrics in queue_report["queues"].items():
        print(f"{queue}: depth={metrics.get('depth', 0)}, utilization={metrics.get('utilization', 0):.2%}")
    
    # Check workflow health
    health = await integration.check_workflow_health("workflow_123")
    print(f"\n=== Workflow Health ===")
    print(f"Status: {health['status']}")
    if health["recommendations"]:
        print("Recommendations:")
        for rec in health["recommendations"]:
            print(f"  - {rec}")
    
    # Get inspector stats
    stats = integration.get_inspector_stats()
    print(f"\n=== Inspector Stats ===")
    print(f"Success Rate: {stats['success_rate']:.2%}")
    print(f"Total Inspections: {stats['total_inspections']}")


if __name__ == "__main__":
    asyncio.run(main())
