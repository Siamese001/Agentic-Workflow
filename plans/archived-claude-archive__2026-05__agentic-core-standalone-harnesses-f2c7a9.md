---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\2026-05\\agentic-core-standalone-harnesses-f2c7a9.md'
original_relative_path: '_archive\\2026-05\\agentic-core-standalone-harnesses-f2c7a9.md'
source_sha256: 131391c53b96732a3cdd6fc5d44e4911c12109ee08cc489f5024469d02f0543d
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Agentic-Core Standalone Runtime Harnesses — Eliminate apps_rg Overlay Dependency

> **Plan slug**: `agentic-core-standalone-harnesses-f2c7a9`
> **Plan path**: `.cursor/plans/agentic-core-standalone-harnesses-f2c7a9.md`
> **Parent plan**: `agentic-core-signoff-hardening-b8e2c4` (AUTHORITY.md §4 deferral)
> **Status**: Completed

PLAN_CREATED: slug=agentic-core-standalone-harnesses-f2c7a9 path=.cursor/plans/agentic-core-standalone-harnesses-f2c7a9.md

## 1. Background

76 of the 102 SIGNED_OFF rows in the agentic_core certification bundle draw their evidence
from `artifacts/certification/runtime/RTC-REQ-*/apps_rg_*` artifacts — i.e., the apps_rg
runtime acts as the integration harness for the agentic_core L0..L6 engine. Currently 0 rows
cite paths under the `agentic_core/` source tree directly.

This means:
- The agentic_core arm's SIGNED_OFF status is coupled to the apps_rg runtime remaining healthy.
- Per-layer agentic_core behavior is not independently provable without running apps_rg.
- Any apps_rg structural change risks invalidating agentic_core certification evidence.

This plan authors **per-layer standalone runtime harnesses** that exercise each agentic_core
layer (L0–L6) directly, emit assertion-valid evidence artifacts under
`artifacts/certification/runtime/agentic_core/`, and add corresponding rows to
`certification/evidence_assertions.jsonl` so the compiler can draw from native agentic_core
evidence paths.

Additionally, the git-commit divergence (bundle commit `34446a483bbe...` ≠ HEAD) is resolved
here by performing a clean rebuild at the end of the harness authoring work, when the working
tree is committed and HEAD is clean.

## 2. Scope

### 2.1 In scope

- Author per-layer standalone harnesses: L0 (routing), L1 (cognition), L2 (execution),
  L3 (orchestration), L4 (state), L5 (safety/HITL), L6 (observability).
- Each harness: runs the layer under test, emits an artifact at
  `artifacts/certification/runtime/agentic_core/<layer>/<harness_name>.json`, emits
  assertions in `certification/evidence_assertions.jsonl`.
- Commit working tree; rebuild at clean HEAD; re-sign; verify both verifiers exit 0.
- Update `certification/agentic_core/AUTHORITY.md` evidence-source breakdown (§2.3).

### 2.2 Out of scope

- Removing existing apps_rg evidence rows from the bundle (backward-compatible additive approach).
- L7 closure (separate plan `l7-route-family-closure-d3e8f1`).
- OTEL collector receipt (separate plan `otel-collector-cert-receipt-b4d2e6`).
- External Sigstore attestation.

### 2.3 Non-goals

- No changes to apps_rg package code.
- No breaking changes to existing assertion IDs or evidence artifacts.

## 3. Files In Scope

### Read
- `certification/requirements_source.json` (which requirements allow agentic_core artifact paths)
- `certification/evidence_assertions.jsonl` (existing assertions shape)
- `agentic_core/L{0..6}/` source files (to understand harness entry points)
- `tools/cert/` (existing harness patterns to follow)

