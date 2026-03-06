"""Semantic Gap Analyzer for Agentic Architecture Major Arteries.

Traces actual execution flows through L0-L6 layers and identifies where
architectural intent (lower latency, deterministic lookups, cache-first patterns)
diverges from implementation reality.

Usage:
    python tools/semantic_gap_analyzer.py --output docs/reports/plans/semantic_gap_analysis.md
"""

from __future__ import annotations

import ast
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).parent.parent
AGENTIC_CORE = REPO_ROOT / "agentic_core"

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


@dataclass
class ImportTrace:
    """Tracks an import statement and its usage context."""

    module: str
    imported_names: list[str]
    file_path: Path
    line_number: int
    is_used: bool = False


@dataclass
class CacheOpportunity:
    """Represents a potential caching opportunity."""

    layer: str
    hot_path: str
    current_pattern: str
    cache_candidate: str
    impact: str
    priority: str
    evidence: list[str] = field(default_factory=list)


@dataclass
class SemanticGap:
    """Represents a gap between architectural intent and implementation."""

    gap_id: str
    layer: str
    artery: str
    intent: str
    reality: str
    impact: str
    priority: str
    evidence_files: list[str] = field(default_factory=list)
    recommended_fix: str = ""


class ASTAnalyzer:
    """AST-based code analyzer for tracing execution flows."""

    def __init__(self, root: Path):
        self.root = root
        self.import_graph: dict[str, list[ImportTrace]] = {}
        self.function_calls: dict[str, list[tuple[str, int]]] = {}

    def analyze_file(self, file_path: Path) -> dict[str, Any]:
        """Analyze a Python file and extract imports, calls, and patterns."""
        try:
            content = file_path.read_text(encoding="utf-8")
            tree = ast.parse(content, filename=str(file_path))
        except (SyntaxError, UnicodeDecodeError, OSError) as e:
            logger.warning(f"Failed to parse {file_path}: {e}")
            return {}

        imports = []
        calls = []
        cache_reads = []
        cache_writes = []
        l4_state_accesses = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(
                        ImportTrace(
                            module=alias.name,
                            imported_names=[alias.asname or alias.name],
                            file_path=file_path,
                            line_number=node.lineno,
                        )
                    )
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(
                        ImportTrace(
                            module=node.module,
                            imported_names=[alias.name for alias in node.names],
                            file_path=file_path,
                            line_number=node.lineno,
                        )
                    )
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    call_name = node.func.attr
                    calls.append((call_name, node.lineno))

                    # Detect cache patterns
                    if call_name in ("get_json", "get", "hget"):
                        cache_reads.append(node.lineno)
                    elif call_name in ("set_json", "set", "hset"):
                        cache_writes.append(node.lineno)

                    # Detect L4 state accesses
                    if "ledger" in call_name.lower() or "blob" in call_name.lower():
                        l4_state_accesses.append(node.lineno)

        return {
            "imports": imports,
            "calls": calls,
            "cache_reads": cache_reads,
            "cache_writes": cache_writes,
            "l4_state_accesses": l4_state_accesses,
        }

    def find_hot_paths(self, layer_dir: Path, pattern: str) -> list[Path]:
        """Find files matching a pattern in a layer directory."""
        return list(layer_dir.rglob(pattern))


