"""Append C4-NEW-A..F (REQ-189..194) to the 10c semantic ledger and matrix."""
import csv
from pathlib import Path

ROOT = Path(r"c:\Git\Agentic-Workflow-FRESH")
ledger = ROOT / "docs/reports/design/10c_reconciliation/10c_semantic_requirement_ledger.csv"
matrix = ROOT / "docs/reports/design/10c_reconciliation/10c_requirements_vs_10a_matrix.csv"

rows_ledger = list(csv.DictReader(ledger.open(encoding="utf-8")))
rows_matrix = list(csv.DictReader(matrix.open(encoding="utf-8")))
ledger_fields = list(rows_ledger[0].keys())
matrix_fields = list(rows_matrix[0].keys())

new_ledger = [
    {
        "req_id": "10C-REQ-189",
        "source_file": "Anthropic Cache Engineering 2025 + best-practice gap analysis 2026-04-30",
        "source_section": "C4-NEW-A cache-stable prefix",
        "source_unit_type": "Derived requirement (Anthropic prompt caching / Claude Code harness architecture)",
        "source_text_short": "PromptEnvelope declares cache_stable_prefix and cache_volatile_suffix with cache_control markers and hit/miss telemetry",
        "canonical_requirement_statement": (
            "PromptEnvelope MUST declare a cache_stable_prefix (system prompt + tool definitions + "
            "frozen exemplars) and a cache_volatile_suffix (per-request evidence, user turn, session "
            "delta). The stable prefix MUST be emitted with provider-native cache_control markers "
            "(e.g. Anthropic cache_control: ephemeral). Cache hit/miss ratio MUST be recorded per "
            "call as an L6 telemetry datum. Prompt assembly (PA) MUST NOT reorder or mutate the "
            "stable prefix mid-session unless an explicit cache-invalidation receipt is emitted."
        ),
        "direct_or_implied": "implied",
        "semantic_class": "C. Runtime layers and sovereignty",
        "layer_owner": "prompt assembly + L0",
        "runtime_phase": "Pre-execution",
        "required_artifacts": "PromptEnvelope.cache_stable_prefix; PromptEnvelope.cache_volatile_suffix; CacheHitMissReceipt",
        "required_controls": "CacheStablePrefixAssembler; CacheControlMarkerInjector; CacheHitMissTelemetryEmitter",
        "required_tests": "Stable prefix invariant across turns; cache_control markers present in provider payload; hit/miss ratio telemetry emitted; mutation triggers invalidation receipt",
        "severity_if_missing": "CRITICAL",
        "confidence_score": "0.94",
    },
    {
        "req_id": "10C-REQ-190",
        "source_file": "Anthropic Cache Engineering 2025 + Effective Context Engineering 2025",
        "source_section": "C4-NEW-B system-reminder delta pattern and tool-set stability",
        "source_unit_type": "Derived requirement (Anthropic cache-preserving update pattern)",
        "source_text_short": "Mid-conversation updates via system-reminder block; tool set stable across session unless resealed",
        "canonical_requirement_statement": (
            "Mid-conversation context updates (time, state refreshes, reminder injections) MUST be "
            "appended via a system-reminder block into the next user message or tool result, never "
            "by re-issuing or mutating the system prompt. The tool set registered at session start "
            "MUST remain stable across the session; adding or removing tools mid-session MUST trigger "
            "an explicit cache-reseal receipt and L6 telemetry event. Unacknowledged tool-set mutation "
            "is a cache-coherence violation."
        ),
        "direct_or_implied": "implied",
        "semantic_class": "C. Runtime layers and sovereignty",
        "layer_owner": "prompt assembly + L1",
        "runtime_phase": "Pre-execution",
        "required_artifacts": "SystemReminderBlock; CacheResealReceipt; ToolSetStabilityContract",
        "required_controls": "SystemReminderInjector; ToolSetMutationDetector; CacheResealEmitter",
        "required_tests": "System prompt hash unchanged after mid-session update; tool-set mutation detected and receipted; unacknowledged mutation blocked or flagged",
        "severity_if_missing": "CRITICAL",
        "confidence_score": "0.93",
    },
    {
        "req_id": "10C-REQ-191",
        "source_file": "Anthropic Agent SDK 2025 + Claude Code sub-agent architecture (arxiv 2604.14228)",
        "source_section": "C4-NEW-C typed sub-agent harness",
        "source_unit_type": "Derived requirement (Anthropic sub-agent decomposition pattern)",
        "source_text_short": "Sub-agent harness with typed agents (general/explore/plan/verify), bounded tool sets, isolated memory",
        "canonical_requirement_statement": (
            "The agent harness MUST support typed sub-agents with at minimum the roles {general, "
            "explore, plan, verify}. Each sub-agent type MUST have: (1) a bounded tool set (no "
            "superset-of-all-tools), (2) isolated session memory (full conversation history MUST NOT "
            "cross sub-agent boundaries), (3) a structured handoff context contract (summary + "
            "relevant artifacts only). Sub-agent invocation MUST be an L6-traced span with "
            "sub_agent_type, tool_count, context_tokens_in, context_tokens_out recorded."
        ),
        "direct_or_implied": "implied",
        "semantic_class": "C. Runtime layers and sovereignty",
        "layer_owner": "L2 execution + L3 orchestration",
        "runtime_phase": "Execution",
        "required_artifacts": "SubAgentTypeRegistry; SubAgentHandoffContract; SubAgentSpanTelemetry",
        "required_controls": "SubAgentToolSetBinder; SubAgentMemoryIsolator; SubAgentContextSummarizer",
        "required_tests": "Sub-agent cannot access tools outside its declared set; conversation history does not leak across sub-agent boundary; handoff contract schema validation; telemetry span emitted per invocation",
        "severity_if_missing": "HIGH",
        "confidence_score": "0.90",
    },
    {
        "req_id": "10C-REQ-192",
        "source_file": "Anthropic Building Effective Agents 2024 + Demystifying Evals 2025",
        "source_section": "C4-NEW-D three-phase span stamp (gather-context / act / verify)",
        "source_unit_type": "Derived requirement (Anthropic three-phase agent loop)",
        "source_text_short": "Every L2 step OTEL span carries phase in {gather_context, act, verify}; Exit X1F checks phase completeness",
        "canonical_requirement_statement": (
            "Every L2 execution step MUST stamp its OTEL span with agent_phase in {gather_context, "
            "act, verify}. The three-phase loop MUST be the canonical step lifecycle: gather_context "
            "(retrieve evidence, load state), act (invoke tool or generate output), verify (check "
            "output against ground truth from environment). Exit X1F coherence check MUST verify "
            "each step achieved all three phases or explicitly skipped verify with a skip_reason. "
            "Steps lacking the phase stamp fail X1H Observability gate. L6 calibration MUST measure "
            "verify-skip rate and flag routes exceeding 20 percent skip rate."
        ),
        "direct_or_implied": "implied",
        "semantic_class": "E. Metrics / evaluation / shadow / learning",
        "layer_owner": "L2 execution + L5 exit control",
        "runtime_phase": "Execution + Exit evaluation",
        "required_artifacts": "AgentPhaseStamp; VerifySkipReceipt; VerifySkipRateCalibrationReport",
        "required_controls": "PhaseStampInjector; ExitPhaseCompletenessChecker; VerifySkipRateMonitor",
        "required_tests": "Span carries agent_phase attribute; missing phase fails X1H; skip_reason present when verify omitted; verify-skip rate measured per route",
        "severity_if_missing": "HIGH",
        "confidence_score": "0.91",
    },
    {
        "req_id": "10C-REQ-193",
        "source_file": "Anthropic Writing Effective Tools 2025",
        "source_section": "C4-NEW-E tool response token cap",
        "source_unit_type": "Derived requirement (Anthropic 25k-token tool response default)",
        "source_text_short": "Tool response capped at 25k tokens default; pagination/filter on exceed; per-tool override in capability_registry",
        "canonical_requirement_statement": (
            "Tool responses MUST be capped at a configurable response_token_max (default: 25000 "
            "tokens). Responses exceeding the cap MUST be truncated to the cap with a structured "
            "pagination envelope containing: truncated_at, total_available, next_page_token, and "
            "a 1-line summary of omitted content. Per-tool overrides MUST be declared in "
            "capability_registry[tool].response_token_max. Cap enforcement MUST be in the L2 "
            "tool-call wrapper, not in each tool implementation. L6 telemetry MUST record "
            "tool_response_tokens per call for weekly p95 calibration."
        ),
        "direct_or_implied": "implied",
        "semantic_class": "C. Runtime layers and sovereignty",
        "layer_owner": "L2 execution",
        "runtime_phase": "Execution",
        "required_artifacts": "ToolResponseTokenCap; PaginationEnvelope; capability_registry.response_token_max",
        "required_controls": "ToolResponseCapEnforcer; PaginationEnvelopeSerializer; ToolTokenTelemetryEmitter",
        "required_tests": "Response exceeding cap truncated with pagination envelope; per-tool override respected; L2 wrapper enforces (not individual tools); telemetry records token count",
        "severity_if_missing": "HIGH",
        "confidence_score": "0.92",
    },
    {
        "req_id": "10C-REQ-194",
        "source_file": "Anthropic Writing Effective Tools 2025 + Effective Context Engineering 2025",
        "source_section": "C4-NEW-F heavy-tool pagination floor",
        "source_unit_type": "Derived requirement (Anthropic tool pagination / range / filter guidance)",
        "source_text_short": "Tools with p95 response >5k tokens MUST support pagination/range/filter; L6 flags non-compliant tools",
        "canonical_requirement_statement": (
            "Any tool whose weekly p95 response size exceeds 5000 tokens MUST support at least one "
            "of {pagination, range_select, filter} with sensible default parameter values that keep "
            "the default response under 5000 tokens. L6 weekly calibration MUST measure per-tool "
            "p95 response tokens and flag tools exceeding the floor without pagination support. "
            "Flagged tools MUST be blocked from registration in new routes until paginated. Existing "
            "routes using flagged tools receive a DEGRADED_TOOL warning in their next calibration report."
        ),
        "direct_or_implied": "implied",
        "semantic_class": "C. Runtime layers and sovereignty",
        "layer_owner": "L2 execution + L6 observability",
        "runtime_phase": "Execution + Post-run learning",
        "required_artifacts": "ToolPaginationFloorPolicy; ToolP95CalibrationReport; DEGRADED_TOOL_warning",
        "required_controls": "ToolP95Monitor; PaginationFloorEnforcer; DegradedToolWarningEmitter",
        "required_tests": "Tool with p95 >5k without pagination flagged; flagged tool blocked from new routes; existing routes warned; tool with pagination under 5k passes",
        "severity_if_missing": "HIGH",
        "confidence_score": "0.89",
    },
]

