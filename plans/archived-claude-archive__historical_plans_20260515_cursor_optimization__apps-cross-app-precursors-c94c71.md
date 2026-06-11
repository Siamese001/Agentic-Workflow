---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\historical_plans_20260515_cursor_optimization\\apps-cross-app-precursors-c94c71.md'
original_relative_path: '_archive\\historical_plans_20260515_cursor_optimization\\apps-cross-app-precursors-c94c71.md'
source_sha256: 3dd4066deecf8525517994f60e7c3a8463a49267183db90b74769335a5d39ea2
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: apps-cross-app-precursors-c94c71
plan_type: refactor
---

# apps_* Cross-App Precursors — Typed Envelopes + Chassis Validation

Formalizes the 4 real cross-app HOP precursors identified in the 2026-05-01 orchestration inventory as typed, sealed, traced envelopes; validates duplication classifications before proposing any chassis extraction; resolves the `apps_eval → apps_exec` Python-import coupling.

---

## Context (SCQA)

- **Situation** — The 2026-05-01 orchestration inventory (see the "apps_* Orchestration Inventory — Discovery Report" produced prior to this plan) mapped all 9 `apps_*` packages and found exactly 4 real cross-app producer→consumer relationships, all landing in **apps_qna** as file-based artifact handoffs with regex/ad-hoc parsing. It also found 6 copies of `RepoSignalService`, 7 `observability_adapter.py` files with similar shapes, 5 parallel `<app>_spine_adapter.py` files, and 5 parallel `<app>_ingress_runner.py` files. One Python-import coupling (`apps_eval/engines/scenario_runner.py → apps_exec.reasoning.ExecOrchestrator`) is not a HOP precursor but is worth classifying.
- **Complication** — The 4 cross-app artifact handoffs are implemented via brittle markdown-regex / loose-YAML parsers on the consumer side (`apps_qna/integrations/from_apps_*.py`). The `from_apps_rg` docstring explicitly admits `today's contract is loose`. Drift in producer output silently produces empty consumer loads, and there is no schema_version, seal hash, trace, or freshness check. Separately, the duplicated utilities (`RepoSignalService`, observability adapters, etc.) may be genuinely divergent domain code or may be copy-paste — no byte-level diff has been run, so "chassis extraction" is speculative abstraction today.
- **Question** — How do we harden the 4 real cross-app precursors and resolve the evaluator coupling without prematurely extracting a chassis that may not reflect real shared code?
- **Answer** — Two parallel streams. Stream A ships the 4 typed producer-sealed consumer-validated envelopes with lineage (SHA-linked producer→downstream SHA). Stream B runs byte-level diffs on the 4 duplicated-surface families (RepoSignalService, observability_adapter, spine_adapter, ingress_runner) and produces a classification report; only code that provably duplicates lands in `apps_common`. Stream C resolves the `apps_eval → apps_exec` import with an explicit `EvalHarnessSubject` protocol. `apps_common` creation is explicitly gated on Stream B's classification report — no chassis extraction before evidence.

---

## Evidence Sources

