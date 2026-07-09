from __future__ import annotations

import logging
from pathlib import Path

from ops_scripts.ci import check_no_legacy_ide_refs as gate


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    logging.info("C3 write receipt: no-legacy IDE fixture written")


def test_detects_python_path_join(tmp_path: Path) -> None:
    _write(tmp_path / "agentic_core" / "bad.py", 'target = root / ".cursor" / "mcp.json"\n')

    hits = gate._active_path_uses(tmp_path)

    assert any("agentic_core/bad.py" in hit for hit in hits)


def test_detects_windows_cursor_literal(tmp_path: Path) -> None:
    _write(tmp_path / "tools" / "bad.py", 'target = ".cursor\\\\mcp.json"\n')

    hits = gate._active_path_uses(tmp_path)

    assert any("tools/bad.py" in hit for hit in hits)


def test_detects_powershell_join_path(tmp_path: Path) -> None:
    _write(tmp_path / "tools" / "setup" / "bad.ps1", 'Join-Path $repoRoot ".cursor\\mcp.json"\n')

    hits = gate._active_path_uses(tmp_path)

    assert any("tools/setup/bad.ps1" in hit for hit in hits)


def test_detects_workflow_path_filter(tmp_path: Path) -> None:
    _write(tmp_path / ".github" / "workflows" / "bad.yml", 'paths:\n  - ".cursor/schemas/x.json"\n')

    hits = gate._active_path_uses(tmp_path)

    assert any(".github/workflows/bad.yml" in hit for hit in hits)


def test_ignores_comments_and_path_home_cursor(tmp_path: Path) -> None:
    _write(
        tmp_path / "tools" / "ok.py",
        '# target = root / ".cursor" / "mcp.json"\ncanvas = Path.home() / ".cursor" / "projects"\n',
    )

    assert gate._active_path_uses(tmp_path) == []


def test_ignores_migration_tooling(tmp_path: Path) -> None:
    _write(tmp_path / "tools" / "migration" / "sweep.py", 'target = ".cursor/schemas"\n')

    assert gate._active_path_uses(tmp_path) == []
