---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\historical_plans_20260515_cursor_optimization\\fortknox-100pct-static-runtime-gap-9a3d4f.md'
original_relative_path: '_archive\\historical_plans_20260515_cursor_optimization\\fortknox-100pct-static-runtime-gap-9a3d4f.md'
source_sha256: 07fa24d81a41ef18d49dcdb434f1ddcb42103c485d1d662b9998ae13a3120c11
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: fortknox-100pct-static-runtime-gap-9a3d4f
plan_type: governance
---

# Fort Knox — Open Gaps to 100% Static + Runtime Certification

Enumerates every remaining gap between the current Fort Knox signoff claim (87/87 SIGNED_OFF / `trust_level=INTEGRITY_PROOF`) and an uncontested 100% static + runtime certification claim, and sequences the closure work into 5 waves. **No code changes in this plan** — it defines the gap surface and the exit criteria per gap.

---

## Context (SCQA)

- **Situation** — `scripts/compile_requirement_signoff.py` emits `artifacts/certification/final_requirement_signoff_report.json` with `percent_signed_off: 100.0`, `signed_off: 87`, `blocked: 0`, `trust_level: INTEGRITY_PROOF`. Mutation-rejection report `overall_verdict: PASS` across 5 tamper scenarios. Bundle-verification `checks_run: 2080`, `failures: []`, `signature_verification_status: VERIFIED`. The signed universe contains 87 requirements across 9 claim types: `STATIC_ENFORCEMENT` (29), `NO_BYPASS_RUNTIME` (26), `INTEGRATED_RUNTIME` (8), `COMPONENT_RUNTIME` (8), `OBSERVABILITY_RUNTIME` (5), `PRODUCTION_DEPENDENCY_RUNTIME` (5), `REPLAY_RUNTIME` (3), `COMPOSITION_RUNTIME` (2), `STATIC_CONTRACT` (1). Alongside, the L7_AUDITABILITY plane certifies 4 of 9 route families as `REAL_RUNTIME` (R1B, R1A_EXACT_CACHE, R5_FALLBACK, UWG_BLOCK_PATH), 1 as `STRUCTURAL_ONLY` (MANAGED_WORKFLOW), 4 as `NOT_CERTIFIED` (R3_GROUNDED_READ, R4_SINGLE_ACTION, UWG_COMMIT_PATH, MANAGED_WORKFLOW_REAL_EXECUTION).

- **Complication** — A disciplined reviewer can still decline the "100% Fort Knox certified" claim on six defensible grounds: (1) the RTC-REQ universe does not bind the L7_AUDITABILITY plane at all (0 of 87 requirements mention `L7_AUDITABILITY`, `route_family`, `how_trace`, `fortknox_l7`, or the new R1A / R5 / UWG_BLOCK chains); (2) `trust_level` is `INTEGRITY_PROOF`, two levels below the schema ceiling `FINAL_SIGNED_CERTIFICATION`; (3) the clean bundle was compiled with `git_dirty: True` against an uncommitted tree; (4) evidence freshness is 168 h per RTC-REQ-* config but the workflow that re-emits that evidence does not run on every PR for every claim type; (5) mutation-rejection runs only over synthesized sandbox artifacts, never against tampered production artifacts; (6) 4 of 9 route families remain structurally or entirely uncertified, with no RTC-REQ row covering MW_REAL / R3 / R4 / UWG_COMMIT substrate.

- **Question** — What is the complete set of certification gaps between the current `INTEGRITY_PROOF` signoff and an uncontested `FINAL_SIGNED_CERTIFICATION` claim, and what is the smallest sequenced closure path?

- **Answer** — Six gap families (GAP-1 through GAP-6) map to five closure waves (W1..W5). Each wave terminates with a hostile-review acceptance test that a skeptic would have to concede. No wave in this plan authors production code; waves prescribe *what* to certify, *against what evidence class*, and *with which new RTC-REQ rows* — the code authoring happens in downstream execution plans that this plan frames.

---

## Evidence Sources

