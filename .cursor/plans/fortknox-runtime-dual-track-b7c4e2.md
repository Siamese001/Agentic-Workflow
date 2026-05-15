---
plan_id: fortknox-runtime-dual-track-b7c4e2
plan_type: governance
touches_agentic_core: false
touches_governance_ci: true
touches_cursor_rules: true
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
hardened: false
hardening_round: 0
status: Not Started
---

# Fort Knox + runtime signoff — dual-track governance (keep / clarify / wire)

One-sentence summary: **Keep Fort Knox as tamper-evident certification (notary) for RTC-REQ status; make runtime proof an explicit, cheap, documented second track** so agents and humans never confuse “bundle green” with “seam ran.”

> **plan_id discipline**: filename stem `fortknox-runtime-dual-track-b7c4e2` matches `plan_id` and Notion `Slug`. Wave markers: `plan=fortknox-runtime-dual-track-b7c4e2`.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: TODO
CURRENT_WAVE: W0
LAST_COMPLETED_WAVE: NONE
LAST_UPDATED: 2026-05-15

---

## Context (SCQA)

- **Situation** — Fort Knox (compiler + verifier + atomic assertions + mutation rejection + canary) passes in CI; separate work produced **runtime evidence manifests** (e.g. pytest + junit + logs under `docs/reports/runtime_cert/`).
- **Complication** — Fort Knox was introduced partly to compensate for IDE/runtime proof weakness; **passing Fort Knox did not imply runtime correctness**, causing perceived low ROI and scope confusion.
- **Question** — How do we **preserve the integrity value** of Fort Knox while **making runtime signoff explicit, discoverable, and low ceremony**?
- **Answer** — **Dual-track discipline**: (1) *Certification track* = Fort Knox unchanged in role; (2) *Runtime track* = contract tests + command logs + optional small JSON manifests; **documentation + CI clarity + assertion hygiene** in waves below.

---

## Status Tables

### Wave Progress

| Wave | Focus | Status | Tests Added | Files Changed |
|------|-------|--------|-------------|---------------|
| W0 | Narrative SSOT — what Fort Knox is / is not | 🔲 TODO | — | — |
| W1 | CI posture — fail-closed vs advisory Fort Knox gates | 🔲 TODO | — | — |
| W2 | Assertion ledger hygiene — RTC-REQ ↔ high-signal seams | 🔲 TODO | — | — |
| W3 | Runtime evidence template — link + reuse pattern | 🔲 TODO | — | — |
| W4 | Long-term — ADR-091 / in-toto retirement path | 🔲 TODO | — | — |

### Phase Progress

| Phase | Title | Status |
|-------|-------|--------|
| W0.1 | ADR or architecture note: dual-track model | 🔲 TODO |
| W0.2 | AGENTS.md + Fort Knox skill cross-links | 🔲 TODO |
| W1.1 | Inventory `check_fortknox_*` + `run_contract_gates` wiring | 🔲 TODO |
| W1.2 | Document or adjust fail-closed vs advisory policy | 🔲 TODO |
| W2.1 | Audit `certification/evidence_assertions.jsonl` coverage | 🔲 TODO |
| W2.2 | Criteria + checklist for new RTC-REQ assertions | 🔲 TODO |
| W3.1 | Runtime manifest template + example | 🔲 TODO |
| W3.2 | Link template from `fortknox-evidence` SKILL + runtime seam rule | 🔲 TODO |
| W4.1 | ADR-091 alignment note + retirement triggers | 🔲 TODO |

---

