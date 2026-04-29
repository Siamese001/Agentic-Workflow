# Three-Bucket ADG Gap Remediation

Status: **Active — W1 complete, W2-W8 pending**
Created: 2026-04-29
Owner: Cascade
Plan slug: `three-bucket-gap-remediation-069806`
Predecessor: `.windsurf/plans/three-bucket-otel-view-5db409.md` (W1–W8 complete)
Related deferred scope:
- `[P2] W9 W9.1` — GenAI SIG semconv migration across 20 OTel emit sites
- `[P3] W11 W11.1` — Prompt-slot registry resolver pending canonical declarative manifest
- `[P5] W10 W10.1` — Schema graduation to column-level NOT NULL after 4-week green window

## Mission

Close the producer gaps identified in the post-W8 three-bucket health audit so
that the ADG snapshot pipeline produces real data into all three buckets
(🟦 Static, 🟪 Registry, 🟧 Runtime), validators run in strict mode, and the
triplet-attested fraction (`ADG_CERTIFIED` health score) trends from today's
**0%** toward a sustainable ≥60% within 4 weeks.

## Doctrinal source

- `docs/architecture/adr/ADR-074-runtime-bucket-as-otel-view.md`
- `docs/reports/adg/THREE_BUCKET_GAP_REPORT.json` (current state — 100% UNOBSERVED_CODE)
- Constitutional §22 (graph-layer primary driver)
- Constitutional §28 (SQLite-direct fallback supersedes grep)

## Audit findings being remediated

Per the bucket-coverage table (chat 2026-04-29 13:50 UTC):

