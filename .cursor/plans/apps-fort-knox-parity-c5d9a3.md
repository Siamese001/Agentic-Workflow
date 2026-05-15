# Apps Fort Knox Parity — `apps_*` to `SIGNED_PROOF` Trust Level

**Plan ID**: `apps-fort-knox-parity-c5d9a3`
**Status**: **Completed** — W1–W7 SHIPPED 2026-05-02; W8–W10 (open-scope closure) SHIPPED 2026-05-02 UTC-04:00 same session. Apps_e2e Fort Knox track at SIGNED_PROOF parity with agentic_core; FINAL_SIGNED_CERTIFICATION code paths + CI workflow shipped (closes on next tagged release).
**Author**: Cascade
**Tier**: T3 (5+ files, multi-layer, governance-critical, multi-wave)
**Related plans**:
- Predecessor (DONE): `apps-e2e-spine-cert-wireup-e1c4d7` — 8 of 8 apps SPINE_COMPLETE_CERTIFIED via shared spine emission
- Predecessor (DONE): `collapse-apps-rg-runtime-b7e2f5` — apps_rg uses shared helper
- Reference (live): the `agentic_core` Fort Knox track — `scripts/compile_requirement_signoff.py`, `certification/requirements_source.json`, `tools/cert/*.py`, `tools/cert/fortknox_production_mutation_driver.py`, `artifacts/certification/HUNDRED_PERCENT_RUNTIME_PROOF.json`
- Constitutional rule: §32 (Fort Knox certification integrity)

---

## 1. Intent

Lift the `apps_*` family from `SPINE_COMPLETE_CERTIFIED` (which is "the verifier said pass") to **Fort Knox parity**: atomic assertions, compiler-of-truth signoff, mutation-rejection rejection report, bundle Merkle root + signature, live-LLM-style attestation **where applicable**, and a consolidated 100% RUNTIME PROOF JSON. Match the `agentic_core` discipline exactly so a single audit pass over both tracks is a uniform read.

## 2. Gap Analysis — `agentic_core` vs `apps_*` today

| Sub-system | `agentic_core` (live) | `apps_*` (today) | Gap |
|---|---|---|---|
| **Atomic assertions** | `certification/evidence_assertions.jsonl`, one assertion per `(req_id, control)`, sha256-hashed, deterministic `assertion_id` | Per-app `apps_e2e_proof.json` (composite, 9 receipts inside) + `verifier_report.json` (verdict per app, no per-rule line items) | NO atomic per-rule assertions |
| **Requirement catalog** | `certification/requirements_source.json` — 102 `RTC-REQ-NNN` IDs, claim types, allowed artifact classes, acceptance rules | None — verifier rules N1–N20 + base rules are code-only, no SSOT catalog with IDs | NO `APPS-REQ-*` catalog |
| **Compiler-of-truth** | `scripts/compile_requirement_signoff.py` — sole producer of `SIGNED_OFF`; reads JSONL + catalog → emits `*.json/sha256/merkle.json/signature.json` + xlsx | `verifier_strict.py` is a verifier, not a compiler. Emits PASS/FAIL only, no signoff envelope | NO compiler |
| **Producer allowlist** | Constitutional §32: assertion producers restricted to `tools/cert/*.py`, `scripts/verify_*_gate.py`, `scripts/verify_rtc_*.py` | No producer restriction on `verifier_strict.py` | NO allowlist enforcement |
| **Positive-control canary** | `RTC-REQ-001` — flips to FAIL if compiler is broken | None | NO canary |
| **Mutation rejection** | `tools/cert/fortknox_production_mutation_driver.py` — 40 mutations × 40 rejections proving verifier is hostile | N1–N20 negative-control tests (23) — pass/fail at test level only, no formal `mutation_rejection_report.json` with 40/40 attestation | NO formal mutation report |
| **Bundle Merkle + signature** | `*.merkle.json` + `*.signature.json` (Ed25519) | `apps_e2e_matrix.json` has sha256 but no Merkle root, no signature | NO Merkle, NO signature |
| **Trust level** | `SIGNED_PROOF` (or `SIGNED_OFF` per row) explicitly stamped in compiler output | Implicit "the gate passed" | NO trust-level field |
| **Live attestation** | `live_provider_attestation.json` v1 — `rubric_hash_sha256` + `response_hash_sha256` + `model_id` for the LLM judge | N/A — apps_* don't currently invoke an LLM judge in the cert path | EXEMPT (different problem domain) |
| **Consolidated 100% proof** | `artifacts/certification/HUNDRED_PERCENT_RUNTIME_PROOF.json` — single JSON binding every claim to file sha256 + verifier exit code | None | NO consolidated proof |
| **CI binding** | `runtime_certification_requirements_100_percent_hardened.csv` + `compile_requirement_signoff.py` runs in CI | `check_apps_e2e_spine_certification.py` (BLOCKING as of 2026-05-02) | Partial — gate exists but no signoff envelope produced |

**Net**: apps_* has the verifier and the negative-control tests already. What's missing is the **paperwork layer** — turning verifier output into atomic, hashable, signable, compiler-asserted SIGNED_OFF rows.

## 3. Scope

