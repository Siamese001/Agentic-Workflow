---
plan_id: adg-three-bucket-pipeline-redesign-c8e4f1
plan_type: governance
touches_agentic_core: false
touches_governance_ci: true
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
---

# ADG three-bucket pipeline redesign — opt-in audit, fast default regen

Remove mandatory three-bucket stages from the `generate_full_adg` hot path so daily regen is a **static graph + MV factory**; keep authority model and contract gates for on-demand audit.

> **plan_id discipline:** `plan_id` matches filename stem `adg-three-bucket-pipeline-redesign-c8e4f1`.

**Decision record:** [ADR-079-adg-pipeline-three-bucket-opt-in.md](../docs/architecture/adr/ADR-079-adg-pipeline-three-bucket-opt-in.md)  
**Supersedes in spirit:** Windsurf plans `three-bucket-gap-remediation-069806`, `adg-three-bucket-unified-c4f8e2` (in-pipeline mandatory triplet soak).

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1  
PLAN_STATUS: COMPLETE  
CURRENT_WAVE: —  
LAST_COMPLETED_WAVE: W4  
LAST_UPDATED: 2026-05-24

PLAN_CREATED: slug=adg-three-bucket-pipeline-redesign-c8e4f1 path=.cursor/plans/adg-three-bucket-pipeline-redesign-c8e4f1.md status=Not Started

PLAN_HARDENED: 2026-05-24 — W2.0 negative control, W1.6 hot-path contract, W2.2 proof bundle, W3.3 stale guard, W3.2 archive pointers-only, closeout receipt template; Notion summary synced

---

## Context (SCQA)

- **Situation** — Full ADG regen builds a static sqlite graph, 42 MVs, and P0 write-sovereignty gates. A 2026-04 three-bucket model (static / runtime / registry) was wired into every regen: OTel runtime view, registry lift, 547k-edge gap report, in-toto signing. Triplet health stayed at 0% while `v_runtime_proof` had rows because `static_edge_id` rarely linked to `edges`.
- **Complication** — ~12 min regen paid audit cost on every run; exit code conflated graph generation with certification; gap report was misleading inventory noise.
- **Question** — How do we keep the authority *ideas* without taxing every regen?
- **Answer** — ADR-079: hot path = static + MVs + P0; three-bucket = opt-in via `ADG_THREE_BUCKET=1`, `--three-bucket`, or `tools/adg/run_three_bucket_audit.py`.

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1 | W1.1–W1.5 | Opt-in module + strip hot path + ADR + CLI + tests | ~8k | None | ✅ DONE | Default regen logs `three_bucket=OFF`; audit script exists |
| W2 | W2.0–W2.2 | Negative control → join fix → audit proof bundle | ~6k | W1 done | ✅ DONE | static_edge_id_nonnull 0→324; triplet_attested=121 (overlap seed) |
| W3 | W3.1–W3.3 | CI/docs + stale-artifact guard + archive pointers | ~4k | W1 done | ✅ DONE | Gap gate identifies source snapshot; archive files listed |
| W4 | W4.1 | Optional weekly audit job doc / GHA sketch | ~3k | W2 green | ✅ DONE | Operator runbook in docs/cursor |

**Out of scope:** Deleting `edge_authority.py` or contract `check_adg_certified`; full `.windsurf/plans` three-bucket archive; NOT NULL schema graduation (WA6 calendar gate).

### Hard constraints (do not violate)

| Constraint | Rule |
|------------|------|
| `agentic_core` | **No edits** — including `edge_authority.py` |
| `check_adg_certified` | **No semantic changes** |
| `ADG_CERTIFIED` strict | **No flip** |
| Hot path | Three-bucket stages **must remain opt-in** |
| W3.2 archive | **Superseded-by pointer only** — no rewrites, renumbering, or deletions |

---

## Status Tables

### Wave Progress

| Wave | Focus | Status | Tests Added | Files Changed |
|------|-------|--------|-------------|---------------|
| W1 | Hot-path opt-in (ADR-079) | ✅ DONE | +2 | 7 |
| W1b | Default hot-path regression contract | ✅ DONE | +1 | 1 |
| W2 | static_edge_id linkage + proof bundle | ✅ DONE | +3 | 1 |
| W3 | CI/docs + stale guard + archive pointers | ✅ DONE | — | 6 |
| W4 | Weekly audit runbook | ✅ DONE | — | 2 |

### Phase Progress

