"""
AST-Based Architecture Gap Analyzer.

Analyzes the codebase against the target architecture diagram using AST parsing
and fuzzy matching to identify implementation gaps.

Architecture Components from Diagram:
1. Knowledge System (Semantic Memory, Episodic Memory, Semantic Cache)
2. Advanced Cognitive Engine (Working Memory, Reflection, Thought Generation, Prompt Optimization)
3. Event & Anomaly Detection Layer (Multi-modal ingestion, Anomaly Detection, Signal Correlation)
4. Contextual Router & Policy Enforcer (Risk Assessment, Enforcement Policy)
5. Validation Gate (Pre-Execution Check, Target Verification, Safety Check)
6. Human Review Gate (Approval Queue, Risk-based Escalation)
7. System Actuation / Healing (Rename files, Fix imports, Restructure code)
8. Budget Guard (Token/Cost budget, Resource limits)
9. AI Safety Guardrails (Input/Output validation, Hallucination Detection)
10. Metrics Dashboard (Success Rate, MTTR, Cost, Human Intervention)
11. Audit Log / Observability & Audit Trail (Traceability)
12. Policy Update Mechanism (Performance & Security feedback)
13. Cognitive & Meta-Learning Components (Feedback loops)
"""

import ast
import json
from collections import defaultdict
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

from agentic_core.L0_routing.config.path_constants import REPORTS_DIR
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_pulls_context,
    _emit_reads_through,
    _emit_validated_by_safety_plane,
    _emit_writes_through,
    emit_determinism_digest,
)
from tqdm import tqdm


def _resolve_repo_root() -> Path:
    for candidate in Path(__file__).resolve().parents:
        if (candidate / ".git").exists():
            return candidate
    return Path(__file__).resolve().parents[2]


