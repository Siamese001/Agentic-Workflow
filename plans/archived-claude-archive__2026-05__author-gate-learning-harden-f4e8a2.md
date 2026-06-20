---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\2026-05\\author-gate-learning-harden-f4e8a2.md'
original_relative_path: '_archive\\2026-05\\author-gate-learning-harden-f4e8a2.md'
source_sha256: b4166d3ef1ca32a0a8f45bcc89341dafef3071d8c334e0672bc0b83b0231a858
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: author-gate-learning-harden-f4e8a2
plan_type: governance
touches_agentic_core: false
touches_governance_ci: true
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: true
---

# Author-Gate system learning — hardening roadmap

Prioritized waves to harden the Author-Gate learning loop (precedent lookup, outcome binding, pattern promotion, and calibration) **without** weakening gates. **Delivered** — waves W1–W5 executed; Notion Plans row **Completed** (aligned 2026-05-16).

> **plan_id**: `author-gate-learning-harden-f4e8a2` — use `plan=author-gate-learning-harden-f4e8a2` in lifecycle markers.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: COMPLETED
CURRENT_WAVE: W5
LAST_COMPLETED_WAVE: W5
LAST_UPDATED: 2026-05-16

---

## Context (SCQA)

- **Situation** — Author-Gate captures decisions in `refactor_decision_ledger.sqlite`, binds outcomes to git activity, promotes repeated clean precedents, and feeds `emit_packet` / `lookup_refactor_decisions.py`. CI already includes ledger hash-chain, precedent usage, promotion parity, outcome coverage, and AG v2 completeness checks.
- **Complication** — Outcome labels can be noisy; commit-to-decision binding uses file overlap; FTS precedent can misfire across areas; `.cursor` vs `.windsurf` ledger paths can diverge; promotion can strengthen too fast on thin evidence; `ask_user_question` calibration and refactor outcomes are not automatically joined.
- **Question** — How do we harden learning-signal quality and operational resilience while keeping Author-Gate fail-closed and auditable?
- **Answer** — Deliver truthier outcomes and bindings first, then SSOT and scope-safe precedent, then abuse/integrity observability, then unified calibration reporting.

---

## Non-Negotiable Hardening Invariants

1. **Advisory unless policy-bound** — Author-Gate **learning signals** (precedent lookup results, promoted patterns, option confidence scores, calibration reports, join analytics) are **advisory** for humans and tools. They become **operationally binding** only where **deterministic governance policy** already consumes them (e.g. schema-valid packets, documented CI gates, hash-chain verification). This plan does **not** authorize silent “model decides” shortcuts.

2. **No gate weakening** — Learned precedent, promoted patterns, confidence scores, and calibration outputs **must never** be used to **reduce**, **skip**, **downgrade**, or **bypass** developer-loop **HITL**, plan **Definition of Done**, **Author-Gate** capture or completeness rules, or **governance CI**. If a change appears to do so, it is **out of charter** and must be reverted or split to a separate, explicitly authorized policy change (not this roadmap).

3. **Additive ledger discipline** — Schema and writer changes stay **additive** and **no-history-delete** except under an explicit migration receipt and review; conflicting readers/writers are a **BLOCK** until reconciled.

4. **Scope boundary** — This plan touches **developer-loop** Author-Gate learning only; it does **not** alter runtime production HITL under `agentic_core/L5_safety/` or constitutional **policy triggers** for when Author-Gate fires.

---

## Fail-closed behavior (learning path)

If implementation consults learning or binding pipelines, the following conditions **must not** collapse to silent **ALLOW** on learning alone. They resolve to **REVIEW** (operator attention, degraded labels, no strengthening) or **BLOCK** (stop promotion / stop strong injection / fail CI per wave design):

| Condition | Posture |
|-----------|---------|
| Missing **CI artifacts** when a CI receipt is required for the tier | **REVIEW** — cap tier at **medium** or lower; **no** auto-promotion; outcome labeling **undecided** or **blocked** until receipt exists |
| Missing **ledger rows** where governance expects a captured decision | **BLOCK** / **REVIEW** per existing Author-Gate completeness gates; **no** precedent-based auto-proceed |
| **Stale ADG snapshot** when ADG-scoped matching was required | **REVIEW** — explicit **degraded** flag; path-prefix-only fallback **without** new **`strong`**; refresh or **BLOCK** ADG-dependent promotion |
| **Schema mismatch** between learning writers and readers | **BLOCK** promotion and tier upgrades until schema version reconciles |
| **Ambiguous commit binding** (multiple candidates, weak overlap, skew) | **REVIEW** — classify **low** or **disputed**; **exclude** from automatic promotion |

