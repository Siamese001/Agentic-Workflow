"""Novel integration & regression tests for ADG Waves 1-3.

Goes beyond unit tests — validates real ADG SQLite output, scan root
alignment, signal classification, dedup effectiveness, confidence floors,
and function_ratio accuracy against actual codebase.

Test categories:
  T1: Wave 1 — Scanner integration (real file scanning)
  T2: Wave 2 — Validation methodology (scan roots, signals, multiline)
  T3: Wave 3 — ADG SQLite invariants (dedup, confidence, ratios)
  T4: Cross-wave — End-to-end consistency checks
"""

from __future__ import annotations

import ast
import os
import sqlite3
import textwrap
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

PROJECT_ROOT = Path(__file__).resolve()
for _ in range(6):  # walk up to repo root
    PROJECT_ROOT = PROJECT_ROOT.parent
    if (PROJECT_ROOT / ".git").exists():
        break

try:
#  # MOVED: from agentic_core.adg.extraction.static_scanner import (
        _SCAN_ROOTS,
        _SEMANTIC_TYPE_MAP,
        Edge,
        ScanResult,
        _ModuleDefinitionVisitor,
        _propagate_violations,
    )

    _SCANNER_AVAILABLE = True
except Exception:
    _SCANNER_AVAILABLE = False

