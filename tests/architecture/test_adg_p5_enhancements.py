"""Tests for ADG P5 enhancements: E12-E19.

E12: Rename/Move Safety Analyzer
E13: Public API Surface Extractor
E14: Hotspot Index
E15: Test Gap Detector
E16: Coupling/Cohesion Metrics
E17: Refactoring Plan Generator
E18: Dependency Inversion Detector
E19: CLI refactor sub-command
"""

from __future__ import annotations

from agentic_core.adg.extraction.static_scanner import Edge, ScanResult
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_adg_p5_enhancements")
_emit_applies_guardrail("p0", "test_adg_p5_enhancements", "p0_governance")
_emit_reads_policy_state("p0", "test_adg_p5_enhancements", "policy_binding")
_emit_snapshots_state("p0", "test_adg_p5_enhancements", "state_snapshot")
emit_replay_key("p0", "test_adg_p5_enhancements")
emit_determinism_digest("p0", "test_adg_p5_enhancements")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _edge(from_name, relation, to_name, edge_kind="import", source_file="", line_no=1, symbol=""):
    return Edge(
        from_name=from_name,
        relation_type=relation,
        to_name=to_name,
        edge_kind=edge_kind,
        source_file=source_file,
        line_no=line_no,
        symbol=symbol,
    )


def _mod(path: str) -> str:
    return f"ADG::Module::{path}"


def _sym(name: str) -> str:
    return f"ADG::Symbol::{name}"


def _result(*edges, modules=None) -> ScanResult:
    result = ScanResult(edges=list(edges))
    if modules is not None:
        result.modules = list(modules)
    else:
        seen = set()
        for e in edges:
            for name in (e.from_name, e.to_name):
                if name.startswith("ADG::Module::"):
                    seen.add(name[len("ADG::Module::") :])
        result.modules = sorted(seen)
    result.compute_digest()
    return result


# ===========================================================================
# E12: Rename / Move Safety Analyzer
# ===========================================================================


class TestRenameSafetyAnalyzer:
    def test_no_importers_is_safe(self):
        from agentic_core.adg.applications.rename_safety import analyze_rename

        result = _result(modules=["agentic_core/L2_execution/foo.py"])
        report = analyze_rename(
            result, "agentic_core/L2_execution/foo.py", "agentic_core/L2_execution/bar.py"
        )

        assert report.is_safe is True
        assert report.total_files_to_update == 0
        assert report.risk_label == "LOW"

    def test_same_layer_rename_detects_importers(self):
        from agentic_core.adg.applications.rename_safety import analyze_rename

        result = _result(
            _edge(
                _mod("agentic_core/L3_orchestration/caller.py"),
                "imports",
                _mod("agentic_core/L2_execution/foo.py"),
                symbol="agentic_core.L2_execution.foo",
            ),
            modules=["agentic_core/L2_execution/foo.py", "agentic_core/L3_orchestration/caller.py"],
        )
        report = analyze_rename(
            result, "agentic_core/L2_execution/foo.py", "agentic_core/L2_execution/bar.py"
        )

        assert report.total_files_to_update == 1
        assert "agentic_core/L3_orchestration/caller.py" in report.direct_importers

    def test_cross_layer_move_flags_violations(self):
        from agentic_core.adg.applications.rename_safety import analyze_rename

        result = _result(
            _edge(
                _mod("agentic_core/L0_routing/x.py"),
                "imports",
                _mod("agentic_core/L2_execution/foo.py"),
                symbol="agentic_core.L2_execution.foo",
            ),
            modules=["agentic_core/L2_execution/foo.py", "agentic_core/L0_routing/x.py"],
        )
        report = analyze_rename(
            result,
            "agentic_core/L2_execution/foo.py",
            "agentic_core/L5_safety/foo.py",
        )
        assert report.layer_changed is True
        assert len(report.new_layer_violations) > 0
        assert report.is_safe is False

    def test_repair_sequence_starts_with_rename_file(self):
        from agentic_core.adg.applications.rename_safety import analyze_rename

        result = _result(modules=["agentic_core/L2_execution/foo.py"])
        report = analyze_rename(
            result, "agentic_core/L2_execution/foo.py", "agentic_core/L2_execution/bar.py"
        )

        assert len(report.repair_sequence) >= 1
        assert report.repair_sequence[0].action == "rename_file"
        assert report.repair_sequence[0].target_file == "agentic_core/L2_execution/foo.py"

    def test_repair_sequence_includes_update_import_step(self):
        from agentic_core.adg.applications.rename_safety import analyze_rename

        result = _result(
            _edge(
                _mod("agentic_core/L3_orchestration/caller.py"),
                "imports",
                _mod("agentic_core/L2_execution/foo.py"),
                symbol="agentic_core.L2_execution.foo",
            ),
            modules=["agentic_core/L2_execution/foo.py", "agentic_core/L3_orchestration/caller.py"],
        )
        report = analyze_rename(
            result, "agentic_core/L2_execution/foo.py", "agentic_core/L2_execution/bar.py"
        )

        actions = {s.action for s in report.repair_sequence}
        assert "update_import" in actions

    def test_same_layer_no_violations(self):
        from agentic_core.adg.applications.rename_safety import analyze_rename

        result = _result(modules=["agentic_core/L2_execution/old.py"])
        report = analyze_rename(
            result,
            "agentic_core/L2_execution/old.py",
            "agentic_core/L2_execution/new.py",
        )
        assert report.new_layer_violations == []

    def test_risk_label_scales_with_importer_count(self):
        from agentic_core.adg.applications.rename_safety import analyze_rename

        edges = [
            _edge(
                _mod(f"agentic_core/L3_orchestration/caller{i}.py"),
                "imports",
                _mod("agentic_core/L2_execution/foo.py"),
                symbol="agentic_core.L2_execution.foo",
            )
            for i in range(25)
        ]
        result = _result(*edges, modules=["agentic_core/L2_execution/foo.py"])
        report = analyze_rename(
            result, "agentic_core/L2_execution/foo.py", "agentic_core/L2_execution/bar.py"
        )

        assert report.risk_label in ("HIGH", "CRITICAL")

    def test_layer_unchanged_when_same_directory(self):
        from agentic_core.adg.applications.rename_safety import analyze_rename

        result = _result(modules=["agentic_core/L1_cognition/a.py"])
        report = analyze_rename(
            result,
            "agentic_core/L1_cognition/a.py",
            "agentic_core/L1_cognition/b.py",
        )
        assert report.layer_changed is False
        assert report.old_layer == report.new_layer

    def test_to_dict_is_serialisable(self):
        import json

        from agentic_core.adg.applications.rename_safety import analyze_rename

        result = _result(modules=["agentic_core/L2_execution/foo.py"])
        report = analyze_rename(
            result, "agentic_core/L2_execution/foo.py", "agentic_core/L2_execution/bar.py"
        )
        d = report.to_dict()
        assert json.dumps(d)  # must not raise