class SemanticGapAnalyzer:
    """Main analyzer for detecting semantic gaps in the architecture."""

    def __init__(self):
        self.ast_analyzer = ASTAnalyzer(AGENTIC_CORE)
        self.gaps: list[SemanticGap] = []
        self.cache_opportunities: list[CacheOpportunity] = []

    def analyze_l0_routing_gate(self) -> list[SemanticGap]:
        """Analyze L0 routing gate for semantic gaps."""
        logger.info("Analyzing L0 Routing Gate...")
        gaps = []

        # Check if discovery_cache is wired into full_agent_discovery
        discovery_py = AGENTIC_CORE / "utils" / "full_agent_discovery.py"
        if discovery_py.exists():
            analysis = self.ast_analyzer.analyze_file(discovery_py)
            imports = analysis.get("imports", [])

            # Check if discovery_cache is imported
            cache_imported = any("discovery_cache" in imp.module for imp in imports)

            if not cache_imported:
                gaps.append(
                    SemanticGap(
                        gap_id="L0-GAP-001",
                        layer="L0",
                        artery="Agent Discovery Hot Path",
                        intent="Cache agent discovery results to avoid repeated file I/O and AST parsing",
                        reality="full_agent_discovery.py does not import or use discovery_cache.py",
                        impact="Every agent discovery call re-scans filesystem and re-parses Python files",
                        priority="HIGH",
                        evidence_files=[str(discovery_py)],
                        recommended_fix="Import AgentDiscoveryCache and wrap get_all_agents() with cache.get_or_fetch()",
                    )
                )

        # Check reasoning_policy_engine for policy registry cache usage
        policy_engine = AGENTIC_CORE / "L0_routing" / "engines" / "reasoning_policy_engine.py"
        if policy_engine.exists():
            analysis = self.ast_analyzer.analyze_file(policy_engine)
            imports = analysis.get("imports", [])

            policy_cache_imported = any("policy_registry_cache" in imp.module for imp in imports)

            if not policy_cache_imported:
                gaps.append(
                    SemanticGap(
                        gap_id="L0-GAP-002",
                        layer="L0",
                        artery="Reasoning Policy Engine",
                        intent="Cache immutable policy configurations to avoid repeated L4 state lookups",
                        reality="reasoning_policy_engine.py does not use policy_registry_cache.py",
                        impact="Policy config fetched from L4 state on every request",
                        priority="MEDIUM",
                        evidence_files=[str(policy_engine)],
                        recommended_fix="Wrap policy_config retrieval with PolicyRegistryCache.get_or_fetch()",
                    )
                )

        return gaps

    def analyze_l1_cognition(self) -> list[SemanticGap]:
        """Analyze L1 cognition layer for semantic gaps."""
        logger.info("Analyzing L1 Cognition Layer...")
        gaps = []

        # Check cognitive_engine for tool embedding cache
        cognitive_engine = AGENTIC_CORE / "L1_cognition" / "engines" / "cognitive_engine.py"
        if cognitive_engine.exists():
            analysis = self.ast_analyzer.analyze_file(cognitive_engine)
            imports = analysis.get("imports", [])

            tool_cache_imported = any("tool_embedding_cache" in imp.module for imp in imports)

            if not tool_cache_imported:
                gaps.append(
                    SemanticGap(
                        gap_id="L1-GAP-001",
                        layer="L1",
                        artery="Cognitive Engine Tool Resolution",
                        intent="Cache expensive tool embedding computations to avoid repeated API calls",
                        reality="cognitive_engine.py does not use tool_embedding_cache.py",
                        impact="Tool embeddings recomputed on every cognition cycle",
                        priority="HIGH",
                        evidence_files=[str(cognitive_engine)],
                        recommended_fix="Import ToolEmbeddingCache and wrap embedding generation with cache.get_or_fetch()",
                    )
                )

        # Check for prompt artifact cache usage
        prompt_files = list((AGENTIC_CORE / "L1_cognition").rglob("*prompt*.py"))
        for prompt_file in prompt_files:
            analysis = self.ast_analyzer.analyze_file(prompt_file)
            imports = analysis.get("imports", [])

            prompt_cache_imported = any("prompt_artifact_cache" in imp.module for imp in imports)

            if not prompt_cache_imported and "cache" not in prompt_file.name:
                gaps.append(
                    SemanticGap(
                        gap_id=f"L1-GAP-PROMPT-{prompt_file.stem}",
                        layer="L1",
                        artery="Prompt Artifact Retrieval",
                        intent="Cache parsed prompt templates to avoid repeated file I/O and parsing",
                        reality=f"{prompt_file.name} does not use prompt_artifact_cache",
                        impact="Prompt templates re-read and re-parsed on every request",
                        priority="MEDIUM",
                        evidence_files=[str(prompt_file)],
                        recommended_fix="Wrap prompt loading with prompt_artifact_cache.get_or_fetch()",
                    )
                )

        return gaps

    def analyze_l2_execution(self) -> list[SemanticGap]:
        """Analyze L2 execution layer for semantic gaps."""
        logger.info("Analyzing L2 Execution Layer...")
        gaps = []

        # Check for schema validator cache usage
        validator_files = list((AGENTIC_CORE / "L2_execution").rglob("*validator*.py"))
        for validator_file in validator_files:
            if "cache" in validator_file.name:
                continue

            analysis = self.ast_analyzer.analyze_file(validator_file)
            imports = analysis.get("imports", [])

            schema_cache_imported = any("schema_validator_cache" in imp.module for imp in imports)

            if not schema_cache_imported:
                gaps.append(
                    SemanticGap(
                        gap_id=f"L2-GAP-VALIDATOR-{validator_file.stem}",
                        layer="L2",
                        artery="Schema Validation Hot Path",
                        intent="Cache compiled JSON schema validators to avoid repeated compilation",
                        reality=f"{validator_file.name} does not use schema_validator_cache",
                        impact="Schema validators recompiled on every validation request",
                        priority="HIGH",
                        evidence_files=[str(validator_file)],
                        recommended_fix="Wrap validator compilation with schema_validator_cache.get_or_fetch()",
                    )
                )

        return gaps

    def analyze_l3_orchestration(self) -> list[SemanticGap]:
        """Analyze L3 orchestration layer for semantic gaps."""
        logger.info("Analyzing L3 Orchestration Layer...")
        gaps = []

        # Check orchestrator_engine for plan caching
        orchestrator = AGENTIC_CORE / "L3_orchestration" / "engines" / "orchestrator_engine.py"
        if orchestrator.exists():
            analysis = self.ast_analyzer.analyze_file(orchestrator)
            imports = analysis.get("imports", [])

            plan_cache_imported = any("orchestration_plan_cache" in imp.module for imp in imports)

            if not plan_cache_imported:
                gaps.append(
                    SemanticGap(
                        gap_id="L3-GAP-001",
                        layer="L3",
                        artery="Orchestration Plan Construction",
                        intent="Cache orchestration plans to avoid repeated planning for identical requests",
                        reality="orchestrator_engine.py does not use orchestration_plan_cache",
                        impact="Orchestration plans recomputed on every request",
                        priority="MEDIUM",
                        evidence_files=[str(orchestrator)],
                        recommended_fix="Wrap plan construction with orchestration_plan_cache.get_or_fetch()",
                    )
                )

        return gaps

    def analyze_l4_state(self) -> list[SemanticGap]:
        """Analyze L4 state layer for semantic gaps."""
        logger.info("Analyzing L4 State Layer...")
        gaps = []

        # Check blob_storage_provider for repeated lookups
        blob_storage = AGENTIC_CORE / "L4_state" / "memory" / "blob_storage_provider.py"
        if blob_storage.exists():
            analysis = self.ast_analyzer.analyze_file(blob_storage)
            l4_accesses = analysis.get("l4_state_accesses", [])

            if len(l4_accesses) > 10:
                gaps.append(
                    SemanticGap(
                        gap_id="L4-GAP-001",
                        layer="L4",
                        artery="Blob Storage Provider",
                        intent="Minimize repeated blob lookups via caching layer",
                        reality=f"blob_storage_provider.py has {len(l4_accesses)} direct state accesses",
                        impact="Repeated blob fetches increase latency and L4 state pressure",
                        priority="HIGH",
                        evidence_files=[str(blob_storage)],
                        recommended_fix="Add read-through cache layer for frequently accessed blobs",
                    )
                )

        return gaps

    def analyze_l5_safety(self) -> list[SemanticGap]:
        """Analyze L5 safety layer for semantic gaps."""
        logger.info("Analyzing L5 Safety Layer...")
        gaps = []

        # Check safety enforcement for policy cache usage
        enforcement_files = list((AGENTIC_CORE / "L5_safety" / "enforcement").rglob("*.py"))
        for enf_file in enforcement_files:
            if "cache" in enf_file.name:
                continue

            analysis = self.ast_analyzer.analyze_file(enf_file)
            imports = analysis.get("imports", [])

            policy_cache_imported = any("policy_registry_cache" in imp.module for imp in imports)

            if not policy_cache_imported and "policy" in enf_file.name.lower():
                gaps.append(
                    SemanticGap(
                        gap_id=f"L5-GAP-POLICY-{enf_file.stem}",
                        layer="L5",
                        artery="Safety Policy Enforcement",
                        intent="Cache immutable safety policies to avoid repeated L4 lookups",
                        reality=f"{enf_file.name} does not use policy_registry_cache",
                        impact="Safety policies fetched from L4 on every enforcement check",
                        priority="MEDIUM",
                        evidence_files=[str(enf_file)],
                        recommended_fix="Wrap policy retrieval with policy_registry_cache.get_or_fetch()",
                    )
                )

        return gaps

    def analyze_l6_observability(self) -> list[SemanticGap]:
        """Analyze L6 observability layer for semantic gaps."""
        logger.info("Analyzing L6 Observability Layer...")
        gaps = []

        # Check telemetry engine for config caching
        telemetry_files = list((AGENTIC_CORE / "L6_observability").rglob("*telemetry*.py"))
        for telem_file in telemetry_files:
            analysis = self.ast_analyzer.analyze_file(telem_file)
            imports = analysis.get("imports", [])

            config_cache_imported = any("config_file_cache" in imp.module for imp in imports)

            if not config_cache_imported:
                gaps.append(
                    SemanticGap(
                        gap_id=f"L6-GAP-CONFIG-{telem_file.stem}",
                        layer="L6",
                        artery="Telemetry Configuration",
                        intent="Cache parsed telemetry config files to avoid repeated I/O",
                        reality=f"{telem_file.name} does not use config_file_cache",
                        impact="Config files re-read and re-parsed on every telemetry event",
                        priority="LOW",
                        evidence_files=[str(telem_file)],
                        recommended_fix="Wrap config loading with config_file_cache.get_or_fetch()",
                    )
                )

        return gaps

    def run_analysis(self) -> dict[str, Any]:
        """Run full semantic gap analysis across all layers."""
        logger.info("Starting Semantic Gap Analysis...")

        all_gaps = []
        all_gaps.extend(self.analyze_l0_routing_gate())
        all_gaps.extend(self.analyze_l1_cognition())
        all_gaps.extend(self.analyze_l2_execution())
        all_gaps.extend(self.analyze_l3_orchestration())
        all_gaps.extend(self.analyze_l4_state())
        all_gaps.extend(self.analyze_l5_safety())
        all_gaps.extend(self.analyze_l6_observability())

        self.gaps = all_gaps

        # Categorize by priority
        high_priority = [g for g in all_gaps if g.priority == "HIGH"]
        medium_priority = [g for g in all_gaps if g.priority == "MEDIUM"]
        low_priority = [g for g in all_gaps if g.priority == "LOW"]

        logger.info("\nAnalysis Complete:")
        logger.info(f"  Total Gaps: {len(all_gaps)}")
        logger.info(f"  HIGH Priority: {len(high_priority)}")
        logger.info(f"  MEDIUM Priority: {len(medium_priority)}")
        logger.info(f"  LOW Priority: {len(low_priority)}")

        return {
            "total_gaps": len(all_gaps),
            "high_priority": len(high_priority),
            "medium_priority": len(medium_priority),
            "low_priority": len(low_priority),
            "gaps": all_gaps,
        }

    def generate_report(self, output_path: Path) -> None:
        """Generate markdown report of semantic gaps."""
        logger.info(f"Generating report: {output_path}")

        lines = []

        def h(text: str) -> None:
            lines.append(text)

        def blank() -> None:
            lines.append("")

        h("# Semantic Gap Analysis - Agentic Architecture Major Arteries")
        blank()
        h("## Executive Summary")
        blank()
        h(f"**Total Gaps Identified:** {len(self.gaps)}")
        h(f"**High Priority:** {len([g for g in self.gaps if g.priority == 'HIGH'])}")
        h(f"**Medium Priority:** {len([g for g in self.gaps if g.priority == 'MEDIUM'])}")
        h(f"**Low Priority:** {len([g for g in self.gaps if g.priority == 'LOW'])}")
        blank()
        h("## Analysis Methodology")
        blank()
        h("This analysis traces actual execution flows through L0-L6 layers using AST-based")
        h("code scanning to identify where architectural intent (lower latency, deterministic")
        h("lookups, cache-first patterns) diverges from implementation reality.")
        blank()
        h("**Approach:**")
        h("1. Map critical hot paths across each layer")
        h("2. AST scan for import statements and cache usage patterns")
        h("3. Identify missing wirings between cache modules and consumers")
        h("4. Categorize gaps by layer, artery, and priority")
        blank()

        # Group gaps by layer
        layers = {}
        for gap in self.gaps:
            if gap.layer not in layers:
                layers[gap.layer] = []
            layers[gap.layer].append(gap)

        for layer in sorted(layers.keys()):
            h(f"## {layer} Layer Gaps")
            blank()

            for gap in sorted(layers[layer], key=lambda g: (g.priority, g.gap_id)):
                h(f"### {gap.gap_id}: {gap.artery}")
                blank()
                h(f"**Priority:** {gap.priority}")
                blank()
                h("**Architectural Intent:**")
                h(f"{gap.intent}")
                blank()
                h("**Implementation Reality:**")
                h(f"{gap.reality}")
                blank()
                h("**Impact:**")
                h(f"{gap.impact}")
                blank()
                h("**Evidence Files:**")
                for ef in gap.evidence_files:
                    h(f"- `{ef}`")
                blank()
                h("**Recommended Fix:**")
                h(f"{gap.recommended_fix}")
                blank()
                h("---")
                blank()

        h("## Priority Matrix")
        blank()
        h("| Layer | High | Medium | Low | Total |")
        h("|-------|------|--------|-----|-------|")
        for layer in sorted(layers.keys()):
            layer_gaps = layers[layer]
            high = len([g for g in layer_gaps if g.priority == "HIGH"])
            medium = len([g for g in layer_gaps if g.priority == "MEDIUM"])
            low = len([g for g in layer_gaps if g.priority == "LOW"])
            total = len(layer_gaps)
            h(f"| {layer} | {high} | {medium} | {low} | {total} |")
        blank()

        h("## Next Steps")
        blank()
        h("1. **High Priority Gaps:** Address immediately - these cause repeated expensive operations")
        h("2. **Medium Priority Gaps:** Schedule for next sprint - moderate latency impact")
        h("3. **Low Priority Gaps:** Backlog - minor optimizations")
        blank()
        h("## Validation")
        blank()
        h("After implementing fixes, rerun semantic gap analysis to verify:")
        h("- Cache modules are imported in hot path files")
        h("- `get_or_fetch` pattern is used consistently")
        h("- Replay mode tests pass with warm cache (no redundant fetches)")
        h("- Side-effect envelope tests confirm cache-first behavior")
        blank()

        content = "\n".join(lines)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content, encoding="utf-8")
        logger.info(f"Report written to {output_path}")


def main() -> None:
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Semantic Gap Analyzer")
    parser.add_argument(
        "--output",
        type=Path,
        default=REPO_ROOT / "docs" / "reports" / "plans" / "semantic_gap_analysis.md",
        help="Output path for the analysis report",
    )
    args = parser.parse_args()

    analyzer = SemanticGapAnalyzer()
    analyzer.run_analysis()
    analyzer.generate_report(args.output)


if __name__ == "__main__":
    main()
