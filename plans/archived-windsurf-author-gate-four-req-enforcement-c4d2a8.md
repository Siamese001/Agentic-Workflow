---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\author-gate-four-req-enforcement-c4d2a8.md'
original_relative_path: 'author-gate-four-req-enforcement-c4d2a8.md'
source_sha256: a186ac20a975b3c55cdfb269c9af17ba5394976992da8bb6ed6bb8f33b21116d
recovered_status: SURVIVED_IN_CURRENT
last_commit: '315fd11926d'
last_commit_date: '2026-05-06 06:26:53 -0400'
created_date: '2026-05-03'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: author-gate-four-req-enforcement-c4d2a8
plan_type: governance
---

# Author-Gate Four-Requirement Enforcement

Close the last enforcement gap so every Cascade `ask_user_question` decision-class invocation surfaces compliant Author-Gate options carrying clickable affordance, pros/cons, calibrated confidence, and dominance star.

---

## Context (SCQA)

- **Situation** — The 12-component Author-Gate stack from plan `author-gate-ssot-consolidation-b7c3e1` already enforces three of four requirements end-to-end: clickable surface (`ask_user_question`), confidence prefix (`[confidence=0.NN]` invariant 1), and dominance star (`[RECOMMENDED ⭐ …]` invariants 2+3). Vacuum-closure audit `post_cascade_ask_user_question_packet_audit.py` enforces packet pairing.
- **Complication** — The fourth requirement, **pros/cons** surfaced to the approver, is half-enforced: schema requires `key_tradeoffs ≥2` per surfaced candidate at emit time, but the UI audit only validates the prefix line — not that any tradeoff text reaches the rendered option description. A Cascade composition mistake can drop tradeoffs without any audit firing. Separately, the vacuum-closure runtime audit lacks a CI freshness gate (sibling `check_ui_conformance.py` exists for the UI log but no twin for `ask_user_question_packet_violations.jsonl`).
- **Question** — How do we make the four requirements (clickable / pros-cons / confidence / star) deterministically enforced at emit time, audit time, and CI time?
- **Answer** — Have `emit_packet.py` mint a `surface_description_floor` (confidence prefix + first key-tradeoff snippet) plus an extensible `surface_description`, have `render_card.py` pass the canonical `surface_description` through to `OPTIONS_JSON`, add UI-audit invariant 4 (description must contain a tradeoff segment), and stand up a freshness CI gate watching the vacuum-closure violations log.

---

## Evidence Sources

| Source | Why needed | Status |
|---|---|---|
| `.windsurf/rules/author-gate-enforcement.md` | governing rule — Pipeline step 7 | ✅ read |
| `.windsurf/rules/author-gate-decision-points.md` | §AG-10 option shape contract | ✅ read |
| `.windsurf/schemas/author_gate_packet.schema.json` | canonical SSOT | ✅ read |
| `.windsurf/skills/author-gate-packet-builder/emit_packet.py` | description prefix logic | ✅ read |
| `.windsurf/skills/author-gate-ui-renderer/SKILL.md` + `render_card.py` | UI rendering | ✅ read |
| `.windsurf/scripts/post_cascade_author_gate_ui_audit.py` | invariants 1–3 | ✅ read |
| `.windsurf/scripts/post_cascade_ask_user_question_packet_audit.py` | vacuum-closure | ✅ read |
| `ops_scripts/ci/author_gate/check_ui_conformance.py` | template for new freshness gate | ✅ read |
| `ops_scripts/ci/run_contract_gates.py` | gate registration site | ✅ read |

---

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Pros/cons enforced end-to-end | emit_packet.py, render_card.py, post_cascade_author_gate_ui_audit.py | A | ~6K 🟢 |
| Wave 2 | CI freshness + rule/skill text + tests | new CI gate, rule, SKILL.md, unit tests | B | ~6K 🟢 |

**Total: ~12K tokens across 2 waves, all GREEN**

---

## Out Of Scope

