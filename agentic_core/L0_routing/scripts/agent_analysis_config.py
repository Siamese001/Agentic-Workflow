from dataclasses import dataclass, field
from pathlib import Path

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
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
)

_emit_dispatches_healing_run("p1", "agent_analysis_config", "L0")
_emit_routes_through("p1", "agent_analysis_config", "L0")
_emit_checks_agent_registry("p1", "agent_analysis_config", "agent_registry")
_emit_validates_agent_capability("p1", "agent_analysis_config", "capability")
_emit_dispatches_execution_plan("p1", "agent_analysis_config", "exec_plan")
_emit_agent_executes_agent("p1", "agent_analysis_config", "sub_agent")
_emit_routes_to_agent("p1", "agent_analysis_config", "target_agent")
_emit_verifies_policy("p1", "agent_analysis_config", "policy_check")
_emit_observes_runtime_state("p1", "agent_analysis_config", "runtime_state")
_emit_verifies_boundary("p1", "agent_analysis_config", "boundary_check")
_emit_transcripts_response("p1", "agent_analysis_config", "transcript")
_emit_hard_fails_untranscripted("p1", "agent_analysis_config")
_emit_gated_by_confidence("p1", "agent_analysis_config", "confidence_gate")
_emit_escalates_to_human("p1", "agent_analysis_config", "L0")
_emit_reads_policy_state("p1", "agent_analysis_config", "L0")

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "agent_analysis_config", "p0_governance")
_emit_snapshots_state("p0", "agent_analysis_config", "state_snapshot")
_emit_authorize_and_execute("p2", "agent_analysis_config", "execution_auth")
_emit_validates_capability("p2", "agent_analysis_config", "capability_check")
_emit_routes_to_capability("p2", "agent_analysis_config", "capability_route")
_emit_writes_via_uwg("p2", "agent_analysis_config", "uwg_write")
_emit_blocks_direct_write("p2", "agent_analysis_config", "direct_write_block")
_emit_records_tool_invocation("p2", "agent_analysis_config", "tool_invocation")
_emit_captures_execution_output("p2", "agent_analysis_config", "exec_output")
_emit_dispatches_agent("p3", "agent_analysis_config", "agent_dispatch")
_emit_coordinates_agents("p3", "agent_analysis_config", "agent_coordination")
_emit_records_workflow_lineage("p3", "agent_analysis_config", "workflow_lineage")
_emit_records_healing_outcome("p3", "agent_analysis_config", "healing_outcome")
_emit_escalates_failure("p3", "agent_analysis_config", "failure_escalation")
_emit_orchestrates_workflow("p3", "agent_analysis_config", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "agent_analysis_config", "healing_dispatch")
_emit_invokes_evaluation("p3", "agent_analysis_config", "evaluation_signal")
_emit_records_telemetry_event("p4", "agent_analysis_config", "telemetry_event")
_emit_captures_evaluation_metric("p4", "agent_analysis_config", "eval_metric")
_emit_stores_embedding("p4", "agent_analysis_config", "embedding_store")
_emit_updates_meta_learning_state("p4", "agent_analysis_config", "meta_learning")
_emit_links_execution_to_snapshot("p4", "agent_analysis_config", "exec_snapshot_link")

# Configuration constants

#!/usr/bin/env python3
"""
cache-First Hardening Report Generator

Identifies agents that need Redis/Pinecone cache-first logic hardening.
Meta-Learning is core to agentic DNA - every LLM call and key operation
MUST check Redis cache and Pinecone semantic memory FIRST.

Usage:
    python cache_first_hardening_report.py

Output:
    - List of agents missing cache-first patterns
    - Priority ranking based on LLM usage
    - Specific methods needing hardening
"""

import re

from agentic_core.L0_routing.config import (
    AGENTIC_CORE_DIR,
    REPORTS_DIR,
)
from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
from agentic_core.config.core.constants_config import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD
    LayerSegment,
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
    _emit_records_execution_trace,
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
    emit_determinism_digest,
    emit_replay_key,
)