| Source | Why needed | Status |
|---|---|---|
| `certification/requirements_source.json` (87 rows, schema `fortknox-v2`) | Canonical universe; new RTC-REQ rows land here | ✅ read |
| `certification/evidence_assertions.jsonl` (472 records, all `PASS`, 4 artifact classes) | Current evidence envelope; staleness + drift metric source | ✅ read |
| `artifacts/certification/final_requirement_signoff_report.json` (`trust_level: INTEGRITY_PROOF`, `git_dirty: True`) | Current compiler output and integrity stamp | ✅ read |
| `artifacts/certification/final_requirement_signoff_bundle_verification.json` (`checks_run: 2080`, `failures: []`) | Independent reproduction receipt | ✅ read |
| `artifacts/certification/fortknox_mutation_rejection_report.json` (5 sandbox scenarios, all `REJECTED`) | Negative-control receipt | ✅ read |
| `certification/schemas/final_requirement_signoff_report.schema.json` (`trust_level` enum ceiling = `FINAL_SIGNED_CERTIFICATION`) | Trust-level headroom definition | ✅ read |
| `artifacts/certification/integrated_runtime/{latest, mw_latest, r1a_latest, r5_latest, uwg_block_latest}/agentic_core_l7_route_family_coverage.json` | L7 plane certification state per chain | ✅ read |
| `agentic_core/L7_auditability/coverage/route_family_l7_coverage.py` (9-family static catalog) | Route-family certification classifier | ✅ read |
| `.github/workflows/runtime-certification.yml` + `.github/workflows/agentic-core-auditability.yml` | Per-PR regen surface; freshness driver | ✅ read |
| `.windsurf/rules/fortknox-certification-discipline.md` + skill `fortknox-evidence` | Governing contract; hostile-verifier doctrine | 🔲 consult during execution |

---

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | L7_AUDITABILITY plane added to RTC-REQ universe (target: 87 → 97 reqs) | `certification/requirements_source.json` + new `certification/schemas/` fields + binder doc | A | ~12K 🟢 |
| Wave 2 | Trust-level ladder advanced to `FINAL_SIGNED_CERTIFICATION` | Signature / KMS binding, git-clean gate, per-PR regen, bundle widening to cover XLSX | B | ~15K 🟢 |
| Wave 3 | Mutation rejection generalized to production artifacts (not sandbox) | `scripts/generate_mutation_rejection_report.py` + new `tools/cert/fortknox_production_mutation_driver.py` contract | C | ~10K 🟢 |
| Wave 4 | Four remaining route families receive real runtime substrate (R3, R4, UWG_COMMIT, MW_REAL) | New substrate entrypoints + typed contracts; new RTC-REQ rows bind them | D | ~55K 🟢 |
| Wave 5 | Capstone hardening: trust-level flip, freshness ceiling, reviewer-hostile audit packet | `artifacts/certification/FINAL_SIGNED_CERTIFICATION_AUDIT_PACKET.md` + receipt | E | ~8K 🟢 |

**Total: ~100K tokens across 5 waves, all GREEN**

---

## Out Of Scope

