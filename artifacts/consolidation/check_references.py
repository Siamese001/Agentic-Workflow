"""Check import references for retirement/merge candidates."""

from __future__ import annotations

import ast
from collections import defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
INV_PATH = PROJECT_ROOT / "artifacts" / "consolidation" / "agent_inventory.json"

RETIREMENT_CANDIDATES = {
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

MERGE_CANDIDATES = {
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

ALL_TARGETS = RETIREMENT_CANDIDATES | MERGE_CANDIDATES

# Scan all Python files for references
PY_EXTENSIONS = {".py"}
SKIP_DIRS = {".git", ".venv", ".nox", "__pycache__", ".pytest_cache", "node_modules", ".ruff_cache"}


def scan_references():
    refs: dict[str, list[str]] = defaultdict(list)

    for py_file in PROJECT_ROOT.rglob("*.py"):
        if any(skip in py_file.parts for skip in SKIP_DIRS):
            continue

        rel = py_file.relative_to(PROJECT_ROOT).as_posix()

        try:
            source = py_file.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue

        for target in ALL_TARGETS:
            if target in source:
                # Verify it's a real reference (import or class usage), not just in a comment
                try:
                    tree = ast.parse(source)
                except SyntaxError:
                    if target in source:
                        refs[target].append(f"{rel} (unparseable)")
                    continue

                for node in ast.walk(tree):
                    if isinstance(node, ast.ImportFrom):
                        if node.names:
                            for alias in node.names:
                                if alias.name == target:
                                    refs[target].append(f"{rel} (import)")
                                    break
                    elif isinstance(node, ast.Name) and node.id == target:
                        refs[target].append(f"{rel} (name_ref)")
                    elif isinstance(node, ast.Attribute) and node.attr == target:
                        refs[target].append(f"{rel} (attr_ref)")
                    elif (
                        isinstance(node, ast.Constant)
                        and isinstance(node.value, str)
                        and target in node.value
                    ):
                        refs[target].append(f"{rel} (string_ref)")

    return refs


def main():
    refs = scan_references()

    print("=" * 80)
    print("RETIREMENT CANDIDATES — Import References")
    print("=" * 80)
    for name in sorted(RETIREMENT_CANDIDATES):
        r = refs.get(name, [])
        # Deduplicate
        unique = sorted(set(r))
        tag = "SAFE" if len(unique) <= 1 else f"REFS={len(unique)}"
        print(f"  [{tag:8s}] {name}")
        for ref in unique:
            print(f"           -> {ref}")

    print()
    print("=" * 80)
    print("MERGE CANDIDATES — Import References")
    print("=" * 80)
    for name in sorted(MERGE_CANDIDATES):
        r = refs.get(name, [])
        unique = sorted(set(r))
        tag = "SAFE" if len(unique) <= 1 else f"REFS={len(unique)}"
        print(f"  [{tag:8s}] {name}")
        for ref in unique[:5]:
            print(f"           -> {ref}")
        if len(unique) > 5:
            print(f"           -> ... and {len(unique) - 5} more")

    # Summary
    print()
    safe_retire = sum(1 for n in RETIREMENT_CANDIDATES if len(set(refs.get(n, []))) <= 1)
    safe_merge = sum(1 for n in MERGE_CANDIDATES if len(set(refs.get(n, []))) <= 1)
    print(f"Safe retirements (≤1 ref): {safe_retire}/{len(RETIREMENT_CANDIDATES)}")
    print(f"Safe merges (≤1 ref): {safe_merge}/{len(MERGE_CANDIDATES)}")


if __name__ == "__main__":
    main()
