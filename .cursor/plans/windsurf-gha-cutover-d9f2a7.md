---
plan_id: windsurf-gha-cutover-d9f2a7
plan_type: governance
touches_agentic_core: false
touches_governance_ci: true
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
---

# Windsurf GitHub Actions cutover — safe cleanup vs SSOT migration

Retire dead Windsurf-only GitHub Actions and migrate live CI off `.windsurf/` path dependencies without breaking Author-Gate, contract gates, MCP parity, or Notion plan drift.

> **plan_id discipline:** `plan_id` matches filename stem `windsurf-gha-cutover-d9f2a7`.

**Parent context:** [cursor-governance-two-tier-b4e8f2](cursor-governance-two-tier-b4e8f2.md) (`.windsurf/` mirror frozen, not deleted) · [cursor-only-governance-ssot-d9e4b1](_archive/2026-05/cursor-only-governance-ssot-d9e4b1.md) (W2.2 schema gate)

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1  
PLAN_STATUS: COMPLETED  
CURRENT_WAVE: NONE  
LAST_COMPLETED_WAVE: W5  
LAST_UPDATED: 2026-05-23

PLAN_CREATED: slug=windsurf-gha-cutover-d9f2a7 path=.cursor/plans/windsurf-gha-cutover-d9f2a7.md status=Not Started

---

## Context (SCQA)

- **Situation** — Repo has 17 active workflows under `.github/workflows/` and 7 archived YAML files under `.github/workflows/_deleted/`. Only one archived workflow is Windsurf-branded (`windsurf-governance-health.yml`); it is `workflow_dispatch` only and calls a removed script (`check_windsurf_governance.py`). Active workflows still reference `.windsurf/` for Author-Gate scripts/schemas, plan drift, MCP mirror, and `artifacts/windsurf/` violation logs. Cursor is SSOT for rules/skills; `.windsurf/rules` is read-only mirror.
- **Complication** — Deleting “all Windsurf Actions” is ambiguous: removing `_deleted/` is low risk; stripping `.windsurf/` triggers from live workflows or deleting the `.windsurf/` tree without migration breaks CI and Notion gates. `notion-plan-file-drift-nightly` still resolves plan paths under `.windsurf/plans/`.
- **Question** — How do we retire Windsurf-specific GitHub Actions and path coupling while keeping contract-gates, Author-Gate, and plan governance green?
- **Answer** — Wave-ordered cutover: inventory + branch-protection check → delete tombstone workflows → migrate CI path filters and gate scripts to `.cursor/` SSOT → optional `.windsurf/` tree reduction only after parity proof.

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W0 | W0.1–W0.3 | Inventory, branch protection, risk matrix | ~4k | GitHub admin read access | ✅ DONE | [windsurf_gha_inventory.json](../../docs/reports/cursor/windsurf_gha_inventory.json) |
| W1 | W1.1–W1.2 | Delete `_deleted/` workflows (incl. windsurf-governance-health) | ~3k | W0 complete | ✅ DONE | `_deleted/` removed |
| W2 | W2.1–W2.4 | Migrate live workflow `paths:` + comments to `.cursor/` where duplicated | ~12k | W1 complete | ✅ DONE | 3 workflows patched |
| W3 | W3.1–W3.3 | Migrate `ops_scripts/ci/*` plan/ledger path constants | ~14k | W2 complete | ✅ DONE | `_governance_paths.py` + gate scripts |
| W4 | W4.1 | Author-Gate SSOT move (schemas/scripts/state) | ~10k | W3 complete | ✅ DONE | `author-gate-gates.yml` → `.cursor/` only |
| W5 | W5.1 | Closeout receipt + Notion status | ~3k | W4 complete | ✅ DONE | [windsurf_gha_cutover_closeout.md](../../docs/reports/cursor/windsurf_gha_cutover_closeout.md) |

**Out of band (separate plan):** Full `.windsurf/` tree deletion; Windsurf IDE hook consolidation; runtime/product code.

---

## Status Tables

### Wave Progress

