"""Unit tests for agentic_core.adg.extraction.static_scanner.

Targets Wave-2 / Phase P5. Source: 2551 lines, fan_in=150 (L_TOOLS, impact 112.5).
Focused on the public dataclasses (Edge, ScanManifest, ScanResult) and digest
determinism — the core contract that downstream consumers rely on.
"""

from __future__ import annotations

import hashlib

from agentic_core.adg.extraction.static_scanner import (
    Edge,
    ScanManifest,
    ScanResult,
    _import_target_module_key,
    _is_scannable_static_path,
    _module_key_prefixes,
    _module_node_key,
    _propagate_violations,
)


class TestEdgeDataclass:
    """Edge is a frozen, sortable, total-order-keyed dataclass."""

    def test_minimal_construction(self) -> None:
        e = Edge(
            from_name="A",
            relation_type="imports",
            to_name="B",
            edge_kind="import",
            source_file="a.py",
            line_no=1,
        )
        assert e.from_name == "A"
        assert e.symbol == ""  # default
        assert e.semantic_type == ""
        assert e.confidence == 1.0

    def test_is_frozen(self) -> None:
        import pytest

        e = Edge("A", "imports", "B", "import", "a.py", 1)
        with pytest.raises(AttributeError):
            e.from_name = "C"  # type: ignore[misc]

    def test_hashable(self) -> None:
        e = Edge("A", "imports", "B", "import", "a.py", 1)
        s = {e, e}  # dedup in set
        assert len(s) == 1

    def test_equality_by_value(self) -> None:
        e1 = Edge("A", "imports", "B", "import", "a.py", 1)
        e2 = Edge("A", "imports", "B", "import", "a.py", 1)
        assert e1 == e2
        assert hash(e1) == hash(e2)

    def test_order_by_tuple(self) -> None:
        e1 = Edge("A", "imports", "B", "import", "a.py", 1)
        e2 = Edge("B", "imports", "C", "import", "b.py", 2)
        assert e1 < e2

    def test_default_span_values(self) -> None:
        e = Edge("A", "imports", "B", "import", "a.py", 1)
        assert e.source_span_start == 0
        assert e.target_span_end == 0
        assert e.dynamic_resolution == ""


class TestScanManifestDataclass:
    def test_defaults(self) -> None:
        m = ScanManifest()
        assert m.discovered_module_count == 0
        assert m.syntax_error_count == 0
        assert m.tests_included is False
        assert m.scan_mode == "full"
        assert m.edge_counts_by_graph == {}
        assert m.cardinality_violations == []

    def test_to_dict_roundtrip_shape(self) -> None:
        m = ScanManifest(discovered_module_count=5, parsed_module_count=5, tests_included=True)
        d = m.to_dict()
        assert d["discovered_module_count"] == 5
        assert d["tests_included"] is True
        # to_dict includes every dataclass field
        assert "scanner_version" in d
        assert "edge_counts_by_graph" in d

    def test_independent_default_factories(self) -> None:
        m1 = ScanManifest()
        m2 = ScanManifest()
        m1.edge_counts_by_graph["x"] = 1
        assert "x" not in m2.edge_counts_by_graph


class TestScanResultDataclass:
    """ScanResult aggregates the scanner run output."""

    def _sample_edges(self) -> list[Edge]:
        return [
            Edge("A", "imports", "B", "import", "a.py", 1),
            Edge("A", "imports", "C", "import", "a.py", 2),
            Edge("B", "calls", "C", "call", "b.py", 5),
        ]

    def test_empty_defaults(self) -> None:
        r = ScanResult()
        assert r.edges == []
        assert r.modules == []
        assert r.digest == ""
        assert isinstance(r.manifest, ScanManifest)

    def test_edge_counts_by_relation(self) -> None:
        r = ScanResult(edges=self._sample_edges())
        counts = r.edge_counts_by_relation()
        assert counts["imports"] == 2
        assert counts["calls"] == 1

    def test_canonical_edge_text_is_stable(self) -> None:
        r1 = ScanResult(edges=self._sample_edges())
        r2 = ScanResult(edges=self._sample_edges())
        assert r1.canonical_edge_text() == r2.canonical_edge_text()

    def test_canonical_edge_text_contains_all_fields(self) -> None:
        r = ScanResult(edges=[Edge("A", "imports", "B", "import", "a.py", 7, "sym")])
        text = r.canonical_edge_text()
        # pipe-delimited: from|rel|to|kind|file|line|symbol
        assert "A|imports|B|import|a.py|7|sym" == text

    def test_compute_digest_is_sha256_of_canonical_text(self) -> None:
        r = ScanResult(edges=self._sample_edges())
        digest = r.compute_digest()
        expected = hashlib.sha256(r.canonical_edge_text().encode("utf-8")).hexdigest()
        assert digest == expected
        assert r.digest == digest

    def test_compute_digest_deterministic_across_runs(self) -> None:
        d1 = ScanResult(edges=self._sample_edges()).compute_digest()
        d2 = ScanResult(edges=self._sample_edges()).compute_digest()
        assert d1 == d2

    def test_digest_changes_on_edge_change(self) -> None:
        r1 = ScanResult(edges=self._sample_edges())
        r2_edges = self._sample_edges()
        r2_edges.append(Edge("X", "imports", "Y", "import", "x.py", 9))
        r2 = ScanResult(edges=r2_edges)
        assert r1.compute_digest() != r2.compute_digest()

    def test_to_dict_roundtrip_via_from_dict(self) -> None:
        original = ScanResult(
            edges=self._sample_edges(),
            modules=["a", "b"],
            commit_sha="abc",
            repo_state_hash="hash-xyz",
        )
        original.compute_digest()
        d = original.to_dict()
        restored = ScanResult.from_dict(d)
        assert restored.modules == ["a", "b"]
        assert restored.commit_sha == "abc"
        assert restored.digest == original.digest
        assert len(restored.edges) == len(original.edges)
        # Edge equality via frozen dataclass __eq__
        assert restored.edges[0] == original.edges[0]

    def test_from_dict_tolerates_extra_fields(self) -> None:
        # Forward-compat: new cache fields shouldn't break deserialization
        d = {
            "edges": [],
            "modules": [],
            "digest": "",
            "commit_sha": "",
            "repo_state_hash": "",
            "manifest": {"scanner_version": "0", "future_field": 42},
            "syntax_errors": [],
            "type_surface_map": {},
            "hollow_file_map": {},
            "boilerplate_ratio_map": {},
        }
        result = ScanResult.from_dict(d)
        assert result.modules == []
        # future_field was discarded in the filter
        assert not hasattr(result.manifest, "future_field")

    def test_from_dict_with_missing_optional_fields(self) -> None:
        result = ScanResult.from_dict({"edges": [], "modules": []})
        assert result.digest == ""
        assert result.commit_sha == ""


