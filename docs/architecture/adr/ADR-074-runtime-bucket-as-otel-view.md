# ADR-074 — Runtime Bucket as OTEL View (Replace Lift With View)

**Status**: Accepted
**Date**: 2026-04-29
**Deciders**: User (architectural correction), Codex (validation + implementation)
**Plan**: `.codex/plans/three-bucket-otel-view-5db409.md`
**Supersedes**: parts of ADR-030 (Runtime ADG Ingest Contract) — see "Relationship to ADR-030" below.

## Context

The 2026-04-29 three-bucket authority model (predecessor plan
`adg-three-bucket-authority-model-7e2a91`) shipped W1–W4 with a runtime
bucket implementation that LIFTED OTel spans from `runtime_adg.sqlite` into
the static `edges` table via `tools/adg/runtime_bucket_lift.py`. The lift
produced one row per span event in the unified `edges.bucket=runtime` rows.

During the 2026-04-29 mid-day review the user posed a sharp critique:

> the runtime ADG isnt that a fake concept? should it is OTEL traces

This was correct. The implementation had three problems:

1. **Re-encoding.** The lift took OTel-shaped spans and re-encoded them as
   `(src, dst, relation_type)` rows, flattening structured span attributes
   into a fixed shape. Information loss.
2. **Two indirections.** Spans landed in `runtime_adg_store` (the OTel sink)
   and were then copied into `edges`. The same evidence existed in two
   stores, with the second being a strict subset of the first.
3. **Operational fragility.** The "0% runtime coverage" status in the audit
   JSON was a measurement artifact: nobody had run the lift. The runtime
   evidence existed in the OTel store all along.

A web search across Anthropic's Claude Code monitoring docs, OpenAI's Agents
SDK tracing docs, and the OpenTelemetry GenAI SIG semconv (gen-ai-agent-spans)
confirmed that the industry standard is **OTel-as-SSOT for runtime
evidence**. Neither Anthropic nor OpenAI builds a derivative graph store on
top of OTel; both treat the trace tree itself as the runtime graph.

## Decision

**The runtime bucket is implemented as a SUMMARY VIEW
(`v_runtime_proof` table) refreshed at snapshot generation time, not as
lifted rows in the unified `edges` table.**

Concretely:

1. The static ADG snapshot schema gains a new table `v_runtime_proof`
   (defined in `agentic_core/adg/artifact/edge_authority.py` constant
   `SQL_CREATE_V_RUNTIME_PROOF`), with one row per
   `(src_name, dst_name, relation_type)` triple.
2. The new builder `tools/otel/runtime_view_builder.py` queries the
   `runtime_adg_store` (the local OTel span sink) and writes summary rows
   into `v_runtime_proof` with `attesting_trace_count`, `latest_trace_id`,
   and `evidence_refs={trace_ids:[...top 5...], run_ids:[...]}`.
3. The convenience view `proof_view_all` UNIONs `edges`-proof rows with
   `v_runtime_proof` AUTHORITATIVE_RUNTIME rows on a normalized projection,
   for consumers that need cross-bucket proof.
4. `tools/adg/runtime_bucket_lift.py` is **archived** to
   `archives/tools_adg_lift_5db409/`. No production code referenced it
   outside its own tests.
5. The runtime classifier `runtime_authority_for(attesting_trace_count,
   partial_trace_count)` maps OTel evidence counts to the closed runtime
   enums:
   - `>=1` verified trace → `(VERIFIED_RUNTIME, AUTHORITATIVE_RUNTIME)`
   - `0` verified, `>=1` partial → `(PARTIAL_TRACE, PARTIAL)`
   - `0` of either → `(MISSING_TRACE, UNKNOWN_NOT_PROOF)`

## Industry Validation

This decision aligns with five external reference points:

