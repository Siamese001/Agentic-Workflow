---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\ci-hardening-dedup-a8c4f1__dup434.md'
original_relative_path: 'ci-hardening-dedup-a8c4f1__dup434.md'
source_sha256: 94b86582c3f1064b59628810b9444de37e77efa8021e69e63d296cacaa3dd202
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Plan: CI Hardening and Deduplication

**Slug:** `ci-hardening-dedup-a8c4f1`
**Status:** Completed
**Created:** 2026-05-05

## Summary

Hardened and deduplicated the CI pipeline by analyzing the pre-commit config, ADG CI gates, and Windsurf Cascade CI. Eliminated true redundancy without weakening intentional layered coverage. Fixed all stale Windsurf hook working_directory paths. Expanded trigger regexes. Reclassified expensive commit-time gates. Promoted manual-only gates to CI. Added freshness checks for Cascade hook violation logs.

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|-----------------|
| W1 | H2, H7 | Remove true CI duplicate; verify intentional two-lane | ~500 | Duplicate confirmed by inspection | ✅ DONE | No duplicate in same plane |
| W2 | H20 | Fix stale hooks.json paths + extend schema gate | ~1000 | All 35 entries used stale path | ✅ DONE | All hooks.json entries pass schema gate |
| W3 | H25, H26, H15, H23, H24 | Fix trigger gaps; demote expensive gate; fix name collisions | ~800 | Pre-commit YAML inspection | ✅ DONE | Trigger regexes match all owned files |
| W4 | H22 | Promote 4 manual gates to CI assurance plane | ~400 | Gates stable at 0 violations | ✅ DONE | 4 scripts in assurance_gates |
| W5 | H17, H18 | New freshness CI gates for Cascade violation logs | ~600 | Log paths confirmed from hook scripts | ✅ DONE | CF1/CF2 scripts created and registered |
| W6 | H8 | Two-lane comments; acceptance tests | ~800 | All prior waves complete | ✅ DONE | 36/36 tests pass |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| H2 | Remove duplicate schema gate from assurance_gates | ops_scripts/ci/run_contract_gates.py | Duplicate invocation in same CI plane | ~150 | ✅ Done |
| H7 | Verify spine delegation two-lane | run_contract_gates.py | Confirmed intentional, no change | ~50 | ✅ Done |
| H20 | Fix stale hooks.json working_directory paths | .windsurf/hooks.json, ops_scripts/ci/check_windsurf_config_schema.py | 35 entries pointed to wrong repo clone — ALL hooks silently failing | ~500 | ✅ Done |
| H25 | Fix HITL corpus trigger regex | .pre-commit-config.yaml | Trigger only matched hitl-*.md; missed author-gate-enforcement.md etc. | ~150 | ✅ Done |
| H26 | Fix ledger-schema trigger DDL gap | .pre-commit-config.yaml | DDL file mentioned in description but absent from files: regex | ~100 | ✅ Done |
| H15 | Demote runtime-certification to manual-only | .pre-commit-config.yaml | Gate ran on every commit (~12s); CI wiring_gates is authoritative | ~100 | ✅ Done |
| H23 | Fix T7e label collision | .pre-commit-config.yaml | hitl-rules-corpus labelled T7e, same as author-gate-ledger-coverage | ~50 | ✅ Done |
| H24 | Fix T6d label collision | .pre-commit-config.yaml | agents-md-autogen-sync labelled T6d, same as author-gate-ledger-schema | ~50 | ✅ Done |
| H22 | Promote 4 manual gates to assurance plane | run_contract_gates.py | OTEL coverage, required spans, apps_shared purity, PII telemetry | ~200 | ✅ Done |
| H17 | Create ADG-first violations freshness gate (CF1) | ops_scripts/ci/check_adg_first_violations_freshness.py | No CI backstop for Cascade hook log | ~300 | ✅ Done |
| H18 | Create MCP serialization violations freshness gate (CF2) | ops_scripts/ci/check_mcp_serialization_violations_freshness.py | No CI backstop for Cascade hook log; TTL-aware | ~300 | ✅ Done |
| H8 | Two-lane comments + acceptance tests | .pre-commit-config.yaml, tests/unit/ops_scripts/ci/test_ci_hardening_2026_05_05.py | 36 acceptance tests covering all hardening items | ~800 | ✅ Done |

## Gap Register

None — all items delivered this session.

## Files Modified

- `.windsurf/hooks.json` — corrected all 35 stale working_directory values
- `ops_scripts/ci/check_windsurf_config_schema.py` — added `_validate_working_directory()`
- `ops_scripts/ci/run_contract_gates.py` — removed duplicate; promoted 4 manual gates + 2 freshness gates
- `.pre-commit-config.yaml` — H25/H26/H15/H23/H24 + two-lane comments

## Files Created

- `ops_scripts/ci/check_adg_first_violations_freshness.py` (CF1)
- `ops_scripts/ci/check_mcp_serialization_violations_freshness.py` (CF2)
- `tests/unit/ops_scripts/ci/test_ci_hardening_2026_05_05.py` (36 tests, all green)

## Acceptance Criteria

- [x] No duplicate gate in the same CI plane
- [x] `check_windsurf_config_schema.py` in `wiring_gates` only
- [x] Live `hooks.json` passes schema gate (all paths corrected)
- [x] Stale absolute path → gate fails; correct path → gate passes
- [x] HITL corpus trigger covers all 4 validator files
- [x] Ledger-schema trigger covers the DDL file
- [x] `runtime-certification` is manual-only in pre-commit
- [x] 4 promoted scripts appear in `assurance_gates`
- [x] CF1/CF2 `evaluate()` logic is correct (bypass, resolved, aged-out, fresh)
- [x] 36/36 acceptance tests pass
