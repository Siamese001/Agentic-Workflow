"""Tests for ADG P4 enhancements: E8 (Protocol/ABC Coverage), E10 (Schema Migration), E11 (Symbol Index).

All tests use synthetic ScanResult/edge fixtures — no filesystem access.
"""

from __future__ import annotations

from agentic_core.adg.analysis.protocol_coverage import (
    check_protocol_coverage,
)
from agentic_core.adg.analysis.schema_migration import (
    CURRENT_SCHEMA_VERSION,
    get_migration,
    list_migrations,
    migrate_scan_result_dict,
    register_migration,
)
from agentic_core.adg.analysis.symbol_index import SymbolIndex
from agentic_core.adg.extraction.static_scanner import Edge, ScanResult

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_module_adg(rel: str) -> str:
    return f"ADG::Module::{rel}"


def _make_implements_edge(from_class: str, to_base_sym: str, base_short: str) -> Edge:
    return Edge(
        from_name=from_class,
        relation_type="implements",
        to_name=f"ADG::Symbol::{to_base_sym}",
        edge_kind="resolved_internal",
        source_file="foo.py",
        line_no=1,
        symbol=base_short,
    )


def _make_exports_edge(module_rel: str, symbol: str) -> Edge:
    return Edge(
        from_name=_make_module_adg(module_rel),
        relation_type="exports",
        to_name=f"ADG::Symbol::{module_rel}::{symbol}",
        edge_kind="export",
        source_file=module_rel,
        line_no=1,
        symbol=symbol,
    )


def _scan_result(*edges: Edge) -> ScanResult:
    result = ScanResult()
    result.edges = sorted(set(edges))
    result.modules = []
    return result


# ===========================================================================
# E8: Protocol / ABC Coverage Check
# ===========================================================================


