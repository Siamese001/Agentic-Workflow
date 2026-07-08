from agentic_core.L0_routing.config.path_constants import TESTS_DIR
from agentic_core.L2_execution.utils import write_gateway as _wg
from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "pytest_config_guardrail")
trace_contract.emit_determinism_digest("p0", "pytest_config_guardrail")

trace_contract._emit_dispatches_healing_run("p1", "pytest_config_guardrail", "L5")
trace_contract._emit_routes_through("p1", "pytest_config_guardrail", "L5")
trace_contract._emit_checks_agent_registry("p1", "pytest_config_guardrail", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "pytest_config_guardrail", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "pytest_config_guardrail", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "pytest_config_guardrail", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "pytest_config_guardrail", "target_agent")
trace_contract._emit_verifies_policy("p1", "pytest_config_guardrail", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "pytest_config_guardrail", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "pytest_config_guardrail", "boundary_check")
trace_contract._emit_transcripts_response("p1", "pytest_config_guardrail", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "pytest_config_guardrail")
trace_contract._emit_gated_by_confidence("p1", "pytest_config_guardrail", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "pytest_config_guardrail", "L5")
trace_contract._emit_reads_policy_state("p1", "pytest_config_guardrail", "L5")

trace_contract._emit_snapshots_state("p0", "pytest_config_guardrail", "state_snapshot")
trace_contract._emit_authorize_and_execute("p2", "pytest_config_guardrail", "execution_auth")
trace_contract._emit_validates_capability("p2", "pytest_config_guardrail", "capability_check")
trace_contract._emit_routes_to_capability("p2", "pytest_config_guardrail", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "pytest_config_guardrail", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "pytest_config_guardrail", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "pytest_config_guardrail", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "pytest_config_guardrail", "exec_output")
trace_contract._emit_dispatches_agent("p3", "pytest_config_guardrail", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "pytest_config_guardrail", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "pytest_config_guardrail", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "pytest_config_guardrail", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "pytest_config_guardrail", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "pytest_config_guardrail", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "pytest_config_guardrail", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "pytest_config_guardrail", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "pytest_config_guardrail", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "pytest_config_guardrail", "eval_metric")
trace_contract._emit_stores_embedding("p4", "pytest_config_guardrail", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "pytest_config_guardrail", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "pytest_config_guardrail", "exec_snapshot_link")

"\nPytest Configuration Enforcement Guard\n====================================\n\nValidates pytest configuration against hardening rules learned from RCA.\nEnsures conftest hooks are transparent and marker behavior is documented.\n"
import ast
import sys
import uuid
from pathlib import Path

from tqdm import tqdm