| Bucket | Gap | Remediation wave |
|--------|-----|------------------|
| 🟪 Registry | Resolvers exist + tested but pipeline never calls them → **0 registry edges in any snapshot** | **W1** |
| 🟧 Runtime | `build_runtime_view` wired but `runtime_adg_store` empty → 0 attested rows | **W2** (synthetic traces), **W3** (real emitters) |
| 🟧 Runtime | GenAI semconv helper shipped but 20 emit sites at 0% adoption | **W3** (= deferred W9) |
| ⬛ Cross | 3 ADG gates run advisory; cannot fail-closed yet | **W4** (after W1–W3 land) |
| ⬛ Cross | `three_bucket_gap_report.py` operational but not enforced in CI | **W5** |
| ⬛ Cross | No cryptographic provenance (in-toto / Sigstore) on the artifact | **W6** |
| ⬛ Cross | `bucket`/`resolution_status`/`authority_status` columns NULLABLE | **W7** (= deferred W10) |
| ⬛ Cross | Verification + audit JSON refresh + ADG_CERTIFIED green in strict mode | **W8** |

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| **W1 — Wire registry resolvers** | P1.1 stage call, P1.2 edge persistence, P1.3 tests, P1.4 verify | Add `resolve_all_registries()` invocation into `generate_full_adg.py` final-stage block; persist returned edges into `edges` with `bucket='registry'`, `authority_status='AUTHORITATIVE_REGISTRY'`; add round-trip test | ~6,000 | `resolve_all_registries()` returns the documented shape (route_contract + agent_spec + mcp_config edges); `edges` schema accepts `bucket='registry'` (already does, per W7 schema) | **Done 2026-04-29** | ✅ Live snapshot now has 33 registry edges; gap report shows CONFIG_BLOAT=33; 12/12 new tests + 23/23 existing resolver tests green |
| **W2 — Synthetic OTel traces** | P2.1 pytest OTel exporter fixture, P2.2 `runtime_adg_store` seeder, P2.3 regen + verify | Build a pytest plugin / conftest that exports OTel spans into `runtime_adg_store` during a designated test run (`pytest -m runtime_observability`); regenerate ADG against the seeded store to validate the W1 runtime view path produces non-empty `v_runtime_proof` | ~10,000 | `runtime_adg_store` exposes a writable interface (or has a seed helper); pytest's OTel plugin (`pytest-opentelemetry`) is acceptable | Pending | After test run + regen: `v_runtime_proof.attesting_trace_count >= 1` for at least 50 distinct (src,dst,relation) tuples; gap report classes DEAD_PATH and TRIPLET_ATTESTED both populated |
| **W3 — GenAI emitter migration** | P3.1 inventory 20 sites, P3.2 migrate top-10 by call density, P3.3 migrate remaining 10, P3.4 advisory→threshold flip preview | Replace ad-hoc OTel span emission across the 20 detected sites with imports from `agentic_core.L6_observability.semconv.gen_ai`; closes the W9 deferred-scope item | ~14,000 | `gen_ai.py` helper API stable (it is — 27/27 tests pass); migration is mechanical (helper exposes attribute keys + span builders) | Pending | `check_otel_genai_semconv_coverage` reports ≥80% emitter alignment; coverage gate ready to flip strict |
| **W4 — Strict-mode flip** | P4.1 set `CONSUMER_MODE_GATE_STRICT=1` default, P4.2 set `RUNTIME_PROOF_STRICT=1` default, P4.3 set `OTEL_SEMCONV_STRICT=1` default, P4.4 ADG_CERTIFIED strict run | Flip the three currently-advisory gates to fail-closed defaults; update `run_contract_gates.py` and `check_adg_certified.py` env-var wiring; document the rollback knob | ~3,000 | W1, W2, W3 all green so strict mode does not regress | Pending | `python ops_scripts/ci/check_adg_certified.py` exits 0 in strict mode against current snapshot; CI surfaces strict-mode failure on any regression |
| **W5 — Gap report CI gate** | P5.1 fail-criteria spec, P5.2 `check_three_bucket_gap.py`, P5.3 wire into `run_contract_gates`, P5.4 tests | Promote `three_bucket_gap_report.py` from informational to enforcing: new gate `check_three_bucket_gap.py` fails on `SHADOW_CHANNEL > 0` (P1) or `health_score < threshold` (configurable; advisory at 60%, strict at 80%) | ~5,000 | Gap report JSON output stable (it is — just shipped); thresholds reasonable post-W3 | Pending | Gate operational; produces clear violation rows; passes against current state once W1+W2+W3 land |
| **W6 — in-toto signing** | P6.1 ADR for signing strategy, P6.2 Sigstore/Cosign integration choice, P6.3 implement Tier-1 signing stage, P6.4 verification gate, P6.5 tests | Add cryptographic signing of the ADG artifact manifest (extends the W7 deterministic-digest stage); produces an in-toto attestation alongside the snapshot for downstream supply-chain verification | ~12,000 | Sigstore CLI available in dev/CI environments; OIDC identity available for keyless signing; team comfortable with Sigstore (else fall back to long-lived key managed via existing secrets process) | Pending | New ADR posted; `artifacts/adg/adg_indexed_<ts>.intoto.jsonl` produced every regen; verification gate passes against valid signature, fails on tamper |
| **W7 — Schema graduation** | P7.1 SQL migration script, P7.2 backfill verification, P7.3 ALTER TABLE on `bucket`/`resolution_status`/`authority_status` columns, P7.4 runtime-assertion removal in `ArtifactPaths.py` block 7 | After 4-week green window of W1–W5, flip the 3 NULLABLE columns to NOT NULL; remove the runtime assertion (now redundant); closes the W10 deferred-scope item | ~4,000 | Green window held (no regressions in `check_adg_certified` for ≥4 weeks); zero NULL rows present | Pending | Migration applied; ALTER TABLE succeeds against fresh and existing snapshots; `check_adg_certified` strict run still green |
| **W8 — Verify + close-out** | P8.1 full regen, P8.2 gap report run, P8.3 audit JSON refresh, P8.4 plan close-out + Notion writeback | Full regen against W1+W2+W3+W4+W5+W6 stack; produce final gap report and audit JSON; mark plan complete; commit + push | ~3,000 | All previous waves landed | Pending | `THREE_BUCKET_GAP_REPORT.json` shows triplet_attested_pct ≥ 60%; SHADOW_CHANNEL = 0; ADG_CERTIFIED green in strict mode |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| **P1.1** | Pipeline stage call | `tools/generate/generate_full_adg.py` (~30 lines inserted after r6 enrichment, before final edge-authority backfill) | Insertion site picked to mirror A6/A12/r6 supplementary-scanner pattern | 2,000 | **Done** |
| **P1.2** | Edge persistence | `tools/adg/registry_bucket_lift.py` `_ensure_static_node()` updated to satisfy 5 NOT NULL columns on `nodes` (entity_type/layer/identity_kind/confidence/resolved_path) | Schema drift — original lift predated NOT NULL columns; caught by live regen | 2,500 | **Done** |
| **P1.3** | Round-trip test | `tests/unit/tools/adg/test_registry_bucket_lift.py` (12 tests; canonical NOT NULL fixture mirrors prod schema) | Synthetic fixture must match prod schema or false greens hide schema drift | 1,000 | **Done** |
| **P1.4** | Verify | Live lift against `adg_indexed_04292026_1513.sqlite` → 33 edges inserted, 36 nodes stubbed; gap report confirms CONFIG_BLOAT=33 | — | 500 | **Done** |
| **P2.1** | OTel pytest fixture | `tests/conftest.py` (add `pytest_opentelemetry` exporter wiring under `--otel-export` flag) | OTel exporter coexistence with existing logging | 4,000 | Pending |
| **P2.2** | Trace seeder | `tests/fixtures/runtime_adg_seeder.py` (new) | Seeder needs to write to `runtime_adg_store` API (or its underlying SQLite if writer interface absent) | 4,000 | Pending |
| **P2.3** | Regen + verify | run `pytest -m runtime_observability` then `python tools/generate/generate_full_adg.py` | Test isolation — seeded traces must not leak into prod traces | 2,000 | Pending |
| **P3.1** | Inventory 20 sites | `python ops_scripts/ci/check_otel_genai_semconv_coverage.py --list-emitters` | Some emitters are conditional / behind feature flags | 2,000 | Pending |
| **P3.2** | Migrate top-10 | top 10 emit sites by call density (use `otel_spans_by_agent` to rank) | Span-emission shape diversity — may need helper extensions | 6,000 | Pending |
| **P3.3** | Migrate remaining 10 | bottom 10 emit sites | Mechanical | 5,000 | Pending |
| **P3.4** | Threshold flip preview | `python ops_scripts/ci/check_otel_genai_semconv_coverage.py` advisory run | Validate ≥80% before W4 | 1,000 | Pending |
| **P4.1** | Consumer-mode strict | `ops_scripts/ci/check_consumer_mode_declared.py` (default env), `run_contract_gates.py` | None — gate is solid | 750 | Pending |
| **P4.2** | Runtime-proof strict | `ops_scripts/ci/check_runtime_proof_view_well_formed.py`, `run_contract_gates.py` | Depends on W2 | 750 | Pending |
| **P4.3** | OTel-semconv strict | `ops_scripts/ci/check_otel_genai_semconv_coverage.py`, `run_contract_gates.py` | Depends on W3 ≥80% | 750 | Pending |
| **P4.4** | ADG_CERTIFIED strict | `ops_scripts/ci/check_adg_certified.py` (env propagation) | All sub-gates must already be strict-clean | 750 | Pending |
| **P5.1** | Fail-criteria spec | comments + ADR addendum | Threshold debate — start advisory at health<60%, strict at <80% | 1,000 | Pending |
| **P5.2** | Gate script | `ops_scripts/ci/check_three_bucket_gap.py` (new) | Reads `THREE_BUCKET_GAP_REPORT.json`; no MCP dependency | 2,000 | Pending |
| **P5.3** | Wire into runner | `ops_scripts/ci/run_contract_gates.py` | — | 1,000 | Pending |
| **P5.4** | Tests | `tests/unit/ops_scripts/ci/test_check_three_bucket_gap.py` (new) | Synthetic gap-report fixtures | 1,000 | Pending |
| **P6.1** | Signing ADR | `docs/architecture/adr/ADR-NNN-adg-artifact-attestation.md` (new) | Sigstore vs long-lived-key choice — surface as Author-Gate decision | 3,000 | Pending |
| **P6.2** | Tooling choice | (decision artifact only) | OIDC availability for keyless signing | 500 | Pending |
| **P6.3** | Tier-1 signing stage | `tools/generate/generate_full_adg.py` (new stage after digest) + `tools/sign/intoto_signer.py` (new) | Sigstore CLI invocation; offline mode handling | 5,000 | Pending |
| **P6.4** | Verification gate | `ops_scripts/ci/check_adg_artifact_signature.py` (new) | Tamper detection via digest mismatch | 2,000 | Pending |
| **P6.5** | Tests | `tests/unit/tools/sign/test_intoto_signer.py` (new) | Signing tests need test keys / mocked Sigstore | 1,500 | Pending |
| **P7.1** | Migration script | `tools/migrations/2026_05_NN_adg_schema_graduation.py` (new) | Idempotent migration — must handle existing snapshots | 1,500 | Pending |
| **P7.2** | Backfill verification | `python tools/migrations/...` --dry-run on snapshot | Zero NULLs precondition | 1,000 | Pending |
| **P7.3** | ALTER TABLE | migration apply | SQLite ALTER limitations — may need rebuild | 1,000 | Pending |
| **P7.4** | Remove runtime assertion | `agentic_core/adg/artifact/ArtifactPaths.py` (block 7) | Now redundant with column-level NOT NULL | 500 | Pending |
| **P8.1** | Full regen | `python tools/generate/generate_full_adg.py` | — | 1,000 | Pending |
| **P8.2** | Gap report run | `python tools/adg/three_bucket_gap_report.py --top-n 20` | Verify triplet_attested ≥ 60% | 500 | Pending |
| **P8.3** | Audit JSON refresh | `docs/reports/adg/ADG_THREE_BUCKET_AUTHORITY_AUDIT.json` | — | 1,000 | Pending |
| **P8.4** | Plan close-out + Notion | this file + Wave/Phase Convergence row updates | — | 500 | Pending |