class TestProtocolCoverageCheck:
    """E8: verify abstract base detection and coverage reporting.

    Model:
      Pass 1: class C extends Protocol/ABC -> C is an abstract base.
      Pass 2: class D extends C (where C is abstract) -> C is covered.
    """

    def test_abstract_class_with_concrete_implementor_is_covered(self):
        """MyProtocol extends Protocol (abstract). ConcreteImpl extends MyProtocol (covered)."""
        my_protocol_adg = _make_module_adg("iface.py") + "::MyProtocol"
        concrete_adg = _make_module_adg("impl.py") + "::ConcreteImpl"
        e1 = Edge(
            from_name=my_protocol_adg,
            relation_type="implements",
            to_name="ADG::Symbol::Protocol",
            edge_kind="resolved_internal",
            source_file="iface.py",
            line_no=1,
            symbol="Protocol",
        )
        e2 = Edge(
            from_name=concrete_adg,
            relation_type="implements",
            to_name=my_protocol_adg,
            edge_kind="resolved_internal",
            source_file="impl.py",
            line_no=5,
            symbol="MyProtocol",
        )
        result = _scan_result(e1, e2)
        report = check_protocol_coverage(result)
        assert my_protocol_adg in report.abstract_bases
        assert my_protocol_adg in report.covered_bases
        assert my_protocol_adg not in report.uncovered_bases
        assert report.coverage_rate == 1.0

    def test_abstract_class_without_implementor_is_uncovered(self):
        """MyABC extends ABC, but nothing extends MyABC — uncovered."""
        my_abc_adg = _make_module_adg("base.py") + "::MyABC"
        e1 = Edge(
            from_name=my_abc_adg,
            relation_type="implements",
            to_name="ADG::Symbol::ABC",
            edge_kind="resolved_internal",
            source_file="base.py",
            line_no=1,
            symbol="ABC",
        )
        result = _scan_result(e1)
        report = check_protocol_coverage(result)
        assert my_abc_adg in report.abstract_bases
        assert my_abc_adg in report.uncovered_bases
        assert my_abc_adg not in report.covered_bases
        assert report.coverage_rate == 0.0

    def test_multiple_implementors_same_abstract_base(self):
        """Two concrete classes extend the same abstract base — it is covered once."""
        base_adg = _make_module_adg("iface.py") + "::IFace"
        declare = Edge(
            from_name=base_adg,
            relation_type="implements",
            to_name="ADG::Symbol::Protocol",
            edge_kind="resolved_internal",
            source_file="iface.py",
            line_no=1,
            symbol="Protocol",
        )
        impl_a = Edge(
            from_name=_make_module_adg("a.py") + "::ImplA",
            relation_type="implements",
            to_name=base_adg,
            edge_kind="resolved_internal",
            source_file="a.py",
            line_no=1,
            symbol="IFace",
        )
        impl_b = Edge(
            from_name=_make_module_adg("b.py") + "::ImplB",
            relation_type="implements",
            to_name=base_adg,
            edge_kind="resolved_internal",
            source_file="b.py",
            line_no=1,
            symbol="IFace",
        )
        result = _scan_result(declare, impl_a, impl_b)
        report = check_protocol_coverage(result)
        assert len(report.covered_bases) == 1
        assert len(report.uncovered_bases) == 0

    def test_no_implements_edges_full_coverage(self):
        result = _scan_result()
        report = check_protocol_coverage(result)
        assert report.abstract_bases == []
        assert report.coverage_rate == 1.0

    def test_non_abstract_base_not_counted(self):
        """A class extending a non-ABC/Protocol base is NOT tracked as abstract."""
        edge = Edge(
            from_name=_make_module_adg("a.py") + "::Child",
            relation_type="implements",
            to_name="ADG::Symbol::MyMixin",
            edge_kind="resolved_internal",
            source_file="a.py",
            line_no=1,
            symbol="MyMixin",
        )
        result = _scan_result(edge)
        report = check_protocol_coverage(result)
        assert len(report.abstract_bases) == 0

    def test_typing_protocol_detected(self):
        """typing.Protocol should be recognized as an abstract anchor."""
        my_iface_adg = _make_module_adg("iface.py") + "::MyInterface"
        e = Edge(
            from_name=my_iface_adg,
            relation_type="implements",
            to_name="ADG::Symbol::typing.Protocol",
            edge_kind="resolved_internal",
            source_file="iface.py",
            line_no=1,
            symbol="typing.Protocol",
        )
        result = _scan_result(e)
        report = check_protocol_coverage(result)
        assert my_iface_adg in report.abstract_bases

    def test_to_dict_structure(self):
        my_abc_adg = _make_module_adg("base.py") + "::MyABC"
        e = Edge(
            from_name=my_abc_adg,
            relation_type="implements",
            to_name="ADG::Symbol::ABC",
            edge_kind="resolved_internal",
            source_file="base.py",
            line_no=1,
            symbol="ABC",
        )
        report = check_protocol_coverage(_scan_result(e))
        d = report.to_dict()
        assert "abstract_count" in d
        assert "covered_count" in d
        assert "uncovered_count" in d
        assert "coverage_rate" in d
        assert "uncovered_bases" in d

    def test_coverage_rate_partial(self):
        """Two abstract bases: one covered, one not.

        IFaceCovered extends Protocol, and ConcreteImpl extends IFaceCovered.
        IFaceUncovered extends ABC, but nothing extends IFaceUncovered.
        """
        covered_adg = _make_module_adg("iface.py") + "::IFaceCovered"
        uncovered_adg = _make_module_adg("base.py") + "::IFaceUncovered"

        declare_covered = Edge(
            from_name=covered_adg,
            relation_type="implements",
            to_name="ADG::Symbol::Protocol",
            edge_kind="resolved_internal",
            source_file="iface.py",
            line_no=1,
            symbol="Protocol",
        )
        concrete_impl = Edge(
            from_name=_make_module_adg("impl.py") + "::Concrete",
            relation_type="implements",
            to_name=covered_adg,
            edge_kind="resolved_internal",
            source_file="impl.py",
            line_no=5,
            symbol="IFaceCovered",
        )
        declare_uncovered = Edge(
            from_name=uncovered_adg,
            relation_type="implements",
            to_name="ADG::Symbol::ABC",
            edge_kind="resolved_internal",
            source_file="base.py",
            line_no=1,
            symbol="ABC",
        )
        result = _scan_result(declare_covered, concrete_impl, declare_uncovered)
        report = check_protocol_coverage(result)
        assert len(report.abstract_bases) == 2
        assert len(report.covered_bases) == 1
        assert len(report.uncovered_bases) == 1
        assert 0.0 < report.coverage_rate < 1.0