| Source | What it says | Relevance |
|---|---|---|
| [OpenTelemetry GenAI SIG semconv](https://opentelemetry.io/docs/specs/semconv/gen-ai/gen-ai-agent-spans/) | Standardized agent span types: `create_agent`, `invoke_agent`, `invoke_workflow`, `execute_tool` | The trace tree IS the runtime graph |
| [OpenTelemetry AI Agent Observability blog 2025](https://opentelemetry.io/blog/2025/ai-agent-observability/) | "Tighter integration with AI model observability to provide end-to-end visibility" | OTel is the unified surface, not a feed |
| [Anthropic Claude Code Monitoring](https://docs.anthropic.com/en/docs/claude-code/monitoring-usage) | Claude Code exports OTel directly to user's chosen collector | No intermediate Claude-runtime-graph |
| [OpenAI Agents SDK Tracing](https://openai.github.io/openai-agents-python/tracing/) | TraceProvider + BatchTraceProcessor + BackendSpanExporter; community OTel bridge plugs in as a processor | OTel is terminal, no derivative storage |
| CNCF/OTel "single source of truth" principle | "Avoid reinventing the wheel; align with existing OpenTelemetry standards" | Custom derivative graphs are the anti-pattern |

The OLD design (lift to `edges.bucket=runtime`) had **zero published
patterns** supporting it. The NEW design (OTel-as-SSOT, view-on-demand) has
five.

## Consequences

### Positive

- **No re-encoding.** Span attributes stay in the OTel store; the view
  references trace_ids, not flattened span data.
- **Single SoT.** The OTel store (`runtime_adg_store` / `FileBackedRuntimeADGStore`)
  is the canonical runtime graph; the view is a deterministic projection at
  snapshot time.
- **Industry-aligned.** Future migration to a real OTel collector
  (Jaeger/Tempo/SigNoz/etc.) requires only swapping the store reader in
  `runtime_view_builder.py` — the view shape and CI gates do not change.
- **CI gates assert against real evidence.** `check_runtime_proof_view_well_formed.py`
  (W4) asserts every AUTHORITATIVE_RUNTIME row has a real trace_id; this is
  meaningful only because the trace_id IS the evidence pointer, not a
  derivative.
- **Fail-soft.** Empty OTel store yields empty `v_runtime_proof` and
  generation continues; nothing assumes runtime evidence is required for
  static / registry buckets to work.

### Negative

- **`runtime_adg_store` naming is now misleading.** It is, functionally,
  the local OTel span sink. A future rename to `otel_span_store` is tracked
  as deferred scope.
- **The view is point-in-time, not live.** Consumers querying
  `v_runtime_proof` see the OTel state at snapshot generation. For live
  runtime introspection, callers should query the OTel store directly via
  `tools/otel/otel_services_query.py`. Documented.
- **`evidence_refs.trace_ids` is bounded to top-5.** Consumers wanting all
  attesting traces for an edge must follow the trace_id pointer back into
  the OTel store. This is a deliberate trade-off (snapshot size vs. full
  attestation).

### Mitigations Considered and Rejected

| Alternative | Why rejected |
|---|---|
| Keep both lift + view (parallel) | Doubles storage; doubles CI gate surface; resolves nothing. |
| Make `v_runtime_proof` a SQL VIEW (not table) | Requires the OTel store to be a SQLite attachment; couples snapshot to live runtime; loses point-in-time semantics. |
| Lift but with smaller summary rows | Still copies data; still has the "0% coverage = nobody ran the lift" trap. |
| Retire `system_learning/runtime_adg/` entirely | 229 references across 37 files, including 4 production engines. Out-of-scope for this change. |

## Relationship to ADR-030

ADR-030 (Runtime ADG Ingest Contract) defined the contract for in-process
producers calling `emit_span_to_runtime_adg` / `emit_spans_to_runtime_adg`
to land OTel-shaped spans in the runtime ADG store. **That contract is
preserved.** This ADR does not modify the producer side; it modifies only
the **consumer** side — replacing the lift step with a view-builder step.

ADR-030's "Trace ingest freshness" KPI continues to operate; the
`runtime_view_builder` is purely additive.

## Implementation

| Component | File | Status |
|---|---|---|
| Schema constant | `agentic_core/adg/artifact/edge_authority.py` `SQL_CREATE_V_RUNTIME_PROOF` | ✅ Landed (W1) |
| All-bucket proof view | `agentic_core/adg/artifact/edge_authority.py` `SQL_PROOF_VIEW_ALL` | ✅ Landed (W1) |
| Classifier | `agentic_core/adg/artifact/edge_authority.py` `runtime_authority_for(...)` | ✅ Landed (W1) |
| Builder | `tools/otel/runtime_view_builder.py` | ✅ Landed (W1) |
| Schema wiring | `agentic_core/adg/artifact/ArtifactPaths.py` (DDL block 6) | ✅ Landed (W1) |
| Generator wiring | `tools/generate/generate_full_adg.py` (final stage call) | ✅ Landed (W1) |
| Tests | `tests/unit/tools/otel/test_runtime_view_builder.py` (16 tests) | ✅ Passing (W1) |
| Lift archived | `tools/adg/runtime_bucket_lift.py` → `archives/tools_adg_lift_5db409/` | ✅ Landed (W2) |
| CI gate | `ops_scripts/ci/check_runtime_proof_view_well_formed.py` | Pending W4 |
| GenAI semconv alignment | `agentic_core/L6_observability/semconv/gen_ai.py` | Pending W3 |

## Verification

Builder smoke test (16 unit tests pass):

```
pytest tests/unit/tools/otel/test_runtime_view_builder.py
============================== 16 passed in 4.89s ==============================
```

End-to-end will be verified in W8 by regenerating the full ADG snapshot and
confirming `v_runtime_proof` populates from the live `runtime_adg_store`.

## References

- Plan: `.codex/plans/three-bucket-otel-view-5db409.md`
- Predecessor plan: `.codex/plans/adg-three-bucket-authority-model-7e2a91.md`
- Three-bucket model spec: `docs/architecture/adr/ADG_THREE_BUCKET_AUTHORITY_MODEL.md`
- Audit: `docs/reports/adg/ADG_THREE_BUCKET_AUTHORITY_AUDIT.json`
- ADR-030: Runtime ADG Ingest Contract (preserved)
- ADR-027: OTel Anthropic Alignment (W3C trace context — preserved)
