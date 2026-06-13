---
plan_id: apps-rfp-deprecation-deletion-6f4a2b
plan_format: v2
plan_type: platform_core_change
touches_agentic_core: true
touches_governance_ci: true
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: true
author_gate_receipt_ref: "artifacts/governance/core_addition_author_gate/apps-rfp-deprecation-deletion-6f4a2b.json"
dod_exempt: false
supersedes: []
---

# apps_rfp Deprecation and Deletion

Retire `apps_rfp` from active runtime, proof, certification, ingestion, packaging, and catalog surfaces, then hard-delete the implementation only after active references are gone.

> **plan_id discipline**: `apps-rfp-deprecation-deletion-6f4a2b` is the filename stem and all lifecycle markers use `plan=apps-rfp-deprecation-deletion-6f4a2b`.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: TODO
CURRENT_WAVE: W0
LAST_COMPLETED_WAVE: NONE
LAST_UPDATED: 2026-06-13

---

## Context (SCQA)

- **Situation** - `apps_rfp` is still an active app overlay. The current evidence pull found 95 tracked implementation files under `apps_rfp`, 65 ADG module nodes, 36 tracked dedicated tests, and active references in `apps_shared`, `tools/certification`, `tools/ingestion`, `agentic_core` catalogs, packaging metadata, config, certification data, and docs.
- **Complication** - A raw directory delete would break active registries, proof drivers, certification specs, ingestion/indexing stages, tests, packaging, and core structural catalogs. The worktree is also already dirty with unrelated changes, including a separate app deletion, so execution must avoid mixing scopes.
- **Question** - How do we deprecate and delete `apps_rfp` without leaving active callers, stale certification requirements, or broken app inventories?
- **Answer** - Execute in gated waves: authorize core catalog edits, deactivate active surfaces, remove tests/fixtures, clean `agentic_core` and ADG/structure catalogs, hard-delete the package, then prove no active `apps_rfp` references remain outside historical archives.

**Evidence Baseline**:
- ADG fallback: `DEGRADED_FALLBACK: reason=adg_sqlite MCP tools unavailable in Codex session; used canonical SQLite snapshot read-only.`
- ADG provenance: `backend=sqlite`, `snapshot=artifacts/adg/adg_indexed_06132026_0847.sqlite`, generated `2026-06-13T12:51:00Z`, git head `2f859d82ba71204ce9d7d200552794333cd8b070`, dirty tree noted by snapshot metadata.
- Literal scan baseline: `rg -n "apps_rfp" . -g "!apps_rfp/**" -g "!artifacts/**" -g "!docs/archive/**" -g "!tools/reference/_archive/**" -g "!tests/_archived_obsolete/**" -g "!.git/**"` returned active references across app, shared, tool, test, doc, data, config, and plan surfaces.

---

## Status Tables

### Wave Progress

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W0 | W0.1, W0.2, W0.3 | Authorization, baseline refresh, dirty-tree isolation | ~8K | Core catalog edits require author-gate receipt | TODO | Receipt path populated or core edits deferred; refreshed inventory captured |
| W1 | W1.1, W1.2, W1.3 | Deprecate active non-core runtime/proof/certification surfaces | ~18K | RFP capability is being retired, not rerouted | TODO | No active shared/tool registry treats `apps_rfp` as runnable or required |
| W2 | W2.1, W2.2, W2.3 | Remove or rewrite tests and fixtures | ~16K | RFP-only tests are deleted; cross-app tests adopt reduced app set | TODO | Targeted test collection no longer imports `apps_rfp` |
| W3 | W3.1, W3.2, W3.3 | Remove `apps_rfp` from `agentic_core` and ADG/structure catalogs | ~20K | W0 author-gate receipt is valid and attached | TODO | Core catalogs no longer enumerate `apps_rfp`; core gate stays green |
| W4 | W4.1, W4.2, W4.3 | Hard-delete package and active docs | ~12K | Historical archives remain intact | TODO | `git ls-files apps_rfp` is empty and active docs reflect retired app |
| W5 | W5.1, W5.2, W5.3 | Verification, ADG refresh, closeout | ~14K | Repo scripts are available locally | TODO | Pytest selectors, ADG checks, and literal scans prove clean retirement |