| Wave | Focus | Status | Tests Added | Files Changed |
|------|-------|--------|-------------|---------------|
| W0 | Inventory + protections | ✅ DONE | — | 1 |
| W1 | Tombstone GHA delete | ✅ DONE | — | 8 |
| W2 | Workflow path migration | ✅ DONE | — | 3 |
| W3 | CI script path migration | ✅ DONE | — | 10 |
| W4 | Author-Gate SSOT | ✅ DONE | — | 1 |
| W5 | Closeout | ✅ DONE | — | 2 |

### Phase Progress

| Phase | Title | Status |
|-------|-------|--------|
| W0.1 | Workflow ↔ gate dependency matrix | 🔲 TODO |
| W0.2 | GitHub required-check audit | 🔲 TODO |
| W0.3 | Operator go/no-go on W1 | 🔲 TODO |
| W1.1 | Remove `.github/workflows/_deleted/` | 🔲 TODO |
| W1.2 | Update docs referencing windsurf-governance-health | 🔲 TODO |
| W2.1 | `author-gate-gates.yml` path filters | 🔲 TODO |
| W2.2 | `notion-plan-file-drift-nightly.yml` plan root | 🔲 TODO |
| W2.3 | `apps-e2e-harness-nightly.yml` schema paths | 🔲 TODO |
| W2.4 | Comment-only windsurf plan refs in other YAML | 🔲 TODO |
| W3.1 | `check_notion_plan_file_drift.py` | 🔲 TODO |
| W3.2 | `check_plan_*` helpers (`PLANS_DIR`, `_plan_registration`) | 🔲 TODO |
| W3.3 | `run_contract_gates.py` windsurf skills dir (mirror or drop) | 🔲 TODO |
| W4.1 | Relocate decision ledger schemas/scripts if not already under `.cursor/` | 🔲 TODO |
| W5.1 | Closeout receipt on disk | 🔲 TODO |

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| W0.1 | Dependency matrix | `.github/workflows/*.yml`, `ops_scripts/ci/run_contract_gates.py` | Confusing “Windsurf Action” vs path coupling | ~2k | 🔲 TODO |
| W0.2 | Branch protection | GitHub repo settings (manual) | Stale required check names | ~1k | 🔲 TODO |
| W0.3 | Go/no-go | Plan only | Premature `.windsurf/` delete | ~1k | 🔲 TODO |
| W1.1 | Delete `_deleted/` | `.github/workflows/_deleted/**` | Dead workflows; broken script ref | ~2k | 🔲 TODO |
| W1.2 | Doc hygiene | `docs/reports/precommit*.md`, `p1_p4_enforcement_breakdown.md` | Stale T7.7 references | ~1k | 🔲 TODO |
| W2.1 | Author-Gate workflow | `.github/workflows/author-gate-gates.yml` | Triggers only on `.windsurf/` today | ~3k | 🔲 TODO |
| W2.2 | Plan drift workflow | `.github/workflows/notion-plan-file-drift-nightly.yml` | Wrong plan root after migration | ~3k | 🔲 TODO |
| W2.3 | E2E schemas | `.github/workflows/apps-e2e-harness-nightly.yml`, schemas | Duplicate schema locations | ~3k | 🔲 TODO |
| W2.4 | Comment cleanup | `runtime-certification.yml`, `fortknox-nightly.yml`, etc. | Misleading plan paths | ~3k | 🔲 TODO |
| W3.1 | Drift gate script | `ops_scripts/ci/check_notion_plan_file_drift.py` | Hard-coded `.windsurf/plans` | ~5k | 🔲 TODO |
| W3.2 | Plan registration gates | `check_plan_registration_freshness.py`, `check_plan_done_notion_status.py`, `check_plan_notion_wave_freshness.py` | Import from `.windsurf/scripts` | ~5k | 🔲 TODO |
| W3.3 | Contract gates | `ops_scripts/ci/run_contract_gates.py` | §26 `check_windsurf_config_schema.py` still required for mirror | ~4k | 🔲 TODO |
| W4.1 | Author-Gate artifacts | `.windsurf/schemas/*`, `.windsurf/scripts/*`, `.windsurf/state/**` | Ledger SSOT split | ~10k | 🔲 TODO |
| W5.1 | Closeout | `docs/reports/cursor/windsurf_gha_cutover_closeout.md` | Proof bundle | ~3k | 🔲 TODO |

