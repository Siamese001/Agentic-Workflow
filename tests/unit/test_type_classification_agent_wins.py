"""
Test Agent Suffix Wins Subfolder policy.

Validates:
- Agent in types/config/validators/utils/enforcement triggers violation
- Recommended move/split to reasoning/
"""

import ast
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    L3_ORCHESTRATION_DIR,
)


def detect_agent_in_wrong_subfolder(file_path: Path) -> dict | None:
    """
    Detect if an Agent class is in a non-reasoning subfolder.

    Returns violation dict if found, None otherwise.
    """
    path_str = str(file_path)

    # Skip if already in reasoning/
    if "/reasoning/" in path_str or "\\reasoning\\" in path_str:
        return None

    # Skip base_agents (allowed location)
    if "/base_agents/" in path_str or "\\base_agents\\" in path_str:
        return None

    # Check for Agent class
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
        tree = ast.parse(content)

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if node.name.endswith("Agent") and not node.name.startswith("I"):
                    # Check if Protocol
                    is_protocol = any(
                        (isinstance(base, ast.Name) and base.id == "Protocol") for base in node.bases
                    )
                    if not is_protocol:
                        # Determine current subfolder
                        parts = Path(path_str).parts
                        for i, part in enumerate(parts):
                            if part in ("types", "config", "validators", "utils", "enforcement"):
                                return {
                                    "file": str(file_path),
                                    "agent_class": node.name,
                                    "current_subfolder": part,
                                    "recommended_subfolder": "reasoning",
                                    "action": "MOVE" if "types" not in path_str else "SPLIT",
                                }
    except SyntaxError:
        pass

    return None


class TestAgentInTypesViolation:
    """Tests for Agent in types/ violation."""

    def test_agent_in_types_detected(self, tmp_path):
        """Agent class in types/ should be detected as violation."""
        types_dir = tmp_path / AGENTIC_CORE_DIR / "L5_safety" / "types"
        types_dir.mkdir(parents=True)

        agent_file = types_dir / "embedded_agent_types.py"
        agent_file.write_text("""
class EmbeddedAgent:
    def execute(self):
        pass
""")

        violation = detect_agent_in_wrong_subfolder(agent_file)
        assert violation is not None
        assert violation["current_subfolder"] == "types"
        assert violation["recommended_subfolder"] == "reasoning"

    def test_agent_in_types_recommends_split(self, tmp_path):
        """Agent in types/ should recommend SPLIT action."""
        types_dir = tmp_path / AGENTIC_CORE_DIR / "L5_safety" / "types"
        types_dir.mkdir(parents=True)

        agent_file = types_dir / "mixed_types.py"
        agent_file.write_text("""
from dataclasses import dataclass

@dataclass
class SomeType:
    value: str

class MixedAgent:
    def execute(self):
        pass
""")

        violation = detect_agent_in_wrong_subfolder(agent_file)
        assert violation is not None
        assert violation["action"] == "SPLIT"


class TestAgentInConfigViolation:
    """Tests for Agent in config/ violation."""

    def test_agent_in_config_detected(self, tmp_path):
        """Agent class in config/ should be detected as violation."""
        config_dir = tmp_path / L3_ORCHESTRATION_DIR / "config"
        config_dir.mkdir(parents=True)

        agent_file = config_dir / "dag_mutator_config.py"
        agent_file.write_text("""
class DAGMutatorAgent:
    def mutate(self, dag):
        pass
""")

        violation = detect_agent_in_wrong_subfolder(agent_file)
        assert violation is not None
        assert violation["current_subfolder"] == "config"


class TestAgentInValidatorsViolation:
    """Tests for Agent in validators/ violation."""

    def test_agent_in_validators_detected(self, tmp_path):
        """Agent class in validators/ should be detected as violation."""
        validators_dir = tmp_path / AGENTIC_CORE_DIR / "L5_safety" / "validators"
        validators_dir.mkdir(parents=True)

        agent_file = validators_dir / "naming_validator.py"
        agent_file.write_text("""
class NamingAgent:
    def validate_name(self, name):
        return True
""")

        violation = detect_agent_in_wrong_subfolder(agent_file)
        assert violation is not None
        assert violation["current_subfolder"] == "validators"


class TestAgentInUtilsViolation:
    """Tests for Agent in utils/ violation."""

    def test_agent_in_utils_detected(self, tmp_path):
        """Agent class in utils/ should be detected as violation."""
        utils_dir = tmp_path / AGENTIC_CORE_DIR / "L5_safety" / "utils"
        utils_dir.mkdir(parents=True)

        agent_file = utils_dir / "cache_invalidation_util.py"
        agent_file.write_text("""
class HealerAgent:
    def heal(self):
        pass
""")

        violation = detect_agent_in_wrong_subfolder(agent_file)
        assert violation is not None
        assert violation["current_subfolder"] == "utils"


class TestAgentInEnforcementViolation:
    """Tests for Agent in enforcement/ violation."""

    def test_agent_in_enforcement_detected(self, tmp_path):
        """Agent class in enforcement/ should be detected as violation."""
        enforcement_dir = tmp_path / AGENTIC_CORE_DIR / "L5_safety" / "enforcement"
        enforcement_dir.mkdir(parents=True)

        agent_file = enforcement_dir / "hygiene_guardian.py"
        agent_file.write_text("""
class HygieneGuardianAgent:
    def guard(self):
        pass
""")

        violation = detect_agent_in_wrong_subfolder(agent_file)
        assert violation is not None
        assert violation["current_subfolder"] == "enforcement"


class TestAgentInReasoningAllowed:
    """Tests for Agent in reasoning/ (allowed)."""

    def test_agent_in_reasoning_no_violation(self, tmp_path):
        """Agent class in reasoning/ should NOT be a violation."""
        reasoning_dir = tmp_path / AGENTIC_CORE_DIR / "L5_safety" / "reasoning"
        reasoning_dir.mkdir(parents=True)

        agent_file = reasoning_dir / "GoodAgent.py"
        agent_file.write_text("""
class GoodAgent:
    def execute(self):
        pass
""")

        violation = detect_agent_in_wrong_subfolder(agent_file)
        assert violation is None


class TestProtocolInterfaceAllowed:
    """Tests for Protocol interfaces (allowed anywhere)."""

    def test_protocol_in_types_no_violation(self, tmp_path):
        """Protocol interface in types/ should NOT be a violation."""
        types_dir = tmp_path / L3_ORCHESTRATION_DIR / "types"
        types_dir.mkdir(parents=True)

        protocol_file = types_dir / "orchestrator_types.py"
        protocol_file.write_text("""
from typing import Protocol

class IOrchestratorAgent(Protocol):
    def execute(self) -> None:
        ...
""")

        violation = detect_agent_in_wrong_subfolder(protocol_file)
        assert violation is None
