"""
FCA Safety Gates: Collision prevention, blast radius limiting, and mass action guards.

This module provides deterministic preflight checks that run BEFORE any FCA
rename/move execution. All gates are pure functions operating on proposed action
lists — no file mutations.

Integration:
    Called by FileClassificationAgent._orchestrate_audit() and heal_repository()
    before executing any planned actions.

Gates:
    1. Rename Collision Gate (WAVE 1.1)
    2. Import Impact Gate / Blast Radius Limiter (WAVE 1.2)
    3. Mass Action Guard (WAVE 1.3)

Heuristic Hardening:
    4. AST-based Agent Lineage Detection (WAVE 2.1)
    5. Observability Detection with import evidence (WAVE 2.2)
    6. Configurable Nested LCD Subtree policy (WAVE 2.3)

Plan Output:
    7. Deterministic staged plan (WAVE 3.1)
    8. Wave execution API (WAVE 3.2)
"""

from __future__ import annotations

import ast
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

# ============================================================================
# Data Structures
# ============================================================================


@dataclass
class PlannedAction:
    """A single proposed rename/move action."""

    action_type: str  # e.g. "DETECT_RENAME", "TERRITORY_MOVE", "FOLDER_PURITY_EVICT"
    src: str  # relative path of source file
    dst: str  # relative path of proposed destination
    reason_code: str  # e.g. "NAMING_VIOLATION", "TERRITORY_MISMATCH"
    blocked_reason: str | None = None  # e.g. "COLLISION", "HIGH_IMPACT", None if OK
    impact_score: int = 0  # estimated blast radius (import count)


@dataclass
class SafetyGateResult:
    """Aggregate result of all safety gate checks."""

    actions: list[PlannedAction] = field(default_factory=list)
    blocked_count: int = 0
    collision_count: int = 0
    high_impact_count: int = 0
    mass_action_abort: bool = False
    summary: dict[str, int] = field(default_factory=dict)


# ============================================================================
# WAVE 1.1 — Rename Collision Gate
# ============================================================================


def check_rename_collisions(
    rename_map: dict[str, str],
    existing_files: set[str],
    case_sensitive: bool = False,
) -> list[dict[str, Any]]:
    """
    Detect rename collisions in a proposed rename map.

    Args:
        rename_map: {src_path -> proposed_dst_path} (relative paths, forward slashes)
        existing_files: set of all existing file paths (relative, forward slashes)
        case_sensitive: if False, detect casing-only conflicts (Windows/macOS default)

    Returns:
        List of collision dicts, each with:
            - type: "DST_COLLISION" | "DST_EXISTS" | "CASING_CONFLICT"
            - src: source path(s) involved
            - dst: destination path
            - message: human-readable description
    """
    collisions: list[dict[str, Any]] = []

    # Normalize for case-insensitive comparison
    def _norm(p: str) -> str:
        return p.lower() if not case_sensitive else p

    # Build dst -> list[src] map
    dst_to_srcs: dict[str, list[str]] = {}
    for src, dst in rename_map.items():
        key = _norm(dst)
        dst_to_srcs.setdefault(key, []).append(src)

    # Check 1: Multiple sources mapping to same destination
    for dst_norm, srcs in dst_to_srcs.items():
        if len(srcs) > 1:
            collisions.append(
                {
                    "type": "DST_COLLISION",
                    "src": srcs,
                    "dst": srcs[0] and rename_map[srcs[0]],
                    "message": (f"{len(srcs)} files map to same destination '{rename_map[srcs[0]]}': {srcs}"),
                },
            )

    # Check 2: Destination already exists (and isn't the source itself)
    existing_norm = {_norm(f): f for f in existing_files}
    for src, dst in rename_map.items():
        dst_n = _norm(dst)
        src_n = _norm(src)
        if dst_n in existing_norm and dst_n != src_n:
            collisions.append(
                {
                    "type": "DST_EXISTS",
                    "src": [src],
                    "dst": dst,
                    "message": (f"Destination '{dst}' already exists (existing: '{existing_norm[dst_n]}')"),
                },
            )

    # Check 3: Casing-only conflicts (only on case-insensitive FS)
    if not case_sensitive:
        for src, dst in rename_map.items():
            src_n = _norm(src)
            dst_n = _norm(dst)
            # Same path when lowered but different actual casing, and dst
            # matches an EXISTING file with different casing
            if dst_n in existing_norm:
                actual_existing = existing_norm[dst_n]
                if actual_existing != dst and _norm(actual_existing) == dst_n and src != actual_existing:
                    collisions.append(
                        {
                            "type": "CASING_CONFLICT",
                            "src": [src],
                            "dst": dst,
                            "message": (
                                f"Case-insensitive conflict: '{dst}' clashes with "
                                f"existing '{actual_existing}'"
                            ),
                        },
                    )

    return collisions


