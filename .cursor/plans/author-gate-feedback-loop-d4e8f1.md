---
plan_id: author-gate-feedback-loop-d4e8f1
plan_type: governance
touches_agentic_core: false
touches_governance_ci: true
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: "artifacts/governance/migration_receipts/20260517_043100_author_gate_feedback_w1.json"
w13_null_bind_gate_receipt: "artifacts/governance/author_gate_feedback_loop/20260517_044212_w13_null_bind_gate.json"
contract_gates_run_evidence: "artifacts/governance/author_gate_feedback_loop/20260517_contract_gates_after_adg_touch.txt"
ledger_schema_alignment_proof: "artifacts/governance/author_gate_feedback_loop/20260517_044731_ledger_schema_alignment_proof.json"
ledger_integrity_diagnostic: "artifacts/governance/author_gate_feedback_loop/20260517_045057_ledger_integrity_diagnostic.json"
ledger_integrity_repair_receipt: "artifacts/governance/author_gate_feedback_loop/20260517_045057_ledger_integrity_repair_receipt.json"
w0_baseline_latest: "artifacts/governance/author_gate_feedback_loop/20260517_044326_w0_baseline.json"
dod_exempt: false
---

# Author-Gate feedback loop — closure and signal quality

Wave plan to **close the learning loop**: truthier outcomes and bindings, **persisted precedent linkage** on capture, **per-option signals** in SQLite, **smarter lookup ranking**, and **usable calibration** — without weakening Author-Gate or HITL.

> **plan_id**: `author-gate-feedback-loop-d4e8f1` — use `plan=author-gate-feedback-loop-d4e8f1` in lifecycle markers.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: POST_W4_PARTIAL
CURRENT_WAVE: POST_W4
LAST_COMPLETED_WAVE: W4
LAST_UPDATED: 2026-05-17

---

## Context (SCQA)

- **Situation** — `refactor_decision_ledger.sqlite` already captures decisions, FTS lookup feeds `precedent_injector` / `emit_packet`, and CI guards ledger integrity. Prior slice analysis showed sparse **`bind_confidence`**, empty **`decision_signals`**, **`precedent_match_count` often unset**, and flat **`confidence_calibrated`** despite **`confidence_top`** variance.
- **Complication** — Without durable **match IDs + outcome tiers** on rows, audits replay FTS; without **`decision_signals`**, the **precedent_agreement** dimension in the packet signal vector stays default; calibration cannot improve without **non-degenerate outcome labels**.
- **Question** — How do we make the feedback loop **measurable and debuggable** while keeping learning **advisory** and gates **fail-closed**?
- **Answer** — **W0 baseline receipt** (schema, null rates, signals population, lookup behavior) → four implementation waves: **outcome/bind + captured precedent metadata → persisted signals → lookup quality → calibration + join analytics**.

---

## Invariants (non-negotiable)

1. **No gate weakening** — Learning outputs do not **skip** Author-Gate, **reduce** HITL, or **bypass** CI completeness; auto-proceed rules stay governed by **existing** dominance + policy only (no new auto-proceed paths from learned signals).
2. **Additive ledger** — Schema changes are **additive**; no history delete without migration receipt; no destructive ledger migration.
3. **Scope** — Developer-loop Author-Gate and capture tooling only; **out of scope**: `agentic_core/L5` runtime HITL.
4. **Unknown/null/empty evidence** — Must not be treated as **PASS** or **strong**; downgrade to **weak** / **unknown** / **review** per safety laws below.
5. **W3 preserved** — **No `strong` precedent from degraded scope**; degraded paths remain non-strong.
6. **Calibration** — **Min-n** guarded; must **not** train on degenerate labels; degenerate training sets emit **`NOOP_DEGENERATE_LABELS`** (or equivalent explicit NOOP), never a fake calibrated confidence.

---

## Feedback Loop Safety Laws

These laws are **constitutional for this plan**: they bound what feedback machinery may **mean** in the spine. Violating them is **out of charter** even if implementation is easy.

1. **Stored precedent metadata is audit support, not authority** — Fields such as `precedent_match_count`, `precedent_top_match_ids_json`, `precedent_lookup_query_digest`, and capture timestamps exist so operators and CI can **replay and verify**; they **do not** authorize proceed, merge, write, or skip HITL.

