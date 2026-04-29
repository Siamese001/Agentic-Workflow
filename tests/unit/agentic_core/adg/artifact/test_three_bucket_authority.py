"""Unit tests for the three-bucket authority model (2026-04-29).

These tests cover the new three-bucket primitives in
``agentic_core/adg/artifact/edge_authority.py``:

* Closed enums: ``Bucket``, ``ResolutionStatus``, ``AuthorityStatus``
* Authority law: ``is_proof()``, ``is_risk()``, ``is_inventory_only()``
* Mapping: ``LEGACY_AUTHORITY_TO_TRIPLET`` /  ``map_legacy_authority``
* Triplet classifier: ``classify_triplet``
* SQL backfill: ``SQL_TRIPLET_BACKFILL`` (lockstep with the Python path)
* The three canonical views: ``proof_view`` / ``risk_view`` / ``inventory_view``
"""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[5]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from agentic_core.adg.artifact.edge_authority import (  # noqa: E402
    ALL_AUTHORITIES,
    ALL_AUTHORITY_STATUSES,
    ALL_BUCKETS,
    ALL_RESOLUTION_STATUSES,
    INVENTORY_ONLY_STATUSES,
    LEGACY_AUTHORITY_TO_TRIPLET,
    PROOF_STATUSES,
    REGISTRY_RESOLUTION_STATUSES,
    RISK_STATUSES,
    RUNTIME_RESOLUTION_STATUSES,
    SQL_AUTHORITY_BACKFILL,
    SQL_INVENTORY_VIEW,
    SQL_PROOF_VIEW,
    SQL_RISK_VIEW,
    SQL_TRIPLET_BACKFILL,
    STATIC_RESOLUTION_STATUSES,
    classify_triplet,
    is_inventory_only,
    is_proof,
    is_risk,
    map_legacy_authority,
)


class TestClosedEnums:
    def test_three_buckets(self) -> None:
        assert ALL_BUCKETS == frozenset({"static", "runtime", "registry"})

    def test_authority_statuses_total_count(self) -> None:
        # Per spec Section 2: 10 distinct authority_status values.
        assert len(ALL_AUTHORITY_STATUSES) == 10

    def test_authority_statuses_values(self) -> None:
        assert ALL_AUTHORITY_STATUSES == frozenset(
            {
                "AUTHORITATIVE",
                "AUTHORITATIVE_RUNTIME",
                "AUTHORITATIVE_REGISTRY",
                "PARTIAL",
                "NON_AUTHORITATIVE_HINT",
                "RISK_SIGNAL_ONLY",
                "EXCLUDED_TEST_ONLY",
                "EXCLUDED_TYPE_ONLY",
                "EXTERNAL_ONLY",
                "UNKNOWN_NOT_PROOF",
            }
        )

    def test_resolution_statuses_per_bucket(self) -> None:
        # Static-bucket-only resolution statuses
        assert "VERIFIED_MODULE" in STATIC_RESOLUTION_STATUSES
        assert "UNRESOLVED_DYNAMIC" in STATIC_RESOLUTION_STATUSES
        # Runtime-bucket-only
        assert "VERIFIED_RUNTIME" in RUNTIME_RESOLUTION_STATUSES
        assert "MISSING_TRACE" in RUNTIME_RESOLUTION_STATUSES
        # Registry-bucket-only
        assert "VERIFIED_REGISTRY" in REGISTRY_RESOLUTION_STATUSES
        assert "STALE_REGISTRY" in REGISTRY_RESOLUTION_STATUSES

    def test_all_resolution_statuses_is_union(self) -> None:
        assert ALL_RESOLUTION_STATUSES == (
            STATIC_RESOLUTION_STATUSES | RUNTIME_RESOLUTION_STATUSES | REGISTRY_RESOLUTION_STATUSES
        )


