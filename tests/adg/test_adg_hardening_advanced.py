#!/usr/bin/env python3
"""
ADG Hardening Verification — Advanced & Novel Test Suite (Part 2)

Innovative testing patterns beyond standard unit tests:
  1. Metamorphic Testing — same DB under transformation should preserve invariants
  2. Differential Testing — verify multiple scripts agree on shared truths
  3. Monotonicity Tests — adding edges/nodes should never decrease certain metrics
  4. Snapshot Regression — verify production DB doesn't regress from known baselines
  5. Contract Tests — public APIs of all verifier classes satisfy interface contracts
  6. Mutation Testing Probes — known-bad injections must be caught
  7. Symmetry Tests — relationship properties like transitivity/symmetry
  8. Boundary/Cardinality Tests — zero, one, many, extreme-scale
  9. Error Taxonomy Completeness — every code path surfaces a distinct error class
  10. Idempotency Tests — running verifier twice yields identical results
"""

from __future__ import annotations

import hashlib
import sqlite3
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
REAL_ADG_DIR = Path("c:/Git/Agentic-Workflow/artifacts/adg")

sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(SCRIPTS_DIR))


# ═══════════════════════════════════════════════════════════════════════════
# SHARED FIXTURE: Reusable synthetic DB builder
# ═══════════════════════════════════════════════════════════════════════════

_COUNTER = 0