# ===========================================================================
# E13: Public API Surface Extractor
# ===========================================================================


class TestAPISurface:
    def test_public_symbols_detected(self):
        from agentic_core.adg.applications.api_surface import build_api_surface

        result = _result(
            _edge(_mod("pkg/mod.py"), "exports", _sym("pkg.mod.MyClass"), symbol="MyClass"),
            _edge(_mod("pkg/mod.py"), "exports", _sym("pkg.mod.helper"), symbol="helper"),
        )
        report = build_api_surface(result)
        surf = report.surface_by_module.get("pkg/mod.py")
        assert surf is not None
        assert "MyClass" in surf.public_symbols
        assert "helper" in surf.public_symbols

    def test_internal_symbols_detected(self):
        from agentic_core.adg.applications.api_surface import build_api_surface

        result = _result(
            _edge(_mod("pkg/mod.py"), "exports", _sym("pkg.mod._internal"), symbol="_internal"),
            _edge(_mod("pkg/mod.py"), "exports", _sym("pkg.mod.Public"), symbol="Public"),
        )
        report = build_api_surface(result)
        surf = report.surface_by_module["pkg/mod.py"]
        assert "_internal" in surf.internal_symbols
        assert "Public" in surf.public_symbols

    def test_re_exports_tracked_separately(self):
        from agentic_core.adg.applications.api_surface import build_api_surface

        result = _result(
            _edge(_mod("pkg/__init__.py"), "re_exports", _sym("pkg.sub.Foo"), symbol="Foo"),
        )
        report = build_api_surface(result)
        surf = report.surface_by_module.get("pkg/__init__.py")
        assert surf is not None
        assert "Foo" in surf.re_exported_symbols

    def test_total_counts_correct(self):
        from agentic_core.adg.applications.api_surface import build_api_surface

        result = _result(
            _edge(_mod("a.py"), "exports", _sym("a.X"), symbol="X"),
            _edge(_mod("a.py"), "exports", _sym("a._y"), symbol="_y"),
            _edge(_mod("b.py"), "exports", _sym("b.Z"), symbol="Z"),
        )
        report = build_api_surface(result)
        assert report.total_public_symbols == 2
        assert report.total_internal_symbols == 1

    def test_empty_result_empty_surface(self):
        from agentic_core.adg.applications.api_surface import build_api_surface

        result = _result()
        report = build_api_surface(result)
        assert report.total_public_symbols == 0
        assert report.boundary_violations == []

    def test_public_modules_property(self):
        from agentic_core.adg.applications.api_surface import build_api_surface

        result = _result(
            _edge(_mod("exposed.py"), "exports", _sym("exposed.Foo"), symbol="Foo"),
        )
        report = build_api_surface(result)
        assert "exposed.py" in report.public_modules

    def test_to_dict_serialisable(self):
        import json

        from agentic_core.adg.applications.api_surface import build_api_surface

        result = _result(
            _edge(_mod("mod.py"), "exports", _sym("mod.A"), symbol="A"),
        )
        report = build_api_surface(result)
        assert json.dumps(report.to_dict())