class TestAuthorityLaw:
    """Tests for the proof/risk/inventory_only law functions.

    Spec Section 2: "Only AUTHORITATIVE/AUTHORITATIVE_RUNTIME/
    AUTHORITATIVE_REGISTRY may be treated as proof. Everything else is not
    proof."
    """

    def test_proof_subset(self) -> None:
        assert PROOF_STATUSES == frozenset(
            {"AUTHORITATIVE", "AUTHORITATIVE_RUNTIME", "AUTHORITATIVE_REGISTRY"}
        )

    def test_risk_subset(self) -> None:
        assert RISK_STATUSES == frozenset({"RISK_SIGNAL_ONLY", "UNKNOWN_NOT_PROOF", "PARTIAL"})

    def test_inventory_only_subset(self) -> None:
        assert INVENTORY_ONLY_STATUSES == frozenset(
            {"EXCLUDED_TEST_ONLY", "EXCLUDED_TYPE_ONLY", "EXTERNAL_ONLY", "NON_AUTHORITATIVE_HINT"}
        )

    def test_three_subsets_partition_authority_statuses(self) -> None:
        # Every authority_status falls into exactly one law-bucket.
        assert PROOF_STATUSES.isdisjoint(RISK_STATUSES)
        assert PROOF_STATUSES.isdisjoint(INVENTORY_ONLY_STATUSES)
        assert RISK_STATUSES.isdisjoint(INVENTORY_ONLY_STATUSES)
        assert PROOF_STATUSES | RISK_STATUSES | INVENTORY_ONLY_STATUSES == ALL_AUTHORITY_STATUSES

    def test_is_proof_returns_true_for_proof_statuses(self) -> None:
        for s in PROOF_STATUSES:
            assert is_proof(s)

    def test_is_proof_returns_false_for_non_proof_statuses(self) -> None:
        for s in RISK_STATUSES | INVENTORY_ONLY_STATUSES:
            assert not is_proof(s)

    def test_is_risk_returns_true_for_risk_statuses(self) -> None:
        for s in RISK_STATUSES:
            assert is_risk(s)

    def test_is_risk_returns_false_for_proof_or_inventory(self) -> None:
        for s in PROOF_STATUSES | INVENTORY_ONLY_STATUSES:
            assert not is_risk(s)

    def test_is_inventory_only_partition(self) -> None:
        for s in INVENTORY_ONLY_STATUSES:
            assert is_inventory_only(s)
        for s in PROOF_STATUSES | RISK_STATUSES:
            assert not is_inventory_only(s)


class TestLegacyMapping:
    """Tests for the back-compat mapping from 2026-04-28 ``authority`` →
    2026-04-29 (bucket, resolution_status, authority_status) triplet.
    """

    def test_every_legacy_value_maps(self) -> None:
        for legacy in ALL_AUTHORITIES:
            assert legacy in LEGACY_AUTHORITY_TO_TRIPLET
            triplet = LEGACY_AUTHORITY_TO_TRIPLET[legacy]
            bucket, res, auth = triplet
            assert bucket in ALL_BUCKETS
            assert res in ALL_RESOLUTION_STATUSES
            assert auth in ALL_AUTHORITY_STATUSES

    def test_verified_maps_to_authoritative_static(self) -> None:
        assert map_legacy_authority("verified") == ("static", "VERIFIED_MODULE", "AUTHORITATIVE")

    def test_unresolved_maps_to_risk_signal_only(self) -> None:
        assert map_legacy_authority("unresolved") == (
            "static",
            "UNRESOLVED_MODULE",
            "RISK_SIGNAL_ONLY",
        )

    def test_dynamic_maps_to_unknown_not_proof(self) -> None:
        assert map_legacy_authority("dynamic") == (
            "static",
            "UNRESOLVED_DYNAMIC",
            "UNKNOWN_NOT_PROOF",
        )

    def test_external_maps_to_external_only(self) -> None:
        assert map_legacy_authority("external") == ("static", "NOT_APPLICABLE", "EXTERNAL_ONLY")

    def test_test_only_maps_to_excluded_test_only(self) -> None:
        assert map_legacy_authority("test_only") == (
            "static",
            "VERIFIED_MODULE",
            "EXCLUDED_TEST_ONLY",
        )

    def test_runtime_observed_maps_to_authoritative_runtime(self) -> None:
        assert map_legacy_authority("runtime_observed") == (
            "runtime",
            "VERIFIED_RUNTIME",
            "AUTHORITATIVE_RUNTIME",
        )

    def test_unknown_legacy_raises(self) -> None:
        try:
            map_legacy_authority("not_a_legacy_value")
        except KeyError:
            return
        raise AssertionError("expected KeyError for unknown legacy authority")


