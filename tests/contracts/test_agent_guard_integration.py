"""Phase 4 — Guard + Policy Participation Gate.

Enforces:
1. execute method must include at least one approved guard decorator:
   - runtime_guard
   - _optional_runtime_guard
2. OR class-level decorator equivalent.
3. execute body must reference policy_config or call into base policy method.

AST-only. No runtime imports. §29 non-growing debt pattern.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from tests.contracts._scanner import (
    APPROVED_GUARD_DECORATORS,
    ast_contains_call,
    ast_contains_name,
    check_exemption,
    collect_reasoning_agent_files,
    find_agent_class,
    find_method,
    get_decorator_names,
    get_top_level_classes,
    parse_file_ast,
    rel,
)

POLICY_NAMES = frozenset({"policy_config"})


# ── Gate logic ─────────────────────────────────────────────────────────────────
def _check_guard_integration(filepath: Path, tree: ast.Module) -> list[str]:
    """Return list of violation descriptions. Empty list = pass."""
    issues: list[str] = []
    stem = filepath.stem

    # Find agent class
    agent_cls = find_agent_class(tree, stem)
    if agent_cls is None:
        all_classes = get_top_level_classes(tree)
        agent_classes = [c for c in all_classes if c.name.endswith("Agent") and not c.name.startswith("_")]
        if len(agent_classes) == 1:
            agent_cls = agent_classes[0]
        else:
            issues.append("no_agent_class_for_guard_check")
            return issues

    # 1. Check execute method for guard decorator
    execute_method = find_method(agent_cls, "execute")
    has_guard = False

    if execute_method is not None:
        exec_decorators = get_decorator_names(execute_method)
        if any(d in APPROVED_GUARD_DECORATORS for d in exec_decorators):
            has_guard = True

    # 2. Check class-level decorators
    if not has_guard:
        class_decorators = get_decorator_names(agent_cls)
        if any(d in APPROVED_GUARD_DECORATORS for d in class_decorators):
            has_guard = True

    if not has_guard:
        issues.append("missing_guard_decorator")

    # 3. Policy participation: execute body references policy_config
    has_policy = False
    if execute_method is not None:
        if ast_contains_name(execute_method, POLICY_NAMES):
            has_policy = True
        # Check kwargs.get("policy_config") pattern
        if ast_contains_call(execute_method, frozenset({"get"})):
            for child in ast.walk(execute_method):
                if isinstance(child, ast.Call):
                    for arg in child.args:
                        if (
                            isinstance(arg, ast.Constant)
                            and isinstance(arg.value, str)
                            and "policy_config" in arg.value
                        ):
                            has_policy = True
                            break
        # Check if it calls super().execute() which handles policy
        for child in ast.walk(execute_method):
            if isinstance(child, ast.Call):
                func = child.func
                if isinstance(func, ast.Attribute) and func.attr == "execute":
                    if isinstance(func.value, ast.Call):
                        if isinstance(func.value.func, ast.Name) and func.value.func.id == "super":
                            has_policy = True

    if not has_policy and not has_guard:
        issues.append("missing_policy_participation")

    return issues


# ── Known pre-existing debt ────────────────────────────────────────────────────
KNOWN_DEBT: frozenset[str] = frozenset(
    {
        "agentic_core/L5_safety/reasoning/BenchmarkingAgent.py",
        "agentic_core/L5_safety/reasoning/BootstrapAgent.py",
        "agentic_core/L5_safety/reasoning/DocstringComplianceAgent.py",
        "agentic_core/L5_safety/reasoning/FilesystemSSOTReconcilerAgent.py",
        "agentic_core/L5_safety/reasoning/GospelSyncAgent.py",
        "agentic_core/L5_safety/reasoning/IntegrityGateExecutorAgent.py",
        "agentic_core/L0_routing/reasoning/RootCustomsAgent.py",
        "agentic_core/L0_routing/reasoning/SSOTFolderCleanupAgent.py",
        "agentic_core/L1_cognition/reasoning/ASTValidatorAgent.py",
        "agentic_core/L1_cognition/reasoning/MetaLearningAgent.py",
        "agentic_core/L1_cognition/reasoning/StrategicRecommendationAgent.py",
        "agentic_core/L2_execution/reasoning/EmbeddingSovereignAgent.py",
        "agentic_core/L2_execution/reasoning/SovereignMCPGatewayAgent.py",
        "agentic_core/L2_execution/reasoning/StructuredEngineAgent.py",
        "agentic_core/L2_execution/reasoning/SubAtomicRegistryAgent.py",
        "agentic_core/L2_execution/reasoning/ToolsmithAgent.py",
        "agentic_core/L3_orchestration/reasoning/CoverageAgent.py",
        "agentic_core/L3_orchestration/reasoning/DAGMutatorAgent.py",
        "agentic_core/L3_orchestration/reasoning/DagEngineAgent.py",
        "agentic_core/L3_orchestration/reasoning/DomainPlannerAgent.py",
        "agentic_core/L3_orchestration/reasoning/FissionManagerAgent.py",
        "agentic_core/L3_orchestration/reasoning/NervousSystemAgent.py",
        "agentic_core/L3_orchestration/reasoning/OrchestrationHandshakeAgent.py",
        "agentic_core/L3_orchestration/reasoning/SemanticGatekeeperAgent.py",
        "agentic_core/L3_orchestration/reasoning/StateManagementAgent.py",
        "agentic_core/L3_orchestration/reasoning/SubAtomicAgent.py",
        "agentic_core/L3_orchestration/reasoning/SubatomicHopAgent.py",
        "agentic_core/L3_orchestration/reasoning/UnifiedAgent.py",
        "agentic_core/L4_state/reasoning/CachedStateLedgerAgent.py",
        "agentic_core/L4_state/reasoning/CheckpointManagerAgent.py",
        "agentic_core/L4_state/reasoning/GravityStateAgent.py",
        "agentic_core/L4_state/reasoning/PineconeSovereignAgent.py",
        "agentic_core/L4_state/reasoning/RedisSovereignAgent.py",
        "agentic_core/L5_safety/reasoning/AdversarialProbeAgent.py",
        "agentic_core/L5_safety/reasoning/AdversarialRedTeamerAgent.py",
        "agentic_core/L5_safety/reasoning/ArchitectureGovernorAgent.py",
        "agentic_core/L5_safety/reasoning/AutonomousThreatEvolutionAgent.py",
        "agentic_core/L5_safety/reasoning/AutonomyGuardianAgent.py",
        "agentic_core/L5_safety/reasoning/BoundaryTestingAgent.py",
        "agentic_core/L5_safety/reasoning/ChaosEngineeringAgent.py",
        "agentic_core/L5_safety/reasoning/CodeDeduplicationAgent.py",
        "agentic_core/L5_safety/reasoning/CodeDetectorAgent.py",
        "agentic_core/L5_safety/reasoning/CodeEnforcerAgent.py",
        "agentic_core/L5_safety/reasoning/CodeFormatterAgent.py",
        "agentic_core/L5_safety/reasoning/CodeHealerAgent.py",
        "agentic_core/L5_safety/reasoning/CodeValidatorAgent.py",
        "agentic_core/L5_safety/reasoning/CognitiveDispositionAgent.py",
        "agentic_core/L5_safety/reasoning/ComplexityAnalyzerAgent.py",
        "agentic_core/L5_safety/reasoning/ConstitutionalReviewerAgent.py",
        "agentic_core/L5_safety/reasoning/CostGovernorAgent.py",
        "agentic_core/L5_safety/reasoning/CredentialScannerAgent.py",
        "agentic_core/L5_safety/reasoning/DDDAlignmentAgent.py",
        "agentic_core/L5_safety/reasoning/DependencyPruningAgent.py",
        "agentic_core/L5_safety/reasoning/DocumentationAgent.py",
        "agentic_core/L5_safety/reasoning/DuplicateCodeDetectorAgent.py",
        "agentic_core/L5_safety/reasoning/DynamicSealAgent.py",
        "agentic_core/L5_safety/reasoning/FileClassificationAgent.py",
        "agentic_core/L5_safety/reasoning/GenerativeGuardAgent.py",
        "agentic_core/L5_safety/reasoning/GitHygieneAgent.py",
        "agentic_core/L5_safety/reasoning/GovernanceAgent.py",
        "agentic_core/L5_safety/reasoning/GravityLeakRepairAgent.py",
        "agentic_core/L5_safety/reasoning/HierarchyAgent.py",
        "agentic_core/L5_safety/reasoning/HygieneGuardianAgent.py",
        "agentic_core/L5_safety/reasoning/InterfaceBoundaryAgent.py",
        "agentic_core/L5_safety/reasoning/L5SafetyExerciserAgent.py",
        "agentic_core/L5_safety/reasoning/LocationAgent.py",
        "agentic_core/L5_safety/reasoning/LocationHealerAgent.py",
        "agentic_core/L5_safety/reasoning/LocationValidatorAgent.py",
        "agentic_core/L5_safety/reasoning/NamingAgent.py",
        "agentic_core/L5_safety/reasoning/NeuralAutoImmuneAgent.py",
        "agentic_core/L5_safety/reasoning/PolicyNeuralAutoImmuneAgent.py",
        "agentic_core/L5_safety/reasoning/PreCommitSovereignAgent.py",
        "agentic_core/L5_safety/reasoning/PredictiveCostAuditorAgent.py",
        "agentic_core/L5_safety/reasoning/RedSentinelAgent.py",
        "agentic_core/L5_safety/reasoning/RedTeamAgent.py",
        "agentic_core/L5_safety/reasoning/RegressionOracleAgent.py",
        "agentic_core/L5_safety/reasoning/ReportLocationAgent.py",
        "agentic_core/L5_safety/reasoning/ResourceManagerAgent.py",
        "agentic_core/L5_safety/reasoning/RootHygieneAgent.py",
        "agentic_core/L5_safety/reasoning/SafetyDetectorAgent.py",
        "agentic_core/L5_safety/reasoning/SafetyExecutorAgent.py",
        "agentic_core/L5_safety/reasoning/SafetyInspectorAgent.py",
        "agentic_core/L5_safety/reasoning/SecurityManagerAgent.py",
        "agentic_core/L5_safety/reasoning/SelfUpdatingSafetyEngineAgent.py",
        "agentic_core/L5_safety/reasoning/SovereignActionPlaneAgent.py",
        "agentic_core/L5_safety/reasoning/SprawlInspectorAgent.py",
        "agentic_core/L5_safety/reasoning/StructuralEngineerAgent.py",
        "agentic_core/L5_safety/reasoning/StructuralValidatorAgent.py",
        "agentic_core/L5_safety/reasoning/StructureEnforcerAgent.py",
        "agentic_core/L5_safety/reasoning/StructureHealerAgent.py",
        "agentic_core/L5_safety/reasoning/SystemArchitectAgent.py",
        "agentic_core/L5_safety/reasoning/TerritoryChangeHandlerAgent.py",
        "agentic_core/L5_safety/reasoning/TestGeneratorAgent.py",
        "agentic_core/L5_safety/reasoning/TypeHintFixerAgent.py",
        "agentic_core/L5_safety/reasoning/TypeMechanicAgent.py",
        "agentic_core/L5_safety/reasoning/UnusedCleanupAgent.py",
        "agentic_core/knowledge/reasoning/SovereignRAGManagerAgent.py",
    },
)


# ── Tests ──────────────────────────────────────────────────────────────────────
def test_guard_integration_no_new_violations():
    """No new guard/policy violations beyond known debt."""
    violations: dict[str, list[str]] = {}
    for f in collect_reasoning_agent_files():
        tree = parse_file_ast(f)
        if tree is None:
            continue
        exempt, _ = check_exemption(tree)
        if exempt:
            continue
        issues = _check_guard_integration(f, tree)
        if issues:
            violations[rel(f)] = issues

    new_violations = set(violations.keys()) - KNOWN_DEBT
    if new_violations:
        details = "\n".join(f"  {k}: {violations[k]}" for k in sorted(new_violations))
        pytest.fail(f"New guard/policy violations:\n{details}")


def test_guard_integration_debt_ceiling():
    """Debt count must not exceed known ceiling (§29, §32)."""
    count = 0
    for f in collect_reasoning_agent_files():
        tree = parse_file_ast(f)
        if tree is None:
            continue
        exempt, _ = check_exemption(tree)
        if exempt:
            continue
        if _check_guard_integration(f, tree):
            count += 1
    ceiling = len(KNOWN_DEBT)
    assert count <= ceiling, f"Guard/policy debt grew: actual={count}, ceiling={ceiling}"
