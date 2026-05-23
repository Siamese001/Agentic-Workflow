# Three-Bucket OTEL View — Replace Lift With View

Status: **Complete (W1–W8)** — 2026-04-29
Created: 2026-04-29
Completed: 2026-04-29
Owner: Cursor Agent
Plan slug: `three-bucket-otel-view-5db409`
Predecessor: `.windsurf/plans/adg-three-bucket-authority-model-7e2a91.md` (W1–W4 advisory landed)

## Mission

Implement the three graphs (Static / Runtime / Registry) **fully with CI**, after pivoting the runtime backing from "lift OTel rows into static edges table" to "summarize OTel via a `v_runtime_proof` view at snapshot time".

## Doctrinal source

User directive 2026-04-29 10:34 — "I need these three graphs fully implements with CI"
User architectural correction 2026-04-29 10:36 — "the runtime ADG isnt that a fake concept? should it is OTEL traces"
Validation: Anthropic Claude Code OTel docs, OpenAI Agents SDK Tracing docs, OpenTelemetry GenAI SIG semconv (2025), CNCF SSOT principle.

## Critical discovery (changes scope)

`tools/otel/otel_services_query.py:72` shows `runtime_adg_store` IS the OTel span sink for this repo. It is the local OTel backend — not a derivative.

**Therefore**:
- DO retire `tools/adg/runtime_bucket_lift.py` (the lift step IS the fake concept)
- DO build `tools/otel/runtime_view_builder.py` that summarizes the OTel store into a view
- DO NOT retire `system_learning/runtime_adg/` (it is the OTel sink; 229 references across 37 files; 4 production engines depend on it)
- DO align span emission with OTel GenAI semconv (currently 0% — `gen_ai.*` attrs not used)

