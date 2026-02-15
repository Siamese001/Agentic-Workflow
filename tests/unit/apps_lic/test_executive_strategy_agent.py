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
        result = agent.conduct_shadow_audit({"organization": "TechCorp", "focus_area": "Engineering"})

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
        result = agent.generate_strategy_roadmap({"company": "StartupXYZ", "timeline": "Q1 2026"})

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
        result = agent.profile_interviewer(
            {"interviewer_name": "Jane Smith", "interviewer_company": "BigTech Inc"}
        )

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

    def test_dispatch_functions_reachable_via_registry(self, tmp_path: Path, monkeypatch) -> None:
        """Test that dispatch functions are reachable via apps_lic.engines registry."""
        # Create executive directory and mock prompts
        (tmp_path / "executive").mkdir()

        # Mock PromptLoader methods
        def mock_load_prompt(self, domain: str, name: str):
            return {"template": "Mock template for {name}"}

        def mock_get_template(self, domain: str, name: str, **kwargs):
            if name == "k11_shadow_audit":
                return "Shadow audit for {department}"
            elif name == "k12_strategy_roadmap":
                return "Strategy roadmap for {timeline}"
            elif name == "k13_interviewer_sim":
                return "Interviewer profile for {role}"
            return "Default template"

        from agentic_core.prompt_governance import PromptLoader

        monkeypatch.setattr(PromptLoader, "load_prompt", mock_load_prompt)
        monkeypatch.setattr(PromptLoader, "get_template", mock_get_template)

        # Import dispatch functions via registry (minimal import)
        from apps_lic.engines import (
            get_exec_interviewer_profile,
            get_exec_shadow_audit,
            get_exec_strategy_roadmap,
        )

        # Test shadow audit dispatch
        shadow_payload = {"department": "Engineering"}
        shadow_result = get_exec_shadow_audit(shadow_payload, prompt_root=tmp_path)
        assert shadow_result == "Shadow audit for Engineering"

        # Test strategy roadmap dispatch
        roadmap_payload = {"timeline": "Q1 2024"}
        roadmap_result = get_exec_strategy_roadmap(roadmap_payload, prompt_root=tmp_path)
        assert roadmap_result == "Strategy roadmap for Q1 2024"

        # Test interviewer profile dispatch
        interviewer_payload = {"role": "Senior Developer"}
        interviewer_result = get_exec_interviewer_profile(interviewer_payload, prompt_root=tmp_path)
        assert interviewer_result == "Interviewer profile for Senior Developer"

    def test_dispatch_functions_prompt_root_injection(self, tmp_path: Path, monkeypatch) -> None:
        """Test that dispatch functions correctly use injected prompt_root."""
        # Create executive directory and mock prompts
        (tmp_path / "executive").mkdir()

        # Track which prompt_root was used
        used_prompt_roots = []

        def mock_init(self, prompt_root=None):
            if prompt_root is None:
                prompt_root = Path(__file__).parent.parent.parent.parent / "data" / "prompt_governance"
            used_prompt_roots.append(prompt_root)
            self.prompt_root = prompt_root
            self._prompt_loader = MagicMock()

        def mock_conduct_shadow_audit(self, payload):
            return f"Shadow audit with root {self.prompt_root.name}"

        def mock_generate_strategy_roadmap(self, payload):
            return f"Roadmap with root {self.prompt_root.name}"

        def mock_profile_interviewer(self, payload):
            return f"Profile with root {self.prompt_root.name}"

        # Mock ExecutiveStrategyAgent methods
        monkeypatch.setattr(
            "apps_lic.engines.ExecutiveStrategyAgent.ExecutiveStrategyAgent.__init__", mock_init
        )
        monkeypatch.setattr(
            "apps_lic.engines.ExecutiveStrategyAgent.ExecutiveStrategyAgent.conduct_shadow_audit",
            mock_conduct_shadow_audit,
        )
        monkeypatch.setattr(
            "apps_lic.engines.ExecutiveStrategyAgent.ExecutiveStrategyAgent.generate_strategy_roadmap",
            mock_generate_strategy_roadmap,
        )
        monkeypatch.setattr(
            "apps_lic.engines.ExecutiveStrategyAgent.ExecutiveStrategyAgent.profile_interviewer",
            mock_profile_interviewer,
        )

        # Import dispatch functions
        from apps_lic.engines import (
            get_exec_interviewer_profile,
            get_exec_shadow_audit,
            get_exec_strategy_roadmap,
        )

        # Test with injected prompt_root
        custom_root = tmp_path / "custom_prompts"
        get_exec_shadow_audit({"test": "data"}, prompt_root=custom_root)
        get_exec_strategy_roadmap({"test": "data"}, prompt_root=custom_root)
        get_exec_interviewer_profile({"test": "data"}, prompt_root=custom_root)

        # Verify custom prompt_root was used
        assert all(root == custom_root for root in used_prompt_roots[-3:])

        # Test with default prompt_root (None)
        get_exec_shadow_audit({"test": "data"})
        assert used_prompt_roots[-1].name == "prompt_governance"

    def test_dispatch_functions_prompt_loader_exception_propagation(
        self, tmp_path: Path, monkeypatch
    ) -> None:
        """Test that PromptLoader exceptions propagate through dispatch functions."""
        # Import dispatch functions
        from agentic_core.prompt_governance import PromptLoadError
        from apps_lic.engines import (
            get_exec_interviewer_profile,
            get_exec_shadow_audit,
            get_exec_strategy_roadmap,
        )

        # Mock PromptLoader to raise PromptLoadError
        def mock_init(self, prompt_root=None):
            if prompt_root is None:
                prompt_root = Path(__file__).parent.parent.parent.parent / "data" / "prompt_governance"
            self.prompt_root = prompt_root
            self._prompt_loader = MagicMock()

        def mock_conduct_shadow_audit(self, payload):
            raise PromptLoadError("Prompt file not found")

        def mock_generate_strategy_roadmap(self, payload):
            raise PromptLoadError("Strategy roadmap not found")

        def mock_profile_interviewer(self, payload):
            raise PromptLoadError("Interviewer sim not found")

        # Mock ExecutiveStrategyAgent methods
        monkeypatch.setattr(
            "apps_lic.engines.ExecutiveStrategyAgent.ExecutiveStrategyAgent.__init__", mock_init
        )
        monkeypatch.setattr(
            "apps_lic.engines.ExecutiveStrategyAgent.ExecutiveStrategyAgent.conduct_shadow_audit",
            mock_conduct_shadow_audit,
        )
        monkeypatch.setattr(
            "apps_lic.engines.ExecutiveStrategyAgent.ExecutiveStrategyAgent.generate_strategy_roadmap",
            mock_generate_strategy_roadmap,
        )
        monkeypatch.setattr(
            "apps_lic.engines.ExecutiveStrategyAgent.ExecutiveStrategyAgent.profile_interviewer",
            mock_profile_interviewer,
        )

        # Test exception propagation
        with pytest.raises(PromptLoadError) as exc_info:
            get_exec_shadow_audit({"test": "data"})
        assert str(exc_info.value) == "Prompt file not found"

        with pytest.raises(PromptLoadError) as exc_info:
            get_exec_strategy_roadmap({"test": "data"})
        assert str(exc_info.value) == "Strategy roadmap not found"

        with pytest.raises(PromptLoadError) as exc_info:
            get_exec_interviewer_profile({"test": "data"})
        assert str(exc_info.value) == "Interviewer sim not found"

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
        agent.conduct_shadow_audit(
            {
                "name": "SHOULD_NOT_BE_PASSED",  # Reserved key
                "domain": "SHOULD_NOT_BE_PASSED",  # Reserved key
                "prompt_name": "SHOULD_NOT_BE_PASSED",  # Reserved key
                "x": 1,  # Should be passed
                "y": 2,  # Should be passed
            }
        )

        # Reserved keys should be filtered out
        assert "name" not in captured_vars
        assert "domain" not in captured_vars
        assert "prompt_name" not in captured_vars

        # Non-reserved keys should be passed
        assert captured_vars["x"] == 1
        assert captured_vars["y"] == 2
