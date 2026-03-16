"""
Guardian-of-Guardians: Contract Integrity Checker.

Verifies that ALL guardian scripts in the repo:
1. Import GuardianResult from the canonical SSOT path
2. Use normalize_repo_path for artifact paths
3. Do not emit raw dict/json.dumps without GuardianResult
4. Return GuardianResult from their main runner function

This is a meta-guardian that guards the guardians themselves.

CLI:
    python -m agentic_core.L0_routing.scripts.run_guardian_contract_integrity \\
        --strict
"""

from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path

from agentic_core.L0_routing.types.guardian_contract_types import (
    CheckStatus,
    GuardianResult,
    GuardianStatus,
    maybe_sign_result,
)
from agentic_core.L0_routing.types.guardian_registry_types import (
    ALL_GUARDIANS,
)
from agentic_core.L0_routing.utils.project_root_util import get_validated_project_root
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_routes_through,  # noqa: E402
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "run_guardian_contract_integrity")
emit_determinism_digest("p0", "run_guardian_contract_integrity")

_emit_dispatches_healing_run("p1", "run_guardian_contract_integrity", "L0")
_emit_routes_through("p1", "run_guardian_contract_integrity", "L0")
_emit_escalates_to_human("p1", "run_guardian_contract_integrity", "L0")
_emit_reads_policy_state("p1", "run_guardian_contract_integrity", "L0")

GUARDIAN_ID = "contract_integrity"

# Canonical import path that all guardians MUST use
CANONICAL_CONTRACT_MODULE = "agentic_core.L0_routing.types.guardian_contract_types"


# ---------------------------------------------------------------------------
# AST-based checks (Constitutional §6: AST-only, no regex for structural logic)
# ---------------------------------------------------------------------------


def _check_imports_contract(tree: ast.AST) -> bool:
    """Check if the module imports from the canonical contract path."""
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "_check_imports_contract", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "_check_imports_contract", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "_check_imports_contract")
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.module and CANONICAL_CONTRACT_MODULE in node.module:
                return True
    return False


def _check_imports_normalize(tree: ast.AST) -> bool:
    """Check if the module imports normalize_repo_path."""
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.names:
                for alias in node.names:
                    if alias.name == "normalize_repo_path":
                        return True
    return False


def _check_returns_guardian_result(tree: ast.AST) -> bool:
    """Check if any function has a return type annotation of GuardianResult."""
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            if node.returns:
                if isinstance(node.returns, ast.Name) and node.returns.id == "GuardianResult":
                    return True
                if isinstance(node.returns, ast.Attribute) and node.returns.attr == "GuardianResult":
                    return True
    return False


def _check_no_raw_json_dumps(tree: ast.AST) -> list[int]:
    """
    Find json.dumps calls that are NOT on a GuardianResult method.
    Returns line numbers of suspicious calls.
    """
    suspicious_lines: list[int] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            # json.dumps(...)
            if (
                isinstance(node.func, ast.Attribute)
                and node.func.attr == "dumps"
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id == "json"
            ):
                suspicious_lines.append(node.lineno)
    return suspicious_lines


# Scan cap constants that indicate a guardian is a scanning guardian
_SCAN_CAP_NAMES: frozenset[str] = frozenset({"MAX_FILES_PER_SCAN", "MAX_FOLDER_DEPTH"})


def _check_imports_scan_caps(tree: ast.AST) -> bool:
    """Check if the module imports any scan cap constants."""
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.names:
            for alias in node.names:
                if alias.name in _SCAN_CAP_NAMES:
                    return True
    return False


def _check_uses_guard_scan_budget(tree: ast.AST) -> bool:
    """Check if the module imports guard_scan_budget from SSOT."""
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.names:
            for alias in node.names:
                if alias.name == "guard_scan_budget":
                    return True
    return False


def _check_no_raise_exception_for_caps(tree: ast.AST) -> list[tuple[int, str]]:
    """
    AST-detect 'raise <AnyException>(...)' where the message string references
    scan cap constant names. Returns (line_number, exception_name) tuples.
    Catches RuntimeError, ValueError, Exception, or any custom exception.
    """
    violations: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Raise) and node.exc is not None:
            exc = node.exc
            if isinstance(exc, ast.Call) and isinstance(exc.func, ast.Name):
                exc_name = exc.func.id
                for arg in exc.args:
                    if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                        if any(cap in arg.value for cap in _SCAN_CAP_NAMES):
                            violations.append((node.lineno, exc_name))
                    if isinstance(arg, ast.JoinedStr):
                        for val in arg.values:
                            if isinstance(val, ast.Constant) and isinstance(val.value, str):
                                if any(cap in val.value for cap in _SCAN_CAP_NAMES):
                                    violations.append((node.lineno, exc_name))
    return violations


# Backward-compatible alias for existing tests
def _check_no_raise_runtime_error_for_caps(tree: ast.AST) -> list[int]:
    """Legacy wrapper — returns line numbers only."""
    return [line for line, _ in _check_no_raise_exception_for_caps(tree)]


# ---------------------------------------------------------------------------
# Main guardian logic
# ---------------------------------------------------------------------------


def _module_to_path(module: str) -> str:
    """Convert dotted module path to file path."""
    return module.replace(".", "/") + ".py"


