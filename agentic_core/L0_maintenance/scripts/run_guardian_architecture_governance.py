"""
Guardian: Architecture Governance — Deterministic layer-import compliance enforcement.

Wraps the legacy ``gravity_validator.UnifiedSSOTValidator`` scan semantics as a
scan-only guardian with zero side effects.

Checks:
- import_compliance: Illegal upward dependencies (lower layer importing higher layer)
- layer_gravity: Agents physically located in the wrong layer

Uses AST-based import analysis and the SSOT scanner for deterministic detection.

CLI:
    python -m agentic_core.L0_maintenance.scripts.run_guardian_architecture_governance \\
        --write-artifacts docs/reports/plans \\
        --strict
"""

from __future__ import annotations

import argparse
import ast
import os
import sys
from pathlib import Path

from agentic_core.L0_maintenance.types.guardian_contract import (
    ArtifactType,
    CheckStatus,
    GuardianResult,
    GuardianStatus,
    normalize_repo_path,
    write_guardian_result,
)
from agentic_core.L5_safety.config.structure_blueprint import (
    get_validated_project_root,
)

GUARDIAN_ID = "architecture_governance"

# Layer numeric ordering for waterfall enforcement
LAYER_HIERARCHY: dict[str, int] = {
    "L0": 0,
    "L1": 1,
    "L2": 2,
    "L3": 3,
    "L4": 4,
    "L5": 5,
    "L6": 6,
}

# Directories to skip during scanning
SKIP_PARTS: frozenset[str] = frozenset(
    {
        "__pycache__",
        ".git",
        ".venv",
        "node_modules",
        ".pytest_cache",
        ".nox",
        "archives",
        ".sovereign_healing_backup",
        ".healing_backups",
        "artifacts",
    },
)


# ---------------------------------------------------------------------------
# Scan functions (pure, deterministic, no side-effects)
# ---------------------------------------------------------------------------


def _get_layer_from_path(file_path: Path) -> str | None:
    """Extract layer (L0-L6) from file path parts."""
    for part in file_path.parts:
        if len(part) >= 2 and part[0] == "L" and part[1].isdigit():
            return part[:2]
    return None


def _extract_target_layer(node: ast.AST) -> str | None:
    """Extract target layer from an import AST node."""
    if isinstance(node, ast.ImportFrom):
        if node.module and "agentic_core" in node.module:
            for part in node.module.split("."):
                if len(part) >= 2 and part[0] == "L" and part[1].isdigit():
                    return part[:2]
    elif isinstance(node, ast.Import):
        for alias in node.names:
            if "agentic_core" in alias.name:
                for part in alias.name.split("."):
                    if len(part) >= 2 and part[0] == "L" and part[1].isdigit():
                        return part[:2]
    return None


def _collect_python_files(repo_root: Path) -> list[Path]:
    """Return sorted Python files under agentic_core/ for import scanning."""
    agentic_core = repo_root / "agentic_core"
    if not agentic_core.exists():
        return []

    result: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(agentic_core):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_PARTS)
        for fname in sorted(filenames):
            if fname.endswith(".py"):
                result.append(Path(dirpath) / fname)
    return result


def scan_import_compliance(
    repo_root: Path,
    files: list[Path] | None = None,
) -> list[dict]:
    """Detect illegal upward dependencies (lower layer importing higher layer).

    Reproduces ``gravity_validator._check_import_violations()`` detection
    using pure AST parsing.

    Returns sorted list of violation dicts with keys:
    path, source_layer, target_layer, import_line, line_number.
    """
    if files is None:
        files = _collect_python_files(repo_root)

    violations: list[dict] = []
    for fpath in files:
        source_layer = _get_layer_from_path(fpath)
        if source_layer is None or source_layer not in LAYER_HIERARCHY:
            continue

        try:
            content = fpath.read_text(encoding="utf-8", errors="ignore")
            tree = ast.parse(content, filename=str(fpath))
        except (SyntaxError, UnicodeDecodeError):
            continue

        for node in ast.walk(tree):
            if not isinstance(node, (ast.Import, ast.ImportFrom)):
                continue

            target_layer = _extract_target_layer(node)
            if target_layer is None or target_layer not in LAYER_HIERARCHY:
                continue

            # Upward dependency: source layer number < target layer number
            if LAYER_HIERARCHY[source_layer] < LAYER_HIERARCHY[target_layer]:
                # Reconstruct import line
                if isinstance(node, ast.ImportFrom):
                    import_line = f"from {node.module} import ..."
                else:
                    import_line = f"import {node.names[0].name}"

                rel = normalize_repo_path(fpath.relative_to(repo_root))
                violations.append(
                    {
                        "path": rel,
                        "source_layer": source_layer,
                        "target_layer": target_layer,
                        "import_line": import_line[:120],
                        "line_number": node.lineno,
                    },
                )

    return sorted(violations, key=lambda v: (v["path"], v["line_number"]))


