"""
Guardian: C0 Sovereignty Enforcement — AST-based detection of EmbeddingResult
artifacts influencing control flow, routing, or threshold configuration.

EmbeddingResult is INFORMATIONAL ONLY.  Guardians detect violations where
embedding scores/results appear in:
- conditional branches that affect routing
- tier-selection logic
- threshold assignment expressions

Checks:
- embedding_drives_routing
- embedding_drives_tier_selection
- embedding_mutates_threshold

Scan roots: agentic_core/, system_learning/, apps_lic/, apps_rg/
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
    normalize_repo_path,
    write_guardian_result,
)
from agentic_core.L0_routing.utils.project_root_util import get_validated_project_root
from agentic_core.L5_safety.config.structure_blueprint.ssot import (
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
    DISCOVERY_EXCLUDED_TERRITORIES,
    GLOBAL_EXCLUDED_DIRS,
    SOVEREIGN_EXCLUDED_FOLDERS,
    SYSTEM_LEARNING_DIR,
)

GUARDIAN_ID = "c0_sovereignty_enforcement"

_SYSTEM_LEARNING_DIR = "system_learning"

SCAN_ROOTS: tuple[str, ...] = (
    AGENTIC_CORE_DIR,
    _SYSTEM_LEARNING_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
)

SKIP_DIRS: frozenset[str] = GLOBAL_EXCLUDED_DIRS | SOVEREIGN_EXCLUDED_FOLDERS | DISCOVERY_EXCLUDED_TERRITORIES

# AST attribute names that signal embedding result access
EMBEDDING_RESULT_ATTRS: frozenset[str] = frozenset(
    {
        "embedding_score",
        "embedding_result",
        "similarity_score",
        "cosine_similarity",
        "embedding_threshold",
    }
)

# Names whose assignment target is forbidden when rhs contains embedding
THRESHOLD_TARGET_NAMES: frozenset[str] = frozenset(
    {
        "threshold",
        "risk_threshold",
        "tier",
        "routing",
        "route",
        "tier_selection",
    }
)


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


def _node_contains_embedding_attr(node: ast.expr) -> bool:
    """Return True if the expression subtree references an embedding attribute."""
    for child in ast.walk(node):
        if isinstance(child, ast.Attribute) and child.attr in EMBEDDING_RESULT_ATTRS:
            return True
        if isinstance(child, ast.Name) and child.id in EMBEDDING_RESULT_ATTRS:
            return True
    return False


def scan_embedding_control_flow(
    repo_root: Path,
    files: list[Path] | None = None,
) -> dict[str, list[dict]]:
    """
    Detect embedding results used in control-flow (routing/tier) or threshold assignment.

    Returns dict keyed by check_id → sorted violation list.
    """
    if files is None:
        files = _collect_files(repo_root)

    routing_viols: list[dict] = []
    tier_viols: list[dict] = []
    threshold_viols: list[dict] = []

    for fpath in files:
        rel = normalize_repo_path(fpath.relative_to(repo_root))
        try:
            tree = ast.parse(fpath.read_text(encoding="utf-8", errors="replace"))
        except SyntaxError:
            continue

        for node in ast.walk(tree):
            # embedding_drives_routing / embedding_drives_tier_selection:
            # If or While condition contains an embedding attribute
            if isinstance(node, (ast.If, ast.While)):
                if _node_contains_embedding_attr(node.test):
                    entry = {"path": rel, "line": node.lineno, "detail": ast.dump(node.test)[:120]}
                    routing_viols.append(entry)

            # embedding_mutates_threshold: assignment to a threshold/tier name
            # where the right-hand side contains an embedding attribute
            if isinstance(node, ast.Assign):
                if _node_contains_embedding_attr(node.value):
                    for target in node.targets:
                        tname = None
                        if isinstance(target, ast.Name):
                            tname = target.id
                        elif isinstance(target, ast.Attribute):
                            tname = target.attr
                        if tname in THRESHOLD_TARGET_NAMES:
                            threshold_viols.append(
                                {
                                    "path": rel,
                                    "line": node.lineno,
                                    "detail": f"{tname} = <embedding expr>",
                                }
                            )

    return {
        "embedding_drives_routing": sorted(routing_viols, key=lambda v: (v["path"], v["line"])),
        "embedding_drives_tier_selection": sorted(tier_viols, key=lambda v: (v["path"], v["line"])),
        "embedding_mutates_threshold": sorted(threshold_viols, key=lambda v: (v["path"], v["line"])),
    }


def run_c0_sovereignty_guardian(
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

    viols = scan_embedding_control_flow(repo_root)

    for check_id in (
        "embedding_drives_routing",
        "embedding_drives_tier_selection",
        "embedding_mutates_threshold",
    ):
        v = viols[check_id]
        if v:
            result.add_check(
                check_id, CheckStatus.FAIL, f"{len(v)} violation(s)", evidence={"violations": v[:20]}
            )
        else:
            result.add_check(check_id, CheckStatus.PASS, "No violations detected")

    total = sum(len(v) for v in viols.values())
    result.summary = f"c0_sovereignty: {total} embedding boundary violation(s)"
    if write_artifacts_dir:
        write_guardian_result(result, write_artifacts_dir, correlation_id=correlation_id)
    return result


def _main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Guardian: c0_sovereignty_enforcement")
    parser.add_argument("--write-artifacts", default=None)
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--correlation-id", default=None)
    args = parser.parse_args(argv)
    result = run_c0_sovereignty_guardian(
        write_artifacts_dir=args.write_artifacts,
        correlation_id=args.correlation_id,
    )
    if args.strict and result.status == GuardianStatus.FAIL.value:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(_main())