| Source | Why needed | Status |
|---|---|---|
| Inventory report (inline in session 2026-05-01) | baseline inventory, precursor classification, chassis recommendations | ✅ referenced |
| `@c:/Git/Agentic-Workflow-FRESH/apps_qna/integrations/from_apps_shared.py` | Contract 1 current state (master_resume.json loader) | ✅ read |
| `@c:/Git/Agentic-Workflow-FRESH/apps_qna/integrations/from_apps_research.py` | Contract 2 current state (research brief regex parser) | ✅ read (first 60 lines) |
| `@c:/Git/Agentic-Workflow-FRESH/apps_qna/integrations/from_apps_exec.py` | Contract 3 current state (executive brief regex parser) | ✅ read |
| `@c:/Git/Agentic-Workflow-FRESH/apps_qna/integrations/from_apps_rg.py` | Contract 4 current state — docstring admits contract is loose | ✅ read |
| `@c:/Git/Agentic-Workflow-FRESH/apps_shared/integrations/app_registry.py` | Governance status per app; substrate contract | ✅ read |
| `@c:/Git/Agentic-Workflow-FRESH/apps_shared/integrations/governed_app_runner.py` | How producer apps emit today — hook point for producer-side envelope emit | 🔲 |
| `apps_*/services/repo_signal_service.py` (6 copies) | Stream B diff input | 🔲 |
| `apps_*/integrations/observability_adapter.py` (7 copies) | Stream B diff input | 🔲 |
| `apps_*/spine/*_spine_adapter.py` (5 copies) | Stream B diff input | 🔲 |
| `apps_*/integrations/*_ingress_runner.py` (5 copies) | Stream B diff input | 🔲 |
| `@c:/Git/Agentic-Workflow-FRESH/apps_eval/engines/scenario_runner.py` lines 561–620 | Stream C evidence — apps_eval imports apps_exec | ✅ read |

---

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 — Stream B prerequisite | Duplication classification report | Byte-level diff of 4 duplicated families; PASS/DIVERGE verdict per family | A | ~8K 🟢 |
| Wave 2 — Stream A contracts | 4 typed cross-app envelopes | `apps_shared/contracts/cross_app/` (NEW) with 4 Pydantic envelopes, schema-version registry, seal/hash + TTL helpers | B | ~14K 🟢 |
| Wave 3 — Stream A producers | Producer-side envelope emit | apps_shared/apps_research/apps_exec/apps_rg emit envelope JSON alongside current artifacts; dual-write for one release | C | ~14K 🟢 |
| Wave 4 — Stream A consumers | Consumer-side envelope load | apps_qna `from_apps_*.py` modules grow a typed-envelope loader; regex path retained as fallback; deprecation warning on fallback | D | ~12K 🟢 |
| Wave 5 — Stream B chassis extraction (conditional) | Extract code that Wave 1 proved identical | Only runs for families Wave 1 flagged PASS (zero divergence). DIVERGE families stay per-app. | E | ~18K 🟡 (gated) |
| Wave 6 — Stream C evaluator coupling | Resolve apps_eval → apps_exec | Author-Gate: move scenario_runner to tests/, OR keep with typed `EvalHarnessSubject` protocol, OR accept as documented coupling | F | ~8K 🟢 |
| Wave 7 — Retire regex fallbacks + CI gate | Remove dual-write path; enforce envelope-only loading | Pre-commit gate: no new `from_apps_*` markdown-regex loaders | G | ~6K 🟢 |