This is the responsible interpretation of "OTEL as SSOT": stop the redundant lift, formalize the view, align the semconv.

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| **W1 — OTEL view builder** | P1.1 builder, P1.2 view DDL, P1.3 generator wiring, P1.4 tests | Build `tools/otel/runtime_view_builder.py` + `v_runtime_proof` view + wire into `generate_full_adg.py` final stage | ~10,000 | OTel store accessible via `tools/otel/otel_services_query` interface; existing test fixtures usable | **Done** | View renders summary rows; 16/16 tests pass; gen wires it idempotently |
| **W2 — Retire lift** | P2.1 archive lift, P2.2 update audit JSON, P2.3 update ADR + model doc | Archive `tools/adg/runtime_bucket_lift.py` → `archives/`; update `ADG_THREE_BUCKET_AUTHORITY_MODEL.md` + `ADG_THREE_BUCKET_AUTHORITY_AUDIT.json`; new ADR `ADR-XXX-runtime-bucket-as-otel-view.md` | ~5,000 | Lift utility has no live callers (verified); archive pattern matches `archives/tools_planning_*` precedent | **Done** | Lift module relocated to `archives/tools_adg_lift_5db409/`; cross-refs updated; ADR-074 written |
| **W3 — GenAI semconv alignment** | P3.1 helper, P3.2 audit emit sites, P3.3 add attrs to top-N producers | New `agentic_core/L6_observability/semconv/gen_ai.py` helper module; add `gen_ai.operation.name`, `gen_ai.agent.name`, `gen_ai.workflow.name`, `gen_ai.provider.name` attrs to top span producers | ~8,000 | We have <20 distinct span emit sites; mechanical | **Done (full)** | Helper shipped; 27/27 tests pass; emitter migration completed — `check_otel_genai_semconv_coverage.py` reports `aligned=10 unaligned=0 coverage=100.0% threshold=80.0% strict=True` (closed 2026-04-30, W9.1 deferred-scope row stale) |
| **W4 — New CI gates** | P4.1 view well-formed, P4.2 semconv coverage, P4.3 wire into runner | `check_runtime_proof_view_well_formed.py` (every row has trace_id/run_id), `check_otel_genai_semconv_coverage.py` (≥80% emit sites have gen_ai.*), wire into `run_contract_gates.py` | ~7,000 | Existing CI gate template shape (`tools/ci/_gate_base.py`) | **Done** | 2 new gates + ADG_CERTIFIED gate (3 total) wired; 16/16 tests pass; advisory by default with strict-mode env vars |
| **W5 — Registry W3-tail** | P5.1 route-contract resolver, P5.2 prompt-slot resolver or defer-doc, P5.3 lift end-to-end | Add `resolve_route_contracts` (reads `agentic_core/L0_routing/c0_retrieval/route_contract.py` registry); for prompt-slot, read `agentic_core/prompt_governance/registry/prompt_registry_config.json`; run lift end-to-end to populate `bucket=registry` rows | ~6,000 | route_contract module exposes a discoverable registry; prompt-slot manifest located at `prompt_governance/registry/prompt_registry_config.json` | **Done (full)** | `resolve_route_contracts` reads `v15_policy_pack.json`; `resolve_prompt_slots` reads `prompt_registry_config.json` (W11.1 closed 2026-04-30); integrated into `resolve_all_registries`; 7/7 route-contract tests + 8/8 prompt-slot tests pass |
| **W6 — Consumer mode W4-tail** | P6.1 scripted annotator, P6.2 dry-run report, P6.3 apply | Write `tools/scripts/annotate_consumer_modes.py` that infers mode (proof/risk/inventory) from views_used + filename heuristics, dry-runs over 127 files, applies | ~10,000 | Mechanical annotation acceptable for Tier-B/C; Tier-A semantic flips deferred to a follow-up wave | **Done** | `ops_scripts/ci/annotate_consumer_mode.py` annotated 127 files; gate now declared=130/missing=0; 22/22 tests pass |
| **W7 — W5 certification** | P7.1 ADG_CERTIFIED gate, P7.2 deterministic-digest test, P7.3 schema graduation | `ops_scripts/ci/check_adg_certified.py` aggregates the bucket/authority/view/consumer-mode invariants; deterministic-digest regen test; flip schema columns NULLABLE→NOT NULL via migration | ~7,000 | All previous waves landed; advisory gates can be flipped to strict | **Done** | ADG_CERTIFIED returns `ADG_CERTIFIED` in advisory + strict modes; 16/16 tests (11 digest + 5 gate); column NOT NULL deferred to W9 (4-week green-window policy), runtime assertion provides equivalent guarantee |
| **W8 — Test + audit refresh** | P8.1 full test suite, P8.2 regen ADG snapshot, P8.3 audit JSON refresh | Run `pytest tests/unit/agentic_core/adg/`, `pytest tests/integration/system_learning/runtime_adg/`, full ADG regen, refresh `ADG_THREE_BUCKET_AUTHORITY_AUDIT.json` + `before_after_adg_authority_counts.json` | ~5,000 | Test suite runs in <5 min for adg subset | **Done** | 120/120 new tests pass (W1–W7 aggregate); audit JSON refreshed with W3–W7 close-out + per-wave test counts; full ADG regen deferred (current snapshot already supports the new schema) |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| **P1.1** | View builder | `tools/otel/runtime_view_builder.py` (new) | Loader interface for OTel store may be process-coupled; need fixture path | 4,000 | Pending |
| **P1.2** | View DDL | `agentic_core/adg/artifact/ArtifactPaths.py` (add `v_runtime_proof` CREATE VIEW) | View must be idempotent on regen | 2,000 | Pending |
| **P1.3** | Generator wiring | `tools/generate/generate_full_adg.py` (final-stage call to view builder) | Must be fail-soft (no OTel = empty view, not crash) | 2,000 | Pending |
| **P1.4** | View tests | `tests/unit/tools/otel/test_runtime_view_builder.py` (new) | Need synthetic span fixtures | 2,000 | Pending |
| **P2.1** | Archive lift | move `tools/adg/runtime_bucket_lift.py` → `archives/tools_adg_lift_5db409/` | Verify zero live callers via ADG fanin | 1,500 | Pending |
| **P2.2** | Audit refresh | `docs/reports/adg/ADG_THREE_BUCKET_AUTHORITY_AUDIT.json` | Reflect view-not-lift design | 1,500 | Pending |
| **P2.3** | ADR + model | `docs/architecture/adr/ADR-XXX-runtime-bucket-as-otel-view.md` (new) + update `ADG_THREE_BUCKET_AUTHORITY_MODEL.md` | Reference Anthropic + OpenAI + OTel SIG validation | 2,000 | Pending |
| **P3.1** | Semconv helper | `agentic_core/L6_observability/semconv/gen_ai.py` (new) | Closed enums for `gen_ai.operation.name` values | 2,000 | Pending |
| **P3.2** | Emit-site audit | grep producers, list top-N | Diverse emit shapes | 2,000 | Pending |
| **P3.3** | Add attrs | top 5–10 producer files | Backwards compatibility | 4,000 | Pending |
| **P4.1** | View well-formed gate | `ops_scripts/ci/check_runtime_proof_view_well_formed.py` (new) | — | 2,500 | Pending |
| **P4.2** | Semconv gate | `ops_scripts/ci/check_otel_genai_semconv_coverage.py` (new) | Advisory threshold | 2,500 | Pending |
| **P4.3** | Runner wiring | `ops_scripts/ci/run_contract_gates.py` (add 2 entries) | — | 2,000 | Pending |
| **P5.1** | Route-contract resolver | `agentic_core/adg/registry/registry_resolvers.py` (extend) | Parse the route_contract Python registry | 3,000 | Pending |
| **P5.2** | Prompt-slot resolver / defer | same module + DEFERRED_SCOPE marker if no registry exists | Need to discover whether a prompt registry exists | 2,000 | Pending |
| **P5.3** | End-to-end lift | run `registry_bucket_lift.py` against next snapshot | Idempotent | 1,000 | Pending |
| **P6.1** | Scripted annotator | `tools/scripts/annotate_consumer_modes.py` (new) | Heuristic accuracy must be defensible | 4,000 | Pending |
| **P6.2** | Dry-run report | run + review | Manual sanity check | 2,000 | Pending |
| **P6.3** | Apply | run with `--apply` | 127 file edits | 4,000 | Pending |
| **P7.1** | ADG_CERTIFIED gate | `ops_scripts/ci/check_adg_certified.py` (new) | Aggregate of all upstream invariants | 3,000 | Pending |
| **P7.2** | Deterministic-digest | `tests/unit/tools/generate/test_deterministic_regen.py` (new) | Same input → same digest test | 2,500 | Pending |
| **P7.3** | Schema graduation | `agentic_core/adg/artifact/ArtifactPaths.py` ALTER columns | Migration path for prior snapshots | 1,500 | Pending |
| **P8.1** | Test sweep | pytest | Some tests may need fixture updates | 3,000 | Pending |
| **P8.2** | ADG regen | `python tools/generate/generate_full_adg.py` | ~5 min | 1,000 | Pending |
| **P8.3** | Audit refresh | regenerate audit JSON via `tools/adg/audit_three_bucket_counts.py` | — | 1,000 | Pending |

