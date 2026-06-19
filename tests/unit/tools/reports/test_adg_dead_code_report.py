import json
import sqlite3
from pathlib import Path

from tools.reports.adg_dead_code_report import emit_mandatory_adg_dead_code_report


def _sqlite(path: Path) -> None:
    with sqlite3.connect(path) as conn:
        conn.execute(
            "create table nodes(id int, layer text, domain text, confidence text, adg_name text, identity_kind text, entity_type text)"
        )
        rows = [
            (1, "L0", "core", "HIGH", "ADG::Module::stable_0", "module", "symbol"),
            (2, "L0", "core", "HIGH", "ADG::Module::stable_1", "module", "symbol"),
            (3, "L0", "core", "HIGH", "ADG::Module::stable_2", "module", "symbol"),
            (4, "L0", "core", "HIGH", "ADG::Module::stable_3", "module", "symbol"),
            (5, "L0", "core", "HIGH", "ADG::Module::stable_4", "module", "symbol"),
            (6, "L0", "core", "HIGH", "ADG::Module::stable_5", "module", "symbol"),
            (7, "L0", "core", "HIGH", "ADG::Module::stable_6", "module", "symbol"),
            (8, "L0", "core", "HIGH", "ADG::Module::stable_7", "module", "symbol"),
            (9, "L0", "core", "HIGH", "ADG::Module::stable_8", "module", "symbol"),
            (10, "L0", "core", "LOW", "ADG::Module::unstable_import", "unresolved_import", "symbol"),
        ]
        conn.executemany("insert into nodes values (?,?,?,?,?,?,?)", rows)
        conn.execute("create table edges(src_id int, dst_id int, relation_type text)")


def _add_dead_import_overlay(path: Path) -> None:
    with sqlite3.connect(path) as conn:
        conn.execute(
            """
            create table overlay_violations(
                id integer primary key,
                category text not null,
                severity text not null,
                file_path text not null,
                line_no integer,
                evidence text not null,
                violation_class text not null,
                disposition text not null
            )
            """
        )
        conn.executemany(
            """
            insert into overlay_violations(
                category, severity, file_path, line_no, evidence, violation_class, disposition
            ) values (?,?,?,?,?,?,?)
            """,
            [
                ("dead_import_resolved", "HIGH", "pkg/a.py", 10, "unused import x", "overlay_enrichment", "untriaged"),
                ("dead_import_resolved", "HIGH", "pkg/a.py", 11, "unused import y", "overlay_enrichment", "untriaged"),
                ("dead_import_resolved", "HIGH", "pkg/b.py", 5, "unused import z", "overlay_enrichment", "untriaged"),
                ("hidden_write_outside_uwg", "HIGH", "pkg/c.py", 1, "not dead code", "overlay_enrichment", "untriaged"),
            ],
        )
        conn.execute(
            """
            create view mv_dead_import_hotspots_overlay as
            select file_path as file, count(*) as dead_count
            from overlay_violations
            where category = 'dead_import_resolved'
            group by file_path
            order by dead_count desc
            """
        )


def test_emit_dead_code_report_writes_latest_copies(tmp_path: Path) -> None:
    artifacts = tmp_path / "artifacts" / "adg"
    artifacts.mkdir(parents=True)
    db = artifacts / "adg_indexed_20260618_120000.sqlite"
    _sqlite(db)
    docs = tmp_path / "docs_mirror"

    rc, out = emit_mandatory_adg_dead_code_report(
        adg_artifacts_dir=artifacts,
        ts="run",
        print_inline=False,
        fail_closed=False,
        docs_dir=docs,
    )

    assert rc == 0
    assert out == artifacts / "dead_code_zone_control_report_run.json"
    assert (artifacts / "dead_code_zone_control_report_latest.json").is_file()
    assert (docs / "dead_code_zone_control_report_latest.json").is_file()

    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["status"] == "PASS"
    assert data["source"]["adg_snapshot"].endswith("adg_indexed_20260618_120000.sqlite")
    assert data["source"]["adg_snapshot_ts"] == "20260618_120000"
    assert data["summary"]["adg_snapshot"].endswith("adg_indexed_20260618_120000.sqlite")
    assert data["summary"]["adg_snapshot_ts"] == "20260618_120000"
    assert data["summary"]["total_dead_code_candidates"] == 0
    assert data["summary"]["executive_ready"] is True
    assert data["dead_code_candidates"]["dead_code_hotspots"] == []