**Total: ~80K tokens across 7 waves.** Wave 5 gated on Wave 1 verdict; if all 4 families DIVERGE the wave no-ops.

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| 1.1 | Byte-diff `RepoSignalService` × 6 | `apps_{eval,exec,research,rfp,rg,lic}/services/repo_signal_service.py` + `apps_rg/utils/repo_signal_service.py` | PP-1 | ~2K | 🔲 TODO |
| 1.2 | Byte-diff `observability_adapter.py` × 7 | one per app `integrations/` | PP-1 | ~2K | 🔲 TODO |
| 1.3 | Byte-diff `<app>_spine_adapter.py` × 5 | `apps_*/spine/*_spine_adapter.py` | PP-1 | ~2K | 🔲 TODO |
| 1.4 | Byte-diff `<app>_ingress_runner.py` × 5 | `apps_*/integrations/*_ingress_runner.py` | PP-1 | ~2K | 🔲 TODO |
| 1.5 | Classification report | `docs/reports/apps_common_duplication_report.md` (NEW) | — | (included) | 🔲 TODO |
| 2.1 | Envelope base class + seal/hash/freshness helpers | `apps_shared/contracts/cross_app/base.py` (NEW) | GAP-1 | ~4K | 🔲 TODO |
| 2.2 | `ExperienceLibraryEnvelope` (Contract 1) | `apps_shared/contracts/cross_app/experience_library.py` (NEW) | GAP-2 | ~3K | 🔲 TODO |
| 2.3 | `ResearchBriefEnvelope` (Contract 2) | `apps_shared/contracts/cross_app/research_brief.py` (NEW) | GAP-3 | ~3K | 🔲 TODO |
| 2.4 | `ExecutiveBriefEnvelope` (Contract 3) | `apps_shared/contracts/cross_app/executive_brief.py` (NEW) | GAP-3 | ~2K | 🔲 TODO |
| 2.5 | `ResumeBankEnvelope` (Contract 4) with `master_resume_source_sha256` lineage | `apps_shared/contracts/cross_app/resume_bank.py` (NEW) | GAP-4 | ~2K | 🔲 TODO |
| 3.1 | `apps_shared/data/master_resume.json` producer-side envelope emitter | `apps_shared/data/__main__.py` or script | GAP-2 | ~3K | 🔲 TODO |
| 3.2 | apps_research envelope emit (hook into governed_research_run) | `apps_research/integrations/governed_research_run.py` (edit), `apps_research/outputs/*` (new emitter) | GAP-3 | ~4K | 🔲 TODO |
| 3.3 | apps_exec envelope emit | `apps_exec/integrations/governed_exec_run.py` (edit) + emitter | GAP-3 | ~3K | 🔲 TODO |
| 3.4 | apps_rg envelope emit (new — currently no bank emission contract) | apps_rg bank emitter | GAP-4 | ~4K | 🔲 TODO |
| 4.1 | `from_apps_shared` typed-envelope loader + regex fallback deprecation warning | `apps_qna/integrations/from_apps_shared.py` (edit) | GAP-2 | ~3K | 🔲 TODO |
| 4.2 | `from_apps_research` typed-envelope loader | `apps_qna/integrations/from_apps_research.py` (edit) | GAP-3 | ~3K | 🔲 TODO |
| 4.3 | `from_apps_exec` typed-envelope loader | `apps_qna/integrations/from_apps_exec.py` (edit) | GAP-3 | ~3K | 🔲 TODO |
| 4.4 | `from_apps_rg` typed-envelope loader + replace `today's contract is loose` note | `apps_qna/integrations/from_apps_rg.py` (edit) | GAP-4 | ~3K | 🔲 TODO |
| 5.1 | If Wave 1 RepoSignalService=PASS: extract to `apps_common/services/repo_signal_service.py` + migrate 6 imports | conditional | PP-2 | ~6K | 🔲 GATED |
| 5.2 | If Wave 1 observability_adapter=PASS: extract | conditional | PP-2 | ~4K | 🔲 GATED |
| 5.3 | If Wave 1 spine_adapter=PASS: extract | conditional | PP-2 | ~4K | 🔲 GATED |
| 5.4 | If Wave 1 ingress_runner=PASS: extract | conditional | PP-2 | ~4K | 🔲 GATED |
| 6.1 | Author-Gate — resolve `apps_eval → apps_exec` coupling | (decision packet) | AG-1 | ~1K | 🔲 TODO |
| 6.2 | Execute chosen path (move to tests/ or define EvalHarnessSubject protocol) | scope depends on AG-1 verdict | — | ~7K | 🔲 TODO |
| 7.1 | Retire regex fallbacks in `from_apps_*.py` | 4 files | GAP-5 | ~2K | 🔲 TODO |
| 7.2 | CI gate forbidding new `from_apps_*` regex loaders | `ops_scripts/ci/check_cross_app_envelope_loaders.py` (NEW) | — | ~4K | 🔲 TODO |

---

## Gap Register

**GAP-1** — No base envelope with seal/hash/trace/freshness fields exists. Every cross-app load reinvents.

**GAP-2** — `master_resume.json` has no producer-side emit envelope; consumers read the raw JSON directly. Changes to the master file silently change consumer behavior.

**GAP-3** — `research_brief_*.md` and `exec_brief_*.md` are markdown output primarily for humans; consumer regex parsing is brittle. Producer should emit a sidecar `.envelope.json` with the typed fields.

