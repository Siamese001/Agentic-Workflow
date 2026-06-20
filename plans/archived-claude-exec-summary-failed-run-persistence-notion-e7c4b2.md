---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\exec-summary-failed-run-persistence-notion-e7c4b2.md'
original_relative_path: 'exec-summary-failed-run-persistence-notion-e7c4b2.md'
source_sha256: da6c82e2ccd3194778fa33416ef613067452027e9aba9c18997772b580e05d35
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: exec-summary-failed-run-persistence-notion-e7c4b2
plan_type: product
touches_agentic_core: false
touches_governance_ci: false
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
---

# Apps_* — Failed X1D Judge-Regen Candidate Persistence + Notion Review

> **Slug note:** Plan file id `exec-summary-failed-run-persistence-notion-e7c4b2` is historical (Notion row registered). **Scope is all `apps_*` lanes** that run X1D judge-directed regen, not executive summary only.

**North star:** Any `apps_*` section run that fails judges or exhausts judge regen leaves a **receipt-bound, replayable candidate pool** on disk and a **Notion review index** (metadata + links only) — without implying L4/UWG promotion. L6 may read pool summaries; operators never lose scratch vs regen vs rejected identity.

**Plan status:** **NEEDS HARDENING → HARDENED** (2026-05-26). Safe to execute after this revision; not a plan-defect — execution must implement receipt contract below.

**Motivation (2026-05-26):** Brown floor-matrix `exec_summary_20260526_070105` (floor 4.2): judge regen accepted while Claude **4.0→3.6**; scratch only in `provider_request_regen.json` assistant turn; published text = regen draft. Applies to **any** apps-owned lane with judge regen.

**Sibling (implement together — strict boundaries):**

- [exec-summary-judge-regen-control-loop-f8a3c2.md](exec-summary-judge-regen-control-loop-f8a3c2.md) — **sole authority** for best-of publish selection; G3 monotonicity
- This plan — **persistence mirror + receipt-bound pool + index + Notion review** (W0–W7). **Does not** implement or fork publish logic.

> **plan_id discipline:** `exec-summary-failed-run-persistence-notion-e7c4b2`

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: TODO
PLAN_HARDENING: APPLIED_2026-05-26
CURRENT_WAVE: W1
LAST_COMPLETED_WAVE: W0
LAST_UPDATED: 2026-05-26

NOTION_PAGE_ID: 36c27693-f55c-81d8-8cba-d0181e262ba2
NOTION_PLAN_URL: https://www.notion.so/exec-summary-failed-run-persistence-notion-e7c4b2-36c27693f55c81d88cbad0181e262ba2
PLAN_CREATED: slug=exec-summary-failed-run-persistence-notion-e7c4b2 path=.cursor/plans/exec-summary-failed-run-persistence-notion-e7c4b2.md status=Not Started notion_page=36c27693-f55c-81d8-8cba-d0181e262ba2

---

## Pre-Execution Hardening Gate (MUST — incorporated below)

| # | Hardening | Where in plan |
|---|-----------|----------------|
| 1 | Receipt-bound pool (refs + hashes + contract_type) | § Pool manifest + § Candidate record |
| 2 | LIVE_RUNTIME vs BACKFILL proof_class separation | § Pool origin |
| 3 | Exact candidate lineage (scratch/regen/rejected/published) | § Candidate record |
| 4 | X3/UWG negative contract test | § DoD D10 + W1.3 |
| 5 | Notion not SSOT | § Notion boundaries |
| 6 | Atomic writer | § Writer discipline |
| 7 | W3 defers publish to f8a3c2 | § W3 boundary |
| 8 | Exact closeout commands | § Closeout commands |
| 9 | `candidate_pool_summary.json` for L6 | § Optional W4.2 |
| 10 | PII-safe Notion preview | § Notion boundaries |
| 11 | Lane adapter fail-closed | § Adapter discipline |
| 12 | W6 historical classification | § W6 backfill |

---

## Scope — all `apps_*` with X1D judge regen

### In scope

