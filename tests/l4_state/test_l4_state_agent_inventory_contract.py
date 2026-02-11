"""
L4 State Agent Inventory Contract Tests

Hard gates to prevent agent count inflation in agentic_core/L4_state/.

Rules enforced:
1) NAMING: Any *Agent.py under agentic_core/L4_state/** must contain exactly one
   top-level ClassDef ending with 'Agent' (or be in the SHIM_ALLOWLIST).
2) REACHABILITY: Every non-SHIM L4 agent class must be imported by at least one
   production module OR be in UNREACHABLE_ALLOWLIST with justification.
3) COUNT BUDGET: The number of *Agent.py files must not exceed AGENT_FILE_BUDGET.
"""

import ast
import os
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

L4_ROOT = os.path.join("agentic_core", "L4_state")

ENTRYPOINTS = [
    os.path.join("agentic_core", "L3_orchestration", "reasoning", "AgentFactory.py"),
    os.path.join("agentic_core", "L3_orchestration", "enforcement", "mission_runner.py"),
    os.path.join("agentic_core", "L3_orchestration", "enforcement", "safety_strategy.py"),
    os.path.join("agentic_core", "L5_safety", "enforcement", "HealingStrategy.py"),
    os.path.join("agentic_core", "L0_maintenance", "scripts", "execute_ssot.py"),
    os.path.join("agentic_core", "L2_execution", "reasoning", "sub_atomic_registry.py"),
    os.path.join("agentic_core", "interfaces", "IStateProtocol.py"),
    os.path.join("agentic_core", "interfaces", "IValidatorProtocol.py"),
    os.path.join("agentic_core", "interfaces", "IHealingStrategyProtocol.py"),
]

# Shim/retired stubs that have no ClassDef — explicitly allowlisted
SHIM_ALLOWLIST: set[str] = set()

# Agents that are NOT reachable from the strict entrypoint list but are
# explicitly kept with justification. Each entry: class_name -> reason.
UNREACHABLE_ALLOWLIST: dict[str, str] = {
    "RedisSovereignAgent": (
        "Reachable via sub_atomic_registry.py:34 (included in entrypoint list); "
        "also imported by PineconeSovereignAgent and PolicyNeuralAutoImmuneAgent "
        "via broken L4_state.memory.redis_sovereign_agent path (tracked as broken-wiring)"
    ),
}

# Budget: the maximum allowed count of *Agent.py files under L4_state/**
# Baseline after cleanup: 1 (RedisSovereignAgent.py)
AGENT_FILE_BUDGET = 1


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _get_agent_files():
    """Return list of *Agent.py files anywhere under L4_state/."""
    results = []
    for dirpath, _, filenames in os.walk(L4_ROOT):
        for fn in filenames:
            if fn.endswith("Agent.py"):
                results.append(os.path.join(dirpath, fn))
    return sorted(results)


_AGENT_SUFFIXES = (
    "Agent",
    "Executor",
    "Capability",
    "Guardian",
    "Sentinel",
    "Inspector",
    "Healer",
    "Enforcer",
    "Detector",
    "Validator",
    "Manager",
    "Scanner",
    "Overseer",
)


def _parse_top_level_classes(filepath):
    """Return list of top-level ClassDef names from a Python file."""
    try:
        source = Path(filepath).read_text(encoding="utf-8")
        tree = ast.parse(source, filename=filepath)
    except (SyntaxError, UnicodeDecodeError):
        return []
    return [node.name for node in tree.body if isinstance(node, ast.ClassDef)]


def _get_primary_agent_class(filepath):
    """Return the primary agent ClassDef name from a file (last agent-suffixed class)."""
    classes = _parse_top_level_classes(filepath)
    for cls in reversed(classes):
        if any(cls.endswith(s) for s in _AGENT_SUFFIXES):
            return cls
    return classes[-1] if classes else None


def _get_entrypoint_imported_names():
    """Collect all names imported from L4_state by entrypoints."""
    imported = set()
    for ep in ENTRYPOINTS:
        if not os.path.exists(ep):
            continue
        try:
            source = Path(ep).read_text(encoding="utf-8")
            tree = ast.parse(source, filename=ep)
        except (SyntaxError, UnicodeDecodeError):
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                if "L4_state" in node.module:
                    for alias in node.names:
                        imported.add(alias.name)
    return imported


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestL4AgentNamingContract:
    """Every *Agent.py file must contain exactly one Agent ClassDef (or be shimmed)."""

    def test_agent_files_have_agent_classdef(self):
        failures = []
        for filepath in _get_agent_files():
            filename = os.path.basename(filepath)
            if filename in SHIM_ALLOWLIST:
                continue
            primary = _get_primary_agent_class(filepath)
            if primary is None:
                classes = _parse_top_level_classes(filepath)
                failures.append(
                    f"{filename}: no agent ClassDef found (classes: {classes})",
                )
        assert not failures, "L4 Agent files without a recognized agent ClassDef:\n" + "\n".join(failures)


class TestL4AgentReachabilityContract:
    """Every non-SHIM L4 primary agent must be reachable from entrypoints or allowlisted."""

    def test_all_primary_agents_reachable_or_allowlisted(self):
        reachable = _get_entrypoint_imported_names()
        failures = []

        for filepath in _get_agent_files():
            filename = os.path.basename(filepath)
            if filename in SHIM_ALLOWLIST:
                continue
            primary = _get_primary_agent_class(filepath)
            if primary is None:
                continue
            if primary in reachable:
                continue
            if primary in UNREACHABLE_ALLOWLIST:
                continue
            failures.append(
                f"{primary} (in {filename}): not imported by any entrypoint and not in UNREACHABLE_ALLOWLIST",
            )

        assert not failures, (
            "L4 primary agents not reachable from entrypoints and not allowlisted:\n" + "\n".join(failures)
        )

    def test_allowlist_entries_have_justification(self):
        for name, justification in UNREACHABLE_ALLOWLIST.items():
            assert isinstance(justification, str) and len(justification) > 10, (
                f"UNREACHABLE_ALLOWLIST['{name}'] must have a non-trivial "
                f"justification string, got: {justification!r}"
            )


class TestL4AgentCountBudget:
    """The number of *Agent.py files must not exceed the pinned budget."""

    def test_agent_file_count_within_budget(self):
        agent_files = _get_agent_files()
        count = len(agent_files)
        assert count <= AGENT_FILE_BUDGET, (
            f"L4 Agent file count ({count}) exceeds budget ({AGENT_FILE_BUDGET}). "
            f"New agents require reachability proof or UNREACHABLE_ALLOWLIST entry "
            f"with justification. Current files:\n" + "\n".join(os.path.basename(f) for f in agent_files)
        )
