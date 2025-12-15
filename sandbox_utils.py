import docker
import os
import logging
import shutil
from typing import Optional, Dict, Tuple

# Configure logging
logger = logging.getLogger("DockerSandbox")
logging.basicConfig(level=logging.INFO)

class DockerSandbox:
    def __init__(self, image: str = "python:3.11-slim"):
        self.image = image
        self.client = None
        try:
            self.client = docker.from_env()
        except docker.errors.DockerException:
            logger.warning("Docker is not running or not installed. Sandbox capabilities are disabled.")
        except Exception as e:
            logger.warning(f"Failed to initialize Docker client: {e}")

    def run_command(self, 
                    command: str, 
                    work_dir: str = "/app", 
                    volumes: Optional[Dict[str, Dict[str, str]]] = None,
                    environment: Optional[Dict[str, str]] = None) -> Tuple[int, str]:
        """
        Runs a command in an ephemeral container.
        
        Args:
            command: The shell command to run.
            work_dir: Working directory inside container.
            volumes: Dict of host_path -> {'bind': container_path, 'mode': 'ro'/'rw'}
            environment: Env vars for the container.
            
        Returns:
            Tuple[int, str]: (exit_code, logs)
        """
        try:
            logger.info(f"Spinning up sandbox ({self.image}) for command: {command}")
            
            self.container = self.client.containers.run(
                self.image,
                command=f"sh -c '{command}'",
                volumes=volumes,
                working_dir=work_dir,
                environment=environment,
                detach=True,
                # NETWORK ISOLATION (Protocol 8 preview)
                # network_mode="none" # Uncomment to block internet access
            )
            
            # Wait for result
            result = self.container.wait()
            logs = self.container.logs().decode('utf-8')
            exit_code = result['StatusCode']
            
            return exit_code, logs
            
        except Exception as e:
            logger.error(f"Sandbox execution failed: {e}")
            return -1, str(e)
            
        finally:
            self.cleanup()

    def cleanup(self):
        """Destroys the container immediately."""
        if self.container:
            try:
                self.container.remove(force=True)
                logger.info("Sandbox container destroyed.")
            except Exception as e:
                logger.warning(f"Failed to remove container: {e}")

# Helper for integration
def execute_in_sandbox(repo_path: str, command: str) -> bool:
    """
    High-level wrapper to run a check in the repo safely.
    Mounts repo_path as Read-Only to /code.
    """
    sandbox = DockerSandbox()
    
    # Mount host repo to /code (Read-Only)
    volumes = {
        os.path.abspath(repo_path): {'bind': '/code', 'mode': 'ro'}
    }
    
    # We copy /code to /app so we can write/generate pycache without hurting host
    # Then run the target command
    safe_command = f"cp -r /code /app && cd /app && {command}"
    
    exit_code, logs = sandbox.run_command(safe_command, volumes=volumes)
    
    if exit_code != 0:
        logger.warning(f"Sandbox Check Failed:\n{logs}")
        return False
    
    logger.info("Sandbox Check Passed.")
    return True