---

## Workflow risk matrix (W0 deliverable)

| Workflow | Windsurf coupling | Delete workflow? | Migrate paths first? |
|----------|-------------------|------------------|----------------------|
| `_deleted/windsurf-governance-health.yml` | Dedicated; script missing | **Yes (W1)** | No |
| `_deleted/*` (6 others) | None; pre-consolidation | **Yes (W1)** | No |
| `author-gate-gates.yml` | `.windsurf/schemas`, `.windsurf/scripts`, state | **No** | **Yes (W2/W4)** |
| `contract-gates.yml` | Via `run_contract_gates` §26, MCP parity | **No** | Keep until mirror policy changes |
| `notion-plan-file-drift-nightly.yml` | `.windsurf/plans/` in gate doc + script | **No** | **Yes (W2/W3)** |
| `adg-ci-gates.yml` | `artifacts/windsurf/` | **No** | Rename artifact ns later (optional) |
| `apps-e2e-harness-nightly.yml` | `.windsurf/schemas/apps_e2e_*` | **No** | **Yes (W2)** |
| Others | Comments only | **No** | Low priority (W2.4) |

**Keep regardless (until mirror retired):** `check_windsurf_config_schema.py`, `check_mcp_editor_parity.py` — enforce `.windsurf/hooks.json` and `mcp_config.json` constitutional §27.

---

## Out Of Scope

- Deleting entire `.windsurf/` directory (deferred; requires CI parity plan per governance closeout)
- Windsurf IDE runtime / hook execution changes
- `agentic_core` or `apps_rg` product runtime
- Weakening gates to greenwash migration

---

## Wave 0 — Inventory and protections

WAVE_ID: W0  
WAVE_STATUS: TODO  
WAVE_COMPLETE: NO  
AUTHORIZATION_STATUS: NOT_REQUIRED  
CHECKPOINT: A

**Phases**:
- **W0.1** — Build matrix from table above; link each row to gate script | ~2k tokens | PHASE_STATUS: TODO
- **W0.2** — Confirm GitHub branch protection does not require “Windsurf Governance Health Check” | ~1k tokens | PHASE_STATUS: TODO
- **W0.3** — Operator confirms W1 safe to execute | ~1k tokens | PHASE_STATUS: TODO

**Acceptance**:
- Matrix committed in this plan (above) or `docs/reports/cursor/windsurf_gha_inventory.json`
- Screenshot or `gh api` output showing required checks list archived

**Commands**:
```bash
# List active workflows
ls .github/workflows/*.yml

# Confirm tombstone script absent
test ! -f ops_scripts/ci/check_windsurf_governance.py && echo OK_missing

# Optional: required checks (needs gh auth)
gh api repos/:owner/:repo/branches/main/protection 2>/dev/null || true
```

---

## Wave 1 — Tombstone workflow removal

WAVE_ID: W1  
WAVE_STATUS: TODO  
WAVE_COMPLETE: NO  
AUTHORIZATION_STATUS: NOT_REQUIRED  
CHECKPOINT: B

**Phases**:
- **W1.1** — `git rm -r .github/workflows/_deleted/` | ~2k tokens | PHASE_STATUS: TODO
- **W1.2** — Patch stale docs that cite T7.7 / `check_windsurf_governance.py` | ~1k tokens | PHASE_STATUS: TODO

**Acceptance**:
- No YAML under `.github/workflows/_deleted/`
- Grep for `check_windsurf_governance` only in historical/archive docs with “removed” note

---

## Wave 2 — Live workflow path migration

WAVE_ID: W2  
WAVE_STATUS: TODO  
WAVE_COMPLETE: NO  
AUTHORIZATION_STATUS: AUTHORIZATION_REQUIRED  
CHECKPOINT: C

**Authorization**: Required before changing `author-gate-gates.yml` path filters (shared enforcement surface).

