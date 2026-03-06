"""
SSOT Scanner - Direct Filesystem Scanning Without Registry

Eliminates the need for agent_discovery_full.json by scanning the filesystem
directly and parsing AST on-demand. This provides always-current data without
the 15-18 second registry refresh overhead.

Performance: <1 second for full scan (vs 15-18s for registry rebuild)
"""

import ast
from dataclasses import dataclass
from pathlib import Path
from agentic_core.L0_routing.config import (
    ARCHIVES_DIR,
)


@dataclass
class AgentMetadata:
    """Metadata for a single agent file."""

    file_path: Path
    relative_path: str
    class_name: str
    layer: str
    assigned_layer: str
    base_classes: list[str]
    signals: set[str]

    @property
    def has_gravity_violation(self) -> bool:
        """
        Check if agent is in wrong layer (gravity violation).

        Only L0-L5 layers can have violations. APP and UNKNOWN are not violations.
        """
        # Skip if either layer is APP or UNKNOWN (not subject to gravity rules)
        if self.layer in ("APP", "UNKNOWN") or self.assigned_layer in ("APP", "UNKNOWN"):
            return False

        # Violation if actual layer doesn't match assigned layer
        return self.layer != self.assigned_layer

    @property
    def is_compliant(self) -> bool:
        """Check if agent is in correct Gospel-assigned layer."""
        return not self.has_gravity_violation


