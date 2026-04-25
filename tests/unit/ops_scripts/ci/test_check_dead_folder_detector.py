"""Unit tests for D_dead_folder_detector gate.

Scope
    * _parent_dir normalisation (Windows back-slash → POSIX).
    * _is_init_module detection.
    * _skip_directory basename filter.
    * find_dead_folders logic:
        - all-dead folder above threshold flagged
        - mixed folder (some live) NOT flagged
        - folder with 1 non-init module NOT flagged (too small)
        - folder with an anchor match NOT flagged
        - folder basename in skip list NOT flagged
        - __init__.py presence ignored for the all-dead check
    * Gate integration: empty → no violations; live snapshot smoke.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from ops_scripts.ci.check_dead_folder_detector import (
    DeadFolderDetectorGate,
    _is_init_module,
    _parent_dir,
    _skip_directory,
    find_dead_folders,
)


# ---- pure helpers ------------------------------------------------


@pytest.mark.parametrize(
    "path,expected",
    [
        ("agentic_core/utils/dead.py", "agentic_core/utils"),
        (r"agentic_core\utils\dead.py", "agentic_core/utils"),
        ("", ""),
        ("root.py", "."),
    ],
)
def test_parent_dir_normalises(path: str, expected: str) -> None:
    assert _parent_dir(path) == expected


@pytest.mark.parametrize(
    "path,expected",
    [
        ("pkg/__init__.py", True),
        (r"pkg\__init__.py", True),
        ("pkg/not_init.py", False),
        ("", False),
    ],
)
def test_is_init_module(path: str, expected: bool) -> None:
    assert _is_init_module(path) == expected


@pytest.mark.parametrize(
    "dir_path,expected",
    [
        ("agentic_core/tests", True),
        ("apps_rg/__pycache__", True),
        ("agentic_core/L1_cognition/utils", False),
        ("", True),
    ],
)
def test_skip_directory(dir_path: str, expected: bool) -> None:
    assert _skip_directory(dir_path) == expected


# ---- find_dead_folders with synthetic in-memory ADG ----------------


def _make_adg(rows: list[tuple[int, str, str, str, str]]) -> sqlite3.Connection:
    """rows: (id, layer, entity_type, resolved_path, adg_name)."""
    conn = sqlite3.connect(":memory:")
    conn.executescript(
        """
        CREATE TABLE nodes (
            id INTEGER PRIMARY KEY,
            layer TEXT,
            entity_type TEXT,
            resolved_path TEXT,
            adg_name TEXT
        );
        CREATE TABLE edges (
            src_id INTEGER,
            dst_id INTEGER,
            relation_type TEXT
        );
        """
    )
    conn.executemany("INSERT INTO nodes VALUES (?,?,?,?,?)", rows)
    return conn


def test_all_dead_folder_is_flagged(monkeypatch: pytest.MonkeyPatch) -> None:
    conn = _make_adg(
        [
            # L0 seed (so find_archival_orphans has something to start from).
            (1, "L0", "module", "agentic_core/L0_routing/main.py", "main"),
            # A dead folder: 3 non-init modules in agentic_core/dead_utils,
            # none reachable from L0.
            (10, "L2", "module", "agentic_core/dead_utils/__init__.py", "x"),
            (11, "L2", "module", "agentic_core/dead_utils/a.py", "a"),
            (12, "L2", "module", "agentic_core/dead_utils/b.py", "b"),
            (13, "L2", "module", "agentic_core/dead_utils/c.py", "c"),
        ]
    )
    result = find_dead_folders(conn, anchor_patterns=[])
    folders = [f for f, _ in result]
    assert "agentic_core/dead_utils" in folders
    files = dict(result)["agentic_core/dead_utils"]
    # __init__.py must NOT be counted.
    assert all("__init__" not in f for f in files)
    assert len(files) == 3


def test_mixed_folder_with_live_module_not_flagged() -> None:
    conn = _make_adg(
        [
            (1, "L0", "module", "agentic_core/L0_routing/main.py", "main"),
            (10, "L2", "module", "pkg/live.py", "live"),
            (11, "L2", "module", "pkg/dead.py", "dead"),
        ]
    )
    # Mark pkg/live.py as imported from main → it becomes reachable.
    conn.execute("INSERT INTO edges VALUES (?,?,?)", (1, 10, "imports"))
    conn.commit()
    result = find_dead_folders(conn, anchor_patterns=[])
    assert not any(f == "pkg" for f, _ in result)


def test_small_folder_below_threshold_not_flagged() -> None:
    conn = _make_adg(
        [
            (1, "L0", "module", "agentic_core/L0_routing/main.py", "main"),
            (10, "L2", "module", "pkg_tiny/only.py", "only"),
        ]
    )
    result = find_dead_folders(conn, anchor_patterns=[])
    assert not any(f == "pkg_tiny" for f, _ in result)


def test_folder_with_anchor_match_not_flagged() -> None:
    conn = _make_adg(
        [
            (1, "L0", "module", "agentic_core/L0_routing/main.py", "main"),
            (10, "L2", "module", "pkg/plugin_entry.py", "plugin_entry"),
            (11, "L2", "module", "pkg/helper.py", "helper"),
        ]
    )
    # plugin_entry.py is pinned via a dynamic-dispatch anchor → whole
    # folder disqualified.
    result = find_dead_folders(conn, anchor_patterns=["*plugin_entry.py"])
    assert not any(f == "pkg" for f, _ in result)


def test_tests_folder_skipped_by_basename() -> None:
    conn = _make_adg(
        [
            (1, "L0", "module", "agentic_core/L0_routing/main.py", "main"),
            (10, "L2", "module", "agentic_core/tests/a.py", "a"),
            (11, "L2", "module", "agentic_core/tests/b.py", "b"),
        ]
    )
    result = find_dead_folders(conn, anchor_patterns=[])
    assert not any(f.endswith("/tests") for f, _ in result)


def test_non_production_layer_ignored() -> None:
    conn = _make_adg(
        [
            (1, "L0", "module", "agentic_core/L0_routing/main.py", "main"),
            (10, "L6", "module", "pkg_obs/a.py", "a"),
            (11, "L6", "module", "pkg_obs/b.py", "b"),
        ]
    )
    result = find_dead_folders(conn, anchor_patterns=[])
    assert not any(f == "pkg_obs" for f, _ in result)


def test_min_folder_size_override_respected() -> None:
    conn = _make_adg(
        [
            (1, "L0", "module", "agentic_core/L0_routing/main.py", "main"),
            (10, "L2", "module", "pkg_one/solo.py", "solo"),
        ]
    )
    result = find_dead_folders(conn, anchor_patterns=[], min_folder_size=1)
    assert any(f == "pkg_one" for f, _ in result)


# ---- violation shape --------------------------------------------


def test_violation_contains_dead_file_list(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Gate violation must carry the file list so reviewers can act on it."""
    conn = _make_adg(
        [
            (1, "L0", "module", "agentic_core/L0_routing/main.py", "main"),
            (10, "L2", "module", "pkg_dead/a.py", "a"),
            (11, "L2", "module", "pkg_dead/b.py", "b"),
        ]
    )
    gate = DeadFolderDetectorGate()
    violations = gate.run(conn)
    assert violations, "expected at least one violation"
    v = next((x for x in violations if x.subject == "pkg_dead"), None)
    assert v is not None
    assert v.gate_id == "D_dead_folder_detector"
    assert v.extra is not None
    assert v.extra["dead_file_count"] == 2
    assert set(v.extra["dead_files"]) == {"pkg_dead/a.py", "pkg_dead/b.py"}
    assert "archive the whole folder" in v.detail.lower()


