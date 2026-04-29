"""Unit tests for the edge-authority classifier.

The classifier is the SSOT for the closed-enum value of every edge in the
canonical ADG ``edges`` table. Per 2026-04-28 graph-authority directive,
every edge MUST be typed as one of: verified, unresolved, dynamic, external,
test_only, runtime_observed.
"""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[5]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from agentic_core.adg.artifact.edge_authority import (  # noqa: E402
    ALL_AUTHORITIES,
    SQL_AUTHORITY_BACKFILL,
    SQL_MV_GOVERNANCE,
    SQL_MV_UNRESOLVED,
    SQL_MV_VERIFIED,
    classify_authority,
    is_internal_module_name,
)


class TestClosedEnum:
    def test_six_authorities_total(self) -> None:
        assert ALL_AUTHORITIES == frozenset(
            {
                "verified",
                "unresolved",
                "dynamic",
                "external",
                "test_only",
                "runtime_observed",
            }
        )


class TestIsInternalModuleName:
    @pytest.mark.parametrize(
        "name",
        [
            "agentic_core",
            "agentic_core.L0_routing",
            "agentic_core.L0_routing.config.path_constants",
            "apps_eval.engines.x",
            "apps_shared",
            "system_learning.bus",
            "ops_scripts.ci.run_contract_gates",
            "tools.adg.scanner",
            "infrastructure.sdks_mcps.client_wrappers",
            "scripts.proof.run_cache_proof",
        ],
    )
    def test_internal_paths(self, name: str) -> None:
        assert is_internal_module_name(name) is True

    @pytest.mark.parametrize(
        "name",
        [
            "os",
            "pathlib",
            "json",
            "numpy.linalg",
            "requests.adapters",
            "pytest",
            "torch.nn",
            "",
            "agentic_corex",  # near-miss but not a true prefix
        ],
    )
    def test_external_paths(self, name: str) -> None:
        assert is_internal_module_name(name) is False


class TestPrecedence:
    """Highest-to-lowest precedence: runtime_observed > test_only > dynamic >
    external > verified > unresolved."""

    def test_runtime_observed_wins_over_test(self) -> None:
        # A runtime-observed edge from a test file is still runtime_observed.
        assert (
            classify_authority(
                source_file="tests/unit/foo.py",
                dst_resolved_path="agentic_core/x.py",
                dst_adg_name="ADG::Module::agentic_core.x",
                is_runtime_observed=True,
            )
            == "runtime_observed"
        )

    def test_test_only_wins_over_dynamic(self) -> None:
        assert (
            classify_authority(
                source_file="tests/integration/foo.py",
                dst_resolved_path="",
                dst_adg_name="ADG::Module::agentic_core.x",
                is_dynamic=True,
            )
            == "test_only"
        )

    def test_dynamic_wins_over_verified(self) -> None:
        assert (
            classify_authority(
                source_file="agentic_core/loader.py",
                dst_resolved_path="agentic_core/target.py",
                dst_adg_name="ADG::Module::agentic_core.target",
                is_dynamic=True,
            )
            == "dynamic"
        )


class TestBaseClassification:
    def test_verified_when_resolved_path_set(self) -> None:
        assert (
            classify_authority(
                source_file="agentic_core/consumer.py",
                dst_resolved_path="agentic_core/target.py",
                dst_adg_name="ADG::Module::agentic_core.target",
            )
            == "verified"
        )

    def test_unresolved_when_internal_but_no_resolved_path(self) -> None:
        # The exact pre-2026-04-28 bug: kernel typo path
        assert (
            classify_authority(
                source_file="agentic_core/L0_routing/enforcement/safety_kernel_seam.py",
                dst_resolved_path="",
                dst_adg_name=(
                    "ADG::Symbol::agentic_core.L5_safety.core_kernel"
                    ".classification_kernel.classify_file_standalone"
                ),
            )
            == "unresolved"
        )

    def test_external_when_third_party(self) -> None:
        assert (
            classify_authority(
                source_file="agentic_core/x.py",
                dst_resolved_path="",
                dst_adg_name="ADG::Module::numpy.linalg",
            )
            == "external"
        )

    def test_external_when_stdlib(self) -> None:
        assert (
            classify_authority(
                source_file="agentic_core/x.py",
                dst_resolved_path="",
                dst_adg_name="ADG::Module::os.path",
            )
            == "external"
        )

    def test_test_only_for_tests_subtree(self) -> None:
        assert (
            classify_authority(
                source_file="tests/unit/agentic_core/foo.py",
                dst_resolved_path="agentic_core/x.py",
                dst_adg_name="ADG::Module::agentic_core.x",
            )
            == "test_only"
        )

    def test_test_only_for_conftest(self) -> None:
        assert (
            classify_authority(
                source_file="conftest.py",
                dst_resolved_path="agentic_core/x.py",
                dst_adg_name="ADG::Module::agentic_core.x",
            )
            == "test_only"
        )

    def test_test_only_for_nested_conftest(self) -> None:
        assert (
            classify_authority(
                source_file="agentic_core/L0_routing/conftest.py",
                dst_resolved_path="agentic_core/x.py",
                dst_adg_name="ADG::Module::agentic_core.x",
            )
            == "test_only"
        )


