#!/usr/bin/env python3
"""
W8 CI Gate: APPS-RG-L2-V4-ENVELOPE (Hardened - AST-based)

Validates the apps_rg L2 v4 envelope (E1-E2-E3-E4-E5) plus W7B feature flag bridge.
Uses AST-based scanning to avoid false positives from comments/docstrings.

Hard-fail scope:
- apps_rg/runtime/bindings/l2_binding_adapter.py
- apps_rg/runtime/bindings/l2_envelope_adapter.py

Checks:
A. Full envelope test execution (all E1-E5, W7, W7B tests)
B. Collect-only proof (zero collection errors)
C. Provider governance (AST scan for private calls, direct SDK/HTTP)
D. Boundary checks (AST scan for unauthorized executable references)
E. Mutation law (execute tests + AST inspection for state invariants)
F. Core purity (deterministic agentic_core diff check with allowlist)
G. Feature flag bridge (env var, explicit dev legacy override, type validation)

Exit codes:
  0 = all checks PASS, or advisory mode with failures logged
  1 = one or more checks FAIL (default fail-closed behavior)

Environment:
  APPS_RG_L2_V4_ENVELOPE_ADVISORY=1 — exit 0 when failures are logged for local diagnostics.
"""

import ast
import subprocess
import sys
import os
from pathlib import Path
from typing import Set, Tuple, List

# Gate metadata
GATE_NAME = "APPS-RG-L2-V4-ENVELOPE"
GATE_VERSION = "W8.2-HARDENED-AST"

# Repo root detection
REPO_ROOT = Path(__file__).parent.parent.parent.resolve()
APPS_RG_PATH = REPO_ROOT / "apps_rg"
TEST_FILE = REPO_ROOT / "tests" / "_apps_contract" / "test_apps_rg_l2_envelope.py"
GOVERNED_EXIT_TEST_FILE = REPO_ROOT / "tests" / "_apps_contract" / "test_apps_rg_governed_l2_exit_w6.py"
COLLECT_ONLY_TARGETS = (
    TEST_FILE,
    GOVERNED_EXIT_TEST_FILE,
)

# Hard-fail scope: L2 v4 envelope files only
HARD_FAIL_FILES = [
    APPS_RG_PATH / "runtime" / "bindings" / "l2_binding_adapter.py",
    APPS_RG_PATH / "runtime" / "bindings" / "l2_envelope_adapter.py",
]

# Pre-existing agentic_core diff allowlist (not from W8)
AGENTIC_CORE_ALLOWLIST = {
    "agentic_core/L6_system_learning/future_run_promotion/future_run_proposal_builder.py": "Pre-existing file, not touched by W8"
}


def run_command(cmd: list[str], cwd: Path = None, timeout: int = 60) -> tuple[int, str, str]:
    """Run a command and return (exit_code, stdout, stderr)."""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd or REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=timeout,
            shell=False,
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return 1, "", f"Command timed out after {timeout}s"
    except Exception as e:
        return 1, "", str(e)


