---
plan_id: governance-dedup-closeout-e8a4c2
plan_type: governance
touches_agentic_core: false
touches_governance_ci: true
touches_cursor_rules: true
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
---

# Governance dedup closeout — hooks, CI gates, plan sprawl, legacy editor mirror

Close all **deferred scope** from [governance_dedup_audit_20260526.md](../../docs/reports/cursor/governance_dedup_audit_20260526.md) (2026-05-26 partial pass). Parent track: [cursor-governance-two-tier-b4e8f2](cursor-governance-two-tier-b4e8f2.md) (COMPLETED); this plan finishes Option A leftovers without reopening Tier-1 invariants.

> **plan_id discipline:** `plan_id` = filename stem `governance-dedup-closeout-e8a4c2`.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1  
PLAN_STATUS: COMPLETED  
CURRENT_WAVE: W5  
LAST_COMPLETED_WAVE: W5  
LAST_UPDATED: 2026-05-26  

PLAN_CREATED: slug=governance-dedup-closeout-e8a4c2 path=.claude/plans/governance-dedup-closeout-e8a4c2.md status=Not Started

---

## Context (SCQA)

- **Situation** — 2026-05-26 dedup pass fixed README (4 always-on rules), regenerated [RULES_INDEX.md](../RULES_INDEX.md), unified post-agent SSOT on `after_agent_governance_dispatch.py`, shortened Author-Gate pre-prompt reminder, and documented legacy/obsolete hooks. Tier-1 budget PASS (~4.6k tokens per [governance_tier_inventory.json](../../docs/reports/cursor/governance_tier_inventory.json)).
- **Complication** — Four deferred items remain: (1) obsolete `post_cursor_agent_*` scripts still on disk; (2) `check_cursor_native_config.py` FAIL on `.windsurf` tokens in active `.cursor` scripts; (3) ~86 active top-level plans vs &lt;20 policy target; (4) 13 legacy editor `always_on` rules (~47 KB) not demoted per Option A. Dispatch shadow period (≥7 days) not formally recorded before script deletion.
- **Question** — How do we close governance dedup deferred scope with receipts, CI proof, and zero-loss hook coverage?
- **Answer** — Five waves: baseline + shadow metrics → hook retirement → CI legacy-ref remediation → plan archive → legacy editor demotion doc/execution → closeout manifest; each wave gated by explicit commands and artifact paths.

---

## Status Tables

### Wave Progress

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W0 | W0.1–W0.2 | Baseline matrix refresh + dispatch shadow metrics | ~4k | `POST_CURSOR_AGENT_DISPATCHER=1` already default in dispatch | ✅ DONE | [governance_dedup_w0_receipt.md](../../docs/reports/cursor/governance_dedup_w0_receipt.md) |
| W1 | W1.1–W1.3 | Retire obsolete post-agent scripts + legacy hook | ~10k | W0 shadow ≥7 days OR operator waives with receipt | ✅ DONE | [governance_dedup_w1_receipt.md](../../docs/reports/cursor/governance_dedup_w1_receipt.md) |
| W2 | W2.1–W2.2 | `check_cursor_native_config` + RULES_INDEX drift gate | ~6k | W1 complete | ✅ DONE | [governance_dedup_w2_receipt.md](../../docs/reports/cursor/governance_dedup_w2_receipt.md) |
| W3 | W3.1–W3.2 | Active plan sprawl archive (&lt;20 top-level) | ~8k | Archive policy from W3 cursor-governance plan | ✅ DONE | [governance_dedup_w3_receipt.md](../../docs/reports/cursor/governance_dedup_w3_receipt.md) |
| W4 | W4.1 | legacy editor `always_on` demotion / mirror freeze receipt | ~6k | No legacy editor deletion without migration receipt | ✅ DONE | [governance_dedup_w4_receipt.md](../../docs/reports/cursor/governance_dedup_w4_receipt.md) |
| W5 | W5.1 | Closeout manifest + audit link-back | ~2k | W0–W4 done or DEFERRED_SCOPE captured | ✅ DONE | [governance_dedup_closeout_receipt.md](../../docs/reports/cursor/governance_dedup_closeout_receipt.md) |