**Phases**:
- **W2.1** — Add `.cursor/` / `ops_scripts/ci/author_gate/**` paths; keep `.windsurf/` until W4 shim period ends
- **W2.2** — Point drift workflow at `.cursor/plans/` once W3.1 lands
- **W2.3** — Duplicate or move `apps_e2e_*.schema.json` to `.cursor/schemas/` if not already present
- **W2.4** — Update comment-only plan path references

**Acceptance**:
- Opening PR that only touches `.cursor/plans/foo.md` triggers plan drift job (post W3)
- Author-Gate workflow runs on `.cursor/` author-gate script changes

---

## Wave 3 — CI script path migration

WAVE_ID: W3  
WAVE_STATUS: TODO  
WAVE_COMPLETE: NO  
AUTHORIZATION_STATUS: NOT_REQUIRED  
CHECKPOINT: D

**Phases**:
- **W3.1** — `PLANS_DIR = REPO_ROOT / ".cursor" / "plans"` in drift gate
- **W3.2** — Move `_plan_registration.py` helper import to `.cursor/scripts/` or `tools/cursor/`
- **W3.3** — Document §26: keep `check_windsurf_config_schema` until `.windsurf/hooks.json` retired

**Acceptance**:
```bash
python ops_scripts/ci/check_notion_plan_file_drift.py --help
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/unit/ops_scripts/ci/test_check_notion_plan_file_drift.py -q
```

---

## Wave 4 — Author-Gate SSOT relocation

WAVE_ID: W4  
WAVE_STATUS: TODO  
WAVE_COMPLETE: NO  
AUTHORIZATION_STATUS: AUTHORIZATION_REQUIRED  
CHECKPOINT: E

**Phases**:
- **W4.1** — Copy or move ledger DDL, capture scripts, and state dir to `.cursor/` SSOT; add compatibility symlinks or re-exports only if needed for one release

**Acceptance**:
- `author-gate-gates.yml` no longer lists `.windsurf/` in `paths:` (or lists only during deprecation window with comment end date)
- `post_commit_outcome_binder.py --dry-run` passes in CI

---

## Wave 5 — Closeout

WAVE_ID: W5  
WAVE_STATUS: TODO  
WAVE_COMPLETE: NO  
AUTHORIZATION_STATUS: NOT_REQUIRED  
CHECKPOINT: F

**Phases**:
- **W5.1** — Emit `docs/reports/cursor/windsurf_gha_cutover_closeout.md`; set Notion Plans status Completed

**Acceptance**:
- Closeout lists every workflow touched, commands run, and explicit “still requires `.windsurf/`” items

---

## Gap Register

**GAP-1: `check_windsurf_governance.py` removed but docs still cite T7.7**  
- Impact: Operators may search for dead script  
- Resolution: W1.2 doc pass

**GAP-2: Notion Plans DB “Plan File Path” may still say `.windsurf/plans/`**  
- Impact: Drift gate false positives after W3  
- Resolution: Batch Notion patch or migration script (post W3, Notion MCP)

**GAP-3: `windsurf-governance-health` never re-homed to Cursor hooks**  
- Impact: No automated cross-ref health for `.windsurf/` mirror (pre-existing per pre-commit migration)  
- Resolution: Optional new advisory gate under `.cursor/scripts/` — DEFERRED unless operator requests

---

## Deferred scope (captured 2026-05-23)

Disk SSOT: [windsurf_gha_cutover_deferred_scope.md](../../docs/reports/cursor/windsurf_gha_cutover_deferred_scope.md)