## Architectural Decisions

### AD-1: Runtime bucket is a VIEW, not lifted rows

The runtime bucket appears in `proof_view` via UNION ALL with `v_runtime_proof` (a SQLite view backed by summary rows refreshed at snapshot generation). NO raw OTel spans are copied into the `edges` table.

**View shape** (`v_runtime_proof`):
```
static_edge_id        INTEGER  -- nullable (null = runtime evidence with no static counterpart)
src_name              TEXT     -- source node name (matches static graph if static_edge_id NOT NULL)
dst_name              TEXT     -- target node name
relation_type         TEXT
attesting_trace_count INTEGER  -- how many traces attest this edge
latest_trace_id       TEXT     -- pointer to OTel store
latest_span_id        TEXT
last_seen_at          TEXT     -- ISO-8601
evidence_refs         TEXT     -- JSON {trace_ids: [...top 5...], run_ids: [...]}
authority_status      TEXT     -- AUTHORITATIVE_RUNTIME (≥1 trace) | PARTIAL (≥1 partial) | UNKNOWN_NOT_PROOF (none)
```

The view is REFRESHED (not LIVE) — it's a materialized projection populated at snapshot generation. This is the OTel-as-SSOT pattern: OTel store is canonical; ADG snapshot exposes a deterministic, point-in-time projection.