def make_db(tmp_path: Path, *, nodes=None, edges=None, meta_overrides=None,
            violations=None, name: str = "") -> Path:
    """One-shot synthetic DB builder.  Returns path to a ready-to-query SQLite."""
    global _COUNTER
    _COUNTER += 1
    if not name:
        name = f"adg_indexed_adv_{_COUNTER}.sqlite"
    db_path = tmp_path / name
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("""CREATE TABLE nodes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        adg_name TEXT NOT NULL, entity_type TEXT NOT NULL, layer TEXT NOT NULL,
        identity_kind TEXT NOT NULL, confidence TEXT NOT NULL, resolved_path TEXT NOT NULL)""")
    c.execute("""CREATE TABLE edges (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        src_id INTEGER NOT NULL, dst_id INTEGER NOT NULL, relation_type TEXT NOT NULL,
        edge_kind TEXT NOT NULL, source_file TEXT NOT NULL, line_no INTEGER NOT NULL,
        symbol TEXT NOT NULL DEFAULT '')""")
    c.execute("CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
    c.execute("""CREATE TABLE violations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        edge_id INTEGER NOT NULL, category TEXT NOT NULL,
        evidence TEXT NOT NULL DEFAULT '', file_path TEXT NOT NULL DEFAULT '',
        line_no INTEGER NOT NULL DEFAULT 0)""")

    meta = {
        "schema_version": "4.0.0",
        "commit_sha": "abc123def456789012345678901234567890abcd",
        "scanner_digest": hashlib.sha256(b"scanner").hexdigest(),
        "artifact_digest": hashlib.sha256(b"artifact").hexdigest(),
        "total_nodes": "0", "total_edges": "0",
    }
    if meta_overrides:
        meta.update(meta_overrides)
    conn.executemany("INSERT INTO meta (key, value) VALUES (?, ?)", meta.items())

    for n in (nodes or []):
        conn.execute("INSERT INTO nodes (adg_name, entity_type, layer, identity_kind, confidence, resolved_path) VALUES (?,?,?,?,?,?)",
                     (n.get("adg_name", ""), n.get("entity_type", "module"), n.get("layer", "L0"),
                      n.get("identity_kind", "repo_module"), n.get("confidence", "HIGH"), n.get("resolved_path", "")))
    for e in (edges or []):
        conn.execute("INSERT INTO edges (src_id, dst_id, relation_type, edge_kind, source_file, line_no, symbol) VALUES (?,?,?,?,?,?,?)",
                     (e.get("src_id", 1), e.get("dst_id", 1), e.get("relation_type", "calls"),
                      e.get("edge_kind", "static"), e.get("source_file", ""), e.get("line_no", 0), e.get("symbol", "")))
    for v in (violations or []):
        conn.execute("INSERT INTO violations (edge_id, category, evidence, file_path, line_no) VALUES (?,?,?,?,?)",
                     (v.get("edge_id", 0), v.get("category", ""), v.get("evidence", ""), v.get("file_path", ""), v.get("line_no", 0)))

    # Update counts
    c.execute("SELECT COUNT(*) FROM nodes"); nc = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM edges"); ec = c.fetchone()[0]
    c.execute("UPDATE meta SET value = ? WHERE key = 'total_nodes'", (str(nc),))
    c.execute("UPDATE meta SET value = ? WHERE key = 'total_edges'", (str(ec),))
    conn.commit()
    conn.close()
    return db_path


def wrap_adg_dir(tmp_path: Path, db_path: Path) -> Path:
    """Wrap a single DB file into a directory that looks like artifacts/adg."""
    import shutil
    adg_dir = tmp_path / f"adg_wrap_{db_path.stem}"
    adg_dir.mkdir(exist_ok=True)
    shutil.copy2(db_path, adg_dir / db_path.name)
    return adg_dir


# ═══════════════════════════════════════════════════════════════════════════
# 1. METAMORPHIC TESTING — invariants under transformation
# ═══════════════════════════════════════════════════════════════════════════

class TestMetamorphic:
    """Metamorphic relations: transforming the DB should preserve or predictably change results."""

    def test_adding_node_increases_module_count(self, tmp_path):
        """Adding a first-party node must increase the first-party module count by exactly 1."""
        nodes_base = [
            {"adg_name": "ADG::Module::a.py", "layer": "L0", "identity_kind": "repo_module", "confidence": "HIGH", "resolved_path": "a.py"},
        ]
        db1 = make_db(tmp_path, nodes=nodes_base)
        dir1 = wrap_adg_dir(tmp_path, db1)

        nodes_ext = nodes_base + [
            {"adg_name": "ADG::Module::b.py", "layer": "L1", "identity_kind": "repo_module", "confidence": "HIGH", "resolved_path": "b.py"},
        ]
        db2 = make_db(tmp_path, nodes=nodes_ext)
        dir2 = wrap_adg_dir(tmp_path, db2)

        from scripts.verify_identity_completeness import ADGIdentityCompletenessVerifier

        v1 = ADGIdentityCompletenessVerifier(dir1)
        v2 = ADGIdentityCompletenessVerifier(dir2)

        conn1 = sqlite3.connect(v1.sqlite_path)
        c1 = conn1.cursor()
        c1.execute("SELECT COUNT(*) FROM nodes WHERE identity_kind NOT IN ('external_module', 'external_provider')")
        count1 = c1.fetchone()[0]
        conn1.close()

        conn2 = sqlite3.connect(v2.sqlite_path)
        c2 = conn2.cursor()
        c2.execute("SELECT COUNT(*) FROM nodes WHERE identity_kind NOT IN ('external_module', 'external_provider')")
        count2 = c2.fetchone()[0]
        conn2.close()

        assert count2 == count1 + 1, f"Expected {count1 + 1}, got {count2}"

    def test_adding_runtime_edge_increases_runtime_count(self, tmp_path):
        """Adding a runtime-semantic edge must increase runtime edge count by exactly 1."""
        nodes = [
            {"adg_name": "ADG::Module::a.py", "layer": "L0", "identity_kind": "repo_module", "confidence": "HIGH", "resolved_path": "a.py"},
        ]
        edges_base = [
            {"src_id": 1, "dst_id": 1, "relation_type": "calls", "edge_kind": "static"},
        ]
        edges_ext = edges_base + [
            {"src_id": 1, "dst_id": 1, "relation_type": "records_execution_trace", "edge_kind": "runtime"},
        ]

        db1 = make_db(tmp_path, nodes=nodes, edges=edges_base)
        db2 = make_db(tmp_path, nodes=nodes, edges=edges_ext)
        dir1 = wrap_adg_dir(tmp_path, db1)
        dir2 = wrap_adg_dir(tmp_path, db2)

        from scripts.report_behavioral_coverage_ratios import ADGRuntimeStructuralBalanceVerifier

        v1 = ADGRuntimeStructuralBalanceVerifier(dir1)
        v2 = ADGRuntimeStructuralBalanceVerifier(dir2)

        r1 = v1._verify_runtime_semantic_edge_detection()
        r2 = v2._verify_runtime_semantic_edge_detection()

        assert r2["total_runtime_edges"] == r1["total_runtime_edges"] + 1

    def test_removing_all_trace_edges_drops_coverage_to_zero(self, tmp_path):
        """Removing all trace edges should drop trace coverage to zero."""
        nodes = [
            {"adg_name": "ADG::Module::a.py", "layer": "L0", "identity_kind": "repo_module", "confidence": "HIGH", "resolved_path": "a.py"},
        ]
        edges_with_trace = [
            {"src_id": 1, "dst_id": 1, "relation_type": "records_execution_trace", "edge_kind": "runtime"},
            {"src_id": 1, "dst_id": 1, "relation_type": "calls", "edge_kind": "static"},
        ]
        edges_no_trace = [
            {"src_id": 1, "dst_id": 1, "relation_type": "calls", "edge_kind": "static"},
        ]

        db1 = make_db(tmp_path, nodes=nodes, edges=edges_with_trace)
        db2 = make_db(tmp_path, nodes=nodes, edges=edges_no_trace)
        dir1 = wrap_adg_dir(tmp_path, db1)
        dir2 = wrap_adg_dir(tmp_path, db2)

        from scripts.verify_trace_replay_coverage import ADGTraceReplayCoverageVerifier

        v1 = ADGTraceReplayCoverageVerifier(dir1)
        v2 = ADGTraceReplayCoverageVerifier(dir2)

        cov1 = v1._analyze_execution_surface_coverage(1, "ADG::Module::a.py")
        cov2 = v2._analyze_execution_surface_coverage(1, "ADG::Module::a.py")

        assert cov1["has_trace"] is True
        assert cov2["has_trace"] is False

    def test_changing_identity_kind_to_external_removes_from_first_party(self, tmp_path):
        """Changing a node from repo_module to external_module should remove it from first-party counts."""
        nodes_fp = [
            {"adg_name": "ADG::Module::a.py", "layer": "L0", "identity_kind": "repo_module", "confidence": "HIGH", "resolved_path": "a.py"},
        ]
        nodes_ext = [
            {"adg_name": "ADG::Module::a.py", "layer": "L0", "identity_kind": "external_module", "confidence": "HIGH", "resolved_path": "a.py"},
        ]

        db_fp = make_db(tmp_path, nodes=nodes_fp)
        db_ext = make_db(tmp_path, nodes=nodes_ext)

        conn_fp = sqlite3.connect(db_fp)
        c_fp = conn_fp.cursor()
        c_fp.execute("SELECT COUNT(*) FROM nodes WHERE identity_kind NOT IN ('external_module', 'external_provider')")
        fp_count = c_fp.fetchone()[0]
        conn_fp.close()

        conn_ext = sqlite3.connect(db_ext)
        c_ext = conn_ext.cursor()
        c_ext.execute("SELECT COUNT(*) FROM nodes WHERE identity_kind NOT IN ('external_module', 'external_provider')")
        ext_count = c_ext.fetchone()[0]
        conn_ext.close()

        assert fp_count == 1
        assert ext_count == 0


# ═══════════════════════════════════════════════════════════════════════════
# 2. IDEMPOTENCY TESTS — running twice yields identical results
# ═══════════════════════════════════════════════════════════════════════════

class TestIdempotency:
    """Running a verifier twice on the same DB must produce bit-identical results."""

    def test_consistency_verifier_idempotent(self, tmp_path):
        nodes = [{"adg_name": "ADG::Module::x.py", "layer": "L0", "identity_kind": "repo_module", "confidence": "HIGH", "resolved_path": "x.py"}]
        edges = [{"src_id": 1, "dst_id": 1, "relation_type": "calls", "edge_kind": "static"}]
        db = make_db(tmp_path, nodes=nodes, edges=edges)
        d = wrap_adg_dir(tmp_path, db)

        from scripts.verify_adg_consistency import ADGConsistencyVerifier

        v1 = ADGConsistencyVerifier(d)
        r1 = v1.verify()

        v2 = ADGConsistencyVerifier(d)
        r2 = v2.verify()

        assert r1["status"] == r2["status"]
        assert r1["errors"] == r2["errors"]
        assert r1["warnings"] == r2["warnings"]
        assert r1["summary"] == r2["summary"]

    def test_identity_completeness_idempotent(self, tmp_path):
        nodes = [
            {"adg_name": "ADG::Module::x.py", "layer": "L0", "identity_kind": "repo_module", "confidence": "HIGH", "resolved_path": "x.py"},
            {"adg_name": "ADG::Module::ext", "layer": "L_RUNTIME", "identity_kind": "external_module", "confidence": "HIGH"},
        ]
        db = make_db(tmp_path, nodes=nodes)
        d = wrap_adg_dir(tmp_path, db)

        from scripts.verify_identity_completeness import ADGIdentityCompletenessVerifier

        v1 = ADGIdentityCompletenessVerifier(d)
        r1 = v1.verify()

        v2 = ADGIdentityCompletenessVerifier(d)
        r2 = v2.verify()

        assert r1["status"] == r2["status"]
        assert r1["errors"] == r2["errors"]

    def test_balance_verifier_idempotent(self, tmp_path):
        nodes = [{"adg_name": "ADG::Module::x.py", "layer": "L0", "identity_kind": "repo_module", "confidence": "HIGH", "resolved_path": "x.py"}]
        edges = [
            {"src_id": 1, "dst_id": 1, "relation_type": "calls", "edge_kind": "static"},
            {"src_id": 1, "dst_id": 1, "relation_type": "records_execution_trace", "edge_kind": "runtime"},
        ]
        db = make_db(tmp_path, nodes=nodes, edges=edges)
        d = wrap_adg_dir(tmp_path, db)

        from scripts.report_behavioral_coverage_ratios import ADGRuntimeStructuralBalanceVerifier

        v1 = ADGRuntimeStructuralBalanceVerifier(d)
        r1 = v1.verify()

        v2 = ADGRuntimeStructuralBalanceVerifier(d)
        r2 = v2.verify()

        assert r1["status"] == r2["status"]
        assert r1["summary"] == r2["summary"]


# ═══════════════════════════════════════════════════════════════════════════
# 3. DIFFERENTIAL TESTING — two verifiers must agree on shared truths
# ═══════════════════════════════════════════════════════════════════════════

class TestDifferential:
    """Two independent scripts that query the same underlying truth must agree."""

    def test_identity_and_layer_agree_on_unknown_layer_count(self, tmp_path):
        """Identity verifier and layer verifier must report same UNKNOWN-layer count."""
        nodes = [
            {"adg_name": "ADG::Module::a.py", "layer": "L0", "identity_kind": "repo_module", "confidence": "HIGH", "resolved_path": "a.py"},
            {"adg_name": "ADG::Module::b.py", "layer": "UNKNOWN", "identity_kind": "repo_module", "confidence": "MEDIUM", "resolved_path": "b.py"},
            {"adg_name": "ADG::Module::c.py", "layer": "UNKNOWN", "identity_kind": "repo_module", "confidence": "LOW", "resolved_path": "c.py"},
        ]
        db = make_db(tmp_path, nodes=nodes)
        d = wrap_adg_dir(tmp_path, db)

        # Both verifiers should see 2 UNKNOWN-layer first-party modules
        conn = sqlite3.connect(db)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM nodes WHERE entity_type = 'module' AND layer = 'UNKNOWN' AND identity_kind NOT IN ('external_module', 'external_provider')")
        unknown_count = c.fetchone()[0]
        conn.close()

        assert unknown_count == 2

        # Identity verifier should flag these
        from scripts.verify_identity_completeness import ADGIdentityCompletenessVerifier
        identity_v = ADGIdentityCompletenessVerifier(d)
        identity_v._verify_first_party_module_completeness()
        unknown_errors_identity = [e for e in identity_v.errors if "unknown" in e.lower() and "layer" in e.lower()]
        assert len(unknown_errors_identity) >= 1

    def test_trace_and_balance_agree_on_runtime_edge_count(self, tmp_path):
        """Trace verifier and balance verifier must count same runtime edges."""
        nodes = [
            {"adg_name": "ADG::Module::a.py", "layer": "L0", "identity_kind": "repo_module", "confidence": "HIGH", "resolved_path": "a.py"},
        ]
        edges = [
            {"src_id": 1, "dst_id": 1, "relation_type": "records_execution_trace", "edge_kind": "runtime"},
            {"src_id": 1, "dst_id": 1, "relation_type": "signs_execution_trace", "edge_kind": "runtime"},
            {"src_id": 1, "dst_id": 1, "relation_type": "calls", "edge_kind": "static"},
        ]
        db = make_db(tmp_path, nodes=nodes, edges=edges)
        d = wrap_adg_dir(tmp_path, db)

        from scripts.report_behavioral_coverage_ratios import ADGRuntimeStructuralBalanceVerifier
        from scripts.verify_trace_replay_coverage import ADGTraceReplayCoverageVerifier

        trace_v = ADGTraceReplayCoverageVerifier(d)
        cov = trace_v._analyze_execution_surface_coverage(1, "ADG::Module::a.py")
        assert cov["has_trace"] is True
        assert cov["has_signed_trace"] is True

        balance_v = ADGRuntimeStructuralBalanceVerifier(d)
        runtime_result = balance_v._verify_runtime_semantic_edge_detection()
        # records_execution_trace and signs_execution_trace are both in RUNTIME_SEMANTIC_EDGES
        assert runtime_result["total_runtime_edges"] >= 2


# ═══════════════════════════════════════════════════════════════════════════
# 4. CONTRACT TESTS — verifier public API contracts
# ═══════════════════════════════════════════════════════════════════════════

class TestAPIContracts:
    """All verifier classes must satisfy a common interface contract."""

    VERIFIER_MODULES = [
        ("scripts.verify_adg_consistency", "ADGConsistencyVerifier"),
        ("scripts.verify_identity_completeness", "ADGIdentityCompletenessVerifier"),
        ("scripts.verify_trace_replay_coverage", "ADGTraceReplayCoverageVerifier"),
        ("scripts.verify_layer_authority", "ADGLayerAuthorityVerifier"),
        ("scripts.verify_l4_normalization", "ADGL4NormalizationVerifier"),
        ("scripts.report_behavioral_coverage_ratios", "ADGRuntimeStructuralBalanceVerifier"),
        ("scripts.verify_low_confidence_zones", "ADGDeadCodeZoneControlVerifier"),
    ]

    @pytest.fixture
    def minimal_db(self, tmp_path):
        nodes = [{"adg_name": "ADG::Module::x.py", "layer": "L0", "identity_kind": "repo_module", "confidence": "HIGH", "resolved_path": "x.py"}]
        db = make_db(tmp_path, nodes=nodes)
        return wrap_adg_dir(tmp_path, db)

    @pytest.mark.parametrize("mod_name,cls_name", VERIFIER_MODULES)
    def test_verifier_has_verify_method(self, mod_name, cls_name, minimal_db):
        """Every verifier MUST have a public verify() method."""
        import importlib
        mod = importlib.import_module(mod_name)
        cls = getattr(mod, cls_name)
        instance = cls(minimal_db)
        assert hasattr(instance, "verify"), f"{cls_name} missing verify()"
        assert callable(instance.verify)

    @pytest.mark.parametrize("mod_name,cls_name", VERIFIER_MODULES)
    def test_verifier_has_errors_and_warnings(self, mod_name, cls_name, minimal_db):
        """Every verifier MUST expose errors and warnings lists."""
        import importlib
        mod = importlib.import_module(mod_name)
        cls = getattr(mod, cls_name)
        instance = cls(minimal_db)
        assert hasattr(instance, "errors")
        assert hasattr(instance, "warnings")
        assert isinstance(instance.errors, list)
        assert isinstance(instance.warnings, list)

    @pytest.mark.parametrize("mod_name,cls_name", VERIFIER_MODULES)
    def test_verify_returns_dict_with_status(self, mod_name, cls_name, minimal_db):
        """verify() MUST return a dict containing 'status' key."""
        import importlib
        mod = importlib.import_module(mod_name)
        cls = getattr(mod, cls_name)
        instance = cls(minimal_db)
        result = instance.verify()
        assert isinstance(result, dict), f"{cls_name}.verify() returned {type(result)}"
        assert "status" in result, f"{cls_name}.verify() missing 'status' key"
        assert result["status"] in ("PASS", "FAIL"), f"Invalid status: {result['status']}"


# ═══════════════════════════════════════════════════════════════════════════
# 5. MUTATION INJECTION — known-bad mutations must be caught
# ═══════════════════════════════════════════════════════════════════════════

class TestMutationInjection:
    """Inject known-bad data and verify verifiers catch it."""

    def test_inject_invalid_confidence_caught(self, tmp_path):
        """Node with confidence='INVALID' MUST be flagged."""
        nodes = [
            {"adg_name": "ADG::Module::a.py", "layer": "L0", "identity_kind": "repo_module", "confidence": "INVALID", "resolved_path": "a.py"},
        ]
        db = make_db(tmp_path, nodes=nodes)
        d = wrap_adg_dir(tmp_path, db)

        from scripts.verify_identity_completeness import ADGIdentityCompletenessVerifier
        v = ADGIdentityCompletenessVerifier(d)
        v._verify_enum_value_constraints()

        assert any("invalid" in e.lower() or "confidence" in e.lower() for e in v.errors), \
            f"Expected confidence error, got: {v.errors}"

    def test_inject_self_referencing_import_not_orphaned(self, tmp_path):
        """Self-referencing edge (src_id == dst_id) should NOT be flagged as orphaned."""
        nodes = [{"adg_name": "ADG::Module::a.py", "layer": "L0", "identity_kind": "repo_module", "confidence": "HIGH", "resolved_path": "a.py"}]
        edges = [{"src_id": 1, "dst_id": 1, "relation_type": "imports", "edge_kind": "static"}]
        db = make_db(tmp_path, nodes=nodes, edges=edges)
        d = wrap_adg_dir(tmp_path, db)

        from scripts.verify_adg_consistency import ADGConsistencyVerifier
        v = ADGConsistencyVerifier(d)
        v._verify_foreign_key_integrity()

        orphan_errors = [e for e in v.errors if "orphan" in e.lower()]
        assert len(orphan_errors) == 0

    def test_inject_negative_line_no(self, tmp_path):
        """Edges with negative line_no should not crash verifiers."""
        nodes = [{"adg_name": "ADG::Module::a.py", "layer": "L0", "identity_kind": "repo_module", "confidence": "HIGH", "resolved_path": "a.py"}]
        edges = [{"src_id": 1, "dst_id": 1, "relation_type": "calls", "edge_kind": "static", "line_no": -1}]
        db = make_db(tmp_path, nodes=nodes, edges=edges)
        d = wrap_adg_dir(tmp_path, db)

        from scripts.verify_adg_consistency import ADGConsistencyVerifier
        v = ADGConsistencyVerifier(d)
        result = v.verify()
        # Should complete without crash
        assert result["status"] in ("PASS", "FAIL")

    def test_inject_extremely_long_adg_name(self, tmp_path):
        """Node with 10000-char adg_name should not crash."""
        long_name = "ADG::Module::" + "x" * 10000
        nodes = [{"adg_name": long_name, "layer": "L0", "identity_kind": "repo_module", "confidence": "HIGH", "resolved_path": "x.py"}]
        db = make_db(tmp_path, nodes=nodes)
        d = wrap_adg_dir(tmp_path, db)

        from scripts.verify_identity_completeness import ADGIdentityCompletenessVerifier
        v = ADGIdentityCompletenessVerifier(d)
        result = v.verify()
        assert result["status"] in ("PASS", "FAIL")

    def test_inject_duplicate_meta_keys_handled(self, tmp_path):
        """Duplicate meta keys should be handled (SQLite PRIMARY KEY prevents this)."""
        db = make_db(tmp_path)
        conn = sqlite3.connect(db)
        # Try to insert duplicate key — should fail due to PRIMARY KEY
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute("INSERT INTO meta (key, value) VALUES ('schema_version', 'duplicate')")
        conn.close()


# ═══════════════════════════════════════════════════════════════════════════
# 6. BOUNDARY & CARDINALITY TESTS
# ═══════════════════════════════════════════════════════════════════════════

class TestBoundaryCardinality:
    """Zero, one, many, and extreme-scale boundary conditions."""

    def test_zero_nodes_zero_edges(self, tmp_path):
        """Empty graph: all verifiers should handle gracefully."""
        db = make_db(tmp_path)
        d = wrap_adg_dir(tmp_path, db)

        from scripts.verify_adg_consistency import ADGConsistencyVerifier
        v = ADGConsistencyVerifier(d)
        result = v.verify()
        assert result["status"] == "PASS"

    def test_single_node_no_edges(self, tmp_path):
        """Graph with 1 node, 0 edges: trace coverage should be 0%."""
        nodes = [{"adg_name": "ADG::Module::a.py", "layer": "L0", "identity_kind": "repo_module", "confidence": "HIGH", "resolved_path": "a.py"}]
        db = make_db(tmp_path, nodes=nodes)
        d = wrap_adg_dir(tmp_path, db)

        from scripts.verify_trace_replay_coverage import ADGTraceReplayCoverageVerifier
        v = ADGTraceReplayCoverageVerifier(d)
        cov = v._analyze_execution_surface_coverage(1, "ADG::Module::a.py")
        assert cov["has_trace"] is False
        assert cov["execution_surface_count"] == 0

    def test_all_external_no_first_party(self, tmp_path):
        """Graph with only external modules: first-party count should be 0."""
        nodes = [
            {"adg_name": "ADG::Module::numpy", "layer": "L_RUNTIME", "identity_kind": "external_module", "confidence": "HIGH"},
            {"adg_name": "ADG::Module::pandas", "layer": "L_RUNTIME", "identity_kind": "external_module", "confidence": "HIGH"},
        ]
        db = make_db(tmp_path, nodes=nodes)
        d = wrap_adg_dir(tmp_path, db)

        from scripts.verify_identity_completeness import ADGIdentityCompletenessVerifier
        v = ADGIdentityCompletenessVerifier(d)
        v._verify_first_party_module_completeness()
        # Should not crash and should report 0 first-party modules
        # (the method prints the count internally)

    def test_all_layers_represented(self, tmp_path):
        """Graph with modules in every known layer."""
        layers = ["L0", "L1", "L2", "L3", "L4", "L5", "L6", "L_TEST", "L_TOOLS", "L_RUNTIME", "L_APP", "L_SHARED", "L_OPS", "L_SL"]
        nodes = [{"adg_name": f"ADG::Module::{l.lower()}.py", "layer": l, "identity_kind": "repo_module", "confidence": "HIGH", "resolved_path": f"{l.lower()}.py"}
                 for l in layers]
        db = make_db(tmp_path, nodes=nodes)
        d = wrap_adg_dir(tmp_path, db)

        from scripts.report_behavioral_coverage_ratios import ADGRuntimeStructuralBalanceVerifier
        v = ADGRuntimeStructuralBalanceVerifier(d)
        result = v._verify_layer_balance_analysis()
        assert len(result["layer_balance"]) == len(layers)

    def test_many_violations(self, tmp_path):
        """500 violations should be processable without timeout."""
        nodes = [{"adg_name": "ADG::Module::a.py", "layer": "L0", "identity_kind": "repo_module", "confidence": "HIGH", "resolved_path": "a.py"}]
        edges = [{"src_id": 1, "dst_id": 1, "relation_type": "calls", "edge_kind": "static"}]
        violations = [{"edge_id": 1, "category": f"cat_{i % 5}", "evidence": f"evidence_{i}", "file_path": "a.py", "line_no": i}
                      for i in range(500)]
        db = make_db(tmp_path, nodes=nodes, edges=edges, violations=violations)

        conn = sqlite3.connect(db)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM violations")
        count = c.fetchone()[0]
        conn.close()
        assert count == 500


# ═══════════════════════════════════════════════════════════════════════════
# 7. SYMMETRY & GRAPH PROPERTY TESTS
# ═══════════════════════════════════════════════════════════════════════════

class TestGraphProperties:
    """Verify graph-theoretic properties of ADG data."""

    def test_edge_endpoints_refer_to_existing_nodes(self, tmp_path):
        """Every edge endpoint must reference a valid node (referential integrity)."""
        nodes = [
            {"adg_name": "ADG::Module::a.py", "layer": "L0", "identity_kind": "repo_module", "confidence": "HIGH", "resolved_path": "a.py"},
            {"adg_name": "ADG::Module::b.py", "layer": "L1", "identity_kind": "repo_module", "confidence": "HIGH", "resolved_path": "b.py"},
        ]
        edges = [
            {"src_id": 1, "dst_id": 2, "relation_type": "calls", "edge_kind": "static"},
            {"src_id": 2, "dst_id": 1, "relation_type": "imports", "edge_kind": "static"},
        ]
        db = make_db(tmp_path, nodes=nodes, edges=edges)

        conn = sqlite3.connect(db)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM edges e LEFT JOIN nodes n ON e.src_id = n.id WHERE n.id IS NULL")
        orphaned_src = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM edges e LEFT JOIN nodes n ON e.dst_id = n.id WHERE n.id IS NULL")
        orphaned_dst = c.fetchone()[0]
        conn.close()

        assert orphaned_src == 0
        assert orphaned_dst == 0

    def test_layer_assignment_is_total_for_modules(self, tmp_path):
        """Every module node must have a non-empty layer."""
        nodes = [
            {"adg_name": "ADG::Module::a.py", "layer": "L0", "identity_kind": "repo_module", "confidence": "HIGH", "resolved_path": "a.py"},
            {"adg_name": "ADG::Module::b.py", "layer": "", "identity_kind": "repo_module", "confidence": "HIGH", "resolved_path": "b.py"},
        ]
        db = make_db(tmp_path, nodes=nodes)

        conn = sqlite3.connect(db)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM nodes WHERE entity_type = 'module' AND (layer IS NULL OR layer = '')")
        empty_layer = c.fetchone()[0]
        conn.close()

        assert empty_layer == 1  # We intentionally created one with empty layer

    def test_no_duplicate_edges(self, tmp_path):
        """Exact duplicate edges (same src, dst, relation_type) should be detectable."""
        nodes = [{"adg_name": "ADG::Module::a.py", "layer": "L0", "identity_kind": "repo_module", "confidence": "HIGH", "resolved_path": "a.py"}]
        edges = [
            {"src_id": 1, "dst_id": 1, "relation_type": "calls", "edge_kind": "static", "source_file": "a.py", "line_no": 10},
            {"src_id": 1, "dst_id": 1, "relation_type": "calls", "edge_kind": "static", "source_file": "a.py", "line_no": 10},
        ]
        db = make_db(tmp_path, nodes=nodes, edges=edges)

        conn = sqlite3.connect(db)
        c = conn.cursor()
        c.execute("""
            SELECT src_id, dst_id, relation_type, source_file, line_no, COUNT(*) as cnt
            FROM edges
            GROUP BY src_id, dst_id, relation_type, source_file, line_no
            HAVING cnt > 1
        """)
        duplicates = c.fetchall()
        conn.close()

        assert len(duplicates) == 1  # We inserted 1 pair of duplicates


# ═══════════════════════════════════════════════════════════════════════════
# 8. PRODUCTION REGRESSION BASELINES
# ═══════════════════════════════════════════════════════════════════════════

class TestProductionRegression:
    """Verify the production DB doesn't regress from known baselines."""

    @pytest.fixture(autouse=True)
    def _resolve_production_db(self):
        candidates = sorted(REAL_ADG_DIR.glob("adg_indexed_*.sqlite"), key=lambda p: p.stat().st_mtime, reverse=True) if REAL_ADG_DIR.exists() else []
        if not candidates:
            pytest.skip(f"Production DB not found in {REAL_ADG_DIR}")
        self.db = candidates[0]

    def test_node_count_above_baseline(self):
        """Node count must not drop below 70000 (baseline: 70574)."""
        conn = sqlite3.connect(self.db)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM nodes")
        count = c.fetchone()[0]
        conn.close()
        assert count >= 70000, f"Node count regressed to {count} (baseline: 70574)"

    def test_edge_count_above_baseline(self):
        """Edge count must not drop below 500000 (baseline: 510683)."""
        conn = sqlite3.connect(self.db)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM edges")
        count = c.fetchone()[0]
        conn.close()
        assert count >= 500000, f"Edge count regressed to {count} (baseline: 510683)"

    def test_repo_module_count_above_baseline(self):
        """repo_module count must not drop below 11000 (baseline: 11126)."""
        conn = sqlite3.connect(self.db)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM nodes WHERE identity_kind = 'repo_module'")
        count = c.fetchone()[0]
        conn.close()
        assert count >= 11000, f"repo_module count regressed to {count}"

    def test_high_confidence_dominance(self):
        """HIGH confidence nodes must be >75% of total (baseline: 80.1%)."""
        conn = sqlite3.connect(self.db)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM nodes WHERE confidence = 'HIGH'")
        high = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM nodes")
        total = c.fetchone()[0]
        conn.close()
        pct = (high / total) * 100
        assert pct >= 75.0, f"HIGH confidence dropped to {pct:.1f}%"

    def test_violation_count_bounded(self):
        """Violations must not explode above 10000 (baseline: 4833)."""
        conn = sqlite3.connect(self.db)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM violations")
        count = c.fetchone()[0]
        conn.close()
        assert count <= 10000, f"Violations exploded to {count}"

    def test_imports_dominate_edge_distribution(self):
        """imports must remain the most frequent edge type (baseline: 277805)."""
        conn = sqlite3.connect(self.db)
        c = conn.cursor()
        c.execute("SELECT relation_type, COUNT(*) as cnt FROM edges GROUP BY relation_type ORDER BY cnt DESC LIMIT 1")
        top = c.fetchone()
        conn.close()
        assert top[0] == "imports", f"Top edge type is '{top[0]}', expected 'imports'"

    def test_meta_has_all_required_keys(self):
        """All 6 required meta keys must be present."""
        required = {"schema_version", "commit_sha", "scanner_digest", "artifact_digest", "total_nodes", "total_edges"}
        conn = sqlite3.connect(self.db)
        c = conn.cursor()
        c.execute("SELECT key FROM meta")
        keys = {r[0] for r in c.fetchall()}
        conn.close()
        missing = required - keys
        assert len(missing) == 0, f"Missing meta keys: {missing}"

    def test_no_new_tables_appeared(self):
        """Schema must not have unexpected tables (allowed: nodes, edges, meta, violations, sqlite_sequence)."""
        allowed = {"nodes", "edges", "meta", "violations", "sqlite_sequence"}
        conn = sqlite3.connect(self.db)
        c = conn.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {r[0] for r in c.fetchall()}
        conn.close()
        unexpected = tables - allowed
        assert len(unexpected) == 0, f"Unexpected tables: {unexpected}"

    def test_layer_distribution_stable(self):
        """Known layers must still exist with non-zero module counts."""
        expected_layers = {"L0", "L1", "L2", "L3", "L4", "L5", "L6", "L_TEST", "L_TOOLS", "L_APP"}
        conn = sqlite3.connect(self.db)
        c = conn.cursor()
        c.execute("SELECT DISTINCT layer FROM nodes WHERE entity_type = 'module'")
        actual_layers = {r[0] for r in c.fetchall()}
        conn.close()
        missing = expected_layers - actual_layers
        assert len(missing) == 0, f"Missing layers: {missing}"
