"""Unit tests for ExecutiveStrategyAgent.

Tests executive domain prompt integration with deterministic tmp_path injection.
"""

from pathlib import Path

import pytest

from agentic_core.prompt_governance import PromptLoadError, PromptSchemaError
from apps_lic.engines.ExecutiveStrategyAgent import ExecutiveStrategyAgent


class TestExecutiveStrategyAgent:
    """Test suite for ExecutiveStrategyAgent with tmp_path injection."""

    def test_conduct_shadow_audit_happy_path(self, tmp_path: Path) -> None:
        """Test shadow audit renders template correctly."""
        # Create minimal executive domain prompt
        (tmp_path / "executive").mkdir()
        prompt_file = tmp_path / "executive" / "k11_shadow_audit.yaml"
        prompt_file.write_text("""
template: "Shadow Audit: {organization} - {focus_area}\\nConstraints: {constraints}"
constraints:
  - "Be objective"
  - "Provide evidence"
""")

        agent = ExecutiveStrategyAgent(prompt_root=tmp_path)
        result = agent.conduct_shadow_audit({
            "organization": "TechCorp",
            "focus_area": "Engineering"
        })

        assert "Shadow Audit: TechCorp - Engineering" in result
        assert "Be objective" in result
        assert "Provide evidence" in result

    def test_generate_strategy_roadmap_happy_path(self, tmp_path: Path) -> None:
        """Test strategy roadmap renders template correctly."""
        (tmp_path / "executive").mkdir()
        prompt_file = tmp_path / "executive" / "k12_strategy_roadmap.yaml"
        prompt_file.write_text("""
template: "Roadmap for {company}: {timeline}\\nConstraints: {constraints}"
constraints:
  - "30-60-90 day structure"
  - "Measurable milestones"
""")

        agent = ExecutiveStrategyAgent(prompt_root=tmp_path)
        result = agent.generate_strategy_roadmap({
            "company": "StartupXYZ",
            "timeline": "Q1 2026"
        })

        assert "Roadmap for StartupXYZ: Q1 2026" in result
        assert "30-60-90 day structure" in result
        assert "Measurable milestones" in result

    def test_profile_interviewer_happy_path(self, tmp_path: Path) -> None:
        """Test interviewer profiling renders template correctly."""
        (tmp_path / "executive").mkdir()
        prompt_file = tmp_path / "executive" / "k13_interviewer_sim.yaml"
        prompt_file.write_text("""
template: "Interviewer Profile: {interviewer_name} at {interviewer_company}\\nConstraints: {constraints}"
constraints:
  - "Research background"
  - "Prepare questions"
""")

        agent = ExecutiveStrategyAgent(prompt_root=tmp_path)
        result = agent.profile_interviewer({
            "interviewer_name": "Jane Smith",
            "interviewer_company": "BigTech Inc"
        })

        assert "Interviewer Profile: Jane Smith at BigTech Inc" in result
        assert "Research background" in result
        assert "Prepare questions" in result

    def test_conduct_shadow_audit_missing_file(self, tmp_path: Path) -> None:
        """Test PromptLoadError propagates when file missing."""
        (tmp_path / "executive").mkdir()

        agent = ExecutiveStrategyAgent(prompt_root=tmp_path)

        with pytest.raises(PromptLoadError, match="Prompt file not found"):
            agent.conduct_shadow_audit({"organization": "Test"})

    def test_generate_strategy_roadmap_invalid_schema(self, tmp_path: Path) -> None:
        """Test PromptSchemaError propagates when schema invalid."""
        (tmp_path / "executive").mkdir()
        prompt_file = tmp_path / "executive" / "k12_strategy_roadmap.yaml"
        prompt_file.write_text("not_a_dict: true")  # Missing 'template' key

        agent = ExecutiveStrategyAgent(prompt_root=tmp_path)

        with pytest.raises(PromptSchemaError, match="Missing required 'template' key"):
            agent.generate_strategy_roadmap({"company": "Test"})

    def test_profile_interviewer_missing_template_variable(self, tmp_path: Path) -> None:
        """Test PromptSchemaError propagates when template variable missing."""
        (tmp_path / "executive").mkdir()
        prompt_file = tmp_path / "executive" / "k13_interviewer_sim.yaml"
        prompt_file.write_text("""
template: "Profile: {interviewer_name} at {interviewer_company}"
""")

        agent = ExecutiveStrategyAgent(prompt_root=tmp_path)

        with pytest.raises(PromptSchemaError, match="Missing template variable"):
            agent.profile_interviewer({"interviewer_name": "John"})  # Missing 'interviewer_company'

    def test_correct_domain_and_name_requested(self, tmp_path: Path, monkeypatch) -> None:
        """Test that correct domain/name pairs are requested from PromptLoader."""
        (tmp_path / "executive").mkdir()

        # Track calls to get_template
        calls = []

        def mock_load_prompt(self, domain: str, name: str):
            return {"template": "Mock"}
        
        def mock_get_template(self, domain: str, name: str, **kwargs):
            calls.append((domain, name))
            return f"Mock template for {domain}:{name}"

        from agentic_core.prompt_governance import PromptLoader
        monkeypatch.setattr(PromptLoader, "load_prompt", mock_load_prompt)
        monkeypatch.setattr(PromptLoader, "get_template", mock_get_template)

        agent = ExecutiveStrategyAgent(prompt_root=tmp_path)

        agent.conduct_shadow_audit({"test": "data"})
        assert calls[-1] == ("executive", "k11_shadow_audit")

        agent.generate_strategy_roadmap({"test": "data"})
        assert calls[-1] == ("executive", "k12_strategy_roadmap")

        agent.profile_interviewer({"test": "data"})
        assert calls[-1] == ("executive", "k13_interviewer_sim")

    def test_prompt_loader_instantiation(self, tmp_path: Path) -> None:
        """Test PromptLoader is correctly instantiated with injected path."""
        agent = ExecutiveStrategyAgent(prompt_root=tmp_path)

        assert agent._prompt_loader is not None
        assert agent._prompt_loader._prompt_dir == tmp_path.resolve()

    def test_default_prompt_root_when_none(self) -> None:
        """Test default prompt root points to data/prompt_governance."""
        agent = ExecutiveStrategyAgent(prompt_root=None)

        expected_path = Path(__file__).parent.parent.parent.parent / "data" / "prompt_governance"
        assert agent.prompt_root.resolve() == expected_path.resolve()

    def test_constraints_inclusion(self, tmp_path: Path, monkeypatch) -> None:
        """Test constraints are prefixed deterministically when present."""
        (tmp_path / "executive").mkdir()

        # Mock PromptLoader methods
        def mock_load_prompt(self, domain: str, name: str):
            return {"constraints": ["Be objective", "Provide evidence"]}
        
        def mock_get_template(self, domain: str, name: str, **kwargs):
            return "BODY"

        from agentic_core.prompt_governance import PromptLoader
        monkeypatch.setattr(PromptLoader, "load_prompt", mock_load_prompt)
        monkeypatch.setattr(PromptLoader, "get_template", mock_get_template)

        agent = ExecutiveStrategyAgent(prompt_root=tmp_path)
        result = agent.conduct_shadow_audit({"test": "data"})

        assert result == "CONSTRAINTS:\n- Be objective\n- Provide evidence\n\nBODY"

    def test_reserved_key_collision(self, tmp_path: Path, monkeypatch) -> None:
        """Test reserved keys are filtered out to prevent collisions."""
        (tmp_path / "executive").mkdir()

        # Capture template_vars passed to get_template
        captured_vars = {}

        def mock_load_prompt(self, domain: str, name: str):
            return {"template": "Template with {x}"}
        
        def mock_get_template(self, domain: str, name: str, **kwargs):
            captured_vars.update(kwargs)
            return "Rendered"

        from agentic_core.prompt_governance import PromptLoader
        monkeypatch.setattr(PromptLoader, "load_prompt", mock_load_prompt)
        monkeypatch.setattr(PromptLoader, "get_template", mock_get_template)

        agent = ExecutiveStrategyAgent(prompt_root=tmp_path)
        agent.conduct_shadow_audit({
            "name": "SHOULD_NOT_BE_PASSED",  # Reserved key
            "domain": "SHOULD_NOT_BE_PASSED",  # Reserved key
            "prompt_name": "SHOULD_NOT_BE_PASSED",  # Reserved key
            "x": 1,  # Should be passed
            "y": 2  # Should be passed
        })

        # Reserved keys should be filtered out
        assert "name" not in captured_vars
        assert "domain" not in captured_vars
        assert "prompt_name" not in captured_vars
        
        # Non-reserved keys should be passed
        assert captured_vars["x"] == 1
        assert captured_vars["y"] == 2
