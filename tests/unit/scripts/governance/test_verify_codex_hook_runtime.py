"""Tests for Codex hook contract and runtime-registration verification."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "scripts" / "governance"))

import verify_codex_hook_runtime as mod  # noqa: E402


def _root(tmp_path: Path) -> Path:
    (tmp_path / ".codex").mkdir()
    (tmp_path / ".codex" / "config.toml").write_text("[features]\nhooks = true\n", encoding="utf-8")
    (tmp_path / ".codex" / "hooks.json").write_text(
        json.dumps(
            {
                "hooks": {
                    "PreToolUse": [
                        {
                            "matcher": "^Bash$",
                            "hooks": [{"type": "command", "command": "python hook.py"}],
                        }
                    ]
                }
            }
        ),
        encoding="utf-8",
    )
    return tmp_path


def test_repo_hook_contract_uses_supported_configuration() -> None:
    report = mod.validate_contract(REPO_ROOT)

    assert report["status"] == "PASS"
    assert len(report["registered_commands"]) == 22


def test_contract_rejects_deprecated_feature_alias(tmp_path: Path) -> None:
    root = _root(tmp_path)
    (root / ".codex" / "config.toml").write_text("[features]\ncodex_hooks = true\n", encoding="utf-8")

    report = mod.validate_contract(root)

    assert report["status"] == "FAIL"
    assert any("deprecated" in error for error in report["errors"])


def test_runtime_registration_requires_each_trusted_handler(tmp_path: Path) -> None:
    root = _root(tmp_path)
    runtime = tmp_path / "runtime.toml"
    runtime.write_text(
        'selected-avatar-id = "patch-fox"\n\n[features]\nhooks = true\n\n[hooks.state]\n'
        '"C:/repo/.codex/hooks.json:pre_tool_use:0:0" = "sha256:trusted"\n',
        encoding="utf-8",
    )

    report = mod.validate_runtime_registration(root, runtime)

    assert report["status"] == "PASS"


def test_runtime_registration_reports_missing_trust_state(tmp_path: Path) -> None:
    root = _root(tmp_path)
    runtime = tmp_path / "runtime.toml"
    runtime.write_text(
        'selected-avatar-id = "patch-fox"\n\n[features]\nhooks = true\n\n[hooks.state]\n',
        encoding="utf-8",
    )

    report = mod.validate_runtime_registration(root, runtime)

    assert report["status"] == "FAIL"
    assert any("runtime trust state missing" in error for error in report["errors"])


def test_runtime_registration_rejects_wrong_selected_avatar(tmp_path: Path) -> None:
    root = _root(tmp_path)
    runtime = tmp_path / "runtime.toml"
    runtime.write_text(
        'selected-avatar-id = "fireball"\n\n[features]\nhooks = true\n\n[hooks.state]\n'
        '"C:/repo/.codex/hooks.json:pre_tool_use:0:0" = "sha256:trusted"\n',
        encoding="utf-8",
    )

    report = mod.validate_runtime_registration(root, runtime)

    assert report["status"] == "FAIL"
    assert any("selected-avatar-id" in error for error in report["errors"])