2. **`decision_signals` are advisory ranking/eval inputs only** — Signal rows inform humans, analytics, and **non-binding** scoring; they **must not** be read as green-light for bypassing Author-Gate, CI completeness, or policy.

3. **`precedent_agreement` is subordinate** — It **cannot** override Author-Gate packet rules, HITL, CI gates, enforcement policy, or dominance routing. It adjusts **advisory** signal vectors only.

4. **`confidence_calibrated` is not an approval bit** — It **cannot** be used as release/merge/auto-proceed approval. Release and merge remain governed by existing human/process/CI law.

5. **Bind and label hygiene** — Any **missing**, **disputed**, **stale**, or **degenerate** outcome label must **downgrade** learning posture to **weak** / **unknown**; it must **never** justify **`strong`** precedent, **strong** promotion, or **strong** calibration buckets.

6. **Self-match, echo, and duplicate capture** — **Self-match** (same `decision_id`), **same-plan echo**, and **duplicate capture** must be **excluded** from strong lineage or **explicitly reason-coded** (e.g. `SELF_MATCH_EXCLUDED`, `DUPLICATE_SCOPE_COLLAPSED`) so they cannot inflate precedent strength.

7. **Calibration snapshots** — Require **lineage** (query, dataset digest, code version, policy version, timestamp), **min-n**, **label variance**, **staleness guard**, and **degenerate-label NOOP**. Snapshots without sufficient evidence **must not** silently pass as trained.

8. **Writers must be auditable** — Every **new signal writer** must emit **replay/audit refs** (e.g. digest, policy version, source ref) or **fail closed** (no silent empty PASS): missing refs → missing proof → gate/test failure.

---

## Wave Progress

| Wave | Phase IDs | Focus | Est. Tokens | Status | Success Criteria |
|------|-----------|-------|-------------|--------|------------------|
| W0 | W0.1–W0.3 | Baseline ledger / schema / lookup signal inventory | ~8K | ✅ DONE | Baseline artifact proves current schema, null rates, `decision_signals` population, calibration variance, and lookup verdict/reason behavior **before** W1; **no** schema or code mutation |
| W1 | W1.1–W1.3 | Outcomes, binds, precedent fields on `decisions` | ~40K | ✅ DONE | W1.1–W1.2 delivered; **W1.3** closed via **read-only null-bind gate** (`tools/governance/w13_null_bind_gate.py`) + receipt (advisory **WARN** on dev ledger — not `FAIL`) |
| W2 | W2.1–W2.2 | `decision_signals` + packet alignment | ~32K | ✅ DONE | Per-option rows with required fields; golden alignment packet↔store↔lookup↔reason |
| W3 | W3.1–W3.2 | Lookup quality + reason taxonomy | ~28K | ✅ DONE | Deterministic reason codes; tests for self-match, dedup, degraded, null bind, tie-break, stability |
| W4 | W4.1–W4.2 | Calibration + joins | ~30K | ✅ DONE | Min-n, variance, staleness, leakage guard, disputed handling, `NOOP_DEGENERATE_LABELS`; lineage on snapshots |

---

## Phase Progress

| Phase | Title | Status |
|-------|-------|--------|
| W0.1 | Inspect current SQLite schema and table inventory | ✅ DONE |
| W0.2 | Baseline decision / outcome / signal / calibration counts | ✅ DONE |
| W0.3 | Baseline lookup behavior on frozen sample decisions | ✅ DONE |
| W1.1 | Enrich `decision_outcomes` bind + CI receipt paths | ✅ DONE |
| W1.2 | Persist precedent capture metadata on `decisions` (see W1 acceptance) | ✅ DONE |
| W1.3 | High-churn null/unknown/no-bind **audit gate** (read-only; no ledger mutation) | ✅ DONE — see `w13_null_bind_gate_receipt` in frontmatter |
| W2.1 | Capture hook writes per-option `decision_signal` rows | ✅ DONE |
| W2.2 | Golden packet: signal vector vs store vs lookup vs reason | ✅ DONE |
| W3.1 | `lookup_refactor_decisions`: taxonomy + rank + self-exclude | ✅ DONE |
| W3.2 | Reason-code completeness + stability tests | ✅ DONE |
| W4.1 | Calibrator train/refresh with safeguards + NOOP path | ✅ DONE |
| W4.2 | Join report cadence + dashboard handoff | ✅ DONE |

