# apps_rg — E2E Gap Remediation Plan

FORMAT_VERSION: hardened-remediation-plan-v2
PLAN_ID: apps-rg-e2e-gap-remediation-7e2d9c
PLAN_STATUS: NOT_STARTED
CURRENT_WAVE: W0
LAST_UPDATED: 2026-06-08
SCOPE: apps_rg only unless explicitly stated otherwise

---

## 0. Decision

Treat this as a **P0 system-path blocker**, not a resume-quality issue.

The immediate goal is to restore deterministic product-mode E2E generation from a clean checkout and prevent false-green runs.

### Release is blocked until

- AIG full run produces the canonical JSON resume plus required run, lane, C0.2, Exit, and aggregation artifacts.
- Brown & Brown full run produces the canonical JSON resume plus required run, lane, C0.2, Exit, and aggregation artifacts.
- Failed or blocked runs exit non-zero and always emit diagnostic evidence.
- C0.2 dense retrieval never reports PASS with zero usable evidence.
- Whole-resume aggregation and cross-section overlap checks run and pass.
- Product-mode tests run without test-harness shortcuts.

### DOCX decision

DOCX is **not required** for product success.

DOCX may exist as an optional export smoke test behind an explicit flag, but it must not block X2, X3, CI, release eligibility, or E2E closeout.

Product truth is JSON plus evidence receipts.

### Base-resume decision

Base resume is **identity source only** for generated employment sections.

Base resume may be used for:

- contact information;
- employer names;
- position titles;
- locations;
- start/end dates and current-role flag;
- education and certifications when intentionally locked copy.

Base resume must not be used for:

- bullet prose;
- claim text;
- metrics, unless separately promoted by graph/proof-pool evidence;
- seniority calibration;
- tone / voice calibration;
- scope calibration;
- proof authority for generated lanes.

Generated bullet content for Unify, IBM, InsurTech, and EY must come from graph / role-episode / proof-pool evidence and candidate-selection artifacts.

---

## 1. Current failure summary

Outcome: **BLOCKED**.

Both targets produced no required product artifacts:

- no canonical JSON resume;
- no successful run report;
- no final Exit disposition proving allow/finish;
- no whole-resume aggregation evidence;
- no cross-section overlap/dedup proof.

DOCX absence is not itself a product failure because DOCX is no longer a required product artifact.

### Observed targets

- AIG — VP, Global Head of Agentic AI Solutions: all 11 lanes ended in `X3_BLOCK / REQUIRED_PROOF_ABSENT`; provider was never called.
- Brown & Brown — SVP IT Strategy & Innovation: identical failure pattern; all 11 lanes blocked before generation.

The failure is upstream of company-specific content generation. The shared blocker is mandatory C0.2 evidence retrieval plus fresh-checkout/bootstrap gaps.

---

## 2. Hardening principles

1. **Fail loud before fixing deep logic.** A false success is worse than a red build.
2. **Fresh checkout must be diagnosable.** Missing `.env`, missing `fact_vectors`, and missing provider config must produce deterministic preflight errors.
3. **C0.2 PASS requires evidence.** PASS-with-zero selected evidence is invalid.
4. **No silent embedding fallback.** Query embedding metadata must match indexed metadata.
5. **Exit must tell the truth.** Aggregate X3 must reflect lane-level blocks, missing artifacts, and aggregate-review failures.
6. **Every terminal run emits evidence.** Blocked runs need diagnostic reports and exact blockers.
7. **Mechanical stitching is not aggregation.** The sealed section index is inventory only; whole-resume review is separate.
8. **Base resume is identity only.** Generated bullets must not use base-resume prose or base-resume metrics as proof.
9. **Product-mode tests must test product mode.** Harness/mocked runs cannot certify the fail-closed path.
10. **JSON is the product artifact.** DOCX must not be a release blocker.

---

## 3. Complete gap register — G1 through G21

