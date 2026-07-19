# ADR-SR0B: Active Configuration Snapshot Authority

**Status:** APPROVED
**Date:** 2026-07-19
**Decision scope:** SR0H approval binding only; no production implementation is authorized.

## Decision Binding

- **Decision:** `SR0B_OPTION_A`
- **Contract:** `ActiveConfigSnapshotProviderV1`
- **Authority type:** `NEW_ARCHITECTURE_OWNER_DECISION`
- **Authority origin:** `USER_SUPPLIED_ARCHITECTURE_OWNER_DECISION`
- **Approving authority:** Conversation principal — Architecture Owner
- **Approval timestamp:** `2026-07-19T16:57:20-04:00`
- **Approval channel:** architecture-owner decision supplied in project conversation

This is a newly approved architecture contract. It is not a recovered source contract, frozen-source parity claim, or existing `fc703982` behavior claim.

## Recovered Source Evidence

- `agentic_core/L2_execution/enforcement/manifest_hash_validator.py` imports `agentic_core.L4_state.config.versioned_configs.get_active_configs` before validating `policy_hash`, `routing_hash`, `model_hash`, and `budget_hash`.
- `V15ExecutionGateway._validate_manifest()` conditionally invokes that validator when one or more of those manifest fields are present.
- `agentic_core/L4_state/config/versioned_configs.py` and a `config` package initializer are absent from the frozen source tree at `fc7039821148151e08459f8473cc8428df39bc8b` / `8e3fa68878aef4224f781335850a9eab7ff2c6c9`.
- The validator test is import-only. The gateway suite patches out `_get_manifest_hash_validator`, while a retrieval consumer test replaces `get_active_configs` with a mock.

## Inferred Behavior (Not Contract Authority)

- The source appears to intend binding manifest hashes to some active configuration state.
- The source does not define the authority root, profile selection, canonical bytes, required digest set, freshness rule, snapshot lifetime, or replay provenance.

These observations remain diagnostic evidence. They do not establish the approved contract.

## Newly Proposed Behavior (Historical Draft)

Before approval, Codex drafted option A as a candidate immutable-snapshot boundary. That proposal did not establish authority. The Architecture Owner decision below, not the prior proposal, is the authority for the approved behavior.

## Approved Behavior

The Architecture Owner approved `ActiveConfigSnapshotProviderV1` under `SR0B_OPTION_A`.

### Approved Rules

- One immutable configuration snapshot is loaded before the bounded operation.
- Canonicalization occurs once.
- Digest binding occurs once.
- The same snapshot is used throughout manifest-integrity enforcement.
- Missing, malformed, stale, unsupported, incomplete, drifting, or `UNKNOWN` configuration fails closed.
- Environment variables may select a declared profile before snapshot creation.
- Environment variables may not override snapshot-bound fields afterward.
- No mutable process-global fallback may fabricate active configuration.
- No silent fallback to another profile or default configuration is permitted.
- The provider is read-only.
- The provider performs no provider call or network access.
- The public contract contains no Agentic-Workflow path dependency.

### Approved Minimum Failure Reasons

- `ACTIVE_CONFIG_MISSING`
- `ACTIVE_CONFIG_MALFORMED`
- `ACTIVE_CONFIG_VERSION_UNSUPPORTED`
- `ACTIVE_CONFIG_NONCANONICAL`
- `ACTIVE_CONFIG_DIGEST_MISMATCH`
- `ACTIVE_CONFIG_PROFILE_MISMATCH`
- `ACTIVE_CONFIG_SOURCE_CHANGED`
- `ACTIVE_CONFIG_DRIFT_DURING_OPERATION`
- `ACTIVE_CONFIG_INCOMPLETE`
- `ACTIVE_CONFIG_UNKNOWN`

## Rejected Alternatives

| Option | Status | Rationale |
|---|---|---|
| `SR0B_OPTION_A` | Approved | Binds one read-only, replayable snapshot before validation and avoids mutable or remote configuration reads. |
| `SR0B_OPTION_B` | Rejected | Mutable or remote reads during validation violate the approved immutable snapshot boundary and undermine deterministic replay. |
| `SR0B_OPTION_C` | Rejected | Removing active-configuration binding is incompatible with a deterministic manifest-integrity path. |

## Approved Test Specification

A separate implementation directive must include deterministic tests for:

1. Valid snapshot.
2. Missing bundle.
3. Malformed bundle.
4. Unsupported schema.
5. Noncanonical serialization.
6. Profile mismatch.
7. Source changed during load.
8. Configuration drift during manifest construction.
9. Digest mismatch.
10. Incomplete digest set.
11. Mutable-global fallback rejection.
12. Post-snapshot environment override rejection.
13. Deterministic replay.
14. Zero writes.
15. Zero provider calls.
16. Zero network access.
17. Zero Agentic-Workflow path dependency.

## Implementation Boundary

This approval closes the SR0B contract-authority decision only. It does not authorize a production module, schema/protocol in production source, consumer integration, runtime trace, graph work, embedding work, target creation, commit, push, PR, merge, or source refreeze.