class TestTripletClassifier:
    """Tests for ``classify_triplet`` (Python path).

    The triplet classifier is a thin wrapper around ``classify_authority``
    + ``map_legacy_authority``; tests verify the wrap is correct.
    """

    def test_resolved_internal_yields_authoritative(self) -> None:
        triplet = classify_triplet(
            source_file="agentic_core/L0_routing/foo.py",
            dst_resolved_path="agentic_core/L0_routing/bar.py",
            dst_adg_name="ADG::Module::agentic_core.L0_routing.bar",
        )
        assert triplet == ("static", "VERIFIED_MODULE", "AUTHORITATIVE")

    def test_unresolved_internal_yields_risk_signal_only(self) -> None:
        triplet = classify_triplet(
            source_file="agentic_core/foo.py",
            dst_resolved_path="",
            dst_adg_name="ADG::Symbol::agentic_core.does_not_exist",
        )
        assert triplet == ("static", "UNRESOLVED_MODULE", "RISK_SIGNAL_ONLY")

    def test_dynamic_yields_unknown_not_proof(self) -> None:
        triplet = classify_triplet(
            source_file="agentic_core/loader.py",
            dst_resolved_path="agentic_core/x.py",
            dst_adg_name="ADG::Module::agentic_core.x",
            is_dynamic=True,
        )
        assert triplet == ("static", "UNRESOLVED_DYNAMIC", "UNKNOWN_NOT_PROOF")

    def test_external_yields_external_only(self) -> None:
        triplet = classify_triplet(
            source_file="agentic_core/foo.py",
            dst_resolved_path="",
            dst_adg_name="ADG::Module::numpy",
        )
        assert triplet == ("static", "NOT_APPLICABLE", "EXTERNAL_ONLY")

    def test_test_only_yields_excluded_test_only(self) -> None:
        triplet = classify_triplet(
            source_file="tests/unit/foo.py",
            dst_resolved_path="agentic_core/x.py",
            dst_adg_name="ADG::Module::agentic_core.x",
        )
        assert triplet == ("static", "VERIFIED_MODULE", "EXCLUDED_TEST_ONLY")

    def test_runtime_observed_yields_authoritative_runtime(self) -> None:
        triplet = classify_triplet(
            source_file="otel_span:foo",
            dst_resolved_path="agentic_core/x.py",
            dst_adg_name="ADG::Module::agentic_core.x",
            is_runtime_observed=True,
        )
        assert triplet == ("runtime", "VERIFIED_RUNTIME", "AUTHORITATIVE_RUNTIME")


class TestSQLTripletBackfill:
    """SQL path for the triplet backfill must agree with the Python path."""

    @staticmethod
    def _build_db(legacy_authorities: list[str]) -> sqlite3.Connection:
        con = sqlite3.connect(":memory:")
        con.executescript(
            "CREATE TABLE nodes (id INTEGER PRIMARY KEY, adg_name TEXT, resolved_path TEXT);"
            "CREATE TABLE edges ("
            "  id INTEGER PRIMARY KEY,"
            "  authority TEXT,"
            "  bucket TEXT,"
            "  resolution_status TEXT,"
            "  authority_status TEXT"
            ")"
        )
        for i, legacy in enumerate(legacy_authorities, start=1):
            con.execute(
                "INSERT INTO edges (id, authority) VALUES (?, ?)",
                (i, legacy),
            )
        con.commit()
        return con

    def test_backfill_runtime_observed(self) -> None:
        con = self._build_db(["runtime_observed"])
        con.executescript(SQL_TRIPLET_BACKFILL + ";")
        row = con.execute(
            "SELECT bucket, resolution_status, authority_status FROM edges WHERE id=1"
        ).fetchone()
        assert row == ("runtime", "VERIFIED_RUNTIME", "AUTHORITATIVE_RUNTIME")

    def test_backfill_verified_yields_static_authoritative(self) -> None:
        con = self._build_db(["verified"])
        con.executescript(SQL_TRIPLET_BACKFILL + ";")
        row = con.execute(
            "SELECT bucket, resolution_status, authority_status FROM edges WHERE id=1"
        ).fetchone()
        assert row == ("static", "VERIFIED_MODULE", "AUTHORITATIVE")

    def test_backfill_all_six_legacy_values(self) -> None:
        legacies = ["verified", "unresolved", "dynamic", "external", "test_only", "runtime_observed"]
        con = self._build_db(legacies)
        con.executescript(SQL_TRIPLET_BACKFILL + ";")
        rows = con.execute(
            "SELECT id, bucket, resolution_status, authority_status FROM edges ORDER BY id"
        ).fetchall()
        assert len(rows) == 6
        # Each row must match the Python-path mapping exactly.
        for row, legacy in zip(rows, legacies):
            _id, bucket, res, auth = row
            assert (bucket, res, auth) == map_legacy_authority(legacy), (
                f"SQL mapping diverged for legacy={legacy}: SQL={row[1:]} Python={map_legacy_authority(legacy)}"
            )

    def test_backfill_is_idempotent(self) -> None:
        con = self._build_db(["verified", "unresolved"])
        con.executescript(SQL_TRIPLET_BACKFILL + ";")
        # Run again — should be a no-op (WHERE clause excludes non-NULL).
        con.executescript(SQL_TRIPLET_BACKFILL + ";")
        rows = con.execute("SELECT bucket, authority_status FROM edges ORDER BY id").fetchall()
        assert rows == [("static", "AUTHORITATIVE"), ("static", "RISK_SIGNAL_ONLY")]


