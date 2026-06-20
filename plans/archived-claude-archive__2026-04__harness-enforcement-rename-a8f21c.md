---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\2026-04\\harness-enforcement-rename-a8f21c.md'
original_relative_path: '_archive\\2026-04\\harness-enforcement-rename-a8f21c.md'
source_sha256: e188cf04b7ce3fe4cf2d90f07a3fef30fa4ffe67b1c07bd6f7fcfb57e4d1b271
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: harness-enforcement-rename-a8f21c
plan_type: governance
---

# Harness Enforcement Rename & Build Plan

**Plan ID:** `harness-enforcement-rename-a8f21c`
**Type:** T3 (cross-cutting rename + new subsystem)
**Plan type:** governance — this plan governs gates, schemas, CI, and the Author-Gate subsystem itself; it is not a code refactor whose blast radius can be measured against the ADG graph layer. §22 graph-layer-evidence gate opted out via frontmatter.
**Status:** W2 + W3 + W4 + W5 (integrity) + W7.1 (calibration) DELIVERED 2026-04-21; W1 DEFERRED; W3 in shadow-mode bake (flip date 2026-04-28)

**W5 Deliverables (integrity, verified passing):**
- `.windsurf/scripts/author_gate_ledger_integrity.py` — hash-chain lib: `canonicalize_row`, `compute_row_hash`, `verify_chain`, `backfill_chain`, `ensure_row_hash`
- `.windsurf/scripts/post_cascade_author_gate_capture.py` — calls `ensure_row_hash` after every commit (fail-open)
- `ops_scripts/ci/author_gate/check_ledger_integrity.py` — CI gate (PASS: 35/35 rows verified)
- `ops_scripts/ci/run_contract_gates.py` — integrity gate wired after schema + coverage
- `.github/workflows/author-gate-gates.yml` — integrity step added between coverage and binder dry-run
- Backfill run: 35 pre-W5 rows sealed into genesis chain
- Tamper test: verified — modifying one row detects exactly-that-row break

**W7.1 Deliverable (calibration report):**
- `.windsurf/scripts/generate_calibration_report.py` — weekly metrics emitter with flip-readiness recommendation (GO/HOLD/INVESTIGATE)
- `.windsurf/workflows/author-gate-calibration-report.md` — `/author-gate-calibration-report` slash command + 2026-04-28 flip-day playbook
- `docs/reports/author-gate/2026-W17.md` — first report auto-generated; UTF-8 clean
- Current week signal: HOLD (only 1 shadow event; FP estimate too noisy for flip decision yet — expected mid-bake)

**W4 Deliverables (verified passing):**
- `.windsurf/skills/author-gate-packet-builder/SKILL.md` — progressive-disclosure entry with HITL-10 + didactic-field spec
- `.windsurf/skills/author-gate-packet-builder/packet_template.md` — full HITL-10 + didactic rules + gold-star convention
- `.windsurf/skills/author-gate-packet-builder/emit_packet.py` — builder with routing, schema validation, precedent injection, `is_recommended`/`surface_label`/`surface_description_prefix` gold-star fields
- `.windsurf/skills/author-gate-packet-builder/precedent_injector.py` — wrapper over refactor-decision-memory lookup
- `.windsurf/rules/author-gate-enforcement.md` — terminology note + gold-star `ask_user_question` convention added

**W4 Exit Criteria (all met):**
- ✅ Emits `AUTHOR_GATE_PACKET:` (canonical) + `HITL_PACKET:` (legacy alias) JSON blocks
- ✅ Dominance routing verified (0.88 with 0.27 gap → alternative suppressed)
- ✅ Gold-star marking verified (recommended option has `⭐ Recommended — ` label + `[RECOMMENDED ⭐ confidence=0.88]` prefix; non-recommended has `[confidence=0.NN]` prefix)
- ✅ Policy snapshot (SHA of rule file) stamped on every packet
- ✅ Context fingerprint matches pre_author_gate fingerprint algorithm (bidirectional correlation works)
- ✅ Strict validation rejects missing didactic fields
- ✅ Terminology disambiguated — Author-Gate Decision (developer loop) vs Runtime Author-Gate (v30 step [5], ADR-023)

**Bonus — Notion map fix (not in original plan but requested):**
- `config/notion_databases.yaml` — added `database_id` (write parent) alongside `id` (data source / reads) for all 8 DBs
- `.windsurf/scripts/sync_mcp_config.py` — `generate_notion_map_block` emits both columns + write pattern guidance
- `AGENTS.md` Notion Workspace Map — regenerated with two-ID column