| Trigger | Meaning |
|---------|---------|
| Lane emits `judge_remediation_cycles.json` (or successor) | Judge-directed regen ran |
| `x3_code` is `X3_REVIEW*` or judge soft-fail on exit | Failed / review disposition |
| `regen_outcome` / cycle `reject_gate` | Regen did not clear floor |

### Lane registry (inventory — W7)

| `section_id` | App tree | Judge regen today | `display_field_key` | Artifact root |
|--------------|----------|-------------------|---------------------|---------------|
| `executive_summary` | `apps_rg` | **Yes** | `resume_display_text` | `artifacts/apps_rg/runtime_proofs/executive_summary/{real\|mock}/<run_id>/` |
| `unify_narrative` | `apps_rg` | No | `resume_display_text` | `.../unify_narrative/...` |
| `headline` | `apps_rg` | No | `headline_text` | `.../headline/...` |
| **Future `apps_*`** | per app | When regen ships | lane manifest | `artifacts/<app>/runtime_proofs/<lane>/...` |

**Reference implementation:** `executive_summary` (W2).

---

## Product Contract (one sentence)

> **Every apps_* lane that runs X1D judge regen emits a receipt-bound candidate pool (provenance + hashes + lineage); REVIEW runs are indexed for Notion triage only; publish selection remains f8a3c2 lane authority.**

---

## Architecture Invariants

| ID | Invariant |
|----|-----------|
| INV-1 | `candidate_pool/` append-only within a run; atomic writes (§ Writer) |
| INV-2 | `X3_REVIEW` → **no UWG commit** — executable guard in contract test |
| INV-3 | L6 reads refs/summary only; no mutation of X3 or L4 |
| INV-4 | Pool records **all** candidate types including rejected/regressed |
| INV-5 | **Notion ≠ SSOT** — metadata, previews, links only |
| INV-6 | Backfill: `proof_class=FILESYSTEM_BACKFILL_RECONSTRUCTION` — not live-hook proof |
| INV-7 | Section-agnostic schema with `display_field_key` |
| INV-8 | No `agentic_core` edits |
| INV-9 | **No parallel publish selector** — mirror f8a3c2 `publish_decision` only |
| INV-10 | Candidate pool **receipt-bound** — `source_artifact_refs` + `source_artifact_hashes` required |

---

## DO NOT ADD (explicit non-goals)

- Do not touch `agentic_core`.
- Do not add L4/Chroma writes for failed candidates.
- Do not change X3 disposition semantics.
- Do not implement judge regen for lanes that do not already have it.
- Do not create a parallel publish selector in `candidate_pool`.
- Do not let Notion become canonical storage for candidate text.

---

## Pool origin & proof class (MUST — #2)

Every `pool_manifest.json` **must** include:

| Field | Values | Meaning |
|-------|--------|---------|
| `pool_origin` | `LIVE_RUNTIME` \| `BACKFILL` | Who produced this pool directory |
| `proof_class` | `LIVE_RUNTIME_PERSISTENCE` \| `FILESYSTEM_BACKFILL_RECONSTRUCTION` | What kind of evidence this is |
| `backfill_non_claims` | string[] (required when `BACKFILL`) | Fixed set below |

**When `pool_origin=BACKFILL`, `backfill_non_claims` must include all of:**

- `no_llm_rerun`
- `no_original_runtime_hook_proof`
- `no_x3_change`
- `no_l4_uwg_commit`

**Receipt rule:** Backfill may reconstruct candidates from logs; it **cannot** claim the original runtime emitted `candidate_pool/` at lane exit.

---

## Receipt-bound `pool_manifest.json` (MUST — #1)

**Schema:** `apps_candidate_pool_v1`  
**Path:** `<artifact_dir>/candidate_pool/pool_manifest.json` (written **last** after all candidates)

### Manifest required fields

