"""
File: tests/unit/agentic_core/base_agents/test_healer_interface.py
Description: Verifies LegacyAgentAdapter handles fragmentation and HealerMixin enforces schema.
Mandate: 100% Pass.
"""

from agentic_core.base_agents.HealerProtocol import (
    LegacyAgentAdapter,
    HealerAgentMixin,
    HEAL_RESULT_SCHEMA,
)

# --- MOCK LEGACY AGENTS ---


class LegacyFixer:
    """Old style: fix(path) -> bool"""

    def fix(self, file_path):
        return True


class LegacyRunner:
    """Old style: run([files]) -> list of modified"""

    def run(self, files):
        return files  # returns list of what it touched


class LegacyResolver:
    """Old style: resolve(dict) -> str"""

    def resolve(self, violation):
        return "Fixed the issue"


class BrokenAgent:
    """No recognized methods"""

    pass


class StandardAgent(HealerAgentMixin):
    """New style implementing Mixin"""

    def _heal_impl(self, violation):
        return {"status": "success", "details": "Native implementation"}


class CrashingAgent:
    """Agent that raises exception during fix"""

    def fix(self, file_path):
        raise ValueError("Boom")


class DictReturningAgent:
    """Agent that already returns proper dict format"""

    def resolve(self, violation):
        return {
            "status": "success",
            "details": "Already compliant",
            "artifacts": ["test.py"],
            "errors": [],
        }


# --- TESTS ---


class TestAgentStandardization:
    def test_adapter_strategy_fix(self):
        """Scenario: Agent has fix(file_path)."""
        agent = LegacyFixer()
        adapter = LegacyAgentAdapter(agent)

        violation = {"file": "/tmp/test.py", "type": "NAMING"}
        result = adapter.heal(violation)

        assert result["status"] == "success"
        assert result["details"] == "Legacy boolean return"

    def test_adapter_strategy_run(self):
        """Scenario: Agent has run(files_list)."""
        agent = LegacyRunner()
        adapter = LegacyAgentAdapter(agent)

        violation = {"file": "/tmp/test.py"}
        result = adapter.heal(violation)

        assert result["status"] == "success"
        assert "/tmp/test.py" in result["artifacts"]

    def test_adapter_strategy_resolve(self):
        """Scenario: Agent has resolve(violation)."""
        agent = LegacyResolver()
        adapter = LegacyAgentAdapter(agent)

        violation = {"type": "COMPLEX"}
        result = adapter.heal(violation)

        assert result["status"] == "success"
        assert result["details"] == "Fixed the issue"

    def test_adapter_unsupported_agent(self):
        """Scenario: Agent matches no known patterns."""
        agent = BrokenAgent()
        adapter = LegacyAgentAdapter(agent)

        result = adapter.heal({"file": "x.py"})

        assert result["status"] == "failed"
        assert "no recognized healing method" in result["errors"][0]

    def test_mixin_enforcement(self):
        """Scenario: Modern agent uses Mixin for standardization."""
        agent = StandardAgent()

        # Test 1: Valid output
        result = agent.heal({"file": "x.py"})
        assert result["status"] == "success"
        assert "artifacts" in result  # Auto-added by mixin normalization

        # Test 2: Input validation
        result_bad = agent.heal("not a dict")
        assert result_bad["status"] == "failed"
        assert "must be a dictionary" in result_bad["errors"][0]

    def test_adapter_crash_resilience(self):
        """Scenario: Legacy agent raises exception."""
        adapter = LegacyAgentAdapter(CrashingAgent())
        result = adapter.heal({"file": "x.py"})

        assert result["status"] == "failed"
        assert "Legacy Adapter Error" in result["errors"][0]
        assert "Boom" in result["errors"][0]

    def test_adapter_dict_return_normalization(self):
        """Scenario: Legacy agent already returns dict format."""
        agent = DictReturningAgent()
        adapter = LegacyAgentAdapter(agent)

        violation = {"type": "TEST"}
        result = adapter.heal(violation)

        assert result["status"] == "success"
        assert result["details"] == "Already compliant"
        assert result["artifacts"] == ["test.py"]
        assert result["errors"] == []

    def test_adapter_no_file_path_for_fix(self):
        """Scenario: fix() agent called without file path."""
        agent = LegacyFixer()
        adapter = LegacyAgentAdapter(agent)

        violation = {"type": "NAMING"}  # No file path
        result = adapter.heal(violation)

        assert result["status"] == "skipped"
        assert "Legacy agent requires file path" in result["details"]

    def test_mixin_result_normalization(self):
        """Scenario: Mixin normalizes various result formats."""

        class TestAgent(HealerAgentMixin):
            def _heal_impl(self, violation):
                return "simple string result"

        agent = TestAgent()
        result = agent.heal({"test": "data"})

        assert result["status"] == "success"
        assert result["details"] == "simple string result"
        assert "artifacts" in result
        assert "errors" in result

    def test_mixin_missing_keys_backfill(self):
        """Scenario: Mixin backfills missing schema keys."""

        class TestAgent(HealerAgentMixin):
            def _heal_impl(self, violation):
                return {"status": "partial_success"}  # Missing other keys

        agent = TestAgent()
        result = agent.heal({"test": "data"})

        assert result["status"] == "partial_success"
        assert "details" in result
        assert "artifacts" in result
        assert "errors" in result
        assert result["details"] == "Fixed"  # Default value

    def test_protocol_compliance_check(self):
        """Scenario: Check if agent implements HealerProtocol."""
        agent = StandardAgent()

        # Should be recognized as implementing the protocol
        # Note: This is a duck typing check, not strict isinstance
        assert hasattr(agent, "heal")
        assert callable(agent.heal)

    def test_adapter_name_tracking(self):
        """Scenario: Adapter tracks original agent name."""
        agent = LegacyFixer()
        adapter = LegacyAgentAdapter(agent)

        assert adapter.name == "LegacyFixer"

    def test_mixin_exception_handling(self):
        """Scenario: Mixin handles exceptions in _heal_impl."""

        class BrokenMixinAgent(HealerAgentMixin):
            def _heal_impl(self, violation):
                raise RuntimeError("Implementation error")

        agent = BrokenMixinAgent()
        result = agent.heal({"test": "data"})

        assert result["status"] == "failed"
        assert "Implementation error" in result["errors"][0]

    def test_adapter_list_result_handling(self):
        """Scenario: Adapter handles list returns from legacy agents."""

        class ListAgent:
            def run(self, files):
                return ["file1.py", "file2.py", "file3.py"]

        adapter = LegacyAgentAdapter(ListAgent())
        result = adapter.heal({"file": "file1.py"})

        assert result["status"] == "success"
        assert result["artifacts"] == ["file1.py", "file2.py", "file3.py"]
        assert "Modified 3 files" in result["details"]

    def test_schema_constants(self):
        """Scenario: Verify schema constants are properly defined."""
        assert "status" in HEAL_RESULT_SCHEMA
        assert "details" in HEAL_RESULT_SCHEMA
        assert "artifacts" in HEAL_RESULT_SCHEMA
        assert "errors" in HEAL_RESULT_SCHEMA
        assert HEAL_RESULT_SCHEMA["status"] == "str"
        assert HEAL_RESULT_SCHEMA["details"] == "str"
        assert HEAL_RESULT_SCHEMA["artifacts"] == "list"
        assert HEAL_RESULT_SCHEMA["errors"] == "list"
