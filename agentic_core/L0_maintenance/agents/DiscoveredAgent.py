"""
Agentic Core Discovery Module

This module provides the core discovery functionality for the Agentic Workflow system.
It includes the DiscoveredAgent dataclass and AgentRegistry class for finding and
cataloging agents across the entire ecosystem.
"""

import ast
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from agentic_core.utils.ssot_discovery_validator import get_python_files

logger = logging.getLogger(__name__)


@dataclass
class DiscoveredAgent:
    """
    Represents a discovered agent in the ecosystem.

    Attributes:
        name: The name of the agent class
        layer: The architectural layer the agent belongs to
        instance: An instance of the agent (if available)
        class_ref: The class reference for the agent
        file_path: Path to the file containing the agent
        module_path: Python module path for imports
    """

    name: str
    layer: str
    instance: Any
    class_ref: type
    file_path: Path | None = None
    module_path: str | None = None


class AgentRegistry:
    """
    Discovers and catalogs agents across the Agentic Workflow ecosystem.
    """

    def __init__(self, project_root: Path | None = None):
        self.project_root = project_root or Path(__file__).parent.parent.parent.parent
        self.discovered_agents: list[DiscoveredAgent] = []

    def discover_all(self) -> list[DiscoveredAgent]:
        """
        Discovers all agents in the ecosystem.

        Returns:
            List of discovered agents
        """
        agents = []

        # Get all Python files in the project
        python_files = get_python_files(self.project_root)

        for file_path in python_files:
            try:
                file_agents = self._scan_file_for_agents(file_path)
                agents.extend(file_agents)
            except Exception as e:
                logger.warning(f"Failed to scan {file_path}: {e}")

        self.discovered_agents = agents
        logger.info(f"Discovered {len(agents)} agents across {len(python_files)} files")
        return agents

    def _scan_file_for_agents(self, file_path: Path) -> list[DiscoveredAgent]:
        """
        Scans a single Python file for agent classes.

        Args:
            file_path: Path to the Python file to scan

        Returns:
            List of discovered agents in the file
        """
        agents = []

        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Check if this class looks like an agent
                    if self._is_agent_class(node):
                        layer = self._determine_layer(file_path, node)

                        # Create a mock instance for testing
                        instance = None
                        try:
                            # Try to create an instance (may fail for abstract classes)
                            class_ref = self._get_class_reference(file_path, node.name)
                            if class_ref:
                                instance = class_ref()
                        except Exception:
                            # Fallback to mock instance
                            instance = Mock()

                        agent = DiscoveredAgent(
                            name=node.name,
                            layer=layer,
                            instance=instance,
                            class_ref=self._get_class_reference(file_path, node.name)
                            or type(node.name, (), {}),
                            file_path=file_path,
                            module_path=self._get_module_path(file_path),
                        )
                        agents.append(agent)

        except Exception as e:
            logger.debug(f"Failed to parse {file_path}: {e}")

        return agents

    def _is_agent_class(self, class_node: ast.ClassDef) -> bool:
        """
        Determines if a class node represents an agent.

        Args:
            class_node: AST class node to analyze

        Returns:
            True if this appears to be an agent class
        """
        # Check if class name ends with "Agent"
        if not class_node.name.endswith("Agent"):
            return False

        # Check if it has agent-like methods
        agent_methods = {"execute", "run", "process", "handle", "heal", "validate"}
        for node in class_node.body:
            if isinstance(node, ast.FunctionDef):
                if node.name in agent_methods:
                    return True

        # Check inheritance for agent-like base classes
        if class_node.bases:
            for base in class_node.bases:
                if isinstance(base, ast.Name) and base.name.endswith("Agent"):
                    return True

        return class_node.name.endswith("Agent")  # Fallback to naming convention

    def _determine_layer(self, file_path: Path, class_node: ast.ClassDef) -> str:
        """
        Determines the architectural layer for an agent based on its file location.

        Args:
            file_path: Path to the file containing the agent
            class_node: AST class node for the agent

        Returns:
            Layer name as string
        """
        path_str = str(file_path)

        # Map directory patterns to layers
        layer_mappings = {
            "L0_maintenance": "L0_maintenance",
            "L1_cognition": "L1_cognition",
            "L2_execution": "L2_execution",
            "L3_orchestration": "L3_orchestration",
            "L4_coordination": "L4_coordination",
            "L5_safety": "L5_safety",
            "L6_observability": "L6_observability",
            "tests": "tests",
            "test": "tests",
        }

        for pattern, layer in layer_mappings.items():
            if pattern in path_str:
                return layer

        return "unknown"

    def _get_class_reference(self, file_path: Path, class_name: str) -> type | None:
        """
        Attempts to get the actual class reference from a file.

        Args:
            file_path: Path to the file containing the class
            class_name: Name of the class to retrieve

        Returns:
            Class reference or None if not found
        """
        try:
            # This is a simplified implementation
            # In practice, you'd need proper module loading
            return None
        except Exception:
            return None

    def _get_module_path(self, file_path: Path) -> str:
        """
        Converts a file path to a Python module path.

        Args:
            file_path: Path to convert

        Returns:
            Module path as string
        """
        # Convert path to module path
        parts = file_path.parts
        if "agentic_core" in parts:
            start_idx = parts.index("agentic_core")
            module_parts = parts[start_idx:-1]  # Exclude filename
            module_parts = [p.replace(".py", "") for p in module_parts if not p.startswith("__")]
            return ".".join(module_parts)
        return str(file_path)


class Mock:
    """Mock class for testing purposes."""

    pass