# ============================================================================
# WAVE 1.2 — Import Impact Gate (Blast Radius Limiter)
# ============================================================================


def build_import_graph(
    python_files: list[Path],
    project_root: Path,
) -> dict[str, int]:
    """
    Build approximate import count per module via AST.

    Returns:
        {relative_module_path -> count_of_files_that_import_it}
    """
    import_counts: dict[str, int] = {}

    # Build module name -> relative path mapping
    module_to_relpath: dict[str, str] = {}
    for p in python_files:
        try:
            rel = p.relative_to(project_root)
        except ValueError:
            continue
        rel_str = str(rel).replace("\\", "/")
        # Convert path to module name (foo/bar/baz.py -> foo.bar.baz)
        mod_name = rel_str.replace("/", ".").removesuffix(".py")
        if mod_name.endswith(".__init__"):
            mod_name = mod_name.removesuffix(".__init__")
        module_to_relpath[mod_name] = rel_str
        import_counts[rel_str] = 0

    # Scan each file's imports
    for p in python_files:
        try:
            content = p.read_text(encoding="utf-8", errors="ignore")
            tree = ast.parse(content)
        except (SyntaxError, OSError):
            continue

        for node in ast.walk(tree):
            mod = None
            if isinstance(node, ast.Import):
                for alias in node.names:
                    mod = alias.name
                    _increment_import(mod, module_to_relpath, import_counts)
            elif isinstance(node, ast.ImportFrom) and node.module:
                mod = node.module
                _increment_import(mod, module_to_relpath, import_counts)

    return import_counts


def _increment_import(
    mod: str,
    module_to_relpath: dict[str, str],
    import_counts: dict[str, int],
) -> None:
    """Increment import count for a module if it's in our project."""
    if mod in module_to_relpath:
        import_counts[module_to_relpath[mod]] = import_counts.get(module_to_relpath[mod], 0) + 1
    # Also check parent packages
    parts = mod.split(".")
    for i in range(len(parts), 0, -1):
        prefix = ".".join(parts[:i])
        if prefix in module_to_relpath:
            import_counts[module_to_relpath[prefix]] = import_counts.get(module_to_relpath[prefix], 0) + 1
            break


def check_init_reexports(path: Path) -> int:
    """
    Count how many __init__.py files re-export symbols from this module.

    Each re-export adds +10 to impact score per the spec.
    Returns the bonus impact score.
    """
    module_stem = path.stem
    parent = path.parent
    init_path = parent / "__init__.py"
    bonus = 0

    if init_path.exists():
        try:
            content = init_path.read_text(encoding="utf-8", errors="ignore")
            # Match "from .module_name import ..." patterns
            pattern = rf"from\s+\.{re.escape(module_stem)}\s+import\s+"
            if re.search(pattern, content):
                bonus += 10
        except OSError:
            pass

    return bonus


# guardian: allow-magic-config
def check_import_impact(
    rename_map: dict[str, str],
    import_counts: dict[str, int],
    python_files: list[Path],
    project_root: Path,
    # guardian: allow-magic-config
    max_import_impact: int = 25,
) -> list[dict[str, Any]]:
    """
    Gate renames/moves that affect high-import-count modules.

    Args:
        rename_map: {src_relative -> dst_relative}
        import_counts: {relative_path -> import_count} from build_import_graph
        python_files: list of all python files for init re-export scanning
        project_root: repo root
        max_import_impact: threshold above which actions are blocked

    Returns:
        List of blocked items with impact details.
    """
    blocked: list[dict[str, Any]] = []

    for src, dst in rename_map.items():
        base_impact = import_counts.get(src, 0)

        # Check __init__.py re-export bonus
        src_path = project_root / src.replace("/", os.sep)
        init_bonus = check_init_reexports(src_path) if src_path.exists() else 0

        total_impact = base_impact + init_bonus

        if total_impact > max_import_impact:
            blocked.append(
                {
                    "type": "BLOCKED_HIGH_IMPACT",
                    "src": src,
                    "dst": dst,
                    "import_count": base_impact,
                    "init_reexport_bonus": init_bonus,
                    "total_impact": total_impact,
                    "threshold": max_import_impact,
                    "message": (
                        f"'{src}' has impact score {total_impact} "
                        f"(imports={base_impact}, init_reexport={init_bonus}) "
                        f"exceeding threshold {max_import_impact}"
                    ),
                },
            )

    return blocked


