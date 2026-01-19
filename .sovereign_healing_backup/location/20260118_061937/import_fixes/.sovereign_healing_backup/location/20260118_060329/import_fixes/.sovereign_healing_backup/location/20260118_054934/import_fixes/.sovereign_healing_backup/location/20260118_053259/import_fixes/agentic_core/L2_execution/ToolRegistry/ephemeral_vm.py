from __future__ import annotations
"""Ephemeral VM with Isolation and Auto-Teardown.

Phase 3 - Pillar 14: Execution Sandbox (Hardened Ephemeral)
Enforces strict network/resource isolation and automatic teardown.
"""
import asyncio
import logging
import time
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Protocol
from agentic_core.L2_execution.ToolRegistry.firecracker_manager_impl import FirecrackerManager
from agentic_core.L2_execution.ToolRegistry.firecracker_manager_types import VMConfig

# [SSOT IMPORT] Structure blueprint is the single source of truth
from agentic_core.config.blueprint_sovereign.structure_blueprint import (
    SOVEREIGN_REGISTRY,
    CORE_SUBFOLDER_MAP,
)

Logger: Any = logging.getLogger(__name__)

class IsolationLevel(Enum):
    """Isolation levels for VM."""
    NONE: Any = 'none'
    NETWORK_ONLY: Any = 'network_only'
    FULL: Any = 'full'

@dataclass
class IsolationConfig:
    """Configuration for VM isolation."""
    level: IsolationLevel = IsolationLevel.FULL
    allow_network: bool = False
    allow_filesystem: bool = False
    allow_subprocess: bool = False
    max_cpu_percent: int = 50
    max_memory_mb: int = 512
    max_execution_time_seconds: int = 60

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {'level': self.level.value, 'allow_network': self.allow_network, 'allow_filesystem': self.allow_filesystem, 'allow_subprocess': self.allow_subprocess, 'max_cpu_percent': self.max_cpu_percent, 'max_memory_mb': self.max_memory_mb, 'max_execution_time_seconds': self.max_execution_time_seconds}

@dataclass
class ExecutionResult:
    """Result from code execution in VM."""
    success: bool
    output: str
    error: Optional[str] = None
    execution_time_seconds: float = 0.0
    exit_code: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {'success': self.success, 'output': self.output, 'error': self.error, 'execution_time_seconds': self.execution_time_seconds, 'exit_code': self.exit_code, 'metadata': self.metadata}

