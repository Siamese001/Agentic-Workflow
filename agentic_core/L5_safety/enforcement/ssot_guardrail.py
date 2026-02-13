"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  SSOT GUARDRAIL — Shadow Classification Detector                           ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  Scans the repository AST to detect "shadow classification" — any code     ║
║  that reimplements agent detection or file classification logic outside     ║
║  the canonical kernel (agentic_core/core/classification_kernel.py).        ║
║                                                                            ║
║  Detections:                                                               ║
║  1. Function definitions named is_agent_class, classify_file, etc.         ║
║     outside the kernel and its known consumer (FileClassificationAgent).   ║
║  2. Usage of endswith('Agent') string checks inside logic functions         ║
║     (heuristic for inline shadow classification).                          ║
║                                                                            ║
║  Usage:                                                                    ║
║    python -m agentic_core.L5_safety.enforcement.ssot_guardrail              ║
║    python -m agentic_core.L5_safety.enforcement.ssot_guardrail --fail       ║
║                                                                            ║
║  Exit codes:                                                               ║
║    0 — No violations found                                                 ║
║    1 — Violations detected (with --fail)                                   ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import argparse
import ast
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path

# ============================================================================
# CONFIGURATION
# ============================================================================

# The canonical kernel — exempt from all checks
KERNEL_PATH = "agentic_core/core/classification_kernel.py"

# Files that are allowed to have classification-related function names
# because they are direct consumers/wrappers of the kernel
ALLOWLISTED_FILES: frozenset[str] = frozenset(
    {
        KERNEL_PATH,
        # FCA is the high-level consumer that wraps the kernel
        "agentic_core/L5_safety/reasoning/FileClassificationAgent.py",
        # This guardrail itself
        "agentic_core/L5_safety/enforcement/ssot_guardrail.py",
        # Contract tests reference the kernel
        "tests/core/test_classification_contract.py",
        # --- Phase 1 refactored wrappers (delegate to kernel) ---
        # complexity_visitor_util: is_sovereign_agent() → kernel, is_agent_class() shim
        "agentic_core/L0_maintenance/utils/complexity_visitor_util.py",
        # full_agent_discovery: analyze_agent_integrity() → kernel classify_file_standalone()
        "agentic_core/L0_maintenance/scripts/full_agent_discovery.py",
        # run_classification: classify_file() → kernel classify_file_standalone()
        "ops_scripts/maintenance/run_classification.py",
        # discovery_util: _scan_file_for_agents() → kernel is_agent_file()
        "agentic_core/runtime/utils/discovery_util.py",
        # file_intent: _is_agent_class() aligned with kernel naming rules
        "agentic_core/prompt_governance/scripts/file_intent.py",
        # type_erasure_validator: _is_agent_class() aligned with kernel
        "agentic_core/L5_safety/validators/type_erasure_validator.py",
        # Dedup utilities: is_agent_file() aligned with kernel naming
        "agentic_core/L0_maintenance/scripts/extract_agent_duplicates_util.py",
        "agentic_core/L0_maintenance/scripts/find_real_duplicates_v2_util.py",
        # --- Phase 2 Step 1: Refactored to delegate to kernel ---
        # generate_agent_table_simple_util: is_agent_file() wraps kernel for string paths
        "dev_tools/l0_scripts/generate_agent_table_simple_util.py",
        # pascal_sovereignty_fixer: classify_file() → kernel classify_file_standalone()
        "agentic_core/L0_maintenance/scripts/pascal_sovereignty_fixer.py",
        # mece_test_rebaseline: classify_file() → kernel classify_file_standalone()
        "ops_scripts/general/mece_test_rebaseline.py",
    },
)

# Function names that indicate shadow classification logic
SHADOW_FUNCTION_NAMES: frozenset[str] = frozenset(
    {
        "is_agent_class",
        "classify_file",
        "classify_file_standalone",
        "_is_agent_class",
        "_classify_file",
        "is_agent_file",
    },
)

# Files allowed to have endswith('Agent') checks because they operate on
# AST class nodes for metadata extraction (not classification)
ENDSWITH_AGENT_ALLOWLIST: frozenset[str] = frozenset(
    {
        KERNEL_PATH,
        "agentic_core/L5_safety/reasoning/FileClassificationAgent.py",
        "agentic_core/L5_safety/enforcement/ssot_guardrail.py",
        "tests/core/test_classification_contract.py",
        # These use endswith("Agent") for metadata extraction, not classification:
        "agentic_core/L0_maintenance/utils/complexity_visitor_util.py",
        "agentic_core/L0_maintenance/scripts/full_agent_discovery.py",
        # Naming/renaming scripts that check suffixes for compliance:
        "agentic_core/L5_safety/enforcement/ssot_scanner.py",
        "agentic_core/L5_safety/enforcement/registry_verification.py",
        "agentic_core/L5_safety/enforcement/data.py",
        "agentic_core/L5_safety/enforcement/ssot_structure_validation.py",
        # Dedup/migration scripts:
        "agentic_core/L0_maintenance/scripts/extract_agent_duplicates_util.py",
        "agentic_core/L0_maintenance/scripts/find_real_duplicates_v2_util.py",
        # Naming convention enforcement:
        "ops_scripts/maintenance/run_classification.py",
    },
)

# Directories to exclude from scanning
EXCLUDE_DIRS: frozenset[str] = frozenset(
    {
        "__pycache__",
        ".git",
        "node_modules",
        ".backup",
        "archives",
        ".healing_backups",
        ".venv",
        "venv",
        ".tox",
    },
)


# ============================================================================
# VIOLATION DATA MODEL
# ============================================================================


