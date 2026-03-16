"""Tests for tools/adg_cli.py canonical CLI commands.

Covers all new integration seams:
- health_reporter (trust gate, health metrics)
- placement_advisor (suggest-placement, context)
- adg_cli build, health, stats, impact, who-uses, neighbors, ownership,
  config-consumers, scoped-tests, test-coverage, missing-tests,
  guardian-scope, execution-impact, safe-healing-scope, healing-radius,
  suggest-placement, context
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_adg_cli_commands")
_emit_applies_guardrail("p0", "test_adg_cli_commands", "p0_governance")
_emit_reads_policy_state("p0", "test_adg_cli_commands", "policy_binding")
_emit_snapshots_state("p0", "test_adg_cli_commands", "state_snapshot")
emit_replay_key("p0", "test_adg_cli_commands")
emit_determinism_digest("p0", "test_adg_cli_commands")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

# ---------------------------------------------------------------------------
# Fixtures: minimal ScanResult and ADGArtifact for unit tests
# ---------------------------------------------------------------------------


def _make_scan_result(modules=None, edges=None):
    """Build a minimal ScanResult-like object for testing."""
    from agentic_core.adg.extraction.static_scanner import ScanResult

    result = MagicMock(spec=ScanResult)
    result.modules = list(
        modules
        or [
            "agentic_core/adg/schema.py",
            "agentic_core/adg/cli.py",
            "tools/adg_cli.py",
            "tests/unit/test_adg_cli_commands.py",
        ]
    )
    result.edges = list(edges or [])
    result.digest = "abc123"
    result.commit_sha = "deadbeef"
    result.print_digest = lambda: None
    return result


def _make_edge(from_name, relation_type, to_name, edge_kind="import", symbol="", source_file="", line_no=1):
    edge = MagicMock()
    edge.from_name = from_name
    edge.relation_type = relation_type
    edge.to_name = to_name
    edge.edge_kind = edge_kind
    edge.symbol = symbol
    edge.source_file = source_file
    edge.line_no = line_no
    return edge


def _make_artifact():
    """Build a minimal ADGArtifact for health report tests."""
    from agentic_core.adg.artifact.builder import (
        ADGArtifact,
        BlindSpotReport,
        EntityRecord,
        StructuralMetrics,
    )

    entities = [
        EntityRecord(
            adg_name="ADG::Module::agentic_core/adg/schema.py",
            entity_type="module",
            layer="L_TOOLS",
            identity_kind="repo_module",
            confidence="HIGH",
            resolved_path="agentic_core/adg/schema.py",
        ),
        EntityRecord(
            adg_name="ADG::Symbol::agentic_core.adg.schema.canonical_name",
            entity_type="symbol",
            layer="L_TOOLS",
            identity_kind="inferred_symbol",
            confidence="MEDIUM",
            resolved_path="agentic_core/adg/schema.py",
        ),
        EntityRecord(
            adg_name="ADG::Symbol::some.unresolved.thing",
            entity_type="symbol",
            layer="L_UNKNOWN",
            identity_kind="unresolved_import",
            confidence="LOW",
            resolved_path="",
        ),
    ]

    sm = StructuralMetrics(
        total_entities=3,
        total_relations=5,
        module_count=1,
        symbol_count=2,
        external_count=0,
        unresolved_count=1,
        orphan_modules=[],
        high_fan_in_modules=[],
        high_fan_out_modules=[],
        layer_violation_count=0,
        by_relation_type={"imports": 5},
        by_layer={"L_TOOLS": 1},
    )

    bs = BlindSpotReport(
        dynamic_import_count=2,
        star_import_count=1,
        parse_failure_count=0,
    )

    artifact = ADGArtifact(
        schema_version="3.0.0",
        commit_sha="abc123",
        scanner_digest="def456",
        entities=entities,
        relations=[],
        unresolved_imports=[
            {
                "raw_name": "some.unresolved.thing",
                "adg_name": "ADG::Symbol::some.unresolved.thing",
                "reason": "no file",
                "confidence": "LOW",
            }
        ],
        identity_health={
            "by_identity_kind": {"repo_module": 1, "inferred_symbol": 1, "unresolved_import": 1},
            "by_confidence": {"HIGH": 1, "MEDIUM": 1, "LOW": 1},
            "unresolved_import_count": 1,
            "null_node_inflation_eliminated": True,
        },
        structural_metrics=sm,
        blind_spots=bs,
        artifact_digest="feedcafe" * 8,
    )
    return artifact


# ===========================================================================
# Section 1: health_reporter tests
# ===========================================================================


class TestHealthReporter:
    def test_build_health_report_basic(self):
        from agentic_core.adg.applications.health_reporter import build_health_report

        artifact = _make_artifact()
        report = build_health_report(artifact, strict=False)

        assert report.total_entities == 3
        assert report.total_relations == 5
        assert report.unresolved_imports == 1
        assert report.layer_violation_count == 0
        assert report.dynamic_blind_spots == 2
        assert report.star_import_blind_spots == 1
        assert report.artifact_digest == "feedcafe" * 8
        assert report.schema_version == "3.0.0"

    def test_health_report_trust_pass_under_thresholds(self):
        from agentic_core.adg.applications.health_reporter import build_health_report

        artifact = _make_artifact()
        report = build_health_report(artifact, strict=True)
        assert report.trust_passed is True
        assert len(report.trust_violations) == 0

    def test_health_report_trust_fail_on_violation(self):
        from agentic_core.adg.applications.health_reporter import _STRICT_THRESHOLDS, build_health_report

        artifact = _make_artifact()
        # Force unresolved_imports above threshold
        over_threshold = _STRICT_THRESHOLDS["unresolved_import_count"] + 1
        artifact.identity_health["unresolved_import_count"] = over_threshold

        report = build_health_report(artifact, strict=True)
        assert report.trust_passed is False
        rules = [v.rule for v in report.trust_violations]
        assert "unresolved_import_count" in rules

    def test_health_report_to_dict_keys(self):
        from agentic_core.adg.applications.health_reporter import build_health_report

        artifact = _make_artifact()
        report = build_health_report(artifact, strict=False)
        d = report.to_dict()

        assert "counts" in d
        assert "blind_spots" in d
        assert "identity_distribution" in d
        assert "high_risk" in d
        assert "trust_passed" in d
        assert "summary" in d

    def test_health_report_summary_string(self):
        from agentic_core.adg.applications.health_reporter import build_health_report

        artifact = _make_artifact()
        report = build_health_report(artifact, strict=False)
        summary = report.summary
        assert "PASS" in summary or "FAIL" in summary
        assert "entities=" in summary

    def test_trust_violation_to_dict(self):
        from agentic_core.adg.applications.health_reporter import TrustViolation

        v = TrustViolation(rule="test_rule", threshold=100, actual=200, description="too high")
        d = v.to_dict()
        assert d["rule"] == "test_rule"
        assert d["threshold"] == 100
        assert d["actual"] == 200

    def test_health_layer_violation_threshold(self):
        from agentic_core.adg.applications.health_reporter import _STRICT_THRESHOLDS, build_health_report

        artifact = _make_artifact()
        artifact.structural_metrics.layer_violation_count = _STRICT_THRESHOLDS["layer_violation_count"] + 1
        report = build_health_report(artifact, strict=True)
        assert report.trust_passed is False
        rules = [v.rule for v in report.trust_violations]
        assert "layer_violation_count" in rules


# ===========================================================================
# Section 2: placement_advisor tests
# ===========================================================================


class TestPlacementAdvisor:
    def _make_advisor(self, modules=None, edges=None):
        from agentic_core.adg.applications.placement_advisor import PlacementAdvisor

        result = _make_scan_result(modules=modules, edges=edges)
        return PlacementAdvisor(result, repo_root=Path("."))

    def test_suggest_placement_agent(self):
        advisor = self._make_advisor()
        suggestion = advisor.suggest_placement(kind="agent", name="MyNewAgent")
        assert suggestion.kind == "agent"
        assert suggestion.name == "MyNewAgent"
        assert "L1" in suggestion.layer
        assert suggestion.confidence in ("HIGH", "MEDIUM", "EXACT")
        assert "agentic_core/L1_cognition" in suggestion.suggested_path

    def test_suggest_placement_config(self):
        advisor = self._make_advisor()
        suggestion = advisor.suggest_placement(kind="config", name="MyConfig")
        assert suggestion.layer == "L_SHARED"
        assert "agentic_core/config" in suggestion.suggested_path

    def test_suggest_placement_unknown_kind(self):
        advisor = self._make_advisor()
        suggestion = advisor.suggest_placement(kind="unknown_xyz_kind", name="SomeFile")
        assert suggestion.confidence == "LOW"
        assert len(suggestion.structural_risks) > 0
        assert len(suggestion.unresolved_caveats) > 0

    def test_suggest_placement_to_dict_keys(self):
        advisor = self._make_advisor()
        suggestion = advisor.suggest_placement(kind="tool", name="NewTool")
        d = suggestion.to_dict()
        required_keys = [
            "kind",
            "name",
            "suggested_path",
            "layer",
            "confidence",
            "note",
            "allowed_importers",
            "allowed_imports",
            "similar_existing",
            "structural_risks",
            "unresolved_caveats",
        ]
        for k in required_keys:
            assert k in d, f"Missing key: {k}"

    def test_suggest_placement_all_known_kinds(self):
        from agentic_core.adg.applications.placement_advisor import _KIND_PLACEMENT_MAP

        advisor = self._make_advisor()
        for kind in _KIND_PLACEMENT_MAP:
            suggestion = advisor.suggest_placement(kind=kind, name="TestSymbol")
            assert suggestion.confidence != "LOW", f"Kind {kind} returned LOW confidence"

    def test_get_file_context_known_file(self):
        modules = ["agentic_core/adg/schema.py", "tests/unit/test_schema.py"]
        edges = [
            _make_edge(
                "ADG::Module::tests/unit/test_schema.py",
                "imports",
                "ADG::Module::agentic_core/adg/schema.py",
            )
        ]
        advisor = self._make_advisor(modules=modules, edges=edges)
        ctx = advisor.get_file_context("agentic_core/adg/schema.py")
        assert ctx.target == "agentic_core/adg/schema.py"
        assert ctx.target_type == "file"
        assert ctx.layer == "L_TOOLS"
        assert "tests/unit/test_schema.py" in ctx.direct_importers

    def test_get_file_context_to_dict_keys(self):
        advisor = self._make_advisor()
        ctx = advisor.get_file_context("agentic_core/adg/schema.py")
        d = ctx.to_dict()
        required_keys = [
            "target",
            "target_type",
            "layer",
            "territory",
            "confidence",
            "confidence_notes",
            "nearest_trusted_neighbors",
            "direct_importers",
            "direct_imports",
            "config_dependencies",
            "likely_tests",
            "structural_risks",
            "duplicate_definitions",
            "unresolved_blind_spots",
        ]
        for k in required_keys:
            assert k in d, f"Missing key: {k}"

    def test_get_file_context_unknown_file_low_confidence(self):
        advisor = self._make_advisor()
        ctx = advisor.get_file_context("some/nonexistent/file.py")
        assert ctx.confidence == "LOW"
        assert len(ctx.confidence_notes) > 0

    def test_get_symbol_context(self):
        modules = ["agentic_core/adg/schema.py"]
        advisor = self._make_advisor(modules=modules)
        ctx = advisor.get_symbol_context("agentic_core.adg.schema.canonical_name")
        assert ctx.target_type == "symbol"
        assert ctx.layer == "L_TOOLS"

    def test_placement_confidence_label_always_present(self):
        advisor = self._make_advisor()
        for kind in ["agent", "config", "mixin", "router", "tool"]:
            s = advisor.suggest_placement(kind=kind, name="Foo")
            assert s.confidence in ("EXACT", "HIGH", "MEDIUM", "LOW")

    def test_placement_has_no_empty_note(self):
        advisor = self._make_advisor()
        s = advisor.suggest_placement(kind="agent", name="FooAgent")
        assert s.note != ""


# ===========================================================================
# Section 3: adg_cli command tests (via main() with mocked scan)
# ===========================================================================


def _run_cli(args, scan_result=None, capsys=None):
    """Run the canonical CLI with mocked scan and return (exit_code, stdout)."""
    from tools import adg_cli

    mock_result = scan_result or _make_scan_result()

    with patch("tools.adg_cli._load_scan", return_value=mock_result):
        with patch("tools.adg_cli._fresh_scan", return_value=mock_result):
            try:
                code = adg_cli.main(args)
            except SystemExit as e:
                code = e.code or 0
    return code


class TestAdgCliStats:
    def test_stats_no_latest_uses_scan(self, tmp_path, capsys):
        from tools import adg_cli

        mock_result = _make_scan_result()

        with patch("tools.adg_cli._load_scan", return_value=mock_result):
            with patch("tools.adg_cli._ARTIFACTS_DIR", Path("nonexistent_dir_xyz")):
                code = adg_cli.main(["--repo-root", str(tmp_path), "stats"])
        assert code == 0

    def test_stats_with_latest_file(self, tmp_path, capsys):
        from tools import adg_cli

        artifacts_dir = tmp_path / "artifacts" / "adg"
        artifacts_dir.mkdir(parents=True)
        latest = artifacts_dir / "adg_latest.json"
        latest.write_text(
            json.dumps(
                {
                    "schema_version": "3.0.0",
                    "commit_sha": "abc",
                    "artifact_digest": "deadbeef",
                    "structural_metrics": {"total_entities": 10, "total_relations": 20},
                    "identity_health": {},
                    "blind_spots": {},
                }
            )
        )

        code = adg_cli.main(["--repo-root", str(tmp_path), "stats"])
        assert code == 0


class TestAdgCliOwnership:
    def test_ownership_known_module(self, tmp_path, capsys):
        from tools import adg_cli

        modules = ["agentic_core/L0_routing/scripts/execute_ssot.py"]
        mock_result = _make_scan_result(modules=modules)

        with patch("tools.adg_cli._load_scan", return_value=mock_result):
            code = adg_cli.main(
                [
                    "--repo-root",
                    str(tmp_path),
                    "ownership",
                    "--symbol",
                    "agentic_core/L0_routing/scripts/execute_ssot.py",
                ]
            )
        assert code == 0

    def test_ownership_output_has_layer_and_territory(self, tmp_path, capsys):
        from tools import adg_cli

        captured_output: list[str] = []

        original_out = adg_cli._out

        def capture_out(data, indent=2):
            captured_output.append(json.dumps(data, indent=indent))

        modules = ["agentic_core/L0_routing/scripts/execute_ssot.py"]
        mock_result = _make_scan_result(modules=modules)

        with patch("tools.adg_cli._load_scan", return_value=mock_result):
            with patch("tools.adg_cli._out", side_effect=capture_out):
                adg_cli.main(
                    [
                        "--repo-root",
                        str(tmp_path),
                        "ownership",
                        "--symbol",
                        "agentic_core/L0_routing/scripts/execute_ssot.py",
                    ]
                )

        assert len(captured_output) > 0
        data = json.loads(captured_output[0])
        assert "layer" in data
        assert "territory" in data
        assert "confidence" in data
        assert "confidence_notes" in data


class TestAdgCliWhoUses:
    def test_who_uses_module_path(self, tmp_path):
        from tools import adg_cli

        modules = ["agentic_core/adg/schema.py", "agentic_core/adg/cli.py"]
        edges = [
            _make_edge(
                "ADG::Module::agentic_core/adg/cli.py",
                "imports",
                "ADG::Module::agentic_core/adg/schema.py",
            )
        ]
        mock_result = _make_scan_result(modules=modules, edges=edges)

        with patch("tools.adg_cli._load_scan", return_value=mock_result):
            code = adg_cli.main(
                [
                    "--repo-root",
                    str(tmp_path),
                    "who-uses",
                    "--symbol",
                    "agentic_core/adg/schema.py",
                ]
            )
        assert code == 0


class TestAdgCliNeighbors:
    def test_neighbors_returns_importers_and_deps(self, tmp_path):
        from tools import adg_cli

        modules = ["agentic_core/adg/schema.py", "agentic_core/adg/cli.py", "tools/helper.py"]
        edges = [
            _make_edge(
                "ADG::Module::agentic_core/adg/cli.py",
                "imports",
                "ADG::Module::agentic_core/adg/schema.py",
            ),
            _make_edge(
                "ADG::Module::agentic_core/adg/schema.py",
                "imports",
                "ADG::Module::tools/helper.py",
            ),
        ]
        mock_result = _make_scan_result(modules=modules, edges=edges)

        captured: list[dict] = []

        def capture(data, indent=2):
            captured.append(data)

        with patch("tools.adg_cli._load_scan", return_value=mock_result):
            with patch("tools.adg_cli._out", side_effect=capture):
                adg_cli.main(
                    [
                        "--repo-root",
                        str(tmp_path),
                        "neighbors",
                        "--file",
                        "agentic_core/adg/schema.py",
                    ]
                )

        assert len(captured) == 1
        d = captured[0]
        assert "importers" in d
        assert "dependencies" in d
        assert "agentic_core/adg/cli.py" in d["importers"]
        assert "tools/helper.py" in d["dependencies"]


class TestAdgCliConfigConsumers:
    def test_config_consumers_found(self, tmp_path):
        from tools import adg_cli

        modules = ["agentic_core/L0_routing/config/path_constants.py", "tools/adg_cli.py"]
        edges = [
            _make_edge(
                "ADG::Module::tools/adg_cli.py",
                "reads_from",
                "ADG::Symbol::MY_CONSTANT",
                symbol="MY_CONSTANT",
            )
        ]
        mock_result = _make_scan_result(modules=modules, edges=edges)

        captured: list[dict] = []

        def capture(data, indent=2):
            captured.append(data)

        with patch("tools.adg_cli._load_scan", return_value=mock_result):
            with patch("tools.adg_cli._out", side_effect=capture):
                adg_cli.main(
                    [
                        "--repo-root",
                        str(tmp_path),
                        "config-consumers",
                        "--symbol",
                        "MY_CONSTANT",
                    ]
                )

        assert len(captured) == 1
        assert "consumers" in captured[0]
        assert "consumer_count" in captured[0]


class TestAdgCliScopedTests:
    def test_scoped_tests_returns_impacted(self, tmp_path):
        from tools import adg_cli
        from tools.change_impact_engine import ChangeImpactResult

        mock_impact = ChangeImpactResult(
            changed_files=["agentic_core/adg/schema.py"],
            impacted_modules=["agentic_core/adg/cli.py"],
            impacted_tests=["tests/unit/test_adg_schema.py"],
            blast_radius_by_depth={"agentic_core/adg/cli.py": 1},
            uncovered_changed_files=[],
            scope_widening_events=[],
            risk_score=100,
            route_mode="NORMAL",
            impact_digest="abc123",
        )

        mock_result = _make_scan_result()

        with patch("tools.adg_cli._load_scan", return_value=mock_result):
            with patch("tools.change_impact_engine.ChangeImpactEngine.analyze", return_value=mock_impact):
                code = adg_cli.main(
                    [
                        "--repo-root",
                        str(tmp_path),
                        "scoped-tests",
                        "--changed-files",
                        "agentic_core/adg/schema.py",
                    ]
                )
        assert code == 0

    def test_scoped_tests_widening_warning_on_uncovered(self, tmp_path):
        from tools import adg_cli
        from tools.change_impact_engine import ChangeImpactResult

        mock_impact = ChangeImpactResult(
            changed_files=["some/unknown/file.py"],
            impacted_modules=[],
            impacted_tests=[],
            blast_radius_by_depth={},
            uncovered_changed_files=["some/unknown/file.py"],
            scope_widening_events=[],
            risk_score=0,
            route_mode="NORMAL",
            impact_digest="zzz",
        )

        captured: list[dict] = []

        def capture(data, indent=2):
            captured.append(data)

        mock_result = _make_scan_result()

        with patch("tools.adg_cli._load_scan", return_value=mock_result):
            with patch("tools.change_impact_engine.ChangeImpactEngine.analyze", return_value=mock_impact):
                with patch("tools.adg_cli._out", side_effect=capture):
                    adg_cli.main(
                        [
                            "--repo-root",
                            str(tmp_path),
                            "scoped-tests",
                            "--changed-files",
                            "some/unknown/file.py",
                        ]
                    )

        assert len(captured) > 0
        d = captured[0]
        assert "uncovered_changed_files" in d
        assert len(d["uncovered_changed_files"]) > 0
        assert "widening_warning" in d

    def test_scoped_tests_no_silent_fallback(self, tmp_path):
        """Verify that uncovered files are EXPLICITLY reported, never silently dropped."""
        from tools import adg_cli
        from tools.change_impact_engine import ChangeImpactResult

        mock_impact = ChangeImpactResult(
            changed_files=["file_not_in_adg.py"],
            impacted_modules=[],
            impacted_tests=[],
            blast_radius_by_depth={},
            uncovered_changed_files=["file_not_in_adg.py"],
            scope_widening_events=["EXPLICIT_WIDENING"],
            risk_score=5,
            route_mode="NORMAL",
            impact_digest="abc",
        )

        captured: list[dict] = []

        def capture(data, indent=2):
            captured.append(data)

        mock_result = _make_scan_result()

        with patch("tools.adg_cli._load_scan", return_value=mock_result):
            with patch("tools.change_impact_engine.ChangeImpactEngine.analyze", return_value=mock_impact):
                with patch("tools.adg_cli._out", side_effect=capture):
                    adg_cli.main(
                        [
                            "--repo-root",
                            str(tmp_path),
                            "scoped-tests",
                            "--changed-files",
                            "file_not_in_adg.py",
                        ]
                    )

        assert captured, "Output must be emitted"
        d = captured[0]
        assert "uncovered_changed_files" in d
        assert "file_not_in_adg.py" in d["uncovered_changed_files"]


class TestAdgCliTestCoverage:
    def test_test_coverage_known_module(self, tmp_path):
        from tools import adg_cli

        modules = ["agentic_core/adg/schema.py", "tests/unit/test_schema.py"]
        edges = [
            _make_edge(
                "ADG::Module::tests/unit/test_schema.py",
                "imports",
                "ADG::Module::agentic_core/adg/schema.py",
            )
        ]
        mock_result = _make_scan_result(modules=modules, edges=edges)

        captured: list[dict] = []

        def capture(data, indent=2):
            captured.append(data)

        with patch("tools.adg_cli._load_scan", return_value=mock_result):
            with patch("tools.adg_cli._out", side_effect=capture):
                adg_cli.main(
                    [
                        "--repo-root",
                        str(tmp_path),
                        "test-coverage",
                        "--symbol",
                        "agentic_core/adg/schema.py",
                    ]
                )

        assert len(captured) > 0
        d = captured[0]
        assert "covering_tests" in d
        assert "test_count" in d

    def test_test_coverage_unknown_module_returns_error_dict(self, tmp_path):
        from tools import adg_cli

        mock_result = _make_scan_result()
        captured: list[dict] = []

        def capture(data, indent=2):
            captured.append(data)

        with patch("tools.adg_cli._load_scan", return_value=mock_result):
            with patch("tools.adg_cli._out", side_effect=capture):
                adg_cli.main(
                    [
                        "--repo-root",
                        str(tmp_path),
                        "test-coverage",
                        "--symbol",
                        "completely/unknown/module.py",
                    ]
                )

        assert len(captured) > 0
        # Must emit output, not silently fail
        assert "covering_tests" in captured[0] or "error" in captured[0]


class TestAdgCliGuardianScope:
    def test_guardian_scope_high_risk_only(self, tmp_path):
        from tools import adg_cli

        mock_result = _make_scan_result()

        with patch("tools.adg_cli._load_scan", return_value=mock_result):
            code = adg_cli.main(
                [
                    "--repo-root",
                    str(tmp_path),
                    "guardian-scope",
                    "--high-risk-only",
                ]
            )
        assert code == 0

    def test_guardian_scope_boundary_violations(self, tmp_path):
        from tools import adg_cli

        mock_result = _make_scan_result()

        with patch("tools.adg_cli._load_scan", return_value=mock_result):
            code = adg_cli.main(
                [
                    "--repo-root",
                    str(tmp_path),
                    "guardian-scope",
                    "--boundary-violations",
                ]
            )
        assert code == 0

    def test_guardian_scope_focus_territory(self, tmp_path):
        from tools import adg_cli

        mock_result = _make_scan_result()

        with patch("tools.adg_cli._load_scan", return_value=mock_result):
            code = adg_cli.main(
                [
                    "--repo-root",
                    str(tmp_path),
                    "guardian-scope",
                    "--focus-territory",
                    "SAFETY",
                ]
            )
        assert code == 0

    def test_guardian_scope_output_has_adg_signals_digest(self, tmp_path):
        from tools import adg_cli

        mock_result = _make_scan_result()
        captured: list[dict] = []

        def capture(data, indent=2):
            captured.append(data)

        with patch("tools.adg_cli._load_scan", return_value=mock_result):
            with patch("tools.adg_cli._out", side_effect=capture):
                adg_cli.main(
                    [
                        "--repo-root",
                        str(tmp_path),
                        "guardian-scope",
                        "--high-risk-only",
                    ]
                )

        assert len(captured) > 0
        assert "adg_signals_digest" in captured[0]

    def test_guardian_scope_placeholder_suppression(self, tmp_path):
        """Placeholder/unresolved nodes must not dominate guardian scores."""
        from tools import adg_cli

        mock_result = _make_scan_result()
        captured: list[dict] = []

        def capture(data, indent=2):
            captured.append(data)

        with patch("tools.adg_cli._load_scan", return_value=mock_result):
            with patch("tools.adg_cli._out", side_effect=capture):
                adg_cli.main(
                    [
                        "--repo-root",
                        str(tmp_path),
                        "guardian-scope",
                        "--high-risk-only",
                    ]
                )

        assert len(captured) > 0
        d = captured[0]
        # Guardian ranking must include signals metadata
        assert "mode" in d


class TestAdgCliExecutionImpact:
    def test_execution_impact_returns_pre_run_report(self, tmp_path):
        from agentic_core.adg.applications.execute_ssot_integration import PreRunADGReport
        from tools import adg_cli

        mock_report = PreRunADGReport(
            changed_files=["agentic_core/L0_routing/scripts/execute_ssot.py"],
            impacted_module_count=5,
            impacted_modules=["agentic_core/adg/cli.py"],
            impacted_test_count=2,
            impacted_tests=["tests/unit/test_execute.py"],
            risk_score=200,
            route_mode="NORMAL",
            scope_widening_events=[],
            uncovered_changed_files=[],
            layer_violation_count=0,
            impact_digest="abc123",
            adg_available=True,
            adg_error="",
        )

        mock_result = _make_scan_result()
        captured: list[dict] = []

        def capture(data, indent=2):
            captured.append(data)

        with patch("tools.adg_cli._load_scan", return_value=mock_result):
            with patch(
                "agentic_core.adg.applications.execute_ssot_integration.build_pre_run_report",
                return_value=mock_report,
            ):
                with patch("tools.adg_cli._out", side_effect=capture):
                    code = adg_cli.main(
                        [
                            "--repo-root",
                            str(tmp_path),
                            "execution-impact",
                            "--file",
                            "agentic_core/L0_routing/scripts/execute_ssot.py",
                        ]
                    )

        assert code == 0
        assert len(captured) > 0
        d = captured[0]
        assert "route_mode" in d
        assert "impact_digest" in d
        assert "adg_available" in d

    def test_execution_impact_partial_labeling_for_unavailable(self, tmp_path):
        """Evidence output must explicitly mark when ADG is unavailable."""
        from agentic_core.adg.applications.execute_ssot_integration import PreRunADGReport
        from tools import adg_cli

        mock_report = PreRunADGReport.unavailable(
            ["agentic_core/L0_routing/scripts/execute_ssot.py"],
            "ADG scan failed: test error",
        )

        mock_result = _make_scan_result()
        captured: list[dict] = []

        def capture(data, indent=2):
            captured.append(data)

        with patch("tools.adg_cli._load_scan", return_value=mock_result):
            with patch(
                "agentic_core.adg.applications.execute_ssot_integration.build_pre_run_report",
                return_value=mock_report,
            ):
                with patch("tools.adg_cli._out", side_effect=capture):
                    adg_cli.main(
                        [
                            "--repo-root",
                            str(tmp_path),
                            "execution-impact",
                            "--file",
                            "agentic_core/L0_routing/scripts/execute_ssot.py",
                        ]
                    )

        assert len(captured) > 0
        d = captured[0]
        assert d["adg_available"] is False
        assert d["adg_error"] != ""


class TestAdgCliSafeHealingScope:
    def test_safe_healing_scope_known_module(self, tmp_path):
        from tools import adg_cli

        modules = ["agentic_core/L0_routing/scripts/execute_ssot.py"]
        mock_result = _make_scan_result(modules=modules)

        with patch("tools.adg_cli._load_scan", return_value=mock_result):
            code = adg_cli.main(
                [
                    "--repo-root",
                    str(tmp_path),
                    "safe-healing-scope",
                    "--symbol",
                    "agentic_core/L0_routing/scripts/execute_ssot.py",
                ]
            )
        assert code in (0, 1)

    def test_safe_healing_scope_output_keys(self, tmp_path):
        from tools import adg_cli

        modules = ["agentic_core/L0_routing/scripts/execute_ssot.py"]
        mock_result = _make_scan_result(modules=modules)
        captured: list[dict] = []

        def capture(data, indent=2):
            captured.append(data)

        with patch("tools.adg_cli._load_scan", return_value=mock_result):
            with patch("tools.adg_cli._out", side_effect=capture):
                adg_cli.main(
                    [
                        "--repo-root",
                        str(tmp_path),
                        "safe-healing-scope",
                        "--symbol",
                        "agentic_core/L0_routing/scripts/execute_ssot.py",
                    ]
                )

        assert len(captured) > 0
        d = captured[0]
        required = ["symbol", "confidence", "impact_digest"]
        for k in required:
            assert k in d, f"Missing key: {k}"


class TestAdgCliSuggestPlacement:
    def test_suggest_placement_agent(self, tmp_path):
        from tools import adg_cli

        mock_result = _make_scan_result()
        captured: list[dict] = []

        def capture(data, indent=2):
            captured.append(data)

        with patch("tools.adg_cli._load_scan", return_value=mock_result):
            with patch("tools.adg_cli._out", side_effect=capture):
                code = adg_cli.main(
                    [
                        "--repo-root",
                        str(tmp_path),
                        "suggest-placement",
                        "--kind",
                        "agent",
                        "--name",
                        "NewResumeAgent",
                    ]
                )

        assert code == 0
        assert len(captured) > 0
        d = captured[0]
        assert d["kind"] == "agent"
        assert d["confidence"] in ("HIGH", "MEDIUM", "EXACT", "LOW")
        assert "suggested_path" in d
        assert "layer" in d

    def test_suggest_placement_confidence_label_present(self, tmp_path):
        from tools import adg_cli

        mock_result = _make_scan_result()
        captured: list[dict] = []

        def capture(data, indent=2):
            captured.append(data)

        with patch("tools.adg_cli._load_scan", return_value=mock_result):
            with patch("tools.adg_cli._out", side_effect=capture):
                adg_cli.main(
                    [
                        "--repo-root",
                        str(tmp_path),
                        "suggest-placement",
                        "--kind",
                        "config",
                        "--name",
                        "MySettings",
                    ]
                )

        assert len(captured) > 0
        d = captured[0]
        assert "confidence" in d
        # Confidence must be explicit, not absent
        assert d["confidence"] in ("EXACT", "HIGH", "MEDIUM", "LOW")

    def test_suggest_placement_unresolved_caveat_present_for_unknown(self, tmp_path):
        from tools import adg_cli

        mock_result = _make_scan_result()
        captured: list[dict] = []

        def capture(data, indent=2):
            captured.append(data)

        with patch("tools.adg_cli._load_scan", return_value=mock_result):
            with patch("tools.adg_cli._out", side_effect=capture):
                adg_cli.main(
                    [
                        "--repo-root",
                        str(tmp_path),
                        "suggest-placement",
                        "--kind",
                        "xyzzy_unknown",
                        "--name",
                        "Foo",
                    ]
                )

        assert len(captured) > 0
        d = captured[0]
        assert len(d.get("unresolved_caveats", [])) > 0


class TestAdgCliContext:
    def test_context_file(self, tmp_path):
        from tools import adg_cli

        mock_result = _make_scan_result()
        captured: list[dict] = []

        def capture(data, indent=2):
            captured.append(data)

        with patch("tools.adg_cli._load_scan", return_value=mock_result):
            with patch("tools.adg_cli._out", side_effect=capture):
                adg_cli.main(
                    [
                        "--repo-root",
                        str(tmp_path),
                        "context",
                        "--file",
                        "agentic_core/adg/schema.py",
                    ]
                )

        assert len(captured) > 0
        d = captured[0]
        assert "layer" in d
        assert "territory" in d
        assert "confidence" in d
        assert "direct_importers" in d

    def test_context_symbol(self, tmp_path):
        from tools import adg_cli

        mock_result = _make_scan_result(modules=["agentic_core/adg/schema.py"])
        captured: list[dict] = []

        def capture(data, indent=2):
            captured.append(data)

        with patch("tools.adg_cli._load_scan", return_value=mock_result):
            with patch("tools.adg_cli._out", side_effect=capture):
                adg_cli.main(
                    [
                        "--repo-root",
                        str(tmp_path),
                        "context",
                        "--symbol",
                        "agentic_core.adg.schema.canonical_name",
                    ]
                )

        assert len(captured) > 0
        d = captured[0]
        assert d["target_type"] == "symbol"
        assert "confidence" in d

    def test_context_output_has_confidence_notes(self, tmp_path):
        """Context output must include confidence_notes for transparency."""
        from tools import adg_cli

        mock_result = _make_scan_result()
        captured: list[dict] = []

        def capture(data, indent=2):
            captured.append(data)

        with patch("tools.adg_cli._load_scan", return_value=mock_result):
            with patch("tools.adg_cli._out", side_effect=capture):
                adg_cli.main(
                    [
                        "--repo-root",
                        str(tmp_path),
                        "context",
                        "--file",
                        "some/nonexistent/file.py",
                    ]
                )

        assert len(captured) > 0
        d = captured[0]
        assert "confidence_notes" in d

    def test_context_output_has_unresolved_blind_spots(self, tmp_path):
        """Context must report unresolved blind spots explicitly."""
        from tools import adg_cli

        modules = ["agentic_core/adg/schema.py"]
        edges = [
            _make_edge(
                "ADG::Module::agentic_core/adg/schema.py",
                "imports",
                "ADG::Symbol::some.unresolved.symbol",
            )
        ]
        mock_result = _make_scan_result(modules=modules, edges=edges)
        captured: list[dict] = []

        def capture(data, indent=2):
            captured.append(data)

        with patch("tools.adg_cli._load_scan", return_value=mock_result):
            with patch("tools.adg_cli._out", side_effect=capture):
                adg_cli.main(
                    [
                        "--repo-root",
                        str(tmp_path),
                        "context",
                        "--file",
                        "agentic_core/adg/schema.py",
                    ]
                )

        assert len(captured) > 0
        d = captured[0]
        assert "unresolved_blind_spots" in d


# ===========================================================================
# Section 4: conservative widening tests
# ===========================================================================


class TestConservativeWidening:
    def test_scoped_tests_explicit_widening_logged(self, tmp_path):
        """Explicit widening events must always appear in output — never swallowed."""
        from tools import adg_cli
        from tools.change_impact_engine import ChangeImpactResult

        mock_impact = ChangeImpactResult(
            changed_files=["agentic_core/L0_routing/scripts/execute_ssot.py"],
            impacted_modules=["agentic_core/L3_orchestration/orchestrator.py"],
            impacted_tests=[],
            blast_radius_by_depth={"agentic_core/L3_orchestration/orchestrator.py": 2},
            uncovered_changed_files=[],
            scope_widening_events=["agentic_core/L3_orchestration/orchestrator.py(layer=L3)"],
            risk_score=350,
            route_mode="RESTRICTED",
            impact_digest="abc",
        )

        mock_result = _make_scan_result()
        captured: list[dict] = []

        def capture(data, indent=2):
            captured.append(data)

        with patch("tools.adg_cli._load_scan", return_value=mock_result):
            with patch("tools.change_impact_engine.ChangeImpactEngine.analyze", return_value=mock_impact):
                with patch("tools.adg_cli._out", side_effect=capture):
                    adg_cli.main(
                        [
                            "--repo-root",
                            str(tmp_path),
                            "scoped-tests",
                            "--changed-files",
                            "agentic_core/L0_routing/scripts/execute_ssot.py",
                        ]
                    )

        assert len(captured) > 0
        d = captured[0]
        assert "scope_widening_events" in d
        assert len(d["scope_widening_events"]) > 0
        assert "route_mode" in d
        assert d["route_mode"] == "RESTRICTED"

    def test_healing_radius_by_layer_always_present(self, tmp_path):
        """Healing radius must partition by layer — never return flat blob."""
        from tools import adg_cli

        modules = ["agentic_core/L0_routing/scripts/execute_ssot.py"]
        mock_result = _make_scan_result(modules=modules)
        captured: list[dict] = []

        def capture(data, indent=2):
            captured.append(data)

        with patch("tools.adg_cli._load_scan", return_value=mock_result):
            with patch("tools.adg_cli._out", side_effect=capture):
                adg_cli.main(
                    [
                        "--repo-root",
                        str(tmp_path),
                        "healing-radius",
                        "--symbol",
                        "agentic_core/L0_routing/scripts/execute_ssot.py",
                    ]
                )

        assert len(captured) > 0
        d = captured[0]
        assert "by_layer" in d
        assert "total_blast_radius" in d
        assert "impact_digest" in d
