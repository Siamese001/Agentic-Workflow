from __future__ import annotations

from pathlib import Path

from ops_scripts.ci import check_no_archives_imports as gate


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_detects_from_archives_import(tmp_path: Path) -> None:
    _write(tmp_path / "agentic_core" / "bad.py", "from archives.legacy import foo\n")

    hits = gate._archive_import_hits(tmp_path)

    assert any("agentic_core/bad.py" in h for h in hits)


def test_detects_ops_scripts_archives_import_with_alias(tmp_path: Path) -> None:
    _write(tmp_path / "apps_foo" / "x.py", "import ops_scripts.archives.helper as h\n")

    hits = gate._archive_import_hits(tmp_path)

    assert any("apps_foo/x.py" in h for h in hits)


def test_detects_tools_archive_import(tmp_path: Path) -> None:
    _write(tmp_path / "agentic_core" / "y.py", "from tools.archive import legacy_thing\n")

    hits = gate._archive_import_hits(tmp_path)

    assert any("agentic_core/y.py" in h for h in hits)


def test_ignores_commented_import(tmp_path: Path) -> None:
    _write(tmp_path / "agentic_core" / "ok.py", "# from archives.legacy import foo\n")

    assert gate._archive_import_hits(tmp_path) == []


def test_ignores_lookalike_segment(tmp_path: Path) -> None:
    # 'archival_gatekeeper' contains 'archiv' but is NOT an 'archive'/'archives' segment.
    _write(
        tmp_path / "agentic_core" / "real.py",
        "from agentic_core.L5_safety.enforcement.archival_gatekeeper_gate import run\n",
    )

    assert gate._archive_import_hits(tmp_path) == []


def test_ignores_files_inside_archive_dirs(tmp_path: Path) -> None:
    # Archived code is allowed to import archived code.
    _write(tmp_path / "apps_foo" / "archives" / "old.py", "from archives.legacy import foo\n")

    assert gate._archive_import_hits(tmp_path) == []


def test_ignores_test_files(tmp_path: Path) -> None:
    _write(tmp_path / "agentic_core" / "test_smoke.py", "from archives.legacy import foo\n")

    assert gate._archive_import_hits(tmp_path) == []
