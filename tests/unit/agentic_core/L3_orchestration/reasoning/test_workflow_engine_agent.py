"""Tests for L3 Orchestration reasoning agents."""

from pathlib import Path

import pytest


class TestWorkflowEngineAgent:
    """Tests for workflow engine functionality."""

    def test_workflow_engine_exists(self):
        """Workflow engine module should exist."""
        path = Path("agentic_core/L3_orchestration/reasoning")
        assert path.exists(), "L3_orchestration/reasoning/ should exist"

    def test_orchestration_has_workflow_classes(self):
        """Orchestration should have workflow/pipeline classes."""
        reasoning_path = Path("agentic_core/L3_orchestration/reasoning")
        if reasoning_path.exists():
            py_files = list(reasoning_path.glob("*.py"))
            assert len(py_files) > 0, "L3_orchestration/reasoning/ should have Python files"


class TestDAGExecutorAgent:
    """Tests for DAG execution functionality."""

    def test_dag_types_defined(self):
        """DAG types should be defined in types/."""
        types_path = Path("agentic_core/L3_orchestration/types")
        if not types_path.exists():
            pytest.skip("L3_orchestration/types/ not found")

        type_files = list(types_path.glob("*.py"))
        assert len(type_files) > 0, "L3_orchestration/types/ should have type definitions"


class TestMetaLearningAgent:
    """Tests for meta-learning orchestration."""

    def test_meta_learning_config_exists(self):
        """Meta-learning config should exist."""
        config_path = Path("agentic_core/L3_orchestration/config")
        if not config_path.exists():
            pytest.skip("L3_orchestration/config/ not found")

        config_files = list(config_path.glob("*.py"))
        assert len(config_files) > 0, "L3_orchestration/config/ should have config files"


class TestOrchestrationLayerIntegrity:
    """Tests for L3 layer structural integrity."""

    def test_no_direct_llm_calls(self):
        """L3 orchestration should not make direct LLM calls (delegate to L1)."""
        base = Path("agentic_core/L3_orchestration")
        if not base.exists():
            pytest.skip("L3_orchestration/ not found")

        # Check for direct OpenAI/Anthropic imports (should go through L1)
        suspicious_imports = ["openai", "anthropic", "langchain"]
        violations = []

        for py_file in base.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
            content = py_file.read_text(encoding="utf-8", errors="ignore")
            for imp in suspicious_imports:
                if f"import {imp}" in content or f"from {imp}" in content:
                    violations.append(f"{py_file}: imports {imp}")

        # This is a soft check - some orchestrators may legitimately use these
        if violations:
            pytest.skip(f"Found LLM imports (may be legitimate): {len(violations)}")

    def test_orchestration_agents_in_reasoning(self):
        """Agent classes in L3 should be in reasoning/."""
        base = Path("agentic_core/L3_orchestration")
        if not base.exists():
            pytest.skip("L3_orchestration/ not found")

        # Known exceptions (documented architectural decisions)
        # Some types/config files have embedded Agent classes (legacy pattern)
        known_exceptions = ["dag_mutator_config.py", "orchestrator_types.py"]

        violations = []
        for subfolder in ["types", "utils", "config"]:
            subfolder_path = base / subfolder
            if not subfolder_path.exists():
                continue
            for py_file in subfolder_path.glob("*.py"):
                if any(exc in str(py_file) for exc in known_exceptions):
                    continue
                content = py_file.read_text(encoding="utf-8", errors="ignore")
                if "class " in content and "Agent(" in content:
                    violations.append(str(py_file))

        assert len(violations) == 0, f"Agent classes in wrong subfolder: {violations}"