class ASTPatternScanner(ast.NodeVisitor):
    """AST scanner to find executable references (not docstrings/comments)."""
    
    def __init__(self, target_patterns: List[str]):
        self.target_patterns = target_patterns
        self.found_patterns: Set[Tuple[str, int, str]] = set()
        
    def visit_Call(self, node: ast.Call) -> None:
        """Detect function calls."""
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
            for pattern in self.target_patterns:
                if pattern in func_name:
                    self.found_patterns.add((pattern, node.lineno, f"call:{func_name}"))
        elif isinstance(node.func, ast.Attribute):
            attr_chain = self._get_attr_chain(node.func)
            for pattern in self.target_patterns:
                if pattern in attr_chain:
                    self.found_patterns.add((pattern, node.lineno, f"call:{attr_chain}"))
        self.generic_visit(node)
        
    def visit_Attribute(self, node: ast.Attribute) -> None:
        """Detect attribute access."""
        attr_chain = self._get_attr_chain(node)
        for pattern in self.target_patterns:
            if pattern in attr_chain:
                self.found_patterns.add((pattern, node.lineno, f"attr:{attr_chain}"))
        self.generic_visit(node)
        
    def visit_Name(self, node: ast.Name) -> None:
        """Detect bare name references."""
        for pattern in self.target_patterns:
            if pattern in node.id:
                self.found_patterns.add((pattern, node.lineno, f"name:{node.id}"))
        self.generic_visit(node)
        
    def visit_Import(self, node: ast.Import) -> None:
        """Detect imports."""
        for alias in node.names:
            for pattern in self.target_patterns:
                if pattern in alias.name:
                    self.found_patterns.add((pattern, node.lineno, f"import:{alias.name}"))
        self.generic_visit(node)
        
    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Detect from imports."""
        if node.module:
            for pattern in self.target_patterns:
                if pattern in node.module:
                    self.found_patterns.add((pattern, node.lineno, f"from_import:{node.module}"))
        self.generic_visit(node)
        
    def visit_Assign(self, node: ast.Assign) -> None:
        """Detect assignments."""
        for target in node.targets:
            if isinstance(target, ast.Name):
                for pattern in self.target_patterns:
                    if pattern in target.id:
                        value_str = self._get_value_str(node.value)
                        self.found_patterns.add((pattern, node.lineno, f"assign:{target.id}={value_str}"))
        self.generic_visit(node)
        
    def _get_attr_chain(self, node) -> str:
        """Get full attribute chain."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_attr_chain(node.value)}.{node.attr}"
        return ""
        
    def _get_value_str(self, node) -> str:
        """Get string representation of a value node."""
        if isinstance(node, ast.Constant):
            return repr(node.value)
        elif isinstance(node, ast.NameConstant):
            return repr(node.value)
        elif isinstance(node, ast.Name):
            return node.id
        return "<complex>"


def scan_file_with_ast(file_path: Path, patterns: List[str]) -> Set[Tuple[str, int, str]]:
    """Scan a Python file using AST to find executable references."""
    if not file_path.exists():
        return set()
    try:
        source = file_path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        scanner = ASTPatternScanner(patterns)
        scanner.visit(tree)
        return scanner.found_patterns
    except SyntaxError as e:
        print(f"  WARNING: Syntax error in {file_path}: {e}")
        return set()
    except Exception as e:
        print(f"  WARNING: Failed to parse {file_path}: {e}")
        return set()


def check_a_full_envelope_tests() -> dict:
    """Check A: Full envelope test execution (E1-E5, W7, W7B)."""
    print(f"\n{'='*60}")
    print(f"[A] Full Envelope Test Execution")
    print(f"{'='*60}")
    
    results = {"pass": True, "details": []}
    
    # A1: Run FULL test suite (not just W7B subset)
    exit_code, stdout, stderr = run_command([
        sys.executable, "-m", "pytest",
        str(TEST_FILE),
        "-v",
        "--tb=line",
    ], timeout=180)
    
    if exit_code != 0:
        results["pass"] = False
        results["details"].append(f"FAIL: Full envelope tests returned exit code {exit_code}")
        if stderr:
            results["details"].append(f"stderr: {stderr[:500]}")
    else:
        passed = stdout.count("PASSED")
        failed = stdout.count("FAILED")
        error = stdout.count("ERROR")
        results["details"].append(f"PASS: Full envelope tests passed ({passed} passed, {failed} failed, {error} errors)")
        if failed > 0 or error > 0:
            results["pass"] = False
            results["details"].append(f"FAIL: {failed} failures, {error} errors detected")
    
    for detail in results["details"]:
        print(f"  {detail}")
    
    return results


