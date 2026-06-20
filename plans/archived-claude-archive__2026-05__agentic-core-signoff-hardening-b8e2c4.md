---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\2026-05\\agentic-core-signoff-hardening-b8e2c4.md'
original_relative_path: '_archive\\2026-05\\agentic-core-signoff-hardening-b8e2c4.md'
source_sha256: 26ad6200dcc80079009a618d8fcf79be36aa9ff1b214a5d1eae3e0e76b7b7050
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: agentic-core-signoff-hardening-b8e2c4
plan_type: audit
touches_agentic_core: false
touches_governance_ci: false
touches_windsurf_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
---

# Agentic-Core Signoff Hardening + Re-Curate

Re-curate the agentic_core certification bundle to address signature gaps, internal contradictions, and disclosure gaps. No source code changes — curation and documentation only.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: IN_PROGRESS
CURRENT_WAVE: W0
LAST_COMPLETED_WAVE: NONE
LAST_UPDATED: 2026-05-12

---

## Wave Overview

**Waves**: 4 total (W0–W4)
**Current**: W0 (planning + Notion registration)

**Wave Manifest**:
- **W0** — Planning and Notion registration | DONE
- **W1** — Bundle cleanup + rebuild | TODO
- **W2** — Signature application | TODO
- **W3** — OTEL reconcile path | TODO
- **W4** — L7 closure vs scope-out | TODO

PLAN_CREATED: slug=agentic-core-signoff-hardening-b8e2c4 path=.cursor/plans/agentic-core-signoff-hardening-b8e2c4.md

AG_QUEUE_SEED: plan=agentic-core-signoff-hardening-b8e2c4 id=AG-W3-otel-reconcile depends_on= title=OTEL replay 020/022 reconcile path (launch collector vs authority-manifest scope)
AG_QUEUE_SEED: plan=agentic-core-signoff-hardening-b8e2c4 id=AG-W4-l7-closure depends_on= title=L7 route-family 8-of-9 closure vs scope-out manifest

## Wave 0 — Planning

WAVE_ID: W0
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: Planning

**Phases**:
- **W0.1** — Notion registration | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

---

## Wave 1 — Bundle Cleanup + Rebuild

WAVE_ID: W1
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: A

**Phases**:
- **W1.1** — Quiesce working tree | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W1.2** — Capture clean HEAD | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W1.3** — Rebuild signoff reports | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

---

## Wave 2 — Signature Application

WAVE_ID: W2
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: B

**Phases**:
- **W2.1** — Apply ed25519 signer to agentic_core arm | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W2.2** — Verify signature | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

---

## Wave 3 — OTEL Reconcile Path

WAVE_ID: W3
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: REQUIRED
CHECKPOINT: C

**Authorization Required**: W3 has 2 declared Author-Gate decisions on OTEL reconcile path.

**Phases**:
- **W3.1** — Reconcile RTC-REQ-020 + RTC-REQ-022 | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

---

## Wave 4 — L7 Closure vs Scope-Out

WAVE_ID: W4
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: REQUIRED
CHECKPOINT: D

**Authorization Required**: W4 has Author-Gate decision on L7 route-family 8-of-9 closure.

**Phases**:
- **W4.1** — L7 closure decision | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W4.2** — Authority manifest update | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

---

## 1. Background

The `artifacts/certification/` bundle for the agentic_core arm shows `102/102 SIGNED_OFF` and `bundle_verification_status: PASS (2449 checks)`, but a hostile-reviewer audit found four classes of defect that survive any re-packaging:

1. **Unsigned arm.** `final_requirement_signoff_report.signature.json` is `UNSIGNED_PENDING_SIGNATURE` with `signer_identity: null`, `signature_algorithm: null`. The sibling apps_e2e arm IS signed (ed25519 VERIFIED, signer `DEVELOPMENT_SIGNER:ed25519:f8dbd2c42e377626`).
2. **Internal contradiction.** `rtc_req_otel_replay_report.json` marks RTC-REQ-020 + RTC-REQ-022 `BLOCKED` (missing external OTEL collector receipt + missing metric delta report), yet the same compile run marks both `SIGNED_OFF` in `final_requirement_signoff_report.json`.
3. **Three-way commit divergence.** Bundle `git_commit: 34446a48...`, per-chain spine proofs at `87663889...` and `bb44b389...`, current HEAD `705478d3...`, and 274 modified files in WT.
4. **Disclosure gap.** Per-chain proofs uniformly report `l7_route_family_coverage_summary: {certified: 1, fixture_only: 1, not_certified: 8, total: 9}`. The agentic_core arm draws 76/102 rows from `apps_rg/` overlay evidence and 0 rows from paths under `agentic_core/`. Neither fact is surfaced in any top-level claim.