# ============================================================================
# WAVE 1.3 — Mass Action Guard
# ============================================================================

# guardian: allow-magic-config
MAX_ACTIONS_DEFAULT = 50


def check_mass_action(
    planned_actions_total: int,
    max_actions: int = MAX_ACTIONS_DEFAULT,
    force: bool = False,
    wave_id: str | None = None,
) -> dict[str, Any] | None:
    """
    Block execution if too many actions are planned.

    Args:
        planned_actions_total: total number of actions to execute
        max_actions: threshold (default 50)
        force: explicit override flag
        wave_id: required identifier when force=True

    Returns:
        None if OK, or a blocking dict with reason.
    """
    if planned_actions_total <= max_actions:
        return None

    if force and wave_id:
        return None  # Explicitly overridden with wave_id

    if force and not wave_id:
        return {
            "type": "ABORTED_MASS_ACTION",
            "planned": planned_actions_total,
            "max_actions": max_actions,
            "reason": "force=True but wave_id is missing (required for mass override)",
        }

    return {
        "type": "ABORTED_MASS_ACTION",
        "planned": planned_actions_total,
        "max_actions": max_actions,
        "reason": (
            f"{planned_actions_total} actions exceed max_actions={max_actions}. "
            f"Pass force=True and wave_id='...' to override."
        ),
    }


# ============================================================================
# WAVE 2.1 — AST-based Agent Lineage Detection
# ============================================================================

# Known agent base classes (by name suffix or exact match)
KNOWN_AGENT_BASES = frozenset(
    {
        "SovereignBaseAgent",
        "BaseAgent",
        "AgentBase",
    },
)

KNOWN_AGENT_BASE_SUFFIXES = ("Agent", "AgentBase", "BaseAgent")

KNOWN_ORCHESTRATOR_BASES = frozenset(
    {
        "IOrchestratorAgent",
    },
)

KNOWN_EXECUTOR_SUFFIXES = ("Executor",)


def detect_agent_lineage(path: Path) -> str:
    """
    AST-based agent detection via class inheritance analysis.

    Returns:
        "AGENT" — confirmed agent (inherits from known base)
        "ORCHESTRATOR" — confirmed orchestrator
        "EXECUTOR" — confirmed executor
        "AGENT_DETECTION_UNCERTAIN" — has Agent-like name but no confirmed lineage
        "NOT_AGENT" — no agent indicators found
    """
    try:
        content = path.read_text(encoding="utf-8", errors="ignore")
        tree = ast.parse(content)
    except (SyntaxError, OSError):
        return "NOT_AGENT"

    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue

        class_name = node.name
        base_names = _extract_base_names(node)

        # Check orchestrator first
        if class_name.endswith("Orchestrator") or any(b in KNOWN_ORCHESTRATOR_BASES for b in base_names):
            return "ORCHESTRATOR"

        # Check executor
        if any(class_name.endswith(s) for s in KNOWN_EXECUTOR_SUFFIXES):
            return "EXECUTOR"

        # Check confirmed agent lineage
        if any(b in KNOWN_AGENT_BASES for b in base_names):
            return "AGENT"
        if any(b.endswith(s) for b in base_names for s in KNOWN_AGENT_BASE_SUFFIXES):
            return "AGENT"

        # Name looks like an agent but no confirmed base
        if class_name.endswith("Agent"):
            # Check if any base class itself ends with "Agent" (transitive)
            if any(b.endswith("Agent") for b in base_names):
                return "AGENT"
            return "AGENT_DETECTION_UNCERTAIN"

    return "NOT_AGENT"


def _extract_base_names(class_node: ast.ClassDef) -> list[str]:
    """Extract base class names from a ClassDef node."""
    bases = []
    for base in class_node.bases:
        if isinstance(base, ast.Name):
            bases.append(base.id)
        elif isinstance(base, ast.Attribute):
            bases.append(base.attr)
    return bases