- Rewriting the Fort Knox compiler (`scripts/compile_requirement_signoff.py`) — treated as canon; only its inputs and independent verifier evolve.
- Deleting or weakening any existing RTC-REQ row — the universe may grow, never shrink or relax.
- Certifying structural-only or fixture-only paths as `REAL_RUNTIME` — honest classification is non-negotiable.
- Rebuilding the L7_AUDITABILITY framework — Wave 4 consumes the existing emitter / verifier / coverage chain authored in the preceding session.
- Changing the 5 CERTIFIED families' artifact shape — existing Tier-A receipts remain stable; new binding happens through new RTC-REQ rows, not artifact migration.
- Promoting `MANAGED_WORKFLOW_STRUCTURAL` from `STRUCTURAL_ONLY` to `REAL_RUNTIME` without the MW_REAL substrate landing first (that promotion is a W4 deliverable, not a shortcut).
- Any Notion / ledger writeback — the plan is a governance artifact, not a status board mutation.

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| 1.1 | Define L7-plane RTC-REQ rows | `certification/requirements_source.json` (+10 rows) | GAP-1, GAP-2 | ~4K | 🔲 TODO |
| 1.2 | Emit L7-plane evidence assertions for the 5 certified families | existing L7 emitters wired to drop `evidence_assertions.jsonl` rows tagged with the 10 new req_ids | GAP-1 | ~4K | 🔲 TODO |
| 1.3 | Extend `requirement_signoff_schema.json` + binder doc for the L7 cluster | `certification/requirement_signoff_schema.json` + `docs/reference/runtime_certification/contract_span_binding_matrix.md` | GAP-1 | ~4K | 🔲 TODO |
| 2.1 | Git-clean gate on signoff compile | new gate `ops_scripts/ci/check_signoff_git_clean.py`; compiler refuses to emit when `git_dirty=True` unless `FORTKNOX_DEV_MODE=1` | GAP-2, GAP-4 | ~3K | 🔲 TODO |
| 2.2 | Per-PR regen of every evidence-assertion cluster | `.github/workflows/runtime-certification.yml` regen matrix: one job per claim_type, all fail-closed | GAP-4 | ~5K | 🔲 TODO |
| 2.3 | Signature chain of custody → `SIGNED_PROOF` | Bind `final_requirement_signoff_report.signature.json` to a key-management record (KMS reference OR committed public-key fingerprint + signer id) | GAP-2 | ~4K | 🔲 TODO |
| 2.4 | Widen bundle-verification to XLSX + L7 bundle | `scripts/verify_final_requirement_signoff_bundle.py` includes XLSX sha256 + L7 coverage-matrix sha256 | GAP-2 | ~3K | 🔲 TODO |
| 3.1 | Production-artifact mutation driver | new `tools/cert/fortknox_production_mutation_driver.py` (read-only; mutates copies of real artifacts, never the originals) | GAP-5 | ~5K | 🔲 TODO |
| 3.2 | Extend mutation-rejection report to cover every claim_type | 1 mutation scenario per artifact_class per requirement (87 × 1..3 ≈ 150 scenarios) | GAP-5 | ~5K | 🔲 TODO |
| 4.1 | R3_GROUNDED_READ substrate entrypoint | new `agentic_core/runtime/entrypoints/integrated_grounded_read_run.py` + real C0 retrieval pipeline contract | GAP-6a | ~15K | 🔲 TODO |
| 4.2 | R4_SINGLE_ACTION substrate entrypoint | new `agentic_core/runtime/entrypoints/integrated_single_action_run.py` + real L2 cascade + tool-authorization receipt | GAP-6b | ~15K | 🔲 TODO |
| 4.3 | UWG_COMMIT_PATH substrate | new `agentic_core/runtime/entrypoints/integrated_uwg_commit_run.py` exercising a real `DurableWriteGateway.process_commit_request()` from Exit | GAP-6c | ~10K | 🔲 TODO |
| 4.4 | MANAGED_WORKFLOW_REAL_EXECUTION substrate | new `agentic_core/runtime/entrypoints/integrated_managed_workflow_real_run.py` that chains 4.1 + 4.2 + 4.3 under a real static DAG | GAP-6d | ~10K | 🔲 TODO |
| 4.5 | 4 new RTC-REQ rows for the 4 new families (1 per family, claim_type matched to substrate depth) | `certification/requirements_source.json` (+4 rows, one per family) | GAP-1 + GAP-6 | ~5K | 🔲 TODO |
| 5.1 | Trust-level flip from `INTEGRITY_PROOF` → `FINAL_SIGNED_CERTIFICATION` | Compiler upgrades `trust_level` only when all of §5 Acceptance Checklist is green | GAP-3 | ~3K | 🔲 TODO |
| 5.2 | Hostile-review audit packet | `artifacts/certification/FINAL_SIGNED_CERTIFICATION_AUDIT_PACKET.md` answers the six hostile questions in §Complication with primary-evidence hashes | GAP-3, GAP-5 | ~5K | 🔲 TODO |

---

## Gap Register

**GAP-1: L7_AUDITABILITY plane unbound to the RTC-REQ universe**
- 0 of 87 `requirements_source.json` rows reference `L7_AUDITABILITY`, `route_family`, `how_trace`, `fortknox_l7`, or the new `R1A_EXACT_CACHE` / `R5_FALLBACK` / `UWG_BLOCK_PATH` chains.
- Impact: Fort Knox compiler says 100%, but the claim only covers 87 requirements that deliberately exclude the L7 plane added in the preceding session. A hostile reviewer will cite this asymmetry to decline the 100% claim.
- Exit criterion: +10 new RTC-REQ rows (one per new chain kind + one per new L7 artifact: `agentic_core_how_trace.json`, `agentic_core_l7_route_family_coverage.json`, `fortknox_l7_evidence/*.json`, `integrated_runtime_artifact_manifest.json`, `spine_proof_bundle.json`), bound to the existing 5 CERTIFIED chains' evidence; compiler reports 97/97 SIGNED_OFF.

