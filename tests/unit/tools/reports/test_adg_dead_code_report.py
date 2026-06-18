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
    assert "Maintain SVP engineer-level repo standards" in captured.out
