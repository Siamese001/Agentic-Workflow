# All Requirements Enforcement Baseline

> **Status**: READY &mdash; master `all_requirements_gate` green, Tier 0&ndash;6 complete.
>
> **Required wording**: The full 150-row Step 1 requirement set is
> tier-assigned and protected by machine-checkable metadata enforcement,
> static evidence consistency gates, fail-closed hardening, and CI
> workflows. This does not claim real replay execution, real OTEL
> emission, full production runtime proof, or full architecture proof.

## 1. Executive summary

All 150 Step 1 requirements have been tier-assigned (Tier 0&ndash;6) and are
protected by three layers of machine enforcement: (a) a per-tier
metadata enforcement gate that refuses to ship until every selected
row reaches LINKED_LITERAL with zero blockers; (b) a per-tier
runtime/static proof gate that validates static evidence consistency
(code/validator/test/artifact/replay/negative-control/OTEL refs exist
on disk; artifact + replay JSON content matches row REQ_ID and
expected_fail_reason; replay pairs share a stable invariant_digest); and
(c) a cross-tier fail-closed hardening test suite exercising every
documented anti-cheat case via `tmp_path` copies. A master
`all-requirements-gate` aggregates all 15 verifiers and re-validates
the 150-row coverage in one command.

This baseline **does not** claim real replay execution, real OTEL
emission, full production runtime proof, or full architecture proof.

## 2. Tier count table

| Tier | Count |
|-----:|------:|
| Tier 0 | 17 |
| Tier 1 | 15 |
| Tier 2 | 22 |
| Tier 3 | 25 |
| Tier 4 | 25 |
| Tier 5 | 25 |
| Tier 6 | 21 |
| **Total** | **150** |

## 3. Full gate list

### Metadata enforcement gates (7)

- `scripts/verify_tier0_enforcement_gate.py`
- `scripts/verify_tier1_enforcement_gate.py`
- `scripts/verify_tier2_enforcement_gate.py`
- `scripts/verify_tier3_enforcement_gate.py`
- `scripts/verify_tier4_enforcement_gate.py`
- `scripts/verify_tier5_enforcement_gate.py`
- `scripts/verify_tier6_enforcement_gate.py`

### Runtime/static proof gates (7)

- `scripts/verify_tier0_runtime_proof_gate.py`
- `scripts/verify_tier1_runtime_proof_gate.py`
- `scripts/verify_tier2_runtime_proof_gate.py`
- `scripts/verify_tier3_runtime_proof_gate.py`
- `scripts/verify_tier4_runtime_proof_gate.py`
- `scripts/verify_tier5_runtime_proof_gate.py`
- `scripts/verify_tier6_runtime_proof_gate.py`

### Hardening gate (1)

- `scripts/verify_tier_gate_hardening.py`

### Master all-requirements gate (1)

- `scripts/verify_all_requirements_gates.py`

## 4. CI workflow list

| Workflow | Scope |
|----------|-------|
| `tier0-enforcement-gate.yml` | Tier 0 metadata |
| `tier0-runtime-proof-gate.yml` | Tier 0 runtime/static proof |
| `tier1-enforcement-gate.yml` | Tier 1 metadata |
| `tier1-runtime-proof-gate.yml` | Tier 1 runtime/static proof |
| `tier2-enforcement-gate.yml` | Tier 2 metadata |
| `tier2-runtime-proof-gate.yml` | Tier 2 runtime/static proof |
| `tier3-runtime-proof-gate.yml` | Tier 3 runtime/static proof (runs metadata gate transitively) |
| `tier4-runtime-proof-gate.yml` | Tier 4 runtime/static proof (runs metadata gate transitively) |
| `tier5-runtime-proof-gate.yml` | Tier 5 runtime/static proof (runs metadata gate transitively) |
| `tier6-runtime-proof-gate.yml` | Tier 6 runtime/static proof (runs metadata gate transitively) |
| `tier-gate-hardening.yml` | Cross-tier fail-closed hardening |
| `all-requirements-gate.yml` | Master aggregator (runs all 15 verifiers + 150-row coverage validation) |

**Note**: Tier 0&ndash;2 have dedicated metadata-gate workflows.
Tier 3&ndash;6 metadata gates are invoked transitively by their
runtime/static proof workflow (the verifier script subprocess-runs the
metadata gate before evaluating). The master workflow also runs every
metadata gate independently.

## 5. Hardening count