# ===========================================================================
# E10: Schema Version Migration Guard
# ===========================================================================


class TestSchemaMigration:
    """E10: verify migration registration, application, and registry."""

    def test_builtin_migration_registered(self):
        migrations = list_migrations()
        assert ("0.9", "1.0") in migrations

    def test_0_9_to_1_0_adds_symbol_field(self):
        fn = get_migration("0.9", "1.0")
        assert fn is not None
        data = {
            "manifest": {"schema_version": "0.9"},
            "edges": [
                {
                    "from_name": "ADG::Module::a.py",
                    "relation_type": "imports",
                    "to_name": "ADG::Symbol::os",
                    "edge_kind": "import",
                    "source_file": "a.py",
                    "line_no": 1,
                }
            ],
        }
        result = fn(data)
        assert result["edges"][0]["symbol"] == ""

    def test_migrate_current_version_no_op(self):
        data = {
            "manifest": {"schema_version": CURRENT_SCHEMA_VERSION},
            "edges": [],
        }
        result = migrate_scan_result_dict(data)
        assert result is not data  # deepcopy
        assert result["manifest"]["schema_version"] == CURRENT_SCHEMA_VERSION

    def test_migrate_legacy_0_9_updates_version(self):
        data = {
            "manifest": {"schema_version": "0.9"},
            "edges": [],
        }
        result = migrate_scan_result_dict(data)
        assert result["manifest"]["schema_version"] == CURRENT_SCHEMA_VERSION

    def test_migrate_does_not_modify_original(self):
        data = {
            "manifest": {"schema_version": "0.9"},
            "edges": [{"from_name": "x", "symbol": "existing"}],
        }
        _ = migrate_scan_result_dict(data)
        assert data["edges"][0]["symbol"] == "existing"

    def test_register_custom_migration(self):
        @register_migration("test_from", "test_to")
        def my_migration(d: dict) -> dict:
            d["migrated"] = True
            return d

        fn = get_migration("test_from", "test_to")
        assert fn is not None
        result = fn({})
        assert result["migrated"] is True

    def test_missing_version_defaults_to_0_9(self):
        data = {"manifest": {}, "edges": [{"from_name": "x"}]}
        result = migrate_scan_result_dict(data)
        assert result["manifest"]["schema_version"] == CURRENT_SCHEMA_VERSION

    def test_get_missing_migration_returns_none(self):
        assert get_migration("99.0", "100.0") is None

    def test_current_schema_version_is_string(self):
        assert isinstance(CURRENT_SCHEMA_VERSION, str)
        assert len(CURRENT_SCHEMA_VERSION) > 0


# ===========================================================================
# E11: Cross-File Symbol Resolution Index
# ===========================================================================


