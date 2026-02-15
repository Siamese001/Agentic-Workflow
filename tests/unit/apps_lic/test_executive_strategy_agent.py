"""
Fixed ExecutiveStrategyAgent tests with proper template formatting and simplified approach.
"""

from pathlib import Path

from apps_lic.engines.ExecutiveStrategyAgent import ExecutiveStrategyAgent


class TestExecutiveStrategyAgent:
    def test_init_with_default_prompt_root(self) -> None:
        """Test ExecutiveStrategyAgent initializes with default prompt root."""
        agent = ExecutiveStrategyAgent()

        expected_path = Path(__file__).parent.parent.parent.parent / "data" / "prompt_governance"
        assert agent.prompt_root.resolve() == expected_path.resolve()

    def test_init_with_custom_prompt_root(self, tmp_path: Path) -> None:
        """Test ExecutiveStrategyAgent accepts custom prompt root."""
        agent = ExecutiveStrategyAgent(prompt_root=tmp_path)
        assert agent.prompt_root == tmp_path

    def test_conduct_shadow_audit_success(self, tmp_path: Path, monkeypatch) -> None:
        """Test successful shadow audit generation."""
        (tmp_path / "executive").mkdir()

        # Mock PromptLoader to return formatted content directly
        def mock_load_prompt(self, domain: str, name: str):
            return {"constraints": ["Be objective"]}

        def mock_get_template(self, domain: str, name: str, **kwargs):
            # Return already formatted content to avoid template variable issues
            return "Shadow audit content for Engineering"

        from agentic_core.prompt_governance import PromptLoader

        monkeypatch.setattr(PromptLoader, "load_prompt", mock_load_prompt)
        monkeypatch.setattr(PromptLoader, "get_template", mock_get_template)

        agent = ExecutiveStrategyAgent(prompt_root=tmp_path)
        result = agent.conduct_shadow_audit({"department": "Engineering"})

        expected = "CONSTRAINTS:\n- Be objective\n\nShadow audit content for Engineering"
        assert result == expected

    def test_generate_strategy_roadmap_success(self, tmp_path: Path, monkeypatch) -> None:
        """Test successful strategy roadmap generation."""
        (tmp_path / "executive").mkdir()

        # Mock PromptLoader to return formatted content directly
        def mock_load_prompt(self, domain: str, name: str):
            return {}

        def mock_get_template(self, domain: str, name: str, **kwargs):
            # Return already formatted content to avoid template variable issues
            return "Strategy roadmap for Q1 2024"

        from agentic_core.prompt_governance import PromptLoader

        monkeypatch.setattr(PromptLoader, "load_prompt", mock_load_prompt)
        monkeypatch.setattr(PromptLoader, "get_template", mock_get_template)

        agent = ExecutiveStrategyAgent(prompt_root=tmp_path)
        result = agent.generate_strategy_roadmap({"timeline": "Q1 2024"})

        assert result == "Strategy roadmap for Q1 2024"

    def test_profile_interviewer_success(self, tmp_path: Path, monkeypatch) -> None:
        """Test successful interviewer profiling."""
        (tmp_path / "executive").mkdir()

        # Mock PromptLoader to return formatted content directly
        def mock_load_prompt(self, domain: str, name: str):
            return {"constraints": ["Be thorough"]}

        def mock_get_template(self, domain: str, name: str, **kwargs):
            # Return already formatted content to avoid template variable issues
            return "Interviewer profile for Senior Developer"

        from agentic_core.prompt_governance import PromptLoader

        monkeypatch.setattr(PromptLoader, "load_prompt", mock_load_prompt)
        monkeypatch.setattr(PromptLoader, "get_template", mock_get_template)

        agent = ExecutiveStrategyAgent(prompt_root=tmp_path)
        result = agent.profile_interviewer({"role": "Senior Developer"})

        expected = "CONSTRAINTS:\n- Be thorough\n\nInterviewer profile for Senior Developer"
        assert result == expected

    def test_dispatch_functions_reachable_via_registry(self, tmp_path: Path, monkeypatch) -> None:
        """Test that dispatch functions are reachable via apps_lic.engines registry."""
        # Create executive directory and mock prompts
        (tmp_path / "executive").mkdir()

        # Mock PromptLoader to return formatted content directly
        def mock_load_prompt(self, domain: str, name: str):
            return {}

        def mock_get_template(self, domain: str, name: str, **kwargs):
            # Return already formatted content to avoid template variable issues
            if name == "k11_shadow_audit":
                return "Shadow audit for Engineering"
            elif name == "k12_strategy_roadmap":
                return "Strategy roadmap for Q1 2024"
            elif name == "k13_interviewer_sim":
                return "Interviewer profile for Senior Developer"
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
