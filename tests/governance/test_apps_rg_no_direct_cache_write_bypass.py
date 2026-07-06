from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.apps_test_model("GOVERNANCE STATIC")

REPO_ROOT = Path(__file__).resolve().parents[2]
SCANNER = REPO_ROOT / "ops_scripts" / "ci" / "check_apps_rg_no_direct_durable_writes.py"


def _run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        timeout=30,
        check=False,
    )


def test_direct_durable_write_scanner_passes_repo() -> None:
    result = _run(str(SCANNER))
    assert result.returncode == 0, result.stdout + result.stderr
    assert "gate GREEN" in result.stdout


def test_direct_durable_write_scanner_fails_chroma_bypass_fixture(tmp_path: Path) -> None:
    fixture = tmp_path / "bad_direct_write.py"
    fixture.write_text(
        "import chromadb\n"
        "def write_directly():\n"
        "    client = chromadb.PersistentClient(path='cache')\n"
        "    collection = client.get_or_create_collection('apps_rg_cache')\n"
        "    collection.upsert(ids=['1'], documents=['x'])\n",
        encoding="utf-8",
    )

    result = _run(str(SCANNER), "--extra-path", str(fixture))

    assert result.returncode == 1
    assert "direct chromadb import" in result.stdout
    assert "direct Chroma durable write primitive" in result.stdout
