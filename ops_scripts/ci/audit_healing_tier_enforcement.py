"""
Phase 1 Static Enforcement Audit — Confidence-Tier Healing Design.

Waves:
  1. Enumerate tiered agents: scan for router imports + allowlist membership.
  2. Detect direct escalation violations: gemini/qwen/vllm outside router.
  3. Confidence threshold validation: X > Y, retry override, no magic numbers.

Hard-fails on any violation. Prints deterministic table output.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
    L2_EXECUTION_DIR,
    get_validated_project_root,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "audit_healing_tier_enforcement")
_emit_applies_guardrail("p0", "audit_healing_tier_enforcement", "p0_governance")
_emit_reads_policy_state("p0", "audit_healing_tier_enforcement", "policy_binding")
_emit_snapshots_state("p0", "audit_healing_tier_enforcement", "state_snapshot")
emit_replay_key("p0", "audit_healing_tier_enforcement")
emit_determinism_digest("p0", "audit_healing_tier_enforcement")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

REPO_ROOT = get_validated_project_root()
ROUTER_MODULE = "agentic_core.L2_execution.healers.healing_tier_router"
ROUTER_FILE = REPO_ROOT / L2_EXECUTION_DIR / "healers" / "healing_tier_router.py"
ALLOWLIST_FILE = REPO_ROOT / L2_EXECUTION_DIR / "healers" / "tiering_allowlist.py"
CONFIG_FILE = REPO_ROOT / L2_EXECUTION_DIR / "healers" / "healing_tier_config.py"

# Scan roots for agent files
SCAN_ROOTS = [
    REPO_ROOT / AGENTIC_CORE_DIR,
    REPO_ROOT / APPS_LIC_DIR,
    REPO_ROOT / APPS_RG_DIR,
    REPO_ROOT / APPS_SHARED_DIR,
]

# Files that are part of the healing tier system itself (exempt from bypass check)
HEALING_TIER_SYSTEM_FILES: frozenset[str] = frozenset(
    {
        "agentic_core/L2_execution/healers/healing_tier_router.py",
        "agentic_core/L2_execution/healers/healing_tier_dispatcher.py",
        "agentic_core/L2_execution/healers/healing_tier_types.py",
        "agentic_core/L2_execution/healers/healing_tier_config.py",
        "agentic_core/L2_execution/healers/tiering_allowlist.py",
    }
)

# HealingTier enum member names -- direct use outside system files = bypass
HEALING_TIER_MEMBERS = {"LOCAL_AGENT", "QWEN_VLLM", "GEMINI_2_5_PRO"}


# ---------------------------------------------------------------------------
# AST helpers
# ---------------------------------------------------------------------------


def parse_file(path: Path) -> ast.Module | None:
    """Parse a Python file into an AST. Returns None on syntax error."""
    try:
        return ast.parse(path.read_text(encoding="utf-8", errors="replace"), filename=str(path))
    except SyntaxError:
        return None


def get_imports(tree: ast.Module) -> list[str]:
    """Extract all imported module names from an AST."""
    imports: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)
    return imports


def get_function_calls(tree: ast.Module) -> list[str]:
    """Extract all function call names from an AST."""
    calls: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                calls.append(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                calls.append(node.func.attr)
    return calls


def get_imported_names(tree: ast.Module) -> set[str]:
    """Extract all locally-bound names from import statements."""
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                names.add(alias.asname or alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                names.add(alias.asname or alias.name)
    return names


def file_directly_selects_healing_tier(path: Path) -> list[str]:
    """Return HealingTier member names used via HealingTier.<MEMBER> attribute access.

    Only flags files that import HealingTier AND reference its members directly.
    System files (router, types, config, allowlist) are exempt via caller.
    """
    tree = parse_file(path)
    if tree is None:
        return []

    imported_names = get_imported_names(tree)
    if "HealingTier" not in imported_names:
        return []

    found_members: list[str] = []
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Attribute)
            and node.attr in HEALING_TIER_MEMBERS
            and isinstance(node.value, ast.Name)
            and node.value.id == "HealingTier"
        ):
            found_members.append(node.attr)

    return list(set(found_members))


# ---------------------------------------------------------------------------
# Load allowlist from source (AST-based, no import)
# ---------------------------------------------------------------------------


def load_allowlist_from_source() -> tuple[frozenset[str], frozenset[str]]:
    """Extract TIERING_ALLOWLIST agent names and file paths via AST (no import)."""
    tree = parse_file(ALLOWLIST_FILE)
    if tree is None:
        print("FAIL: Could not parse tiering_allowlist.py", file=sys.stderr)
        sys.exit(1)

    agent_names: set[str] = set()
    file_paths: set[str] = set()

    for node in ast.walk(tree):
        # TIERING_ALLOWLIST is AnnAssign: frozenset[...] = frozenset({(str,str),...})
        if (
            isinstance(node, ast.AnnAssign)
            and isinstance(node.target, ast.Name)
            and node.target.id == "TIERING_ALLOWLIST"
            and node.value is not None
        ):
            rhs = node.value
            # RHS: Call(frozenset, [Set([Tuple(Constant, Constant), ...])])
            if isinstance(rhs, ast.Call) and rhs.args:
                inner = rhs.args[0]
                for elt in getattr(inner, "elts", []):
                    if (
                        isinstance(elt, ast.Tuple)
                        and len(elt.elts) == 2
                        and all(isinstance(e, ast.Constant) for e in elt.elts)
                    ):
                        agent_names.add(elt.elts[0].value)
                        file_paths.add(elt.elts[1].value)

    return frozenset(agent_names), frozenset(file_paths)


# ---------------------------------------------------------------------------
# Load config constants from source (AST-based, no import)
# ---------------------------------------------------------------------------


def load_config_constants() -> dict[str, float | int | str]:
    """Extract heal_confidence_x, heal_confidence_y, max_heal_retries from config source."""
    tree = parse_file(CONFIG_FILE)
    if tree is None:
        print("FAIL: Could not parse healing_tier_config.py", file=sys.stderr)
        sys.exit(1)

    constants: dict[str, float | int | str] = {}

    # Find load_default_healing_tier_config function and extract keyword args
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            for kw in node.keywords:
                if kw.arg in {
                    "heal_confidence_x",
                    "heal_confidence_y",
                    "max_heal_retries",
                    "model_qwen_vllm_id",
                    "model_gemini_2_5_pro_id",
                }:
                    if isinstance(kw.value, ast.Constant):
                        constants[kw.arg] = kw.value.value

    return constants


# ---------------------------------------------------------------------------
# Collect all Python files in scan roots
# ---------------------------------------------------------------------------


def collect_python_files() -> list[Path]:
    """Collect all .py files under SCAN_ROOTS, excluding __pycache__."""
    files: list[Path] = []
    for root in SCAN_ROOTS:
        if not root.exists():
            continue
        for p in root.rglob("*.py"):
            if "__pycache__" in p.parts:
                continue
            files.append(p)
    return sorted(files)


# ---------------------------------------------------------------------------
# Wave 1: Enumerate tiered agents
# ---------------------------------------------------------------------------


def wave1_enumerate_tiered_agents(
    allowlist_names: frozenset[str],
    allowlist_paths: frozenset[str],
    all_files: list[Path],
) -> list[dict]:
    """Produce table of agents: allowlisted? imports router? calls route_healing_tier?"""
    print("\n" + "=" * 70)
    print("WAVE 1: Enumerate Tiered Agents")
    print("=" * 70)

    rows: list[dict] = []

    for fpath in all_files:
        rel = fpath.relative_to(REPO_ROOT).as_posix()
        tree = parse_file(fpath)
        if tree is None:
            continue

        imports = get_imports(tree)
        calls = get_function_calls(tree)

        imports_router = any(ROUTER_MODULE in imp for imp in imports)
        calls_router = "route_healing_tier" in calls
        is_allowlisted = rel in allowlist_paths or fpath.stem in allowlist_names

        if not (is_allowlisted or imports_router or calls_router):
            continue

        rows.append(
            {
                "agent": fpath.stem,
                "path": rel,
                "allowlisted": is_allowlisted,
                "imports_router": imports_router,
                "calls_route_healing_tier": calls_router,
            }
        )

    col_w = [35, 60, 12, 15, 24]
    header = (
        f"{'Agent':<{col_w[0]}} {'Path':<{col_w[1]}} "
        f"{'Allowlisted':<{col_w[2]}} {'ImportsRouter':<{col_w[3]}} "
        f"{'CallsRouteHealTier':<{col_w[4]}}"
    )
    print(header)
    print("-" * sum(col_w))
    for row in rows:
        print(
            f"{row['agent']:<{col_w[0]}} {row['path']:<{col_w[1]}} "
            f"{'Y' if row['allowlisted'] else 'N':<{col_w[2]}} "
            f"{'Y' if row['imports_router'] else 'N':<{col_w[3]}} "
            f"{'Y' if row['calls_route_healing_tier'] else 'N':<{col_w[4]}}"
        )

    found_paths = {row["path"] for row in rows}
    missing = sorted(allowlist_paths - found_paths)
    if missing:
        print(f"\nINFO: {len(missing)} allowlisted agent(s) not yet importing router:")
        for m in missing:
            print(f"  NOT_YET_IMPORTING: {m}")

    print(f"\nOK: Wave 1 complete. {len(rows)} tiered-agent rows produced.")
    return rows


# ---------------------------------------------------------------------------
# Wave 2: Detect direct escalation violations
# ---------------------------------------------------------------------------


def wave2_detect_escalation_violations(all_files: list[Path]) -> None:
    """Scan all files for direct HealingTier member selection outside system files.

    A violation = non-system file imports HealingTier AND uses HealingTier.<MEMBER>
    directly (implying tier selection bypass of route_healing_tier).
    Test files are also exempt (they verify the router, not bypass it).
    """
    print("\n" + "=" * 70)
    print("WAVE 2: Detect Direct HealingTier Bypass Violations")
    print("=" * 70)

    violations: list[str] = []

    for fpath in all_files:
        rel = fpath.relative_to(REPO_ROOT).as_posix()
        # Exempt: system files and test files
        if rel in HEALING_TIER_SYSTEM_FILES:
            continue
        if "/tests/" in rel or rel.startswith("tests/"):
            continue

        members = file_directly_selects_healing_tier(fpath)
        if members:
            msg = f"  VIOLATION: {rel} — HealingTier members: {sorted(members)}"
            violations.append(msg)
            print(msg)

    if violations:
        print(
            f"\nFAIL: {len(violations)} file(s) directly select HealingTier members "
            f"outside the router (bypass detected).",
            file=sys.stderr,
        )
        sys.exit(1)

    print("OK: Wave 2 complete. 0 direct HealingTier bypass violations found.")


# ---------------------------------------------------------------------------
# Wave 3: Confidence threshold validation
# ---------------------------------------------------------------------------


def wave3_threshold_validation(constants: dict) -> None:
    """Assert X > Y, retry override, no magic numbers in router tier comparisons."""
    print("\n" + "=" * 70)
    print("WAVE 3: Confidence Threshold Validation")
    print("=" * 70)

    x = constants.get("heal_confidence_x")
    y = constants.get("heal_confidence_y")
    max_retries = constants.get("max_heal_retries")

    print(f"  heal_confidence_x = {x}")
    print(f"  heal_confidence_y = {y}")
    print(f"  max_heal_retries  = {max_retries}")

    # Assert X > Y
    if x is None or y is None:
        print("FAIL: Could not extract X/Y thresholds from config", file=sys.stderr)
        sys.exit(1)
    if not (x > y):
        print(f"FAIL: heal_confidence_x ({x}) must be > heal_confidence_y ({y})", file=sys.stderr)
        sys.exit(1)
    print(f"  OK: X ({x}) > Y ({y})")

    # Assert max_retries >= 1
    if max_retries is None or int(max_retries) < 1:
        print(f"FAIL: max_heal_retries ({max_retries}) must be >= 1", file=sys.stderr)
        sys.exit(1)
    print(f"  OK: max_heal_retries ({max_retries}) >= 1")

    # Assert router uses config constants, not magic numbers, for tier comparisons
    # Scan router AST for Compare nodes that use numeric literals instead of attribute access
    tree = parse_file(ROUTER_FILE)
    if tree is None:
        print("FAIL: Could not parse healing_tier_router.py", file=sys.stderr)
        sys.exit(1)

    # Assert router uses config attributes for X/Y comparisons, not magic literals.
    # Specifically: the Compare nodes for tier routing must reference config.heal_confidence_x
    # and config.heal_confidence_y (Attribute nodes), not raw float literals equal to X or Y.
    magic_number_violations: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Compare):
            all_operands = [node.left] + node.comparators
            for operand in all_operands:
                if isinstance(operand, ast.Constant) and isinstance(operand.value, float):
                    val = operand.value
                    # Flag if the literal equals X or Y (would be a magic number bypass)
                    if val == float(x) or val == float(y):
                        magic_number_violations.append(
                            f"    Magic literal {val} in Compare at line {node.lineno}"
                        )

    if magic_number_violations:
        print("FAIL: Router uses magic number literals for X/Y tier comparisons:", file=sys.stderr)
        for v in magic_number_violations:
            print(v, file=sys.stderr)
        sys.exit(1)

    print("  OK: Router tier comparisons use config attributes (no magic X/Y literals)")

    # Assert retry override: router must check retry_count >= max_heal_retries
    # Verify via AST: find Compare with retry_count and max_heal_retries attribute
    found_retry_check = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Compare):
            left_src = ast.unparse(node.left)
            for comp in node.comparators:
                comp_src = ast.unparse(comp)
                if "retry_count" in left_src and "max_heal_retries" in comp_src:
                    found_retry_check = True
                    break

    if not found_retry_check:
        print(
            "FAIL: Router does not contain retry_count >= max_heal_retries check",
            file=sys.stderr,
        )
        sys.exit(1)
    print("  OK: Router contains retry_count >= config.max_heal_retries override check")

    print("\nOK: Wave 3 complete. All threshold invariants satisfied.")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    print("=" * 70)
    print("HEALING TIER ENFORCEMENT AUDIT — Static Phase")
    print("=" * 70)

    # Verify required files exist
    for label, path in [
        ("router", ROUTER_FILE),
        ("allowlist", ALLOWLIST_FILE),
        ("config", CONFIG_FILE),
    ]:
        if not path.exists():
            print(f"FAIL: {label} file not found: {path}", file=sys.stderr)
            sys.exit(1)
    print("OK: All required healing tier source files present")

    allowlist_names, allowlist_paths = load_allowlist_from_source()
    print(f"OK: Loaded allowlist — {len(allowlist_names)} agents, {len(allowlist_paths)} paths")

    constants = load_config_constants()
    print(f"OK: Loaded config constants — {constants}")

    all_files = collect_python_files()
    print(f"OK: Collected {len(all_files)} Python files for scanning")

    wave1_enumerate_tiered_agents(allowlist_names, allowlist_paths, all_files)
    wave2_detect_escalation_violations(all_files)
    wave3_threshold_validation(constants)

    print("\n" + "=" * 70)
    print("AUDIT COMPLETE: All static enforcement invariants satisfied.")
    print("=" * 70)


if __name__ == "__main__":
    main()
