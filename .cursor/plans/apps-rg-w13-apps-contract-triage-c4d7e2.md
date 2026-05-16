---
plan_id: apps-rg-w13-apps-contract-triage-c4d7e2
plan_type: tracker
touches_agentic_core: false
touches_governance_ci: false
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: true
---

# apps_rg W13 — Full `tests/_apps_contract` triage (classification playbook)

Executable Cursor plan for running and classifying the entire `tests/_apps_contract` surface **without** mandating fixes in-wave. Parent context: prompt-authority program **W12 CLOSED** (scoped 171 green); full suite remains a **separate** promotion surface. See also narrative: `docs/reports/apps_rg_prompt_authority/W13_apps_contract_triage_plan.md`.

> **plan_id discipline**: `plan_id` matches filename stem; wave markers use `plan=apps-rg-w13-apps-contract-triage-c4d7e2`.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1  
PLAN_STATUS: TODO  
CURRENT_WAVE: W0  
LAST_COMPLETED_WAVE: NONE  
LAST_UPDATED: 2026-05-15  

---

## Context (SCQA)

- **Situation** — W12 closed with scoped proof (57 + 70 + 44 = **171**); `topic/apps_rg-prompt-authority` has clean `agentic_core` hygiene. Full `_apps_contract` was intentionally out of scope.
- **Complication** — The full contract directory mixes apps_rg prompt work with other apps, stale BOM assumptions, collection hazards, and judge-harness drift; failures require **bucketed triage**, not ad-hoc whack-a-mole.
- **Question** — How do we run, archive, and classify full `tests/_apps_contract` so regressions map to a single primary bucket and fix order is explicit?
- **Answer** — Three-wave playbook: collection archive → clustered runs → written classification + optional fix promotion (separate PRs).

---

## Wave summary

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1 | W1.P1–W1.P2 | Collection smoke + transcript archive | ~2K | `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`, `pytest_timeout` available | 🔲 TODO | `collect-only` log stored; 0 collection errors OR errors classified |
| W2 | W2.P1–W2.P2 | Full/clustered pytest + first-failure capture | ~8K | Repo root; same env as W12 | 🔲 TODO | Exit codes + `lastfailed` path recorded; `--maxfail=1` first pass done |
| W3 | W3.P1 | Bucket report + owner hints | ~3K | W2 artifacts exist | 🔲 TODO | Every failure row has exactly one primary bucket; fix order stated |

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| W1.P1 | Collection-only run | `tests/_apps_contract` | Imports, plugin conflicts | ~1K | 🔲 TODO |
| W1.P2 | Archive `collect_output.txt` | `artifacts/` or operator-chosen log path | Path discipline | ~0.5K | 🔲 TODO |
| W2.P1 | First hard failure (`--maxfail=1`) | same | Ordering noise | ~2K | 🔲 TODO |
| W2.P2 | Cluster runs (apps_rg prompt / other / harness) | same | Timeout / flake | ~5K | 🔲 TODO |
| W3.P1 | Classification table + next actions | `docs/reports/` or issue tracker | Scope creep | ~3K | 🔲 TODO |

---

## Out of scope

- Fixing `test_apps_rg_prompt_bom_exists.py` or other failures **unless** explicitly promoted in a child PR.
- Any `agentic_core` edits (belongs on binding/exit branch if needed).
- Replacing W12 scoped proof as release evidence for prompt-authority seams.

---

## Failure buckets (primary assignment — exactly one per failure)

1. **Prompt-authority regression** — registry, no-inline PA, ledger-only, X2/X1D contracts.
2. **Stale BOM/layout contract** — `prompt_bom`, template roots, `app` vs `app_id`.
3. **Route/profile drift** — L2 maps, manifest, dispatch registry vs tests.
4. **Judge harness** — X1D / mock fixtures / rubric paths.
5. **Collection/setup** — imports, fixtures, optional deps.
6. **pytest/plugin environment** — autoload vs `-p`, timeout/xdist.
7. **Fixture drift** — golden paths, artifacts renamed.
8. **Unrelated app contract** — non–apps_rg tests under shared folder.

---

## Canonical commands

```bat
set PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
python -m pytest -p pytest_timeout tests/_apps_contract --collect-only -q
python -m pytest -p pytest_timeout tests/_apps_contract -q --tb=short
```

---

## Known inventory (seed)

| Module | Bucket (seed) | Notes |
|--------|-----------------|-------|
| `test_apps_rg_prompt_bom_exists.py` | Stale BOM/layout | `app` vs `app_id`, template root drift, missing symbols |

---

## Gap register

**GAP-1:** Full-suite green is **not** a goal of this plan — classification and honest **PASS/PARTIAL** is.

**GAP-2:** Re-run **W12 scoped 171** after any `apps_rg` prompt seam change.

---

## Definition of Done

*(dod_exempt: true — triage playbook; evidence is documentation + archived logs, not a mandated green full suite.)*

- DoD-1: W1 collection transcript exists with path recorded in wave note.
- DoD-2: W2 pytest transcript(s) archived with exit codes and `lastfailed` pointer when applicable.
- DoD-3: W3 classification table covers every observed failure with one primary bucket.
- DoD-4: Fix-order recommendation documented (import → BOM → prompt-authority → remainder).
- DoD-5: Explicit statement whether full suite **PASS** was achieved or **PARTIAL** with buckets.

---

## Marker quick reference

```
WAVE_START: plan=apps-rg-w13-apps-contract-triage-c4d7e2 wave=1
WAVE_COMPLETE: plan=apps-rg-w13-apps-contract-triage-c4d7e2 wave=1 note="collection archived, scope=triage"
PLAN_COMPLETE: plan=apps-rg-w13-apps-contract-triage-c4d7e2 note="triage playbook executed or deferred with reason"
```
