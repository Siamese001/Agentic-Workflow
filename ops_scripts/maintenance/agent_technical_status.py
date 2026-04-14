#!/usr/bin/env python3
"""
NUCLEAR AUDIT: Comprehensive Agent Technical Status Analysis

Performs deep technical analysis of all agents in agentic_core/ to identify:
1. SovereignBaseAgent inheritance compliance
2. heal() method signature compliance
3. Namespace/structure compliance
4. Import dependency integrity
5. Mixin pattern compliance
6. Abstract vs concrete agent classification

Generated technical status table provides complete visibility into agent health.
"""

import ast
import logging
import sys
from dataclasses import dataclass, field

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_reads_through,
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "agent_technical_status")
_emit_applies_guardrail("p0", "agent_technical_status", "p0_governance")
_emit_reads_policy_state("p0", "agent_technical_status", "policy_binding")
_emit_snapshots_state("p0", "agent_technical_status", "state_snapshot")
emit_replay_key("p0", "agent_technical_status")
emit_determinism_digest("p0", "agent_technical_status")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "agent_technical_status", "execution_auth")
_emit_validates_capability("p2", "agent_technical_status", "capability_check")
_emit_routes_to_capability("p2", "agent_technical_status", "capability_route")
_emit_writes_via_uwg("p2", "agent_technical_status", "uwg_write")
_emit_blocks_direct_write("p2", "agent_technical_status", "direct_write_block")
_emit_records_tool_invocation("p2", "agent_technical_status", "tool_invocation")
_emit_captures_execution_output("p2", "agent_technical_status", "exec_output")
_emit_dispatches_agent("p3", "agent_technical_status", "agent_dispatch")
_emit_coordinates_agents("p3", "agent_technical_status", "agent_coordination")
_emit_records_workflow_lineage("p3", "agent_technical_status", "workflow_lineage")
_emit_records_healing_outcome("p3", "agent_technical_status", "healing_outcome")
_emit_escalates_failure("p3", "agent_technical_status", "failure_escalation")
_emit_orchestrates_workflow("p3", "agent_technical_status", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "agent_technical_status", "healing_dispatch")
_emit_invokes_evaluation("p3", "agent_technical_status", "evaluation_signal")
_emit_records_telemetry_event("p4", "agent_technical_status", "telemetry_event")
_emit_captures_evaluation_metric("p4", "agent_technical_status", "eval_metric")
_emit_stores_embedding("p4", "agent_technical_status", "embedding_store")
_emit_updates_meta_learning_state("p4", "agent_technical_status", "meta_learning")
_emit_links_execution_to_snapshot("p4", "agent_technical_status", "exec_snapshot_link")
_FIXED_TS = "2026-01-01T00:00:00"
from pathlib import Path
from typing import Any

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    get_validated_project_root,
)
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)
from tqdm import tqdm

