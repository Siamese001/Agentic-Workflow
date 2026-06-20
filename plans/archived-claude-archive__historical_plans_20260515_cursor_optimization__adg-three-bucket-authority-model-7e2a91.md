---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\historical_plans_20260515_cursor_optimization\\adg-three-bucket-authority-model-7e2a91.md'
original_relative_path: '_archive\\historical_plans_20260515_cursor_optimization\\adg-three-bucket-authority-model-7e2a91.md'
source_sha256: af03de3626206a599b3ac04402fc66e07b7c37878e5d982d4fb2b83dc6587238
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# ADG Three-Bucket Authority Model

Status: **Superseded by `adg-three-bucket-unified-c4f8e2`** (2026-04-30)
Predecessor status preserved below. Open Notion Wave/Phase rows migrated to the unified plan slug.
Created: 2026-04-29
Owner: Cascade

## Mission

Redesign and harden ADG around the three-bucket graph authority model:

1. **STATIC GRAPH** — what the code can reference (AST evidence)
2. **RUNTIME GRAPH** — what actually happened (OTel traces, sealed receipts)
3. **REGISTRY GRAPH** — what configuration declares as wired (registries, configs, plugin maps)

Source of mission: 2026-04-29 user directive "Redesign and harden ADG around the correct three-bucket graph authority model."

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| **W1 — Foundation** | P1.1 schema, P1.2 classifier, P1.3 views, P1.4 backfill, P1.5 tests, P1.6 deliverables | Schema + STATIC bucket reclassification + 3 views + tests + 4 deliverable artifacts | ~24,000 | Existing `edges.authority` (6-value enum from 2026-04-28) is the seed; mapping is mechanical | **In progress** | Schema accepts new columns, all existing edges classify into one of the 10 authority_status values, proof_view contains only AUTHORITATIVE/AUTHORITATIVE_RUNTIME/AUTHORITATIVE_REGISTRY, all 4 deliverables generated |
| **W2 — Runtime hardening + SSOTDecisionRecord** | P2.1 runtime lift, P2.2 SSOT schema, P2.3 SSOT reconciler, P2.4 8-cell decision matrix, P2.5 tamper-evident signing, P2.6 SSOT/runtime tests | Wire `tools/generate/generate_runtime_adg.py` outputs as bucket=`runtime` with proper evidence_refs (run_id, trace_id, span_id). Add `SSOTDecisionRecord` cross-bucket reconciliation primitive — answers "did the thing exist (static), was it allowed (registry), did it happen (runtime), and was the result sealed?" via 8-cell decision matrix | ~30,000 | Runtime ADG SQLite already exists; SSOT primitive is new code | **Landed 2026-04-29** | Every runtime edge has run_id + trace_id; missing-trace edges classify as PARTIAL/UNKNOWN_NOT_PROOF; SSOT records include manifest_hash + replay_key + hmac_sig; 8 reconciler outcomes covered by tests |
| **W3 — Registry resolver** | P3.1 MCP config resolver, P3.2 agent specs resolver, P3.3 registry bucket lift CLI, P3.4 registry tests | Implement registry resolvers + lift utility that emit bucket=`registry` edges with registry_digest evidence | ~12,000 | `.windsurf/mcp_config.json` + `apps_*/config/agent_specs*.json` are the live source registries (route-contract / prompt-slot registries deferred) | **Landed 2026-04-29** | Every registry edge has registry_digest in evidence_refs; disabled MCP servers classified as RISK_SIGNAL_ONLY; idempotent lift on (src,dst,relation_type,source_file,authority='registry_declared'); 16 tests cover MCP+agent_specs resolvers + digest determinism |
| **W4 — Consumer audit (exemplar wave)** | P4.1 declaration spec, P4.2 5 exemplar consumer declarations, P4.3 mode-mismatch CI gate (advisory), P4.4 gate tests | Define `__adg_consumer_mode__` module attribute, apply to 5 exemplar CI gates (one per archetype: proof, risk×3, inventory×1), build `ops_scripts/ci/check_consumer_mode_declared.py` in advisory mode (CONSUMER_MODE_GATE_STRICT=1 toggles to blocking) | ~14,000 | Live scan finds 130 candidate consumers; 127 still missing declarations (deferred to per-team owners) | **Landed 2026-04-29 (advisory)** | Spec module + gate published; advisory CI run produces structured JSON report; 32 unit tests cover spec + gate + 8-cell mode-compatibility matrix |
| **W4-tail — Full consumer audit** | Apply declaration to remaining ~127 consumers | Per-owner declaration application | ~15,000 | Each consumer team owns its file's mode declaration | **Deferred** | All consumers declare; gate flips to strict (`CONSUMER_MODE_GATE_STRICT=1` becomes default) |
| **W5 — Certification gate** | P5.1 ADG_CERTIFIED check, P5.2 deterministic-digest test, P5.3 wire to CI | Implement ADG_CERTIFIED status + deterministic regeneration verification | ~12,000 | All previous waves landed | **Deferred** | ADG_CERTIFIED passes; same inputs → same digest; same authority counts |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| **P1.1** | Schema migration | `agentic_core/adg/artifact/ArtifactPaths.py` (CREATE TABLE edges + indexes), `agentic_core/adg/artifact/multi_writer.py` (mirror), `tools/generate/generate_full_adg.py` (final-stage backfill) | Existing `authority` column persists; need to add `bucket`, `resolution_status`, `authority_status`, `evidence_refs` (JSON) without breaking prior consumers | 4,000 | In progress |
| **P1.2** | Classifier expansion | `agentic_core/adg/artifact/edge_authority.py` (add 3 closed enums + mapping table + `is_proof()` / `is_risk()` / `is_inventory_only()` law functions + SQL backfill) | The existing `Authority` 6-enum maps mechanically to the new 10-value `AuthorityStatus`; need bidirectional mapping for back-compat | 5,000 | Pending |
| **P1.3** | Three views | Same files — DROP/CREATE `proof_view`, `risk_view`, `inventory_view`. Mark `mv_edges_verified` and `mv_edges_governance` as deprecated aliases (keep working, point to proof_view) | View definitions must be idempotent under repeated regeneration | 3,000 | Pending |
| **P1.4** | Backfill | SQL UPDATE script that maps existing `authority` → (bucket, resolution_status, authority_status). Runs in same place existing backfill runs | Three-column update on millions of rows; need single-pass UPDATE | 3,000 | Pending |
| **P1.5** | Tests | `tests/unit/agentic_core/adg/artifact/test_edge_authority.py` (extend existing); `tests/unit/agentic_core/adg/artifact/test_three_bucket_views.py` (new) — closed-enum invariants, mapping, view membership, law-function correctness | Test fixtures need to cover all 10 authority_status values + 3 buckets + edge kinds for STATIC bucket | 4,000 | Pending |
| **P1.6** | Deliverables | `docs/architecture/adr/ADG_THREE_BUCKET_AUTHORITY_MODEL.md`, `artifacts/adg/audit/ADG_THREE_BUCKET_AUTHORITY_AUDIT.json`, `docs/reports/adg/downstream_consumer_mode_matrix.md`, `artifacts/adg/audit/before_after_adg_authority_counts.json` | Audit JSON requires consumer scan (best-effort static grep for now); count comparison needs current + prior snapshot | 5,000 | Pending |