| Gap | Severity | Covered by | Required remediation | Required evidence |
| --- | --- | --- | --- | --- |
| G1: Fresh checkout lacks `.env` | High | W1 | Add `doctor --strict`, `.env.example`, documented secret provisioning | Clean checkout fails actionably, then passes after provisioning |
| G2: Fresh checkout lacks `fact_vectors` / chromadb bootstrap | Critical | W1, W3 | Bootstrap `fact_vectors` from tracked graph/proof-pool sources | CI deletes cache, bootstraps, and reruns fixtures |
| G3: C0.2 dense lane PASS-but-empty | Critical | W2 | PASS only if `selected_count > 0` with valid citations | Before/after dense traces for both targets |
| G4: Integrated CLI masks failure with exit 0 | High | W1, W4 | Propagate internal error/all-lanes-blocked to process exit | All-blocked integrated run exits non-zero |
| G5: Aggregate X3 mismatch | Medium | W4 | Lane-aware aggregate disposition | `exit_disposition.json` matches lane outcomes |
| G6: Generic non-actionable errors | Medium | W1, W2 | Named blocker taxonomy | CLI/log message names exact blocker |
| G7: Stale embedding alias fallback | Medium | W2, W3 | Embedding metadata parity hard-fail | Mismatch test fails with named remediation |
| G8: Blocked-run report / renderer path drift | Medium | W4 | Always emit reports; canonical output/proof root | Blocked and green runs emit artifact manifests |
| G9: Whole-resume review exists but unproven in E2E | High | W4 | Require aggregate-review artifacts in green-run DoD | AIG and Brown & Brown emit and pass whole-resume review |
| G10: Mechanical stitching confused with aggregation | High | W4 | Treat `section_sealed_index` as inventory only | Distinct whole-resume judge artifacts exist |
| G11: Cross-section overlap / dedup not runtime-proven | High | W4 | Require cross-section X2 gates and overlap decisions | `cross_section_x2_gate_outputs.json` and `overlap_decisions.json` pass |
| G12: Aggregate judge artifacts missing from final artifact contract | High | W4 | Extend artifact manifest and schema checks | Manifest lists full-resume judge / overlap / aggregate X2 artifacts |
| G13: Aggregate failure could be masked after section success | Medium | W4 | Missing/failed aggregate review blocks final success | Forced-missing aggregate artifact test exits non-zero |
| G14: No runtime evidence of full-resume quorum behavior | Medium | W4 | Emit quorum trace with provider attempts/votes/rubric | `x1d_full_resume_judge_outputs.json` contains quorum proof |
| G15: Base-resume n-gram gate is vestigial as hard X2 | Medium | W5 | Demote base-resume n-gram from hard X2 to advisory/debug | Valid graph-generated bullet cannot fail solely on base n-gram similarity |
| G16: Base-resume authority boundary too broad | High | W3, W5 | Base resume identity-only; generated C0 excludes base prose | C0 prompt/runtime payload inventory proves no base-resume prose in generated lanes |
| G17: Locked-copy still includes generated employers | High | W4, W5 | InsurTech/EY generated content owned by generated lanes; locked copy identity only | Final assembly proves generated content + base identity atoms |
| G18: Deterministic fallback can mask generation failure | High | W5 | Empty/invalid provider output retries or blocks, never synthesizes product success | Forced-empty provider response exits non-zero and emits no product success |
| G19: Generate-N / pick-X not proven across all four employers | High | W5 | Standardize candidate pool, selected set, rejected set, selector rationale, evidence refs | All four lanes emit generate-N/select-X receipt |
| G20: Product-mode tests missing | Critical | W5 | Add product-mode E2E tests without `APPS_RG_TEST_HARNESS=1` | Tests exercise mandatory C0.2, live embeddings/config, non-zero blocked exits |
| G21: DOCX remains in product-artifact wording | Medium | W4, W5 | JSON-only product contract; DOCX optional behind explicit flag | CI has no DOCX existence assertion unless optional export job requested |

---

## 4. Critical path waves

### W0 — Freeze evidence and reproduction fixtures

Purpose: lock the failure state before changing behavior.

Actions:

- Preserve proof bundles for current AIG and Brown & Brown failures.
- Capture exact commands for:
  - clean checkout with no `.env` and no chromadb cache;
  - run pointed at populated `fact_vectors`;
  - standalone `--section` run;
  - integrated `python -m apps_rg` run.
- Add fixture manifest with expected artifact paths, expected exit codes, and expected terminal dispositions.

Acceptance tests:

- `tests/fixtures/e2e_gap_7e2d9c/manifest.json` exists.
- Failing fixture proves `provider_attempted:false` and all 11 lanes blocked.
- Fixture includes evidence for integrated CLI exit-code masking.

---

### W1 — Fresh checkout runnable and fail-loud

Purpose: stop false-green CI and remove tribal setup.

Actions:

- Add `python -m apps_rg doctor --strict`.
- Add `.env.example` with required keys and comments.
- Preflight must check:
  - required env vars;
  - provider config;
  - chromadb path;
  - `fact_vectors` existence;
  - output directory writability;
  - canonical proof/output root.