**GAP-2: Trust-level is `INTEGRITY_PROOF`, schema ceiling is `FINAL_SIGNED_CERTIFICATION`**
- Schema enum (from `final_requirement_signoff_report.schema.json`): `DEVELOPMENT_PROOF` → `INTEGRITY_PROOF` → `SIGNED_PROOF` → `FINAL_SIGNED_CERTIFICATION`.
- Current level `INTEGRITY_PROOF` is valid only as "compiler produced a reproducible, signed, merkle-stamped report"; it does not assert key-management provenance, nor that the signing key is tied to a human or CI identity with public attestation.
- `SIGNED_PROOF` would require: signature chain to a named key, committed public fingerprint, signer-id field in `signature.json`.
- `FINAL_SIGNED_CERTIFICATION` would require all of the above + §GAP-3 + §GAP-4 + §GAP-5 all green.
- Impact: Every claim of "Fort Knox certified" currently derives from `INTEGRITY_PROOF`, which a reviewer can frame as "the compiler hashed itself" rather than "an independent trust authority signed off".
- Exit criterion: `trust_level=FINAL_SIGNED_CERTIFICATION` after W5.1; `signature.json.signer_id` non-empty; public key fingerprint committed.

**GAP-3: Capstone row coverage is thin (3 rows) and does not cover the L7 plane or the new families**
- Only RTC-REQ-120 ("100% runtime certification definition"), RTC-REQ-121 ("100% static enforcement separate from runtime"), RTC-REQ-122 ("no scoped blockers in final claim") carry `is_final_hundred_percent_row: true`.
- None of the three reference the L7 plane or the 4 newly CERTIFIED families.
- Impact: The 100% capstone claim is scoped to the 87-row universe, so growing the universe (GAP-1) does not automatically re-validate the capstone — a new capstone row is required.
- Exit criterion: 1 new capstone row (`RTC-REQ-130` or next free ID) that asserts "100% L7_AUDITABILITY coverage of every route family with real runtime substrate"; at minimum, 4 of 9 families must be `REAL_RUNTIME`-certified for it to pass today, and the target shifts to 8 of 9 after W4 (MW_STRUCTURAL remains structural-only by design).

**GAP-4: Signoff compiled against dirty working tree; no per-PR regen for every claim_type**
- `final_requirement_signoff_report.json.git_dirty: True` → the report is non-reproducible from `git_commit` alone; the attacker / auditor cannot `git checkout <commit>` and re-emit an identical bundle.
- Evidence-assertion cluster freshness: `run_timestamp_utc: 2026-05-02T03:42:18+00:00`; every row carries `freshness_hours: 168`, but the certification workflow (`.github/workflows/runtime-certification.yml`) does not regenerate every claim_type per PR — several clusters are committed artifacts rather than PR-regenerated evidence.
- Impact: Two staleness failure modes: (a) a PR can merge changes to a production module without re-emitting that module's evidence, leaving the signoff certifying stale code; (b) a rebuild from `git_commit` will not reproduce the signed report, defeating the reproducibility claim that underlies `SIGNED_PROOF`.
- Exit criterion: Compiler refuses `trust_level ≥ SIGNED_PROOF` when `git_dirty=True` (unless `FORTKNOX_DEV_MODE=1`, which forces level to `DEVELOPMENT_PROOF`); every claim_type has a dedicated CI job that regens evidence on every PR touching that layer; freshness drift > 168 h blocks merge.

**GAP-5: Mutation rejection runs only over synthesized sandbox artifacts**
- `fortknox_mutation_rejection_report.json` lists 5 tamper scenarios, all under `artifacts/certification/_mutation_sandbox/`. Scenarios (linked_req_ids_only, broad_all_pass, missing_payload, neg_no_block, unapproved_cmd) are synthesized from scratch.
- No scenario tampers a real production artifact (e.g. a real `runtime_identity_envelope.json` or `agentic_core_how_trace.json` with a flipped bit) and then confirms the compiler rejects it.
- Impact: A reviewer can claim "you have only proved the compiler rejects hand-crafted bad JSON, not that it detects realistic tampering of genuine evidence". SLSA L3 / in-toto style assurance requires real-artifact tamper tests.
- Exit criterion: Mutation driver exercises at least 1 tamper class per `artifact_class` in `certification/schemas/evidence_assertion.schema.json` (`INTEGRATED_RUNTIME_BUNDLE`, `STATIC_VERIFIER_REPORT`, `LAYER_BOUNDARY_REPORT`, `MERKLE_TREE_REPORT`, `STATIC_SCAN_REPORT`, `CSV_GATE_RESULT`, `ACCEPTANCE_LEGALITY_REPORT`, `SIGNATURE_ENVELOPE`) applied to *copies of real production artifacts*; all tampers rejected; `all_scenarios_rejected: true` with `scenarios_count ≥ 30`; report bundle hashes unchanged post-run.

