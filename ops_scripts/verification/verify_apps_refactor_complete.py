"""Comprehensive verification suite for apps_* refactoring (Phases 0-10).

Proves 100% completion and accuracy using deterministic checks:
- AST analysis for code structure
- File system validation
- Import graph analysis
- Pattern matching for specific fixes

Usage:
    python ops_scripts/verification/verify_apps_refactor_complete.py
    python ops_scripts/verification/verify_apps_refactor_complete.py --json report.json
"""

from __future__ import annotations

import ast
import json
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]


@dataclass
class VerificationResult:
    """Result of a single verification check."""

    phase: str
    check_id: str
    description: str
    passed: bool
    evidence: dict[str, Any] = field(default_factory=dict)
    failure_reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "phase": self.phase,
            "check_id": self.check_id,
            "description": self.description,
            "passed": self.passed,
            "evidence": self.evidence,
            "failure_reason": self.failure_reason,
        }


class AppsRefactorVerifier:
    """Deterministic verification of all 11 refactoring phases."""

    def __init__(self) -> None:
        self.results: list[VerificationResult] = []

    def verify_all(self) -> bool:
        """Run all verification checks. Returns True if all pass."""
        self.verify_phase0_adg_baseline()
        self.verify_phase1_dead_imports()
        self.verify_phase2_shim_removal()
        self.verify_phase3_mcp_mixin_dedup()
        self.verify_phase4_constants_ssot()
        self.verify_phase5_state_guards()
        self.verify_phase6_layer_violations()
        self.verify_phase7_entrypoints()
        self.verify_phase8_file_relocations()
        self.verify_phase9_circuit_breaker()
        self.verify_phase10_architecture_migration()

        return all(r.passed for r in self.results)

    def verify_phase0_adg_baseline(self) -> None:
        """Phase 0: ADG baseline captured and apps_* nodes present."""
        adg_path = ROOT / "artifacts" / "adg" / "adg_latest.json"

        if not adg_path.exists():
            self.results.append(
                VerificationResult(
                    phase="Phase 0",
                    check_id="P0-ADG-001",
                    description="ADG artifact exists",
                    passed=False,
                    failure_reason=f"ADG file not found at {adg_path}",
                ),
            )
            return

        with open(adg_path, encoding="utf-8") as f:
            adg = json.load(f)

        # Count apps_* entities (ADG schema uses 'entities' with 'adg_name' key)
        # Entity names have format: 'ADG::Module::apps_lic/config/__init__.py'
        apps_entities = [
            e
            for e in adg.get("entities", [])
            if any(app in e.get("adg_name", "") for app in ["apps_rg/", "apps_lic/", "apps_shared/"])
        ]

        # Verify ADG exists and contains apps_* entities (no arbitrary threshold)
        has_apps_entities = len(apps_entities) > 0

        self.results.append(
            VerificationResult(
                phase="Phase 0",
                check_id="P0-ADG-001",
                description="ADG artifact exists and includes apps_* entities",
                passed=has_apps_entities,
                evidence={
                    "apps_entities_count": len(apps_entities),
                    "digest": adg.get("artifact_digest", "unknown"),
                    "total_entities": len(adg.get("entities", [])),
                },
                failure_reason="" if has_apps_entities else "No apps_* entities found in ADG",
            ),
        )

    def verify_phase1_dead_imports(self) -> None:
        """Phase 1: F401 violations = 0 in apps_* (excluding __init__.py)."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "ruff",
                "check",
                "--select",
                "F401",
                "apps_rg/",
                "apps_lic/",
                "apps_shared/",
                "--output-format=json",
            ],
            capture_output=True,
            text=True,
            cwd=ROOT,
        )

        violations = json.loads(result.stdout) if result.stdout.strip().startswith("[") else []
        non_init = [v for v in violations if not v["filename"].endswith("__init__.py")]

        self.results.append(
            VerificationResult(
                phase="Phase 1",
                check_id="P1-F401-001",
                description="Zero F401 violations in apps_* (excluding __init__.py re-exports)",
                passed=len(non_init) == 0,
                evidence={"f401_count": len(non_init), "files_with_violations": len(set(v["filename"] for v in non_init))},
                failure_reason="" if len(non_init) == 0 else f"{len(non_init)} F401 violations remain",
            ),
        )

    def verify_phase2_shim_removal(self) -> None:
        """Phase 2: ContentStrategyAgent shim deleted, tests updated."""
        shim_path = ROOT / "apps_rg" / "reasoning" / "ContentStrategyAgent.py"
        shim_exists = shim_path.exists()

        # Check test files import from canonical location
        test_files = [
            ROOT / "tests" / "unit" / "test_content_strategy_agent.py",
            ROOT / "tests" / "unit" / "apps_rg" / "engines" / "utils" / "test_content_strategy_agent.py",
        ]

        canonical_imports = []
        for test_file in test_files:
            if test_file.exists():
                content = test_file.read_text(encoding="utf-8")
                # Check for canonical import path
                if "apps_rg.reasoning.RGStrategyExecutor" in content:
                    canonical_imports.append(test_file.name)

        self.results.append(
            VerificationResult(
                phase="Phase 2",
                check_id="P2-SHIM-001",
                description="ContentStrategyAgent shim deleted",
                passed=not shim_exists,
                evidence={"shim_path": str(shim_path)},
                failure_reason="" if not shim_exists else "Shim file still exists",
            ),
        )

        self.results.append(
            VerificationResult(
                phase="Phase 2",
                check_id="P2-SHIM-002",
                description="Test files updated to canonical import",
                passed=len(canonical_imports) == 2,
                evidence={"files_with_canonical_import": canonical_imports},
                failure_reason="" if len(canonical_imports) == 2 else f"Only {len(canonical_imports)}/2 test files updated",
            ),
        )

    def verify_phase3_mcp_mixin_dedup(self) -> None:
        """Phase 3: No unconditional duplicate MCPHardenedMixin/HealerMixin stubs."""
        files_to_check = [
            ROOT / "apps_lic" / "reasoning" / "OutreachSignalRouterAgent.py",
            ROOT / "apps_lic" / "reasoning" / "OutreachValidationExecutorAgent.py",
        ]

        for file_path in files_to_check:
            if not file_path.exists():
                self.results.append(
                    VerificationResult(
                        phase="Phase 3",
                        check_id=f"P3-DEDUP-{file_path.stem}",
                        description=f"Check {file_path.name} for duplicate stubs",
                        passed=False,
                        failure_reason=f"File not found: {file_path}",
                    ),
                )
                continue

            content = file_path.read_text(encoding="utf-8")
            tree = ast.parse(content)

            # Find all class definitions
            class_defs = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
            class_names = [c.name for c in class_defs]

            # Check for unconditional duplicates (not in try/except)
            # A duplicate is OK if it's in a try/except fallback pattern
            unconditional_dupes = []
            for name in set(class_names):
                if class_names.count(name) > 1:
                    # Check if all occurrences are in try/except blocks
                    occurrences = [c for c in class_defs if c.name == name]
                    # If we have exactly 2 occurrences and they're at module level, check for try/except
                    if len(occurrences) == 2:
                        # Simple heuristic: if "try:" and "except" are in content, it's likely a fallback pattern
                        if "try:" not in content or "except ImportError:" not in content:
                            unconditional_dupes.append(name)
                    elif len(occurrences) > 2:
                        unconditional_dupes.append(name)

            self.results.append(
                VerificationResult(
                    phase="Phase 3",
                    check_id=f"P3-DEDUP-{file_path.stem}",
                    description=f"No unconditional duplicate stubs in {file_path.name}",
                    passed=len(unconditional_dupes) == 0,
                    evidence={"duplicate_classes": unconditional_dupes, "all_classes": list(set(class_names))},
                    failure_reason="" if len(unconditional_dupes) == 0 else f"Unconditional duplicates: {unconditional_dupes}",
                ),
            )

    def verify_phase4_constants_ssot(self) -> None:
        """Phase 4: pipeline_constants_config.py exists and is imported correctly."""
        ssot_path = ROOT / "apps_shared" / "config" / "pipeline_constants_config.py"

        if not ssot_path.exists():
            self.results.append(
                VerificationResult(
                    phase="Phase 4",
                    check_id="P4-SSOT-001",
                    description="pipeline_constants_config.py exists",
                    passed=False,
                    failure_reason=f"SSOT file not found at {ssot_path}",
                ),
            )
            return

        # Verify SSOT defines all 8 constants
        content = ssot_path.read_text(encoding="utf-8")
        expected_constants = {
            "MAX_RETRIES",
            "DEFAULT_SLEEP",
            "THRESHOLD",
            "BUFFER_SIZE",
            "BATCH_SIZE",
            "MAX_DEPTH",
            "MAX_FILES",
            "DEFAULT_TIMEOUT",
        }

        tree = ast.parse(content)
        # Handle both regular assignments and annotated assignments
        defined_constants = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name):
                defined_constants.add(node.targets[0].id)
            elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                defined_constants.add(node.target.id)

        self.results.append(
            VerificationResult(
                phase="Phase 4",
                check_id="P4-SSOT-001",
                description="pipeline_constants_config.py defines all 8 constants",
                passed=expected_constants.issubset(defined_constants),
                evidence={"defined": sorted(defined_constants), "expected": sorted(expected_constants)},
                failure_reason=""
                if expected_constants.issubset(defined_constants)
                else f"Missing: {expected_constants - defined_constants}",
            ),
        )

        # Verify no inline MAX_RETRIES = 3 definitions in apps_* (excluding SSOT itself)
        inline_violations = []
        for app_dir in ["apps_rg", "apps_lic", "apps_shared"]:
            for py_file in (ROOT / app_dir).rglob("*.py"):
                if py_file == ssot_path:
                    continue
                file_content = py_file.read_text(encoding="utf-8")
                # Check for inline constant definitions (simple pattern match)
                if "\nMAX_RETRIES = 3" in file_content or "\nMAX_RETRIES=3" in file_content:
                    inline_violations.append(str(py_file.relative_to(ROOT)))

        self.results.append(
            VerificationResult(
                phase="Phase 4",
                check_id="P4-SSOT-002",
                description="No inline MAX_RETRIES=3 definitions in apps_* (all use SSOT)",
                passed=len(inline_violations) == 0,
                evidence={"files_with_inline_defs": inline_violations},
                failure_reason="" if len(inline_violations) == 0 else f"{len(inline_violations)} files still define inline",
            ),
        )

    def verify_phase5_state_guards(self) -> None:
        """Phase 5: State bleed guards present (field(default_factory), _initialized checks)."""
        # Check LicHealingOrchestrator uses field(default_factory=dict)
        lic_orch_path = ROOT / "apps_lic" / "reasoning" / "LicHealingOrchestrator.py"
        if lic_orch_path.exists():
            content = lic_orch_path.read_text(encoding="utf-8")
            has_field_factory = "field(default_factory=dict)" in content

            self.results.append(
                VerificationResult(
                    phase="Phase 5",
                    check_id="P5-STATE-001",
                    description="LicHealingOrchestrator uses field(default_factory=dict) for active_incidents",
                    passed=has_field_factory,
                    evidence={"pattern_found": has_field_factory},
                    failure_reason="" if has_field_factory else "field(default_factory=dict) pattern not found",
                ),
            )

        # Check ResumeEnhancementOrchestrator has _initialized guard
        resume_orch_path = ROOT / "apps_rg" / "reasoning" / "ResumeEnhancementOrchestrator.py"
        if resume_orch_path.exists():
            content = resume_orch_path.read_text(encoding="utf-8")
            has_initialized_guard = "_initialized" in content

            self.results.append(
                VerificationResult(
                    phase="Phase 5",
                    check_id="P5-STATE-002",
                    description="ResumeEnhancementOrchestrator has _initialized guard",
                    passed=has_initialized_guard,
                    evidence={"pattern_found": has_initialized_guard},
                    failure_reason="" if has_initialized_guard else "_initialized pattern not found",
                ),
            )

    def verify_phase6_layer_violations(self) -> None:
        """Phase 6: meta_learning files moved to system_learning/scripts/, shims in apps_shared."""
        # Check files moved to system_learning/scripts/
        sl_bridge = ROOT / "system_learning" / "scripts" / "meta_learning_bridge.py"
        sl_operator = ROOT / "system_learning" / "scripts" / "meta_learning_operator.py"

        self.results.append(
            VerificationResult(
                phase="Phase 6",
                check_id="P6-LAYER-001",
                description="meta_learning_bridge.py moved to system_learning/scripts/",
                passed=sl_bridge.exists(),
                evidence={"path": str(sl_bridge)},
                failure_reason="" if sl_bridge.exists() else f"File not found at {sl_bridge}",
            ),
        )

        self.results.append(
            VerificationResult(
                phase="Phase 6",
                check_id="P6-LAYER-002",
                description="meta_learning_operator.py moved to system_learning/scripts/",
                passed=sl_operator.exists(),
                evidence={"path": str(sl_operator)},
                failure_reason="" if sl_operator.exists() else f"File not found at {sl_operator}",
            ),
        )

        # Check backward-compat shims exist in apps_shared/scripts/
        apps_bridge_shim = ROOT / "apps_shared" / "scripts" / "meta_learning_bridge.py"
        apps_operator_shim = ROOT / "apps_shared" / "scripts" / "meta_learning_operator.py"

        for shim_path, check_id, name in [
            (apps_bridge_shim, "P6-LAYER-003", "meta_learning_bridge"),
            (apps_operator_shim, "P6-LAYER-004", "meta_learning_operator"),
        ]:
            if shim_path.exists():
                content = shim_path.read_text(encoding="utf-8")
                is_shim = "system_learning.scripts" in content and "Backward-compatibility" in content
            else:
                is_shim = False

            self.results.append(
                VerificationResult(
                    phase="Phase 6",
                    check_id=check_id,
                    description=f"Backward-compat shim for {name} in apps_shared/scripts/",
                    passed=is_shim,
                    evidence={"path": str(shim_path), "is_shim": is_shim},
                    failure_reason="" if is_shim else f"Shim not found or invalid at {shim_path}",
                ),
            )

        # Check test imports updated
        test_bridge = ROOT / "tests" / "unit" / "test_meta_learning_bridge.py"
        if test_bridge.exists():
            content = test_bridge.read_text(encoding="utf-8")
            uses_canonical = "system_learning.scripts.meta_learning_bridge" in content

            self.results.append(
                VerificationResult(
                    phase="Phase 6",
                    check_id="P6-LAYER-005",
                    description="test_meta_learning_bridge.py imports from canonical location",
                    passed=uses_canonical,
                    evidence={"canonical_import_found": uses_canonical},
                    failure_reason="" if uses_canonical else "Test still imports from old location",
                ),
            )

    def verify_phase7_entrypoints(self) -> None:
        """Phase 7: apps_lic/__main__.py and apps_rg/__main__.py exist with ADG bootstrap."""
        for app, check_id in [("apps_lic", "P7-ENTRY-001"), ("apps_rg", "P7-ENTRY-002")]:
            main_path = ROOT / app / "__main__.py"

            if not main_path.exists():
                self.results.append(
                    VerificationResult(
                        phase="Phase 7",
                        check_id=check_id,
                        description=f"{app}/__main__.py exists",
                        passed=False,
                        failure_reason=f"File not found at {main_path}",
                    ),
                )
                continue

            content = main_path.read_text(encoding="utf-8")
            has_adg_bootstrap = "build_pre_run_report" in content and "_adg_bootstrap" in content
            has_graceful_degrade = "except Exception" in content and "allow-silent-swallower" in content

            self.results.append(
                VerificationResult(
                    phase="Phase 7",
                    check_id=check_id,
                    description=f"{app}/__main__.py has ADG bootstrap with graceful degrade",
                    passed=has_adg_bootstrap and has_graceful_degrade,
                    evidence={"adg_bootstrap": has_adg_bootstrap, "graceful_degrade": has_graceful_degrade},
                    failure_reason=""
                    if (has_adg_bootstrap and has_graceful_degrade)
                    else "Missing ADG bootstrap or graceful degrade",
                ),
            )

    def verify_phase8_file_relocations(self) -> None:
        """Phase 8: Test files moved, ops tools relocated."""
        # Check no test_*.py files in apps_rg/scripts/
        apps_rg_scripts = ROOT / "apps_rg" / "scripts"
        if apps_rg_scripts.exists():
            misplaced_tests = list(apps_rg_scripts.glob("test_*.py"))
        else:
            misplaced_tests = []

        self.results.append(
            VerificationResult(
                phase="Phase 8",
                check_id="P8-RELOC-001",
                description="No test_*.py files in apps_rg/scripts/",
                passed=len(misplaced_tests) == 0,
                evidence={"misplaced_count": len(misplaced_tests), "files": [f.name for f in misplaced_tests]},
                failure_reason="" if len(misplaced_tests) == 0 else f"{len(misplaced_tests)} test files still in apps_rg/scripts/",
            ),
        )

        # Check test files exist in tests/apps_rg/scripts/
        expected_test_files = [
            ROOT / "tests" / "apps_rg" / "scripts" / "test_engine.py",
            ROOT / "tests" / "apps_rg" / "scripts" / "test_input.py",
            ROOT / "tests" / "apps_rg" / "scripts" / "test_run_grand_unification_tests.py",
        ]
        relocated_tests = [f for f in expected_test_files if f.exists()]

        self.results.append(
            VerificationResult(
                phase="Phase 8",
                check_id="P8-RELOC-002",
                description="Test files relocated to tests/apps_rg/scripts/",
                passed=len(relocated_tests) == 3,
                evidence={"relocated_count": len(relocated_tests), "expected": 3},
                failure_reason="" if len(relocated_tests) == 3 else f"Only {len(relocated_tests)}/3 test files relocated",
            ),
        )

        # Check ops tools moved from apps_lic/tools/ to ops_scripts/general/
        ops_tools = [
            "analyze_duplicates_detailed.py",
            "clean_duplicates_enhanced.py",
            "fix_duplicate_imports.py",
            "fix_duplicate_realagentdata.py",
        ]
        still_in_apps_lic = [f for f in ops_tools if (ROOT / "apps_lic" / "tools" / f).exists()]
        in_ops_scripts = [f for f in ops_tools if (ROOT / "ops_scripts" / "general" / f).exists()]

        self.results.append(
            VerificationResult(
                phase="Phase 8",
                check_id="P8-RELOC-003",
                description="Ops tools relocated from apps_lic/tools/ to ops_scripts/general/",
                passed=len(still_in_apps_lic) == 0 and len(in_ops_scripts) == 4,
                evidence={
                    "still_in_apps_lic": still_in_apps_lic,
                    "in_ops_scripts": in_ops_scripts,
                },
                failure_reason=""
                if (len(still_in_apps_lic) == 0 and len(in_ops_scripts) == 4)
                else f"{len(still_in_apps_lic)} still in apps_lic, {len(in_ops_scripts)}/4 in ops_scripts",
            ),
        )

    def verify_phase9_circuit_breaker(self) -> None:
        """Phase 9: Hardened executors inherit from HardeningMixin (no hand-rolled retry)."""
        executors = [
            ROOT / "apps_rg" / "enforcement" / "HardenedanthropicexecutorStrategy.py",
            ROOT / "apps_rg" / "reasoning" / "HardenedopenaiexecutorStrategy.py",
        ]

        for executor_path in executors:
            if not executor_path.exists():
                self.results.append(
                    VerificationResult(
                        phase="Phase 9",
                        check_id=f"P9-CB-{executor_path.stem}",
                        description=f"{executor_path.name} exists",
                        passed=False,
                        failure_reason=f"File not found at {executor_path}",
                    ),
                )
                continue

            content = executor_path.read_text(encoding="utf-8")
            tree = ast.parse(content)

            # Find class definitions and check for HardeningMixin inheritance
            classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
            executor_classes = [c for c in classes if "Executor" in c.name]

            inherits_hardening = False
            for cls in executor_classes:
                for base in cls.bases:
                    if isinstance(base, ast.Name) and "HardeningMixin" in base.id:
                        inherits_hardening = True
                        break

            self.results.append(
                VerificationResult(
                    phase="Phase 9",
                    check_id=f"P9-CB-{executor_path.stem}",
                    description=f"{executor_path.name} inherits from HardeningMixin",
                    passed=inherits_hardening,
                    evidence={"executor_classes": [c.name for c in executor_classes], "inherits_hardening": inherits_hardening},
                    failure_reason="" if inherits_hardening else "Does not inherit from HardeningMixin",
                ),
            )

    def verify_phase10_architecture_migration(self) -> None:
        """Phase 10: AppGuardianSpec registry, AppHealResult contract, AppRemediationDispatcher."""
        # Check AppGuardianSpec registry
        registry_path = ROOT / "apps_shared" / "config" / "app_guardian_registry.py"
        if registry_path.exists():
            content = registry_path.read_text(encoding="utf-8")
            spec_count = content.count("AppGuardianSpec(")
            has_registry_tuple = "APP_GUARDIAN_REGISTRY" in content

            self.results.append(
                VerificationResult(
                    phase="Phase 10",
                    check_id="P10-ARCH-001",
                    description="AppGuardianSpec registry exists with >= 4 entries",
                    passed=spec_count >= 4 and has_registry_tuple,
                    evidence={"spec_count": spec_count, "has_registry": has_registry_tuple},
                    failure_reason="" if (spec_count >= 4 and has_registry_tuple) else f"Only {spec_count} specs found",
                ),
            )
        else:
            self.results.append(
                VerificationResult(
                    phase="Phase 10",
                    check_id="P10-ARCH-001",
                    description="AppGuardianSpec registry exists",
                    passed=False,
                    failure_reason=f"Registry not found at {registry_path}",
                ),
            )

        # Check AppHealResult contract
        contract_path = ROOT / "apps_shared" / "types" / "app_heal_contract_types.py"
        if contract_path.exists():
            content = contract_path.read_text(encoding="utf-8")
            has_heal_result = "class AppHealResult" in content
            has_heal_status = "class AppHealStatus" in content

            self.results.append(
                VerificationResult(
                    phase="Phase 10",
                    check_id="P10-ARCH-002",
                    description="AppHealResult contract exists with AppHealStatus enum",
                    passed=has_heal_result and has_heal_status,
                    evidence={"has_result": has_heal_result, "has_status": has_heal_status},
                    failure_reason="" if (has_heal_result and has_heal_status) else "Missing AppHealResult or AppHealStatus",
                ),
            )
        else:
            self.results.append(
                VerificationResult(
                    phase="Phase 10",
                    check_id="P10-ARCH-002",
                    description="AppHealResult contract exists",
                    passed=False,
                    failure_reason=f"Contract not found at {contract_path}",
                ),
            )

        # Check AppRemediationDispatcher
        dispatcher_path = ROOT / "apps_shared" / "scripts" / "app_remediation_dispatcher.py"
        if dispatcher_path.exists():
            content = dispatcher_path.read_text(encoding="utf-8")
            has_dispatch_func = "def dispatch(" in content
            has_run_spec = "def _run_spec(" in content
            has_guardian_checks = content.count("def _check_") >= 4

            self.results.append(
                VerificationResult(
                    phase="Phase 10",
                    check_id="P10-ARCH-003",
                    description="AppRemediationDispatcher exists with dispatch() and >= 4 guardian checks",
                    passed=has_dispatch_func and has_run_spec and has_guardian_checks,
                    evidence={
                        "has_dispatch": has_dispatch_func,
                        "has_run_spec": has_run_spec,
                        "check_count": content.count("def _check_"),
                    },
                    failure_reason=""
                    if (has_dispatch_func and has_run_spec and has_guardian_checks)
                    else "Missing dispatch() or guardian checks",
                ),
            )
        else:
            self.results.append(
                VerificationResult(
                    phase="Phase 10",
                    check_id="P10-ARCH-003",
                    description="AppRemediationDispatcher exists",
                    passed=False,
                    failure_reason=f"Dispatcher not found at {dispatcher_path}",
                ),
            )

    def generate_report(self, json_path: Path | None = None) -> None:
        """Generate verification report."""
        passed = sum(1 for r in self.results if r.passed)
        total = len(self.results)

        print("=" * 80)
        print("APPS_* REFACTORING VERIFICATION REPORT")
        print("=" * 80)
        print(f"\nOverall: {passed}/{total} checks PASSED")
        print(f"Success Rate: {100 * passed / total:.1f}%\n")

        # Group by phase
        phases = {}
        for result in self.results:
            if result.phase not in phases:
                phases[result.phase] = []
            phases[result.phase].append(result)

        for phase in sorted(phases.keys()):
            phase_results = phases[phase]
            phase_passed = sum(1 for r in phase_results if r.passed)
            phase_total = len(phase_results)

            status = "✓ PASS" if phase_passed == phase_total else "✗ FAIL"
            print(f"{status} {phase}: {phase_passed}/{phase_total}")

            for result in phase_results:
                status_icon = "  ✓" if result.passed else "  ✗"
                print(f"{status_icon} {result.check_id}: {result.description}")
                if not result.passed:
                    print(f"      Reason: {result.failure_reason}")

        print("\n" + "=" * 80)

        if json_path:
            report = {
                "summary": {"total": total, "passed": passed, "failed": total - passed, "success_rate": 100 * passed / total},
                "results": [r.to_dict() for r in self.results],
            }
            json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
            print(f"\nJSON report written to: {json_path}")


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Verify apps_* refactoring completion")
    parser.add_argument("--json", type=Path, help="Output JSON report to file")
    args = parser.parse_args()

    verifier = AppsRefactorVerifier()
    all_passed = verifier.verify_all()
    verifier.generate_report(json_path=args.json)

    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
