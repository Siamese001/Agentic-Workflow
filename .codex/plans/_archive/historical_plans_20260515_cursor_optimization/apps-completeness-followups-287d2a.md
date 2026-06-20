# Plan — `apps_*` Completeness Follow-Ups

**Slug:** `apps-completeness-followups-287d2a`
**Created:** 2026-05-02
**Tier:** T2 (multi-file, multi-app, bounded)
**Driver:** Open + deferred items surfaced during `apps-completeness-remediation-907fac` (now Completed)
**Status:** Completed (2026-05-02)
**Predecessor:** `.windsurf/plans/apps-completeness-remediation-907fac.md` (Completed 2026-05-02)

## Goal

Close the bounded follow-up items that emerged during the `apps_*` completeness remediation. Two items genuinely require multi-day SME-engaged scope (W4 underwriting domain logic, W7 apps_shared 74-stub audit) — both captured as `DEFERRED_SCOPE` rows for separate plan cycles, NOT executed here.

## Files In Scope

- W1: `apps_research/reasoning/__init__.py`, `apps_research/services/source_discovery_service.py`, `tests/integration/apps_research/test_apps_research_integration.py`
- W2: `apps_underwriting_ai/TECHNICAL_SPEC.md`, `apps_underwriting_ai/TEST_STRATEGY.md`, `apps_underwriting_ai/spine_manifest.yaml` (new)
- W3: `apps_underwriting_ai/tests/test_contract.py`, `test_underwriting_types.py`, `test_integrations.py`, `test_outputs.py` (new)
- W5: `apps_lic/reasoning/ValidatorAgent.py`, `apps_lic/reasoning/OutreachMessageAgent.py` (audit + decision)
- W6: `tools/analysis/_apps_completeness_review2.py` (PromptGap column fix), ADG snapshot regen via `tools/generate_full_adg.py`

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---|---|---|---|
| W1 | P1.1, P1.2 | Fix 8 pre-existing `apps_research` integration test failures | ~3k | Root cause: `__getattr__` shadowed by submodule lookup + `discover_from_query` missing alias | DONE | 12/12 tests pass (was 8 failed + 23 passed) |
| W2 | P2.1, P2.2, P2.3 | `apps_underwriting_ai` doc completion | ~5k | TECHNICAL_SPEC + TEST_STRATEGY mirror `apps_rfp` shape; `spine_manifest.yaml` mirrors `apps_rg` shape | DONE | All three files present (~5k + ~5k + ~2k bytes) |
| W3 | P3.1, P3.2, P3.3, P3.4 | `apps_underwriting_ai` contract test suite | ~6k | Mirror `apps_rfp/tests/` 4-file split (types/integrations/outputs/contract) | DONE | 61 tests pass (5 smoke + 56 new contract/types/integrations/outputs) |
| W5 | P5.1, P5.2 | `apps_lic` `NotImpl` pattern audit + convention doc | ~2k | 3 of 5 remaining `NotImpl` were heal-stub pattern; converted to no-op + documented convention | DONE | 3 sites converted (ValidatorAgent, OutreachMessageAgent ×2); 3 ABC `_validate`/`_process` retained; convention added to `apps_lic/RUNBOOK.md` |
| W6 | P6.1, P6.2 | Tooling cleanup | ~2k | Scanner column-key fix is one-line; ADG regen produced "lite" snapshot — scanner now picks the most recent FULL snapshot | DONE | New snapshot `adg_indexed_05022026_1819.sqlite`; scanner emits valid `PromptGap` values (was -1 for all apps); auto-selects best snapshot |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| P1.1 | Fix `apps_research/reasoning/__init__.py` `__getattr__` shadowing | 1 file | Submodule lookup beats `__getattr__` for matching names — switched to eager imports | ~1k | DONE |
| P1.2 | Add `SourceDiscoveryService.discover_from_query` alias | 1 file, +20 lines | Test asserts the interface; alias delegates to existing `discover_sources` | ~500 | DONE |
| P2.1 | `apps_underwriting_ai/TECHNICAL_SPEC.md` | 1 new file | Pipeline topology, type contracts, integration surfaces, skeleton seams, error model, observability, versioning | ~2k | DONE |
| P2.2 | `apps_underwriting_ai/TEST_STRATEGY.md` | 1 new file | Smoke / contract / integration / output / types tiers documented | ~1.5k | DONE |
| P2.3 | `apps_underwriting_ai/spine_manifest.yaml` | 1 new file | R3_grounded_read claim with entry/exit points + pre-migration audit | ~1k | DONE |
| P3.1 | `tests/test_underwriting_types.py` | 1 new file (16 tests) | Verifies frozen-dataclass discipline + DecisionVerdict enum bounds | ~2k | DONE |
| P3.2 | `tests/test_integrations.py` | 1 new file (16 tests) | Adapter contract tests (ExecutionAdapter, IngressRunner, SpineHandoff, Observability) | ~1.5k | DONE |
| P3.3 | `tests/test_outputs.py` | 1 new file (14 tests) | Renderer round-trip tests + disk-emit tests | ~1.5k | DONE |
| P3.4 | `tests/test_contract.py` | 1 new file (10 tests) | End-to-end contract invariants (verdict, evidence, trace_id, gate_violations, evidence-register growth) | ~1k | DONE |
| P5.1 | Audit 5× `NotImpl` sites in apps_lic | survey | 3 are heal-stub (convert), 2 are ABC `_validate`/`_process` template-method (keep) | ~1k | DONE |
| P5.2 | Document NotImpl convention | `apps_lic/RUNBOOK.md` +50 lines | "Heal-Method NotImpl Convention" section with 3-category table + when-to-use guidance + conversion log | ~1k | DONE |
| P6.1 | Fix scanner PromptGap column | 1 file, +per-MV column resolution | `mv_prompt_assembly_wiring_gaps` keys on `target_file` not `file`; auto-selects most recent FULL snapshot | ~500 | DONE |
| P6.2 | Regenerate ADG snapshot | 1 command + verify | New snapshot `adg_indexed_05022026_1819.sqlite` (lite — 4 MVs); scanner falls back to most recent FULL snapshot for gap data | ~500 | DONE |

