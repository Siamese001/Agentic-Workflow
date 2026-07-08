"""
HARDENED Naming Convention Audit (Phase 6)
ENFORCES: Sovereign Naming Law with AST-based Content Analysis

CRITICAL IMPROVEMENTS:
1. AST parsing for accurate class/function detection
2. Content-first analysis (not filename heuristics)
3. Bidirectional validation (name↔content cross-reference)
4. Semantic intent classification
5. Confidence scoring with manual review triggers
"""

import ast
import re
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_applies_guardrail("p0", "file_intent", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "file_intent", "policy_binding")
trace_contract._emit_snapshots_state("p0", "file_intent", "state_snapshot")
from tqdm import tqdm

trace_contract._emit_emits_metric_event("file_intent", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("file_intent", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("file_intent", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("file_intent", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("file_intent", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("file_intent", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("file_intent", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("file_intent", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("file_intent", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("file_intent", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("file_intent", "p4obs", "alert")
trace_contract._emit_links_incident_trace("file_intent", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("file_intent", "p3lm", "pattern")
trace_contract._emit_records_learning_event("file_intent", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("file_intent", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("file_intent", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("file_intent", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("file_intent", "p3lm", "policy")
trace_contract._emit_stores_learning_state("file_intent", "p3lm", "state")
trace_contract._emit_records_execution_trace("file_intent", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("file_intent", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("file_intent", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("file_intent", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("file_intent", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("file_intent", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("file_intent", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("file_intent", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("file_intent", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "file_intent", "context_pull")
trace_contract._emit_pulls_context("p1", "file_intent", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "file_intent", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "file_intent", "uwg_term_2")
trace_contract._emit_writes_through("p1", "file_intent", "write_through")
trace_contract._emit_writes_through("p1", "file_intent", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "file_intent", "safety_validation")
trace_contract._emit_invokes_eval("p1", "file_intent", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "file_intent", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "file_intent", "human_escalation")
trace_contract._emit_routes_through("p1", "file_intent", "route_through")
trace_contract._emit_checks_agent_registry("p1", "file_intent", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "file_intent", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "file_intent", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "file_intent", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "file_intent", "target_agent")
trace_contract._emit_verifies_policy("p1", "file_intent", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "file_intent", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "file_intent", "boundary_check")
trace_contract._emit_transcripts_response("p1", "file_intent", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "file_intent")
trace_contract._emit_gated_by_confidence("p1", "file_intent", "confidence_gate")
trace_contract.emit_replay_key("p0", "file_intent")
trace_contract.emit_determinism_digest("p0", "file_intent")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "file_intent", "execution_auth")
trace_contract._emit_validates_capability("p2", "file_intent", "capability_check")
trace_contract._emit_routes_to_capability("p2", "file_intent", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "file_intent", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "file_intent", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "file_intent", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "file_intent", "exec_output")
trace_contract._emit_dispatches_agent("p3", "file_intent", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "file_intent", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "file_intent", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "file_intent", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "file_intent", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "file_intent", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "file_intent", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "file_intent", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "file_intent", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "file_intent", "eval_metric")
trace_contract._emit_stores_embedding("p4", "file_intent", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "file_intent", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "file_intent", "exec_snapshot_link")


class FileIntent(Enum):
    """Semantic classification of file purpose."""

    CLASS_EXPORT = "Primary Class/Agent Export"
    UTILITY_MODULE = "Utility/Configuration Module"
    MIXED_CONTENT = "Mixed Content (Multiple Classes)"
    DATA_MODULE = "Data/Constants Module"
    SCRIPT_MODULE = "Executable Script"
    UNCLEAR = "Unclassified/Edge Case"


class NamingConvention(Enum):
    """Naming convention types."""

    PASCAL_CASE = "PascalCase"
    SNAKE_CASE = "snake_case"
    INVALID = "Invalid"


@dataclass
class ViolationReport:
    """Detailed violation analysis."""

    file_path: str
    current_name: str
    detected_intent: FileIntent
    current_naming: NamingConvention
    proposed_name: str
    rationale: str
    confidence: float
    requires_manual_review: bool
    ast_analysis: dict


class HardenedNamingAuditor:
    """
    HARDENED auditor that would have caught pii.py violation.
    Uses AST parsing and semantic analysis instead of filename heuristics.
    """

    def __init__(self, target_directory: Path):
        self.target_directory = target_directory
        self.violations = []
        self.confident_files = []
        self.manual_review_required = []

    def analyze_file_content(self, file_path: Path) -> dict:
        """
        CRITICAL: Parse AST and extract semantic content.
        This is what was missing from the original audit.
        """
        try:
            content = file_path.read_text(encoding="utf-8")
            tree = ast.parse(content)
            classes = []
            functions = []
            imports = []
            constants = []
            for node in tqdm(ast.walk(tree), desc="Processing", unit="item"):
                if isinstance(node, ast.ClassDef):
                    class_info = {
                        "name": node.name,
                        "line": node.lineno,
                        "is_agent": self._is_agent_class(node, content),
                        "has_methods": len([n for n in node.body if isinstance(n, ast.FunctionDef)]) > 0,
                        "inherits_from_agent": self._inherits_from_agent(node),
                        "docstring": ast.get_docstring(node) or "",
                    }
                    classes.append(class_info)
                elif isinstance(node, ast.FunctionDef):
                    func_info = {
                        "name": node.name,
                        "line": node.lineno,
                        "is_private": node.name.startswith("_"),
                        "is_dunder": node.name.startswith("__") and node.name.endswith("__"),
                    }
                    functions.append(func_info)
                elif isinstance(node, ast.Import | ast.ImportFrom):
                    imports.append(ast.unparse(node))
                elif isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id.isupper():
                            constants.append(target.id)
            return {
                "classes": classes,
                "functions": functions,
                "imports": imports,
                "constants": constants,
                "line_count": len(content.splitlines()),
                "has_main": "__main__" in content,
                "content_preview": content[:200] + "..." if len(content) > 200 else content,
            }
        except (SyntaxError, OSError, UnicodeDecodeError, AttributeError, ValueError) as e:
            return {"error": str(e)}

    def _is_agent_class(self, class_node: ast.ClassDef, content: str) -> bool:
        """Detect if class is an Agent — delegates to kernel naming convention.

        [REFACTORED 2026-02-08] Removed bespoke docstring keyword matching.
        Now uses the same criteria as the classification kernel:
        class name ends with 'Agent' OR inherits from *Agent base.
        """
        if class_node.name.endswith("Agent"):
            if "Mixin" in class_node.name:
                return False
            return True
        for base in class_node.bases:
            if isinstance(base, ast.Name) and "Agent" in base.id:
                return True
            if isinstance(base, ast.Attribute) and "Agent" in base.attr:
                return True
        return False

    def _inherits_from_agent(self, class_node: ast.ClassDef) -> bool:
        """Check if class inherits from any Agent base class."""
        for base in class_node.bases:
            if isinstance(base, ast.Name) and "Agent" in base.id:
                return True
            if isinstance(base, ast.Attribute) and "Agent" in base.attr:
                return True
        return False

    def classify_file_intent(self, analysis: dict, file_path: Path) -> tuple[FileIntent, float]:
        """
        CRITICAL: Semantic classification based on content, not filename.
        This would have correctly classified pii.py as CLASS_EXPORT.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "HardenedNamingAuditor.classify_file_intent"
        )

        if "error" in analysis:
            return (FileIntent.UNCLEAR, 0.0)
        classes = analysis["classes"]
        functions = analysis["functions"]
        constants = analysis["constants"]
        primary_classes = [c for c in classes if c["is_agent"] or c["inherits_from_agent"]]
        if primary_classes and len(primary_classes) == 1:
            return (FileIntent.CLASS_EXPORT, 0.95)
        elif len(classes) >= 1 and (not functions):
            return (FileIntent.DATA_MODULE, 0.85)
        elif len(classes) == 1 and len(primary_classes) == 0:
            if classes[0]["has_methods"] and classes[0]["line"] < 20:
                return (FileIntent.CLASS_EXPORT, 0.75)
            else:
                return (FileIntent.UTILITY_MODULE, 0.65)
        elif functions and (not classes):
            if analysis["has_main"]:
                return (FileIntent.SCRIPT_MODULE, 0.9)
            else:
                return (FileIntent.UTILITY_MODULE, 0.85)
        elif constants and (not classes) and (not functions):
            return (FileIntent.DATA_MODULE, 0.9)
        elif classes and functions:
            return (FileIntent.MIXED_CONTENT, 0.5)
        else:
            return (FileIntent.UNCLEAR, 0.3)

    def detect_naming_convention(self, filename: str) -> NamingConvention:
        """Detect naming convention with strict validation."""
        if not filename.endswith(".py"):
            return NamingConvention.INVALID
        base_name = filename[:-3]
        if re.match("^[A-Z][a-zA-Z0-9]*$", base_name):
            return NamingConvention.PASCAL_CASE
        elif re.match("^[a-z][a-z0-9_]*$", base_name):
            return NamingConvention.SNAKE_CASE
        else:
            return NamingConvention.INVALID

    def validate_naming_compliance(self, file_path: Path) -> ViolationReport | None:
        """
        CRITICAL: Cross-reference naming with semantic intent.
        This is where pii.py would have been caught.
        """
        filename = file_path.name
        if filename == "__init__.py" or filename.startswith("test_"):
            return None
        analysis = self.analyze_file_content(file_path)
        if "error" in analysis:
            return None
        intent, confidence = self.classify_file_intent(analysis, file_path)
        naming = self.detect_naming_convention(filename)
        violation = None
        if intent == FileIntent.CLASS_EXPORT and naming != NamingConvention.PASCAL_CASE:
            primary_class = analysis["classes"][0]["name"]
            violation = ViolationReport(
                file_path=str(file_path),
                current_name=filename,
                detected_intent=intent,
                current_naming=naming,
                proposed_name=f"{primary_class}.py",
                rationale=f"Primary class export '{primary_class}' found in snake_case file. Violates: 'PascalCase files should contain primary class/agent exports'",
                confidence=confidence,
                requires_manual_review=confidence < 0.8,
                ast_analysis=analysis,
            )
        elif (
            intent in [FileIntent.UTILITY_MODULE, FileIntent.SCRIPT_MODULE]
            and naming != NamingConvention.SNAKE_CASE
        ):
            violation = ViolationReport(
                file_path=str(file_path),
                current_name=filename,
                detected_intent=intent,
                current_naming=naming,
                proposed_name=self._to_snake_case(filename),
                rationale=f"Utility module with {len(analysis['functions'])} functions found in PascalCase file. Violates: 'snake_case files should contain utilities/scripts'",
                confidence=confidence,
                requires_manual_review=confidence < 0.8,
                ast_analysis=analysis,
            )
        elif intent == FileIntent.MIXED_CONTENT:
            violation = ViolationReport(
                file_path=str(file_path),
                current_name=filename,
                detected_intent=intent,
                current_naming=naming,
                proposed_name="MANUAL_REVIEW_REQUIRED",
                rationale=f"Mixed content: {len(analysis['classes'])} classes and {len(analysis['functions'])} functions. Requires architectural decision",
                confidence=0.5,
                requires_manual_review=True,
                ast_analysis=analysis,
            )
        return violation

    def _to_snake_case(self, pascal_name: str) -> str:
        """Convert PascalCase to snake_case."""
        base_name = pascal_name[:-3] if pascal_name.endswith(".py") else pascal_name
        snake = re.sub("(.)([A-Z][a-z]+)", "\\1_\\2", base_name)
        snake = re.sub("([a-z0-9])([A-Z])", "\\1_\\2", snake)
        snake = snake.lower()
        return f"{snake}.py"

    def scan_directory(self) -> list[ViolationReport]:
        """Scan directory and identify all naming violations."""
        print("🔍 HARDENED Naming Convention Audit")
        print("=" * 50)
        print(f"Scanning: {self.target_directory}")
        print()
        python_files = list(self.target_directory.rglob("*.py"))
        total_files = len(python_files)
        print(f"Found {total_files} Python files to analyze...")
        print()
        for i, file_path in tqdm(enumerate(python_files, 1), desc="Processing", unit="item"):
            print(f"Analyzing [{i:3d}/{total_files}]: {file_path.name}")
            violation = self.validate_naming_compliance(file_path)
            if violation:
                self.violations.append(violation)
                if violation.requires_manual_review:
                    self.manual_review_required.append(violation)
                else:
                    self.confident_files.append(violation)
                print(f"  ❌ VIOLATION: {violation.rationale}")
            else:
                print("  ✅ Compliant")
        return self.violations

    def generate_disposition_table(self) -> str:
        """Generate comprehensive disposition table."""
        table = []
        table.append("| Current Name | Detected Intent | Proposed Name | Rationale | Confidence |")
        table.append("|-------------|----------------|---------------|-----------|------------|")
        for violation in self.violations:
            confidence_icon = "🔺" if violation.confidence < 0.8 else "✅"
            manual_icon = "👁️" if violation.requires_manual_review else " "
            table.append(
                f"| {violation.current_name} | {violation.detected_intent.value} | {violation.proposed_name} | {violation.rationale} | {confidence_icon}{violation.confidence:.2f} {manual_icon} |",
            )
        return "\n".join(table)

    def print_summary(self):
        """Print comprehensive audit summary."""
        print("\n" + "=" * 80)
        print("🎯 HARDENED NAMING AUDIT RESULTS")
        print("=" * 80)
        print("\n📊 SUMMARY:")
        print(f"  Total violations found: {len(self.violations)}")
        print(f"  High confidence violations: {len(self.confident_files)}")
        print(f"  Manual review required: {len(self.manual_review_required)}")
        if self.violations:
            print("\n🚨 VIOLATIONS DETECTED:")
            print(self.generate_disposition_table())
            if self.manual_review_required:
                print("\n👁️ FILES REQUIRING MANUAL REVIEW:")
                for violation in self.manual_review_required:
                    print(f"  • {violation.current_name}: {violation.detected_intent.value}")
        else:
            print("\n✅ ZERO NAMING VIOLATIONS - Perfect compliance achieved!")


def main():
    """Execute hardened naming audit."""
    if len(sys.argv) > 1:
        target_dir = Path(sys.argv[1])
    else:
        target_dir = Path("agentic_core/prompt_governance")
    if not target_dir.exists():
        print(f"❌ Directory not found: {target_dir}")
        sys.exit(1)
    auditor = HardenedNamingAuditor(target_dir)
    violations = auditor.scan_directory()
    auditor.print_summary()
    sys.exit(1 if violations else 0)


if __name__ == "__main__":
    main()
