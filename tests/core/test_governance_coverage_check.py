"""Unit tests for governance_coverage_check.py (SSOT governance expansion)."""

from __future__ import annotations

import ast
import sys
import textwrap
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from ops_scripts.ci.governance_coverage_check import (
    _EXEMPT_SCRIPTS,
    _find_governed_references,
    _imports_helper,
)


class TestImportsHelper:
    """AST-based helper import detection."""

    def test_from_import(self):
        source = "from ops_scripts.ci.active_set_helper import get_active_set"
        tree = ast.parse(source)
        assert _imports_helper(tree) is True

    def test_plain_import(self):
        source = "import ops_scripts.ci.active_set_helper as h"
        tree = ast.parse(source)
        assert _imports_helper(tree) is True

    def test_no_import(self):
        source = "import os\nimport sys"
        tree = ast.parse(source)
        assert _imports_helper(tree) is False


class TestFindGovernedReferences:
    """Detection of governed resource references."""

    def test_prohibited_module_import_from(self):
        source = "from agentic_core.L0_maintenance.utils.ssot_discovery_util import load_agent_discovery"
        tree = ast.parse(source)
        refs = _find_governed_references(tree, source)
        assert len(refs) >= 1
        assert any("prohibited module" in r for r in refs)

    def test_prohibited_module_plain_import(self):
        source = "import agentic_core.L0_maintenance.scripts.full_agent_discovery"
        tree = ast.parse(source)
        refs = _find_governed_references(tree, source)
        assert len(refs) >= 1
        assert any("prohibited module" in r for r in refs)

    def test_prohibited_name_import(self):
        source = "from some_module import perform_deep_integrity_scan"
        tree = ast.parse(source)
        refs = _find_governed_references(tree, source)
        assert any("prohibited" in r for r in refs)

    def test_string_literal_reference(self):
        source = 'path = "agent_discovery_full.json"'
        tree = ast.parse(source)
        refs = _find_governed_references(tree, source)
        assert any("agent_discovery_full.json" in r for r in refs)

    def test_clean_script_no_refs(self):
        source = textwrap.dedent("""\
            import os
            import sys
            def main():
                print("hello")
        """)
        tree = ast.parse(source)
        refs = _find_governed_references(tree, source)
        assert refs == []

    def test_dict_key_not_false_positive(self):
        source = textwrap.dedent("""\
            config = {"some_key": "value"}
            x = config.get("other_key", None)
        """)
        tree = ast.parse(source)
        refs = _find_governed_references(tree, source)
        assert refs == []


class TestExemptions:
    """Governance infrastructure scripts are exempt."""

    def test_exempt_scripts_include_infra(self):
        assert "active_set_helper.py" in _EXEMPT_SCRIPTS
        assert "active_set_ssot_check.py" in _EXEMPT_SCRIPTS
        assert "governance_coverage_check.py" in _EXEMPT_SCRIPTS
        assert "gate_consistency_check.py" in _EXEMPT_SCRIPTS
        assert "mro_new_diamond_check.py" in _EXEMPT_SCRIPTS

    def test_exempt_scripts_do_not_include_consumer_scripts(self):
        assert "agent_count_cap.py" not in _EXEMPT_SCRIPTS
        assert "discovery_registry_consistency_check.py" not in _EXEMPT_SCRIPTS


class TestBypassDetection:
    """A script with prohibited refs but no helper import is caught."""

    def test_bypass_caught(self):
        source = textwrap.dedent("""\
            from agentic_core.L0_maintenance.utils.ssot_discovery_util import load_agent_discovery

            def main():
                data = load_agent_discovery(".")
        """)
        tree = ast.parse(source)
        refs = _find_governed_references(tree, source)
        has_helper = _imports_helper(tree)
        assert len(refs) >= 1
        assert has_helper is False

    def test_compliant_script_not_caught(self):
        source = textwrap.dedent("""\
            from ops_scripts.ci.active_set_helper import get_active_set

            def main():
                result = get_active_set(".")
        """)
        tree = ast.parse(source)
        refs = _find_governed_references(tree, source)
        has_helper = _imports_helper(tree)
        # No governed references (it uses the helper properly)
        assert refs == []
        assert has_helper is True
