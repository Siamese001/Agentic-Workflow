"""
Hardened MCP Executor - Safe Tool Execution with Timeouts and Isolation.

Implements a robust MCP tool executor with:
- Process isolation using asyncio subprocess
- Configurable timeouts with graceful termination
- Resource limits (memory, CPU)
- Input/output sanitization
- Comprehensive error handling and logging
"""

import logging
import asyncio
import json
import signal
import psutil
import tempfile
import shutil
from typing import Any, Dict, List, Optional, Union, Callable
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, field
from pydantic import BaseModel, Field
from enum import Enum
import traceback
import os
import sys

logger = logging.getLogger(__name__)

class ExecutionStatus(str, Enum):
    """Status of tool execution."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    TIMEOUT = "timeout"
    FAILED = "failed"
    KILLED = "killed"
    CANCELLED = "cancelled"

class ResourceLimitType(str, Enum):
    """Types of resource limits."""
    MEMORY = "memory"
    CPU_TIME = "cpu_time"
    WALL_TIME = "wall_time"
    OUTPUT_SIZE = "output_size"

@dataclass
class ResourceLimits:
    """Resource limits for tool execution."""
    max_memory_mb: Optional[int] = None  # Memory limit in MB
    max_cpu_time_seconds: Optional[float] = None  # CPU time limit
    max_wall_time_seconds: Optional[float] = None  # Wall clock time limit
    max_output_size_mb: Optional[int] = None  # Output size limit in MB
    max_processes: Optional[int] = None  # Number of processes

    def to_rlimits(self) -> Dict[str, int]:
        """Convert to resource limit format for subprocess."""
        import resource

        limits = {}

        if self.max_memory_mb:
            limits[resource.RLIMIT_AS] = self.max_memory_mb * 1024 * 1024

        if self.max_cpu_time_seconds:
            limits[resource.RLIMIT_CPU] = int(self.max_cpu_time_seconds)

        if self.max_processes:
            limits[resource.RLIMIT_NPROC] = self.max_processes

        return limits

@dataclass
class ExecutionContext:
    """Context for tool execution."""
    tool_name: str
    tool_path: Union[str, Path]
    arguments: List[str]
    environment: Dict[str, str]
    working_directory: Optional[Path] = None
    input_data: Optional[str] = None
    timeout_seconds: float = 30.0
    resource_limits: ResourceLimits = field(default_factory=ResourceLimits)

    def __post_init__(self):
        if isinstance(self.tool_path, str):
            self.tool_path = Path(self.tool_path)
        if isinstance(self.working_directory, str):
            self.working_directory = Path(self.working_directory)

@dataclass
class ExecutionResult:
    """Result of tool execution."""
    status: ExecutionStatus
    exit_code: Optional[int] = None
    stdout: str = ""
    stderr: str = ""
    execution_time_seconds: float = 0.0
    peak_memory_mb: float = 0.0
    cpu_time_seconds: float = 0.0
    error_message: Optional[str] = None
    timed_out: bool = False
    killed: bool = False
    resource_usage: Dict[str, Any] = field(default_factory=dict)

class ProcessMonitor:
    """Monitors a subprocess for resource usage."""

    def __init__(self, pid: int):
        self.pid = pid
        self.process = psutil.Process(pid)
        self.peak_memory = 0.0
        self.start_time = time.time()
        self.cpu_times_start = self.process.cpu_times()

    def update(self) -> Dict[str, float]:
        """Update resource usage metrics."""
        try:
            # Memory usage
            memory_info = self.process.memory_info()
            memory_mb = memory_info.rss / (1024 * 1024)
            self.peak_memory = max(self.peak_memory, memory_mb)

            # CPU time
            cpu_times = self.process.cpu_times()
            cpu_time = sum(cpu_times) - sum(self.cpu_times_start)

            # Wall time
            wall_time = time.time() - self.start_time

            return {
                "memory_mb": memory_mb,
                "peak_memory_mb": self.peak_memory,
                "cpu_time_seconds": cpu_time,
                "wall_time_seconds": wall_time
            }
        except psutil.NoSuchProcess:
            return {}

    def terminate(self) -> bool:
        """Terminate the process gracefully."""
        try:
            self.process.terminate()
            return True
        except psutil.NoSuchProcess:
            return False

    def kill(self) -> bool:
        """Force kill the process."""
        try:
            self.process.kill()
            return True
        except psutil.NoSuchProcess:
            return False

class HardenedMCPExecutor:
    """
    Hardened MCP tool executor with isolation and safety.

    Features:
    - Process isolation using asyncio subprocess
    - Configurable timeouts with graceful termination
    - Resource limits (memory, CPU, output size)
    - Input/output sanitization
    - Comprehensive error handling
    """

    def __init__(
        self,
        default_timeout: float = 30.0,
        default_resource_limits: Optional[ResourceLimits] = None,
        temp_dir: Optional[Path] = None,
        enable_sandbox: bool = True
    ):
        """Initialize hardened MCP executor.

        Args:
            default_timeout: Default timeout for tool execution
            default_resource_limits: Default resource limits
            temp_dir: Temporary directory for execution
            enable_sandbox: Whether to enable sandboxing
        """
        self.default_timeout = default_timeout
        self.default_resource_limits = default_resource_limits or ResourceLimits()
        self.temp_dir = temp_dir or Path(tempfile.gettempdir()) / "mcp_executor"
        self.enable_sandbox = enable_sandbox

        # Ensure temp directory exists
        self.temp_dir.mkdir(parents=True, exist_ok=True)

        # Execution statistics
        self.stats = {
            "total_executions": 0,
            "successful_executions": 0,
            "failed_executions": 0,
            "timeout_executions": 0,
            "killed_executions": 0
        }

    async def execute_tool(
        self,
        context: ExecutionContext
    ) -> ExecutionResult:
        """Execute a tool with hardening.

        Args:
            context: Execution context with tool details

        Returns:
            ExecutionResult with execution details
        """
        self.stats["total_executions"] += 1

        # Validate context
        await self._validate_context(context)

        # Prepare execution environment
        exec_dir = await self._prepare_execution_dir(context)

        try:
            # Start execution
            result = await self._execute_with_monitoring(context, exec_dir)

            # Update statistics
            if result.status == ExecutionStatus.COMPLETED:
                self.stats["successful_executions"] += 1
            elif result.status == ExecutionStatus.TIMEOUT:
                self.stats["timeout_executions"] += 1
            elif result.status == ExecutionStatus.KILLED:
                self.stats["killed_executions"] += 1
            else:
                self.stats["failed_executions"] += 1

            return result

        finally:
            # Cleanup execution directory
            await self._cleanup_execution_dir(exec_dir)

    async def _validate_context(self, context: ExecutionContext) -> None:
        """Validate execution context."""
        if not context.tool_path.exists():
            raise ValueError(f"Tool not found: {context.tool_path}")

        if not context.tool_path.is_file():
            raise ValueError(f"Tool path is not a file: {context.tool_path}")

        # Check for dangerous commands
        dangerous_commands = ["rm -rf", "sudo", "su", "chmod 777", "dd if="]
        for arg in context.arguments:
            for dangerous in dangerous_commands:
                if dangerous in arg:
                    raise ValueError(f"Dangerous command detected: {arg}")

    async def _prepare_execution_dir(self, context: ExecutionContext) -> Path:
        """Prepare isolated execution directory."""
        import uuid

        exec_id = str(uuid.uuid4())[:8]
        exec_dir = self.temp_dir / f"exec_{exec_id}"
        exec_dir.mkdir(parents=True, exist_ok=True)

        # Copy tool to execution directory if sandboxing
        if self.enable_sandbox:
            tool_dest = exec_dir / context.tool_path.name
            shutil.copy2(context.tool_path, tool_dest)
            context.tool_path = tool_dest

        # Write input data if provided
        if context.input_data:
            input_file = exec_dir / "input.txt"
            input_file.write_text(context.input_data)

        return exec_dir

    async def _execute_with_monitoring(
        self,
        context: ExecutionContext,
        exec_dir: Path
    ) -> ExecutionResult:
        """Execute tool with monitoring."""
        start_time = time.time()
        result = ExecutionResult(status=ExecutionStatus.PENDING)

        # Prepare environment
        env = os.environ.copy()
        env.update(context.environment)

        # Add sandbox restrictions if enabled
        if self.enable_sandbox:
            env = self._apply_sandbox_env(env)

        try:
            # Start subprocess
            process = await asyncio.create_subprocess_exec(
                str(context.tool_path),
                *context.arguments,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                stdin=asyncio.subprocess.PIPE if context.input_data else None,
                cwd=context.working_directory or exec_dir,
                env=env,
                preexec_fn=self._apply_resource_limits(context.resource_limits) if sys.platform != "win32" else None
            )

            # Start monitoring
            monitor = ProcessMonitor(process.pid)

            # Write input if provided
            if context.input_data:
                process.stdin.write(context.input_data.encode())
                process.stdin.close()

            # Wait for completion with timeout
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=context.timeout_seconds
                )

                result.exit_code = process.returncode
                result.status = ExecutionStatus.COMPLETED if process.returncode == 0 else ExecutionStatus.FAILED

            except asyncio.TimeoutError:
                # Handle timeout
                logger.warning(f"Tool {context.tool_name} timed out after {context.timeout_seconds}s")

                # Try graceful termination
                if monitor.terminate():
                    await asyncio.sleep(1)  # Give it time to clean up

                # Force kill if still running
                if process.returncode is None:
                    monitor.kill()
                    await asyncio.sleep(0.5)

                result.status = ExecutionStatus.TIMEOUT
                result.timed_out = True
                result.exit_code = process.returncode

                # Get any remaining output
                stdout, stderr = await process.communicate()

            # Collect output
            result.stdout = stdout.decode('utf-8', errors='replace')
            result.stderr = stderr.decode('utf-8', errors='replace')

            # Sanitize output
            result.stdout = self._sanitize_output(result.stdout)
            result.stderr = self._sanitize_output(result.stderr)

            # Update resource usage
            usage = monitor.update()
            result.execution_time_seconds = usage.get("wall_time_seconds", 0)
            result.peak_memory_mb = usage.get("peak_memory_mb", 0)
            result.cpu_time_seconds = usage.get("cpu_time_seconds", 0)
            result.resource_usage = usage

            # Check resource violations
            await self._check_resource_violations(context, result, usage)

        except Exception as e:
            logger.error(f"Tool execution failed: {e}")
            result.status = ExecutionStatus.FAILED
            result.error_message = str(e)
            result.execution_time_seconds = time.time() - start_time

        return result

    def _apply_resource_limits(self, limits: ResourceLimits) -> Callable:
        """Apply resource limits to subprocess."""
        def limit_function():
            import resource

            rlimits = limits.to_rlimits()
            for resource_type, limit_value in rlimits.items():
                try:
                    resource.setrlimit(resource_type, (limit_value, limit_value))
                except (ValueError, OSError) as e:
                    logger.warning(f"Failed to set resource limit {resource_type}: {e}")

        return limit_function

    def _apply_sandbox_env(self, env: Dict[str, str]) -> Dict[str, str]:
        """Apply sandbox environment variables."""
        sandbox_env = env.copy()

        # Restrict PATH
        sandbox_env["PATH"] = "/usr/bin:/bin"

        # Disable dangerous environment variables
        dangerous_vars = ["LD_PRELOAD", "LD_LIBRARY_PATH", "PYTHONPATH"]
        for var in dangerous_vars:
            sandbox_env.pop(var, None)

        return sandbox_env

    def _sanitize_output(self, output: str) -> str:
        """Sanitize tool output."""
        if not output:
            return ""

        # Remove potential ANSI escape sequences
        import re
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        output = ansi_escape.sub('', output)

        # Truncate if too long
        max_length = 1024 * 1024  # 1MB
        if len(output) > max_length:
            output = output[:max_length] + "\n... [Output truncated]"

        return output

    async def _check_resource_violations(
        self,
        context: ExecutionContext,
        result: ExecutionResult,
        usage: Dict[str, float]
    ) -> None:
        """Check for resource limit violations."""
        violations = []

        if context.resource_limits.max_memory_mb:
            if usage.get("peak_memory_mb", 0) > context.resource_limits.max_memory_mb:
                violations.append(f"Memory exceeded: {usage.get('peak_memory_mb'):.1f}MB > {context.resource_limits.max_memory_mb}MB")

        if context.resource_limits.max_cpu_time_seconds:
            if usage.get("cpu_time_seconds", 0) > context.resource_limits.max_cpu_time_seconds:
                violations.append(f"CPU time exceeded: {usage.get('cpu_time_seconds'):.1f}s > {context.resource_limits.max_cpu_time_seconds}s")

        if violations:
            logger.warning(f"Resource violations for {context.tool_name}: {'; '.join(violations)}")
            result.error_message = "; ".join(violations)

    async def _cleanup_execution_dir(self, exec_dir: Path) -> None:
        """Clean up execution directory."""
        try:
            if exec_dir.exists():
                shutil.rmtree(exec_dir)
        except Exception as e:
            logger.warning(f"Failed to cleanup execution directory {exec_dir}: {e}")

    async def execute_with_fallback(
        self,
        primary_context: ExecutionContext,
        fallback_contexts: List[ExecutionContext]
    ) -> ExecutionResult:
        """Execute tool with fallback options.

        Args:
            primary_context: Primary execution context
            fallback_contexts: List of fallback contexts to try

        Returns:
            ExecutionResult from first successful execution
        """
        contexts = [primary_context] + fallback_contexts

        for i, context in enumerate(contexts):
            try:
                result = await self.execute_tool(context)

                if result.status == ExecutionStatus.COMPLETED:
                    if i > 0:
                        logger.info(f"Tool {context.tool_name} succeeded with fallback #{i}")
                    return result

            except Exception as e:
                logger.warning(f"Tool {context.tool_name} failed with attempt {i+1}: {e}")
                continue

        # All attempts failed
        raise RuntimeError(f"All execution attempts failed for {primary_context.tool_name}")

    def get_stats(self) -> Dict[str, Any]:
        """Get execution statistics."""
        total = self.stats["total_executions"]
        if total == 0:
            return self.stats

        stats = self.stats.copy()
        stats["success_rate"] = self.stats["successful_executions"] / total
        stats["failure_rate"] = self.stats["failed_executions"] / total
        stats["timeout_rate"] = self.stats["timeout_executions"] / total

        return stats

    async def cleanup(self) -> None:
        """Clean up resources."""
        # Clean up any remaining execution directories
        try:
            for item in self.temp_dir.iterdir():
                if item.is_dir() and item.name.startswith("exec_"):
                    # Check if it's older than 1 hour
                    if time.time() - item.stat().st_mtime > 3600:
                        shutil.rmtree(item)
        except Exception as e:
            logger.warning(f"Failed to cleanup temp directories: {e}")

# Factory function for creating hardened MCP executor
def create_hardened_mcp_executor(
    default_timeout: float = 30.0,
    default_resource_limits: Optional[ResourceLimits] = None,
    temp_dir: Optional[Path] = None,
    enable_sandbox: bool = True
) -> HardenedMCPExecutor:
    """Create a hardened MCP executor.

    Args:
        default_timeout: Default timeout for executions
        default_resource_limits: Default resource limits
        temp_dir: Temporary directory for execution
        enable_sandbox: Whether to enable sandboxing

    Returns:
        HardenedMCPExecutor instance
    """
    return HardenedMCPExecutor(
        default_timeout=default_timeout,
        default_resource_limits=default_resource_limits,
        temp_dir=temp_dir,
        enable_sandbox=enable_sandbox
    )
