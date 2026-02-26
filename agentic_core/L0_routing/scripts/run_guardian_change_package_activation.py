"""
Guardian: Change Package Activation Guard — AST-based enforcement of
proposal_only=True meta-learning invariant.

No ChangePackage may be activated without BOTH version_store and
approval_gate injections.  Direct VersionStore commits are forbidden.

Checks:
- proposal_only_bypass
- direct_version_store_commit
- activation_without_approval_gate

Scan roots: agentic_core/, system_learning/
"""

from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path

from agentic_core.L0_routing.types.guardian_contract import (
    CheckStatus,
    GuardianResult,
    GuardianStatus,
    normalize_repo_path,
    write_guardian_result,
)
from agentic_core.L0_routing.utils.project_root import get_validated_project_root

GUARDIAN_ID = "change_package_activation_guard"

SCAN_ROOTS: tuple[str, ...] = ("agentic_core", "system_learning")
SKIP_DIRS: frozenset[str] = frozenset({"__pycache__", ".git", ".venv", ".pytest_cache", ".nox", "archives"})

# Direct VersionStore commit method names
VERSION_STORE_COMMIT_METHODS: frozenset[str] = frozenset({"commit", "write", "persist", "save"})
VERSION_STORE_CLASS_NAMES: frozenset[str] = frozenset({"VersionStore", "version_store"})

# Activation call names that must be gated
ACTIVATION_CALL_NAMES: frozenset[str] = frozenset({"activate", "apply_change_package", "execute_change"})


def _collect_files(repo_root: Path) -> list[Path]:
    result: list[Path] = []
    for root_name in sorted(SCAN_ROOTS):
        root_path = repo_root / root_name
        if not root_path.exists():
            continue
        for dirpath, dirnames, filenames in __import__("os").walk(root_path):
            dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
            for fname in sorted(filenames):
                if fname.endswith(".py"):
                    result.append(Path(dirpath) / fname)
    return result


def scan_activation_patterns(
    repo_root: Path,
    files: list[Path] | None = None,
) -> dict[str, list[dict]]:
    if files is None:
        files = _collect_files(repo_root)

    bypass_viols: list[dict] = []
    vs_commit_viols: list[dict] = []
    gate_viols: list[dict] = []

    for fpath in files:
        rel = normalize_repo_path(fpath.relative_to(repo_root))
        try:
            tree = ast.parse(fpath.read_text(encoding="utf-8", errors="replace"))
        except SyntaxError:
            continue

        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            func = node.func

            # direct_version_store_commit: <version_store_var>.<commit_method>(...)
            if isinstance(func, ast.Attribute):
                if func.attr in VERSION_STORE_COMMIT_METHODS:
                    if isinstance(func.value, ast.Name) and func.value.id in VERSION_STORE_CLASS_NAMES:
                        vs_commit_viols.append(
                            {
                                "path": rel,
                                "line": node.lineno,
                                "detail": f"{func.value.id}.{func.attr}() — direct VersionStore write",
                            }
                        )

                # proposal_only_bypass / activation_without_approval_gate:
                # <obj>.activate() or apply_change_package() calls
                if func.attr in ACTIVATION_CALL_NAMES:
                    # Check keyword args — must include approval_gate=
                    kwarg_names = {kw.arg for kw in node.keywords}
                    if "approval_gate" not in kwarg_names:
                        gate_viols.append(
                            {
                                "path": rel,
                                "line": node.lineno,
                                "detail": f".{func.attr}() missing approval_gate kwarg",
                            }
                        )
                    if "version_store" not in kwarg_names and "proposal_only" not in kwarg_names:
                        bypass_viols.append(
                            {
                                "path": rel,
                                "line": node.lineno,
                                "detail": f".{func.attr}() missing version_store/proposal_only kwarg",
                            }
                        )

    return {
        "proposal_only_bypass": sorted(bypass_viols, key=lambda v: (v["path"], v["line"])),
        "direct_version_store_commit": sorted(vs_commit_viols, key=lambda v: (v["path"], v["line"])),
        "activation_without_approval_gate": sorted(gate_viols, key=lambda v: (v["path"], v["line"])),
    }


def run_change_package_activation_guardian(
    repo_root: Path | None = None,
    write_artifacts_dir: str | None = None,
    timestamp: str | None = None,
    correlation_id: str | None = None,
) -> GuardianResult:
    if repo_root is None:
        repo_root = get_validated_project_root()
    result = GuardianResult(
        guardian_id=GUARDIAN_ID,
        timestamp=timestamp,
        correlation_id=correlation_id,
    )

    viols = scan_activation_patterns(repo_root)
    for check_id in (
        "proposal_only_bypass",
        "direct_version_store_commit",
        "activation_without_approval_gate",
    ):
        v = viols[check_id]
        if v:
            result.add_check(
                check_id, CheckStatus.FAIL, f"{len(v)} violation(s)", evidence={"violations": v[:20]}
            )
        else:
            result.add_check(check_id, CheckStatus.PASS, "No violations detected")

    total = sum(len(v) for v in viols.values())
    result.summary = f"change_package_activation_guard: {total} violation(s)"
    if write_artifacts_dir:
        write_guardian_result(result, write_artifacts_dir, correlation_id=correlation_id)
    return result


def _main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Guardian: change_package_activation_guard")
    parser.add_argument("--write-artifacts", default=None)
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--correlation-id", default=None)
    args = parser.parse_args(argv)
    result = run_change_package_activation_guardian(
        artifact_dir=args.write_artifacts,
        correlation_id=args.correlation_id,
    )
    if args.strict and result.status == GuardianStatus.FAIL.value:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(_main())