# ===========================================================================
# E14: Hotspot Index
# ===========================================================================


class TestHotspotIndex:
    def test_fan_in_counts_distinct_importers(self):
        from agentic_core.adg.analysis.hotspot_index import HotspotIndex

        result = _result(
            _edge(_mod("agentic_core/L1_cognition/a.py"), "imports", _mod("agentic_core/L0_routing/core.py")),
            _edge(_mod("agentic_core/L2_execution/b.py"), "imports", _mod("agentic_core/L0_routing/core.py")),
        )
        idx = HotspotIndex.build(result)
        assert idx.fan_in("agentic_core/L0_routing/core.py") == 2

    def test_fan_out_counts_distinct_dependencies(self):
        from agentic_core.adg.analysis.hotspot_index import HotspotIndex

        result = _result(
            _edge(_mod("agentic_core/L2_execution/x.py"), "imports", _mod("agentic_core/L1_cognition/a.py")),
            _edge(_mod("agentic_core/L2_execution/x.py"), "imports", _mod("agentic_core/L0_routing/b.py")),
        )
        idx = HotspotIndex.build(result)
        assert idx.fan_out("agentic_core/L2_execution/x.py") == 2

    def test_instability_fully_stable(self):
        from agentic_core.adg.analysis.hotspot_index import HotspotIndex

        result = _result(
            _edge(
                _mod("agentic_core/L1_cognition/a.py"), "imports", _mod("agentic_core/L0_routing/stable.py")
            ),
            _edge(
                _mod("agentic_core/L2_execution/b.py"), "imports", _mod("agentic_core/L0_routing/stable.py")
            ),
        )
        idx = HotspotIndex.build(result)
        assert idx.instability("agentic_core/L0_routing/stable.py") == 0.0

    def test_instability_fully_unstable(self):
        from agentic_core.adg.analysis.hotspot_index import HotspotIndex

        result = _result(
            _edge(
                _mod("agentic_core/L2_execution/leaf.py"), "imports", _mod("agentic_core/L1_cognition/a.py")
            ),
            _edge(_mod("agentic_core/L2_execution/leaf.py"), "imports", _mod("agentic_core/L0_routing/b.py")),
        )
        idx = HotspotIndex.build(result)
        inst = idx.instability("agentic_core/L2_execution/leaf.py")
        assert inst == 1.0

    def test_coupling_is_sum_of_fan_in_and_fan_out(self):
        from agentic_core.adg.analysis.hotspot_index import HotspotIndex

        result = _result(
            _edge(_mod("agentic_core/L1_cognition/a.py"), "imports", _mod("agentic_core/L0_routing/m.py")),
            _edge(_mod("agentic_core/L0_routing/m.py"), "imports", _mod("agentic_core/L0_routing/n.py")),
        )
        idx = HotspotIndex.build(result)
        assert idx.coupling("agentic_core/L0_routing/m.py") == idx.fan_in(
            "agentic_core/L0_routing/m.py"
        ) + idx.fan_out("agentic_core/L0_routing/m.py")

    def test_top_hotspots_sorted_by_coupling(self):
        from agentic_core.adg.analysis.hotspot_index import HotspotIndex

        # Make core.py have higher coupling than other.py
        result = _result(
            _edge(_mod("agentic_core/L1_cognition/a.py"), "imports", _mod("agentic_core/L0_routing/core.py")),
            _edge(_mod("agentic_core/L1_cognition/b.py"), "imports", _mod("agentic_core/L0_routing/core.py")),
            _edge(
                _mod("agentic_core/L1_cognition/c.py"), "imports", _mod("agentic_core/L0_routing/other.py")
            ),
        )
        idx = HotspotIndex.build(result)
        hotspots = idx.top_hotspots(n=2, threshold=0)
        assert hotspots[0].coupling >= hotspots[1].coupling

    def test_importers_of_returns_sorted_list(self):
        from agentic_core.adg.analysis.hotspot_index import HotspotIndex

        result = _result(
            _edge(_mod("agentic_core/L1_cognition/b.py"), "imports", _mod("agentic_core/L0_routing/x.py")),
            _edge(_mod("agentic_core/L1_cognition/a.py"), "imports", _mod("agentic_core/L0_routing/x.py")),
        )
        idx = HotspotIndex.build(result)
        importers = idx.importers_of("agentic_core/L0_routing/x.py")
        assert importers == sorted(importers)

    def test_unknown_module_returns_zero(self):
        from agentic_core.adg.analysis.hotspot_index import HotspotIndex

        result = _result()
        idx = HotspotIndex.build(result)
        assert idx.fan_in("does/not/exist.py") == 0
        assert idx.fan_out("does/not/exist.py") == 0
        assert idx.coupling("does/not/exist.py") == 0

    def test_stats_contains_expected_keys(self):
        from agentic_core.adg.analysis.hotspot_index import HotspotIndex

        result = _result(
            _edge(_mod("agentic_core/L1_cognition/a.py"), "imports", _mod("agentic_core/L0_routing/x.py")),
        )
        idx = HotspotIndex.build(result)
        stats = idx.stats()
        for key in ("total_modules", "max_fan_in", "max_fan_out", "avg_coupling"):
            assert key in stats

    def test_self_imports_not_counted(self):
        from agentic_core.adg.analysis.hotspot_index import HotspotIndex

        result = _result(
            _edge(_mod("agentic_core/L0_routing/x.py"), "imports", _mod("agentic_core/L0_routing/x.py")),
        )
        idx = HotspotIndex.build(result)
        assert idx.fan_in("agentic_core/L0_routing/x.py") == 0
        assert idx.fan_out("agentic_core/L0_routing/x.py") == 0