## ADG_HOTSPOT_REPORT

The work in this plan adds new edges/stages rather than refactoring existing
hotspots; the relevant hotspot consideration is the impact-blast-radius of
modifying `generate_full_adg.py` itself. Per `mv_hotspot_centrality` and
`mv_dependency_cone_risk` against the current snapshot:

| File | Archetype | Surface | Layer | Fan-in | Layer mult | Impact | Wave |
|------|-----------|---------|-------|-------:|-----------:|-------:|------|
| `tools/generate/generate_full_adg.py` | ORCHESTRATOR | Execution + State | L4 | 23 | ×1.75 | high | W1, W6 |
| `agentic_core/adg/registry/registry_resolvers.py` | CENTRAL_DEPENDENCY | State (registry) | L0 | 7 | ×2.0 | medium | W1 |
| `agentic_core/L6_observability/semconv/gen_ai.py` | CENTRAL_DEPENDENCY (post-W3) | Observability | L6 | 0 → 20 (post-W3) | ×0.75 | low (today) | W3 |
| `ops_scripts/ci/check_adg_certified.py` | SAFETY_GATEKEEPER | Security | L_OPS | 5 | ×2.0 | medium | W4 |
| `agentic_core/adg/artifact/ArtifactPaths.py` | CENTRAL_DEPENDENCY | State | L4 | 31 | ×1.75 | high | W7 |

