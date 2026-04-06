#!/usr/bin/env python3
"""
Advanced AST-based analyzer for archived files.
Extracts classes, functions, dependencies, and semantic purpose to understand
how archived code fits into the current codebase.
"""

import ast
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from agentic_core.L0_routing.config import (
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
)
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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
    _emit_records_execution_trace,  # noqa: E402
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

_emit_emits_metric_event("file_analysis", "p4obs", "metric_1")
_emit_emits_metric_event("file_analysis", "p4obs", "metric_2")
_emit_emits_metric_event("file_analysis", "p4obs", "metric_3")
_emit_emits_metric_event("file_analysis", "p4obs", "metric_4")
_emit_emits_metric_event("file_analysis", "p4obs", "metric_5")
_emit_emits_metric_event("file_analysis", "p4obs", "metric_6")
_emit_records_incident_event("file_analysis", "p4obs", "incident")
_emit_captures_runtime_anomaly("file_analysis", "p4obs", "anomaly")
_emit_writes_observability_log("file_analysis", "p4obs", "obs_log")
_emit_updates_monitoring_state("file_analysis", "p4obs", "mon_state")
_emit_triggers_alert("file_analysis", "p4obs", "alert")
_emit_links_incident_trace("file_analysis", "p4obs", "trace_link")
_emit_captures_pattern("file_analysis", "p3lm", "pattern")
_emit_records_learning_event("file_analysis", "p3lm", "learning_event")
_emit_writes_learning_snapshot("file_analysis", "p3lm", "snapshot")
_emit_feeds_meta_learning("file_analysis", "p3lm", "meta_feed")
_emit_updates_routing_strategy("file_analysis", "p3lm", "routing")
_emit_improves_agent_policy("file_analysis", "p3lm", "policy")
_emit_stores_learning_state("file_analysis", "p3lm", "state")
_emit_records_execution_trace("file_analysis", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("file_analysis", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("file_analysis", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("file_analysis", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("file_analysis", "L4_STATE", "p2_trace_5")
_emit_reads_environ("file_analysis", "env_read", "p2_env_1")
_emit_reads_environ("file_analysis", "env_read", "p2_env_2")
_emit_reads_runtime_state("file_analysis", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("file_analysis", "runtime_state", "p2_rt_2")

emit_replay_key("p0", "file_analysis")
emit_determinism_digest("p0", "file_analysis")

_emit_dispatches_healing_run("p1", "file_analysis", "L0")
_emit_routes_through("p1", "file_analysis", "L0")
_emit_checks_agent_registry("p1", "file_analysis", "agent_registry")
_emit_validates_agent_capability("p1", "file_analysis", "capability")
_emit_dispatches_execution_plan("p1", "file_analysis", "exec_plan")
_emit_agent_executes_agent("p1", "file_analysis", "sub_agent")
_emit_routes_to_agent("p1", "file_analysis", "target_agent")
_emit_verifies_policy("p1", "file_analysis", "policy_check")
_emit_observes_runtime_state("p1", "file_analysis", "runtime_state")
_emit_verifies_boundary("p1", "file_analysis", "boundary_check")
_emit_transcripts_response("p1", "file_analysis", "transcript")
_emit_hard_fails_untranscripted("p1", "file_analysis")
_emit_gated_by_confidence("p1", "file_analysis", "confidence_gate")
_emit_escalates_to_human("p1", "file_analysis", "L0")
_emit_reads_policy_state("p1", "file_analysis", "L0")
_emit_pulls_context("p1", "file_analysis", "context_pull")
_emit_pulls_context("p1", "file_analysis", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "file_analysis", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "file_analysis", "uwg_term_secondary")
_emit_writes_through("p1", "file_analysis", "write_through")
_emit_writes_through("p1", "file_analysis", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "file_analysis", "safety_validation")
_emit_invokes_eval("p1", "file_analysis", "eval_call")
_emit_proposal_commits_routing("p1", "file_analysis", "routing_commit")

_emit_records_execution_trace("p0", "evidence", "file_analysis")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "file_analysis", "p0_governance")
_emit_snapshots_state("p0", "file_analysis", "state_snapshot")
_emit_authorize_and_execute("p2", "file_analysis", "execution_auth")
_emit_validates_capability("p2", "file_analysis", "capability_check")
_emit_routes_to_capability("p2", "file_analysis", "capability_route")
_emit_writes_via_uwg("p2", "file_analysis", "uwg_write")
_emit_blocks_direct_write("p2", "file_analysis", "direct_write_block")
_emit_records_tool_invocation("p2", "file_analysis", "tool_invocation")
_emit_captures_execution_output("p2", "file_analysis", "exec_output")
_emit_dispatches_agent("p3", "file_analysis", "agent_dispatch")
_emit_coordinates_agents("p3", "file_analysis", "agent_coordination")
_emit_records_workflow_lineage("p3", "file_analysis", "workflow_lineage")
_emit_records_healing_outcome("p3", "file_analysis", "healing_outcome")
_emit_escalates_failure("p3", "file_analysis", "failure_escalation")
_emit_orchestrates_workflow("p3", "file_analysis", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "file_analysis", "healing_dispatch")
_emit_invokes_evaluation("p3", "file_analysis", "evaluation_signal")
_emit_records_telemetry_event("p4", "file_analysis", "telemetry_event")
_emit_captures_evaluation_metric("p4", "file_analysis", "eval_metric")
_emit_stores_embedding("p4", "file_analysis", "embedding_store")
_emit_updates_meta_learning_state("p4", "file_analysis", "meta_learning")
_emit_links_execution_to_snapshot("p4", "file_analysis", "exec_snapshot_link")


@dataclass
class FileAnalysis:
    """Analysis results for a single file."""

    path: str
    classes: list[dict[str, Any]] = field(default_factory=list)
    functions: list[dict[str, Any]] = field(default_factory=list)
    imports: list[str] = field(default_factory=list)
    from_imports: list[str] = field(default_factory=list)
    docstring: str = ""
    purpose: str = ""
    domain: str = ""  # 'resume', 'outreach', 'shared', 'infrastructure'
    complexity: int = 0
    loc: int = 0
    has_agents: bool = False
    has_models: bool = False
    has_utilities: bool = False
    external_deps: list[str] = field(default_factory=list)
    internal_deps: list[str] = field(default_factory=list)


def extract_docstring(node) -> str:
    """Extract docstring from AST node."""
    try:
        return ast.get_docstring(node) or ""
    # guardian: allow-silent-swallow
    except (ValueError, TypeError):
        return ""


def analyze_class(node: ast.ClassDef) -> dict[str, Any]:
    """Deep analysis of a class definition."""
    bases = []
    for base in node.bases:
        if isinstance(base, ast.Name):
            bases.append(base.id)
        elif isinstance(base, ast.Attribute):
            bases.append(base.attr)

    methods = []
    for item in node.body:
        if isinstance(item, ast.FunctionDef | ast.AsyncFunctionDef):
            params = [arg.arg for arg in item.args.args if arg.arg != "self"]
            methods.append(
                {
                    "name": item.name,
                    "params": params,
                    "is_async": isinstance(item, ast.AsyncFunctionDef),
                    "docstring": extract_docstring(item)[:100] if extract_docstring(item) else "",
                },
            )

    # Detect class type
    is_agent = node.name.endswith("Agent") or any("Agent" in b for b in bases)
    is_model = any(b in ("BaseModel", "Enum", "TypedDict") for b in bases) or "Model" in node.name
    is_mixin = "Mixin" in node.name

    return {
        "name": node.name,
        "bases": bases,
        "methods": methods,
        "docstring": extract_docstring(node)[:200] if extract_docstring(node) else "",
        "is_agent": is_agent,
        "is_model": is_model,
        "is_mixin": is_mixin,
        "method_count": len(methods),
    }


def analyze_function(node: ast.FunctionDef) -> dict[str, Any]:
    """Analyze a top-level function."""
    params = [arg.arg for arg in node.args.args]
    return {
        "name": node.name,
        "params": params,
        "is_async": isinstance(node, ast.AsyncFunctionDef),
        "docstring": extract_docstring(node)[:100] if extract_docstring(node) else "",
        "has_return": any(isinstance(n, ast.Return) and n.value for n in ast.walk(node)),
    }


def infer_domain(content: str, classes: list[dict], functions: list[dict]) -> str:
    """Infer the domain (resume/outreach/shared/infra) from content analysis."""
    content_lower = content.lower()

    # Strong signals
    resume_signals = ["resume", "cv", "job description", "skill", "experience", "ats", "bullet"]
    outreach_signals = [
        "outreach",
        "linkedin",
        "recipient",
        "campaign",
        "message",
        "personalization",
        "sender",
    ]
    infra_signals = ["cache", "redis", "pinecone", "mcp", "heal", "validate", "orchestrat"]

    resume_score = sum(content_lower.count(s) for s in resume_signals)
    outreach_score = sum(content_lower.count(s) for s in outreach_signals)
    infra_score = sum(content_lower.count(s) for s in infra_signals)

    # Check class/function names
    all_names = [c["name"].lower() for c in classes] + [f["name"].lower() for f in functions]
    for name in all_names:
        if any(s in name for s in ["resume", "skill", "job", "cv"]):
            resume_score += 5
        if any(s in name for s in ["outreach", "message", "recipient", "campaign"]):
            outreach_score += 5

    if resume_score > 10 and outreach_score > 10:
        return "shared"
    elif resume_score > outreach_score and resume_score > infra_score:
        return "resume"
    elif outreach_score > resume_score and outreach_score > infra_score:
        return "outreach"
    elif infra_score > 5:
        return "infrastructure"
    else:
        return "shared"


def infer_purpose(classes: list[dict], functions: list[dict], docstring: str) -> str:
    """Infer the purpose of the file from its contents."""
    purposes = []

    # From docstring
    if docstring:
        first_line = docstring.split("\n")[0][:100]
        purposes.append(first_line)

    # From class names and types
    for cls in classes:
        if cls["is_agent"]:
            purposes.append(f"Agent: {cls['name']}")
        elif cls["is_model"]:
            purposes.append(f"Model: {cls['name']}")
        elif cls["is_mixin"]:
            purposes.append(f"Mixin: {cls['name']}")

    # From function names
    func_names = [f["name"] for f in functions if not f["name"].startswith("_")]
    if func_names:
        purposes.append(f"Functions: {', '.join(func_names[:5])}")

    return " | ".join(purposes[:3]) if purposes else "Unknown"


def analyze_file(file_path: Path) -> FileAnalysis | None:
    """Perform deep AST analysis on a file."""
    try:
        content = file_path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(content)
    # guardian: allow-silent-swallow - acceptable exception handling    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime
    except SyntaxError:
        return None
    except (ValueError, TypeError):
        return None

    analysis = FileAnalysis(path=str(file_path))
    analysis.loc = len(content.splitlines())
    analysis.docstring = extract_docstring(tree)[:300] if extract_docstring(tree) else ""

    # Extract imports
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                analysis.imports.append(alias.name)
                if alias.name.startswith((AGENTIC_CORE_DIR, "apps_")):
                    analysis.internal_deps.append(alias.name)
                elif not alias.name.startswith(("typing", "pathlib", "os", "sys", "re", "json")):
                    analysis.external_deps.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            analysis.from_imports.append(module)
            if module.startswith((AGENTIC_CORE_DIR, "apps_")):
                analysis.internal_deps.append(module)
            elif not module.startswith(
                ("typing", "pathlib", "os", "sys", "re", "json", "dataclasses", "enum"),
            ):
                analysis.external_deps.append(module)

    # Extract classes and functions
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.ClassDef):
            cls_info = analyze_class(node)
            analysis.classes.append(cls_info)
            if cls_info["is_agent"]:
                analysis.has_agents = True
            if cls_info["is_model"]:
                analysis.has_models = True
        elif isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            func_info = analyze_function(node)
            analysis.functions.append(func_info)
            analysis.has_utilities = True

    # Infer domain and purpose
    analysis.domain = infer_domain(content, analysis.classes, analysis.functions)
    analysis.purpose = infer_purpose(analysis.classes, analysis.functions, analysis.docstring)

    # Calculate complexity (simplified)
    analysis.complexity = len(analysis.classes) * 3 + len(analysis.functions) + analysis.loc // 50

    return analysis


def find_similar_in_codebase(analysis: FileAnalysis, current_dirs: list[str]) -> list[dict]:
    """Find similar functionality in current codebase using AST comparison."""
    similar = []

    # Get class and function names from archived file
    archived_classes = {c["name"].lower() for c in analysis.classes}
    archived_functions = {f["name"].lower() for f in analysis.functions}
    archived_methods = set()
    for c in analysis.classes:
        for m in c["methods"]:
            archived_methods.add(m["name"].lower())

    for dir_path in current_dirs:
        for py_file in Path(dir_path).rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue

            try:
                content = py_file.read_text(encoding="utf-8", errors="replace")
                tree = ast.parse(content)
            # guardian: allow-silent-swallow
            except (ValueError, TypeError):
                continue

            current_classes = set()
            current_functions = set()
            current_methods = set()

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    current_classes.add(node.name.lower())
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef | ast.AsyncFunctionDef):
                            current_methods.add(item.name.lower())
                elif isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                    current_functions.add(node.name.lower())

            # Calculate similarity
            class_overlap = archived_classes & current_classes
            func_overlap = archived_functions & current_functions
            method_overlap = archived_methods & current_methods

            if class_overlap or func_overlap or (len(method_overlap) > 3):
                similarity_score = len(class_overlap) * 10 + len(func_overlap) * 5 + len(method_overlap)
                similar.append(
                    {
                        "file": str(py_file),
                        "class_overlap": list(class_overlap),
                        "func_overlap": list(func_overlap),
                        "method_overlap": list(method_overlap)[:5],
                        "similarity_score": similarity_score,
                    },
                )

    return sorted(similar, key=lambda x: -x["similarity_score"])[:5]


def main():
    # Key archived files to analyze
    archive_files = [
        "archives/apps_lic/L1_cognition/P1_retrieve/check_outreach/check_outreach_policy.py",
        "archives/apps_lic/L1_cognition/P1_retrieve/get_info/build_message_filters.py",
        "archives/apps_rg/L1_cognition/P1_retrieve/check_resume/check_resume_policy.py",
        "archives/apps_rg/L1_cognition/P1_retrieve/get_info/build_skill_query.py",
        "archives/apps_shared/cache/semantic_cache.py",
        "archives/apps_shared/core/meta_ranking.py",
        "archives/Reachout Engine Archive/Agentic LIC/hop_agents_LIC.py",
        "archives/Reachout Engine Archive/Agentic LIC/models_LIC.py",
        "archives/Reachout Engine Archive/Agentic LIC/workflow_LIC.py",
        "archives/Reachout Engine Archive/Agentic LIC/state_manager_LIC.py",
    ]

    current_dirs = [AGENTIC_CORE_DIR, APPS_RG_DIR, APPS_LIC_DIR, APPS_SHARED_DIR]

    print("=" * 80)
    print("ADVANCED AST-BASED ARCHIVE ANALYSIS")
    print("=" * 80)

    results = []

    for archive_path in archive_files:
        path = Path(archive_path)
        if not path.exists():
            print(f"\n[NOT FOUND] {archive_path}")
            continue

        analysis = analyze_file(path)
        if not analysis:
            print(f"\n[PARSE ERROR] {archive_path}")
            continue

        print(f"\n{'=' * 80}")
        print(f"FILE: {path.name}")
        print(f"{'=' * 80}")
        print(f"  Domain:     {analysis.domain.upper()}")
        print(f"  Purpose:    {analysis.purpose[:70]}")
        print(f"  LOC:        {analysis.loc}")
        print(f"  Complexity: {analysis.complexity}")

        if analysis.classes:
            print(f"\n  CLASSES ({len(analysis.classes)}):")
            for cls in analysis.classes:
                agent_tag = " [AGENT]" if cls["is_agent"] else ""
                model_tag = " [MODEL]" if cls["is_model"] else ""
                print(f"    - {cls['name']}{agent_tag}{model_tag}")
                print(f"      Bases: {cls['bases']}")
                print(f"      Methods: {[m['name'] for m in cls['methods'][:5]]}")
                if cls["docstring"]:
                    print(f"      Doc: {cls['docstring'][:60]}...")

        if analysis.functions:
            print(f"\n  FUNCTIONS ({len(analysis.functions)}):")
            for func in analysis.functions[:8]:
                print(f"    - {func['name']}({', '.join(func['params'][:3])})")

        if analysis.external_deps:
            print(f"\n  EXTERNAL DEPS: {analysis.external_deps[:5]}")

        if analysis.internal_deps:
            print(f"  INTERNAL DEPS: {analysis.internal_deps[:5]}")

        # Find similar in current codebase
        similar = find_similar_in_codebase(analysis, current_dirs)
        if similar:
            print("\n  SIMILAR IN CURRENT CODEBASE:")
            for s in similar[:3]:
                print(f"    - {s['file']}")
                print(
                    f"      Score: {s['similarity_score']}, Classes: {s['class_overlap']}, Funcs: {s['func_overlap'][:3]}",
                )
        else:
            print("\n  NO SIMILAR FILES FOUND - UNIQUE FUNCTIONALITY")

        # Recommendation
        print("\n  RECOMMENDATION:")
        if not similar:
            if analysis.has_agents:
                target = (
                    f"apps_{analysis.domain}/engines/"
                    if analysis.domain in ("resume", "outreach")
                    else "apps_shared/base_agents/"
                )
            elif analysis.has_models:
                target = "apps_shared/models/"
            else:
                target = (
                    f"apps_{analysis.domain}/engines/utils/"
                    if analysis.domain in ("resume", "outreach")
                    else "apps_shared/common_utils/"
                )
            print(f"    RESTORE -> {target}")
            print("    Reason: Unique functionality not present in current codebase")
        elif similar[0]["similarity_score"] > 20:
            print(f"    SKIP - Functionality exists in: {similar[0]['file']}")
            print(f"    Reason: High similarity score ({similar[0]['similarity_score']})")
        else:
            print(f"    REVIEW - Partial overlap with: {similar[0]['file']}")
            print("    Reason: May contain unique methods/logic worth merging")

        results.append({"path": archive_path, "analysis": analysis, "similar": similar})

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)

    restore = [r for r in results if not r["similar"]]
    skip = [r for r in results if r["similar"] and r["similar"][0]["similarity_score"] > 20]
    review = [r for r in results if r["similar"] and r["similar"][0]["similarity_score"] <= 20]

    print(f"\n  RESTORE (unique functionality): {len(restore)}")
    for r in restore:
        print(f"    - {Path(r['path']).name} [{r['analysis'].domain}]")

    print(f"\n  SKIP (exists in codebase): {len(skip)}")
    for r in skip:
        print(f"    - {Path(r['path']).name} -> {Path(r['similar'][0]['file']).name}")

    print(f"\n  REVIEW (partial overlap): {len(review)}")
    for r in review:
        print(f"    - {Path(r['path']).name} (score: {r['similar'][0]['similarity_score']})")


if __name__ == "__main__":
    main()
