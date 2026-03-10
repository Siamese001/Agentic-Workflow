"""
Guardian: Escalation Determinism — AST-based detection of non-deterministic
escalation context construction.

Escalation paths must be built from structured, typed inputs only.
Raw-note concatenation or mutable-context patterns are forbidden.

Checks:
- failure_signal_built_from_raw_notes
- alternate_escalation_context_construction
- escalation_context_mutation

Scan roots: agentic_core/, apps_lic/, apps_rg/
"""

from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path

from agentic_core.L0_routing.types.guardian_contract_types import (
MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

    CheckStatus,
    GuardianResult,
    GuardianStatus,
    normalize_repo_path,
    write_guardian_result,
)
from agentic_core.L0_routing.utils.project_root_util import get_validated_project_root
from agentic_core.L5_safety.config.structure_blueprint.ssot import (
    DISCOVERY_EXCLUDED_TERRITORIES,
    GLOBAL_EXCLUDED_DIRS,
    SOVEREIGN_EXCLUDED_FOLDERS,
)

GUARDIAN_ID = "escalation_determinism"

SCAN_ROOTS: tuple[str, ...] = (AGENTIC_CORE_DIR, APPS_LIC_DIR, APPS_RG_DIR)
SKIP_DIRS: frozenset[str] = GLOBAL_EXCLUDED_DIRS | SOVEREIGN_EXCLUDED_FOLDERS | DISCOVERY_EXCLUDED_TERRITORIES

# Functions that must not be called with free-form string args as escalation inputs
RAW_NOTE_SENTINELS: frozenset[str] = frozenset(
    {
        "FailureSignal",
        "EscalationContext",
        "EscalationRecord",
    }
)

# In-place mutation method names on escalation types
MUTATION_METHOD_NAMES: frozenset[str] = frozenset(
    {
        "append",
        "update",
        "extend",
        "setdefault",
        "__setitem__",
        "add_note",
        "set_context",
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


def scan_escalation_patterns(
    repo_root: Path,
    files: list[Path] | None = None,
) -> dict[str, list[dict]]:
    if files is None:
        files = _collect_files(repo_root)

    raw_note_viols: list[dict] = []
    alt_ctx_viols: list[dict] = []
    mutation_viols: list[dict] = []

    for fpath in files:
        rel = normalize_repo_path(fpath.relative_to(repo_root))
        try:
            tree = ast.parse(fpath.read_text(encoding="utf-8", errors="replace"))
        except SyntaxError:
            continue

        for node in ast.walk(tree):
            # failure_signal_built_from_raw_notes:
            # FailureSignal(...) or EscalationContext(...) call where any
            # positional arg is a JoinedStr (f-string) or BinOp(str concat)
            if isinstance(node, ast.Call):
                fname_node = node.func
                call_name = None
                if isinstance(fname_node, ast.Name):
                    call_name = fname_node.id
                elif isinstance(fname_node, ast.Attribute):
                    call_name = fname_node.attr

                if call_name in RAW_NOTE_SENTINELS:
                    for arg in node.args:
                        if isinstance(arg, (ast.JoinedStr, ast.BinOp)):
                            raw_note_viols.append(
                                {
                                    "path": rel,
                                    "line": node.lineno,
                                    "detail": f"{call_name}() receives f-string/concat arg",
                                }
                            )
                            break

            # escalation_context_mutation:
            # <var>.<mutation_method>(...) where var name contains "escalation"/"context"
            if isinstance(node, ast.Call):
                func = node.func
                if isinstance(func, ast.Attribute) and func.attr in MUTATION_METHOD_NAMES:
                    if isinstance(func.value, ast.Name):
                        vname = func.value.id.lower()
                        if "escalation" in vname or "context" in vname or "signal" in vname:
                            mutation_viols.append(
                                {
                                    "path": rel,
                                    "line": node.lineno,
                                    "detail": f"{func.value.id}.{func.attr}() — mutation on escalation obj",
                                }
                            )

    return {
        "failure_signal_built_from_raw_notes": sorted(raw_note_viols, key=lambda v: (v["path"], v["line"])),
        "alternate_escalation_context_construction": sorted(
            alt_ctx_viols, key=lambda v: (v["path"], v["line"])
        ),
        "escalation_context_mutation": sorted(mutation_viols, key=lambda v: (v["path"], v["line"])),
    }


def run_escalation_determinism_guardian(
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

    viols = scan_escalation_patterns(repo_root)
    for check_id in (
        "failure_signal_built_from_raw_notes",
        "alternate_escalation_context_construction",
        "escalation_context_mutation",
    ):
        v = viols[check_id]
        if v:
            result.add_check(
                check_id, CheckStatus.FAIL, f"{len(v)} violation(s)", evidence={"violations": v[:20]}
            )
        else:
            result.add_check(check_id, CheckStatus.PASS, "No violations detected")

    total = sum(len(v) for v in viols.values())
    result.summary = f"escalation_determinism: {total} violation(s)"
    if write_artifacts_dir:
        write_guardian_result(result, write_artifacts_dir, correlation_id=correlation_id)
    return result


def _main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Guardian: escalation_determinism")
    parser.add_argument("--write-artifacts", default=None)
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--correlation-id", default=None)
    args = parser.parse_args(argv)
    result = run_escalation_determinism_guardian(
        artifact_dir=args.write_artifacts,
        correlation_id=args.correlation_id,
    )
    if args.strict and result.status == GuardianStatus.FAIL.value:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(_main())