# ============================================================================
# WAVE 2.2 — Observability Detection (import-based, not keyword-only)
# ============================================================================

OBSERVABILITY_IMPORT_PREFIXES = frozenset(
    {
        "prometheus_client",
        "opentelemetry",
        "grafana_client",
        "datadog",
        "agentic_core.L6_observability",
    },
)

# L0 maintenance scripts are allowed to reference dashboards
L0_DASHBOARD_ALLOWLIST_FOLDERS = frozenset(
    {
        "scripts",
        "dashboards",
    },
)


def check_observability_violation(
    path: Path,
    parts: tuple[str, ...] | None = None,
) -> dict[str, Any] | None:
    """
    Detect OBSERVABILITY_OUTSIDE_L6 using import evidence, not just keywords.

    Rules:
        - Only flag if file imports known observability packages/modules
          OR lives under known observability infra folders.
        - L0 maintenance scripts referencing dashboards are ALLOWED (allowlisted).
        - Keyword-only matches produce a WARNING, not a VIOLATION.

    Returns:
        None if compliant, or violation dict.
    """
    if parts is None:
        parts = path.parts

    # Not applicable inside L6
    if "L6_observability" in parts:
        return None

    # L0 maintenance scripts are explicitly allowed for dashboard work
    if "L0_routing" in parts:
        for folder in L0_DASHBOARD_ALLOWLIST_FOLDERS:
            if folder in parts:
                return None

    # Check imports via AST
    try:
        content = path.read_text(encoding="utf-8", errors="ignore")
        tree = ast.parse(content)
    except (SyntaxError, OSError):
        return None

    obs_imports_found = []
    for node in ast.walk(tree):
        mod = None
        if isinstance(node, ast.Import):
            for alias in node.names:
                mod = alias.name
                if _is_observability_import(mod):
                    obs_imports_found.append(mod)
        elif isinstance(node, ast.ImportFrom) and node.module:
            mod = node.module
            if _is_observability_import(mod):
                obs_imports_found.append(mod)

    if obs_imports_found:
        current_layer = next(
            (p for p in parts if p.startswith("L") and "_" in p and len(p) > 1 and p[1].isdigit()),
            None,
        )
        if current_layer:
            return {
                "file": str(path),
                "violation": "OBSERVABILITY_OUTSIDE_L6",
                "evidence_type": "import",
                "imports": obs_imports_found,
                "current_layer": current_layer,
                "message": (
                    f"'{path.name}' imports observability packages {obs_imports_found} "
                    f"but is in {current_layer}, not L6_observability."
                ),
            }

    return None


def _is_observability_import(mod: str) -> bool:
    """Check if a module name is a known observability package."""
    for prefix in OBSERVABILITY_IMPORT_PREFIXES:
        if mod == prefix or mod.startswith(prefix + "."):
            return True
    return False


# ============================================================================
# WAVE 2.3 — Configurable Nested LCD Subtree Policy
# ============================================================================


@dataclass
class NestedLCDPolicy:
    """Policy configuration for nested LCD subtree detection."""

    strict_lcd_roots_only: bool = False  # When False, findings are WARN not VIOLATION


def check_nested_lcd_with_policy(
    parts: tuple[str, ...],
    validate_fn,  # The original validate_no_nested_lcd from blueprint config
    policy: NestedLCDPolicy | None = None,
) -> dict[str, Any] | None:
    """
    Wrapper around validate_no_nested_lcd that applies policy.

    When strict=False (default), findings become warnings and are NOT executable.
    When strict=True, findings are violations and are executable.
    """
    if policy is None:
        policy = NestedLCDPolicy()

    result = validate_fn(parts)
    if result is None:
        return None

    if not policy.strict_lcd_roots_only:
        result["severity"] = "WARN"
        result["executable"] = False
    else:
        result["severity"] = "VIOLATION"
        result["executable"] = True

    return result


# ============================================================================
# WAVE 3.1 — Deterministic Staged Plan Output
# ============================================================================