class TestSqlMirror:
    """The SQL CASE/UPDATE templates must match the Python implementation —
    we test by running them on an in-memory database."""

    def _build_db(self, edges: list[dict], nodes: list[dict]) -> sqlite3.Connection:
        con = sqlite3.connect(":memory:")
        con.execute("CREATE TABLE nodes (id INTEGER PRIMARY KEY, adg_name TEXT, resolved_path TEXT)")
        con.execute(
            "CREATE TABLE edges (id INTEGER PRIMARY KEY, src_id INTEGER, dst_id INTEGER, "
            "relation_type TEXT, edge_kind TEXT, source_file TEXT, line_no INTEGER, "
            "symbol TEXT, dynamic_resolution TEXT, authority TEXT)"
        )
        for n in nodes:
            con.execute(
                "INSERT INTO nodes (id, adg_name, resolved_path) VALUES (?, ?, ?)",
                (n["id"], n["adg_name"], n.get("resolved_path", "")),
            )
        for e in edges:
            # progress_bar: bounded — test fixture inserts ≤O(10) rows.
            con.execute(
                "INSERT INTO edges (id, src_id, dst_id, relation_type, edge_kind, "
                "source_file, line_no, symbol, dynamic_resolution, authority) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, NULL)",
                (
                    e["id"],
                    e.get("src_id", 1),
                    e["dst_id"],
                    e.get("relation_type", "imports"),
                    e.get("edge_kind", "from_import"),
                    e["source_file"],
                    e.get("line_no", 0),
                    e.get("symbol", ""),
                    e.get("dynamic_resolution"),
                ),
            )
        con.commit()
        return con

    def test_backfill_assigns_correct_authorities(self) -> None:
        nodes = [
            # Resolved internal target → verified
            {
                "id": 10,
                "adg_name": "ADG::Module::agentic_core.real",
                "resolved_path": "agentic_core/real.py",
            },
            # Unresolved internal target
            {
                "id": 11,
                "adg_name": "ADG::Symbol::agentic_core.fake.bogus",
                "resolved_path": "",
            },
            # External target
            {
                "id": 12,
                "adg_name": "ADG::Module::numpy.linalg",
                "resolved_path": "",
            },
            # Resolved internal target for a test_only edge
            {
                "id": 13,
                "adg_name": "ADG::Module::agentic_core.x",
                "resolved_path": "agentic_core/x.py",
            },
            # Resolved internal target for a dynamic edge
            {
                "id": 14,
                "adg_name": "ADG::Module::agentic_core.dyn",
                "resolved_path": "agentic_core/dyn.py",
            },
        ]
        edges = [
            {"id": 1, "dst_id": 10, "source_file": "agentic_core/c.py"},  # verified
            {"id": 2, "dst_id": 11, "source_file": "agentic_core/c.py"},  # unresolved
            {"id": 3, "dst_id": 12, "source_file": "agentic_core/c.py"},  # external
            {"id": 4, "dst_id": 13, "source_file": "tests/unit/foo.py"},  # test_only
            {
                "id": 5,
                "dst_id": 14,
                "source_file": "agentic_core/loader.py",
                "dynamic_resolution": "dynamic",
            },  # dynamic
        ]
        con = self._build_db(edges, nodes)
        con.executescript(SQL_AUTHORITY_BACKFILL + ";")
        result = dict(con.execute("SELECT id, authority FROM edges ORDER BY id").fetchall())
        assert result == {
            1: "verified",
            2: "unresolved",
            3: "external",
            4: "test_only",
            5: "dynamic",
        }

    def test_mv_verified_filters_correctly(self) -> None:
        nodes = [
            {"id": 10, "adg_name": "ADG::Module::agentic_core.real", "resolved_path": "agentic_core/real.py"},
            {"id": 11, "adg_name": "ADG::Symbol::agentic_core.fake.bogus", "resolved_path": ""},
        ]
        edges = [
            {"id": 1, "dst_id": 10, "source_file": "agentic_core/c.py"},
            {"id": 2, "dst_id": 11, "source_file": "agentic_core/c.py"},
        ]
        con = self._build_db(edges, nodes)
        con.executescript(SQL_AUTHORITY_BACKFILL + ";")
        con.executescript(SQL_MV_VERIFIED)
        rows = con.execute("SELECT id FROM mv_edges_verified").fetchall()
        assert rows == [(1,)]

    def test_dynamic_import_kind_maps_to_dynamic(self) -> None:
        # Wave 2: synthetic edge from importlib.import_module(literal) emission
        # has edge_kind='dynamic_import' which the SQL backfill MUST map to
        # authority='dynamic' even when its target happens to resolve.
        nodes = [
            {
                "id": 14,
                "adg_name": "ADG::Symbol::agentic_core.dyn_target",
                "resolved_path": "agentic_core/dyn_target.py",
            },
        ]
        edges = [
            {
                "id": 5,
                "dst_id": 14,
                "source_file": "agentic_core/loader.py",
                "edge_kind": "dynamic_import",
            },
        ]
        con = self._build_db(edges, nodes)
        con.executescript(SQL_AUTHORITY_BACKFILL + ";")
        result = dict(con.execute("SELECT id, authority FROM edges").fetchall())
        assert result == {5: "dynamic"}

    def test_mv_governance_excludes_unresolved_and_dynamic(self) -> None:
        # Wave 3: governance MV is the canonical projection downstream
        # consumers MUST join on. It includes verified + external + test_only +
        # runtime_observed and EXCLUDES unresolved + dynamic (the two classes
        # that should not feed hotspot/coverage/governance reports).
        nodes = [
            {"id": 10, "adg_name": "ADG::Module::agentic_core.real", "resolved_path": "agentic_core/real.py"},
            {"id": 11, "adg_name": "ADG::Symbol::agentic_core.fake.bogus", "resolved_path": ""},
            {"id": 12, "adg_name": "ADG::Module::numpy", "resolved_path": ""},
            {"id": 13, "adg_name": "ADG::Module::agentic_core.x", "resolved_path": "agentic_core/x.py"},
            {"id": 14, "adg_name": "ADG::Module::agentic_core.dyn", "resolved_path": "agentic_core/dyn.py"},
        ]
        edges = [
            {"id": 1, "dst_id": 10, "source_file": "agentic_core/c.py"},  # verified
            {"id": 2, "dst_id": 11, "source_file": "agentic_core/c.py"},  # unresolved
            {"id": 3, "dst_id": 12, "source_file": "agentic_core/c.py"},  # external
            {"id": 4, "dst_id": 13, "source_file": "tests/unit/foo.py"},  # test_only
            {
                "id": 5,
                "dst_id": 14,
                "source_file": "agentic_core/loader.py",
                "edge_kind": "dynamic_import",
            },  # dynamic
        ]
        con = self._build_db(edges, nodes)
        con.executescript(SQL_AUTHORITY_BACKFILL + ";")
        con.executescript(SQL_MV_GOVERNANCE)
        rows = sorted(r[0] for r in con.execute("SELECT id FROM mv_edges_governance").fetchall())
        # 1 (verified) + 3 (external) + 4 (test_only) IN; 2 (unresolved) + 5 (dynamic) OUT
        assert rows == [1, 3, 4]

    def test_mv_unresolved_includes_dst_name(self) -> None:
        nodes = [
            {"id": 11, "adg_name": "ADG::Symbol::agentic_core.fake.bogus", "resolved_path": ""},
        ]
        edges = [
            {"id": 2, "dst_id": 11, "source_file": "agentic_core/c.py"},
        ]
        con = self._build_db(edges, nodes)
        con.executescript(SQL_AUTHORITY_BACKFILL + ";")
        con.executescript(SQL_MV_UNRESOLVED)
        rows = con.execute("SELECT id, dst_adg_name, authority FROM mv_edges_unresolved").fetchall()
        assert rows == [(2, "ADG::Symbol::agentic_core.fake.bogus", "unresolved")]