- Normalize process exit codes:
  - `0` = JSON/evidence artifacts produced and Exit allows finish;
  - `2` = preflight/config error;
  - `3` = evidence/retrieval block;
  - `4` = model/tool execution error;
  - `5` = renderer/export/artifact error;
  - `10` = internal invariant violation.
- Integrated CLI must never return 0 when internal `exit_status=error` or all mandatory lanes block.

Acceptance tests:

- Clean checkout without `.env` exits non-zero with exact missing-key list.
- Clean checkout without `fact_vectors` exits non-zero with bootstrap command suggestion.
- Integrated `python -m apps_rg ...` exits non-zero when all lanes are blocked.
- CI fails if required JSON/evidence artifacts are absent.
- DOCX absence does not fail product CI.

---

### W2 — Fix C0.2 dense lane PASS-but-empty

Purpose: make mandatory evidence retrieval truthful.

Actions:

- Add C0.2 trace fields per lane:
  - `query_text`;
  - `section_id`;
  - `collection_name`;
  - `embedding_model_id`;
  - `raw_candidate_count`;
  - `after_acl_count`;
  - `after_where_filter_count`;
  - `after_section_filter_count`;
  - `after_threshold_count`;
  - `selected_count`;
  - `dense_completed`;
  - `support_status`;
  - `block_reason`.
- Fix section filters so populated `fact_vectors` cannot be filtered to zero silently.
- Query appropriate evidence strata:
  - profile / identity facts only for locked identity fields;
  - graph / role-episode / proof-pool facts for generated content;
  - project evidence only when linked to source/proof authority.
- Add fallback from exact section metadata to broader section group only when trace records it and cited evidence exists.
- Enforce embedding parity:
  - `embedding_model_id`;
  - `embedding_dim`;
  - `embedding_provider`;
  - `index_schema_version`.
- Status rules:
  - `PASS` only if `selected_count > 0` and citations are valid;
  - `EMPTY` if collection exists but no usable facts survive filters;
  - `BLOCKED` if collection/config missing;
  - `WEAK_WITH_CAVEATS` only if evidence exists but is below full confidence.

Acceptance tests:

- Populated collection returns selected evidence or precise non-PASS reason.
- No lane sets `dense_completed=true` with `selected_count=0`.
- At least one generation lane reaches provider call for AIG and Brown & Brown once evidence exists.
- Regression test fails if where-filter removes 100 percent of raw candidates without named reason.

---

### W3 — fact_vectors bootstrap from graph/proof-pool sources

Purpose: make clean checkout reproducible without copying a private cache.

Actions:

- Add `python -m apps_rg bootstrap fact-vectors --strict`.
- Build `fact_vectors` from tracked graph/proof-pool sources, not gitignored chromadb state.
- Source inputs must include:
  - augmented skills graph / graph_8x8 competencies pool;
  - candidate fact ledger;
  - role-episode bundles;
  - proof-pool atoms;
  - section metadata mapping;
  - identity-only base-resume atoms for contact/employer/title/location/dates only.
- Base resume must not supply generated bullet prose, claim text, metrics, seniority calibration, or tone calibration.
- Bootstrap output must include:
  - collection name;
  - row counts by stratum;
  - embedding model metadata;
  - checksum of source inputs;
  - index schema version;
  - bootstrap timestamp;
  - `bootstrap_manifest.json` path.
- Bootstrap must be idempotent:
  - same inputs and embedding config produce same manifest hash;
  - changed inputs produce new manifest hash;
  - corrupt/partial collection is rebuilt or blocked with repair command.

Acceptance tests:

- CI deletes `data/cache/chromadb`, runs bootstrap, and reruns E2E fixtures.
- Bootstrap recreates expected strata counts from manifest.
- Bootstrap fails non-zero on missing source ledger or embedding mismatch.
- `doctor --strict` passes after bootstrap and fails before bootstrap.
- Base-resume prose is absent from generated-lane C0.

---

### W4 — Exit disposition, reports, renderer/export, and aggregation

Purpose: ensure terminal state matches reality and leaves usable evidence.

Actions:

- Aggregate disposition must reflect lane outcomes:
  - all mandatory lanes blocked -> aggregate blocked;
  - any required JSON/evidence artifact missing -> artifact failure;
  - generation success but aggregation failure -> aggregate failure;
  - optional DOCX export failure -> export failure only when optional export job is requested;
  - final success only when JSON, evidence, aggregate review, and Exit allow/finish all pass.