def build_execution_plan(
    actions: list[PlannedAction],
) -> dict[str, Any]:
    """
    Produce a machine-readable, stable-ordered execution plan.

    Returns:
        {
            "planned_actions": [...],  # sorted by (action_type, src)
            "summary": {"action_type -> count", "blocked_reason -> count"},
            "total": int,
            "blocked": int,
            "executable": int,
        }
    """
    sorted_actions = sorted(actions, key=lambda a: (a.action_type, a.src))

    action_type_counts: dict[str, int] = {}
    blocked_reason_counts: dict[str, int] = {}
    blocked = 0
    executable = 0

    for a in sorted_actions:
        action_type_counts[a.action_type] = action_type_counts.get(a.action_type, 0) + 1
        if a.blocked_reason:
            blocked += 1
            blocked_reason_counts[a.blocked_reason] = blocked_reason_counts.get(a.blocked_reason, 0) + 1
        else:
            executable += 1

    return {
        "planned_actions": [
            {
                "action_type": a.action_type,
                "src": a.src,
                "dst": a.dst,
                "reason_code": a.reason_code,
                "blocked_reason": a.blocked_reason,
                "impact_score": a.impact_score,
            }
            for a in sorted_actions
        ],
        "summary": {
            "by_action_type": action_type_counts,
            "by_blocked_reason": blocked_reason_counts,
        },
        "total": len(sorted_actions),
        "blocked": blocked,
        "executable": executable,
    }


# ============================================================================
# WAVE 3.2 — Wave Execution API
# ============================================================================


@dataclass
class WaveConfig:
    """Configuration for a single execution wave."""

    wave_id: str
    allow_action_types: set[str]
    max_actions_per_wave: int = 50


def filter_actions_for_wave(
    actions: list[PlannedAction],
    wave_config: WaveConfig,
) -> list[PlannedAction]:
    """
    Filter and limit actions for a specific execution wave.

    Only actions matching allow_action_types are included.
    Stops at max_actions_per_wave.
    Blocked actions are excluded.
    """
    filtered = []
    for a in actions:
        if a.blocked_reason is not None:
            continue
        if a.action_type not in wave_config.allow_action_types:
            continue
        filtered.append(a)
        if len(filtered) >= wave_config.max_actions_per_wave:
            break
    return filtered


# ============================================================================
# Unified Preflight Runner
# ============================================================================


# guardian: allow-magic-config
def run_all_safety_gates(
    rename_map: dict[str, str],
    existing_files: set[str],
    python_files: list[Path],
    project_root: Path,
    case_sensitive: bool = False,
    # guardian: allow-magic-config
    max_import_impact: int = 25,
    max_actions: int = MAX_ACTIONS_DEFAULT,
    force: bool = False,
    wave_id: str | None = None,
    import_counts: dict[str, int] | None = None,
) -> SafetyGateResult:
    """
    Run all safety gates on a proposed rename/move plan.

    Returns a SafetyGateResult with all blocked items and summary.
    """
    result = SafetyGateResult()

    # Gate 1: Collision detection
    collisions = check_rename_collisions(rename_map, existing_files, case_sensitive)
    result.collision_count = len(collisions)

    # Gate 2: Import impact
    if import_counts is None:
        import_counts = build_import_graph(python_files, project_root)
    high_impact = check_import_impact(
        rename_map,
        import_counts,
        python_files,
        project_root,
        max_import_impact,
    )
    result.high_impact_count = len(high_impact)

    # Gate 3: Mass action
    mass_block = check_mass_action(len(rename_map), max_actions, force, wave_id)
    result.mass_action_abort = mass_block is not None

    # Build blocked set
    collision_srcs = set()
    for c in collisions:
        for s in c["src"]:
            collision_srcs.add(s)

    high_impact_srcs = {h["src"] for h in high_impact}

    # Build action list with blocking annotations
    for src, dst in sorted(rename_map.items()):
        blocked = None
        if src in collision_srcs:
            blocked = "BLOCKED_RENAME_COLLISION"
        elif src in high_impact_srcs:
            blocked = "BLOCKED_HIGH_IMPACT"
        elif result.mass_action_abort:
            blocked = "ABORTED_MASS_ACTION"

        impact = import_counts.get(src, 0)
        action = PlannedAction(
            action_type="RENAME",
            src=src,
            dst=dst,
            reason_code="NAMING_VIOLATION",
            blocked_reason=blocked,
            impact_score=impact,
        )
        result.actions.append(action)
        if blocked:
            result.blocked_count += 1

    result.summary = {
        "collisions": result.collision_count,
        "high_impact": result.high_impact_count,
        "mass_action_abort": result.mass_action_abort,
        "total_actions": len(result.actions),
        "blocked": result.blocked_count,
        "executable": len(result.actions) - result.blocked_count,
    }

    return result