### Phase Progress

| Phase | Title | Status |
|-------|-------|--------|
| W0.1 | Produce CoreAdditionAuthorGateReceipt for planned `agentic_core/**` removals | TODO |
| W0.2 | Refresh ADG/literal/reference inventory at execution start | TODO |
| W0.3 | Confirm dirty-tree overlap and branch/commit sequencing | TODO |
| W1.1 | Remove from active app registries, proof inventory, judge registry, and FEC producer lists | TODO |
| W1.2 | Remove from certification/e2e harness specs and app-proof matrices | TODO |
| W1.3 | Remove from ingestion, packaging, prompt/cert config, and active app lists outside core | TODO |
| W2.1 | Delete dedicated `tests/apps_rfp` and `tests/unit/apps_rfp` suites | TODO |
| W2.2 | Delete or rewrite RFP-specific contract/governance tests and fixtures | TODO |
| W2.3 | Update cross-app tests to expect the reduced canonical app set | TODO |
| W3.1 | Remove from `agentic_core` path, route, taxonomy, and proof catalogs | TODO |
| W3.2 | Remove from structure blueprint generated/static catalog surfaces | TODO |
| W3.3 | Remove ADG layer override and repair/analysis references that make it active | TODO |
| W4.1 | `git rm -r apps_rfp` after active callers are gone | TODO |
| W4.2 | Remove active `docs/reports/apps_rfp` and update current docs/runbooks | TODO |
| W4.3 | Preserve archived plans/reports unless separately authorized for purge | TODO |
| W5.1 | Run targeted pytest and collection checks | TODO |
| W5.2 | Run ADG/audit checks and literal no-active-reference scans | TODO |
| W5.3 | Close plan, sync Notion/memory, and record rollback notes | TODO |

---

## Out Of Scope

- Replacing the RFP product capability with another app or route.
- Purging archived plans, historical reports, or legacy evidence solely to erase old `apps_rfp` mentions.
- Fixing unrelated dirty-tree changes already present before this plan.
- Full-suite pytest unless targeted checks expose cross-cutting fallout.
- Changing governance rules, plan templates, or Cursor/Claude rule SSOTs beyond normal plan lifecycle.

---

## Wave 0 - Authorization and Baseline Freeze

WAVE_ID: W0
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: REQUIRED
CHECKPOINT: A

**Authorization**: REQUIRED - Execution will edit `agentic_core/**`; no core catalog edit may occur until a valid `CoreAdditionAuthorGateReceipt` is produced, stored, and referenced in `author_gate_receipt_ref`.

**Phases**:
- **W0.1** - Core author-gate receipt | ~3K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W0.2** - Fresh inventory | ~3K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W0.3** - Dirty-tree isolation | ~2K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Acceptance**:
- `author_gate_receipt_ref` is populated with a valid receipt path before any `agentic_core/**` edit.
- Fresh ADG/literal scan confirms current blast radius.
- Dirty worktree changes are classified as related, unrelated, or blocking before edits.

---

## Wave 1 - Deprecate Active Non-Core Surfaces

WAVE_ID: W1
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: B

**Phases**:
- **W1.1** - Shared registries and proof drivers | ~7K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W1.2** - Certification and app-proof harnesses | ~7K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W1.3** - Ingestion, packaging, and non-core app lists | ~4K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Expected Surfaces**:
- `apps_shared/integrations/app_registry.py`
- `apps_shared/proof/**` and `apps_shared/validators/proof/**`
- `apps_shared/cert/grounded_fec_producers.py`
- `apps_shared/judge_registry.py`
- `tools/certification/apps_e2e/app_specs.py`
- `tools/cert/apps_e2e/**`
- `tools/apps_proof/**`
- `tools/ingestion/pipeline.py`
- `tools/ingestion/_validate_stage.py`
- `pyproject.toml`
- Active config under `config/**`