Risk treatment: `generate_full_adg.py` and `ArtifactPaths.py` are high-fan-in
ORCHESTRATORS — every change MUST land behind a fail-soft `_pipeline_stage`
context manager (already the pipeline's idiom) so a wave-level regression
cannot break snapshot production for unrelated work.

## ADG_GRAPH_LAYER_EVIDENCE

Materialized views consulted for plan ranking and wave ordering:

1. **`mv_hotspot_centrality`** — confirmed `generate_full_adg.py` and
   `ArtifactPaths.py` as the two CENTRAL_DEPENDENCY anchors that every wave
   modifies; informs the fail-soft requirement above.
2. **`mv_graph_critical_path_blast_radius`** — confirmed that adding a new
   stage to `generate_full_adg.py` (W1, W6) intersects the **Execution + State**
   ADG surfaces; both waves must use the existing `_pipeline_stage` idiom to
   stay fail-soft.
3. **`mv_runtime_spine_gaps`** — current snapshot shows the runtime spine
   has zero attested edges (consistent with the audit). W2 + W3 directly fill
   this gap; W4 strict mode then enforces it.

Semantic edges relied on:

- `flows_to` — used to identify the data path from `runtime_adg_store` →
  `build_runtime_view` → `v_runtime_proof` (W2 verification surface).
- `controls_flow` — used to identify the gate-runner relationship in
  `run_contract_gates.py` → individual gates (W4, W5 wiring sites).
- `emits_side_effect` — flags the new SQLite writes added in W1 (registry
  edge persistence) and W6 (in-toto signing) — both must respect the UWG
  commit pattern already used by the pipeline.

P-views cross-referenced:

- `v_p0_apps_direct_infra` — confirms no apps_eval / apps_orchestration files
  are touched by this plan (correct — work is L4 / L0 / L6 / L_OPS).
- `v_p1_zero_caller_infra` — confirms `registry_resolvers.py` shows up as a
  zero-caller node today (consistent with the gap — W1 fixes this).
- `v_p3_isolated_experimental` — confirms the W3 helper module is currently
  isolated (zero importers); W3 changes that.

## Sequencing dependencies

```
W1 (registry) ──┬──> W4 (strict-flip)
                │
W2 (traces) ────┼──> W4
                │
W3 (emitters) ──┘──> W4 ──> W5 (gap-report CI gate)
                                     │
                                     └──> W7 (schema graduation, after 4-week green window)
W6 (in-toto) ─── independent of W1–W5; can land in parallel after W4 strict pass
W8 (verify) ── consumes all of the above
```

W1, W2, W3 can run **in parallel** — they touch disjoint files and have no
cross-dependencies. W6 is independent of the bucket work and can be
prioritized separately (in-toto adds supply-chain provenance regardless of
bucket fill state).

## Out of scope (explicit non-goals)

- Re-architecting `runtime_adg_store` itself (W1 OTEL view pivot already
  treats it as the SSOT — that decision stands per ADR-074).
- Full prompt-slot registry resolver — covered separately by deferred-scope
  W11 (`[P3]` priority); blocked on a canonical declarative slot manifest
  that does not yet exist. **NOT** part of this plan.
- Migration of static-bucket producers (AST scan) — already operational at
  100% on this bucket.

## Definition of Done

This plan is complete when:

1. `python tools/adg/three_bucket_gap_report.py` reports
   `health_score_pct_triplet_attested ≥ 60` and `SHADOW_CHANNEL = 0`.
2. `python ops_scripts/ci/check_adg_certified.py` exits 0 in strict mode
   (`CONSUMER_MODE_GATE_STRICT=1 RUNTIME_PROOF_STRICT=1 OTEL_SEMCONV_STRICT=1`).
3. Every snapshot produces an in-toto attestation alongside it; tamper
   detection verified by red-team test.
4. Schema columns `bucket`, `resolution_status`, `authority_status` are
   `NOT NULL` at the column level (W7 graduation).
5. `docs/reports/adg/ADG_THREE_BUCKET_AUTHORITY_AUDIT.json` and
   `docs/reports/adg/before_after_adg_authority_counts.json` reflect the
   post-remediation state.
6. ADR-NNN (W6 in-toto signing) merged.
7. All waves marked **Done** in this plan; Notion Wave/Phase Convergence
   rows updated.
