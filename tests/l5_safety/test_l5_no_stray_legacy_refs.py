"""
L5 No Stray Legacy String Refs Contract Test

Ensures that deleted legacy agent names do not appear as string literals
outside their canonical allowlist and this test file. This prevents
re-inflation of agent counts via orphaned string references.
"""

import os
from pathlib import Path


class TestNoStrayLegacyStringRefs:
    """Deleted legacy agent names must not appear as string literals outside canonical locations."""

    _CANONICAL_FILES = {
        os.path.normpath("agentic_core/L0_maintenance/legacy_agent_name_allowlist.py"),
        os.path.normpath("tests/l5_safety/test_l5_agent_inventory_contract.py"),
        os.path.normpath("tests/l5_safety/test_l5_no_stray_legacy_refs.py"),
    }

    def test_no_stray_string_refs_for_legacy_agents(self):
        from agentic_core.L0_maintenance.legacy_agent_name_allowlist import (
            LEGACY_AGENT_NAME_ALLOWLIST,
        )

        project_root = Path(__file__).parent.parent.parent
        failures = []

        for legacy_name in LEGACY_AGENT_NAME_ALLOWLIST:
            for py_file in project_root.rglob("*.py"):
                rel = os.path.normpath(py_file.relative_to(project_root))
                if rel in self._CANONICAL_FILES:
                    continue
                basename = os.path.basename(rel)
                if legacy_name in basename:
                    continue
                parts = Path(rel).parts
                if any(p.startswith(".") or p == "__pycache__" or p == ".nox" for p in parts):
                    continue
                try:
                    text = py_file.read_text(encoding="utf-8", errors="ignore")
                except OSError:
                    continue
                if legacy_name in text:
                    failures.append(f"{legacy_name} found in {rel}")

        assert not failures, (
            f"Stray string refs for deleted legacy agents found outside canonical "
            f"locations ({len(failures)} hits).\n"
            f"Fix: remove the literal or import from "
            f"agentic_core.L0_maintenance.legacy_agent_name_allowlist.\n"
            + "\n".join(failures)
        )