def test_emit_dead_code_report_inline_uses_bcg_brief(tmp_path: Path, capsys) -> None:
    artifacts = tmp_path / "artifacts" / "adg"
    artifacts.mkdir(parents=True)
    db = artifacts / "adg_indexed_20260618_120000.sqlite"
    _sqlite(db)

    rc, _ = emit_mandatory_adg_dead_code_report(
        adg_artifacts_dir=artifacts,
        ts="run",
        print_inline=True,
        fail_closed=False,
        docs_dir=tmp_path / "docs_mirror",
    )

    assert rc == 0
    captured = capsys.readouterr()
    assert "## ADG Dead Code Report" in captured.out
    assert "### BCG Deletion Brief" in captured.out
    assert "ADG source:" in captured.out
    assert "adg_indexed_20260618_120000.sqlite" in captured.out
    assert "(snapshot 20260618_120000)" in captured.out
    assert "Maintain SVP engineer-level repo standards" in captured.out


def test_emit_dead_code_report_uses_completed_overlay_dead_imports(tmp_path: Path, capsys) -> None:
    artifacts = tmp_path / "artifacts" / "adg"
    artifacts.mkdir(parents=True)
    db = artifacts / "adg_indexed_20260618_120000.sqlite"
    _sqlite(db)
    _add_dead_import_overlay(db)

    rc, out = emit_mandatory_adg_dead_code_report(
        adg_artifacts_dir=artifacts,
        ts="run",
        print_inline=True,
        fail_closed=False,
        docs_dir=tmp_path / "docs_mirror",
    )

    assert rc == 0
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["summary"]["total_dead_imports"] == 3
    assert data["summary"]["adg_snapshot"].endswith("adg_indexed_20260618_120000.sqlite")
    assert data["summary"]["adg_snapshot_ts"] == "20260618_120000"
    assert data["dead_imports"]["source_counts"]["overlay_dead_import_resolved"] == 3
    assert data["dead_imports"]["dead_import_hotspots"][0] == ["pkg/a.py", 2]

    captured = capsys.readouterr()
    assert "ADG source:" in captured.out
    assert "adg_indexed_20260618_120000.sqlite" in captured.out
    assert "(snapshot 20260618_120000)" in captured.out
    assert "Remove confirmed dead imports" in captured.out
    assert "3 resolved dead-import overlay row(s)" not in captured.out
    assert "2 resolved dead-import overlay row(s) point at this file." in captured.out


def test_emit_dead_code_report_prefers_valid_snapshot_over_newer_placeholder(tmp_path: Path) -> None:
    artifacts = tmp_path / "artifacts" / "adg"
    artifacts.mkdir(parents=True)
    valid = artifacts / "adg_indexed_20260618_120000.sqlite"
    _sqlite(valid)
    placeholder = artifacts / "adg_indexed_20260619_120000.sqlite"
    placeholder.write_text("not a sqlite database", encoding="utf-8")

    rc, out = emit_mandatory_adg_dead_code_report(
        adg_artifacts_dir=artifacts,
        ts="run",
        print_inline=False,
        fail_closed=False,
        docs_dir=tmp_path / "docs_mirror",
    )

    assert rc == 0
    assert out == artifacts / "dead_code_zone_control_report_run.json"
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["summary"]["total_dead_code_candidates"] == 0
    assert data["summary"]["executive_ready"] is True


def test_emit_dead_code_report_without_ts_does_not_self_copy_latest(tmp_path: Path) -> None:
    artifacts = tmp_path / "artifacts" / "adg"
    artifacts.mkdir(parents=True)
    db = artifacts / "adg_indexed_20260618_120000.sqlite"
    _sqlite(db)

    rc, out = emit_mandatory_adg_dead_code_report(
        adg_artifacts_dir=artifacts,
        print_inline=False,
        fail_closed=True,
        docs_dir=tmp_path / "docs_mirror",
    )

    assert rc == 0
    assert out == artifacts / "dead_code_zone_control_report_latest.json"
    assert out.is_file()