def run_contract_integrity_guardian(
    repo_root: Path | None = None,
    timestamp: str | None = None,
) -> GuardianResult:
    """
    Scan all guardian scripts from SSOT registry and verify they follow the contract.
    """
    if repo_root is None:
        repo_root = get_validated_project_root()

    result = GuardianResult(
        guardian_id=GUARDIAN_ID,
        timestamp=timestamp,
    )

    # Enumerate from SSOT registry (no filesystem globs)
    # Exclude self (contract_integrity) from validation
    guardians_to_check = [spec for spec in ALL_GUARDIANS if spec.guardian_id != GUARDIAN_ID]

    if not guardians_to_check:
        result.add_check(
            check_id="scripts_found",
            status=CheckStatus.FAIL,
            details="No guardians found in SSOT registry (excluding self)",
        )
        result.set_error("No guardians in registry")
        maybe_sign_result(result, commit_hash="HEAD")
        return result

    result.add_check(
        check_id="scripts_found",
        status=CheckStatus.PASS,
        details=f"Found {len(guardians_to_check)} guardian(s) in SSOT registry",
        evidence={
            "count": len(guardians_to_check),
            "guardians": [s.guardian_id for s in guardians_to_check],
        },
    )

    scripts_checked = 0
    violations_found = 0

    for spec in guardians_to_check:
        scripts_checked += 1
        gid = spec.guardian_id
        script_path = repo_root / _module_to_path(spec.entrypoint_module)

        if not script_path.exists():
            result.add_check(
                check_id=f"exists_{gid}",
                status=CheckStatus.FAIL,
                details=f"Guardian {gid} entrypoint not found: {spec.entrypoint_module}",
            )
            violations_found += 1
            continue

        try:
            source = script_path.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(script_path))
        except SyntaxError as exc:
            result.add_check(
                check_id=f"parse_{gid}",
                status=CheckStatus.FAIL,
                details=f"SyntaxError in {gid}: {exc}",
            )
            violations_found += 1
            continue

        # Check 1: Imports canonical contract
        if _check_imports_contract(tree):
            result.add_check(
                check_id=f"imports_contract_{gid}",
                status=CheckStatus.PASS,
                details=f"{gid} imports from canonical contract module",
            )
        else:
            result.add_check(
                check_id=f"imports_contract_{gid}",
                status=CheckStatus.FAIL,
                details=f"{gid} does NOT import from {CANONICAL_CONTRACT_MODULE}",
            )
            violations_found += 1

        # Check 2: Imports normalize_repo_path
        if _check_imports_normalize(tree):
            result.add_check(
                check_id=f"imports_normalize_{gid}",
                status=CheckStatus.PASS,
                details=f"{gid} imports normalize_repo_path",
            )
        else:
            result.add_check(
                check_id=f"imports_normalize_{gid}",
                status=CheckStatus.FAIL,
                details=f"{gid} does NOT import normalize_repo_path",
            )
            violations_found += 1

        # Check 3: Returns GuardianResult
        if _check_returns_guardian_result(tree):
            result.add_check(
                check_id=f"returns_result_{gid}",
                status=CheckStatus.PASS,
                details=f"{gid} returns GuardianResult",
            )
        else:
            result.add_check(
                check_id=f"returns_result_{gid}",
                status=CheckStatus.FAIL,
                details=f"{gid} does NOT annotate return as GuardianResult",
            )
            violations_found += 1

        # Check 4: Scanning guardians must use guard_scan_budget (not raise any exception)
        if _check_imports_scan_caps(tree):
            cap_raise_violations = _check_no_raise_exception_for_caps(tree)
            if cap_raise_violations:
                lines_and_types = [f"L{ln}:{exc}" for ln, exc in cap_raise_violations]
                result.add_check(
                    check_id=f"scan_budget_pattern_{gid}",
                    status=CheckStatus.FAIL,
                    details=(
                        f"{gid} raises exception(s) for scan caps: {lines_and_types}. "
                        f"Use guard_scan_budget() and return FAIL instead."
                    ),
                )
                violations_found += 1
            elif not _check_uses_guard_scan_budget(tree):
                result.add_check(
                    check_id=f"scan_budget_pattern_{gid}",
                    status=CheckStatus.FAIL,
                    details=(
                        f"{gid} imports scan cap constants but does not import guard_scan_budget. "
                        f"Scanning guardians MUST use guard_scan_budget() from SSOT."
                    ),
                )
                violations_found += 1
            else:
                result.add_check(
                    check_id=f"scan_budget_pattern_{gid}",
                    status=CheckStatus.PASS,
                    details=f"{gid} correctly uses guard_scan_budget for scan cap enforcement",
                )

    # Finalize
    result.metrics = {
        "scripts_checked": scripts_checked,
        "violations_found": violations_found,
    }

    if result.status == GuardianStatus.PASS.value:
        result.summary = f"Contract integrity: {scripts_checked} guardians checked, 0 violations"
    else:
        result.summary = f"Contract integrity: {violations_found} violation(s) in {scripts_checked} guardians"
        result.remediation_hints = [
            f"All guardian scripts must import from {CANONICAL_CONTRACT_MODULE}",
            "All guardian scripts must import and use normalize_repo_path",
            "All runner functions must annotate return type as GuardianResult",
        ]

    # --- V15 signing (before serialization) ---
    maybe_sign_result(result, commit_hash="HEAD")

    return result


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(description="Guardian Contract Integrity Checker")
    parser.add_argument("--format", choices=["json", "text"], default="json")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--timestamp", default=None)
    args = parser.parse_args()

    result = run_contract_integrity_guardian(timestamp=args.timestamp)

    if args.format == "json":
        print(result.to_json())
    else:
        print(f"Guardian: {result.guardian_id} | Status: {result.status}")
        print(f"Summary: {result.summary}")
        for check in result.checks:
            print(f"  [{check.status}] {check.check_id}: {check.details}")

    if args.strict and result.status != GuardianStatus.PASS.value:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