**GAP-6: Route-family L7 coverage matrix has 4 of 9 families uncertified**
- From each chain's `agentic_core_l7_route_family_coverage.json` (current state):
  - **GAP-6a** `R3_GROUNDED_READ` — `NOT_CERTIFIED`; missing real C0 retrieval pipeline + typed `FinalEvidenceContract`.
  - **GAP-6b** `R4_SINGLE_ACTION` — `NOT_CERTIFIED`; missing real L2 cascade + tool-authorization receipt.
  - **GAP-6c** `UWG_COMMIT_PATH` — `NOT_CERTIFIED`; no integrated run currently drives a successful commit through `DurableWriteGateway`.
  - **GAP-6d** `MANAGED_WORKFLOW_REAL_EXECUTION` — `NOT_CERTIFIED`; depends on 6a + 6b + 6c.
  - `MANAGED_WORKFLOW_STRUCTURAL` remains `STRUCTURAL_ONLY` by design (structural DAG proof, not runtime proof) — not in scope for this plan.
- Impact: The route-family coverage matrix is the most visible L7 artifact; shipping it with 4 of 9 families `NOT_CERTIFIED` undercuts any "full agentic_core L7 coverage" claim.
- Exit criterion: All 4 families `REAL_RUNTIME`-certified via new entrypoints, regen scripts, family-specific verifiers, and hostile-mutation tests (same discipline as the Tier-A work already landed). New RTC-REQ row per family. MW_STRUCTURAL stays `STRUCTURAL_ONLY` with explicit cert-row acknowledgement.

---

## Execution Plan

### Wave 1 — L7_AUDITABILITY plane binding (closes GAP-1; partially closes GAP-3)

**Scope**: Add 10 new RTC-REQ rows to `certification/requirements_source.json` that bind the L7 plane to the canonical universe. Emit evidence assertions tagged with the new req_ids from the existing L7 emitters. Extend `requirement_signoff_schema.json` to declare `L7_COVERAGE_MATRIX` as an allowed `artifact_class`. Update the contract-span binding-matrix doc.

**Commands**:
```bash
python scripts/compile_requirement_signoff.py --dry-run                           # baseline 87/87
# After Wave 1 rows land:
python scripts/compile_requirement_signoff.py                                      # target 97/97
python scripts/verify_final_requirement_signoff_bundle.py                          # bundle stays PASS
python scripts/generate_mutation_rejection_report.py                               # still REJECTS all sandbox scenarios
```

**Acceptance**:
- `final_requirement_signoff_report.json.summary.total == 97` and `signed_off == 97`.
- All 10 new RTC-REQ rows appear in the `rows` array with `computed_status: SIGNED_OFF`.
- `trust_level` remains `INTEGRITY_PROOF` (ladder does not advance until W5).
- `evidence_assertions.jsonl` record count increases by ≥ 10 × 5 = 50 (one per new req × existing chain).

### Wave 2 — Trust-level ladder to `SIGNED_PROOF` (closes GAP-2, partially closes GAP-4)

**Scope**: Author `ops_scripts/ci/check_signoff_git_clean.py` (new gate). Extend `.github/workflows/runtime-certification.yml` with a regen matrix — one job per claim_type (9 jobs). Bind signature to a named key (initial: committed public-key fingerprint + signer-id literal; upgrade path to KMS in a follow-on plan). Widen `scripts/verify_final_requirement_signoff_bundle.py` to include XLSX sha256 + L7 coverage-matrix sha256 in its `clean_bundle_paths_monitored` list.

**Commands**:
```bash
python ops_scripts/ci/check_signoff_git_clean.py                                   # exit 0 only when git clean
python scripts/compile_requirement_signoff.py --require-clean-git                  # new flag
python scripts/verify_final_requirement_signoff_bundle.py --include-xlsx --include-l7
```

**Acceptance**:
- Compiler emits `trust_level: SIGNED_PROOF` when: `git_dirty=False`, `signature.json.signer_id` non-empty, public key fingerprint matches `certification/signing_keys/public_key_fingerprint.txt`, freshness ≤ 168 h per row.
- Per-PR workflow runs all 9 claim_type regen jobs; any FAIL blocks merge.
- `final_requirement_signoff_bundle_verification.json.clean_bundle_paths_monitored` contains the XLSX path AND at least one L7 coverage-matrix path.

### Wave 3 — Production-artifact mutation rejection (closes GAP-5)