---

## Wave 0 — Baseline and measurement receipt

WAVE_ID: W0
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: BASELINE

**Purpose** — Turn informal “prior slice” observations into a **durable before/after anchor**. Without W0, W1–W4 can ship without proof of improvement.

**Phases**: W0.1–W0.3 (see Phase Progress).

### W0 acceptance

- Captures **current SQLite schema** (columns + types per table or `PRAGMA`) for **`decisions`**, **`decision_outcomes`**, **`decision_signals`**, and **`decision_calibration_snapshots`**, plus relevant table inventory for the SSOT DB path from `tools.refactor_decisions.ledger_paths.REFACTOR_DECISION_LEDGER_DB`.
- Captures **row counts** and **null / default counts** where applicable for:
  - `decision_outcomes.bind_confidence`
  - `decision_outcomes.ci_receipt_status` (if present)
  - `decisions.precedent_match_count`
  - `decisions.confidence_top`
  - `decisions.confidence_calibrated`
  - (and any W1-planned columns **only as “absent” inventory** — do not add columns in W0)
- Captures whether **`decision_signals`** is **empty vs populated** (row count + optional breakdown by `signal_name` if column exists).
- Captures **calibration variance** summary from `decision_calibration_snapshots` and/or joined `decisions` (e.g. distribution of `confidence_calibrated`, snapshot counts — enough to show degenerate vs varying state).
- Runs **`lookup_refactor_decisions.py`** stdin/stdout on **3–5 representative** `decision_id` / intent / `decision_type` / `repo_area` tuples drawn from the live ledger (or **frozen fixtures** that point at a copied SQLite path) and records **verdict**, **matches**, and any **`reason`** / echo fields emitted.
- Saves a single baseline artifact:

  `artifacts/governance/author_gate_feedback_loop/<timestamp>_w0_baseline.json`

  where `<timestamp>` is UTC `YYYYMMDD_HHMMSS` or ISO-8601 safe for filenames, and the JSON includes schema inventory, counts, null rates, lookup runs, git sha (optional), ledger path, and **explicit note that no mutation occurred in W0**.

- **No schema or code mutation in W0** — read-only inventory + subprocess lookup only; no migrations, no writers, no capture hook edits.

**W0 receipt (latest known in-repo)** — `artifacts/governance/author_gate_feedback_loop/20260517_044326_w0_baseline.json` (re-run `python tools/governance/author_gate_w0_baseline.py` for a fresh `<timestamp>_w0_baseline.json`; filename changes each run). Canonical pointer also in frontmatter `w0_baseline_latest`.

**W1 additive-schema attestation (not a historical ledger migration log)** — `artifacts/governance/migration_receipts/20260517_043100_author_gate_feedback_w1.json` (schema helpers + verifier commands; **does not** claim production ledger was batch-migrated).

## Wave 1 — Outcomes and captured precedent metadata

WAVE_ID: W1
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: A

### W1 acceptance (hardened)

**New `decisions` row persistence at capture** (additive columns as needed; names may map to existing equivalents if already present, but semantics must match):

- `precedent_match_count` — integer count of matches considered **after** filters (self-exclude, dedup, policy).
- `precedent_top_match_ids_json` — JSON array of top-k `decision_id` (ordered, stable tie-break).
- `precedent_lookup_query_digest` — deterministic hash or normalized digest of the **inputs** to lookup (intent, type, repo_area, layer, degraded flags, policy version).
- `precedent_lookup_policy_version` — string tying lookup rules to a **released** policy/commit or schema tag.
- Capture-time timestamp for precedent persistence — **either** dedicated column **or** unambiguous subfield in an existing audit JSON **with** the same durability guarantees as other ledger columns.

**Outcome / bind tier logic** (logical labels; may map to `bind_confidence`, flags, or enums):

