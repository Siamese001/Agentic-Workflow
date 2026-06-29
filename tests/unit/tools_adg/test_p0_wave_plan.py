from __future__ import annotations

import sqlite3
from pathlib import Path

from tools.adg.core import p0_wave_plan


def _write_source(root: Path, rel_path: str) -> None:
    path = root / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("# test fixture\n", encoding="utf-8")


def _make_reachability_sqlite(path: Path, *, include_orphan: bool) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(path)
    try:
        con.execute(
            """
            CREATE TABLE nodes (
                id INTEGER PRIMARY KEY,
                layer TEXT,
                entity_type TEXT,
                resolved_path TEXT,
                file_path TEXT,
                adg_name TEXT
            )
            """
        )
        con.execute(
            """
            CREATE TABLE edges (
                id INTEGER PRIMARY KEY,
                src_id INTEGER,
                dst_id INTEGER,
                relation_type TEXT,
                source_file TEXT,
                line_no INTEGER
            )
            """
        )
        con.executemany(
            "INSERT INTO nodes VALUES (?, ?, ?, ?, ?, ?)",
            [
                (
                    1,
                    "L0",
                    "module",
                    "agentic_core/L0_routing/entry.py",
                    "agentic_core/L0_routing/entry.py",
                    "ADG::Module::agentic_core/L0_routing/entry.py",
                ),
                (
                    2,
                    "L3",
                    "module",
                    "agentic_core/L3_orchestration/reachable.py",
                    "agentic_core/L3_orchestration/reachable.py",
                    "ADG::Module::agentic_core/L3_orchestration/reachable.py",
                ),
                (
                    3,
                    "L3",
                    "module",
                    "agentic_core/L3_orchestration/orphan.py",
                    "agentic_core/L3_orchestration/orphan.py",
                    "ADG::Module::agentic_core/L3_orchestration/orphan.py",
                ),
            ],
        )
        imports = [(1, 1, 2, "imports", "agentic_core/L0_routing/entry.py", 1)]
        if not include_orphan:
            imports.append((2, 2, 3, "imports", "agentic_core/L3_orchestration/reachable.py", 2))
        con.executemany("INSERT INTO edges VALUES (?, ?, ?, ?, ?, ?)", imports)
        con.commit()
    finally:
        con.close()
    return path


def test_p0_wave_plan_includes_l0_reachability_orphans(tmp_path, monkeypatch):
    monkeypatch.setattr(p0_wave_plan, "_REPO_ROOT", tmp_path)
    _write_source(tmp_path, "agentic_core/L0_routing/entry.py")
    _write_source(tmp_path, "agentic_core/L3_orchestration/reachable.py")
    _write_source(tmp_path, "agentic_core/L3_orchestration/orphan.py")
    sqlite_path = _make_reachability_sqlite(tmp_path / "adg.sqlite", include_orphan=True)

    plan = p0_wave_plan.build_p0_remediation_wave_plan(sqlite_path)

    assert plan["plan_required"] is True
    assert plan["summary"]["total_p0_issues"] == 1
    assert plan["summary"]["l0_reachability_orphans"] == 1
    reachability_wave = next(
        wave for wave in plan["waves"] if wave["wave_id"] == "wave_1_l0_reachability_ratchet"
    )
    assert reachability_wave["item_count"] == 1
    assert reachability_wave["items"][0]["gate_id"] == "G_REACH_l0_reachability"
    assert reachability_wave["items"][0]["source_file"] == "agentic_core/L3_orchestration/orphan.py"


def test_p0_wave_plan_stays_clean_when_modules_are_l0_reachable(tmp_path, monkeypatch):
    monkeypatch.setattr(p0_wave_plan, "_REPO_ROOT", tmp_path)
    _write_source(tmp_path, "agentic_core/L0_routing/entry.py")
    _write_source(tmp_path, "agentic_core/L3_orchestration/reachable.py")
    _write_source(tmp_path, "agentic_core/L3_orchestration/orphan.py")
    sqlite_path = _make_reachability_sqlite(tmp_path / "adg.sqlite", include_orphan=False)

    plan = p0_wave_plan.build_p0_remediation_wave_plan(sqlite_path)

    assert plan["plan_required"] is False
    assert plan["summary"]["total_p0_issues"] == 0
    assert plan["summary"]["l0_reachability_orphans"] == 0


def test_p0_wave_plan_accepts_nodes_without_file_path_column(tmp_path, monkeypatch):
    monkeypatch.setattr(p0_wave_plan, "_REPO_ROOT", tmp_path)
    _write_source(tmp_path, "agentic_core/L0_routing/entry.py")
    _write_source(tmp_path, "agentic_core/L3_orchestration/orphan.py")
    sqlite_path = tmp_path / "adg_no_file_path.sqlite"
    con = sqlite3.connect(sqlite_path)
    try:
        con.execute(
            """
            CREATE TABLE nodes (
                id INTEGER PRIMARY KEY,
                layer TEXT,
                entity_type TEXT,
                resolved_path TEXT,
                adg_name TEXT
            )
            """
        )
        con.execute(
            """
            CREATE TABLE edges (
                id INTEGER PRIMARY KEY,
                src_id INTEGER,
                dst_id INTEGER,
                relation_type TEXT,
                source_file TEXT,
                line_no INTEGER
            )
            """
        )
        con.executemany(
            "INSERT INTO nodes VALUES (?, ?, ?, ?, ?)",
            [
                (1, "L0", "module", "agentic_core/L0_routing/entry.py", "ADG::Module::entry"),
                (2, "L3", "module", "agentic_core/L3_orchestration/orphan.py", "ADG::Module::orphan"),
            ],
        )
        con.commit()
    finally:
        con.close()

    plan = p0_wave_plan.build_p0_remediation_wave_plan(sqlite_path)

    assert plan["plan_required"] is True
    assert plan["summary"]["l0_reachability_orphans"] == 1
    reachability_wave = next(
        wave for wave in plan["waves"] if wave["wave_id"] == "wave_1_l0_reachability_ratchet"
    )
    assert reachability_wave["items"][0]["source_file"] == "agentic_core/L3_orchestration/orphan.py"