## Wave Structure (summary)

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W0 | P0.1–P0.2 | Authoritative prose: Fort Knox = notary; runtime = pytest/logs/manifests | ~2.5k | No CI behavior change yet | Not Started | ADR/arch note merged; AGENTS + skill point to it |
| W1 | P1.1–P1.2 | CI truth table for Fort Knox gates (strict vs advisory) | ~3k | `run_contract_gates.py` is SSOT for gate order | Not Started | Table in repo; optional env to tighten main branch |
| W2 | P2.1–P2.2 | Assertion hygiene: fewer, sharper RTC-REQ rows | ~4k | Compiler/schema unchanged | Not Started | Audit doc + contribution checklist |
| W3 | P3.1–P3.2 | Runtime evidence pack template + cross-links | ~3k | Reuse `docs/reports/runtime_cert/` pattern | Not Started | Template + links; one example migrated |
| W4 | P4.1 | Long-term: in-toto / ADR-091 retirement criteria | ~2k | No vendor commitment | Not Started | Single ADR section or plan appendix |

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| P0.1 | Dual-track architecture note | `docs/architecture/adr/` (new ADR) or `docs/reference/` | Avoid duplicating Fort Knox rule text | ~1.2k | Not Started |
| P0.2 | Discoverability | `AGENTS.md`, `.cursor/skills/fortknox-evidence/SKILL.md`, optional `.cursor/rules/` pointer | Keep short; link to ADR | ~1.3k | Not Started |
| P1.1 | Gate inventory | `ops_scripts/ci/check_fortknox_*.py`, `run_contract_gates.py`, `.github/workflows/*` | Advisory vs strict scattered in headers | ~1.5k | Not Started |
| P1.2 | Policy decision | Same + `docs/` table | Changing fail-closed may affect CI noise | ~1.5k | Not Started |
| P2.1 | Assertion audit | `certification/evidence_assertions.jsonl`, `tools/cert/` | Large file; use scripts not hand edits | ~2k | Not Started |
| P2.2 | Contribution guardrails | `docs/` or `.cursor/skills/` checklist | Balance rigor vs contributor friction | ~2k | Not Started |
| P3.1 | Runtime manifest template | `docs/reports/runtime_cert/README.md` or template dir | Align with `CURSOR_RUNTIME_SEAM` contract | ~1.5k | Not Started |
| P3.2 | Cross-link discipline | `.cursor/skills/fortknox-evidence/SKILL.md`, `.cursor/rules/001-cursor-runtime-seam-execution.mdc` or sibling | Avoid circular SSOT | ~1.5k | Not Started |
| P4.1 | Retirement / evolution | Reference `ADR-091`, constitutional §32 | Speculative; document only | ~2k | Not Started |

---

## Out Of Scope

- Replacing Fort Knox with in-toto **implementation** in this plan (documentation of path only).
- Rewriting all RTC-REQ rows or re-baselining the entire assertion ledger in one wave.
- Notion schema changes beyond standard Plans row for this plan.

---

## Wave 0 — Narrative SSOT (Fort Knox vs runtime)

WAVE_ID: W0
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: A

**Phases**:
- **W0.1** — Author `ADR-NNN-fortknox-runtime-dual-track.md` (or equivalent): definitions, anti-patterns (“Fort Knox proves runtime”), diagram optional | ~1.2k | PHASE_STATUS: TODO
- **W0.2** — `AGENTS.md` short subsection + `fortknox-evidence` SKILL “When not to invoke” / pointer to runtime template | ~1.3k | PHASE_STATUS: TODO

**Acceptance**:
- One canonical doc is citeable in reviews.
- Fort Knox skill opens with **two-sentence role boundary** + link.

---

## Wave 1 — CI posture (truth table)

WAVE_ID: W1
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: B

**Phases**:
- **W1.1** — Inventory each `check_fortknox_*` + where invoked; capture exit semantics (fail-closed vs advisory) | ~1.5k | PHASE_STATUS: TODO
- **W1.2** — Publish **CI truth table** (markdown under `docs/` or `ops_scripts/ci/README`); optionally one gate flip behind env if team agrees | ~1.5k | PHASE_STATUS: TODO

**Acceptance**:
- Table lists gate name, default behavior, env bypass, owner.
- No accidental “everything advisory” without explicit decision recorded.

---

## Wave 2 — Assertion ledger hygiene

WAVE_ID: W2
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: B