class TestEdgeOrderConsistency:
    """Edge sort order must match canonical_edge_text serialization order."""

    def test_sorted_edges_produce_lexical_text(self) -> None:
        edges = [
            Edge("B", "imports", "C", "import", "b.py", 1),
            Edge("A", "imports", "B", "import", "a.py", 1),
            Edge("A", "imports", "A", "import", "a.py", 1),
        ]
        sorted_edges = sorted(edges)
        # After sort, the first edge's from_name should be "A" and to_name "A"
        assert sorted_edges[0].from_name == "A"
        assert sorted_edges[0].to_name == "A"
        assert sorted_edges[-1].from_name == "B"


class TestScannablePathExclusions:
    """The scanner should ignore generated junk trees while keeping source trees."""

    def test_excludes_archive_temp_and_venv_trees(self) -> None:
        assert not _is_scannable_static_path("tools/archive/old_helper.py", include_tests=False)
        assert not _is_scannable_static_path("tools/build/generated.py", include_tests=False)
        assert not _is_scannable_static_path("tools/dist/generated.py", include_tests=False)
        assert not _is_scannable_static_path("tools/.cache/generated.py", include_tests=False)
        assert not _is_scannable_static_path("tools/.venv/site-packages/x.py", include_tests=False)
        assert not _is_scannable_static_path("tools/tmp/work/x.py", include_tests=False)
        assert not _is_scannable_static_path("tools/temp/work/x.py", include_tests=False)
        assert not _is_scannable_static_path("tools/.tmp/work/x.py", include_tests=False)

    def test_keeps_real_source_cache_packages(self) -> None:
        assert _is_scannable_static_path("agentic_core/cache/cache_loader.py", include_tests=False)


class TestViolationPropagation:
    def test_module_key_helpers_normalize_symbols_modules_and_prefixes(self) -> None:
        assert (
            _import_target_module_key("ADG::Symbol::agentic_core.L5_safety.target::Thing")
            == "agentic_core/L5_safety/target"
        )
        assert _module_node_key("ADG::Module::agentic_core/L5_safety/target.py") == "agentic_core/L5_safety/target"
        assert _module_node_key("ADG::Module::apps_rg/__init__.py") == "apps_rg"
        assert _module_key_prefixes("agentic_core/L5_safety/target") == (
            "agentic_core",
            "agentic_core/L5_safety",
            "agentic_core/L5_safety/target",
        )

    def test_propagates_violation_through_symbol_import(self) -> None:
        violating_module = "ADG::Module::agentic_core/L5_safety/target.py"
        importing_module = "ADG::Module::agentic_core/L0_routing/entry.py"
        result = ScanResult(
            edges=[
                Edge(
                    violating_module,
                    "violates",
                    "layer_rule",
                    "violation",
                    "agentic_core/L5_safety/target.py",
                    1,
                ),
                Edge(
                    importing_module,
                    "imports",
                    "ADG::Symbol::agentic_core.L5_safety.target::Thing",
                    "import",
                    "agentic_core/L0_routing/entry.py",
                    2,
                ),
            ]
        )

        propagated = _propagate_violations(result)

        assert len(propagated) == 1
        assert propagated[0].from_name == violating_module
        assert propagated[0].to_name == importing_module
        assert propagated[0].relation_type == "violation_propagates_through"
        assert propagated[0].dynamic_resolution == "derived"