class TestThreeViews:
    """Tests for proof_view / risk_view / inventory_view membership."""

    @staticmethod
    def _build_db_with_views() -> sqlite3.Connection:
        con = sqlite3.connect(":memory:")
        # Minimal `edges` table + the new triplet columns.
        con.executescript(
            "CREATE TABLE edges ("
            "  id INTEGER PRIMARY KEY,"
            "  authority TEXT,"
            "  bucket TEXT,"
            "  resolution_status TEXT,"
            "  authority_status TEXT"
            ")"
        )
        # Seed one edge per authority_status.
        cases = [
            (1, "AUTHORITATIVE", "static"),
            (2, "AUTHORITATIVE_RUNTIME", "runtime"),
            (3, "AUTHORITATIVE_REGISTRY", "registry"),
            (4, "PARTIAL", "static"),
            (5, "NON_AUTHORITATIVE_HINT", "static"),
            (6, "RISK_SIGNAL_ONLY", "static"),
            (7, "EXCLUDED_TEST_ONLY", "static"),
            (8, "EXCLUDED_TYPE_ONLY", "static"),
            (9, "EXTERNAL_ONLY", "static"),
            (10, "UNKNOWN_NOT_PROOF", "static"),
        ]
        for _id, status, bucket in cases:
            con.execute(
                "INSERT INTO edges (id, bucket, authority_status) VALUES (?, ?, ?)",
                (_id, bucket, status),
            )
        con.commit()
        # Build the three views.
        con.executescript(SQL_PROOF_VIEW)
        con.executescript(SQL_RISK_VIEW)
        con.executescript(SQL_INVENTORY_VIEW)
        return con

    def test_proof_view_contains_only_authoritative_statuses(self) -> None:
        con = self._build_db_with_views()
        rows = sorted(r[0] for r in con.execute("SELECT id FROM proof_view").fetchall())
        # ids 1, 2, 3 carry the three AUTHORITATIVE* statuses.
        assert rows == [1, 2, 3]

    def test_proof_view_excludes_partial(self) -> None:
        con = self._build_db_with_views()
        ids = {r[0] for r in con.execute("SELECT id FROM proof_view").fetchall()}
        assert 4 not in ids  # PARTIAL is not proof

    def test_proof_view_excludes_unresolved_dynamic_external_test(self) -> None:
        con = self._build_db_with_views()
        ids = {r[0] for r in con.execute("SELECT id FROM proof_view").fetchall()}
        # 6=RISK_SIGNAL_ONLY, 7=EXCLUDED_TEST, 8=EXCLUDED_TYPE, 9=EXTERNAL, 10=UNKNOWN
        for excluded in (6, 7, 8, 9, 10):
            assert excluded not in ids

    def test_risk_view_contains_risk_statuses_only(self) -> None:
        con = self._build_db_with_views()
        rows = sorted(r[0] for r in con.execute("SELECT id FROM risk_view").fetchall())
        # 4=PARTIAL, 6=RISK_SIGNAL_ONLY, 10=UNKNOWN_NOT_PROOF
        assert rows == [4, 6, 10]

    def test_risk_view_excludes_proof_and_inventory_only(self) -> None:
        con = self._build_db_with_views()
        ids = {r[0] for r in con.execute("SELECT id FROM risk_view").fetchall()}
        # No proof statuses, no inventory-only statuses
        for s in (1, 2, 3, 5, 7, 8, 9):
            assert s not in ids

    def test_inventory_view_contains_every_edge(self) -> None:
        con = self._build_db_with_views()
        rows = sorted(r[0] for r in con.execute("SELECT id FROM inventory_view").fetchall())
        assert rows == list(range(1, 11))

    def test_views_are_idempotent_on_recreation(self) -> None:
        con = self._build_db_with_views()
        # Re-run the DDL — each view uses DROP+CREATE so this is a no-op
        # equivalent.
        con.executescript(SQL_PROOF_VIEW)
        con.executescript(SQL_RISK_VIEW)
        con.executescript(SQL_INVENTORY_VIEW)
        # And each view still has the right membership.
        proof = sorted(r[0] for r in con.execute("SELECT id FROM proof_view").fetchall())
        assert proof == [1, 2, 3]