- Decision-density classifier improvements in `post_cascade_ask_user_question_packet_audit.py` (current heuristic is good enough; tuning belongs to a follow-up).
- Calibrator changes (`ops_scripts/calibration/author_gate_calibrator.py`).
- Schema bump beyond adding optional `surface_description` / `surface_description_floor` properties (no breaking change).
- Notion writebacks beyond plan registration + final status update — handled per `notion-plan-wave-deferral.md`.

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| 1.1 | Floor + extensible description in emitter | `.windsurf/skills/author-gate-packet-builder/emit_packet.py` | tradeoff dropped at emit time | ~2K | 🔲 TODO |
| 1.2 | Renderer passes canonical description | `.windsurf/skills/author-gate-ui-renderer/render_card.py` | renderer rebuilt its own desc | ~1K | 🔲 TODO |
| 1.3 | UI audit invariant 4 (description tradeoff segment) | `.windsurf/scripts/post_cascade_author_gate_ui_audit.py` | invariant gap | ~2K | 🔲 TODO |
| 2.1 | New CI gate `check_ask_user_question_packet_freshness.py` + register | `ops_scripts/ci/author_gate/check_ask_user_question_packet_freshness.py`, `ops_scripts/ci/run_contract_gates.py` | vacuum-closure log unwatched in CI | ~2K | 🔲 TODO |
| 2.2 | Rule clarity (Pipeline step 7 enumerates 4 reqs) | `.windsurf/rules/author-gate-enforcement.md` | rule prose ambiguous | ~1K | 🔲 TODO |
| 2.3 | Renderer SKILL.md update | `.windsurf/skills/author-gate-ui-renderer/SKILL.md` | non-recommended-only tradeoff text | ~1K | 🔲 TODO |
| 2.4 | Tests | `tests/unit/windsurf_scripts/test_author_gate_ui_audit.py` (extend) + new test for freshness gate | invariant 4 has no test | ~2K | 🔲 TODO |

---

## Gap Register

**GAP-1: UI audit cannot detect missing tradeoff segment in option descriptions.**
- Schema requires `key_tradeoffs ≥2` per surfaced candidate; emitter validates at emit time. But the rendered `ask_user_question` description currently contains only the `[confidence=0.NN]` prefix — no tradeoff text reaches the approver.
- Impact: a Cascade composition mistake (or any consumer that re-builds descriptions) silently drops the pros/cons signal. UI audit invariants 1–3 still pass.

**GAP-2: Vacuum-closure violations log unwatched in CI.**
- `post_cascade_ask_user_question_packet_audit.py` writes to `artifacts/windsurf/ask_user_question_packet_violations.jsonl` at runtime. No CI gate checks this log for unresolved rows.
- Impact: critical-severity rows ("ask_user_question + no packet + high decision-density") accumulate unnoticed.

**GAP-3: Rule prose ambiguous about all four requirements.**
- `author-gate-enforcement.md` Pipeline step 7 mentions confidence + star but does not enumerate the four canonical requirements together.
- Impact: future authors / Cascade sessions treat the four as ambient rather than load-bearing.

---

## Execution Plan

### Wave 1 — Close the Pros/Cons Enforcement Gap

#### Phase 1.1 — emit_packet.py: floor + extensible description

**Scope**: `_attach_signal_vectors` site (post-routing block). Add per-surfaced-option fields:

- `surface_description_floor` = `[confidence=0.NN] · trade-off: <key_tradeoffs[0][:80]>` (or `[RECOMMENDED ⭐ confidence=0.NN] · trade-off: …` when dominance fires).
- `surface_description` = same as floor by default. Designated as the canonical text the renderer should pass to `ask_user_question`. Extensible by callers via spec.

Keep `surface_description_prefix` field for back-compat with consumers reading the old contract.

**Acceptance**: Emit a sample packet via `python emit_packet.py --no-precedent` from a fixture; assert the surfaced candidate has all three fields populated; assert floor begins with `[` and contains ` · trade-off: `.

#### Phase 1.2 — render_card.py: pass surface_description through

**Scope**: When assembling `OPTIONS_JSON`, prefer `candidate.surface_description` over locally-built description. Fall back to `surface_description_floor` then to `surface_description_prefix` for older packets.

**Acceptance**: Pipe a sample packet through `render_card.py`; parse `OPTIONS_JSON:` line; assert each option's `description` matches its candidate's `surface_description`.

#### Phase 1.3 — UI audit invariant 4

**Scope**: `audit_response` / `_audit_invocation` in `post_cascade_author_gate_ui_audit.py`. Add invariant 4:

- For every surfaced option description, after the `[…]` prefix, look for `· trade-off:` followed by ≥20 non-whitespace chars. If absent → emit violation `description_missing_tradeoff` with option index.
- Bypass already covered by `AUTHOR_GATE_UI_BYPASS=1`.

**Acceptance**: Synthetic responses (one with tradeoff segment, one without) round-trip through `audit_response`; first emits zero rows, second emits one `description_missing_tradeoff` row.

