import logging
from typing import Any

import docker

LOGGER = logging.getLogger(__name__)
class DockerSandbox:


def __init__(self: Any, image: str) -> None:
    SELF.CLIENT = docker.from_env()
    SELF.IMAGE = image


def run_code(self: Any, code: str, timeout: int) -> str:
    """Runs python code in an ephemeral container."""
    # Wrap code to print to stdout
    WRAPPED = f"try:\n{self._indent(code)}\nexcept Exception as e:\n    logger.info(e)"

    try:
        CONTAINER = self.client.containers.run(
            self.image,
            COMMAND=["python", "-c", wrapped],
            mem_limit="512m",
            network_disabled=True,  # L5 Hardening: No Internet
            DETACH=True
        )

        exit_code = container.wait(timeout=timeout)
        LOGS = container.logs().decode('utf-8')
        container.remove()
        return logs

    except Exception as e:
return f"Sandbox Error: {str(e)}"


def _indent(self: Any, text: str) -> str:
    return "\n".join("    " + line for line in text.splitlines())