**79 cases** covering Tier 0 enforcement, Tier 1 enforcement, and Tier 0&ndash;6
runtime/static proof fail-closed paths (missing files, REQ_ID mismatches,
expected_fail_reason mismatches, replay-pair digest drift, missing
negative-control / test / code / validator / OTEL refs, Tier 6
reference-only policy violations).

## 6. Tier 6 split-mode explanation

Tier 6 is **split-mode** because it is the Step 1 tier where requirements
divide naturally into two evidence classes:

| Mode | Row count | Policy |
|------|----------:|--------|
| **MUST / RELEASE_BLOCKING** | 6 | Normal static evidence consistency: code/validator/test/artifact/replay/negative-control/OTEL refs exist on disk; artifact + replay JSONs match `step1_req_id` and `expected_fail_reason`; replay pairs share `invariant_digest`. |
| **REFERENCE / NON_BLOCKING_REFERENCE** | 15 | Reference-only policy contract: `release_gate_rule == NON_BLOCKING_REFERENCE`, `requirement_strength == REFERENCE`, `code_refs`/`validator_refs` point at `reference_only_policy_refs.py`, `artifact_refs` include `tier6_reference_only_policy.json`, policy artifact membership in `reference_only_req_ids`. |

**Reference-only rows do not claim runtime proof.** The policy artifact
declares explicit caveats: *no real replay execution, no real OTEL
emission, no runtime proof claim for these rows*. The Tier 6 runtime
proof gate enforces the partition: any attempt to attach
`replay_refs` / `otel_span_refs` / `negative_control_refs` to a
NON_BLOCKING_REFERENCE row is blocked.

## 7. Full 150-row coverage validation

| Check | Expected | Actual | Status |
|-------|---------:|-------:|:------:|
| Step 1 universe | 150 | 150 | PASSED |
| Tiered rows | 150 | 150 | PASSED |
| Distinct tiered rows | 150 | 150 | PASSED |
| Duplicates | 0 | 0 | PASSED |
| Missing | 0 | 0 | PASSED |

## 8. Exact validation commands

```
python scripts/verify_all_requirements_gates.py

python scripts/verify_tier0_enforcement_gate.py
python scripts/verify_tier0_runtime_proof_gate.py
python scripts/verify_tier1_enforcement_gate.py
python scripts/verify_tier1_runtime_proof_gate.py
python scripts/verify_tier2_enforcement_gate.py
python scripts/verify_tier2_runtime_proof_gate.py
python scripts/verify_tier3_enforcement_gate.py
python scripts/verify_tier3_runtime_proof_gate.py
python scripts/verify_tier4_enforcement_gate.py
python scripts/verify_tier4_runtime_proof_gate.py
python scripts/verify_tier5_enforcement_gate.py
python scripts/verify_tier5_runtime_proof_gate.py
python scripts/verify_tier6_enforcement_gate.py
python scripts/verify_tier6_runtime_proof_gate.py
python scripts/verify_tier_gate_hardening.py
```

## 9. Latest relevant commit hashes

| Commit | Subject |
|--------|---------|
| `aa2befcb43` | Tier 6 runtime/static proof gate + CI + 16 hardening cases |
| `391265fb7b` | Tier 6: close all 21 rows (6 MUST scenarios + 15 reference-only policy) |

Checkpoint tag: **`all-requirements-enforcement-baseline`** (attached at
the commit introducing this baseline document).

## 10. Explicit caveats

- **No full pytest** is run by any gate in this baseline.
- **No proof harness** is invoked.
- **No replay machinery** is executed.
- **No OTEL exporter** is run.
- This baseline **does not claim real replay execution**.
- This baseline **does not claim real OTEL emission**.
- This baseline **does not claim full production runtime proof**.
- This baseline **does not claim full architecture proof**.

Every gate inspects on-disk static JSON artifacts, file paths, and
metadata surfaces only. Runtime behavior is intentionally out of scope.

## 11. Next-phase roadmap (all optional, all deferred)

- **Real replay execution proof** &mdash; invoke replay machinery in CI,
  bind actual run outputs to the ledger, validate invariant_digest
  stability at runtime rather than via pre-generated fixtures.
- **Real OTEL emission proof** &mdash; exporter-in-CI verifying span
  shapes match `otel_span_refs` declarations.
- **Production runtime integration proof** &mdash; exercise the full
  L0&ndash;L6 pipeline on representative workloads with the requirements
  ledger attached.
- **Evidence freshness / drift monitor** &mdash; detect stale fixtures,
  stale reference-only policy, or selection drift; alert when Step 1
  matrices evolve out of step with the tier assignment.
- **Release dashboard** &mdash; aggregate Tier 0&ndash;6 status,
  hardening, and coverage in one human view.