- Emit reports for every terminal state:
  - `run_report.json`;
  - `exit_disposition.json`;
  - `lane_dispositions.jsonl`;
  - `c0_2_dense_trace.jsonl` or equivalent;
  - `artifact_manifest.json`.
- Pick a canonical proof/output root and document compatibility behavior.
- Whole-resume aggregation is mandatory for product success:
  - deterministic sealed index is inventory only;
  - LLM whole-resume judge/quorum is separate;
  - cross-section overlap/dedup gates must pass;
  - aggregate failures block final X3 allow/finish.

Required aggregate artifacts:

- `section_sealed_index.json`;
- assembled full-resume text artifact;
- `x1d_full_resume_judge_outputs.json`;
- `cross_section_x2_gate_outputs.json`;
- `overlap_decisions.json`;
- final aggregate X2 receipt;
- aggregate entries in `artifact_manifest.json`;
- aggregate summary in `run_report.json` and `exit_disposition.json`.

Acceptance tests:

- Blocked run emits run report and exits non-zero.
- Successful E2E run emits JSON resume, artifact manifest, run report, Exit disposition, aggregate artifacts, and X3 allow/finish disposition.
- Missing aggregate artifact blocks final success.
- DOCX is optional only and not asserted by product CI.

---

### W5 — Product-mode tests and vestigial artifact cleanup

Purpose: close the structural testing gap and remove old-model remnants.

Actions:

- Add product-mode tests that do not set `APPS_RG_TEST_HARNESS=1`.
- Demote base-resume n-gram overlap from hard X2 to advisory/debug.
- Keep exact/verbatim base-resume bullet copy blockers.
- Keep hydration-operation blockers.
- Add C0 inventory test proving base-resume prose is absent from generated-lane C0.
- Remove DOCX from required success gates and CI.
- Remove generated employer content from locked-copy ownership; keep only identity atoms.
- Prohibit deterministic fallback from becoming product success.
- Standardize generate-N / select-X receipts across:
  - Unify;
  - IBM;
  - InsurTech;
  - EY.

Required checks:

1. `product-mode-does-not-set-test-harness`
2. `mandatory-c0-2-runs-in-product-mode`
3. `all-lanes-blocked-exits-nonzero`
4. `base-resume-prose-not-in-generated-lane-c0`
5. `base-resume-hydration-operation-fails`
6. `verbatim-base-resume-bullet-output-fails`
7. `valid-graph-generated-bullet-not-blocked-by-base-ngram`
8. `unify-ibm-insurtech-ey-record-generate-n-select-x`
9. `docx-not-required-for-product-success`
10. `json-and-aggregate-artifacts-required-for-product-success`
11. `aggregate-review-failure-blocks-final-x3`
12. `empty-provider-output-does-not-fallback-to-product-success`

Acceptance tests:

- Product-mode E2E exercises mandatory C0.2 and fails closed when evidence is absent.
- Valid graph-generated bullets cannot fail solely due to base-resume n-gram similarity.
- Verbatim base-resume bullet output still fails.
- Any change-log hydration operation still fails.
- Empty/invalid provider output retries or blocks; it does not produce product success via deterministic fallback.
- All four employer lanes emit generate-N/select-X evidence receipts.
- JSON-only product success passes without DOCX.

---

## 5. CI contract

Required checks before remediation closeout:

1. `doctor-clean-checkout-fails-actionably`
2. `bootstrap-fact-vectors-from-source`
3. `c0-2-populated-collection-has-evidence-or-named-nonpass`
4. `integrated-cli-fails-when-all-lanes-block`
5. `blocked-run-emits-run-report`
6. `aig-e2e-produces-json-and-evidence-artifacts`
7. `brown-brown-e2e-produces-json-and-evidence-artifacts`
8. `artifact-contract-validates-output-paths`
9. `full-resume-assembly-artifact-present`
10. `full-resume-llm-coherence-quorum-executed`
11. `cross-section-overlap-gates-pass`
12. `aggregate-review-failure-blocks-final-x3`
13. `artifact-manifest-includes-aggregate-review`
14. `product-mode-does-not-set-test-harness`
15. `docx-not-required-for-product-success`
16. `generate-n-select-x-receipts-for-all-employers`

CI must assert file existence and schema validity for:

- canonical JSON resume artifact;
- `run_report.json`;
- `exit_disposition.json`;
- `artifact_manifest.json`;
- lane disposition receipt;
- C0.2 trace receipt;
- aggregate judge artifacts;
- cross-section overlap artifacts.