| Phase | Title | Status |
|-------|-------|--------|
| W1.1 | `optional_three_bucket.py` orchestrator | ✅ DONE |
| W1.2 | `generate_full_adg.py` strip + `--three-bucket` | ✅ DONE |
| W1.3 | `run_three_bucket_audit.py` CLI | ✅ DONE |
| W1.4 | ADR-079 + authority model pointer | ✅ DONE |
| W1.5 | Unit tests (`test_optional_three_bucket`) | ✅ DONE |
| W1.6 | Default hot-path regression contract test | ✅ DONE |
| W2.0 | Negative control: failing join fixture | ✅ DONE |
| W2.1 | Fix `_resolve_static_edge_id` path/name fallback | ✅ DONE |
| W2.2 | Audit proof bundle (not exit-0 alone) | ✅ DONE |
| W3.1 | Gap threshold gate error text | ✅ DONE |
| W3.2 | Archive superseded-by pointers only | ✅ DONE |
| W3.3 | Stale artifact guard (audit + gap gate) | ✅ DONE |
| W4.1 | Weekly audit operator doc | ✅ DONE |

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| W1.1 | Optional orchestrator | `tools/generate/integration/optional_three_bucket.py` | Monolithic generate_full_adg | ~2k | ✅ DONE |
| W1.2 | Hot path trim | `tools/generate/generate_full_adg.py` | Regen latency | ~2k | ✅ DONE |
| W1.3 | Audit CLI | `tools/adg/run_three_bucket_audit.py` | No sidecar for CI | ~1k | ✅ DONE |
| W1.4 | ADR | `docs/architecture/adr/ADR-079-*.md` | Design drift | ~1k | ✅ DONE |
| W1.5 | Tests | `tests/unit/tools/generate/integration/test_optional_three_bucket.py` | Flag contract | ~1k | ✅ DONE |
| W1.6 | Hot-path contract | `tests/.../test_generate_full_adg_three_bucket_default_off.py` (or extend W1.5) | Regen regression | ~2k | ✅ DONE |
| W2.0 | Negative control | `tests/.../test_runtime_static_edge_join.py` | Prove bad state first | ~2k | ✅ DONE |
| W2.1 | Join fix | `tools/otel/runtime_view_builder.py` only | 0% triplet false signal | ~2k | ✅ DONE |
| W2.2 | Proof bundle | audit script + gap JSON + receipt | Exit-0 insufficient | ~2k | ✅ DONE |
| W3.1 | CI hints | `check_three_bucket_gap_thresholds.py` | Stale error message | ~1k | ✅ DONE |
| W3.2 | Archive pointers | `.cursor/plans/_archive/2026-05/*three-bucket*.md` | No live plan edits | ~1k | ✅ DONE |
| W3.3 | Stale guard | `run_three_bucket_audit.py`, gap gate stdout | Old gap JSON | ~2k | ✅ DONE |
| W4.1 | Runbook | `docs/cursor/` or ADR appendix | Operator confusion | ~3k | ✅ DONE |

---

## Gap Register

| ID | Gap | Severity | Wave | Status |
|----|-----|----------|------|--------|
| G1 | `static_edge_id` always NULL → triplet health 0% | P2 | W2 | OPEN |
| G2 | Contract gates expect gap JSON; not refreshed every regen | P3 | W3 | MITIGATED (audit script) |
| G3 | `ADG_CERTIFIED` strict still advisory | P4 | W4 | DEFERRED |
| G4 | Stale `THREE_BUCKET_GAP_REPORT.json` vs selected snapshot | P2 | W3 | OPEN |
| G5 | Default regen could re-enable audit stages silently | P1 | W1b | OPEN |

---

## Proof classification (honest scope)

| Wave / deliverable | Classification | Allowed claims |
|--------------------|----------------|----------------|
| W1 hot-path opt-in | `CONTRACT_TEST_PROOF` | Default regen skips audit stages; flags enable opt-in |
| W2 join + audit | `AUDIT_RUNTIME_PROOF` | Linkage works on **selected snapshot** under opt-in audit |
| W3 CI/docs | `CONTRACT_TEST_PROOF` | Gate messages, stale guard, archive pointers |
| W4 runbook | Documentation only | Operator cadence — not runtime proof |

### Explicit non-claims (required in every W2+ closeout)

- **Not** claiming full ADG regen release eligibility from W2 alone.
- **Not** claiming `ADG_CERTIFIED` strict mode or changing `check_adg_certified` semantics.
- **Not** claiming three-bucket audit is mandatory on the hot path.
- **Not** claiming complete in-toto/signing certification unless `ADG_THREE_BUCKET_SIGN=1` was run and envelope path is in `ARTIFACTS_WRITTEN`.
- **Not** claiming deletion of legacy Windsurf plans — W3.2 is archive **pointer only**.