**Acceptance**:
- No active shared registry can instantiate `apps_rfp`.
- Certification/app-proof tools no longer require `apps_rfp`.
- Packaging metadata no longer includes `apps_rfp*`.

---

## Wave 2 - Remove Tests and Fixtures

WAVE_ID: W2
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: C

**Phases**:
- **W2.1** - Dedicated app tests | ~5K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W2.2** - Contract/governance tests and fixtures | ~7K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W2.3** - Cross-app expectation updates | ~4K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Expected Surfaces**:
- `tests/apps_rfp/**`
- `tests/unit/apps_rfp/**`
- `tests/_apps_contract/test_apps_rfp_fec_producer.py`
- `tests/_apps_contract/test_w2_rfp_spine_migration.py`
- `tests/governance/test_apps_rfp_spine.py`
- `tests/golden/prompt_reception/fixtures/apps_rfp__proposal_section_draft.json`
- `tests/fixtures/apps_rfp/**`
- Cross-app tests under `tests/_apps_contract`, `tests/unit/apps_shared`, `tests/unit/apps_e2e`, and `tests/agentic_core`

**Acceptance**:
- Pytest collection for targeted cross-app selectors succeeds without importing `apps_rfp`.
- RFP-only tests/fixtures are deleted rather than skipped.
- Reduced canonical app set is asserted explicitly where needed.

---

## Wave 3 - Remove Core and ADG Catalog References

WAVE_ID: W3
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: REQUIRED
CHECKPOINT: D

**Authorization**: REQUIRED - W0 author-gate receipt must be valid and referenced before this wave.

**Phases**:
- **W3.1** - `agentic_core` proof/path/taxonomy catalogs | ~8K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W3.2** - Structure blueprint SSOT/generated data | ~8K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W3.3** - ADG layer/repair/analysis active surfaces | ~4K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Expected Surfaces**:
- `agentic_core/runtime/prove_requirements/layer_paths.py`
- `agentic_core/runtime/prove_requirements/code_symbol_catalog.py`
- `agentic_core/L0_routing/config/path_constants.py`
- `agentic_core/L2_execution/types/agent_taxonomy_registry.py`
- `agentic_core/L3_orchestration/exit_eval/v6/apps_eval_doctrine.py`
- `agentic_core/adg/contracts/schema.py`
- `agentic_core/adg/contracts/schema_util.py`
- `agentic_core/L5_safety/config/structure_blueprint/**`
- `tools/adg/adg_layer_overrides.yaml`
- Active ADG repair/analysis app lists that classify `apps_rfp` as current

**Acceptance**:
- Core write gate permits edits only with the receipt attached.
- Active `agentic_core` catalogs no longer enumerate `apps_rfp`.
- Structure blueprint and ADG layer classification do not recreate `apps_rfp` as a valid active surface.

---

## Wave 4 - Hard-Delete Package and Active Docs

WAVE_ID: W4
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: E

**Phases**:
- **W4.1** - Delete package implementation | ~3K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W4.2** - Remove active app docs/reports | ~6K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W4.3** - Preserve historical archives | ~3K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Commands**:
```bash
git rm -r apps_rfp
git rm -r docs/reports/apps_rfp
```

**Acceptance**:
- `git ls-files apps_rfp` returns no paths.
- `python -c "import apps_rfp"` raises `ModuleNotFoundError`.
- Active docs describe `apps_rfp` as retired or omit it from current app lists.
- Archived plans/reports remain untouched unless separately authorized.

---

## Wave 5 - Verification and Closeout

WAVE_ID: W5
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: F

**Phases**:
- **W5.1** - Targeted pytest and collection checks | ~5K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W5.2** - ADG/audit/literal scans | ~6K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W5.3** - Plan, Notion, memory closeout | ~3K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Commands**:
```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -p pytest_timeout tests/_apps_contract tests/governance tests/unit/apps_shared tests/unit/tools/analysis tests/unit/apps_e2e -q
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -p pytest_timeout tests/agentic_core tests/runtime -q
python tools/adg/run_full_adg_audit.py
rg -n "apps_rfp|GovernedRfpRun|rfp_proposal_assembly|RfpRequest" . -g "!artifacts/**" -g "!docs/archive/**" -g "!tools/reference/_archive/**" -g "!tests/_archived_obsolete/**" -g "!plans/archived-*"
python -c "import apps_rfp"
```