def check_b_collect_only() -> dict:
    """Check B: Collect-only proof - zero collection errors."""
    print(f"\n{'='*60}")
    print(f"[B] Collect-Only Proof")
    print(f"{'='*60}")
    
    results = {"pass": True, "details": []}
    
    # B1: pytest collect-only for the contract files owned by this gate.
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        *(str(path) for path in COLLECT_ONLY_TARGETS),
        "--collect-only",
        "-q",
    ]
    exit_code, stdout, stderr = run_command(cmd)
    
    if exit_code != 0:
        results["pass"] = False
        results["details"].append(f"FAIL: pytest collect-only returned {exit_code}")
        if "collection error" in stderr.lower() or "collection error" in stdout.lower():
            results["details"].append("FAIL: Collection errors detected")
        if stderr:
            results["details"].append(f"stderr: {stderr[:500]}")
    else:
        results["details"].append(
            "PASS: focused pytest --collect-only exits 0 with zero collection errors"
        )
    
    for detail in results["details"]:
        print(f"  {detail}")
    
    return results


def check_b_feature_flag_bridge() -> dict:
    """Check B: Feature flag bridge implementation."""
    print(f"\n{'='*60}")
    print(f"[B] Feature Flag Bridge Check")
    print(f"{'='*60}")
    
    results = {"pass": True, "details": []}
    
    l2_binding = HARD_FAIL_FILES[0]  # l2_binding_adapter.py
    
    if not l2_binding.exists():
        results["pass"] = False
        results["details"].append(f"FAIL: l2_binding_adapter.py not found")
        return results
    
    source = l2_binding.read_text(encoding="utf-8")
    
    # B1: Check _use_v4_l2_envelope helper exists
    if "def _use_v4_l2_envelope()" in source:
        results["details"].append("PASS: _use_v4_l2_envelope() helper found")
    else:
        results["pass"] = False
        results["details"].append("FAIL: _use_v4_l2_envelope() helper not found")
    
    # B2: Check APPS_RG_L2_USE_V4_ENVELOPE env var handling
    if 'APPS_RG_L2_USE_V4_ENVELOPE' in source:
        results["details"].append("PASS: APPS_RG_L2_USE_V4_ENVELOPE env var referenced")
    else:
        results["pass"] = False
        results["details"].append("FAIL: APPS_RG_L2_USE_V4_ENVELOPE env var not referenced")
    
    # B3: Check bridge calls run_apps_rg_l2_envelope
    if "run_apps_rg_l2_envelope" in source:
        results["details"].append("PASS: run_apps_rg_l2_envelope called in bridge")
    else:
        results["pass"] = False
        results["details"].append("FAIL: run_apps_rg_l2_envelope not called in bridge")
    
    # B4: Check TypeError before feature flag (input validation order)
    if "isinstance(prompt, CompiledPromptArtifact)" in source:
        results["details"].append("PASS: isinstance check for CompiledPromptArtifact found")
    else:
        results["pass"] = False
        results["details"].append("FAIL: CompiledPromptArtifact type check not found")
    
    # B5: Check explicit dev legacy override is preserved.
    if "APPS_RG_L2_DEV_LEGACY_PACKAGE" in source and "_legacy_package_driven(prompt)" in source:
        results["details"].append("PASS: Explicit dev legacy override preserved")
    else:
        results["pass"] = False
        results["details"].append("FAIL: Explicit dev legacy override not clearly preserved")
    
    for detail in results["details"]:
        print(f"  {detail}")
    
    return results


