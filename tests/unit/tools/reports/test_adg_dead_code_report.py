import json
import sqlite3
from pathlib import Path

from tools.reports.adg_dead_code_report import emit_mandatory_adg_dead_code_report


def _sqlite(path: Path) -> None:
    with sqlite3.connect(path) as conn:
        conn.execute(
            """
            create table nodes(
                id int,
                layer text,
                domain text,
                confidence text,
                adg_name text,
                identity_kind text,
                entity_type text,
                resolved_path text
            )
            """
        )
        rows = [
            (1, "L0", "core", "HIGH", "ADG::Module::stable_0", "module", "module", "pkg/stable_0.py"),
            (2, "L0", "core", "HIGH", "ADG::Module::stable_1", "module", "module", "pkg/stable_1.py"),
            (3, "L0", "core", "HIGH", "ADG::Module::stable_2", "module", "module", "pkg/stable_2.py"),
            (4, "L0", "core", "HIGH", "ADG::Module::stable_3", "module", "module", "pkg/stable_3.py"),
            (5, "L0", "core", "HIGH", "ADG::Module::stable_4", "module", "module", "pkg/stable_4.py"),
            (6, "L0", "core", "HIGH", "ADG::Module::stable_5", "module", "module", "pkg/stable_5.py"),
            (7, "L0", "core", "HIGH", "ADG::Module::stable_6", "module", "module", "pkg/stable_6.py"),
            (8, "L0", "core", "HIGH", "ADG::Module::stable_7", "module", "module", "pkg/stable_7.py"),
            (9, "L0", "core", "HIGH", "ADG::Module::stable_8", "module", "module", "pkg/stable_8.py"),
            (10, "L0", "core", "LOW", "ADG::Module::unstable_import", "unresolved_import", "symbol", "pkg/unstable_import.py"),
        ]
        conn.executemany("insert into nodes values (?,?,?,?,?,?,?,?)", rows)
        conn.execute("create table edges(src_id int, dst_id int, relation_type text)")
        conn.execute(
            """
            create table overlay_violations(
                id integer primary key autoincrement,
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
            "insert into overlay_violations(category, severity, file_path, line_no, evidence, violation_class, disposition) values (?,?,?,?,?,?,?)",
            [
                ("dead_import_resolved", "MEDIUM", "pkg/stable_0.py", 1, "unused import", "overlay_enrichment", "untriaged"),
                ("dead_import_resolved", "MEDIUM", "pkg/stable_0.py", 2, "unused import", "overlay_enrichment", "untriaged"),
                ("dead_import_resolved", "MEDIUM", "pkg/stable_0.py", 3, "unused import", "overlay_enrichment", "untriaged"),
                ("dead_import_resolved", "MEDIUM", "pkg/stable_1.py", 4, "unused import", "overlay_enrichment", "untriaged"),
            ],
        )
        conn.execute(
            """
            create view mv_dead_import_hotspots_overlay as
            select file_path as file, count(*) as dead_count
            from overlay_violations
            where category = 'dead_import_resolved'
            group by file_path
            order by dead_count desc, file_path asc
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
    assert data["summary"]["total_dead_code_candidates"] == 4
    assert data["summary"]["total_dead_imports"] == 4
    assert data["summary"]["executive_ready"] is True
    assert data["dead_imports"]["dead_import_hotspots"][0] == ["pkg/stable_0.py", 3]
    assert data["dead_code_candidates"]["dead_code_hotspots"][0] == ["pkg/stable_0.py", 3]


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
    assert "DELETION_CANDIDATES" in captured.out
    assert "Maintain SVP engineer-level repo standards" in captured.out