### Write
- `tools/cert/agentic_core/harness_l{0..6}.py` (7 new harness scripts)
- `artifacts/certification/runtime/agentic_core/<layer>/<harness_name>.json` (evidence artifacts)
- `certification/evidence_assertions.jsonl` (new assertions)
- `certification/agentic_core/compiler_output/*` (rebuilt + signed bundle mirror)
- `certification/agentic_core/AUTHORITY.md` (§2.3 evidence-source breakdown updated)

## 4. Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Status | Success Criteria |
|------|-----------|-------|-------------|--------|------------------|
| W1 | P1.1 | Map which requirements allow agentic_core artifact paths; determine harness contract per layer | ~6k | Planned | Matrix: layer → requirements → required controls → allowed_artifact_classes + allowed_verifier_commands |
| W2 | P2.1–P2.7 | Author + run per-layer harnesses (L0–L6) | ~50k | Planned | Each layer: harness exits 0; evidence artifact on disk; assertions added |
| W3 | P3.1, P3.2 | Commit WT; clean rebuild at HEAD; verify git_dirty=False | ~4k | Planned | `git_dirty: False` in rebuilt report; bundle commit == HEAD |
| W4 | P4.1, P4.2 | Re-sign + verify both verifiers | ~3k | Planned | `trust_level: SIGNED_PROOF`; verifier PASS; signature VERIFIED |
| W5 | P5.1 | Update AUTHORITY.md + closeout report | ~4k | Planned | §2.3 updated; at least some rows cite agentic_core paths; closeout at `docs/reports/runtime_cert/standalone_harnesses/<YYYY-Www>.md` |

## 5. Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| P1.1 | Requirements mapping | `requirements_source.json`, existing assertion shape | Some requirements may only allow apps_rg artifact class; need to check `allowed_artifact_classes` per req | ~6k | Planned |
| P2.1–P2.7 | Per-layer harnesses (×7) | `tools/cert/agentic_core/harness_l{0..6}.py` | Layer entry points vary; some layers (L5 HITL) may need mock escalation path | ~7k each | Planned |
| P3.1 | Commit WT | git | 274 modified files — author-gate or stash before commit | ~2k | Planned |
| P3.2 | Clean rebuild | `scripts/compile_requirement_signoff.py` | Freshness windows; per-chain harnesses if needed | ~2k | Planned |
| P4.1–P4.2 | Re-sign + verify | signer + verifiers | git_dirty must be False | ~3k | Planned |
| P5.1 | AUTHORITY.md + closeout | `certification/agentic_core/AUTHORITY.md` | — | ~4k | Planned |

## 6. Author-Gate Decisions Foreseen

### AG-W3 — Commit strategy for 274-file dirty working tree

- **Trigger**: Start of W3 / P3.1.
- **Options**:
  - **A. Commit all 274 files** in a single chore commit.
  - **B. Stash + rebuild** at last clean HEAD (avoids a dirty commit, but stash is lossy for untracked files).
  - **C. Selective commit** — commit only the files needed for a clean cert rebuild; stash the rest.
- **Recommended**: C. Minimizes noise in the cert commit; preserves in-progress work on stash.

## 7. Success Criteria

- [ ] At least 7 new agentic_core-path evidence artifacts on disk (one per layer).
- [ ] New assertions accepted by compiler; at least some rows cite `agentic_core/` paths.
- [ ] `git_dirty: False` in rebuilt report; `git_commit` == HEAD at rebuild time.
- [ ] Bundle verifier PASS; signature VERIFIED; `trust_level: SIGNED_PROOF`.
- [ ] AUTHORITY.md §2.3 updated to reflect native agentic_core evidence rows.
- [ ] Closeout report at `docs/reports/runtime_cert/standalone_harnesses/<YYYY-Www>.md`.

## 8. References

- Parent plan `agentic-core-signoff-hardening-b8e2c4` — AUTHORITY.md §2.3 + §4 deferral
- `tools/cert/` — existing harness pattern reference
- Constitutional §32 (Fort Knox certification integrity)
- `certification/requirements_source.json` — controls + allowed_verifier_commands per requirement