**W3 Deliverables (verified passing):**
- `.windsurf/schemas/author_gate_triggers.yaml` — 10 triggers, 5 bypass conditions, shadow-mode launch config
- `.windsurf/scripts/pre_author_gate.py` — gate script with tier router, bypass, deny-and-continue
- `.windsurf/hooks.json` — wired as first pre_write_code hook
- `artifacts/windsurf/hitl_violations.jsonl` — event stream (shadow-mode warnings)
- `artifacts/windsurf/hitl_session_state.json` — denial counters per session

**W3 Launch posture: SHADOW MODE**
- `enforcement: shadow` in triggers.yaml — warns only, never exits 2
- Rationale: current session already matches 3 triggers; switching to `block` mid-session would break ongoing work
- Promotion criteria (per triggers.yaml `defaults.shadow_min_days: 7`): run ≥7 days, verify false-positive rate <5% in `hitl_violations.jsonl`, then flip to `block`
- Promotion procedure: edit triggers.yaml → `enforcement: block` → commit

**W3 Integration complete:**
- ✅ `run_contract_gates.py` calls both author_gate checks
- ✅ `.pre-commit-config.yaml` T6d entry for ledger schema
- ✅ `.github/workflows/author-gate-gates.yml` (peer of adg-ci-gates.yml)
- ✅ Git post-commit hook installed via `install_git_hooks.py`
- ✅ `hooks.json` pre_write_code wires `pre_author_gate.py` first

**W2 Deliverables (verified passing):**
- `.windsurf/schemas/decision_ledger.schema.sql` — canonical DDL (SSOT)
- `.windsurf/schemas/decision_record.schema.json` — JSON schema for packet validation
- `.windsurf/scripts/apply_ledger_schema.py` — idempotent migrator (18 additive columns applied)
- `.windsurf/scripts/post_commit_outcome_binder.py` — outcome binder (standalone/--head/--dry-run)
- `ops_scripts/ci/author_gate/check_ledger_schema.py` — drift gate (PASS)
- `ops_scripts/ci/author_gate/check_outcome_coverage.py` — coverage gate with baseline ratchet (PASS @ baseline=1)
- `ops_scripts/ci/author_gate/baselines/outcome_coverage_baseline.json` — ratchet SSOT

**W2 Exit Criteria (all met):**
- ✅ Existing ledger rows revalidate against new schema
- ✅ Migrator idempotent (second run = "up-to-date")
- ✅ Binder operational (dry-run returns 0 with structured match logic)
- ✅ Both CI gates exit 0 on current state

**W2 Remaining hook integration (deferred to W3 co-ship):**
- Git post-commit hook to invoke `post_commit_outcome_binder.py --head`
- Wire `check_ledger_schema.py` + `check_outcome_coverage.py` into `run_contract_gates.py` and `.github/workflows/author-gate-gates.yml`
- Pre-commit entry for `check_ledger_schema.py`
**Depends on:** none
**Siblings:** `runtime-hitl-exit-control-c4e7b3.md`

---

## Context & Motivation

Prior design work (conversations 2026-04-21 T03:24–04:33) produced a detailed plan labeled
"Author-Gate enforcement" covering gating of Cascade-authored code changes, decision ledger,
precedent lookup, and outcome binding. Web research + review of
`@docs/reference/_notes/agentic_process_mapping_v34.md` step [5] established that this is **not**
runtime Author-Gate. It is **harness enforcement** in Martin Fowler's taxonomy — the developer-loop
/ author-side gate that sits outside the v30 runtime system entirely.

Runtime Author-Gate (v30 step [5] ESCALATE) is a distinct subsystem tracked in the sibling plan
`runtime-hitl-exit-control-c4e7b3.md`.

This plan does two things:

1. **Rename** existing `hitl-*` artifacts in `.windsurf/` to `author-gate-*` / `harness-*`
   naming so the word "Author-Gate" is reserved for the runtime concept.
2. **Build** the harness enforcement subsystem per the prior design (schemas, triggers, gate,
   packet builder, ledger integrity, outcome binding, CI).

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|-------------------|
| W1 | P1.1–P1.3 | Rename migration (reversible, no behavior change) | ~8k | Grep-safe rename; `validate_hitl_*` scripts kept as back-compat shims | TODO | All existing tests green; `rg -n "hitl-enforcement"` returns only doc refs |
| W2 | P2.1–P2.3 | Schema + outcome binding (close the loop first) | ~18k | SQLite migration path from current `decision_ledger.db` exists | TODO | Existing ledger rows revalidate; post-commit hook populates `execution.*` within 60s |
| W3 | P3.1–P3.3 | Triggers + gate (stop the bleed) | ~15k | `artifacts/adg/*.sqlite` readable for blast-radius queries | TODO | ≥2-file cross-layer edit without active decision → blocked |
| W4 | P4.1–P4.2 | Packet builder skill + audit | ~14k | Skill progressive-disclosure still works after rename | TODO | Every author-gate event produces schema-valid packet; 7-day audit zero-miss |
| W5 | P5.1–P5.2 | Integrity + precedent auto-injection | ~10k | `ed25519` optional (hash-only if no key) | TODO | Ledger tamper detected; precedent appears without manual skill invocation |
| W6 | P6.1–P6.3 | Review patterns + didactic layer | ~12k | "Review & Edit Plan" + "Review Tool Calls" can be emitted by Cascade | TODO | Non-approve/reject patterns available; didactic fields validated |
| W7 | P7.1–P7.3 | Reporting + CI wiring | ~10k | GHA runner available; pre-commit config writable | TODO | Weekly calibration report lands; `author-gate.yml` GHA green |

