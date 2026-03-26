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


L4_ROOT = os.path.join(AGENTIC_CORE_DIR, L4_STATE_DIR)


ENTRYPOINTS = [
    os.path.join(AGENTIC_CORE_DIR, L3_ORCHESTRATION_DIR, "engines", "AgentFactory.py"),
    os.path.join(AGENTIC_CORE_DIR, L3_ORCHESTRATION_DIR, "enforcement", "mission_runner.py"),
    os.path.join(AGENTIC_CORE_DIR, L3_ORCHESTRATION_DIR, "enforcement", "safety_strategy.py"),
    os.path.join(AGENTIC_CORE_DIR, "L5_safety", "enforcement", "HealingStrategy.py"),
    os.path.join(AGENTIC_CORE_DIR, L0_ROUTING_DIR, "scripts", "execute_ssot.py"),
    os.path.join(AGENTIC_CORE_DIR, L2_EXECUTION_DIR, "reasoning", "SubAtomicRegistryAgent.py"),
    os.path.join(AGENTIC_CORE_DIR, "interfaces", "IStateProtocol.py"),
    os.path.join(AGENTIC_CORE_DIR, "interfaces", "IValidatorProtocol.py"),
    os.path.join(AGENTIC_CORE_DIR, "interfaces", "IHealingStrategyProtocol.py"),
]


# Files with multiple ClassDefs (agent + helper dataclasses) — explicitly allowlisted

# from the exactly-one-ClassDef check but still validated for agent suffix.

SHIM_ALLOWLIST: set[str] = {
    "CheckpointManagerAgent.py",  # 3 ClassDefs: Checkpoint, RecoveryResult, CheckpointManagerAgent
}


# Agents that are NOT reachable from the strict entrypoint list but are

# explicitly kept with justification. Each entry: class_name -> reason.

UNREACHABLE_ALLOWLIST: dict[str, str] = {
    "RedisSovereignAgent": (
        "Reachable via SubAtomicRegistryAgent.py (included in entrypoint list); "
        "also imported by PolicyNeuralAutoImmuneAgent "
        "via L4_state.reasoning.RedisSovereignAgent (wiring fixed in Phase 5)"
    ),
    "CachedStateLedgerAgent": (
        "Renamed from cached_state_ledger.py per PascalCase+Agent naming convention. "
        "Used by SubAtomicRegistryAgent and test fixtures for state ledger caching."
    ),
    "CheckpointManagerAgent": (
        "Renamed from checkpoint_manager.py per PascalCase+Agent naming convention. "
        "Used by SubAtomicRegistryAgent, autonomous_execution_engine, and 15+ files."
    ),
}


# Budget: the maximum allowed count of *Agent.py files under L4_state/**

# Baseline: 3 (Redis + CachedStateLedger + CheckpointManager; Pinecone removed Wave 1)

AGENT_FILE_BUDGET = 3


# ---------------------------------------------------------------------------

# Helpers

# ---------------------------------------------------------------------------


def _get_agent_files():
    """Return list of *Agent.py files anywhere under L4_state/."""

    results = []

    for dirpath, dirs, filenames in os.walk(L4_ROOT):
        dirs[:] = [d for d in dirs if d not in SOVEREIGN_EXCLUDED_FOLDERS]
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
                if L4_STATE_DIR in node.module:
                    for alias in node.names:
                        imported.add(alias.name)

    return imported


# ---------------------------------------------------------------------------

# Tests

# ---------------------------------------------------------------------------


class TestL4AgentNamingContract:
    """Every *Agent.py file must contain exactly one top-level ClassDef ending with Agent."""

    def test_agent_files_have_exactly_one_classdef(self):
    """Test agent_files_have_exactly_one_classdef contract compliance."""
        from agentic_core.L0_routing.config.path_constants import (
            AGENTIC_CORE_DIR,
            L0_ROUTING_DIR,
            L2_EXECUTION_DIR,
            L3_ORCHESTRATION_DIR,
            L4_STATE_DIR,
        )
        from agentic_core.L5_safety.config.structure_blueprint.ssot import SOVEREIGN_EXCLUDED_FOLDERS

    # Arrange
    # TODO: Set up contract parties and terms
    contract_terms = {}  # Replace with actual contract terms

    # Act
    # TODO: Execute contract operations
    contract_result = None  # Replace with actual contract operation

    # Assert - Core Contract
    assert contract_result is not None, "Contract operation should produce a result"
    assert isinstance(contract_result, dict), "Contract result should be structured"
    # TODO: Add specific contract assertions
    # assert contract_result.get("enforced", False), "Contract terms should be enforced"

            elif len(classes) > 1:
                failures.append(
                    f"{filename}: {len(classes)} ClassDefs ({', '.join(classes)}); expected exactly 1",
                )

        assert not failures, "L4 Agent files violating exactly-one-ClassDef rule:\n" + "\n".join(failures)

    def test_agent_files_have_agent_classdef(self):
    """Test agent_files_have_agent_classdef contract compliance."""
    # Arrange
    # TODO: Set up contract parties and terms
    contract_terms = {}  # Replace with actual contract terms

    # Act
    # TODO: Execute contract operations
    contract_result = None  # Replace with actual contract operation

    # Assert - Core Contract
    assert contract_result is not None, "Contract operation should produce a result"
    assert isinstance(contract_result, dict), "Contract result should be structured"
    # TODO: Add specific contract assertions
    # assert contract_result.get("enforced", False), "Contract terms should be enforced"

                failures.append(
                    f"{filename}: no agent ClassDef found (classes: {classes})",
                )

        assert not failures, "L4 Agent files without a recognized agent ClassDef:\n" + "\n".join(failures)


class TestL4AgentReachabilityContract:
    """Every non-SHIM L4 primary agent must be reachable from entrypoints or allowlisted."""

    def test_all_primary_agents_reachable_or_allowlisted(self):
    """Test all_primary_agents_reachable_or_allowlisted contract compliance."""
    # Arrange
    # TODO: Set up contract parties and terms
    contract_terms = {}  # Replace with actual contract terms

    # Act
    # TODO: Execute contract operations
    contract_result = None  # Replace with actual contract operation

    # Assert - Core Contract
    assert contract_result is not None, "Contract operation should produce a result"
    assert isinstance(contract_result, dict), "Contract result should be structured"
    # TODO: Add specific contract assertions
    # assert contract_result.get("enforced", False), "Contract terms should be enforced"

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
    """Test allowlist_entries_have_justification contract compliance."""
    # Arrange
    # TODO: Set up contract parties and terms
    contract_terms = {}  # Replace with actual contract terms

    # Act
    # TODO: Execute contract operations
    contract_result = None  # Replace with actual contract operation

    # Assert - Core Contract
    assert contract_result is not None, "Contract operation should produce a result"
    """Test agent_file_count_within_budget contract compliance."""
    # Arrange
    # TODO: Set up contract parties and terms
    contract_terms = {}  # Replace with actual contract terms

    # Act
    # TODO: Execute contract operations
    contract_result = None  # Replace with actual contract operation

    # Assert - Core Contract
    assert contract_result is not None, "Contract operation should produce a result"
    assert isinstance(contract_result, dict), "Contract result should be structured"
    # TODO: Add specific contract assertions
    # assert contract_result.get("enforced", False), "Contract terms should be enforced"