@dataclass
class Violation:
    """A single guardrail violation."""

    file: str
    line: int
    rule: str
    detail: str
    severity: str = "ERROR"


@dataclass
class ScanResult:
    """Aggregated scan results."""

    files_scanned: int = 0
    violations: list[Violation] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return len(self.violations) == 0


# ============================================================================
# AST SCANNERS
# ============================================================================


def _normalize_path(path: Path, project_root: Path) -> str:
    """Convert absolute path to forward-slash relative path."""
    try:
        rel = path.relative_to(project_root)
    except ValueError:
        rel = path
    return str(rel).replace("\\", "/")


def scan_shadow_functions(
    tree: ast.AST,
    rel_path: str,
) -> list[Violation]:
    """Detect function definitions that shadow kernel classification."""
    violations = []

    if rel_path in ALLOWLISTED_FILES:
        return violations

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name in SHADOW_FUNCTION_NAMES:
                violations.append(
                    Violation(
                        file=rel_path,
                        line=node.lineno,
                        rule="SHADOW_FUNCTION",
                        detail=(
                            f"Function '{node.name}()' reimplements classification logic. "
                            f"Use: from agentic_core.core.classification_kernel import is_agent_file"
                        ),
                    ),
                )
    return violations


def scan_endswith_agent(
    tree: ast.AST,
    rel_path: str,
) -> list[Violation]:
    """Detect usage of endswith('Agent') string checks in logic functions.

    This is a heuristic for inline shadow classification. We look for
    ast.Call nodes where the function is an Attribute named 'endswith'
    and the argument is a string containing 'Agent'.
    """
    violations = []

    if rel_path in ENDSWITH_AGENT_ALLOWLIST:
        return violations

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        # Match: <expr>.endswith("Agent") or <expr>.endswith("Agent")
        if not isinstance(node.func, ast.Attribute):
            continue
        if node.func.attr != "endswith":
            continue
        # Check if any argument is a string containing "Agent"
        for arg in node.args:
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                if "Agent" in arg.value:
                    violations.append(
                        Violation(
                            file=rel_path,
                            line=node.lineno,
                            rule="ENDSWITH_AGENT",
                            detail=(
                                f"Inline endswith('{arg.value}') check detected. "
                                f"Consider using classification_kernel.is_agent_file() instead."
                            ),
                            severity="WARNING",
                        ),
                    )
            # Also check tuples: endswith(("Agent", "BaseAgent"))
            if isinstance(arg, ast.Tuple):
                for elt in arg.elts:
                    if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                        if "Agent" in elt.value:
                            violations.append(
                                Violation(
                                    file=rel_path,
                                    line=node.lineno,
                                    rule="ENDSWITH_AGENT",
                                    detail=(
                                        f"Inline endswith((..., '{elt.value}', ...)) check detected. "
                                        f"Consider using classification_kernel.is_agent_file() instead."
                                    ),
                                    severity="WARNING",
                                ),
                            )
                            break  # One violation per call site is enough
    return violations


# ============================================================================
# MAIN SCANNER
# ============================================================================


def scan_repository(project_root: Path) -> ScanResult:
    """Scan all Python files in the repository for SSOT violations."""
    result = ScanResult()

    scan_dirs = [
        project_root / "agentic_core",
        project_root / "apps_lic",
        project_root / "apps_rg",
        project_root / "apps_shared",
        project_root / "ops_scripts",
        project_root / "tests",
    ]

    for scan_dir in scan_dirs:
        if not scan_dir.exists():
            continue
        for dirpath, dirnames, filenames in os.walk(scan_dir):
            dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
            for fn in filenames:
                if not fn.endswith(".py"):
                    continue
                fp = Path(dirpath) / fn
                rel_path = _normalize_path(fp, project_root)

                try:
                    content = fp.read_text(encoding="utf-8", errors="replace")
                    tree = ast.parse(content)
                except (SyntaxError, OSError):
                    continue

                result.files_scanned += 1
                result.violations.extend(scan_shadow_functions(tree, rel_path))
                result.violations.extend(scan_endswith_agent(tree, rel_path))

    return result


# ============================================================================
# CLI
# ============================================================================


def main() -> int:
    """Run the SSOT guardrail scanner."""
    parser = argparse.ArgumentParser(
        description="SSOT Guardrail: Detect shadow classification logic",
    )
    parser.add_argument(
        "--fail",
        action="store_true",
        help="Exit with code 1 if any violations are found",
    )
    parser.add_argument(
        "--errors-only",
        action="store_true",
        help="Only report ERROR severity (ignore WARNINGs)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON",
    )
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parent.parent.parent.parent
    result = scan_repository(project_root)

    violations = result.violations
    if args.errors_only:
        violations = [v for v in violations if v.severity == "ERROR"]

    if args.json:
        import json

        output = {
            "files_scanned": result.files_scanned,
            "violation_count": len(violations),
            "passed": len(violations) == 0,
            "violations": [
                {
                    "file": v.file,
                    "line": v.line,
                    "rule": v.rule,
                    "detail": v.detail,
                    "severity": v.severity,
                }
                for v in violations
            ],
        }
        print(json.dumps(output, indent=2))
    else:
        print(f"SSOT Guardrail Scan: {result.files_scanned} files scanned")
        print(f"Violations: {len(violations)}")
        if violations:
            print()
            for v in violations:
                print(f"  [{v.severity}] {v.file}:{v.line}")
                print(f"    Rule: {v.rule}")
                print(f"    {v.detail}")
                print()
        else:
            print("Status: PASS — No shadow classification detected.")

    if args.fail and len(violations) > 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