- **strong_bind** — Eligible to contribute to **strong**-tier **learning signals only where existing W3 policy already allows**; never bypasses HITL/CI.
- **weak_bind** — Contributes at most **suggestive** / weak learning; never **strong** precedent alone.
- **disputed_bind** — Excluded from strong calibration and strong promotion inputs; must surface in audits.
- **no_bind** — Explicit absence of bind evidence; **never** strong.
- **unknown_bind** — Insufficient evidence; **never** strong; must not be treated as PASS for learning.

**Calibration / label feeding**

- **Disputed / null / unknown** binds **must not** feed **strong** calibration labels or positive strong-precedent training rows.

**Migration discipline** (if new columns):

- Forward migration script (additive `ALTER` or equivalent).
- **Idempotency** check — safe re-run; no double-apply corruption.
- **Schema introspection** test — asserts expected columns exist post-migration.
- **Rollback or downgrade note** — documented operator path (even if “restore from backup”) — **no** silent destructive rollback.
- **Migration receipt path** — `artifacts/governance/migration_receipts/<timestamp>_author_gate_feedback_w1.json` (or plan-consistent path) with files, checksums, verifier command.

**Receipt status (2026-05-17)** — Attestation on disk: `artifacts/governance/migration_receipts/20260517_043100_author_gate_feedback_w1.json`. It documents **code-level** additive migration (`ledger_w1_schema.py`) and pytest verifiers; it **does not** retroactively certify a one-shot DBA migration on a named ledger file.

**Acceptance (summary)**: New captures persist enough **precedent linkage** to audit **without** replaying FTS **as the sole proof**; outcomes use **bind tiers** when evidence exists; CI or gate flags **disputed** binds that must not feed **strong**. **Safety laws** above remain satisfied.

---

## Wave 2 — Decision signals

WAVE_ID: W2
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: B

### W2 acceptance (hardened)

**Row shape** — `decision_signals` rows are **per-option**, not only per-decision (minimum one row per surfaced option that receives a signal vector dimension, or explicit NULL/omit reason row where policy allows).

**Required fields** (additive columns if needed):

| Field | Purpose |
|-------|--------|
| `decision_id` | Parent decision |
| `option_id` or `surfaced_option_key` | Stable key matching packet candidate |
| `signal_name` | e.g. `precedent_agreement`, `verbalized`, … |
| `signal_value` | Numeric or encoded value |
| `signal_source` | e.g. `capture_hook`, `replayed_lookup`, `default_cold_start` |
| `source_ref` | Digest, row id, or path to raw fragment used |
| `policy_version` | Writer policy / schema tag |
| `created_at` | UTC timestamp |

**`precedent_agreement`**

- **Must** be computed from **persisted capture-time matches** where possible (W1 metadata + lookup raw at capture).
- If **lookup replay** is required after capture, set `signal_source = replayed_lookup` and include **replay reason** in `source_ref` or sibling column (additive).

**Golden packet test** (blocking) — single test or suite that compares:

1. Emitted packet **signal vector** (per surfaced option)
2. Stored **`decision_signals`**
3. **Lookup raw** results (or frozen fixture from same digest)
4. **Final lookup reason** string / code list

Allowable drift: none on canonical golden; fixture updates require explicit bump of `policy_version` + receipt.

**Acceptance (summary)**: **`decision_signals`** populated per-option for signal-vector captures; **precedent_agreement** not stuck at default when persisted matches exist; **advisory-only** per Safety Laws.

---

## Wave 3 — Lookup quality

WAVE_ID: W3
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: C

### W3 acceptance (hardened)

**Deterministic reason-code taxonomy** (extend via additive enum only; unknown codes fail closed in CI if emitted):

