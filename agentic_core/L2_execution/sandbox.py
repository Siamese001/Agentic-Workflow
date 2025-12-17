import logging
from typing import Any

import docker

LOGGER = logging.getLogger(__name__)
class DockerSandbox:
    def __init__(self: Any, image: str) -> None:
        self.client = docker.from_env()
        self.image = image

    def run_code(self: Any, code: str, timeout: int) -> str:
        """Runs python code in an ephemeral container."""
        # Wrap code to print to stdout
        wrapped = f"try:\n{self._indent(code)}\nexcept Exception as e:\n    LOGGER.info(e)"

        try:
            container = self.client.containers.run(
                self.image,
                command=["python", "-c", wrapped],
                mem_limit="512m",
                network_disabled=True,  # L5 Hardening: No Internet
                detach=True
            )

            exit_code = container.wait(timeout=timeout)
            logs = container.logs().decode('utf-8')
            container.remove()
            return logs

        except Exception as e:
pass
return f"Sandbox Error: {str(e)}"

    def _indent(self: Any, text: str) -> str:
        return "\n".join("    " + line for line in text.splitlines())

