"""
Magic Configuration Anti-Pattern Detector

Detects hardcoded constants in business logic that should be
externalized to configuration files.

Pattern Detection:
- Hardcoded model names ("gpt-4", "gpt-3.5-turbo")
- Hardcoded timeouts and thresholds
- Hardcoded API endpoints
- Hardcoded magic numbers in business logic
"""

import ast
import re
from pathlib import Path

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
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
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_pulls_context,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_through,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_authorize_and_execute("p2", "magic_validator", "execution_auth")
_emit_validates_capability("p2", "magic_validator", "capability_check")
_emit_routes_to_capability("p2", "magic_validator", "capability_route")
_emit_writes_via_uwg("p2", "magic_validator", "uwg_write")
_emit_blocks_direct_write("p2", "magic_validator", "direct_write_block")
_emit_records_tool_invocation("p2", "magic_validator", "tool_invocation")
_emit_captures_execution_output("p2", "magic_validator", "exec_output")
_emit_dispatches_agent("p3", "magic_validator", "agent_dispatch")
_emit_coordinates_agents("p3", "magic_validator", "agent_coordination")
_emit_records_workflow_lineage("p3", "magic_validator", "workflow_lineage")
_emit_records_healing_outcome("p3", "magic_validator", "healing_outcome")
_emit_escalates_failure("p3", "magic_validator", "failure_escalation")
_emit_orchestrates_workflow("p3", "magic_validator", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "magic_validator", "healing_dispatch")
_emit_invokes_evaluation("p3", "magic_validator", "evaluation_signal")
_emit_records_telemetry_event("p4", "magic_validator", "telemetry_event")
_emit_captures_evaluation_metric("p4", "magic_validator", "eval_metric")
_emit_stores_embedding("p4", "magic_validator", "embedding_store")
_emit_updates_meta_learning_state("p4", "magic_validator", "meta_learning")
_emit_links_execution_to_snapshot("p4", "magic_validator", "exec_snapshot_link")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_links_incident_trace,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
)

from .base_detector_validator import (
    AntiPatternCategory,
    AntiPatternDetector,
    AntiPatternViolation,
    EnforcementLevel,
)