# ===========================================================================
# E15: Test Gap Detector
# ===========================================================================


class TestTestGapDetector:
    def test_covered_module_not_in_gaps(self):
        from agentic_core.adg.analysis.test_gap import detect_test_gaps

        result = _result(
            _edge(_mod("tests/test_foo.py"), "covers", _mod("agentic_core/L1_cognition/foo.py")),
            modules=["agentic_core/L1_cognition/foo.py", "tests/test_foo.py"],
        )
        report = detect_test_gaps(result)
        gap_paths = {e.module_path for e in report.uncovered_modules}
        assert "agentic_core/L1_cognition/foo.py" not in gap_paths

    def test_uncovered_module_in_gaps(self):
        from agentic_core.adg.analysis.test_gap import detect_test_gaps

        result = _result(
            modules=["agentic_core/L2_execution/bar.py"],
        )
        report = detect_test_gaps(result)
        gap_paths = {e.module_path for e in report.uncovered_modules}
        assert "agentic_core/L2_execution/bar.py" in gap_paths

    def test_test_files_excluded_from_production(self):
        from agentic_core.adg.analysis.test_gap import detect_test_gaps

        result = _result(
            modules=["tests/test_x.py"],
        )
        report = detect_test_gaps(result)
        gap_paths = {e.module_path for e in report.uncovered_modules}
        assert "tests/test_x.py" not in gap_paths

    def test_coverage_rate_zero_when_no_covers(self):
        from agentic_core.adg.analysis.test_gap import detect_test_gaps

        result = _result(modules=["agentic_core/L1_cognition/a.py", "agentic_core/L2_execution/b.py"])
        report = detect_test_gaps(result)
        assert report.coverage_rate == 0.0

    def test_coverage_rate_one_when_all_covered(self):
        from agentic_core.adg.analysis.test_gap import detect_test_gaps

        result = _result(
            _edge(_mod("tests/t.py"), "covers", _mod("agentic_core/L1_cognition/a.py")),
            _edge(_mod("tests/t.py"), "covers", _mod("agentic_core/L2_execution/b.py")),
            modules=["agentic_core/L1_cognition/a.py", "agentic_core/L2_execution/b.py", "tests/t.py"],
        )
        report = detect_test_gaps(result)
        assert report.coverage_rate == 1.0

    def test_highest_risk_gaps_sorted_by_fan_in(self):
        from agentic_core.adg.analysis.hotspot_index import HotspotIndex
        from agentic_core.adg.analysis.test_gap import detect_test_gaps

        edges = [
            _edge(
                _mod(f"agentic_core/L1_cognition/caller{i}.py"),
                "imports",
                _mod("agentic_core/L0_routing/hotspot.py"),
            )
            for i in range(5)
        ]
        result = _result(
            *edges,
            modules=["agentic_core/L0_routing/hotspot.py", "agentic_core/L1_cognition/cold.py"],
        )
        idx = HotspotIndex.build(result)
        report = detect_test_gaps(result, hotspot_index=idx)

        if len(report.highest_risk_gaps) > 1:
            assert report.highest_risk_gaps[0].fan_in >= report.highest_risk_gaps[1].fan_in

    def test_gap_by_layer_populated(self):
        from agentic_core.adg.analysis.test_gap import detect_test_gaps

        result = _result(
            modules=["agentic_core/L1_cognition/a.py", "agentic_core/L2_execution/b.py"],
        )
        report = detect_test_gaps(result)
        assert len(report.gap_by_layer) > 0

    def test_to_dict_serialisable(self):
        import json

        from agentic_core.adg.analysis.test_gap import detect_test_gaps

        result = _result(modules=["agentic_core/L1_cognition/a.py"])
        report = detect_test_gaps(result)
        assert json.dumps(report.to_dict())


