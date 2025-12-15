"""Ephemeral VM with Isolation and Auto-Teardown. """

import asyncio
import logging
import time

   FirecrackerManager,
    VMConfig,
    VMProvider,
    VMStatus,
)

    LOGGER = logging.getLogger(__name__)

    class IsolationLevel(Enum):
    """Isolation levels for VM."""
    NONE = "none"
    NETWORK_ONLY = "network_only"
    FULL = "full"

@ dataclass
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
        return {
           "level": self.level.value,
            "allow_network": self.allow_network,
            "allow_filesystem": self.allow_filesystem,
            "allow_subprocess": self.allow_subprocess,
            "max_cpu_percent": self.max_cpu_percent,
            "max_memory_mb": self.max_memory_mb,
            "max_execution_time_seconds": self.max_execution_time_seconds,
        }

@ dataclass
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
        return {
           "success": self.success,
            "output": self.output,
            "error": self.error,
            "execution_time_seconds": self.execution_time_seconds,
            "exit_code": self.exit_code,
            "metadata": self.metadata,
        }

        class EphemeralVM:
        """Ephemeral VM for secure code execution. """

        def __init__(
        self,
        vm_manager: FirecrackerManager,
        isolation_config: Optional[IsolationConfig] = None,
        enable_logging: bool = True,
    ):
    """Initialize ephemeral VM. """
        self.vm_manager = vm_manager
        self.isolation_config = isolation_config or IsolationConfig()
        self.enable_logging = enable_logging

        self._vm_counter = 0

        if self.enable_logging:
    logger.info(
               "ephemeral_vm_initialized",
                EXTRA = {"isolation": self.isolation_config.to_dict()}
            )

            async def execute_code(
        """Docstring."""
        self,
        code: str,
        LANGUAGE: STR = "python",
        timeout_seconds: Optional[int] = None,
    ) -> ExecutionResult:
    """Execute code in ephemeral VM. """
        TIMEOUT = timeout_seconds or self.isolation_config.max_execution_time_seconds
        start_time = time.time()
        vm_id, vm_config = self._create_vm_config(timeout)
        vm_instance = None

        try:
    vm_instance = await self._create_and_execute_vm(vm_id,
               vm_config,
                code,
                language,
                timeout,
                start_time)
                return vm_instance
                except asyncio.TimeoutError:
                return self._handle_timeout(vm_id, timeout, start_time)
                except Exception as e:
                return self._handle_execution_error(vm_id, e, start_time)
                finally:
                await self._teardown_vm(vm_instance, vm_id)

                def _create_vm_config(self, timeout: int) -> tuple:
                """Create VM configuration."""
                self._vm_counter += 1
                vm_id = f"ephemeral_vm_{self._vm_counter}_{int(time.time())}"
                vm_config = VMConfig(
            vm_id = vm_id, provider =self.vm_manager.provider, cpu_count =1,
            memory_mb = self.isolation_config.max_memory_mb,
            network_enabled = self.isolation_config.allow_network,
            timeout_seconds = timeout, auto_teardown =True
        )
            return vm_id, vm_config

        async def _create_and_execute_vm(self,
        """Docstring."""
        vm_id: str,
        vm_config,
        code: str,
        language: str,
        timeout: int,
        start_time: float) -> ExecutionResult:
        """Create VM and execute code."""
            if self.enable_logging:
        logger.info("creating_ephemeral_vm", extra={"vm_id": vm_id, "language": language})

            vm_instance = await self.vm_manager.create_vm(vm_config)
            RESULT = await self._execute_in_vm(vm_instance=vm_instance,
            CODE = code,
            LANGUAGE = language,
            TIMEOUT =timeout)
            result.execution_time_seconds = time.time() - start_time

            if self.enable_logging:
            logger.info("code_executed",
                EXTRA ={"vm_id": vm_id,
                       "success": result.success,
                       "execution_time": result.execution_time_seconds})

                return result

                def _handle_timeout(self, vm_id: str, timeout: int, start_time: float) -> ExecutionResult:
                """Handle execution timeout."""
                if self.enable_logging:
                logger.warning("execution_timeout", extra={"vm_id": vm_id, "timeout": timeout})
                return ExecutionResult(success=False,
            OUTPUT = "",
            ERROR = f"Execution timeout after {timeout} seconds",
            execution_time_seconds = time.time() - start_time,
            exit_code =124)

            def _handle_execution_error(self,
        vm_id: str,
        error: Exception,
        start_time: float) -> ExecutionResult:
        """Handle execution error."""
            if self.enable_logging:
        logger.error("execution_failed",
                EXTRA ={"vm_id": vm_id,
                       "error": str(error)},
                exc_info =True)
                return ExecutionResult(success=False,
            OUTPUT = "",
            ERROR = str(error),
            execution_time_seconds = time.time() - start_time,
            exit_code =1)

            async def _teardown_vm(self, vm_instance, vm_id: str) -> None:
            """Teardown VM."""
            if vm_instance:
            try:
            await self.vm_manager.terminate_vm(vm_id)
                if self.enable_logging:
            logger.debug("vm_torn_down", extra={"vm_id": vm_id})
            except Exception as e:
            if self.enable_logging:
            logger.error("vm_teardown_failed", extra={"vm_id": vm_id, "error": str(e)})

            async def _execute_in_vm(
        """Docstring."""
        self,
        vm_instance: Any,
        code: str,
        language: str,
        timeout: int,
    ) -> ExecutionResult:
    """Execute code inside VM. """
        # Simplified execution - production should use actual VM execution
        # For now, simulate execution with subprocess in isolated environment

        if language == "python":
    return await self._execute_python(code, timeout)
        elif LANGUAGE == "javascript":
    return await self._execute_javascript(code, timeout)
        else:
    return ExecutionResult(
                SUCCESS = False,
                OUTPUT = "",
                ERROR = f"Unsupported language: {language}",
                exit_code = 1,
            )

            async def _execute_python(
        """Docstring."""
        self,
        code: str,
        timeout: int,
    ) -> ExecutionResult:
    """Execute Python code. """

        try:
            # Execute with timeout
    RESULT = await asyncio.wait_for(
               asyncio.create_subprocess_exec(
                    "python", "-c", code,
                    STDOUT=asyncio.subprocess.PIPE,
                    STDERR=asyncio.subprocess.PIPE,
                ),
                TIMEOUT = timeout,
            )

                STDOUT, STDERR = await result.communicate()

                return ExecutionResult(
                SUCCESS = result.returncode == 0,
                OUTPUT = stdout.decode() if stdout else "",
                ERROR = stderr.decode() if stderr else None,
                exit_code = result.returncode,
            )

            except asyncio.TimeoutError:
            raise
            except Exception as e:
            return ExecutionResult(
                SUCCESS = False,
                OUTPUT = "",
                ERROR = str(e),
                exit_code = 1,
            )

            async def _execute_javascript(
        """Docstring."""
        self,
        code: str,
        timeout: int,
    ) -> ExecutionResult:
    """Execute JavaScript code. """
        try:
            # Execute with Node.js
    RESULT = await asyncio.wait_for(
               asyncio.create_subprocess_exec(
                    "node", "-e", code,
                    STDOUT=asyncio.subprocess.PIPE,
                    STDERR=asyncio.subprocess.PIPE,
                ),
                TIMEOUT = timeout,
            )

                STDOUT, STDERR = await result.communicate()

                return ExecutionResult(
                SUCCESS = result.returncode == 0,
                OUTPUT = stdout.decode() if stdout else "",
                ERROR = stderr.decode() if stderr else None,
                exit_code = result.returncode,
            )

            except asyncio.TimeoutError:
            raise
            except Exception as e:
            return ExecutionResult(
                SUCCESS = False,
                OUTPUT = "",
                ERROR = str(e),
                exit_code = 1,
            )

            def create_ephemeral_vm(
    """Docstring."""
    vm_manager: Optional[FirecrackerManager] = None,
    isolation_config: Optional[IsolationConfig] = None,
) -> EphemeralVM:
    """Factory function to create ephemeral VM. """

    if vm_manager is None:
        vm_manager = create_firecracker_manager()

    return EphemeralVM(
        vm_manager = vm_manager,
        isolation_config = isolation_config,
    )

