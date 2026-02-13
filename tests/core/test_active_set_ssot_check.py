#!/usr/bin/env python3
"""Unit tests for the AST-based Active Set SSOT Check.

Tests check_script_ast with compliant and non-compliant fixtures
to confirm that aliased imports, direct pipeline calls, and
prohibited string references are all caught.
"""

from __future__ import annotations

import sys
from pathlib import Path
from textwrap import dedent

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from ops_scripts.ci.active_set_ssot_check import (
    check_script_ast,
    discover_governed_scripts,
)

COMPLIANT_SCRIPT = dedent("""\
    from __future__ import annotations
    import sys
    from pathlib import Path

    def main():
        from ops_scripts.ci.active_set_helper import get_active_set
        result = get_active_set(Path("."))
        print(result.count)
""")

COMPLIANT_PLAIN_IMPORT = dedent("""\
    from __future__ import annotations
    import sys
    from pathlib import Path
    import ops_scripts.ci.active_set_helper as h

    def main():
        result = h.get_active_set(Path("."))
        print(result.count)
""")

NON_COMPLIANT_DIRECT_IMPORT = dedent("""\
    from __future__ import annotations
    from agentic_core.L0_routing.utils.ssot_discovery_util import load_agent_discovery
    from ops_scripts.ci.active_set_helper import get_active_set

    def main():
        raw = load_agent_discovery(None)
""")

NON_COMPLIANT_ALIASED_IMPORT = dedent("""\
    from __future__ import annotations
    from agentic_core.L0_routing.scripts import full_agent_discovery as fad
    from ops_scripts.ci.active_set_helper import get_active_set

    def main():
        verified, stats = fad.perform_deep_integrity_scan([], None)
""")

NON_COMPLIANT_STRING_REF = dedent("""\
    from __future__ import annotations
    import json
    from ops_scripts.ci.active_set_helper import get_active_set

    DISCOVERY = "agent_discovery_full.json"
""")

NON_COMPLIANT_NO_HELPER = dedent("""\
    from __future__ import annotations
    import json

    def main():
        pass
""")

NON_COMPLIANT_NAME_REF = dedent("""\
    from __future__ import annotations
    from ops_scripts.ci.active_set_helper import get_active_set

    def main():
        x = load_agent_discovery
""")

NON_COMPLIANT_ATTR_REF = dedent("""\
    from __future__ import annotations
    from ops_scripts.ci.active_set_helper import get_active_set

    def main():
        y = obj.perform_deep_integrity_scan
""")

NON_COMPLIANT_CALL_ONLY = dedent("""\
    from __future__ import annotations
    from ops_scripts.ci.active_set_helper import get_active_set

    def main():
        result = get_active_set(None)
        # Bypass: also call pipeline directly via alias
        obj = some_module
        obj.perform_deep_integrity_scan([], None)
""")


class TestCompliantScript:
    def test_no_violations(self) -> None:
        violations = check_script_ast(COMPLIANT_SCRIPT, "test_compliant.py")
        assert violations == []

    def test_no_violations_plain_import(self) -> None:
        violations = check_script_ast(COMPLIANT_PLAIN_IMPORT, "test_plain_import.py")
        assert violations == []


class TestNonCompliantScripts:
    def test_direct_import_ssot_discovery_util(self) -> None:
        violations = check_script_ast(NON_COMPLIANT_DIRECT_IMPORT, "test_direct.py")
        assert len(violations) >= 1
        assert any("ssot_discovery_util" in v for v in violations)

    def test_aliased_import_full_agent_discovery(self) -> None:
        violations = check_script_ast(NON_COMPLIANT_ALIASED_IMPORT, "test_aliased.py")
        assert len(violations) >= 1
        assert any("full_agent_discovery" in v for v in violations)

    def test_prohibited_string_reference(self) -> None:
        violations = check_script_ast(NON_COMPLIANT_STRING_REF, "test_string.py")
        assert len(violations) >= 1
        assert any("agent_discovery_full.json" in v for v in violations)

    def test_missing_helper_import(self) -> None:
        violations = check_script_ast(NON_COMPLIANT_NO_HELPER, "test_no_helper.py")
        assert len(violations) >= 1
        assert any("active_set_helper" in v for v in violations)

    def test_prohibited_call_via_attribute(self) -> None:
        violations = check_script_ast(NON_COMPLIANT_CALL_ONLY, "test_call.py")
        assert len(violations) >= 1
        assert any("perform_deep_integrity_scan" in v for v in violations)

    def test_prohibited_name_reference_without_call(self) -> None:
        violations = check_script_ast(NON_COMPLIANT_NAME_REF, "test_name_ref.py")
        assert len(violations) >= 1
        assert any("reference to prohibited name" in v for v in violations)
        assert any("load_agent_discovery" in v for v in violations)

    def test_prohibited_attr_reference_without_call(self) -> None:
        violations = check_script_ast(NON_COMPLIANT_ATTR_REF, "test_attr_ref.py")
        assert len(violations) >= 1
        assert any("reference to prohibited attribute" in v for v in violations)
        assert any("perform_deep_integrity_scan" in v for v in violations)


class TestGovernanceSelector:
    def test_discovers_governed_script(self, tmp_path: Path) -> None:
        """A script containing active-set markers is governed."""
        ci_dir = tmp_path / "ops_scripts" / "ci"
        ci_dir.mkdir(parents=True)
        governed_script = ci_dir / "my_gate.py"
        governed_script.write_text(
            "from ops_scripts.ci.active_set_helper import get_active_set\n",
            encoding="utf-8",
        )
        ungoverned_script = ci_dir / "other_gate.py"
        ungoverned_script.write_text(
            "import json\ndef main(): pass\n",
            encoding="utf-8",
        )
        # Excluded by name
        helper = ci_dir / "active_set_helper.py"
        helper.write_text("# helper\n", encoding="utf-8")

        result = discover_governed_scripts(ci_dir)
        assert "ops_scripts/ci/my_gate.py" in result
        assert "ops_scripts/ci/other_gate.py" not in result
        assert "ops_scripts/ci/active_set_helper.py" not in result

    def test_excludes_self_and_helper(self, tmp_path: Path) -> None:
        ci_dir = tmp_path / "ops_scripts" / "ci"
        ci_dir.mkdir(parents=True)
        for name in ("__init__.py", "active_set_helper.py", "active_set_ssot_check.py"):
            (ci_dir / name).write_text("# active_set_helper marker\n", encoding="utf-8")
        result = discover_governed_scripts(ci_dir)
        assert result == []

    def test_prohibited_usage_auto_governed(self, tmp_path: Path) -> None:
        """Scripts with prohibited usage are auto-governed even without helper import."""
        ci_dir = tmp_path / "ops_scripts" / "ci"
        ci_dir.mkdir(parents=True)
        # a.py: imports helper -> governed
        (ci_dir / "a.py").write_text(
            "from ops_scripts.ci.active_set_helper import get_active_set\n",
            encoding="utf-8",
        )
        # b.py: no helper, no prohibited -> NOT governed
        (ci_dir / "b.py").write_text(
            "import json\ndef main(): pass\n",
            encoding="utf-8",
        )
        # c.py: contains prohibited string -> SHOULD be governed
        (ci_dir / "c.py").write_text(
            'DISCOVERY = "agent_discovery_full.json"\n',
            encoding="utf-8",
        )
        result = discover_governed_scripts(ci_dir)
        assert result == ["ops_scripts/ci/a.py", "ops_scripts/ci/c.py"]
