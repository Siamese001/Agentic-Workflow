"""Tests for scripts/governance/verify_codex_primary.py."""

from __future__ import annotations

import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "scripts" / "governance"))

import verify_codex_primary as mod  # noqa: E402


def _write(path: Path, text: str = "placeholder") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _valid_root(tmp_path: Path) -> Path:
    for relative in mod.REQUIRED_FILES:
        _write(tmp_path / relative)
    _write(
        tmp_path / "AGENTS.md",
        "\n".join(
            [
                "## Codex primary execution adapter",
                "docs/codex-primary-execution.md",
                "scripts/governance/codex_readiness.py",
                "scripts/governance/verify_codex_run_receipt.py",
                "scripts/governance/verify_codex_primary.py",
            ]
        ),
    )
    _write(
        tmp_path / "docs/codex-primary-execution.md",
        "\n".join(
            [
                "Codex primary execution surface",
                "scripts/governance/codex_readiness.py",
                "scripts/governance/verify_codex_run_receipt.py",
                "scripts/governance/verify_codex_primary.py",
                "docs/reports/codex/codex_primary_mcp_live_snapshot.md",
                "No parallel registry",
            ]
        ),
    )
    _write(
        tmp_path / "docs/codex-backup-adapter.md",
        "\n".join(
            [
                "docs/codex-primary-execution.md",
                "scripts/governance/verify_codex_primary.py",
                "scripts/governance/codex_readiness.py",
                "scripts/governance/verify_codex_run_receipt.py",
            ]
        ),
    )
    _write(
        tmp_path / "docs/reports/codex/codex_primary_mcp_live_snapshot.json",
        json.dumps(
            {
                "schema_version": "codex-primary-mcp-snapshot/v1",
                "routes": [
                    {
                        "server_id": "memory",
                        "codex_status": "callable",
                        "evidence": "live call",
                        "run_policy": "use memory",
                    }
                ],
            }
        ),
    )
    return tmp_path


def test_valid_primary_contract_passes(tmp_path: Path) -> None:
    assert mod.validate(_valid_root(tmp_path)) == []


def test_missing_anchor_fails(tmp_path: Path) -> None:
    root = _valid_root(tmp_path)
    (root / "AGENTS.md").write_text("## Codex primary execution adapter\n", encoding="utf-8")

    failures = mod.validate(root)

    assert any("missing anchor" in failure for failure in failures)