### Phase Progress

| Phase | Title | Status |
|-------|-------|--------|
| W0.1 | Regenerate `governance_w3_hook_audit_matrix` | ✅ DONE |
| W0.2 | Record dispatch shadow baseline (7-day window) | ✅ DONE |
| W1.1 | Archive obsolete scripts to `_legacy_cursor` | ✅ DONE |
| W1.2 | Remove or test-only `after_agent_author_gate_audits.py` | ✅ DONE |
| W1.3 | Update unit tests + `check_ag_hook_wiring` references | ✅ DONE |
| W2.1 | Allowlist migration scripts in native config check | ✅ DONE |
| W2.2 | Exclude generated timestamp from `generate_rules_index --check` | ✅ DONE |
| W3.1 | Classify active plans (keep / archive / merge) | ✅ DONE |
| W3.2 | Move completed plans to `.claude/plans/_archive/` | ✅ DONE |
| W4.1 | legacy editor always_on inventory + demotion decision doc | ✅ DONE |
| W5.1 | Emit closeout receipt + Notion `Completed` | ✅ DONE |

---

## Out Of Scope

- Runtime RAG / contextual retrieval ([anthropic-rag-gaps-7f3c2a](anthropic-rag-gaps-7f3c2a.md))
- Deleting `.windsurf/` tree wholesale
- Changing Tier-1 always-on rule text (`000`–`003`, `AGENTS.md` autogen blocks)
- `agentic_core` or `apps_rg` product runtime
- Removing MCP redirect stub directories (optional gap GAP-4 only if W4 time permits)

---

## Gap Register

**GAP-1: Dispatch shadow period not formalized**  
- `post_cursor_agent_dispatch.py` requires ≥7 days shadow before removing standalone entries.  
- Impact: Premature deletion risks silent audit outage (constitutional §30 precedent).

**GAP-2: Twelve `obsolete_candidate` hook scripts**  
- Per [governance_w3_hook_audit_matrix.md](../../docs/reports/cursor/governance_w3_hook_audit_matrix.md): `author_gate_audit`, `author_gate_suite`, `cleanup`, `grep_budget`, `heartbeat`, `notion_plans_status`, `plan_complete`, `plan_creation`, `plans_dup`, `read_budget`, `token_telemetry`, etc.  
- Impact: Confusion, duplicate maintenance; some still referenced in docs/tests.

**GAP-3: `check_cursor_native_config` legacy-reference FAIL**  
- ~30 active `.cursor/scripts/*` files mention `.windsurf` for sync/migration.  
- Impact: CI noise; false FAIL masks real drift.

**GAP-4: MCP redirect stubs vs AGENTS.md Skill column**  
- 13 skills deprecated → `mcp-integration` §1–§13; AGENTS links stubs for discovery.  
- Impact: Token waste if agents load stub bodies; mitigated by AGENTS note (2026-05-26). Optional: autogen Skill column → section anchors only.

**GAP-5: Plan sprawl (86 active)**  
- `check_cursor_optimized_config.py` warns; W3 of parent plan targeted &lt;20.  
- Impact: Agent plan-selection noise.

**GAP-6: legacy editor 13× `always_on` (~47 KB)**  
- Option A W1 froze mirror; demotion never executed.  
- Impact: legacy editor sessions still load duplicate invariants (separate product surface).

---

## Wave 0 — Baseline and shadow metrics

WAVE_ID: W0  
WAVE_STATUS: DONE  
WAVE_COMPLETE: YES  
AUTHORIZATION_STATUS: NOT_REQUIRED  
CHECKPOINT: A

**Phases**:
- **W0.1** — Run `python ops_scripts/ci/governance_w3_hook_audit_matrix.py`; commit refreshed JSON/MD if drift | ~2k | PHASE_STATUS: DONE
- **W0.2** — Append 7-day shadow start to `artifacts/cursor/governance_dispatch_shadow.jsonl` (dispatcher invocations, error counts) | ~2k | PHASE_STATUS: DONE

WAVE_COMPLETE: plan=governance-dedup-closeout-e8a4c2 wave=0 note="matrix 42 scripts 12 obsolete, shadow jsonl, AG-WIRE PASS, receipt on disk"