def check_c_provider_governance() -> dict:
    """Check C: Provider governance - AST scan for private calls, direct SDK/HTTP."""
    print(f"\n{'='*60}")
    print(f"[C] Provider Governance Check (AST-based, Hard-fail scope)")
    print(f"{'='*60}")
    
    results = {"pass": True, "details": [], "advisory": []}
    
    # Forbidden patterns for provider governance
    forbidden_patterns = [
        "_invoke_local_vllm",
        "_invoke_external_api",
        "urllib.request",
        "requests",
        "httpx",
        "openai",
        "anthropic",
    ]
    
    # Hard-fail: scan L2 envelope files only
    for f in HARD_FAIL_FILES:
        if f.exists():
            found = scan_file_with_ast(f, forbidden_patterns)
            for pattern, line, context in found:
                # Allow 'requests' in import context if it's just the module name
                # Block 'requests.get', 'requests.post', etc.
                if pattern == "requests" and "call:" not in context and "attr:" not in context:
                    continue  # Just importing requests module is OK if not used
                results["pass"] = False
                results["details"].append(f"FAIL: {f.name}:{line} - {context}")
    
    # Check for gateway.invoke at expected locations
    gateway_found = []
    for f in HARD_FAIL_FILES:
        if f.exists():
            source = f.read_text(encoding="utf-8")
            for i, line in enumerate(source.split("\n"), 1):
                if "gateway.invoke" in line and not line.strip().startswith("#"):
                    gateway_found.append(f"{f.name}:{i}")
    
    if gateway_found:
        results["details"].append(f"PASS: gateway.invoke at expected locations: {', '.join(gateway_found[:3])}")
    else:
        results["advisory"].append("INFO: gateway.invoke not found in hard-fail scope")
    
    for detail in results["details"]:
        print(f"  {detail}")
    for adv in results["advisory"]:
        print(f"  {adv}")
    
    return results


def check_d_boundary_checks() -> dict:
    """Check D: Boundary checks - AST scan for unauthorized executable references."""
    print(f"\n{'='*60}")
    print(f"[D] Boundary Check (AST-based, executable behavior only)")
    print(f"{'='*60}")
    
    results = {"pass": True, "details": [], "advisory": []}
    
    unauthorized_patterns = [
        "prompt_assembly",
        "c0_retrieval",
        "substrate_ingest",
        "choose_route",
        "route_change",
        "replan",
        "reground",
        "workflow_expand",
        "step_expand",
        "judge_quality",
        "score_resume",
        "exit_eval",
        "l4_write",
        "uwg_write",
        "durable_commit",
    ]
    
    # Hard-fail: scan L2 envelope files only
    for f in HARD_FAIL_FILES:
        if not f.exists():
            continue
        found = scan_file_with_ast(f, unauthorized_patterns)
        for pattern, line, context in found:
            # Distinguish between:
            # - Assigning to False (correct: is_uwg_write_authority=False)
            # - Assigning to True (violation)
            # - Other references (needs review)
            if "assign:" in context:
                if "=False" in context or "=False" in context.replace(" ", ""):
                    results["details"].append(f"PASS: {f.name}:{line} - {pattern} correctly set to False")
                elif "=True" in context or "=True" in context.replace(" ", ""):
                    results["pass"] = False
                    results["details"].append(f"FAIL: {f.name}:{line} - {pattern} set to True (violation)")
                else:
                    results["advisory"].append(f"INFO: {f.name}:{line} - {pattern} assignment: {context}")
            elif "call:" in context or "attr:" in context:
                # Function calls or attribute access - potential violation
                results["pass"] = False
                results["details"].append(f"FAIL: {f.name}:{line} - {pattern} executable reference: {context}")
            else:
                # Import or name reference - advisory
                results["advisory"].append(f"INFO: {f.name}:{line} - {pattern} reference: {context}")
    
    for detail in results["details"]:
        print(f"  {detail}")
    for adv in results["advisory"]:
        print(f"  {adv}")
    
    return results


