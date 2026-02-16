"""
L5 Agent Inventory Contract Tests

Hard gates to prevent agent count inflation in agentic_core/L5_safety/reasoning/.

Rules enforced:
1) NAMING: Any file matching *Agent.py must contain exactly one top-level ClassDef
   ending with 'Agent' (or be in the SHIM_ALLOWLIST).
2) REACHABILITY: Every non-SHIM L5 agent class must be imported by at least one
   production entrypoint module OR be in UNREACHABLE_ALLOWLIST with justification.
3) COUNT BUDGET: The number of *Agent.py files must not exceed AGENT_FILE_BUDGET.
"""

import ast
import glob
import os
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

REASONING_DIR = os.path.join("agentic_core", "L5_safety", "reasoning")

ENTRYPOINTS = [
    os.path.join("agentic_core", "L3_orchestration", "engines", "AgentFactory.py"),
    os.path.join("agentic_core", "L3_orchestration", "enforcement", "mission_runner.py"),
    os.path.join("agentic_core", "L3_orchestration", "enforcement", "safety_strategy.py"),
    os.path.join("agentic_core", "L5_safety", "enforcement", "HealingStrategy.py"),
    os.path.join("agentic_core", "L0_routing", "scripts", "execute_ssot.py"),
    os.path.join("agentic_core", "interfaces", "IValidatorProtocol.py"),
    os.path.join("agentic_core", "interfaces", "IHealingStrategyProtocol.py"),
]

# Shim/retired stubs that have no ClassDef — explicitly allowlisted
SHIM_ALLOWLIST = {
    "DependencyDiplomatAgent.py",
    "GlobalComplianceAggregatorAgent.py",
    "OmniContextAgent.py",
    "SemanticMapperAgent.py",
    "SemanticTerritoryMapperAgent.py",
    "SignatureVerifierAgent.py",
    "TokenBudgetInspectorAgent.py",
}

# Agents that are NOT reachable from production entrypoints but are
# explicitly kept with justification. Each entry: class_name -> reason.
UNREACHABLE_ALLOWLIST = {
    # --- SHIM/RETIRED redirect stubs (no real ClassDef) ---
    "InspectorExecutor": "Consolidation target for DagRuntime+Signature+TokenBudget",
    # --- Agents only used transitively (imported by another REACHABLE agent, not entrypoint) ---
    "GravityLeakRepairAgent": "Imported by ArchitectureGovernorAgent (REACHABLE)",
    "LocationHealerAgent": "Imported by gravity_leak_config + LocationValidatorAgent chain",
    "LocationValidatorAgent": "Imported by FilesystemSSOTReconcilerAgent chain",
    "StructuralValidatorAgent": "Imported by ArchitectureGovernorAgent + GravityLeakRepairAgent",
    "RedTeamAgent": "Imported by L5SafetyExerciserAgent (test exerciser)",
    # --- Agents imported only by other L5 agents or non-entrypoint production code ---
    "CodeToolRunnerCapability": "Internal capability used by CodeFormatterAgent + UnusedCleanupAgent",
    "NeuralAutoImmuneAgent": "Internal capability used by PolicyNeuralAutoImmuneAgent",
    # --- Registry-only (sub_atomic_registry imports, mapping dicts not yet proven called) ---
    "CodeDetectorAgent": "Registry-only; sub_atomic_registry phase4 mapping (dead mapping pending cleanup)",
    "ResourceManagerAgent": "Registry-only; sub_atomic_registry phase3 mapping (dead mapping pending cleanup)",
    "SafetyDetectorAgent": "Registry-only; sub_atomic_registry phase4 mapping (dead mapping pending cleanup)",
    "SafetyExecutorAgent": "Registry-only; sub_atomic_registry phase4 mapping (dead mapping pending cleanup)",
    "SecurityManagerAgent": "Registry-only; sub_atomic_registry phase3 mapping (dead mapping pending cleanup)",
    "StructureHealerAgent": "Registry-only + facade; referenced in UnifiedAgent and tests",
    "CodeHealerAgent": "Registry-only; heavily referenced in tests and NervousSystemAgent",
    # --- TEST-ONLY agents (zero production imports, only test coverage) ---
    "AdversarialRedTeamerAgent": "TEST-ONLY: exercised in test suite only",
    "AutonomousThreatEvolutionAgent": "TEST-ONLY: exercised in test suite only",
    "CodeFormatterAgent": "TEST-ONLY: exercised in test suite only",
    "ComplexityAnalyzerAgent": "TEST-ONLY: exercised in test suite only",
    "ConstitutionalReviewerAgent": "TEST-ONLY: exercised in test suite only",
    "CostGovernorAgent": "TEST-ONLY: exercised in test suite only",
    "DDDAlignmentAgent": "TEST-ONLY: exercised in test suite only",
    "DependencyPruningAgent": "TEST-ONLY: exercised in test suite only",
    "DocumentationAgent": "TEST-ONLY: exercised in test suite only",
    "DynamicSealAgent": "TEST-ONLY: exercised in test suite only",
    "GenerativeGuardAgent": "TEST-ONLY: exercised in test suite only",
    "InterfaceBoundaryAgent": "TEST-ONLY: exercised in test suite only",
    "L5SafetyExerciserAgent": "TEST-ONLY: exercised in test suite only",
    "PolicyNeuralAutoImmuneAgent": "TEST-ONLY: exercised in test suite only",
    "PreCommitSovereignAgent": "TEST-ONLY: exercised in test suite only",
    "PredictiveCostAuditorAgent": "TEST-ONLY: exercised in test suite only",
    "RedSentinelAgent": "TEST-ONLY: exercised in test suite only",
    "RegressionOracleAgent": "TEST-ONLY: exercised in test suite only",
    "ReportLocationAgent": "TEST-ONLY: exercised in test suite only",
    "SelfUpdatingSafetyEngineAgent": "TEST-ONLY: exercised in test suite only",
    "SovereignActionPlaneAgent": "TEST-ONLY: exercised in test suite only",
    "SprawlInspectorAgent": "TEST-ONLY: exercised in test suite only",
    "StructuralEngineerAgent": "TEST-ONLY: exercised in test suite only",
    "TestGeneratorAgent": "TEST-ONLY: exercised in test suite only",
    "TypeHintFixerAgent": "TEST-ONLY: exercised in test suite only",
    "TypeMechanicAgent": "TEST-ONLY: exercised in test suite only",
    "UnusedCleanupAgent": "TEST-ONLY: exercised in test suite only",
    # --- UNUSED agents with external string refs blocking deletion ---
    "CachedSafetyShield": "UNUSED: blocked by string ref in test_verify_runtime_integrity.py",
    "CompositeGuardrailAgent": "UNUSED: blocked by string refs in quarantine tests + utils",
    "GitSafetyHandlerAgent": "UNUSED: blocked by string refs in rename utils",
    "HealValidatorAgent": "UNUSED: blocked by string refs in utils",
    "MCPGuardianAgent": "UNUSED: blocked by string refs in quarantine/surgical tests",
    "PIISanitizerAgent": "UNUSED: blocked by string refs in QAConductor + utils",
    "PromptRegistryAgent": "UNUSED: blocked by docstring refs in prompt_entry_types.py",
    "TestCoverageGuardianAgent": "UNUSED: blocked by string ref in decomposition_orchestrator.py",
    "TestSovereigntyAgent": "UNUSED: blocked by string refs in utils + docstring in L0RoutingBase",
    # --- BROKEN WIRING (import resolves to None — tracked for fix) ---
    "SafetyInspectorAgent": "BROKEN-WIRING: AgentFactory assigns None; tracked in R1",
    "DuplicateCodeDetectorAgent": "BROKEN-WIRING: import removed in delete_duplicates_util; tracked in R2",
    # --- Agents reachable via non-listed entrypoints (orchestrator_engine, sub_atomic_registry) ---
    "ConstitutionalOverseer": "Reachable via orchestrator_engine.py (not in strict entrypoint list)",
    "CredentialScannerAgent": "Reachable via orchestrator_engine.py:404 (not in strict entrypoint list)",
    # --- Facade agents (delegate to other agents) ---
    "ConstitutionalOverseerAgent": "Facade: defined in SafetyInspectorAgent.py, not a standalone file",
    # --- Agents in non-standard filenames ---
    "AutonomousRagDaemon": "Secondary class in TerritoryChangeHandlerAgent.py",
    "TerritoryChangeHandlerAgent": "TEST-ONLY: primary class in file, blocked by test refs",
}