Pure re-curation closes only stale-artifact-in-bundle and missing-arm visibility. Items 1–4 require hardening or explicit scope declaration.

## Definition of Done

DoD-1: Working tree quiesced and clean HEAD captured
- Evidence: Single source-of-truth commit documented
- Status: TODO

DoD-2: Signoff reports rebuilt
- Evidence: final_requirement_signoff_report files regenerated
- Status: TODO

DoD-3: Signature applied and verified
- Evidence: signature.json shows VERIFIED, trust_level=SIGNED_PROOF
- Status: TODO

DoD-4: OTEL reconcile resolved
- Evidence: RTC-REQ-020 + RTC-REQ-022 consistent state
- Status: TODO

DoD-5: Authority manifest authored
- Evidence: certification/agentic_core/AUTHORITY.md exists
- Status: TODO

---

## 2. Scope

### 2.1 In scope

- Quiesce working tree, capture single clean HEAD as the bundle's source-of-truth commit.
- Rebuild `final_requirement_signoff_report.{json,sha256,merkle.json,md,xlsx}` against that commit.
- Apply the existing ed25519 signer to the agentic_core arm; produce a populated `final_requirement_signoff_report.signature.json` with `signature_verification_status: VERIFIED`, lifting `trust_level` to `SIGNED_PROOF`.
- Reconcile RTC-REQ-020 + RTC-REQ-022 (OTEL replay BLOCKED vs final-report SIGNED_OFF) by one of two declared paths.
- Author `certification/agentic_core/AUTHORITY.md` declaring authoritative reports, superseded artifacts, scope, and explicit deferrals.
- Re-curate `certification/agentic_core/` to mirror the rebuilt + signed canonical bundle plus apps_e2e arm + L7 evidence dirs + 9 per-chain proofs + the new authority manifest.

### 2.2 Out of scope (deferred with disclosure)