**Acceptance**:
- Targeted pytest selectors pass or failures are explicitly tied to unrelated dirty-tree work.
- Fresh ADG snapshot has zero `nodes.resolved_path like 'apps_rfp/%'`.
- Literal scan shows no active references outside approved historical archives.
- Plan markers and Notion status reflect the final disposition.

---

## Execution Details

### W0.1 - Core Author-Gate Receipt

**Scope**: Produce a `CoreAdditionAuthorGateReceipt` covering only removal of stale `apps_rfp` references from `agentic_core/**` catalogs. Patch `author_gate_receipt_ref` in this plan after the receipt is valid.

**Stop Condition**: If author-gate cannot PASS, defer W3 and do not delete the app package.

### W0.2 - Fresh Inventory

**Scope**: Refresh the exact file/reference list before edits.

**Commands**:
```bash
git status --short
git ls-files apps_rfp
git ls-files tests/apps_rfp tests/unit/apps_rfp tests/_apps_contract/test_apps_rfp_fec_producer.py tests/_apps_contract/test_w2_rfp_spine_migration.py tests/governance/test_apps_rfp_spine.py
rg -n "apps_rfp" . -g "!apps_rfp/**" -g "!artifacts/**" -g "!docs/archive/**" -g "!tools/reference/_archive/**" -g "!tests/_archived_obsolete/**" -g "!.git/**"
```

### W0.3 - Dirty-Tree Isolation

**Scope**: Do not revert unrelated user or generated changes. If unrelated dirty files overlap planned edits, inspect and work with them; if overlap makes the plan unsafe, stop for user direction.

### W1-W4 - Edits

**Scope**: Use `apply_patch` for manual edits and `git rm` for deletions after references are inactive. Avoid skip markers; delete obsolete tests or rewrite cross-app expectations.

### W5 - Proof

**Scope**: Run targeted tests, ADG audit, import failure proof, and literal scans. Regenerate/inspect ADG only after deletion is complete.

---

## Gap Register

**GAP-1: Core write authorization**
- `agentic_core/**` edits are blocked until a valid receipt exists and this plan references it.
- Impact: W3 and any dependent deletion step must stop if receipt is unavailable.

**GAP-2: Dirty worktree overlap**
- Current repo state already contains unrelated modifications and deletions.
- Impact: execution may need branch or commit sequencing before touching shared files.

**GAP-3: ADG MCP unavailable in Codex session**
- Evidence pull used direct SQLite fallback because `adg_sqlite` tools were not exposed.
- Impact: execution should prefer MCP if available, otherwise stamp `DEGRADED_FALLBACK` and use direct SQLite read-only queries.

**GAP-4: Historical references are numerous**
- Plans and archived reports contain many valid historical mentions.
- Impact: literal no-reference gates must exclude approved archive/history paths instead of purging audit history.

**GAP-5: Product capability ambiguity**
- This plan assumes RFP generation is retired, not moved.
- Impact: any requirement to preserve RFP capability must split to a migration/reroute plan before deletion.

---

## Definition of Done

DoD-1: `apps_rfp` implementation is hard-deleted from tracked active source.
- Evidence: `git ls-files apps_rfp` returns no paths.
- Status: TODO

DoD-2: Active registries, proof drivers, certification specs, ingestion stages, packaging, and config no longer require `apps_rfp`.
- Evidence: targeted literal scan returns no active registry/harness matches outside approved history.
- Status: TODO

DoD-3: Dedicated tests and fixtures are removed, and cross-app tests assert the reduced canonical app set.
- Evidence: `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -p pytest_timeout tests/_apps_contract tests/governance tests/unit/apps_shared tests/unit/apps_e2e -q`.
- Status: TODO

