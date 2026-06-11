---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\rtc-w1-phase3-blockers-close-d7a2f1.md'
original_relative_path: 'rtc-w1-phase3-blockers-close-d7a2f1.md'
source_sha256: 34890ef0ce64ac6626eca2a49f74e8880ff58c0d9d500bb2e326c44686c52f8f
recovered_status: SURVIVED_IN_CURRENT
last_commit: '153652b9eb3'
last_commit_date: '2026-06-07 06:37:48 -0400'
created_date: '2026-04-30'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# RTC-REQ-055 W1 Phase 3 — Close Remaining Blockers (Honestly)

Status: Draft (authored 2026-04-30T22:21Z)
Plan SSOT: `.windsurf/plans/rtc-w1-phase3-blockers-close-d7a2f1.md`
Parent plan: `.windsurf/plans/runtime-cert-hardened-w0-7e3c9a.md` (W1 track)
Phase: W1 phase 3 (post-commit `61cfb3adbb`)
Tier classification: **T3** (new runtime code path, new CI gate, new artifacts, cross-layer evidence chain)

## Executive Summary

W1 phase 2 (commit `61cfb3adbb`) landed 6 honest evidence probes + composer + sidecar. RTC-REQ-055 final_acceptance_status = PARTIAL with 3 soft blockers:

1. `R1B_APPROVED_MODEL_PROOF = PARTIAL` (MISMATCH_EXPLAINED — identifier parity but `EMBEDDING_ENABLED=false`)
2. `R1B_PRODUCTION_THRESHOLD_PROOF = CALIBRATION_GAP` (no positive pairs measured)
3. `R1B_DENSE_SIMILARITY_COMPOSITION_PROOF = PARTIAL` (Rule 5 strict composition downgrade from #1 and #2)

W1 phase 3 closes blockers #1 and #2 operationally (where infrastructure allows) OR emits a proper BLOCKED with remediation plan (where it does not). Blocker #3 resolves automatically via Rule 5 when #1 and #2 flip to PASS.

**Honest-outcome target matrix**:

| Local env (BGE-M3 cached, deps OK) | CI env (BGE-M3 not cached) | Expected RTC-REQ-055 |
|---|---|---|
| MODEL=PASS, THRESH=PASS | MODEL=BLOCKED, THRESH=BLOCKED | local: ACCEPTED@E5 ; CI: PARTIAL |
| MODEL=PASS, THRESH=CALIBRATION_GAP | MODEL=BLOCKED, THRESH=BLOCKED | local: PARTIAL+CALIBRATION_GAP ; CI: PARTIAL |
| MODEL=BLOCKED (local deps missing) | MODEL=BLOCKED | both: PARTIAL+BLOCKED |

User Rule 1 (no silent threshold lowering), Rule 2 (no silent fallback PASS), Rule 4 (UWG-or-INFRASTRUCTURE_GAP), Rule 5 (strict composition) are ALL preserved. We never force green.

## Scope Boundaries (STRICT — user-confirmed 2026-04-30 18:21Z)

- ❌ W2 integrated runtime — UNTOUCHED
- ❌ W3 OTEL/replay — UNTOUCHED
- ❌ W4 final-certification language / Merkle — UNTOUCHED
- ❌ `SemanticCacheManager` behavior — UNTOUCHED (including thresholds)
- ❌ No silent threshold lowering — ENFORCED
- ❌ No ADR-backed threshold change in this phase — documented path only
- ✅ New probe: BGE-M3 live operational load (uses existing `bge_runtime.py` surface)
- ✅ New probe: threshold calibration with positive/negative pairs
- ✅ New dataset artifact: calibration pairs (≥20, 4 classes)
- ✅ Existing model + threshold probes extended to consume new evidence
- ✅ Composer extended to bind new evidence to subclaim verdicts

## Environment Reconnaissance (2026-04-30)

| Component | Local status | CI status (expected) |
|---|---|---|
| `FlagEmbedding` package | ✅ OK | Need `pip install FlagEmbedding` |
| `sentence_transformers` | ✅ OK | Need install |
| `torch` | ✅ OK | Need install |
| `transformers` | ✅ OK | Need install |
| `huggingface_hub` | ✅ OK | Need install |
| BGE-M3 model files | ✅ cached at `~/.cache/huggingface/hub/models--BAAI--bge-m3` | Absent (fresh runner) |
| `EMBEDDING_ENABLED` env | unset by default (fail-closed) | unset by default |
| `BGE_ALLOW_MODEL_DOWNLOAD` env | unset (fail-closed, local-files-only) | unset |
| `bge_runtime._get_model()` | functional (loads from cache with `local_files_only=True`) | would fail without cache |

**Architectural decision**: probe attempts **local-files-only** BGE-M3 load. If cache present → PASS. If cache absent → BLOCKED with remediation plan naming the download command. This is identical behavior whether running locally, in Docker, or in CI — the only difference is whether the cache is populated.

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---:|---|---|---|
| W1p3 | P1, P2, P3 | Close RTC-REQ-055 blockers #1 + #2 operationally | ~18000 | BGE-M3 works locally; CI emits BLOCKED; Rule 1/2/4/5 preserved | Draft | RTC-REQ-055 flips to ACCEPTED@E5 on local; honest PARTIAL on CI |

Single wave, 3 sequential phases.

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---:|---|
| P1 | BGE-M3 operational probe + calibration dataset | 2 new probes, 1 new dataset artifact, 2 new test files | Probe must load BGE-M3 without triggering download; dataset must cover 4 required classes | ~8000 | Todo |
| P2 | Threshold calibration probe + updated existing probes | 1 new probe, 2 edits to existing probes | Positive-pair cosine score at 0.95 may fail for paraphrases — honest CALIBRATION_GAP emission path required | ~6000 | Todo |
| P3 | Composer extension + CI wiring + tests + verify | Composer edit, workflow edit, 2 new test files | Composer must consume calibration results honestly; CI must attempt local-files-only load and emit BLOCKED when absent | ~4000 | Todo |

## Phase 1 — BGE-M3 Operational Probe + Calibration Dataset

**New files**:

1. `tools/certification/evidence/probe_bge_m3_operational.py`
   - Attempts `bge_runtime._get_model()` with `BGE_ALLOW_MODEL_DOWNLOAD=false` and `EMBEDDING_ENABLED=true` applied before import
   - On success: records model identifier, cached dimension (actual live embed of a known string), device, SentenceTransformer class, path provenance
   - On failure: records remediation plan — `huggingface-cli download BAAI/bge-m3 --local-dir <cache>` or `BGE_ALLOW_MODEL_DOWNLOAD=true python ...`
   - Output: `artifacts/certification/bge_m3_operational_proof.json`
   - Status ladder: `OPERATIONAL` / `CACHE_MISSING` / `DEPS_MISSING` / `LOAD_ERROR`

2. `data/certification/calibration_pairs.json` (the dataset artifact per user §C)
   - 24 pairs minimum, 4 classes:
     - 8× **paraphrase positives** (same meaning, different words — expected sim ≥ 0.95)
     - 6× **near-miss negatives** (topically similar but semantically different — expected sim < 0.95)
     - 6× **lexical-overlap different-meaning negatives** (share keywords, different intent — expected sim < 0.95)
     - 4× **reference** pairs cross-ref'd to NEG-5/6/7 (tenant-scope mismatch, expired freshness, missing model ref, unsafe reuse class — these don't test similarity but act as documentation anchors)
   - Schema: `{version, schema, pairs: [{id, class, text_a, text_b, expected_label, notes}]}`
   - Deterministic, repo-committed

