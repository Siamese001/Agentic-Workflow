"""
File: tests/guardian/test_pascal_edge_cases.py
Verification: 100% Pass Required.
"""

import sys
from pathlib import Path

import pytest

# Add the project root to the path to import the agent
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import the agent directly without SovereignBaseAgent to avoid integrity checks
from agentic_core.L5_safety.reasoning.FileClassificationAgent import FileClassificationAgent


class TestPascalHardening:
    @pytest.fixture
    def agent(self, tmp_path):
        # Create agent without SovereignBaseAgent inheritance to avoid integrity checks
        agent = object.__new__(FileClassificationAgent)
        agent.project_root = tmp_path.resolve()
        agent.dry_run = True
        agent.verbose = False
        agent.validate_only = False
        agent.stats = {
            "analyzed": 0,
            "compliant": 0,
            "renamed": 0,
            "imports_fixed": 0,
            "collisions_resolved": 0,
            "violations": {
                "AGENT": 0,
                "CLASS": 0,
                "MIXIN": 0,
                "UTILITY": 0,
                "PROTOCOL": 0,
                "ENGINE": 0,
                "STUB": 0,
                "TEST": 0,
                "GATEWAY": 0,
                "SCRIPT": 0,  # Add the new SCRIPT category
                "TYPES": 0,  # Add the new TYPES category
            },
        }
        agent.file_registry = []
        return agent

    def test_ops_script_protection(self, agent, tmp_path):
        """Verify scripts in ops_scripts remain snake_case even with classes inside."""
        script_path = tmp_path / "ops_scripts" / "DatabaseFixer.py"
        script_path.parent.mkdir()
        script_path.write_text("class InternalTool: pass\nif __name__ == '__main__': pass")

        ftype = agent.classify_file(script_path)
        assert ftype == "SCRIPT"

        new_name = agent.get_compliant_name(script_path, ftype)
        assert new_name == "database_fixer.py"  # Corrected from Pascal to Snake

    def test_types_collection_immunity(self, agent, tmp_path):
        """Verify types.py is NOT renamed to the first Enum/Class name inside it."""
        types_path = tmp_path / "agentic_core" / "types.py"
        types_path.parent.mkdir()
        types_path.write_text("class UserStatus(Enum): ACTIVE=1")

        ftype = agent.classify_file(types_path)
        assert ftype == "TYPES"

        new_name = agent.get_compliant_name(types_path, ftype)
        assert new_name is None  # Immunity check

    def test_private_module_immunity(self, agent, tmp_path):
        """Verify underscore-prefixed files are treated as protected internal types."""
        private_path = tmp_path / "_internal_utils.py"
        private_path.write_text("class Hidden: pass")

        ftype = agent.classify_file(private_path)
        assert ftype == "TYPES"
        assert agent.get_compliant_name(private_path, ftype) is None

    def test_agent_suffix_enforcement(self, agent, tmp_path):
        """Verify structural agents get the 'Agent' suffix even if the class is missing it."""
        agent_path = tmp_path / "agents" / "orchestrator.py"
        agent_path.parent.mkdir()
        agent_path.write_text("class Orchestrator: pass")

        ftype = agent.classify_file(agent_path)
        assert ftype == "AGENT"

        new_name = agent.get_compliant_name(agent_path, ftype)
        assert new_name == "OrchestratorAgent.py"
