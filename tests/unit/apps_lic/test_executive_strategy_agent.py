"""
Fixed dispatch tests for ExecutiveStrategyAgent.
This replaces the problematic test file with corrected monkeypatch paths.
"""

from pathlib import Path
from unittest.mock import MagicMock

import pytest

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

        # Mock PromptLoader methods
        def mock_load_prompt(self, domain: str, name: str):
            return {"constraints": ["Be objective"]}

        def mock_get_template(self, domain: str, name: str, **kwargs):
            return "Shadow audit content for {department}"

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

        # Mock PromptLoader methods
        def mock_load_prompt(self, domain: str, name: str):
            return {}

        def mock_get_template(self, domain: str, name: str, **kwargs):
            return "Strategy roadmap for {timeline}"

        from agentic_core.prompt_governance import PromptLoader

        monkeypatch.setattr(PromptLoader, "load_prompt", mock_load_prompt)
        monkeypatch.setattr(PromptLoader, "get_template", mock_get_template)

        agent = ExecutiveStrategyAgent(prompt_root=tmp_path)
        result = agent.generate_strategy_roadmap({"timeline": "Q1 2024"})

        assert result == "Strategy roadmap for Q1 2024"

    def test_profile_interviewer_success(self, tmp_path: Path, monkeypatch) -> None:
        """Test successful interviewer profiling."""
        (tmp_path / "executive").mkdir()

        # Mock PromptLoader methods
        def mock_load_prompt(self, domain: str, name: str):
            return {"constraints": ["Be thorough"]}

        def mock_get_template(self, domain: str, name: str, **kwargs):
            return "Interviewer profile for {role}"

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

        # Mock PromptLoader methods
        def mock_load_prompt(self, domain: str, name: str):
            return {}

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

        # Mock ExecutiveStrategyAgent methods - use correct module path
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

        # Mock ExecutiveStrategyAgent methods - use correct module path
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