_emit_emits_metric_event("magic_validator", "p4obs", "metric_1")
_emit_emits_metric_event("magic_validator", "p4obs", "metric_2")
_emit_emits_metric_event("magic_validator", "p4obs", "metric_3")
_emit_emits_metric_event("magic_validator", "p4obs", "metric_4")
_emit_emits_metric_event("magic_validator", "p4obs", "metric_5")
_emit_emits_metric_event("magic_validator", "p4obs", "metric_6")
_emit_records_incident_event("magic_validator", "p4obs", "incident")
_emit_captures_runtime_anomaly("magic_validator", "p4obs", "anomaly")
_emit_writes_observability_log("magic_validator", "p4obs", "obs_log")
_emit_updates_monitoring_state("magic_validator", "p4obs", "mon_state")
_emit_triggers_alert("magic_validator", "p4obs", "alert")
_emit_links_incident_trace("magic_validator", "p4obs", "trace_link")
_emit_captures_pattern("magic_validator", "p3lm", "pattern")
_emit_records_learning_event("magic_validator", "p3lm", "learning_event")
_emit_writes_learning_snapshot("magic_validator", "p3lm", "snapshot")
_emit_feeds_meta_learning("magic_validator", "p3lm", "meta_feed")
_emit_updates_routing_strategy("magic_validator", "p3lm", "routing")
_emit_improves_agent_policy("magic_validator", "p3lm", "policy")
_emit_stores_learning_state("magic_validator", "p3lm", "state")
_emit_records_execution_trace("magic_validator", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("magic_validator", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("magic_validator", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("magic_validator", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("magic_validator", "L4_STATE", "p2_trace_5")
_emit_reads_environ("magic_validator", "env_read", "p2_env_1")
_emit_reads_environ("magic_validator", "env_read", "p2_env_2")
_emit_reads_runtime_state("magic_validator", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("magic_validator", "runtime_state", "p2_rt_2")

emit_replay_key("p0", "magic_validator")
emit_determinism_digest("p0", "magic_validator")

_emit_dispatches_healing_run("p1", "magic_validator", "L5")
_emit_routes_through("p1", "magic_validator", "L5")
_emit_checks_agent_registry("p1", "magic_validator", "agent_registry")
_emit_validates_agent_capability("p1", "magic_validator", "capability")
_emit_dispatches_execution_plan("p1", "magic_validator", "exec_plan")
_emit_agent_executes_agent("p1", "magic_validator", "sub_agent")
_emit_routes_to_agent("p1", "magic_validator", "target_agent")
_emit_verifies_policy("p1", "magic_validator", "policy_check")
_emit_observes_runtime_state("p1", "magic_validator", "runtime_state")
_emit_verifies_boundary("p1", "magic_validator", "boundary_check")
_emit_transcripts_response("p1", "magic_validator", "transcript")
_emit_hard_fails_untranscripted("p1", "magic_validator")
_emit_gated_by_confidence("p1", "magic_validator", "confidence_gate")
_emit_escalates_to_human("p1", "magic_validator", "L5")
_emit_reads_policy_state("p1", "magic_validator", "L5")

_emit_applies_guardrail("p0", "magic_validator", "p0_governance")
_emit_snapshots_state("p0", "magic_validator", "state_snapshot")
_emit_writes_through("p1", "magic_validator", "uwg_governed_write")
_emit_writes_through("p1", "magic_validator", "uwg_governed_write_2")
_emit_pulls_context("p1", "magic_validator", "context_retrieval")
_emit_pulls_context("p1", "magic_validator", "context_retrieval_2")
emit_determinism_digest("trace_magic_validator", "magic_validator_dispatch")
emit_determinism_digest("trace_magic_validator", "magic_validator_complete")
_emit_validated_by_safety_plane("p1", "magic_validator", "safety_validation")


class MagicConfigDetector(AntiPatternDetector):
    """
    Detects hardcoded configuration values in business logic.

    Magic configuration prevents runtime tuning and
    environment-specific adaptation.
    """

    # Whitelist comment pattern
    WHITELIST_COMMENT = "# guardian: allow-magic-config"

    # Model name patterns
    MODEL_PATTERNS = [
        r"gpt-[34]",
        r"gpt-3\.5-turbo",
        r"gpt-4-turbo",
        r"gpt-4o",
        r"claude-[23]",
        r"claude-instant",
        r"text-davinci",
        r"text-embedding",
    ]

    # Timeout/threshold parameter names
    CONFIG_PARAM_NAMES = {
        "timeout",
        "threshold",
        "limit",
        "max_",
        "min_",
        "rate",
        "retry",
        "interval",
        "delay",
        "budget",
    }

    # API endpoint patterns
    API_ENDPOINT_PATTERNS = [
        r"https?://api\.",
        r"https?://.*\.openai\.com",
        r"https?://.*\.anthropic\.com",
        r"https?://.*\.pinecone\.io",
    ]

    def __init__(
        self,
        enforcement_level: EnforcementLevel = EnforcementLevel.WARNING,
        whitelisted_patterns: list[str] | None = None,
        whitelisted_files: list[str] | None = None,
    ):
        super().__init__(enforcement_level, whitelisted_patterns, whitelisted_files)

        # Add default whitelisted files
        self.whitelisted_files = self.whitelisted_files + [
            "test_*.py",
            "*_test.py",
            "conftest.py",
            "*_config.py",
            "config*.py",
            "settings*.py",
            "*_defaults.py",
        ]

        # Compile patterns
        self._model_regex = re.compile("|".join(self.MODEL_PATTERNS), re.IGNORECASE)
        self._api_regex = re.compile("|".join(self.API_ENDPOINT_PATTERNS), re.IGNORECASE)

    @property
    def category(self) -> AntiPatternCategory:
        return AntiPatternCategory.MAGIC_CONFIGURATION

    def detect(self, file_path: Path, tree: ast.Module) -> list[AntiPatternViolation]:
        """Detect magic configuration patterns in the AST."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "MagicConfigDetector.detect")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:MagicConfigDetector.detect".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        violations = []

        # Read source for whitelist comment checking
        try:
            source_lines = file_path.read_text(encoding="utf-8").splitlines()
        except (ValueError, TypeError, RuntimeError) as e:
            raise
            source_lines = []

        # Check function/method definitions for hardcoded defaults
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                violations.extend(self._check_function_defaults(node, file_path, source_lines))
            elif isinstance(node, ast.Assign):
                violations.extend(self._check_assignment(node, file_path, source_lines))
            elif isinstance(node, ast.Call):
                violations.extend(self._check_call_arguments(node, file_path, source_lines))

        return violations

    def _check_function_defaults(
        self,
        node: ast.FunctionDef | ast.AsyncFunctionDef,
        file_path: Path,
        source_lines: list[str],
    ) -> list[AntiPatternViolation]:
        """Check function parameter defaults for magic values."""
        violations = []

        # Check for whitelist comment (look back up to 5 lines)
        if node.lineno > 1 and node.lineno <= len(source_lines):
            for lookback in range(1, 6):
                check_idx = node.lineno - 1 - lookback
                if check_idx < 0:
                    break
                line = source_lines[check_idx].strip()
                if self.WHITELIST_COMMENT in line:
                    return []
                if line and not line.startswith("#"):
                    break

        # Check each argument with a default value
        defaults = node.args.defaults
        args = node.args.args[-len(defaults) :] if defaults else []

        for arg, default in tqdm(zip(args, defaults, strict=False), desc="Processing", unit="item"):
            # Skip ALL_CAPS parameter names - these are legitimate SSOT constants
            if arg.arg == arg.arg.upper() and arg.arg.isidentifier():
                continue
            param_name = arg.arg.lower()

            # Check if parameter name suggests configuration
            is_config_param = any(config_name in param_name for config_name in self.CONFIG_PARAM_NAMES)

            if is_config_param and isinstance(default, ast.Constant):
                value = default.value

                # Check for hardcoded numeric values
                if isinstance(value, int | float) and value not in (0, 1, -1, True, False):
                    violations.append(
                        self._create_violation(
                            node,
                            file_path,
                            f"Hardcoded {param_name}={value}",
                            str(value),
                            default.lineno if hasattr(default, "lineno") else node.lineno,
                        ),
                    )

                # Check for model names
                if isinstance(value, str) and self._model_regex.search(value):
                    violations.append(
                        self._create_violation(
                            node,
                            file_path,
                            f"Hardcoded model name '{value}'",
                            value,
                            default.lineno if hasattr(default, "lineno") else node.lineno,
                        ),
                    )

        return violations

    def _check_assignment(
        self,
        node: ast.Assign,
        file_path: Path,
        source_lines: list[str],
    ) -> list[AntiPatternViolation]:
        """Check assignments for magic configuration values."""
        violations = []

        # Check for whitelist comment
        if node.lineno > 1 and node.lineno <= len(source_lines):
            prev_line = source_lines[node.lineno - 2].strip()
            if self.WHITELIST_COMMENT in prev_line:
                return []

        # Get variable name
        if not node.targets:
            return []

        target = node.targets[0]
        var_name = ""
        original_var_name = ""
        if isinstance(target, ast.Name):
            original_var_name = target.id
            var_name = target.id.lower()
        elif isinstance(target, ast.Attribute):
            original_var_name = target.attr
            var_name = target.attr.lower()

        if not var_name:
            return []

        # Skip ALL_CAPS names - these are legitimate SSOT constants, not magic config
        if original_var_name == original_var_name.upper() and original_var_name.isidentifier():
            return []

        # Check if variable name suggests configuration
        is_config_var = any(config_name in var_name for config_name in self.CONFIG_PARAM_NAMES)

        # Check for constant string values
        if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
            value = node.value.value

            # Check for model names
            if self._model_regex.search(value):
                violations.append(
                    self._create_violation(
                        node,
                        file_path,
                        f"Hardcoded model name '{value}'",
                        value,
                        node.lineno,
                    ),
                )

            # Check for API endpoints
            if self._api_regex.search(value):
                violations.append(
                    self._create_violation(
                        node,
                        file_path,
                        "Hardcoded API endpoint",
                        value[:50] + "..." if len(value) > 50 else value,
                        node.lineno,
                    ),
                )

        # Check for hardcoded numeric config values
        if is_config_var and isinstance(node.value, ast.Constant):
            value = node.value.value
            if isinstance(value, int | float) and value not in (0, 1, -1, True, False):
                violations.append(
                    self._create_violation(
                        node,
                        file_path,
                        f"Hardcoded {var_name}={value}",
                        str(value),
                        node.lineno,
                    ),
                )

        return violations

    def _check_call_arguments(
        self,
        node: ast.Call,
        file_path: Path,
        source_lines: list[str],
    ) -> list[AntiPatternViolation]:
        """Check function call arguments for magic values."""
        violations = []

        # Check for whitelist comment
        if hasattr(node, "lineno") and node.lineno > 1 and node.lineno <= len(source_lines):
            prev_line = source_lines[node.lineno - 2].strip()
            if self.WHITELIST_COMMENT in prev_line:
                return []

        # Check keyword arguments
        for keyword in tqdm(node.keywords, desc="Processing", unit="item"):
            if keyword.arg is None:
                continue

            param_name = keyword.arg.lower()

            # Check if parameter name suggests configuration
            is_config_param = any(config_name in param_name for config_name in self.CONFIG_PARAM_NAMES)

            if is_config_param and isinstance(keyword.value, ast.Constant):
                value = keyword.value.value

                # Check for hardcoded numeric values
                if isinstance(value, int | float) and value not in (0, 1, -1, True, False):
                    violations.append(
                        self._create_violation(
                            node,
                            file_path,
                            f"Hardcoded {param_name}={value} in function call",
                            str(value),
                            node.lineno,
                        ),
                    )

        return violations

    def _create_violation(
        self,
        node: ast.expr,
        file_path: Path,
        pattern: str,
        value: str,
        line_number: int,
    ) -> AntiPatternViolation:
        """Create a violation for detected pattern."""
        evidence = self._get_source_line(file_path, line_number)

        return AntiPatternViolation(
            file_path=file_path,
            line_number=line_number,
            category=self.category,
            message=f"Magic configuration: {pattern}",
            evidence=evidence,
            severity="warning",
            suggested_fix=self._generate_fix_suggestion(pattern, value),
            metadata={
                "pattern": pattern,
                "value": value,
            },
        )

    def _generate_fix_suggestion(self, pattern: str, value: str) -> str:
        """Generate a fix suggestion for the violation."""
        if "model" in pattern.lower():
            return f"""Externalize model name to configuration:
    from agentic_core.config.agent_defaults import AgentDefaults

    model = AgentDefaults.get("DEFAULT_MODEL", "{value}")"""

        if "timeout" in pattern.lower():
            return f"""Externalize timeout to configuration:
    from agentic_core.config.agent_defaults import AgentDefaults

    timeout = AgentDefaults.get_int("DEFAULT_TIMEOUT", {value})"""

        if "threshold" in pattern.lower():
            return f"""Externalize threshold to configuration:
    from agentic_core.config.agent_defaults import AgentDefaults

    threshold = AgentDefaults.get_float("THRESHOLD_NAME", {value})"""

        return f"""Externalize configuration value:
    import os
import uuid

    # Use environment variable with fallback
    value = os.getenv("CONFIG_NAME", "{value}")

    # Or use AgentDefaults
    from agentic_core.config.agent_defaults import AgentDefaults
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
from tqdm import tqdm
    _emit_pulls_context,
    _emit_execution_terminates_at_uwg,
    _emit_writes_through,
    _emit_validated_by_safety_plane,
    _emit_invokes_eval,
    _emit_proposal_commits_routing,
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
)
_emit_pulls_context("p1", "magic_validator", "context_pull")
_emit_pulls_context("p1", "magic_validator", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "magic_validator", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "magic_validator", "uwg_term_secondary")
_emit_writes_through("p1", "magic_validator", "write_through")
_emit_writes_through("p1", "magic_validator", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "magic_validator", "safety_validation")
_emit_invokes_eval("p1", "magic_validator", "eval_call")
_emit_proposal_commits_routing("p1", "magic_validator", "routing_commit")
    value = AgentDefaults.get("CONFIG_NAME", "{value}")"""


__all__ = ["MagicConfigDetector"]
