"""Regression tests for Memory MCP lightweight startup imports."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def test_adg_memory_server_import_does_not_load_torch(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[4]
    env = os.environ.copy()
    env["ADG_REDIS_URL"] = "redis://localhost:6379/0"
    env["MEMORY_DB"] = str(tmp_path / "knowledge_graph.sqlite")
    env["PYTHONPATH"] = str(repo_root)

    command = (
        "import sys; "
        "import tools.memory.adg_memory_server; "
        "print('memory import ok'); "
        "print('torch_loaded', 'torch' in sys.modules)"
    )
    result = subprocess.run(
        [sys.executable, "-c", command],
        cwd=repo_root,
        env=env,
        text=True,
        capture_output=True,
        shell=False,
        timeout=30,
    )

    assert result.returncode == 0, result.stderr
    assert "memory import ok" in result.stdout
    assert "torch_loaded False" in result.stdout
