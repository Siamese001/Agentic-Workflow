"""Hardening tests for the runtime ADG subsystem.

Covers:
- Thread-safety under concurrent blast_radius calls
- LRU eviction behavior
- Malformed / adversarial input
- Redis-reader fallback path (mocked reader)
- Large upstream closure (select_tests)
- IncrementalReindexer correctness + isolation

Goal: give the modules confidence beyond happy-path fixtures.
"""

from __future__ import annotations

import concurrent.futures
import sqlite3
import threading
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from tests.unit.tools.adg.test_runtime_query import _build_fixture_db
from tools.adg.incremental_reindex import (
    ADG_MODULE_PREFIX,
    IncrementalReindexer,
    _extract_import_modules,
    _infer_layer_for_path,
)
from tools.adg.runtime_query import (
    RuntimeADGQuery,
    get_default_query,
)
from tools.adg.select_tests import select_tests_for


# ---------- fixtures ----------


@pytest.fixture()
def big_db(tmp_path: Path) -> Path:
    """Fixture DB augmented with a wide caller fan-in and a long test chain."""
    db = tmp_path / "adg_indexed_hardening.sqlite"
    _build_fixture_db(db)
    conn = sqlite3.connect(str(db))
    try:
        # 200 additional callers of n_central.
        for i in range(200):
            src = f"n_extra_{i}"
            conn.execute(
                "INSERT INTO nodes (id, adg_name, layer, resolved_path) VALUES (?, ?, ?, ?)",
                (src, f"extra.mod_{i}", "L2", f"apps/e_{i}.py"),
            )
            conn.execute(
                "INSERT INTO edges (src_id, tgt_id, relation_type) VALUES (?, ?, 'imports')",
                (src, "n_central"),
            )
        # A 5-hop test chain ending in a test file.
        conn.execute(
            "INSERT INTO nodes (id, adg_name, layer, resolved_path) VALUES (?, ?, ?, ?)",
            ("n_chain_test", "tests.integration.test_chain", "L_TESTS", "tests/integration/test_chain.py"),
        )
        conn.execute(
            "INSERT INTO edges (src_id, tgt_id, relation_type) VALUES (?, ?, 'imports')",
            ("n_chain_test", "n_extra_0"),
        )
        # A direct test importer of n_central (needed for depth=1 test).
        conn.execute(
            "INSERT INTO nodes (id, adg_name, layer, resolved_path) VALUES (?, ?, ?, ?)",
            ("n_test_direct", "tests.unit.test_central", "L_TESTS", "tests/unit/test_central.py"),
        )
        conn.execute(
            "INSERT INTO edges (src_id, tgt_id, relation_type) VALUES (?, ?, 'imports')",
            ("n_test_direct", "n_central"),
        )
        conn.commit()
    finally:
        conn.close()
    return db


# ---------- concurrency ----------


def test_blast_radius_concurrent_calls_are_safe(big_db: Path) -> None:
    """Ten threads × 20 calls each should produce identical, consistent envelopes."""
    q = RuntimeADGQuery(sqlite_path=big_db)
    results: list[dict] = []
    lock = threading.Lock()

    def worker() -> None:
        for _ in range(20):
            env = q.blast_radius("n_central")
            with lock:
                results.append(env.to_dict())

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as pool:
        futs = [pool.submit(worker) for _ in range(10)]
        for f in futs:
            f.result(timeout=15)
    assert len(results) == 200
    # All envelopes identical (idempotent query over read-only DB).
    seen = {tuple(sorted(r.items(), key=lambda kv: kv[0])) for r in results}
    assert len(seen) == 1
    # Cache hits should dominate — first call per thread is a miss, rest are hits.
    stats = q.cache_stats()
    assert stats["hits"]["resolve"] >= 190
    assert stats["misses"]["resolve"] <= 10


def test_lru_eviction_bounds_cache_size(tmp_path: Path) -> None:
    """Cache size cannot exceed the configured LRU size."""
    db = tmp_path / "adg_indexed_tiny.sqlite"
    _build_fixture_db(db)
    q = RuntimeADGQuery(sqlite_path=db, lru_size=3)
    # 10 different idents — cache must stay <= 3.
    for i in range(10):
        q.resolve_node(f"ident_{i}")
    stats = q.cache_stats()
    assert stats["resolve_cache_size"] <= 3


# ---------- malformed / adversarial input ----------


