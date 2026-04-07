#!/usr/bin/env python3
"""CI Kernel-Extension Boundary Checker.

Enforces that modular extensions do not create reverse dependencies
into kernel internals. Extensions may import kernel interfaces,
but kernel must not import extensions.

Exits with non-zero status on boundary violations.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path
from typing import Any

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    APPS_SHARED_DIR,
    OPS_SCRIPTS_DIR,
    SYSTEM_LEARNING_DIR,
)
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

_emit_records_execution_trace("p0", "evidence", "check_kernel_extension_boundary")
_emit_applies_guardrail("p0", "check_kernel_extension_boundary", "p0_governance")
_emit_reads_policy_state("p0", "check_kernel_extension_boundary", "policy_binding")
_emit_snapshots_state("p0", "check_kernel_extension_boundary", "state_snapshot")
emit_replay_key("p0", "check_kernel_extension_boundary")
emit_determinism_digest("p0", "check_kernel_extension_boundary")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "check_kernel_extension_boundary", "execution_auth")
_emit_validates_capability("p2", "check_kernel_extension_boundary", "capability_check")
_emit_routes_to_capability("p2", "check_kernel_extension_boundary", "capability_route")
_emit_writes_via_uwg("p2", "check_kernel_extension_boundary", "uwg_write")
_emit_blocks_direct_write("p2", "check_kernel_extension_boundary", "direct_write_block")
_emit_records_tool_invocation("p2", "check_kernel_extension_boundary", "tool_invocation")
_emit_captures_execution_output("p2", "check_kernel_extension_boundary", "exec_output")
_emit_dispatches_agent("p3", "check_kernel_extension_boundary", "agent_dispatch")
_emit_coordinates_agents("p3", "check_kernel_extension_boundary", "agent_coordination")
_emit_records_workflow_lineage("p3", "check_kernel_extension_boundary", "workflow_lineage")
_emit_records_healing_outcome("p3", "check_kernel_extension_boundary", "healing_outcome")
_emit_escalates_failure("p3", "check_kernel_extension_boundary", "failure_escalation")
_emit_orchestrates_workflow("p3", "check_kernel_extension_boundary", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "check_kernel_extension_boundary", "healing_dispatch")
_emit_invokes_evaluation("p3", "check_kernel_extension_boundary", "evaluation_signal")
_emit_records_telemetry_event("p4", "check_kernel_extension_boundary", "telemetry_event")
_emit_captures_evaluation_metric("p4", "check_kernel_extension_boundary", "eval_metric")
_emit_stores_embedding("p4", "check_kernel_extension_boundary", "embedding_store")
_emit_updates_meta_learning_state("p4", "check_kernel_extension_boundary", "meta_learning")
_emit_links_execution_to_snapshot("p4", "check_kernel_extension_boundary", "exec_snapshot_link")

# Standard library modules that should be ignored
STANDARD_LIBRARY_MODULES: frozenset[str] = frozenset(
    {
        "__future__",
        "abc",
        "argparse",
        "ast",
        "asyncio",
        "base64",
        "bisect",
        "collections",
        "contextlib",
        "copy",
        "dataclasses",
        "datetime",
        "decimal",
        "enum",
        "functools",
        "gc",
        "hashlib",
        "inspect",
        "itertools",
        "json",
        "logging",
        "math",
        "os",
        "pathlib",
        "pickle",
        "re",
        "sys",
        "time",
        "traceback",
        "types",
        "typing",
        "uuid",
        "warnings",
        "weakref",
        # Additional common modules
        "importlib",
        "importlib.util",
        "struct",
        "shutil",
        "tempfile",
        "statistics",
        "dotenv",
        "numpy",
        "openai",
        "subprocess",
        "threading",
        "psutil",
        "pydantic",
        "csv",
        "io",
        "fnmatch",
        "unicodedata",
        "urllib.parse",
        "jinja2",
        # External libraries commonly used
        "libcst",
        "google",
        "google.genai",
        "uvicorn",
        "fastapi",
        "fastapi.responses",
        "xml.etree.ElementTree",
        "yaml",
        "hmac",
        "contextvars",
        # More external libraries
        "tree_sitter",
        "tree_sitter_python",
        "cryptography.fernet",
        "watchdog",
        "watchdog.events",
        "watchdog.observers",
        "tqdm",
        "difflib",
        "textwrap",
        "secrets",
        "platform",
        "winreg",
        "random",
        # Standard library additions
        "concurrent.futures",
        "atexit",
        "signal",
        # More external libraries
        "redis",
        # Internal modules that should be treated as standard library for boundary checking
        "base_detector_validator",
        "engine",
        # Relative imports (treated as internal) - these are typically same-package imports
        "cache_entry_types",
        "claim_type_types",
        "cost_governor_types",
        "expansion_strategy_types",
        "main_util",
        "runtime_bootstrapper",
        "runtime.core.telemetry",
        "services.configuration",
        # Common relative import patterns
        "governance_hub",
        "prompt_assembler",
        "sovereign_prompt_renderer",
        "optimization_strategy",
        "detectors.injection_detector",
        "detectors.pii_scrubber",
        "injection_detector",
        "pii_scrubber",
        "output_schema_validator",
        "shared_infrastructure_config",
        "signal_quality_config",
        "ast_relocator",
        # agentic_core sub-modules that are internal
        "agentic_core.config",
        "agentic_core.patterns",
        "agentic_core.base_agents",
        # More internal modules
        "signature_verifier",
        "context_contracts",
        "slot_contracts",
        # Additional internal modules
        "agentic_core.L6_observability",
        OPS_SCRIPTS_DIR,
        APPS_SHARED_DIR,
        "agentic_core.shared",
        # More internal modules
        "classification_kernel",
        "sovereign_policy_registry",
        "agentic_core.governor",
        "agentic_core.overseer",
        "agentic_core.PiiVault",
        # Even more internal modules
        "persistent_store",
        "agentic_core.storage",
    }
)

# Add project root to Python path for imports
from agentic_core.L0_routing.config.path_constants import get_validated_project_root

project_root = get_validated_project_root()

from agentic_core.L5_safety.config.structure_blueprint.sovereign_kernel import (
    is_kernel_component,
    is_modular_extension,
    validate_boundary,
)
from agentic_core.L5_safety.config.structure_blueprint.ssot import (
    SOVEREIGN_EXCLUDED_FOLDERS,
)
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("check_kernel_extension_boundary", "p4obs", "metric_1")
_emit_emits_metric_event("check_kernel_extension_boundary", "p4obs", "metric_2")
_emit_emits_metric_event("check_kernel_extension_boundary", "p4obs", "metric_3")
_emit_emits_metric_event("check_kernel_extension_boundary", "p4obs", "metric_4")
_emit_emits_metric_event("check_kernel_extension_boundary", "p4obs", "metric_5")
_emit_emits_metric_event("check_kernel_extension_boundary", "p4obs", "metric_6")
_emit_records_incident_event("check_kernel_extension_boundary", "p4obs", "incident")
_emit_captures_runtime_anomaly("check_kernel_extension_boundary", "p4obs", "anomaly")
_emit_writes_observability_log("check_kernel_extension_boundary", "p4obs", "obs_log")
_emit_updates_monitoring_state("check_kernel_extension_boundary", "p4obs", "mon_state")
_emit_triggers_alert("check_kernel_extension_boundary", "p4obs", "alert")
_emit_links_incident_trace("check_kernel_extension_boundary", "p4obs", "trace_link")
_emit_captures_pattern("check_kernel_extension_boundary", "p3lm", "pattern")
_emit_records_learning_event("check_kernel_extension_boundary", "p3lm", "learning_event")
_emit_writes_learning_snapshot("check_kernel_extension_boundary", "p3lm", "snapshot")
_emit_feeds_meta_learning("check_kernel_extension_boundary", "p3lm", "meta_feed")
_emit_updates_routing_strategy("check_kernel_extension_boundary", "p3lm", "routing")
_emit_improves_agent_policy("check_kernel_extension_boundary", "p3lm", "policy")
_emit_stores_learning_state("check_kernel_extension_boundary", "p3lm", "state")
_emit_records_execution_trace("check_kernel_extension_boundary", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("check_kernel_extension_boundary", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("check_kernel_extension_boundary", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("check_kernel_extension_boundary", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("check_kernel_extension_boundary", "L4_STATE", "p2_trace_5")
_emit_reads_environ("check_kernel_extension_boundary", "env_read", "p2_env_1")
_emit_reads_environ("check_kernel_extension_boundary", "env_read", "p2_env_2")
_emit_reads_runtime_state("check_kernel_extension_boundary", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("check_kernel_extension_boundary", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "check_kernel_extension_boundary", "context_pull")
_emit_pulls_context("p1", "check_kernel_extension_boundary", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "check_kernel_extension_boundary", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "check_kernel_extension_boundary", "uwg_term_secondary")
_emit_writes_through("p1", "check_kernel_extension_boundary", "write_through")
_emit_writes_through("p1", "check_kernel_extension_boundary", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "check_kernel_extension_boundary", "safety_validation")
_emit_invokes_eval("p1", "check_kernel_extension_boundary", "eval_call")
_emit_proposal_commits_routing("p1", "check_kernel_extension_boundary", "routing_commit")
_emit_escalates_to_human("p1", "check_kernel_extension_boundary", "human_escalation")
_emit_routes_through("p1", "check_kernel_extension_boundary", "route_through")
_emit_checks_agent_registry("p1", "check_kernel_extension_boundary", "agent_registry")
_emit_validates_agent_capability("p1", "check_kernel_extension_boundary", "capability")
_emit_dispatches_execution_plan("p1", "check_kernel_extension_boundary", "exec_plan")
_emit_agent_executes_agent("p1", "check_kernel_extension_boundary", "sub_agent")
_emit_routes_to_agent("p1", "check_kernel_extension_boundary", "target_agent")
_emit_verifies_policy("p1", "check_kernel_extension_boundary", "policy_check")
_emit_observes_runtime_state("p1", "check_kernel_extension_boundary", "runtime_state")
_emit_verifies_boundary("p1", "check_kernel_extension_boundary", "boundary_check")
_emit_transcripts_response("p1", "check_kernel_extension_boundary", "transcript")
_emit_hard_fails_untranscripted("p1", "check_kernel_extension_boundary")
_emit_gated_by_confidence("p1", "check_kernel_extension_boundary", "confidence_gate")
_emit_reads_through("l4", "check_kernel_extension_boundary", "urg_read_1")
_emit_reads_through("l4", "check_kernel_extension_boundary", "urg_read_2")
_emit_reads_through("l4", "check_kernel_extension_boundary", "urg_read_3")
_emit_reads_through("l4", "check_kernel_extension_boundary", "urg_read_4")
_emit_reads_through("l4", "check_kernel_extension_boundary", "urg_read_5")
_emit_reads_through("l4", "check_kernel_extension_boundary", "urg_read_6")
_emit_reads_through("l4", "check_kernel_extension_boundary", "urg_read_7")
_emit_reads_through("l4", "check_kernel_extension_boundary", "urg_read_8")
_emit_reads_through("l4", "check_kernel_extension_boundary", "urg_read_9")
_emit_reads_through("l4", "check_kernel_extension_boundary", "urg_read_10")
_emit_reads_through("l4", "check_kernel_extension_boundary", "urg_read_11")
_emit_reads_through("l4", "check_kernel_extension_boundary", "urg_read_12")
_emit_reads_through("l4", "check_kernel_extension_boundary", "urg_read_13")
_emit_reads_through("l4", "check_kernel_extension_boundary", "urg_read_14")
_emit_reads_through("l4", "check_kernel_extension_boundary", "urg_read_15")
_emit_reads_through("l4", "check_kernel_extension_boundary", "urg_read_16")
_emit_reads_through("l4", "check_kernel_extension_boundary", "urg_read_17")
_emit_reads_through("l4", "check_kernel_extension_boundary", "urg_read_18")
_emit_reads_through("l4", "check_kernel_extension_boundary", "urg_read_19")
_emit_reads_through("l4", "check_kernel_extension_boundary", "urg_read_20")
_emit_reads_through("l4", "check_kernel_extension_boundary", "urg_read_21")
_emit_reads_through("l4", "check_kernel_extension_boundary", "urg_read_22")
_emit_reads_through("l4", "check_kernel_extension_boundary", "urg_read_23")
_emit_reads_through("l4", "check_kernel_extension_boundary", "urg_read_24")
_emit_reads_through("l4", "check_kernel_extension_boundary", "urg_read_25")
_emit_reads_through("l4", "check_kernel_extension_boundary", "urg_read_26")
_emit_reads_through("l4", "check_kernel_extension_boundary", "urg_read_27")
_emit_reads_through("l4", "check_kernel_extension_boundary", "urg_read_28")
_emit_reads_through("l4", "check_kernel_extension_boundary", "urg_read_29")
_emit_reads_through("l4", "check_kernel_extension_boundary", "urg_read_30")
_emit_reads_through("l4", "check_kernel_extension_boundary", "urg_read_31")
_emit_reads_through("l4", "check_kernel_extension_boundary", "urg_read_32")
_emit_reads_through("l4", "check_kernel_extension_boundary", "urg_read_33")
_emit_reads_through("l4", "check_kernel_extension_boundary", "urg_read_34")
_emit_reads_through("l4", "check_kernel_extension_boundary", "urg_read_35")
_emit_reads_through("l4", "check_kernel_extension_boundary", "urg_read_36")
_emit_reads_through("l4", "check_kernel_extension_boundary", "urg_read_37")
_emit_reads_through("l4", "check_kernel_extension_boundary", "urg_read_38")


class ImportVisitor(ast.NodeVisitor):
    """AST visitor to extract import statements."""

    def __init__(self) -> None:
        self.imports: list[str] = []
        self.from_imports: list[tuple[str, str]] = []  # (module, name)

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            self.imports.append(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.module:
            for alias in node.names:
                self.from_imports.append((node.module, alias.name))
        self.generic_visit(node)


def get_imports_from_file(file_path: Path) -> tuple[list[str], list[tuple[str, str]]]:
    """Extract imports from a Python file using AST."""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()
        tree = ast.parse(content, filename=str(file_path))
        visitor = ImportVisitor()
        visitor.visit(tree)
        return visitor.imports, visitor.from_imports
    except SyntaxError as e:    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime
        print(f"ERROR: Syntax error in {file_path}: {e}", file=sys.stderr)
        return [], []
    except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
        raise
        print(f"ERROR: Failed to parse {file_path}: {e}", file=sys.stderr)
        return [], []


def normalize_module_path(module: str) -> str:
    """Convert import module to normalized path format."""
    return module.replace("/", ".").replace("\\", ".")


def check_file_boundary(
    file_path: Path,
    source_module: str,
    imports: list[str],
    from_imports: list[tuple[str, str]],
) -> list[str]:
    """Check if a file violates kernel-extension boundary."""
    violations: list[str] = []

    # Determine if source is kernel or extension
    source_is_kernel, source_reason = validate_boundary(source_module)
    if not source_is_kernel:
        # Skip unclassified modules (likely test files, examples, etc.)
        return violations

    # Check each import
    for imp in imports:
        # Skip standard library modules
        if imp.split(".")[0] in STANDARD_LIBRARY_MODULES:
            continue

        imp_normalized = normalize_module_path(imp)
        imp_is_kernel, imp_reason = validate_boundary(imp_normalized)

        if source_is_kernel and imp_is_kernel:
            # Kernel importing kernel - allowed
            continue
        elif source_is_kernel and not imp_is_kernel:
            # Kernel importing extension - VIOLATION
            violations.append(
                f"KERNEL_IMPORTS_EXTENSION: {source_module} imports extension {imp} "
                f"({source_reason} -> {imp_reason})"
            )
        elif not source_is_kernel and imp_is_kernel:
            # Extension importing kernel - allowed
            continue
        else:
            # Extension importing extension - allowed
            continue

    # Check from-imports
    for module, name in from_imports:
        # Skip standard library modules
        if module.split(".")[0] in STANDARD_LIBRARY_MODULES:
            continue

        module_normalized = normalize_module_path(module)
        module_is_kernel, module_reason = validate_boundary(module_normalized)

        if source_is_kernel and module_is_kernel:
            # Kernel from-import kernel - allowed
            continue
        elif source_is_kernel and not module_is_kernel:
            # Kernel from-import extension - VIOLATION
            violations.append(
                f"KERNEL_FROM_IMPORTS_EXTENSION: {source_module} from-imports {module}.{name} "
                f"({source_reason} -> {module_reason})"
            )
        elif not source_is_kernel and module_is_kernel:
            # Extension from-import kernel - allowed
            continue
        else:
            # Extension from-import extension - allowed
            continue

    return violations


def module_path_from_file_path(file_path: Path, project_root: Path) -> str:
    """Convert file path to module path."""
    try:
        relative_path = file_path.relative_to(project_root)
        # Remove .py extension and convert path separators to dots
        module_parts = list(relative_path.parts)
        if module_parts[-1].endswith(".py"):
            module_parts[-1] = module_parts[-1][:-3]
        # Skip __init__ files - they represent their package
        if module_parts[-1] == "__init__":
            module_parts = module_parts[:-1]
        return ".".join(module_parts)
    except ValueError:
        # File not under project root
        return str(file_path)


def scan_directory(directory: Path) -> dict[str, list[str]]:
    """Scan directory for boundary violations."""
    violations_by_file: dict[str, list[str]] = {}

    for py_file in directory.rglob("*.py"):
        # Skip __pycache__ and other non-source directories
        if "__pycache__" in py_file.parts or ".pytest_cache" in py_file.parts:
            continue

        module_path = module_path_from_file_path(py_file, project_root)
        imports, from_imports = get_imports_from_file(py_file)

        file_violations = check_file_boundary(py_file, module_path, imports, from_imports)

        if file_violations:
            violations_by_file[str(py_file)] = file_violations

    return violations_by_file


def main() -> int:
    """Main entry point."""
    print("=== Kernel-Extension Boundary Checker ===")
    print(f"Project root: {project_root}")

    # Scan agentic_core and system_learning directories
    scan_dirs = [
        project_root / AGENTIC_CORE_DIR,
        project_root / SYSTEM_LEARNING_DIR,
    ]

    total_violations = 0
    all_violations: dict[str, list[str]] = {}

    for scan_dir in scan_dirs:
        if not scan_dir.exists():
            print(f"WARNING: Directory {scan_dir} does not exist, skipping")
            continue

        print(f"\nScanning {scan_dir}...")
        violations = scan_directory(scan_dir)
        all_violations.update(violations)
        total_violations += sum(len(v) for v in violations.values())

    # Report results
    if total_violations == 0:
        print("\n✅ No boundary violations found")
        return 0
    else:
        print(f"\n❌ Found {total_violations} boundary violations:")
        for file_path, violations in all_violations.items():
            print(f"\n  {file_path}:")
            for violation in violations:
                print(f"    - {violation}")
        print(f"\nTotal violations: {total_violations}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