class SSOTScanner:
    """
    Direct filesystem scanner for SSOT enforcement.

    Replaces agent_discovery_full.json with instant, always-current scanning.
    Uses on-demand AST parsing to minimize overhead.
    """

    # Layer assignment rules from structure_blueprint.py
    LAYER_ASSIGNMENTS: dict[str, str] = {
        "L0_routing": "L0",
        "L1_cognition": "L1",
        "L2_execution": "L2",
        "L3_orchestration": "L3",
        "L4_state": "L4",
        "L5_safety": "L5",
        "observability": "L3",  # observability is L3 orchestration
        "utils": "L2",  # Utils are L2 execution tools
        "schemas": "L2",  # Schemas are L2 execution support
        "patterns": "L2",  # Patterns are L2 execution support
        "config": "L2",  # Config is L2 execution support
        "prompt_governance": "L2",  # Prompt governance is L2
        "runtime": "L2",  # Runtime is L2 execution
        "semantic_memory": "L2",  # Semantic memory is L2
    }

    # DEPRECATED: CANON_SIGNALS removed - replaced by dynamic validation
    # SOVEREIGN_SIGNALS: set[str] = {
    #     "healing",
    #     "testing",
    #     "validation",
    #     "execution",
    #     "orchestration",
    #     "state",
    #     "safety",
    #     "cognition",
    #     "intent",
    #     "learning",
    #     "planning",
    # }

    def __init__(self, project_root: Path):
        """
        Initialize SSOT scanner.

        Args:
            project_root: Root directory of the project
        """
        self.project_root = project_root.resolve()
        self._cache: dict[str, AgentMetadata] = {}

    def scan_agents(self, use_cache: bool = False) -> list[AgentMetadata]:
        """
        Scan filesystem for all agent files.

        Args:
            use_cache: If True, return cached results (for performance)

        Returns:
            List of agent metadata
        """
        if use_cache and self._cache:
            return list(self._cache.values())

        agents = []

        # Find all *Agent.py files
        # Operation Zero: Use ssot_discovery instead of glob
        from agentic_core.utils.ssot_discovery_validator import get_agent_files

        agent_files = list(get_agent_files(self.project_root))

        for agent_file in agent_files:
            # Skip vendor/cache directories
            if self._should_exclude(agent_file):
                continue

            try:
                metadata = self._parse_agent_file(agent_file)
                if metadata:
                    agents.append(metadata)
                    self._cache[str(agent_file)] = metadata
            # guardian: allow-silent-swallow
            except Exception:
                # Skip files that can't be parsed
                continue

        return agents

    def get_layer_assignment(self, file_path: Path) -> str:
        """
        Derive layer assignment from file path.

        Args:
            file_path: Path to agent file

        Returns:
            Layer assignment (L0-L5)
        """
        relative_path = file_path.relative_to(self.project_root)
        parts = relative_path.parts

        # Check if in agentic_core
        if parts[0] == "agentic_core" and len(parts) > 1:
            folder = parts[1]
            return self.LAYER_ASSIGNMENTS.get(folder, "UNKNOWN")

        # Apps are not assigned to layers
        if parts[0].startswith("apps_"):
            return "APP"

        return "UNKNOWN"

    def get_actual_layer(self, file_path: Path) -> str:
        """
        Get actual layer from file path (where file currently is).

        Args:
            file_path: Path to agent file

        Returns:
            Actual layer (L0-L5)
        """
        relative_path = file_path.relative_to(self.project_root)
        parts = relative_path.parts

        # Check if in agentic_core
        if parts[0] == "agentic_core" and len(parts) > 1:
            folder = parts[1]

            # Direct layer folders
            if folder.startswith("L") and folder[1].isdigit():
                return folder[:2]  # L0, L1, L2, etc.

            # Infrastructure folders map to layers
            return self.LAYER_ASSIGNMENTS.get(folder, "UNKNOWN")

        return "UNKNOWN"

    def find_gravity_violations(self) -> list[AgentMetadata]:
        """
        Find all agents with gravity violations (wrong layer).

        Checks agentic_core and apps_* folders.

        Returns:
            List of agents in wrong layers
        """
        agents = self.scan_agents()
        return [agent for agent in agents if agent.has_gravity_violation]

    def get_compliance_stats(self) -> dict[str, any]:
        """
        Get compliance statistics.

        Returns:
            Dictionary with compliance metrics
        """
        agents = self.scan_agents()
        violations = [a for a in agents if a.has_gravity_violation]

        return {
            "total_agents": len(agents),
            "compliant_agents": len(agents) - len(violations),
            "gravity_violations": len(violations),
            "compliance_percentage": round((len(agents) - len(violations)) / len(agents) * 100, 1)
            if agents
            else 100.0,
        }

    def _should_exclude(self, file_path: Path) -> bool:
        """Check if file should be excluded from scanning."""
        exclude_patterns = [
            ".venv",
            "venv",
            "node_modules",
            "__pycache__",
            ".git",
            ".pytest_cache",
            "vendor",
            ARCHIVES_DIR,
        ]

        path_str = str(file_path)
        return any(pattern in path_str for pattern in exclude_patterns)

    def _parse_agent_file(self, file_path: Path) -> AgentMetadata | None:
        """
        Parse agent file to extract metadata.

        Args:
            file_path: Path to agent file

        Returns:
            Agent metadata or None if not a valid agent
        """
        try:
            content = file_path.read_text(encoding="utf-8")
            tree = ast.parse(content)
        except (SyntaxError, UnicodeDecodeError):
            return None

        # Find agent class (aligned with classification kernel: endswith "Agent", exclude Mixin)
        agent_class = None
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if node.name.endswith("Agent") and "Mixin" not in node.name:
                    agent_class = node
                    break

        if not agent_class:
            return None

        # Extract base classes
        base_classes = []
        for base in agent_class.bases:
            if isinstance(base, ast.Name):
                base_classes.append(base.id)
            elif isinstance(base, ast.Attribute):
                base_classes.append(base.attr)

        # Extract signals from class body (simple heuristic)
        signals = self._extract_signals(content)

        # Get layer assignments
        actual_layer = self.get_actual_layer(file_path)
        assigned_layer = self.get_layer_assignment(file_path)

        relative_path = str(file_path.relative_to(self.project_root))

        return AgentMetadata(
            file_path=file_path,
            relative_path=relative_path.replace("\\", "/"),
            class_name=agent_class.name,
            layer=actual_layer,
            assigned_layer=assigned_layer,
            base_classes=base_classes,
            signals=signals,
        )

    def _extract_signals(self, content: str) -> set[str]:
        """
        Extract canonical signals from agent code.

        Args:
            content: File content

        Returns:
            Set of detected signals
        """
        signals = set()
        content_lower = content.lower()

        for signal in self.CANON_SIGNALS:
            if signal in content_lower:
                signals.add(signal)

        return signals
