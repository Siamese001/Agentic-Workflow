# All Requirements Merkle Root &mdash; Baseline Attestation

> **100% requirements enforcement baseline complete.**
>
> **Caveat:** This Merkle root attests the exact file and
> requirement-evidence state of the 100% requirements enforcement
> baseline. It does not claim real replay execution, real OTEL emission,
> full production runtime proof, or full architecture proof.

## 1. Executive summary

This document records the cryptographic Merkle-root attestation over
the full 150-row Step 1 requirements enforcement baseline. Every Step 1
REQ_ID is bound to exactly one tier (Tier 0&ndash;6); each REQ_ID
contributes one deterministic SHA-256 leaf that records its tier,
metadata, gate verdicts, evidence references, and the SHA-256 of every
referenced evidence file on disk. Leaves are sorted lexicographically by
`req_id` and combined pair-wise with a versioned prefix
(`REQ_NODE_V1`) up to a single root.

The root is reproducible: the verifier script recomputes it from the
written leaves on every run and refuses to exit `0` on mismatch.

## 2. Merkle root value

| Field | Value |
|-------|-------|
| Merkle scheme | `REQ_MERKLE_V1` |
| Hash algorithm | SHA-256 |
| Leaf-prefix | `b"REQ_LEAF_V1\0"` |
| Node-prefix | `b"REQ_NODE_V1\0"` |
| Leaf count | **150** |
| **First-observed Merkle root** | `31fe535c374712e7553f6f81e17c1b8bdfb1f24b38445e7d3671f1572b51a089` |
| Authoritative root file | `artifacts/runtime/requirements_proof/all_requirements_merkle_root.json` |
| Baseline tag | `all-requirements-enforcement-baseline` |
| Baseline commit | `67bc5af2031a2bf3a7c748472fd05b5460eadf5d` |
| Merkle tag | `all-requirements-merkle-root-baseline` |

The "first-observed" root is the value computed at attestation time
against the current artifact set. Any deterministic re-run of
`verify_all_requirements_merkle_root.py` must reproduce the same root
when the underlying selection files, generated metadata, and referenced
evidence files have not changed.

## 3. Tier counts (full 150-row coverage)

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

| Coverage metric | Expected | Observed | Status |
|-----------------|---------:|---------:|:------:|
| Step 1 universe | 150 | 150 | PASSED |
| Total tiered REQ_IDs | 150 | 150 | PASSED |
| Distinct tiered REQ_IDs | 150 | 150 | PASSED |
| Duplicate REQ_IDs | 0 | 0 | PASSED |
| Missing Step 1 REQ_IDs | 0 | 0 | PASSED |
| Master gate | READY | READY | PASSED |
| Hardening cases | &ge; 79 | 79 | PASSED |
| Recompute matches | true | true | PASSED |

## 4. Evidence mode counts

| Mode | Count |
|------|------:|
| `STANDARD_STATIC_EVIDENCE` | 135 |
| `REFERENCE_ONLY_POLICY` | 15 |

The 15 `REFERENCE_ONLY_POLICY` leaves correspond exactly to the 15
Tier 6 NON_BLOCKING_REFERENCE rows. Their leaves bind the SHA-256 of
`tier6_reference_only_policy.json` and the policy's
`reference_only_req_ids` membership, **not** any fake runtime proof.

## 5. Per-leaf shape

Each leaf records, at minimum:

