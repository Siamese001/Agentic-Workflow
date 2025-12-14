"""
Docker Sandbox for Safe Code Execution

Provides an ephemeral execution environment where agents can run dangerous code
without destroying your laptop. Spins up containers, captures output, and nukes them.
"""

import asyncio
import logging
from dataclasses import dataclass
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

try:
    import docker
    DOCKER_AVAILABLE = True
except ImportError:
    DOCKER_AVAILABLE = False
    logger.warning("Docker library not available. Install with: pip install docker")


@dataclass
class ExecutionResult:
    """Result of code execution in sandbox."""
    stdout: str
    stderr: str
    exit_code: int
    files_created: List[str]
    execution_time_ms: float


class DockerSandbox:
    """
    An ephemeral execution environment.
    Spins up a container, runs the agent's code, captures output, and nukes the container.
    """
    
    def __init__(self, image: str = "python:3.10-slim", network_disabled: bool = True):
        """
        Initialize the Docker sandbox.
        
        Args:
            image: Docker image to use for execution
            network_disabled: Whether to disable network access (security)
        """
        if not DOCKER_AVAILABLE:
            raise ImportError("Docker library not installed. Run: pip install docker")
        
        try:
            self.client = docker.from_env()
            self.client.ping()
        except Exception as e:
            raise RuntimeError(f"Docker daemon not available: {e}")
        
        self.image = image
        self.network_disabled = network_disabled
        
        logger.info(f"Docker sandbox initialized (image={image}, network_disabled={network_disabled})")
        
        self._ensure_image_available()

    def _ensure_image_available(self):
        """Ensure the Docker image is available locally."""
        try:
            self.client.images.get(self.image)
            logger.debug(f"Docker image {self.image} already available")
        except docker.errors.ImageNotFound:
            logger.info(f"Pulling Docker image: {self.image}")
            self.client.images.pull(self.image)
            logger.info(f"Docker image {self.image} pulled successfully")

    async def run_code(
        self, 
        code: str, 
        inputs: Optional[Dict] = None,
        timeout: int = 30
    ) -> ExecutionResult:
        """
        Execute code in an isolated Docker container.
        
        Args:
            code: Python code to execute
            inputs: Optional input data to pass to the code
            timeout: Execution timeout in seconds
            
        Returns:
            ExecutionResult with stdout, stderr, exit code, etc.
        """
        import time
        start_time = time.time()
        
        wrapper_code = self._create_wrapper(code, inputs or {})
        
        logger.debug(f"Executing code in sandbox (timeout={timeout}s)")
        
        try:
            container = self.client.containers.run(
                self.image,
                command=["python", "-c", wrapper_code],
                mem_limit="512m",
                network_disabled=self.network_disabled,
                detach=True,
                remove=False
            )
            
            try:
                result = container.wait(timeout=timeout)
                exit_code = result.get('StatusCode', 1)
            except Exception as e:
                logger.warning(f"Container execution timeout or error: {e}")
                container.kill()
                exit_code = 124
            
            logs = container.logs(stdout=True, stderr=True).decode('utf-8')
            
            stdout_lines = []
            stderr_lines = []
            for line in logs.split('\n'):
                if line.startswith('STDERR:'):
                    stderr_lines.append(line[7:])
                else:
                    stdout_lines.append(line)
            
            stdout = '\n'.join(stdout_lines)
            stderr = '\n'.join(stderr_lines)
            
            container.remove(force=True)
            
            execution_time = (time.time() - start_time) * 1000
            
            result = ExecutionResult(
                stdout=stdout.strip(),
                stderr=stderr.strip(),
                exit_code=exit_code,
                files_created=[],
                execution_time_ms=execution_time
            )
            
            if exit_code == 0:
                logger.info(f"Code executed successfully in {execution_time:.0f}ms")
            else:
                logger.warning(f"Code execution failed with exit code {exit_code}")
            
            return result
            
        except Exception as e:
            logger.error(f"Sandbox execution error: {e}")
            return ExecutionResult(
                stdout="",
                stderr=str(e),
                exit_code=1,
                files_created=[],
                execution_time_ms=(time.time() - start_time) * 1000
            )

    def _create_wrapper(self, code: str, inputs: Dict) -> str:
        """
        Create a wrapper script that handles inputs/outputs cleanly.
        
        Args:
            code: User code to wrap
            inputs: Input data
            
        Returns:
            Wrapped code string
        """
        indented_code = '\n'.join(['    ' + line for line in code.splitlines()])
        
        wrapper = f"""
import json
import sys

inputs = {repr(inputs)}

try:
{indented_code}
except Exception as e:
    print(f"STDERR:{{str(e)}}", file=sys.stderr)
    sys.exit(1)
"""
        return wrapper

    def _indent_code(self, code: str) -> str:
        """Indent code for wrapping."""
        return '\n'.join(['    ' + line for line in code.splitlines()])

    async def verify_code(self, code: str) -> bool:
        """
        Dry-run verification: Check if code is syntactically valid.
        
        Args:
            code: Code to verify
            
        Returns:
            True if code is valid, False otherwise
        """
        verification_code = f"""
import ast
import sys

code = '''{code}'''

try:
    ast.parse(code)
    print("VALID")
except SyntaxError as e:
    print(f"STDERR:Syntax error: {{e}}", file=sys.stderr)
    sys.exit(1)
"""
        
        result = await self.run_code(verification_code, timeout=5)
        return result.exit_code == 0 and "VALID" in result.stdout

    def cleanup(self):
        """Cleanup any lingering containers."""
        try:
            containers = self.client.containers.list(
                all=True,
                filters={"ancestor": self.image}
            )
            for container in containers:
                container.remove(force=True)
            logger.info(f"Cleaned up {len(containers)} containers")
        except Exception as e:
            logger.error(f"Cleanup error: {e}")


async def create_sandbox(
    image: str = "python:3.10-slim",
    network_disabled: bool = True
) -> DockerSandbox:
    """
    Factory function to create a Docker sandbox.
    
    Args:
        image: Docker image to use
        network_disabled: Whether to disable network access
        
    Returns:
        DockerSandbox instance
    """
    return DockerSandbox(image=image, network_disabled=network_disabled)
