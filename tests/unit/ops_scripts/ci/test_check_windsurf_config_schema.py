"""Tests for the Windsurf config schema purity gate (constitutional §27).

Validates the gate passes on the live config and fails when an unknown
field is injected into a hooks.json copy. Required because §27 was
previously gate-only with no test coverage — a 2026-04-23 regression
(``powershell`` field added to 23 hook entries) silently disabled the
post_cascade hook chain across a full Windsurf restart.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
GATE = REPO_ROOT / "ops_scripts" / "ci" / "check_windsurf_config_schema.py"
HOOKS_JSON = REPO_ROOT / ".windsurf" / "hooks.json"


def _run_gate(cwd: Path, *, gate_path: Path | None = None) -> subprocess.CompletedProcess:
    """Run the gate. ``gate_path`` defaults to the real-repo gate; pass an
    alternate path to exercise a copied gate against a fake-repo fixture."""
    return subprocess.run(  # noqa: S603 — fixed argv, shell=False
        [sys.executable, str(gate_path or GATE)],
        capture_output=True,
        text=True,
        cwd=str(cwd),
        timeout=30,
        check=False,
    )


class TestPassesOnLiveConfig:
    def test_live_config_passes(self) -> None:
        """The current repo's hooks.json + mcp_config.json must pass §27."""
        result = _run_gate(REPO_ROOT)
        assert result.returncode == 0, (
            f"live config rejected; stdout={result.stdout!r}, "
            f"stderr={result.stderr!r}"
        )


class TestRejectsUnknownFieldInHooks:
    def test_powershell_field_rejected(self, tmp_path: Path) -> None:
        """Constitutional §27 invariant: unknown hooks.json fields fail closed."""
        # Create a fake repo layout with a tampered hooks.json.
        fake_repo = tmp_path / "repo"
        (fake_repo / ".windsurf").mkdir(parents=True)
        (fake_repo / "ops_scripts" / "ci").mkdir(parents=True)

        # Copy the real gate into the fake repo so its REPO_ROOT resolves
        # to fake_repo.
        gate_copy = fake_repo / "ops_scripts" / "ci" / GATE.name
        shutil.copy2(GATE, gate_copy)

        # Tampered hooks.json with an unknown `powershell` field.
        tampered = {
            "post_cascade_response": [
                {
                    "command": "echo hi",
                    "working_directory": ".",
                    "show_output": False,
                    "powershell": "not-allowed",
                }
            ]
        }
        (fake_repo / ".windsurf" / "hooks.json").write_text(
            json.dumps(tampered, indent=2), encoding="utf-8"
        )
        # Minimal valid mcp_config.json so the mcp validator does not error.
        (fake_repo / ".windsurf" / "mcp_config.json").write_text(
            json.dumps({"mcpServers": {}}, indent=2), encoding="utf-8"
        )

        result = _run_gate(fake_repo, gate_path=gate_copy)
        assert result.returncode != 0, (
            "gate must reject hooks.json with unknown 'powershell' field; "
            f"stdout={result.stdout!r}"
        )


class TestRejectsUnknownFieldInMcp:
    def test_unknown_mcp_field_rejected(self, tmp_path: Path) -> None:
        fake_repo = tmp_path / "repo"
        (fake_repo / ".windsurf").mkdir(parents=True)
        (fake_repo / "ops_scripts" / "ci").mkdir(parents=True)
        gate_copy = fake_repo / "ops_scripts" / "ci" / GATE.name
        shutil.copy2(GATE, gate_copy)

        (fake_repo / ".windsurf" / "hooks.json").write_text(
            json.dumps({}, indent=2), encoding="utf-8"
        )
        # Tampered mcp_config.json with unknown `platform` field on a server.
        tampered = {
            "mcpServers": {
                "fake": {
                    "command": "python",
                    "args": ["-m", "fake"],
                    "platform": "windows-only",  # NOT in published schema
                }
            }
        }
        (fake_repo / ".windsurf" / "mcp_config.json").write_text(
            json.dumps(tampered, indent=2), encoding="utf-8"
        )

        result = _run_gate(fake_repo, gate_path=gate_copy)
        assert result.returncode != 0, (
            "gate must reject mcp_config.json with unknown 'platform' field"
        )