3. `tests/runtime/test_bge_m3_operational.py` (8 tests)
   - Probe exits zero
   - Artifact schema valid
   - When cache present: status=OPERATIONAL, embedding_dimension_actual recorded, fallback_used=false
   - When cache absent (simulated via HF_HOME override): status=CACHE_MISSING, remediation_plan recorded, fallback_used not=true
   - Anti-cheat Rule 2: status=OPERATIONAL requires actual_model_matches_expected AND embedding_enabled AND no fallback

4. `tests/runtime/test_calibration_dataset.py` (6 tests)
   - Dataset file exists and is valid JSON
   - ≥20 total pairs (user "more than two happy examples" floor)
   - All 4 classes present with ≥4 pairs each
   - No duplicate ids, no empty texts
   - Paraphrase positives have distinct text_a != text_b
   - Dataset version field matches expected

**Success criteria**:
- Local run: `probe_bge_m3_operational.py` prints `status=OPERATIONAL dimension=1024 fallback_used=false`
- `data/certification/calibration_pairs.json` is valid + committed
- 14 new tests pass

## Phase 2 — Threshold Calibration Probe + Existing Probe Updates

**New file**:

5. `tools/certification/evidence/probe_threshold_calibration.py`
   - Reads `data/certification/calibration_pairs.json`
   - Calls `bge_runtime.bge_embed_batch` on all `text_a` + `text_b`
   - Computes cosine similarity for each pair
   - Compares each against production threshold (0.95 dynamic tier, read from SSOT — no override)
   - Records per-pair results (id, class, sim_score, passed_at_threshold, expected_label, agreement)
   - Computes aggregate: positive_pass_count / negative_miss_count / false_positive_count / false_negative_count
   - Emits PASS only if FP=0 AND FN=0 at production threshold
   - Emits CALIBRATION_GAP otherwise with ADR remediation path documented (no ADR created)
   - Output: `artifacts/certification/semantic_cache_calibration_results.json`
   - Also updates/overwrites `artifacts/certification/semantic_cache_threshold_proof.json` subsection: consumer-level flag `calibration_evidence_present=true`