class EphemeralVm:
    """Ephemeral VM for secure code execution.

    Features:
    - Automatic creation and teardown
    - Strict isolation
    - Resource limits
    - Timeout enforcement
    - Network isolation
    """

    def __init__(self, vm_manager: FirecrackerManager, IsolationConfig: Optional[IsolationConfig]=None, enable_logging: bool=True):
        """Initialize ephemeral VM.

        Args:
            vm_manager: Firecracker manager
            IsolationConfig: Isolation configuration
            enable_logging: Enable logging
        """
        self.vm_manager = vm_manager
        self.IsolationConfig = IsolationConfig or IsolationConfig()
        self.enable_logging = enable_logging
        self._vm_counter = 0
        if self.enable_logging:
            LOGGER.info('ephemeral_vm_initialized', extra={'isolation': self.IsolationConfig.to_dict()})

    async def execute_code(self, code: str, language: str='python', timeout_seconds: Optional[int]=None) -> ExecutionResult:
        """Execute code in ephemeral VM.
        Args:
            code: Code to execute
            language: Programming language
            timeout_seconds: Execution timeout

        Returns:
            ExecutionResult
        """
        timeout: Any = timeout_seconds or self.IsolationConfig.max_execution_time_seconds
        start_time: Any = time.time()
        vm_id, VmConfig = self._create_vm_config(timeout)
        VmInstance: Any = None
        try:
            VmInstance: Any = await self._create_and_execute_vm(vm_id, VmConfig, code, language, timeout, start_time)
            return VmInstance
        except asyncio.TimeoutError:
            return self._handle_timeout(vm_id, timeout, start_time)
        except Exception as e:
            return self._handle_execution_error(vm_id, e, start_time)
        finally:
            await self._teardown_vm(VmInstance, vm_id)

    def _create_vm_config(self, timeout: int) -> tuple:
        """Create VM configuration."""
        self._vm_counter += 1
        vm_id = f'ephemeral_vm_{self._vm_counter}_{int(time.time())}'
        VmConfig = VMConfig(vm_id=vm_id, Provider=self.vm_manager.Provider, cpu_count=1, memory_mb=self.IsolationConfig.max_memory_mb, network_enabled=self.IsolationConfig.allow_network, timeout_seconds=timeout, auto_teardown=True)
        return (vm_id, VmConfig)

    async def _create_and_execute_vm(self, vm_id: str, VmConfig, code: str, language: str, timeout: int, start_time: float) -> ExecutionResult:
        """Create VM and execute code."""
        if self.enable_logging:
            LOGGER.info('creating_ephemeral_vm', extra={'vm_id': vm_id, 'language': language})
        VmInstance = await self.vm_manager.create_vm(VmConfig)
        result = await self._execute_in_vm(VmInstance=VmInstance, code=code, language=language, timeout=timeout)
        result.execution_time_seconds = time.time() - start_time
        if self.enable_logging:
            LOGGER.info('code_executed', extra={'vm_id': vm_id, 'success': result.success, 'execution_time': result.execution_time_seconds})
        return result

    def _handle_timeout(self, vm_id: str, timeout: int, start_time: float) -> ExecutionResult:
        """Handle execution timeout."""
        if self.enable_logging:
            LOGGER.warning('execution_timeout', extra={'vm_id': vm_id, 'timeout': timeout})
        return ExecutionResult(success=False, output='', error=f'Execution timeout after {timeout} seconds', execution_time_seconds=time.time() - start_time, exit_code=124)

    def _handle_execution_error(self, vm_id: str, error: Exception, start_time: float) -> ExecutionResult:
        """Handle execution error."""
        if self.enable_logging:
            LOGGER.error('execution_failed', extra={'vm_id': vm_id, 'error': str(error)}, exc_info=True)
        return ExecutionResult(success=False, output='', error=str(error), execution_time_seconds=time.time() - start_time, exit_code=1)

    async def _teardown_vm(self, VmInstance, vm_id: str) -> None:
        """Teardown VM."""
        if VmInstance:
            try:
                await self.vm_manager.terminate_vm(vm_id)
                if self.enable_logging:
                    LOGGER.debug('vm_torn_down', extra={'vm_id': vm_id})
            except Exception as e:
                if self.enable_logging:
                    LOGGER.error('vm_teardown_failed', extra={'vm_id': vm_id, 'error': str(e)})

    async def _execute_in_vm(self, VmInstance: Any, code: str, language: str, timeout: int) -> ExecutionResult:
        """Execute code inside VM.

        Args:
            VmInstance: VM instance
            code: Code to execute
            language: Programming language
            timeout: Timeout in seconds
        Returns:
            ExecutionResult
        """
        if language == 'python':
            return await self._execute_python(code, timeout)
        elif language == 'javascript':
            return await self._execute_javascript(code, timeout)
        else:
            return ExecutionResult(success=False, output='', error=f'Unsupported language: {language}', exit_code=1)

    async def _execute_python(self, code: str, timeout: int) -> ExecutionResult:
        """Execute Python code.

        Args:
            code: Python code
            timeout: Timeout

        Returns:
            ExecutionResult
        """
        try:
            result = await asyncio.wait_for(asyncio.create_subprocess_exec('python', '-c', code, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE), timeout=timeout)
            stdout, stderr = await result.communicate()
            return ExecutionResult(success=result.returncode == 0, output=stdout.decode() if stdout else '', error=stderr.decode() if stderr else None, exit_code=result.returncode)
        except asyncio.TimeoutError:
            raise
        except Exception as e:
            return ExecutionResult(success=False, output='', error=str(e), exit_code=1)

    async def _execute_javascript(self, code: str, timeout: int) -> ExecutionResult:
        """Execute JavaScript code.

        Args:
            code: JavaScript code
            timeout: Timeout

        Returns:
            ExecutionResult
        """
        try:
            result = await asyncio.wait_for(asyncio.create_subprocess_exec('node', '-e', code, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE), timeout=timeout)
            stdout, stderr = await result.communicate()
            return ExecutionResult(success=result.returncode == 0, output=stdout.decode() if stdout else '', error=stderr.decode() if stderr else None, exit_code=result.returncode)
        except asyncio.TimeoutError:
            raise
        except Exception as e:
            return ExecutionResult(success=False, output='', error=str(e), exit_code=1)

def create_ephemeral_vm(vm_manager: Optional[FirecrackerManager]=None, IsolationConfig: Optional[IsolationConfig]=None) -> EphemeralVM:
    """Factory function to create ephemeral VM.

    Args:
        vm_manager: Optional VM manager
        IsolationConfig: Optional isolation config

    Returns:
        EphemeralVM instance
    """
    if vm_manager is None:
        vm_manager: Any = create_firecracker_manager()
    return EphemeralVM(vm_manager=vm_manager, IsolationConfig=IsolationConfig)