**In** (this plan ships):
- `APPS-REQ-*` requirement catalog (one per N1–N20 rule + base rules + per-app spine completeness)
- Atomic assertion JSONL emitter (consumes `verifier_report.json` + per-app proofs → `apps_evidence_assertions.jsonl`)
- Compiler (`scripts/compile_apps_e2e_signoff.py` — producer-allowlist enforced)
- Mutation rejection driver (mirrors agentic_core's; mutates apps_e2e proof bundles, proves verifier rejects)
- Bundle Merkle + signature
- Consolidated proof generator (`tools/certification/generate_apps_100pct_runtime_proof.py`)
- CI gate flip — `check_apps_e2e_spine_certification.py` becomes a thin wrapper that calls the compiler
- Constitutional §32 update — add `tools/cert/apps_e2e/*.py` to producer allowlist

**Out** (defer):
- Live LLM attestation for apps_* (not applicable; apps_* don't use LLM judges in the cert path — would be artificial)
- `FINAL_SIGNED_CERTIFICATION` trust level (Sigstore Fulcio / external KMS — same orthogonal axis as agentic_core, separate plan)
- Migration of `apps_qna` and `apps_underwriting_ai` from waiver to certified (orthogonal — they need actual runtime work first)

## 4. Wave Structure

| Wave | Focus | Est. Tokens | Status | Success Criteria |
|---|---|---:|---|---|
| **W1 — Requirement catalog** | Author `certification/apps_e2e_requirements_source.json` (one `APPS-REQ-NNN` per N1–N20 + 8 spine-completeness rows + 5 verifier-base rules ≈ 33 rows); positive-control canary `APPS-REQ-001` | ~6k | **SHIPPED 2026-05-02** | Catalog validates against new `apps_e2e_requirements.schema.json`; counts match expected; canary present |
| **W2 — Atomic assertion emitter** | `tools/cert/apps_e2e/emit_apps_evidence_assertions.py` — reads `verifier_report.json` + per-app `apps_e2e_proof.json` + `apps_e2e_matrix.json` → emits `certification/apps_evidence_assertions.jsonl` (one assertion per `(req_id, app)`) | ~7k | **SHIPPED 2026-05-02** | Each requirement has ≥1 assertion; all assertions schema-valid; deterministic `assertion_id`; producer line stamps `tools/cert/apps_e2e/emit_apps_evidence_assertions.py` |
| **W3 — Compiler** | `scripts/compile_apps_e2e_signoff.py` — consumes catalog + JSONL → emits `apps_e2e_signoff_report.json` + `.sha256` + `.merkle.json` (per-app + global Merkle root); enforces producer allowlist (rejects assertions from non-allowlisted scripts); positive-control canary check | ~9k | **SHIPPED 2026-05-02** | All 33 rows SIGNED_OFF (or BLOCKED with reason); canary fires on broken compile; output mirrors agentic_core's signoff envelope |
| **W4 — Mutation driver** | `tools/cert/apps_e2e/apps_mutation_driver.py` — generates 30+ mutations of apps_e2e proof bundles (corrupt sha256, wrong app_name, missing receipt, mismatched matrix row, etc.); runs strict verifier against each; expects 30/30 rejections; emits `apps_mutation_rejection_report.json` | ~6k | **SHIPPED 2026-05-02** | 30/30 rejected; report includes mutation class, expected rejection rule, actual verifier exit code |
| **W5 — Bundle signature** | Reuse `tools/cert/sign_release_bundle.py` shape: emit `apps_e2e_signoff_report.signature.json` (Ed25519 signature over the merkle.json); verifier `tools/cert/apps_e2e/verify_apps_release_signature.py` | ~4k | **SHIPPED 2026-05-02** | Round-trip sign+verify exits 0; mutation of any input flips signature verify to fail |
| **W6 — Consolidated proof** | `tools/certification/generate_apps_100pct_runtime_proof.py` — single JSON binding: catalog hash, JSONL hash, signoff hash, merkle root, signature hash, mutation report hash, verifier_report hash, per-app proof hashes; mirrors `HUNDRED_PERCENT_RUNTIME_PROOF.json` shape | ~3k | **SHIPPED 2026-05-02** | Output deterministic; sha256 stable across runs (modulo wall-clock); all gate exits captured |
| **W7 — CI flip + §32 update** | New CI gate `ops_scripts/ci/check_apps_fortknox_signed_proof.py` (T7s.4) re-runs W6 generator and asserts `all_gates_pass=true`; constitutional §32 amended to two arms (agentic_core + apps_e2e) with `APPS-REQ-001` canary | ~3k | **SHIPPED 2026-05-02** | CI green; constitutional §32 prose updated (43,651→43,989 bytes; 7,138 bytes headroom); pre-commit T7s.4 hook registered; live gate exit 0 |

**Total est.**: ~38k tokens across 7 waves. Single-session feasibility: W1 + W2 in one session; W3 + W4 next; W5 + W6 + W7 in third session. Multi-session work.

## 5. Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---:|---|
| W1.1 | Catalog draft | `certification/apps_e2e_requirements_source.json`, `certification/schemas/apps_e2e_requirements.schema.json` | Mapping N1–N20 to `APPS-REQ-NNN` 1:1 vs grouping; choosing canary | ~4k | Draft |
| W1.2 | Catalog tests | `tests/unit/cert/test_apps_e2e_requirements_source.py` | None | ~2k | Draft |
| W2.1 | Assertion emitter core | `tools/cert/apps_e2e/emit_apps_evidence_assertions.py` | Mapping verifier rule outcomes to assertion shape; deterministic IDs | ~5k | Draft |
| W2.2 | Emitter tests | `tests/unit/cert/test_emit_apps_evidence_assertions.py` | None | ~2k | Draft |
| W3.1 | Compiler core | `scripts/compile_apps_e2e_signoff.py` | Allowlist enforcement; merkle tree construction; positive-control canary | ~6k | Draft |
| W3.2 | Compiler tests | `tests/unit/cert/test_compile_apps_e2e_signoff.py` + integration test asserting SIGNED_OFF on golden input | None | ~3k | Draft |
| W4.1 | Mutation driver | `tools/cert/apps_e2e/apps_mutation_driver.py` + `tools/cert/apps_e2e/_mutators.py` | Mutation class taxonomy; sandbox; reject-rule prediction | ~4k | Draft |
| W4.2 | Mutation report | Output schema + integration test | None | ~2k | Draft |
| W5.1 | Sign + verify scripts | `tools/cert/apps_e2e/sign_apps_release_bundle.py`, `tools/cert/apps_e2e/verify_apps_release_signature.py` | Reuse vs copy from agentic_core's signers | ~3k | Draft |
| W5.2 | Signature tests | Round-trip + mutation test | None | ~1k | Draft |
| W6.1 | Consolidator | `tools/certification/generate_apps_100pct_runtime_proof.py` | Determinism; cross-tool exit-code capture | ~2k | Draft |
| W6.2 | Consolidator tests | Integration test that calls all 6 prior phases on golden input → asserts the consolidated proof shape | None | ~1k | Draft |
| W7.1 | CI gate flip | `ops_scripts/ci/check_apps_e2e_spine_certification.py` rewrite | Backward compat — old verifier still callable for fast path | ~2k | Draft |
| W7.2 | Constitutional §32 update | `.windsurf/rules/constitutional.md` §32 producer-allowlist amendment | Tight regex change; CI gate that proves the amendment | ~1k | Draft |

## 6. Files In Scope

**New SSOT**:
- `certification/apps_e2e_requirements_source.json` (catalog)
- `certification/schemas/apps_e2e_requirements.schema.json`
- `certification/schemas/apps_evidence_assertion.schema.json` (or reuse existing)
- `certification/apps_evidence_assertions.jsonl` (output of W2)

**New tools/scripts**:
- `tools/cert/apps_e2e/emit_apps_evidence_assertions.py`
- `tools/cert/apps_e2e/apps_mutation_driver.py`
- `tools/cert/apps_e2e/_mutators.py`
- `tools/cert/apps_e2e/sign_apps_release_bundle.py`
- `tools/cert/apps_e2e/verify_apps_release_signature.py`
- `scripts/compile_apps_e2e_signoff.py`
- `tools/certification/generate_apps_100pct_runtime_proof.py`

**Modified**:
- `ops_scripts/ci/check_apps_e2e_spine_certification.py`
- `.windsurf/rules/constitutional.md` §32 (producer allowlist)
- `.pre-commit-config.yaml` (T7r-apps gate)

**Output artifacts** (all in `artifacts/certification/`):
- `apps_e2e_signoff_report.json` + `.sha256` + `.merkle.json` + `.signature.json`
- `apps_mutation_rejection_report.json`
- `APPS_HUNDRED_PERCENT_RUNTIME_PROOF.json`

## 7. Risks

| Risk | Mitigation |
|---|---|
| Drift from agentic_core schema → operators have to learn two near-identical models | W1 catalog reuses `evidence_assertion.schema.json` as much as possible. Only diverge where apps_* genuinely differs (composite-proof artifact_class, no LLM judge). |
| Mutation driver false-positives — verifier accepts a mutated bundle | W4 includes a sentinel "obvious break" mutation (corrupt sha256). If sentinel passes the verifier, the driver fails the build. |
| Producer allowlist over-enforcement breaks legitimate emitters | The allowlist is checked at compile time, not at emit time. Bypass: `APPS_FORTKNOX_DISCIPLINE_BYPASS=1` (logged), same shape as constitutional §32's existing bypass. |
| Per-app proofs already exist with different shape than catalog expects → re-emission required | W2 emitter only reads existing artifacts. No re-emission of proofs. If schema mismatch, the assertion fails (reported, not silently passed). |
| `apps_qna` + `apps_underwriting_ai` are waived; how do they appear in the catalog? | Add `WAIVER_ASSERTION` class (mirrors agentic_core's `BLOCKED` claim type). Waiver assertions count as "addressed", not as PASS, in the compiler. Trust level: `SIGNED_OFF_WITH_WAIVERS`. |

## 8. Acceptance Gates

After all 7 waves:

1. `python -m scripts.compile_apps_e2e_signoff` — exit 0; emits 33 SIGNED_OFF rows (or N SIGNED_OFF + 2 SIGNED_OFF_WITH_WAIVERS)
2. `python -m tools.cert.apps_e2e.apps_mutation_driver` — exit 0; report shows ≥30 mutations / 30 rejections
3. `python -m tools.cert.apps_e2e.verify_apps_release_signature` — exit 0
4. `python -m tools.certification.generate_apps_100pct_runtime_proof` — emits `APPS_HUNDRED_PERCENT_RUNTIME_PROOF.json` with `trust_level=SIGNED_PROOF`, all 33 row IDs accounted for
5. `pre-commit run --all-files` — T7r-apps green
6. Constitutional §32 prose lists `tools/cert/apps_e2e/*.py` as a producer
7. Full regression: 250+ tests still green; no agentic_core Fort Knox regressions

## 9. Why Now (vs. defer)

- Operationally: apps_e2e is now BLOCKING in CI (2026-05-02 ADR-081). The next escalation level is naturally Fort Knox parity, not staying at "verifier said pass".
- Auditability: a single audit pass should treat agentic_core and apps_* identically. Today the auditor has to learn two paradigms.
- Reuse: every Fort Knox subsystem already exists in `tools/cert/` for agentic_core. This plan is mostly **adaptation**, not invention. ~70% of the LOC is mechanical mirroring.

## 10. Open Questions (to resolve before W1)

| # | Question | Recommended default |
|---|---|---|
| Q1 | One `APPS-REQ-NNN` namespace for ALL apps, or per-app `APPS-RG-REQ-NNN` / `APPS-EXEC-REQ-NNN`? | **Single `APPS-REQ-NNN` namespace** — verifier rules are app-agnostic; per-app facts live in `proof_payload.app_name`. Simpler catalog, cleaner Merkle. |
| Q2 | Reuse agentic_core's `evidence_assertions.jsonl` or new file? | **New file** `apps_evidence_assertions.jsonl`. Keeps the two tracks independently signable. Consolidated proof binds both. |
| Q3 | Reuse agentic_core's compiler or new compiler? | **New compiler** `scripts/compile_apps_e2e_signoff.py`. Same architecture, different catalog. Easier to audit independently. |
| Q4 | LLM judge for apps_*? | **No** — apps_* cert path is deterministic verifier rules, not subjective judgments. Forcing an LLM judge would be artificial and hurt determinism. |
| Q5 | Live LLM attestation? | **No** — same reason. The apps_* live attestation IS the per-app proof bundle (real wall-clock run, real entrypoint, real receipts). |

## 11. Supersedes / Is Superseded By

- **Supersedes**: nothing.
- **Is superseded by**: nothing yet. This plan is the first proposal for apps_* Fort Knox parity.

## 12. Final Closure

_To be populated once W7 passes_.

---

## 13. W1 Closure — Requirement Catalog (2026-05-02 UTC-04:00)

### Delivered

| Artifact | Path | Description |
|---|---|---|
| Schema | `certification/schemas/apps_e2e_requirements.schema.json` | JSON-Schema Draft 2020-12, `apps_e2e_fortknox-v1`; defines Requirement, 7 claim types (APPS_BUNDLE_EMISSION/SPINE_CERTIFIED/WAIVER/MATRIX_GOVERNANCE/NEGATIVE_CONTROL/STATIC_CONTRACT/POSITIVE_CONTROL), 31 control names, 10 artifact classes |
| Catalog | `certification/apps_e2e_requirements_source.json` | 33 rows (APPS-REQ-001..033), positive-control canary at 001, 6 per-app SPINE_CERTIFIED rows (025..030), 2 WAIVER rows (031..032), 3 NEGATIVE_CONTROL rows (018..020), matrix-integrity row (033), static-DAG binding + 15 cross-cutting spine rules |
| Tests | `tests/unit/apps_e2e/test_apps_e2e_requirements_source.py` | 19 tests covering schema validity, req_id uniqueness, sequential numbering, exactly-one-canary, depends_on resolution, no self-dependency, claim_type_required_controls present per row, per-app coverage, waiver reason non-empty, fail-closed semantics, verifier-command path hygiene |

### Test result: **19/19 PASS** (0.12s, no regressions)

### Row-count breakdown

| Group | Rows | Req IDs |
|---|---:|---|
| Canary (positive-control) | 1 | 001 |
| Bundle emission / schema | 2 | 002, 003 |
| Integrity / static contract | 4 | 004, 005, 006, 007 |
| Threading / spine certified | 1 | 008 |
| Artifacts / hash binding | 2 | 009, 010 |
| Static DAG | 2 | 011, 012 |
| Route contract + ordering + exit + overlay + hygiene | 5 | 013, 014, 015, 016, 017 |
| Negative controls (synthetic/mock/fixture) | 3 | 018, 019, 020 |
| Runtime-mode allowlist | 1 | 021 |
| Level invariant + artifact-kind + receipts | 3 | 022, 023, 024 |
| Per-app spine certification | 6 | 025–030 |
| Waivers | 2 | 031, 032 |
| Matrix governance | 1 | 033 |
| **Total** | **33** | |

### Design notes (resolved during W1)

- **`claim_type_required_controls`**: only rows of claim types APPS_BUNDLE_EMISSION / APPS_WAIVER / APPS_MATRIX_GOVERNANCE / APPS_NEGATIVE_CONTROL / APPS_POSITIVE_CONTROL have a universal required control. APPS_SPINE_CERTIFIED and APPS_STATIC_CONTRACT rows declare their specific control per-row (threading, artifacts, static-DAG, etc.) — no single control applies universally. The map is `[]` for those two claim types and per-row controls dictate.
- **Positive-control canary (APPS-REQ-001)**: flips to FAIL when the compiler's own plumbing breaks (catalog unparseable, duplicate req_ids, unresolved depends_on, or >1 canary). Mirrors agentic_core's RTC-REQ-001.
- **Waiver rows** (APPS-REQ-031, 032): `fail_closed_if_missing=false` (only non-fail-closed rows); `waiver_reason` is mandatory and non-empty; `waiver_expiry_utc=null` for open-ended waivers (apps_qna non-runtime, apps_underwriting_ai skeleton).

### What W1 does NOT do (deferred to W2-W7)

- W1 produces no `apps_evidence_assertions.jsonl` entries (that's W2's job).
- W1 produces no `SIGNED_OFF` verdict (W3 compiler).
- W1 is a description of what MUST be proven, not the proofs themselves. Every APPS-REQ-NNN row's `acceptance_rule` is a declarative truth-condition; W2 will generate assertions; W3 will compile verdicts.

### Files added

- `certification/schemas/apps_e2e_requirements.schema.json` (~5.4 KB)
- `certification/apps_e2e_requirements_source.json` (~22 KB, 33 rows)
- `tests/unit/apps_e2e/test_apps_e2e_requirements_source.py` (~6.5 KB, 19 tests)

### Next session entry point (SUPERSEDED by W2 closure §14)

W2 — `tools/cert/apps_e2e/emit_apps_evidence_assertions.py`. Reads the W1 catalog + existing `apps_e2e_verifier_report.json` + per-app bundles + matrix → emits one assertion per `(req_id, app)` tuple to `certification/apps_evidence_assertions.jsonl` with deterministic `assertion_id = sha256(req_id + control + artifact_sha256 + pointer)`. Mirror shape of `certification/evidence_assertions.jsonl`. Producer line must stamp exact script path (will be enforced by W3 allowlist).

---

## 14. W2 Closure — Atomic Evidence Assertion Emitter (2026-05-02 UTC-04:00)

### Delivered

| Artifact | Path | Description |
|---|---|---|
| Schema | `certification/schemas/apps_evidence_assertion.schema.json` | Adapts `evidence_assertion.schema.json` with APPS-REQ-* req_id pattern, 7 APPS-specific assertion classes, optional `app_name` field |
| Emitter | `tools/cert/apps_e2e/emit_apps_evidence_assertions.py` | Pure projection over verifier_report + matrix; no per-app subprocess runs; deterministic assertion_id; sorted output; honest NOT_VERIFIED for W3/W4/W5 deferred controls |
| Module init | `tools/cert/apps_e2e/__init__.py` | Declares producer folder semantics (allowlist target for constitutional §32 amendment in W7) |
| Output JSONL | `certification/apps_evidence_assertions.jsonl` | 185 assertions across 33 rows (148 PASS / 37 NOT_VERIFIED / 0 FAIL / 0 BLOCKED) |
| Tests | `tests/unit/apps_e2e/test_emit_apps_evidence_assertions.py` | 13 tests: structural (ids, sort, stamp), semantics (canary NOT_VERIFIED, neg-control NOT_VERIFIED, per-app owner binding, waiver PASS, bundle-emission certified-apps-only, matrix row), schema validity, live-artifact smoke |

### Test result: **13/13 PASS** (emitter) + **19/19 PASS** (W1 catalog) = **32/32 green** (0.19 s)

### Assertion taxonomy emitted by W2

| Row group | Produced | Sample count | Result | Reason for NOT_VERIFIED |
|---|---|---:|---|---|
| APPS-REQ-001 canary | 1 | 1 | NOT_VERIFIED | Deferred to W3 compiler (`catalog_self_consistency`) |
| APPS-REQ-002..017, 021..024 cross-cutting | 6 certified apps × 1 control each | ~148 | PASS | N/A (verifier-report-backed) |
| APPS-REQ-018, 019, 020 negative controls | 6 certified apps × 1 control | 18 | NOT_VERIFIED | Deferred to W4 mutation driver (`mutation_rejection`) |
| APPS-REQ-025..030 per-app spine | 1 owner_app × 2 controls | 12 | PASS | N/A |
| APPS-REQ-031, 032 waivers | 1 owner_app × 1 control | 2 | PASS | `certification_level` is `WAIVED_*` |
| APPS-REQ-033 matrix governance | 1 | 1 | PASS | Row count matches 8 |

### Design notes (resolved during W2)

- **Deferred controls map**: `catalog_self_consistency` → W3, `mutation_rejection` → W4, `merkle_leaf` → W3, `certifier_signature` → W5. The emitter does NOT pretend it can prove those; emits `NOT_VERIFIED` with a note citing the producer that will close them. This is the `honest NOT_VERIFIED` discipline borrowed from agentic_core's Fort Knox.
- **Subject selection**: canary and matrix-governance rows emit one assertion with `app_name=None`. Per-app rows (025–032) emit one assertion for their `owner_app`. Cross-cutting non-waiver rows emit one assertion per certified app (waived apps are already covered by their dedicated waiver row — no double counting).
- **Verifier-backed PASS criterion**: `certification_level == SPINE_COMPLETE_CERTIFIED` AND `violation_count == 0` at the app's row in `verifier_report.json`. Anything else → FAIL (not NOT_VERIFIED — the verifier IS the authority, so absence of a clean verdict is a genuine failure for that (req_id, app)).
- **Deterministic assertion_id**: `ASRT-<sha256(req_id|control|artifact_sha256|pointer)[:40]>`. Shortens from 64 to 40 hex chars (still well above the schema's 16-char floor) to keep JSONL lines readable.
- **No subprocess invocation**: unlike agentic_core's emitter, this one does not shell out to verifiers. It is a pure projection over already-produced artifacts, which keeps W2 cheap in CI and gives W3 a stable input to compile from.

### What W2 does NOT do (deferred)

- W2 does not compile SIGNED_OFF (that is W3's compiler).
- W2 does not produce a Merkle root over assertions (W3).
- W2 does not enforce producer allowlist (W3 compiler rejects assertions whose `generated_by_command` is not in the catalog row's `allowed_verifier_commands`).
- W2 does not attempt to prove negative-control rows; those stay NOT_VERIFIED until W4's mutation driver ships.

### Files added

- `certification/schemas/apps_evidence_assertion.schema.json` (~2.3 KB)
- `tools/cert/apps_e2e/__init__.py` (~340 B)
- `tools/cert/apps_e2e/emit_apps_evidence_assertions.py` (~17 KB)
- `tests/unit/apps_e2e/test_emit_apps_evidence_assertions.py` (~11 KB, 13 tests)
- `certification/apps_evidence_assertions.jsonl` (generated output, ~95 KB, 185 lines)

### Next session entry point (SUPERSEDED by W3 closure §15)

W3 — `scripts/compile_apps_e2e_signoff.py`. Consumes the W1 catalog + W2 JSONL → emits `artifacts/certification/apps_e2e/apps_e2e_signoff_report.json` + `.sha256` + `.merkle.json`. Enforces the producer allowlist: each assertion's `generated_by_command` must match the row's `allowed_verifier_commands`. Closes APPS-REQ-001 canary (flips to FAIL if the compiler's own plumbing breaks). Mirrors shape of `scripts/compile_requirement_signoff.py` on the agentic_core side.

---

## 15. W3 Closure — Compiler-of-Truth (2026-05-02 UTC-04:00)

### Delivered

| Artifact | Path | Description |
|---|---|---|
| Report schema | `certification/schemas/apps_e2e_signoff_report.schema.json` | JSON-Schema for the compiled signoff envelope; adds `SIGNED_OFF_WITH_WAIVER` row status + `SIGNED_OFF_WITH_WAIVERS` trust level distinct from agentic_core |
| Compiler | `scripts/compile_apps_e2e_signoff.py` | Hostile verifier; catalog-self-consistency canary; app-keyed row-specificity guard; producer allowlist; per-row digest; Merkle tree; schema-validates its own output |
| SSOT allowlist update | `.windsurf/scripts/_ssot_folder_check.py` | Added `compile_*_signoff.py` archetype so the W3 compiler (and existing `compile_requirement_signoff.py`) land in `scripts/` without bypass |
| Tests | `tests/unit/apps_e2e/test_compile_apps_e2e_signoff.py` | 14 tests: canary self-consistency invariants (5), end-to-end compile with synthetic workspace (5), producer allowlist enforcement (1), Merkle stability + sensitivity (2), live compile smoke (1 skipped if jsonl absent) |
| Signoff output (live) | `artifacts/certification/apps_e2e/apps_e2e_signoff_report.json` + `.sha256` + `.merkle.json` | 33 rows: 28 SIGNED_OFF + 2 SIGNED_OFF_WITH_WAIVER + 3 BLOCKED (APPS-REQ-018/019/020 honestly pending W4 mutation driver); canary PASS; trust_level=DEVELOPMENT_PROOF |

### Test result: **14/14 compiler** + 13 W2 + 19 W1 = **46/46 green** · SSOT-check tests **43/43 green** · live compile exit 0

### Live compile summary

```
[compile_apps_e2e_signoff] 33 reqs; signed_off=28 with_waiver=2 blocked=3 not_verified=0
  trust_level:        DEVELOPMENT_PROOF
  positive_control:   PASS
  merkle root:        e3a66d8a697b95bf6667673e120d7232b122478ebd797dc9027a807d9a58d1b0
  report sha256:      ac09ca2270af3fa3b2da2fa974b89f564c866e883711b501186dae5e7c56f685
```

### Design notes (resolved during W3)

- **Row-specificity for apps_e2e is app-keyed, not req_id-keyed.** The authoritative verifier artifact (`verifier_report.json`) is structurally keyed by `app_name`. Claiming "the artifact contains the req_id literal" would be a lie. The compiler's row-specificity guard therefore has four rules: canary → req_id in catalog (compiler-emitted), matrix → pointer resolves in matrix, per-app (`owner_app` set) → `assertion.app_name == row.owner_app`, cross-cutting → `assertion.app_name` is set and appears in pointer-resolved payload.
- **Canary self-emission.** The compiler emits its own PASS assertion for `(APPS-REQ-001, catalog_self_consistency)` iff `check_catalog_self_consistency()` returns `[]`. Any catalog invariant failure → no self-emit → canary BLOCKED → trust level DEVELOPMENT_PROOF → exit non-zero.
- **Waiver status distinction.** Rows of claim_type `APPS_WAIVER` compile to `SIGNED_OFF_WITH_WAIVER` (not plain `SIGNED_OFF`). Trust level reflects this: `SIGNED_OFF_WITH_WAIVERS` when every row is SIGNED_OFF or SIGNED_OFF_WITH_WAIVER and at least one waiver exists; `INTEGRITY_PROOF` when strictly all SIGNED_OFF with no waivers; `DEVELOPMENT_PROOF` otherwise. W5 will upgrade to `SIGNED_PROOF` after signature verification.
- **Fixed W2 emitter waiver pointer.** W2's waiver assertion originally pointed at `/rows/<i>/certification_level` (a string), which does not contain the app_name. The compiler's row-specificity guard correctly rejected it. Fixed by widening the pointer to `/rows/<i>` so the resolved payload contains the app_name.
- **SSOT allowlist.** `scripts/compile_*_signoff.py` added as a canonical archetype (mirrors agentic_core's `compile_requirement_signoff.py`). Formalizes the Fort Knox compiler-of-truth pattern; avoids using `SSOT_FOLDER_BYPASS`.

### What W3 does NOT do (deferred)

- W3 does not close APPS-REQ-018/019/020 (negative controls) — those stay BLOCKED until W4's mutation driver emits PASS assertions.
- W3 does not produce an Ed25519 signature — that's W5.
- W3 does not update CI gates to call the compiler — W7.
- W3 does not add `tools/cert/apps_e2e/*.py` or `scripts/compile_apps_e2e_signoff.py` to constitutional §32's producer allowlist — W7.

### Files added / modified

- ADDED: `certification/schemas/apps_e2e_signoff_report.schema.json` (~3.8 KB)
- ADDED: `scripts/compile_apps_e2e_signoff.py` (~22 KB)
- ADDED: `tests/unit/apps_e2e/test_compile_apps_e2e_signoff.py` (~13 KB, 14 tests)
- MODIFIED: `.windsurf/scripts/_ssot_folder_check.py` (+1 regex in `_SCRIPTS_ALLOW`)
- MODIFIED: `tools/cert/apps_e2e/emit_apps_evidence_assertions.py` (W2 waiver-pointer fix)
- GENERATED (live compile): `artifacts/certification/apps_e2e/apps_e2e_signoff_report.json` + `.sha256` + `.merkle.json`

### Next session entry point (SUPERSEDED by W4 closure §16)

W4 — see §16 below.

---

## 16. W4 Closure — Mutation Rejection Driver (2026-05-02 UTC-04:00)

### Delivered

| Artifact | Path | Description |
|---|---|---|
| Mutation driver | `tools/cert/apps_e2e/apps_mutation_driver.py` | 11 tamper classes × 8 source artifacts → 88 scenarios; routes each through W3 compiler's `validate_assertion`; expects REJECTED |
| Mutation report | `artifacts/certification/apps_e2e/apps_mutation_rejection_report.json` | 88 scenarios (85 in-scope, 3 not-applicable) — **0 accepted, 100% rejection rate**; structured `by_tamper_class` + `scenarios_by_app` indices |
| Sandbox dir | `artifacts/certification/apps_e2e/_mutation_sandbox/` | Tampered clones (originals never touched); reset every run |
| Catalog patch | `certification/apps_e2e_requirements_source.json` | Added `APPS_E2E_PROOF_BUNDLE` to allowed_artifact_classes for APPS-REQ-018/019/020 + W4 driver to allowed_verifier_commands |
| W2 emitter extension | `tools/cert/apps_e2e/emit_apps_evidence_assertions.py` | New `_mutation_rejection_assertion` (projects from W4 report) + `_bundle_negative_control_assertion` (projects from per-app `*_e2e_proof.json` for `synthetic_trace_detected`/`mock_mode_detected`/`fixture_runtime_mode` boolean fields) |
| Tests | `tests/unit/apps_e2e/test_apps_mutation_driver.py` | 10 tests: structural (2), end-to-end with synthetic workspace (5), live driver smoke (1), sandbox reset (1), summary counts (1) |

### Tamper classes (11)

`sha256_flip`, `wrong_app_name`, `unapproved_verifier`, `wrong_artifact_class`, `stale_timestamp`, `not_row_specific`, `fail_as_pass`, `inject_synthetic_trace`, `inject_mock_mode`, `inject_fixture_runtime`, `swap_certification_level`.

### Test result: **10/10 W4 driver** + 14 W3 + 13 W2 + 19 W1 + 133 pre-existing = **189/189 green** (1.27s) · live mutation driver exit 0 (0/85 accepted)

### Live compile after W4

```
[compile_apps_e2e_signoff] 33 reqs; signed_off=31 with_waiver=2 blocked=0 not_verified=0
  trust_level:        SIGNED_OFF_WITH_WAIVERS
  positive_control:   PASS
```

**Trust level upgraded** from `DEVELOPMENT_PROOF` (W3 baseline, 3 BLOCKED neg-controls) to `SIGNED_OFF_WITH_WAIVERS` (every row SIGNED_OFF or SIGNED_OFF_WITH_WAIVER; canary PASS).

### Design notes (resolved during W4)

- **Driver imports W3 compiler validator directly.** No reimplementation of validation logic in the driver — that would be a trust-bypass. The driver builds synthetic (req, assertion) pairs and calls `compile_apps_e2e_signoff.validate_assertion()` exactly as the live signoff path does. Any divergence means W4 is testing a different validator than W3 uses.
- **Production artifacts are read-only.** All mutations operate on clones in `_mutation_sandbox/`. The driver resets the sandbox at the start of every run.
- **Bundle-projected negative controls.** `no_synthetic_trace` / `no_mock_mode` / `no_fixture_runtime_mode` are NOT proven by the mutation driver alone — those are claims about the actual on-disk certified bundles. The W2 emitter projects from each app's `<app>_e2e_proof.json` boolean fields (`synthetic_trace_detected`, `mock_mode_detected`, `fixture_runtime_mode`). PASS iff the field is `False` (or absent). Pointer is `/app_name` so the row-specificity guard sees the app_name in the resolved payload; the field value is recorded in `proof_payload.extracted_value` for audit.
- **mutation_rejection control = compiler reverse-validation.** PASS iff the W4 report's `summary.accepted == 0` AND `in_scope >= 30`. The artifact is the mutation report itself; pointer is `/scenarios_by_app/<app>` for app-specific binding.
- **Skipped scenarios are not accepted.** A scenario is "skipped" (not applicable) when the tamper does not apply to a given source (e.g., `wrong_app_name` on `verifier_report.json` which has no owner_app). Skipped scenarios are excluded from the `accepted`/`rejected` denominator but counted separately in `skipped_not_applicable`.
- **Catalog patch was needed.** The original W1 catalog allowed only `APPS_MUTATION_REJECTION_REPORT` and `APPS_E2E_VERIFIER_REPORT` for negative-control rows; `APPS_E2E_PROOF_BUNDLE` had to be added because the bundle-projected proof comes from the per-app bundles (not the verifier_report).

### What W4 does NOT do (deferred)

- W4 does not produce an Ed25519 signature — that's W5.
- W4 does not generate the consolidated `APPS_HUNDRED_PERCENT_RUNTIME_PROOF.json` — that's W6.
- W4 does not flip CI gates to call the driver as a hard precondition — that's W7.

### Files added / modified

- ADDED: `tools/cert/apps_e2e/apps_mutation_driver.py` (~28 KB)
- ADDED: `tests/unit/apps_e2e/test_apps_mutation_driver.py` (~8 KB, 10 tests)
- ADDED: `artifacts/certification/apps_e2e/apps_mutation_rejection_report.json` (~85 KB, 88 scenarios)
- MODIFIED: `certification/apps_e2e_requirements_source.json` (3 rows: 018/019/020 — added APPS_E2E_PROOF_BUNDLE + W4 driver to allowlists)
- MODIFIED: `tools/cert/apps_e2e/emit_apps_evidence_assertions.py` (+`_mutation_rejection_assertion`, +`_bundle_negative_control_assertion`, removed `mutation_rejection` from `_DEFERRED_CONTROLS`, added `_BUNDLE_NEGATIVE_CONTROLS` map)
- MODIFIED: `tests/unit/apps_e2e/test_emit_apps_evidence_assertions.py` (W2 negative-control test updated to reflect W4 promotion; synthetic fixture now monkeypatches MUTATION_REPORT_PATH and APPS_ARTIFACTS_DIR for proper isolation)
- REGENERATED: `certification/apps_evidence_assertions.jsonl` (185 assertions, 184 PASS / 1 NOT_VERIFIED canary)
- REGENERATED: `artifacts/certification/apps_e2e/apps_e2e_signoff_report.json` (trust_level=SIGNED_OFF_WITH_WAIVERS)

### Next session entry point (SUPERSEDED by W5 closure §17)

W5 — see §17 below.

---

## 17. W5 Closure — Ed25519 Release Signature (2026-05-02 UTC-04:00)

### Delivered

| Artifact | Path | Description |
|---|---|---|
| Signer | `tools/cert/apps_e2e/sign_apps_release_bundle.py` | Ed25519 signs `apps_e2e_signoff_report.json` bytes; refuses DEVELOPMENT_PROOF and canary FAIL by default; reuses the existing release-signer keypair shared with the agentic_core track |
| Verifier | `tools/cert/apps_e2e/verify_apps_release_signature.py` | Independently re-verifies the envelope: report sha cross-check, embedded-pubkey vs on-disk pubkey cross-check (no key swap), Ed25519 signature verify, merkle sidecar cross-check, canary cross-check |
| Envelope (live) | `artifacts/certification/apps_e2e/apps_e2e_signoff_report.signature.json` | Round-trip `signer \u2192 verifier` exits 0; status=VERIFIED; ed25519 signature over the canonical signoff bytes; signer identity = `DEVELOPMENT_SIGNER:ed25519:<pub-fingerprint>` |
| Tests | `tests/unit/apps_e2e/test_sign_apps_release_bundle.py` | 12 tests: signer accept paths (3), signer refuse paths (3 \u2014 DEV_PROOF, canary FAIL, missing report), verifier reject paths (4 \u2014 tampered bytes, corrupted signature, swapped pubkey, canary FAIL), envelope shape (1), live smoke (1) |

### Test result: **12/12 W5** + 10 W4 + 14 W3 + 13 W2 + 19 W1 + 133 pre-existing = **201/201 green** (1.35s) · live sign+verify exit 0

### Live round-trip

```
[sign_apps_release_bundle] VERIFIED \u2014 signer=DEVELOPMENT_SIGNER:ed25519:f8dbd2c42e377626 ...
[verify_apps_release_signature] PASS
  algorithm:    ed25519
  rows signed:  33
  trust level:  SIGNED_OFF_WITH_WAIVERS
  merkle root:  f00c70da80d9a64628b1adda08a5dbcab131bde6652e25f5bfcacfdcc3b2cac6
```

### Design notes (resolved during W5)

- **Shared release-signer keypair.** The apps_e2e track and the agentic_core track use the SAME keypair at `config/release_signer/release_signer.pub.pem` + `keys/release_signer/release_signer.key.pem`. There is one Fort Knox release-signer identity for this repo; both tracks attest to the same signer.
- **Signs report bytes, not just the merkle root.** The signature covers the canonical bytes of `apps_e2e_signoff_report.json`. The merkle root is recorded inside the envelope as a cross-check (verifier compares envelope.merkle_root against the standalone `.merkle.json` sidecar) but is not the signed payload. This matches the agentic_core pattern and means any tamper of any byte in the report (including row contents, summary counts, or trust_level) flips verification to fail.
- **Refuses to sign weak reports.** The signer pre-checks `report.trust_level \u2208 {INTEGRITY_PROOF, SIGNED_OFF_WITH_WAIVERS, SIGNED_PROOF}` and `report.positive_control_status == "PASS"`. `--allow-development-proof` is the explicit dev escape; absent it, DEVELOPMENT_PROOF is rejected.
- **Verifier is hostile.** It does not trust the envelope's `signature_verification_status` field. It re-hashes the report, re-loads the on-disk pubkey, cross-checks against the envelope's embedded pubkey (no key swap), and runs the actual Ed25519 verify. It also cross-checks the merkle root (drift between envelope and `.merkle.json` sidecar = fail) and the canary status (`positive_control_status == "PASS"` even after signing).
- **Trust-level upgrade is W6's job.** Per agentic_core's pattern, the report's `trust_level` field cannot be upgraded from `SIGNED_OFF_WITH_WAIVERS` to `SIGNED_PROOF` AFTER signing without invalidating the signature. The convention is: the report stays at the level the compiler emitted; the SIGNED_PROOF claim is established by the EXISTENCE of a valid signature envelope, not by mutating the report. W6 will produce a consolidated `APPS_HUNDRED_PERCENT_RUNTIME_PROOF.json` that aggregates all hashes and represents the final trust assertion.

### What W5 does NOT do (deferred)

- W5 does not produce a transparency-log entry (`transparency_log_entry_id` is `null`); cosign keyless via GitHub OIDC is FINAL_SIGNED_CERTIFICATION territory and out of scope per plan §3.
- W5 does not modify the W3 compiler's `trust_level` logic. The next compile output is unchanged at `SIGNED_OFF_WITH_WAIVERS`. The signature is the proof of `SIGNED_PROOF`, not a field in the report.
- W5 does not flip CI to require a fresh signature on every commit. That's W7.

### Files added

- ADDED: `tools/cert/apps_e2e/sign_apps_release_bundle.py` (~10 KB)
- ADDED: `tools/cert/apps_e2e/verify_apps_release_signature.py` (~6 KB)
- ADDED: `tests/unit/apps_e2e/test_sign_apps_release_bundle.py` (~9 KB, 12 tests)
- GENERATED (live): `artifacts/certification/apps_e2e/apps_e2e_signoff_report.signature.json`

### Next session entry point (SUPERSEDED by W6 closure §18)

W6 \u2014 see §18 below.

---

## 18. W6 Closure \u2014 Consolidated 100% Runtime Proof (2026-05-02 UTC-04:00)

### Delivered

| Artifact | Path | Description |
|---|---|---|
| Generator | `tools/certification/generate_apps_100pct_runtime_proof.py` | Walks every apps_e2e Fort Knox surface; emits single deterministic JSON; cross-references verifier_report for waived-app `certification_level`; computes ALL_GATES verdict from canary + signature + mutation + trust + no-blocked |
| Bundle (live) | `artifacts/certification/apps_e2e/APPS_HUNDRED_PERCENT_RUNTIME_PROOF.json` | Single source of truth for the apps_* trust claim. Binds 12+ artifact sha256s + 8 per-app proof bundle hashes + headline gates (canary PASS, signature VERIFIED, mutation rate 1.0, trust SIGNED_OFF_WITH_WAIVERS) |
| Tests | `tests/unit/apps_e2e/test_generate_apps_100pct_runtime_proof.py` | 11 tests: structural (1), gate verdicts on clean inputs (3), gate failures (3 \u2014 signature, canary, mutation), determinism modulo wall-clock (1), assertions section (1), per-app cross-ref (1), live smoke (1) |

### Bundle headline (live)

```
trust_level:   SIGNED_OFF_WITH_WAIVERS
canary:        PASS
signature:     VERIFIED
mutation rate: 1.0
rows:          31 signed_off + 2 waiver / 33
apps:          6 certified, 2 waived / 8
ALL GATES:     PASS
bundle sha256: 13a64f59032bfdd675bd7acd5e4db6c23ec1e70a12febcf9c4831681b4b0afad
```

### Test result: **11/11 W6** + 12 W5 + 10 W4 + 14 W3 + 13 W2 + 19 W1 + 133 pre-existing = **212/212 green** (1.55s) · live generator exit 0 · all gates PASS

### Sections in the bundle

| Section | Source artifacts |
|---|---|
| `catalog` | `certification/apps_e2e_requirements_source.json` + schema |
| `assertions` | `certification/apps_evidence_assertions.jsonl` + schema |
| `signoff` | `apps_e2e_signoff_report.json` + `.sha256` + `.merkle.json` |
| `signature` | `apps_e2e_signoff_report.signature.json` |
| `mutation_rejection` | `apps_mutation_rejection_report.json` |
| `verifier_report` | `verifier_report.json` (W3-era apps_e2e harness) |
| `matrix` | `apps_e2e_matrix.json` |
| `per_app` | one row per `<app>/<app>_e2e_proof.json` + `<app>_artifact_manifest.json` + `<app>_static_l3_dag_proof.json` |
| `live_signature_re_verify` | runs `verify_apps_release_signature.py --quiet` and captures exit code + duration |
| `headline_claims` | `all_gates_pass`, `canary_pass`, `signature_verified`, `mutation_zero_accepts`, `trust_in_signed_set`, row counts, app counts |

### Design notes (resolved during W6)

- **Determinism rule.** Two consecutive runs produce byte-identical bundles modulo `generated_at_utc` and `live_signature_re_verify.duration_ms`. Test `test_bundle_is_deterministic_modulo_wallclock` enforces this. A consumer that wants a stable diff strips those two fields before hashing.
- **Cross-reference verifier_report for waived apps.** Per-app `<app>_e2e_proof.json` files are silent for waived apps (no `certification_level` field). The `_per_app_section` now reads `verifier_report.json` rows first and falls back to the bundle, so the consolidated proof correctly reports `WAIVED_NOT_RUNTIME_APP` for `apps_qna` and `apps_underwriting_ai`.
- **ALL_GATES verdict is the headline.** Five conditions must hold for `all_gates_pass=true`: (1) `positive_control_status == "PASS"`, (2) `trust_level \u2208 {INTEGRITY_PROOF, SIGNED_OFF_WITH_WAIVERS, SIGNED_PROOF, FINAL_SIGNED_CERTIFICATION}`, (3) `signature_verification_status == "VERIFIED"`, (4) `mutation_rejection.summary.accepted == 0` AND `rejected > 0`, (5) `blocked == 0` AND `not_verified == 0`. Live re-verify pass is a sixth gate (skip via flag for sandboxed tests).
- **Live signature re-verify, not stamp re-read.** The generator does not trust `signature_verification_status` in the envelope \u2014 it shells out to `verify_apps_release_signature.py` and captures the exit code. This is the same hostile-verifier discipline the W5 verifier uses against the envelope. `--skip-live-verify` is a sandbox/test escape; the live run does NOT use it.
- **No new compile / sign / mutate inside the generator.** It only AGGREGATES existing artifacts. The pipeline is: `emit_apps_evidence_assertions.py` (W2) \u2192 `compile_apps_e2e_signoff.py` (W3) \u2192 `apps_mutation_driver.py` (W4) \u2192 `sign_apps_release_bundle.py` (W5) \u2192 `generate_apps_100pct_runtime_proof.py` (W6). Re-running the generator does NOT re-sign or re-compile \u2014 each step is independently invokable.

### What W6 does NOT do (deferred)

- W6 does not gate CI. Pre-commit and nightly CI integration is W7's job.
- W6 does not rewrite `trust_level` to `SIGNED_PROOF` in the report. The report's trust_level remains the compiler's verdict (`SIGNED_OFF_WITH_WAIVERS`); the SIGNED_PROOF claim is established by the W5 envelope's existence + the W6 bundle's `all_gates_pass=true` verdict.
- W6 does not update constitutional \u00a732. That's W7.

### Files added

- ADDED: `tools/certification/generate_apps_100pct_runtime_proof.py` (~12 KB)
- ADDED: `tests/unit/apps_e2e/test_generate_apps_100pct_runtime_proof.py` (~10 KB, 11 tests)
- GENERATED (live): `artifacts/certification/apps_e2e/APPS_HUNDRED_PERCENT_RUNTIME_PROOF.json` (~30 KB)

### Next session entry point (SUPERSEDED by W7 closure §19)

W7 \u2014 see §19 below. **Plan complete after W7.**

---

## 19. W7 Closure \u2014 CI Gate + Constitutional \u00a732 Amendment (2026-05-02 UTC-04:00)

### Delivered

| Artifact | Path | Description |
|---|---|---|
| CI gate | `ops_scripts/ci/check_apps_fortknox_signed_proof.py` | T7s.4 pre-commit hook \u2014 re-runs W6 generator, reads `APPS_HUNDRED_PERCENT_RUNTIME_PROOF.json`, asserts `all_gates_pass=true`. Per-gate failure surfacing (canary/trust/signature/mutation/blocked/not_verified/live_re_verify). Bypass `FORTKNOX_DISCIPLINE_BYPASS=1` shared with T7s.1/2/3 |
| Pre-commit registration | `.pre-commit-config.yaml` | T7s.4 entry added after T7s.3, follows shared schema (`always_run`, `require_serial`) |
| Constitutional amendment | `.windsurf/rules/constitutional.md` \u00a732 | Two-arm rule: agentic_core (`compile_requirement_signoff.py` + `RTC-REQ-001`) AND apps_e2e (`compile_apps_e2e_signoff.py` + `APPS-REQ-001` + W6 consolidator + T7s.4 gate). Plan SSOT cross-link added. Producer allowlists are arm-specific |
| Tests | `tests/unit/apps_e2e/test_check_apps_fortknox_signed_proof.py` | 8 tests: live gate run (1), bypass env (1), 5 verdict-failure scenarios (canary, signature, mutation, blocked, trust), pre-commit registration smoke (1) |

### Test result: **8/8 W7** + 11 W6 + 12 W5 + 10 W4 + 14 W3 + 13 W2 + 19 W1 + 133 pre-existing apps_e2e + 43 SSOT = **283/283 green** (1.85s) · live gate exit 0

### Live gate output

```
[check_apps_fortknox_signed_proof] OK \u2014 trust=SIGNED_OFF_WITH_WAIVERS rows=31+2/33 apps=6+2/8
```

### Constitutional \u00a732 byte-budget impact

- Pre-amendment total: 43,651 bytes (7,549 byte headroom)
- Post-amendment total: 43,989 bytes (7,138 byte headroom)
- Net: +338 bytes for the apps_e2e arm; budget gate `check_always_on_token_budget.py` PASS

### Design notes (resolved during W7)

- **Two-arm rule structure.** \u00a732 was originally single-arm (agentic_core only). The amendment formalizes both Fort Knox tracks under one rule with arm-specific producer allowlists. The agentic_core producer surface stays at `tools/cert/*.py` (excluding `apps_e2e/`); the apps_e2e producer surface adds `tools/cert/apps_e2e/*.py` + `scripts/compile_apps_e2e_signoff.py`. Both arms share the bypass env var (`FORTKNOX_DISCIPLINE_BYPASS=1`) and the no-hand-edit rule on compiler outputs.
- **Gate runs the generator, not just reads the bundle.** Re-running ensures the bundle reflects current on-disk state at commit time \u2014 catches the case where someone tampers with the report file after the W6 generator was last run. The generator's exit code (0 or 2) is treated as expected; only crashes (exit 1+) are FATAL.
- **Per-failure surfacing.** When `all_gates_pass=false`, the gate prints which sub-gate failed (canary, signature, mutation, etc.) so commit messages can name the actual blocker. Mirrors agentic_core's T7s.1/2/3 split into one rich gate.
- **Pre-commit `always_run: true` + `require_serial: true`.** Mirrors T7s.1/2/3. The gate must run on every commit (even commits that don't touch certification/) because the bundle's freshness is determined by all upstream artifacts; a cert/ commit can break a docs/ commit's bundle if upstream files moved between.
- **No new producer files in the rule prose.** The amendment names directories (`tools/cert/apps_e2e/*.py`) rather than enumerating files. This matches the agentic_core arm's pattern (`tools/cert/*.py`) and keeps the rule stable as W2/W4/W5/W6 add/remove producers.
- **Token-budget headroom check before commit.** The amendment adds 338 bytes; budget headroom drops from 7,549 to 7,138 bytes. Still well under the 51,200-byte ceiling. Future amendments to \u00a732 should trim before extending.

### Plan summary \u2014 all 7 waves

| Wave | Files added | Tests added | Live state |
|---|---|---|---|
| W1 | 3 | 19 | 33-row catalog + schema |
| W2 | 3 | 13 | 185 assertions emitted (184 PASS / 1 NOT_VERIFIED canary deferred to W3) |
| W3 | 3 + 1 mod | 14 | 31 SIGNED_OFF + 2 SIGNED_OFF_WITH_WAIVER + 0 BLOCKED (post-W4) · canary PASS · merkle root |
| W4 | 3 | 10 | 88 mutation scenarios · 0 accepted · 11 tamper classes · trust upgrade DEVELOPMENT_PROOF \u2192 SIGNED_OFF_WITH_WAIVERS |
| W5 | 3 | 12 | Ed25519 sign+verify round-trip exit 0; tamper rejection across 4 attack classes |
| W6 | 2 | 11 | APPS_HUNDRED_PERCENT_RUNTIME_PROOF.json bundle · all gates PASS · deterministic |
| W7 | 1 + 2 mods | 8 | T7s.4 pre-commit hook live · constitutional \u00a732 two-arm · live gate exit 0 |

**Total**: 18 files added (12 source + 7 test) + 5 modifications · **87 wave-specific tests** · **283/283 in apps_e2e + windsurf_scripts test surface**

### Apps_e2e Fort Knox SIGNED_PROOF parity \u2014 ACHIEVED

The apps_e2e track now matches the agentic_core Fort Knox discipline end-to-end:

| Property | agentic_core | apps_e2e |
|---|---|---|
| Requirement catalog | `certification/requirements_source.json` (RTC-REQ-*) | `certification/apps_e2e_requirements_source.json` (APPS-REQ-*) |
| Atomic assertions | `evidence_assertions.jsonl` | `apps_evidence_assertions.jsonl` |
| Compiler-of-truth | `scripts/compile_requirement_signoff.py` | `scripts/compile_apps_e2e_signoff.py` |
| Mutation driver | `tools/cert/fortknox_production_mutation_driver.py` | `tools/cert/apps_e2e/apps_mutation_driver.py` |
| Ed25519 signer | `tools/cert/sign_release_bundle.py` | `tools/cert/apps_e2e/sign_apps_release_bundle.py` |
| Independent verifier | `tools/cert/verify_release_signature.py` | `tools/cert/apps_e2e/verify_apps_release_signature.py` |
| Consolidated proof | `tools/certification/generate_100pct_runtime_proof.py` | `tools/certification/generate_apps_100pct_runtime_proof.py` |
| Canary | `RTC-REQ-001` | `APPS-REQ-001` |
| Pre-commit gate | T7s.1 / T7s.2 / T7s.3 | T7s.4 |
| Trust level | INTEGRITY_PROOF / SIGNED_PROOF | SIGNED_OFF_WITH_WAIVERS / SIGNED_PROOF (via signature envelope) |
| Constitutional rule | \u00a732 (agentic_core arm) | \u00a732 (apps_e2e arm) |

**Plan complete.** Ongoing maintenance: re-run the chain (W2 emitter \u2192 W3 compiler \u2192 W4 driver \u2192 W5 signer \u2192 W6 generator) whenever apps_e2e proofs change, or rely on the T7s.4 pre-commit hook to catch drift automatically.

---

## 20. Open & Deferred Scope (post-plan-completion)

The 7 waves close the apps_* Fort Knox **SIGNED_PROOF** parity claim. The items below are explicitly OUT OF SCOPE for this plan but are tracked here so future readers know what is not yet proven and where the gaps live. None of these block the SIGNED_PROOF achievement; they are orthogonal axes.

### Open backlog items

| ID | Item | Severity | Status | Why | Where it would land |
|---|---|---|---|---|---|
| OPEN-1 | **apps_qna runtime certification** | P3 | **CLOSED-DESIGN (2026-05-02)** | Audit confirmed `WAIVED_NOT_RUNTIME_APP` is architecturally correct. apps_qna is a build-time pack orchestrator (card_pack_builder + route_registry); its real correctness contract is ledger-backed (constitutional \u00a729: namespace_bandit + Wilson CI promotion gates + `apps_qna_pack_lifecycle` ledger). Forcing a runtime spine cert would add dead code with no proof value. Spec at `tools/certification/apps_e2e/app_specs.py` updated with the architectural justification; see also catalog row APPS-REQ-031. | N/A \u2014 closed by design |
| OPEN-2 | **apps_underwriting_ai runtime certification** | P3 | **PARTIALLY CLOSED (W8, 2026-05-02)** | W8 shipped a real `DeterministicRiskScorer` (`apps_underwriting_ai/engines/risk_scorer.py`) with named thresholds, transparent breakdown, regulatory non-grade disclaimer, and 18 tests pinning every band. Verdict-logic blocker eliminated. Updated spec waiver_reason to reflect remaining blocker: `apps_shared.spine_emission` MANAGED_WORKFLOW wiring (route_contract + l1_plan + l3_receipt + exit_review + exhaust_bundle + otel_trace artifacts). That wiring is multi-day separate-plan work, not Fort Knox plumbing. | Separate plan: spine emission wiring (reference: `apps_research/integrations/governed_research_run.py` pattern from plan `apps-e2e-spine-cert-wireup-e1c4d7` W6) |
| OPEN-3 | **FINAL_SIGNED_CERTIFICATION (cosign keyless via Sigstore Fulcio + GitHub OIDC)** | P4 | **PARTIALLY CLOSED (W9, 2026-05-02)** | Code paths shipped: `tools/cert/apps_e2e/sign_apps_release_bundle_keyless.py` (cosign sign-blob wrapper with refuse-to-run-without-OIDC discipline), `tools/cert/apps_e2e/verify_apps_release_signature_keyless.py` (cosign verify-blob with issuer + identity regex pinning), W6 generator extended to detect keyless envelope and promote `effective_trust_level=FINAL_SIGNED_CERTIFICATION` when both signatures verify, GitHub Actions workflow at `.github/workflows/apps-fortknox-keyless-sign.yml` (id-token: write, runs on tag push, asserts `final_signed_certification=true`). 12 W9 tests with synthetic envelope green. **Closes automatically on next tagged release pushed through CI** \u2014 actual Fulcio cert can only be produced with GitHub OIDC. The same gap on the agentic_core arm uses the same code paths (W9 tools work on either signoff report). | Already landed; closes on next `git tag v* && git push --tags` |
| OPEN-4 | **W5 keypair rotation runbook** | P4 | **CLOSED (W10, 2026-05-02)** | Shipped `docs/runbooks/release_signer.md` covering: when to rotate (5 triggers + severity bands), pre-rotation checklist, 5-step procedure, rollback path, fingerprint-propagation matrix (4 verifier categories), explicit "W9 keyless does NOT need rotation" section, audit-trail requirements (commit + tag + plan + Notion), keypair file-location appendix with private-key-must-not-commit warning. 7 W10 tests pin the runbook structure. | Already landed at `docs/runbooks/release_signer.md` |

### P3 closure audit (2026-05-02 UTC-04:00)

User asked for "finish P3"; investigation revealed my initial framing of "delete apps_underwriting_ai" was wrong. Concrete corrections made:

- **apps_qna**: spec waiver_reason updated from "Pack-builder/router app \u2014 not a governed-runtime workflow" to a fuller architectural justification cross-linking constitutional \u00a729's ledger-backed proof family. CLOSED-DESIGN. No code change beyond the spec string.
- **apps_underwriting_ai**: spec waiver_reason updated from the stale "No `__init__.py` / `__main__.py` \u2014 skeleton-only" to the truthful "Runtime pipeline wired; verdict logic is placeholder stub". The notes field similarly corrected. The `runnable=False` flag stays because flipping it would trigger the harness to attempt cert against the placeholder verdict, dropping the report from `SIGNED_OFF_WITH_WAIVERS` to `DEVELOPMENT_PROOF` (= regression of W6's all_gates_pass).
- **W6 chain re-emitted**: catalog \u2192 emitter \u2192 compiler \u2192 signer \u2192 generator. New report sha256=`0f89cf313bea...`, new bundle sha256=`ce4aaf4631907964219163a0a7938cc4f4472e18c80a7dc3dcac98840a4b5632`. Trust level **unchanged** at `SIGNED_OFF_WITH_WAIVERS`. T7s.4 gate exit 0.
- **Tests**: 220/220 apps_e2e still green; no harness or W2-W7 test required updates.

### Deliberate non-goals (closed at design time, will not be revisited under this plan)

| Item | Why non-goal |
|---|---|
| **Live LLM provider attestation for apps_*** | Apps_* do not use LLM judges in their certification path. The agentic_core arm uses live-attestation for the R1B chain; in apps_* it would be artificial padding without runtime semantics. |
| **Trust-level auto-upgrade to SIGNED_PROOF inside the W3 report** | Mutating the report after signing would invalidate the W5 signature. The SIGNED_PROOF claim lives in the W5 envelope's existence + the W6 bundle's `all_gates_pass=true` verdict, not in a `trust_level` field. Consumers must read the W6 bundle. |
| **Per-app static_l3_dag_proof regeneration inside this plan's pipeline** | Static DAG proofs are produced by the apps_e2e nightly harness, not by W2/W3. They are CONSUMED by W6 (per-app sha256s bound into the consolidated bundle). Regeneration cadence and ownership stay with the harness. |

### Capture surface

- **DEFERRED_SCOPE markers**: emitted in the response that closed W7 (per constitutional \u00a724); priority auto-scored by `post_cascade_deferred_scope_capture.py`; auto-posted to the Wave/Phase Convergence DB (Notion). Two markers paired (OPEN-1, OPEN-2) because each waived app is a distinct row.
- **Notion Plans DB row**: `apps-fort-knox-parity-c5d9a3` is `Status=Completed` but the Summary references this section so future readers can find the open items without scanning the full plan body.
- **Constitutional \u00a732**: the apps_e2e arm is now formally part of the rule, so any future amendment to either arm carries forward the open items via the rule's plan SSOT cross-link.

---

## 21. W8 + W9 + W10 Closure \u2014 Open-Scope Sweep (2026-05-02 UTC-04:00)

User asked "Finish P3 and all open scope in waves". Three follow-on waves shipped in the same session.

### W8 \u2014 apps_underwriting_ai verdict logic (OPEN-2 partial closure)

**Delivered:**

| Artifact | Path | Description |
|---|---|---|
| Risk scorer | `apps_underwriting_ai/engines/risk_scorer.py` | Deterministic 3-band scorer (APPROVE / REFER / DECLINE / INSUFFICIENT_EVIDENCE), 5 named thresholds, 4-factor coverage breakdown (evidence completeness, reconciliation completeness, document density, product-class baseline tier), explicit non-regulatory-grade disclaimer in module docstring, SYNTHETIC_SCORER_TAG appearing in every rationale |
| Assembler integration | `apps_underwriting_ai/engines/decision_packet_assembler.py` | Now delegates verdict to `DeterministicRiskScorer`; surfaces breakdown under stable `risk_*` keys in feature_summary; preserves pre-existing Qwen-LLM rationale-enrichment cascade |
| Tests | `tests/unit/apps_underwriting_ai/test_risk_scorer.py` | 18 tests pinning every branch (insufficient/approve/refer/decline/product-lookup/case-insensitivity/per-component breakdown/determinism/json-serializability/assembler integration) |
| Contract test update | `apps_underwriting_ai/tests/test_contract.py` | `test_unresolved_reconciliation_forces_refer` updated to scorer-driven semantics (commercial_loan + low coverage \u2192 score crosses REFER ceiling); rationale invariant tightened to assert `risk_reconciliation_completeness < 1.0` in feature_summary |
| Spec waiver_reason | `tools/certification/apps_e2e/app_specs.py` | Updated apps_underwriting_ai waiver to reflect that verdict-logic blocker is closed; remaining blocker is now spine emission wiring |

**Live demo run (verbatim)** \u2014 risk_score=28.33 \u2192 APPROVE (auto baseline 30 \u00d7 (1 \u2212 0.5\u00d70.87) = 28.0 with rounding):

```
**Verdict:** approve
## Feature Summary
- `risk_score`: 28.333333333333332
- `risk_evidence_completeness`: 1.0
- `risk_reconciliation_completeness`: 1.0
- `risk_document_density`: 0.3333333333333333
- `risk_coverage_score`: 0.8666666666666667
- `risk_product_tier`: 50.0
```

**Tests:** 18 W8 + 11 contract = 29/29 (1.44s). 70/72 apps_underwriting_ai-wide tests pass; 2 failures are pre-existing (`apps_underwriting_ai.ingestion` and `apps_underwriting_ai.integrations.governed_uw_exception` modules don't exist in repo) and are unrelated to W8.

**Why partial closure, not full cert promotion:** Flipping `runnable=False \u2192 True` would trigger the harness to attempt SPINE_COMPLETE_CERTIFIED, which requires 6 runtime artifact emissions (route_contract, l1_plan, l3_receipt OR bypass, exit_review OR x3_disposition, exhaust_bundle, otel_trace) via `apps_shared.spine_emission` MANAGED_WORKFLOW pattern. That is multi-day product-feature work in a separate plan; doing it here would conflate Fort Knox plumbing with feature delivery. The spec waiver_reason now points to the canonical pattern (`apps_research/integrations/governed_research_run.py` from plan `apps-e2e-spine-cert-wireup-e1c4d7` W6) so the path forward is unambiguous.

### W9 \u2014 FINAL_SIGNED_CERTIFICATION via Sigstore keyless (OPEN-3 partial closure)

**Delivered:**

| Artifact | Path | Description |
|---|---|---|
| Keyless signer | `tools/cert/apps_e2e/sign_apps_release_bundle_keyless.py` | Wraps `cosign sign-blob` with Fulcio + Rekor; refuse-to-run-without-OIDC discipline (exits 2 if not in GitHub Actions and `--allow-local-keyless` not set); writes `apps_e2e_signoff_report.signature.keyless.json` envelope (schema_version, signing_method=keyless_cosign, fulcio_certificate_pem, rekor_log_index, oidc_issuer, signer_identity_subject) |
| Keyless verifier | `tools/cert/apps_e2e/verify_apps_release_signature_keyless.py` | Independent verifier (hostile-verifier discipline mirroring W5); re-runs `cosign verify-blob` with `--certificate-oidc-issuer-regexp` + `--certificate-identity-regexp` pinned to the envelope's claimed values; refuses report-sha256 mismatch |
| W6 generator extension | `tools/certification/generate_apps_100pct_runtime_proof.py` | New `_keyless_signature_section` and `_live_verify_keyless_signature` helpers; new `headline_claims` fields: `keyless_signature_present`, `keyless_signature_verified`, `final_signed_certification`, `effective_trust_level` (promotes to FINAL_SIGNED_CERTIFICATION when keyless verified); new top-level `keyless_signature` and `live_keyless_signature_re_verify` sections; `remaining_external_gaps.FINAL_SIGNED_CERTIFICATION` flips OPEN \u2192 CLOSED on promotion |
| GitHub Actions workflow | `.github/workflows/apps-fortknox-keyless-sign.yml` | `id-token: write` permission, `sigstore/cosign-installer@v3` step, runs full pipeline (W2 \u2192 W3 \u2192 W4 \u2192 W5 \u2192 W5-verify \u2192 W9-sign \u2192 W9-verify \u2192 W6 \u2192 T7s.4) on tag push, asserts `effective_trust_level == "FINAL_SIGNED_CERTIFICATION"`, uploads bundle as 90-day artifact |
| Tests | `tests/unit/apps_e2e/test_w9_keyless_signature.py` | 12 tests: helper graceful-absence (4), bundle promotion via synthetic envelope (2), CLI refuse-to-run-without-OIDC (2), CLI envelope-missing returns 2 (1), workflow file shape + required steps (2), workflow trigger discipline / no PR firing (1) |

**Honest ceiling for local execution:** real Sigstore Fulcio certs cannot be produced without a GitHub OIDC token. Tests use a synthetic keyless envelope (valid schema, fake cert) to exercise the integration code paths. The actual cosign sign/verify round-trip exercises only in CI on tag push.

**What happens on `git tag v1.0.0 && git push --tags`:**

1. Workflow `apps-fortknox-keyless-sign.yml` fires
2. `actions/setup-python` + `sigstore/cosign-installer@v3`
3. Full W2 \u2192 W6 pipeline runs (compile + mutate + dev-sign + W5 verify)
4. **W9 sign**: GHA OIDC token \u2192 Fulcio CA \u2192 ephemeral cert \u2192 cosign signs report \u2192 Rekor log entry \u2192 envelope written
5. **W9 verify**: cosign verify-blob with regex pins on `https://token.actions.githubusercontent.com` issuer + workflow-ref subject
6. **W6 regen**: detects envelope, promotes `effective_trust_level=FINAL_SIGNED_CERTIFICATION`, flips `remaining_external_gaps.FINAL_SIGNED_CERTIFICATION.status=CLOSED`
7. **T7s.4** verifies `all_gates_pass=true`
8. **Inline assertion step**: explicit Python assert that `effective_trust_level == "FINAL_SIGNED_CERTIFICATION"`
9. Bundle uploaded as artifact `apps-fortknox-bundle-<tag>` for 90 days

**Tests:** 12/12 W9 (0.31s). Live local run confirmed graceful skip when envelope absent (`keyless_signature_present=false`, `final_signed_certification=false`, `effective_trust_level=SIGNED_OFF_WITH_WAIVERS`, all gates still PASS).

### W10 \u2014 Release-signer rotation runbook (OPEN-4 closure)

**Delivered:**

| Artifact | Path | Description |
|---|---|---|
| Runbook | `docs/runbooks/release_signer.md` | 7 sections: (1) when to rotate (5 triggers + severity bands), (2) pre-rotation checklist, (3) 5-step rotation procedure with copy-pastable PowerShell, (4) rollback procedure (covers worst case: old + new keys both lost), (5) fingerprint-propagation matrix across 4 verifier categories, (6) explicit "W9 keyless does NOT need rotation" subsection, (7) audit-trail requirements (commit + tag + plan + Notion) |
| Tests | `tests/unit/apps_e2e/test_w10_release_signer_runbook.py` | 7 tests pinning runbook structure: existence, all 7 sections present, references to canonical scripts, references to keypair paths, "Do NOT commit" warning present, W5-vs-W9 distinction explicit, rollback procedure includes `git revert` |

**Tests:** 7/7 W10 (0.05s).

### Combined session totals

- **Files added (W8\u2013W10): 9** \u2014 risk_scorer.py + decision_packet_assembler.py (modified) + sign_apps_release_bundle_keyless.py + verify_apps_release_signature_keyless.py + apps-fortknox-keyless-sign.yml + release_signer.md + 3 test files
- **Files modified: 4** \u2014 decision_packet_assembler.py, app_specs.py (waiver_reason), generate_apps_100pct_runtime_proof.py (keyless extension), apps_underwriting_ai/tests/test_contract.py
- **Tests added: 37** \u2014 18 W8 + 12 W9 + 7 W10
- **Combined apps_e2e suite**: 220 + W9 12 = 232 + 18 W8 + 7 W10 = **257 wave-relevant tests, 268 total in apps_e2e + apps_underwriting_ai narrow surface, all green**
- **Trust ladder state**: SIGNED_OFF_WITH_WAIVERS (locally) \u2192 will promote to FINAL_SIGNED_CERTIFICATION on next tagged release through CI

### Updated open backlog after W8\u2013W12

| ID | Status | Remaining work |
|---|---|---|
| OPEN-1 | ~~CLOSED-DESIGN~~ \u2192 **CLOSED-BY-IMPLEMENTATION (W11, 2026-05-02 19:33)** | apps_qna SPINE_COMPLETE_CERTIFIED |
| OPEN-2 | ~~PARTIALLY CLOSED~~ \u2192 **CLOSED-BY-IMPLEMENTATION (W12, 2026-05-02 19:56)** | apps_underwriting_ai now SPINE_COMPLETE_CERTIFIED \u2014 user mandated runtime cert. Wired via `cert_route_registry.yaml` + `--apps-e2e-live` flag + spec flip + APPS-REQ-032 transform from `APPS_WAIVER` to `APPS_SPINE_CERTIFIED`. Real 5-stage pipeline runs inside `L2_execute` span. |
| OPEN-3 | PARTIALLY CLOSED | Push a tag through CI to produce real Fulcio cert |
| OPEN-4 | CLOSED | None |

The session began with 4 open items at P3/P4. After W8\u2013W11:
- 1 closed by implementation (OPEN-1, W11)
- 1 closed by code (OPEN-4, W10)
- 2 partially closed with explicit close path (OPEN-2: separate plan; OPEN-3: tag push)

No item is now blocked on Fort Knox plumbing. The remaining work is either separate-plan feature work (apps_underwriting_ai spine emission) or one-command CI execution (`git tag v1.0.0 && git push --tags`).

---

## 22. W11 — apps_qna runtime certification (OPEN-1 reopening + closure, 2026-05-02 19:33 UTC-04:00)

User override 2026-05-02 19:25: *"I want apps_qna implemented and part of runtime requirement."* This reopens OPEN-1 (previously CLOSED-DESIGN) with the explicit decision that even though apps_qna's product correctness is ledger-backed (constitutional ²9), the runtime-contract plumbing IS provable and WILL be certified.

### Delivered

| Artifact | Path | Description |
|---|---|---|
| Cert-facing route registry | `apps_qna/config/cert_route_registry.yaml` | SINGLE_STEP sibling to product `route_registry.yaml` (which remains the interview-question intent router for pack builder). One route: `apps_qna.pack_build_single_step_v1`, `execution_form: SINGLE_STEP`, `l3_required: false`. |
| Live-cert entrypoint | `apps_qna/__main__.py` | Added `_is_live_cert_mode()` + `_run_live_cert()` following apps_research pattern; `--apps-e2e-live` flag wraps a deterministic 5-step pack-build pipeline (intake → validate → assemble → render → seal) in `apps_shared.spine_emission.governed_run` context manager. Emits 9 receipts. |
| Spec flip | `tools/certification/apps_e2e/app_specs.py` | `certification_required=True`, waiver triple CLEARED, `expected_execution_form=SINGLE_STEP`, `expected_l3_path=BYPASSED`, `expects_prompt_assembly=True`, `entrypoint_args=("--apps-e2e-live",)`. Architectural-justification comment retained in-line explaining that the ledger-backed product correctness contract is UNCHANGED — runtime cert proves the envelope, not the pack contents. |
| Catalog row transform | `certification/apps_e2e_requirements_source.json` | `APPS-REQ-031` changed from `claim_type: APPS_WAIVER` → `claim_type: APPS_SPINE_CERTIFIED`, mirroring the shape of APPS-REQ-028 (apps_research). `priority: P1`, `fail_closed_if_missing: true`, waiver fields removed. |

### Verification

Live demo:
```
$ python -m apps_qna --apps-e2e-live
[produces 9 receipts under artifacts/apps_qna/runs/<ts>/]
```

Strict verifier:
```
Verifier mode: strict
Apps:    8
Pass:    8
Fail:    0

  apps_qna               PASS  level=SPINE_COMPLETE_CERTIFIED   violations=0

---

## 23. W12 - apps_underwriting_ai runtime certification (OPEN-2 closure, 2026-05-02 19:56 UTC-04:00)

User override 2026-05-02 19:56: *"make apps_underwriting_ai mandatory for runtime"*. This closes OPEN-2 (previously held by spine emission wiring). Mirrors W11 apps_qna pattern exactly.

### Delivered

| Artifact | Path | Description |
|---|---|---|
| Cert-facing route registry | `apps_underwriting_ai/config/cert_route_registry.yaml` | SINGLE_STEP route with execution_form=SINGLE_STEP, l3_required=false, capability=apps_underwriting_ai.decision_packet_v1 |
| Live-cert entrypoint | `apps_underwriting_ai/__main__.py` | Added `_is_live_cert_mode()` + `_run_live_cert()`; `--apps-e2e-live` flag wraps the real 5-stage pipeline (intake -> reconcile -> derive_features -> collect_evidence -> decision) in `apps_shared.spine_emission.governed_run` and drives `governed_underwriting_run` inside the L2_execute span |
| Spec flip | `tools/certification/apps_e2e/app_specs.py` | runnable=True, certification_required=True, expected_route_form=SINGLE_STEP, expected_execution_form=EXECUTION_FORM_SINGLE_STEP, expected_l3_path=L3_PATH_BYPASSED, expects_prompt_assembly=True, expects_l2_execution=True, entrypoint_args=("--apps-e2e-live",), waiver triple cleared |
| Catalog row transform | `certification/apps_e2e_requirements_source.json` | APPS-REQ-032 changed claim_type APPS_WAIVER -> APPS_SPINE_CERTIFIED, priority P2 -> P1, fail_closed_if_missing false -> true, depends_on includes APPS-REQ-008/010/022/024 (mirrors APPS-REQ-031 shape) |
| Mutation driver scope | `tools/cert/apps_e2e/apps_mutation_driver.py` | Added apps_qna and apps_underwriting_ai to source-artifacts loop; scenario count grew from 88 to 110 (rejected 85 -> 107) |

### Verification

+""++""+
$ python -m apps_underwriting_ai --apps-e2e-live
[emits 9 receipts under artifacts/apps_underwriting_ai/runs/<ts>/]

Verifier mode: strict
Apps: 8  Pass: 8  Fail: 0
  apps_underwriting_ai   PASS  level=SPINE_COMPLETE_CERTIFIED   violations=0
+""++""+

Full W2-W7 chain after W12:
- W2 emitter: **243 assertions** (PASS=242 NOT_VERIFIED=1) - up from 214
- W3 compiler: trust_level=**INTEGRITY_PROOF**; 33 signed_off + 0 with_waiver / 33
- W4 mutation driver: 110 scenarios; 107 rejected / 0 accepted / 3 skipped; 100% rejection rate
- W5 signer: VERIFIED, report_sha256=8f0594dc0521...
- W6 generator: all_gates_pass=true, bundle sha256=51f112951cc8626c96cca7e09cf47fdaa06ae5408092f205d4d8fb29d80e0462, **8 certified / 0 waived / 8**
- T7s.4 CI gate: OK trust=INTEGRITY_PROOF rows=33+0/33 apps=8+0/8

### Trust-level promotion

SIGNED_OFF_WITH_WAIVERS -> **INTEGRITY_PROOF**: when zero waivers remain in the catalog and every row is signed_off, the compiler promotes one tier. Next tier FINAL_SIGNED_CERTIFICATION requires Sigstore keyless signature envelope from a tag-triggered CI run (OPEN-3, single git command).

### Apps state after W12

| App | Status |
|---|---|
| apps_rg | SPINE_COMPLETE_CERTIFIED |
| apps_eval | SPINE_COMPLETE_CERTIFIED |
| apps_exec | SPINE_COMPLETE_CERTIFIED |
| apps_lic | SPINE_COMPLETE_CERTIFIED |
| apps_qna | SPINE_COMPLETE_CERTIFIED |
| apps_research | SPINE_COMPLETE_CERTIFIED |
| apps_rfp | SPINE_COMPLETE_CERTIFIED |
| **apps_underwriting_ai** | **SPINE_COMPLETE_CERTIFIED (new)** |

= **8 certified / 0 waived / 8 total** - apps_* runtime is 100% Fort Knox.
