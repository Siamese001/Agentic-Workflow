"""CI parity test — generic binding consumer script semantics."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_generic_app_binding_consumer_script_passes() -> None:
    script = REPO_ROOT / "ops_scripts/ci/check_generic_app_binding_consumer.py"
    proc = subprocess.run(
        [sys.executable, str(script)],
        cwd=str(REPO_ROOT),
        check=False,
    )
    assert proc.returncode == 0


def test_fixture_package_manifest_exists() -> None:
    manifest = REPO_ROOT / "tests/_core_contract/fixtures/apps_rg_binding_package/app_binding_sections.binding_v1.yaml"
    assert manifest.is_file()