# ---- CI wiring regression --------------------------------------


def test_gate_wired_into_run_contract_gates() -> None:
    """The gate MUST be registered in the wiring-CI gate plane so
    ``ops_scripts/ci/run_contract_gates.py`` executes it on every run."""
    from pathlib import Path as _Path

    repo_root = _Path(__file__).resolve().parents[4]
    src = (repo_root / "ops_scripts" / "ci" / "run_contract_gates.py").read_text(encoding="utf-8")
    assert "check_dead_folder_detector.py" in src, (
        "D_dead_folder_detector must remain wired into run_contract_gates.py::wiring_gates"
    )


# ---- live smoke against the real snapshot (if present) -----------


def test_smoke_against_live_snapshot() -> None:
    """If an ADG snapshot is present, the gate must complete without error."""
    from ops_scripts.ci._adg_wiring_gate_base import latest_snapshot

    try:
        snapshot = latest_snapshot()
    except FileNotFoundError:
        pytest.skip("no ADG snapshot on disk")
    with sqlite3.connect(f"file:{snapshot.as_posix()}?mode=ro", uri=True) as conn:
        result = find_dead_folders(conn, anchor_patterns=[])
    # Purely a smoke test — we don't assert count, but result must be a list
    # of tuples with shape (str, list[str]).
    assert isinstance(result, list)
    for folder, files in result:
        assert isinstance(folder, str)
        assert isinstance(files, list)
        assert all(isinstance(f, str) for f in files)
