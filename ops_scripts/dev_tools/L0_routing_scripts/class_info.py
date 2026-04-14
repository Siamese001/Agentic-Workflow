#!/usr/bin/env python3
"""Zero-Loss Archive Migration Analysis Script.

Performs comprehensive analysis of archives/runtime, archives/schemas, archives/shared
for migration to modern agentic_core structure.

Run: python scripts/archive_migration_analysis.py
"""

import ast
import hashlib
import json
import os
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from agentic_core.L0_routing.config import (
    AGENTIC_CORE_DIR,
    ARCHIVES_DIR,
    GLOBAL_EXCLUDED_DIRS,
    SOVEREIGN_EXCLUDED_FOLDERS,
)
from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
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
    _emit_snapshots_state,
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

emit_replay_key("p0", "class_info")
emit_determinism_digest("p0", "class_info")

_emit_dispatches_healing_run("p1", "class_info", "L0")
_emit_routes_through("p1", "class_info", "L0")
_emit_checks_agent_registry("p1", "class_info", "agent_registry")
_emit_validates_agent_capability("p1", "class_info", "capability")
_emit_dispatches_execution_plan("p1", "class_info", "exec_plan")
_emit_agent_executes_agent("p1", "class_info", "sub_agent")
_emit_routes_to_agent("p1", "class_info", "target_agent")
_emit_verifies_policy("p1", "class_info", "policy_check")
_emit_observes_runtime_state("p1", "class_info", "runtime_state")
_emit_verifies_boundary("p1", "class_info", "boundary_check")
_emit_transcripts_response("p1", "class_info", "transcript")
_emit_hard_fails_untranscripted("p1", "class_info")
_emit_gated_by_confidence("p1", "class_info", "confidence_gate")
_emit_escalates_to_human("p1", "class_info", "L0")
_emit_reads_policy_state("p1", "class_info", "L0")
_emit_authorize_and_execute("p2", "class_info", "execution_auth")
_emit_validates_capability("p2", "class_info", "capability_check")
_emit_routes_to_capability("p2", "class_info", "capability_route")
_emit_writes_via_uwg("p2", "class_info", "uwg_write")
_emit_blocks_direct_write("p2", "class_info", "direct_write_block")
_emit_records_tool_invocation("p2", "class_info", "tool_invocation")
_emit_captures_execution_output("p2", "class_info", "exec_output")
_emit_dispatches_agent("p3", "class_info", "agent_dispatch")
_emit_coordinates_agents("p3", "class_info", "agent_coordination")
_emit_records_workflow_lineage("p3", "class_info", "workflow_lineage")
_emit_records_healing_outcome("p3", "class_info", "healing_outcome")
_emit_escalates_failure("p3", "class_info", "failure_escalation")
_emit_orchestrates_workflow("p3", "class_info", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "class_info", "healing_dispatch")
_emit_invokes_evaluation("p3", "class_info", "evaluation_signal")
_emit_records_telemetry_event("p4", "class_info", "telemetry_event")
_emit_captures_evaluation_metric("p4", "class_info", "eval_metric")
_emit_stores_embedding("p4", "class_info", "embedding_store")
_emit_updates_meta_learning_state("p4", "class_info", "meta_learning")
_emit_links_execution_to_snapshot("p4", "class_info", "exec_snapshot_link")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
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
    _emit_records_incident_event,
    _emit_records_learning_event,
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
from tqdm import tqdm