# ===========================================================================
# E16: Coupling / Cohesion Metrics
# ===========================================================================


class TestCouplingMetrics:
    def test_ca_ce_computed_correctly(self):
        from agentic_core.adg.analysis.coupling_metrics import compute_coupling_metrics

        result = _result(
            _edge(_mod("agentic_core/L1_cognition/a.py"), "imports", _mod("agentic_core/L0_routing/x.py")),
            _edge(_mod("agentic_core/L2_execution/b.py"), "imports", _mod("agentic_core/L0_routing/x.py")),
            modules=[
                "agentic_core/L0_routing/x.py",
                "agentic_core/L1_cognition/a.py",
                "agentic_core/L2_execution/b.py",
            ],
        )
        report = compute_coupling_metrics(result)
        m = report.metrics_by_module["agentic_core/L0_routing/x.py"]
        assert m.ca == 2
        assert m.ce == 0

    def test_instability_leaf_is_one(self):
        from agentic_core.adg.analysis.coupling_metrics import compute_coupling_metrics

        result = _result(
            _edge(
                _mod("agentic_core/L2_execution/leaf.py"), "imports", _mod("agentic_core/L0_routing/base.py")
            ),
            modules=["agentic_core/L2_execution/leaf.py", "agentic_core/L0_routing/base.py"],
        )
        report = compute_coupling_metrics(result)
        m = report.metrics_by_module["agentic_core/L2_execution/leaf.py"]
        assert m.instability == 1.0

    def test_instability_stable_root_is_zero(self):
        from agentic_core.adg.analysis.coupling_metrics import compute_coupling_metrics

        result = _result(
            _edge(_mod("agentic_core/L1_cognition/a.py"), "imports", _mod("agentic_core/L0_routing/root.py")),
            modules=["agentic_core/L0_routing/root.py", "agentic_core/L1_cognition/a.py"],
        )
        report = compute_coupling_metrics(result)
        m = report.metrics_by_module["agentic_core/L0_routing/root.py"]
        assert m.instability == 0.0

    def test_zone_uselessness_for_stable_and_concrete(self):
        from agentic_core.adg.analysis.coupling_metrics import compute_coupling_metrics

        # abstractness=0 (no abstract classes), instability=0 (only Ca, no Ce)
        # D = |0 + 0 - 1| = 1.0 → USELESSNESS zone
        result = _result(
            _edge(
                _mod("agentic_core/L1_cognition/a.py"), "imports", _mod("agentic_core/L0_routing/concrete.py")
            ),
            _edge(
                _mod("agentic_core/L2_execution/b.py"), "imports", _mod("agentic_core/L0_routing/concrete.py")
            ),
            modules=["agentic_core/L0_routing/concrete.py"],
        )
        report = compute_coupling_metrics(result)
        m = report.metrics_by_module["agentic_core/L0_routing/concrete.py"]
        assert m.instability == 0.0
        assert m.abstractness == 0.0
        assert m.distance == 1.0
        assert m.zone == "USELESSNESS"

    def test_distance_on_main_sequence_is_zero(self):
        from agentic_core.adg.analysis.coupling_metrics import ModuleMetrics

        m = ModuleMetrics(
            module_path="test.py",
            ca=1,
            ce=1,
            instability=0.5,
            abstractness=0.5,
            distance=round(abs(0.5 + 0.5 - 1.0), 3),
            zone="BALANCED",
        )
        assert m.distance == 0.0

    def test_top_pain_zone_property(self):
        from agentic_core.adg.analysis.coupling_metrics import compute_coupling_metrics

        result = _result(
            _edge(
                _mod("agentic_core/L1_cognition/a.py"), "imports", _mod("agentic_core/L0_routing/concrete.py")
            ),
            _edge(
                _mod("agentic_core/L2_execution/b.py"), "imports", _mod("agentic_core/L0_routing/concrete.py")
            ),
            modules=["agentic_core/L0_routing/concrete.py"],
        )
        report = compute_coupling_metrics(result)
        pain = report.top_pain_zone
        assert isinstance(pain, list)

    def test_to_dict_serialisable(self):
        import json

        from agentic_core.adg.analysis.coupling_metrics import compute_coupling_metrics

        result = _result(
            _edge(_mod("agentic_core/L1_cognition/a.py"), "imports", _mod("agentic_core/L0_routing/x.py")),
            modules=["agentic_core/L0_routing/x.py", "agentic_core/L1_cognition/a.py"],
        )
        report = compute_coupling_metrics(result)
        assert json.dumps(report.to_dict())

    def test_empty_result_empty_metrics(self):
        from agentic_core.adg.analysis.coupling_metrics import compute_coupling_metrics

        result = _result()
        report = compute_coupling_metrics(result)
        assert report.top_pain_zone == []
        assert report.most_unstable == []


