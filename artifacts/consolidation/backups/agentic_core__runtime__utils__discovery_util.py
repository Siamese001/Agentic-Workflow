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

from agentic_core.core.classification_kernel import is_agent_file

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
            # guardian: allow-silent-swallow
            except Exception as e:
                logger.warning(f"Failed to scan {file_path}: {e}")

        self.discovered_agents = agents
        logger.info(f"Discovered {len(agents)} agents across {len(python_files)} files")
        return agents

    def _scan_file_for_agents(self, file_path: Path) -> list[DiscoveredAgent]:
        """
        Scans a single Python file for agent classes.

        [REFACTORED 2026-02-08] Uses classification kernel (SSOT) to determine
        if a file is an agent. Only then extracts class metadata from AST.

        Args:
            file_path: Path to the Python file to scan

        Returns:
            List of discovered agents in the file
        """
        agents = []

        try:
            # SSOT: Use kernel to determine if this file is an agent
            if not is_agent_file(file_path):
                return agents

            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)

            # Find the primary agent class (name matching filename stem preferred)
            class_nodes = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
            if not class_nodes:
                return agents

            # Select primary class: prefer name matching stem, then first ending with 'Agent'
            import re as _re

            stem_clean = _re.sub(r"[^a-zA-Z0-9]", "", file_path.stem.lower())
            primary = None
            for node in class_nodes:
                if _re.sub(r"[^a-zA-Z0-9]", "", node.name.lower()) == stem_clean:
                    primary = node
                    break
            if primary is None:
                for node in class_nodes:
                    if node.name.endswith("Agent"):
                        primary = node
                        break
            if primary is None:
                primary = class_nodes[0]

            layer = self._determine_layer(file_path, primary)

            # Create a mock instance for testing
            instance = None
            try:
                class_ref = self._get_class_reference(file_path, primary.name)
                if class_ref:
                    instance = class_ref()
            # guardian: allow-silent-swallow
            except Exception:
                instance = Mock()

            agent = DiscoveredAgent(
                name=primary.name,
                layer=layer,
                instance=instance,
                class_ref=self._get_class_reference(file_path, primary.name) or type(primary.name, (), {}),
                file_path=file_path,
                module_path=self._get_module_path(file_path),
            )
            agents.append(agent)

        # guardian: allow-silent-swallow
        except Exception as e:
            logger.debug(f"Failed to parse {file_path}: {e}")

        return agents

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