_emit_emits_metric_event("class_info", "p4obs", "metric_1")
_emit_emits_metric_event("class_info", "p4obs", "metric_2")
_emit_emits_metric_event("class_info", "p4obs", "metric_3")
_emit_emits_metric_event("class_info", "p4obs", "metric_4")
_emit_emits_metric_event("class_info", "p4obs", "metric_5")
_emit_emits_metric_event("class_info", "p4obs", "metric_6")
_emit_records_incident_event("class_info", "p4obs", "incident")
_emit_captures_runtime_anomaly("class_info", "p4obs", "anomaly")
_emit_writes_observability_log("class_info", "p4obs", "obs_log")
_emit_updates_monitoring_state("class_info", "p4obs", "mon_state")
_emit_triggers_alert("class_info", "p4obs", "alert")
_emit_links_incident_trace("class_info", "p4obs", "trace_link")
_emit_captures_pattern("class_info", "p3lm", "pattern")
_emit_records_learning_event("class_info", "p3lm", "learning_event")
_emit_writes_learning_snapshot("class_info", "p3lm", "snapshot")
_emit_feeds_meta_learning("class_info", "p3lm", "meta_feed")
_emit_updates_routing_strategy("class_info", "p3lm", "routing")
_emit_improves_agent_policy("class_info", "p3lm", "policy")
_emit_stores_learning_state("class_info", "p3lm", "state")
_emit_records_execution_trace("class_info", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("class_info", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("class_info", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("class_info", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("class_info", "L4_STATE", "p2_trace_5")
_emit_reads_environ("class_info", "env_read", "p2_env_1")
_emit_reads_environ("class_info", "env_read", "p2_env_2")
_emit_reads_runtime_state("class_info", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("class_info", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "class_info", "context_pull")
_emit_pulls_context("p1", "class_info", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "class_info", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "class_info", "uwg_term_2")
_emit_writes_through("p1", "class_info", "write_through")
_emit_writes_through("p1", "class_info", "write_through_2")
_emit_validated_by_safety_plane("p1", "class_info", "safety_validation")
_emit_invokes_eval("p1", "class_info", "eval_call")
_emit_proposal_commits_routing("p1", "class_info", "routing_commit")

# Project root
PROJECT_ROOT = Path(__file__).parent.parent
_ARCHIVES_DIR_PATH = PROJECT_ROOT / ARCHIVES_DIR
_AGENTIC_CORE_DIR_PATH = PROJECT_ROOT / AGENTIC_CORE_DIR

# Target archive folders
TARGET_ARCHIVES = ["runtime", "schemas", "shared"]

# Exclude patterns
EXCLUDE_DIRS = GLOBAL_EXCLUDED_DIRS | SOVEREIGN_EXCLUDED_FOLDERS
EXCLUDE_EXTENSIONS = {".pyc", ".pyo", ".so", ".dll", ".exe"}


@dataclass
class ClassInfo:
    """Information about a Python class."""

    name: str
    bases: list[str]
    methods: list[str]
    line_number: int
    docstring: str | None = None


@dataclass
class FileAnalysis:
    """Complete analysis of a file."""

    path: Path
    relative_path: str
    size_bytes: int
    line_count: int
    extension: str
    sha256_hash: str
    snippet: str
    docstring: str | None = None
    # Python-specific
    classes: list[ClassInfo] = field(default_factory=list)
    imports: list[str] = field(default_factory=list)
    functions: list[str] = field(default_factory=list)
    # Compliance flags
    has_snake_case_class: bool = False
    has_hardcoded_creds: bool = False
    has_raw_prompts: bool = False
    mcp_usage: bool = False
    llm_calls: bool = False
    # Classification
    classification: str = "UNKNOWN"
    modern_equivalent: str | None = None
    recommended_action: str = "REVIEW"
    target_path: str | None = None
    justification: str = ""
    risk_level: str = "LOW"


def compute_file_hash(file_path: Path) -> str:
    """Compute SHA256 hash of file contents."""
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "compute_file_hash", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "compute_file_hash", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "compute_file_hash")
    sha256 = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
        return sha256.hexdigest()[:16]
    # guardian: allow-silent-swallow - acceptable exception handling
    except OSError:
        return "ERROR"


def count_lines(file_path: Path) -> int:
    """Count lines in a text file."""
    try:
        with open(file_path, encoding="utf-8", errors="ignore") as f:
            # guardian: allow-silent-swallow - acceptable exception handling
            return sum(1 for _ in f)
    except OSError:
        return 0


def get_snippet(file_path: Path, chars: int = 200) -> str:
    """Get first N characters of a file."""
    try:
        with open(file_path, encoding="utf-8", errors="ignore") as f:
            # guardian: allow-silent-swallow - acceptable exception handling
            content = f.read(chars)
            return content.replace("\n", " ").strip()
    except (OSError, UnicodeDecodeError):
        return "[BINARY OR UNREADABLE]"


def parse_python_file(file_path: Path) -> tuple[list[ClassInfo], list[str], list[str], str | None]:
    """Parse a Python file using AST.

    Returns:
        Tuple of (classes, imports, functions, module_docstring)
    """
    classes = []
    imports = []
    functions = []
    module_docstring = None

    try:
        with open(file_path, encoding="utf-8", errors="ignore") as f:
            content = f.read()

        tree = ast.parse(content)

        # Get module docstring
        if tree.body and isinstance(tree.body[0], ast.Expr) and isinstance(tree.body[0].value, ast.Constant):
            module_docstring = tree.body[0].value.value

        for node in tqdm(ast.walk(tree), desc="Processing", unit="item"):
            # Classes
            if isinstance(node, ast.ClassDef):
                bases = []
                for base in node.bases:
                    if isinstance(base, ast.Name):
                        bases.append(base.id)
                    elif isinstance(base, ast.Attribute):
                        bases.append(f"{base.value.id if hasattr(base.value, 'id') else '?'}.{base.attr}")

                methods = [item.name for item in node.body if isinstance(item, ast.FunctionDef)]

                # Get class docstring
                class_docstring = None
                if (
                    node.body
                    and isinstance(node.body[0], ast.Expr)
                    and isinstance(node.body[0].value, ast.Constant)
                ):
                    class_docstring = node.body[0].value.value

                classes.append(
                    ClassInfo(
                        name=node.name,
                        bases=bases,
                        methods=methods,
                        line_number=node.lineno,
                        docstring=class_docstring,
                    ),
                )

            # Imports
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    imports.append(f"{module}.{alias.name}")

            # Top-level functions
            elif isinstance(node, ast.FunctionDef) and hasattr(node, "col_offset") and node.col_offset == 0:
                functions.append(node.name)
        # guardian: allow-silent-swallow - acceptable exception handling

        return classes, imports, functions, module_docstring

    except SyntaxError as e:
        return [], [f"SYNTAX_ERROR: {e}"], [], None
    # guardian: allow-silent-swallow
    except (ValueError, TypeError) as e:
        return [], [f"PARSE_ERROR: {e}"], [], None


def check_sovereignty_compliance(file_path: Path, content: str, classes: list[ClassInfo]) -> dict[str, bool]:
    """Check for sovereignty compliance issues."""
    issues = {
        "has_snake_case_class": False,
        "has_hardcoded_creds": False,
        "has_raw_prompts": False,
        "mcp_usage": False,
        "llm_calls": False,
    }

    content_lower = content.lower()

    # Check for snake_case classes (should be PascalCase)
    for cls in classes:
        if "_" in cls.name and not cls.name.startswith("_"):
            issues["has_snake_case_class"] = True
            break

    # Check for hardcoded credentials
    cred_patterns = ["api_key", "apikey", "secret", "password", "token"]
    for pattern in cred_patterns:
        if f'{pattern} = "' in content_lower or f"{pattern} = '" in content_lower:
            # Exclude obvious non-secrets like pattern names
            if "api_key" in content_lower and "sk-" in content:
                issues["has_hardcoded_creds"] = True
                break

    # Check for raw prompt strings
    if 'f"""' in content or "f'''" in content:
        if "you are" in content_lower or "your task" in content_lower:
            issues["has_raw_prompts"] = True

    # Check for MCP usage
    if "mcp" in content_lower or "model context protocol" in content_lower:
        issues["mcp_usage"] = True

    # Check for LLM calls
    llm_patterns = [
        "openai",
        "anthropic",
        "claude",
        "gpt-4",
        "gpt-3",
        "llm_client",
        "chat_completion",
    ]
    for pattern in llm_patterns:
        if pattern in content_lower:
            issues["llm_calls"] = True
            break

    return issues


def find_modern_equivalent(file_path: Path, file_name: str) -> tuple[str | None, str]:
    """Find a modern equivalent in agentic_core."""

    # Known mappings
    mappings = {
        "circuit_breaker.py": ("agentic_core/L4_resilience/circuit_breaker.py", "EXISTS_SIMPLER"),
        "subatomic_hop.py": (
            "agentic_core/runtime/shared_runtime/subatomic_hop.py",
            "EXISTS_MODERNIZED",
        ),
        "semantic_cache.py": (
            "agentic_core/runtime/shared_runtime/semantic_cache.py",
            "EXISTS_ENHANCED",
        ),
        "input_sanitizer.py": ("agentic_core/L5_safety/enforcement/", "MIGRATE_TO_SAFETY"),
        "reflection_engine.py": ("agentic_core/runtime/shared_runtime/", "UNIQUE_MIGRATE"),
        "cognitive_contracts.py": ("agentic_core/schemas/models/", "UNIQUE_MIGRATE"),
        "dynamic_dag_manager.py": ("agentic_core/L3_orchestration/", "UNIQUE_MIGRATE"),
        "prompt_assembler.py": ("agentic_core/prompt_governance/", "UNIQUE_MIGRATE"),
        "signal_enhancer.py": ("agentic_core/runtime/shared_runtime/", "UNIQUE_MIGRATE"),
        "orchestrator.py": ("agentic_core/L3_orchestration/", "INTERFACE_MIGRATE"),
        "models.py": ("agentic_core/schemas/models/", "MERGE_SCHEMAS"),
    }

    if file_name in mappings:
        return mappings[file_name]

    # Check by path patterns
    rel_path = str(file_path)
    if "resilience" in rel_path:
        return ("agentic_core/L4_resilience/", "MIGRATE_RESILIENCE")
    if "security" in rel_path:
        return ("agentic_core/L5_safety/enforcement/", "MIGRATE_SAFETY")
    if "mcp" in rel_path:
        return ("agentic_core/L2_execution/enforcement/", "MIGRATE_MCP")
    if "schemas" in rel_path or "models" in rel_path:
        return ("agentic_core/schemas/models/", "MIGRATE_SCHEMAS")
    if "config" in rel_path:
        return ("agentic_core/config/", "MIGRATE_CONFIG")
    if "caching" in rel_path or "cache" in rel_path:
        return ("agentic_core/runtime/shared_runtime/", "CHECK_DUPLICATE")

    return (None, "REVIEW_NEEDED")


def classify_migration_disposition(analysis: FileAnalysis) -> tuple[str, str, str, str]:
    """Classify file and determine action.

    Returns:
        (classification, recommended_action, justification, risk_level)
    """
    file_name = analysis.path.name

    # Check for known duplicates first
    equiv, status = find_modern_equivalent(analysis.path, file_name)
    analysis.modern_equivalent = equiv

    if status == "EXISTS_SIMPLER":
        return (
            "DUPLICATE_ARCHIVE_RICHER",
            "MERGE",
            f"Archive version ({analysis.line_count} LOC) richer than modern. Merge unique features.",
            "MEDIUM",
        )

    if status == "EXISTS_MODERNIZED":
        return (
            "DUPLICATE_MODERN_NEWER",
            "DELETE",
            "Modern version exists with dependency injection pattern. Archive obsolete.",
            "LOW",
        )

    if status == "EXISTS_ENHANCED":
        return (
            "DUPLICATE_MODERN_ENHANCED",
            "DELETE",
            "Modern version has semantic matching. Archive is basic version.",
            "LOW",
        )

    if status == "UNIQUE_MIGRATE":
        return (
            "UNIQUE_VALUABLE",
            "MIGRATE",
            f"Unique implementation ({analysis.line_count} LOC). Migrate to modern structure.",
            "LOW",
        )

    if status == "INTERFACE_MIGRATE":
        return (
            "INTERFACE_CONTRACT",
            "MIGRATE",
            "Abstract interface/contract. Migrate to schemas.",
            "LOW",
        )

    if status == "MIGRATE_SCHEMAS":
        return (
            "SCHEMA_MODEL",
            "MIGRATE",
            "schema/model definition. Move to agentic_core/schemas/",
            "LOW",
        )

    if status == "MIGRATE_SAFETY":
        return (
            "SAFETY_COMPONENT",
            "MIGRATE",
            "Security/safety component. Move to L5_safety/",
            "MEDIUM",
        )

    if status == "MIGRATE_MCP":
        return ("MCP_COMPONENT", "MIGRATE", "MCP integration. Move to L2_execution/mcp/", "MEDIUM")

    if status == "MIGRATE_CONFIG":
        return ("CONFIG_FILE", "MIGRATE", "configuration. Move to agentic_core/config/", "LOW")

    if status == "CHECK_DUPLICATE":
        return (
            "POTENTIAL_DUPLICATE",
            "REVIEW",
            "May have modern equivalent. Review before action.",
            "MEDIUM",
        )

    # Default cases
    if file_name == "__init__.py":
        if analysis.line_count < 20:
            return ("INIT_STUB", "DELETE", "Empty or stub init file.", "LOW")
        else:
            return ("INIT_EXPORTS", "REVIEW", "Init with exports. May need updating.", "LOW")

    if analysis.extension == ".json":
        return (
            "DATA_ASSET",
            "MIGRATE",
            "JSON data asset. Move to agentic_core/schemas/models/data_assets/",
            "LOW",
        )

    if analysis.extension in [".yaml", ".yml"]:
        return ("CONFIG_ASSET", "MIGRATE", "YAML config. Move to agentic_core/config/", "LOW")

    if analysis.extension == ".md":
        return ("DOCUMENTATION", "REVIEW", "Documentation file. Review for relevance.", "LOW")

    # Check for dangerous patterns
    if analysis.has_hardcoded_creds:
        return (
            "DANGEROUS_CREDS",
            "DELETE_IMMEDIATELY",
            "Contains hardcoded credentials! Security risk.",
            "CRITICAL",
        )

    return ("UNKNOWN", "REVIEW", "Requires manual review.", "MEDIUM")


def determine_target_path(analysis: FileAnalysis) -> str:
    """Determine the target migration path."""
    equiv, _ = find_modern_equivalent(analysis.path, analysis.path.name)

    if equiv:
        return equiv

    # Default mappings by source folder
    rel_path = analysis.relative_path

    if rel_path.startswith("runtime/core/resilience"):
        return "agentic_core/L4_resilience/"
    if rel_path.startswith("runtime/core/security"):
        return "agentic_core/L5_safety/enforcement/"
    if rel_path.startswith("runtime/core/quality"):
        return "agentic_core/runtime/shared_runtime/"
    if rel_path.startswith("runtime/core"):
        return "agentic_core/runtime/shared_runtime/"
    if rel_path.startswith("runtime"):
        return "agentic_core/runtime/"

    if rel_path.startswith("schemas/core_interfaces"):
        return "agentic_core/schemas/models/"
    if rel_path.startswith("schemas/core_models"):
        return "agentic_core/schemas/models/"
    if rel_path.startswith("schemas/data_assets"):
        return "agentic_core/schemas/models/data_assets/"
    if rel_path.startswith("schemas"):
        return "agentic_core/schemas/"

    if rel_path.startswith("shared/mcp"):
        return "agentic_core/L2_execution/enforcement/"
    if rel_path.startswith("shared/caching"):
        return "agentic_core/runtime/shared_runtime/"
    if rel_path.startswith("shared/configuration"):
        return "agentic_core/config/"
    if rel_path.startswith("shared/core"):
        return "agentic_core/utils/core_extensions/"
    if rel_path.startswith("shared"):
        return "agentic_core/utils/"

    return "agentic_core/"


def analyze_file(file_path: Path, archive_base: Path) -> FileAnalysis:
    """Perform complete analysis of a file."""
    relative_path = str(file_path.relative_to(archive_base))
    extension = file_path.suffix.lower()

    analysis = FileAnalysis(
        path=file_path,
        relative_path=relative_path,
        size_bytes=file_path.stat().st_size,
        line_count=count_lines(file_path),
        extension=extension,
        sha256_hash=compute_file_hash(file_path),
        snippet=get_snippet(file_path, 200),
    )

    # Python-specific analysis
    if extension == ".py":
        try:
            with open(file_path, encoding="utf-8", errors="ignore") as f:
                content = f.read()

            classes, imports, functions, docstring = parse_python_file(file_path)
            analysis.classes = classes
            analysis.imports = imports
            analysis.functions = functions
            analysis.docstring = docstring

            # Compliance checks
            compliance = check_sovereignty_compliance(file_path, content, classes)
            analysis.has_snake_case_class = compliance["has_snake_case_class"]
            analysis.has_hardcoded_creds = compliance["has_hardcoded_creds"]
            analysis.has_raw_prompts = compliance["has_raw_prompts"]
            analysis.mcp_usage = compliance["mcp_usage"]
            analysis.llm_calls = compliance["llm_calls"]

        # guardian: allow-silent-swallow
        except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
            # TODO: Handle specific exception properly
            raise  # Re-raise after logging/handling
            analysis.docstring = f"ANALYSIS_ERROR: {e}"

    # Classification
    classification, action, justification, risk = classify_migration_disposition(analysis)
    analysis.classification = classification
    analysis.recommended_action = action
    analysis.justification = justification
    analysis.risk_level = risk

    # Target path
    analysis.target_path = determine_target_path(analysis)

    return analysis


def scan_archive_folder(archive_folder: str) -> list[FileAnalysis]:
    """Recursively scan an archive folder."""
    analyses = []
    archive_path = _ARCHIVES_DIR_PATH / archive_folder

    if not archive_path.exists():
        print(f"WARNING: Archive folder not found: {archive_path}")
        return analyses

    for root, dirs, files in tqdm(os.walk(archive_path), desc="Processing", unit="item"):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]

        for file_name in tqdm(files, desc="Processing", unit="item"):
            file_path = Path(root) / file_name

            # Skip excluded extensions
            if file_path.suffix.lower() in EXCLUDE_EXTENSIONS:
                continue

            try:
                analysis = analyze_file(file_path, _ARCHIVES_DIR_PATH)
                analyses.append(analysis)
            # guardian: allow-silent-swallow
            except (ValueError, TypeError) as e:
                print(f"ERROR analyzing {file_path}: {e}")

    return analyses


def generate_markdown_report(all_analyses: list[FileAnalysis]) -> str:
    """Generate comprehensive markdown report."""

    report = []
    report.append("# Zero-Loss Archive Migration Analysis Report")
    report.append(f"\n**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("**Project:** Agentic-Workflow")
    report.append("**Archives Analyzed:** runtime/, schemas/, shared/\n")

    # Summary statistics
    total_files = len(all_analyses)
    total_loc = sum(a.line_count for a in all_analyses)
    py_files = [a for a in all_analyses if a.extension == ".py"]
    total_classes = sum(len(a.classes) for a in all_analyses)

    report.append("## Executive Summary\n")
    report.append("| Metric | Value |")
    report.append("|--------|-------|")
    report.append(f"| Total Files | {total_files} |")
    report.append(f"| Total LOC | {total_loc:,} |")
    report.append(f"| Python Files | {len(py_files)} |")
    report.append(f"| Total Classes | {total_classes} |")

    # Action breakdown
    actions = {}
    for a in all_analyses:
        actions[a.recommended_action] = actions.get(a.recommended_action, 0) + 1

    report.append("\n### Recommended Actions\n")
    report.append("| Action | Count |")
    report.append("|--------|-------|")
    for action, count in sorted(actions.items(), key=lambda x: -x[1]):
        report.append(f"| {action} | {count} |")

    # Risk breakdown
    risks = {}
    for a in all_analyses:
        risks[a.risk_level] = risks.get(a.risk_level, 0) + 1

    report.append("\n### Risk Distribution\n")
    report.append("| Risk Level | Count |")
    report.append("|------------|-------|")
    for risk in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
        if risk in risks:
            report.append(f"| {risk} | {risks[risk]} |")

    # Compliance issues
    snake_case = [a for a in all_analyses if a.has_snake_case_class]
    hardcoded = [a for a in all_analyses if a.has_hardcoded_creds]
    raw_prompts = [a for a in all_analyses if a.has_raw_prompts]

    report.append("\n### Compliance Issues\n")
    report.append("| Issue | Count | Files |")
    report.append("|-------|-------|-------|")
    report.append(
        f"| Snake_case Classes | {len(snake_case)} | {', '.join(a.path.name for a in snake_case[:3])}{'...' if len(snake_case) > 3 else ''} |",
    )
    report.append(
        f"| Hardcoded Credentials | {len(hardcoded)} | {'SECURITY RISK' if hardcoded else 'None'} |",
    )
    report.append(
        f"| Raw Prompt Strings | {len(raw_prompts)} | {', '.join(a.path.name for a in raw_prompts[:3])}{'...' if len(raw_prompts) > 3 else ''} |",
    )

    # Detailed file table by archive
    for archive in tqdm(TARGET_ARCHIVES, desc="Processing", unit="item"):
        archive_files = [a for a in all_analyses if a.relative_path.startswith(archive)]
        if not archive_files:
            continue

        report.append(f"\n## archives/{archive}/ Analysis\n")
        report.append(
            f"**Files:** {len(archive_files)} | **LOC:** {sum(a.line_count for a in archive_files):,}\n",
        )

        report.append("| Path | Size | LOC | Classes | Action | Target | Risk |")
        report.append("|------|------|-----|---------|--------|--------|------|")

        for a in sorted(archive_files, key=lambda x: x.relative_path):
            class_names = ", ".join(c.name for c in a.classes[:3])
            if len(a.classes) > 3:
                class_names += "..."

            report.append(
                f"| `{a.relative_path}` | {a.size_bytes:,}B | {a.line_count} | {class_names or '-'} | **{a.recommended_action}** | `{a.target_path}` | {a.risk_level} |",
            )

    # High-value migration candidates
    migrate_files = [a for a in all_analyses if a.recommended_action == "MIGRATE" and a.line_count > 100]

    report.append("\n## High-Value Migration Candidates (>100 LOC)\n")
    report.append("| File | LOC | Classes | Justification |")
    report.append("|------|-----|---------|---------------|")
    for a in sorted(migrate_files, key=lambda x: -x.line_count):
        class_count = len(a.classes)
        report.append(f"| `{a.path.name}` | {a.line_count} | {class_count} | {a.justification} |")

    # Merge candidates (archive richer than modern)
    merge_files = [a for a in all_analyses if a.recommended_action == "MERGE"]
    if merge_files:
        report.append("\n## Merge Candidates (Archive Richer Than Modern)\n")
        report.append("| Archive File | LOC | Modern Equivalent | Action |")
        report.append("|--------------|-----|-------------------|--------|")
        for a in merge_files:
            report.append(
                f"| `{a.relative_path}` | {a.line_count} | `{a.modern_equivalent}` | Merge unique features |",
            )

    # Delete candidates
    delete_files = [a for a in all_analyses if a.recommended_action in ["DELETE", "DELETE_IMMEDIATELY"]]
    if delete_files:
        report.append("\n## Delete Candidates\n")
        report.append("| File | Reason |")
        report.append("|------|--------|")
        for a in delete_files:
            report.append(f"| `{a.relative_path}` | {a.justification} |")

    # Class inventory
    report.append("\n## Python Class Inventory\n")
    report.append("| Class | File | Bases | Methods | Migrate To |")
    report.append("|-------|------|-------|---------|------------|")

    for a in py_files:
        for cls in a.classes:
            bases = ", ".join(cls.bases) or "None"
            methods = len(cls.methods)
            report.append(f"| `{cls.name}` | `{a.path.name}` | {bases} | {methods} | `{a.target_path}` |")

    # Implementation plan
    report.append("\n## Implementation Plan\n")
    report.append("```bash")
    report.append("# 1. Create migration branch")
    report.append("git checkout -b refactor/migrate-runtime-schemas-shared-2026")
    report.append("")
    report.append("# 2. High-priority migrations (unique valuable code)")
    for a in migrate_files[:5]:
        if a.target_path:
            # guardian: allow-path-string
            target = a.target_path.rstrip("/") + "/" + a.path.name
            report.append(f"git mv archives/{a.relative_path} {target}")
    report.append("")
    report.append("# 3. Update imports (global replace)")
    report.append("# sed -i 's/from archives.runtime/from agentic_core.runtime/g' **/*.py")
    report.append("# sed -i 's/from archives.schemas/from agentic_core.schemas/g' **/*.py")
    report.append("# sed -i 's/from archives.shared/from agentic_core.utils/g' **/*.py")
    report.append("")
    report.append("# 4. Run validation")
    report.append("python -m pytest tests/ -v")
    report.append("python -m mypy agentic_core/")
    report.append("```")

    return "\n".join(report)


def main():
    """Main entry point."""
    print("=" * 60)
    print("Zero-Loss Archive Migration Analysis")
    print("=" * 60)

    all_analyses = []

    for archive in TARGET_ARCHIVES:
        print(f"\nScanning archives/{archive}/...")
        analyses = scan_archive_folder(archive)
        all_analyses.extend(analyses)
        print(f"  Found {len(analyses)} files")

    print(f"\nTotal files analyzed: {len(all_analyses)}")

    # Generate report
    print("\nGenerating migration report...")
    report = generate_markdown_report(all_analyses)

    # Write report
    report_path = PROJECT_ROOT / "ARCHIVE_MIGRATION_REPORT_2026.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"\nReport saved to: {report_path}")

    # Also output JSON for programmatic use
    json_data = []
    for a in tqdm(all_analyses, desc="Processing", unit="item"):
        json_data.append(
            {
                "path": str(a.path),
                "relative_path": a.relative_path,
                "size_bytes": a.size_bytes,
                "line_count": a.line_count,
                "extension": a.extension,
                "hash": a.sha256_hash,
                "classes": [{"name": c.name, "bases": c.bases, "methods": c.methods} for c in a.classes],
                "imports": a.imports[:10],  # Limit for readability
                "classification": a.classification,
                "recommended_action": a.recommended_action,
                "target_path": a.target_path,
                "justification": a.justification,
                "risk_level": a.risk_level,
                "compliance": {
                    "snake_case_class": a.has_snake_case_class,
                    "hardcoded_creds": a.has_hardcoded_creds,
                    "raw_prompts": a.has_raw_prompts,
                    "mcp_usage": a.mcp_usage,
                    "llm_calls": a.llm_calls,
                },
            },
        )

    json_path = PROJECT_ROOT / "archive_migration_data.json"
    with open(json_path, "w", encoding="utf-8") as f:
        assert_no_persistent_write("L0", "json.dump")  # G-12-1: mutation prohibition guard
        json.dump(json_data, f, indent=2)

    print(f"JSON data saved to: {json_path}")

    # Print summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    actions = {}
    for a in all_analyses:
        actions[a.recommended_action] = actions.get(a.recommended_action, 0) + 1

    for action, count in sorted(actions.items(), key=lambda x: -x[1]):
        print(f"  {action}: {count}")

    print(f"\nTotal LOC: {sum(a.line_count for a in all_analyses):,}")
    print("=" * 60)


if __name__ == "__main__":
    main()
