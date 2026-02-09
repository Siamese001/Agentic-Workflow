"""List exact file paths for all retirement and merge targets."""

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
INV_PATH = PROJECT_ROOT / "artifacts" / "consolidation" / "agent_inventory.json"

RETIRE = {
    "OutreachAgent",
    "MCPHardenedMixin",
    "DiscoveredAgent",
    "DependencyDiplomatAgent",
    "SemanticTerritoryMapperAgent",
    "OmniContextAgent",
    "SemanticMapperAgent",
    "StrategistAgent",
    "GlobalComplianceAggregatorAgent",
    "UiValidationAgent",
    "IntelligenceLibrarianAgent",
    "MessageArchitectAgent",
    "CampaignPlannerAgent",
    "CartographerAgent",
    "LeadQualityAgent",
}

MERGE = {
    "HOP1ProfileAnalysisAgent",
    "HOP2ResearchAgent",
    "HOP3SenderGroundingAgent",
    "HOP4RoutingAgent",
    "HOP5GenerationAgent",
    "HOP6ValidationAgent",
    "HOP7GateDecisionAgent",
    "HOP8QAReportAgent",
    "HOP9IntegrationAgent",
    "ATSCompatibilityAgent",
    "BrandComplianceAgent",
    "FactCheckAgent",
    "SectionBalanceAgent",
    "CampaignBalanceAgent",
    "DeliverabilityAgent",
    "DagRuntimeInspectorAgent",
    "SignatureVerifierAgent",
    "TokenBudgetInspectorAgent",
    "TrackObservabilityCostAgent",
    "CoordinateObservabilityOperationsAgent",
    "StrategicObservationAgent",
    "DeadlockDetectorAgent",
    "DebateSynthesisAgent",
    "RuntimeTelemetryAgent",
    "ContentStrategyAgent",
    "RgStrategicPlannerAgent",
    "RgTemplateOptimizerAgent",
}

inv = json.loads(INV_PATH.read_text(encoding="utf-8"))

print("=== RETIREMENT TARGETS ===")
retire_paths = []
for a in inv["agents"]:
    if a["class_name"] in RETIRE:
        fp = a["file_path"]
        full = PROJECT_ROOT / fp
        exists = full.exists()
        print(f"  {a['class_name']:42s} {fp:60s} exists={exists}")
        retire_paths.append(fp)

print(f"\nTotal retirement files: {len(retire_paths)}")

print("\n=== MERGE TARGETS ===")
merge_paths = []
for a in inv["agents"]:
    if a["class_name"] in MERGE:
        fp = a["file_path"]
        full = PROJECT_ROOT / fp
        exists = full.exists()
        print(f"  {a['class_name']:42s} {fp:60s} exists={exists}")
        merge_paths.append(fp)

print(f"\nTotal merge files: {len(merge_paths)}")

# Save paths for implementation script
out = {
    "retire": retire_paths,
    "merge": merge_paths,
}
out_path = PROJECT_ROOT / "artifacts" / "consolidation" / "target_paths.json"
out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
print(f"\nSaved to {out_path}")