**Edits to existing probes**:

6. `tools/certification/evidence/probe_semantic_cache_model.py` — extend
   - When `EMBEDDING_ENABLED=true` AND `bge_runtime` importable: call `bge_embed_query("test")`, measure dimension, upgrade MATCH → full PASS
   - Record `embedding_dimension_actual`, `fallback_used=false`, `live_embed_test_passed=true`
   - Add env var `BGE_ALLOW_MODEL_DOWNLOAD` recording (probe does NOT set it)

7. `tools/certification/evidence/probe_semantic_cache_threshold.py` — extend
   - If `semantic_cache_calibration_results.json` exists AND overall_status=PASS: threshold_subclaim_status=PASS with calibration reference
   - If calibration results present but PASS criteria not met: CALIBRATION_GAP with full per-pair drill-down
   - If calibration results absent: CALIBRATION_GAP with "no measurement yet" (current behavior preserved)

**New tests**:

8. `tests/runtime/test_threshold_calibration.py` (12 tests)
   - Calibration probe runs successfully when BGE-M3 operational
   - Produces per-pair results with required fields
   - Production threshold read from SSOT (no override)
   - Agreement check: paraphrase positives should mostly score ≥0.95
   - Agreement check: near-miss + lexical-overlap negatives should mostly score <0.95
   - If BGE-M3 not operational: probe emits `INFRASTRUCTURE_GAP` (not silent PASS)
   - If calibration fails: emits CALIBRATION_GAP (not threshold lowering)
   - ADR-path-required test: changing threshold without `semantic_cache_threshold_adr.json` is BLOCKED
   - Anti-cheat: no `SEMANTIC_CACHE_THRESHOLD_DYNAMIC` override tolerated — probe records override-present and fails

**Success criteria**:
- Local run: `probe_threshold_calibration.py` emits either PASS (if all pairs agree) or CALIBRATION_GAP with per-pair breakdown
- Extended model probe: `model_match_status=MATCH` with live dimension measurement
- Extended threshold probe: reads calibration results when present
- 12 new tests pass

## Phase 3 — Composer + CI Wiring + Full Verification

**Edits**:

9. `scripts/compose_semantic_cache_subclaims.py` — extend
   - Consume new evidence artifacts: `bge_m3_operational_proof.json` + `semantic_cache_calibration_results.json`
   - `R1B_APPROVED_MODEL_PROOF = PASS` only when model probe `model_match_status=MATCH` AND bge_m3_operational `status=OPERATIONAL` AND `fallback_used=false`
   - `R1B_PRODUCTION_THRESHOLD_PROOF = PASS` only when calibration results `overall_status=PASS` (positives pass + negatives miss + FP=FN=0)
   - `R1B_DENSE_SIMILARITY_COMPOSITION_PROOF = PASS` per Rule 5 when both above PASS AND negatives PASS

10. `.github/workflows/runtime-certification.yml` — extend
    - Add step `W1.2g probe_bge_m3_operational` before threshold probe
    - Add step `W1.2h probe_threshold_calibration` after BGE-M3 operational probe
    - Both marked `continue-on-error: true` because CI runners don't have BGE-M3 cached — honest BLOCKED is expected CI outcome
    - When W1.1 advisory flips to PASS locally, remove `continue-on-error` from W1.1 (future W1 phase 4)

11. Full verification chain:
    - All 9 probes run
    - Composer re-runs
    - Verifier advisory + strict
    - All W0 + W0 closure + W1p1 + W1p2 + W1p3 tests pass (target: 190+ tests)
    - `acceptance_legality_report.json` shows RTC-REQ-055 at expected state (ACCEPTED if local with all PASS, else honest PARTIAL)

12. Commit + push with scope-hygiene check (26→38 files expected).

**Success criteria**:
- Composer maps 9 subclaims with correct dependency chain
- Local end-to-end: RTC-REQ-055 = ACCEPTED@E5 OR honest PARTIAL (not forced green)
- CI end-to-end: RTC-REQ-055 = honest PARTIAL with BLOCKED model + threshold (no silent PASS)
- No hitchhiker files in commit

## Gap Register

