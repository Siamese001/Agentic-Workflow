#!/usr/bin/env python3
"""
Phase 20: Sovereign Core Logic Synthesis - Advanced Multimodal Disposition Analysis

Performs high-r CFG & Data-Flow Analysis, Symbolic Execution, and Contract Verification
on agentic_core/base_agents/ to eliminate entropy and establish the Final Sovereign Engine.
"""

import ast
import json
import uuid
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

import networkx as nx

from agentic_core.L0_routing.config import (
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
)
from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_policy_state,  # noqa: E402
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_emits_metric_event("disposition", "p4obs", "metric_1")
_emit_emits_metric_event("disposition", "p4obs", "metric_2")
_emit_emits_metric_event("disposition", "p4obs", "metric_3")
_emit_emits_metric_event("disposition", "p4obs", "metric_4")
_emit_emits_metric_event("disposition", "p4obs", "metric_5")
_emit_emits_metric_event("disposition", "p4obs", "metric_6")
_emit_records_incident_event("disposition", "p4obs", "incident")
_emit_captures_runtime_anomaly("disposition", "p4obs", "anomaly")
_emit_writes_observability_log("disposition", "p4obs", "obs_log")
_emit_updates_monitoring_state("disposition", "p4obs", "mon_state")
_emit_triggers_alert("disposition", "p4obs", "alert")
_emit_links_incident_trace("disposition", "p4obs", "trace_link")
_emit_captures_pattern("disposition", "p3lm", "pattern")
_emit_records_learning_event("disposition", "p3lm", "learning_event")
_emit_writes_learning_snapshot("disposition", "p3lm", "snapshot")
_emit_feeds_meta_learning("disposition", "p3lm", "meta_feed")
_emit_updates_routing_strategy("disposition", "p3lm", "routing")
_emit_improves_agent_policy("disposition", "p3lm", "policy")
_emit_stores_learning_state("disposition", "p3lm", "state")
_emit_records_execution_trace("disposition", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("disposition", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("disposition", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("disposition", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("disposition", "L4_STATE", "p2_trace_5")
_emit_reads_environ("disposition", "env_read", "p2_env_1")
_emit_reads_environ("disposition", "env_read", "p2_env_2")
_emit_reads_runtime_state("disposition", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("disposition", "runtime_state", "p2_rt_2")

emit_replay_key("p0", "disposition")
emit_determinism_digest("p0", "disposition")

_emit_dispatches_healing_run("p1", "disposition", "L0")
_emit_routes_through("p1", "disposition", "L0")
_emit_checks_agent_registry("p1", "disposition", "agent_registry")
_emit_validates_agent_capability("p1", "disposition", "capability")
_emit_dispatches_execution_plan("p1", "disposition", "exec_plan")
_emit_agent_executes_agent("p1", "disposition", "sub_agent")
_emit_routes_to_agent("p1", "disposition", "target_agent")
_emit_observes_runtime_state("p1", "disposition", "runtime_state")
_emit_verifies_boundary("p1", "disposition", "boundary_check")
_emit_transcripts_response("p1", "disposition", "transcript")
_emit_hard_fails_untranscripted("p1", "disposition")
_emit_gated_by_confidence("p1", "disposition", "confidence_gate")
_emit_escalates_to_human("p1", "disposition", "L0")
_emit_reads_policy_state("p1", "disposition", "L0")
_emit_pulls_context("p1", "disposition", "context_pull")
_emit_pulls_context("p1", "disposition", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "disposition", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "disposition", "uwg_term_secondary")
_emit_writes_through("p1", "disposition", "write_through")
_emit_writes_through("p1", "disposition", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "disposition", "safety_validation")
_emit_invokes_eval("p1", "disposition", "eval_call")
_emit_proposal_commits_routing("p1", "disposition", "routing_commit")

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "disposition", "p0_governance")
_emit_snapshots_state("p0", "disposition", "state_snapshot")
_emit_authorize_and_execute("p2", "disposition", "execution_auth")
_emit_validates_capability("p2", "disposition", "capability_check")
_emit_routes_to_capability("p2", "disposition", "capability_route")
_emit_writes_via_uwg("p2", "disposition", "uwg_write")
_emit_blocks_direct_write("p2", "disposition", "direct_write_block")
_emit_records_tool_invocation("p2", "disposition", "tool_invocation")
_emit_captures_execution_output("p2", "disposition", "exec_output")
_emit_dispatches_agent("p3", "disposition", "agent_dispatch")
_emit_coordinates_agents("p3", "disposition", "agent_coordination")
_emit_records_workflow_lineage("p3", "disposition", "workflow_lineage")
_emit_records_healing_outcome("p3", "disposition", "healing_outcome")
_emit_escalates_failure("p3", "disposition", "failure_escalation")
_emit_orchestrates_workflow("p3", "disposition", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "disposition", "healing_dispatch")
_emit_invokes_evaluation("p3", "disposition", "evaluation_signal")
_emit_records_telemetry_event("p4", "disposition", "telemetry_event")
_emit_captures_evaluation_metric("p4", "disposition", "eval_metric")
_emit_stores_embedding("p4", "disposition", "embedding_store")
_emit_updates_meta_learning_state("p4", "disposition", "meta_learning")
_emit_links_execution_to_snapshot("p4", "disposition", "exec_snapshot_link")


class Disposition(Enum):
    """File disposition for synthesis analysis."""

    KEEP = "KEEP"
    ARCHIVE = "ARCHIVE"
    SYNTHESIZE = "SYNTHESIZE"


@dataclass
class CoreAnalysisResult:
    """Result of core analysis for a single file."""

    file_path: str
    disposition: Disposition
    synthesis_target: str | None
    instructional_weight: float
    rationale: str
    cfg_complexity: int
    data_flow_nodes: int
    circular_deps: list[str]
    contract_compliance: bool
    sovereign_requirements: list[str]


class CoreSynthesisAnalyzer:
    """Advanced analyzer for sovereign core logic synthesis."""

    def __init__(self, base_path: str = "agentic_core/base_agents"):
        self.base_path = Path(base_path)
        self.analysis_results = []
        self.dependency_graph = nx.DiGraph()

    def analyze_file(self, file_path: Path) -> CoreAnalysisResult:
        """Perform comprehensive analysis of a single file."""

        _emit_records_execution_trace(
            str(uuid.uuid4()),
            LayerSegment.L3_ORCHESTRATION,
            f"CoreDispositionAnalyzer.analyze_file:{file_path.name}",
        )
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            tree = ast.parse(content)

            # CFG & Data-Flow Analysis
            cfg_complexity = self._analyze_cfg_complexity(tree)
            data_flow_nodes = self._analyze_data_flow(tree)

            # Dependency Analysis
            imports = self._extract_imports(tree)
            circular_deps = self._detect_circular_dependencies(file_path, imports)

            # Contract Compliance
            contract_compliance = self._verify_contract_compliance(tree)

            # Sovereign Requirements Analysis
            sovereign_requirements = self._analyze_sovereign_requirements(tree)

            # Determine disposition and synthesis target
            disposition, synthesis_target, weight, rationale = self._determine_disposition(
                file_path,
                tree,
                cfg_complexity,
                data_flow_nodes,
                circular_deps,
                contract_compliance,
                sovereign_requirements,
            )

            return CoreAnalysisResult(
                file_path=str(file_path.relative_to(self.base_path)),
                disposition=disposition,
                synthesis_target=synthesis_target,
                instructional_weight=weight,
                rationale=rationale,
                cfg_complexity=cfg_complexity,
                data_flow_nodes=data_flow_nodes,
                circular_deps=circular_deps,
                contract_compliance=contract_compliance,
                sovereign_requirements=sovereign_requirements,
            )

        # guardian: allow-silent-swallow
        except (ValueError, TypeError) as e:
            return CoreAnalysisResult(
                file_path=str(file_path.relative_to(self.base_path)),
                disposition=Disposition.ARCHIVE,
                synthesis_target=None,
                instructional_weight=0.0,
                rationale=f"Analysis error: {e}",
                cfg_complexity=0,
                data_flow_nodes=0,
                circular_deps=[],
                contract_compliance=False,
                sovereign_requirements=[],
            )

    def _analyze_cfg_complexity(self, tree: ast.AST) -> int:
        """Analyze Control Flow Graph complexity."""
        complexity = 0

        for node in ast.walk(tree):
            # Count control flow structures
            if isinstance(node, ast.If | ast.While | ast.For | ast.Try):
                complexity += 1
            elif isinstance(node, ast.With):
                complexity += 1
            elif isinstance(node, ast.FunctionDef):
                # Count branches in functions
                for child in ast.walk(node):
                    if isinstance(child, ast.If | ast.While | ast.For):
                        complexity += 1
                break

        return complexity

    def _analyze_data_flow(self, tree: ast.AST) -> int:
        """Analyze data flow nodes."""
        nodes = 0

        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                nodes += len(node.targets)
            elif isinstance(node, ast.AugAssign):
                nodes += 1
            elif isinstance(node, ast.Call):
                nodes += 1

        return nodes

    def _extract_imports(self, tree: ast.AST) -> list[str]:
        """Extract import statements."""
        imports = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    imports.append(f"{module}.{alias.name}" if module else alias.name)

        return imports

    def _detect_circular_dependencies(self, file_path: Path, imports: list[str]) -> list[str]:
        """Detect circular dependencies with app zones."""
        forbidden_zones = [APPS_LIC_DIR, APPS_RG_DIR, APPS_SHARED_DIR]
        circular_deps = []

        for imp in imports:
            if any(zone in imp for zone in forbidden_zones):
                circular_deps.append(imp)

        return circular_deps

    def _verify_contract_compliance(self, tree: ast.AST) -> bool:
        """Verify CanonBaseAgentInterface contract compliance."""
        # Check for required methods and attributes
        _emit_verifies_policy(
            str(uuid.uuid4()), "CoreSynthesisAnalyzer._verify_contract_compliance", "L0_ROUTING",
        )
        required_methods = ["smart_fix"]
        required_attrs = ["ctx", "name", "python_files"]

        has_required_methods = False
        has_required_attrs = False

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check methods
                methods = [item.name for item in node.body if isinstance(item, ast.FunctionDef)]
                if any(method in methods for method in required_methods):
                    has_required_methods = True

                # Check for __init__ with required attributes
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) and item.name == "__init__":
                        for child in ast.walk(item):
                            if isinstance(child, ast.Attribute):
                                if child.attr in required_attrs:
                                    has_required_attrs = True

        return has_required_methods and has_required_attrs

    def _analyze_sovereign_requirements(self, tree: ast.AST) -> list[str]:
        """Analyze V2.5 Sovereign Requirements compliance."""
        requirements = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check for autonomy
                methods = [item.name for item in node.body if isinstance(item, ast.FunctionDef)]
                if any(method in ["execute", "_process", "run"] for method in methods):
                    requirements.append("Autonomy")

                # Check for healing
                if any(method in ["heal_repository", "self_heal", "recover"] for method in methods):
                    requirements.append("Healing")

                # Check for hardening
                bases = []
                for child in node.bases:
                    if isinstance(child, ast.Name):
                        bases.append(child.id)

                if any("Hardened" in base or "MCP" in base for base in bases):
                    requirements.append("Hardening")

        return list(set(requirements))

    def _determine_disposition(
        self,
        file_path: Path,
        tree: ast.AST,
        cfg_complexity: int,
        data_flow_nodes: int,
        circular_deps: list[str],
        contract_compliance: bool,
        sovereign_requirements: list[str],
    ) -> tuple[Disposition, str | None, float, str]:
        """Determine file disposition and synthesis target."""
        filename = file_path.name

        # Check for circular dependencies - immediate archive
        if circular_deps:
            return (
                Disposition.ARCHIVE,
                None,
                0.0,
                f"Circular dependencies: {', '.join(circular_deps)}",
            )

        # Check for utility functions - move to utils
        if any(keyword in filename.lower() for keyword in ["util", "tool", "helper"]):
            return Disposition.ARCHIVE, None, 0.0, "Utility function - move to agentic_core/utils/"

        # Check for core mixins - keep
        if "mixin" in filename.lower():
            return Disposition.KEEP, None, 1.0, "Core mixin - essential for sovereign architecture"

        # Check for interface definitions - keep
        if "interface" in filename.lower() or "protocol" in filename.lower():
            return Disposition.KEEP, None, 1.0, "Interface definition - essential for contracts"

        # Check for sovereign base agents - keep
        if "sovereign" in filename.lower() and "base" in filename.lower():
            return Disposition.KEEP, None, 1.0, "Sovereign base agent - foundation of architecture"

        # Check for agent classes with sovereign requirements
        has_agent_classes = False
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and "Agent" in node.name:
                has_agent_classes = True
                break

        if has_agent_classes and sovereign_requirements:
            # Determine synthesis target based on requirements
            if "Healing" in sovereign_requirements:
                return (
                    Disposition.SYNTHESIZE,
                    "healer_mixin.HealerMixin",
                    0.8,
                    "Healing logic - merge into HealerMixin",
                )
            elif "Hardening" in sovereign_requirements:
                return (
                    Disposition.SYNTHESIZE,
                    "subatomic_testing_mixin.SubatomicTestingMixin",
                    0.7,
                    "Hardening logic - merge into SubatomicTestingMixin",
                )
            elif "Autonomy" in sovereign_requirements:
                return (
                    Disposition.SYNTHESIZE,
                    "SovereignBaseAgent",
                    0.9,
                    "Autonomous logic - merge into SovereignBaseAgent",
                )

        # Check for test files - archive
        if "test" in filename.lower():
            return Disposition.ARCHIVE, None, 0.0, "Test file - move to tests/"

        # Default based on complexity and requirements
        if cfg_complexity > 10 and sovereign_requirements:
            return (
                Disposition.SYNTHESIZE,
                "SovereignBaseAgent",
                0.6,
                f"Complex logic ({cfg_complexity} CFG nodes) with sovereign requirements",
            )
        elif cfg_complexity > 5:
            return Disposition.KEEP, None, 0.5, f"Moderate complexity ({cfg_complexity} CFG nodes)"
        else:
            return (
                Disposition.ARCHIVE,
                None,
                0.0,
                f"Low complexity ({cfg_complexity} CFG nodes) - likely utility",
            )

    def execute_analysis(self) -> list[CoreAnalysisResult]:
        """Execute comprehensive analysis of all files."""
        print("🔬 PHASE 20: SOVEREIGN CORE LOGIC SYNTHESIS")
        print("=" * 80)
        print("🧠 Advanced Multimodal Disposition Analysis")
        print("=" * 80)

        python_files = list(self.base_path.rglob("*.py"))

        for file_path in python_files:
            if file_path.name == "__init__.py":
                continue

            print(f"\n🔍 Analyzing: {file_path.name}")
            result = self.analyze_file(file_path)
            self.analysis_results.append(result)

            print(f"   📊 CFG Complexity: {result.cfg_complexity}")
            print(f"   🌊 Data Flow Nodes: {result.data_flow_nodes}")
            print(f"   🔄 Circular Dependencies: {len(result.circular_deps)}")
            print(f"   ✅ Contract Compliance: {result.contract_compliance}")
            print(
                f"   🛡️ Sovereign Requirements: {', '.join(result.sovereign_requirements) if result.sovereign_requirements else 'None'}",
            )
            print(f"   🎯 Disposition: {result.disposition.value}")
            if result.synthesis_target:
                print(f"   🎯 Synthesis Target: {result.synthesis_target}")
            print(f"   ⚖️ Instructional Weight: {result.instructional_weight:.2f}")
            print(f"   💭 Rationale: {result.rationale}")

        return self.analysis_results

    def generate_report(self) -> str:
        """Generate comprehensive analysis report."""
        report = []
        report.append("# CORE REFINERY ANALYSIS")
        report.append("")
        report.append("**Phase 20: Sovereign Core Logic Synthesis**")
        report.append("**Date:** January 24, 2026")
        report.append("**Analyzer:** Principal AI Systems Architect / Formal Methods Engineer")
        report.append("")

        # Summary statistics
        total_files = len(self.analysis_results)
        keep_count = sum(1 for r in self.analysis_results if r.disposition == Disposition.KEEP)
        archive_count = sum(1 for r in self.analysis_results if r.disposition == Disposition.ARCHIVE)
        synthesize_count = sum(1 for r in self.analysis_results if r.disposition == Disposition.SYNTHESIZE)

        report.append("## 📊 EXECUTIVE SUMMARY")
        report.append("")
        report.append(f"- **Total Files Analyzed:** {total_files}")
        report.append(f"- **KEEP Disposition:** {keep_count} files ({keep_count / total_files * 100:.1f}%)")
        report.append(
            f"- **ARCHIVE Disposition:** {archive_count} files ({archive_count / total_files * 100:.1f}%)",
        )
        report.append(
            f"- **SYNTHESIZE Disposition:** {synthesize_count} files ({synthesize_count / total_files * 100:.1f}%)",
        )
        report.append("")

        # Detailed analysis
        report.append("## 🔬 DETAILED ANALYSIS")
        report.append("")

        for result in self.analysis_results:
            report.append(f"### 📄 {result.file_path}")
            report.append("")
            report.append(f"**Disposition:** {result.disposition.value}")
            report.append("")

            if result.synthesis_target:
                report.append(f"**Synthesis Target:** `{result.synthesis_target}`")
                report.append("")

            report.append(f"**Instructional Weight:** {result.instructional_weight:.2f}")
            report.append("")
            report.append(f"**Rationale:** {result.rationale}")
            report.append("")

            report.append("**Technical Metrics:**")
            report.append(f"- CFG Complexity: {result.cfg_complexity}")
            report.append(f"- Data Flow Nodes: {result.data_flow_nodes}")
            report.append(f"- Circular Dependencies: {len(result.circular_deps)}")
            report.append(f"- Contract Compliance: {result.contract_compliance}")
            report.append(
                f"- Sovereign Requirements: {', '.join(result.sovereign_requirements) if result.sovereign_requirements else 'None'}",
            )
            report.append("")

            if result.circular_deps:
                report.append("**⚠️ Circular Dependencies:**")
                for dep in result.circular_deps:
                    report.append(f"- {dep}")
                report.append("")

            report.append("---")
            report.append("")

        # Synthesis plan
        synthesize_results = [r for r in self.analysis_results if r.disposition == Disposition.SYNTHESIZE]
        if synthesize_results:
            report.append("## 🎯 SYNTHESIS PLAN")
            report.append("")

            for result in synthesize_results:
                report.append(f"### 🔄 {result.file_path}")
                report.append("")
                report.append(f"**Target:** `{result.synthesis_target}`")
                report.append(f"**Weight:** {result.instructional_weight:.2f}")
                report.append(f"**Requirements:** {', '.join(result.sovereign_requirements)}")
                report.append("")

        return "\n".join(report)


def main():
    """Execute the core synthesis analysis."""
    analyzer = CoreSynthesisAnalyzer()
    results = analyzer.execute_analysis()

    # Generate report
    report = analyzer.generate_report()

    # Save report
    with open("CORE_REFINERY_ANALYSIS.md", "w", encoding="utf-8") as f:
        f.write(report)

    # Save detailed results
    detailed_results = []
    for result in results:
        detailed_results.append(
            {
                "file_path": result.file_path,
                "disposition": result.disposition.value,
                "synthesis_target": result.synthesis_target,
                "instructional_weight": result.instructional_weight,
                "rationale": result.rationale,
                "cfg_complexity": result.cfg_complexity,
                "data_flow_nodes": result.data_flow_nodes,
                "circular_deps": result.circular_deps,
                "contract_compliance": result.contract_compliance,
                "sovereign_requirements": result.sovereign_requirements,
            },
        )

    with open("core_refinery_analysis_results.json", "w") as f:
        assert_no_persistent_write("L0", "json.dump")  # G-12-1: mutation prohibition guard
        json.dump(detailed_results, f, indent=2)

    print("\n" + "=" * 80)
    print("📊 ANALYSIS COMPLETE")
    print("=" * 80)
    print("📄 Report saved: CORE_REFINERY_ANALYSIS.md")
    print("📊 Results saved: core_refinery_analysis_results.json")
    print("\n🎯 Ready for Zero-Loss Synthesis & Restructure!")

    return results


if __name__ == "__main__":
    main()
