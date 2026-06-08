"""Tests for check_mcp_config_sovereignty.py — Constitutional Rule #0."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from ops_scripts.ci import check_mcp_config_sovereignty as sovereignty


def _filesystem_block(
    launcher: str = "${env:AGENTIC_REPO_ROOT}/.claude/governance/scripts/filesystem_mcp_launcher.js",
    root_arg: str = "${env:AGENTIC_REPO_ROOT}",
    *,
    disabled: bool = True,
    comment: str = "Filesystem MCP scope is locked to repo root only (Rule #0).",
) -> dict:
    return {
        "command": "node",
        "args": [launcher, root_arg],
        "disabled": disabled,
        "_comment": comment,
    }


def _minimal_config(filesystem: dict | None = None) -> dict:
    fs = filesystem if filesystem is not None else _filesystem_block()
    return {
        "mcpServers": {
            "filesystem": fs,
            "memory": {"command": "python", "args": ["-u", "x.py"], "disabled": False},
        }
    }


def test_evaluate_passes_on_repo_configs() -> None:
    report = sovereignty.evaluate()
    assert report["valid"] is True
    assert report["violation_count"] == 0


def test_missing_filesystem_fails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    cfg = {"mcpServers": {"memory": {"command": "python", "args": []}}}
    path = tmp_path / "mcp.json"
    path.write_text(json.dumps(cfg), encoding="utf-8")
    violations = sovereignty.validate_profile("cursor", path, ".claude/governance/scripts/filesystem_mcp_launcher.js")
    assert any(v.code == "MISSING_FILESYSTEM" for v in violations)


def test_forbidden_path_fragment_fails(tmp_path: Path) -> None:
    cfg = _minimal_config(
        _filesystem_block(
            launcher="${env:AGENTIC_REPO_ROOT}/.claude/governance/scripts/filesystem_mcp_launcher.js",
        )
    )
    cfg["mcpServers"]["notion"] = {
        "command": "cmd",
        "args": ["/c", "npx", "C:/Users/amita/secret"],
    }
    path = tmp_path / "mcp.json"
    path.write_text(json.dumps(cfg), encoding="utf-8")
    violations = sovereignty.validate_profile("cursor", path, ".claude/governance/scripts/filesystem_mcp_launcher.js")
    assert any(v.code == "FORBIDDEN_PATH_FRAGMENT" for v in violations)


def test_wrong_root_arg_fails(tmp_path: Path) -> None:
    cfg = _minimal_config(
        _filesystem_block(root_arg="C:/Git/Agentic-Workflow-FRESH")
    )
    path = tmp_path / "mcp.json"
    path.write_text(json.dumps(cfg), encoding="utf-8")
    violations = sovereignty.validate_profile("cursor", path, ".claude/governance/scripts/filesystem_mcp_launcher.js")
    assert any(v.code == "FILESYSTEM_ROOT_ARG" for v in violations)


def test_shadow_disabled_still_passes_scope(tmp_path: Path) -> None:
    cfg = _minimal_config(_filesystem_block(disabled=True))
    path = tmp_path / "mcp.json"
    path.write_text(json.dumps(cfg), encoding="utf-8")
    violations = sovereignty.validate_profile("cursor", path, ".claude/governance/scripts/filesystem_mcp_launcher.js")
    assert violations == []


def test_main_bypass(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MCP_CONFIG_SOVEREIGNTY_BYPASS", "1")
    assert sovereignty.main() == 0


def test_main_writes_artifact(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    artifact = tmp_path / "mcp_config_sovereignty.json"
    monkeypatch.setattr(sovereignty, "ARTIFACT_PATH", artifact)
    monkeypatch.delenv("MCP_CONFIG_SOVEREIGNTY_BYPASS", raising=False)
    exit_code = sovereignty.main()
    assert exit_code == 0
    assert artifact.exists()
    payload = json.loads(artifact.read_text(encoding="utf-8"))
    assert payload["valid"] is True


def test_windsurf_launcher_path_required(tmp_path: Path) -> None:
    cfg = _minimal_config(
        _filesystem_block(
            launcher="${env:AGENTIC_REPO_ROOT}/.claude/governance/scripts/filesystem_mcp_launcher.js",
        )
    )
    path = tmp_path / "mcp.json"
    path.write_text(json.dumps(cfg), encoding="utf-8")
    violations = sovereignty.validate_profile("windsurf", path, ".claude/governance/scripts/filesystem_mcp_launcher.js")
    assert violations == []