class TestSymbolIndex:
    """E11: verify symbol index build, queries, and all_registry."""

    def test_build_from_exports_edges(self):
        result = _scan_result(
            _make_exports_edge("pkg/mod.py", "MyClass"),
            _make_exports_edge("pkg/mod.py", "helper_func"),
        )
        idx = SymbolIndex.build(result)
        assert idx.total_exports == 2

    def test_resolve_symbol_to_module(self):
        result = _scan_result(
            _make_exports_edge("pkg/mod.py", "MyClass"),
        )
        idx = SymbolIndex.build(result)
        resolved = idx.resolve("MyClass")
        assert resolved == _make_module_adg("pkg/mod.py")

    def test_resolve_unknown_symbol_returns_none(self):
        idx = SymbolIndex.build(_scan_result())
        assert idx.resolve("NonExistent") is None

    def test_exports_of_by_rel_path(self):
        result = _scan_result(
            _make_exports_edge("pkg/mod.py", "Alpha"),
            _make_exports_edge("pkg/mod.py", "Beta"),
        )
        idx = SymbolIndex.build(result)
        exports = idx.exports_of("pkg/mod.py")
        assert sorted(exports) == ["Alpha", "Beta"]

    def test_exports_of_by_adg_name(self):
        result = _scan_result(
            _make_exports_edge("pkg/mod.py", "Alpha"),
        )
        idx = SymbolIndex.build(result)
        exports = idx.exports_of("ADG::Module::pkg/mod.py")
        assert "Alpha" in exports

    def test_exports_of_unknown_module_returns_empty(self):
        idx = SymbolIndex.build(_scan_result())
        assert idx.exports_of("pkg/ghost.py") == []

    def test_build_all_registry_dotted_path(self):
        result = _scan_result(
            _make_exports_edge("pkg/utils.py", "parse"),
            _make_exports_edge("pkg/utils.py", "format_output"),
        )
        idx = SymbolIndex.build(result)
        registry = idx.build_all_registry()
        assert "pkg.utils" in registry
        assert sorted(registry["pkg.utils"]) == ["format_output", "parse"]

    def test_all_registry_strips_py_extension(self):
        result = _scan_result(
            _make_exports_edge("helpers.py", "helper"),
        )
        idx = SymbolIndex.build(result)
        registry = idx.build_all_registry()
        assert "helpers" in registry
        assert ".py" not in "helpers"

    def test_all_registry_strips_init(self):
        result = _scan_result(
            _make_exports_edge("pkg/__init__.py", "pkg_func"),
        )
        idx = SymbolIndex.build(result)
        registry = idx.build_all_registry()
        assert "pkg" in registry

    def test_non_exports_edges_ignored(self):
        result = _scan_result(
            Edge(
                from_name=_make_module_adg("a.py"),
                relation_type="imports",
                to_name="ADG::Symbol::os",
                edge_kind="import",
                source_file="a.py",
                line_no=1,
                symbol="os",
            ),
        )
        idx = SymbolIndex.build(result)
        assert idx.total_exports == 0
        assert idx.resolve("os") is None

    def test_stats_dict(self):
        result = _scan_result(
            _make_exports_edge("a.py", "func_a"),
            _make_exports_edge("b.py", "func_b"),
        )
        idx = SymbolIndex.build(result)
        stats = idx.stats()
        assert stats["total_exports"] == 2
        assert stats["unique_symbols"] == 2
        assert stats["modules_with_exports"] == 2

    def test_empty_result_empty_index(self):
        idx = SymbolIndex.build(_scan_result())
        assert idx.total_exports == 0
        assert idx.symbol_to_module == {}
        assert idx.module_to_symbols == {}

    def test_multiple_modules_different_symbols(self):
        result = _scan_result(
            _make_exports_edge("mod_a.py", "ClassA"),
            _make_exports_edge("mod_b.py", "ClassB"),
        )
        idx = SymbolIndex.build(result)
        assert idx.resolve("ClassA") == _make_module_adg("mod_a.py")
        assert idx.resolve("ClassB") == _make_module_adg("mod_b.py")

    def test_exports_sorted_in_module_to_symbols(self):
        result = _scan_result(
            _make_exports_edge("mod.py", "Zebra"),
            _make_exports_edge("mod.py", "Apple"),
            _make_exports_edge("mod.py", "Mango"),
        )
        idx = SymbolIndex.build(result)
        exports = idx.exports_of("mod.py")
        assert exports == sorted(exports)

    def test_all_registry_multiple_modules(self):
        result = _scan_result(
            _make_exports_edge("pkg/a.py", "foo"),
            _make_exports_edge("pkg/b.py", "bar"),
        )
        idx = SymbolIndex.build(result)
        registry = idx.build_all_registry()
        assert "pkg.a" in registry
        assert "pkg.b" in registry