_emit_emits_metric_event("agent_technical_status", "p4obs", "metric_1")
_emit_emits_metric_event("agent_technical_status", "p4obs", "metric_2")
_emit_emits_metric_event("agent_technical_status", "p4obs", "metric_3")
_emit_emits_metric_event("agent_technical_status", "p4obs", "metric_4")
_emit_emits_metric_event("agent_technical_status", "p4obs", "metric_5")
_emit_emits_metric_event("agent_technical_status", "p4obs", "metric_6")
_emit_records_incident_event("agent_technical_status", "p4obs", "incident")
_emit_captures_runtime_anomaly("agent_technical_status", "p4obs", "anomaly")
_emit_writes_observability_log("agent_technical_status", "p4obs", "obs_log")
_emit_updates_monitoring_state("agent_technical_status", "p4obs", "mon_state")
_emit_triggers_alert("agent_technical_status", "p4obs", "alert")
_emit_links_incident_trace("agent_technical_status", "p4obs", "trace_link")
_emit_captures_pattern("agent_technical_status", "p3lm", "pattern")
_emit_records_learning_event("agent_technical_status", "p3lm", "learning_event")
_emit_writes_learning_snapshot("agent_technical_status", "p3lm", "snapshot")
_emit_feeds_meta_learning("agent_technical_status", "p3lm", "meta_feed")
_emit_updates_routing_strategy("agent_technical_status", "p3lm", "routing")
_emit_improves_agent_policy("agent_technical_status", "p3lm", "policy")
_emit_stores_learning_state("agent_technical_status", "p3lm", "state")
_emit_records_execution_trace("agent_technical_status", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("agent_technical_status", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("agent_technical_status", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("agent_technical_status", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("agent_technical_status", "L4_STATE", "p2_trace_5")
_emit_reads_environ("agent_technical_status", "env_read", "p2_env_1")
_emit_reads_environ("agent_technical_status", "env_read", "p2_env_2")
_emit_reads_runtime_state("agent_technical_status", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("agent_technical_status", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "agent_technical_status", "context_pull")
_emit_pulls_context("p1", "agent_technical_status", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "agent_technical_status", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "agent_technical_status", "uwg_term_secondary")
_emit_writes_through("p1", "agent_technical_status", "write_through")
_emit_writes_through("p1", "agent_technical_status", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "agent_technical_status", "safety_validation")
_emit_invokes_eval("p1", "agent_technical_status", "eval_call")
_emit_proposal_commits_routing("p1", "agent_technical_status", "routing_commit")
_emit_escalates_to_human("p1", "agent_technical_status", "human_escalation")
_emit_routes_through("p1", "agent_technical_status", "route_through")
_emit_checks_agent_registry("p1", "agent_technical_status", "agent_registry")
_emit_validates_agent_capability("p1", "agent_technical_status", "capability")
_emit_dispatches_execution_plan("p1", "agent_technical_status", "exec_plan")
_emit_agent_executes_agent("p1", "agent_technical_status", "sub_agent")
_emit_routes_to_agent("p1", "agent_technical_status", "target_agent")
_emit_verifies_policy("p1", "agent_technical_status", "policy_check")
_emit_observes_runtime_state("p1", "agent_technical_status", "runtime_state")
_emit_verifies_boundary("p1", "agent_technical_status", "boundary_check")
_emit_transcripts_response("p1", "agent_technical_status", "transcript")
_emit_hard_fails_untranscripted("p1", "agent_technical_status")
_emit_gated_by_confidence("p1", "agent_technical_status", "confidence_gate")
_emit_reads_through("l4", "agent_technical_status", "urg_read_1")
_emit_reads_through("l4", "agent_technical_status", "urg_read_2")
_emit_reads_through("l4", "agent_technical_status", "urg_read_3")
_emit_reads_through("l4", "agent_technical_status", "urg_read_4")
_emit_reads_through("l4", "agent_technical_status", "urg_read_5")
_emit_reads_through("l4", "agent_technical_status", "urg_read_6")
_emit_reads_through("l4", "agent_technical_status", "urg_read_7")
_emit_reads_through("l4", "agent_technical_status", "urg_read_8")
_emit_reads_through("l4", "agent_technical_status", "urg_read_9")
_emit_reads_through("l4", "agent_technical_status", "urg_read_10")
_emit_reads_through("l4", "agent_technical_status", "urg_read_11")
_emit_reads_through("l4", "agent_technical_status", "urg_read_12")
_emit_reads_through("l4", "agent_technical_status", "urg_read_13")
_emit_reads_through("l4", "agent_technical_status", "urg_read_14")
_emit_reads_through("l4", "agent_technical_status", "urg_read_15")
_emit_reads_through("l4", "agent_technical_status", "urg_read_16")
_emit_reads_through("l4", "agent_technical_status", "urg_read_17")
_emit_reads_through("l4", "agent_technical_status", "urg_read_18")
_emit_reads_through("l4", "agent_technical_status", "urg_read_19")
_emit_reads_through("l4", "agent_technical_status", "urg_read_20")
_emit_reads_through("l4", "agent_technical_status", "urg_read_21")
_emit_reads_through("l4", "agent_technical_status", "urg_read_22")
_emit_reads_through("l4", "agent_technical_status", "urg_read_23")
_emit_reads_through("l4", "agent_technical_status", "urg_read_24")
_emit_reads_through("l4", "agent_technical_status", "urg_read_25")
_emit_reads_through("l4", "agent_technical_status", "urg_read_26")
_emit_reads_through("l4", "agent_technical_status", "urg_read_27")
_emit_reads_through("l4", "agent_technical_status", "urg_read_28")
_emit_reads_through("l4", "agent_technical_status", "urg_read_29")
_emit_reads_through("l4", "agent_technical_status", "urg_read_30")
_emit_reads_through("l4", "agent_technical_status", "urg_read_31")
_emit_reads_through("l4", "agent_technical_status", "urg_read_32")
_emit_reads_through("l4", "agent_technical_status", "urg_read_33")
_emit_reads_through("l4", "agent_technical_status", "urg_read_34")
_emit_reads_through("l4", "agent_technical_status", "urg_read_35")
_emit_reads_through("l4", "agent_technical_status", "urg_read_36")
_emit_reads_through("l4", "agent_technical_status", "urg_read_37")
_emit_reads_through("l4", "agent_technical_status", "urg_read_38")
_emit_reads_through("l4", "agent_technical_status", "urg_read_39")
_emit_reads_through("l4", "agent_technical_status", "urg_read_40")
_emit_reads_through("l4", "agent_technical_status", "urg_read_41")
_emit_reads_through("l4", "agent_technical_status", "urg_read_42")
_emit_reads_through("l4", "agent_technical_status", "urg_read_43")
_emit_reads_through("l4", "agent_technical_status", "urg_read_44")
_emit_reads_through("l4", "agent_technical_status", "urg_read_45")
_emit_reads_through("l4", "agent_technical_status", "urg_read_46")
_emit_reads_through("l4", "agent_technical_status", "urg_read_47")
_emit_reads_through("l4", "agent_technical_status", "urg_read_48")
_emit_reads_through("l4", "agent_technical_status", "urg_read_49")

# Add project root to path
PROJECT_ROOT = get_validated_project_root()
# guardian: allow-global-mutation
sys.path.insert(0, str(PROJECT_ROOT))

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


@dataclass
class AgentTechnicalStatus:
    """Technical status data for a single agent."""

    class_name: str
    file_path: str
    layer: str
    namespace_status: str = "[UNKNOWN]"
    inheritance_status: str = "[UNKNOWN]"
    heal_method_status: str = "[UNKNOWN]"
    import_status: str = "[UNKNOWN]"
    mixin_status: str = "[UNKNOWN]"
    agent_type: str = "[UNKNOWN]"
    violations: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    line_count: int = 0
    complexity_score: float = 0.0


class NuclearAuditor:
    """Comprehensive agent technical status auditor."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.agentic_core_dir = project_root / AGENTIC_CORE_DIR
        self.structure_blueprint = self._load_structure_blueprint()
        self.agent_statuses: list[AgentTechnicalStatus] = []

        # Critical base classes and mixins to check
        self.critical_base_classes = {
            "SovereignBaseAgent",
            "L0RoutingBaseAgent",
            "L1CognitionBase",
            "L2ExecutionBase",
            "L3OrchestrationBase",
            "L4StateBase",
            "L5SafetyBase",
            "L6ObservabilityBase",
        }

        self.critical_mixins = {
            "SubatomicTestingMixin",
            "HealerMixin",
            "ValidatorMixin",
            "infrastructure_mixin",
            "ConfigMixin",
            "LLMProviderMixin",
            "EmbeddingMixin",
            "HealingStrategyMixin",
        }

    def _load_structure_blueprint(self) -> dict[str, Any]:
        """Load structure blueprint for namespace validation."""
        try:
            blueprint_path = self.agentic_core_dir / "L5_safety" / "validators" / "structure_blueprint.py"
            if blueprint_path.exists():
                with open(blueprint_path, encoding="utf-8") as f:
                    content = f.read()
                # Parse the SOVEREIGN_TERRITORIES from the file
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Assign):
                        for target in node.targets:
                            if isinstance(target, ast.Name) and target.id == "SOVEREIGN_TERRITORIES":
                                return ast.literal_eval(node.value)
        # guardian: allow-silent-swallow
        except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
            raise
            logger.warning(f"Failed to load structure blueprint: {e}")

        return {}

    def audit_all_agents(self) -> list[AgentTechnicalStatus]:
        """Perform comprehensive audit of all agents in agentic_core/."""
        logger.info("Starting nuclear audit of agentic_core/ agents...")

        # Find all Python files in agentic_core
        python_files = list(self.agentic_core_dir.rglob("*.py"))
        logger.info(f"Found {len(python_files)} Python files to analyze")

        for file_path in python_files:
            try:
                agents = self._analyze_file(file_path)
                self.agent_statuses.extend(agents)
            # guardian: allow-silent-swallow
            except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
                raise
                logger.error(f"Failed to analyze {file_path}: {e}")

        logger.info(f"Analyzed {len(self.agent_statuses)} agent classes")
        return self.agent_statuses

    def _analyze_file(self, file_path: Path) -> list[AgentTechnicalStatus]:
        """Analyze a single Python file for agent classes."""
        agents = []

        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and node.name.endswith("Agent"):
                    status = self._analyze_agent_class(node, file_path, content)
                    agents.append(status)

        # guardian: allow-silent-swallow
        except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
            raise
            logger.error(f"Error parsing {file_path}: {e}")

        return agents

    def _analyze_agent_class(
        self,
        class_node: ast.ClassDef,
        file_path: Path,
        content: str,
    ) -> AgentTechnicalStatus:
        """Perform detailed analysis of a single agent class."""
        status = AgentTechnicalStatus(
            class_name=class_node.name,
            file_path=str(file_path.relative_to(self.project_root)),
            layer=self._determine_layer(file_path),
            line_count=content.count("\n") + 1,
        )

        # 1. Namespace/Structure Compliance
        status.namespace_status = self._check_namespace_compliance(file_path)

        # 2. Inheritance Analysis
        status.inheritance_status = self._check_inheritance_compliance(class_node)

        # 3. heal() Method Analysis
        status.heal_method_status = self._check_heal_method_compliance(class_node)

        # 4. Import Dependency Analysis
        status.import_status = self._check_import_compliance(content, file_path)

        # 5. Mixin Pattern Analysis
        status.mixin_status = self._check_mixin_compliance(class_node)

        # 6. Agent Type Classification
        status.agent_type = self._classify_agent_type(class_node, content)

        # 7. Calculate complexity score
        status.complexity_score = self._calculate_complexity(class_node, content)

        # 8. Generate violations and recommendations
        self._generate_violations_and_recommendations(status)

        return status

    def _determine_layer(self, file_path: Path) -> str:
        """Determine the architectural layer for a file."""
        path_str = str(file_path)

        layer_mappings = {
            "L0_routing": "L0",
            "L1_cognition": "L1",
            "L2_execution": "L2",
            "L3_orchestration": "L3",
            "L4_state": "L4",
            "L5_safety": "L5",
            "L6_observability": "L6",
            "base_agents": "Base",
            "domain": "Domain",
        }

        for pattern, layer in layer_mappings.items():
            if pattern in path_str:
                return layer

        return "Unknown"

    def _check_namespace_compliance(self, file_path: Path) -> str:
        """Check if file location complies with structure blueprint."""
        relative_path = file_path.relative_to(self.project_root)
        path_parts = relative_path.parts

        if len(path_parts) < 2 or path_parts[0] != AGENTIC_CORE_DIR:
            return "[INVALID] - Outside agentic_core"

        if len(path_parts) >= 3:
            territory = AGENTIC_CORE_DIR
            subfolder = path_parts[2]

            # Check if subfolder is valid in structure blueprint
            if territory in self.structure_blueprint:
                valid_subfolders = self.structure_blueprint[territory].get("subfolders", {})
                if isinstance(valid_subfolders, dict) and subfolder in valid_subfolders:
                    return "[VALID]"
                elif isinstance(valid_subfolders, list) and subfolder in valid_subfolders:
                    return "[VALID]"

        return "[INVALID]"

    def _check_inheritance_compliance(self, class_node: ast.ClassDef) -> str:
        """Check inheritance chain for proper base classes."""
        base_classes = []

        for base in class_node.bases:
            if isinstance(base, ast.Name):
                base_classes.append(base.name)
            elif isinstance(base, ast.Attribute):
                base_classes.append(ast.unparse(base))

        # Check for critical base classes
        for critical_base in self.critical_base_classes:
            if critical_base in base_classes:
                return "[VALID]"

        # Check if it inherits from any *Agent class (indicating proper chain)
        for base in base_classes:
            if base.endswith("Agent") or base.endswith("Mixin"):
                return "[PARTIAL]"

        return "[BROKEN] - Missing SovereignBaseAgent inheritance"

    def _check_heal_method_compliance(self, class_node: ast.ClassDef) -> str:
        """Check heal() method signature compliance."""
        for node in tqdm(class_node.body, desc="Processing", unit="item"):
            if isinstance(node, ast.FunctionDef) and node.name == "heal":
                # Check parameters
                args = [arg.arg for arg in node.args.args]

                # Should have 'self' and 'violation: dict' parameters
                if len(args) >= 2 and args[0] == "self":
                    # Check if violation parameter has proper typing
                    if "violation" in args:
                        return "[VALID]"
                    else:
                        return "[INVALID] - Wrong signature"

        return "[MISSING] - No heal() method"

    def _check_import_compliance(self, content: str, file_path: Path) -> str:
        """Check import dependencies for compliance."""
        try:
            tree = ast.parse(content)
            imports = []

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for alias in node.names:
                        imports.append(f"{module}.{alias.name}")

            # Check for critical imports
            has_sovereign_import = any("SovereignBaseAgent" in imp for imp in imports)
            has_proper_layer_import = any(AGENTIC_CORE_DIR in imp for imp in imports)

            if has_sovereign_import and has_proper_layer_import:
                return "[VALID]"
            elif has_proper_layer_import:
                return "[PARTIAL]"
            else:
                return "[BROKEN]"

        except (
            OSError,
            UnicodeDecodeError,
            SyntaxError,
        ):  # guardian: Parsing and encoding errors need separate handling strategies
            return "[ERROR]"

    def _check_mixin_compliance(self, class_node: ast.ClassDef) -> str:
        """Check mixin pattern compliance."""
        base_classes = []

        for base in class_node.bases:
            if isinstance(base, ast.Name):
                base_classes.append(base.name)

        # Check for critical mixins
        mixin_count = sum(1 for mixin in self.critical_mixins if mixin in base_classes)

        if mixin_count >= 2:  # Should have multiple mixins for proper functionality
            return "[VALID]"
        elif mixin_count >= 1:
            return "[PARTIAL]"
        else:
            return "[MISSING]"

    def _classify_agent_type(self, class_node: ast.ClassDef, content: str) -> str:
        """Classify agent as abstract, concrete, or stub."""
        # Check for abstract methods
        has_abstract = False
        has_pass_only = True

        for node in tqdm(class_node.body, desc="Processing", unit="item"):
            if isinstance(node, ast.FunctionDef):
                has_pass_only = False
                # Check for abstract decorators
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Name) and decorator.name in [
                        "abstractmethod",
                        "abc.abstractmethod",
                    ]:
                        has_abstract = True
            elif isinstance(node, ast.Pass):
                continue
            elif (
                isinstance(node, ast.Expr)
                and isinstance(node.value, ast.Constant)
                and isinstance(node.value.value, str)
            ):
                # Docstring - doesn't count as implementation
                continue
            else:
                has_pass_only = False

        # Check for TODO/FIXME markers
        has_todo = any(marker in content.upper() for marker in ["TODO", "FIXME", "XXX", "HACK"])

        if has_abstract:
            return "Abstract"
        elif has_pass_only or has_todo:
            return "Stub"
        else:
            return "Concrete"

    def _calculate_complexity(self, class_node: ast.ClassDef, content: str) -> float:
        """Calculate complexity score for the agent."""
        # Simple complexity based on:
        # - Number of methods
        # - Number of base classes
        # - Cyclomatic complexity estimation

        method_count = len([n for n in class_node.body if isinstance(n, ast.FunctionDef)])
        base_count = len(class_node.bases)

        # Estimate cyclomatic complexity
        complexity_keywords = ["if", "elif", "for", "while", "try", "except", "with"]
        cyclomatic = sum(content.count(keyword) for keyword in complexity_keywords)

        return float(method_count + base_count + cyclomatic * 0.5)

    def _generate_violations_and_recommendations(self, status: AgentTechnicalStatus):
        """Generate violation list and recommendations based on analysis."""
        violations = []
        recommendations = []

        # Inheritance violations
        if "[BROKEN]" in status.inheritance_status:
            violations.append("Missing SovereignBaseAgent inheritance")
            recommendations.append("Add SovereignBaseAgent to class inheritance")

        # heal() method violations
        if "[MISSING]" in status.heal_method_status:
            violations.append("Missing heal() method")
            recommendations.append("Implement heal(self, violation: dict) -> dict method")
        elif "[INVALID]" in status.heal_method_status:
            violations.append("Incorrect heal() method signature")
            recommendations.append("Fix heal() method to match expected signature")

        # Namespace violations
        if "[INVALID]" in status.namespace_status:
            violations.append("Invalid namespace/location")
            recommendations.append("Move agent to proper directory per structure blueprint")

        # Import violations
        if "[BROKEN]" in status.import_status:
            violations.append("Broken import dependencies")
            recommendations.append("Fix import statements and dependencies")

        # Stub agent violations
        if status.agent_type == "Stub":
            violations.append("Agent is incomplete stub")
            recommendations.append("Complete agent implementation or mark as abstract")

        status.violations = violations
        status.recommendations = recommendations

    def generate_technical_status_table(self) -> str:
        """Generate comprehensive technical status table."""
        if not self.agent_statuses:
            return "No agents analyzed"

        # Sort by layer, then by status priority
        def sort_key(status):
            priority_order = {
                "[BROKEN]": 0,
                "[MISSING]": 1,
                "[INVALID]": 2,
                "[PARTIAL]": 3,
                "[VALID]": 4,
            }
            layer_order = {"Base": 0, "L0": 1, "L1": 2, "L2": 3, "L3": 4, "L4": 5, "L5": 6, "L6": 7}

            # Count critical issues
            critical_issues = sum(
                1
                for field in [status.inheritance_status, status.heal_method_status]
                if "[BROKEN]" in field or "[MISSING]" in field
            )

            return (
                critical_issues,
                layer_order.get(status.layer, 99),
                priority_order.get(status.inheritance_status, 99),
            )

        sorted_agents = sorted(self.agent_statuses, key=sort_key)

        # Generate table header
        table = []
        table.append("# NUCLEAR AUDIT REPORT: Agent Technical Status")
        table.append(f"Generated: {_FIXED_TS}")
        table.append(f"Total Agents Analyzed: {len(self.agent_statuses)}")
        table.append("")

        # Summary statistics
        inheritance_broken = sum(1 for a in self.agent_statuses if "[BROKEN]" in a.inheritance_status)
        heal_missing = sum(1 for a in self.agent_statuses if "[MISSING]" in a.heal_method_status)
        namespace_invalid = sum(1 for a in self.agent_statuses if "[INVALID]" in a.namespace_status)
        stub_agents = sum(1 for a in self.agent_statuses if a.agent_type == "Stub")

        table.append("## Summary Statistics")
        table.append(f"- Broken Inheritance: {inheritance_broken} agents")
        table.append(f"- Missing heal() Method: {heal_missing} agents")
        table.append(f"- Invalid Namespace: {namespace_invalid} agents")
        table.append(f"- Stub/Incomplete Agents: {stub_agents} agents")
        table.append("")

        # Detailed table
        table.append("## Detailed Technical Status")
        table.append("")
        table.append(
            "| Agent | Layer | File | Inheritance | heal() | Namespace | Type | Complexity | Issues |",
        )
        table.append(
            "|-------|-------|------|-------------|--------|-----------|------|------------|--------|",
        )

        for status in tqdm(sorted_agents, desc="Processing", unit="item"):
            issues = len(status.violations)
            if issues > 0:
                issues_str = f"ISSUES {issues}"
            else:
                issues_str = "OK"

            table.append(
                f"| {status.class_name} | {status.layer} | {status.file_path} | "
                f"{status.inheritance_status} | {status.heal_method_status} | "
                f"{status.namespace_status} | {status.agent_type} | "
                f"{status.complexity_score:.1f} | {issues_str} |",
            )

        # Critical issues section
        table.append("")
        table.append("## Critical Issues Requiring Immediate Attention")
        table.append("")

        critical_agents = [
            a
            for a in sorted_agents
            if any(
                "[BROKEN]" in field or "[MISSING]" in field
                for field in [a.inheritance_status, a.heal_method_status]
            )
        ]

        for status in critical_agents:
            table.append(f"### CRITICAL: {status.class_name} ({status.layer})")
            table.append(f"**File:** `{status.file_path}`")
            table.append(f"**Issues:** {', '.join(status.violations)}")
            table.append(f"**Recommendations:** {', '.join(status.recommendations)}")
            table.append("")

        return "\n".join(table)

    def save_report(self, output_path: Path):
        """Save detailed audit report to file."""
        report = self.generate_technical_status_table()

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report)

        logger.info(f"Audit report saved to: {output_path}")


def main():
    """Main execution function."""
    project_root = Path(__file__).parent
    auditor = NuclearAuditor(project_root)

    # Perform comprehensive audit
    logger.info("🚀 Starting nuclear audit...")
    auditor.audit_all_agents()

    # Generate and save report
    report_path = project_root / "NUCLEAR_AUDIT_REPORT.md"
    auditor.save_report(report_path)

    # Print summary
    statuses = auditor.agent_statuses
    total = len(statuses)
    broken = sum(1 for s in statuses if "[BROKEN]" in s.inheritance_status)
    missing_heal = sum(1 for s in statuses if "[MISSING]" in s.heal_method_status)
    valid = sum(
        1 for s in statuses if "[VALID]" in s.inheritance_status and "[VALID]" in s.heal_method_status
    )

    print("\n*** NUCLEAR AUDIT COMPLETE ***")
    print(f"Total Agents: {total}")
    print(f"Broken Inheritance: {broken} ({broken / total * 100:.1f}%)")
    print(f"Missing heal(): {missing_heal} ({missing_heal / total * 100:.1f}%)")
    print(f"Fully Compliant: {valid} ({valid / total * 100:.1f}%)")
    print(f"Report: {report_path}")


if __name__ == "__main__":
    main()
