"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  CLASSIFICATION KERNEL — THE SINGLE SOURCE OF TRUTH (SSOT)                 ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  This module is the CANONICAL definition for file type classification      ║
║  across the entire Agentic-Workflow repository.                            ║
║                                                                            ║
║  ZERO DEPENDENCIES: Uses ONLY the Python standard library.                 ║
║  Any layer (L0–L6, Runtime, Apps, Tests) can safely import this module     ║
║  without risking circular imports.                                         ║
║                                                                            ║
║  Consumers:                                                                ║
║  - FileClassificationAgent.py (L5_safety) — full AST classification       ║
║  - full_agent_discovery.py (L0_routing) — agent manifest generation    ║
║  - complexity_visitor_util.py (L0_routing) — dashboard discovery       ║
║  - discovery_util.py (runtime) — runtime agent registry                   ║
║  - file_intent.py (prompt_governance) — prompt intent classification      ║
║  - type_erasure_validator.py (L5_safety) — type checking                  ║
║  - ssot_scanner.py, registry_verification.py (L5 enforcement)             ║
║  - tests/guardian/*, tests/integration/* — governance tests               ║
║                                                                            ║
║  MODIFICATION POLICY: Changes here affect the ENTIRE repository.           ║
║  Always run the full verification suite after edits.                       ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import ast
import logging
import re
from contextlib import contextmanager
from functools import lru_cache
from pathlib import Path
from typing import Literal

logger = logging.getLogger(__name__)


# ============================================================================
# FileType — Canonical type taxonomy for all Python files in the repo
# ============================================================================

FileType = Literal[
    "AGENT",
    "CLASS",
    "MIXIN",
    "UTILITY",
    "PROTOCOL",
    "ENGINE",
    "STUB",
    "TEST",
    "SCRIPT",
    "TYPES",
    "GATEWAY",
    "ORCHESTRATOR",
    "VALIDATOR",
    "FACTORY",
    "CONFIG",
    "CONFIG_WITH_LOGIC",  # CONFIG file containing executable methods (violation)
    "ADAPTER",
    "STRATEGY",
    "ENFORCER",
    "SEAM",
    "EXCEPTION",
    "SERVICE",
    "IGNORE",
]

# Classification conflict tracking for governance hardening
_classification_conflicts: list[dict] = []


def get_classification_conflicts() -> list[dict]:
    """Return list of dual-tag/ambiguity conflicts detected during classification."""
    return _classification_conflicts.copy()


def clear_classification_conflicts() -> None:
    """Clear the conflict tracking list."""
    global _classification_conflicts
    _classification_conflicts = []


# ============================================================================
# EXCLUDED / CRITICAL FILES — exempt from classification
# ============================================================================

_CRITICAL_IGNORES = frozenset(
    {
        "conftest.py",
        "__init__.py",
        "__main__.py",
        "setup.py",
        "tool_registry.py",
    },
)


# ============================================================================
# classify_file_standalone — Lightweight SSOT classification
# ============================================================================


def classify_file_standalone(path: Path) -> FileType:
    """
    Classify a Python file's architectural role using AST analysis.

    This is the CANONICAL, zero-dependency classification function.
    It mirrors the priority ordering of FileClassificationAgent.classify_file()
    but requires NO internal repo imports.

    Results are cached (LRU, maxsize=1024) keyed on resolved absolute path
    for high performance during batch scans.

    Priority Queue (first match wins):
        0. IGNORE  — Critical infrastructure files (__init__.py, conftest.py, etc.)
        1. CLASS   — Files in base_agents/ directory (foundational classes)
        2. STUB    — Files containing NOT_AN_AGENT marker
        3. TEST    — Files in tests/ or starting with test_
        4. SCRIPT  — No-class files with __main__ guard
        5. UTILITY — No-class files without __main__
        6. EXCEPTION — Primary class inherits from Exception/Error
        7. MIXIN   — Primary class name ends with 'Mixin'
        8. PROTOCOL — Primary class inherits from Protocol or file starts with I
        9. ORCHESTRATOR — Primary class name contains Orchestrator/Coordinator/Pipeline
       10. AGENT   — Primary class name ends with 'Agent' or inherits from *Agent
       11. STRATEGY — Primary class name ends with 'Strategy'
       12. ADAPTER  — Primary class name ends with Adapter/Wrapper/Bridge
       13. SERVICE  — Singleton pattern (_instance attribute)
       14. CONFIG   — Name/path contains config/settings/blueprint
       15. VALIDATOR — Name/path contains validator
       16. FACTORY  — Primary class name ends with 'Factory'
       17. TYPES   — TypedDict/Protocol/Enum/dataclass heavy files
       18. CLASS   — Fallback for files with classes
       19. UTILITY — Fallback for files without classes

    Args:
        path: Absolute or relative Path to a .py file.

    Returns:
        A FileType string literal.
    """
    # Resolve to absolute path for consistent cache keys
    try:
        resolved = path.resolve()
    except (OSError, ValueError):
        resolved = path
    try:
        return _classify_impl(resolved)
    # guardian: allow-silent-swallow
    except Exception as exc:
        logger.warning(
            "Kernel: unexpected error classifying %s: %s — returning IGNORE",
            path,
            exc,
        )
        return "IGNORE"


@lru_cache(maxsize=1024)
def _classify_impl(path: Path) -> FileType:
    """Cached implementation of classify_file_standalone."""
    # --- PRIORITY 0: CRITICAL IGNORES ---
    if path.name in _CRITICAL_IGNORES:
        return "IGNORE"

    # --- PRIORITY 1: BASE AGENT directory → CLASS ---
    if "base_agents" in path.parts:
        if "Mixin" in path.name or "mixin" in path.name.lower():
            pass  # let normal classification handle
        elif path.name.endswith(("_util.py", "_exceptions.py", "_types.py")):
            pass  # let normal classification handle
        else:
            return "CLASS"

    # --- Read file content ---
    try:
        if not path.exists() or path.stat().st_size == 0:
            return "IGNORE"
        content = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        logger.warning("Kernel: UnicodeDecodeError reading %s — returning IGNORE", path)
        return "IGNORE"
    except OSError as exc:
        logger.warning("Kernel: OSError reading %s: %s — returning IGNORE", path, exc)
        return "IGNORE"

    # --- PRIORITY 2: STUB detection ---
    if any(line.strip().startswith("NOT_AN_AGENT") for line in content.splitlines()):
        return "STUB"

    # --- Parse AST ---
    try:
        tree = ast.parse(content)
    except SyntaxError as exc:
        logger.warning(
            "Kernel: SyntaxError in %s (line %s) — returning IGNORE",
            path,
            getattr(exc, "lineno", "?"),
        )
        return "IGNORE"

    # --- PRIORITY 3: TEST detection ---
    if "tests" in path.parts or path.name.startswith("test_"):
        return "TEST"
    # Heuristic: file has TestCase inheritance or pytest fixtures
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            for base in node.bases:
                if isinstance(base, ast.Name) and base.id == "TestCase":
                    return "TEST"
                if isinstance(base, ast.Attribute) and base.attr == "TestCase":
                    return "TEST"

    # --- Collect class nodes ---
    class_nodes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]

    if not class_nodes:
        # PRIORITY 4/5: SCRIPT vs UTILITY (no classes)
        has_main_guard = any(
            isinstance(node, ast.If)
            and isinstance(node.test, ast.Compare)
            and any(
                isinstance(c, ast.Constant) and c.value == "__main__"
                for c in [node.test.left] + node.test.comparators
            )
            for node in ast.walk(tree)
        )
        func_count = sum(1 for node in ast.walk(tree) if isinstance(node, ast.FunctionDef))
        if has_main_guard or (func_count > 0 and ("scripts" in path.parts or "ops_scripts" in path.parts)):
            return "SCRIPT"
        return "UTILITY"

    # --- Determine primary class ---
    class_names = [node.name for node in class_nodes]
    primary_name = class_names[0]
    stem_clean = re.sub(r"[^a-zA-Z0-9]", "", path.stem.lower())
    for name in class_names:
        if re.sub(r"[^a-zA-Z0-9]", "", name.lower()) == stem_clean:
            primary_name = name
            break

    primary_node = next(n for n in class_nodes if n.name == primary_name)

    # --- Extract base class names ---
    def _base_names(node: ast.ClassDef) -> list[str]:
        names = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                names.append(base.id)
            elif isinstance(base, ast.Attribute):
                names.append(base.attr)
        return names

    bases = _base_names(primary_node)

    # --- Compute classification flags ---
    is_exception = primary_name.endswith(("Error", "Exception")) or any(
        b in ("Exception", "BaseException", "Error") for b in bases
    )
    is_mixin = primary_name.endswith("Mixin")
    is_protocol = any(b == "Protocol" for b in bases) or (
        path.name.startswith("I") and len(path.name) > 2 and path.name[1:2].isupper()
    )
    # Phase 3: Explicit router => ENGINE (must precede orchestrator check)
    is_router = path.stem.endswith("_router") or primary_name.endswith("Router")
    if is_router:
        return "ENGINE"

    is_orchestrator = any(p in primary_name for p in ("Orchestrator", "Coordinator", "Pipeline"))
    if not is_orchestrator:
        orchestrator_bases = {
            "Coordinator",
            "Orchestrator",
            "WorkflowCoordinator",
            "L3OrchestrationBase",
        }
        if orchestrator_bases & set(bases):
            is_orchestrator = True
    is_agent = primary_name.endswith("Agent")
    if not is_agent:
        for b in bases:
            if "Agent" in b:
                is_agent = True
                break
    is_strategy = primary_name.endswith("Strategy")
    is_enforcer = primary_name.endswith(("Enforcer", "Guard", "Guardrail")) or path.stem.endswith(
        (
            "_enforcer",
            "_guard",
            "_guardrail",
        )
    )
    is_seam = primary_name.endswith("Seam") or "seams" in path.parts
    is_adapter = any(primary_name.endswith(s) for s in ("Adapter", "Wrapper", "Bridge"))
    is_factory = primary_name.endswith("Factory")

    # --- DUAL-TAG CONFLICT DETECTION (governance hardening) ---
    top_tier_signals = []
    if is_agent:
        top_tier_signals.append("AGENT")
    if is_orchestrator:
        top_tier_signals.append("ORCHESTRATOR")
    if is_mixin:
        top_tier_signals.append("MIXIN")
    if is_protocol:
        top_tier_signals.append("PROTOCOL")
    if is_strategy:
        top_tier_signals.append("STRATEGY")

    if len(top_tier_signals) > 1:
        # Track dual-tag conflict for governance reporting
        _classification_conflicts.append(
            {
                "path": str(path),
                "conflict_type": "DUAL_TAG",
                "signals": top_tier_signals,
                "message": f"Multiple top-tier signals detected: {', '.join(top_tier_signals)}",
            }
        )

    # --- Priority execution ---
    # PRIORITY 6: EXCEPTION
    if is_exception:
        return "EXCEPTION"

    # PRIORITY 7: MIXIN
    if is_mixin:
        return "MIXIN"

    # PRIORITY 8: PROTOCOL
    if is_protocol:
        return "PROTOCOL"

    # PRIORITY 9: ORCHESTRATOR
    if is_orchestrator:
        return "ORCHESTRATOR"

    # PRIORITY 10: AGENT (strongest architectural signal)
    if is_agent:
        return "AGENT"

    # PRIORITY 11: STRATEGY
    if is_strategy:
        return "STRATEGY"

    # PRIORITY 11.5: ENFORCER (policy authority boundary)
    if is_enforcer:
        return "ENFORCER"

    # PRIORITY 11.6: SEAM (structural boundary primitive)
    if is_seam:
        return "SEAM"

    # PRIORITY 12: ADAPTER
    if is_adapter:
        return "ADAPTER"

    # PRIORITY 13: SERVICE (singleton pattern)
    for item in primary_node.body:
        if isinstance(item, ast.Assign):
            for target in item.targets:
                if isinstance(target, ast.Name) and target.id == "_instance":
                    return "SERVICE"
        if isinstance(item, ast.AnnAssign):
            if isinstance(item.target, ast.Name) and item.target.id == "_instance":
                return "SERVICE"

    # PRIORITY 14: CONFIG (with logic detection for governance hardening)
    config_keywords = {"config", "blueprint", "settings", "manifest"}
    if any(k in path.stem.lower() for k in config_keywords):
        # Check if CONFIG file contains executable methods (violation)
        has_executable_methods = False
        for node in class_nodes:
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    # Skip __init__, __post_init__, property getters, and dunder methods
                    if not (
                        item.name.startswith("__")
                        or item.name.startswith("_")
                        or any(isinstance(d, ast.Name) and d.id == "property" for d in item.decorator_list)
                    ):
                        has_executable_methods = True
                        break
            if has_executable_methods:
                break

        if has_executable_methods:
            # Track conflict for governance reporting
            _classification_conflicts.append(
                {
                    "path": str(path),
                    "conflict_type": "CONFIG_WITH_LOGIC",
                    "message": f"CONFIG file {path.name} contains executable methods",
                }
            )
            return "CONFIG_WITH_LOGIC"
        return "CONFIG"

    # PRIORITY 15: VALIDATOR
    if "validators" in path.parts or path.stem.lower().endswith("_validator"):
        return "VALIDATOR"

    # PRIORITY 16: FACTORY
    if is_factory:
        return "FACTORY"

    # PRIORITY 17: TYPES (dataclass/TypedDict/Enum-heavy files)
    type_keywords = {"TypedDict", "Protocol", "TypeAlias", "Enum", "Literal", "Final", "dataclass"}
    if "types" in path.parts or path.stem.lower().endswith("_types"):
        return "TYPES"
    if any(kw in content for kw in type_keywords):
        # Count type-related constructs vs other constructs
        type_hits = sum(1 for kw in type_keywords if kw in content)
        if type_hits >= 3:
            return "TYPES"

    # PRIORITY 18: CLASS (fallback for files with classes)
    return "CLASS"


# ============================================================================
# is_agent_file — Convenience predicate
# ============================================================================


def is_agent_file(path: Path) -> bool:
    """
    SSOT predicate: Is this file classified as AGENT?

    This is the ONE function all consumers should call to answer
    "is this an agent?" — replacing all bespoke _is_agent_class() methods.
    Inherits LRU cache from classify_file_standalone.

    Args:
        path: Path to a .py file.

    Returns:
        True if classify_file_standalone(path) == "AGENT".
    """
    return classify_file_standalone(path) == "AGENT"


# ============================================================================
# is_agent_or_orchestrator — Extended predicate for discovery manifests
# ============================================================================


def is_agent_or_orchestrator(path: Path) -> bool:
    """
    SSOT predicate: Is this file an AGENT or ORCHESTRATOR?

    Used by agent discovery scripts that treat orchestrators as a
    specialized form of agent for manifest purposes.
    Inherits LRU cache from classify_file_standalone.

    Args:
        path: Path to a .py file.

    Returns:
        True if classification is AGENT or ORCHESTRATOR.
    """
    return classify_file_standalone(path) in ("AGENT", "ORCHESTRATOR")


def clear_classification_cache() -> None:
    """Clear the LRU cache. Useful in tests or after file mutations."""
    _classify_impl.cache_clear()


def classification_cache_info():
    """Return cache statistics (hits, misses, maxsize, currsize)."""
    return _classify_impl.cache_info()


@contextmanager
def classification_cache_context():
    """Context manager that clears the cache on entry and exit.

    Useful for batch operations (Discovery, CI scans) where files won't
    change mid-operation, ensuring no stale state carries into the next
    operation.

    Usage::

        from agentic_core.L5_safety.core_kernel.classification_kernel import classification_cache_context

        with classification_cache_context():
            # Run heavy discovery / scan here
            ...
    """
    clear_classification_cache()
    try:
        yield
    finally:
        clear_classification_cache()