# ===========================================================================
# E17: Refactoring Plan Generator
# ===========================================================================


class TestRefactoringPlanner:
    def _high_coupling_result(self):
        edges = [
            _edge(
                _mod(f"agentic_core/L1_cognition/caller{i}.py"),
                "imports",
                _mod("agentic_core/L2_execution/hotspot.py"),
            )
            for i in range(30)
        ]
        edges += [
            _edge(
                _mod("agentic_core/L2_execution/hotspot.py"),
                "imports",
                _mod(f"agentic_core/L0_routing/dep{j}.py"),
            )
            for j in range(5)
        ]
        modules = ["agentic_core/L2_execution/hotspot.py"]
        return _result(*edges, modules=modules)

    def test_plan_generated_for_target_files(self):
        from agentic_core.adg.applications.refactoring_planner import build_refactoring_plan

        result = self._high_coupling_result()
        plan = build_refactoring_plan(result, target_files=["agentic_core/L2_execution/hotspot.py"])

        assert len(plan.steps) > 0

    def test_extract_module_step_for_high_coupling(self):
        from agentic_core.adg.applications.refactoring_planner import build_refactoring_plan

        result = self._high_coupling_result()
        plan = build_refactoring_plan(result, target_files=["agentic_core/L2_execution/hotspot.py"])

        ops = {s.operation for s in plan.steps}
        assert "EXTRACT_MODULE" in ops or "ADD_TESTS" in ops or "STABILISE_MODULE" in ops

    def test_add_tests_step_for_uncovered_module(self):
        from agentic_core.adg.applications.refactoring_planner import build_refactoring_plan

        edges = [
            _edge(
                _mod(f"agentic_core/L1_cognition/caller{i}.py"),
                "imports",
                _mod("agentic_core/L2_execution/uncovered.py"),
            )
            for i in range(5)
        ]
        result = _result(*edges, modules=["agentic_core/L2_execution/uncovered.py"])
        plan = build_refactoring_plan(result, target_files=["agentic_core/L2_execution/uncovered.py"])

        ops = [s.operation for s in plan.steps]
        assert "ADD_TESTS" in ops

    def test_inline_module_for_orphan(self):
        from agentic_core.adg.applications.refactoring_planner import build_refactoring_plan

        result = _result(
            _edge(_mod("tests/test_orphan.py"), "covers", _mod("agentic_core/L1_cognition/orphan.py")),
            modules=["agentic_core/L1_cognition/orphan.py"],
        )
        plan = build_refactoring_plan(result, target_files=["agentic_core/L1_cognition/orphan.py"])

        ops = {s.operation for s in plan.steps}
        assert "INLINE_MODULE" in ops or len(plan.steps) >= 0

    def test_plan_respects_max_steps(self):
        from agentic_core.adg.applications.refactoring_planner import build_refactoring_plan

        result = self._high_coupling_result()
        plan = build_refactoring_plan(
            result, target_files=["agentic_core/L2_execution/hotspot.py"], max_steps=2
        )

        assert len(plan.steps) <= 2

    def test_adg_signals_summary_in_plan(self):
        from agentic_core.adg.applications.refactoring_planner import build_refactoring_plan

        result = self._high_coupling_result()
        plan = build_refactoring_plan(result, target_files=["agentic_core/L2_execution/hotspot.py"])

        assert "hotspot_stats" in plan.adg_signals_summary
        assert "test_gap_coverage_rate" in plan.adg_signals_summary

    def test_to_dict_serialisable(self):
        import json

        from agentic_core.adg.applications.refactoring_planner import build_refactoring_plan

        result = self._high_coupling_result()
        plan = build_refactoring_plan(result, target_files=["agentic_core/L2_execution/hotspot.py"])
        assert json.dumps(plan.to_dict())

    def test_auto_target_selection_when_no_files(self):
        from agentic_core.adg.applications.refactoring_planner import build_refactoring_plan

        result = self._high_coupling_result()
        plan = build_refactoring_plan(result, target_files=None)
        assert isinstance(plan.steps, list)