| Field | Required | Notes |
|-------|----------|-------|
| `contract_type` | yes | `apps_candidate_pool_v1` |
| `contract_version` | yes | `1.0.0` |
| `producer_stage` | yes | `L2` \| `Exit` persistence hook \| `backfill_cli` |
| `generated_at_utc` | yes | ISO-8601 |
| `app_id` | yes | e.g. `apps_rg` |
| `section_id` | yes | e.g. `executive_summary` |
| `run_id` | yes | |
| `trace_root` | if available | from `run_manifest.json` / runtime payload |
| `display_field_key` | yes | e.g. `resume_display_text` |
| `pool_origin` | yes | § Pool origin |
| `proof_class` | yes | § Pool origin |
| `backfill_non_claims` | when BACKFILL | § Pool origin |
| `operator_judge_pass_floor` | if set | |
| `x3_code` | yes | from `x3_disposition.json` at write time |
| `source_artifact_refs` | yes | repo-relative paths to inputs used to build pool |
| `source_artifact_hashes` | yes | `{ "<ref>": "<sha256>" }` for each ref |
| `candidates` | yes | ordered list of `candidate_id` only (detail in per-candidate files) |
| `published_candidate_id` | yes | |
| `publish_decision_ref` | yes | repo-relative `publish_decision.json` |
| `publish_decision_status` | yes | `MIRRORED` \| `UNKNOWN` \| `MISSING_F8A3C2` |
| `validation_status` | yes | `PASS` \| `FAIL` |
| `validation_errors` | yes | `[]` when PASS |
| `explicit_non_claims` | yes | includes `REVIEW_INDEX_ONLY_NOT_PROMOTION` when X3_REVIEW* |

**Reason:** Contract law requires replayable, signed/policy-bound handoff. Files without refs/hashes are convenience snapshots, not proof.

**Receipt links:** [receipt_links.py](ops_scripts/apps_rg/l6_benchmarks/receipt_links.py) → parallel `*_links` objects.

---

## Candidate record schema (MUST — #3)

**Path:** `<artifact_dir>/candidate_pool/candidates/<candidate_id>.json`  
(`candidate_id` = stable hash — see below)

### Per-candidate required fields

| Field | Required | Notes |
|-------|----------|-------|
| `contract_type` | yes | `apps_candidate_pool_candidate_v1` |
| `candidate_id` | yes | stable: `sha256(section_id + candidate_type + cycle_number + content_hash)[:16]` |
| `candidate_type` | yes | enum below |
| `content_hash` | yes | sha256 of canonical display text bytes |
| `display_text` | yes | inline for replay; refs still required |
| `display_field_key` | yes | |
| `cycle_number` | nullable | null for SCRATCH / FINAL_PUBLISHED |
| `candidate_type` | yes | `SCRATCH` \| `REGEN_ACCEPTED` \| `REGEN_REJECTED` \| `REGEN_PARSE_FAILED` \| `FINAL_PUBLISHED` |
| `extraction_method` | yes | `LIVE_HOOK` \| `BACKFILL_PROVIDER_RESPONSE` \| `BACKFILL_PROVIDER_REQUEST_ASSISTANT_TURN` \| `BACKFILL_L2_OUTPUT` |
| `provider_request_ref` | nullable | repo-relative |
| `provider_response_ref` | nullable | repo-relative |
| `parsed_output_ref` | nullable | |
| `judge_output_ref` | nullable | post-regen rescore artifact if applicable |
| `judge_scores_by_model` | yes | `{ "anthropic_claude": 3.6, ... }` |
| `min_score` | yes | |
| `floor` | yes | operator floor at evaluation time |
| `accept_gate` | nullable | |
| `reject_gate` | nullable | |
| `regression_from_prior_best` | yes | boolean |
| `published_candidate` | yes | boolean |
| `publish_decision_ref` | nullable | |
| `source_artifact_refs` | yes | |
| `source_artifact_hashes` | yes | |
| `validation_status` | yes | `PASS` \| `FAIL` |
| `validation_errors` | yes | |

**Legacy filenames** (`scratch.json`, `regen_cycle_N.json`) may remain as **symlinks or manifest aliases** to `candidates/<id>.json` for operator ergonomics; canonical store is `candidates/<candidate_id>.json`.

**Reason:** Observed bug collapsed scratch/regressed regen into “final output.” Schema must make identity loss impossible.

---

## W3 boundary — publish authority (MUST — #7)

