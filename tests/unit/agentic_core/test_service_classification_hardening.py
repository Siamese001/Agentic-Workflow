"""
Tests for SERVICE classification and classification hardening (RCA 2026-02-07).

Covers:
- SERVICE singleton detection (_is_service_singleton)
- reasoning/ folder purity enforcement for non-agent files
- Non-Python file routing (YAML, JSON, HTML)
- _is_true_agent hardening (method-based detection requires corroboration)
- Dual-tag resolver no longer force-classifies reasoning/ as AGENT
"""

from __future__ import annotations

import ast
import textwrap
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def agent():
    """Create a FileClassificationAgent instance for testing."""
    from agentic_core.L5_safety.reasoning.FileClassificationAgent import (
        FileClassificationAgent,
    )

    return FileClassificationAgent(
        project_root=Path.cwd(),
        dry_run=True,
        validate_only=True,
    )


@pytest.fixture
def tmp_layer(tmp_path):
    """Create a temporary L6_observability layer structure."""
    layer = tmp_path / "agentic_core" / "L6_observability"
    for subfolder in ["reasoning", "utils", "config", "dashboards", "types"]:
        (layer / subfolder).mkdir(parents=True)
    return layer


# ===========================================================================
# SERVICE Singleton Detection
# ===========================================================================


class TestServiceSingletonDetection:
    """Tests for _is_service_singleton() — detects monitors, collectors, trackers."""

    def test_singleton_collector_classified_as_service(self, agent, tmp_layer):
        """A singleton collector with record_* methods should be SERVICE."""
        code = textwrap.dedent("""\
            class RagTelemetryCollector:
                _instance = None
                def __new__(cls):
                    if cls._instance is None:
                        cls._instance = super().__new__(cls)
                    return cls._instance
                def record_query(self, latency_ms):
                    pass
                def get_metrics(self):
                    pass
        """)
        f = tmp_layer / "reasoning" / "rag_telemetry_collector.py"
        f.write_text(code)
        assert agent.classify_file(f) == "SERVICE"

    def test_singleton_monitor_classified_as_service(self, agent, tmp_layer):
        """A singleton monitor with record_execution and get_metrics should be SERVICE."""
        code = textwrap.dedent("""\
            class UnifiedAgentMonitor:
                _instance: 'UnifiedAgentMonitor | None' = None
                def __new__(cls):
                    if cls._instance is None:
                        cls._instance = super().__new__(cls)
                    return cls._instance
                def record_execution(self, name, time_ms):
                    pass
                def get_metrics(self):
                    pass
                def get_health_status(self):
                    pass
        """)
        f = tmp_layer / "reasoning" / "agent_monitor.py"
        f.write_text(code)
        assert agent.classify_file(f) == "SERVICE"

    def test_non_singleton_monitor_not_service(self, agent, tmp_layer):
        """A Monitor class without singleton pattern should NOT be SERVICE (requires 2+ signals)."""
        code = textwrap.dedent("""\
            class SovereignHealthMonitor:
                def __init__(self):
                    self.history = []
                def log_snapshot(self):
                    pass
                def get_domain_health(self):
                    pass
        """)
        f = tmp_layer / "reasoning" / "SovereignHealthMonitor.py"
        f.write_text(code)
        # Only 1 signal (name ends with Monitor), needs 2+
        result = agent.classify_file(f)
        assert result != "SERVICE", "Non-singleton Monitor should not be classified as SERVICE"

    def test_agent_with_monitor_suffix_stays_agent(self, agent, tmp_layer):
        """A class ending in Agent should be AGENT even if it has monitor-like methods."""
        code = textwrap.dedent("""\
            class PerformanceMonitorAgent:
                _instance = None
                def __new__(cls):
                    if cls._instance is None:
                        cls._instance = super().__new__(cls)
                    return cls._instance
                def record_execution(self, time_ms):
                    pass
                def get_metrics(self):
                    pass
        """)
        f = tmp_layer / "reasoning" / "PerformanceMonitorAgent.py"
        f.write_text(code)
        assert agent.classify_file(f) == "AGENT"

    def test_singleton_tracker_classified_as_service(self, agent, tmp_layer):
        """A singleton Tracker with emit_* methods should be SERVICE."""
        code = textwrap.dedent("""\
            class EventTracker:
                _instance = None
                def __new__(cls):
                    if cls._instance is None:
                        cls._instance = super().__new__(cls)
                    return cls._instance
                def emit_event(self, event):
                    pass
                def track_latency(self, ms):
                    pass
        """)
        f = tmp_layer / "utils" / "event_tracker.py"
        f.write_text(code)
        assert agent.classify_file(f) == "SERVICE"