DoD-4: Core catalog cleanup is authorized and complete.
- Evidence: valid `author_gate_receipt_ref`; targeted scan over `agentic_core/**` shows no active `apps_rfp` catalog/list references except explicit historical comments approved in closeout.
- Status: TODO

DoD-5: Fresh ADG proof shows `apps_rfp` is gone from active graph nodes.
- Evidence: `python tools/adg/run_full_adg_audit.py`; latest SQLite query `select count(*) from nodes where resolved_path like 'apps_rfp/%'` returns `0`.
- Status: TODO

DoD-6: Smoke proof confirms the deleted package is not importable.
- Evidence: `python -c "import apps_rfp"` exits non-zero with `ModuleNotFoundError`.
- Status: TODO

DoD-7: Plan lifecycle is closed cleanly.
- Evidence: `PLAN_COMPLETE` marker emitted; Notion plan status updated or Notion unavailability reported; memory writeback recorded for major decision.
- Status: TODO

### Verification vs Deferral

| Item | Required Before Complete | May Defer | Notes |
|------|--------------------------|-----------|-------|
| Active runtime/shared/tool references removed | Yes | No | Otherwise deletion leaves broken imports or false certification requirements |
| Dedicated tests deleted/rewritten | Yes | No | No `pytest.mark.skip` workaround |
| `agentic_core` catalog cleanup | Yes | Only if package deletion is also deferred | Core catalogs cannot point to a deleted app |
| Historical archive purge | No | Yes | Preserve plans/reports unless separately authorized |
| Full pytest suite | No | Yes | Run targeted suite unless fallout shows broader risk |
| Notion registration/closeout | Yes if connector available | Report if unavailable | Filesystem plan remains SSOT |

---

## Scope Expansion Authorization

When scope is discovered during execution, emit markers in order:

```text
DISCOVERED_SCOPE: plan=apps-rfp-deprecation-deletion-6f4a2b wave=<N> phase=<M> gap="<what>" impact="<severity>"
AUTHORIZATION_DECISION: plan=apps-rfp-deprecation-deletion-6f4a2b decision=<ACCEPTED|DEFERRED|SPLIT_TO_NEW_PLAN|REJECTED> authorized_by=<user|author_gate|self> decisive_reason="<why>"
SCOPE_EXPANSION: plan=apps-rfp-deprecation-deletion-6f4a2b reason="<summary>" added="<waves/phases>" authorized="yes"
```

| Decision | When | Continues? |
|---|---|---|
| ACCEPTED | In-charter and absorbable | Yes, expanded scope |
| DEFERRED | Valid but time-gated | Yes, original scope |
| SPLIT_TO_NEW_PLAN | Too large or changes product intent | Yes, original scope |
| REJECTED | Off-charter cleanup | Yes, original scope |

---

## Supersedes

| Predecessor slug | Reason |
|---|---|
| _None - net-new plan._ | This is a new retirement/deletion plan, not a replacement for historical `apps_rfp` build or refactor plans. |

---

## Marker Quick Reference

```text
PLAN_CREATED: slug=apps-rfp-deprecation-deletion-6f4a2b path=plans/apps-rfp-deprecation-deletion-6f4a2b.md status=Not Started
WAVE_START: plan=apps-rfp-deprecation-deletion-6f4a2b wave=<N>
WAVE_COMPLETE: plan=apps-rfp-deprecation-deletion-6f4a2b wave=<N> note="+N tests, N files, scope=<summary>"
PHASE_COMPLETE: plan=apps-rfp-deprecation-deletion-6f4a2b phase=<W1.1>
PLAN_COMPLETE: plan=apps-rfp-deprecation-deletion-6f4a2b note="<final outcome>"
```

---

## Rollback and Repair

- Before W4 package deletion: revert individual registry/test/catalog edits with normal git restore for the affected files.
- After W4 package deletion: restore `apps_rfp` and its tests from git if active callers are found.
- If W3 core authorization fails: leave `apps_rfp` in place and close this plan as blocked or split a non-core deprecation-only plan.