**Acceptance**:
- Hook matrix disposition counts match live `after_agent_governance_dispatch.py` chain
- Shadow file exists with `started_at` ISO timestamp

**Commands**:
```bash
python ops_scripts/ci/governance_w3_hook_audit_matrix.py
python ops_scripts/ci/check_ag_hook_wiring.py
python .cursor/scripts/check_cursor_optimized_config.py
```

---

## Wave 1 — Hook obsolete retirement

WAVE_ID: W1  
WAVE_STATUS: DONE  
WAVE_COMPLETE: YES  
AUTHORIZATION_STATUS: EXECUTED  
CHECKPOINT: B

**Authorization**: REQUIRED — Deletes/archives governance scripts; blast radius across post-agent audits. **Waived** 7-day shadow per operator W1 request (logged in shadow jsonl).

**Phases**:
- **W1.1** — Move `obsolete_candidate` scripts to `.cursor/scripts/_legacy_cursor/` (preserve git history); add `README.md` index | ~4k | PHASE_STATUS: DONE
- **W1.2** — Retain `after_agent_author_gate_audits.py` only under `tests/` import path OR delete with test rewrite to mock governance_dispatch | ~3k | PHASE_STATUS: DONE
- **W1.3** — Update `tests/unit/ops_scripts/hooks/cursor/*`, `check_ag_hook_wiring.py` docs, stale plan cross-refs | ~3k | PHASE_STATUS: DONE

WAVE_COMPLETE: plan=governance-dedup-closeout-e8a4c2 wave=1 note="12 scripts+1 hook _legacy_cursor, adr removed from dispatch, 34 pytest PASS"

**Acceptance**:
- No `hooks.json` entry points at archived scripts
- `pytest tests/unit/ops_scripts/hooks/cursor/ -q` PASS
- `check_ag_hook_wiring.py` PASS

**Smoke**:
```bash
python -m pytest tests/unit/ops_scripts/hooks/cursor/ -q --tb=no
python ops_scripts/ci/check_ag_hook_wiring.py
```

---

## Wave 2 — CI native config and index drift

WAVE_ID: W2  
WAVE_STATUS: DONE  
WAVE_COMPLETE: YES  
AUTHORIZATION_STATUS: NOT_REQUIRED  
CHECKPOINT: C

**Phases**:
- **W2.1** — Add `legacy_reference_allowlist.yaml` (or extend existing) for sanctioned sync scripts: `sync_mcp_config.py`, `refresh-windsurf-docs.ps1`, migration replay tools | ~3k | PHASE_STATUS: DONE
- **W2.2** — `generate_rules_index.py --check`: ignore `**Generated**:` line or compare normalized body | ~3k | PHASE_STATUS: DONE

**Acceptance**:
- `python .cursor/scripts/check_cursor_native_config.py --strict` → exit 0 ✅
- `python .cursor/scripts/generate_rules_index.py --check` → exit 0 ✅

WAVE_COMPLETE: plan=governance-dedup-closeout-e8a4c2 wave=2 note="legacy_reference_allowlist.yaml, 31->0 native config failures, index check normalized"

---

## Wave 3 — Plan sprawl archive

WAVE_ID: W3  
WAVE_STATUS: DONE  
WAVE_COMPLETE: YES  
AUTHORIZATION_STATUS: EXECUTED  
CHECKPOINT: D

**Phases**:
- **W3.1** — Inventory CSV at `docs/reports/cursor/plan_sprawl_inventory_20260526.csv` (87 rows classified) | ~4k | PHASE_STATUS: DONE
- **W3.2** — 76 plans moved to `.claude/plans/_archive/2026-05/`; registration cache refreshed | ~4k | PHASE_STATUS: DONE

**Acceptance**:
- `check_cursor_optimized_config.py` → `active_plan_files_count` **11** (≤ 20) ✅
- `check_plan_registration_freshness.py --refresh` → OK ✅

WAVE_COMPLETE: plan=governance-dedup-closeout-e8a4c2 wave=3 note="76 archived, 11 top-level remaining, sprawl inventory CSV on disk"

