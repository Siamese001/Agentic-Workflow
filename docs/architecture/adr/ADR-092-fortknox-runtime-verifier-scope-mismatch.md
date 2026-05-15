# ADR-092 — Fort Knox runtime verifier scope mismatch (NO_BYPASS_RUNTIME rows)

| Field | Value |
|---|---|
| Status | Accepted |
| Decision date | 2026-05-01 |
| Deciders | Repo owner + Cursor Agent |
| Supersedes | — |
| Related | ADR-091 (Fort Knox certification discipline) |

## Context

While opening a runtime evidence pass for the semantic-cache subsystem
(plan B2 from the 2026-05-01 Author-Gate decision), reconnaissance found
a structural mismatch between `certification/requirements_source.json`
and the verifier surface actually present on disk.

For the three NO_BYPASS_RUNTIME rows in the candidate set:

| Row | Title | Declared `allowed_verifier_commands` |
|---|---|---|
| RTC-REQ-032 | Source divergence block | `scripts/verify_semantic_cache_certification.py`, `tools/cert/verify_cache_fixture_vs_uwg.py` |
| RTC-REQ-033 | Hardening minimum enforced | same |
| RTC-REQ-123 | Artifact payload content-hash validation | same |

Both declared verifiers are non-functional for these rows:

1. `scripts/verify_semantic_cache_certification.py` exists (18 KB) but its
   own `rule` field self-identifies as
   `"RTC-REQ-055/056/057/058 R1B subclaim gating"`. It does not process
   032/033/123. Its `in_scope_rows` are `[RTC-REQ-055, RTC-REQ-059]`. Its
   current run status is `FAIL_CLOSED` in advisory mode (`phase = W1_phase_1_sidecar_contract_only`).
2. `tools/cert/verify_cache_fixture_vs_uwg.py` does not exist on disk.
   The artifact `cache_fixture_vs_uwg_proof.json` was produced by an
   ad-hoc probe (`emitter: w1_phase_2_probe`) that explicitly stamps
   `rule_5_fixture_only_label_emitted: true` — by Fort Knox rule 8
   ("no fixture-only artifacts for runtime claims") this probe output
   cannot attest `runtime_evidence` for production rows.

The pre-existing semantic-cache artifacts that *are* on disk
(`semantic_cache_negative_controls.json`, `semantic_cache_subclaims.json`,
`semantic_cache_certification_report.json`) likewise carry fixture-only
honesty stamps (`deterministic_fixtures_only: true`,
`no_live_embedding_or_cache: true`) and therefore cannot attest
`runtime_evidence` or `no_bypass` for these three rows.

## Decision

Empty `allowed_verifier_commands` for RTC-REQ-032, RTC-REQ-033, and
RTC-REQ-123 in `certification/requirements_source.json`. Do not weaken
their `required_controls` — they continue to require
`verifier_pass`, `verifier_exit_zero`, `last_verified_timestamp`,
`no_bypass`, and `runtime_evidence`. With no approved verifier listed,
the compiler cannot accept any atomic assertion for these rows; they
remain `BLOCKED` (or `NOT_VERIFIED`), which is the truthful state.

## Consequences

- The Fort Knox compiler's `signed_off` count is unaffected (these rows
  were not signed off; they continue not to be).
- The `requirements_source.json` allowlist now reflects the actual
  attestation surface. Future recon will not find phantom verifier paths.
- Promoting any of 032/033/123 to `SIGNED_OFF` will require either:
  1. A new approved verifier built specifically for these rows
     (e.g. `scripts/verify_no_bypass_runtime.py` reading real production
     OTEL spans / UWG write-receipts), OR
  2. Extending `verify_semantic_cache_certification.py` to genuinely
     process these rows (which would require it to have something to
     verify — currently the runtime/observability/replay scope_flags are
     all `False` per the sidecar contract).
- Either path is system-implementation work, not evidence-emission work.

## What was NOT changed

- `required_controls` for any row (preserved per Fort Knox rule)
- Schemas, compiler, bundle verifier, mutation tests
- Any row's `claim_type` or `required_proof_depth`
- Any pre-existing semantic-cache artifact (untouched)

## Next steps

This ADR closes the recon. Reopening the semantic-cache runtime
evidence pass requires the system-implementation path above. No further
evidence-emission work is honest until that lands.