| Rule | Detail |
|------|--------|
| This plan **does not** decide best-of candidate selection | f8a3c2 owns argmax / G3 |
| This plan **records** whatever f8a3c2 + lane decided | mirror only |
| `publish_decision.json` | persistence mirror of lane/f8a3c2 artifacts — **not** an independent selector |
| Missing f8a3c2 artifacts | `publish_decision_status=UNKNOWN` or `MISSING_F8A3C2`; **must not** infer best candidate |
| `FINAL_PUBLISHED` candidate | written from lane authoritative display field + `publish_decision_ref` when status `MIRRORED` |

---

## Writer discipline — atomic append (MUST — #6)

`apps_rg/runtime/candidate_pool/writer.py`:

1. Write each candidate JSON to `candidates/<candidate_id>.json.tmp` → `fsync` → atomic rename.
2. Never overwrite existing candidate file unless `--force-backfill` **and** incoming `content_hash` matches existing (idempotent) or operator confirms mismatch in receipt.
3. Write `pool_manifest.json` **last** (same tmp → rename).
4. Index append (`failed_judge_regen_runs_index.jsonl`):
   - lock file `failed_judge_regen_runs_index.lock` or atomic append via temp + concat rename
   - upsert key: `app_id + section_id + run_id + artifact_dir_hash` — **idempotent**, no duplicate rows
5. Notion sync failure **must not** mutate `candidate_pool/` or X3.

---

## Lane adapter — fail-closed (MUST — #11)

`lane_adapter.py` extraction **raises** `CandidatePoolExtractionError` (fail-closed) when:

| Condition | Action |
|-----------|--------|
| `display_field_key` missing from lane manifest | FAIL — no pool write |
| `parsed_output` and `l2_output` disagree on display text without `publish_decision` | FAIL |
| candidate text empty | FAIL |
| `section_id` unknown (not in registry) | FAIL |
| `artifact_dir` cannot be resolved | FAIL |
| multiple display artifacts conflict | FAIL |

**Forbidden silent fallback:** Do not use `provider_response` text as display text unless `extraction_method` explicitly records that fallback (e.g. `BACKFILL_PROVIDER_RESPONSE`) and `validation_errors` documents the ambiguity.

---

## Notion boundaries (MUST — #5, #10)

| Rule | Detail |
|------|--------|
| Read-only sources | Notion sync reads **only** `failed_judge_regen_runs_index.jsonl` + `pool_manifest.json` (+ `candidate_pool_summary.json` if present) |
| Not stored in Notion | Full candidate text as canonical payload |
| Notion stores | metadata, `preview_chars` snippet, repo-relative links, hashes, explicit non-claims |
| Upsert key | `app_id + section_id + run_id + artifact_dir_hash` |
| Sync failure | exit non-zero; **no** writes to `candidate_pool/` or X3 |
| Required non-claim on row | `REVIEW_INDEX_ONLY_NOT_PROMOTION` |
| PII default | `preview_chars=200` max; **redact emails/phones** in preview unless `APPS_RG_NOTION_PREVIEW_REDACT=0` |
| Full payload | disk only under `candidate_pool/candidates/` |

---

## Optional — `candidate_pool_summary.json` (#9, W4.2)

**Path:** `<artifact_dir>/candidate_pool/candidate_pool_summary.json`

| Field | Purpose |
|-------|---------|
| `run_id`, `section_id`, `x3_code` | L6 RCA header |
| `candidate_count`, `rejected_count`, `regressed_count` | counts |
| `best_score_seen`, `published_candidate_id` | |
| `failed_judges` | |
| `candidate_pool_manifest_ref` | |

L6 reads summary + manifest ref; does not parse every full candidate body for high-level RCA.

---

## W6 backfill — historical classification (MUST — #12)

Each backfilled index line and manifest when `pool_origin=BACKFILL`:

| Field | Values |
|-------|--------|
| `historical_runtime_pool_present` | bool — was `candidate_pool/` already on disk at backfill time |
| `reconstructed_from_logs` | bool — always true for BACKFILL |
| `reconstruction_confidence` | `HIGH` \| `MEDIUM` \| `LOW` |
| `missing_refs` | string[] — refs that could not be resolved |

**Confidence rubric:**

- `HIGH`: provider_response + cycles + x3 + display field all present
- `MEDIUM`: missing one of judge rescore / parsed_output
- `LOW`: scratch inferred only from provider_request assistant turn

