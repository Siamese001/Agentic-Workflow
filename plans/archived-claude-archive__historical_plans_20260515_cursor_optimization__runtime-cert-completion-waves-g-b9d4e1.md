---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\historical_plans_20260515_cursor_optimization\\runtime-cert-completion-waves-g-b9d4e1.md'
original_relative_path: '_archive\\historical_plans_20260515_cursor_optimization\\runtime-cert-completion-waves-g-b9d4e1.md'
source_sha256: aa77a796550d8ca1f9654410af617924e780f883687dc851c049251a4c1a730e
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Runtime Certification — Completion Wave G

**Plan slug**: `runtime-cert-completion-waves-g-b9d4e1`
**Status**: DONE 2026-05-01T20:37 UTC — 63 SIGNED_OFF / 24 BLOCKED / 0 NOT_VERIFIED
**Created**: 2026-05-01T20:30 UTC
**Predecessor**: `runtime-cert-formula-driven-signoff-a8f5c2` (closed)

---

## 1. Goal

Drive remaining 31 NOT_VERIFIED rows to closure by mapping each to:
- **Existing PASS verifier output** → SIGNED_OFF (formula-derived)
- **Existing FAIL verifier output** → BLOCKED with attribution

No row may end in NOT_VERIFIED state — every row gets a formula-derived verdict backed by evidence inputs (per architecture established in plan `formula-driven-signoff-a8f5c2`).

---

## 2. Wave Structure

| Wave | Focus | Reqs | Status | Outcome |
|---|---|---:|---|---|
| **G1** | Sign off rows backed by PASSing verifiers + on-disk reports | 12 | **DONE 20:34 UTC** | RTC-REQ-072, 092, 095, 096, 100, 101, 102, 103, 114, 121, 122, 124 → SIGNED_OFF |
| **G2** | Sign off rows backed by tier/UWG/control-surface artifacts | 12 | **DONE 20:36 UTC** | RTC-REQ-060, 065, 066, 070, 071, 073, 082, 091, 093, 094, 097, 120 → SIGNED_OFF |
| **G3** | BLOCKED with attribution (8 rows) — tier_gate_hardening errors + missing CI gates + collector dependency | 8 | **DONE 20:36 UTC** | RTC-REQ-080, 081, 083, 084, 090, 112, 113, 115 → BLOCKED |
| **G4** | tier0 step1 source bootstrap + refined BLOCKED attribution | 6 | **DONE 20:49 UTC** | `tools/cert/bootstrap_tier0_step1_sources.py` authored; tier_gate_hardening 79 errors → 53 PASS + 26 fail; tier1/3/4/5/6 enforcement & runtime gates now PASS exit=0 |

**Total reqs touched**: 32 (G1: 12 + G2: 12 + G3: 8). All 31 NOT_VERIFIED + 1 mis-classified BLOCKED (RTC-REQ-124) re-evaluated.

---

## 3. Final Sign-Off Rollup

**Before plan G**: 39 SIGNED_OFF / 17 BLOCKED / 31 NOT_VERIFIED
**After plan G**:  **63 SIGNED_OFF / 24 BLOCKED / 0 NOT_VERIFIED**

Net change: **+24 SIGNED_OFF**, +7 BLOCKED, -31 NOT_VERIFIED.

| Verification | Result |
|---|---|
| `verify_formula_against_evidence.py` | **PASS — 87/87 match** |
| `verify_rtc_req_csv_gate.py` | READY (rollup={63 SIGNED_OFF, 24 BLOCKED}) |
| `verify_runtime_certification_acceptance.py` | PASS (legal=87 illegal=0) |
| `verify_control_surface_separation.py` | PASS (0 violations) |

---

## 4. The 24 BLOCKED rows — operator gates inventory

| Cluster | Reqs | Operator gate to unblock |
|---|---|---|
| **OTEL collector infrastructure** | 020, 022, 057, 113 | External collector exporter receipt + counter delta export |
| **API keys (Gemini + Anthropic + OpenAI)** | 056, 058, 059 | Set env vars + run `probe_integrated_runtime_safe_reuse.py` |
| **R1B operator gates (model proof + threshold ADR + calibration)** | 044, 045, 046, 125, 126, 129 | EMBEDDING_ENABLED=true + threshold ADR + BGE-M3 calibration data |
| **Component runtime cache claims (R1A surface)** | 041, 042, 043 | Wave D follow-up — seed/live form, L1 exact miss, vector compare |
| **Tier-gate hardening verifier (79 errors)** | 080, 081, 083, 084 | Populate `requirements_index` with tier-gate-hardening claim rows |
| **Tier0 enforcement** | 090 | Restore `artifacts/runtime/requirements_proof/tier0_*` in this checkout |
| **Cross-checkout dep (apps_rg integrated runtime)** | 128 | Same dep as 010..015 (already SIGNED_OFF in R1B; 128 expects gate verdict bundle consumption) |
| **CI gates not yet authored** | 112, 115 | New `pre-commit` entries + tier_gate_hardening fix |
| **Source binding edge case** | (none — 124 unblocked by formula) | — |

---

## 5. Files modified