**GAP-4** — `apps_rg/data/*.yaml` contract is self-described as loose. `ResumeBankEnvelope` must also carry `master_resume_source_sha256` to thread lineage.

**GAP-5** — No CI gate exists to prevent new brittle loaders.

---

## Pain Points

**PP-1** — 4 duplicated-surface families (RepoSignalService×6, observability_adapter×7, spine_adapter×5, ingress_runner×5) may or may not be real duplication; no byte-level evidence exists. Premature chassis extraction is a documented failure mode (see the 2026-02-08 apps_lic HOP consolidation that lost the domain logic).

**PP-2** — Once Wave 1 produces PASS verdicts, migrating imports across apps is mechanical but touches many files; each migration needs a per-app parity check.

---

## Execution Plan

### Wave 1 — Duplication Classification (prerequisite to chassis)

Run `git diff --no-index` (or equivalent) pairwise across each family. Produce a single report at `docs/reports/apps_common_duplication_report.md` with this shape:

| Family | Files | Byte-identical pairs | Near-identical (≤5% diff) pairs | Divergent pairs | Verdict |
|---|---|---:|---:|---:|---|
| RepoSignalService | 6+1 | N | M | K | PASS / DIVERGE |
| observability_adapter | 7 | ... | ... | ... | ... |
| spine_adapter | 5 | ... | ... | ... | ... |
| ingress_runner | 5 | ... | ... | ... | ... |

**PASS rule**: ≥80% of pairs byte-identical AND zero divergent pairs → family is chassis-extractable.
**DIVERGE rule**: any pair with ≥20% difference → family stays per-app; report captures why.

No code changes in this wave.

### Wave 2 — Envelope Base + 4 Contracts

`apps_shared/contracts/cross_app/base.py` exports:
```
class CrossAppEnvelope(BaseModel, frozen=True):
    schema_version: str           # semver; consumers track compat
    trace_id: str                 # producer's run trace
    producer_app: str             # "apps_research", etc.
    emitted_at: datetime          # UTC
    source_sha256: str            # hash of the produced bytes
    ttl_days: int = 30            # default freshness window
    # subclasses add fields
```

4 concrete envelopes in sibling modules, each with a producer-side `emit(...)` classmethod and a consumer-side `load(path) -> Envelope` classmethod that raises on schema/TTL/hash mismatch.

### Wave 3 — Producer-Side Emit (dual-write)

Each producer emits the envelope JSON **alongside** its current artifact. Backward-compat maintained. Example for apps_research:

```
reports/research/
  research_brief_<trace>.md          ← unchanged
  source_register_<trace>.json       ← unchanged
  research_brief_<trace>.envelope.json   ← NEW (ResearchBriefEnvelope)
```

### Wave 4 — Consumer-Side Envelope Load

`apps_qna/integrations/from_apps_research.py` gets a new code path:
1. Try loading `*.envelope.json` — if present, use typed load (fast, safe).
2. Fallback to current markdown-regex parser — emit `DeprecationWarning: envelope missing, falling back to regex`.

Same pattern for the other 3 consumers.

### Wave 5 — Chassis Extraction (Gated on Wave 1)

For each family Wave 1 reports as PASS: extract to `apps_common/<subpackage>/`, rewrite N imports across apps, run existing per-app tests. For DIVERGE families: no action; inventory report documents why they diverged.

### Wave 6 — Resolve apps_eval → apps_exec Coupling

Author-Gate packet with options:
- (A) Move `scenario_runner._scenario_exec_*` scenarios into `apps_eval/tests/integration/` — accept that eval-of-exec is test-time only.
- (B) Define `EvalHarnessSubject` protocol in `apps_shared/contracts/eval_harness.py` that apps_exec (and future subjects) implements; `scenario_runner` imports the protocol only.
- (C) Accept current coupling and add a CI allowlist entry documenting the cross-app import.

Execute the chosen option.

### Wave 7 — Retire Fallbacks + CI Gate

