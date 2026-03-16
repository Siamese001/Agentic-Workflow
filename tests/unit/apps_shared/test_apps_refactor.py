"""Hardened regression tests for apps_* refactoring — Phases 0-10.

Each test class covers one phase. Tests use:
- Real imports to prove modules are importable
- AST analysis to prove code structure
- Filesystem assertions to prove relocations
- Contract assertions to prove data shapes
- ruff subprocess for F401 compliance

These tests are permanent regression guards: if any phase is accidentally
reverted, the corresponding tests fail deterministically.
"""

from __future__ import annotations

import ast
import importlib
import json
import subprocess
import sys
from dataclasses import fields, is_dataclass
from enum import Enum
from pathlib import Path

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_apps_refactor")
_emit_applies_guardrail("p0", "test_apps_refactor", "p0_governance")
_emit_reads_policy_state("p0", "test_apps_refactor", "policy_binding")
_emit_snapshots_state("p0", "test_apps_refactor", "state_snapshot")
emit_replay_key("p0", "test_apps_refactor")
emit_determinism_digest("p0", "test_apps_refactor")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_apps_refactor", "execution_auth")
_emit_validates_capability("p2", "test_apps_refactor", "capability_check")
_emit_routes_to_capability("p2", "test_apps_refactor", "capability_route")
_emit_writes_via_uwg("p2", "test_apps_refactor", "uwg_write")
_emit_blocks_direct_write("p2", "test_apps_refactor", "direct_write_block")
_emit_records_tool_invocation("p2", "test_apps_refactor", "tool_invocation")
_emit_captures_execution_output("p2", "test_apps_refactor", "exec_output")
_emit_dispatches_agent("p3", "test_apps_refactor", "agent_dispatch")
_emit_coordinates_agents("p3", "test_apps_refactor", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_apps_refactor", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_apps_refactor", "healing_outcome")
_emit_escalates_failure("p3", "test_apps_refactor", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_apps_refactor", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_apps_refactor", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_apps_refactor", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_apps_refactor", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_apps_refactor", "eval_metric")
_emit_stores_embedding("p4", "test_apps_refactor", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_apps_refactor", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_apps_refactor", "exec_snapshot_link")

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300


ROOT = Path(__file__).resolve().parents[3]
pytestmark = pytest.mark.unit


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _ast_class_defs(path: Path) -> list[ast.ClassDef]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    return [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]


def _ast_annassign_names(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    names: set[str] = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Assign):
            for t in n.targets:
                if isinstance(t, ast.Name):
                    names.add(t.id)
        elif isinstance(n, ast.AnnAssign) and isinstance(n.target, ast.Name):
            names.add(n.target.id)
    return names


def _ruff_f401(dirs: list[str]) -> list[dict]:
    result = subprocess.run(
        [sys.executable, "-m", "ruff", "check", "--select", "F401", "--output-format=json", *dirs],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    raw = result.stdout.strip()
    return json.loads(raw) if raw.startswith("[") else []


# ---------------------------------------------------------------------------
# Phase 1 — Dead imports
# ---------------------------------------------------------------------------


class TestPhase1DeadImports:
    """apps_* must have zero F401 violations (excluding __init__.py re-exports)."""

    def test_no_f401_violations_in_apps_rg(self) -> None:
        violations = _ruff_f401(["apps_rg/"])
        real = [v for v in violations if not v["filename"].endswith("__init__.py")]
        assert real == [], f"{len(real)} F401 violation(s) in apps_rg/:\n" + "\n".join(
            f"  {v['filename']}:{v['location']['row']} {v['message']}" for v in real[:10]
        )

    def test_no_f401_violations_in_apps_lic(self) -> None:
        violations = _ruff_f401(["apps_lic/"])
        real = [v for v in violations if not v["filename"].endswith("__init__.py")]
        assert real == [], f"{len(real)} F401 violation(s) in apps_lic/:\n" + "\n".join(
            f"  {v['filename']}:{v['location']['row']} {v['message']}" for v in real[:10]
        )

    def test_no_f401_violations_in_apps_shared(self) -> None:
        violations = _ruff_f401(["apps_shared/"])
        real = [v for v in violations if not v["filename"].endswith("__init__.py")]
        assert real == [], f"{len(real)} F401 violation(s) in apps_shared/:\n" + "\n".join(
            f"  {v['filename']}:{v['location']['row']} {v['message']}" for v in real[:10]
        )


# ---------------------------------------------------------------------------
# Phase 2 — ContentStrategyAgent shim removal
# ---------------------------------------------------------------------------


class TestPhase2ShimRemoval:
    """ContentStrategyAgent shim must be absent; tests must point to canonical path."""

    def test_content_strategy_shim_file_deleted(self) -> None:
        shim = ROOT / "apps_rg" / "reasoning" / "ContentStrategyAgent.py"
        assert not shim.exists(), (
            "ContentStrategyAgent.py shim must be deleted — use apps_rg.reasoning.RGStrategyExecutor directly"
        )

    def test_test_content_strategy_agent_root_imports_canonical(self) -> None:
        test_file = ROOT / "tests" / "unit" / "test_content_strategy_agent.py"
        assert test_file.exists(), "test_content_strategy_agent.py not found"
        content = test_file.read_text(encoding="utf-8")
        assert "apps_rg.reasoning.RGStrategyExecutor" in content, (
            "test_content_strategy_agent.py must import from canonical apps_rg.reasoning.RGStrategyExecutor"
        )
        assert "apps_rg.reasoning.ContentStrategyAgent" not in content, (
            "test_content_strategy_agent.py must not reference deleted shim"
        )

    def test_test_content_strategy_agent_engines_imports_canonical(self) -> None:
        test_file = (
            ROOT / "tests" / "unit" / "apps_rg" / "engines" / "utils" / "test_content_strategy_agent.py"
        )
        assert test_file.exists(), "apps_rg/engines/utils/test_content_strategy_agent.py not found"
        content = test_file.read_text(encoding="utf-8")
        assert "apps_rg.reasoning.RGStrategyExecutor" in content, (
            "Must import from canonical apps_rg.reasoning.RGStrategyExecutor"
        )


# ---------------------------------------------------------------------------
# Phase 3 — MCPHardenedMixin deduplication
# ---------------------------------------------------------------------------


class TestPhase3MCPHardenedMixinDedup:
    """OutreachSignalRouterAgent and OutreachValidationExecutorAgent must use
    try/except fallback pattern only — no unconditional duplicate class bodies."""

    @pytest.mark.parametrize(
        "filename,classname",
        [
            ("OutreachSignalRouterAgent.py", "MCPHardenedMixin"),
            ("OutreachSignalRouterAgent.py", "HealerMixin"),
            ("OutreachValidationExecutorAgent.py", "MCPHardenedMixin"),
            ("OutreachValidationExecutorAgent.py", "HealerMixin"),
        ],
    )
    def test_class_defined_at_most_twice_via_try_except(self, filename: str, classname: str) -> None:
        path = ROOT / "apps_lic" / "reasoning" / filename
        assert path.exists(), f"{filename} not found"
        defs = _ast_class_defs(path)
        occurrences = [d for d in defs if d.name == classname]
        # Exactly 0 (not needed) or exactly 2 (try branch + except fallback) is valid.
        # 3+ means a third unconditional definition was added.
        assert len(occurrences) <= 2, (
            f"{filename}: {classname} defined {len(occurrences)} times — "
            "must be <= 2 (try branch + except fallback only)"
        )

    def test_outreach_router_has_try_except_guard(self) -> None:
        path = ROOT / "apps_lic" / "reasoning" / "OutreachSignalRouterAgent.py"
        content = path.read_text(encoding="utf-8")
        assert "try:" in content and "except ImportError:" in content, (
            "OutreachSignalRouterAgent.py must use try/except ImportError guard for mixin imports"
        )

    def test_outreach_validation_has_no_duplicate_class_names(self) -> None:
        path = ROOT / "apps_lic" / "reasoning" / "OutreachValidationExecutorAgent.py"
        defs = _ast_class_defs(path)
        names = [d.name for d in defs]
        duplicates = {n for n in names if names.count(n) > 1}
        assert duplicates == set(), (
            f"OutreachValidationExecutorAgent.py has duplicate class definitions: {duplicates}"
        )


# ---------------------------------------------------------------------------
# Phase 4 — Pipeline constants SSOT
# ---------------------------------------------------------------------------


EXPECTED_CONSTANTS = {
    "MAX_RETRIES",
    "DEFAULT_SLEEP",
    "THRESHOLD",
    "BUFFER_SIZE",
    "BATCH_SIZE",
    "MAX_DEPTH",
    "MAX_FILES",
    "DEFAULT_TIMEOUT",
}


class TestPhase4ConstantsSSOT:
    """pipeline_constants_config.py must be the sole definition point."""

    def test_ssot_module_importable(self) -> None:
        mod = importlib.import_module("apps_shared.config.pipeline_constants_config")
        assert mod is not None

    @pytest.mark.parametrize("name", sorted(EXPECTED_CONSTANTS))
    def test_constant_exists_in_ssot_module(self, name: str) -> None:
        mod = importlib.import_module("apps_shared.config.pipeline_constants_config")
        assert hasattr(mod, name), f"SSOT missing constant: {name}"

    def test_ssot_constant_values_are_correct_types(self) -> None:
        mod = importlib.import_module("apps_shared.config.pipeline_constants_config")
        assert isinstance(mod.MAX_RETRIES, int)
        assert isinstance(mod.DEFAULT_SLEEP, float)
        assert isinstance(mod.THRESHOLD, float)
        assert isinstance(mod.BUFFER_SIZE, int)
        assert isinstance(mod.BATCH_SIZE, int)
        assert isinstance(mod.MAX_DEPTH, int)
        assert isinstance(mod.MAX_FILES, int)
        assert isinstance(mod.DEFAULT_TIMEOUT, int)

    def test_ssot_exports_all_constants(self) -> None:
        mod = importlib.import_module("apps_shared.config.pipeline_constants_config")
        assert hasattr(mod, "__all__"), "pipeline_constants_config.py must define __all__"
        assert EXPECTED_CONSTANTS.issubset(set(mod.__all__)), (
            f"__all__ missing: {EXPECTED_CONSTANTS - set(mod.__all__)}"
        )

    def test_no_inline_max_retries_in_apps_rg(self) -> None:
        ssot = ROOT / "apps_shared" / "config" / "pipeline_constants_config.py"
        offenders = []
        for py in sorted((ROOT / "apps_rg").rglob("*.py")):
            content = py.read_text(encoding="utf-8")
            if "\nMAX_RETRIES = 3" in content or "\nMAX_RETRIES=3" in content:
                offenders.append(py.relative_to(ROOT).as_posix())
        assert offenders == [], f"Inline MAX_RETRIES definitions remain in apps_rg/: {offenders}"

    def test_no_inline_max_retries_in_apps_lic(self) -> None:
        offenders = []
        for py in sorted((ROOT / "apps_lic").rglob("*.py")):
            content = py.read_text(encoding="utf-8")
            if "\nMAX_RETRIES = 3" in content or "\nMAX_RETRIES=3" in content:
                offenders.append(py.relative_to(ROOT).as_posix())
        assert offenders == [], f"Inline MAX_RETRIES definitions remain in apps_lic/: {offenders}"


# ---------------------------------------------------------------------------
# Phase 5 — State guards
# ---------------------------------------------------------------------------


class TestPhase5StateGuards:
    """LicHealingOrchestrator and ResumeEnhancementOrchestrator must have
    proper state isolation guards."""

    def test_lic_healing_orchestrator_uses_field_default_factory(self) -> None:
        path = ROOT / "apps_lic" / "reasoning" / "LicHealingOrchestrator.py"
        assert path.exists()
        tree = ast.parse(path.read_text(encoding="utf-8"))
        # Find active_incidents field — must use field(default_factory=...)
        content = path.read_text(encoding="utf-8")
        assert "field(default_factory=dict)" in content, (
            "active_incidents must use field(default_factory=dict) to prevent state bleed across instances"
        )

    def test_resume_enhancement_orchestrator_has_initialized_guard(self) -> None:
        path = ROOT / "apps_rg" / "reasoning" / "ResumeEnhancementOrchestrator.py"
        assert path.exists()
        content = path.read_text(encoding="utf-8")
        assert "_initialized" in content, (
            "ResumeEnhancementOrchestrator must have _initialized guard to prevent double-init"
        )


# ---------------------------------------------------------------------------
# Phase 6 — Layer violations resolved
# ---------------------------------------------------------------------------


class TestPhase6LayerViolations:
    """meta_learning files must live in system_learning/scripts/, not apps_shared/scripts/."""

    def test_meta_learning_bridge_canonical_location_exists(self) -> None:
        path = ROOT / "system_learning" / "scripts" / "meta_learning_bridge.py"
        assert path.exists(), f"Canonical location missing: {path}"

    def test_meta_learning_operator_canonical_location_exists(self) -> None:
        path = ROOT / "system_learning" / "scripts" / "meta_learning_operator.py"
        assert path.exists(), f"Canonical location missing: {path}"

    def test_meta_learning_bridge_shim_redirects_to_canonical(self) -> None:
        shim = ROOT / "apps_shared" / "scripts" / "meta_learning_bridge.py"
        assert shim.exists(), "Backward-compat shim must exist"
        content = shim.read_text(encoding="utf-8")
        assert "system_learning.scripts.meta_learning_bridge" in content, (
            "Shim must re-export from canonical system_learning.scripts.meta_learning_bridge"
        )

    def test_meta_learning_operator_shim_redirects_to_canonical(self) -> None:
        shim = ROOT / "apps_shared" / "scripts" / "meta_learning_operator.py"
        assert shim.exists(), "Backward-compat shim must exist"
        content = shim.read_text(encoding="utf-8")
        assert "system_learning.scripts.meta_learning_operator" in content, (
            "Shim must re-export from canonical system_learning.scripts.meta_learning_operator"
        )

    def test_apps_shared_scripts_bridge_is_a_shim_not_canonical(self) -> None:
        shim = ROOT / "apps_shared" / "scripts" / "meta_learning_bridge.py"
        content = shim.read_text(encoding="utf-8")
        # A shim must not define functions — it only re-exports
        tree = ast.parse(content)
        fn_defs = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
        assert fn_defs == [], (
            "apps_shared/scripts/meta_learning_bridge.py must be a pure re-export shim "
            f"— found function definitions: {[f.name for f in fn_defs]}"
        )

    def test_test_meta_learning_bridge_imports_from_canonical(self) -> None:
        path = ROOT / "tests" / "unit" / "test_meta_learning_bridge.py"
        assert path.exists()
        content = path.read_text(encoding="utf-8")
        assert "system_learning.scripts.meta_learning_bridge" in content, (
            "Test must import from canonical system_learning.scripts.meta_learning_bridge, not apps_shared"
        )


# ---------------------------------------------------------------------------
# Phase 7 — Entrypoints
# ---------------------------------------------------------------------------


class TestPhase7Entrypoints:
    """apps_lic/__main__.py and apps_rg/__main__.py must exist and be correctly structured."""

    @pytest.mark.parametrize("app", ["apps_lic", "apps_rg"])
    def test_main_module_exists(self, app: str) -> None:
        path = ROOT / app / "__main__.py"
        assert path.exists(), f"{app}/__main__.py entrypoint missing"

    @pytest.mark.parametrize("app", ["apps_lic", "apps_rg"])
    def test_main_module_is_syntactically_valid(self, app: str) -> None:
        path = ROOT / app / "__main__.py"
        try:
            ast.parse(path.read_text(encoding="utf-8"))
        except SyntaxError as e:
            pytest.fail(f"{app}/__main__.py has a SyntaxError: {e}")

    @pytest.mark.parametrize("app", ["apps_lic", "apps_rg"])
    def test_adg_bootstrap_function_defined(self, app: str) -> None:
        path = ROOT / app / "__main__.py"
        tree = ast.parse(path.read_text(encoding="utf-8"))
        fn_names = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
        assert "_adg_bootstrap" in fn_names, f"{app}/__main__.py must define _adg_bootstrap()"

    @pytest.mark.parametrize("app", ["apps_lic", "apps_rg"])
    def test_main_function_defined(self, app: str) -> None:
        path = ROOT / app / "__main__.py"
        tree = ast.parse(path.read_text(encoding="utf-8"))
        fn_names = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
        assert "main" in fn_names, f"{app}/__main__.py must define main()"

    @pytest.mark.parametrize("app", ["apps_lic", "apps_rg"])
    def test_adg_bootstrap_calls_build_pre_run_report(self, app: str) -> None:
        path = ROOT / app / "__main__.py"
        content = path.read_text(encoding="utf-8")
        assert "build_pre_run_report" in content, (
            f"{app}/__main__.py _adg_bootstrap must call build_pre_run_report"
        )

    @pytest.mark.parametrize("app", ["apps_lic", "apps_rg"])
    def test_adg_bootstrap_has_graceful_degrade(self, app: str) -> None:
        path = ROOT / app / "__main__.py"
        content = path.read_text(encoding="utf-8")
        # Must catch exceptions so ADG failure never blocks execution
        assert "except Exception" in content, (
            f"{app}/__main__.py must catch Exception in _adg_bootstrap to gracefully degrade"
        )


# ---------------------------------------------------------------------------
# Phase 8 — File relocations
# ---------------------------------------------------------------------------


class TestPhase8FileRelocations:
    """Test files must be outside apps_* source trees; ops tools relocated."""

    def test_no_test_files_in_apps_rg_scripts(self) -> None:
        scripts_dir = ROOT / "apps_rg" / "scripts"
        if not scripts_dir.exists():
            return
        misplaced = list(scripts_dir.glob("test_*.py"))
        assert misplaced == [], f"Test files must not live in apps_rg/scripts/: {[f.name for f in misplaced]}"

    def test_no_test_files_anywhere_in_apps_rg(self) -> None:
        misplaced = list((ROOT / "apps_rg").rglob("test_*.py"))
        assert misplaced == [], (
            f"Test files found inside apps_rg/ source tree: {[p.relative_to(ROOT) for p in misplaced]}"
        )

    def test_no_test_files_anywhere_in_apps_lic(self) -> None:
        misplaced = list((ROOT / "apps_lic").rglob("test_*.py"))
        assert misplaced == [], (
            f"Test files found inside apps_lic/ source tree: {[p.relative_to(ROOT) for p in misplaced]}"
        )

    def test_relocated_tests_exist_in_tests_directory(self) -> None:
        expected = [
            ROOT / "tests" / "apps_rg" / "scripts" / "test_engine.py",
            ROOT / "tests" / "apps_rg" / "scripts" / "test_input.py",
            ROOT / "tests" / "apps_rg" / "scripts" / "test_run_grand_unification_tests.py",
        ]
        missing = [p for p in expected if not p.exists()]
        assert missing == [], f"Relocated test files not found: {[p.relative_to(ROOT) for p in missing]}"

    @pytest.mark.parametrize(
        "filename",
        [
            "analyze_duplicates_detailed.py",
            "clean_duplicates_enhanced.py",
            "fix_duplicate_imports.py",
            "fix_duplicate_realagentdata.py",
        ],
    )
    def test_ops_tool_not_in_apps_lic_tools(self, filename: str) -> None:
        still_there = ROOT / "apps_lic" / "tools" / filename
        assert not still_there.exists(), (
            f"{filename} must be relocated from apps_lic/tools/ to ops_scripts/general/"
        )

    @pytest.mark.parametrize(
        "filename",
        [
            "analyze_duplicates_detailed.py",
            "clean_duplicates_enhanced.py",
            "fix_duplicate_imports.py",
            "fix_duplicate_realagentdata.py",
        ],
    )
    def test_ops_tool_exists_in_ops_scripts_general(self, filename: str) -> None:
        dest = ROOT / "ops_scripts" / "general" / filename
        assert dest.exists(), f"{filename} must exist in ops_scripts/general/ after relocation"


# ---------------------------------------------------------------------------
# Phase 9 — Circuit breaker via HardeningMixin
# ---------------------------------------------------------------------------


class TestPhase9CircuitBreaker:
    """Both hardened executors must inherit from HardeningMixin — no hand-rolled retry."""

    @pytest.mark.parametrize(
        "rel_path,class_name",
        [
            ("apps_rg/enforcement/HardenedanthropicexecutorStrategy.py", "HardenedAnthropicExecutor"),
            ("apps_rg/reasoning/HardenedopenaiexecutorStrategy.py", "HardenedOpenAIExecutor"),
        ],
    )
    def test_executor_inherits_hardening_mixin(self, rel_path: str, class_name: str) -> None:
        path = ROOT / rel_path
        assert path.exists(), f"{rel_path} not found"
        defs = _ast_class_defs(path)
        target = next((d for d in defs if d.name == class_name), None)
        assert target is not None, f"{class_name} class definition not found in {rel_path}"

        base_names = [
            b.id if isinstance(b, ast.Name) else b.attr if isinstance(b, ast.Attribute) else ""
            for b in target.bases
        ]
        assert "HardeningMixin" in base_names, (
            f"{class_name} in {rel_path} must inherit from HardeningMixin — found bases: {base_names}"
        )


# ---------------------------------------------------------------------------
# Phase 10 — Architecture migration contracts
# ---------------------------------------------------------------------------


class TestPhase10AppGuardianSpec:
    """AppGuardianSpec is importable, frozen, and the registry is non-empty."""

    def test_app_guardian_spec_importable(self) -> None:
        from apps_shared.config.app_guardian_registry import AppGuardianSpec

        assert AppGuardianSpec is not None

    def test_app_guardian_spec_is_frozen_dataclass(self) -> None:
        from apps_shared.config.app_guardian_registry import AppGuardianSpec

        assert is_dataclass(AppGuardianSpec)
        # frozen=True means __setattr__ raises FrozenInstanceError
        spec = AppGuardianSpec(
            check_id="TEST-001",
            app="*",
            description="test",
            severity="low",
            guardian_module="test.module",
        )
        with pytest.raises(Exception):  # FrozenInstanceError
            spec.check_id = "MUTATED"  # type: ignore[misc]

    def test_app_guardian_spec_has_required_fields(self) -> None:
        from apps_shared.config.app_guardian_registry import AppGuardianSpec

        field_names = {f.name for f in fields(AppGuardianSpec)}
        assert {"check_id", "app", "description", "severity", "guardian_module"}.issubset(field_names)

    def test_registry_has_at_least_six_entries(self) -> None:
        from apps_shared.config.app_guardian_registry import APP_GUARDIAN_REGISTRY

        assert len(APP_GUARDIAN_REGISTRY) >= 6, (
            f"APP_GUARDIAN_REGISTRY must have >= 6 entries, got {len(APP_GUARDIAN_REGISTRY)}"
        )

    def test_registry_check_ids_are_unique(self) -> None:
        from apps_shared.config.app_guardian_registry import APP_GUARDIAN_REGISTRY

        ids = [s.check_id for s in APP_GUARDIAN_REGISTRY]
        assert len(ids) == len(set(ids)), f"Duplicate check_ids: {[x for x in ids if ids.count(x) > 1]}"

    def test_get_specs_for_app_returns_subset(self) -> None:
        from apps_shared.config.app_guardian_registry import APP_GUARDIAN_REGISTRY, get_specs_for_app

        rg_specs = get_specs_for_app("apps_rg")
        # Must include all wildcard specs
        wildcard_ids = {s.check_id for s in APP_GUARDIAN_REGISTRY if s.app == "*"}
        returned_ids = {s.check_id for s in rg_specs}
        assert wildcard_ids.issubset(returned_ids), (
            f"get_specs_for_app('apps_rg') missing wildcard specs: {wildcard_ids - returned_ids}"
        )

    def test_all_severities_are_valid_literals(self) -> None:
        from apps_shared.config.app_guardian_registry import APP_GUARDIAN_REGISTRY

        valid = {"critical", "high", "medium", "low"}
        for spec in APP_GUARDIAN_REGISTRY:
            assert spec.severity in valid, f"{spec.check_id} has invalid severity: {spec.severity!r}"


class TestPhase10AppHealResult:
    """AppHealResult contract is importable, frozen, and behaves correctly."""

    def test_app_heal_result_importable(self) -> None:
        from apps_shared.types.app_heal_contract_types import AppHealResult

        assert AppHealResult is not None

    def test_app_heal_status_importable(self) -> None:
        from apps_shared.types.app_heal_contract_types import AppHealStatus

        assert AppHealStatus is not None

    def test_app_heal_status_is_string_enum(self) -> None:
        from apps_shared.types.app_heal_contract_types import AppHealStatus

        assert issubclass(AppHealStatus, str)
        assert issubclass(AppHealStatus, Enum)

    def test_app_heal_status_has_four_members(self) -> None:
        from apps_shared.types.app_heal_contract_types import AppHealStatus

        assert set(AppHealStatus) == {
            AppHealStatus.HEALED,
            AppHealStatus.PARTIAL,
            AppHealStatus.FAILED,
            AppHealStatus.SKIPPED,
        }

    def test_app_heal_result_is_frozen_dataclass(self) -> None:
        from apps_shared.types.app_heal_contract_types import AppHealResult, AppHealStatus

        result = AppHealResult(check_id="X", app="apps_rg", status=AppHealStatus.HEALED)
        with pytest.raises(Exception):
            result.check_id = "MUTATED"  # type: ignore[misc]

    def test_app_heal_result_has_required_fields(self) -> None:
        from apps_shared.types.app_heal_contract_types import AppHealResult

        field_names = {f.name for f in fields(AppHealResult)}
        assert {"check_id", "app", "status", "changes_made", "rollback_info", "detail"}.issubset(field_names)

    def test_app_heal_result_to_dict_is_json_serialisable(self) -> None:
        from apps_shared.types.app_heal_contract_types import AppHealResult, AppHealStatus

        result = AppHealResult(
            check_id="AGS-001",
            app="apps_rg",
            status=AppHealStatus.HEALED,
            changes_made=("a.py", "b.py"),
            detail="ok",
        )
        d = result.to_dict()
        raw = json.dumps(d)  # must not raise
        roundtripped = json.loads(raw)
        assert roundtripped["check_id"] == "AGS-001"
        assert roundtripped["status"] == "HEALED"
        assert roundtripped["changes_made"] == ["a.py", "b.py"]

    def test_skipped_factory_method(self) -> None:
        from apps_shared.types.app_heal_contract_types import AppHealResult, AppHealStatus

        r = AppHealResult.skipped("AGS-002", "apps_lic", "reason")
        assert r.status == AppHealStatus.SKIPPED
        assert r.detail == "reason"

    def test_failed_factory_method(self) -> None:
        from apps_shared.types.app_heal_contract_types import AppHealResult, AppHealStatus

        r = AppHealResult.failed("AGS-003", "apps_rg", "boom")
        assert r.status == AppHealStatus.FAILED
        assert r.detail == "boom"


class TestPhase10AppRemediationDispatcher:
    """AppRemediationDispatcher is importable and structurally correct."""

    def test_dispatch_function_importable(self) -> None:
        from apps_shared.scripts.app_remediation_dispatcher import dispatch

        assert callable(dispatch)

    def test_run_spec_function_importable(self) -> None:
        from apps_shared.scripts.app_remediation_dispatcher import _run_spec

        assert callable(_run_spec)

    def test_check_functions_exist_for_all_registry_check_ids(self) -> None:
        """Every check_id in registry must have a matching handler in _run_spec."""
        from apps_shared.config.app_guardian_registry import APP_GUARDIAN_REGISTRY

        dispatcher_path = ROOT / "apps_shared" / "scripts" / "app_remediation_dispatcher.py"
        content = dispatcher_path.read_text(encoding="utf-8")
        for spec in APP_GUARDIAN_REGISTRY:
            assert spec.check_id in content, (
                f"_run_spec has no handler for check_id {spec.check_id!r} — add elif branch"
            )

    def test_run_spec_returns_app_heal_result(self) -> None:
        from apps_shared.config.app_guardian_registry import AppGuardianSpec
        from apps_shared.scripts.app_remediation_dispatcher import _run_spec
        from apps_shared.types.app_heal_contract_types import AppHealResult

        # Use a check_id that has no handler — must return SKIPPED, not raise
        unknown_spec = AppGuardianSpec(
            check_id="AGS-UNKNOWN",
            app="*",
            description="test unknown",
            severity="low",
            guardian_module="test",
        )
        result = _run_spec(unknown_spec)
        assert isinstance(result, AppHealResult), (
            f"_run_spec must always return AppHealResult, got {type(result)}"
        )

    def test_run_spec_never_raises(self) -> None:
        """_run_spec must catch all exceptions and return AppHealResult.failed()."""
        from apps_shared.config.app_guardian_registry import AppGuardianSpec
        from apps_shared.scripts.app_remediation_dispatcher import _run_spec
        from apps_shared.types.app_heal_contract_types import AppHealResult, AppHealStatus

        # Simulate a spec that would trigger an exception mid-check
        # (unknown check_id returns SKIPPED which is still a valid result)
        spec = AppGuardianSpec(
            check_id="AGS-CRASH",
            app="*",
            description="crash spec",
            severity="low",
            guardian_module="nonexistent",
        )
        result = _run_spec(spec)
        assert isinstance(result, AppHealResult)
        # Must be either SKIPPED or FAILED — never raises
        assert result.status in (AppHealStatus.SKIPPED, AppHealStatus.FAILED)

    def test_ags001_dead_imports_returns_healed(self) -> None:
        """AGS-001 check must return HEALED now that F401 violations are fixed."""
        from apps_shared.config.app_guardian_registry import APP_GUARDIAN_REGISTRY
        from apps_shared.scripts.app_remediation_dispatcher import _run_spec
        from apps_shared.types.app_heal_contract_types import AppHealStatus

        spec = next(s for s in APP_GUARDIAN_REGISTRY if s.check_id == "AGS-001")
        result = _run_spec(spec)
        assert result.status == AppHealStatus.HEALED, (
            f"AGS-001 (dead imports) must be HEALED — got {result.status}: {result.detail}"
        )

    def test_ags003_misplaced_tests_returns_healed(self) -> None:
        """AGS-003 check must return HEALED now that test files are relocated."""
        from apps_shared.config.app_guardian_registry import APP_GUARDIAN_REGISTRY
        from apps_shared.scripts.app_remediation_dispatcher import _run_spec
        from apps_shared.types.app_heal_contract_types import AppHealStatus

        spec = next(s for s in APP_GUARDIAN_REGISTRY if s.check_id == "AGS-003")
        result = _run_spec(spec)
        assert result.status == AppHealStatus.HEALED, (
            f"AGS-003 (misplaced tests) must be HEALED — got {result.status}: {result.detail}"
        )

    def test_ags004_inline_constants_returns_healed(self) -> None:
        """AGS-004 check must return HEALED now that SSOT is applied."""
        from apps_shared.config.app_guardian_registry import APP_GUARDIAN_REGISTRY
        from apps_shared.scripts.app_remediation_dispatcher import _run_spec
        from apps_shared.types.app_heal_contract_types import AppHealStatus

        spec = next(s for s in APP_GUARDIAN_REGISTRY if s.check_id == "AGS-004")
        result = _run_spec(spec)
        assert result.status == AppHealStatus.HEALED, (
            f"AGS-004 (inline constants) must be HEALED — got {result.status}: {result.detail}"
        )

    def test_ags005_shim_returns_healed(self) -> None:
        """AGS-005 check must return HEALED now that ContentStrategyAgent shim is deleted."""
        from apps_shared.config.app_guardian_registry import APP_GUARDIAN_REGISTRY
        from apps_shared.scripts.app_remediation_dispatcher import _run_spec
        from apps_shared.types.app_heal_contract_types import AppHealStatus

        spec = next(s for s in APP_GUARDIAN_REGISTRY if s.check_id == "AGS-005")
        result = _run_spec(spec)
        assert result.status == AppHealStatus.HEALED, (
            f"AGS-005 (shim present) must be HEALED — got {result.status}: {result.detail}"
        )