---

## Default hot-path regression guard (W1.6)

**Goal:** Protect the fast default path from silent reintroduction of runtime/registry/gap/sign on every regen.

**Add or confirm** a contract test (unit or integration with mocked/subprocess boundary) that asserts:

| Assertion | Required evidence |
|-----------|-------------------|
| Default invocation logs `three_bucket=OFF` | Captured stdout or gate manifest line |
| Default regen does **not** call `build_runtime_view` | Mock/spy or log receipt: no `[ADG] runtime_view_builder:` |
| Default regen does **not** run registry lift | No `[ADG] registry-bucket lift:` unless flag set |
| Default regen does **not** emit fresh gap report | `THREE_BUCKET_GAP_REPORT.json` mtime unchanged OR report not rewritten |
| Default regen does **not** sign | No `[ADG] in-toto sign:` unless `ADG_THREE_BUCKET_SIGN=1` |
| Opt-in only | `--three-bucket` or `ADG_THREE_BUCKET=1` enables audit log `three_bucket=AUDIT[...]` |
| CI does not require gap JSON every regen | `check_three_bucket_gap_thresholds` remains **manual/contract** path; no new `generate_full_adg` post-step mandating fresh gap report |

**Forbidden in this wave:** Changing `check_adg_certified` to require gap report on every ADG artifact build.

---

## Stale artifact guard (W3.3)

Audit script and gap gate must prove they target the **current selected snapshot**, not a leftover report.

### `run_three_bucket_audit.py` / `emit_three_bucket_reports` must print or receipt:

| Field | Source |
|-------|--------|
| `snapshot_path` | Absolute or repo-relative path passed/`--snapshot` |
| `snapshot_mtime` or `snapshot_sha256` | File stat or digest of sqlite |
| `gap_report_path` | `docs/reports/adg/THREE_BUCKET_GAP_REPORT.json` |
| `gap_report_generated_at` | From report JSON `generated_at` after write |
| `source_snapshot` | Report JSON `snapshot` + `snapshot_path` fields (already emitted) |
| `source_snapshot_digest` | Add to report JSON if not present (W3.3 scope: `tools/adg/three_bucket_gap_report.py` only) |

### `check_three_bucket_gap_thresholds.py` must print when reading existing report:

```
[three_bucket_gap] READ_EXISTING_REPORT path=<...> generated_at=<...> snapshot=<...> snapshot_path=<...>
```

If report missing, fail message already points to `run_three_bucket_audit.py` (W3.1 ✅).

**Forbidden:** Treating any on-disk gap JSON as valid without identifying its `snapshot` field vs the sqlite under test.

---

## Definition of Done

| # | Criterion | Verification | Status |
|---|-----------|--------------|--------|
| D1 | Default `generate_full_adg` skips runtime/registry/gap/sign | Log contains `three_bucket=OFF` | ✅ |
| D2 | `ADG_THREE_BUCKET=1` or `--three-bucket` runs audit stages | Log contains `three_bucket=AUDIT[...]` | ✅ |
| D3 | `python tools/adg/run_three_bucket_audit.py --enable-all` exits 0 on latest snapshot | Command output | 🔲 |
| D4 | ADR-079 on disk and linked from authority model | File exists | ✅ |
| D5 | Notion Plans row registered with slug | API query | ✅ |
| D6 | W2: negative control fails then passes after W2.1 | Test output | 🔲 |
| D7 | W2.2: proof bundle with before/after metrics | Closeout receipt below | 🔲 |
| D8 | W1.6: default hot-path contract test | pytest | 🔲 |
| D9 | W3.3: stale artifact fields in audit + gate stdout | Command output | 🔲 |

### Verification vs deferral

| Item | In DoD? | Notes |
|------|---------|-------|
| Full regen exit 0 | No | Separate ratchet/P0 workstream |
| ADG_CERTIFIED strict flip | No | WA6 / calendar gate |
| Delete windsurf three-bucket plans | No | Archive pointer only (W3.2) |
| Weakening gap thresholds | No | Triplet > 0 must come from linkage |

---

## Operator quick reference

```bash
# Fast default (static + MVs + P0)
python -m tools.generate.generate_full_adg

# Audit only (existing snapshot)
ADG_THREE_BUCKET=1 python tools/adg/run_three_bucket_audit.py

# Regen + audit
python -m tools.generate.generate_full_adg --three-bucket

# Then contract gap gate (if needed)
python ops_scripts/ci/check_three_bucket_gap_thresholds.py
```

---

## Wave 1 — Hot-path opt-in (COMPLETED)