---

## Shared Module (apps_rg SSOT)

**Package:** `apps_rg/runtime/candidate_pool/`

| Module | Role |
|--------|------|
| `schema.py` | `apps_candidate_pool_v1` + candidate v1 validators |
| `writer.py` | atomic writes, manifest-last |
| `hasher.py` | `content_hash`, `candidate_id`, `artifact_dir_hash` |
| `lane_adapter.py` | fail-closed protocol |
| `adapters/executive_summary.py` | W2 reference |
| `index.py` | idempotent jsonl append |
| `mirror_publish.py` | W3 f8a3c2 mirror only |

---

## Cross-run index

`artifacts/apps_rg/runtime_proofs/failed_judge_regen_runs_index.jsonl` — one line per in-scope run; includes `pool_origin`, `proof_class`, `artifact_dir_hash`, `reconstruction_confidence` when backfill.

---

## Execution Waves

| Wave | Focus | Status | Success Criteria |
|------|--------|--------|------------------|
| W0 | Plan + Notion Plans row | ✅ DONE | Registered |
| W1 | Receipt-bound schema + writer + contract test | 🔲 TODO | § Closeout commands (unit + contract) |
| W2 | executive_summary LIVE_RUNTIME hooks | 🔲 TODO | 070105 backfill + live path |
| W3 | Mirror f8a3c2 publish only | 🔲 TODO | `publish_decision_status` never infers |
| W4 | L6 summary + exhaust refs | 🔲 TODO | `candidate_pool_summary.json` |
| W5 | Notion index sync (read-only) | 🔲 TODO | PII redaction + non-claim |
| W6 | Backfill CLI + historical fields | 🔲 TODO | `proof_class=FILESYSTEM_BACKFILL_RECONSTRUCTION` |
| W7 | Lane registry + adoption | 🔲 TODO | fail-closed adapter doc |

### Phase Detail (updated)

| Phase | Title |
|-------|-------|
| W1.0 | `apps_candidate_pool_v1` + candidate v1 JSON schema + `.cursor/schemas/` mirror |
| W1.1 | Atomic `writer.py` + `hasher.py` |
| W1.2 | Unit tests: schema validation, atomic write, idempotent index |
| W1.3 | **Contract test:** `test_apps_rg_candidate_pool_review_no_commit.py` (D10) |
| W2.0 | executive_summary adapter (fail-closed) |
| W2.1 | LIVE_RUNTIME hooks at scratch / cycle / publish mirror |
| W2.2 | Migrate exec snapshot helpers → shared writer |
| W3.0 | `mirror_publish.py` — read f8a3c2/lane only; UNKNOWN when missing |
| W4.0 | L6 `input_refs` + optional `candidate_pool_summary.json` |
| W4.1 | Exhaust inventory |
| W4.2 | `candidate_pool_summary.json` writer |
| W5.0 | `apps_failed_judge_regen_review_sync.py` (read-only, upsert key) |
| W5.1 | Operator doc + PII policy |
| W6.0 | `backfill_apps_candidate_pool.py` with historical classification |
| W6.1 | Index emit idempotent |
| W7.0 | `LANE_REGISTRY.md` |

---

## Proof / Definition of Done

| # | Criterion | Evidence |
|---|-----------|----------|
| D1 | `pool_manifest.json` with `contract_type`, refs, hashes, `validation_status=PASS` | schema validator |
| D2 | SCRATCH + REGEN_* candidates distinct `candidate_id` + `candidate_type` | 070105 backfill |
| D3 | Rejected cycle: `REGEN_REJECTED` + `reject_gate` | candidate file |
| D4 | `r1b` `NOT_EMITTED` on REVIEW | contract test |
| D5 | L6 lists `candidate_pool_manifest_ref` | l6_shadow_learning.json |
| D6 | Notion row: metadata only + `REVIEW_INDEX_ONLY_NOT_PROMOTION` | sync dry-run |
| D7 | Index ≥3 runs, idempotent re-run | jsonl |
| D8 | Unit tests PASS | pytest |
| D9 | W7 registry | doc |
| **D10** | **X3/UWG negative guard** | § Contract test |
| D11 | BACKFILL manifest has `backfill_non_claims` | backfill receipt |
| D12 | `publish_decision_status` not inferred without f8a3c2 | W3 test |