| Code | Meaning (summary) |
|------|-------------------|
| `SELF_MATCH_EXCLUDED` | Same `decision_id` removed from match set |
| `DUPLICATE_SCOPE_COLLAPSED` | Duplicate/near-duplicate capture collapsed per policy |
| `COLD_CORPUS` | Insufficient corpus for meaningful match |
| `MATCHED_STRONG_BIND` | Top match(es) carry strong-bind tier |
| `MATCHED_WEAK_BIND` | Top match weak-bind tier |
| `MATCHED_DISPUTED_BIND` | Match disputed — cap strength |
| `MATCHED_NO_BIND` | Match row has explicit no-bind |
| `MATCHED_UNKNOWN_BIND` | Bind unknown — cap strength |
| `DEGRADED_SCOPE_NOT_STRONG` | Degraded scope — **never** strong |
| `RECENCY_BOOST_APPLIED` | Deterministic recency adjustment applied |
| `OUTCOME_TIER_BOOST_APPLIED` | Outcome tier adjusted rank |
| `BELOW_THRESHOLD` | Below FTS/score threshold |
| `POLICY_BLOCKED_STRONG` | Policy prevented strong elevation |

**Required tests** (blocking):

- **No self-hit** — same `decision_id` never ranks as own precedent for strong.
- **Duplicate collapse** — duplicates do not multiply strength.
- **Degraded scope** — cannot produce **strong** (existing W3 + Safety Laws).
- **Null / unknown bind** — cannot produce **strong** from those matches alone.
- **Tie-break** — same text / intent with newer decision → **deterministic** ordering.
- **Reason stability** — repeated query with frozen DB + policy version → **identical** reason code set and ordering (or documented acceptable ordering of equivalent codes).

**Acceptance (summary)**: Verdict **`reason`** / codes are **stable**, **human-readable**, and **replayable**; self-hit and echo excluded or coded; **no strong** from degraded scope.

---

## Wave 4 — Calibration and analytics

WAVE_ID: W4
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: D

### W4 acceptance (hardened)

**Calibration safeguards** (all blocking where applicable):

- **Minimum n guard** — refuse train below configured **n**; emit explicit NOOP.
- **Minimum positive and negative label counts** — no all-success or all-failure degenerate fit.
- **Label variance check** — zero variance → **NOOP**.
- **Stale snapshot check** — reject or quarantine training from outdated policy/schema without bump.
- **Training-data leakage check** — document and test that train/eval split or temporal policy prevents trivial leakage (per chosen methodology).
- **Disputed labels** — excluded or **down-weighted** per explicit rule; never silently treated as clean positive.
- **Snapshot lineage** — each snapshot row includes: **query** (or digest), **dataset digest**, **code version** (git sha or tag), **policy version**, **UTC timestamp**.
- **Degenerate labels** — if labels are degenerate, calibration **must** emit **`NOOP_DEGENERATE_LABELS`** (or equivalent) and **must not** emit a fake non-null calibrated confidence that implies a fit occurred.

**Join / analytics**

- `author_gate_learning_join_report` (or successor) remains **advisory**; not a runtime release gate.

**Acceptance (summary)**: Calibration **fails closed** on bad data; **`NOOP_DEGENERATE_LABELS`** path tested; lineage complete; join report runnable with artifact path.

---

## Required Proof Matrix

Concrete module paths (2026-05-17 reconciliation). Use `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` when `-p pytest_timeout` conflicts with autoloaded `pytest-timeout` (duplicate plugin registration).

