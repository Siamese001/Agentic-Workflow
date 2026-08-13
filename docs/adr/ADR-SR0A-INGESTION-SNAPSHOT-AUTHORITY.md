# ADR-SR0A: Ingestion Snapshot Authority

**Status:** APPROVED
**Date:** 2026-07-19
**Decision scope:** SR0H approval binding only; no production implementation is authorized.

## Decision Binding

- **Decision:** `SR0A_OPTION_A`
- **Contract:** `IngestionSnapshotLoaderV1`
- **Artifact classification:** `OFFLINE_DERIVED_ARTIFACT`
- **Authority type:** `NEW_ARCHITECTURE_OWNER_DECISION`
- **Authority origin:** `USER_SUPPLIED_ARCHITECTURE_OWNER_DECISION`
- **Approving authority:** Conversation principal — Architecture Owner
- **Approval timestamp:** `2026-07-19T16:57:20-04:00`
- **Approval channel:** architecture-owner decision supplied in project conversation

This is a newly approved architecture contract. It is not a recovered source contract, frozen-source parity claim, or existing `fc703982` behavior claim.

## Recovered Source Evidence

- `agentic_core/L2_execution/config/hybrid_retriever_config.py` reads `agentic_core/L4_state/memory/.sovereign_local_index.json` when that path exists. It expects a `chunks` field, builds a BM25 index, and treats only `RuntimeError` and `ValueError` as a corrupt-cache condition.
- On cache miss or those errors, `HybridRetriever.rebuild_from_ingestion()` imports `ops_scripts.dev_tools.L0_routing_scripts.sovereign_ingestion_mission.load_latest_ingested_chunks`.
- That imported module and loader do not exist in the frozen source tree at `fc7039821148151e08459f8473cc8428df39bc8b` / `8e3fa68878aef4224f781335850a9eab7ff2c6c9`.
- The available retriever test is import-only. It does not establish cache-hit validity, cache-miss behavior, schema/versioning, publication, concurrency, provenance, or durable-write authority.

## Inferred Behavior (Not Contract Authority)

- The source appears to intend a local derived index that can be reused after process restart.
- The source does not establish whether a runtime cache miss may mutate state, which producer owns chunk creation, what validates a snapshot, or whether the index is durable state.

These observations remain diagnostic evidence. They do not establish the approved contract.

## Newly Proposed Behavior (Historical Draft)

Before approval, Codex drafted option A as a candidate read-only/runtime and explicit-offline-build split. That proposal did not establish authority. The Architecture Owner decision below, not the prior proposal, is the authority for the approved behavior.

## Approved Behavior

The Architecture Owner approved `IngestionSnapshotLoaderV1` under `SR0A_OPTION_A` and classified its generated snapshot as `OFFLINE_DERIVED_ARTIFACT`.

### Approved Rules

- Runtime loading is read-only.
- Cache or snapshot miss fails closed.
- Stale, malformed, partial, incompatible, or `UNKNOWN` state fails closed.
- Runtime load never rebuilds.
- Runtime load never creates an empty fallback.
- Runtime load never creates directories as a read side effect.
- Runtime load never invokes providers or network access.
- Runtime load never repairs graph or candidate data.
- Runtime load never advances a generation pointer.
- Rebuild is an explicit offline operation.
- Offline rebuild is deterministic.
- Publication is staged, validated, immutable, and atomic.
- Pointer publication is last.
- Source and configuration digests are rechecked before activation.
- No Agentic-Workflow fallback exists in the public contract.

### Approved Minimum Failure Reasons

- `SNAPSHOT_MISSING`
- `SNAPSHOT_STALE`
- `SNAPSHOT_MALFORMED`
- `INPUT_DIGEST_MISMATCH`
- `CONFIG_DIGEST_MISMATCH`
- `SCHEMA_VERSION_MISMATCH`
- `BUILDER_VERSION_MISMATCH`
- `SNAPSHOT_VALIDATION_FAILED`
- `SNAPSHOT_PUBLICATION_INCOMPLETE`
- `REBUILD_REQUIRED`
- `REBUILD_NOT_AUTHORIZED`

## Rejected Alternatives

| Option | Status | Rationale |
|---|---|---|
| `SR0A_OPTION_A` | Approved | Keeps runtime reads side-effect free, makes generation explicit, supports replay, and avoids inherited legacy bootstrap or Redis dependencies. |
| `SR0A_OPTION_B` | Rejected | A runtime mutation request requires a separately authorized mutation workflow and publication path, neither of which is approved here. |
| `SR0A_OPTION_C` | Rejected | Excluding the conditionally reachable path would remove behavior without the approved architecture contract now supplied by option A. |

## Approved Test Specification

A separate implementation directive must include deterministic tests for:

1. Valid snapshot hit.
2. Missing snapshot.
3. Stale snapshot.
4. Malformed snapshot.
5. Wrong input digest.
6. Wrong configuration digest.
7. Wrong schema version.
8. Wrong builder version.
9. Partial publication.
10. Source drift during offline build.
11. Deterministic repeated build.
12. Concurrent builder attempt.
13. Unauthorized runtime rebuild.
14. Zero runtime writes.
15. Zero network attempts.
16. Zero provider attempts.
17. Zero source mutation.
18. Zero target-repository dependency.

## Implementation Boundary

This approval closes the SR0A contract-authority decision only. It does not authorize a production module, schema/protocol in production source, consumer integration, runtime trace, graph work, embedding work, target creation, commit, push, PR, merge, or source refreeze.