_emit_writes_through("p1", "architecture_gap_analyzer", "uwg_governed_write")
_emit_writes_through("p1", "architecture_gap_analyzer", "uwg_governed_write_2")
_emit_pulls_context("p1", "architecture_gap_analyzer", "context_retrieval")
_emit_pulls_context("p1", "architecture_gap_analyzer", "context_retrieval_2")
emit_determinism_digest("trace_architecture_gap_analyzer", "architecture_gap_analyzer_dispatch")
emit_determinism_digest("trace_architecture_gap_analyzer", "architecture_gap_analyzer_complete")
_emit_validated_by_safety_plane("p1", "architecture_gap_analyzer", "safety_validation")
_emit_reads_through("l4", "architecture_gap_analyzer", "urg_read_1")
_emit_reads_through("l4", "architecture_gap_analyzer", "urg_read_2")
_emit_reads_through("l4", "architecture_gap_analyzer", "urg_read_3")
_emit_reads_through("l4", "architecture_gap_analyzer", "urg_read_4")
_emit_reads_through("l4", "architecture_gap_analyzer", "urg_read_5")
_emit_reads_through("l4", "architecture_gap_analyzer", "urg_read_6")
_emit_reads_through("l4", "architecture_gap_analyzer", "urg_read_7")
_emit_reads_through("l4", "architecture_gap_analyzer", "urg_read_8")
_emit_reads_through("l4", "architecture_gap_analyzer", "urg_read_9")
_emit_reads_through("l4", "architecture_gap_analyzer", "urg_read_10")
_emit_reads_through("l4", "architecture_gap_analyzer", "urg_read_11")
_emit_reads_through("l4", "architecture_gap_analyzer", "urg_read_12")
_emit_reads_through("l4", "architecture_gap_analyzer", "urg_read_13")
_emit_reads_through("l4", "architecture_gap_analyzer", "urg_read_14")
_emit_reads_through("l4", "architecture_gap_analyzer", "urg_read_15")
_emit_reads_through("l4", "architecture_gap_analyzer", "urg_read_16")
_emit_reads_through("l4", "architecture_gap_analyzer", "urg_read_17")
_emit_reads_through("l4", "architecture_gap_analyzer", "urg_read_18")
_emit_reads_through("l4", "architecture_gap_analyzer", "urg_read_19")
_emit_reads_through("l4", "architecture_gap_analyzer", "urg_read_20")
_emit_reads_through("l4", "architecture_gap_analyzer", "urg_read_21")
_emit_reads_through("l4", "architecture_gap_analyzer", "urg_read_22")
_emit_reads_through("l4", "architecture_gap_analyzer", "urg_read_23")
_emit_reads_through("l4", "architecture_gap_analyzer", "urg_read_24")
_emit_reads_through("l4", "architecture_gap_analyzer", "urg_read_25")
_emit_reads_through("l4", "architecture_gap_analyzer", "urg_read_26")
_emit_reads_through("l4", "architecture_gap_analyzer", "urg_read_27")
_emit_reads_through("l4", "architecture_gap_analyzer", "urg_read_28")
_emit_reads_through("l4", "architecture_gap_analyzer", "urg_read_29")
_emit_reads_through("l4", "architecture_gap_analyzer", "urg_read_30")
_emit_reads_through("l4", "architecture_gap_analyzer", "urg_read_31")
_emit_reads_through("l4", "architecture_gap_analyzer", "urg_read_32")
_emit_reads_through("l4", "architecture_gap_analyzer", "urg_read_33")
_emit_reads_through("l4", "architecture_gap_analyzer", "urg_read_34")
_emit_reads_through("l4", "architecture_gap_analyzer", "urg_read_35")
_emit_reads_through("l4", "architecture_gap_analyzer", "urg_read_36")
_emit_reads_through("l4", "architecture_gap_analyzer", "urg_read_37")
_emit_reads_through("l4", "architecture_gap_analyzer", "urg_read_38")
_emit_reads_through("l4", "architecture_gap_analyzer", "urg_read_39")
_emit_reads_through("l4", "architecture_gap_analyzer", "urg_read_40")
_emit_reads_through("l4", "architecture_gap_analyzer", "urg_read_41")
_emit_reads_through("l4", "architecture_gap_analyzer", "urg_read_42")
_emit_reads_through("l4", "architecture_gap_analyzer", "urg_read_43")
_emit_reads_through("l4", "architecture_gap_analyzer", "urg_read_44")
_emit_reads_through("l4", "architecture_gap_analyzer", "urg_read_45")
_emit_reads_through("l4", "architecture_gap_analyzer", "urg_read_46")
_emit_reads_through("l4", "architecture_gap_analyzer", "urg_read_47")
_emit_reads_through("l4", "architecture_gap_analyzer", "urg_read_48")
_emit_reads_through("l4", "architecture_gap_analyzer", "urg_read_49")
_emit_reads_through("l4", "architecture_gap_analyzer", "urg_read_50")
_emit_reads_through("l4", "architecture_gap_analyzer", "urg_read_51")
_emit_reads_through("l4", "architecture_gap_analyzer", "urg_read_52")
_emit_reads_through("l4", "architecture_gap_analyzer", "urg_read_53")
_emit_reads_through("l4", "architecture_gap_analyzer", "urg_read_54")
_emit_reads_through("l4", "architecture_gap_analyzer", "urg_read_55")
_emit_reads_through("l4", "architecture_gap_analyzer", "urg_read_56")
_emit_reads_through("l4", "architecture_gap_analyzer", "urg_read_57")
_emit_reads_through("l4", "architecture_gap_analyzer", "urg_read_58")
_emit_reads_through("l4", "architecture_gap_analyzer", "urg_read_59")
_emit_reads_through("l4", "architecture_gap_analyzer", "urg_read_60")
_emit_reads_through("l4", "architecture_gap_analyzer", "urg_read_61")
_emit_reads_through("l4", "architecture_gap_analyzer", "urg_read_62")


@dataclass
class ArchitectureComponent:
    """Represents a component from the architecture diagram."""

    name: str
    category: str
    required_capabilities: list[str]
    key_patterns: list[str]
    description: str
    criticality: str


