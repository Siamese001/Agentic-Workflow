# ADG CI, Guardian / Burndown, Three-Bucket & Severity Harmonization — Consolidated Plan

**Slug:** `adg-ci-guardian-hardening-consolidated-f8a2b1`  
**Status:** Not Started  
**Sources:** Cursor session synthesis (ADG generator, MV layer, CI registry, burndown semantics, Error & Exception Handling v4 primer, P0–P3 vs CRITICAL alignment).

---

## Executive summary

Consolidate **truthful burndown reporting** (guardian vs net vs gross), **Windows/post-ADG gate reliability**, **schema drift** (A6 entrypoint), **three-bucket producer/consumer clarity**, **v4-aligned governance** (exemption ≠ substitute for precision), and **display harmonization** of **P-bands vs CRITICAL/HIGH/MEDIUM/LOW** — without collapsing the dual vocabulary in the SQLite SSOT.

---

## Principles (non-negotiable)

1. **Do not weaken gates** to get green; fix code, baselines, or infra with receipts.  
2. **`agentic_core/adg/severity_bands.py`** remains the SSOT for **Severity ↔ Band** mapping.  
3. **Notion holds the row; disk holds the artifact** — this file is SSOT for narrative.

---

## Wave 0 — Already landed (context only)

| Item | Evidence |
|------|----------|
| MV `sqlite_helpers.py` + shared PRAGMAs for phases A–F | `tools/generate/materialized_views/sqlite_helpers.py` |
| `generate_full_adg` JSON payload helper + typing `Any` + graphdb copy loop | `tools/generate/generate_full_adg.py` |
| Lazy ADG shim | `tools/adg/generate_full_adg.py` |

_No further work unless regression._

---

## Wave 1 — Burndown truth & report UX (highest ROI)

**Problem:** `adg_burndown_table.json` / markdown label **“Diff vs prev”** does not match stored semantics (`diff` equals current `guardian` in-band); P0 aggregates **layer net + CRITICAL antipatterns** — easy to misread.

**Actions**

1. Rename or split `summary[*].diff` in `tools/generate/reporting/reports.py` (or fix renderer only) so prose matches data.  
2. Update `tools/reports/adg_burndown_report.py` headers + footnote for P0 composition.  
3. Unit tests: fixture SQLite/JSON proving `gross = net + guardian` for P0 layer slice.

**Verify:** `pytest` targeted; regenerate `adg_burndown_report.md` once.

---

## Wave 2 — Post-ADG subprocess reliability (Windows)

**Problem:** `check_exception_contract.py` / `check_test_harness_coverage.py` fail with `ModuleNotFoundError: tools` when spawned from `generate_full_adg` subprocess.

**Actions**

1. Add repo-root bootstrap (`sys.path` or `python -m ops_scripts.ci...`) in gate entrypoints **or** set `PYTHONPATH` in `_run_post_adg_gate` invoker.  
2. Smoke test: subprocess import of `tools.adg.shared_modules.path_resolver`.

**Verify:** `python tools/generate/generate_full_adg.py --continue-on-p0` completes post-ADG gates on Windows.

---

## Wave 3 — ADG pipeline schema integrity (A6 entrypoint)

**Problem:** `OperationalError: table nodes has no column named entrypoint_kind` — A6 scanner skipped.

**Actions**

1. Trace `entrypoint_scanner` + `nodes` DDL in artifact writer; add column or adjust scanner to current schema with migration note.  
2. Regression test: materialize + scanner on minimal fixture DB.

**Verify:** Full ADG log shows A6 not SKIPPED.

---

## Wave 4 — Guardian / exemption audibility (P1–P3 inference)

**Problem:** P1–P3 “guardian” counts are **inferred** from antipattern edges absent in `violations` — semantically weaker than P0 `allow-layer-violation` SSOT.

**Actions**

1. Document inference contract in `tools/generate/reporting/reports.py` module docstring + short `docs/reference/_notes/` note (optional).  
2. (Optional) Advisory gate: high `guardian`/gross ratio without test witness — calibrate before fail-closed.

**Verify:** ADG regen + human review of `adg_burndown_table.json` `provenance.counting_mode`.

---

## Wave 5 — v4 primer alignment (governance + signal)

**Primer:** `docs/reference/_primers/Python/Error & Exception Handling v4.md` — guardian = **approval** for risky patterns; **narrowing** beats tagging.

**Actions**

1. Policy note (short): map v4 columns → allowed `guardian: allow-*` + required companion (test / contract / ADR).  
2. Burndown/report extension (optional): “exemptions lacking test witness” slice — **signal first**, not hard FAIL until calibrated.  
3. Mechanical burndown backlog (separate child plan if large): prioritize `broad_exception_catch` / `silent_exception_swallow` in **high fan-in** files — **narrow tuples / domain exceptions** per v4.

**Verify:** trend in ratchet JSON + exception-contract gate history.

---

## Wave 6 — CI architecture & taxonomy UX (no DB rename tsunami)

**Goals**

1. **ADG CI dispatcher:** keep `unified_registry` SSOT; document which gates are **overlay** vs **base** (not MECE by design).  
2. **Three-bucket:** clarify **producer** (`generate_full_adg`: runtime view, registry lift, signing) vs **consumer** (`run_contract_gates` 3B1–3B7).  
3. **Harmonization recommendation:** keep **CRITICAL…LOW** in SQLite + **P0–P3** in gates/UI; display **`P2 (MEDIUM)`** pattern in dashboards; use `normalize_band()` for parsers; forbid third ladders (retired B/R/W).

**Verify:** Doc-only wave — peer review + optional ADR stub.

---

## Wave 7 — Optional hardening (defer if scoped)

| Item | Notes |
|------|--------|
| `adg_gates.run` H4 in-process migration | Reduces subprocess startup; larger blast radius |
| Single pinned `ADG_SNAPSHOT` per CI job | Log in gate manifest |
| Redis/MV projection alignment | Only if hot-cache consumers drift |

---

## Success criteria (program-level)

- [ ] Burndown markdown **never** labels a column in a way that contradicts JSON.  
- [ ] Post-ADG five-pack runs on Windows **without import errors**.  
- [ ] A6 entrypoint scanner **runs** (not SKIPPED) on clean regen.  
- [ ] Operators can explain **P-band vs Severity** in one sentence + link to `severity_bands.py`.  
- [ ] v4 alignment: visible **narrowing** workstream exists (child plan or backlog rows).

---

## References (in-repo)

- `agentic_core/adg/severity_bands.py` — Severity ↔ Band SSOT, `normalize_band`  
- `ops_scripts/ci/adg_gates/unified_registry.py` — ALL_GATES registry  
- `tools/adg/core/guardian_filter.py` — P0 layer exemption SSOT  
- `tools/generate/reporting/reports.py` — burndown aggregation  
- `docs/reference/_primers/Python/Error & Exception Handling v4.md`  
- `tools/notion/plan_creation_helper.py` — Notion Plans DB row creation

---

## Notion

Plans DB row created via `create_plan_in_notion` with **Plan File Path** = `.cursor/plans/adg-ci-guardian-hardening-consolidated-f8a2b1.md`.

- **Plans row (Notion):** https://www.notion.so/36127693f55c81af8619e1291f49c872  
- **Page ID:** `36127693-f55c-81af-8619-e1291f49c872`
