"""
Hardened Redis Inspector - Safe Read-Only Memory Inspection for Agents.

Implements a secure Redis inspection tool with:
- Whitelisted read-only commands only
- Namespace isolation and key validation
- Integration with HardenedCacheClient
- MCP executor registration support
"""

import logging
import json
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field, validator
from enum import Enum

logger = logging.getLogger(__name__)


class RedisCommand(str, Enum):
    """Whitelisted Redis commands for safe inspection."""
    GET = "GET"           # Read simple value
    HGETALL = "HGETALL"   # Read hash object (e.g., User Profile)
    LLEN = "LLEN"         # Check queue depth
    LRANGE = "LRANGE"     # Read recent logs/history
    EXISTS = "EXISTS"     # Check availability
    SCARD = "SCARD"       # Get set size
    SMEMBERS = "SMEMBERS" # Get all set members
    ZCARD = "ZCARD"       # Get sorted set size
    TYPE = "TYPE"         # Get key type


class RedisInspectionInput(BaseModel):
    """Input schema for the Redis Inspector tool."""
    command: RedisCommand = Field(..., description="The read-only operation to perform.")
    key: str = Field(..., description="The target key (must match allowed prefixes).")
    args: Optional[List[str]] = Field(None, description="Additional arguments (e.g., start/end for LRANGE).")
    
    @validator('key')
    def validate_key_format(cls, v):
        """Ensure key is not empty."""
        if not v or not v.strip():
            raise ValueError("Key cannot be empty")
        return v.strip()


class RedisInspectionResult(BaseModel):
    """Result of a Redis inspection operation."""
    status: str = Field(..., description="SUCCESS or ERROR")
    command: RedisCommand = Field(..., description="Command that was executed")
    key: str = Field(..., description="Key that was inspected")
    value: Optional[Any] = Field(None, description="Result value (if successful)")
    error_msg: Optional[str] = Field(None, description="Error message (if failed)")
    suggestion: Optional[str] = Field(None, description="Suggestion for fixing errors")
    execution_time_ms: Optional[float] = Field(None, description="Time taken to execute")