**Scope**: Author `tools/cert/fortknox_production_mutation_driver.py` (read-only; copies real production artifacts into a sandbox directory, applies a typed mutation class, passes the copy through the compiler's pure validator, asserts `REJECTED`). Extend `scripts/generate_mutation_rejection_report.py` to consume the new driver and emit ≥ 30 scenarios spanning every `artifact_class` in the schema enum.

**Commands**:
```bash
python tools/cert/fortknox_production_mutation_driver.py --emit-plan-only          # preview scenario matrix
python scripts/generate_mutation_rejection_report.py --mode=production-artifact    # run
cat artifacts/certification/fortknox_mutation_rejection_report.json                # inspect
```

**Acceptance**:
- `fortknox_mutation_rejection_report.json.scenarios` length ≥ 30.
- `all_scenarios_rejected: true`.
- `clean_bundle_unchanged: true` (original production artifacts must not be modified; only copies in sandbox).
- Every `artifact_class` in the schema is exercised by at least one scenario.
- `tamper_class` coverage includes: sha256 flip, payload field removal, req_id poisoning, signature strip, merkle leaf replacement, linked-only broad artifact, unapproved verifier command, negative-control no-block.

### Wave 4 — Route-family substrate landing (closes GAP-6; grows universe to 101 reqs)

**Scope**: One phase per family. Each phase authors a substrate entrypoint + a typed contract + a regen script + a family-specific verifier + a new RTC-REQ row. No shortcuts: each family must demonstrate its distinguishing discriminator in a way the verifier can independently check (see Tier-A discipline in the preceding session).

- **Phase 4.1 R3** — `integrated_grounded_read_run.py` drives a real C0 retrieval (vector + sparse + rerank), emits `FinalEvidenceContract` with non-empty `evidence_refs[].chunk_ref.payload_sha256`; verifier rejects bypass receipts in the C0 slot.
- **Phase 4.2 R4** — `integrated_single_action_run.py` drives a real L2 cascade via `agent_dispatcher`, emits `l2_sealed_artifact` with `structural_only=False` and `tool_authorizations[]` bound to `ToolRegistryRecord` IDs.
- **Phase 4.3 UWG_COMMIT** — `integrated_uwg_commit_run.py` drives `DurableWriteGateway.process_commit_request()` from Exit with a valid `CommitRequest`, emits `uwg_commit_receipt.json` with `commit_status=COMMITTED` and non-empty `audit_append_receipt_ref`.
- **Phase 4.4 MW_REAL** — `integrated_managed_workflow_real_run.py` composes 4.1 + 4.2 + 4.3 under a real static DAG; verifier asserts `runtime_l3_orchestration_receipt.dag_sha256 == static_dag_proof.dag_sha256` and every G01-G29 verdict is `PASS`/`FAIL` (never `NA`).
- **Phase 4.5** — 4 new RTC-REQ rows, one per family, bound to the new substrates' evidence.

**Commands** (per phase, executed only after the substrate lands):
```bash
python tools/certification/regen_<family>_latest.py
python -m ops_scripts.ci.verify_<family>_l7_runtime
python tools/cert/append_evidence_assertion.py --req-id RTC-REQ-<N>
python scripts/compile_requirement_signoff.py                                      # 97 → 98 → 99 → 100 → 101
```

**Acceptance**:
- `agentic_core_l7_route_family_coverage.json` shows `CERTIFIED / REAL_RUNTIME` for all 4 new families per chain.
- Hostile-mutation tests pass for each (same discipline as Tier-A: borrow detection, missing HOW trace, missing Fort Knox, fixture-only forgery).
- Final universe: 101 requirements, 101/101 SIGNED_OFF.

### Wave 5 — Trust-level flip + hostile-review audit packet (closes GAP-3, finalizes GAP-2/4/5)

**Scope**: Compiler upgrades `trust_level` to `FINAL_SIGNED_CERTIFICATION` iff the W5 Acceptance Checklist is fully green. Author `artifacts/certification/FINAL_SIGNED_CERTIFICATION_AUDIT_PACKET.md` — a hostile-reviewer-hostile document that answers each of the six gap questions from the Complication section with primary-evidence hashes and pointers.

**Commands**:
```bash
python scripts/compile_requirement_signoff.py --assert-level=FINAL_SIGNED_CERTIFICATION
python scripts/verify_final_requirement_signoff_bundle.py --strict
python tools/cert/emit_final_certification_audit_packet.py
```

**Acceptance**:
- `final_requirement_signoff_report.json.trust_level == "FINAL_SIGNED_CERTIFICATION"`.
- `FINAL_SIGNED_CERTIFICATION_AUDIT_PACKET.md` exists and answers each GAP with a sha256-pinned primary-evidence reference.
- Bundle verification `checks_run ≥ 2080` (should grow with universe); `failures: []`.
- Independent re-compile from `git_commit` on a clean checkout produces byte-identical `final_requirement_signoff_report.sha256`.

---

## Rules

- No RTC-REQ row shall claim runtime evidence while it only has static evidence (`reference-only rows cannot claim runtime`, RTC-REQ-005).
- Every new RTC-REQ row carries `allowed_verifier_commands` referencing real committed scripts under `tools/cert/**` or `scripts/verify_*` or `ops_scripts/ci/*`, consistent with `fortknox-certification-discipline.md` constitutional §32.
- Mutation-rejection production-artifact driver mutates **copies only**; production artifacts are read-only in the driver's process.
- Trust-level upgrades happen only through the compiler, never by hand-editing `trust_level` in the JSON output.
- The L7_AUDITABILITY plane may expand; existing L7 verifier behaviour must not weaken (no tolerating new chain kinds silently, no relaxing fail-closed rules).
- CI-job fail-closed: any new job added under Wave 2 regen matrix must have no `continue-on-error: true`.
- No plan step in this document may be substituted for actual code; every acceptance criterion must be demonstrable from committed artifacts.
- Honest classification wins: if substrate does not exist, the matrix reports `NOT_CERTIFIED` with `blocking_gap` text — promotion requires substrate, not prose.

---

## Success Criteria

- [ ] **GAP-1 closed** — `certification/requirements_source.json` contains ≥ 97 rows; all new rows bound to the L7 plane; compiler reports all SIGNED_OFF.
- [ ] **GAP-2 closed** — `trust_level: FINAL_SIGNED_CERTIFICATION`; `signature.json.signer_id` non-empty; public key fingerprint committed; bundle verification includes XLSX and L7 artifact hashes.
- [ ] **GAP-3 closed** — ≥ 2 additional capstone rows (one per new dimension: L7 plane coverage, full route-family runtime coverage) with `is_final_hundred_percent_row: true` and `computed_status: SIGNED_OFF`.
- [ ] **GAP-4 closed** — compiler refuses to emit `trust_level ≥ SIGNED_PROOF` when `git_dirty=True` (except `FORTKNOX_DEV_MODE=1`); per-PR regen matrix runs 1 job per claim_type; freshness drift blocks merge.
- [ ] **GAP-5 closed** — mutation-rejection report includes ≥ 30 production-artifact scenarios spanning all `artifact_class` enum values; all rejected; clean bundle unchanged.
- [ ] **GAP-6 closed** — `agentic_core_l7_route_family_coverage.json` reports 8 of 9 families as `REAL_RUNTIME` CERTIFIED; 1 family (`MANAGED_WORKFLOW_STRUCTURAL`) remains `STRUCTURAL_ONLY` by explicit design and is bound by its own RTC-REQ row with `claim_type: STATIC_CONTRACT`.
- [ ] **End-to-end** — on a clean `git` checkout at the final commit, running the full compile+verify+mutation chain produces `trust_level: FINAL_SIGNED_CERTIFICATION` and bundle `PASS` with zero failures.

---

## Implementation Commands

```bash
# Current baseline (run before any wave)
python scripts/compile_requirement_signoff.py
python scripts/verify_final_requirement_signoff_bundle.py
python scripts/generate_mutation_rejection_report.py
# expect: 87/87 SIGNED_OFF, bundle PASS, sandbox mutations REJECTED

# After Wave 1 (L7 rows land)
python scripts/compile_requirement_signoff.py        # expect 97/97

# After Wave 2 (trust ladder to SIGNED_PROOF)
python ops_scripts/ci/check_signoff_git_clean.py     # exit 0 required
python scripts/compile_requirement_signoff.py --require-clean-git
# expect: trust_level = SIGNED_PROOF, signer_id present

# After Wave 3 (production-artifact mutation)
python tools/cert/fortknox_production_mutation_driver.py --emit-plan-only
python scripts/generate_mutation_rejection_report.py --mode=production-artifact
# expect: >= 30 scenarios, all_scenarios_rejected = true

# After Wave 4 (4 new families certified)
for fam in grounded_read single_action uwg_commit mw_real; do
  python tools/certification/regen_${fam}_latest.py
  python -m ops_scripts.ci.verify_${fam}_l7_runtime
done
python scripts/compile_requirement_signoff.py       # expect 101/101

# After Wave 5 (trust flip + audit packet)
python scripts/compile_requirement_signoff.py --assert-level=FINAL_SIGNED_CERTIFICATION
python scripts/verify_final_requirement_signoff_bundle.py --strict
python tools/cert/emit_final_certification_audit_packet.py
```

---

## Rollback Strategy

If any wave fails or introduces regression on the existing 87-row signoff:

1. **Wave 1 regression** — revert `certification/requirements_source.json` to the pre-Wave-1 commit; evidence assertions rollback is purge-driven (`tools/cert/purge_evidence_assertions.py --req-id RTC-REQ-<N>` per added row); compiler returns to 87/87.
2. **Wave 2 regression** — revert `check_signoff_git_clean.py` enable flag; re-emit bundle at `trust_level: INTEGRITY_PROOF`; per-PR regen matrix can be disabled via workflow env `FORTKNOX_REGEN_MATRIX_DISABLED=1`.
3. **Wave 3 regression** — revert `scripts/generate_mutation_rejection_report.py` to sandbox-only mode; production-artifact driver stays checked in but unused until regression is diagnosed.
4. **Wave 4 regression** — each family's substrate is independent; a failing family can be marked `NOT_CERTIFIED` again in the static catalog without affecting the other 3; new RTC-REQ row stays in source with `computed_status: BLOCKED` and `blocking_gap` populated.
5. **Wave 5 regression** — if trust-level flip cannot hold (any of §Success Criteria fails), compiler emits `SIGNED_PROOF` instead of `FINAL_SIGNED_CERTIFICATION`; no data loss; audit packet is regenerated at the lower trust level.

All waves use the existing integrity stack (`git_commit`, bundle merkle/sha256/signature, mutation-rejection report), so any regression is diagnosable by diffing the pre/post bundle verification JSON.

---

## Acceptance Criteria

| Metric | Target | Verification |
|---|---|---|
| Requirement universe size | 97 after W1; 101 after W4 | `jq '.rows | length' artifacts/certification/final_requirement_signoff_report.json` |
| Compiler signoff rate | 100.0 % continuously | `jq '.summary.percent_signed_off' artifacts/certification/final_requirement_signoff_report.json` |
| Trust level | `FINAL_SIGNED_CERTIFICATION` after W5 | `jq '.trust_level' artifacts/certification/final_requirement_signoff_report.json` |
| Git-clean gate | refuses dirty tree | `git status --short` pre-compile; `check_signoff_git_clean.py` exit 0 |
| Per-PR regen matrix | 1 job per claim_type (9 jobs) | `.github/workflows/runtime-certification.yml` contains 9 `claim_type:<X>` matrix entries |
| Bundle verification monitored paths | includes XLSX + L7 coverage-matrix | `jq '.clean_bundle_paths_monitored | length' artifacts/certification/final_requirement_signoff_bundle_verification.json` ≥ 10 |
| Production-artifact mutation scenarios | ≥ 30, all rejected | `jq '.scenarios | length' artifacts/certification/fortknox_mutation_rejection_report.json` ≥ 30 and `all_scenarios_rejected=true` |
| Route-family coverage | 8/9 families `REAL_RUNTIME` CERTIFIED; 1 `STRUCTURAL_ONLY` by design | `agentic_core_l7_route_family_coverage.json.route_families[*].certification_status` |
| Reproducibility | `final_requirement_signoff_report.sha256` reproduces on clean checkout | CI job `verify_reproducibility` diffs current sha256 vs re-emitted sha256 |
| Audit packet | exists; answers all 6 GAP questions with sha256 pointers | `FINAL_SIGNED_CERTIFICATION_AUDIT_PACKET.md` regex match on each GAP ID |

---

## Cascade Alignment Checks

- This plan is `plan_type: governance`; ADG hotspot + graph-layer-evidence gates do not apply (per `.windsurf/rules/adg-graph-layer-enforcement.md` § "Plan Scope via Frontmatter").
- Every acceptance criterion is expressible as a deterministic JSON / sha256 check — no LLM rubric dependence in the gate path.
- The plan does not widen to code authoring; each wave is an execution-plan *hook point* from which a child plan (or direct implementation) may proceed under normal author-gate discipline.
- Fort Knox constitutional §32 authority preserved: compiler-is-only-status-authority, atomic assertions, mutation-rejection pairing, positive-control canary (`RTC-REQ-001`) stay intact; waves *grow* the surface, never relax it.
- No writeback to Notion / memory is part of this plan — the plan itself is the artifact.
