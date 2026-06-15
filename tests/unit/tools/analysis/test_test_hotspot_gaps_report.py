from __future__ import annotations

import sqlite3

from tools.analysis import test_hotspot_gaps_report as report


def _fixture_conn() -> sqlite3.Connection:
    con = sqlite3.connect(":memory:")
    con.executescript(
        """
        CREATE TABLE nodes (
            id INTEGER PRIMARY KEY,
            resolved_path TEXT
        );
        CREATE TABLE edges (
            src_id INTEGER,
            dst_id INTEGER,
            relation_type TEXT,
            source_file TEXT
        );
        CREATE TABLE mv_hotspot_centrality (
            resolved_path TEXT,
            fan_in INTEGER,
            fan_out INTEGER,
            degree INTEGER,
            degree_centrality REAL
        );
        CREATE TABLE coverage_by_path (
            resolved_path TEXT
        );
        """
    )
    con.executemany(
        "INSERT INTO nodes(id, resolved_path) VALUES (?, ?)",
        [
            (1, "tests/unit/apps_rg/test_provider_gateway.py"),
            (2, "apps_rg/runtime/providers/provider_gateway.py"),
            (3, "apps_rg/runtime/sections/untested_lane.py"),
            (4, "tests/unit/apps_lic/test_gateway.py"),
            (5, "apps_lic/runtime/gateway.py"),
        ],
    )
    con.executemany(
        """
        INSERT INTO edges(src_id, dst_id, relation_type, source_file)
        VALUES (?, ?, ?, ?)
        """,
        [
            (
                1,
                2,
                "covers",
                "tests/unit/apps_rg/test_provider_gateway.py",
            ),
            (
                4,
                5,
                "covers",
                "tests/unit/apps_lic/test_gateway.py",
            ),
        ],
    )
    con.executemany(
        """
        INSERT INTO mv_hotspot_centrality(
            resolved_path, fan_in, fan_out, degree, degree_centrality
        ) VALUES (?, ?, ?, ?, ?)
        """,
        [
            ("apps_rg/runtime/providers/provider_gateway.py", 17, 11, 28, 0.0014),
            ("apps_rg/runtime/sections/untested_lane.py", 10, 1, 11, 0.0010),
            ("apps_lic/runtime/gateway.py", 5, 3, 8, 0.0008),
        ],
    )
    con.execute("INSERT INTO coverage_by_path(resolved_path) VALUES (?)", ("apps_lic/runtime/gateway.py",))
    return con


def test_apps_adg_reachability_uses_covers_edges_not_coverage_by_path() -> None:
    con = _fixture_conn()

    rows = {
        row["app"]: row
        for row in report._apps_adg_test_reachability(con)
    }

    assert rows["apps_rg"]["adg_source_paths"] == 2
    assert rows["apps_rg"]["hotspot_paths"] == 2
    assert rows["apps_rg"]["covered_paths"] == 1
    assert rows["apps_rg"]["covering_tests"] == 1
    assert rows["apps_rg"]["covers_edges"] == 1
    assert rows["apps_rg"]["coverage_by_path_rows"] == 0
    assert rows["apps_rg"]["hotspot_paths_without_covers"] == 1

    assert rows["apps_lic"]["coverage_by_path_rows"] == 1
    assert rows["apps_lic"]["covered_paths"] == 1


def test_top_uncovered_app_hotspots_excludes_paths_with_covers_edges() -> None:
    con = _fixture_conn()

    rows = report._top_uncovered_app_hotspots(con)

    assert rows == [
        {
            "app": "apps_rg",
            "path": "apps_rg/runtime/sections/untested_lane.py",
            "fan_in": 10,
            "fan_out": 1,
            "degree": 11,
            "degree_centrality": 0.001,
        }
    ]