def check_e_mutation_law() -> dict:
    """Check E: Mutation law - execute specific tests + AST inspection."""
    print(f"\n{'='*60}")
    print(f"[E] Mutation Law Check (Specific tests + AST inspection)")
    print(f"{'='*60}")
    
    results = {"pass": True, "details": []}
    
    # Run specific mutation law tests using exact class selectors
    mutation_tests = [
        "TestW7BBoundaryChecks::test_w7b_state_diff_authorized_false_in_v4_path",
        "TestW7BBoundaryChecks::test_w7b_is_uwg_write_authority_false_in_v4_path",
    ]
    
    for test_class in mutation_tests:
        exit_code, stdout, stderr = run_command([
            sys.executable, "-m", "pytest",
            str(TEST_FILE),
            "-v",
            "--tb=line",
            "-k", test_class.split("::")[1],
        ], timeout=60)
        
        if exit_code != 0:
            results["pass"] = False
            results["details"].append(f"FAIL: {test_class} failed")
        else:
            results["details"].append(f"PASS: {test_class}")
    
    # AST inspection for mutation law invariants
    for f in HARD_FAIL_FILES:
        if not f.exists():
            continue
        found = scan_file_with_ast(f, ["state_diff_authorized", "is_uwg_write_authority"])
        for pattern, line, context in found:
            if "assign:" in context:
                if "=False" in context or "=False" in context.replace(" ", ""):
                    results["details"].append(f"PASS: {f.name}:{line} - {pattern}=False (invariant enforced)")
                elif "=True" in context or "=True" in context.replace(" ", ""):
                    results["pass"] = False
                    results["details"].append(f"FAIL: {f.name}:{line} - {pattern}=True (invariant violated)")
    
    for detail in results["details"]:
        print(f"  {detail}")
    
    return results


def check_f_core_purity() -> dict:
    """Check F: Core purity - deterministic agentic_core diff check with allowlist."""
    print(f"\n{'='*60}")
    print(f"[F] Core Purity Check (Deterministic with Allowlist)")
    print(f"{'='*60}")
    
    results = {"pass": True, "details": []}
    
    # Run git diff --name-only agentic_core/
    exit_code, stdout, stderr = run_command(
        ["git", "diff", "--name-only", "agentic_core/"]
    )
    
    if exit_code != 0:
        results["details"].append(f"INFO: git diff returned {exit_code}")
    
    changed_files = [f for f in stdout.strip().split("\n") if f.strip()]
    
    # Filter out allowlisted pre-existing changes
    non_allowlisted = []
    for f in changed_files:
        if f in AGENTIC_CORE_ALLOWLIST:
            results["details"].append(f"ALLOWLIST: {f} ({AGENTIC_CORE_ALLOWLIST[f]})")
        else:
            non_allowlisted.append(f)
    
    if non_allowlisted:
        results["pass"] = False
        results["details"].append(f"FAIL: agentic_core/ has {len(non_allowlisted)} non-allowlisted changed file(s):")
        for f in non_allowlisted:
            results["details"].append(f"  - {f}")
    else:
        if changed_files:
            results["details"].append(f"PASS: Only pre-existing allowlisted changes in agentic_core/ ({len(changed_files)} file(s))")
        else:
            results["details"].append("PASS: No changes in agentic_core/")
    
    for detail in results["details"]:
        print(f"  {detail}")
    
    return results