---

## Bind confidence classification (W1 contract)

| Tier | Rules |
|------|--------|
| **high** | Commit touches files captured in **decision context/scope** **and** a **CI receipt** exists for that commit **and** timestamp inside configured binding window **and** a **single** unambiguous decision candidate |
| **medium** | File overlap **and** timestamp inside window **and** (**CI receipt missing** or **partial**) **and** otherwise unambiguous candidate |
| **low** | Weak overlap **or** subject/body inference **or** **multiple** plausible candidates **or** overlap outside narrow scope |
| **disputed** | Operator override **or** **conflicting** CI vs inferred outcome **or** contradictory evidence on the same bind |

---

## Promotion eligibility

- Only **high**-confidence binds may feed **automatic** promotion (e.g. scripts that set or escalate `promote_to_pattern` / injectable strength).
- **medium** binds may appear in **reports** but **must not** strengthen injectable precedent **unless** upgraded to high-equivalent via **complete** CI/outcome corroboration recorded on the row.
- **low** and **disputed** binds are **excluded** from automatic promotion inputs.
- **low-confidence**, **disputed**, **stale**, or **degraded** precedent paths **must never** yield a **`strong`** verdict.

---

## Promotion quarantine

- New promotions start as **candidate / weak** for **≥ one full reporting cycle** before influencing anything beyond **none** / advisory text.
- Escalation toward **`suggestive`** or **`strong`** requires passing **audit sampling** with **no** open **disputed** binds on the pattern.
- A **later disputed bind** tied to a promoted pattern **demotes** it to **review-only** or **weak** until **revalidated** with **high**-tier evidence and a clean audit pass.

---

## Status Tables

### Wave Progress

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1 | W1.1–W1.3 | Outcome truth + bind fidelity | ~45K | CI artifacts may be missing; triggers **REVIEW** not silent allow | ✅ DONE | Tiers + receipts per spec; fail-closed when evidence incomplete |
| W2 | W2.1–W2.2 | Single ledger SSOT + drift | ~25K | `.cursor` path is canonical unless proven otherwise | ✅ DONE | Writes only under `.cursor` SSOT; `.windsurf` mirror read-only if needed; CI fails on post-migration legacy writers; drift detected |
| W3 | W3.1–W3.3 | Scoped precedent + promotion | ~40K | ADG snapshot or path prefixes usable | ✅ DONE | Eligibility + quarantine rules satisfied; `strong` only after audit; stale/degraded paths never yield `strong` |
| W4 | W4.1–W4.2 | Integrity + anomaly signals | ~30K | Logs directory writable | ✅ DONE | Anomaly jsonl or gate; bypass rate visible; documented recovery |
| W5 | W5.1–W5.2 | Calibration join + ops | ~25K | Both ledgers readable | ✅ DONE | Report joins selected option → outcome_label; SLA for unbound surfaced decisions |

### Phase Progress

