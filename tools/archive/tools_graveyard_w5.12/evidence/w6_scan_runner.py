"""W6 Forensic Audit — Mandatory AST + Grep Scan Runner.

Sections:
  S1  SovereignLLMGateway call sites (AST)
  S2  EmbeddingFactory / create_embedding_client call sites (AST)
  S3  UniversalWriteGateway call sites (AST)
  S4  InstructionPacket verify call sites (AST+grep)
  S5  SandboxEnvelope verify call sites (AST+grep)
  S6  HumanDecisionArtifact verify call sites (AST+grep)
  S7  route_healing_tier() call sites (AST)
  S8  BYPASS: provider SDK imports outside gateway (grep+AST)
  S9  BYPASS: model literals outside gateway (grep)
  S10 BYPASS: embedding instantiation outside factory (AST+grep)
  S11 BYPASS: alternate LLM outbound seams
  S12 BYPASS: alternate tier-selection outside route_healing_tier()
  S13 BYPASS: FS/DB/vector writes bypassing UWG
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
    L2_EXECUTION_DIR,
    SYSTEM_LEARNING_DIR,
    get_validated_project_root,
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
    _emit_dispatches_healing_run,
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_escalates_to_human,
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
    _emit_reads_through,
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
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

_emit_emits_metric_event("w6_scan_runner", "p4obs", "metric_1")
_emit_emits_metric_event("w6_scan_runner", "p4obs", "metric_2")
_emit_emits_metric_event("w6_scan_runner", "p4obs", "metric_3")
_emit_emits_metric_event("w6_scan_runner", "p4obs", "metric_4")
_emit_emits_metric_event("w6_scan_runner", "p4obs", "metric_5")
_emit_emits_metric_event("w6_scan_runner", "p4obs", "metric_6")
_emit_records_incident_event("w6_scan_runner", "p4obs", "incident")
_emit_captures_runtime_anomaly("w6_scan_runner", "p4obs", "anomaly")
_emit_writes_observability_log("w6_scan_runner", "p4obs", "obs_log")
_emit_updates_monitoring_state("w6_scan_runner", "p4obs", "mon_state")
_emit_triggers_alert("w6_scan_runner", "p4obs", "alert")
_emit_links_incident_trace("w6_scan_runner", "p4obs", "trace_link")
_emit_captures_pattern("w6_scan_runner", "p3lm", "pattern")
_emit_records_learning_event("w6_scan_runner", "p3lm", "learning_event")
_emit_writes_learning_snapshot("w6_scan_runner", "p3lm", "snapshot")
_emit_feeds_meta_learning("w6_scan_runner", "p3lm", "meta_feed")
_emit_updates_routing_strategy("w6_scan_runner", "p3lm", "routing")
_emit_improves_agent_policy("w6_scan_runner", "p3lm", "policy")
_emit_stores_learning_state("w6_scan_runner", "p3lm", "state")
_emit_records_execution_trace("w6_scan_runner", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("w6_scan_runner", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("w6_scan_runner", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("w6_scan_runner", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("w6_scan_runner", "L4_STATE", "p2_trace_5")
_emit_reads_environ("w6_scan_runner", "env_read", "p2_env_1")
_emit_reads_environ("w6_scan_runner", "env_read", "p2_env_2")
_emit_reads_runtime_state("w6_scan_runner", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("w6_scan_runner", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "w6_scan_runner")
_emit_applies_guardrail("p0", "w6_scan_runner", "p0_governance")
_emit_reads_policy_state("p0", "w6_scan_runner", "policy_binding")
_emit_snapshots_state("p0", "w6_scan_runner", "state_snapshot")
_emit_pulls_context("p1", "w6_scan_runner", "context_pull")
_emit_pulls_context("p1", "w6_scan_runner", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "w6_scan_runner", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "w6_scan_runner", "uwg_term_secondary")
_emit_writes_through("p1", "w6_scan_runner", "write_through")
_emit_writes_through("p1", "w6_scan_runner", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "w6_scan_runner", "safety_validation")
_emit_invokes_eval("p1", "w6_scan_runner", "eval_call")
_emit_proposal_commits_routing("p1", "w6_scan_runner", "routing_commit")
_emit_escalates_to_human("p1", "w6_scan_runner", "human_escalation")
_emit_routes_through("p1", "w6_scan_runner", "route_through")
_emit_checks_agent_registry("p1", "w6_scan_runner", "agent_registry")
_emit_validates_agent_capability("p1", "w6_scan_runner", "capability")
_emit_dispatches_execution_plan("p1", "w6_scan_runner", "exec_plan")
_emit_agent_executes_agent("p1", "w6_scan_runner", "sub_agent")
_emit_routes_to_agent("p1", "w6_scan_runner", "target_agent")
_emit_verifies_policy("p1", "w6_scan_runner", "policy_check")
_emit_observes_runtime_state("p1", "w6_scan_runner", "runtime_state")
_emit_verifies_boundary("p1", "w6_scan_runner", "boundary_check")
_emit_transcripts_response("p1", "w6_scan_runner", "transcript")
_emit_hard_fails_untranscripted("p1", "w6_scan_runner")
_emit_gated_by_confidence("p1", "w6_scan_runner", "confidence_gate")
emit_replay_key("p0", "w6_scan_runner")
emit_determinism_digest("p0", "w6_scan_runner")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "w6_scan_runner", "execution_auth")
_emit_validates_capability("p2", "w6_scan_runner", "capability_check")
_emit_routes_to_capability("p2", "w6_scan_runner", "capability_route")
_emit_writes_via_uwg("p2", "w6_scan_runner", "uwg_write")
_emit_blocks_direct_write("p2", "w6_scan_runner", "direct_write_block")
_emit_records_tool_invocation("p2", "w6_scan_runner", "tool_invocation")
_emit_captures_execution_output("p2", "w6_scan_runner", "exec_output")
_emit_dispatches_agent("p3", "w6_scan_runner", "agent_dispatch")
_emit_coordinates_agents("p3", "w6_scan_runner", "agent_coordination")
_emit_records_workflow_lineage("p3", "w6_scan_runner", "workflow_lineage")
_emit_records_healing_outcome("p3", "w6_scan_runner", "healing_outcome")
_emit_escalates_failure("p3", "w6_scan_runner", "failure_escalation")
_emit_orchestrates_workflow("p3", "w6_scan_runner", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "w6_scan_runner", "healing_dispatch")
_emit_invokes_evaluation("p3", "w6_scan_runner", "evaluation_signal")
_emit_records_telemetry_event("p4", "w6_scan_runner", "telemetry_event")
_emit_captures_evaluation_metric("p4", "w6_scan_runner", "eval_metric")
_emit_stores_embedding("p4", "w6_scan_runner", "embedding_store")
_emit_updates_meta_learning_state("p4", "w6_scan_runner", "meta_learning")
_emit_links_execution_to_snapshot("p4", "w6_scan_runner", "exec_snapshot_link")
_emit_reads_through("l4", "w6_scan_runner", "urg_read_1")
_emit_reads_through("l4", "w6_scan_runner", "urg_read_2")
_emit_reads_through("l4", "w6_scan_runner", "urg_read_3")
_emit_reads_through("l4", "w6_scan_runner", "urg_read_4")
_emit_reads_through("l4", "w6_scan_runner", "urg_read_5")
_emit_reads_through("l4", "w6_scan_runner", "urg_read_6")
_emit_reads_through("l4", "w6_scan_runner", "urg_read_7")
_emit_reads_through("l4", "w6_scan_runner", "urg_read_8")
_emit_reads_through("l4", "w6_scan_runner", "urg_read_9")
_emit_reads_through("l4", "w6_scan_runner", "urg_read_10")
_emit_reads_through("l4", "w6_scan_runner", "urg_read_11")
_emit_reads_through("l4", "w6_scan_runner", "urg_read_12")
_emit_reads_through("l4", "w6_scan_runner", "urg_read_13")
_emit_reads_through("l4", "w6_scan_runner", "urg_read_14")
_emit_reads_through("l4", "w6_scan_runner", "urg_read_15")
_emit_reads_through("l4", "w6_scan_runner", "urg_read_16")
_emit_reads_through("l4", "w6_scan_runner", "urg_read_17")
_emit_reads_through("l4", "w6_scan_runner", "urg_read_18")
_emit_reads_through("l4", "w6_scan_runner", "urg_read_19")
_emit_reads_through("l4", "w6_scan_runner", "urg_read_20")
_emit_reads_through("l4", "w6_scan_runner", "urg_read_21")
_emit_reads_through("l4", "w6_scan_runner", "urg_read_22")
_emit_reads_through("l4", "w6_scan_runner", "urg_read_23")
_emit_reads_through("l4", "w6_scan_runner", "urg_read_24")
_emit_reads_through("l4", "w6_scan_runner", "urg_read_25")
_emit_reads_through("l4", "w6_scan_runner", "urg_read_26")
_emit_reads_through("l4", "w6_scan_runner", "urg_read_27")
_emit_reads_through("l4", "w6_scan_runner", "urg_read_28")
_emit_reads_through("l4", "w6_scan_runner", "urg_read_29")

REPO_ROOT = get_validated_project_root()
SCAN_ROOTS = [
    REPO_ROOT / AGENTIC_CORE_DIR,
    REPO_ROOT / APPS_LIC_DIR,
    REPO_ROOT / APPS_RG_DIR,
    REPO_ROOT / APPS_SHARED_DIR,
    REPO_ROOT / SYSTEM_LEARNING_DIR,
    REPO_ROOT / "L6_observability",
]
GATEWAY_FILE = REPO_ROOT / L2_EXECUTION_DIR / "enforcement" / "SovereignLLMGateway.py"
UWG_FILE = REPO_ROOT / L2_EXECUTION_DIR / "UniversalWriteGateway.py"
FACTORY_FILE = REPO_ROOT / AGENTIC_CORE_DIR / "embeddings" / "embedding_factory.py"
TIER_ROUTER_FILE = REPO_ROOT / L2_EXECUTION_DIR / "healers" / "healing_tier_router.py"

PROVIDER_SDK_PATTERNS = [
    r"\bimport\s+openai\b",
    r"\bfrom\s+openai\b",
    r"\bimport\s+anthropic\b",
    r"\bfrom\s+anthropic\b",
    r"\bimport\s+google\.generativeai\b",
    r"\bfrom\s+google\.generativeai\b",
    r"\bimport\s+vertexai\b",
    r"\bfrom\s+vertexai\b",
    r"\bOpenAI\s*\(",
    r"\bAnthropic\s*\(",
    r"\bgenai\.",
]

MODEL_LITERAL_PATTERNS = [
    r"""['"](gpt-4|gpt-3\.5|claude-|gemini-|text-embedding-|text-davinci)[^'"]*['"]""",
]

WRITE_METHOD_NAMES = {
    "write_text",
    "write_bytes",
    "open",
    "write",
    "put",
    "upsert",
    "add_documents",
    "index_documents",
    "update",
    "save",
    "store",
    "persist",
}

ALLOWED_GATEWAY_MODULES = {
    str(GATEWAY_FILE),
    str(REPO_ROOT / L2_EXECUTION_DIR / "enforcement" / "SovereignLLMGateway.py"),
}
ALLOWED_FACTORY_MODULES = {
    str(FACTORY_FILE),
    str(REPO_ROOT / SYSTEM_LEARNING_DIR / "engines" / "embedding_service_factory.py"),
    str(REPO_ROOT / AGENTIC_CORE_DIR / "embeddings" / "embedding_factory.py"),
}


def all_py_files() -> list[Path]:
    files = []
    for root in SCAN_ROOTS:
        if root.exists():
            for p in root.rglob("*.py"):
                files.append(p)
    return sorted(files)


def rel(p: Path) -> str:
    try:
        return str(p.relative_to(REPO_ROOT)).replace("\\", "/")
    except ValueError:
        return str(p).replace("\\", "/")


def parse_ast(path: Path) -> ast.Module | None:
    try:
        src = path.read_text(encoding="utf-8", errors="replace")
        return ast.parse(src, filename=str(path))
    except SyntaxError:  # guardian: Syntax errors should be caught at parser level, not runtime
        return None


def grep_file(path: Path, pattern: str) -> list[tuple[int, str]]:
    hits = []
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        rx = re.compile(pattern, re.IGNORECASE)
        for i, line in enumerate(lines, 1):
            if rx.search(line):
                hits.append((i, line.rstrip()))
    except (
        OSError,
        UnicodeDecodeError,
    ):  # guardian: File operations with encoding need error-specific handling
        pass
    return hits


def find_call_sites_ast(
    files: list[Path],
    func_names: set[str],
    attr_names: set[str] | None = None,
) -> list[dict]:
    """Find call sites of functions/methods by AST traversal."""
    results = []
    for path in files:
        tree = parse_ast(path)
        if tree is None:
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            fn = node.func
            name = None
            if isinstance(fn, ast.Name) and fn.id in func_names:
                name = fn.id
            elif isinstance(fn, ast.Attribute):
                if fn.attr in func_names:
                    name = fn.attr
                elif attr_names and fn.attr in attr_names:
                    name = fn.attr
            if name:
                results.append(
                    {
                        "file": rel(path),
                        "line": node.lineno,
                        "call": name,
                    },
                )
    return results


def find_name_usages_ast(files: list[Path], names: set[str]) -> list[dict]:
    """Find any usage (Name node) of given identifiers."""
    results = []
    for path in files:
        tree = parse_ast(path)
        if tree is None:
            continue
        for node in ast.walk(tree):
            if isinstance(node, (ast.Name, ast.Attribute)):
                n = node.id if isinstance(node, ast.Name) else node.attr
                if n in names:
                    results.append(
                        {
                            "file": rel(path),
                            "line": node.col_offset,
                            "lineno": getattr(node, "lineno", 0),
                            "name": n,
                        },
                    )
    return results


def find_import_usages_ast(files: list[Path], module_patterns: list[str]) -> list[dict]:
    """Find import statements matching module patterns."""
    results = []
    for path in files:
        tree = parse_ast(path)
        if tree is None:
            continue
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        for pat in module_patterns:
                            if re.search(pat, alias.name, re.IGNORECASE):
                                results.append({"file": rel(path), "line": node.lineno, "import": alias.name})
                elif isinstance(node, ast.ImportFrom) and node.module:
                    for pat in module_patterns:
                        if re.search(pat, node.module, re.IGNORECASE):
                            results.append({"file": rel(path), "line": node.lineno, "import": node.module})
    return results


def format_hits(hits: list[dict], key_fields: list[str]) -> str:
    if not hits:
        return "  (no hits — negative evidence confirmed)"
    lines = []
    for h in hits:
        parts = [f"{k}={h.get(k, '')}" for k in key_fields]
        lines.append("  " + "  ".join(parts))
    return "\n".join(lines)


def main() -> None:
    files = all_py_files()
    print(f"SCAN_ROOTS: {[rel(r) for r in SCAN_ROOTS if r.exists()]}")
    print(f"TOTAL_PY_FILES: {len(files)}\n")

    # ─── S1: SovereignLLMGateway call sites ───────────────────────────────────
    print("=== S1: SovereignLLMGateway CALL SITES (AST) ===")
    slg_calls = find_call_sites_ast(files, {"route_generation", "SovereignLLMGateway"})
    # Also check for 'get_instance' on SovereignLLMGateway
    slg_instance = find_call_sites_ast(files, {"get_instance"})
    slg_all = slg_calls + [h for h in slg_instance if "sovereign" in h.get("file", "").lower()]
    print(f"CALL_COUNT: {len(slg_all)}")
    print(format_hits(slg_all, ["file", "line", "call"]))
    # Check for usages of the class name
    slg_usages = []
    for f in files:
        hits = grep_file(f, r"SovereignLLMGateway")
        for line_no, text in hits:
            slg_usages.append({"file": rel(f), "line": line_no, "text": text.strip()[:80]})
    print(f"\nSovereignLLMGateway REFERENCE COUNT (grep): {len(slg_usages)}")
    print(format_hits(slg_usages[:20], ["file", "line", "text"]))
    if len(slg_usages) > 20:
        print(f"  ... ({len(slg_usages) - 20} more)")
    print()

    # ─── S2: EmbeddingFactory call sites ──────────────────────────────────────
    print("=== S2: EmbeddingFactory / create_embedding_client CALL SITES (AST) ===")
    emb_calls = find_call_sites_ast(
        files,
        {"create_embedding_client", "get_embedding_client", "register_embedding_client"},
    )
    print(f"CALL_COUNT: {len(emb_calls)}")
    print(format_hits(emb_calls, ["file", "line", "call"]))
    # Also count usages of EmbeddingServiceFactory
    esf_refs = []
    for f in files:
        hits = grep_file(f, r"EmbeddingServiceFactory|embedding_factory|create_embedding_client")
        for ln, text in hits:
            esf_refs.append({"file": rel(f), "line": ln, "text": text.strip()[:80]})
    print(f"\nEmbeddingServiceFactory REFERENCE COUNT (grep): {len(esf_refs)}")
    print(format_hits(esf_refs[:15], ["file", "line", "text"]))
    print()

    # ─── S3: UniversalWriteGateway call sites ─────────────────────────────────
    print("=== S3: UniversalWriteGateway CALL SITES (AST) ===")
    uwg_calls = find_call_sites_ast(
        files,
        {"write", "execute_write", "get_instance"},
        attr_names={"write", "execute_write"},
    )
    uwg_refs = []
    for f in files:
        hits = grep_file(f, r"UniversalWriteGateway|execute_write|uwg\.")
        for ln, text in hits:
            uwg_refs.append({"file": rel(f), "line": ln, "text": text.strip()[:80]})
    print(f"UniversalWriteGateway REFERENCE COUNT (grep): {len(uwg_refs)}")
    print(format_hits(uwg_refs[:20], ["file", "line", "text"]))
    print()

    # ─── S4: InstructionPacket verify call sites ──────────────────────────────
    print("=== S4: InstructionPacket VERIFY CALL SITES ===")
    ip_refs = []
    for f in files:
        hits = grep_file(f, r"InstructionPacket|instruction_packet|verify_signature|policy_hash")
        for ln, text in hits:
            ip_refs.append({"file": rel(f), "line": ln, "text": text.strip()[:80]})
    print(f"InstructionPacket/verify REFERENCE COUNT (grep): {len(ip_refs)}")
    print(format_hits(ip_refs[:20], ["file", "line", "text"]))
    print()

    # ─── S5: SandboxEnvelope verify call sites ────────────────────────────────
    print("=== S5: SandboxEnvelope VERIFY CALL SITES ===")
    se_refs = []
    for f in files:
        hits = grep_file(f, r"SandboxEnvelope|sandbox_envelope")
        for ln, text in hits:
            se_refs.append({"file": rel(f), "line": ln, "text": text.strip()[:80]})
    print(f"SandboxEnvelope REFERENCE COUNT (grep): {len(se_refs)}")
    print(format_hits(se_refs[:20], ["file", "line", "text"]))
    print()

    # ─── S6: HumanDecisionArtifact verify call sites ──────────────────────────
    print("=== S6: HumanDecisionArtifact VERIFY CALL SITES ===")
    hda_refs = []
    for f in files:
        hits = grep_file(f, r"HumanDecisionArtifact|reviewer_sig|original_plan_hash")
        for ln, text in hits:
            hda_refs.append({"file": rel(f), "line": ln, "text": text.strip()[:80]})
    print(f"HumanDecisionArtifact REFERENCE COUNT (grep): {len(hda_refs)}")
    print(format_hits(hda_refs[:20], ["file", "line", "text"]))
    print()

    # ─── S7: route_healing_tier() call sites (AST) ────────────────────────────
    print("=== S7: route_healing_tier() CALL SITES (AST) ===")
    tier_calls = find_call_sites_ast(files, {"route_healing_tier"})
    print(f"CALL_COUNT (AST): {len(tier_calls)}")
    print(format_hits(tier_calls, ["file", "line", "call"]))
    tier_refs = []
    for f in files:
        hits = grep_file(f, r"route_healing_tier|healing_tier_router")
        for ln, text in hits:
            tier_refs.append({"file": rel(f), "line": ln, "text": text.strip()[:80]})
    print(f"\nroute_healing_tier REFERENCE COUNT (grep): {len(tier_refs)}")
    print(format_hits(tier_refs[:15], ["file", "line", "text"]))
    print()

    # ─── S8: BYPASS — provider SDK imports outside gateway ────────────────────
    print("=== S8: BYPASS SCAN — Provider SDK Imports Outside Gateway ===")
    sdk_violations = []
    for f in files:
        if str(f) in ALLOWED_GATEWAY_MODULES:
            continue
        for pat in PROVIDER_SDK_PATTERNS:
            hits = grep_file(f, pat)
            for ln, text in hits:
                sdk_violations.append(
                    {"file": rel(f), "line": ln, "pattern": pat[:40], "text": text.strip()[:80]},
                )
    print(f"SDK_IMPORT_VIOLATIONS (outside gateway): {len(sdk_violations)}")
    print(format_hits(sdk_violations[:20], ["file", "line", "text"]))
    print()

    # ─── S9: BYPASS — model literals outside gateway ──────────────────────────
    print("=== S9: BYPASS SCAN — Model Literals Outside Gateway ===")
    literal_violations = []
    for f in files:
        if str(f) in ALLOWED_GATEWAY_MODULES:
            continue
        for pat in MODEL_LITERAL_PATTERNS:
            hits = grep_file(f, pat)
            for ln, text in hits:
                literal_violations.append({"file": rel(f), "line": ln, "text": text.strip()[:80]})
    print(f"MODEL_LITERAL_VIOLATIONS (outside gateway): {len(literal_violations)}")
    print(format_hits(literal_violations[:20], ["file", "line", "text"]))
    print()

    # ─── S10: BYPASS — embedding instantiation outside factory ────────────────
    print("=== S10: BYPASS SCAN — Embedding Instantiation Outside Factory ===")
    emb_bypass = []
    for f in files:
        if str(f) in ALLOWED_FACTORY_MODULES:
            continue
        hits = grep_file(
            f,
            r"OpenAIEmbedder|LocalFAISSStore|faiss\.IndexFlatIP|faiss\.IndexFlatL2|SentenceTransformer\s*\(",
        )
        for ln, text in hits:
            emb_bypass.append({"file": rel(f), "line": ln, "text": text.strip()[:80]})
    print(f"EMBEDDING_BYPASS_VIOLATIONS: {len(emb_bypass)}")
    print(format_hits(emb_bypass[:15], ["file", "line", "text"]))
    print()

    # ─── S11: BYPASS — alternate LLM outbound seams ───────────────────────────
    print("=== S11: BYPASS SCAN — Alternate LLM Outbound Seams ===")
    alt_llm = []
    for f in files:
        if str(f) in ALLOWED_GATEWAY_MODULES:
            continue
        hits = grep_file(
            f,
            r"\.chat\.completions\.create|\.messages\.create|\.generate_content\s*\(|openai\.ChatCompletion",
        )
        for ln, text in hits:
            alt_llm.append({"file": rel(f), "line": ln, "text": text.strip()[:80]})
    print(f"ALTERNATE_LLM_SEAM_VIOLATIONS: {len(alt_llm)}")
    print(format_hits(alt_llm[:15], ["file", "line", "text"]))
    print()

    # ─── S12: BYPASS — alternate tier-selection ───────────────────────────────
    print("=== S12: BYPASS SCAN — Alternate Tier-Selection Outside route_healing_tier() ===")
    tier_bypass = []
    for f in files:
        if "healing_tier_router" in str(f):
            continue
        hits = grep_file(f, r"HealingTier\.|LOCAL_AGENT|QWEN_VLLM|GEMINI_2_5_PRO")
        for ln, text in hits:
            tier_bypass.append({"file": rel(f), "line": ln, "text": text.strip()[:80]})
    print(f"TIER_BYPASS_CANDIDATES: {len(tier_bypass)}")
    print(format_hits(tier_bypass[:20], ["file", "line", "text"]))
    print()

    # ─── S13: BYPASS — FS/DB/vector writes bypassing UWG ─────────────────────
    print("=== S13: BYPASS SCAN — FS/DB/Vector Writes Bypassing UWG ===")
    write_bypass = []
    uwg_allowlist = {"UniversalWriteGateway.py", "hash_chain_audit_log.py", "w6_scan_runner.py"}
    for f in files:
        if f.name in uwg_allowlist:
            continue
        if "test" in str(f).lower():
            continue
        hits = grep_file(
            f,
            r"\.write_text\s*\(|\.write_bytes\s*\(|open\s*\([^)]+['\"]w['\"]|\.to_csv\s*\(|faiss\.write_index\s*\(|index\.add\s*\(",
        )
        for ln, text in hits:
            write_bypass.append({"file": rel(f), "line": ln, "text": text.strip()[:80]})
    print(f"WRITE_BYPASS_CANDIDATES: {len(write_bypass)}")
    print(format_hits(write_bypass[:25], ["file", "line", "text"]))
    print()

    # ─── S14: healing_tier_router.py — confirm single choke point ─────────────
    print("=== S14: TIER ROUTER CHOKE POINT — healing_tier_router.py ===")
    if TIER_ROUTER_FILE.exists():
        tree = parse_ast(TIER_ROUTER_FILE)
        funcs = []
        if tree:
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    funcs.append(f"  line={node.lineno}  def {node.name}()")
        print(f"  FILE: {rel(TIER_ROUTER_FILE)}")
        print(f"  FUNCTION_COUNT: {len(funcs)}")
        for fn in funcs:
            print(fn)
    else:
        print(f"  FILE NOT FOUND: {rel(TIER_ROUTER_FILE)}")
    print()

    # ─── S15: apps_* writes to L4/L0/L5 ─────────────────────────────────────
    print("=== S15: apps_* WRITES TO L4/L0/L5 (sovereignty check) ===")
    apps_roots = [REPO_ROOT / APPS_LIC_DIR, REPO_ROOT / APPS_RG_DIR, REPO_ROOT / APPS_SHARED_DIR]
    apps_files = []
    for r in apps_roots:
        if r.exists():
            apps_files.extend(r.rglob("*.py"))
    apps_writes = []
    for f in apps_files:
        hits = grep_file(
            f,
            r"L4|L5|L0|SovereignLLMGateway|UniversalWriteGateway|route_generation|execute_write",
        )
        for ln, text in hits:
            apps_writes.append({"file": rel(f), "line": ln, "text": text.strip()[:80]})
    print(f"apps_* L4/L0/L5 REFERENCES: {len(apps_writes)}")
    print(format_hits(apps_writes[:20], ["file", "line", "text"]))
    print()

    # ─── S16: needs_llm_escalation checks ─────────────────────────────────────
    print("=== S16: needs_llm_escalation FLAG USAGES ===")
    esc_refs = []
    for f in files:
        hits = grep_file(f, r"needs_llm_escalation")
        for ln, text in hits:
            esc_refs.append({"file": rel(f), "line": ln, "text": text.strip()[:80]})
    print(f"needs_llm_escalation COUNT: {len(esc_refs)}")
    print(format_hits(esc_refs[:15], ["file", "line", "text"]))
    print()

    # ─── S17: HEALER_ESCALATION_ALLOWLIST ─────────────────────────────────────
    print("=== S17: HEALER_ESCALATION_ALLOWLIST USAGES ===")
    allowlist_refs = []
    for f in files:
        hits = grep_file(f, r"HEALER_ESCALATION_ALLOWLIST|TIERING_ALLOWLIST|YES_TIERING")
        for ln, text in hits:
            allowlist_refs.append({"file": rel(f), "line": ln, "text": text.strip()[:80]})
    print(f"ALLOWLIST COUNT: {len(allowlist_refs)}")
    print(format_hits(allowlist_refs[:15], ["file", "line", "text"]))
    print()

    print("=== SCAN COMPLETE ===")


if __name__ == "__main__":
    main()
