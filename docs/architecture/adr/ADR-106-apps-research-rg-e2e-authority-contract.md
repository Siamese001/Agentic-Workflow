# ADR-106: Apps Research to Apps RG E2E Authority Contract

- **Status**: Accepted and implemented through issue #550 Waves 1-6
- **Date**: 2026-07-13
- **Baseline**: `main@de511b54dbed9be7fc63648ad175da2ae9edeefe`
- **Issue**: [#550](https://github.com/Siamese001/Agentic-Workflow/issues/550)
- **Machine-readable SSOT**: `config/certification/apps_research_rg_e2e_authority_contract.v1.json`

## Context

The Apps Research to Apps RG pipeline had strong individual receipts, but its
entrypoints did not enforce one authority chain. Issue #550 closed that false-success
risk by making the frozen contract executable across product entry, runtime Exit,
UWG, Eval, L6, mandatory closeout, and terminal sealing.

Wave 0 froze the target contract before runtime changes began. Waves 1-6 then
implemented it; the contract checker now rejects retained `current_gap_ids`.

The execution checkout did not contain an ADG SQLite snapshot. Entrypoint and module
inventory for this freeze therefore uses static executable-path inspection at the
pinned baseline; this ADR makes no ADG-backed reachability claim.

## Decision

### 1. One authority contract

`apps_research_rg_e2e_authority_contract.v1` is the only reviewed source of truth for:

- the ordered producer, consumer, receipt, schema, and transition matrix;
- the canonical run identity required by each stage declared in the SSOT;
- product, test, replay, and migration entrypoint classification;
- the exact X3 taxonomy;
- `product_authorized`, `pipeline_complete`, and
  `observability_repair_required` semantics; and
- the handoff v2, stage-ledger v2, and terminal-manifest v1 schemas.

Later waves may implement this contract but may not create a parallel authority
model. A contract change requires the SSOT, schemas, checker, tests, and this ADR's
supersession record to move together.

### 2. Canonical identity

The target v2 contract requires each declared product stage to bind this identity profile:

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
`X3_ALLOW`, `X3D`, `EXIT_OK`, and `EXIT_PARTIAL` are forbidden by the v2 product
contract. Direct section tooling is explicitly non-product; all product entrypoints
classified in the SSOT require exact `X3D_ALLOW_FINISH`.

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

Wave 0 defined their shapes; Waves 1-4 implemented producers and consumers; Wave 5
made certification result-backed; and Wave 6 removed the product-path v1 reader and
legacy aliases.

## Consequences

### Positive

- Later waves have one contract and cannot redefine authority locally.
- Product authorization is immutable across the post-boundary observer chain.
- Entrypoints and compatibility modes have explicit authority classifications.
- Schema changes become reviewable and machine checked.

### Trade-offs

- Old v1 handoff fixtures remain historical test data only and are rejected by all
  executable product readers covered by the contract-freeze checker.
- Internal lane-local shorthand may remain in explicitly non-product tooling, but it
  cannot reach product authorization or UWG finality.
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

## Completion record

- Wave 1: handoff v2 and persisted consumer validation.
- Wave 2: signed preflight, receipt-derived ledger v2, split terminal state, and UWG binding.
- Wave 3: sealed read-only Apps Eval with independently resolved evidence.
- Wave 4: exact L6 identity, byte, registry, snapshot, and closure parity.
- Wave 5: complete dependency triggers, failure injection, and JUnit-backed traceability.
- Wave 6: one product entry facade, no v1 product reader, exact X3D, and aligned docs.