| Phase | Title | Status |
|-------|-------|--------|
| W1.1 | Execution receipt + bind confidence model | ✅ DONE |
| W1.2 | Enrich outcome labels from CI / artifacts | ✅ DONE |
| W1.3 | Dispute / low-confidence bind path | ✅ DONE |
| W2.1 | Canonical path migration + doc | ✅ DONE |
| W2.2 | CI drift check (cursor vs windsurf / mirror) | ✅ DONE |
| W3.1 | Intent + `repo_area` + layer scope guards in lookup | ✅ DONE |
| W3.2 | Promotion floors (N, recency decay, similarity) | ✅ DONE |
| W3.3 | Audit sample of `promote_to_pattern` rows | ✅ DONE |
| W4.1 | Anomaly heuristics (spikes, backdated rows) | ✅ DONE |
| W4.2 | Bypass / resign rate dashboard or jsonl rollup | ✅ DONE |
| W5.1 | Join report: AG ledger × ask_user_question × outcomes | ✅ DONE |
| W5.2 | SLAs + runbook for capture/outcome gaps | ✅ DONE |

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| W1.1 | Execution receipt + bind confidence | `post_commit_outcome_binder.py`, ledger schema?, capture hooks | Overlap-only binds too assertive | ~15K | ✅ DONE |
| W1.2 | CI-linked outcome labels | `post_commit_outcome_binder.py`, CI artifact paths | Subject-line inference insufficient | ~15K | ✅ DONE |
| W1.3 | Dispute / manual reconcile | New small tool or ledger flags | No human override for bad bind | ~15K | ✅ DONE |
| W2.1 | Ledger SSOT (bias `.cursor`) | `tools/cursor/migrate_*`, path inventory, legacy readers | `.windsurf` must not remain writable SSOT post-migration | ~12K | ✅ DONE |
| W2.2 | Drift CI gate | `ops_scripts/ci/` | Writers still targeting legacy path | ~13K | ✅ DONE |
| W3.1 | Scoped precedent | `lookup_refactor_decisions.py`, `precedent_injector.py`, `emit_packet.py` | FTS false positives | ~15K | ✅ DONE |
| W3.2 | Promotion guards | `promote_author_gate_patterns.py` | Too-fast `strong` | ~12K | ✅ DONE |
| W3.3 | Promotion audit sample | Ops script or manual checklist | Stale wrong patterns | ~13K | ✅ DONE |
| W4.1 | Anomaly detection | `ops_scripts/ci` or `tools/capture` | Ledger tampering / mistakes | ~15K | ✅ DONE |
| W4.2 | Bypass observability | Aggregate existing `*_bypass.jsonl` | Invisible weakening | ~15K | ✅ DONE |
| W5.1 | Calibration join report | `ops_scripts/calibration/` | Split learning signals | ~12K | ✅ DONE |
| W5.2 | SLA + runbook | `docs/` or `AGENTS.md` pointer | Capture outages | ~13K | ✅ DONE |

---

## Out Of Scope

- Changing constitutional Author-Gate **policy** triggers (what requires HITL) unless a wave discovers a concrete defect.
- Runtime production HITL (`agentic_core/L5_safety/`) — developer-loop only.
- Neural or external hosted “model training” — this plan stays deterministic ledger + CI.

---

## Wave 1 — Outcome truth and bind fidelity

WAVE_ID: W1
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: A

**Phases**: W1.1–W1.3 (see Phase Progress).

**Acceptance**:
- Binds carry **confidence tier** **high / medium / low / disputed** per **Bind confidence classification**; schema or sidecar stores tier + rationale.
- **Outcome_label** prefers **CI-derived** success/fail when a **CI receipt** exists; missing receipt forces **REVIEW** posture (no promotion from that row alone).
- Operators can mark a bind **disputed** without deleting history; **disputed** excludes automatic promotion and forces quarantine review for any linked pattern.
- Rows matching **Fail-closed behavior** never strengthen precedent.

---

## Wave 2 — Ledger single SSOT and drift detection

WAVE_ID: W2
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: B

**Phases**: W2.1–W2.2.

**Acceptance**:
- **Canonical writable SSOT** is **`.cursor/state/refactor_decisions/refactor_decision_ledger.sqlite`** unless repo-wide evidence demonstrates another path is still authoritative (none expected today—re-verify during W2.1).
- **`.windsurf/state/.../refactor_decision_ledger.sqlite`** may remain a **read-only mirror** only if compatibility requires; enumerate exceptions in the path inventory.
- After the migration window, any **writer** still targeting the legacy path is a **CI defect** (W2.2 fail-closed).
- CI detects **drift** (row counts, hashes, or last-write) between mirror and SSOT per configured **strictness**.

---

## Wave 3 — Scoped precedent and promotion discipline

WAVE_ID: W3
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: C

**Phases**: W3.1–W3.3.

**Acceptance**:
- Lookup respects **Promotion eligibility** and **Promotion quarantine**; **`strong`** never originates from low/disputed/stale/degraded paths.
- `promote_author_gate_patterns` (or successor) consumes **high** binds only for automatic strengthen; **medium** only after documented CI corroboration.
- **minimum N**, **recency decay**, **candidate/weak** cycle, and **audit sampling** gates are implemented and evidenced per **Required Evidence Artifacts**.

---

## Wave 4 — Integrity and abuse resistance

WAVE_ID: W4
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: D

**Phases**: W4.1–W4.2.