After ≥2 weeks of dual-write (giving producers time to deploy envelopes), remove regex fallbacks from `from_apps_*.py`. Add `ops_scripts/ci/check_cross_app_envelope_loaders.py` enforcing: any new `from_apps_*.py` MUST load through `CrossAppEnvelope`.

---

## Rules

- **No chassis extraction without Wave 1 PASS verdict** — this is the core discipline of the plan.
- **Dual-write period for ≥2 weeks** between Wave 3 ship and Wave 7 fallback retirement.
- **No envelope claims without a real consumer** — Wave 2 contracts are authored only for Contracts 1–4 (all 4 have apps_qna as consumer).
- **apps_common never takes speculative code** — only code Wave 1 proves identical.
- **Layer gravity preserved** — `apps_shared/contracts/cross_app/` imports only from `agentic_core` and stdlib; `apps_common/` (if it comes to exist) imports only from `agentic_core` and `apps_shared`.
- **No loss of per-stage functionality** — Wave 4 consumers must be backward-compatible via regex fallback until Wave 7.
- **Author-Gate required** for Wave 6 (AG-1).

---

## Success Criteria

- [ ] Wave 1 report published at `docs/reports/apps_common_duplication_report.md` with PASS/DIVERGE verdict per family.
- [ ] 4 envelopes in `apps_shared/contracts/cross_app/`, each with producer emit + consumer load + golden fixture test.
- [ ] All 4 producers emit sidecar `*.envelope.json` alongside current artifacts.
- [ ] All 4 `from_apps_*.py` loaders prefer envelope path; fallback emits DeprecationWarning.
- [ ] Wave 5 chassis extraction completes for every PASS family (zero-regression per-app tests).
- [ ] Wave 6 Author-Gate resolution captured; apps_eval → apps_exec coupling explicitly classified.
- [ ] CI gate `check_cross_app_envelope_loaders.py` active; no new regex loaders.
- [ ] Zero existing apps_qna build behavior regressions (golden-pack parity test).

---

## Implementation Commands

```bash
# Wave 1 — byte diff
python ops_scripts/analysis/diff_duplicated_families.py \
  --family repo_signal_service \
  --out docs/reports/apps_common_duplication_report.md

# Wave 2-4 — per wave
python -m pytest tests/unit/apps_shared/contracts/ -v
python -m pytest tests/integration/cross_app_envelopes/ -v

# Wave 5 (gated)
# only after Wave 1 verdict is read and cleared

# Wave 7
python ops_scripts/ci/check_cross_app_envelope_loaders.py
```

---

## Rollback Strategy

Per-wave independent rollback:
1. **Wave 1**: report-only; no rollback needed.
2. **Wave 2-3**: delete new envelope modules + producer-side emit; dual-write means consumers continue to use regex path.
3. **Wave 4**: revert `from_apps_*.py` to regex-only path; envelopes remain on disk unread.
4. **Wave 5**: per-family rollback — restore pre-extraction copies from git per the affected family.
5. **Wave 6**: revert scenario_runner imports; document as permitted coupling.
6. **Wave 7**: restore regex fallback + CI gate removal; reopen plan.

---

## Acceptance Criteria

| Metric | Target | Verification |
|---|---|---|
| Envelope load latency vs regex load (single file) | ≤ 2x regex latency | micro-benchmark in tests |
| Consumer behavior parity (envelope path vs regex path) | 100% byte-identical output | apps_qna golden pack test |
| Chassis extraction zero-regression | 100% per-app tests pass pre and post migration | existing test suites |
| Cross-app envelope coverage | 4/4 producer→consumer handoffs typed | CI gate asserts |

## Cascade Alignment Checks

- Keep always-on rules lean; place detailed procedures in skills or workflows.
- Retrieve local or scoped evidence before synthesis.
- Prefer exact or structural matches before broad semantic expansion.
- For high-risk outputs, extract evidence or quotes before summarizing.
- Reserve deterministic enforcement for hooks or scripts, not template prose.
