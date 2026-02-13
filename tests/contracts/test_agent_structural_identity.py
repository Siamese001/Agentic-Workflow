"""Phase 1 — Structural Identity Gate.

Enforces:
1. Filename regex: ^[A-Z][A-Za-z0-9]*Agent\\.py$
2. Exactly one public Agent class matching filename stem.
3. No additional public top-level classes (underscore-prefixed helpers allowed).
4. No Agent aliasing (FooAgent = BarAgent).

AST-only. No runtime imports. §29 non-growing debt pattern.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from tests.contracts._scanner import (
    AGENT_FILENAME_RE,
    collect_reasoning_agent_files,
    get_top_level_classes,
    parse_file_ast,
    rel,
)


# ── Gate logic ─────────────────────────────────────────────────────────────────
def _check_structural_identity(filepath: Path, tree: ast.Module) -> list[str]:
    """Return list of violation descriptions. Empty list = pass."""
    issues: list[str] = []
    stem = filepath.stem

    # 1. Filename regex
    if not AGENT_FILENAME_RE.match(filepath.name):
        issues.append(f"filename_regex_fail: {filepath.name}")

    # 2. Top-level public classes
    all_classes = get_top_level_classes(tree)
    public_classes = [c for c in all_classes if not c.name.startswith("_")]
    agent_classes = [c for c in public_classes if c.name.endswith("Agent")]

    if len(agent_classes) == 0:
        issues.append("no_agent_class_found")
    elif len(agent_classes) > 1:
        names = [c.name for c in agent_classes]
        issues.append(f"multiple_agent_classes: {names}")
    else:
        if agent_classes[0].name != stem:
            issues.append(
                f"name_mismatch: class={agent_classes[0].name} file={stem}",
            )

    # 3. Extra public non-Agent top-level classes
    non_agent_public = [c for c in public_classes if not c.name.endswith("Agent")]
    if non_agent_public:
        names = [c.name for c in non_agent_public]
        issues.append(f"extra_public_classes: {names}")

    # 4. Agent aliasing: FooAgent = BarAgent
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id.endswith("Agent"):
                    if isinstance(node.value, ast.Name):
                        issues.append(f"alias: {target.id}={node.value.id}")

    return issues


# ── Known pre-existing debt ────────────────────────────────────────────────────
# Populated via discovery run. Files listed here have known structural
# identity violations that pre-date this contract.
# Adding new files here is forbidden (§29 non-growing debt).
KNOWN_DEBT: frozenset[str] = frozenset(
    {
        "agentic_core/L5_safety/reasoning/BenchmarkingAgent.py",
        "agentic_core/L5_safety/reasoning/FilesystemSSOTReconcilerAgent.py",
        "agentic_core/L5_safety/reasoning/IntegrityGateExecutorAgent.py",
        "agentic_core/L0_routing/reasoning/RootCustomsAgent.py",
        "agentic_core/L1_cognition/reasoning/ASTValidatorAgent.py",
        "agentic_core/L1_cognition/reasoning/MetaLearningAgent.py",
        "agentic_core/L2_execution/reasoning/SovereignMCPGatewayAgent.py",
        "agentic_core/L2_execution/reasoning/StructuredEngineAgent.py",
        "agentic_core/L2_execution/reasoning/ToolsmithAgent.py",
        "agentic_core/L3_orchestration/reasoning/DAGMutatorAgent.py",
        "agentic_core/L3_orchestration/reasoning/DagEngineAgent.py",
        "agentic_core/L3_orchestration/reasoning/DomainPlannerAgent.py",
        "agentic_core/L3_orchestration/reasoning/FissionManagerAgent.py",
        "agentic_core/L3_orchestration/reasoning/StateManagementAgent.py",
        "agentic_core/L3_orchestration/reasoning/SubAtomicAgent.py",
        "agentic_core/L3_orchestration/reasoning/SubatomicHopAgent.py",
        "agentic_core/L3_orchestration/reasoning/UnifiedAgent.py",
        "agentic_core/L4_state/reasoning/CheckpointManagerAgent.py",
        "agentic_core/L4_state/reasoning/GravityStateAgent.py",
        "agentic_core/L5_safety/reasoning/AdversarialRedTeamerAgent.py",
        "agentic_core/L5_safety/reasoning/CodeDetectorAgent.py",
        "agentic_core/L5_safety/reasoning/CodeEnforcerAgent.py",
        "agentic_core/L5_safety/reasoning/CodeHealerAgent.py",
        "agentic_core/L5_safety/reasoning/CodeValidatorAgent.py",
        "agentic_core/L5_safety/reasoning/CognitiveDispositionAgent.py",
        "agentic_core/L5_safety/reasoning/ComplexityAnalyzerAgent.py",
        "agentic_core/L5_safety/reasoning/ConstitutionalReviewerAgent.py",
        "agentic_core/L5_safety/reasoning/CostGovernorAgent.py",
        "agentic_core/L5_safety/reasoning/CredentialScannerAgent.py",
        "agentic_core/L5_safety/reasoning/DDDAlignmentAgent.py",
        "agentic_core/L5_safety/reasoning/DuplicateCodeDetectorAgent.py",
        "agentic_core/L5_safety/reasoning/DynamicSealAgent.py",
        "agentic_core/L5_safety/reasoning/FileClassificationAgent.py",
        "agentic_core/L5_safety/reasoning/GovernanceAgent.py",
        "agentic_core/L5_safety/reasoning/GravityLeakRepairAgent.py",
        "agentic_core/L5_safety/reasoning/HygieneGuardianAgent.py",
        "agentic_core/L5_safety/reasoning/NamingAgent.py",
        "agentic_core/L5_safety/reasoning/PreCommitSovereignAgent.py",
        "agentic_core/L5_safety/reasoning/PredictiveCostAuditorAgent.py",
        "agentic_core/L5_safety/reasoning/ReportLocationAgent.py",
        "agentic_core/L5_safety/reasoning/ResourceManagerAgent.py",
        "agentic_core/L5_safety/reasoning/SafetyDetectorAgent.py",
        "agentic_core/L5_safety/reasoning/SafetyExecutorAgent.py",
        "agentic_core/L5_safety/reasoning/SafetyInspectorAgent.py",
        "agentic_core/L5_safety/reasoning/SecurityManagerAgent.py",
        "agentic_core/L5_safety/reasoning/SelfUpdatingSafetyEngineAgent.py",
        "agentic_core/L5_safety/reasoning/SovereignActionPlaneAgent.py",
        "agentic_core/L5_safety/reasoning/StructuralValidatorAgent.py",
        "agentic_core/L5_safety/reasoning/StructureEnforcerAgent.py",
        "agentic_core/L5_safety/reasoning/StructureHealerAgent.py",
        "agentic_core/L5_safety/reasoning/TerritoryChangeHandlerAgent.py",
        "agentic_core/knowledge/reasoning/SovereignRAGManagerAgent.py",
    },
)


# ── Tests ──────────────────────────────────────────────────────────────────────
def test_structural_identity_no_new_violations():
    """No new structural identity violations beyond known debt."""
    violations: dict[str, list[str]] = {}
    for f in collect_reasoning_agent_files():
        tree = parse_file_ast(f)
        if tree is None:
            continue
        # Structural identity is ALWAYS enforced, even for exempt agents (Phase 8)
        issues = _check_structural_identity(f, tree)
        if issues:
            violations[rel(f)] = issues

    new_violations = set(violations.keys()) - KNOWN_DEBT
    if new_violations:
        details = "\n".join(f"  {k}: {violations[k]}" for k in sorted(new_violations))
        pytest.fail(f"New structural identity violations:\n{details}")


def test_structural_identity_debt_ceiling():
    """Debt count must not exceed known ceiling (§29, §32)."""
    count = 0
    for f in collect_reasoning_agent_files():
        tree = parse_file_ast(f)
        if tree is None:
            continue
        if _check_structural_identity(f, tree):
            count += 1
    ceiling = len(KNOWN_DEBT)
    assert count <= ceiling, f"Structural identity debt grew: actual={count}, ceiling={ceiling}"