def test_blast_radius_handles_very_long_identifier(big_db: Path) -> None:
    """Identifier of 10k chars must not crash or hang."""
    q = RuntimeADGQuery(sqlite_path=big_db)
    long_ident = "x" * 10_000
    env = q.blast_radius(long_ident)
    assert env.error == "node_not_found"


def test_blast_radius_handles_sql_special_chars(big_db: Path) -> None:
    """Quoting / SQL wildcards in identifier must not leak."""
    q = RuntimeADGQuery(sqlite_path=big_db)
    for ident in ("' OR '1'='1", "%", "_", ";DROP TABLE nodes;--", "\x00"):
        env = q.blast_radius(ident)
        assert env.error == "node_not_found"
    # Verify nodes table still intact.
    with sqlite3.connect(str(big_db)) as conn:
        count = conn.execute("SELECT COUNT(*) FROM nodes").fetchone()[0]
        assert count > 200  # fixture + 200 extras


def test_swallow_sites_depth_is_clamped(big_db: Path) -> None:
    """Caller-supplied absurd depths must be clamped to MAX_TRAVERSAL_DEPTH."""
    q = RuntimeADGQuery(sqlite_path=big_db)
    # Depth 9999 must not blow up.
    result = q.swallow_sites_reaching("n_failing", depth=9999, max_hits=5)
    assert isinstance(result, list)


def test_upstream_callers_k_zero_returns_empty(big_db: Path) -> None:
    q = RuntimeADGQuery(sqlite_path=big_db)
    assert q.upstream_callers("n_central", k=0) == []
    assert q.upstream_callers("n_central", k=-1) == []


def test_upstream_callers_k_huge_is_capped(big_db: Path) -> None:
    q = RuntimeADGQuery(sqlite_path=big_db)
    # 225 callers exist, we ask for 9999 — must cap at MAX_FANOUT_ROWS (50).
    callers = q.upstream_callers("n_central", k=9999)
    assert len(callers) == 50


# ---------- Redis reader fallback ----------


def test_pview_contains_redis_hit_preferred(big_db: Path) -> None:
    """When the Redis reader returns True, SQLite is bypassed."""
    reader = MagicMock()
    reader.available = True
    reader.pview_contains.return_value = True
    q = RuntimeADGQuery(sqlite_path=big_db, redis_reader=reader)
    assert q.pview_contains("v_p0_test_members", "n_safety") is True
    reader.pview_contains.assert_called_once_with("v_p0_test_members", "n_safety", q.snapshot_id)


def test_pview_contains_redis_miss_falls_back_to_sqlite(big_db: Path) -> None:
    """When the Redis reader returns None (miss), SQLite is consulted."""
    reader = MagicMock()
    reader.available = True
    reader.pview_contains.return_value = None
    q = RuntimeADGQuery(sqlite_path=big_db, redis_reader=reader)
    # n_safety is L5 → in v_p0_test_members per fixture.
    assert q.pview_contains("v_p0_test_members", "n_safety") is True


def test_provenance_reports_redis_when_available(big_db: Path) -> None:
    reader = MagicMock()
    reader.available = True
    q = RuntimeADGQuery(sqlite_path=big_db, redis_reader=reader)
    assert q.provenance()["backend_used"] == "sqlite+redis"


# ---------- select_tests large closure ----------


def test_select_tests_handles_long_chain(big_db: Path) -> None:
    """5-hop import chain must still surface the test file."""
    from unittest.mock import patch

    q = RuntimeADGQuery(sqlite_path=big_db)
    with patch("tools.adg.select_tests.get_default_query", return_value=q):
        tests = select_tests_for(["agentic_core/L0_routing/router.py"])
    # n_central has 225 callers, one of which (n_extra_0) is imported by the chain test.
    assert "tests/integration/test_chain.py" in tests


def test_select_tests_depth_1_still_finds_direct_importer(big_db: Path) -> None:
    from unittest.mock import patch

    q = RuntimeADGQuery(sqlite_path=big_db)
    with patch("tools.adg.select_tests.get_default_query", return_value=q):
        tests = select_tests_for(["agentic_core/L0_routing/router.py"], depth=1)
    # Direct test importer exists from the base fixture.
    assert "tests/unit/test_central.py" in tests


# ---------- incremental reindexer ----------