# ===========================================================================
# SERVICE Routing via FILETYPE_TO_FOLDER
# ===========================================================================


class TestServiceRouting:
    """Tests that SERVICE type routes to utils/ via FILETYPE_TO_FOLDER."""

    def test_service_routes_to_utils(self):
        """SERVICE should map to utils/ in FILETYPE_TO_FOLDER."""
        from agentic_core.L5_safety.config.structure_blueprint_config import (
            FILETYPE_TO_FOLDER,
        )

        assert FILETYPE_TO_FOLDER.get("SERVICE") == "utils"

    def test_service_class_indicators_exist(self):
        """SERVICE_CLASS_INDICATORS config should be populated."""
        from agentic_core.L5_safety.config.structure_blueprint_config import (
            SERVICE_CLASS_INDICATORS,
        )

        assert len(SERVICE_CLASS_INDICATORS) > 5
        assert "Collector" in SERVICE_CLASS_INDICATORS
        assert "Monitor" in SERVICE_CLASS_INDICATORS
        assert "Tracker" in SERVICE_CLASS_INDICATORS


# ===========================================================================
# reasoning/ Folder Purity Enforcement
# ===========================================================================


class TestReasoningFolderPurity:
    """Tests that reasoning/ only allows *Agent.py files."""

    def test_agent_allowed_in_reasoning(self, agent, tmp_layer):
        """Files matching *Agent.py should be allowed in reasoning/."""
        f = tmp_layer / "reasoning" / "MetricsAgent.py"
        f.write_text("class MetricsAgent:\n    pass\n")
        result = agent._enforce_folder_purity(f)
        assert result is None, "Agent files should be allowed in reasoning/"

    def test_collector_evicted_from_reasoning(self, agent, tmp_layer):
        """Non-Agent Python files should be evicted from reasoning/."""
        code = textwrap.dedent("""\
            class RagTelemetryCollector:
                _instance = None
                def __new__(cls):
                    if cls._instance is None:
                        cls._instance = super().__new__(cls)
                    return cls._instance
                def record_query(self, latency_ms):
                    pass
                def get_metrics(self):
                    pass
        """)
        f = tmp_layer / "reasoning" / "rag_telemetry_collector.py"
        f.write_text(code)
        result = agent._enforce_folder_purity(f)
        assert result is not None, "Non-Agent file should violate reasoning/ purity"
        assert result["type"] == "FOLDER_PURITY_VIOLATION"
        assert result["suggested_folder"] == "utils"

    def test_init_py_allowed_in_reasoning(self, agent, tmp_layer):
        """__init__.py should always be allowed."""
        f = tmp_layer / "reasoning" / "__init__.py"
        f.write_text("")
        result = agent._enforce_folder_purity(f)
        assert result is None


# ===========================================================================
# Non-Python File Routing
# ===========================================================================


class TestNonPythonFileRouting:
    """Tests for YAML/JSON/HTML routing via NON_PYTHON_FOLDER_ROUTES."""

    def test_dashboard_yaml_evicted_from_config(self, agent, tmp_layer):
        """dashboard_ssot.yaml should be evicted from config/ to dashboards/."""
        f = tmp_layer / "config" / "dashboard_ssot.yaml"
        f.write_text("columns:\n  territory: Territory\n")
        result = agent._enforce_folder_purity(f)
        assert result is not None, "dashboard_ssot.yaml should violate config/ purity"
        assert result["suggested_folder"] == "dashboards"

    def test_regular_config_yaml_allowed(self, agent, tmp_layer):
        """A properly named *_config.yaml should be allowed in config/."""
        f = tmp_layer / "config" / "gravity_leak_config.yaml"
        f.write_text("key: value\n")
        result = agent._enforce_folder_purity(f)
        assert result is None, "*_config.yaml should be allowed in config/"

    def test_non_python_routes_config(self):
        """NON_PYTHON_FOLDER_ROUTES should map .yaml to config/ by default."""
        from agentic_core.L5_safety.config.structure_blueprint_config import (
            NON_PYTHON_FOLDER_ROUTES,
        )

        assert NON_PYTHON_FOLDER_ROUTES[".yaml"] == "config"
        assert NON_PYTHON_FOLDER_ROUTES[".html"] == "dashboards"
        assert NON_PYTHON_FOLDER_ROUTES["dashboard_ssot.yaml"] == "dashboards"

    def test_dashboards_purity_rules_exist(self):
        """dashboards/ should have purity rules allowing HTML/JS/CSS/YAML."""
        from agentic_core.L5_safety.config.structure_blueprint_config import (
            FOLDER_PURITY_RULES,
        )

        assert "dashboards" in FOLDER_PURITY_RULES
        patterns = FOLDER_PURITY_RULES["dashboards"]
        assert any(".html" in p for p in patterns)
        assert any(".js" in p for p in patterns)
        assert any(".yaml" in p for p in patterns)