Token budget status: 🟢 (all waves <20k; total ~87k, well under T3 ceiling)

**Token estimator status:** DIRECTLY OBSERVED (2026-04-21).
Budget SSOT: `python tools/utils/planning/token_estimator.py --budget`
→ `{HARD_MAX_CONTEXT: 262000, SAFE_OPERATING_CAP: 223000, WARNING_THRESHOLD: 197000}`.
Every wave in this plan (8–18k) is <10% of the warning threshold → 🟢 GREEN.
Sum of all waves ~87k is <50% of warning threshold → 🟢 GREEN.

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|----------------|-------------|-------------|--------|
| P1.1 | Rename rules | `.windsurf/rules/hitl-*.md` (5 files) → `author-gate-*.md` / `harness-*.md` | Cross-refs in 50+ files (plans, AGENTS.md, RULES_INDEX.md) | 3k | TODO |
| P1.2 | Rename scripts | `.windsurf/scripts/post_cascade_author_gate_capture.py`, `ops_scripts/ci/validate_hitl_*` | Hook bindings in `.windsurf/hooks.json`; back-compat shims | 3k | TODO |
| P1.3 | Update references | `AGENTS.md`, `RULES_INDEX.md`, `constitutional.md` §17, all plans citing `author-gate-enforcement.md` | Memory graph entities reference old names | 2k | TODO |
| P2.1 | Schema SSOT | `.windsurf/schemas/decision_ledger.schema.sql`, `decision_record.schema.json` | Migration from current schema | 6k | TODO |
| P2.2 | Outcome binder | `.windsurf/scripts/post_commit_outcome_binder.py` + git hook | Commit↔decision matching by fingerprint | 7k | TODO |
| P2.3 | Coverage CI | `ops_scripts/ci/author_gate/check_outcome_coverage.py`, `check_ledger_schema.py` | Baseline file for ratchet | 5k | TODO |
| P3.1 | Trigger SSOT | `.windsurf/schemas/author_gate_triggers.yaml`, `tier_permissions.yaml` | Balanced vs strict default (see prior response) | 4k | TODO |
| P3.2 | Pre-author gate | `.windsurf/scripts/pre_author_gate.py`, `pre_author_tier_router.py`, `pre_author_denial_injector.py` | Session state file; 3/20 denial escalation | 7k | TODO |
| P3.3 | Hook wiring | `.windsurf/hooks.json` patch | Order matters: tier router → denial injector → gate | 4k | TODO |
| P4.1 | Packet builder skill | `.windsurf/skills/author-gate-packet-builder/` (4 files) | Schema-valid emission; precedent injection | 9k | TODO |
| P4.2 | Capture + audit | `post_cascade_author_gate_capture.py` (rewrite), `post_cascade_author_gate_audit.py` (new) | Structured JSON block replaces prose scraping | 5k | TODO |
| P5.1 | Ledger integrity | `.windsurf/scripts/author_gate_ledger_integrity.py`, `ops_scripts/ci/author_gate/check_ledger_integrity.py` | Hash chain; ed25519 optional | 6k | TODO |
| P5.2 | Precedent auto-inject | Modify `.windsurf/scripts/pre_prompt_classifier.py` | Call `lookup_refactor_decisions.py` on refactor-class intent detection | 4k | TODO |
| P6.1 | Review patterns | `.windsurf/rules/author-gate-review-patterns.md`, `author-gate-learning-loop.md` | Review & Edit Plan; Review Tool Calls patterns | 5k | TODO |
| P6.2 | Didactic fields | `packet_template.md` + validator update | `principle_at_stake`, `what_youd_miss`, `what_would_flip` | 4k | TODO |
| P6.3 | Rule promotions | `author-gate-decision-points.md` from `model_decision` → `always_on` | Context window impact | 3k | TODO |
| P7.1 | Workflows | `.windsurf/workflows/author-gate-decision-gate.md` (renamed), `author-gate-ledger-review.md`, `author-gate-calibration-report.md` | Slash command stability | 3k | TODO |
| P7.2 | CI gates | `.github/workflows/author-gate-gates.yml`, pre-commit entries, `run_contract_gates.py` additions | Peer of `adg-ci-gates.yml`, not merged | 4k | TODO |
| P7.3 | Documentation | `docs/guides/AuthorGate_Architecture.md`, `docs/guides/AuthorGate_Decision_Schema.md`, `docs/reports/author-gate/` | Didactic rationale preserved | 3k | TODO |