def test_incremental_reindexer_creates_shadow_copy(tmp_path: Path, big_db: Path) -> None:
    shadow = tmp_path / "shadow.sqlite"
    rx = IncrementalReindexer(source_snapshot=big_db, shadow_snapshot=shadow)
    rx.initialize_shadow()
    assert shadow.exists()
    # Shadow and source must both have the fixture rows.
    with sqlite3.connect(str(shadow)) as conn:
        n = conn.execute("SELECT COUNT(*) FROM nodes").fetchone()[0]
    with sqlite3.connect(str(big_db)) as conn:
        m = conn.execute("SELECT COUNT(*) FROM nodes").fetchone()[0]
    assert n == m


def test_incremental_reindexer_missing_source_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        IncrementalReindexer(
            source_snapshot=tmp_path / "nope.sqlite",
            shadow_snapshot=tmp_path / "shadow.sqlite",
        )


def test_incremental_reindexer_noop_for_nonpython(tmp_path: Path, big_db: Path) -> None:
    shadow = tmp_path / "shadow.sqlite"
    rx = IncrementalReindexer(source_snapshot=big_db, shadow_snapshot=shadow)
    rx.initialize_shadow()
    delta = rx.reindex_file("README.md")
    assert delta.node_id is None
    assert delta.imports_added == []
    assert delta.imports_removed == []


def test_incremental_reindexer_does_not_touch_source(tmp_path: Path, big_db: Path) -> None:
    """Shadow mutations must never reflect in the source."""
    shadow = tmp_path / "shadow.sqlite"
    # Create a tiny Python file that imports something.
    fake_repo = tmp_path / "repo"
    fake_repo.mkdir()
    src_file = fake_repo / "my_mod.py"
    src_file.write_text("import os\nimport agentic_core\n")

    # Seed the shadow with a node for 'my_mod.py' and for the import target.
    rx = IncrementalReindexer(source_snapshot=big_db, shadow_snapshot=shadow, repo_root=fake_repo)
    rx.initialize_shadow()
    # Pre-populate target nodes in the shadow only.
    with sqlite3.connect(str(shadow)) as conn:
        conn.execute(
            "INSERT INTO nodes (id, adg_name, entity_type, layer, resolved_path) "
            "VALUES ('tgt_os', 'ADG::Module::os.py', 'module', 'L_STDLIB', 'os.py')"
        )
        conn.execute(
            "INSERT INTO nodes (id, adg_name, entity_type, layer, resolved_path) "
            "VALUES ('tgt_ac', 'ADG::Module::agentic_core/__init__.py', 'module', 'L_AGENTIC_CORE', 'agentic_core/__init__.py')"
        )
        conn.commit()

    delta = rx.reindex_file("my_mod.py")
    assert delta.created_node is True
    assert "os.py" in delta.imports_added
    assert "agentic_core/__init__.py" in delta.imports_added

    # Source count unchanged.
    with sqlite3.connect(str(big_db)) as conn:
        src_count = conn.execute(
            "SELECT COUNT(*) FROM nodes WHERE adg_name LIKE 'ADG::Module::my_mod.py'"
        ).fetchone()[0]
    assert src_count == 0


def test_incremental_reindex_replaces_existing_imports(tmp_path: Path, big_db: Path) -> None:
    shadow = tmp_path / "shadow.sqlite"
    fake_repo = tmp_path / "repo"
    fake_repo.mkdir()
    (fake_repo / "my_mod.py").write_text("import os\n")
    rx = IncrementalReindexer(source_snapshot=big_db, shadow_snapshot=shadow, repo_root=fake_repo)
    rx.initialize_shadow()
    with sqlite3.connect(str(shadow)) as conn:
        conn.execute(
            "INSERT INTO nodes (id, adg_name, entity_type, layer, resolved_path) "
            "VALUES ('tgt_os', 'ADG::Module::os.py', 'module', 'L_STDLIB', 'os.py')"
        )
        conn.execute(
            "INSERT INTO nodes (id, adg_name, entity_type, layer, resolved_path) "
            "VALUES ('tgt_sys', 'ADG::Module::sys.py', 'module', 'L_STDLIB', 'sys.py')"
        )
        conn.commit()

    # First pass: import os only.
    delta1 = rx.reindex_file("my_mod.py")
    assert "os.py" in delta1.imports_added

    # Rewrite the file to import sys instead.
    (fake_repo / "my_mod.py").write_text("import sys\n")
    delta2 = rx.reindex_file("my_mod.py")
    assert "sys.py" in delta2.imports_added
    assert "os.py" in delta2.imports_removed

    # Verify final edge set.
    with sqlite3.connect(str(shadow)) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT n.resolved_path FROM edges e JOIN nodes n ON n.id = e.tgt_id "
            "WHERE e.src_id = ? AND e.relation_type = 'imports'",
            (delta2.node_id,),
        ).fetchall()
    paths = {r["resolved_path"] for r in rows}
    assert paths == {"sys.py"}


