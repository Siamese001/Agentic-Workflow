"""Append C2 Context Engineering best-practice gap REQs (REQ-180..185) to ledger and matrix.

Wave 2 of hybrid audit: C2 concern (context engineering).
Severity: CRITICAL (REQ-182, REQ-185) + HIGH (REQ-180, REQ-181, REQ-183, REQ-184).
"""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LEDGER = ROOT / "docs/reports/design/10c_reconciliation/10c_semantic_requirement_ledger.csv"
MATRIX = ROOT / "docs/reports/design/10c_reconciliation/10c_requirements_vs_10a_matrix.csv"

SOURCE = "best-practice gap analysis 2026-04-30 wave2 C2 context engineering"

# (req_id, source_section, source_unit_type, source_text_short, canonical_statement,
#  direct_or_implied, semantic_class, layer_owner, runtime_phase, required_artifacts,
#  required_controls, required_tests, severity, confidence)
REQS = [
    (
        "10C-REQ-180",
        "C2-NEW-A tool-result clearing gate",
        "Derived requirement (Anthropic Effective Context Engineering 2025 §Tool-result clearing)",
        "PA.5 budget enforcement triggers tool-result clearing before dropping exemplars",
        (
            "PA.5 budget enforcement MUST trigger tool-result clearing (replace consumed tool outputs "
            "with lightweight stubs preserving tool_call_id and status) BEFORE dropping optional "
            "exemplars in the deterministic trim cascade (insert as trim step 2.5). Tool-result stubs "
            "MUST be sufficient for citation provenance but MUST NOT count toward the context token "
            "budget. Each clearing event MUST be logged as a CompactionRecord with action=tool_result_cleared "
            "and original_token_count + stub_token_count fields. Compaction module exists; standalone gate "
            "wired into PA.5 trim order is missing."
        ),
        "implied",
        "B. Prompt assembly / context engineering",
        "L1 cognition + L3 orchestration",
        "Prompt assembly + Long-horizon loop",
        "ToolResultStub; CompactionRecord(action=tool_result_cleared); pa5_trim_step_2_5_receipt",
        "ToolResultClearingGate; CompactionRecordEmitter; StubTokenAccountant",
        "Stub replaces output without losing tool_call_id; budget freed equals original-stub delta; citation chain still resolves; trim order honored before exemplar drop",
        "HIGH",
        "0.91",
    ),
    (
        "10C-REQ-181",
        "C2-NEW-B structured agent scratchpad",
        "Derived requirement (Anthropic Effective Context Engineering 2025 §Structured note-taking)",
        "Typed AgentScratchpad persisted outside context window; injected via M0 slot",
        (
            "L3 orchestration loop MUST provide a typed AgentScratchpad persisted outside the context "
            "window. The scratchpad MUST support keyed read/write of structured notes (typed schema; not "
            "free-text), survive compaction events, and be available to the next loop iteration via a "
            "deterministic injection into the M0 (memory) slot during PA.2 slot composition. Scratchpad "
            "writes MUST be OTEL-traced with span attributes scratchpad.key scratchpad.bytes_written "
            "scratchpad.write_count. The scratchpad MUST be bounded (max_keys + max_bytes_per_key) "
            "with deterministic eviction (LRU) when bounds exceeded. semantic_cache_manager.py and "
            "thought_redactor.py provide adjacent primitives but no formal scratchpad lifecycle exists."
        ),
        "implied",
        "B. Prompt assembly / context engineering",
        "L3 orchestration + L4 state",
        "Long-horizon loop",
        "AgentScratchpad; ScratchpadWriteReceipt; M0_slot_injection_record",
        "ScratchpadStore; ScratchpadSchemaValidator; ScratchpadLRUEvictor; M0SlotInjector",
        "Typed write/read round trip; survives compaction; M0 injection deterministic; LRU eviction at bounds; OTEL spans emitted",
        "HIGH",
        "0.90",
    ),
    (
        "10C-REQ-182",
        "C2-NEW-C trust-level propagation through PA",
        "Derived requirement (Anthropic Security 2025 + OpenAI Guardrails)",
        "Per-chunk trust_level propagated through prompt assembly; refuses untrusted content in authority slots",
        (
            "Every ContextItem and VerifiedChunk entering the PA pipeline MUST carry a trust_level in "
            "{system, policy, user, tool_output, external_retrieval}. PA.2 slot composition MUST refuse "
            "to place content with trust_level in {tool_output, external_retrieval} into authority slots "
            "S0/D0/I0/M0. PA.4 validation MUST reject any prompt where untrusted content appears above "
            "the C0 authority boundary. G13 ToolOutputTrustGate covers runtime detection of instruction-"
            "shaped tool output; this requirement covers compile-time structural enforcement at assembly. "
            "Violation MUST raise PromptAssemblyError with reason_code=trust_boundary_violation and route "
            "to L5 safety-plane for adversarial-injection logging."
        ),
        "implied",
        "C. Safety / guardrails / authority",
        "L1 cognition + L5 safety",
        "Prompt assembly + Pre-execution",
        "trust_level field on ContextItem; PA.2_trust_validation_record; PA.4_authority_boundary_check",
        "TrustLevelPropagator; AuthoritySlotTrustValidator; UntrustedContentRefuser",
        "Tool output cannot occupy S0/D0/I0/M0; external retrieval same; user content allowed in U0; system in S0; PA.4 rejects violations; G13 still active for runtime layer",
        "CRITICAL",
        "0.94",
    ),
    (
        "10C-REQ-183",
        "C2-NEW-D context utilization telemetry",
        "Derived requirement (Anthropic Observability 2025 + OpenAI Tracing)",
        "Per-turn OTEL span attributes for context tokens, slot fill, trim steps, overflow status",
        (
            "Each LLM call MUST emit an OTEL span with attribute set: context.total_tokens, "
            "context.slot_fill_pct (per slot S0..H0 + R0), context.trim_steps_applied (list of step IDs "
            "from BUDGET_TRIM_ORDER), context.overflow_status (OK/TRIMMED/OVERFLOW/REFINE/ABSTAIN), "
            "context.compaction_triggered (bool), context.exemplar_count, context.must_use_token_count, "
            "context.tool_results_cleared_count. L6 6A MUST ingest these for context-efficiency dashboards "
            "and for calibrating PA.5 budget thresholds via the learning flywheel. Missing context "
            "telemetry on an LLM call is a contract violation. ResourceManagerAgent has partial "
            "utilization tracking; this requirement formalizes the per-turn span schema."
        ),
        "implied",
        "E. Metrics / evaluation / shadow / learning",
        "L1 cognition + L6 observability",
        "Prompt assembly + Post-run learning",
        "context_utilization_span; pa5_trim_telemetry; L6_context_efficiency_kpi",
        "ContextSpanEmitter; SpanAttributeValidator; L6ContextKPIIngestor; BudgetThresholdCalibrator",
        "Span emitted on every LLM call; missing attribute fails contract; L6 ingestion produces dashboard; calibration loop adjusts PA.5 thresholds within bounds",
        "HIGH",
        "0.92",
    ),
    (
        "10C-REQ-184",
        "C2-NEW-E citation chain across compaction",
        "Derived requirement (Anthropic Citations + Effective Context Engineering 2025)",
        "CompactionResult preserves citation chain mapping original_chunk_id to compacted_summary_id",
        (
            "CompactionResult MUST include a citation_chain field of type list[CitationMapping] where each "
            "CitationMapping carries (original_chunk_id, compacted_summary_id, original_source_uri, "
            "preserved_quote, span_offsets). Post-compaction, any citation referencing a compacted chunk "
            "MUST resolve via this chain to the original_source_uri. The evidence contract (C0.5) MUST "
            "refuse to finalize if any live citation references a chunk that was compacted without a "
            "corresponding CitationMapping entry; status MUST be set to "
            "EvidenceStatus.COMPACTION_CITATION_BROKEN and routed back to L1 refine. context_compaction.py "
            "docstring mentions citation preservation but no formal binding exists in CompactionResult."
        ),
        "implied",
        "B. Prompt assembly / context engineering",
        "L3 orchestration + L1 cognition",
        "Long-horizon loop + Refine",
        "CitationMapping; CompactionResult.citation_chain; EvidenceStatus.COMPACTION_CITATION_BROKEN",
        "CitationChainBuilder; CitationResolverPostCompaction; EvidenceContractCitationValidator",
        "Compacted chunk citation resolves to original URI; broken chain refused at C0.5; refine loop fires; preserved_quote available for response grounding",
        "HIGH",
        "0.90",
    ),
    (
        "10C-REQ-185",
        "C2-NEW-F session-to-persistent memory promotion",
        "Derived requirement (Anthropic Memory + OpenAI Stateful Agents)",
        "L4 MemoryPromotionGate evaluates session items for promotion to persistent store with provenance",
        (
            "L4 state MUST implement a MemoryPromotionGate that evaluates session-scoped scratchpad "
            "entries and semantic cache items for promotion to the persistent store. Promotion criteria "
            "MUST include: access_count >= access_threshold, relevance_score >= tau_relevance, and "
            "freshness check (not past TTL). Promoted items MUST carry full provenance: originating "
            "run_id, turn_number, source_slot in {M0, C0, scratchpad}, promotion_decision_id. Demotion "
            "(persistent -> archive) MUST require an L6 learning signal (LearningProposal-class), "
            "not silent TTL expiry. The gate MUST emit MemoryPromotionReceipt and MemoryDemotionReceipt "
            "into BUS D for L6 ingestion. Closes the gap between Anthropic structured note-taking and "
            "OpenAI stateful-agents best practices; current L4 memory has TTL but no decision-driven "
            "promotion lifecycle."
        ),
        "implied",
        "D. Governance / capability / replay / observability",
        "L4 state + L6 observability",
        "Post-run learning",
        "MemoryPromotionGate; MemoryPromotionReceipt; MemoryDemotionReceipt; persistent_store_provenance",
        "MemoryPromotionEvaluator; AccessCounter; RelevanceScorer; DemotionGateLearningSignalRequirer",
        "Promotion at thresholds; provenance preserved; demotion requires L6 signal not TTL alone; receipts on BUS D; L6 calibrates thresholds",
        "CRITICAL",
        "0.93",
    ),
]


def main() -> None:
    # Append to ledger
    with LEDGER.open("a", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        for req in REQS:
            writer.writerow([
                req[0],  # req_id
                SOURCE,  # source_file
                req[1],  # source_section
                req[2],  # source_unit_type
                req[3],  # source_text_short
                req[4],  # canonical_requirement_statement
                req[5],  # direct_or_implied
                req[6],  # semantic_class
                req[7],  # layer_owner
                req[8],  # runtime_phase
                req[9],  # required_artifacts
                req[10],  # required_controls
                req[11],  # required_tests
                req[12],  # severity
                req[13],  # confidence
            ])

    # Append to matrix
    with MATRIX.open("a", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        for req in REQS:
            writer.writerow([
                req[0],
                "",
                "false",
                "none",
                f"NEW best-practice gap (Anthropic/OpenAI Wave 2 C2 context engineering); see {req[1]}",
            ])

    print(f"Appended {len(REQS)} REQs ({REQS[0][0]}..{REQS[-1][0]}) to ledger and matrix.")
    print(f"  Ledger: {LEDGER}")
    print(f"  Matrix: {MATRIX}")


if __name__ == "__main__":
    main()
