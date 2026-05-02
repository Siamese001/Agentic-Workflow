# ADR-093 — Fort Knox Wave 1 (STATIC_ENFORCEMENT extension): zero honest yield

| Field | Value |
|---|---|
| Status | Accepted |
| Decision date | 2026-05-01 |
| Deciders | Repo owner + Cascade |
| Supersedes | — |
| Related | ADR-091 (Fort Knox certification discipline), ADR-092 (NO_BYPASS_RUNTIME verifier scope mismatch) |

## Context

A Wave 1 evidence pass was opened to extend the proven CSV-gate
positive-control fixture pattern (which signed off RTC-REQ-001/002/003/004/005/006/030/031/110/111)
to the remaining 20 open rows whose `allowed_verifier_commands` lists
`scripts/verify_rtc_req_csv_gate.py`:

```
RTC-REQ-014, 034, 040, 046, 063, 066, 067, 082, 090, 091,
              093, 094, 100, 101, 102, 103, 121, 122, 124, 127
```

Initial estimate before the audit: 10–15 honestly signed off.
Audit was performed before any code change.

## Discovery

The 10 already-SIGNED_OFF static rows passed because their **claims are
meta-claims about the CSV itself** — universe declared, schema fields
mandatory, claim-type enum enforced, acceptance legality rule, gate
readiness, Merkle root non-empty, CI gates registered. Each such claim
is directly attested by one of the CSV-gate verifier's 5 dep artifacts
(`canonical_universe_manifest`, `schema_validation_report`,
`acceptance_legality_report`, `source_divergence_report`,
`requirement_count_receipt`) by virtue of its `status: PASS`.

The 20 open rows are **not** of that nature. Their claims are about
implementation-level enforcement (provenance fields populated correctly,
subclaim decomposition complete, threshold override recorded, etc.), and
each row's `required_artifacts` field names a specific evidence artifact
that is NOT one of the 5 dep artifacts validated by the CSV-gate verifier.

### Per-row evidence gap

| Row | Title (abbreviated) | required_artifacts | Honest evidence on disk? |
|---|---|---|---|
| 014 | Runtime artifact provenance fields required | `artifact_manifest` | ❌ no `artifact_manifest_report.json`; `verify_artifact_manifest.py` ABSENT |
| 034 | Downgraded rows report required | `downgraded_rows_report.md` | ⚠️ `downgraded_rows_report.json` exists; producing verifier is `verify_runtime_certification_acceptance.py` (not currently approved). W2 territory. |
| 040 | Semantic cache requirement decomposed | `semantic_cache_subclaim_matrix` | ❌ `semantic_cache_subclaims.json` lacks per-row `req_id` keys; cannot satisfy `artifact_contains_req_id` |
| 046 | Threshold override recorded | `semantic_cache_bundle` | ❌ `semantic_cache_threshold_proof.json` lacks literal `RTC-REQ-046` |
| 063 | Cache fixture seeding labelled fixture-only | `fixture_seed_receipt` | ❌ artifact does not exist |
| 066 | Cache invalidation proof | (cache invalidation evidence) | ❌ artifact does not exist |
| 067 | L4 cache state schema fields accounted | (L4 cache state schema) | ❌ `l4_cache_state_schema_proof.json` exists but lacks literal `RTC-REQ-067` |
| 082 | Gate verdicts not final X3 | (gate verdict structure check) | ❌ artifact does not exist |
| 090–094 | architectural layer rules | (architectural conformance) | ❌ artifacts do not exist |
| 100 | SC certification report required | (SC cert report file presence) | ⚠️ `semantic_cache_certification_report.json` exists but `status: FAIL_CLOSED` |
| 101 | Runtime certification report required | (runtime cert report) | ⚠️ `rtc_req_integrated_runtime_report.json` exists with PASS per_req structure, but lacks literal `RTC-REQ-101` |
| 102, 103 | certification language rules | — | ❌ no attesting artifact |
| 121, 122 | meta-claims about coverage | — | ❌ no attesting artifact |
| 124, 127 | structural binding | — | ❌ no attesting artifact |

### Two adjacent paths surfaced (not Wave 1)

1. **RTC-REQ-014 + adjacent** could plausibly be attested if all four of
   these system-implementation pre-conditions land:
   - `scripts/verify_artifact_manifest.py` is built (currently ABSENT)
   - that verifier is registered in a `.github/workflows/*.yml` CI gate
   - `tools/cert/emit_artifact_manifest_report.py` is built and produces
     a `per_req`-keyed report containing the literal `RTC-REQ-014`
   - row's `allowed_verifier_commands` is extended to include the new
     paths

2. **RTC-REQ-034** has direct row-specific evidence today: the
   `downgraded_rows_report.json` artifact's `rule` field literally
   equals `"RTC-REQ-034"`. The producing verifier
   (`scripts/verify_runtime_certification_acceptance.py`) exists and
   exits 0. This is W2 territory and was deferred per the
   2026-05-01 wave Author-Gate.

## Decision

**Wave 1 yield: 0 SIGNED_OFF rows.** Every candidate row failed at
least one Fort Knox honesty rule (rule 8 — no fixture-only artifacts;
required `artifact_contains_req_id`; required ci_gate registration).
No code is changed in this ADR's pass. No fixture is emitted. No row's
`allowed_verifier_commands` is extended.

The wave plan stands: W2 (RTC-REQ-034 sign-off) is the next bounded
honest pass. Beyond that, the Fort Knox runtime evidence frontier
requires system implementation (new emitters and verifiers) per
ADR-091 and ADR-092.

## Consequences

- Fort Knox compiler counts are unchanged: signed_off=10, blocked=5,
  not_verified=72, total=87, trust_level=DEVELOPMENT_PROOF.
- `requirements_source.json` allowed_verifier_commands for the 20 open
  CSV-gate rows is **left unchanged**. Removing the CSV-gate verifier
  from those rows would be more drastic than the audit warrants
  (the verifier's PASS does provide *some* upstream confidence at the
  CSV-structure level, even if it does not row-specifically attest the
  claim). Future ADRs may revisit this if a finer-grained allowlist
  taxonomy is adopted.
- This ADR closes Wave 1. Reopening it requires either:
  1. A new allowlist taxonomy that lets CSV-gate-PASS attest a
     "CSV-row legality" subset of controls without claiming
     row-specific implementation evidence, OR
  2. New evidence emitters per row family (artifact_manifest,
     fixture_seed_receipt, gate_verdict_structure, etc.).

## What was NOT changed

- ❌ No `required_controls`, schemas, compiler, or bundle verifier modifications
- ❌ No `allowed_verifier_commands` modifications
- ❌ No new fixtures emitted
- ❌ No SIGNED_OFF count change
- ❌ No Merkle root change

## Audit reproducibility

The audit is reproducible by running the four commands captured in
the 2026-05-01 session transcript:

1. Open-row enumeration via the compiled report's `rows[].computed_status`
2. Per-row metadata inspection of `certification/requirements_source.json`
3. Verifier presence + CI registration check via
   `Get-ChildItem scripts/verify_*.py` and
   `Select-String -Path .github/workflows/*.yml`
4. Per-candidate-artifact deep inspection: top keys, status, literal
   `RTC-REQ-XXX` substring presence, fixture-only honesty stamps

The audit script can be re-implemented with `~50` lines of Python and
`~10` lines of shell to verify any future re-audit.