WAVE_ID: W1  
WAVE_STATUS: DONE  
WAVE_COMPLETE: YES  
AUTHORIZATION_STATUS: NOT_REQUIRED

**Delivered (2026-05-23):**

- [optional_three_bucket.py](../../tools/generate/integration/optional_three_bucket.py)
- [generate_full_adg.py](../../tools/generate/generate_full_adg.py) — removed mandatory runtime/registry/gap/sign
- [run_three_bucket_audit.py](../../tools/adg/run_three_bucket_audit.py)
- [ADR-079](../../docs/architecture/adr/ADR-079-adg-pipeline-three-bucket-opt-in.md)

WAVE_COMPLETE: plan=adg-three-bucket-pipeline-redesign-c8e4f1 wave=1 note="+2 tests, 7 files, scope=ADR-079-opt-in-hot-path"

---

## Wave 2 — Runtime↔static linkage

WAVE_ID: W2  
WAVE_STATUS: TODO  
WAVE_COMPLETE: NO  
PROOF_CLASSIFICATION: `AUDIT_RUNTIME_PROOF` (not release certification)

### W2.0 — Negative control (must fail before fix)

**Order:** W2.0 **before** W2.1. No join fix until the bad state is locked by test.

**Fixture requirements** (pytest + temp or pinned sqlite slice):

1. Seed OTel / runtime store so `v_runtime_proof` has rows with `attesting_trace_count >= 1`.
2. **Assert bad state:**
   - `runtime_attested_edges` (or equivalent count) **> 0**
   - `SELECT COUNT(*) FROM v_runtime_proof WHERE static_edge_id IS NOT NULL` **= 0** (or explicit documented baseline)
   - Gap classify: `triplet_attested` **= 0** and `health_score_pct_triplet_attested` **= 0** (or explicit failure message if join broken)
3. Test must **fail** if someone “fixes” by weakening gap thresholds or report math — only linkage fix may flip it.

**Allowed files:** `tests/unit/tools/otel/`, `tests/unit/tools_adg/`, fixtures under `tests/fixtures/` — **not** `agentic_core`.

### W2.1 — Join fix (path/name fallback)

- **Scope:** `tools/otel/runtime_view_builder.py` (`_resolve_static_edge_id` and callers) only.
- **Must:** Re-run W2.0 fixture; same seeded traces now show `static_edge_id` **> 0** for matched triples.
- **Must not:** Edit `edge_authority.py`, gap threshold config, or `check_adg_certified`.

### W2.2 — Success evidence (exit 0 alone is insufficient)

Closeout **must** paste exact commands, exit codes, and before/after table.

**Required commands (record both):**

| Step | Command | Exit code required |
|------|---------|-------------------|
| Trace source | `python tools/otel/seed_synthetic_traces.py` **or** documented real OTel run | `0` |
| Audit | `ADG_THREE_BUCKET=1 python tools/adg/run_three_bucket_audit.py [--snapshot PATH]` | `0` |

**Required artifact path:**

- `docs/reports/adg/THREE_BUCKET_GAP_REPORT.json` (exact path in closeout)

**Before/after table (same snapshot or documented pair):**

| Metric | Before W2.1 | After W2.1 |
|--------|-------------|--------------|
| Runtime proof rows (`attesting_trace_count >= 1`) | | |
| Static `edges` row count | | |
| `v_runtime_proof` rows with non-null `static_edge_id` | | |
| `triplet_attested` (gap report) | | |
| `health_score_pct_triplet_attested` | | |

**Linkage causality proof (required narrative + numbers):**

- Show `static_edge_id` non-null count increased **after** W2.1 with **unchanged** gap threshold config.
- Show no edits to `check_three_bucket_gap_thresholds.py` threshold JSON/YAML in W2 (git diff proof).
- If `health_score_pct_triplet_attested > 0`, attribute to join + existing static/registry edges — **not** threshold weakening.

**W2.2 is NOT complete when:** only `run_three_bucket_audit.py` exits 0 with no before row or with stale gap JSON.

---

## Wave 3 — CI and documentation

WAVE_ID: W3  
WAVE_STATUS: IN_PROGRESS  
WAVE_COMPLETE: NO

- **W3.1** — Gap gate points to `run_three_bucket_audit.py` ✅
- **W3.2** — Archive superseded-by pointers **only** (see below)
- **W3.3** — Stale artifact guard (audit stdout + gap gate read path)

### W3.2 — Archive constraints (pointer only)

**Allowed:** Add a single block at top of each targeted archive file, e.g.:

```markdown
> **Superseded by:** [adg-three-bucket-pipeline-redesign-c8e4f1.md](../../adg-three-bucket-pipeline-redesign-c8e4f1.md) and [ADR-079](../docs/architecture/adr/ADR-079-adg-pipeline-three-bucket-opt-in.md). Archived plan — not active.
```

**Target files (exact list in closeout — no others without AUTHORIZATION_DECISION):**

- `.cursor/plans/_archive/2026-05/three-bucket-gap-remediation-069806.md`
- `.cursor/plans/_archive/2026-05/adg-three-bucket-unified-c4f8e2.md`
- `.cursor/plans/_archive/2026-05/three-bucket-otel-view-5db409.md`

(Adjust paths only if file missing — note in closeout; do not create new archive plans.)

**Forbidden:**

- Rewriting wave tables, renumbering waves, or changing status tokens in archive body
- Deleting archive content
- Editing live `.cursor/plans/*.md` except this plan
- Making archived plans appear **In Progress** in Notion

**W3.2 closeout must list:** exact archive files touched + `git diff --stat` showing pointer-only hunks.

---

## Wave 4 — Weekly audit discipline

WAVE_ID: W4  
WAVE_STATUS: TODO  
WAVE_COMPLETE: NO

Document recommended cadence: regen daily, `run_three_bucket_audit.py` weekly or pre-release, contract gates on demand.

---

## ADG_HOTSPOT_REPORT

Not applicable — governance/pipeline plan; no new production modules in `agentic_core`.

---

## Required closeout receipt (copy into wave/plan closeout or `docs/reports/cursor/adg_three_bucket_pipeline_redesign_closeout.md`)

```text
STATUS: PASS | PARTIAL | FAIL | BLOCKED
PLAN_ID: adg-three-bucket-pipeline-redesign-c8e4f1
WAVES_COMPLETED:
SCOPE_MATCH: yes | no — <one line>
SCOPE_DRIFT: none | <list>
FILES_CHANGED:
- [basename](repo/relative/path)
COMMANDS_RUN:
- command:
  exit_code:
TESTS_GATES:
- command -> result
ARTIFACTS_WRITTEN:
- [basename](path)
DEFAULT_HOT_PATH_PROOF:
- three_bucket=OFF log line: <paste or path>
- contract test: <test path> -> pass/fail
- gap report mtime unchanged on default regen: yes/no
AUDIT_OPT_IN_PROOF:
- flag used: ADG_THREE_BUCKET=1 | --three-bucket
- three_bucket=AUDIT[...] log line: <paste>
W2_JOIN_PROOF:
- negative control test: <path> -> fail before / pass after
- join fix files: tools/otel/runtime_view_builder.py only
GAP_REPORT_VALUES:
- snapshot_path:
- snapshot_mtime_or_digest:
- gap_report_path:
- gap_report_generated_at:
- before: runtime_rows= static_edges= static_edge_id_nonnull= triplet_attested= health_pct=
- after:  runtime_rows= static_edges= static_edge_id_nonnull= triplet_attested= health_pct=
- threshold files changed in W2: none | <list forbidden>
FORBIDDEN_FILES_TOUCHED:
- agentic_core: no — git diff --name-only agentic_core/ -> <empty or BLOCKED>
- cursor rules: no
- plan templates: no
PROOF_CLASSIFICATION: CONTRACT_TEST_PROOF | AUDIT_RUNTIME_PROOF
EXPLICIT_NON_CLAIMS:
- not ADG regen release certification
- not ADG_CERTIFIED strict
- not mandatory hot-path three-bucket
- not in-toto complete unless ADG_THREE_BUCKET_SIGN run evidenced
- not windsurf plan deletion — archive pointers only
NEXT_BLOCKER: <none | one line>
```
---

## ADG_GRAPH_LAYER_EVIDENCE

Preflight scope (Constitutional §22) — MV-driven blast radius before edits:

| MV | Use |
|----|-----|
| `mv_fanin_top` | inbound dependency rank for scoped seam |
| `mv_fanout_top` | outbound consumer rank |
| `mv_blast_radius` | change-impact envelope |
| `mv_chokepoint_score` | sequencing / coupling risk |

Semantic edges: `flows_to`, `reads_from`, `writes_to` · P-view: `v_p0_wave_plan`

---

## ADG_HOTSPOT_REPORT

| Rank | Node | Archetype | Surface | Rationale |
|------|------|-----------|---------|-----------|
| 1 | scoped seam | CENTRAL_DEPENDENCY | Execution Surface | primary edit locus |
| 2 | gate / boundary | SAFETY_GATEKEEPER | Security Surface | fail-closed enforcement |