## Gap Register (deferred → tracked via DEFERRED_SCOPE markers)

| Gap | Bucket | Wave | Risk | Tracking |
|---|---|---|---|---|
| Runtime bucket schema/ingest | runtime | W2 | Cannot claim "this happened" without runtime evidence | DEFERRED_SCOPE marker emitted |
| Registry bucket resolvers | registry | W3 | Cannot claim "registry permission" without registry evidence | DEFERRED_SCOPE marker emitted |
| Consumer mode declarations | static+runtime+registry | W4 | Consumers may silently consume inventory as proof | DEFERRED_SCOPE marker emitted |
| ADG_CERTIFIED gate | meta | W5 | Until W5 lands, every snapshot status = ADG_NOT_CERTIFIED | Tracked in this plan + final response |
| TYPE_CHECKING import detection | static | W1.bis (within Phase 1 if time) | Falsely classifies type-only imports as production | Best-effort heuristic in W1; full detection W4 |
| Optional/try-except import detection | static | W1.bis | Falsely classifies optional imports as authoritative | Heuristic in W1 |
| Symbol-level resolution (PARTIAL status) | static | W2 | Module verifies but symbol may not exist; flag as PARTIAL not AUTHORITATIVE | W2 |
| evidence_refs JSON shape | all | W2 (runtime) / W3 (registry) | Static evidence_refs is empty in W1 (just source_file + line_no, not full ledger) | Documented |

## Architectural Decisions

### AD-1: Keep existing `authority` column for back-compat

The 2026-04-28 commit added `authority` (6-value enum). Removing it breaks already-built consumers. **Strategy**: keep `authority` as a *derived* column (computed from new triplet at backfill time), document it as deprecated, point new consumers to `authority_status`.

### AD-2: New columns are nullable initially, NOT NULL in W5

`bucket`, `resolution_status`, `authority_status` start as `TEXT DEFAULT NULL` in W1 (so backfill is non-blocking) and graduate to NOT NULL once ADG_CERTIFIED passes (W5).

### AD-3: `evidence_refs` is JSON TEXT

Per spec, evidence_refs is an array. SQLite has JSON1; we store as JSON text and consumers can `json_extract()`.

### AD-4: Views are idempotent (DROP+CREATE on every regen)

Same pattern as existing `mv_edges_verified`. Avoids stale-view bugs.

### AD-5: `mv_edges_verified`, `mv_edges_governance`, `mv_edges_unresolved` become aliases for `proof_view` / mixed / `risk_view`

Existing consumers continue to work without code change. Eventually retired in W4.

### AD-6: Mapping table from existing `authority` → new triplet

