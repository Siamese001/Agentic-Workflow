# R1B Semantic Cache — Bounded-Staleness Contract

> **Status:** Effective 2026-04-23. Governs all tiers of the R1B cache stack
> (see `docs/reference/03_L0_Routing/R1B Semantic Cache.md` §Cache Tier Map).

## 1. Scope

This contract defines the **maximum age** a cached answer may reach before it
must be invalidated, refreshed, or downgraded to miss. Applies to:

- **L1 (Redis working memory)** — `memory:<ctx_hash>` entries
- **L2 (ChromaDB + SQLite long-term)** — `l2_cache` rows
- **L2 doc-to-cache inverse index** — `l2_doc_to_cache` rows

Does **not** apply to provider-side prompt caches (Anthropic ephemeral, OpenAI
prompt cache, Google Vertex context cache) — those are governed by their own
provider SLAs.

## 2. Per-Tier Bounds

| Tier | Class | Base TTL | Jitter (±) | Max age (SLA) | Event-invalidation trigger |
|---|---|---|---|---|---|
| L1 `learn()` writes | dynamic | 24 h | 10% | **26.4 h** | any scope-change (tenant/model/corpus/policy) |
| L1 `promote_to_long_term()` writes | static | 7 d | 10% | **7.7 d** | doc-fingerprint CDC event (G5) |
| L2 `l2_cache` rows | static | 7 d | none (hard expiry) | **7 d** | doc-fingerprint CDC event (G5); negative-feedback neighborhood evict (G7) |
| L2 `l2_doc_to_cache` rows | n/a | bounded by parent | n/a | bounded by parent | parent row eviction |

> **SLA statement:** under nominal operation, **no cache entry is served more
> than `base_ttl + jitter` seconds after its `written_at` timestamp.** A
> doc-fingerprint CDC event (G5) reduces this to `O(event propagation latency +
> single-flight lock TTL)` = **< 15 seconds** from event emission to scope-wide
> eviction under normal load.

## 3. Consistency Model per Tier

| Tier | Model | Rationale |
|---|---|---|
| L1 dynamic | **eventual, TTL-bounded** | Minutes of staleness tolerated; high volume, low correctness-blast-radius |
| L2 static | **bounded staleness with CDC refresh** | Document updates MUST propagate within SLA via G5 |
| Evidence-gated rows | **read-time validated** | G2 support-manifest validator fails closed on unresolvable evidence |

## 4. Failure Modes and Bounds

| Mode | Exposure | Mitigation |
|---|---|---|
| Embedding model version drift | wrong-model vectors | `_metadata.embedding_model_id` re-verified at read (G4) |
| Cited document updated | stale answer on old doc | G5 CDC scope-evicts inverse-index dependents |
| Hallucination amplification | bad entry across whole cluster | G7 `invalidate_neighborhood(query, k=5)` |
| Thundering herd on cluster invalidation | stampede | G8 single-flight lock + TTL jitter |
| Unresolvable evidence at read | broken grounding served | G2 fail-closed → miss |

## 5. Measurement

| Metric | Meaning | Alert threshold |
|---|---|---|
| `semantic_cache_hit_total{outcome}` | hits / misses / hybrid_reject / support_manifest_reject / cdc_evict / neighborhood_evict | informational |
| `semantic_cache_max_entry_age_seconds` *(to add)* | oldest live entry age | `> base_ttl + 2*jitter` → warn |
| `semantic_cache_cdc_propagation_seconds` *(to add)* | event-to-eviction latency | `> 15s / 5m` → warn |
| `semantic_cache_neighborhood_evict_total` | negative-feedback evictions | spike > 5× 24h baseline → investigate |

## 6. Operational Overrides

| Flag | Default | Effect when `=0` |
|---|---|---|
| `SEMANTIC_CACHE_HYBRID_ENABLED` | 1 | G1 disabled; pure dense cosine |
| `SEMANTIC_CACHE_SUPPORT_MANIFEST_VALIDATION` | 1 | G2 evidence check skipped |
| `SEMANTIC_CACHE_LIVE_SIGNAL_BYPASS` | 1 | G3 regex bypass disabled |
| `SEMANTIC_CACHE_CDC_ENABLED` | 1 | G5 inverse-index disabled |
| `SEMANTIC_CACHE_SINGLE_FLIGHT` | 1 | G8 lock skipped |
| `SEMANTIC_CACHE_TTL_JITTER_PCT` | 0.1 | TTL jitter disabled when `0` |

Disabling any flag degrades the SLA bounds in §2. Acceptable only with an
acknowledged runbook deviation in the MCP Registry.

## 7. References

- R1B spec — `docs/reference/03_L0_Routing/R1B Semantic Cache.md`
- Gap plan — `.codex/plans/r1b-semantic-cache-best-practices-gap-a7c3e1.md`
- Production rollout — `docs/runbooks/d2_semantic_cache_production_rollout.md`
- External source: tianpan.co 2026-04 "Cache Invalidation for AI"
