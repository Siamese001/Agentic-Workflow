"""Phase 5 — Artifact Emission Gate.

Enforces:
Within execute(), AST must contain at least one of:
   - self.emit_artifact(...)
   - Artifact(...)
   - self.publish(...)
   - known artifact helper call

Configurable list via ARTIFACT_CALL_NAMES / ARTIFACT_CLASS_NAMES.

AST-only. No runtime imports. §29 non-growing debt pattern.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from tests.contracts._scanner import (
    ARTIFACT_CALL_NAMES,
    ARTIFACT_CLASS_NAMES,
    ast_contains_call,
    ast_contains_name,
    check_exemption,
    collect_reasoning_agent_files,
    find_agent_class,
    find_method,
    get_top_level_classes,
    parse_file_ast,
    rel,
)


# ── Gate logic ─────────────────────────────────────────────────────────────────
def _check_artifact_emission(filepath: Path, tree: ast.Module) -> list[str]:
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
            issues.append("no_agent_class_for_artifact_check")
            return issues

    # Check execute method for artifact emission
    execute_method = find_method(agent_cls, "execute")
    if execute_method is None:
        issues.append("no_execute_method_for_artifact_check")
        return issues

    has_artifact = False

    # Check for artifact call patterns
    if ast_contains_call(execute_method, ARTIFACT_CALL_NAMES):
        has_artifact = True

    # Check for Artifact(...) constructor calls
    if not has_artifact and ast_contains_name(execute_method, ARTIFACT_CLASS_NAMES):
        has_artifact = True

    # Also check for return of dict with artifact-like keys
    # (common pattern: return {"artifacts": [...], ...})
    if not has_artifact:
        for child in ast.walk(execute_method):
            if isinstance(child, ast.Dict):
                for key in child.keys:
                    if (
                        isinstance(key, ast.Constant)
                        and isinstance(key.value, str)
                        and key.value in ("artifacts", "artifact", "results", "output")
                    ):
                        has_artifact = True
                        break
            if has_artifact:
                break

    if not has_artifact:
        issues.append("no_artifact_emission_in_execute")

    return issues


# ── Known pre-existing debt ────────────────────────────────────────────────────
KNOWN_DEBT: frozenset[str] = frozenset(
    {
        "agentic_core/L0_maintenance/reasoning/BenchmarkingAgent.py",
        "agentic_core/L0_maintenance/reasoning/BootstrapAgent.py",
        "agentic_core/L0_maintenance/reasoning/DocstringComplianceAgent.py",
        "agentic_core/L0_maintenance/reasoning/FilesystemSSOTReconcilerAgent.py",
        "agentic_core/L0_maintenance/reasoning/GospelSyncAgent.py",
        "agentic_core/L0_maintenance/reasoning/IntegrityGateExecutorAgent.py",
        "agentic_core/L0_maintenance/reasoning/RootCustomsAgent.py",
        "agentic_core/L0_maintenance/reasoning/SSOTFolderCleanupAgent.py",
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
def test_artifact_emission_no_new_violations():
    """No new artifact emission violations beyond known debt."""
    violations: dict[str, list[str]] = {}
    for f in collect_reasoning_agent_files():
        tree = parse_file_ast(f)
        if tree is None:
            continue
        exempt, _ = check_exemption(tree)
        if exempt:
            continue
        issues = _check_artifact_emission(f, tree)
        if issues:
            violations[rel(f)] = issues

    new_violations = set(violations.keys()) - KNOWN_DEBT
    if new_violations:
        details = "\n".join(f"  {k}: {violations[k]}" for k in sorted(new_violations))
        pytest.fail(f"New artifact emission violations:\n{details}")


def test_artifact_emission_debt_ceiling():
    """Debt count must not exceed known ceiling (§29, §32)."""
    count = 0
    for f in collect_reasoning_agent_files():
        tree = parse_file_ast(f)
        if tree is None:
            continue
        exempt, _ = check_exemption(tree)
        if exempt:
            continue
        if _check_artifact_emission(f, tree):
            count += 1
    ceiling = len(KNOWN_DEBT)
    assert count <= ceiling, f"Artifact emission debt grew: actual={count}, ceiling={ceiling}"