### D10 — X3/UWG negative test (MUST — #4)

**File:** `tests/_apps_contract/test_apps_rg_candidate_pool_review_no_commit.py`

**Setup:** Use or backfill REVIEW run with `candidate_pool/` present (e.g. `exec_summary_20260526_070105`).

**Assert:**

- `r1b_governed_receipt_chain.json` → `commit_request_status == "NOT_EMITTED"`
- No `commit_request.json` in artifact dir
- No `uwg_commit_receipt.json` / L4 write artifacts
- `pool_manifest.explicit_non_claims` contains `REVIEW_INDEX_ONLY_NOT_PROMOTION`
- Notion sync dry-run output includes same non-claim (when W5 done)

---

## Closeout commands (MUST — #8)

Minimum commands for W7.1 closeout report (record **exit codes**, paths, candidate counts, hashes, non-claims):

```bash
# Unit + contract
set PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
python -m pytest tests/unit/apps_rg/runtime/candidate_pool -q -o addopts=
python -m pytest tests/_apps_contract/test_apps_rg_candidate_pool_review_no_commit.py -q -o addopts=

# Backfill dry-run then apply (reference run)
python tools/cursor/backfill_apps_candidate_pool.py --root artifacts/apps_rg/runtime_proofs --run-id exec_summary_20260526_070105 --dry-run
python tools/cursor/backfill_apps_candidate_pool.py --root artifacts/apps_rg/runtime_proofs --run-id exec_summary_20260526_070105

# Notion index sync (read-only)
python tools/notion/apps_failed_judge_regen_review_sync.py --index artifacts/apps_rg/runtime_proofs/failed_judge_regen_runs_index.jsonl --dry-run
```

**Closeout report path:** `docs/reports/cursor/apps_candidate_pool_persistence_closeout_20260526.md`

**Report must include:** per-command exit code; `candidate_count` / `rejected_count` / `regressed_count`; `pool_manifest.content_hash` or manifest digest; `publish_decision_status`; `proof_class`; explicit non-claims list.

---

## Reference Runs (fixtures)

| Run | Section | Floor | X3 | Notes |
|-----|---------|-------|-----|-------|
| `exec_summary_20260526_070105` | executive_summary | 4.2 | `X3_REVIEW_JUDGE_SOFT_FAIL` | Regen regressed — BACKFILL `MEDIUM` |
| `exec_summary_20260526_070530` | executive_summary | 4.4 | `X3_REVIEW_JUDGE_SOFT_FAIL` | 3 cycles |
| `exec_summary_20260526_065846` | executive_summary | 4.0 | `X3_ALLOW` | SCRATCH + FINAL_PUBLISHED only |

---

## Files Touched (expected)

| File | Role |
|------|------|
| `apps_rg/runtime/candidate_pool/*` | Shared SSOT |
| `.cursor/schemas/apps_candidate_pool_v1.schema.json` | Schema SSOT |
| [executive_summary_lane.py](apps_rg/runtime/sections/executive_summary_lane.py) | LIVE_RUNTIME hooks |
| [l6_shadow_learning.py](apps_rg/runtime/shadow/l6_shadow_learning.py) | summary refs |
| `tools/cursor/backfill_apps_candidate_pool.py` | BACKFILL + historical fields |
| `tools/notion/apps_failed_judge_regen_review_sync.py` | read-only Notion |
| `tests/unit/apps_rg/runtime/candidate_pool/` | unit |
| `tests/_apps_contract/test_apps_rg_candidate_pool_review_no_commit.py` | D10 |

---

## Risks

| Risk | Mitigation |
|------|------------|
| Backfill claimed as live proof | `proof_class` + `backfill_non_claims` |
| Notion becomes SSOT | read-only sync + no full text |
| Publish fork vs f8a3c2 | W3 mirror only + UNKNOWN |
| Corrupt partial writes | atomic writer + manifest last |
| PII in Notion | redact + short preview |

---

WAVE_ID: W0
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
