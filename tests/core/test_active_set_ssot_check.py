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

from ops_scripts.ci.active_set_ssot_check import check_script_ast

COMPLIANT_SCRIPT = dedent("""\
    from __future__ import annotations
    import sys
    from pathlib import Path

    def main():
        from ops_scripts.ci.active_set_helper import get_active_set
        result = get_active_set(Path("."))
        print(result.count)
""")

NON_COMPLIANT_DIRECT_IMPORT = dedent("""\
    from __future__ import annotations
    from agentic_core.L0_maintenance.utils.ssot_discovery_util import load_agent_discovery
    from ops_scripts.ci.active_set_helper import get_active_set

    def main():
        raw = load_agent_discovery(None)
""")

NON_COMPLIANT_ALIASED_IMPORT = dedent("""\
    from __future__ import annotations
    from agentic_core.L0_maintenance.scripts import full_agent_discovery as fad
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