CI must not assert DOCX existence unless running an explicitly optional export job.

---

## 6. PR sequencing

### PR 1 — Fail-loud runtime shell

- W0 fixture freeze.
- W1 doctor/preflight.
- Exit-code propagation.
- No retrieval algorithm changes.

### PR 2 — C0.2 instrumentation

- Dense trace fields.
- Status fields.
- No behavior changes except invariant fail-loud checks.

### PR 3 — C0.2 retrieval fix

- Section filter fix.
- Evidence-strata query logic.
- Status rule change.
- Embedding parity enforcement.

### PR 4 — fact_vectors bootstrap

- Bootstrap CLI.
- Manifest/checksum.
- Clean-cache CI rebuild.
- Base-resume identity-only source boundary.

### PR 5 — Exit/report/aggregation contract

- Aggregate disposition fix.
- Always-on run reports.
- Canonical proof/output directory.
- Artifact manifest.
- Whole-resume judge/overlap gates as required product artifacts.
- DOCX optional only.

### PR 6 — Product-mode tests and vestigial artifact cleanup

- Demote base-resume n-gram hard gate to advisory/debug.
- Keep exact-copy and hydration blockers.
- Remove generated employer content from locked-copy ownership.
- Prohibit deterministic fallback from becoming product success.
- Standardize generate-N/select-X receipts across Unify, IBM, InsurTech, EY.
- Add product-mode tests without harness shortcuts.

### PR 7 — E2E proof closeout

- AIG green proof.
- Brown & Brown green proof.
- Final evidence bundle linked from this plan.
- Closeout proves JSON, lane evidence, C0.2 traces, aggregate artifacts, and final Exit disposition.
- DOCX is optional and not part of closeout gate.

---

## 7. Final Definition of Done

This remediation is complete only when all of the following are true:

- Clean checkout can run `doctor --strict` and explain all missing prerequisites.
- After documented env/secrets provisioning and `bootstrap fact-vectors`, `doctor --strict` passes.
- AIG full run produces:
  - canonical JSON resume artifact;
  - `run_report.json`;
  - `exit_disposition.json`;
  - `artifact_manifest.json`;
  - lane evidence receipts;
  - C0.2 trace receipts;
  - aggregate review artifacts;
  - cross-section overlap artifacts.
- Brown & Brown full run produces the same required artifacts.
- No mandatory lane fails with `REQUIRED_PROOF_ABSENT` when `fact_vectors` is populated correctly.
- C0.2 cannot emit PASS with zero selected evidence.
- Integrated CLI exits non-zero for blocked/error runs.
- Blocked runs emit diagnostic reports.
- Whole-resume aggregation executes and passes.
- Aggregate-review failure blocks final X3 allow/finish.
- Generated employment content uses graph/proof-pool evidence, not base-resume prose.
- Base-resume identity fields are preserved exactly.
- All four employer lanes prove generate-N/select-X behavior.
- Product-mode tests run without harness shortcuts.
- DOCX absence does not fail product success.
- All G1-G21 are either fixed or explicitly deferred with owner, rationale, and non-release-blocking status.

---

## 8. Open decisions to close before PR 3

- What is the canonical output/proof root: `runtime_proofs/` or `runs/`?
- Which graph/proof-pool files are authoritative for `fact_vectors` bootstrap?
- What is the canonical embedding model ID and dimension?
- Should AIG and Brown & Brown be required PR checks or nightly smoke checks after remediation closes?
- What is the canonical JSON resume artifact path?
- What is the exact generate-N and select-X count per employer lane?
- Which optional flag, if any, enables DOCX export smoke testing?

---

## 9. Immediate command shape

```bash
python -m apps_rg doctor --strict
python -m apps_rg bootstrap fact-vectors --strict
python -m apps_rg --target aig --strict --proof-dir runtime_proofs/aig
python -m apps_rg --target brown-brown --strict --proof-dir runtime_proofs/brown-brown
python -m apps_rg verify-artifacts --json-only runtime_proofs/aig runtime_proofs/brown-brown
```

The actual flags should match the repo CLI style, but the behavior above is non-negotiable.

---

## 10. Non-goals until first green

- Resume wording, layout, or cosmetic quality tuning.
- DOCX rendering as required product output.
- New agent architecture.
- Multi-company generalization beyond the two failing fixtures.
- Allowing base-resume prose to become proof substrate.
- Treating harness-mode tests as product proof.
