import logging
import os
from typing import Dict, Optional, Tuple

import docker

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
        if not self.client:
            return -1, "Docker unavailable"

        container = None
        try:
            logger.info(f"Spinning up sandbox ({self.image}) for command: {command}")

            # Ensure image exists (pull if missing, silent failure if offline but image exists)
            try:
                self.client.images.get(self.image)
            except docker.errors.ImageNotFound:
                logger.info(f"Pulling image {self.image}...")
                self.client.images.pull(self.image)

            container = self.client.containers.run(
                self.image,
                command=f"sh -c '{command}'",
                volumes=volumes,
                working_dir=work_dir,
                environment=environment,
                detach=True,
                # NETWORK ISOLATION (Protocol 8 preview)
                # network_mode="none"
            )

            # Wait for result
            result = container.wait()
            logs = container.logs().decode('utf-8')
            exit_code = result['StatusCode']

            return exit_code, logs

        except Exception as e:
            logger.error(f"Sandbox execution failed: {e}")
            return -1, str(e)

        finally:
            if container:
                try:
                    container.remove(force=True)
                    logger.info("Sandbox container destroyed.")
                except Exception as e:
                    logger.warning(f"Failed to remove container: {e}")

    def execute_in_sandbox(repo_path: str, command: str) -> bool:
        """
        High-level wrapper to run a check in the repo safely.
        Mounts repo_path as Read-Only to /code, copies to /app, and executes.

        Args:
            repo_path: Path to the host repository.
            command: Command to run inside the sandbox.

        Returns:
            bool: True if command executed successfully (exit code 0), False otherwise.
        """
        sandbox = DockerSandbox()

        if not sandbox.client:
            logger.error("Skipping sandbox check: Docker unavailable.")
            # FAIL CLOSED: If we can't verify safety, we don't proceed.
            # Change to True if you want "Fail Open" (allow bypass if docker is down)
            return False

        abs_repo_path = os.path.abspath(repo_path)

        # Mount host repo to /code (Read-Only)
        volumes = {
            abs_repo_path: {'bind': '/code', 'mode': 'ro'}
        }

        # 1. Copy /code to /app (to allow writing .pyc or temp files without error)
        # 2. cd /app
        # 3. Run command
        safe_command = f"cp -r /code/. /app && cd /app && {command}"

        exit_code, logs = sandbox.run_command(safe_command, volumes=volumes)

        if exit_code != 0:
            logger.warning(f"Sandbox Check Failed (Exit Code {exit_code}):\n{logs}")
            return False

        logger.info("Sandbox Check Passed.")
        return True
