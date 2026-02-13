"""
Synthetic repository builder for testing blueprint and FCA.

Provides utilities to create temporary directory structures that mimic
the agentic_core layout for testing validation logic.
"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path


class RepoBuilder:
    """Builder for creating synthetic repository structures in tmp_path."""

    def __init__(self, root: Path):
        self.root = root
        self._created_files: list[Path] = []

    def create_layer(self, layer_name: str, subfolders: Sequence[str] | None = None) -> Path:
        """Create a layer directory with optional subfolders."""
        layer_path = self.root / "agentic_core" / layer_name
        layer_path.mkdir(parents=True, exist_ok=True)

        if subfolders:
            for sf in subfolders:
                (layer_path / sf).mkdir(parents=True, exist_ok=True)
                self._touch_init(layer_path / sf)

        self._touch_init(layer_path)
        return layer_path

    def create_lcd_layer(self, layer_name: str, extras: Sequence[str] | None = None) -> Path:
        """Create a layer with standard LCD subfolders + optional extras."""
        standard = ["config", "types", "reasoning", "enforcement", "validators", "utils"]
        all_subfolders = list(standard) + list(extras or [])
        return self.create_layer(layer_name, all_subfolders)

    def create_file(self, relative_path: str, content: str) -> Path:
        """Create a file with the given content."""
        file_path = self.root / relative_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")
        self._created_files.append(file_path)
        return file_path

    def create_agent_file(
        self,
        layer: str,
        subfolder: str,
        agent_name: str,
        base_class: str = "SovereignBaseAgent",
    ) -> Path:
        """Create an Agent class file in the specified location."""
        content = f'''"""Agent module for {agent_name}."""

class {agent_name}({base_class}):
    """A concrete agent class."""

    def execute(self):
        pass
'''
        path = f"agentic_core/{layer}/{subfolder}/{agent_name}.py"
        return self.create_file(path, content)

    def create_script_file(self, name: str, with_main: bool = True) -> Path:
        """Create a script-like module in L0_routing/scripts/."""
        content = '''"""Script module."""

def main():
    print("Running script")

'''
        if with_main:
            content += """if __name__ == "__main__":
    main()
"""
        path = f"agentic_core/L0_routing/scripts/{name}"
        return self.create_file(path, content)

    def create_types_file(self, layer: str, name: str, with_agent: bool = False) -> Path:
        """Create a types file, optionally with an embedded Agent class."""
        content = '''"""Types module."""
from dataclasses import dataclass

@dataclass
class SomeType:
    value: str
'''
        if with_agent:
            content += '''

class EmbeddedAgent:
    """An agent that shouldn't be in types/."""
    def execute(self):
        pass
'''
        path = f"agentic_core/{layer}/types/{name}"
        return self.create_file(path, content)

    def create_subprocess_file(self, layer: str, subfolder: str, name: str) -> Path:
        """Create a file that imports subprocess."""
        content = '''"""Module using subprocess."""
import subprocess

def run_command(cmd: str) -> str:
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout
'''
        path = f"agentic_core/{layer}/{subfolder}/{name}"
        return self.create_file(path, content)

    def create_nested_lcd(self, parent_domain: str, lcd_subfolder: str) -> Path:
        """Create a nested LCD subtree (violation)."""
        path = self.root / "agentic_core" / parent_domain / lcd_subfolder
        path.mkdir(parents=True, exist_ok=True)
        self._touch_init(path)
        return path

    def _touch_init(self, directory: Path) -> None:
        """Create __init__.py in directory."""
        init_file = directory / "__init__.py"
        if not init_file.exists():
            init_file.write_text('"""Package."""\n', encoding="utf-8")

    @property
    def created_files(self) -> list[Path]:
        """Return list of all created files."""
        return self._created_files.copy()


def build_minimal_repo(tmp_path: Path) -> RepoBuilder:
    """Build a minimal valid repository structure."""
    builder = RepoBuilder(tmp_path)

    # Create all L0-L6 layers with LCD subfolders
    builder.create_lcd_layer("L0_routing", extras=["scripts"])
    builder.create_lcd_layer("L1_cognition")
    builder.create_lcd_layer("L2_execution", extras=["tools"])
    builder.create_lcd_layer("L3_orchestration")
    builder.create_lcd_layer("L4_state", extras=["memory"])
    builder.create_lcd_layer("L5_safety")
    builder.create_lcd_layer("L6_observability", extras=["dashboards", "config"])

    # Create global territories
    for territory in [
        "base_agents",
        "runtime",
        "interfaces",
        "mixins",
        "knowledge",
        "prompt_governance",
        "config",
        "utils",
    ]:
        (tmp_path / "agentic_core" / territory).mkdir(parents=True, exist_ok=True)
        builder._touch_init(tmp_path / "agentic_core" / territory)

    return builder


def build_anomaly_repo(tmp_path: Path) -> RepoBuilder:
    """Build a repository with all anomaly types for testing."""
    builder = build_minimal_repo(tmp_path)

    # A: L5 subprocess anomalies
    builder.create_subprocess_file("L5_safety", "enforcement", "dashboard_e2_e_pipeline.py")
    builder.create_subprocess_file("L5_safety", "validators", "analysis_ops_validator.py")

    # C: L4 agents in wrong subfolder
    builder.create_agent_file("L4_state", "enforcement", "CachedStateLedgerAgent")
    builder.create_agent_file("L4_state", "memory", "CheckpointManagerAgent")

    # D: Embedded agents in non-reasoning
    builder.create_types_file("L5_safety", "code_detection_types.py", with_agent=True)

    # E: PascalCase in L0/scripts
    builder.create_file(
        "agentic_core/L0_routing/scripts/AgentAuditResult.py",
        "class AgentAuditResult:\n    pass\n",
    )

    # F: Test files in L0/scripts
    builder.create_file(
        "agentic_core/L0_routing/scripts/test_something.py",
        "def test_example():\n    assert True\n",
    )

    # I: Missing L6/config (remove it)
    config_path = tmp_path / "agentic_core" / "L6_observability" / "config"
    if config_path.exists():
        import shutil

        shutil.rmtree(config_path)

    return builder