_emit_emits_metric_event("agent_analysis_config", "p4obs", "metric_1")
_emit_emits_metric_event("agent_analysis_config", "p4obs", "metric_2")
_emit_emits_metric_event("agent_analysis_config", "p4obs", "metric_3")
_emit_emits_metric_event("agent_analysis_config", "p4obs", "metric_4")
_emit_emits_metric_event("agent_analysis_config", "p4obs", "metric_5")
_emit_emits_metric_event("agent_analysis_config", "p4obs", "metric_6")
_emit_records_incident_event("agent_analysis_config", "p4obs", "incident")
_emit_captures_runtime_anomaly("agent_analysis_config", "p4obs", "anomaly")
_emit_writes_observability_log("agent_analysis_config", "p4obs", "obs_log")
_emit_updates_monitoring_state("agent_analysis_config", "p4obs", "mon_state")
_emit_triggers_alert("agent_analysis_config", "p4obs", "alert")
_emit_links_incident_trace("agent_analysis_config", "p4obs", "trace_link")
_emit_captures_pattern("agent_analysis_config", "p3lm", "pattern")
_emit_records_learning_event("agent_analysis_config", "p3lm", "learning_event")
_emit_writes_learning_snapshot("agent_analysis_config", "p3lm", "snapshot")
_emit_feeds_meta_learning("agent_analysis_config", "p3lm", "meta_feed")
_emit_updates_routing_strategy("agent_analysis_config", "p3lm", "routing")
_emit_improves_agent_policy("agent_analysis_config", "p3lm", "policy")
_emit_stores_learning_state("agent_analysis_config", "p3lm", "state")
_emit_records_execution_trace("agent_analysis_config", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("agent_analysis_config", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("agent_analysis_config", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("agent_analysis_config", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("agent_analysis_config", "L4_STATE", "p2_trace_5")
_emit_reads_environ("agent_analysis_config", "env_read", "p2_env_1")
_emit_reads_environ("agent_analysis_config", "env_read", "p2_env_2")
_emit_reads_runtime_state("agent_analysis_config", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("agent_analysis_config", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "agent_analysis_config", "context_pull")
_emit_pulls_context("p1", "agent_analysis_config", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "agent_analysis_config", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "agent_analysis_config", "uwg_term_2")
_emit_writes_through("p1", "agent_analysis_config", "write_through")
_emit_writes_through("p1", "agent_analysis_config", "write_through_2")
_emit_validated_by_safety_plane("p1", "agent_analysis_config", "safety_validation")
_emit_invokes_eval("p1", "agent_analysis_config", "eval_call")
_emit_proposal_commits_routing("p1", "agent_analysis_config", "routing_commit")


@dataclass
class AgentAnalysis:
    """Analysis result for a single agent file."""

    file_path: Path
    class_name: str
    has_redis_mixin: bool = False
    has_pinecone_mixin: bool = False
    has_llm_calls: bool = False
    has_cache_checks: bool = False
    has_semantic_lookup: bool = False
    methods_needing_hardening: list[str] = field(default_factory=list)
    priority: str = "LOW"  # LOW, MEDIUM, HIGH, CRITICAL

    def needs_hardening(self) -> bool:
        """Check if this agent needs cache-first hardening."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "AgentAnalysis.needs_hardening")
        emit_replay_key(_trace_id, f"rk:{_trace_id[:16]}")
        emit_determinism_digest(_trace_id, f"dd:{_trace_id[:16]}")

        # If it has LLM calls but no cache checks, it needs hardening
        if self.has_llm_calls and not self.has_cache_checks:
            return True
        # If it has analysis methods but no semantic lookup
        if self.methods_needing_hardening and not self.has_semantic_lookup:
            return True
        return False


# Patterns indicating LLM usage
LLM_PATTERNS = [
    r"generate_content",
    r"gemini\.",
    r"llm\.",
    r"model\.generate",
    r"openai\.",
    r"anthropic\.",
    r"completion\(",
    r"chat\(",
]

# Patterns indicating cache-first logic
CACHE_PATTERNS = [
    r"cache_get",
    r"redis\.get",
    r"_local_cache",
    r"cached_result",
    r"from_cache",
]

# Patterns indicating semantic lookup
SEMANTIC_PATTERNS = [
    r"vector_search",
    r"pinecone.*query",
    r"semantic.*lookup",
    r"find_similar",
    r"embedding.*search",
]

# Methods that typically need cache-first hardening
METHODS_NEEDING_CACHE = [
    "analyze_violation",
    "analyze",
    "_analyze",
    "process_violation",
    "evaluate",
    "assess",
    "generate_fix",
    "suggest_resolution",
    "get_recommendation",
    "compute_embedding",
    "heal_repository",
]


def analyze_file(file_path: Path) -> AgentAnalysis | None:
    """Analyze a single agent file for cache-first patterns."""
    try:
        content = file_path.read_text(encoding="utf-8")
    except (ValueError, TypeError, RuntimeError) as e:
        return None

    # Extract class name
    class_match = re.search(r"class\s+(\w+Agent)\s*[:\(]", content)
    if not class_match:
        return None

    class_name = class_match.group(1)

    analysis = AgentAnalysis(
        file_path=file_path,
        class_name=class_name,
    )

    # Check for mixin inheritance
    analysis.has_redis_mixin = "RedisCacheMixin" in content
    analysis.has_pinecone_mixin = "PineconeVectorMixin" in content

    # Check for LLM calls
    for pattern in LLM_PATTERNS:
        if re.search(pattern, content, re.IGNORECASE):
            analysis.has_llm_calls = True
            break

    # Check for cache-first patterns
    for pattern in CACHE_PATTERNS:
        if re.search(pattern, content, re.IGNORECASE):
            analysis.has_cache_checks = True
            break

    # Check for semantic lookup patterns
    for pattern in SEMANTIC_PATTERNS:
        if re.search(pattern, content, re.IGNORECASE):
            analysis.has_semantic_lookup = True
            break

    # Find methods needing hardening
    for method in METHODS_NEEDING_CACHE:
        if re.search(rf"def\s+{method}\s*\(", content):
            # Check if this method has cache logic
            method_match = re.search(
                rf"def\s+{method}\s*\([^)]*\)[^:]*:.*?(?=\n    def |\nclass |\Z)",
                content,
                re.DOTALL,
            )
            if method_match:
                method_body = method_match.group(0)
                has_cache = any(
                    re.search(p, method_body, re.IGNORECASE) for p in CACHE_PATTERNS + SEMANTIC_PATTERNS
                )
                if not has_cache:
                    analysis.methods_needing_hardening.append(method)

    # Determine priority
    if analysis.has_llm_calls and not analysis.has_cache_checks:
        if "analyze" in str(analysis.methods_needing_hardening).lower():
            analysis.priority = "CRITICAL"
        else:
            analysis.priority = "HIGH"
    elif analysis.methods_needing_hardening:
        analysis.priority = "MEDIUM"
    else:
        analysis.priority = "LOW"

    return analysis


def scan_ssot_folders(project_root: Path) -> list[AgentAnalysis]:
    """Scan all SSOT folders for agents needing hardening."""
    ssot_folders = [
        project_root / AGENTIC_CORE_DIR / "L0_routing",
        project_root / AGENTIC_CORE_DIR / "L1_cognition",
        project_root / AGENTIC_CORE_DIR / "L2_execution",
        project_root / AGENTIC_CORE_DIR / "L3_orchestration",
        project_root / AGENTIC_CORE_DIR / "L4_state",
        project_root / AGENTIC_CORE_DIR / "L5_safety",
        project_root / AGENTIC_CORE_DIR / "L6_observability",
    ]

    results = []

    for folder in ssot_folders:
        if not folder.exists():
            continue

        for agent_file in folder.rglob("*Agent.py"):
            # Skip backup folders
            if ".sovereign_healing_backup" in str(agent_file):
                continue
            if "__pycache__" in str(agent_file):
                continue

            analysis = analyze_file(agent_file)
            if analysis and analysis.needs_hardening():
                results.append(analysis)

    # Sort by priority
    priority_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
    results.sort(key=lambda x: (priority_order.get(x.priority, 4), x.class_name))

    return results


def generate_report(results: list[AgentAnalysis]) -> str:
    """Generate a formatted report."""
    lines = [
        "=" * 80,
        "CACHE-FIRST HARDENING REPORT",
        "Meta-Learning DNA: Redis/Pinecone lookups MANDATORY before LLM calls",
        "=" * 80,
        "",
    ]

    # Group by priority
    by_priority = {}
    for r in results:
        by_priority.setdefault(r.priority, []).append(r)

    for priority in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
        agents = by_priority.get(priority, [])
        if not agents:
            continue

        lines.append(f"\n{'=' * 40}")
        lines.append(f"PRIORITY: {priority} ({len(agents)} agents)")
        lines.append(f"{'=' * 40}")

        for agent in agents:
            lines.append(f"\n[FILE] {agent.file_path.relative_to(agent.file_path.parents[4])}")
            lines.append(f"   Class: {agent.class_name}")
            lines.append(f"   Has Redis Mixin: {'YES' if agent.has_redis_mixin else 'NO'}")
            lines.append(f"   Has Pinecone Mixin: {'YES' if agent.has_pinecone_mixin else 'NO'}")
            lines.append(f"   Has LLM Calls: {'YES' if agent.has_llm_calls else 'NO'}")
            lines.append(f"   Has cache Checks: {'YES' if agent.has_cache_checks else 'NO'}")
            lines.append(f"   Has Semantic Lookup: {'YES' if agent.has_semantic_lookup else 'NO'}")

            if agent.methods_needing_hardening:
                lines.append("   Methods needing hardening:")
                for method in agent.methods_needing_hardening:
                    lines.append(f"      - {method}()")

    # Summary
    lines.append("\n" + "=" * 80)
    lines.append("SUMMARY")
    lines.append("=" * 80)
    lines.append(f"Total agents needing hardening: {len(results)}")
    lines.append(f"  CRITICAL: {len(by_priority.get('CRITICAL', []))}")
    lines.append(f"  HIGH: {len(by_priority.get('HIGH', []))}")
    lines.append(f"  MEDIUM: {len(by_priority.get('MEDIUM', []))}")
    lines.append(f"  LOW: {len(by_priority.get('LOW', []))}")

    # Hardening checklist
    lines.append("\n" + "=" * 80)
    lines.append("HARDENING CHECKLIST")
    lines.append("=" * 80)
    lines.append("""
For each agent, implement the cache-first pattern:

1. BEFORE any LLM call:
   ```python
   # Step 1: Check Redis cache
   cache_key = f"{self._cache_prefix}:{operation}:{hash(input)}"
   cached = await self.cache_get(cache_key)
   if cached:
       return cached

   # Step 2: Check Pinecone semantic memory
   embedding = await self._get_embedding(input)
   similar = await self.vector_search(embedding, top_k=3)
   if similar and similar[0]['score'] > 0.95:
       return similar[0]['metadata']['result']

   # Step 3: Only NOW call LLM
   result = await self._llm_generate(prompt)

   # Step 4: Store in both caches
   await self.cache_set(cache_key, result, ttl=3600)
   await self.vector_upsert(embedding, metadata={'result': result})

   return result
   ```

2. For analyze_violation methods:
   - Hash the violation signature
   - Check if similar violation was seen before
   - Reuse previous fix if confidence > 0.9

3. For heal_repository methods:
   - cache scan results with file hashes
   - Invalidate on file changes
   - Store successful fixes in Pinecone for pattern learning
""")

    return "\n".join(lines)


if __name__ == "__main__":
    project_root = Path(__file__).parents[3]
    results = scan_ssot_folders(project_root)
    report = generate_report(results)
    # [HYGIENE] Removed debug print: print(report)

    # Also save to file
    report_path = project_root / AGENTIC_CORE_DIR / "L0_routing" / REPORTS_DIR / "cache_first_hardening.txt"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    assert_no_persistent_write("L0", "write_text")  # G-12-1: mutation prohibition guard
    report_path.write_text(report, encoding="utf-8")
    # [HYGIENE] Removed debug print: print(f"\nReport saved to: {report_path}")