- `req_id`, `tier`, `source_matrix_file`
- `requirement_strength`, `release_gate_rule`, `risk_category`
- `linkage_status`, `expected_fail_reason`
- `metadata_gate_result`, `runtime_static_gate_result`, `master_gate_result`
- `evidence_mode` (`STANDARD_STATIC_EVIDENCE` or `REFERENCE_ONLY_POLICY`)
- `selection_row_hash` &mdash; SHA-256 of the canonical-JSON selection row
- `metadata_row_hashes.{requirements_index,coverage_matrix,implementation_map,artifact_linkage}`
- `evidence_file_hashes.{code_refs,validator_refs,test_refs,artifact_refs,replay_refs,otel_span_refs,negative_control_refs}` &mdash; SHA-256 of the bytes of each referenced file
- `reference_only_policy_hash` (when `evidence_mode == REFERENCE_ONLY_POLICY`)
- `leaf_payload_hash` &mdash; SHA-256 over canonical-JSON of the leaf without `leaf_payload_hash`
- `leaf_node_hash` &mdash; `SHA-256(b"REQ_LEAF_V1\0" + req_id + b"\0" + leaf_payload_hash_hex)`

Canonical JSON: `sort_keys=True`, `separators=(",", ":")`,
`ensure_ascii=False`, UTF-8 bytes. Volatile timestamps
(`evaluated_at_utc`, `generated_at_utc`, `generated_at`, `timestamp`,
`run_started_at`, `run_finished_at`) are stripped from any nested gate
result objects before row-level canonical hashing; raw file bytes are
hashed unmodified so the exact run is still attested.

## 6. Output files

| File | Purpose |
|------|---------|
| `artifacts/runtime/requirements_proof/all_requirements_merkle_leaves.json` | The 150 leaves with full per-leaf evidence binding |
| `artifacts/runtime/requirements_proof/all_requirements_merkle_tree.json` | Every Merkle level from leaves up to the root |
| `artifacts/runtime/requirements_proof/all_requirements_merkle_root.json` | The root, evidence-mode counts, gate verdicts, baseline commit |
| `artifacts/runtime/requirements_proof/all_requirements_merkle_report.md` | Human-readable summary |
| `scripts/verify_all_requirements_merkle_root.py` | Reproducible verifier |
| `.github/workflows/all-requirements-merkle-root.yml` | CI gate that re-runs the verifier on PR / push to main |
| `docs/reference/contracts/enforcement/ALL_REQUIREMENTS_MERKLE_ROOT.md` | This document |
| `docs/reference/contracts/enforcement/ALL_REQUIREMENTS_MERKLE_ROOT.json` | Machine-readable companion to this document |

## 7. Exact commands run

```
python scripts/verify_all_requirements_merkle_root.py
python scripts/verify_all_requirements_gates.py
```

The Merkle verifier internally invokes the master all-requirements
gate, which itself internally invokes all 14 tier gates and the
hardening verifier. No other commands run.

## 8. Verification instructions

To reproduce the Merkle root from a clean checkout:

```
git checkout all-requirements-merkle-root-baseline
python scripts/verify_all_requirements_merkle_root.py
```

The script must exit `0` and the printed `Merkle root:` line must
match the value in &sect;2. If the underlying tier selections,
generated metadata, evidence files, or reference-only policy have
changed, the root will change; the verifier still accepts the run as
`READY` provided the recompute matches and all gate checks pass.

## 9. Caveats (verbatim)

- **No full pytest** is run by this attestation.
- **No proof harness** is invoked.
- **No replay machinery** is executed.
- **No OTEL exporter** is run.
- This Merkle root **does not claim real replay execution**.
- This Merkle root **does not claim real OTEL emission**.
- This Merkle root **does not claim full production runtime proof**.
- This Merkle root **does not claim full architecture proof**.

> This Merkle root attests the exact file and requirement-evidence
> state of the 100% requirements enforcement baseline. It does not
> claim real replay execution, real OTEL emission, full production
> runtime proof, or full architecture proof.

## 10. Next-phase roadmap (all optional, all deferred)

- Real replay execution proof: replay machinery in CI, binding actual
  run outputs to the Merkle leaf evidence set.
- Real OTEL emission proof: exporter-in-CI verifying live span shapes
  against `otel_span_refs`.
- Production runtime integration proof.
- Evidence freshness / drift monitor: recompute the Merkle root
  nightly and alert on unexpected drift.
- Release dashboard surfacing the latest Merkle root + tier verdicts
  in one human view.