---

## Rename Map (Exhaustive)

| Old | New | Reason |
|-----|-----|--------|
| `.windsurf/rules/author-gate-enforcement.md` | `.windsurf/rules/author-gate-enforcement.md` | Reserve "Author-Gate" for runtime |
| `.windsurf/rules/author-gate-decision-points.md` | `.windsurf/rules/author-gate-decision-points.md` | Same |
| `.windsurf/rules/author-gate-svp-calibration.md` | `.windsurf/rules/author-gate-svp-calibration.md` | Same |
| `.windsurf/rules/anti-pattern-author-gate.md` | `.windsurf/rules/anti-pattern-author-gate.md` | Same |
| `.windsurf/rules/refactor-decision-memory.md` | **KEEP** — name is accurate | Not a Author-Gate artifact per se |
| `.windsurf/scripts/post_cascade_author_gate_capture.py` | `.windsurf/scripts/post_cascade_author_gate_capture.py` | Same |
| `.windsurf/workflows/author-gate-decision-gate.md` | `.windsurf/workflows/author-gate-decision-gate.md` | Same |
| `.windsurf/workflows/antipattern-author-gate.md` | `.windsurf/workflows/antipattern-author-gate.md` | Same |
| `ops_scripts/ci/validate_hitl_format.py` | **KEEP as shim** — add deprecation warning, new logic in `check_packet_compliance.py` | Back-compat for CI history |
| `ops_scripts/ci/validate_hitl_rules.py` | **KEEP as shim** — same | Back-compat |
| Memory graph entities referencing `Author-Gate*` | Rewrite to `AuthorGate*` | Sync prior conversations |

### Planned new names (W2–W7 deliverables)

- `.windsurf/schemas/decision_ledger.schema.sql` (generic name — correct as-is)
- `.windsurf/schemas/decision_record.schema.json` (generic — correct as-is)
- `.windsurf/schemas/author_gate_triggers.yaml`
- `.windsurf/schemas/tier_permissions.yaml`
- `.windsurf/scripts/pre_author_gate.py`
- `.windsurf/scripts/pre_author_tier_router.py`
- `.windsurf/scripts/pre_author_denial_injector.py`
- `.windsurf/scripts/post_cascade_author_gate_audit.py`
- `.windsurf/scripts/post_commit_outcome_binder.py`
- `.windsurf/scripts/author_gate_ledger_integrity.py`
- `.windsurf/skills/author-gate-packet-builder/` (SKILL.md + 3 helper files)
- `ops_scripts/ci/author_gate/` (new subdir, 6 gate scripts)

---

## Gap Register

| Gap | Owner | Blocker? | Resolution |
|-----|-------|----------|------------|
| `tools/utils/planning/token_estimator.py` estimates UNRESOLVED | plan author | YES for T3 exec | Run estimator before W1 execution |
| ADG snapshot for blast-radius trigger: which field carries layer-crossing? | W3 author | No | Already proven via `adg_nodes_by_file` + layer attr |
| Hash-chain signing key provisioning (ed25519) | W5 author | No | Hash-only default; signing opt-in via `AUTHOR_GATE_SIGNING_KEY` env |
| Memory graph rename cascade — how many entities reference `Author-Gate`? | W1 author | No | Query `mem_search_nodes(query="Author-Gate")` pre-rename; batch update |
| Back-compat shims lifespan | W1 author | No | 90-day deprecation, then delete (constitutional §3) |

---

## Success Criteria (plan-level)

- [ ] Zero references to `hitl-` in `.windsurf/rules/` filenames (runtime plan owns that namespace)
- [ ] `decision_ledger.db` rows 100% validate against `decision_record.schema.json`
- [ ] Every commit that matches a surfaced decision has `execution.*` populated within 60s
- [ ] `pre_author_gate.py` blocks triggers with false-positive rate <5% on 1-week sample
- [ ] Precedent verdict injected into ≥90% of refactor-class packets without manual skill invocation
- [ ] Weekly calibration report published to `docs/reports/author-gate/<week>.md`
- [ ] `author-gate-gates.yml` GHA green for 7 consecutive days
- [ ] Ledger hash chain unbroken (`check_ledger_integrity.py` zero failures)

---

## Rollback

Each wave is a single commit (or tight commit group) with a pre-wave ADG snapshot and a
backup of `decision_ledger.db`. Rollback = `git revert <sha>` + restore DB from
`artifacts/windsurf/backups/decision_ledger_<pre_wave>.db`.

W1 rename is special: keep shim redirect for 90 days so old filenames resolve to new rules.