---

## Wave 4 — legacy editor always_on demotion

WAVE_ID: W4  
WAVE_STATUS: DONE  
WAVE_COMPLETE: YES  
AUTHORIZATION_STATUS: EXECUTED  
CHECKPOINT: E

**Phases**:
- **W4.1** — Demotion map + 13× `always_on` → `model_decision`; budget gate before/after | ~6k | PHASE_STATUS: DONE

**Acceptance**:
- [windsurf_always_on_demotion_map_20260526.md](../../docs/reports/cursor/windsurf_always_on_demotion_map_20260526.md) on disk ✅
- legacy editor `always_on` count **0** (47,493 B → 0 B); Tier-1 **PASS** unchanged ✅

WAVE_COMPLETE: plan=governance-dedup-closeout-e8a4c2 wave=4 note="13 windsurf rules demoted; windsurf_always_on_total=0"

---

## Wave 5 — Closeout

WAVE_ID: W5  
WAVE_STATUS: DONE  
WAVE_COMPLETE: YES  
AUTHORIZATION_STATUS: NOT_REQUIRED  
CHECKPOINT: F

**Phases**:
- **W5.1** — Closeout manifest + audit link-back + DoD gates | ~2k | PHASE_STATUS: DONE

**Acceptance**:
- [governance_dedup_closeout_receipt.json](../../docs/reports/cursor/governance_dedup_closeout_receipt.json) lists GAP-1..6 (GAP-4 DEFERRED P4) ✅
- All DoD gates PASS; pytest 34/34 ✅

WAVE_COMPLETE: plan=governance-dedup-closeout-e8a4c2 wave=5 note="closeout manifest; plan COMPLETED"

PLAN_COMPLETE: plan=governance-dedup-closeout-e8a4c2 note="governance dedup deferred scope closed 2026-05-26"

---

## Definition of Done

DoD-1: All audit deferred items resolved or explicitly DEFERRED with P-Band in receipt  
- Evidence: [governance_dedup_closeout_receipt.json](../../docs/reports/cursor/governance_dedup_closeout_receipt.json)  
- Status: PASS (GAP-4 DEFERRED P4)

DoD-2: Hook wiring smoke  
- Evidence: `python ops_scripts/ci/check_ag_hook_wiring.py` exit 0  
- Status: PASS

DoD-3: Governance CI gates  
- Evidence: `python .cursor/scripts/check_cursor_optimized_config.py` exit 0; `python ops_scripts/ci/check_agents_md_sync.py` exit 0  
- Status: PASS

DoD-4: Hook/cursor unit tests  
- Evidence: `pytest tests/unit/ops_scripts/hooks/cursor/ -q` — 34 passed  
- Status: PASS

DoD-5: Plan registered on disk + Notion; parent audit cross-linked  
- Evidence: `.claude/plans/governance-dedup-closeout-e8a4c2.md`; audit §6 updated; Notion Completed via wave-exec  
- Status: PASS

---

## Verification vs Deferral

| Item | Wave | If blocked |
|------|------|------------|
| Shadow &lt;7 days | W1 | DEFERRED_SCOPE P-Band; do not delete scripts |
| Notion token missing | W5 | Disk-only; `PLAN_REGISTRATION_BYPASS` for local wave start |
| legacy editor demotion rejected | W4 | Document freeze; defer physical edits |
| Plan archive breaks slug | W3 | Rollback move; fix registration cache |

---

## Related artifacts

| Artifact | Path |
|----------|------|
| Dedup audit (source) | [governance_dedup_audit_20260526.md](../../docs/reports/cursor/governance_dedup_audit_20260526.md) |
| Hook matrix | [governance_w3_hook_audit_matrix.md](../../docs/reports/cursor/governance_w3_hook_audit_matrix.md) |
| Tier inventory | [governance_tier_inventory.json](../../docs/reports/cursor/governance_tier_inventory.json) |
| Parent plan (done) | [cursor-governance-two-tier-b4e8f2.md](cursor-governance-two-tier-b4e8f2.md) |
| RULES_INDEX | [RULES_INDEX.md](../RULES_INDEX.md) |