for r in new_ledger:
    assert set(r.keys()) == set(ledger_fields), f"key mismatch in {r['req_id']}: extra={set(r.keys())-set(ledger_fields)} missing={set(ledger_fields)-set(r.keys())}"

with ledger.open("a", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=ledger_fields, lineterminator="\n")
    for r in new_ledger:
        w.writerow(r)

new_matrix = []
for r in new_ledger:
    new_matrix.append({
        "10c_req_id": r["req_id"],
        "10a_req_id": "",
        "covered_by_10a": "false",
        "10a_coverage_type": "none",
        "coverage_gap_reason": f"NEW best-practice gap (Anthropic C4 Cache+Harness); see {r['source_section']}",
    })
for r in new_matrix:
    assert set(r.keys()) == set(matrix_fields), f"matrix key mismatch in {r['10c_req_id']}"
with matrix.open("a", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=matrix_fields, lineterminator="\n")
    for r in new_matrix:
        w.writerow(r)

rows_after = list(csv.DictReader(ledger.open(encoding="utf-8")))
print(f"ledger: {len(rows_after)} rows; last 6: {[r['req_id'] for r in rows_after[-6:]]}")
rows_after_m = list(csv.DictReader(matrix.open(encoding="utf-8")))
print(f"matrix: {len(rows_after_m)} rows; last 6: {[r['10c_req_id'] for r in rows_after_m[-6:]]}")
