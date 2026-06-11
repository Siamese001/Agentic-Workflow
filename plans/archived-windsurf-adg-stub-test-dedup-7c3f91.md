---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\adg-stub-test-dedup-7c3f91.md'
original_relative_path: 'adg-stub-test-dedup-7c3f91.md'
source_sha256: a64d13fc4a709a8a2999d85ff7b7472de2a38460cd264fc18d3d7dc535554414
recovered_status: LOST_RECOVERED
last_commit: '6477883502e'
last_commit_date: '2026-04-27 08:55:24 -0400'
created_date: '2026-04-23'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# ADG Stub-Test Dedup — `_adg.py` Scaffold Archival

- **Plan ID**: `adg-stub-test-dedup-7c3f91`
- **Created**: 2026-04-23
- **Tier**: T2 (scoped archival; no production source edits)
- **Owner**: Cascade (autonomous execution approved by user)
- **Status**: Active
- **Driver**: Analysis in prior turn found 256 `_adg.py` scaffold tests in `tests/`, ≈78% of which are import-only stubs whose signal is already covered by ADG CI guards (`check_test_harness_coverage.py`, `check_exception_contract.py`, `check_expected_wiring.py`, `check_graph_island.py`).

## Goal

Archive (not delete) `_adg.py` scaffold tests that carry near-zero incremental signal over the ADG graph + CI guard surface, while preserving every production module's test-harness coverage (no new uncovered modules per `check_test_harness_coverage.py` baseline).

## Non-Goals

- No production source edits.
- No deletion (archival only — `tools/archive/stub_tests/<preserved_path>`).
- No change to ADG CI guards or `check_test_harness_coverage.py` baseline semantics.
- No touch to `tests/governance/`, `tests/guardian/`, `tests/ci/`, `tests/ops_scripts/ci/`, `tests/unit/ops_scripts/ci/`, `tests/e2e/`, `tests/integration/`.

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---:|---|---|---|
| W1 | W1.1, W1.2 | Build AST-based stub triage tool; classify all 256 `_adg.py` files | 6,000 | ADG snapshot healthy (optional; tool is pure-AST) | Todo | `artifacts/adg/stub_triage_report.json` emitted with per-file `stub|non-stub` label |
| W2 | W2.1 | Coverage-safety check: for each stub, verify a sibling non-`_adg` test exists OR the production module is already on `check_test_harness_coverage.py` allowlist/baseline | 3,000 | Sibling non-`_adg` test file naming follows `test_<mod>.py` vs `test_<mod>_adg.py` | Todo | `artifacts/adg/stub_archive_candidates.json` emitted; no production module loses its only test-import edge |
| W3 | W3.1 | Archive stubs to `tools/archive/stub_tests/<preserved_tests_path>` via `git mv`; preserve directory structure | 4,000 | `git mv` available; archive target directory writable | Todo | All candidate files moved; `pytest --collect-only` still succeeds; `check_test_harness_coverage.py` exits 0 |
| W4 | W4.1 | Verify: run `check_test_harness_coverage.py`, `check_graph_reach.py`, full `run_contract_gates.py` smoke; commit | 2,000 | Baselines unchanged | Todo | All gates green; commit pushed |
| W5 | W5.1 | Notion update + memory writeback | 1,500 | Notion/memory MCP healthy | Todo | Wave/Phase row updated to Done with final archive count |

Total est.: ≈16,500 tokens.

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---:|---|
| W1.1 | Build AST classifier | `tools/adg/adg_stub_triage.py` (new) | Must distinguish import-only stubs from tests with real behavioral assertions | 3,500 | Todo |
| W1.2 | Run classification | `tests/**/*_adg.py` (256 files) | Reading 256 files AST-parsed | 2,500 | Todo |
| W2.1 | Coverage safety filter | `artifacts/adg/stub_triage_report.json` + sibling-test lookup | Risk: archiving a stub whose production module has no other test file | 3,000 | Todo |
| W3.1 | Bulk archive | `git mv` stubs → `tools/archive/stub_tests/` | `git mv` across 200+ files must preserve history | 4,000 | Todo |
| W4.1 | Gate verification | `run_contract_gates.py` subset (harness coverage, graph reach, pytest collect) | Any gate failure = rollback wave | 2,000 | Todo |
| W5.1 | Notion + memory writeback | Notion Wave/Phase row; Memory `ProceduralPattern:StubTestDedupProtocol` | — | 1,500 | Todo |

## Stub Definition (AST heuristic — SSOT for this plan)

A `_adg.py` file is a **stub** if and only if ALL of:

1. Contains **≤ 5** `def test_*` functions; AND
2. Every test function body consists solely of statements matching these patterns:
   - `assert getattr(...) is not None`
   - `assert <name> is not None`
   - `assert callable(<name>)`
   - `assert isinstance(<name>, type)`
   - `assert <name>.__name__ == <literal>`
   - `pytest.importorskip(...)`
   - `monkeypatch.setenv(...)` (env-shim only)
   - simple class instantiation `<Cls>()` with no assertions on behavior
3. Has no fixtures beyond module-scoped `importorskip` shims.
4. Has a sibling non-`_adg` test file for the same module, OR the production module is already baseline-listed in `check_test_harness_coverage.py`.

Failing any of (1)–(3) → **non-stub**. Condition (4) gates archival (safety), not classification.

## ADG_GRAPH_LAYER_EVIDENCE (advisory — plan touches tests/ only)

This plan archives test-harness scaffolds; it does not refactor production code, so graph-layer MV evidence is not mandatory under rule §22. Evidence used for decision basis (from prior turn):

- `check_test_harness_coverage.py` — enforces every production module has ≥1 test-import edge; stubs with sibling real tests are redundant.
- `check_exception_contract.py` — enforces raise/catch symmetry via ADG `calls`/`imports` edges; covers "module imports/instantiates exception" better than `_adg.py` scaffolds.
- `check_expected_wiring.py` — enforces "X must call Y" structurally; covers "symbol exposed" better than `_adg.py` scaffolds.
- `check_graph_island.py` — enforces connected-component invariants; detects orphan modules that `_adg.py` scaffolds cannot.
- `check_graph_reach.py` + `check_graph_reach_archival.py` — enforce reachability; orthogonal to test-scaffold dedup.

## Rollback

Every phase is reversible:
- W3 archival uses `git mv` — reversible via `git mv` back.
- Worst case: `git revert <commit_range>` restores full pre-plan state.
- Gate baselines are **not** modified; no ratchet drift.

## Verification Commands

```
python tools/adg/adg_stub_triage.py classify --pattern "tests/**/*_adg.py" --json artifacts/adg/stub_triage_report.json
python tools/adg/adg_stub_triage.py archive-plan --input artifacts/adg/stub_triage_report.json --output artifacts/adg/stub_archive_candidates.json
python -m pytest --collect-only -q
python ops_scripts/ci/check_test_harness_coverage.py
python ops_scripts/ci/run_contract_gates.py
```

## Notion Row (Wave/Phase Convergence)

- **Phase Title**: `[P3] adg-stub-test-dedup W1 W1.1 — archive _adg.py scaffold tests redundant with ADG CI`
- **Wave**: `W1`, **Phase**: `W1.1..W5.1`
- **Plan File**: `adg-stub-test-dedup-7c3f91.md`
- **Status**: Todo → In Progress → Done (updated per phase)
