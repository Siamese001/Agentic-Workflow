"""W2 — Exit + X3 disposition uniqueness and consumption."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

LATEST = REPO_ROOT / "artifacts" / "certification" / "integrated_runtime" / "latest"

import pytest  # noqa: E402

pytestmark = pytest.mark.skipif(
    not (LATEST / "integrated_runtime_artifact_manifest.json").exists(),
    reason=(
        "W2b honest non-green: latest/ empty without approved live provider. "
        "Run probe_integrated_runtime_safe_reuse.py with local_qwen reachable "
        "or ANTHROPIC_API_KEY set."
    ),
)


class TestExitX3:
    def test_exactly_one_x3_receipt_in_chain(self):
        x3 = json.loads((LATEST / "x3_disposition_receipt.json").read_text(encoding="utf-8"))
        assert "x3_disposition" in x3["payload"]
        assert x3["payload"]["x3_disposition"] in {"X3A", "X3B", "X3C", "X3D", "X3E", "X3F"}

    def test_exit_review_consumed_terminal_route(self):
        terminal = json.loads((LATEST / "terminal_ret_packet.json").read_text(encoding="utf-8"))
        review = json.loads((LATEST / "exit_review_packet.json").read_text(encoding="utf-8"))
        assert review["payload"]["route_id"] == terminal["payload"]["route_id"]

    def test_exit_review_no_l2_no_l4(self):
        review = json.loads((LATEST / "exit_review_packet.json").read_text(encoding="utf-8"))
        assert review["payload"]["no_l2_execution_assertion"] is True
        assert review["payload"]["no_l4_write_assertion"] is True


class TestExitX3FailClosed:
    def _copy(self, tmp_path: Path) -> Path:
        out = tmp_path / "art"
        shutil.copytree(LATEST, out)
        return out

    def test_x3_receipt_missing_blocks(self, tmp_path):
        art = self._copy(tmp_path)
        (art / "x3_disposition_receipt.json").unlink()
        proc = subprocess.run(
            [sys.executable, "ops_scripts/ci/verify_integrated_runtime_exit_x3.py", str(art)],
            capture_output=True, text=True, cwd=str(REPO_ROOT), timeout=30, shell=False,
        )
        assert proc.returncode == 2
        assert "ARTIFACT_MISSING" in proc.stdout

    def test_terminal_l2_assertion_false_blocks(self, tmp_path):
        art = self._copy(tmp_path)
        env = json.loads((art / "terminal_ret_packet.json").read_text(encoding="utf-8"))
        env["payload"]["no_l2_execution_assertion"] = False
        (art / "terminal_ret_packet.json").write_text(json.dumps(env, indent=2), encoding="utf-8")
        proc = subprocess.run(
            [sys.executable, "ops_scripts/ci/verify_integrated_runtime_exit_x3.py", str(art)],
            capture_output=True, text=True, cwd=str(REPO_ROOT), timeout=30, shell=False,
        )
        assert proc.returncode == 2
        assert "L2_ASSERTION_FALSE" in proc.stdout

    def test_route_mismatch_blocks(self, tmp_path):
        art = self._copy(tmp_path)
        env = json.loads((art / "exit_review_packet.json").read_text(encoding="utf-8"))
        env["payload"]["route_id"] = "ROUTE_MUTATED"
        (art / "exit_review_packet.json").write_text(json.dumps(env, indent=2), encoding="utf-8")
        proc = subprocess.run(
            [sys.executable, "ops_scripts/ci/verify_integrated_runtime_exit_x3.py", str(art)],
            capture_output=True, text=True, cwd=str(REPO_ROOT), timeout=30, shell=False,
        )
        assert proc.returncode == 2
        assert "EXIT_TERMINAL_ROUTE_MISMATCH" in proc.stdout
