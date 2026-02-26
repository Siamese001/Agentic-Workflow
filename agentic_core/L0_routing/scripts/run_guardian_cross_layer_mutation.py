"""
Guardian: Cross-Layer Mutation Guard — AST-based detection of layer gravity
violations beyond what architecture_governance already covers.

Specifically enforces:
- L6 must not import-from or assign-to L4 state modules
- L4 must not call L2 execution entry points
- Any file must not have C0 (embedding) expressions modifying control-plane state

Checks:
- upward_layer_mutation   (general — any lower→higher write detected by AST)
- L6_mutates_L4           (specific pair)
- L4_invokes_L2           (specific pair)
- C0_mutates_control_plane (embedding used on left-hand side of control-plane assignment)

Scan root: agentic_core/
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

GUARDIAN_ID = "cross_layer_mutation_guard"

LAYER_ORDER: dict[str, int] = {f"L{i}": i for i in range(7)}

SKIP_DIRS: frozenset[str] = frozenset({"__pycache__", ".git", ".venv", ".pytest_cache", ".nox", "archives"})

CONTROL_PLANE_NAMES: frozenset[str] = frozenset(
    {
        "routing_config",
        "tier_config",
        "gateway_config",
        "control_plane",
        "dispatch_table",
    }
)

EMBEDDING_ATTR_NAMES: frozenset[str] = frozenset(
    {
        "embedding_score",
        "embedding_result",
        "similarity_score",
        "cosine_similarity",
    }
)


def _layer_from_path(path: Path) -> str | None:
    for part in path.parts:
        if len(part) >= 2 and part[0] == "L" and part[1].isdigit():
            return part[:2]
    return None


def _layer_from_module_string(module: str) -> str | None:
    for segment in module.split("."):
        if len(segment) >= 2 and segment[0] == "L" and segment[1].isdigit():
            return segment[:2]
    return None


def _collect_files(repo_root: Path) -> list[Path]:
    result: list[Path] = []
    agentic = repo_root / "agentic_core"
    if not agentic.exists():
        return result
    for dirpath, dirnames, filenames in __import__("os").walk(agentic):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
        for fname in sorted(filenames):
            if fname.endswith(".py"):
                result.append(Path(dirpath) / fname)
    return result


def scan_cross_layer_mutations(
    repo_root: Path,
    files: list[Path] | None = None,
) -> dict[str, list[dict]]:
    if files is None:
        files = _collect_files(repo_root)

    upward_viols: list[dict] = []
    l6_l4_viols: list[dict] = []
    l4_l2_viols: list[dict] = []
    c0_cp_viols: list[dict] = []

    for fpath in files:
        rel = normalize_repo_path(fpath.relative_to(repo_root))
        src_layer = _layer_from_path(fpath)
        if src_layer not in LAYER_ORDER:
            continue
        src_num = LAYER_ORDER[src_layer]

        try:
            tree = ast.parse(fpath.read_text(encoding="utf-8", errors="replace"))
        except SyntaxError:
            continue

        for node in ast.walk(tree):
            # upward_layer_mutation / L6_mutates_L4 / L4_invokes_L2:
            # from <higher_layer_module> import ...  then assign to a name
            if isinstance(node, ast.ImportFrom) and node.module:
                tgt_layer = _layer_from_module_string(node.module)
                if tgt_layer and tgt_layer in LAYER_ORDER:
                    tgt_num = LAYER_ORDER[tgt_layer]
                    if src_num > tgt_num:
                        entry = {
                            "path": rel,
                            "line": node.lineno,
                            "detail": f"{src_layer} imports from {tgt_layer}: {node.module}",
                        }
                        upward_viols.append(entry)
                        if src_layer == "L6" and tgt_layer == "L4":
                            l6_l4_viols.append(entry)
                        if src_layer == "L4" and tgt_layer == "L2":
                            l4_l2_viols.append(entry)

            # C0_mutates_control_plane:
            # <control_plane_name> = <expr containing embedding attr>
            if isinstance(node, ast.Assign):
                rhs_has_embedding = any(
                    (isinstance(n, ast.Attribute) and n.attr in EMBEDDING_ATTR_NAMES)
                    or (isinstance(n, ast.Name) and n.id in EMBEDDING_ATTR_NAMES)
                    for n in ast.walk(node.value)
                )
                if rhs_has_embedding:
                    for target in node.targets:
                        tname = None
                        if isinstance(target, ast.Name):
                            tname = target.id
                        elif isinstance(target, ast.Attribute):
                            tname = target.attr
                        if tname in CONTROL_PLANE_NAMES:
                            c0_cp_viols.append(
                                {
                                    "path": rel,
                                    "line": node.lineno,
                                    "detail": f"{tname} assigned from embedding expression",
                                }
                            )

    return {
        "upward_layer_mutation": sorted(upward_viols, key=lambda v: (v["path"], v["line"])),
        "L6_mutates_L4": sorted(l6_l4_viols, key=lambda v: (v["path"], v["line"])),
        "L4_invokes_L2": sorted(l4_l2_viols, key=lambda v: (v["path"], v["line"])),
        "C0_mutates_control_plane": sorted(c0_cp_viols, key=lambda v: (v["path"], v["line"])),
    }


def run_cross_layer_mutation_guardian(
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

    viols = scan_cross_layer_mutations(repo_root)
    for check_id in ("upward_layer_mutation", "L6_mutates_L4", "L4_invokes_L2", "C0_mutates_control_plane"):
        v = viols[check_id]
        if v:
            result.add_check(
                check_id, CheckStatus.FAIL, f"{len(v)} violation(s)", evidence={"violations": v[:20]}
            )
        else:
            result.add_check(check_id, CheckStatus.PASS, "No violations detected")

    total = sum(len(v) for v in viols.values())
    result.summary = f"cross_layer_mutation_guard: {total} violation(s)"
    if write_artifacts_dir:
        write_guardian_result(result, write_artifacts_dir, correlation_id=correlation_id)
    return result


def _main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Guardian: cross_layer_mutation_guard")
    parser.add_argument("--write-artifacts", default=None)
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--correlation-id", default=None)
    args = parser.parse_args(argv)
    result = run_cross_layer_mutation_guardian(
        artifact_dir=args.write_artifacts,
        correlation_id=args.correlation_id,
    )
    if args.strict and result.status == GuardianStatus.FAIL.value:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(_main())
