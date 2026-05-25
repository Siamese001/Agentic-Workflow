#!/usr/bin/env python3
"""Build agent capability decision matrix for spine/apps leverage analysis.

Reads runtime assessment + per-agent spine trace; emits JSON matrix and summary counts.
"""
from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

# Integration patterns (how capability could enter agentic_core / apps)
P1_SPINE_FUNCTION = "P1_SPINE_FUNCTION_EXTENSION"
P2_GENERIC_ENGINE = "P2_GENERIC_ENGINE_NEW"
P3_PROFILE_HOOK = "P3_PROFILE_EXTENSION"
P4_APP_CALLABLE = "P4_APP_OWNED_CALLABLE"
P5_JUDGE_PANEL = "P5_EXIT_JUDGE_PANEL_ADAPTER"
P6_MANAGED_WF = "P6_MANAGED_WORKFLOW_BRANCH"
P7_CI_OPS = "P7_CI_OPS_SIDEcar"
P8_CONTRACT = "P8_CONTRACT_ONLY"
P9_ARCHIVE = "P9_ARCHIVE_DELETE"

PATTERNS = (
    P1_SPINE_FUNCTION,
    P2_GENERIC_ENGINE,
    P3_PROFILE_HOOK,
    P4_APP_CALLABLE,
    P5_JUDGE_PANEL,
    P6_MANAGED_WF,
    P7_CI_OPS,
    P8_CONTRACT,
    P9_ARCHIVE,
)

TIER_A = "TIER_A_HARVEST_NOW"
TIER_B = "TIER_B_APP_OPTIONAL"
TIER_C = "TIER_C_CI_ONLY"
TIER_D = "TIER_D_DELETE"

JUDGE_PANEL_CANDIDATES = frozenset({
    "AdversarialProbeAgent",
    "AdversarialRedTeamerAgent",
    "SafetyInspectorAgent",
    "RedTeamAgent",
    "GenerativeGuardAgent",
    "ConstitutionalReviewerAgent",
    "BoundaryTestingAgent",
})

RETRIEVAL_CANDIDATES = frozenset({
    "EmbeddingSovereignAgent",
    "SovereignRAGManager",
    "L2EmbeddingSovereignAgent",
    "RedisSovereignAgent",
})

L0_GATE_CANDIDATES = frozenset({
    "SemanticGatekeeperAgent",
    "AutonomyGuardianAgent",
    "SSOTFolderCleanupAgent",
})

INTEGRITY_GATE = frozenset({
    "IntegrityGateExecutorAgent",
    "L5IntegrityGateExecutorAgent",
})

DAG_ORCHESTRATION = frozenset({
    "DomainPlannerAgent",
    "DagEngineAgent",
    "DAGMutatorAgent",
    "UnifiedAgent",
    "NervousSystemAgent",
    "FissionManagerAgent",
    "OrchestrationHandshakeAgent",
    "SubAtomicAgent",
    "SubatomicHopAgent",
    "StateManagementAgent",
    "FeasibilityAnalystAgent",
    "RiskAssessorAgent",
    "StrategyCoordinatorAgent",
    "StrategyScenarioSimulatorAgent",
    "CoverageAgent",
    "DagRuntimeInspector",
    "GravityStateAgent",
})

L6_POST_RUN = frozenset({
    "MetaLearningAgent",
    "ObservabilityProbeExecutorAgent",
    "PerformanceAnalystAgentSimple",
})

WRAPPER_ONLY = frozenset({
    "SovereignBaseAgent",
    "IOrchestratorAgent",
    "ITieredAgent",
    "L2ExecutionAgent",
    "L2EmbeddingSovereignAgent",
    "L2RedisSovereignAgent",
    "L2SovereignMCPGatewayAgent",
    "L2StructuredEngineAgent",
    "L2SubAtomicRegistryAgent",
    "StructuredEngineAgent",
    "GravityStateAgent",
    "CoverageAgent",
    "OrchestrationHandshakeAgent",
    "StateManagementAgent",
    "DagRuntimeInspector",
})