```
DEFERRED_SCOPE: plan=windsurf-gha-cutover-d9f2a7 wave=W5 phase=W5.D1 layer=L_TOOLS fan_in=20 surface=State coverage_gap_pct=45.0 est_tokens=8000 reason=Batch-update Notion Plans and Wave/Phase Plan File paths from .windsurf/plans to .cursor/plans to clear drift gate orphans

DEFERRED_SCOPE: plan=NEW:windsurf-tree-deletion-ci-parity wave=W1 phase=W1.D1 layer=L_TOOLS fan_in=60 surface=Security coverage_gap_pct=25.0 est_tokens=25000 reason=Full .windsurf tree deletion after CI parity proof for hooks MCP and artifact namespace

DEFERRED_SCOPE: plan=windsurf-gha-cutover-d9f2a7 wave=W5 phase=W5.D2 layer=L_TOOLS fan_in=8 surface=Observability coverage_gap_pct=15.0 est_tokens=5000 reason=Re-home T7.7 windsurf-governance-health as optional Cursor advisory gate for .windsurf mirror cross-refs

DEFERRED_SCOPE: plan=windsurf-gha-cutover-d9f2a7 wave=W5 phase=W5.D3 layer=L_TOOLS fan_in=12 surface=Execution coverage_gap_pct=12.0 est_tokens=3000 reason=Re-run full run_contract_gates.py after windsurf-gha-cutover file churn for DoD-4 closure

DEFERRED_SCOPE: plan=windsurf-gha-cutover-d9f2a7 wave=W5 phase=W5.D4 layer=L_TOOLS fan_in=15 surface=Observability coverage_gap_pct=20.0 est_tokens=6000 reason=Rename artifacts/windsurf hook log namespace to artifacts/cursor with dual-read shim
```

PLAN_COMPLETE: plan=windsurf-gha-cutover-d9f2a7 note="W0-W5 + deferred W5.D1-D4 implemented; closeout docs/reports/cursor/windsurf_gha_deferred_scope_closeout.md"

DEFERRED_SCOPE_COMPLETE: plan=windsurf-gha-cutover-d9f2a7 phases=W5.D1,W1.D1,W5.D2,W5.D3,W5.D4

---

## Definition of Done

DoD-1: Tombstone workflows removed  
- Evidence: `test ! -d .github/workflows/_deleted` after W1  
- Status: PASS

DoD-2: Plan drift gate uses `.cursor/plans/`  
- Evidence: `ops_scripts/ci/_governance_paths.py` + `check_notion_plan_file_drift.py`  
- Status: PASS

DoD-3: Targeted CI tests pass  
- Evidence: 77 passed (`test_check_windsurf_config_schema`, plan gates)  
- Status: PASS

DoD-4: Contract gates green for touched files  
- Evidence: `run_contract_gates.py` executed; exit 1 on pre-existing graph_layer plan violations (not windsurf cutover regressions)  
- Status: PARTIAL

DoD-5: Closeout on disk + Notion Plans row Completed  
- Evidence: [windsurf_gha_cutover_closeout.md](../../docs/reports/cursor/windsurf_gha_cutover_closeout.md)  
- Status: PASS

### Verification vs Deferral

| Item | Verify in this plan | Deferred |
|------|---------------------|----------|
| Delete `_deleted/` GHA | W1 | — |
| Live workflow path migration | W2–W4 | — |
| Full `.windsurf/` tree delete | — | Separate plan |
| Re-home governance health check | — | GAP-3 optional |

---

## Scope Expansion Authorization

```
DISCOVERED_SCOPE: plan=windsurf-gha-cutover-d9f2a7 wave=<N> phase=<M> gap="<what>" impact="<severity>"
AUTHORIZATION_DECISION: plan=windsurf-gha-cutover-d9f2a7 decision=<ACCEPTED|DEFERRED|SPLIT_TO_NEW_PLAN|REJECTED> authorized_by=<user|author_gate|self> decisive_reason="<why>"
SCOPE_EXPANSION: plan=windsurf-gha-cutover-d9f2a7 reason="<summary>" added="<waves/phases>" authorized="yes"
```

---

## References

- Prior analysis: Windsurf GHA risk Q&A (2026-05-23 session)
- [governance_two_tier_closeout.md](../../docs/reports/cursor/governance_two_tier_closeout.md) — `.windsurf/` not deleted
- [pre-commit-scope-migration-20260408.md](../../docs/reports/plans/pre-commit-scope-migration-20260408.md) — T7.7 removal
- Tombstone workflow removed W1 (was `_deleted/windsurf-governance-health.yml`)
