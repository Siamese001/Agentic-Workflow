# ADR-106: Apps Research to Apps RG E2E Authority Contract

- **Status**: Proposed contract freeze; accepted on merge, with runtime convergence in issue #550 Waves 1-6
- **Date**: 2026-07-13
- **Baseline**: `main@de511b54dbed9be7fc63648ad175da2ae9edeefe`
- **Issue**: [#550](https://github.com/Siamese001/Agentic-Workflow/issues/550)
- **Machine-readable SSOT**: `config/certification/apps_research_rg_e2e_authority_contract.v1.json`

## Context

The Apps Research to Apps RG pipeline already has strong individual receipts, but
its entrypoints do not yet enforce one authority chain. The whole-run orchestrator,
section pre-dispatch, Apps Eval, and L6 can interpret success, identity, or evidence
with different rules. The result is a false-success risk: a downstream observer can
appear to change current-run authorization, a stage can report PASS without resolving
the authoritative receipt bytes, and a stale cross-run package can satisfy a late
binding.

Wave 0 freezes the target contract before runtime changes begin. This decision does
not claim that the current implementation already conforms. Each known divergence is
linked to issue #550 and must fail closed as its implementation wave lands.

The execution checkout did not contain an ADG SQLite snapshot. Entrypoint and module
inventory for this freeze therefore uses static executable-path inspection at the
pinned baseline; this ADR makes no ADG-backed reachability claim.

## Decision

### 1. One authority contract

`apps_research_rg_e2e_authority_contract.v1` is the only reviewed source of truth for:

- the ordered producer, consumer, receipt, schema, and transition matrix;
- the canonical run identity carried across every stage;
- product, test, replay, and migration entrypoint classification;
- the exact X3 taxonomy;
- `product_authorized`, `pipeline_complete`, and
  `observability_repair_required` semantics; and
- the handoff v2, stage-ledger v2, and terminal-manifest v1 schemas.

Later waves may implement this contract but may not create a parallel authority
model. A contract change requires the SSOT, schemas, checker, tests, and this ADR's
supersession record to move together.

### 2. Canonical identity

Every product stage binds the same identity profile:

`producer_app_id`, `consumer_app_id`, `parent_run_id`, `child_run_id`,
`request_id`, `trace_root`, `tenant_id`, `target_company`, `target_role`,
`jd_sha256`, `brief_sha256`, `policy_hash`, `blueprint_hash`, and
`schema_version`.

Missing identity is never synthesized on a product path. Normalization may create a
new digest, but it may not overwrite the raw-input digest.

### 3. Exact X3 taxonomy

The only canonical codes are:

| Code | Meaning | Authority |
|---|---|---|
| `X3A_DENY_REROUTE` | Deny or enter a separately authorized reroute | No product authorization |
| `X3B_ESCALATE_HITL` | Freeze and require human review | No product authorization |
| `X3C_COMMIT_REQUEST_TO_UWG` | Request a governed durable write | Authorizes only UWG evaluation |
| `X3D_ALLOW_FINISH` | Clear the exact output for product finalization | Product-authorization prerequisite |
| `X3E_SAFE_ABSTAIN` | Return a bounded abstention | No product authorization |

For this pipeline, only the exact string `X3D_ALLOW_FINISH` may enter product-success
logic. `X3C` is not product success; it is a request to UWG. Values such as `ALLOW`,
`X3_ALLOW`, `X3D`, `EXIT_OK`, and `EXIT_PARTIAL` are migration inputs only and are
forbidden by the v2 product contract. Their runtime removal is sequenced through the
explicit migration window in issue #550 rather than performed as an unreviewed
behavior change in this contract-only wave.

### 4. Split terminal semantics

`product_authorized=true` is permitted only after a fresh continuation, the exact
Apps Research proof chain when research is delegated, Apps RG U0 through Exit,
`X3D_ALLOW_FINISH`, product eligibility, and an UWG commit bound to the exact output
bytes. Once closed true, Apps Eval, L6, promotion, reporting, or closeout cannot
change it.

`pipeline_complete=true` additionally requires a sealed read-only Apps Eval record,
L6 closure and independent parity, a terminal promotion status, mandatory outputs,
stage-ledger v2 closure, and terminal-manifest v1 sealing.

A post-boundary failure produces `pipeline_complete=false` and
`observability_repair_required=true`. It never rewrites a closed product decision.

### 5. Entrypoint classes

Every in-scope entrypoint is classified as `product`, `test`, `replay`, or
`migration` in the SSOT. Product entrypoints bind the canonical authority contract.
Test, replay, and migration entrypoints have no product authority and cannot emit a
product terminal manifest unless they re-enter through a fresh product continuation.

### 6. Versioned artifact schemas

The frozen schemas are:

- `apps_research.apps_rg_handoff.v2`
- `apps_rg.e2e_stage_ledger.v2`
- `apps_rg.e2e_terminal_manifest.v1`

Wave 0 defines and validates their shapes. Waves 1-4 implement producers and
consumers. Wave 5 proves them end to end. Wave 6 removes the migration readers and
legacy aliases.

## Consequences

### Positive

- Later waves have one contract and cannot redefine authority locally.
- Product authorization is immutable across the post-boundary observer chain.
- Entrypoints and compatibility modes have explicit authority classifications.
- Schema changes become reviewable and machine checked.

### Trade-offs

- Current runtime artifacts remain v1 until their implementation waves land.
- Existing shorthand X3 values remain visible during migration but cannot be added to
  the v2 product-success set.
- Static inventory must be refreshed with ADG evidence when a matching snapshot is
  available.

## Enforcement

`ops_scripts/ci/check_apps_research_rg_e2e_contract_freeze.py` fails closed on:

- taxonomy or product-success alias drift;
- missing, duplicate, or disconnected stages;
- unknown entrypoint classifications or product entrypoints without the SSOT;
- post-boundary entrypoints claiming current-run authority;
- schema ID/version drift; and
- missing workflow coverage for the contract surfaces.

The checker and focused negative controls run in the existing
`apps-research-rg-handoff-e2e` workflow.

## Follow-up

- Wave 1 implements handoff v2 and persisted consumer validation.
- Wave 2 implements stage-ledger v2, terminal-state separation, and UWG binding.
- Wave 3 makes Apps Eval read-only and evidence-backed.
- Wave 4 binds L6 identity, bytes, closure, and calibration artifacts.
- Wave 5 certifies the complete chain with negative controls.
- Wave 6 ends dual-read migration and removes product-path aliases.