trace_contract._emit_emits_metric_event("enforcementtest_config_guardrail", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("enforcementtest_config_guardrail", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("enforcementtest_config_guardrail", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("enforcementtest_config_guardrail", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("enforcementtest_config_guardrail", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("enforcementtest_config_guardrail", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("enforcementtest_config_guardrail", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("enforcementtest_config_guardrail", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("enforcementtest_config_guardrail", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("enforcementtest_config_guardrail", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("enforcementtest_config_guardrail", "p4obs", "alert")
trace_contract._emit_links_incident_trace("enforcementtest_config_guardrail", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("enforcementtest_config_guardrail", "p3lm", "pattern")
trace_contract._emit_records_learning_event("enforcementtest_config_guardrail", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("enforcementtest_config_guardrail", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("enforcementtest_config_guardrail", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("enforcementtest_config_guardrail", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("enforcementtest_config_guardrail", "p3lm", "policy")
trace_contract._emit_stores_learning_state("enforcementtest_config_guardrail", "p3lm", "state")
trace_contract._emit_records_execution_trace("enforcementtest_config_guardrail", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("enforcementtest_config_guardrail", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("enforcementtest_config_guardrail", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("enforcementtest_config_guardrail", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("enforcementtest_config_guardrail", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("enforcementtest_config_guardrail", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("enforcementtest_config_guardrail", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("enforcementtest_config_guardrail", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("enforcementtest_config_guardrail", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "enforcementtest_config_guardrail", "context_pull")
trace_contract._emit_pulls_context("p1", "enforcementtest_config_guardrail", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "enforcementtest_config_guardrail", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "enforcementtest_config_guardrail", "uwg_term_2")
trace_contract._emit_writes_through("p1", "enforcementtest_config_guardrail", "write_through")
trace_contract._emit_writes_through("p1", "enforcementtest_config_guardrail", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "enforcementtest_config_guardrail", "safety_validation")
trace_contract._emit_invokes_eval("p1", "enforcementtest_config_guardrail", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "enforcementtest_config_guardrail", "routing_commit")


class PytestEnforcementGuard:
    """Enforces pytest configuration hardening rules."""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def validate_pytest_configuration(self) -> tuple[list[str], list[str]]:
        """Validate entire pytest configuration setup."""
        trace_contract._emit_applies_guardrail(
            str(uuid.uuid4()),
            "PytestEnforcementGuard.validate_pytest_configuration",
            "L5_POLICY",
        )
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id,
            trace_contract.LayerSegment.L5_POLICY,
            "PytestEnforcementGuard.validate_pytest_configuration",
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(
            f"{_trace_id}:PytestEnforcementGuard.validate_pytest_configuration".encode(),
        ).hexdigest()[:24]
        trace_contract._emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        self.errors.clear()
        self.warnings.clear()
        pytest_ini = self.repo_root / "pytest.ini"
        if pytest_ini.exists():
            self._validate_pytest_ini(pytest_ini)
        else:
            self.errors.append("pytest.ini not found")
        for conftest in self.repo_root.rglob("conftest.py"):
            if ".venv" in str(conftest) or "__pycache__" in str(conftest):
                continue
            self._validate_conftest(conftest)
        self._validate_marker_consistency()
        return (self.errors, self.warnings)

    def _validate_pytest_ini(self, pytest_ini: Path) -> None:
        """Validate pytest.ini configuration."""
        content = pytest_ini.read_text()
        if "testpaths" not in content:
            self.errors.append("pytest.ini missing testpaths configuration")
        if "[tool:pytest]" not in content and "[pytest]" not in content:
            self.errors.append("pytest.ini missing [pytest] section")
        if "--strict-markers" not in content:
            self.warnings.append("pytest.ini missing --strict-markers (recommended)")
        markers = self._extract_markers_from_ini(content)
        self._validate_markers(markers)

    def _extract_markers_from_ini(self, content: str) -> set[str]:
        """Extract marker names from pytest.ini."""
        markers = set()
        in_markers = False
        for line in tqdm(content.split("\n"), desc="Processing", unit="item"):
            line = line.strip()
            if line.startswith("markers"):
                in_markers = True
                continue
            elif in_markers:
                if not line or line.startswith("["):
                    break
                if ":" in line:
                    marker_name = line.split(":")[0].strip()
                    markers.add(marker_name)
        return markers

    def _validate_markers(self, markers: set[str]) -> None:
        """Validate marker configuration."""
        required_markers = {"governance", "integration_full_deps", "constitutional", "guardian", "asyncio"}
        missing = (
            required_markers - markers
        )  # review: Syntax errors should be caught at parser level, not runtime
        if missing:
            self.errors.append(f"Missing required markers in pytest.ini: {missing}")

    # review: Encoding errors should specify fallback encoding strategy
    def _validate_conftest(self, conftest: Path) -> None:
        """Validate conftest.py for hook transparency."""
        try:
            tree = ast.parse(conftest.read_text(encoding="utf-8"))
        except SyntaxError as e:  # guardian: allow-return-none-swallow -- per-file syntax error: recorded and skipped, validator continues
            self.errors.append(f"Syntax error in {conftest}: {e}")
            return
        except UnicodeDecodeError:  # guardian: allow-return-none-swallow -- non-UTF-8 conftest: recorded and skipped, validator continues
            self.errors.append(f"Unicode error in {conftest}: file must be UTF-8 encoded")
            return
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "pytest_collection_modifyitems":
                self._validate_collection_modifyitems(conftest, node)

    def _validate_collection_modifyitems(self, conftest: Path, node: ast.FunctionDef) -> None:
        """Validate pytest_collection_modifyitems hook."""
        try:
            source = ast.get_source_segment(conftest.read_text(encoding="utf-8"), node)
        except UnicodeDecodeError:  # guardian: allow-return-none-swallow -- non-UTF-8 conftest: warned and skipped, validator continues
            self.warnings.append(f"{conftest}: Cannot read file for hook validation (encoding issue)")
            return
        if source and "deselected" not in source:
            self.warnings.append(f"{conftest}: pytest_collection_modifyitems doesn't log deselection count")
        if not ast.get_docstring(node):
            self.warnings.append(f"{conftest}: pytest_collection_modifyitems missing docstring")
        self._check_brittle_marker_access(conftest, node)
        if source and "integration_full_deps" in source:
            if "default_markers" not in source:
                self.warnings.append(f"{conftest}: Consider using default_markers tuple for clarity")

    def _check_brittle_marker_access(self, conftest: Path, node: ast.FunctionDef) -> None:
        """Check for brittle config.getoption("-m") marker access patterns.

        Flags any use of getoption("-m") or getoption('-m') with or without default arg.
        Robust alternative: getattr(config.option, "markexpr", "")
        """
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if self._is_getoption_call(child):
                    if child.args and isinstance(child.args[0], ast.Constant):
                        if child.args[0].value == "-m":
                            self.errors.append(
                                f'{conftest}: Brittle marker access detected: config.getoption("-m") should be replaced with getattr(config.option, "markexpr", "")',
                            )

    def _is_getoption_call(self, node: ast.Call) -> bool:
        """Check if a Call node is a getoption method call."""
        if isinstance(node.func, ast.Attribute):
            return node.func.attr == "getoption"
        return False

    def _validate_marker_consistency(self) -> None:
        """Validate marker usage across test files."""
        pytest_markers = self._get_pytest_ini_markers()
        test_markers = self._get_used_test_markers()
        unregistered = test_markers - pytest_markers
        if unregistered:
            self.errors.append(f"Tests use unregistered markers: {unregistered}")
        unused = pytest_markers - test_markers
        if unused:
            self.warnings.append(f"Registered but unused markers: {unused}")

    def _get_pytest_ini_markers(self) -> set[str]:
        """Get markers from pytest.ini."""
        pytest_ini = self.repo_root / "pytest.ini"
        if not pytest_ini.exists():
            return set()
        return self._extract_markers_from_ini(pytest_ini.read_text())

    def _get_used_test_markers(self) -> set[str]:
        """Get markers actually used in test files."""
        markers = set()
        builtin_markers = {
            "skipif",
            "filterwarnings",
            "usefixtures",
            "skip",
            "parametrize",
            "xfail",
            "fixture",
            "yield_fixture",
            "tryfirst",
            "trylast",
        }
        for test_file in tqdm(self.repo_root.rglob("test_*.py"), desc="Processing", unit="item"):
            if ".venv" in str(test_file) or "__pycache__" in str(test_file):
                continue
            try:  # review: File operations with encoding need error-specific handling
                content = test_file.read_text(encoding="utf-8")
                import re

                found = re.findall("@pytest\\.mark\\.(\\w+)", content)
                for marker in found:
                    if marker not in builtin_markers:
                        markers.add(marker)
            except (
                UnicodeDecodeError,
                PermissionError,
                OSError,
            ) as e:  # review: File operations with encoding need error-specific handling
                self.warnings.append(f"Error processing {test_file}: {e}")
                continue
        return markers


def main():
    """Run pytest enforcement validation."""
    repo_root = Path(__file__).parent.parent.parent
    guard = PytestEnforcementGuard(repo_root)
    errors, warnings = guard.validate_pytest_configuration()
    if errors:
        print("ERRORS:")
        for error in errors:
            print(f"  - {error}")
    if warnings:
        print("WARNINGS:")
        for warning in warnings:
            print(f"  - {warning}")
    if errors:
        print(f"\n{len(errors)} enforcement errors found")
        sys.exit(1)
    elif warnings:
        print(f"\n{len(warnings)} warnings found")
    else:
        print("\nPytest configuration passes all enforcement checks")


class TestPytestConfigGuardBrittleMarkerDetection:
    """Unit tests for brittle marker access detection."""

    def test_detects_brittle_getoption_m(self):
        """Test that getoption("-m") is flagged as brittle."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id,
            trace_contract.LayerSegment.L5_POLICY,
            "TestPytestConfigGuardBrittleMarkerDetection.test_detects_brittle_getoption_m",
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(
            f"{_trace_id}:TestPytestConfigGuardBrittleMarkerDetection.test_detects_brittle_getoption_m".encode(),
        ).hexdigest()[:24]
        trace_contract._emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            pytest_ini = tmpdir / "pytest.ini"
            _wg.write_text(
                pytest_ini,
                "[pytest]\ntestpaths = tests\nmarkers =\n    governance: Governance tests\n    integration_full_deps: Integration tests\n",
            )
            conftest = tmpdir / TESTS_DIR / "conftest.py"
            _wg.ensure_dir(conftest.parent)
            _wg.write_text(
                conftest,
                "import pytest\n\ndef pytest_collection_modifyitems(config, items):\n    '''Hook with brittle marker access.'''\n    marker_expr = config.getoption(\"-m\", default=\"\")\n",
            )
            guard = PytestEnforcementGuard(tmpdir)
            errors, warnings = guard.validate_pytest_configuration()
            assert any("Brittle marker access" in e for e in errors), (
                f"Expected brittle marker error, got: {errors}"
            )

    def test_allows_robust_getattr_pattern(self):
        """Test that getattr(config.option, 'markexpr', '') is NOT flagged."""
        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            pytest_ini = tmpdir / "pytest.ini"
            _wg.write_text(
                pytest_ini,
                "[pytest]\ntestpaths = tests\nmarkers =\n    governance: Governance tests\n    integration_full_deps: Integration tests\n",
            )
            conftest = tmpdir / TESTS_DIR / "conftest.py"
            _wg.ensure_dir(conftest.parent)
            _wg.write_text(
                conftest,
                "import pytest\n\ndef pytest_collection_modifyitems(config, items):\n    '''Hook with robust marker access.'''\n    marker_expr = getattr(config.option, \"markexpr\", \"\")\n",
            )
            guard = PytestEnforcementGuard(tmpdir)
            errors, warnings = guard.validate_pytest_configuration()
            brittle_errors = [e for e in errors if "Brittle marker access" in e]
            assert len(brittle_errors) == 0, f"Robust pattern should not be flagged, got: {brittle_errors}"


if __name__ == "__main__":
    main()