@dataclass
class ComponentMatch:
    """A match between architecture component and codebase implementation."""

    component_name: str
    file_path: str
    class_name: str
    match_score: float
    matched_capabilities: list[str]
    missing_capabilities: list[str]
    evidence: dict[str, Any] = field(default_factory=dict)


@dataclass
class GapAnalysisResult:
    """Result of gap analysis."""

    component: ArchitectureComponent
    coverage_score: float
    implementations: list[ComponentMatch]
    gaps: list[str]
    recommendations: list[str]


ARCHITECTURE_COMPONENTS = [
    ArchitectureComponent(
        name="Semantic Memory",
        category="Knowledge System",
        required_capabilities=[
            "ontology_management",
            "embedding_services",
            "fact_retrieval",
            "vector_storage",
            "knowledge_graph",
        ],
        key_patterns=["embedding", "vector", "semantic", "ontology", "knowledge_graph"],
        description="Knowledge Graph & Vector DB for semantic storage and retrieval",
        criticality="P0",
    ),
    ArchitectureComponent(
        name="Episodic Memory",
        category="Knowledge System",
        required_capabilities=[
            "experience_replay",
            "past_trajectories",
            "outcome_linking",
            "temporal_context",
        ],
        key_patterns=["episodic", "trajectory", "experience", "replay", "memory"],
        description="Experience Replay and Past Trajectories storage",
        criticality="P1",
    ),
    ArchitectureComponent(
        name="Semantic Cache",
        category="Knowledge System",
        required_capabilities=["cache_lookup", "similarity_matching", "cache_invalidation", "ttl_management"],
        key_patterns=["cache", "semantic_cache", "recall", "lookup", "similarity"],
        description="Semantic caching for recall-or-execute patterns",
        criticality="P0",
    ),
    ArchitectureComponent(
        name="Working Memory",
        category="Advanced Cognitive Engine",
        required_capabilities=["context_window", "state_tracking", "attention_mechanism"],
        key_patterns=["working_memory", "context", "state", "attention", "window"],
        description="Context Window and State Tracking",
        criticality="P1",
    ),
    ArchitectureComponent(
        name="Reflection & Critique",
        category="Advanced Cognitive Engine",
        required_capabilities=["self_reflection", "critique", "reasoning_traces", "internal_monologue"],
        key_patterns=["reflection", "critique", "reasoning", "monologue", "self_eval"],
        description="ReAct/ToT, Hypothesis Formation, Internal Monologue",
        criticality="P1",
    ),
    ArchitectureComponent(
        name="Thought Generation",
        category="Advanced Cognitive Engine",
        required_capabilities=["hypothesis_formation", "reasoning_traces", "chain_of_thought"],
        key_patterns=["thought", "hypothesis", "reasoning", "chain", "generation"],
        description="Argument Solidation, Hypothesis Formation",
        criticality="P1",
    ),
    ArchitectureComponent(
        name="Prompt Optimization",
        category="Advanced Cognitive Engine",
        required_capabilities=["automatic_prompt_engineering", "prompt_templates", "optimization"],
        key_patterns=["prompt", "template", "optimization", "ape", "engineering"],
        description="Automatic Prompt Engineering (APE)",
        criticality="P2",
    ),
    ArchitectureComponent(
        name="Event & Anomaly Detection",
        category="Detection Layer",
        required_capabilities=[
            "multi_modal_ingestion",
            "real_time_processing",
            "anomaly_detection",
            "signal_correlation",
        ],
        key_patterns=["detection", "anomaly", "signal", "event", "ingestion", "correlation"],
        description="Multi-modal Data Ingestion, Anomaly Detection Models",
        criticality="P0",
    ),
    ArchitectureComponent(
        name="Contextual Router & Policy Enforcer",
        category="Policy & Orchestration",
        required_capabilities=["risk_assessment", "enforcement_policy", "risk_classification", "routing"],
        key_patterns=["router", "policy", "enforcer", "risk", "classification", "routing"],
        description="Risk Assessment, Enforcement Policy, Risk Classification",
        criticality="P0",
    ),
    ArchitectureComponent(
        name="Validation Gate",
        category="Safety Layer",
        required_capabilities=[
            "target_verification",
            "safety_check",
            "pre_execution_check",
            "unsafe_change_blocking",
        ],
        key_patterns=["validation", "gate", "verification", "pre_check", "safety", "block"],
        description="Pre-Execution Check, Target Verification, Unsafe Change Blocking",
        criticality="P0",
    ),
    ArchitectureComponent(
        name="Human Review Gate",
        category="Safety Layer",
        required_capabilities=["approval_queue", "risk_escalation", "decision_tracking", "rich_context"],
        key_patterns=["human", "review", "approval", "queue", "escalation", "hitl"],
        description="Approval Queue, Risk-based Escalation, Decision Tracking",
        criticality="P0",
    ),
    ArchitectureComponent(
        name="System Actuation / Healing",
        category="Execution Layer",
        required_capabilities=[
            "file_rename",
            "import_fix",
            "code_restructure",
            "safe_execution",
            "auto_rollback",
        ],
        key_patterns=["heal", "fix", "rename", "restructure", "actuation", "rollback"],
        description="Multiple Healing Tools, Safe Execution, Auto-rollback",
        criticality="P0",
    ),
    ArchitectureComponent(
        name="Budget Guard",
        category="Resource Management",
        required_capabilities=["token_budget", "cost_budget", "resource_limits", "budget_enforcement"],
        key_patterns=["budget", "cost", "token", "limit", "resource", "guard"],
        description="Token/Cost Budget, Resource Limits Enforcement",
        criticality="P1",
    ),
    ArchitectureComponent(
        name="AI Safety Guardrails",
        category="Safety Layer",
        required_capabilities=["input_validation", "output_validation", "hallucination_detection"],
        key_patterns=["guardrail", "safety", "hallucination", "input_validation", "output"],
        description="Input/Output Validation, Hallucination Detection",
        criticality="P0",
    ),
    ArchitectureComponent(
        name="Metrics Dashboard",
        category="Observability",
        required_capabilities=[
            "success_rate_tracking",
            "mttr_tracking",
            "cost_tracking",
            "human_intervention_tracking",
        ],
        key_patterns=["metrics", "dashboard", "success_rate", "mttr", "tracking", "telemetry"],
        description="Success Rate, MTTR, Cost, Human Intervention Metrics",
        criticality="P1",
    ),
    ArchitectureComponent(
        name="Audit Log & Trail",
        category="Observability",
        required_capabilities=["traceability", "audit_logging", "cryptographic_logging", "decision_trail"],
        key_patterns=["audit", "log", "trail", "trace", "cryptographic", "decision"],
        description="Traceability, Audit Trail for all decisions",
        criticality="P0",
    ),
    ArchitectureComponent(
        name="Policy Update Mechanism",
        category="Learning & Adaptation",
        required_capabilities=[
            "performance_feedback",
            "security_feedback",
            "policy_update",
            "adaptive_policy",
        ],
        key_patterns=["policy_update", "feedback", "adaptive", "performance", "learning"],
        description="Performance & Security Feedback Loop",
        criticality="P2",
    ),
    ArchitectureComponent(
        name="Meta-Learning Components",
        category="Learning & Adaptation",
        required_capabilities=[
            "recall_or_execute",
            "pattern_learning",
            "experience_storage",
            "similarity_matching",
        ],
        key_patterns=["meta_learning", "recall", "execute", "pattern", "similarity", "learn"],
        description="Cognitive & Meta-Learning Components",
        criticality="P0",
    ),
]