**Acceptance**:
- Anomaly signals (e.g. spike in `strong`, identical intents, impossible timestamps) **logged or gated**.
- Bypass/resign frequency **rolled up** for operator review.

---

## Wave 5 — Calibration join and operations

WAVE_ID: W5
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: E

**Phases**: W5.1–W5.2.

**Acceptance**:
- Report correlates **selected option** / recommendation with **`outcome_label`** (and optional ask-user-question acceptance).
- Documented **SLA** for surfaced-but-unbound decisions and capture-failure runbook.

---

## Required Evidence Artifacts

| Wave | Artifact | Purpose |
|------|-----------|---------|
| W1 | Bind confidence **report** (JSON and/or MD summary) | Auditable tier distribution + disputed/low counts |
| W1 | **Migration receipt** (additive schema / flags) | Proves no-history-delete and version bump |
| W1 | **CI-derived outcome sample** (redacted log or fixture path) | Proves labeling prefers receipt over heuristics |
| W2 | **Canonical path inventory** (MD/JSON in-repo) | Lists SSOT, allowed mirrors, forbidden writers |
| W2 | **Migration receipt** (cursor-vs-windsurf completion) | Proves cutover criteria met |
| W2 | **Drift check** output (CI log or saved report) | Evidence mirror vs SSOT parity gate |
| W3 | **Lookup scope test matrix** (table or CSV) | Covers decision_type × repo_area × degraded ADG |
| W3 | **Promotion guard receipt** (script output / gate log) | Shows high-only auto-promote + quarantine |
| W3 | **Audit sample report** | Sampling method + pass/fail for promoted rows |
| W4 | **Anomaly rollup** (JSONL and/or MD digest) | Spike / impossible timestamp / duplicate intent signals |
| W4 | **Bypass / resign summary** | Rolled up operator visibility |
| W5 | **Joined calibration report** | Links selection, optional ask_user_question telemetry, outcome |
| W5 | **SLA + runbook** (single MD under `docs/` or linked) | Capture outage and unbound surfaced decision handling |

---

## Gap Register

**GAP-1: Schema migrations** — W1.1/W1.3 may need additive SQLite columns; must follow additive-only ledger discipline.

**GAP-2: NOTION_TOKEN** — Notion row creation requires env; plan file remains SSOT if API unavailable.

**GAP-3: ADG availability** — If snapshot is **stale** when ADG scope is required, follow **Fail-closed behavior** (**REVIEW**/**BLOCK**, degraded flag, **no** new **`strong`**); path-prefix fallback is explicitly **non-strong**.

---

## W1 — First implementation wave test expectations

_W1 delivered; below remains the acceptance test bar for the bind / outcome path:_

| Area | Expectation |
|------|-------------|
| Bind tiering | **Unit tests** for **high / medium / low / disputed** classification |
| Promotion feed | **Regression tests** asserting **low** and **disputed** rows **never** enqueue automatic promotion |
| CI receipt | Tests for **CI artifact parsing** (happy path, missing file, partial payload) |
| Migration | **No-history-delete** migration test (additive columns only; verify prior rows intact) |
| Regression smoke | Command proving **existing Author-Gate / ledger CI checks** still pass unchanged (e.g. hash-chain / completeness gates as applicable) |

---

## Definition of Done

_Planning DoD satisfied with W1–W5 execution (`dod_exempt: true` retained for historical charter); wave acceptance evidenced in repo (CI, scripts, docs)._

| ID | Criterion | Status |
|----|-----------|--------|
| PDoD-1 | Plan file at `.cursor/plans/author-gate-learning-harden-f4e8a2.md` | DONE |
| PDoD-2 | Notion Plans row **Completed**, path populated | DONE |
| PDoD-3 | Wave order matches prioritized risk (bind truth → SSOT → precedent → integrity → calibration) | DONE |
| PDoD-4 | Out-of-scope and gap register reviewed by executor before W1 | DONE |
| PDoD-5 | Executable smoke/CI coverage added across waves (contract gates + unit tests per wave) | DONE |

---

## Marker Quick Reference

```
WAVE_START: plan=author-gate-learning-harden-f4e8a2 wave=<N>
WAVE_COMPLETE: plan=author-gate-learning-harden-f4e8a2 wave=<N> note="<summary>"
PLAN_COMPLETE: plan=author-gate-learning-harden-f4e8a2 note="<final outcome>"
```