| Wave | Proof command | Expected artifact | Blocking condition |
|------|---------------|-------------------|-------------------|
| W0 | `python tools/governance/author_gate_w0_baseline.py` | `artifacts/governance/author_gate_feedback_loop/<timestamp>_w0_baseline.json` | Missing schema / count / lookup baseline |
| W1 | `python -m pytest -p pytest_timeout tests/unit/tools/refactor_decisions/ -q --tb=short` | Green (suite) | Bind / precedent / W1–W2 schema tests fail |
| W1 | `python -m pytest -p pytest_timeout tests/unit/tools/refactor_decisions/test_precedent_capture_metadata.py -q --tb=short` | Green | Capture metadata assertions fail |
| W1 | `python -m pytest -p pytest_timeout tests/unit/tools/refactor_decisions/test_author_gate_w1_bind.py -q --tb=short` | Green | Disputed / tier bind behavior fails |
| W1.3 | `python tools/governance/w13_null_bind_gate.py` | `artifacts/governance/author_gate_feedback_loop/<timestamp>_w13_null_bind_gate.json` | `verdict: FAIL` over threshold; **WARN/PASS** are acceptable advisory outcomes for learning hygiene |
| W1.3 | `python -m pytest -p pytest_timeout tests/unit/tools/governance/test_w13_null_bind_gate.py -q --tb=short` | Green | Gate logic regression |
| W2 | `python -m pytest -p pytest_timeout tests/unit/tools/refactor_decisions/test_author_gate_w2_golden_packet.py -q --tb=short` | Green | Packet ↔ store ↔ lookup alignment fails |
| W2 | `python -m pytest -p pytest_timeout tests/unit/tools/refactor_decisions/test_w2_ledger_schema.py -q --tb=short` | Green | `decision_signals` additive schema fails |
| W2 | `python -m pytest -p pytest_timeout tests/unit/windsurf/scripts/test_post_cursor_agent_author_gate_capture.py -q --tb=short` | Green | Capture hook / `precedent_agreement` writer fails |
| W3 | `python -m pytest -p pytest_timeout tests/unit/windsurf/skills/test_lookup_refactor_decisions.py tests/unit/tools/refactor_decisions/test_author_gate_lookup_w3.py -q --tb=short` | Green | Lookup reason taxonomy / stability fails |
| W4 | `python -m pytest -p pytest_timeout tests/unit/ops_scripts/calibration/test_author_gate_learning_join_report.py tests/unit/ops_scripts/calibration/test_calibration_min_n_degenerate.py -q --tb=short` | Green; join `advisory_only`; calibrator NOOP paths | Join or calibrator safeguard regression |
| Final | `python ops_scripts/ci/run_contract_gates.py` | **2026-05-17 run: exit code 1** — log `contract_gates_run_evidence`. **Snapshot graph-layer completeness:** **PASS** (canonical indexed snapshot `adg_indexed_05172026_0055.sqlite`, projection `adg_graph_05172026_0055.sqlite`). **Remaining blocker:** **W4d-4 10C pilot proof-evidence** — mass **P4b** failures: `proof_status=EVIDENCE_PRESENT` but bundle `git_head` **`ef555f5a`** ≠ current **`0fdb5213`** (rebuild proof bundles or staged downgrade per gate text). **Blocks `PLAN_COMPLETE`.** | Any gate failure or undocumented weakening |

## Plan closure status (`PLAN_STATUS: POST_W4_PARTIAL`)

- **W1.3** — **DONE** via read-only **`w13_null_bind_gate`** (`tools/governance/w13_null_bind_gate.py`) + JSON receipt (`w13_null_bind_gate_receipt` in frontmatter). Live ledger result **WARN** (`high_churn_null_bind_count` 9, threshold fail &gt; 25 not tripped). No backfill executed; no waiver.
- **Ledger schema alignment** — **`python .cursor/scripts/apply_ledger_schema.py`** applied **`decision_outcomes.promotion_quarantine_started_at`** additively (see `ledger_schema_alignment_proof` in frontmatter); `decision_outcomes` row count unchanged (11).
- **Ledger integrity** — **Triaged** `dec_4c9f4c38c632`: chronologic first sealed row had **stale `row_hash`** vs current `canonicalize_row` / `compute_row_hash` (genesis `prev_hash` correct); **not** caused by `decision_outcomes` schema alignment. **Remediation:** documented **`python .cursor/scripts/author_gate_ledger_integrity.py --rebuild --confirm`** (`rebuild_chain`) — integrity fields only on `decisions`; row counts preserved (17 decisions, 11 outcomes). Evidence: `ledger_integrity_diagnostic`, `ledger_integrity_repair_receipt`. Sub-gate: **`python ops_scripts/ci/author_gate/check_ledger_integrity.py` → exit 0** (17/17).
- **ADG snapshot graph-layer (§22)** — **Root cause:** `check_snapshot_has_mvs.py` picks **newest mtime** `adg_indexed_*.sqlite` with a `nodes` table; **`adg_indexed_05172026_0107.sqlite`** was **incomplete** (only **4** `mv_*` vs min 30) yet **newer** than the **complete** run **`adg_indexed_05172026_0055.sqlite`** (**69** `mv_*`, projection fresh). **Regen:** `python tools/generate/generate_full_adg.py --force` (canonical path; gate banner `tools/generate_full_adg.py` is shorthand). **Local ordering fix:** refresh **`05172026_0055`** file mtime so the resolver prefers it over **`0107`** until the partial **`0107`** WAL/SQLite can be removed. **Contract-gates sub-gate:** “Snapshot graph-layer completeness gate” **PASS** (see latest `contract_gates_run_evidence`).
- **Final governance proof** — **`run_contract_gates.py` → exit 1** at **W4d-4** (**10C** pilot proof-evidence / **P4b** `git_head` drift vs **`0fdb5213`**). Plan remains **`POST_W4_PARTIAL`** — not **`PLAN_COMPLETE`**.
- **`PLAN_COMPLETE`** prerequisites remaining: (1) **refresh Fort Knox 10C proof bundles** at current **`HEAD`** (or follow gate-approved staged downgrade path)—**out of Author-Gate ledger scope**; (2) **`run_contract_gates.py` exit 0**; (3) DoD-7 signoff only after (2).