### Wave 2 — Wire Freshness Gate, Rule, Skill, Tests

#### Phase 2.1 — New CI freshness gate

**Scope**: Create `ops_scripts/ci/author_gate/check_ask_user_question_packet_freshness.py` mirroring `check_ui_conformance.py` shape. Watches `artifacts/windsurf/ask_user_question_packet_violations.jsonl`. Bypass: `ASK_PACKET_AUDIT_FRESHNESS_BYPASS=1`. Staleness window: 7 days (env override `ASK_PACKET_STALENESS_DAYS`).

Register in `ops_scripts/ci/run_contract_gates.py` after `check_ledger_integrity` in the author_gate group.

**Acceptance**: Run gate against synthetic JSONL fixtures (empty → 0; recent unresolved row → 1; only bypass rows → 0; aged rows → 0). Run `run_contract_gates.py` end-to-end and confirm new entry runs without exploding the suite.

#### Phase 2.2 — Rule update

**Scope**: `.windsurf/rules/author-gate-enforcement.md` Pipeline step 7. Replace single-paragraph step 7 with explicit four-requirement table mapping each requirement to its UI-audit invariant.

**Acceptance**: Rule diff names all four requirements with cross-refs to invariants 1–4 and to the `ask_user_question_packet_audit` vacuum-closure.

#### Phase 2.3 — Renderer SKILL.md update

**Scope**: `.windsurf/skills/author-gate-ui-renderer/SKILL.md` — make the tradeoff segment universal (currently described for non-recommended only). Add explicit reference to `surface_description` field as the canonical wire format.

**Acceptance**: SKILL.md prescribes `surface_description` as the source for option descriptions; pros/cons mandate covers recommended + non-recommended.

#### Phase 2.4 — Tests

**Scope**: 
- `tests/unit/windsurf_scripts/test_author_gate_ui_audit.py` — extend (or create) with at least 4 cases covering invariant 4: tradeoff present (clean), tradeoff missing (violation), tradeoff present but <20 chars (violation), description without prefix (caught by invariant 1, not 4).
- `tests/unit/ops_scripts_ci/test_check_ask_user_question_packet_freshness.py` — new file, ≥4 cases mirroring `test_check_ui_conformance.py` shape.

**Acceptance**: All new tests pass under `pytest tests/unit/windsurf_scripts/test_author_gate_ui_audit.py tests/unit/ops_scripts_ci/test_check_ask_user_question_packet_freshness.py -v`. Existing UI audit test suite still passes (no regression).

---

## Rules

- No subprocess/shell anywhere; pure stdlib + jsonschema (already imported).
- All file edits are minimal and append-only on `surface_description*` fields — no breaking schema change.
- Bypass envs documented at every new enforcement point (`AUTHOR_GATE_UI_BYPASS`, `ASK_PACKET_AUDIT_FRESHNESS_BYPASS`).
- `notion-plan-wave-deferral.md` honored: zero Notion writes between W1.start and W2 final test pass.

---

## Success Criteria

- [ ] Sample packet via `emit_packet.py` carries `surface_description_floor` + `surface_description` + legacy `surface_description_prefix` on every surfaced candidate.
- [ ] `render_card.py` `OPTIONS_JSON` description equals `candidate.surface_description`.
- [ ] UI audit emits `description_missing_tradeoff` for synthetic response without tradeoff segment, zero rows for compliant response.
- [ ] New CI gate runs in `run_contract_gates.py` author-gate group without errors.
- [ ] Rule + SKILL prose unambiguously enumerate the four requirements.
- [ ] All new tests pass; no regression in existing Author-Gate test suite.

---

## Rollback Strategy

If anything goes wrong mid-wave:
1. Revert the modified files via `git checkout -- <path>`.
2. The vacuum-closure audits remain advisory (`fail-open`); revert never breaks the response chain.
3. Worst case, set `AUTHOR_GATE_UI_BYPASS=1` and `ASK_PACKET_AUDIT_FRESHNESS_BYPASS=1` in CI to neutralize until repair lands.

---

## Acceptance Criteria

| Metric | Target | Verification |
|---|---|---|
| UI audit invariants enforced | 4 (was 3) | unit tests + grep for invariant labels |
| CI gates in author_gate group | 5 (was 4) | `run_contract_gates.py` listing |
| Pros/cons reach approver | 100% of surfaced options | sample packet emit + render |
| Test count delta | ≥8 new tests | pytest collect |
