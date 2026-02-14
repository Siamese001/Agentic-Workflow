"""§Wave5.0.6 — Micro-tests for robust filesystem helpers."""

from __future__ import annotations

import os
import stat
from pathlib import Path

from tests._helpers.robust_fs import robust_rmtree


class TestRobustRmtree:
    """Prove robust_rmtree handles read-only files without timing."""

    def test_removes_tree_with_readonly_file(self, tmp_path: Path) -> None:
        d = tmp_path / "locked"
        d.mkdir()
        f = d / "readonly.txt"
        f.write_text("locked", encoding="utf-8")
        os.chmod(str(f), stat.S_IREAD)

        robust_rmtree(d)
        assert not d.exists()

    def test_noop_on_missing_path(self, tmp_path: Path) -> None:
        missing = tmp_path / "does_not_exist"
        robust_rmtree(missing)  # must not raise
