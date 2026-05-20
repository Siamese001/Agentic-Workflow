"""E2E prove harness boundary_no_bypass hygiene (git porcelain classification)."""

from __future__ import annotations

import subprocess
import unittest
from pathlib import Path
from unittest.mock import patch

from tests.helpers import ci_lane_dev_boundary as peg

_REPO_ROOT = Path(__file__).resolve().parents[2]


class TestAppsRgE2eBoundaryHygiene(unittest.TestCase):
    def test_classify_mixed_dirty_paths(self) -> None:
        k = peg.classify_agentic_core_porcelain_lines([" M agentic_core/foo.py", "?? agentic_core/bar.tmp"])
        self.assertTrue(k["agentic_core_modified"])
        self.assertIn("TRACKED_AND_UNTRACKED", k["agentic_core_dirty_reason"])

    def test_finalize_pins_modified_by_this_task_false(self) -> None:
        def fake_run(argv: list[str], *, cwd: Path, env=None):  # noqa: ANN001
            if argv[:4] == ["git", "status", "--porcelain=v1", "--"] and argv[4:] == ["agentic_core"]:
                return subprocess.CompletedProcess(argv, 0, "", "")
            raise AssertionError(f"unexpected argv: {argv}")

        with patch.object(peg, "run_git_cmd", fake_run):
            art = peg.minimal_ci_lane_dev_artifact()
            peg.finalize_boundary_no_bypass(art, _REPO_ROOT)
        self.assertFalse(art["boundary_no_bypass"]["agentic_core_modified"])
        self.assertFalse(art["boundary_no_bypass"]["agentic_core_modified_by_this_task"])


if __name__ == "__main__":
    unittest.main()
