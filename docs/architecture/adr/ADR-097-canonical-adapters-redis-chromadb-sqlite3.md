# ADR-097 — Canonical Adapters for `redis`, `chromadb`, `sqlite3`

Status: **Accepted** · 2026-05-03 · Tier: T3 governance · Layer: L4_state

## Context

ADG snapshot `adg_indexed_05032026_0645.sqlite` reports `v_p2_duplicated_adapters` and `v_p2_mixed_usage` P2 views listing three infra primitives with multi-adapter state:

| Infra | Duplicated adapters | Direct use | Wrapped use |
|---|---|---:|---:|
| `redis` | `sovereign_redis_orchestrator.py`, `semantic_cache_manager.py`, `redis_cache_client.py` | 10 | 3 |
| `chromadb` | `gptcache_client.py`, `chroma_client.py` | 10 | 2 |
| `sqlite3` | `gptcache_client.py`, `semantic_cache_manager.py`, `repo_signal_adapter.py`, `sqlite_memory_store.py` | **276** | 4 |

Plus two AP-14 `agentic_antipattern` module-level flags:

- `agentic_core/L4_state/utils/memory/canonical_store.py`
- `apps_rg/enforcement/HardenedanthropicexecutorStrategy.py`

The sqlite3 count (276 direct vs 4 wrapped) makes a big-bang "wrap everything" migration infeasible. ADG doctrine (`adg-canonical-invariants.md`) says we name the canonical adapter, declare the others legacy, and institute a deprecation schedule rather than rip-and-replace.

## Decision

### Canonical Adapters

| Infra | Canonical adapter module | Purpose |
|---|---|---|
| `redis` | `agentic_core/cache/redis_cache_client.py` | Thin connection + serialization wrapper; used by ADG hot-cache ingest (`tools/adg/adg_redis_ingest.py`). New code uses this. |
| `chromadb` | `agentic_core/L4_state/utils/client/chroma_client.py` | Already the "wrapped" adapter per `v_p2_mixed_usage`. New code uses this. |
| `sqlite3` | **None — stdlib sqlite3 is the canonical adapter.** | sqlite3 is a stdlib module with no third-party wrapping needed for the project's usage patterns. The 276 direct uses are legitimate. |

### sqlite3 Disposition

The flagging of 276 `sqlite3` direct uses as "duplicated adapter" is a **classification error in the ADG P2 rule**: stdlib modules do not need a project-specific wrapper to be canonical. The P2 rule treats any Python module imported in 3+ files as a candidate for canonical-adapter review; for stdlib modules with no injected side-effects this is a false signal.

**Disposition**: `sqlite3` is DECLARED canonical-as-stdlib. The 4 "wrapped" adapters (`gptcache_client`, `semantic_cache_manager`, `repo_signal_adapter`, `sqlite_memory_store`) are specialized stores, not competing general-purpose adapters — each owns a distinct data surface. The P2 view entry for `sqlite3` SHOULD be suppressed in a future `tools/adg/*` rule update (DEFERRED_SCOPE).

### redis / chromadb Disposition

For redis and chromadb, the canonical wrapper IS project-specific (connection pooling, error translation, deterministic serialization), so legacy direct-use sites under `agentic_core/L3_orchestration/reasoning/engines/sovereign_redis_orchestrator.py`, `agentic_core/L4_state/cache/gptcache_client.py`, `agentic_core/L4_state/utils/memory/semantic_cache_manager.py`, `apps_shared/data_adapters/repo_signal_adapter.py`, and `tools/memory/sqlite_memory_store.py` (the chromadb ones) remain PERMITTED with the understanding that:

1. **No new code adds new direct-use sites.** New code uses the canonical adapter.
2. **Legacy sites are not a refactor priority** — they work, they have tests, they carry operational knowledge (e.g., `sovereign_redis_orchestrator.py` has tuning specific to its distributed coordination role).
3. **Consolidation is opt-in** — a future session may consolidate if operational churn justifies it.

### AP-14 Sites

| Site | Treatment |
|---|---|
| `agentic_core/L4_state/utils/memory/canonical_store.py` | The name promises canonical — in practice the module is canonical for its scope (L4 canonical memory). The AP-14 flag likely arises from its direct sqlite3 use; per this ADR's §"sqlite3 Disposition" that is accepted. **Disposition**: approved_exempt. |
| `apps_rg/enforcement/HardenedanthropicexecutorStrategy.py` | The AP-14 flag is on a strategy implementation, not an adapter. Likely a stale classification. **Disposition**: approved_exempt pending a targeted re-scan. |

### Enforcement

No code changes required. The classifier heuristic `v_p2_duplicated_adapters` / `v_p2_mixed_usage` in `tools/adg/*` SHOULD learn to:

1. Exempt stdlib modules (sqlite3, json, urllib, etc.) from the "duplicated adapter" signal.
2. Recognize specialized-store patterns (module A wraps sqlite3 for memory, module B wraps for cache) as legitimate rather than duplication.

This classifier refinement is DEFERRED to a separate T2 tooling session (slug: `p2-view-classifier-refinement`).

## Consequences

### Positive

- **Writers know the canonical target** for new redis / chromadb code.
- **sqlite3 is de-mystified** — the 276 direct uses are no longer a pending refactor.
- **AP-14 sites get a clear disposition** instead of rotting at `disp=untriaged`.
- **Zero code changes** — this ADR is docs-only.

### Negative

- **P2 views still flag the current sites** until the classifier is refined. Acceptable because the ADR documents the acceptance and the classifier-refinement is tracked as DEFERRED_SCOPE.
- **Legacy direct-use sites may drift** — without refactor pressure, the `sovereign_redis_orchestrator.py` direct-redis-use becomes a permanent structural exception. This is explicit, not accidental.

### Neutral / deferred

- **Classifier refinement** — DEFERRED_SCOPE: slug=`p2-view-classifier-refinement` phase=followup reason=P2-views-need-stdlib-exemption-and-specialized-store-recognition.

## Cross-References

- ADR-035 — Layered adapter composition is not duplication
- `adg-canonical-invariants.md` §5 — Hotspot archetypes (STATE_NODE applies here)
- Parent plan: `.codex/plans/p1p2-burndown-followup-a2e4c7.md` W3-01