FCA_CLUSTER = frozenset({
    "FileClassificationHealerAgent",
    "FileClassificationValidatorAgent",
    "FilesystemSSOTValidatorAgent",
    "ArchitectureGovernorAgent",
    "ArchitectureGovernorValidatorAgent",
    "HierarchyHealerAgent",
    "HierarchyValidatorAgent",
    "CodeDetectorAgent",
    "StructureEnforcerAgent",
    "StructureHealerAgent",
    "StructuralValidatorAgent",
    "StructuralEngineerAgent",
})

SHIM_NAMES = frozenset({"RootCustomsAgent"})


@dataclass
class DecisionRow:
    class_name: str
    module_path: str
    declared_layer: str
    inventory_role: str
    spine_trace_verdict: str
    spine_closure: bool
    apps_rg_importers: int
    prod_importers: int
    loc_estimate: int
    integration_pattern: str
    spine_stage: str
    recommendation_tier: str
    core_substitute: str
    refactor_effort: str
    apps_payoff: str
    rationale: str
    harvest_action: str


def _loc(path: str) -> int:
    p = REPO / path
    if not p.is_file():
        return 0
    return len(p.read_text(encoding="utf-8", errors="replace").splitlines())


def _classify(name: str, row: dict, trace: dict) -> tuple[str, str, str, str, str, str, str]:
    """Return pattern, tier, stage, substitute, effort, payoff, harvest_action."""
    layer = row["declared_layer"]
    role = row.get("inventory_role", "")
    expected = row.get("expected_spine_role", "")
    verdict = trace.get("verdict", "")
    loc = _loc(row["module_path"])

    if verdict == "ORPHAN_NO_REF" or name in SHIM_NAMES and role == "SHIM_OR_DEAD_LEGACY":
        return (
            P9_ARCHIVE,
            TIER_D,
            "NONE",
            "none",
            "S" if loc < 500 else "M",
            "NONE",
            "Archive or delete; zero spine/apps fan-in",
        )

    if name in WRAPPER_ONLY or role == "UTILITY_OR_WRAPPER":
        return (
            P8_CONTRACT,
            TIER_D if name.startswith("L2") and "Registry" not in name else TIER_C,
            "L2_EXECUTE" if "L2" in name else "NONE",
            "l2_execution_contract / orchestrator protocols",
            "S",
            "LOW",
            "Keep protocol; delete fat wrapper impl if unused",
        )

    if name in JUDGE_PANEL_CANDIDATES:
        return (
            P5_JUDGE_PANEL,
            TIER_B,
            "EXIT_X3",
            "runtime/judges/panel/JudgePanelRunner",
            "M",
            "MED",
            "Extract rubric-facing checks as JudgeProviderAdapter; do not mount Agent on spine",
        )

    if name in RETRIEVAL_CANDIDATES:
        return (
            P3_PROFILE_HOOK,
            TIER_A,
            "C0_CONTEXT",
            "C0 profile + semantic_cache_manager",
            "L",
            "HIGH",
            "Fold into retrieval profile/coordinator; delete sovereign agent class",
        )

    if name in L0_GATE_CANDIDATES:
        return (
            P2_GENERIC_ENGINE,
            TIER_A,
            "L0_ROUTE",
            "check_route_gates + route profiles",
            "M",
            "MED",
            "Extract policy checks into L0 gate util; not RootCustoms-style agent",
        )

    if name in INTEGRITY_GATE:
        return (
            P4_APP_CALLABLE,
            TIER_B,
            "L2_EXECUTE",
            "apps validators + generic gate_executor util",
            "M",
            "MED",
            "Generalize gate executor under runtime/gates; apps inject via profile",
        )

    if name in DAG_ORCHESTRATION or "workflow/DAG" in expected:
        return (
            P6_MANAGED_WF,
            TIER_B,
            "L3_ORCHESTRATION",
            "ExitEvalPipeline + managed_workflow_runner (today)",
            "L",
            "LOW_MED",
            "Only if product adopts MANAGED_WORKFLOW spine; else archive DAG agent graph",
        )

    if name in L6_POST_RUN:
        return (
            P2_GENERIC_ENGINE,
            TIER_B,
            "L6_RUNTIME_EXHAUST",
            "L6_system_learning buses (post-run boundary)",
            "M",
            "MED",
            "Post-run observer only; never current-run spine",
        )

    if name in FCA_CLUSTER or "FileClassification" in name:
        if name == "FileClassificationHealerAgent":
            return (
                P7_CI_OPS,
                TIER_D,
                "NONE",
                "ADG + structure_blueprint + CI folder rules",
                "XL",
                "LOW",
                "Extract file_classification/* to ops CI; delete 5k agent shell",
            )
        return (
            P7_CI_OPS,
            TIER_C,
            "NONE",
            "structure_blueprint / ADG",
            "M",
            "LOW",
            "CI/heal sidecar; collapse into utils not spine",
        )

    if layer == "L5" or "governance/heal" in expected:
        return (
            P7_CI_OPS,
            TIER_C,
            "NONE",
            "generic safety_audit + ADG violations",
            "M",
            "LOW",
            "Dev/CI certification cluster; not product spine",
        )

    if layer == "L3" and truly_agent_heuristic(row):
        return (
            P6_MANAGED_WF,
            TIER_B,
            "L3_ORCHESTRATION",
            "exit_eval v6 pipeline",
            "M",
            "LOW",
            "Orchestration adjunct; prefer functions over agent reinstatement",
        )

    if layer == "L1":
        return (
            P2_GENERIC_ENGINE,
            TIER_B,
            "L1_PLAN",
            "u0_to_l1_plan bridge",
            "M",
            "MED",
            "Plan contract bridge is spine; agent class redundant",
        )

    return (
        P7_CI_OPS,
        TIER_C,
        "NONE",
        "varies",
        "M",
        "LOW",
        "Default: off-spine tooling; prove need before harvest",
    )