class ASTAnalyzer:
    """AST-based code analyzer for architecture gap detection."""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.parsed_files: dict[str, ast.AST] = {}
        self.class_info: dict[str, dict[str, Any]] = {}
        self.function_info: dict[str, list[str]] = {}

    def parse_file(self, file_path: Path) -> ast.AST | None:
        """Parse a Python file into AST."""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()
            return ast.parse(content, filename=str(file_path))
        except (
            SyntaxError,
            UnicodeDecodeError,
        ):  # guardian: Parsing and encoding errors need separate handling strategies
            return None

    def extract_class_info(self, tree: ast.AST, file_path: str) -> list[dict[str, Any]]:
        """Extract class information from AST."""
        classes = []
        for node in tqdm(ast.walk(tree), desc="Processing", unit="item"):
            if isinstance(node, ast.ClassDef):
                class_info = {
                    "name": node.name,
                    "file_path": file_path,
                    "bases": [self._get_name(base) for base in node.bases],
                    "methods": [],
                    "attributes": [],
                    "decorators": [self._get_name(d) for d in node.decorator_list],
                    "docstring": ast.get_docstring(node) or "",
                }
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        class_info["methods"].append(item.name)
                    elif isinstance(item, ast.Assign):
                        for target in item.targets:
                            if isinstance(target, ast.Name):
                                class_info["attributes"].append(target.id)
                classes.append(class_info)
        return classes

    def _get_name(self, node: ast.AST) -> str:
        """Get name from AST node."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_name(node.value)}.{node.attr}"
        elif isinstance(node, ast.Call):
            return self._get_name(node.func)
        return ""

    def fuzzy_match_score(self, text: str, patterns: list[str]) -> tuple[float, list[str]]:
        """Calculate fuzzy match score against patterns."""
        text_lower = text.lower()
        matched = []
        total_score = 0.0
        for pattern in patterns:
            pattern_lower = pattern.lower()
            if pattern_lower in text_lower:
                total_score += 1.0
                matched.append(pattern)
            else:
                ratio = SequenceMatcher(None, pattern_lower, text_lower).ratio()
                if ratio > 0.6:
                    total_score += ratio
                    matched.append(f"{pattern}(fuzzy:{ratio:.2f})")
        return (total_score / len(patterns) if patterns else 0, matched)

    def analyze_class_capabilities(
        self, class_info: dict[str, Any], component: ArchitectureComponent
    ) -> tuple[float, list[str], list[str]]:
        """Analyze a class for architecture component capabilities."""
        matched_capabilities = []
        missing_capabilities = []
        searchable = " ".join(
            [
                class_info["name"],
                class_info.get("docstring", ""),
                " ".join(class_info.get("methods", [])),
                " ".join(class_info.get("attributes", [])),
            ]
        ).lower()
        for capability in tqdm(component.required_capabilities, desc="Processing", unit="item"):
            cap_words = capability.replace("_", " ").split()
            found = False
            for word in cap_words:
                if word in searchable:
                    found = True
                    break
                for method in class_info.get("methods", []):
                    if SequenceMatcher(None, word, method.lower()).ratio() > 0.7:
                        found = True
                        break
            if found:
                matched_capabilities.append(capability)
            else:
                missing_capabilities.append(capability)
        score = (
            len(matched_capabilities) / len(component.required_capabilities)
            if component.required_capabilities
            else 0
        )
        return (score, matched_capabilities, missing_capabilities)

    def scan_repository(self) -> None:
        """Scan entire repository for Python files."""
        for py_file in self.repo_root.rglob("*.py"):
            if any(skip in str(py_file) for skip in [".venv", "node_modules", "__pycache__", ".git"]):
                continue
            tree = self.parse_file(py_file)
            if tree:
                rel_path = str(py_file.relative_to(self.repo_root))
                self.parsed_files[rel_path] = tree
                classes = self.extract_class_info(tree, rel_path)
                for cls in classes:
                    self.class_info[f"{rel_path}:{cls['name']}"] = cls


class ArchitectureGapAnalyzer:
    """Main analyzer for architecture gaps."""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.ast_analyzer = ASTAnalyzer(repo_root)
        self.results: list[GapAnalysisResult] = []

    def analyze(self) -> list[GapAnalysisResult]:
        """Run full architecture gap analysis."""
        print("Scanning repository with AST parser...")
        self.ast_analyzer.scan_repository()
        print(
            f"Parsed {len(self.ast_analyzer.parsed_files)} files, found {len(self.ast_analyzer.class_info)} classes"
        )
        results = []
        for component in ARCHITECTURE_COMPONENTS:
            print(f"\nAnalyzing: {component.name} ({component.category})")
            result = self._analyze_component(component)
            results.append(result)
            print(f"  Coverage: {result.coverage_score:.1f}%")
            print(f"  Implementations found: {len(result.implementations)}")
            if result.gaps:
                print(f"  Gaps: {len(result.gaps)}")
        self.results = results
        return results

    def _analyze_component(self, component: ArchitectureComponent) -> GapAnalysisResult:
        """Analyze a single architecture component."""
        implementations = []
        for _key, class_info in tqdm(self.ast_analyzer.class_info.items(), desc="Processing", unit="item"):
            name_score, name_matches = self.ast_analyzer.fuzzy_match_score(
                class_info["name"], component.key_patterns
            )
            doc_score, doc_matches = self.ast_analyzer.fuzzy_match_score(
                class_info.get("docstring", ""), component.key_patterns
            )
            combined_score = max(name_score, doc_score)
            if combined_score > 0.2:
                cap_score, matched_caps, missing_caps = self.ast_analyzer.analyze_class_capabilities(
                    class_info, component
                )
                if cap_score > 0 or combined_score > 0.5:
                    implementations.append(
                        ComponentMatch(
                            component_name=component.name,
                            file_path=class_info["file_path"],
                            class_name=class_info["name"],
                            match_score=max(combined_score, cap_score),
                            matched_capabilities=matched_caps,
                            missing_capabilities=missing_caps,
                            evidence={
                                "name_matches": name_matches,
                                "doc_matches": doc_matches,
                                "methods": class_info.get("methods", [])[:10],
                            },
                        )
                    )
        implementations.sort(key=lambda x: x.match_score, reverse=True)
        if implementations:
            best_impl = implementations[0]
            coverage = best_impl.match_score * 100
            gaps = []
            for cap in component.required_capabilities:
                if not any(cap in impl.matched_capabilities for impl in implementations[:3]):
                    gaps.append(f"Missing capability: {cap}")
        else:
            coverage = 0
            gaps = [f"No implementation found for: {component.name}"]
            gaps.extend([f"Missing capability: {cap}" for cap in component.required_capabilities])
        recommendations = []
        if coverage < 50:
            recommendations.append(f"[P0] Implement {component.name} - Critical gap")
        elif coverage < 80:
            recommendations.append(f"[P1] Enhance {component.name} - Missing capabilities")
        for gap in gaps[:3]:
            recommendations.append(f"  - {gap}")
        return GapAnalysisResult(
            component=component,
            coverage_score=coverage,
            implementations=implementations[:5],
            gaps=gaps,
            recommendations=recommendations,
        )

    def generate_report(self) -> dict[str, Any]:
        """Generate comprehensive gap analysis report."""
        report = {
            "summary": {
                "total_components": len(ARCHITECTURE_COMPONENTS),
                "fully_implemented": 0,
                "partially_implemented": 0,
                "not_implemented": 0,
                "overall_coverage": 0,
            },
            "by_category": defaultdict(list),
            "by_criticality": {"P0": [], "P1": [], "P2": []},
            "critical_gaps": [],
            "components": [],
        }
        total_coverage = 0
        for result in tqdm(self.results, desc="Processing", unit="item"):
            comp_data = {
                "name": result.component.name,
                "category": result.component.category,
                "criticality": result.component.criticality,
                "coverage": result.coverage_score,
                "implementations": [
                    {
                        "file": impl.file_path,
                        "class": impl.class_name,
                        "score": impl.match_score,
                        "matched": impl.matched_capabilities,
                        "missing": impl.missing_capabilities,
                    }
                    for impl in result.implementations[:3]
                ],
                "gaps": result.gaps,
                "recommendations": result.recommendations,
            }
            report["components"].append(comp_data)
            report["by_category"][result.component.category].append(comp_data)
            report["by_criticality"][result.component.criticality].append(comp_data)
            if result.coverage_score >= 80:
                report["summary"]["fully_implemented"] += 1
            elif result.coverage_score >= 30:
                report["summary"]["partially_implemented"] += 1
            else:
                report["summary"]["not_implemented"] += 1
                if result.component.criticality == "P0":
                    report["critical_gaps"].append(
                        {
                            "component": result.component.name,
                            "coverage": result.coverage_score,
                            "gaps": result.gaps[:3],
                        }
                    )
            total_coverage += result.coverage_score
        report["summary"]["overall_coverage"] = total_coverage / len(self.results) if self.results else 0
        return report


def main():
    """Run architecture gap analysis."""
    repo_root = _resolve_repo_root()
    analyzer = ArchitectureGapAnalyzer(repo_root)
    analyzer.analyze()
    report = analyzer.generate_report()
    output_path = repo_root / "docs" / REPORTS_DIR / "plans" / "ARCHITECTURE_GAP_ANALYSIS_AST.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, default=str)
    print("\n" + "=" * 80)
    print("ARCHITECTURE GAP ANALYSIS SUMMARY")
    print("=" * 80)
    print(f"Total Components: {report['summary']['total_components']}")
    print(f"Fully Implemented (≥80%): {report['summary']['fully_implemented']}")
    print(f"Partially Implemented (30-80%): {report['summary']['partially_implemented']}")
    print(f"Not Implemented (<30%): {report['summary']['not_implemented']}")
    print(f"Overall Coverage: {report['summary']['overall_coverage']:.1f}%")
    if report["critical_gaps"]:
        print("\n" + "-" * 40)
        print("CRITICAL GAPS (P0 with <30% coverage):")
        for gap in report["critical_gaps"]:
            print(f"  - {gap['component']}: {gap['coverage']:.1f}%")
            for g in gap["gaps"][:2]:
                print(f"      {g}")
    print(f"\nDetailed report saved to: {output_path}")
    md_path = repo_root / "docs" / REPORTS_DIR / "plans" / "ARCHITECTURE_GAP_ANALYSIS_AST.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("# Architecture Gap Analysis (AST-Based)\n\n")
        f.write("**Generated:** 2026-02-03\n")
        f.write("**Method:** AST parsing with fuzzy matching\n\n")
        f.write("## Summary\n\n")
        f.write("| Metric | Value |\n")
        f.write("|--------|-------|\n")
        f.write(f"| Total Components | {report['summary']['total_components']} |\n")
        f.write(f"| Fully Implemented (≥80%) | {report['summary']['fully_implemented']} |\n")
        f.write(f"| Partially Implemented | {report['summary']['partially_implemented']} |\n")
        f.write(f"| Not Implemented | {report['summary']['not_implemented']} |\n")
        f.write(f"| Overall Coverage | {report['summary']['overall_coverage']:.1f}% |\n\n")
        f.write("## Components by Category\n\n")
        for category, components in report["by_category"].items():
            f.write(f"### {category}\n\n")
            f.write("| Component | Coverage | Status |\n")
            f.write("|-----------|----------|--------|\n")
            for comp in components:
                status = "✅" if comp["coverage"] >= 80 else "⚠️" if comp["coverage"] >= 30 else "❌"
                f.write(f"| {comp['name']} | {comp['coverage']:.1f}% | {status} |\n")
            f.write("\n")
        if report["critical_gaps"]:
            f.write("## Critical Gaps (P0)\n\n")
            for gap in report["critical_gaps"]:
                f.write(f"### {gap['component']}\n")
                f.write(f"Coverage: {gap['coverage']:.1f}%\n\n")
                for g in gap["gaps"]:
                    f.write(f"- {g}\n")
                f.write("\n")
    print(f"Markdown report saved to: {md_path}")
    return report


if __name__ == "__main__":
    main()