---

## Explicit Non-Goals

- **Do not** run **W0** with schema migrations, capture writers, or production ledger edits — baseline is **read-only inventory + lookup replay** only.
- **Do not** make Author-Gate “autonomous approval” smarter in this plan — no ML-based auto-approve.
- **Do not** promote learned precedent into **hard policy** beyond what is already constitutionally encoded.
- **Do not** replace **human approval** with confidence scoring for merge/release/write.
- **Do not** make calibration a **runtime release gate** or **CI merge blocker** unless an existing ADR/plan explicitly authorizes it (this plan does **not**).
- **Do not** alter **`agentic_core` runtime HITL** (`L5` or production safety path).
- **Do not** make **L6 / current-run learning** changes here.
- **Do not** rewrite existing ledger history except **additive** migration / bounded backfill with **migration receipt** and verifier.

---

## Definition of Done

| ID | Criterion | Status |
|----|-----------|--------|
| DoD-1 | Plan file exists at `.cursor/plans/author-gate-feedback-loop-d4e8f1.md` | DONE |
| DoD-2 | Notion Plans row **Not Started** with path + Summary (`page_id` `36227693-f55c-81ab-9145-c41730a4a98b`) | DONE |
| DoD-3 | Each wave ends with **tests or gates** + short receipt in plan or `artifacts/` | DONE — W0 baseline, W1 schema attestation + W1.3 gate, W3/W4 pytest slices, contract-gates evidence path |
| DoD-4 | No Author-Gate or CI gate weakened (diff review) | **Unproven** until `run_contract_gates.py` green; this closure pass **added** audit tooling only |
| DoD-5 | **Feedback Loop Safety Laws** enforced by tests or **static review** with written attestation | PARTIAL — code+tests align; formal gated proof pending **Final** green |
| DoD-6 | **Proof Matrix** concrete paths for W0–W4 + W1.3 + Final | **DONE** for W0–W4 + W1.3; **Final** row documents **failed** run (**10C P4b** bundle `git_head` vs **`0fdb5213`**) |
| DoD-7 | Final diff review confirms **no** Author-Gate / HITL / CI weakening | **OPEN** — needs human reviewer + green `run_contract_gates.py` |
| DoD-8 | Calibration **`NOOP_DEGENERATE_LABELS`** path tested | DONE |
| DoD-9 | Lookup reasons **stable** / tested | DONE |
| DoD-10 | Stored signals **advisory** — code boundaries + plan attestation | DONE (plan laws + W4 join `advisory_only`) |
| DoD-11 | **W0 baseline** exists and is referenced | DONE — `w0_baseline_latest` in frontmatter; rerun changes `<timestamp>` |

---

## Marker Quick Reference

```
WAVE_START: plan=author-gate-feedback-loop-d4e8f1 wave=0
WAVE_COMPLETE: plan=author-gate-feedback-loop-d4e8f1 wave=0 note="<baseline summary>"
WAVE_START: plan=author-gate-feedback-loop-d4e8f1 wave=<N>
WAVE_COMPLETE: plan=author-gate-feedback-loop-d4e8f1 wave=<N> note="<summary>"
PLAN_COMPLETE: plan=author-gate-feedback-loop-d4e8f1 note="<final outcome>"
```