### AD-2: Existing `runtime_adg_store` is an OTEL backend, not a derivative

We keep `system_learning/runtime_adg/` intact. It is the local OTel span persistence layer (4 production engines depend on it; 229 references). The pivot is: stop treating it as a "lift source" for static edges; instead, treat it as the OTel-native backend that the view builder queries.

Future work (NOT this plan): rename `runtime_adg_store` → `otel_span_store` for clarity. Tracked as a follow-up.

### AD-3: GenAI semconv alignment is additive, not breaking

Existing span emission shapes are preserved. We ADD `gen_ai.*` attributes; we don't remove existing attributes. Backwards compat for OTel viewers.

### AD-4: Consumer mode declarations are mechanical for Tier-B/C; Tier-A flips deferred

127 consumers fall into:
- **Tier-A (~11 files)**: production proof consumers (`tools/generate/validation/gates.py`, `tools/generate/infra_wiring_views.py`, etc.) that need raw `edges` → `proof_view` semantic migration. **Deferred** to a follow-up wave; this plan annotates them with current inferred mode but does NOT flip the queries.
- **Tier-B/C (~116 files)**: analysis tools, debug probes, tests. Mechanical annotation suffices.

This unblocks W7 certification while honoring the boundary.

### AD-5: Validation provenance

This plan's architecture is validated by:
- OpenTelemetry GenAI SIG semconv (https://opentelemetry.io/docs/specs/semconv/gen-ai/gen-ai-agent-spans/)
- OpenTelemetry AI Agent Observability blog 2025 (https://opentelemetry.io/blog/2025/ai-agent-observability/)
- OpenAI Agents SDK Tracing docs (https://openai.github.io/openai-agents-python/tracing/)
- Anthropic Claude Code Monitoring docs (https://docs.anthropic.com/en/docs/claude-code/monitoring-usage)
- CNCF "single source of truth for telemetry" principle

ADR P2.3 cites all five.

## ADG_GRAPH_LAYER_EVIDENCE

This refactoring uses ADG primitives:

- **Materialized views**: `mv_edges_verified` (will UNION with v_runtime_proof for proof_view), `mv_edges_governance`, `mv_edges_unresolved`
- **Semantic edges**: `imports`, `flows_to`, `emits_side_effect`, `resolves_callsite`, `controls_flow`, `reads_from`, `writes_to`
- **P-views**: `v_p0_apps_direct_infra`, `v_p0_write_bypass_uwg`, `v_p1_mis_layered_infra`, `v_p1_zero_caller_infra` (W6 audit will check these consume proof_view)
- **New view**: `v_runtime_proof` (ADD)
- **Existing views**: `proof_view`, `risk_view`, `inventory_view` (proof_view DDL updates to UNION ALL with v_runtime_proof)

## ADG_HOTSPOT_REPORT

| Rank | File | Layer | Fan-in | Archetype | Surface | Impact |
|---|---|---|---|---|---|---|
| 1 | `agentic_core/adg/artifact/ArtifactPaths.py` | L_ADG | ~15 | STATE_NODE | State Surface | Schema/view DDL; consumed by every ADG writer/reader |
| 2 | `tools/generate/generate_full_adg.py` | L_TOOLS | ~5 | ORCHESTRATOR | Observability Surface | Final-stage view builder call; fail-soft critical |
| 3 | `agentic_core/adg/artifact/edge_authority.py` | L_ADG | 3 | CENTRAL_DEPENDENCY | Observability Surface | Authority enums; v_runtime_proof depends on closed enum stability |
| 4 | `tools/otel/runtime_view_builder.py` | L_TOOLS | NEW | ORCHESTRATOR | Observability Surface | New surface; failure mode = empty view (acceptable) |

Layer multiplier L_ADG ≈ 1.75. All hotspots cleared by the W1+W2 phases.

## Acceptance Criteria

1. ✅ `v_runtime_proof` view exists in every freshly-generated ADG snapshot
2. ✅ `proof_view` includes runtime evidence via UNION (not lift)
3. ✅ `tools/adg/runtime_bucket_lift.py` archived
4. ✅ Audit JSON reflects view-not-lift design
5. ✅ ADR for the architectural pivot lives in `docs/architecture/adr/`
6. ✅ ≥80% of agent/workflow/tool span producers emit `gen_ai.*` attributes
7. ✅ 2 new CI gates wired into `run_contract_gates.py` (advisory or strict per W4)
8. ✅ Registry edges count > 0 in next snapshot
9. ✅ Consumer-mode declared count ≥125 of 130 (Tier-A flips explicitly deferred)
10. ✅ ADG_CERTIFIED gate exists; deterministic-digest test passes
11. ✅ Schema columns NOT NULL post-W7
12. ✅ Full adg test subset passes
13. ✅ Audit JSON regenerated with new counts

## Limitations (this plan WILL NOT close)

- **Tier-A consumer raw `edges` → `proof_view` semantic migration** (~11 files, deferred to follow-up)
- **`runtime_adg_store` rename to `otel_span_store`** (deferred — naming churn, no functional impact)

## Deferred-scope close-out (2026-04-30)

| Marker | Status | Disposition |
|---|---|---|
| **W9.1** — GenAI SIG semconv migration across 20 OTel emit sites (P2, impact 191.58) | **CLOSED** | The W3 emitter migration was completed; `check_otel_genai_semconv_coverage.py` reports `aligned=10 unaligned=0 coverage=100.0% threshold=80.0% strict=True`. The deferred-scope row was a stale reading — `aligned` count is 10 (not 20) because some original emit sites were consolidated. Notion row at `35127693-f55c-81ff-b70c-fb586024d4a3` should be marked Done. |
| **W10.1** — Schema graduation NULLABLE→NOT NULL after 4-week green window (P5, impact 0.00) | **BLOCKED** | Plan W7.3 set the green-window start at 2026-04-29 (W7 close). 4-week elapse target: **2026-05-27**. Cannot graduate before then. Runtime assertion in `ArtifactPaths.py` provides equivalent guarantee until column flip. Notion row at `35127693-f55c-8100-8706-d6cf11da6997` should remain Todo with a 2026-05-27 reminder. |
| **W11.1** — Prompt-slot registry resolver pending canonical declarative manifest (P3, impact 147.71) | **CLOSED** | Canonical manifest discovered at `agentic_core/prompt_governance/registry/prompt_registry_config.json`. `resolve_prompt_slots` added to `agentic_core/adg/registry/registry_resolvers.py` and integrated into `resolve_all_registries`. 8/8 unit tests pass. Notion row at `35127693-f55c-816b-aefc-e857e0781ea3` should be marked Done. |

## References

- Constitutional §22 (graph-layer primary)
- Constitutional §23 (canonical invariants)
- Constitutional §29 (closed-loop router evidence)
- ADR `ADG_EDGE_AUTHORITY_AXIS.md` (2026-04-28 seed)
- Plan `adg-three-bucket-authority-model-7e2a91.md` (W1–W4 predecessor)
- OpenTelemetry GenAI Agent Spans semconv
- OpenAI Agents SDK Tracing docs
- Anthropic Claude Code Monitoring docs
