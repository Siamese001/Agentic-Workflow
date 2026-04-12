"""ADG CLI - Command line interface for ADG tools."""

from __future__ import annotations

from typing import Any


class CLICommand:
    """Represents a CLI command."""

    def __init__(self, name: str, description: str = "") -> None:
        """Initialize CLI command.

        Args:
            name: Command name
            description: Command description
        """
        self.name = name
        self.description = description

    def execute(self, *args: Any, **kwargs: Any) -> Any:
        """Execute the command.

        Returns:
            Command result
        """
        return None


def execute_command(command: str, *args: Any, **kwargs: Any) -> Any:
    """Execute a CLI command.

    Args:
        command: Command name to execute
        *args: Positional arguments
        **kwargs: Keyword arguments

    Returns:
        Command execution result
    """
    cmd = CLICommand(command)
    return cmd.execute(*args, **kwargs)


def build_artifact(name: str, config: dict[str, Any] | None = None) -> dict[str, Any]:
    """Build an artifact.

    Args:
        name: Artifact name
        config: Optional configuration

    Returns:
        Built artifact metadata
    """
    return {"name": name, "config": config or {}}


__all__ = [
    "CLICommand",
    "execute_command",
    "build_artifact",
]