class HardenedRedisInspector:
    """
    Safe introspection tool for Agents.
    Enforces 'Read-Only' access and namespace safety.
    
    Features:
    - Command whitelisting (only safe read operations)
    - Key namespace isolation
    - Connection reuse via HardenedCacheClient
    - Comprehensive error handling
    - Execution time tracking
    """
    
    def __init__(self, cache_client):
        """Initialize the Redis inspector.
        
        Args:
            cache_client: HardenedCacheClient instance for connection reuse
        """
        self.client = cache_client
        self.logger = logging.getLogger("RedisInspector")
        
        # Security: Only allow access to specific data partitions
        self.ALLOWED_PREFIXES = (
            "workflow:",
            "memory:",
            "queue:",
            "job:",
            "cache:",
            "session:",
            "state:",
            "checkpoint:",
            "metrics:",
            "trace:"
        )
        
        # Statistics
        self.stats = {
            "total_inspections": 0,
            "successful_inspections": 0,
            "failed_inspections": 0,
            "access_denied": 0,
            "commands_used": {cmd.value: 0 for cmd in RedisCommand}
        }
    
    def _validate_key(self, key: str) -> None:
        """Prevents access to system secrets and unauthorized namespaces.
        
        Args:
            key: Redis key to validate
            
        Raises:
            ValueError: If key is not in allowed namespace
        """
        if not any(key.startswith(prefix) for prefix in self.ALLOWED_PREFIXES):
            self.stats["access_denied"] += 1
            raise ValueError(
                f"Access Denied: Key '{key}' is outside allowed namespaces. "
                f"Allowed prefixes: {self.ALLOWED_PREFIXES}"
            )
    
    async def execute_inspection(
        self,
        command: Union[str, RedisCommand],
        key: str,
        args: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Executes the whitelisted command via the Hardened Client.
        
        Args:
            command: Redis command to execute
            key: Target key
            args: Additional command arguments
            
        Returns:
            Dictionary with inspection result
        """
        import time
        start_time = time.time()
        
        # Convert string command to enum
        if isinstance(command, str):
            try:
                command = RedisCommand(command.upper())
            except ValueError:
                return self._create_error_result(
                    command=command,
                    key=key,
                    error=f"Command '{command}' is not whitelisted",
                    suggestion="Use only whitelisted commands: GET, HGETALL, LLEN, LRANGE, EXISTS, SCARD, SMEMBERS, ZCARD, TYPE"
                )
        
        self.stats["total_inspections"] += 1
        self.stats["commands_used"][command.value] += 1
        
        try:
            # Validate key before execution
            self._validate_key(key)
            
            # Get Redis connection (bypass L1 cache for real-time inspection)
            redis_conn = self.client.redis
            
            # Execute command based on type
            result = await self._execute_redis_command(redis_conn, command, key, args or [])
            
            # Calculate execution time
            execution_time = (time.time() - start_time) * 1000
            
            # Create success result
            inspection_result = RedisInspectionResult(
                status="SUCCESS",
                command=command,
                key=key,
                value=result,
                execution_time_ms=execution_time
            )
            
            self.stats["successful_inspections"] += 1
            
            self.logger.debug(
                f"Inspection successful: {command} {key} -> {type(result).__name__}"
            )
            
            return inspection_result.model_dump()
            
        except ValueError as e:
            # Access denied errors
            self.stats["failed_inspections"] += 1
            return self._create_error_result(
                command=command,
                key=key,
                error=str(e),
                suggestion="Use a key with allowed prefix"
            )
            
        except Exception as e:
            # Redis errors
            self.stats["failed_inspections"] += 1
            self.logger.error(f"Redis inspection failed: {e}")
            
            return self._create_error_result(
                command=command,
                key=key,
                error=str(e),
                suggestion="Check key format or Redis connectivity"
            )
    
    async def _execute_redis_command(
        self,
        redis_conn,
        command: RedisCommand,
        key: str,
        args: List[str]
    ) -> Any:
        """Execute the specific Redis command.
        
        Args:
            redis_conn: Redis connection
            command: Command to execute
            key: Target key
            args: Command arguments
            
        Returns:
            Command result
        """
        if command == RedisCommand.GET:
            val = await redis_conn.get(key)
            return val.decode() if val else None
            
        elif command == RedisCommand.HGETALL:
            val = await redis_conn.hgetall(key)
            # Convert bytes to strings for JSON safety
            return {k.decode(): v.decode() for k, v in val.items()} if val else {}
            
        elif command == RedisCommand.LLEN:
            return await redis_conn.llen(key)
            
        elif command == RedisCommand.LRANGE:
            start = int(args[0]) if args and len(args) > 0 else 0
            end = int(args[1]) if args and len(args) > 1 else -1
            val = await redis_conn.lrange(key, start, end)
            return [v.decode() for v in val] if val else []
            
        elif command == RedisCommand.EXISTS:
            return bool(await redis_conn.exists(key))
            
        elif command == RedisCommand.SCARD:
            return await redis_conn.scard(key)
            
        elif command == RedisCommand.SMEMBERS:
            val = await redis_conn.smembers(key)
            return [v.decode() for v in val] if val else []
            
        elif command == RedisCommand.ZCARD:
            return await redis_conn.zcard(key)
            
        elif command == RedisCommand.TYPE:
            return await redis_conn.type(key)
            
        else:
            raise ValueError(f"Command {command} not implemented")
    
    def _create_error_result(
        self,
        command: Union[str, RedisCommand],
        key: str,
        error: str,
        suggestion: str
    ) -> Dict[str, Any]:
        """Create an error result dictionary.
        
        Args:
            command: Command that failed
            key: Target key
            error: Error message
            suggestion: Fix suggestion
            
        Returns:
            Error result dictionary
        """
        return RedisInspectionResult(
            status="ERROR",
            command=RedisCommand(command) if isinstance(command, str) else command,
            key=key,
            error_msg=error,
            suggestion=suggestion
        ).model_dump()
    
    async def inspect_workflow_state(self, workflow_id: str) -> Dict[str, Any]:
        """Convenience method to inspect workflow state.
        
        Args:
            workflow_id: ID of the workflow to inspect
            
        Returns:
            Workflow state information
        """
        results = {}
        
        # Check workflow exists
        exists = await self.execute_inspection("EXISTS", f"workflow:{workflow_id}")
        results["exists"] = exists
        
        if exists.get("value"):
            # Get workflow data
            data = await self.execute_inspection("HGETALL", f"workflow:{workflow_id}")
            results["data"] = data
            
            # Check checkpoints
            checkpoints = await self.execute_inspection(
                "LRANGE",
                f"workflow:{workflow_id}:checkpoints",
                ["-10", "-1"]
            )
            results["recent_checkpoints"] = checkpoints
            
            # Check current step
            current_step = await self.execute_inspection("GET", f"workflow:{workflow_id}:current_step")
            results["current_step"] = current_step
        
        return results
    
    async def inspect_queue_status(self, queue_name: str = "high_priority") -> Dict[str, Any]:
        """Convenience method to inspect queue status.
        
        Args:
            queue_name: Name of the queue (without prefix)
            
        Returns:
            Queue status information
        """
        queue_key = f"queue:{queue_name}"
        results = {}
        
        # Get queue depth
        depth = await self.execute_inspection("LLEN", queue_key)
        results["depth"] = depth
        
        # Get recent jobs (last 5)
        recent = await self.execute_inspection("LRANGE", queue_key, ["-5", "-1"])
        results["recent_jobs"] = recent
        
        # Check processing queue
        processing = await self.execute_inspection("LLEN", f"{queue_key}:processing")
        results["processing"] = processing
        
        return results
    
    async def inspect_memory_usage(self) -> Dict[str, Any]:
        """Inspect memory usage statistics.
        
        Returns:
            Memory usage information
        """
        results = {}
        
        # Get metrics
        metrics = await self.execute_inspection("HGETALL", "metrics:memory")
        results["metrics"] = metrics
        
        # Check cache hit rates
        cache_stats = await self.execute_inspection("HGETALL", "cache:stats")
        results["cache_stats"] = cache_stats
        
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """Get inspection statistics."""
        total = self.stats["total_inspections"]
        if total == 0:
            return self.stats
        
        stats = self.stats.copy()
        stats["success_rate"] = self.stats["successful_inspections"] / total
        stats["failure_rate"] = self.stats["failed_inspections"] / total
        stats["access_denial_rate"] = self.stats["access_denied"] / total
        
        # Most used commands
        stats["most_used_commands"] = sorted(
            self.stats["commands_used"].items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        return stats
    
    def reset_stats(self) -> None:
        """Reset inspection statistics."""
        for key in self.stats:
            if key == "commands_used":
                for cmd in self.stats[key]:
                    self.stats[key][cmd] = 0
            else:
                self.stats[key] = 0


# Factory function and MCP integration
def create_redis_inspector_config(cache_client) -> 'ToolConfig':
    """Create a ToolConfig for Redis Inspector integration with HardenedMCPExecutor.
    
    Args:
        cache_client: HardenedCacheClient instance
        
    Returns:
        ToolConfig instance
    """
    inspector = HardenedRedisInspector(cache_client)
    
    # Note: ToolConfig should be imported from hardened_mcp_executor
    return ToolConfig(
        name="inspect_memory",
        function=inspector.execute_inspection,
        timeout_seconds=2.0,  # Fast operations only
        max_retries=1,
        fallback_function=None,  # No fallback; if memory is unreadable, we must know
        description="Inspect Redis memory state with read-only operations",
        parameters={
            "command": {
                "type": "string",
                "description": "Redis command (GET, HGETALL, LLEN, LRANGE, EXISTS, SCARD, SMEMBERS, ZCARD, TYPE)",
                "required": True
            },
            "key": {
                "type": "string",
                "description": "Redis key (must start with allowed prefix)",
                "required": True
            },
            "args": {
                "type": "array",
                "description": "Additional arguments for the command",
                "required": False
            }
        }
    )


# Factory function
def create_redis_inspector(cache_client) -> HardenedRedisInspector:
    """Create a configured Redis Inspector.
    
    Args:
        cache_client: HardenedCacheClient instance
        
    Returns:
        HardenedRedisInspector instance
    """
    return HardenedRedisInspector(cache_client)