## Gap Register

- 8× `apps_research` integration test failures (pre-existing, pre-dated the prior plan).
- 3× `apps_underwriting_ai` docs missing (TECHNICAL_SPEC, TEST_STRATEGY, spine_manifest.yaml — deferred from `907fac` P3.7).
- 4× contract test files missing in `apps_underwriting_ai/tests/` (deferred from `907fac` P3.8 — only smoke shipped).
- 5× `NotImplementedError` sites in apps_lic agents (out-of-scope of `907fac`, observed during scanning).
- 1× scanner column-key bug (`PromptGap = -1` for all apps).
- 1× ADG snapshot stale relative to `apps_underwriting_ai` (still shows 7 nodes; should be ~40+ after rescan).

## DEFERRED_SCOPE (separate plan cycles)

DEFERRED_SCOPE: title=`apps_underwriting_ai feature-complete domain logic` reason=`requires actuarial/regulatory SME engagement; multi-day T3 scope` plan=`TBD` predecessor=`apps-completeness-remediation-907fac` files=`apps_underwriting_ai/engines/feature_derivation_engine.py, decision_packet_assembler.py, evidence_register_engine.py, document_reconciliation_engine.py, parsers/, validators/`

DEFERRED_SCOPE: title=`apps_shared 74-stub audit` reason=`74 stubs across 207 files require categorization (Protocol/ABC vs real gap); audit-then-fix pattern needs separate scope` plan=`TBD` predecessor=`apps-completeness-followups-287d2a` files=`apps_shared/enforcement/*Strategy.py, apps_shared/_compat/, apps_shared/reasoning/Base*Agent.py`

## ADG_HOTSPOT_REPORT

Skipped: this is a **completeness/gap-fill** plan, not a hotspot-driven refactor. Targets are determined by structural-completeness gaps already enumerated. Per `.windsurf/rules/adg-graph-layer-enforcement.md`, hotspot ordering is required for **anti-pattern burndown / refactoring** plans; this is neither.

## ADG_GRAPH_LAYER_EVIDENCE

- **`mv_runtime_spine_gaps`** — quantifies the apps_underwriting_ai spine connectivity (improved by W2.3 spine_manifest claim).
- **`mv_task_contract_gaps`** — apps_lic NotImpl sites contribute to this gap; W5 audit categorizes which are legitimate vs real.
- **`mv_unknown_taxonomy_and_orphans`** — apps_underwriting_ai files appear here pre-W6.2; ADG regen reduces orphan count.
- **`mv_prompt_assembly_wiring_gaps`** — scanner column-key bug (P6.1) prevented this MV from contributing real data; fix unblocks future scans.
- **Semantic edge — `imports`** — fan-in queries on `apps_research.reasoning.*` modules drive W1.1 root-cause analysis (lazy-import pattern interferes with submodule lookup).
- **`v_p3_*` views** — apps_underwriting_ai modules (P3 manageable-debt band) reduce as canonical structure lands.

## Verification Strategy

Each wave gates the next:

- **W1 done** = `pytest tests/integration/apps_research/test_apps_research_integration.py -v` 0 failures.
- **W2 done** = `Test-Path` returns true for all three new files; doc lint passes.
- **W3 done** = `pytest apps_underwriting_ai/tests/ -v` ≥25 tests pass (5 smoke + ≥20 contract).
- **W5 done** = `apps_lic/RUNBOOK.md` (or equivalent) contains heal-method NotImpl convention; audit table per site committed.
- **W6 done** = scanner emits `PromptGap >= 0` for at least one app; new `artifacts/adg/adg_indexed_*.sqlite` newer than `05022026_1651`.

## Out of Scope (deferred)

See `DEFERRED_SCOPE` rows above — W4 (feature-complete underwriting domain) and W7 (apps_shared 74-stub audit).