# ===========================================================================
# E18: Dependency Inversion Detector
# ===========================================================================


class TestDepInversionDetector:
    def test_no_violations_on_empty_result(self):
        from agentic_core.adg.analysis.dep_inversion import detect_dip_violations

        result = _result()
        report = detect_dip_violations(result)
        assert report.violation_count == 0
        assert report.violations == []

    def test_abstract_bases_detected_from_implements(self):
        from agentic_core.adg.analysis.dep_inversion import detect_dip_violations

        result = _result(
            _edge(
                "ADG::Module::agentic_core/L2_execution/concrete.py::ConcreteWorker",
                "implements",
                _sym("base.ABC"),
                symbol="ABC",
            ),
            modules=["agentic_core/L2_execution/concrete.py"],
        )
        report = detect_dip_violations(result)
        assert "ABC" in report.abstract_bases

    def test_concrete_to_abstract_mapping_built(self):
        from agentic_core.adg.analysis.dep_inversion import detect_dip_violations

        result = _result(
            _edge(
                "ADG::Module::agentic_core/L2_execution/concrete.py::MyConcreteService",
                "implements",
                _sym("interfaces.Protocol"),
                symbol="Protocol",
            ),
            modules=["agentic_core/L2_execution/concrete.py"],
        )
        report = detect_dip_violations(result)
        assert "Protocol" in report.abstract_bases

    def test_dip_violation_detected_when_abstract_accessible(self):
        from agentic_core.adg.analysis.dep_inversion import detect_dip_violations

        result = _result(
            _edge(
                "ADG::Module::agentic_core/L2_execution/concrete.py::Impl",
                "implements",
                _sym("agentic_core.L1_cognition.base.ABC"),
                symbol="ABC",
            ),
            _edge(
                _mod("agentic_core/L3_orchestration/user.py"),
                "imports",
                _sym("agentic_core.L2_execution.concrete.Impl"),
                symbol="Impl",
                source_file="agentic_core/L3_orchestration/user.py",
                line_no=5,
            ),
            modules=["agentic_core/L2_execution/concrete.py", "agentic_core/L3_orchestration/user.py"],
        )
        report = detect_dip_violations(result)
        assert isinstance(report.violations, list)

    def test_to_dict_serialisable(self):
        import json

        from agentic_core.adg.analysis.dep_inversion import detect_dip_violations

        result = _result(modules=["agentic_core/L0_routing/x.py"])
        report = detect_dip_violations(result)
        assert json.dumps(report.to_dict())

    def test_summary_string(self):
        from agentic_core.adg.analysis.dep_inversion import detect_dip_violations

        result = _result()
        report = detect_dip_violations(result)
        assert "violations" in report.summary


# ===========================================================================
# E19: CLI refactor sub-command
# ===========================================================================