- L7 route-family closure for the remaining 8/9 not_certified families (deferred to its own plan; this plan declares scope, does not close).
- Structural elimination of `apps_rg/` overlay dependency for the 76 affected rows (deferred; per-component agentic_core runtime harnesses are a separate program).
- Promotion to `FINAL_SIGNED_CERTIFICATION` (requires Sigstore/cosign keyless under GitHub OIDC; bundle's own `GAP-2_external_attestation` already documents this and marks it `blocks_100pct_runtime: false`).

### 2.3 Non-goals

- No app-behavior changes.
- No source-code edits to `agentic_core/` or `apps_*` packages.
- No new CI gates beyond what is needed to verify the rebuilt bundle.

## 3. Files In Scope

### Read

- `artifacts/certification/final_requirement_signoff_report.json`
- `artifacts/certification/final_requirement_signoff_report.signature.json`
- `artifacts/certification/final_requirement_signoff_bundle_verification.json`
- `artifacts/certification/rtc_req_otel_replay_report.json`
- `artifacts/certification/HUNDRED_PERCENT_RUNTIME_PROOF.json`
- `artifacts/certification/apps_e2e/apps_e2e_signoff_report.signature.json` (signer reference shape)
- `artifacts/certification/integrated_runtime/*_latest/agentic_core_spine_proof.json` (9 per-chain proofs)
- `artifacts/certification/agentic_core_e2e/agentic_core_spine_proof.json` (stale; to be quarantined)
- `certification/evidence_assertions.jsonl`
- `certification/agentic_core/source_inputs/evidence_assertions.jsonl` (mirror)
- `scripts/compile_requirement_signoff.py`
- `scripts/verify_final_requirement_signoff_bundle.py`
- `tools/cert/apps_e2e/sign_with_ephemeral_key.py` (signer to retarget)
- `config/release_signer/release_signer.pub.pem`
- `docker-compose.otel.yml` (if W3 chooses honest path)

### Write (planning + curation only; no source-code edits)

- `certification/agentic_core/AUTHORITY.md` (new)
- `certification/agentic_core/compiler_output/*` (re-curate, mirror rebuilt artifacts)
- `certification/agentic_core/e2e/*` (re-curate, drop or quarantine stale spine proof)
- `certification/agentic_core/integrated_runtime/*_latest/*` (re-curate, copy 9 per-chain proofs)
- `certification/agentic_core/apps_e2e_arm/*` (new subfolder; copy signed apps_e2e bundle)
- `docs/reports/runtime_cert/agentic_core_signoff_hardening/<YYYY-Www>.md` (closeout report at plan end)

### Tests

- No new tests authored. Verification is via existing scripts:
  - `scripts/verify_final_requirement_signoff_bundle.py` (must exit 0 with VERIFIED signature)
  - `tools/cert/apps_e2e/verify_apps_release_signature.py` (must exit 0 against rebuilt bundle's signature)

## 4. Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1 | P1.1, P1.2 | Quiesce WT + clean rebuild against single HEAD | ~6k | `git stash` is safe; modified files are not required for compile inputs | Planned | Bundle git_commit == HEAD; bundle verifier 2449 checks PASS; report row count unchanged at 102 |
| W2 | P2.1, P2.2 | Sign agentic_core arm with existing ed25519 signer | ~4k | `tools/cert/apps_e2e/sign_with_ephemeral_key.py` (or sibling) is retargetable; `release_signer.pub.pem` is the canonical key | Planned | `signature_verification_status: VERIFIED`; `signer_identity` populated; `trust_level: SIGNED_PROOF`; `verify_final_requirement_signoff_bundle.py` exit 0 |
| W3 | P3.1 (Author-Gate), P3.2 (chosen path) | Reconcile RTC-REQ-020 + RTC-REQ-022 OTEL contradiction | ~6k–12k (path-dependent) | One of two paths approved at P3.1 | Planned | Either OTEL collector receipts on disk + `rtc_req_otel_replay_report.json` regenerated to PASS; OR authority manifest declares alternative evidence chain for 020/022 with explicit assertion ID citations |
| W4 | P4.1 (Author-Gate), P4.2 (chosen path) | L7 1/9 + apps_rg overlay disclosure | ~4k–8k | Per-chain proofs already self-declare 8/9 not_certified; disclosure is the minimum bar | Planned | Authority manifest names L7 scope (1/9 certified, 8/9 deferred to plan `<L7-closure-slug>`); names apps_rg overlay as approved evidence path with row-by-row disclosure |
| W5 | P5.1 | Author authority manifest `certification/agentic_core/AUTHORITY.md` | ~5k | W2/W3/W4 produced their inputs | Planned | Manifest declares authoritative vs superseded reports; declares scope (L0..L6 + 1/9 L7); declares deferrals; cites assertion IDs and successor plan slugs |
| W6 | P6.1, P6.2 | Re-curate `certification/agentic_core/` + verify | ~5k | Rebuilt + signed bundle is on disk | Planned | Folder mirrors canonical artifacts + apps_e2e arm + 9 per-chain proofs + authority manifest; both verifiers exit 0; closeout report written |

## 5. Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| P1.1 | Quiesce working tree | git stash on 274 modified files; capture HEAD as `BUNDLE_COMMIT` | None expected; pure mechanical | ~2k | Planned |
| P1.2 | Clean rebuild of agentic_core arm | Re-run `scripts/compile_requirement_signoff.py`; re-run per-chain runtime harnesses if cheap; re-run `scripts/verify_final_requirement_signoff_bundle.py` | Per-chain runtime harnesses may be expensive; W1 may pin to compile-only and accept per-chain proofs at last good commit (declare in manifest) | ~4k | Planned |
| P2.1 | Locate + retarget signer | Read `tools/cert/apps_e2e/sign_with_ephemeral_key.py` shape; identify whether it is parameterized over input path or hard-coded to apps_e2e | Signer may be apps_e2e-specific and require a thin wrapper; if so, write a one-shot retarget script under `tools/cert/agentic_core_arm/sign_signoff.py` | ~2k | Planned |
| P2.2 | Sign agentic_core final report | Produce populated `final_requirement_signoff_report.signature.json`; verify with bundle verifier | Trust level transitions from `INTEGRITY_PROOF` to `SIGNED_PROOF`; ensure addendum claims that already say `SIGNED_PROOF` now match canonical signature state | ~2k | Planned |
| P3.1 | Author-Gate: OTEL reconcile path | Decision packet between (A) launch `docker-compose.otel.yml` + regenerate replay PASS, vs (B) authority-manifest scope-out with alternative-evidence row-by-row citations | Path A may surface deeper infra gaps; Path B is cheaper but reviewer-visible | ~2k | Planned |
| P3.2 | Execute chosen OTEL path | Per AG-W3 decision: collector launch + recompile, OR manifest authoring | Path A: docker availability, collector wiring; Path B: assertion-ID lookup correctness | ~4k–10k | Planned |
| P4.1 | Author-Gate: L7 closure-vs-scope-out | Decision packet between (A) author L7 closure plan now and chain it to W4, vs (B) scope-out in this plan and chain a successor plan slug | Path A delays signoff hardening; Path B accepts 1/9 L7 disclosure with deferred closure | ~2k | Planned |
| P4.2 | Execute chosen L7 path | Per AG-W4 decision: chain a new plan, OR add scope-out section to authority manifest | Either way, apps_rg overlay disclosure (item 4 of background) lands in same manifest | ~3k–6k | Planned |
| P5.1 | Author `certification/agentic_core/AUTHORITY.md` | New file; declares: authoritative reports list, superseded artifacts list, scope statement, deferral list with successor plan slugs, assertion-ID citations for 020/022 if Path B at W3, evidence-source breakdown (76 apps_rg / 26 spine-scanner / 0 agentic_core paths) with rationale | First time this manifest exists; precedent shape borrowed from `certification/README_REVIEW.md` | ~5k | Planned |
| P6.1 | Re-curate `certification/agentic_core/` | Mirror rebuilt + signed bundle into `compiler_output/`, drop or quarantine stale outer e2e proof, copy 9 per-chain proofs into `integrated_runtime/`, add new `apps_e2e_arm/` subfolder with signed apps_e2e bundle, copy `AUTHORITY.md` to root | None expected; pure file ops | ~3k | Planned |
| P6.2 | Verification + closeout report | Both verifiers exit 0; write `docs/reports/runtime_cert/agentic_core_signoff_hardening/<YYYY-Www>.md`; emit `WAVE_COMPLETE:` for each closed wave | Closeout report follows the apps-eval-harness-deferred precedent (markdown only) | ~2k | Planned |

## 6. Author-Gate Decisions Foreseen

### AG-W3 — OTEL replay 020/022 reconcile path

- **Trigger**: Start of W3 / P3.1.
- **Options**:
  - **A. Launch OTEL collector + regenerate**: `docker-compose -f docker-compose.otel.yml up`, run probe, produce `artifacts/certification/otel_collector_receipt.json` + `artifacts/certification/otel_metric_delta_report.json`, recompile bundle. Strongest evidence, highest cost.
  - **B. Authority-manifest scope-out**: declare in `AUTHORITY.md` that `rtc_req_otel_replay_report.json` is the OTEL-collector sub-claim only; cite the alternative assertion IDs that actually back RTC-REQ-020 and RTC-REQ-022 in the SIGNED_OFF rows; mark Wave-C external collector as deferred. No collector launch.
  - **C. Hybrid**: do (B) now; create a chained plan to do (A) in the next bundle revision.
- **Recommended**: B if (b1) the SIGNED_OFF rows for 020/022 cite assertion IDs that resolve cleanly to non-OTEL-collector evidence and (b2) reviewer audience accepts declared scope. Else C.

### AG-W4 — L7 1/9 closure-vs-scope-out

- **Trigger**: Start of W4 / P4.1.
- **Options**:
  - **A. Close L7 8/9 now**: chain a new plan and complete L7 certification for the 8 not_certified route families before closing this plan.
  - **B. Scope-out in `AUTHORITY.md`**: declare bundle scope as L0..L6 spine + 1/9 L7; chain a successor plan slug for the remaining 8 families; close this plan with disclosure intact.
- **Recommended**: B. Per-chain proofs already self-declare 8/9 not_certified; concealment is impossible; declared scope is the honest move; closing 8 L7 families is a multi-week program that should not block this hardening pass.

## 7. ADG_GRAPH_LAYER_EVIDENCE

This is a **certification-bundle hardening + curation plan**, not a refactoring plan, so constitutional §22 graph-layer-primary-driver requirements (mv_*, semantic edges, P-views) do not apply. No source-code refactor is in scope. The plan does not modify imports, layer assignments, or call graphs.

For completeness: the agentic_core arm's static enforcement claims (30 STATIC_ENFORCEMENT + 1 STATIC_CONTRACT) already cite `layer_boundary_report_csv_gate.json` and `layer_boundary_report_runtime_acceptance.json` as evidence. Those reports are products of ADG-driven layer scanners. This plan preserves them unchanged in the rebuild.

## 8. Risk Register

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| `git stash` loses uncommitted work | Low | Medium | Stash with named label; document recovery command in P1.1 |
| Per-chain runtime harnesses are expensive to re-run | Medium | Low | Pin to last-known-good per-chain proofs; declare commit divergence in `AUTHORITY.md` instead of forcing a full re-run |
| Signer is apps_e2e-specific and not retargetable | Medium | Medium | Write thin wrapper `tools/cert/agentic_core_arm/sign_signoff.py`; reuse same key + algorithm |
| OTEL collector launch (Path A) surfaces additional gaps | Medium | Medium | Default to Path B unless reviewer audience requires Path A |
| Authority manifest scope declaration is rejected by reviewer | Low | Medium | Manifest cites assertion IDs and per-chain proofs verbatim; disagreement becomes about scope, not internal consistency |
| Bundle verifier fails after re-sign due to canonicalization drift | Low | High | Verify with `verify_final_requirement_signoff_bundle.py` immediately after sign; if fail, do not proceed to W6 |

## 9. Success Criteria (plan-level)

- [ ] `final_requirement_signoff_report.signature.json` shows `signature_verification_status: VERIFIED`, `signer_identity` populated, `trust_level: SIGNED_PROOF` on the agentic_core arm.
- [ ] `final_requirement_signoff_bundle_verification.json` shows `bundle_verification_status: PASS` against the rebuilt bundle, with `signature_verification_status: VERIFIED`.
- [ ] Bundle `git_commit` == current HEAD at rebuild time; `git_dirty: false`.
- [ ] RTC-REQ-020 + RTC-REQ-022 contradiction resolved per chosen W3 path; `AUTHORITY.md` documents the resolution.
- [ ] `AUTHORITY.md` exists at `certification/agentic_core/AUTHORITY.md` and declares: authoritative reports, superseded artifacts (incl. stale outer e2e spine proof), scope (L0..L6 + 1/9 L7), evidence-source breakdown, deferrals with successor plan slugs.
- [ ] `certification/agentic_core/` mirrors the rebuilt + signed canonical bundle, includes the apps_e2e signed arm under `apps_e2e_arm/`, includes 9 per-chain proofs, includes the L7 evidence directory.
- [ ] Closeout report at `docs/reports/runtime_cert/agentic_core_signoff_hardening/<YYYY-Www>.md` written with all section requirements per plan §5.

## 10. Notion Registration

- **Plans DB**: page registered with `Slug = agentic-core-signoff-hardening-b8e2c4`, `Status = Draft`, `Exists On Disk = true`, `Plan File Path = .cursor/plans/agentic-core-signoff-hardening-b8e2c4.md`, bullet-style `AI Summary `.
- **Lifecycle**: Draft → Live (when execution starts) → Completed (when all 6 waves close + closeout report written).

## 11. References

- Constitutional §32 (Fort Knox certification integrity, two arms — agentic_core + apps_e2e)
- Constitutional §36 (plan registration enforcement)
- `.cursor/rules/fortknox-certification-discipline.md`
- `.cursor/skills/fortknox-evidence/SKILL.md`
- Sibling apps_e2e signer + verifier (`tools/cert/apps_e2e/`)
- Bundle's own `GAP-2_external_attestation` declaration in `HUNDRED_PERCENT_RUNTIME_PROOF.json` (caps signed-arm trust at SIGNED_PROOF until cosign)
- Audit findings dated 2026-05-03 (pre-plan analysis in conversation; not committed as ADR pending plan completion)