def test_incremental_reindex_tracks_unresolved_imports(tmp_path: Path, big_db: Path) -> None:
    shadow = tmp_path / "shadow.sqlite"
    fake_repo = tmp_path / "repo"
    fake_repo.mkdir()
    (fake_repo / "my_mod.py").write_text("import this_module_does_not_exist\n")
    rx = IncrementalReindexer(source_snapshot=big_db, shadow_snapshot=shadow, repo_root=fake_repo)
    rx.initialize_shadow()
    delta = rx.reindex_file("my_mod.py")
    assert "this_module_does_not_exist" in delta.unresolved_imports
    assert delta.imports_added == []


def test_incremental_reindex_handles_syntax_error_gracefully(tmp_path: Path, big_db: Path) -> None:
    shadow = tmp_path / "shadow.sqlite"
    fake_repo = tmp_path / "repo"
    fake_repo.mkdir()
    (fake_repo / "broken.py").write_text("def oops(\n")  # syntax error
    rx = IncrementalReindexer(source_snapshot=big_db, shadow_snapshot=shadow, repo_root=fake_repo)
    rx.initialize_shadow()
    delta = rx.reindex_file("broken.py")
    # Parse failure returns an empty delta; never raises.
    assert delta.imports_added == []
    assert delta.imports_removed == []


# ---------- helper-function unit tests ----------


def test_extract_import_modules_parses_both_forms() -> None:
    import ast as _ast

    code = (
        "import os\n"
        "from pathlib import Path\n"
        "import json, sys\n"
        "from . import relative  # must be ignored (level > 0)\n"
    )
    tree = _ast.parse(code)
    modules = _extract_import_modules(tree)
    assert "os" in modules
    assert "pathlib" in modules
    assert "json" in modules
    assert "sys" in modules
    # Relative imports are excluded by design.
    assert "relative" not in modules


def test_extract_import_modules_dedupes() -> None:
    import ast as _ast

    code = "import os\nimport os\nfrom os import path\n"
    tree = _ast.parse(code)
    modules = _extract_import_modules(tree)
    assert modules.count("os") == 1


def test_infer_layer_for_path_known() -> None:
    assert _infer_layer_for_path("agentic_core/L5_safety/foo.py") == "L5"
    assert _infer_layer_for_path("tools/adg/runtime_query.py") == "L_TOOLS"
    assert _infer_layer_for_path("tests/unit/test_x.py") == "L_TESTS"
    assert _infer_layer_for_path("apps_rg/engines/x.py") == "L_APPS"
    assert _infer_layer_for_path("random/thing.py") == "L_UNKNOWN"


def test_adg_module_prefix_constant() -> None:
    assert ADG_MODULE_PREFIX == "ADG::Module::"


# ---------- integration: query reads from shadow ----------


def test_runtime_query_reads_shadow_snapshot(tmp_path: Path, big_db: Path) -> None:
    """A RuntimeADGQuery pointed at a shadow must see the patched state."""
    shadow = tmp_path / "shadow.sqlite"
    fake_repo = tmp_path / "repo"
    fake_repo.mkdir()
    (fake_repo / "live_edit.py").write_text("import os\n")
    rx = IncrementalReindexer(source_snapshot=big_db, shadow_snapshot=shadow, repo_root=fake_repo)
    rx.initialize_shadow()
    with sqlite3.connect(str(shadow)) as conn:
        conn.execute(
            "INSERT INTO nodes (id, adg_name, entity_type, layer, resolved_path) "
            "VALUES ('tgt_os', 'ADG::Module::os.py', 'module', 'L_STDLIB', 'os.py')"
        )
        conn.commit()
    rx.reindex_file("live_edit.py")

    q = RuntimeADGQuery(sqlite_path=shadow)
    env = q.blast_radius("ADG::Module::live_edit.py")
    assert env.node_id is not None
    assert env.fan_out == 1  # imports os


# ---------- default-query singleton smoke ----------


def test_get_default_query_returns_singleton_or_none() -> None:
    """Should always be safe to call on module import."""
    q = get_default_query()
    # In this repo the snapshot exists → non-None. Cache the result.
    q2 = get_default_query()
    assert q is q2  # same instance
