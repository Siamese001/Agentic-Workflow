"""E2E tests for layer isolation across the codebase."""

from pathlib import Path

import pytest


class TestLayerIsolation:
    """Tests for layer isolation principles."""

    def test_l1_does_not_import_l3(self):
        """L1 cognition should not import L3 orchestration."""
        base = Path("agentic_core/L1_cognition")
        if not base.exists():
            pytest.skip("L1_cognition/ not found")

        # Known exceptions (documented architectural decisions)
        known_exceptions = ["cognitive_engine.py"]

        violations = []
        for py_file in base.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
            if any(exc in str(py_file) for exc in known_exceptions):
                continue
            content = py_file.read_text(encoding="utf-8", errors="ignore")
            if (
                "from agentic_core.L3_orchestration" in content
                or "import agentic_core.L3_orchestration" in content
            ):
                violations.append(str(py_file))

        assert len(violations) == 0, f"L1 should not import L3: {violations}"

    def test_l4_does_not_import_l1(self):
        """L4 state should not import L1 cognition."""
        base = Path("agentic_core/L4_state")
        if not base.exists():
            pytest.skip("L4_state/ not found")

        violations = []
        for py_file in base.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
            content = py_file.read_text(encoding="utf-8", errors="ignore")
            if "from agentic_core.L1_cognition" in content or "import agentic_core.L1_cognition" in content:
                violations.append(str(py_file))

        assert len(violations) == 0, f"L4 should not import L1: {violations}"

    def test_l6_does_not_import_l1(self):
        """L6 observability should not import L1 cognition."""
        base = Path("agentic_core/L6_observability")
        if not base.exists():
            pytest.skip("L6_observability/ not found")

        # Known exceptions (documented architectural decisions)
        known_exceptions = ["experiencein_config.py"]

        violations = []
        for py_file in base.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
            if any(exc in str(py_file) for exc in known_exceptions):
                continue
            content = py_file.read_text(encoding="utf-8", errors="ignore")
            if "from agentic_core.L1_cognition" in content or "import agentic_core.L1_cognition" in content:
                violations.append(str(py_file))

        assert len(violations) == 0, f"L6 should not import L1: {violations}"


class TestAppsSharedIndependence:
    """Tests for apps_shared independence."""

    def test_apps_shared_does_not_import_apps_rg(self):
        """apps_shared should not import apps_rg."""
        base = Path("apps_shared")
        if not base.exists():
            pytest.skip("apps_shared/ not found")

        # Known exceptions (documented architectural decisions)
        known_exceptions = ["golden_state_evaluator_types.py"]

        violations = []
        for py_file in base.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
            if any(exc in str(py_file) for exc in known_exceptions):
                continue
            content = py_file.read_text(encoding="utf-8", errors="ignore")
            if "from apps_rg" in content or "import apps_rg" in content:
                violations.append(str(py_file))

        assert len(violations) == 0, f"apps_shared should not import apps_rg: {violations}"

    def test_apps_shared_does_not_import_apps_lic(self):
        """apps_shared should not import apps_lic."""
        base = Path("apps_shared")
        if not base.exists():
            pytest.skip("apps_shared/ not found")

        violations = []
        for py_file in base.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
            content = py_file.read_text(encoding="utf-8", errors="ignore")
            if "from apps_lic" in content or "import apps_lic" in content:
                violations.append(str(py_file))

        assert len(violations) == 0, f"apps_shared should not import apps_lic: {violations}"


class TestBaseAgentLocation:
    """Tests for base agent location constitutional rule."""

    def test_base_agents_in_base_agents_folder(self):
        """All *Base.py and *BaseAgent.py files should be in base_agents/."""
        base = Path("agentic_core")
        if not base.exists():
            pytest.skip("agentic_core/ not found")

        # Known exceptions (documented architectural decisions)
        # AdapterBase.py is a V10 Legacy Bridge Pattern base class, not a SovereignBaseAgent
        known_exceptions = ["AdapterBase.py"]

        violations = []
        for py_file in base.rglob("*Base.py"):
            if "__pycache__" in str(py_file):
                continue
            if "base_agents" not in str(py_file):
                if not any(exc in str(py_file) for exc in known_exceptions):
                    violations.append(str(py_file))

        for py_file in base.rglob("*BaseAgent.py"):
            if "__pycache__" in str(py_file):
                continue
            if "base_agents" not in str(py_file):
                if not any(exc in str(py_file) for exc in known_exceptions):
                    violations.append(str(py_file))

        assert len(violations) == 0, f"Base agents outside base_agents/: {violations}"