| Path | Change |
|---|---|
| `@c:/Git/Agentic-Workflow-FRESH/tools/cert/sync_csv_from_formula.py` (new) | Sync CSV signoff_status FROM XLSX formula output (mirrors formula in pure Python) |
| `C:\Users\amita\Downloads\...hardened.csv` | 32 rows updated (12 G1 + 12 G2 + 8 G3) |
| `C:\Users\amita\Downloads\...hardened_FULL_OVERWRITE.xlsx` | 32 rows × evidence-input cells populated; formulas re-derive sign-off |

## 6. Receipts

- `artifacts/certification/csv_signoff_updates/2026-05-01T20-34-21+00-00_evidence_G1-existing-artifact-signoff.json`
- `artifacts/certification/csv_signoff_updates/2026-05-01T20-35-23+00-00_csv_from_formula.json`
- `artifacts/certification/csv_signoff_updates/2026-05-01T20-36-23+00-00_evidence_G2-tier-and-uwg-signoff.json`
- `artifacts/certification/csv_signoff_updates/2026-05-01T20-36-52+00-00_evidence_G3-block-with-attribution.json`
- `artifacts/certification/csv_signoff_updates/2026-05-01T20-37-00+00-00_xlsx_sync.json`
- `artifacts/certification/formula_verification_report.json` (latest, overall=PASS)

## 7. tier_gate_hardening investigation outcome (G4)

### What the bootstrap fixed

`tools/cert/bootstrap_tier0_step1_sources.py` materializes the 6 source JSONs that `tier0_step1_metadata.generate()` requires. These were previously gitignored and authored by a "prior linkage-metadata step" that lives outside this checkout. The bootstrap moves the verifier from:

| Verifier | Before bootstrap | After bootstrap |
|---|---|---|
| `verify_tier_gate_hardening.py` | 79 fixture errors (cannot collect) | **53 PASS / 26 FAIL** |
| `verify_tier0_enforcement_gate.py` | exit=1 (FileNotFoundError) | exit=1 (BLOCKED on residual blockers — see below) |
| `verify_tier1_enforcement_gate.py` | exit=0 | exit=0 |
| `verify_tier3..tier6_enforcement_gate.py` | exit=0 each | exit=0 each |
| `verify_tier1, 3, 4, 5, 6_runtime_proof_gate.py` | exit=0 each | exit=0 each |
| `verify_tier0_runtime_proof_gate.py` | exit=1 | exit=1 (depends on tier0 enforcement) |

### Why the 6 target rows stay BLOCKED

`tier0_enforcement_gate_result.json` shows after bootstrap:

```
result: BLOCKED
blocked_count: 11 (of 17)
blocker_counts:
  NEEDS_TEST_MAPPING: 11
  NEEDS_ARTIFACT_FIELD: 10
  NEEDS_REPLAY_FIELD: 7
blocking_status_counts: {LINKED_CONCEPTUAL: 11}
reasons: ['11 REQ_IDs have blockers or non-ready linkage_status']
```

The remaining gap is **not** in the bootstrap — it's in `tier0_step1_metadata.py`'s hardcoded reference dicts (`TEST_REFERENCES`, `ARTIFACT_REFERENCES`, `REPLAY_REFERENCES`). Those dicts only cover 6 of 17 Tier-0 reqs. Closing the gap requires authoring real test/artifact/replay file paths for the remaining 11 reqs.

### Updated unblock recipe for the 6 rows

| Req | Required action |
|---|---|
| **RTC-REQ-080, 081** | Extend `tier0_step1_metadata.TEST_REFERENCES` to bind the 11 missing Tier-0 reqs (the `gate_schema` reqs already have refs; the rest don't) |
| **RTC-REQ-083** | Fix `TestTier0RuntimeProofGateFailsClosed::test_artifact_efr_mismatch_blocks` — runtime proof gate must detect EFR mismatches in artifact files (this is product hardening, not metadata) |
| **RTC-REQ-084** | Same root cause as 083 — runtime proof gate must enforce no-bypass mutation suite |
| **RTC-REQ-112** | Author `scripts/check_semantic_cache_ci_gate.py` + add to `.pre-commit-config.yaml`. Independent of tier_gate_hardening. |
| **RTC-REQ-115** | Author `scripts/check_no_bypass_mutation_ci_gate.py`. Same shape as 112. |

Net assessment: 080 + 081 are unblockable by **extending tier0_step1_metadata reference dicts** (~1-2 hours of binding work). 083 + 084 require **runtime proof gate hardening** (product code change). 112 + 115 require **new CI gate scripts** (~30 min each, independent).

## 8. Files created (G + G4)

| Path | Purpose |
|---|---|
| `@c:/Git/Agentic-Workflow-FRESH/tools/cert/sync_csv_from_formula.py` | Mirror XLSX formula in Python; sync CSV `signoff_status` from formula output |
| `@c:/Git/Agentic-Workflow-FRESH/tools/cert/bootstrap_tier0_step1_sources.py` | Materialize 6 tier0 source JSONs that `tier0_step1_metadata.generate()` needs (otherwise gitignored and missing from this checkout) |
| `@c:/Git/Agentic-Workflow-FRESH/artifacts/runtime/requirements_proof/tier0_*.json` (6 files) | Bootstrap output — survives until canonical authoring step lands |