def truly_agent_heuristic(row: dict) -> bool:
    return row.get("truly_agent") == "YES"


def main() -> int:
    assess = json.loads(
        (REPO / "docs/reports/agentic_core_agent_inventory_runtime_assessment.json").read_text(
            encoding="utf-8"
        )
    )
    trace_doc = json.loads(
        (REPO / "docs/reports/cursor/agent_spine_trace_per_agent.json").read_text(encoding="utf-8")
    )
    by_trace = {t["class_name"]: t for t in trace_doc["traces"]}

    rows: list[DecisionRow] = []
    for r in assess["rows"]:
        name = r["agent"]
        tr = by_trace.get(name, {})
        pattern, tier, stage, sub, effort, payoff, action = _classify(name, r, tr)
        rows.append(
            DecisionRow(
                class_name=name,
                module_path=r["module_path"],
                declared_layer=r["declared_layer"],
                inventory_role=r.get("inventory_role", ""),
                spine_trace_verdict=tr.get("verdict", "UNKNOWN"),
                spine_closure=bool(tr.get("spine_module_in_closure")),
                apps_rg_importers=int(tr.get("apps_rg_importers", 0)),
                prod_importers=int(tr.get("importer_count_prod", 0)),
                loc_estimate=_loc(r["module_path"]),
                integration_pattern=pattern,
                spine_stage=stage,
                recommendation_tier=tier,
                core_substitute=sub,
                refactor_effort=effort,
                apps_payoff=payoff,
                rationale=r.get("expected_spine_role", "")[:120],
                harvest_action=action,
            )
        )

    by_pattern = Counter(x.integration_pattern for x in rows)
    by_tier = Counter(x.recommendation_tier for x in rows)
    tier_a = [x for x in rows if x.recommendation_tier == TIER_A]

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    out = REPO / "docs/reports/cursor"
    out.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at": ts,
        "model_version": "agent-capability-decision-v1",
        "inputs": [
            "docs/reports/agentic_core_agent_inventory_runtime_assessment.json",
            "docs/reports/cursor/agent_spine_trace_per_agent.json",
        ],
        "summary": {
            "agent_count": len(rows),
            "by_integration_pattern": dict(by_pattern),
            "by_recommendation_tier": dict(by_tier),
            "tier_a_harvest": [x.class_name for x in tier_a],
            "spine_closure_agents": sum(1 for x in rows if x.spine_closure),
        },
        "rows": [asdict(x) for x in rows],
    }
    json_path = out / "agent_capability_decision_matrix.json"
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(json.dumps({"json": json_path.as_posix(), "by_pattern": dict(by_pattern), "by_tier": dict(by_tier)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