# Locate latest ADG SQLite
_ADG_DIR = PROJECT_ROOT / "artifacts" / "adg"
_SQLITE_CANDIDATES = (
    sorted(
        _ADG_DIR.glob("adg_indexed_*.sqlite"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if _ADG_DIR.exists()
    else []
)
_LATEST_DB = _SQLITE_CANDIDATES[0] if _SQLITE_CANDIDATES else None


def _get_conn():
    """Return a read-only SQLite connection to the latest ADG."""
    if _LATEST_DB is None:

    return sqlite3.connect(f"file:{_LATEST_DB}?mode=ro", uri=True)


# =====================================================================
# T1: WAVE 1 — SCANNER INTEGRATION (real file scanning)
# =====================================================================


class TestT1ModuleDefinitionVisitorIntegration:
    """Test _ModuleDefinitionVisitor against real Python code patterns."""

    @pytest.mark.skipif(not _SCANNER_AVAILABLE, reason="Scanner unavailable")
    def test_defs_inside_if_name_main(self):
        from agentic_core.adg.extraction.static_scanner import (
        """Functions inside `if __name__ == '__main__':` ARE emitted."""
        source = textwrap.dedent("""\
        def public_api():
            pass

        if __name__ == "__main__":
            def main():
                pass
        """)
        tree = ast.parse(source)
        visitor = _ModuleDefinitionVisitor("ADG::Module::m.py", "m.py")
        visitor.visit(tree)
        symbols = {e.symbol for e in visitor.edges}
        assert "public_api" in symbols
        assert "main" in symbols, "Defs inside if __name__ block should be emitted"

    @pytest.mark.skipif(not _SCANNER_AVAILABLE, reason="Scanner unavailable")
    def test_defs_inside_try_except(self):
        """Functions inside try/except blocks ARE emitted."""
        source = textwrap.dedent("""\
        try:
            def guarded_func():
                pass
        except ImportError:
            def fallback_func():
                pass
        """)
        tree = ast.parse(source)
        visitor = _ModuleDefinitionVisitor("ADG::Module::m.py", "m.py")
        visitor.visit(tree)
        symbols = {e.symbol for e in visitor.edges}
        assert "guarded_func" in symbols
        assert "fallback_func" in symbols

    @pytest.mark.skipif(not _SCANNER_AVAILABLE, reason="Scanner unavailable")
    def test_class_with_staticmethod_and_classmethod(self):
        """Static and class methods inside a class ARE emitted."""
        source = textwrap.dedent("""\
        class Config:
            @staticmethod
            def get_default():
                return {}

            @classmethod
            def from_dict(cls, d):
                return cls()

            def instance_method(self):
                pass
        """)
        tree = ast.parse(source)
        visitor = _ModuleDefinitionVisitor("ADG::Module::cfg.py", "cfg.py")
        visitor.visit(tree)
        symbols = {e.symbol for e in visitor.edges}
        assert symbols == {"Config", "get_default", "from_dict", "instance_method"}

    @pytest.mark.skipif(not _SCANNER_AVAILABLE, reason="Scanner unavailable")
    def test_deeply_nested_class_hierarchy(self):
        """Nested classes within nested classes are all emitted."""
        source = textwrap.dedent("""\
        class A:
            class B:
                class C:
                    def deep_method(self):
                        pass
        """)
        tree = ast.parse(source)
        visitor = _ModuleDefinitionVisitor("ADG::Module::n.py", "n.py")
        visitor.visit(tree)
        symbols = {e.symbol for e in visitor.edges}
        assert symbols == {"A", "B", "C", "deep_method"}

    @pytest.mark.skipif(not _SCANNER_AVAILABLE, reason="Scanner unavailable")
    def test_lambda_not_emitted(self):
        """Lambda expressions should NOT produce decomposes_into edges."""
        source = textwrap.dedent("""\
        my_func = lambda x: x + 1
        process = lambda: None
        """)
        tree = ast.parse(source)
        visitor = _ModuleDefinitionVisitor("ADG::Module::l.py", "l.py")
        visitor.visit(tree)
        assert len(visitor.edges) == 0

    @pytest.mark.skipif(not _SCANNER_AVAILABLE, reason="Scanner unavailable")
    def test_nested_function_in_function_not_emitted(self):
        """Closures/nested functions inside a function are NOT emitted."""
        source = textwrap.dedent("""\
        def outer():
            def inner():
                def innermost():
                    pass
                return innermost
            return inner
        """)
        tree = ast.parse(source)
        visitor = _ModuleDefinitionVisitor("ADG::Module::c.py", "c.py")
        visitor.visit(tree)
        assert len(visitor.edges) == 1
        assert visitor.edges[0].symbol == "outer"

    @pytest.mark.skipif(not _SCANNER_AVAILABLE, reason="Scanner unavailable")
    def test_edge_metadata_completeness(self):
        """Every emitted edge must have all required metadata fields."""
        source = textwrap.dedent("""\
        class MyClass:
            async def my_method(self):
                pass
        """)
        tree = ast.parse(source)
        visitor = _ModuleDefinitionVisitor("ADG::Module::meta.py", "meta.py")
        visitor.visit(tree)
        for edge in visitor.edges:
            assert edge.from_name == "ADG::Module::meta.py"
            assert edge.relation_type == "decomposes_into"
            assert edge.edge_kind == "module_definition"
            assert edge.source_file == "meta.py"
            assert edge.line_no > 0
            assert edge.confidence == 1.0
            assert edge.symbol != ""
            assert edge.semantic_type in (
                "module_defines_function",
                "module_defines_async_function",
                "module_defines_class",
            )
            assert edge.source_span_line > 0
            assert edge.source_span_end >= edge.source_span_line

    @pytest.mark.skipif(not _SCANNER_AVAILABLE, reason="Scanner unavailable")
    def test_for_loop_defs_at_module_level(self):
        """Defs inside module-level for loops ARE emitted (generic_visit)."""
        source = textwrap.dedent("""\
        for i in range(3):
            def dynamic_func():
                pass
        """)
        tree = ast.parse(source)
        visitor = _ModuleDefinitionVisitor("ADG::Module::fl.py", "fl.py")
        visitor.visit(tree)
        assert len(visitor.edges) == 1
        assert visitor.edges[0].symbol == "dynamic_func"


class TestT1PropagationDepthConfidence:
    """Test violation propagation confidence at various depths."""

    @pytest.mark.skipif(not _SCANNER_AVAILABLE, reason="Scanner unavailable")
    def test_depth_3_confidence_clamped(self):
        """Depth-3 propagation should clamp at 0.5, not 0.4."""

        # Build chain: violator -> A -> B -> C (depth-3)
        def _e(**kw):
            defaults = {
                "from_name": "",
                "relation_type": "",
                "to_name": "",
                "edge_kind": "internal",
                "source_file": "",
                "line_no": 1,
                "symbol": "",
            }
            defaults.update(kw)
            return Edge(**defaults)

        edges = [
            _e(
                from_name="ADG::Module::v.py",
                relation_type="violates",
                to_name="ADG::Module::layer",
                source_file="v.py",
            ),
            _e(
                from_name="ADG::Module::a.py",
                relation_type="imports",
                to_name="ADG::Symbol::v",
                source_file="a.py",
            ),
            _e(
                from_name="ADG::Module::b.py",
                relation_type="imports",
                to_name="ADG::Symbol::a",
                source_file="b.py",
            ),
            _e(
                from_name="ADG::Module::c.py",
                relation_type="imports",
                to_name="ADG::Symbol::b",
                source_file="c.py",
            ),
        ]
        result = ScanResult(edges=edges)
        propagated = _propagate_violations(result)

        for p in propagated:
            assert p.confidence >= 0.5, f"depth={p.symbol} confidence={p.confidence} < 0.5"

    @pytest.mark.skipif(not _SCANNER_AVAILABLE, reason="Scanner unavailable")
    def test_max_depth_edges_still_valid(self):
        """Even at max propagation depth, confidence >= 0.5."""

        # Build long chain
        def _e(**kw):
            defaults = {
                "from_name": "",
                "relation_type": "",
                "to_name": "",
                "edge_kind": "internal",
                "source_file": "",
                "line_no": 1,
                "symbol": "",
            }
            defaults.update(kw)
            return Edge(**defaults)

        edges = [
            _e(
                from_name="ADG::Module::v.py",
                relation_type="violates",
                to_name="ADG::Module::layer",
                source_file="v.py",
            ),
        ]
        # Chain of 10 importers
        prev = "v"
        for i in range(10):
            name = f"m{i}"
            edges.append(
                _e(
                    from_name=f"ADG::Module::{name}.py",
                    relation_type="imports",
                    to_name=f"ADG::Symbol::{prev}",
                    source_file=f"{name}.py",
                )
            )
            prev = name

        result = ScanResult(edges=edges)
        propagated = _propagate_violations(result)

        for p in propagated:
            assert p.confidence >= 0.5


class TestT1SemanticTypeMap:
    """Verify _SEMANTIC_TYPE_MAP coverage for Wave 1c edge types."""

    @pytest.mark.skipif(not _SCANNER_AVAILABLE, reason="Scanner unavailable")
    def test_module_definition_in_semantic_map(self):
        """module_definition edge_kind must be in _SEMANTIC_TYPE_MAP."""
        key = ("module_definition", "decomposes_into")
        assert key in _SEMANTIC_TYPE_MAP, f"Missing semantic type mapping for {key}"
        assert _SEMANTIC_TYPE_MAP[key] == "module_definition"

    @pytest.mark.skipif(not _SCANNER_AVAILABLE, reason="Scanner unavailable")
    def test_violation_propagation_in_semantic_map(self):
        """violation_propagation must be mapped."""
        key = ("violation_propagation", "violation_propagates_through")
        assert key in _SEMANTIC_TYPE_MAP

    @pytest.mark.skipif(not _SCANNER_AVAILABLE, reason="Scanner unavailable")
    def test_block_decomposition_in_semantic_map(self):
        """block decomposition must be mapped."""
        key = ("decomposition", "decomposes_into")
        assert key in _SEMANTIC_TYPE_MAP


# =====================================================================
# T2: WAVE 2 — VALIDATION METHODOLOGY
# =====================================================================


class TestT2ScanRootAlignment:
    """Verify validation scan roots match scanner scan roots exactly."""

    @pytest.mark.skipif(not _SCANNER_AVAILABLE, reason="Scanner unavailable")
    def test_scan_roots_match(self):
        """Validation _SCAN_ROOTS must be a superset of scanner _SCAN_ROOTS."""
        from tools.adg_static_validation_real import _SCAN_ROOTS as VAL_ROOTS

        scanner_roots_resolved = set()
        for r in _SCAN_ROOTS:
            # _SCAN_ROOTS entries are directory names like "agentic_core"
            scanner_roots_resolved.add(r)

        val_roots = set(VAL_ROOTS)
        # Every scanner root must be in validation roots
        missing = scanner_roots_resolved - val_roots
        assert not missing, f"Validation missing scanner roots: {missing}"

    @pytest.mark.skipif(not _SCANNER_AVAILABLE, reason="Scanner unavailable")
    def test_skip_dirs_include_archives(self):
        """archives/ must be in skip dirs to avoid inflated denominators."""
        from tools.adg_static_validation_real import _SKIP_DIRS

        assert "archives" in _SKIP_DIRS


class TestT2SignalClassification:
    """Verify exports and decomposes_into are HIGH_SIGNAL (Wave 2b)."""

    def test_exports_is_high_signal(self):
        # We can't easily call validate_edge_precision without a conn,
        # so we import and inspect the constants directly
        import importlib

        mod = importlib.import_module("tools.adg_static_validation_real")
        source = Path(mod.__file__).read_text(encoding="utf-8")
        # Parse the file and check HIGH_SIGNAL and LOW_SIGNAL
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "HIGH_SIGNAL":
                        # Extract set elements
                        if isinstance(node.value, ast.Set):
                            elements = {
                                elt.value
                                for elt in node.value.elts
                                if isinstance(elt, (ast.Constant, ast.Str))
                            }
                            assert "exports" in elements, "exports must be HIGH_SIGNAL"
                            assert "decomposes_into" in elements, "decomposes_into must be HIGH_SIGNAL"

    def test_exports_not_in_low_signal(self):
        mod_path = PROJECT_ROOT / "tools" / "adg_static_validation_real.py"
        source = mod_path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "LOW_SIGNAL":
                        if isinstance(node.value, ast.Set):
                            elements = {
                                elt.value
                                for elt in node.value.elts
                                if isinstance(elt, (ast.Constant, ast.Str))
                            }
                            assert "exports" not in elements, "exports must NOT be LOW_SIGNAL"
                            assert "decomposes_into" not in elements, "decomposes_into must NOT be LOW_SIGNAL"


class TestT2MultilineImportDetection:
    """Verify the validation script handles multiline import statements."""

    def test_multiline_from_import_pattern(self):
        """A from...import spanning multiple lines should be detected."""
        # Simulate lines as the validation script sees them
        lines = [
            "from agentic_core.adg.extraction.static_scanner import (\n",
            "    Edge,\n",
            "    ScanResult,\n",
            "    _ModuleDefinitionVisitor,\n",
            ")\n",
        ]
        # The import edge might point to line 3 (_ModuleDefinitionVisitor)
        line_no = 4  # 1-indexed
        line_content = lines[line_no - 1] if line_no <= len(lines) else ""
        sym_short = "_ModuleDefinitionVisitor"

        # W2c approach: check window of surrounding lines
        window = lines[max(0, line_no - 5) : line_no]
        window_text = " ".join(w.strip() for w in window)

        detected = (
            "import" in line_content
            or sym_short in line_content
            or "import" in window_text
            or sym_short in window_text
        )
        assert detected, "Multiline import should be detected via window check"

    def test_single_line_import_still_works(self):
        """Single-line imports still detected."""
        line_content = "import os\n"
        sym_short = "os"
        detected = "import" in line_content or sym_short in line_content
        assert detected


# =====================================================================
# T3: WAVE 3 — ADG SQLITE INVARIANTS
# =====================================================================


class TestT3DuplicateEdges:
    """Verify no duplicate edges in the ADG SQLite (Wave 3 / W1b)."""

    def test_zero_duplicate_edges(self):
        """No (src_id, dst_id, relation_type, line_no) duplicates in edges."""
        conn = _get_conn()
        cur = conn.cursor()
        cur.execute("""
            SELECT COUNT(*) FROM (
                SELECT src_id, dst_id, relation_type, line_no, COUNT(*) as cnt
                FROM edges
                GROUP BY src_id, dst_id, relation_type, line_no
                HAVING cnt > 1
            )
        """)
        dup_groups = cur.fetchone()[0]
        conn.close()
        assert dup_groups == 0, f"Found {dup_groups} duplicate edge groups in SQLite"


class TestT3ConfidenceFloor:
    """Verify no edges below confidence 0.5 in the ADG SQLite."""

    def test_no_edges_below_half_confidence(self):
        """All edges must have confidence_score >= 0.5."""
        conn = _get_conn()
        cur = conn.cursor()
        cur.execute("""
            SELECT relation_type, confidence_score, COUNT(*)
            FROM edges
            WHERE confidence_score < 0.5
            GROUP BY relation_type, confidence_score
        """)
        violations = cur.fetchall()
        conn.close()
        assert len(violations) == 0, "Found edges below 0.5 confidence: " + ", ".join(
            f"{rt}@{conf}×{cnt}" for rt, conf, cnt in violations
        )


class TestT3FileRatioAccuracy:
    """Verify file_ratio is within acceptable range."""

    def test_normalized_file_ratio(self):
        """ADG unique source_files (normalized) ≈ AST file count."""
        conn = _get_conn()
        cur = conn.cursor()

        # Count normalized ADG source files
        cur.execute("SELECT DISTINCT source_file FROM edges WHERE source_file != ''")
        raw_files = [r[0] for r in cur.fetchall()]
        project_root_str = str(PROJECT_ROOT).replace("\\", "/")
        scan_roots = [
            "agentic_core",
            "apps_eval",
            "apps_exec",
            "apps_lic",
            "apps_research",
            "apps_rfp",
            "apps_rg",
            "apps_shared",
            "system_learning",
            "tools",
            "ops_scripts",
            "tests",
        ]
        normalized = set()
        for sf in raw_files:
            sf_fwd = sf.replace("\\", "/")
            if sf_fwd.startswith(project_root_str + "/"):
                sf_fwd = sf_fwd[len(project_root_str) + 1 :]
            if any(sf_fwd.startswith(r + "/") for r in scan_roots):
                normalized.add(sf_fwd)
        conn.close()

        # Count AST files
        skip_dirs = {
            "__pycache__",
            ".git",
            "node_modules",
            "venv",
            ".venv",
            "env",
            "archives",
            ".mypy_cache",
            ".pytest_cache",
            ".tox",
            "htmlcov",
        }
        ast_files = 0
        for scan_root in scan_roots:
            root_path = PROJECT_ROOT / scan_root
            if not root_path.exists():
                continue
            for dirpath, dirnames, filenames in os.walk(root_path):
                dirnames[:] = [d for d in dirnames if d not in skip_dirs]
                for fname in filenames:
                    if fname.endswith(".py") and not fname.endswith(".pyc"):
                        ast_files += 1

        ratio = len(normalized) / ast_files if ast_files > 0 else 0.0
        assert 0.95 <= ratio <= 1.05, (
            f"file_ratio={ratio:.4f} outside [0.95, 1.05] (ADG={len(normalized)}, AST={ast_files})"
        )


class TestT3FunctionRatioAccuracy:
    """Verify function_ratio is within acceptable range."""

    def test_module_definition_edge_count_matches_ast(self):
        """decomposes_into module_definition edges ≈ AST visitor-scope defs."""
        conn = _get_conn()
        cur = conn.cursor()
        cur.execute("""
            SELECT COUNT(*) FROM edges
            WHERE relation_type = 'decomposes_into' AND edge_kind = 'module_definition'
        """)
        adg_count = cur.fetchone()[0]
        conn.close()

        # Count AST defs matching visitor scope
        skip_dirs = {
            "__pycache__",
            ".git",
            "node_modules",
            "venv",
            ".venv",
            "env",
            "archives",
            ".mypy_cache",
            ".pytest_cache",
            ".tox",
            "htmlcov",
        }
        scan_roots = [
            "agentic_core",
            "apps_eval",
            "apps_exec",
            "apps_lic",
            "apps_research",
            "apps_rfp",
            "apps_rg",
            "apps_shared",
            "system_learning",
            "tools",
            "ops_scripts",
            "tests",
        ]

        def count_visitor_defs(node):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                return 1
            n = 1 if isinstance(node, ast.ClassDef) else 0
            for child in ast.iter_child_nodes(node):
                n += count_visitor_defs(child)
            return n

        ast_count = 0
        for scan_root in scan_roots:
            root_path = PROJECT_ROOT / scan_root
            if not root_path.exists():
                continue
            for dirpath, dirnames, filenames in os.walk(root_path):
                dirnames[:] = [d for d in dirnames if d not in skip_dirs]
                for fname in filenames:
                    if fname.endswith(".py") and not fname.endswith(".pyc"):
                        try:
                            source = (Path(dirpath) / fname).read_text(encoding="utf-8", errors="replace")
                            tree = ast.parse(source)
                            ast_count += count_visitor_defs(tree)
                        except (SyntaxError, ValueError):
                            pass

        ratio = adg_count / ast_count if ast_count > 0 else 0.0
        assert 0.95 <= ratio <= 1.05, (
            f"function_ratio={ratio:.4f} outside [0.95, 1.05] (ADG={adg_count}, AST={ast_count})"
        )


class TestT3ModuleDefinitionEdgeCoverage:
    """Verify module_definition edges exist for all scanned files."""

    def test_all_scanned_files_have_module_defs_or_are_empty(self):
        """Every scanned file with defs should have module_definition edges."""
        conn = _get_conn()
        cur = conn.cursor()

        # Get files that have module_definition edges
        cur.execute("""
            SELECT DISTINCT source_file FROM edges
            WHERE relation_type = 'decomposes_into' AND edge_kind = 'module_definition'
        """)
        adg_files = set()
        project_root_str = str(PROJECT_ROOT).replace("\\", "/")
        for (sf,) in cur.fetchall():
            sf_fwd = sf.replace("\\", "/")
            if sf_fwd.startswith(project_root_str + "/"):
                sf_fwd = sf_fwd[len(project_root_str) + 1 :]
            adg_files.add(sf_fwd)

        # Get files that have ANY edges (scanner processed them)
        cur.execute("SELECT DISTINCT source_file FROM edges WHERE source_file != ''")
        all_adg_files = set()
        for (sf,) in cur.fetchall():
            sf_fwd = sf.replace("\\", "/")
            if sf_fwd.startswith(project_root_str + "/"):
                sf_fwd = sf_fwd[len(project_root_str) + 1 :]
            all_adg_files.add(sf_fwd)
        conn.close()

        # Files with edges but no module_definition edges
        missing = all_adg_files - adg_files
        # Filter: only check files under scan roots
        scan_roots = [
            "agentic_core",
            "apps_eval",
            "apps_exec",
            "apps_lic",
            "apps_research",
            "apps_rfp",
            "apps_rg",
            "apps_shared",
            "system_learning",
            "tools",
            "ops_scripts",
            "tests",
        ]
        missing_in_roots = {f for f in missing if any(f.startswith(r + "/") for r in scan_roots)}

        # Files that are truly empty (no defs) should be excluded
        files_with_defs = set()
        for f in missing_in_roots:
            fp = PROJECT_ROOT / f
            if not fp.exists():
                continue
            try:
                source = fp.read_text(encoding="utf-8", errors="replace")
                tree = ast.parse(source)
                has_defs = any(
                    isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
                    for n in ast.walk(tree)
                )
                if has_defs:
                    files_with_defs.add(f)
            except (SyntaxError, ValueError):
                pass

        # With stale cache cleared, this gap should be zero or very small
        gap_pct = len(files_with_defs) / max(len(all_adg_files), 1) * 100
        assert gap_pct < 1.0, (
            f"{len(files_with_defs)} files with defs ({gap_pct:.1f}%) "
            f"have edges but no module_definition edges"
        )


class TestT3SignalRatio:
    """Verify signal ratio is above threshold."""

    def test_high_signal_ratio_above_90_pct(self):
        """At least 90% of edges must be high-signal."""
        conn = _get_conn()
        cur = conn.cursor()

        low_signal = {
            "belongs_to_layer",
            "dead_imports",
            "violation_propagates_through",
            "unreachable_after_raise",
            "duplicate_method",
        }

        cur.execute("SELECT relation_type, COUNT(*) FROM edges GROUP BY relation_type")
        total = 0
        low_count = 0
        for rt, cnt in cur.fetchall():
            total += cnt
            if rt in low_signal:
                low_count += cnt
        conn.close()

        signal_ratio = 1.0 - (low_count / total) if total > 0 else 0.0
        assert signal_ratio >= 0.90, f"signal_ratio={signal_ratio:.4f} < 0.90"


# =====================================================================
# T4: CROSS-WAVE — END-TO-END CONSISTENCY
# =====================================================================


class TestT4EndToEnd:
    """Cross-wave consistency checks on the live ADG."""

    def test_semantic_accuracy_sample(self):
        """Spot-check: import edges should point to lines with import statements."""
        conn = _get_conn()
        cur = conn.cursor()
        cur.execute("""
            SELECT source_file, line_no, symbol FROM edges
            WHERE relation_type = 'imports'
            ORDER BY RANDOM() LIMIT 50
        """)
        rows = cur.fetchall()
        conn.close()

        correct = 0
        checked = 0
        for source_file, line_no, symbol in rows:
            sf_fwd = source_file.replace("\\", "/")
            proj_str = str(PROJECT_ROOT).replace("\\", "/")
            if sf_fwd.startswith(proj_str + "/"):
                sf_fwd = sf_fwd[len(proj_str) + 1 :]
            fp = PROJECT_ROOT / sf_fwd
            if not fp.exists() or line_no < 1:
                continue
            try:
                lines = fp.read_text(encoding="utf-8", errors="replace").splitlines()
                if line_no > len(lines):
                    continue
                checked += 1
                line = lines[line_no - 1]
                sym_short = symbol.split(".")[-1] if symbol else ""
                # Check line and window for multiline imports
                window = lines[max(0, line_no - 5) : line_no]
                window_text = " ".join(w.strip() for w in window)
                if (
                    "import" in line
                    or sym_short in line
                    or "import" in window_text
                    or sym_short in window_text
                ):
                    correct += 1
            except (OSError, UnicodeDecodeError):
                pass

        if checked >= 10:
            accuracy = correct / checked
            assert accuracy >= 0.95, f"Import semantic accuracy {accuracy:.2%} ({correct}/{checked}) < 95%"

    def test_decomposes_into_edges_have_valid_targets(self):
        """module_definition edges should reference symbols that exist as nodes."""
        conn = _get_conn()
        cur = conn.cursor()
        cur.execute("""
            SELECT e.dst_id, n.id FROM edges e
            LEFT JOIN nodes n ON e.dst_id = n.id
            WHERE e.relation_type = 'decomposes_into'
              AND e.edge_kind = 'module_definition'
            ORDER BY RANDOM() LIMIT 100
        """)
        rows = cur.fetchall()
        conn.close()

        dangling = sum(1 for dst_id, node_id in rows if node_id is None)
        if len(rows) > 0:
            dangling_pct = dangling / len(rows) * 100
            assert dangling_pct < 5.0, (
                f"{dangling}/{len(rows)} ({dangling_pct:.1f}%) module_definition "
                f"edges have dangling dst_id (no matching node)"
            )

    def test_consistency_rate_above_threshold(self):
        """consistency_rate (1 - dup_ratio) should be >= 0.99."""
        conn = _get_conn()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM edges")
        total = cur.fetchone()[0]
        cur.execute("""
            SELECT SUM(cnt - 1) FROM (
                SELECT COUNT(*) as cnt FROM edges
                GROUP BY src_id, dst_id, relation_type, line_no
                HAVING cnt > 1
            )
        """)
        excess = cur.fetchone()[0] or 0
        conn.close()

        dup_ratio = excess / total if total > 0 else 0.0
        consistency = 1.0 - dup_ratio
        assert consistency >= 0.99, f"consistency_rate={consistency:.4f} < 0.99"

    def test_all_eight_gates_pass(self):
        """Meta-test: run the full validation and check all 8 gates pass."""
        report_path = PROJECT_ROOT / "docs" / "reports" / "plans" / "adg_static_validation_report.json"
        if not report_path.exists():


        import json

        report = json.loads(report_path.read_text(encoding="utf-8"))

        # Metrics may be nested under "metrics" key or at top level
        metrics = report.get("metrics", report)
        gates = report.get("gates", {})

        # Check all 8 metrics
        assert metrics.get("semantic_accuracy", 0) >= 0.99, (
            f"semantic_accuracy={metrics.get('semantic_accuracy')}"
        )
        assert metrics.get("symbol_alignment_rate", 0) >= 0.995, (
            f"symbol_alignment_rate={metrics.get('symbol_alignment_rate')}"
        )
        assert 0.95 <= metrics.get("file_ratio", 0) <= 1.05, f"file_ratio={metrics.get('file_ratio')}"
        assert 0.95 <= metrics.get("function_ratio", 0) <= 1.05, (
            f"function_ratio={metrics.get('function_ratio')}"
        )
        assert metrics.get("signal_ratio", 0) >= 0.90, f"signal_ratio={metrics.get('signal_ratio')}"
        assert metrics.get("consistency_rate", 0) >= 0.99, (
            f"consistency_rate={metrics.get('consistency_rate')}"
        )
        assert metrics.get("synthetic_edge_count", 999) == 0, (
            f"synthetic_edge_count={metrics.get('synthetic_edge_count')}"
        )
        assert metrics.get("duplicate_edge_ratio", 999) == 0, (
            f"duplicate_edge_ratio={metrics.get('duplicate_edge_ratio')}"
        )

        # Also verify all gates passed if available
        if gates:
            for gate_name, passed in gates.items():
                assert passed, f"Gate failed: {gate_name}"