def check_g_feature_flag_bridge() -> dict:
    """Check G: Feature flag bridge (env var, legacy path, type validation)."""
    print(f"\n{'='*60}")
    print(f"[G] Feature Flag Bridge Check")
    print(f"{'='*60}")
    
    results = {"pass": True, "details": []}
    
    l2_binding = HARD_FAIL_FILES[0]  # l2_binding_adapter.py
    
    if not l2_binding.exists():
        results["pass"] = False
        results["details"].append(f"FAIL: l2_binding_adapter.py not found")
        return results
    
    source = l2_binding.read_text(encoding="utf-8")
    
    # G1: Check _use_v4_l2_envelope helper exists
    if "def _use_v4_l2_envelope()" in source:
        results["details"].append("PASS: _use_v4_l2_envelope() helper found")
    else:
        results["pass"] = False
        results["details"].append("FAIL: _use_v4_l2_envelope() helper not found")
    
    # G2: Check APPS_RG_L2_USE_V4_ENVELOPE env var handling
    if 'APPS_RG_L2_USE_V4_ENVELOPE' in source:
        results["details"].append("PASS: APPS_RG_L2_USE_V4_ENVELOPE env var referenced")
    else:
        results["pass"] = False
        results["details"].append("FAIL: APPS_RG_L2_USE_V4_ENVELOPE env var not referenced")
    
    # G3: Check bridge calls run_apps_rg_l2_envelope
    if "run_apps_rg_l2_envelope" in source:
        results["details"].append("PASS: run_apps_rg_l2_envelope called in bridge")
    else:
        results["pass"] = False
        results["details"].append("FAIL: run_apps_rg_l2_envelope not called in bridge")
    
    # G4: Check TypeError before feature flag (input validation order)
    if "isinstance(prompt, CompiledPromptArtifact)" in source:
        results["details"].append("PASS: isinstance check for CompiledPromptArtifact found (TypeError before flag)")
    else:
        results["pass"] = False
        results["details"].append("FAIL: CompiledPromptArtifact type check not found")
    
    # G5: Check explicit dev legacy override is preserved.
    if "APPS_RG_L2_DEV_LEGACY_PACKAGE" in source and "_legacy_package_driven(prompt)" in source:
        results["details"].append("PASS: Explicit dev legacy override preserved")
    else:
        results["pass"] = False
        results["details"].append("FAIL: Explicit dev legacy override not clearly preserved")
    
    # G6: Run specific feature flag tests using class selector
    exit_code, stdout, stderr = run_command([
        sys.executable, "-m", "pytest",
        str(TEST_FILE),
        "-v",
        "--tb=line",
        "-k", "TestW7BFeatureFlag",
    ], timeout=60)
    
    if exit_code != 0:
        results["pass"] = False
        results["details"].append(f"FAIL: TestW7BFeatureFlag tests failed")
    else:
        passed = stdout.count("PASSED")
        results["details"].append(f"PASS: TestW7BFeatureFlag ({passed} tests)")
    
    for detail in results["details"]:
        print(f"  {detail}")
    
    return results


def main() -> int:
    """Main entry point. Returns exit code."""
    print(f"{'='*60}")
    print(f"CI Gate: {GATE_NAME} v{GATE_VERSION}")
    print(f"{'='*60}")
    print(f"Repository: {REPO_ROOT}")
    print(f"Hard-fail scope: {[f.name for f in HARD_FAIL_FILES]}")
    
    all_results = []
    
    # Run all checks (A-G)
    all_results.append(("A. Full Envelope Tests", check_a_full_envelope_tests()))
    all_results.append(("B. Collect-Only Proof", check_b_collect_only()))
    all_results.append(("C. Provider Governance", check_c_provider_governance()))
    all_results.append(("D. Boundary Check", check_d_boundary_checks()))
    all_results.append(("E. Mutation Law", check_e_mutation_law()))
    all_results.append(("F. Core Purity", check_f_core_purity()))
    all_results.append(("G. Feature Flag Bridge", check_g_feature_flag_bridge()))
    
    # Summary
    print(f"\n{'='*60}")
    print(f"SUMMARY")
    print(f"{'='*60}")
    
    total_pass = 0
    total_fail = 0
    
    for name, result in all_results:
        status = "PASS" if result["pass"] else "FAIL"
        if result["pass"]:
            total_pass += 1
        else:
            total_fail += 1
        print(f"  [{status}] {name}")
    
    print(f"\n  Total: {total_pass} passed, {total_fail} failed")
    
    # Final verdict
    advisory = os.environ.get("APPS_RG_L2_V4_ENVELOPE_ADVISORY", "").strip() == "1"

    if total_fail == 0:
        print(f"\n{'='*60}")
        print(f"FINAL: PASS - All checks passed")
        print(f"{'='*60}")
        return 0
    print(f"\n{'='*60}")
    print(f"FINAL: FAIL - {total_fail} check(s) failed")
    print(f"{'='*60}")
    if advisory:
        print(
            "[check_apps_rg_l2_v4_envelope] Advisory mode — partial FAIL above; exiting 0.",
            file=sys.stderr,
        )
        return 0
    print(
        "[check_apps_rg_l2_v4_envelope] Fail-closed mode — exiting 1 "
        "(set APPS_RG_L2_V4_ENVELOPE_ADVISORY=1 for local advisory diagnostics).",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
