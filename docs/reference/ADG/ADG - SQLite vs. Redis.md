ADG STORAGE MODEL
=================

+---------------------------------------------------------------------------------------------------------------------------+
| DIMENSION                   | SQLITE (CANONICAL ADG DATABASE)                  | REDIS (HOT CACHE / RUNTIME LAYER)        |
|-----------------------------+----------------------------------------------------+------------------------------------------|
| ROLE                        | source of truth                                  | deterministic projection                 |
|                             | (library archive + master catalog)               | (front desk cart + quick index)          |
|-----------------------------+----------------------------------------------------+------------------------------------------|
| DATA SCOPE                  | complete nodes + full edges                      | adjacency + summaries + local subgraphs  |
|                             | (all books + full linkage records)               | (only what is needed for fast lookup)    |
|-----------------------------+----------------------------------------------------+------------------------------------------|
| METADATA / PROVENANCE       | full: edge_kind, source_file, line_no, symbol    | must be derivable or referenced          |
|                             | (exact archive citation chain)                   | (no loss, no orphan edges)               |
|-----------------------------+----------------------------------------------------+------------------------------------------|
| WRITE PATH                  | all writes originate here                        | read-only projection from SQLite         |
|                             | (archivist updates master records)               | (cart cannot author records)             |
|-----------------------------+----------------------------------------------------+------------------------------------------|
| QUERY TYPE                  | deep analysis, audit, replay, evidence           | fast lookup, module context, counts      |
|                             | (archivist research)                             | (instant front desk answers)             |
|-----------------------------+----------------------------------------------------+------------------------------------------|
| CONSISTENCY MODEL           | canonical, replayable, auditable                 | must match SQLite via digest parity      |
|                             | (rebuild yields identical archive)               | (cart mirrors archive exactly)           |
|-----------------------------+----------------------------------------------------+------------------------------------------|
| FAILURE / MISUSE RISK       | none if used correctly                           | must not become source of truth          |
|                             | (archive is authoritative)                       | (no divergence, no silent data loss)     |
|-----------------------------+----------------------------------------------------+------------------------------------------|
| ACCESS GATEWAY (MCP)        | N/A (direct access for deep audits)              | `adg_redis` server (strict read-only)    |
|                             |                                                  | (enforces freshness, schema consistency) |
|-----------------------------+----------------------------------------------------+------------------------------------------|
| USAGE DISCIPLINE            | provide authoritative evidence & provenance      | always call `adg_status` first           |
|                             | (ground truth for all judgments)                 | (if stale -> re-ingest, never mutate)    |
+---------------------------------------------------------------------------------------------------------------------------+


REQUEST FLOW & LIFECYCLE
========================

                         (1) ADG BUILD / INGEST
                                |
                                v
+----------------------------------------------------------------------------------+
| SQLITE                                                                           |
| canonical nodes + edges + provenance + violations + snapshot history             |
| (master archive + catalog + evidence ledger)                                     |
+----------------------------------------------------------------------------------+
                                |
                                | (2) deterministic projection only
                                | (no mutation, no enrichment without lineage)
                                | (parity digest enforced)
                                v
+----------------------------------------------------------------------------------+
| REDIS                                                                            |
| adjacency + summaries + freshness + module_context                               |
| (front desk cart + quick lookup index)                                           |
+----------------------------------------------------------------------------------+
                                |
                                | (3) single deterministic read gateway
                                | (all consumer access flows through here)
                                v
====================================================================================
|| *** ADG_REDIS MCP SERVER (THE SENTRY & GATEWAY) *** ||
|| (Enforces boundary, prevents Redis from becoming Source of Truth)              ||
||                                                                                ||
|| Tools:                                                                         ||
|| - Freshness: adg_status (primary), adg_assert_fresh  <-- [CHECKS SQLITE PARITY]||
|| - Metadata:  adg_meta, adg_snapshot                                            ||
|| - Graph:     adg_node, adg_nodes_by_layer,           <-- [READ-ONLY CACHE]     ||
||              adg_nodes_by_file, adg_edge_fanout,                               ||
||              adg_edge_fanin                                                    ||
|| - Audit:     adg_violations                                                    ||
|| - Low-level: redis_get, redis_hgetall, redis_smembers, redis_lrange,           ||
||              redis_scan, redis_ttl, redis_type (all type-safe)                 ||
====================================================================================
                                |
                +---------------+----------------+
                |                                |
                v                                v
      FAST RUNTIME LOOKUP                JUDGE / AUDIT / REPLAY
      (Agents / Observability)           escalate to SQLite evidence
      use Redis via MCP first            (archivist pulls exact record)
      (front desk answer)


NON-NEGOTIABLE INVARIANT
========================

SQLITE = TRUTH
(redis cart never outranks the archive)

REDIS = EXACT, HOT PROJECTION
(front desk mirrors the archive for speed)

MCP SERVER = READ-ONLY GATEWAY
(no writes/enrichments through MCP; enforces parity-preserving reads)

NO DIVERGENCE
NO SILENT METADATA LOSS
NO JUDGMENT WITHOUT SQLITE-BACKED PROVENANCE