class TestEndToEnd:
    """End-to-end test: legacy backfill → triplet backfill → proof_view."""

    @staticmethod
    def _build_full_db() -> sqlite3.Connection:
        con = sqlite3.connect(":memory:")
        con.executescript(
            "CREATE TABLE nodes ("
            "  id INTEGER PRIMARY KEY,"
            "  adg_name TEXT,"
            "  resolved_path TEXT"
            ");"
            "CREATE TABLE edges ("
            "  id INTEGER PRIMARY KEY,"
            "  src_id INTEGER,"
            "  dst_id INTEGER,"
            "  relation_type TEXT DEFAULT 'imports',"
            "  edge_kind TEXT DEFAULT 'from_import',"
            "  source_file TEXT,"
            "  line_no INTEGER DEFAULT 0,"
            "  symbol TEXT DEFAULT '',"
            "  dynamic_resolution TEXT DEFAULT '',"
            "  authority TEXT,"
            "  bucket TEXT,"
            "  resolution_status TEXT,"
            "  authority_status TEXT"
            ")"
        )
        # Five distinct dst nodes: verified, unresolved, dynamic, external, test_src.
        nodes = [
            (1, "ADG::Module::agentic_core.real", "agentic_core/real.py"),
            (2, "ADG::Symbol::agentic_core.fake.bogus", ""),
            (3, "ADG::Module::agentic_core.dyn", "agentic_core/dyn.py"),
            (4, "ADG::Module::numpy", ""),
            (5, "ADG::Module::agentic_core.x", "agentic_core/x.py"),
        ]
        for n in nodes:
            con.execute("INSERT INTO nodes VALUES (?, ?, ?)", n)
        # Edges: verified, unresolved, dynamic, external, test_only
        edges = [
            (1, 0, 1, "imports", "from_import", "agentic_core/c.py", 0, "", ""),
            (2, 0, 2, "imports", "from_import", "agentic_core/c.py", 0, "", ""),
            (3, 0, 3, "imports", "dynamic_import", "agentic_core/loader.py", 0, "", "dynamic"),
            (4, 0, 4, "imports", "from_import", "agentic_core/c.py", 0, "", ""),
            (5, 0, 5, "imports", "from_import", "tests/unit/foo.py", 0, "", ""),
        ]
        for e in edges:
            con.execute(
                "INSERT INTO edges (id, src_id, dst_id, relation_type, edge_kind, "
                "source_file, line_no, symbol, dynamic_resolution) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                e,
            )
        con.commit()
        return con

    def test_full_pipeline_classifies_all_five_edge_classes(self) -> None:
        con = self._build_full_db()
        # Step 1: legacy backfill (single-axis enum).
        con.executescript(SQL_AUTHORITY_BACKFILL + ";")
        # Step 2: triplet backfill (three-bucket model).
        con.executescript(SQL_TRIPLET_BACKFILL + ";")
        # Step 3: build the canonical views.
        con.executescript(SQL_PROOF_VIEW)
        con.executescript(SQL_RISK_VIEW)
        con.executescript(SQL_INVENTORY_VIEW)
        # Verify each edge has the expected (bucket, authority_status).
        rows = con.execute("SELECT id, bucket, authority_status FROM edges ORDER BY id").fetchall()
        assert rows == [
            (1, "static", "AUTHORITATIVE"),
            (2, "static", "RISK_SIGNAL_ONLY"),
            (3, "static", "UNKNOWN_NOT_PROOF"),
            (4, "static", "EXTERNAL_ONLY"),
            (5, "static", "EXCLUDED_TEST_ONLY"),
        ]
        # proof_view should contain only the verified edge (id=1).
        proof = [r[0] for r in con.execute("SELECT id FROM proof_view ORDER BY id").fetchall()]
        assert proof == [1]
        # risk_view: unresolved (2), dynamic (3) — both classified as risk
        # statuses (RISK_SIGNAL_ONLY, UNKNOWN_NOT_PROOF).
        risk = sorted(r[0] for r in con.execute("SELECT id FROM risk_view").fetchall())
        assert risk == [2, 3]
        # inventory_view: everything.
        inv = sorted(r[0] for r in con.execute("SELECT id FROM inventory_view").fetchall())
        assert inv == [1, 2, 3, 4, 5]

    def test_no_edge_can_remain_unclassified(self) -> None:
        """ADG_CERTIFIED invariant: no edge may be missing bucket /
        resolution_status / authority_status after backfill."""
        con = self._build_full_db()
        con.executescript(SQL_AUTHORITY_BACKFILL + ";")
        con.executescript(SQL_TRIPLET_BACKFILL + ";")
        nulls = con.execute(
            "SELECT COUNT(*) FROM edges WHERE bucket IS NULL "
            "OR resolution_status IS NULL OR authority_status IS NULL"
        ).fetchone()[0]
        assert nulls == 0