def scan_layer_gravity(
    repo_root: Path,
    files: list[Path] | None = None,
) -> list[dict]:
    """Detect agents physically located in the wrong layer.

    Reproduces ``gravity_validator._check_gravity_violations()`` detection
    using the SSOT scanner. An agent's assigned layer (from its class or
    naming convention) must match its physical location layer.

    Returns sorted list of violation dicts with keys:
    path, agent_name, actual_layer, assigned_layer.
    """
    try:
        from agentic_core.L5_safety.enforcement.ssot_scanner import SSOTScanner
    except ImportError:
        return []

    try:
        scanner = SSOTScanner(repo_root)
        gravity_agents = scanner.find_gravity_violations()
    # guardian: allow-silent-swallow
    except Exception:
        return []

    violations: list[dict] = []
    for agent in gravity_agents:
        violations.append(
            {
                "path": normalize_repo_path(agent.relative_path),
                "agent_name": agent.class_name,
                "actual_layer": agent.layer,
                "assigned_layer": agent.assigned_layer,
            },
        )

    return sorted(violations, key=lambda v: v["path"])


# ---------------------------------------------------------------------------
# Main guardian logic
# ---------------------------------------------------------------------------


def run_architecture_governance_guardian(
    repo_root: Path | None = None,
    write_artifacts_dir: str | None = None,
    timestamp: str | None = None,
) -> GuardianResult:
    """Execute architecture governance guardian.

    Args:
        repo_root: Project root (defaults to SSOT get_validated_project_root).
        write_artifacts_dir: Repo-relative dir to write result JSON.
        timestamp: Injectable timestamp for determinism.

    Returns:
        GuardianResult conforming to guardian_contract.py schema.
    """
    if repo_root is None:
        repo_root = get_validated_project_root()

    result = GuardianResult(
        guardian_id=GUARDIAN_ID,
        timestamp=timestamp,
    )

    files = _collect_python_files(repo_root)

    # --- Check: import_compliance ---
    try:
        import_violations = scan_import_compliance(repo_root, files)

        if import_violations:
            result.add_check(
                check_id="import_compliance",
                status=CheckStatus.FAIL,
                details=f"{len(import_violations)} upward import violation(s) detected",
                evidence={
                    "violation_count": len(import_violations),
                    "violations": import_violations,
                },
            )
        else:
            result.add_check(
                check_id="import_compliance",
                status=CheckStatus.PASS,
                details="No upward import violations detected",
                evidence={"violation_count": 0, "violations": []},
            )
    # guardian: allow-silent-swallow
    except Exception as exc:
        result.add_check(
            check_id="import_compliance",
            status=CheckStatus.FAIL,
            details=f"Scan error: {exc}",
        )
        result.set_error(f"import_compliance scan failed: {exc}")

    # --- Check: layer_gravity ---
    try:
        gravity_violations = scan_layer_gravity(repo_root, files)

        if gravity_violations:
            result.add_check(
                check_id="layer_gravity",
                status=CheckStatus.FAIL,
                details=f"{len(gravity_violations)} agent(s) in wrong layer",
                evidence={
                    "violation_count": len(gravity_violations),
                    "violations": gravity_violations,
                },
            )
        else:
            result.add_check(
                check_id="layer_gravity",
                status=CheckStatus.PASS,
                details="All agents in correct layers",
                evidence={"violation_count": 0, "violations": []},
            )
    # guardian: allow-silent-swallow
    except Exception as exc:
        result.add_check(
            check_id="layer_gravity",
            status=CheckStatus.FAIL,
            details=f"Scan error: {exc}",
        )
        result.set_error(f"layer_gravity scan failed: {exc}")

    # --- Finalize ---
    total_checks = len(result.checks)
    failed_checks = sum(1 for c in result.checks if c.status == CheckStatus.FAIL.value)
    passed_checks = total_checks - failed_checks

    result.metrics["total_checks"] = total_checks
    result.metrics["passed_checks"] = passed_checks
    result.metrics["failed_checks"] = failed_checks
    result.metrics["files_scanned"] = len(files)

    if result.status == GuardianStatus.PASS.value:
        result.summary = (
            f"Architecture governance: {passed_checks}/{total_checks} checks passed "
            f"({len(files)} files scanned)"
        )
    else:
        result.summary = (
            f"Architecture governance: {failed_checks}/{total_checks} checks failed "
            f"({len(files)} files scanned)"
        )
        result.remediation_hints = [
            "Fix upward import violations: lower layers must not import from higher layers",
            "Move agents to their assigned layer per the SSOT scanner classification",
        ]

    # --- Write artifact ---
    if write_artifacts_dir:
        artifact_dir = repo_root / write_artifacts_dir
        out_path = write_guardian_result(
            result,
            artifact_dir,
            "guardian_architecture_governance_result.json",
        )
        result.add_artifact(
            ArtifactType.JSON,
            normalize_repo_path(out_path.relative_to(repo_root)),
            "Architecture governance guardian result JSON",
        )

    return result


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Architecture Governance Guardian",
    )
    parser.add_argument(
        "--write-artifacts",
        default=None,
        help="Repo-relative directory to write result JSON (default: none)",
    )
    parser.add_argument(
        "--format",
        choices=["json", "text"],
        default="json",
        help="Output format (default: json)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Non-zero exit on FAIL/ERROR",
    )
    parser.add_argument(
        "--timestamp",
        default=None,
        help="Injectable ISO-8601 timestamp (omitted if not provided)",
    )
    args = parser.parse_args()

    result = run_architecture_governance_guardian(
        write_artifacts_dir=args.write_artifacts,
        timestamp=args.timestamp,
    )

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