**Phases**:
- **W2.1** — Read-only audit: stale / duplicate / low-signal assertions; output `docs/reports/...` or `artifacts/` summary (generated, not hand-edited report.json) | ~2k | PHASE_STATUS: TODO
- **W2.2** — **New assertion checklist**: when to add RTC-REQ row; requirement for paired runtime or static proof path | ~2k | PHASE_STATUS: TODO

**Acceptance**:
- Checklist merged; audit artifact path recorded in plan completion note.

---

## Wave 3 — Runtime evidence template

WAVE_ID: W3
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: C

**Phases**:
- **W3.1** — Template: directory layout, `runtime_signoff_manifest.json` optional schema, pytest+junit+log triad | ~1.5k | PHASE_STATUS: TODO
- **W3.2** — Cross-links: Fort Knox skill → runtime template; runtime seam rule → “certification claims need Fort Knox, not vice versa” | ~1.5k | PHASE_STATUS: TODO

**Acceptance**:
- One existing pack (e.g. apps_rg P3) referenced as **normative example** in template.

---

## Wave 4 — Long-term evolution (ADR-091)

WAVE_ID: W4
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: C

**Phases**:
- **W4.1** — Document retirement triggers: what would allow shrinking Fort Knox (e.g. in-toto replaces compiler) per existing constitutional note | ~2k | PHASE_STATUS: TODO

**Acceptance**:
- Appendix or ADR section linked from W0 ADR.

---

## Gap Register

| ID | Gap | Wave |
|----|-----|------|
| G1 | Contributors confuse Fort Knox PASS with runtime PASS | W0, W3 |
| G2 | Unclear which Fort Knox gates are strict on main | W1 |
| G3 | Assertion ledger grows faster than signal | W2 |
| G4 | No single “runtime signoff pack” template | W3 |
| G5 | No documented off-ramp when industry attestation matures | W4 |

---

## Definition of Done

| DoD ID | Criterion | Verification |
|--------|-----------|--------------|
| DoD-1 | Canonical **dual-track** narrative exists (ADR or equivalent) and is linked from AGENTS and Fort Knox skill | Link check + PR review |
| DoD-2 | **CI truth table** committed: every `check_fortknox_*` + invocation + strict/advisory | Doc path listed in completion note |
| DoD-3 | **Assertion contribution checklist** merged (new rows require paired proof class) | File path in repo |
| DoD-4 | **Runtime evidence template** published and one example referenced | Template path + example path |
| DoD-5 | **Smoke:** `python -m pytest tests/_apps_contract/test_apps_rg_app_payload_consumption.py::test_full_dispatch_succeeds_with_ag2_wiring --override-ini="addopts=" -q` exits **0** (token runtime seam alive after doc-only waves) | Command + exit code in wave note |
| DoD-6 | **Notion** Plans row exists with `Exists On Disk=true`, path `.cursor/plans/fortknox-runtime-dual-track-b7c4e2.md`, Status progressed honestly | Notion page id in completion note |

### Verification vs deferral

| Item | Verify now | Defer |
|------|------------|-------|
| Fort Knox compiler / verifier code changes | No — not required for this plan | Any compiler schema change → separate platform plan |
| in-toto / Sigstore rollout | No | Until ADR-091 execution plan exists |
| Migrating all historical plans to runtime template | No | Incremental per plan |

---

## Risks / Mitigations

| Risk | Mitigation |
|------|------------|
| Over-long ADR nobody reads | One page max; deep detail in SKILL |
| Tightening CI causes churn | W1.2 is explicit decision + env flag |
| Assertion audit becomes blame game | W2.1 is factual inventory + criteria, not retroactive mass delete |

---

## References

- `.cursor/rules/fortknox-certification-discipline.mdc`
- `.cursor/skills/fortknox-evidence/SKILL.md`
- `docs/reports/runtime_cert/apps_rg_p31_p32_runtime/` (example runtime pack)
- Constitutional §32 + ADR-091 (in-toto evolution) as cited in Fort Knox rule
