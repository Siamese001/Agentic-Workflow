"""Append Wave 3-10 best-practice gap REQs (REQ-186..200) — concerns C1, C3, C5, C6, C7, C8, C9, C10.

Hybrid audit final batch: critical and high severity only.
"""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LEDGER = ROOT / "docs/reports/design/10c_reconciliation/10c_semantic_requirement_ledger.csv"
MATRIX = ROOT / "docs/reports/design/10c_reconciliation/10c_requirements_vs_10a_matrix.csv"

SOURCE = "best-practice gap analysis 2026-04-30 wave3-10 hybrid audit"

# Tuple shape:
# (req_id, source_section, source_unit_type, source_text_short, canonical,
#  direct_or_implied, semantic_class, layer_owner, runtime_phase,
#  required_artifacts, required_controls, required_tests, severity, confidence)
REQS = [
    # ---------- C1 Tools (Anthropic Writing Effective Tools) ----------
    (
        "10C-REQ-186",
        "C1-NEW-A tool-response token cap + pagination",
        "Derived requirement (Anthropic Writing Effective Tools 2025 §Token efficiency)",
        "Tool responses bounded by token cap with deterministic pagination cursor",
        (
            "Every typed tool MUST declare max_response_tokens in its contract. The L2 tool invoker MUST "
            "truncate responses exceeding the cap and return a deterministic ToolResponseCursor "
            "{cursor_id, next_offset, total_remaining_tokens, truncation_reason} as the response payload. "
            "Subsequent invocations MAY pass cursor_id to continue. Heavy tools (file_read, search, "
            "directory_list) MUST default to a 25k-token soft cap and a 50k hard cap. typed_tool_contract.py "
            "has schema infrastructure but no token-cap field is required, and no canonical truncation "
            "envelope exists."
        ),
        "implied",
        "B. Prompt assembly / context engineering",
        "L2 execution",
        "Tool invocation",
        "max_response_tokens field; ToolResponseCursor; truncation_reason enum",
        "ToolResponseTruncator; CursorMinter; PaginationContractValidator",
        "Cap enforced at invoke time; cursor allows resume; oversized response refused without cursor; total_remaining_tokens accurate",
        "HIGH",
        "0.91",
    ),
    (
        "10C-REQ-187",
        "C1-NEW-B tool-error self-correction schema",
        "Derived requirement (Anthropic Writing Effective Tools 2025 §Errors as teaching)",
        "Tool errors return structured ToolErrorPacket teaching agent how to correct",
        (
            "Tool failures MUST return a structured ToolErrorPacket with fields: error_class in "
            "{INVALID_ARGS, UNAUTHORIZED, RATE_LIMITED, NOT_FOUND, TRANSIENT_FAILURE, SCHEMA_VIOLATION, "
            "POLICY_BLOCKED}, human_readable_message, agent_corrective_hint (one-line directive how to fix "
            "next call), retry_safe (bool), suggested_retry_after_ms, schema_path_violated[]. The hint MUST "
            "be deterministic given (error_class, args), not an LLM-generated apology. Free-text exceptions "
            "leaking stack traces back to the agent are forbidden because they pollute context and degrade "
            "self-correction. Current tool_safety_contract.py has guardrails for inputs but no canonical "
            "error envelope for outputs."
        ),
        "implied",
        "B. Prompt assembly / context engineering",
        "L2 execution + L5 safety",
        "Tool invocation + Error handling",
        "ToolErrorPacket; error_class enum; agent_corrective_hint registry",
        "ToolErrorPacketBuilder; StackTraceLeakDetector; CorrectiveHintRegistry",
        "Schema-violation produces correct hint; rate-limited carries retry_after_ms; policy-blocked is non-retry-safe; no stack traces in agent-visible payload",
        "CRITICAL",
        "0.94",
    ),
    # ---------- C3 Sub-agent harness ----------
    (
        "10C-REQ-188",
        "C3-NEW-A sub-agent context-isolation receipt",
        "Derived requirement (Anthropic Building Effective Agents 2025 §Sub-agents; OpenAI Handoffs)",
        "Sub-agent invocation emits SubAgentIsolationReceipt declaring context bytes in/out",
        (
            "Every sub-agent invocation (delegate, handoff, recursive_orchestrator, ptc_orchestrator dispatch) "
            "MUST emit a SubAgentIsolationReceipt with fields: parent_run_id, child_run_id, "
            "parent_context_bytes_passed, child_context_bytes_returned, isolation_class in "
            "{full_isolation, shared_scratchpad, shared_memory_only, inherited_full}, redaction_applied[], "
            "tools_authorized_subset[]. isolation_class MUST default to full_isolation; inherited_full "
            "MUST require explicit declaration. Receipt MUST be hash-chained to the parent run trace. "
            "Currently 12+ orchestrators delegate without a uniform isolation contract, risking context-"
            "leak between sub-agents."
        ),
        "implied",
        "D. Governance / capability / replay / observability",
        "L3 orchestration",
        "Sub-agent dispatch",
        "SubAgentIsolationReceipt; isolation_class enum; child_run_id linkage",
        "SubAgentDispatchInterceptor; IsolationClassValidator; ContextLeakDetector",
        "Default isolation refused without explicit class; bytes-in/out accurate; hash chain to parent; redaction applied at boundary",
        "HIGH",
        "0.90",
    ),
    (
        "10C-REQ-189",
        "C3-NEW-B sub-agent return summarization contract",
        "Derived requirement (Anthropic Effective Context Engineering 2025 §Sub-agent compaction)",
        "Sub-agent returns compressed summary, not raw transcript, to parent context",
        (
            "Sub-agent results returned to the parent agent MUST conform to a SubAgentResultEnvelope: "
            "{outcome_status, summary_text (bounded to max_return_tokens), key_findings[] (structured), "
            "raw_transcript_uri (out-of-band reference), evidence_refs[], decisions_made[], unresolved_"
            "questions[]}. Default max_return_tokens is 2000. The parent MUST NOT inline the raw transcript "
            "into its own context. raw_transcript_uri preserves replay capability without window pollution. "
            "Anthropic best practice: sub-agents are context-compression devices, not transparent function "
            "calls."
        ),
        "implied",
        "B. Prompt assembly / context engineering",
        "L3 orchestration",
        "Sub-agent return",
        "SubAgentResultEnvelope; max_return_tokens; raw_transcript_uri",
        "SubAgentSummarizer; ResultEnvelopeValidator; RawTranscriptStoreAdapter",
        "Summary <= max_return_tokens; raw URI resolves; key_findings structured; refusal to inline raw transcript",
        "HIGH",
        "0.91",
    ),
    # ---------- C5 Evals ----------
    (
        "10C-REQ-190",
        "C5-NEW-A eval-set version pinning + drift gate",
        "Derived requirement (Anthropic Demystifying Evals 2025 §Eval set versioning; OpenAI evals)",
        "Eval sets are version-pinned; promotion blocked by silent eval-set drift",
        (
            "Every eval set (golden, adversarial, regression) MUST carry a content-addressed version_hash "
            "computed from sorted (prompt, expected, rubric) triples. Promotion gates (L6 6D) MUST refuse "
            "to compare current-run scores against baseline if eval_set.version_hash differs from the "
            "baseline's pinned version_hash. Silent eval-set drift (rows added/removed without explicit "
            "rebaseline) is a contract violation. EvalSetDriftReceipt MUST be produced when drift is "
            "detected, requiring a HITL approval to rebaseline. Current judges and graders evaluate "
            "scores but no version-pinning gate is in place."
        ),
        "implied",
        "E. Metrics / evaluation / shadow / learning",
        "L6 observability",
        "Promotion + Shadow eval",
        "eval_set.version_hash; EvalSetDriftReceipt; rebaseline_approval_record",
        "EvalSetVersionPinner; DriftDetector; PromotionGateVersionValidator",
        "Drift detected on row add/remove; promotion blocked at mismatch; rebaseline requires approval; version_hash deterministic",
        "HIGH",
        "0.92",
    ),
    (
        "10C-REQ-191",
        "C5-NEW-B judge-vs-human calibration cadence enforcement",
        "Derived requirement (Anthropic Demystifying Evals 2025 §Judge calibration; existing judge-calibration-cadence rule)",
        "LLM judges require periodic human calibration; stale judges blocked from promotion influence",
        (
            "Every LLM-rubric judge consumed at runtime (§5 trace-grader) or in shadow (§6B) MUST be "
            "calibrated against a human-labeled sample at minimum cadence: weekly for runtime judges, "
            "monthly for shadow judges, with sample_size >= 30 and Cohen kappa >= 0.6 against ground "
            "truth. JudgeCalibrationReceipt MUST record kappa, sample_size, calibration_date, drift_delta. "
            "L6 6D promotion gates MUST refuse to weight a judge whose last calibration is past TTL. An "
            "unknown-budget watchdog (1 percent of trace volume routed to human-only audit) MUST run "
            "continuously. The judge-calibration-cadence skill in .windsurf/skills exists; this requirement "
            "binds it into the canonical contract layer."
        ),
        "implied",
        "E. Metrics / evaluation / shadow / learning",
        "L6 observability + HITL",
        "Shadow eval + Promotion",
        "JudgeCalibrationReceipt; judge.last_calibration_ts; unknown_budget_watchdog_record",
        "JudgeCalibrationScheduler; KappaCalculator; StaleJudgeBlocker; UnknownBudgetSampler",
        "Stale judge refused at 6D; weekly runtime cadence enforced; kappa < 0.6 blocks weighting; 1 percent watchdog active",
        "CRITICAL",
        "0.93",
    ),
    # ---------- C6 Guardrails ----------
    (
        "10C-REQ-192",
        "C6-NEW-A defense-in-depth guardrail ordering contract",
        "Derived requirement (OpenAI Guardrails 2025 §Layered defenses; Anthropic Safety 2025)",
        "Guardrails execute in deterministic ordered chain with bypass telemetry",
        (
            "Guardrails MUST execute in a deterministic chain: (1) input sanitization, (2) policy "
            "classification, (3) injection detection, (4) authority validation, (5) tool argument "
            "validation, (6) output schema validation, (7) PII egress filter. Each stage emits a "
            "GuardrailStageReceipt {stage_id, decision, evidence, latency_ms}. ANY stage returning "
            "BLOCK MUST short-circuit downstream stages but MUST still emit ChainTerminatedReceipt with "
            "reason_code. Bypass of any stage (env var, debug mode) MUST emit GuardrailBypassReceipt to "
            "BUS D for L6 ingestion and is forbidden in production environment_class. 25+ guardrails "
            "exist; canonical execution-order contract and bypass telemetry are missing."
        ),
        "implied",
        "C. Safety / guardrails / authority",
        "L5 safety",
        "Pre-execution + Post-execution",
        "GuardrailStageReceipt; ChainTerminatedReceipt; GuardrailBypassReceipt; canonical_chain_order",
        "GuardrailChainExecutor; StageReceiptEmitter; BypassDetector; ProductionBypassRefuser",
        "Order honored; BLOCK short-circuits; bypass logged; production refuses bypass; receipts on BUS D",
        "CRITICAL",
        "0.95",
    ),
    (
        "10C-REQ-193",
        "C6-NEW-B prompt-attack regression suite (always-on golden adversarial)",
        "Derived requirement (Anthropic Adversarial Eval; OpenAI Red-team)",
        "Always-on golden adversarial set runs on every promotion; regression blocks promotion",
        (
            "A versioned PromptAttackRegressionSuite MUST run on every L6 6D promotion candidate covering "
            "minimum categories: instruction-injection, tool-injection-via-data, role-confusion, "
            "system-prompt-extraction, citation-fabrication, jailbreak-via-roleplay, encoding-bypass "
            "(base64/unicode), multi-turn-erosion. Pass criteria: 100 percent block-rate on level-1 attacks, "
            ">=95 percent on level-2, >=80 percent on level-3 (stretch). Any regression on level-1 MUST "
            "auto-block promotion and emit RedTeamRegressionAlert to L6 6A. AdversarialRedTeamerAgent "
            "exists; missing piece is the always-on regression-suite contract bound into the promotion "
            "gate."
        ),
        "implied",
        "C. Safety / guardrails / authority",
        "L5 safety + L6 observability",
        "Promotion + Shadow eval",
        "PromptAttackRegressionSuite; attack_category_taxonomy; RedTeamRegressionAlert",
        "RegressionSuiteRunner; LevelBlockRateScorer; PromotionAutoBlocker",
        "Level-1 100 percent block; level-1 regression auto-blocks; suite versioned; alert routed to L6",
        "HIGH",
        "0.92",
    ),
    # ---------- C7 Tracing ----------
    (
        "10C-REQ-194",
        "C7-NEW-A W3C traceparent cross-system propagation",
        "Derived requirement (OpenAI Tracing; W3C Trace Context spec)",
        "Cross-MCP and cross-agent calls propagate W3C traceparent header for end-to-end correlation",
        (
            "Every outbound call across a system boundary (MCP server, sub-agent dispatch, external HTTP, "
            "LLM provider invocation) MUST include the W3C Trace Context traceparent and tracestate "
            "headers. Inbound boundary handlers MUST extract these and continue the trace, never starting "
            "a new root span. End-to-end traces from L0 R0 ingress through L4 commit MUST share a single "
            "trace_id. Missing traceparent on a cross-system call is a contract violation logged to "
            "L6 6A. L6 has rich span emitters but no enforced traceparent propagation contract; "
            "fragmented traces hurt debug and post-mortem RCA."
        ),
        "implied",
        "D. Governance / capability / replay / observability",
        "L6 observability + all layers",
        "All phases (cross-cut)",
        "W3C_traceparent_header; tracestate_header; cross_boundary_correlation_record",
        "TraceparentInjector; TraceparentExtractor; CrossBoundaryValidator",
        "Outbound has header; inbound continues trace; single trace_id end-to-end; missing-header violation logged",
        "HIGH",
        "0.91",
    ),
    (
        "10C-REQ-195",
        "C7-NEW-B PII and secret scrubbing at telemetry egress",
        "Derived requirement (OpenAI Tracing §Privacy; SOC2/GDPR baseline)",
        "Telemetry egress refuses PII or secrets; scrubber runs at the OTEL exporter boundary",
        (
            "Before any OTEL span or log record leaves the process boundary (exporter to collector, log "
            "shipper to remote sink), a deterministic ScrubbingExporter MUST run pattern-based redaction "
            "for: API keys (provider regex set), JWT tokens, AWS credentials, email addresses, phone "
            "numbers, SSN/national-ID, credit cards, password fields, private SSH/TLS keys. Scrubbed "
            "spans MUST carry redaction_applied[] attribute listing categories scrubbed. The scrubber "
            "MUST be on the egress path, not opt-in at write time. ScrubberBypassRefuser MUST refuse to "
            "start the exporter without a registered scrubber. Telemetry leaks of secrets are a CRITICAL "
            "compliance failure; current OTEL pipeline has no canonical scrubbing layer."
        ),
        "implied",
        "C. Safety / guardrails / authority",
        "L6 observability + L5 safety",
        "All phases (cross-cut)",
        "ScrubbingExporter; redaction_applied; redaction_pattern_registry",
        "PiiScrubberRegistry; SecretPatternMatcher; ScrubberBypassRefuser; ExporterStartGate",
        "API key scrubbed; email redacted; bypass refused; redaction_applied attribute present; exporter refuses to start without scrubber",
        "CRITICAL",
        "0.95",
    ),
    # ---------- C8 MCP server design ----------
    (
        "10C-REQ-196",
        "C8-NEW-A MCP discovery cache TTL + invalidation contract",
        "Derived requirement (OpenAI MCP guide §Discovery; Anthropic SDK MCP)",
        "MCP tool/resource discovery cache versioned by server schema_hash with TTL and invalidation",
        (
            "MCP client wrappers MUST cache the (tools, resources, prompts) discovery response keyed by "
            "server_id + server_schema_hash, with TTL <= 5 minutes. On cache miss or TTL expiry, the "
            "wrapper MUST refetch and compare schema_hash; mismatch MUST emit McpServerSchemaDriftEvent "
            "and invalidate any cached tool selection that depended on the old schema. Stale tool "
            "schemas in the agent context cause silent tool-call failures and selection errors. "
            "mcp_client.py / figma_mcp_client.py implement clients without a uniform discovery cache "
            "contract; mcp_drift_recorder exists but is not bound to discovery caching."
        ),
        "implied",
        "D. Governance / capability / replay / observability",
        "L2 execution + L4 state",
        "Tool discovery + Tool invocation",
        "mcp_discovery_cache_entry; server_schema_hash; McpServerSchemaDriftEvent",
        "McpDiscoveryCacheManager; SchemaHashComparator; CachedSelectionInvalidator",
        "TTL honored; schema drift detected; downstream selections invalidated; drift event on BUS D",
        "HIGH",
        "0.89",
    ),
    (
        "10C-REQ-197",
        "C8-NEW-B MCP tool deprecation lifecycle",
        "Derived requirement (OpenAI MCP guide; Anthropic Writing Effective Tools §Deprecation)",
        "MCP tools carry deprecation metadata; agents are warned and routed to replacements",
        (
            "Each tool exposed by an MCP server MUST be able to declare deprecation metadata: "
            "{deprecated: bool, replacement_tool_name, removal_date, deprecation_reason}. The MCP "
            "client wrapper MUST surface deprecation warnings to the agent in the tool description "
            "envelope and MUST emit ToolDeprecationWarning to L6 on each invocation of a deprecated tool. "
            "After removal_date, invocation MUST raise ToolRemovedError; auto-route to replacement "
            "is OPTIONAL but MUST be configurable. Currently no deprecation lifecycle exists; tools "
            "silently disappear or change shape, breaking long-running agent contracts."
        ),
        "implied",
        "D. Governance / capability / replay / observability",
        "L2 execution",
        "Tool discovery + Tool invocation",
        "tool_deprecation_metadata; ToolDeprecationWarning; ToolRemovedError",
        "DeprecationMetadataValidator; DeprecationWarningEmitter; PostRemovalRefuser",
        "Deprecated tool warns agent; removal date enforced; replacement routing configurable; warnings logged",
        "HIGH",
        "0.88",
    ),
    # ---------- C9 Orchestration patterns ----------
    (
        "10C-REQ-198",
        "C9-NEW-A workflow pattern selection rationale logging",
        "Derived requirement (Anthropic Building Effective Agents 2025 §Patterns)",
        "Workflow pattern (chain/router/parallel/orchestrator/evaluator) selection rationale logged per run",
        (
            "Every L3 run MUST log a WorkflowPatternSelectionReceipt declaring which pattern was chosen "
            "from {prompt_chain, router, parallelization, orchestrator_workers, evaluator_optimizer, "
            "autonomous} with rationale_features {task_complexity_score, has_decomposable_subtasks, "
            "needs_iteration, has_fan_out, requires_critique}, and the alternative-pattern scores. "
            "L6 MUST ingest these to learn which pattern fits which task class. Currently "
            "prompt_chain_engine, parallelization_engine, recursive_orchestrator, evaluator_optimizer "
            "all exist but pattern-selection rationale is implicit in routing logic, blocking pattern-"
            "selection learning."
        ),
        "implied",
        "E. Metrics / evaluation / shadow / learning",
        "L3 orchestration + L6 observability",
        "Plan + Post-run learning",
        "WorkflowPatternSelectionReceipt; pattern_alternative_scores",
        "PatternSelectionLogger; PatternRationaleScorer; L6PatternKPIIngestor",
        "Receipt emitted per run; alternative scores recorded; L6 ingests; pattern-fit learning loop closed",
        "HIGH",
        "0.88",
    ),
    # ---------- C10 Cost/latency ----------
    (
        "10C-REQ-199",
        "C10-NEW-A per-request cost ceiling with circuit breaker",
        "Derived requirement (OpenAI cost-control; Anthropic responsible scaling)",
        "Per-request hard cost ceiling enforced; breach trips circuit breaker, blocks further LLM calls",
        (
            "Each ingressed request MUST carry a per_request_cost_ceiling_usd derived from "
            "(env_class, risk_tier, customer_tier). Cost is accumulated across all LLM calls, MCP calls, "
            "external API calls, and sub-agent dispatches. On 80 percent ceiling consumed, a soft warning "
            "MUST emit CostCeilingWarning. On 100 percent, the CostCircuitBreaker MUST trip: no further "
            "billable operations may execute; the run MUST exit with status COST_CEILING_TRIPPED and "
            "return partial results plus CostCeilingTripReceipt. Tripped runs MUST NOT silently degrade. "
            "g20_cost_latency_budget exists as runtime gate but no cross-call accumulator with circuit "
            "breaker is in place; risk of runaway cost on long-horizon agents is real."
        ),
        "implied",
        "C. Safety / guardrails / authority",
        "L5 safety + L3 orchestration",
        "All phases (cross-cut)",
        "per_request_cost_ceiling_usd; CostCeilingWarning; CostCeilingTripReceipt",
        "CostAccumulator; CircuitBreakerEnforcer; PartialResultExitHandler",
        "80 percent emits warning; 100 percent trips; further LLM calls refused; receipt produced; partial result returned",
        "CRITICAL",
        "0.94",
    ),
    (
        "10C-REQ-200",
        "C10-NEW-B per-workflow cost attribution",
        "Derived requirement (OpenAI cost analytics)",
        "Cost attributed per workflow_pattern + sub_agent + provider for L6 efficiency learning",
        (
            "Cost telemetry MUST be attributed at finer granularity than run-total: per "
            "{workflow_pattern, sub_agent_id, provider, tool_name}. Each LLM call span MUST carry "
            "cost.input_tokens, cost.output_tokens, cost.usd, cost.attribution_path. L6 6A MUST aggregate "
            "to produce CostAttributionReport per pattern per provider per week, feeding the L6 6D "
            "promotion gate which MAY demote pattern-provider combinations whose cost-per-success-outcome "
            "exceeds threshold. Closes the loop between cost observability and learning, enabling "
            "data-driven retirement of expensive low-value combinations."
        ),
        "implied",
        "E. Metrics / evaluation / shadow / learning",
        "L6 observability",
        "Post-run learning",
        "cost.attribution_path; CostAttributionReport; pattern_provider_cost_per_success_kpi",
        "CostAttributionAggregator; ReportEmitter; PromotionGateCostDemoter",
        "Attribution per pattern/provider/tool; weekly report; promotion uses cost-per-success; demotion path active",
        "HIGH",
        "0.89",
    ),
]


def main() -> None:
    with LEDGER.open("a", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        for req in REQS:
            writer.writerow([
                req[0], SOURCE, req[1], req[2], req[3], req[4],
                req[5], req[6], req[7], req[8], req[9], req[10],
                req[11], req[12], req[13],
            ])

    with MATRIX.open("a", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        for req in REQS:
            writer.writerow([
                req[0], "", "false", "none",
                f"NEW best-practice gap (Anthropic/OpenAI Wave 3-10 hybrid audit); see {req[1]}",
            ])

    print(f"Appended {len(REQS)} REQs ({REQS[0][0]}..{REQS[-1][0]}) covering C1, C3, C5, C6, C7, C8, C9, C10.")
    print(f"  Ledger: {LEDGER}")
    print(f"  Matrix: {MATRIX}")


if __name__ == "__main__":
    main()
