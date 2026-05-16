"""E2E prove harness boundary_no_bypass hygiene (git porcelain classification)."""

from __future__ import annotations

import importlib.util
import subprocess
import unittest
from pathlib import Path
from unittest.mock import patch

_REPO_ROOT = Path(__file__).resolve().parents[2]


def _load_prove_module():  # noqa: ANN201
    path = _REPO_ROOT / "ops_scripts" / "ci" / "prove_apps_rg_e2e_runtime.py"
    spec = importlib.util.spec_from_file_location("_prove_apps_rg_e2e_runtime_boundary", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


class TestAppsRgE2eBoundaryHygiene(unittest.TestCase):
    def test_classify_mixed_dirty_paths(self) -> None:
        peg = _load_prove_module()
        k = peg.classify_agentic_core_porcelain_lines([" M agentic_core/foo.py", "?? agentic_core/bar.tmp"])
        self.assertTrue(k["agentic_core_modified"])
        self.assertIn("TRACKED_AND_UNTRACKED", k["agentic_core_dirty_reason"])

    def test_finalize_pins_modified_by_this_task_false(self) -> None:
        peg = _load_prove_module()

        def fake_run(argv: list[str], *, cwd: Path, env=None):  # noqa: ANN001
            if argv[:4] == ["git", "status", "--porcelain=v1", "--"] and argv[4:] == ["agentic_core"]:
                return subprocess.CompletedProcess(argv, 0, "", "")
            raise AssertionError(f"unexpected argv: {argv}")

        with patch.object(peg, "_run_cmd", fake_run):
            art = peg._minimal_artifact()
            peg.finalize_boundary_no_bypass(art, _REPO_ROOT)
        self.assertFalse(art["boundary_no_bypass"]["agentic_core_modified"])
        self.assertFalse(art["boundary_no_bypass"]["agentic_core_modified_by_this_task"])


if __name__ == "__main__":
    unittest.main()