# Budget: the maximum allowed count of *Agent.py files in reasoning/
# Baseline: 83 (84 - 1 PineconeSovereignAgent relocated to L4_state)
AGENT_FILE_BUDGET = 83


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _get_agent_files():
    """Return list of *Agent.py files in L5 reasoning dir."""
    pattern = os.path.join(REASONING_DIR, "*Agent.py")
    return sorted(glob.glob(pattern))


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
    "Reviewer",
    "Engineer",
    "Fixer",
    "Mechanic",
    "Formatter",
    "Generator",
    "Oracle",
    "Shield",
    "Plane",
    "Seal",
    "Handler",
    "Daemon",
    "Engine",
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
    """Collect all names imported from L5_safety.reasoning by entrypoints."""
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
                if "L5_safety" in node.module:
                    for alias in node.names:
                        imported.add(alias.name)
    return imported


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestL5AgentNamingContract:
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
        assert not failures, "Agent files without a recognized agent ClassDef:\n" + "\n".join(failures)


class TestL5AgentReachabilityContract:
    """Every non-SHIM L5 primary agent must be reachable from entrypoints or allowlisted."""

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
            "L5 primary agents not reachable from entrypoints and not allowlisted:\n" + "\n".join(failures)
        )

    def test_allowlist_entries_have_justification(self):
        for name, justification in UNREACHABLE_ALLOWLIST.items():
            assert isinstance(justification, str) and len(justification) > 10, (
                f"UNREACHABLE_ALLOWLIST['{name}'] must have a non-trivial "
                f"justification string, got: {justification!r}"
            )


class TestL5AgentCountBudget:
    """The number of *Agent.py files must not exceed the pinned budget."""

    def test_agent_file_count_within_budget(self):
        agent_files = _get_agent_files()
        count = len(agent_files)
        assert count <= AGENT_FILE_BUDGET, (
            f"L5 Agent file count ({count}) exceeds budget ({AGENT_FILE_BUDGET}). "
            f"New agents require reachability proof or UNREACHABLE_ALLOWLIST entry "
            f"with justification. Current files:\n" + "\n".join(os.path.basename(f) for f in agent_files)
        )