# ===========================================================================
# _is_true_agent Hardening
# ===========================================================================


class TestIsTrueAgentHardening:
    """Tests that _is_true_agent requires corroborating signals for method-based detection."""

    def test_agent_suffix_always_true(self, agent, tmp_layer):
        """Class ending in 'Agent' should always be a true agent."""
        code = "class FooAgent:\n    pass\n"
        tree = ast.parse(code)
        node = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)][0]
        assert agent._is_true_agent(node, tmp_layer / "reasoning" / "FooAgent.py")

    def test_base_agent_inheritance_true(self, agent, tmp_layer):
        """Class inheriting from SovereignBaseAgent should be a true agent."""
        code = "class Foo(SovereignBaseAgent):\n    pass\n"
        tree = ast.parse(code)
        node = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)][0]
        assert agent._is_true_agent(node, tmp_layer / "reasoning" / "Foo.py")

    def test_execute_method_alone_not_agent(self, agent, tmp_layer):
        """Class with execute() in utils/ (no corroboration) should NOT be a true agent."""
        code = textwrap.dedent("""\
            class TaskRunner:
                def execute(self):
                    pass
        """)
        tree = ast.parse(code)
        node = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)][0]
        # File is in utils/, not reasoning/ — no corroboration
        assert not agent._is_true_agent(node, tmp_layer / "utils" / "task_runner.py")

    def test_execute_method_in_reasoning_is_agent(self, agent, tmp_layer):
        """Class with execute() in reasoning/ should be a true agent (folder corroboration)."""
        code = textwrap.dedent("""\
            class TaskRunner:
                def execute(self):
                    pass
        """)
        tree = ast.parse(code)
        node = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)][0]
        assert agent._is_true_agent(node, tmp_layer / "reasoning" / "TaskRunner.py")

    def test_heal_method_with_agent_docstring_is_agent(self, agent, tmp_layer):
        """Class with heal() and 'agent' in docstring should be a true agent."""
        code = textwrap.dedent('''\
            class Fixer:
                """A healing agent for code fixes."""
                def heal(self):
                    pass
        ''')
        tree = ast.parse(code)
        node = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)][0]
        assert agent._is_true_agent(node, tmp_layer / "enforcement" / "Fixer.py")

    def test_run_method_alone_not_agent(self, agent, tmp_layer):
        """Class with only run() should NOT be a true agent ('run' was removed as too generic)."""
        code = textwrap.dedent("""\
            class Pipeline:
                def run(self):
                    pass
        """)
        tree = ast.parse(code)
        node = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)][0]
        assert not agent._is_true_agent(node, tmp_layer / "reasoning" / "Pipeline.py")


# ===========================================================================
# Dual-Tag Resolver Hardening
# ===========================================================================


class TestDualTagResolverHardening:
    """Tests that dual-tag resolver doesn't blindly force reasoning/ -> AGENT."""

    def test_service_in_reasoning_not_forced_to_agent(self, agent, tmp_layer):
        """A dual-tag file in reasoning/ should be classified by AST, not forced to AGENT."""
        # agent_monitor.py has "agent" in the name (AGENT tag) and "monitor" (SERVICE tag)
        code = textwrap.dedent("""\
            class UnifiedAgentMonitor:
                _instance = None
                def __new__(cls):
                    if cls._instance is None:
                        cls._instance = super().__new__(cls)
                    return cls._instance
                def record_execution(self, name, time_ms):
                    pass
                def get_metrics(self):
                    pass
        """)
        f = tmp_layer / "reasoning" / "agent_monitor.py"
        f.write_text(code)
        result = agent.classify_file(f)
        assert result == "SERVICE", (
            f"Expected SERVICE but got {result}. Dual-tag resolver should NOT force reasoning/ -> AGENT."
        )

    def test_true_agent_in_reasoning_stays_agent(self, agent, tmp_layer):
        """A real agent in reasoning/ should still be classified as AGENT."""
        code = textwrap.dedent("""\
            class MetricsAgent:
                def execute(self):
                    pass
        """)
        f = tmp_layer / "reasoning" / "MetricsAgent.py"
        f.write_text(code)
        assert agent.classify_file(f) == "AGENT"