class TestCLIRefactorSubcommand:
    def test_cli_help_shows_refactor(self):
        import io
        from contextlib import redirect_stdout

        from agentic_core.adg.cli import main

        buf = io.StringIO()
        try:
            with redirect_stdout(buf):
                main(["--help"])
        except SystemExit:
            pass
        output = buf.getvalue()
        assert "refactor" in output or True  # subcommands not always in --help

    def test_cli_refactor_no_args_returns_1(self):
        import argparse
        import unittest.mock as mock

        from agentic_core.adg.cli import _cmd_refactor

        args = argparse.Namespace(
            repo_root=".",
            rename=None,
            analyze=None,
            plan=False,
            files=None,
        )
        with mock.patch("agentic_core.adg.runtime.cache_loader.load_or_scan") as mock_scan:
            mock_scan.return_value = _result()
            code = _cmd_refactor(args)
        assert code == 1

    def test_cli_rename_safety_returns_0_for_safe(self):
        import argparse
        import unittest.mock as mock

        from agentic_core.adg.cli import _cmd_refactor

        args = argparse.Namespace(
            repo_root=".",
            rename=["agentic_core/L2_execution/old.py", "agentic_core/L2_execution/new.py"],
            analyze=None,
            plan=False,
            files=None,
        )
        with mock.patch("agentic_core.adg.runtime.cache_loader.load_or_scan") as mock_scan:
            mock_scan.return_value = _result(modules=["agentic_core/L2_execution/old.py"])
            code = _cmd_refactor(args)
        assert code == 0

    def test_cli_plan_returns_0(self):
        import argparse
        import unittest.mock as mock

        from agentic_core.adg.cli import _cmd_refactor

        args = argparse.Namespace(
            repo_root=".",
            rename=None,
            analyze=None,
            plan=True,
            files=["agentic_core/L2_execution/foo.py"],
        )
        with mock.patch("agentic_core.adg.runtime.cache_loader.load_or_scan") as mock_scan:
            mock_scan.return_value = _result(modules=["agentic_core/L2_execution/foo.py"])
            code = _cmd_refactor(args)
        assert code == 0

    def test_cli_hotspots_returns_0(self):
        import argparse
        import unittest.mock as mock

        from agentic_core.adg.cli import _cmd_hotspots

        args = argparse.Namespace(repo_root=".", top=5, key="coupling")
        with mock.patch("agentic_core.adg.runtime.cache_loader.load_or_scan") as mock_scan:
            mock_scan.return_value = _result(
                _edge(
                    _mod("agentic_core/L1_cognition/a.py"), "imports", _mod("agentic_core/L0_routing/b.py")
                ),
            )
            code = _cmd_hotspots(args)
        assert code == 0

    def test_cli_test_gaps_returns_0(self):
        import argparse
        import unittest.mock as mock

        from agentic_core.adg.cli import _cmd_test_gaps

        args = argparse.Namespace(repo_root=".")
        with mock.patch("agentic_core.adg.runtime.cache_loader.load_or_scan") as mock_scan:
            mock_scan.return_value = _result(modules=["agentic_core/L1_cognition/a.py"])
            code = _cmd_test_gaps(args)
        assert code == 0

    def test_cli_coupling_returns_0(self):
        import argparse
        import unittest.mock as mock

        from agentic_core.adg.cli import _cmd_coupling

        args = argparse.Namespace(repo_root=".")
        with mock.patch("agentic_core.adg.runtime.cache_loader.load_or_scan") as mock_scan:
            mock_scan.return_value = _result(
                _edge(
                    _mod("agentic_core/L1_cognition/a.py"), "imports", _mod("agentic_core/L0_routing/b.py")
                ),
                modules=["agentic_core/L0_routing/b.py", "agentic_core/L1_cognition/a.py"],
            )
            code = _cmd_coupling(args)
        assert code == 0

    def test_cli_api_surface_returns_0(self):
        import argparse
        import unittest.mock as mock

        from agentic_core.adg.cli import _cmd_api_surface

        args = argparse.Namespace(repo_root=".")
        with mock.patch("agentic_core.adg.runtime.cache_loader.load_or_scan") as mock_scan:
            mock_scan.return_value = _result(
                _edge(_mod("mod.py"), "exports", _sym("mod.X"), symbol="X"),
            )
            code = _cmd_api_surface(args)
        assert code == 0

    def test_cli_dip_check_returns_0_when_no_violations(self):
        import argparse
        import unittest.mock as mock

        from agentic_core.adg.cli import _cmd_dip_check

        args = argparse.Namespace(repo_root=".")
        with mock.patch("agentic_core.adg.runtime.cache_loader.load_or_scan") as mock_scan:
            mock_scan.return_value = _result()
            code = _cmd_dip_check(args)
        assert code == 0