| Old `authority` | New `bucket` | New `resolution_status` | New `authority_status` |
|---|---|---|---|
| `verified` | `static` | `VERIFIED_MODULE` | `AUTHORITATIVE` |
| `unresolved` | `static` | `UNRESOLVED_MODULE` | `RISK_SIGNAL_ONLY` |
| `dynamic` | `static` | `UNRESOLVED_DYNAMIC` | `UNKNOWN_NOT_PROOF` |
| `external` | `static` | `NOT_APPLICABLE` | `EXTERNAL_ONLY` |
| `test_only` | `static` | `VERIFIED_MODULE` | `EXCLUDED_TEST_ONLY` |
| `runtime_observed` | `runtime` | `VERIFIED_RUNTIME` | `AUTHORITATIVE_RUNTIME` |

This mapping is mechanical; tests assert it.

## ADG_GRAPH_LAYER_EVIDENCE

This refactoring uses ADG primitives:

- **mv_edges_verified**: existing materialized view of all proof-grade edges; will be redefined as alias of `proof_view`
- **mv_edges_unresolved**: existing materialized view of broken-target edges; will be redefined as subset of `risk_view`
- **mv_edges_governance**: existing materialized view from prior 2026-04-28 commit; deprecated, kept as alias
- **edge_view**: top-level projection used by downstream consumers; gains `bucket` + `authority_status` columns

Semantic edges used: `imports`, `flows_to`, `emits_side_effect`, `resolves_callsite`, `controls_flow`, `reads_from`, `writes_to`. All retain authority annotation under new model.

P-views referenced: `v_p0_apps_direct_infra`, `v_p0_write_bypass_uwg`, `v_p1_mis_layered_infra`, `v_p1_zero_caller_infra`, `v_p2_duplicated_adapters`, `v_p3_isolated_experimental`. None are modified in W1; W4 will audit each as a proof_mode consumer.

## ADG_HOTSPOT_REPORT

| Rank | File | Layer | Fan-in | Archetype | Surface | Impact |
|---|---|---|---|---|---|---|
| 1 | `agentic_core/adg/artifact/edge_authority.py` | L_ADG | 3 (ArtifactPaths, multi_writer, generate_full_adg) | CENTRAL_DEPENDENCY | Observability Surface | Core classifier; bug here poisons every snapshot |
| 2 | `agentic_core/adg/artifact/ArtifactPaths.py` | L_ADG | ~15 | STATE_NODE | State Surface | Schema definition; consumed by every ADG writer/reader |
| 3 | `tools/generate/generate_full_adg.py` | L_TOOLS | ~5 | ORCHESTRATOR | Observability Surface | Final-stage backfill; misses here mean unclassified edges in shipped snapshots |

Layer multipliers: L_ADG ≈ 1.75 (state-criticality of canonical truth). All 3 hotspots cleared by Phase 1 by re-running the existing backfill mechanism with expanded SQL.

## Acceptance Criteria for Phase 1 (W1)

1. ✅ Schema accepts `bucket`, `resolution_status`, `authority_status`, `evidence_refs` columns on `edges`
2. ✅ Indexes on `bucket`, `authority_status` for proof_view performance
3. ✅ All existing edges in a fresh snapshot classify into one of the 10 authority_status values via deterministic mapping
4. ✅ `proof_view` contains only AUTHORITATIVE / AUTHORITATIVE_RUNTIME / AUTHORITATIVE_REGISTRY rows
5. ✅ `risk_view` contains RISK_SIGNAL_ONLY / UNKNOWN_NOT_PROOF / PARTIAL rows
6. ✅ `inventory_view` contains every edge regardless of authority
7. ✅ `is_proof()`, `is_risk()`, `is_inventory_only()` Python helper functions return correct booleans for all 10 authority_status values
8. ✅ Existing tests still pass (mapping back-compat preserved)
9. ✅ New unit tests pass (10 authority_status values × 3 views × invariants)
10. ✅ The 4 deliverable artifacts are produced
11. ✅ ADG_NOT_CERTIFIED status with explicit list of remaining work

## Limitations (W1 will explicitly NOT close these)

- Runtime bucket: empty in W1 unless an existing snapshot already has `runtime_observed` edges. No new runtime ingestion logic.
- Registry bucket: empty in W1. No registry resolvers implemented.
- TYPE_CHECKING / optional-import / PARTIAL detection: heuristic-only in W1; full implementation in later waves.
- Consumer audit: a STATIC GREP of consumer files is produced in `downstream_consumer_mode_matrix.md`, but consumers are NOT updated to declare modes (W4 work).
- Symbol-level PARTIAL: W1 does not check that `from X import Y` actually has `Y` defined in `X`; module-level resolution only.
- ADG_CERTIFIED: cannot pass until W4 + W5. W1 always reports ADG_NOT_CERTIFIED.

## References

- Constitutional §22 (ADG graph-layer primary for refactoring)
- Constitutional §23 (ADG canonical invariants)
- ADR `ADG_EDGE_AUTHORITY_AXIS.md` (the 2026-04-28 seed work)
- 2026-04-29 user directive (full text in mission section above)