| Gap ID | Description | Severity | Owner phase |
|---|---|:---:|:---:|
| W1p3-G1 | BGE-M3 fails to load locally (unexpected) | Medium | P1 — emit BLOCKED, do not proceed |
| W1p3-G2 | Paraphrase positives fail at 0.95 threshold (known BGE-M3 behavior for some surface forms) | Low | P2 — emit CALIBRATION_GAP, do not lower threshold |
| W1p3-G3 | CI runners without cache — expected | N/A | P3 — `continue-on-error: true` on the 2 new probe steps |
| W1p3-G4 | Calibration dataset quality — 24 pairs may still miss edge cases | Low | Accepted. Can be expanded in follow-up phase if needed. |

## ADG Graph Layer Evidence (constitutional §22)

Per constitutional §22, T2/T3 plans cite materialized views + semantic edges.

**Materialized views consulted** (read-only, for context):
- `mv_hotspot_centrality` — semantic-cache-related nodes
- `mv_graph_chokepoint_bridges` — identify if embedding_factory is a chokepoint (it is: L2 embeddings hub)
- `mv_debt_concentration_hotspots` — semantic cache / embedding modules

**Semantic edges used conceptually**:
- `imports` — probe modules import `bge_runtime` (safe — L2 embeddings layer)
- `reads_from` — probes read SSOT modules (no write edges)
- No `writes_to` / `emits_side_effect` edges introduced (additive + read-only by design)

**P-view cross-reference**:
- `v_p0_apps_direct_infra` — NOT applicable (probes live in `tools/certification/`, a tools-layer)
- `v_p0_write_bypass_uwg` — NOT applicable (probes do not write)
- `v_p2_duplicated_adapters` — calibration probe does NOT duplicate SemanticCacheManager logic (it wraps `bge_runtime` directly per user's "do not touch SemanticCacheManager")

**Layer gravity**: all new code lives in `tools/certification/` (layer L_TOOLS) + `scripts/` + `tests/runtime/`. No cross-layer violations. Imports from `agentic_core.embeddings.bge_runtime` (L2) are read-only and conform to gravity.

## ADG Hotspot Report (constitutional §23)

| File | Layer | Fan-in | Violations | Impact | Archetype | Surface |
|---|---|---:|---:|---:|---|---|
| `tools/certification/evidence/__init__.py` | L_TOOLS | 6 (probes) | 0 | 0 | CENTRAL_DEPENDENCY | Observability |
| `scripts/compose_semantic_cache_subclaims.py` | L_SCRIPTS | 0 | 0 | 0 | ORCHESTRATOR | State (sidecar) |

No refactoring hotspots introduced. W1p3 is purely additive evidence emission — the impact formula
`impact = violation_count × (1 + log10(1 + fan_in)) × layer_multiplier` evaluates to 0 (no new violations).

## Risk Matrix

| Risk | Likelihood | Impact | Mitigation |
|---|:---:|:---:|---|
| Probe load triggers accidental download | Low | Medium | `BGE_ALLOW_MODEL_DOWNLOAD=false` pinned by default; probe only reads `os.environ`, never sets it |
| Positive pairs fail at 0.95 threshold | Medium | Low | Honest CALIBRATION_GAP emission, not silent threshold change. Rule 1 preserved. |
| CI flakiness from BGE-M3 load timing | Medium | Low | `continue-on-error: true` on new CI steps until cache is wired |
| Test suite runtime grows | Medium | Low | BGE-M3 load is ~5s per test module; skip-on-missing-cache test marker shields CI |
| Artifact bloat from committing results | Low | Low | Each artifact <100KB; calibration dataset fixed-content |

## Sign-off Criteria (honest)

Before claiming W1 phase 3 complete, ALL of these must be true:

1. All 9 probes exit zero (including new bge_m3_operational + threshold_calibration)
2. Composer produces sidecar with updated verdicts
3. Full test suite passes locally (190+ tests)
4. On local: `verify_semantic_cache_certification.py --strict` exit = 0 OR honest explanation why not (e.g., calibration gap)
5. On local: `verify_runtime_certification_acceptance.py` exit = 0 with RTC-REQ-055 at ACCEPTED or legal PARTIAL
6. Commit scope-hygiene: `git diff --cached --name-only | grep -v <expected pattern>` = empty
7. No changes to W2/W3/W4 scope flags in sidecar (all three remain `*_claimed=False`)

## Non-goals (explicit)

- NOT producing an ADR-backed threshold recalibration in this phase (user's "ADR/calibration study is a future phase unless explicitly approved")
- NOT wiring BGE-M3 cache into CI (separate infra concern; CI BLOCKED is accepted)
- NOT touching SemanticCacheManager (even for config binding)
- NOT claiming integrated-runtime / OTEL / replay evidence

---

**Plan ready for execution.** Single-threaded execution P1 → P2 → P3. No decision gates expected unless BGE-M3 fails to load locally (then W1p3-G1 triggers, plan pauses, INFRASTRUCTURE_GAP emitted).
