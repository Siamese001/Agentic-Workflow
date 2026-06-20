---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\historical_plans_20260515_cursor_optimization\\chroma-graphrag-lic-rg-research-f4a2e9.md'
original_relative_path: '_archive\\historical_plans_20260515_cursor_optimization\\chroma-graphrag-lic-rg-research-f4a2e9.md'
source_sha256: bb0c8f0fff07f21f288c4632ad8eee9d759bc0921cd5053c02353fc7d092dda5
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: chroma-graphrag-lic-rg-research-f4a2e9
plan_type: refactor
hardened_at: 2026-05-11
hardening_verdict: ACCEPT_WITH_HARDENING
no_core_rebaseline_at: 2026-05-11
no_core_rebaseline_verdict: NO_AGENTIC_CORE_TOUCHES_PERMITTED
---

# ChromaDB + C0.3 Graph RAG Remediation — apps_lic, apps_rg, apps_research

Wire all ChromaDB semantic cache gaps, fix the apps_lic P0 boundary violation, and enable C0.3 Graph RAG (`run_graph_traverse`) for all three apps across a W0–W6 plan.

> **Hardening note (2026-05-11)**: Prior draft described a "four-wave plan" but contained W0–W5; wave count corrected to W0–W6. Two explicit `GENERIC_INFRA_EDIT` labels added to `agentic_core` edits. Five plan contradictions resolved (CONT-1 through CONT-5). Evidence register validated against 13 source files. No runtime code changed in hardening pass.
>
> **No-core rebaseline (2026-05-11)**: W4 and beyond were stopped before execution. All plan-owned `agentic_core/` changes (W2/W3 GENERIC_INFRA_EDITs) were reverted and backed up to `artifacts/chromadb_graphrag_remediation/agentic_core_rollback_backup.patch`. Two unrelated `agentic_core/` files (`apps_rg_pa_binding.py`, `apps_rg_exit_binding.py`) from plan `apps-rg-exit-gate-harness-wiring-e4b7f2` were preserved. The original W1–W6 wave numbering is retained for reference; active work proceeds on the W*N (no-core) track. W1N completed: `apps_lic` boundary fix applied entirely in `apps_lic/` — 20/20 W1 boundary tests pass. W2N–W6N are deferred pending explicit authorization. Receipts: `artifacts/chromadb_graphrag_remediation/no_core_rebaseline_receipt.json`, `w1n_receipt.json`.
>
> **Hardening patch (2026-05-11 rev-2)**: Five additional hardening items applied: (H1) semantic cache YAML key normalized to `semantic_cache` only — `r1b_semantic_cache` removed to prevent declared-but-unwired divergence; (H2) graph profile YAML key normalized to `graph_traverse.graph_expansion_allowed` — `graph_traverse.allowed` removed; (H3) `RouteContract` GENERIC_INFRA_EDIT upgraded from two loose fields to a single `graph_traverse_policy: GraphTraversePolicy | None = None` object carrying all 11 policy fields; (H4) W0 reclassified from DONE to TODO — hardening-pass evidence gathered but implementation preflight receipt not yet emitted; (H5) DoD-10 added — C0.3 adapter selection must be registry/config-driven, not hardcoded by `app_id`.

---

## Context (SCQA)

- **Situation** — The `agentic_core` substrate is fully implemented: `SovereignChromaClient`, `SovereignSemanticCache`, `check_d2_semantic_cache()` in `route_gates.py`, and `run_graph_traverse()` / `GraphTraverseInput` in `c0_3_enhanced/` all exist with zero callers. `apps_research` has a fully-declared R1B cache profile (`cache_profile.company_brief.v1.yaml`, threshold 0.85) that is never wired to the actual lookup. `apps_rg` R1B was quarantined for a correct L4-import violation; no replacement exists. `apps_lic` calls `SovereignChromaClient` directly from `apps_lic/types/` — a P0 boundary violation ported from legacy archives. No app anywhere constructs a `GraphTraverseInput`.

- **Complication** — Three categories of gap exist simultaneously: (1) a P0 boundary violation (`apps_lic/types/lic_vector_memory_types.py` line 11 imports L4 directly from the types layer), (2) two unwired R1B semantic caches (`apps_rg` quarantined, `apps_research` config-only) — and critically `package_driven_l0_binding`'s R1B arm reads `semantic_cache.enabled` and emits a `RouteContract(route_type=CACHE_LOOKUP)` but **never calls `check_d2_semantic_cache()`** — so the lookup always misses, and (3) three apps with no C0.3 Graph RAG despite fully-implemented substrate. Additionally `apps_research/engines/research_retrieval_engine.py` uses `_mock_embed()` (SHA-256/10-dim) in production path and ignores `chromadb_path`. Finally, `apps_research/config/domain_contract/cache_profile.company_brief.v1.yaml` declares `text-embedding-3-large` (3072-dim) which is **incompatible** with the runtime `BAAI/bge-m3` (1024-dim) singleton — this **blocks** ingestion if not resolved before W5.

- **Question** — How do we close the P0 boundary violation, wire live R1B semantic cache for `apps_rg` and `apps_research`, enable C0.3 Graph RAG for all three apps, and resolve the embedding model conflict — with minimal blast radius and zero app-specific `agentic_core` edits?

- **Answer** — Create sanctioned integration shims for each app, add `route_evaluation_order` + `graph_traverse` blocks to app-owned route profiles, call the existing `check_d2_semantic_cache()` from the generic L0 binding, build per-app C0.3 adapters, and retire the `InMemoryResearchStore` mock-embedding path — using exactly two `GENERIC_INFRA_EDIT` changes to `agentic_core`.

---

## Evidence Sources

| Source | Why needed | Status |
|---|---|---|
| `apps_lic/types/lic_vector_memory_types.py:11` | P0 violation — direct `SovereignChromaClient` import from types layer | ✅ Confirmed |
| `apps_rg/cache/r1b_adapter.py:12` | Quarantined; `RuntimeError` on import | ✅ Confirmed |
| `agentic_core/L0_routing/package_driven_l0_binding.py` R1B arm | Reads `semantic_cache.enabled` from profile; emits `RouteContract(route_type=CACHE_LOOKUP)`; **never calls `check_d2_semantic_cache()`** — always misses | ✅ Confirmed |
| `apps_research/config/domain_contract/cache_profile.company_brief.v1.yaml` | R1B `enabled: true`, threshold 0.85, namespace declared; `embedding_model: text-embedding-3-large` (3072-dim) — **incompatible with runtime BGE-M3 1024-dim** | ✅ Confirmed |
| `agentic_core/L0_routing/reasoning/route_gates.check_d2_semantic_cache()` | Canonical R1B entry point — exists at line 217; no callers yet | ✅ Confirmed |
| `agentic_core/L0_routing/c0_retrieval/c0_3_enhanced/pipeline.run_graph_traverse()` | Fully implemented; `GraphTraverseInput` in `contracts.py`; never called from any app | ✅ Confirmed |
| `apps_lic/config/domain_contract/route_profiles.yaml` | No `route_evaluation_order`; no `graph_traverse` block | ✅ Confirmed |
| `apps_rg/config/domain_contract/route_profiles.yaml` | No `route_evaluation_order`; no `graph_traverse` block | ✅ Confirmed |
| `apps_research/config/domain_contract/route_profile.company_brief.v1.yaml` | Has full `route_evaluation_order` — the only app with this shape today | ✅ Confirmed |
| `agentic_core/L0_routing/c0_retrieval/route_contract.RouteContract` | Has `max_hops` (default 1); **does not** have `graph_expansion_allowed` or `allowed_relation_types` yet | ✅ Confirmed |
| `apps_research/engines/research_retrieval_engine.py` | `_mock_embed()` SHA-256/10-dim in production; `create_retrieval_engine()` always returns `InMemoryResearchStore` regardless of `chromadb_path` | ✅ Confirmed |
| All `apps_*/` trees | No `GraphTraverseInput` construction anywhere in any app — confirmed by grep across 15 files | ✅ Confirmed |

---

## Wave Structure

| Wave | Scope | Focus | Est. Tokens | Status |
|------|-------|-------|------------|--------|
| W0 | Pre-flight | Implementation preflight: re-verify live config keys, binding read paths, policy carrier capacity; emit W0 receipt; no code edits | ~800 | ✅ DONE |
| W1 | `apps_lic` | P0 boundary fix: remove direct L4 import from types; integration shim | ~1,500 | ✅ DONE (see W1N) |
| W2 | All apps (generic) | GENERIC_INFRA_EDIT: wire `check_d2_semantic_cache()` in L0 binding R1B arm; add `route_evaluation_order` to apps_lic + apps_rg profiles | ~2,500 | ⏸ REVERTED — no-core constraint; app config preserved; `agentic_core` edits rolled back |
| W3 | All apps (generic) | GENERIC_INFRA_EDIT: add `graph_traverse_policy: GraphTraversePolicy | None = None` to `RouteContract`; read `graph_traverse` block from route profiles in L0 binding; add `graph_traverse` blocks to all three app profiles | ~3,000 | ⏸ REVERTED — no-core constraint; deferred to W3N |
| W4 | Per-app | Three C0.3 graph adapters (`build_*_graph_traverse_input()`); no `run_graph_traverse()` calls inside adapters | ~3,000 | ⏸ STOPPED — not started; deferred to W4N |
| W5 | `apps_research` + ingestion | Fix embedding model conflict (YAML edit); `ChromaResearchStore` (new); gate factory; ingestion scripts | ~3,500 | 🔲 TODO — deferred to W5N |
| W6 | Tests + receipts | Full test suite; negative controls; all receipts emitted | ~3,000 | 🔲 TODO — deferred to W6N |

### No-Core Rebaseline Wave Map (W*N track)

> ⛔ **No-core constraint**: zero `agentic_core/` file touches permitted on the W*N track. All GENERIC_INFRA_EDITs are deferred until the no-core constraint is explicitly lifted.

| Wave | Scope | Focus | No-Core Constraint | Status |
|------|-------|-------|--------------------|--------|
| W0N | Pre-flight | Same as W0 — receipt verified | N/A (no code) | ✅ DONE (W0 receipt reused) |
| W1N | `apps_lic` boundary fix | Remove direct `SovereignChromaClient` import from `lic_vector_memory_types.py`; route via `chroma_delegate.get_sovereign_chroma_client()` | `apps_lic/` only — zero `agentic_core/` touches | ✅ DONE — 20/20 W1 boundary tests pass |
| W2N | App config only | Normalize `semantic_cache` blocks in `apps_lic` + `apps_rg` cache profiles; `live_wiring_deferred=true`; `apps_lic` disabled (`personalized_outreach_not_cacheable`); `apps_rg` prepared (`resume_gen.v1`, threshold 0.88); `apps_research` embedding conflict noted and deferred; **no `package_driven_l0_binding.py` edit** | App-owned YAML only | ✅ DONE — 9/9 tests pass |
| W3N | App config only | Normalize `graph_traverse` blocks in all three app route profiles; canonical relation types, node/edge limits, `contradiction_scan_enabled`, `live_wiring_deferred=true`; **no `route_contract.py` edit, no `package_driven_l0_binding.py` edit** | App-owned YAML only | ✅ DONE — 12/12 tests pass |
| W4N | Per-app adapters | Three C0.3 graph adapter stubs (`c0_graph_adapter.py`); protocol-only, no `run_graph_traverse()` calls | App-owned `integrations/` only | ✅ DONE — 17/17 W4N tests pass; 38/38 combined W2N+W3N+W4N pass |
| W5N | `apps_research` + ingestion | Embedding conflict YAML fix; `ChromaResearchStore`; ingestion scripts | App-owned only (`apps_research/engines/`, `tools/ingestion/`) | ✅ DONE — 16/16 W5N tests pass; 54/54 combined W2N+W3N+W4N+W5N pass |
| W6N | Tests + receipts | Full test suite under no-core constraint; all receipts | Tests only | ✅ DONE — 74/74 pass; all receipts + evidence bundle + gap register emitted |

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| W0.P1 | Implementation preflight | 13 source files + live key re-verification; emit W0 preflight receipt | Re-verify 8 live-repo questions before any code edit; emit `artifacts/chromadb_graphrag_remediation/w0_preflight_receipt.json` | ~800 | ✅ DONE |
| W1.P1 | `apps_lic` boundary fix | `lic_vector_memory_types.py`, new `apps_lic/integrations/chroma_delegate.py` | 76 telemetry emit calls in the file make it large; delegate routing preserves public API | ~1,500 | ✅ DONE (W1N — 20/20 tests pass) |
| W2.P1 | Generic R1B wiring | `package_driven_l0_binding.py` (GENERIC_INFRA_EDIT), `apps_lic/route_profiles.yaml`, `apps_rg/route_profiles.yaml` | Zero app_id checks permitted; namespace + threshold read from app-owned cache profile | ~2,500 | ⏸ REVERTED — `agentic_core` edit rolled back; app config YAMLs preserved; live wiring deferred |
| W3.P1 | RouteContract graph policy object + profile plumbing | `route_contract.py` (GENERIC_INFRA_EDIT), `package_driven_l0_binding.py` (same GENERIC_INFRA_EDIT), all 3 route profiles | `GraphTraversePolicy` dataclass carries all 11 policy fields; `RouteContract.graph_traverse_policy` optional with `None` default; all existing callers unaffected | ~3,000 | ⏸ REVERTED — `agentic_core` edits rolled back; deferred to W3N (app config only) |
| W4.P1 | `apps_lic` C0.3 adapter | new `apps_lic/integrations/c0_graph_adapter.py` | contact/company/policy node types; `max_hops: 2`; contradiction on, supersession off | ~1,000 | ⏸ STOPPED — not started; deferred to W4N |
| W4.P2 | `apps_rg` C0.3 adapter | new `apps_rg/integrations/c0_graph_adapter.py` | JD→skill, résumé provenance; `max_hops: 1` (bounded scope) | ~1,000 | ⏸ STOPPED — not started; deferred to W4N |
| W4.P3 | `apps_research` C0.3 adapter | new `apps_research/integrations/c0_graph_adapter.py` | citation lineage + contradiction + supersession; `max_hops: 2` | ~1,000 | ⏸ STOPPED — not started; deferred to W4N |
| W5.P0 | **Embedding model conflict fix** | `cache_profile.company_brief.v1.yaml` | **MUST precede W5.P1–P3** — change `text-embedding-3-large`/3072-dim → `BAAI/bge-m3`/1024-dim | ~200 | 🔲 TODO |
| W5.P1 | `ChromaResearchStore` | new `apps_research/engines/integration/chroma_research_store.py`, edit `research_retrieval_engine.py` | Remove `_mock_embed` from production path; gate by `chromadb_path is not None` | ~2,000 | 🔲 TODO |
| W5.P2 | `lic_intelligence` ingestion | new `tools/ingestion/ingest_lic_intelligence.py` | Source: `artifacts/apps_rg/runs/` company briefs + exec profiles + trigger signals | ~700 | 🔲 TODO |
| W5.P3 | `rg_docs` ingestion | new `tools/ingestion/ingest_rg_docs.py` | Source: `ops_scripts/apps_rg/jd_*.json` + `*_resume*.json` + `ResumeChunk` outputs | ~700 | 🔲 TODO |
| W5.P4 | `process_docs` ingestion | new `tools/ingestion/ingest_research_artifacts.py` + run existing `ingest_process_docs.py` | Adds research artifacts to existing collection | ~400 | 🔲 TODO |
| W6.P1 | Tests — boundary + R1B | `test_lic_chroma_remediation.py`, `test_rg_r1b_and_graph.py`, `test_research_store_and_graph.py` | Cover positive + negative (miss fallthrough, quarantine untouched, ACL block) | ~1,500 | 🔲 TODO |
| W6.P2 | Tests — C0.3 + receipts | C0.3 adapter tests + negative controls | 9 negative-control tests required; includes `test_c03_adapter_registry_driven` | ~1,500 | 🔲 TODO |

---

## Files In Scope

### New Files
| File | Label | Wave | Purpose |
|------|-------|------|---------|
| `apps_lic/integrations/chroma_delegate.py` | NEW — app-owned | W1 | Sole `SovereignChromaClient` import site for apps_lic |
| `apps_lic/integrations/c0_graph_adapter.py` | NEW — app-owned | W4 | Builds `GraphTraverseInput` for apps_lic C0.3 calls |
| `apps_rg/integrations/c0_graph_adapter.py` | NEW — app-owned | W4 | Builds `GraphTraverseInput` for apps_rg C0.3 calls |
| `apps_research/integrations/c0_graph_adapter.py` | NEW — app-owned | W4 | Builds `GraphTraverseInput` for apps_research C0.3 calls |
| `apps_research/engines/integration/chroma_research_store.py` | NEW — app-owned | W5 | `ChromaResearchStore` backed by `SovereignChromaClient` |
| `tests/_apps_contract/test_lic_chroma_remediation.py` | NEW — test | W6 | Boundary + factory + graph input validity (≥4 tests) |
| `tests/_apps_contract/test_rg_r1b_and_graph.py` | NEW — test | W6 | R1B gate-off, hit, no-L4, graph validity (≥5 tests) |
| `tests/_apps_contract/test_research_store_and_graph.py` | NEW — test | W6 | Store fallback, ChromaStore, R1B wired, graph validity (≥4 tests) |
| `tools/ingestion/ingest_lic_intelligence.py` | NEW — tool | W5 | BGE-M3 ingest: company briefs + exec profiles → `lic_intelligence` collection |
| `tools/ingestion/ingest_rg_docs.py` | NEW — tool | W5 | BGE-M3 ingest: JDs + résumé sections → `rg_docs` collection |
| `tools/ingestion/ingest_research_artifacts.py` | NEW — tool | W5 | BGE-M3 ingest: research run artifacts → `process_docs` collection |

### Edited Files
| File | Label | Wave | Change |
|------|-------|------|--------|
| `apps_lic/types/lic_vector_memory_types.py` | EDIT — app-owned types | W1N ✅ | Removed direct `SovereignChromaClient` import; routes via `chroma_delegate.get_sovereign_chroma_client()` |
| `apps_lic/config/domain_contract/route_profiles.yaml` | EDIT — app-owned config | W2+W3 | Add `route_evaluation_order` (R1B disabled); add `graph_traverse` block (`max_hops: 2`) |
| `apps_rg/config/domain_contract/route_profiles.yaml` | EDIT — app-owned config | W2+W3 | Add `route_evaluation_order` (R1B enabled, threshold 0.88); add `graph_traverse` block (`max_hops: 1`) |
| `apps_research/config/domain_contract/route_profile.company_brief.v1.yaml` | EDIT — app-owned config | W3 | Add `graph_traverse` block (`max_hops: 2`, contradiction on, supersession on) |
| `apps_research/config/domain_contract/cache_profile.company_brief.v1.yaml` | EDIT — app-owned config | W5.P0 | **MUST PRECEDE INGESTION**: change `embedding_model: text-embedding-3-large` → `BAAI/bge-m3`; `embedding_dimensions: 3072` → `1024` |
| `apps_research/engines/research_retrieval_engine.py` | EDIT — app-owned | W5 | Gate `ChromaResearchStore` vs `InMemoryResearchStore` on `chromadb_path is not None`; remove `_mock_embed` from production path |
| `agentic_core/L0_routing/package_driven_l0_binding.py` | EDIT — **GENERIC_INFRA_EDIT** | W2+W3 ⏸ REVERTED | W2: call `check_d2_semantic_cache()` in R1B arm. W3: read `graph_traverse` block → populate `RouteContract`. Rolled back under no-core constraint; backup at `artifacts/chromadb_graphrag_remediation/agentic_core_rollback_backup.patch`. |
| `agentic_core/L0_routing/c0_retrieval/route_contract.py` | EDIT — **GENERIC_INFRA_EDIT** | W3 ⏸ REVERTED | Add `GraphTraversePolicy` dataclass + `RouteContract.graph_traverse_policy`. Rolled back under no-core constraint. |

### Do-Not-Touch
| File | Reason |
|------|--------|
| `apps_rg/cache/r1b_adapter.py` | Remains quarantined; R1B via generic binding only |
| `apps_rg/_quarantine/` | Must not be edited or unquarantined without explicit authorization |
| All other `agentic_core/` files | Only the two labeled GENERIC_INFRA_EDITs are permitted; spine law §5 |

---

## Detailed Implementation Specs

### W1.P1 — `apps_lic` Boundary Fix

**Root cause**: `lic_vector_memory_types.py:11` — `from agentic_core.L4_state.utils.client.chroma_client import SovereignChromaClient` at module level in `apps_lic/types/`. This is a P0 boundary violation: `apps_lic/types/` is a data-contract layer; L4 imports belong in `apps_lic/integrations/`.

**New file** — `apps_lic/integrations/chroma_delegate.py`:
```python
# guardian: allow-l4-import -- sanctioned delegation shim; only file in apps_lic
#           permitted to import SovereignChromaClient directly
from agentic_core.L4_state.utils.client.chroma_client import SovereignChromaClient

def get_lic_chroma_client(persist_dir: str) -> SovereignChromaClient:
    return SovereignChromaClient(persist_dir=persist_dir)
```

**Edit** — `apps_lic/types/lic_vector_memory_types.py`:
- Remove `from agentic_core.L4_state.utils.client.chroma_client import SovereignChromaClient` (line 11)
- Add `from typing import Protocol` and `ChromaClientProtocol` (structural — `get_collection`, `delete_collection`)
- `LICVectorMemory.__init__` adds `chroma_factory: Callable[[str], ChromaClientProtocol] | None = None`
- `initialize()` calls `(self._chroma_factory or _default_factory)(self.persist_directory)` where `_default_factory` imports from `chroma_delegate` lazily

---

### W2.P1 — Generic R1B Semantic Cache Wiring (GENERIC_INFRA_EDIT)

**Root cause**: `package_driven_l0_binding.py` R1B arm checks `semantic_cache.enabled` from app cache profile and emits `RouteContract(route_type=CACHE_LOOKUP)` — but **never calls `check_d2_semantic_cache()`**. The lookup is silently skipped. This affects `apps_rg` and `apps_research` equally.

> **H1 — Key normalization**: All cache profile YAMLs use the single canonical key `semantic_cache`. Do NOT introduce `r1b_semantic_cache`. Reason: `package_driven_l0_binding.py` already reads `semantic_cache.enabled`; a second key would create a new declared-but-unwired path identical to the gap being fixed.

**Edit** — `agentic_core/L0_routing/package_driven_l0_binding.py` (GENERIC_INFRA_EDIT):
- In the `R1B_SEMANTIC_CACHE` arm of `l0_evaluate_routes_package_driven()`: when `requires_cache_hit=True`, call `check_d2_semantic_cache(query_text, namespace, threshold)` from `route_gates`
- `namespace` read from `cache_profile["semantic_cache"]["namespace"]` (app-owned)
- `threshold` read from `cache_profile["semantic_cache"]["similarity_threshold"]` (app-owned)
- On hit: call `emit_r1b_ret_terminal_packet()`; return `RETTerminalPacket` immediately (pipeline short-circuits; C0, PA, L2, L3 not called)
- On miss: continue to R3 as before
- Hit with `support_status=UNKNOWN` → treat as miss (fail closed)
- **Zero `app_id` checks. Zero per-app branches. Pure generic infrastructure.**

**R1B terminal short-circuit invariant**: `RETTerminalPacket` goes to Exit; Exit evaluates it. Never returned directly to user.

**Edit** — `apps_lic/config/domain_contract/route_profiles.yaml`:
```yaml
route_evaluation_order:
  - R5_PRE_ROUTE_FALLBACK
  - R1A_EXACT_CACHE
  - R1B_SEMANTIC_CACHE
semantic_cache:
  enabled: false
  reason: personalized_outreach_not_cacheable
```

**Edit** — `apps_rg/config/domain_contract/route_profiles.yaml`:
```yaml
route_evaluation_order:
  - R5_PRE_ROUTE_FALLBACK
  - R1A_EXACT_CACHE
  - R1B_SEMANTIC_CACHE
semantic_cache:
  enabled: true
  namespace: apps_rg.resume_gen.v1
  similarity_threshold: 0.88
  compatibility_check_fields:
    - role_compatible
    - freshness_within_ttl
    - provenance_known
```

---

### W3.P1 — RouteContract Graph Policy Object + Profile Plumbing (GENERIC_INFRA_EDIT)

> **H2 — Key normalization**: Route profile YAMLs use `graph_traverse.graph_expansion_allowed` (not `graph_traverse.allowed`). The binding reads `graph_traverse["graph_expansion_allowed"]`.

> **H3 — Full policy carrier**: `RouteContract` receives a single `graph_traverse_policy: GraphTraversePolicy | None = None` field rather than two loose fields. C0.3 reads all bounds from this object; no graph policy field is implicit or drift-prone.

**New dataclass** — `agentic_core/L0_routing/c0_retrieval/route_contract.py` (GENERIC_INFRA_EDIT):
```python
@dataclass(frozen=True)
class GraphTraversePolicy:
    graph_expansion_allowed: bool = False
    max_hops: int = 1
    max_nodes: int = 64
    max_edges: int = 128
    allowed_relation_types: tuple[str, ...] = ()
    contradiction_scan_enabled: bool = False
    supersession_scan_enabled: bool = False
    graph_adapter_ref: str | None = None
    acl_scope_ref: str | None = None
    freshness_profile_ref: str | None = None
    support_target: str | None = None
```

**Edit** — `RouteContract` dataclass in same file:
- Add `graph_traverse_policy: GraphTraversePolicy | None = None`
- Remove any prior `graph_expansion_allowed` / `allowed_relation_types` loose fields if present
- `None` default ensures all existing callers continue to work unchanged

**Edit** — `agentic_core/L0_routing/package_driven_l0_binding.py` (same GENERIC_INFRA_EDIT, W3 addition):
- Read `graph_traverse` block from route profile when present
- Construct `GraphTraversePolicy` from the block fields when `graph_traverse.graph_expansion_allowed: true`
- Set `RouteContract(graph_traverse_policy=policy)` — no loose fields
- L0 must NOT call `run_graph_traverse()` — it only sets policy on `RouteContract`

> **H2 reminder**: All three route profile `graph_traverse` blocks use `graph_expansion_allowed` (not `allowed`). The binding reads `graph_traverse["graph_expansion_allowed"]`. `graph_adapter_ref`, `acl_scope_ref`, `freshness_profile_ref`, and `support_target` are optional; omit if app does not yet have these refs wired — `GraphTraversePolicy` defaults to `None` for those fields.

**Edit** — `apps_lic/config/domain_contract/route_profiles.yaml` (add to W2 edit):
```yaml
graph_traverse:
  graph_expansion_allowed: true
  max_hops: 2
  max_nodes: 64
  max_edges: 128
  allowed_relation_types:
    - GOVERNED_BY
    - OBSERVED_IN
    - CONTRADICTS
    - OWNED_BY
    - REQUIRES
  contradiction_scan_enabled: true
  supersession_scan_enabled: false
  graph_adapter_ref: apps_lic.integrations.c0_graph_adapter
```

**Edit** — `apps_rg/config/domain_contract/route_profiles.yaml` (add to W2 edit):
```yaml
graph_traverse:
  graph_expansion_allowed: true
  max_hops: 1
  max_nodes: 32
  max_edges: 64
  allowed_relation_types:
    - DERIVED_FROM
    - IMPLEMENTS
    - CONTRADICTS
    - SOURCE_VERSION
    - EVIDENCE
  contradiction_scan_enabled: true
  supersession_scan_enabled: false
  graph_adapter_ref: apps_rg.integrations.c0_graph_adapter
```

**Edit** — `apps_research/config/domain_contract/route_profile.company_brief.v1.yaml`:
```yaml
graph_traverse:
  graph_expansion_allowed: true
  max_hops: 2
  max_nodes: 64
  max_edges: 128
  allowed_relation_types:
    - SOURCE_AUTHORITY
    - SOURCE_VERSION
    - CONTRADICTS
    - SUPERSEDES
    - SUPERSEDED_BY
    - EVIDENCE
    - DERIVED_FROM
  contradiction_scan_enabled: true
  supersession_scan_enabled: true
  graph_adapter_ref: apps_research.integrations.c0_graph_adapter
```

---

### W4 — Per-App C0.3 Graph Adapters

> **H5 — DoD-10**: C0.3 adapter selection must be registry/config-driven. The `graph_adapter_ref` field in the `graph_traverse` profile block names the adapter module. The C0.3 pipeline resolves the adapter via an `ADAPTER_REGISTRY` dict keyed on `graph_adapter_ref` string — it must NOT branch on `app_id` inside `agentic_core`. W0 preflight must confirm whether C0.3 already has a config-driven adapter registry path before W4 implementation.

**Invariant for all three adapters**:
- Adapter builds `GraphTraverseInput` only — does NOT call `run_graph_traverse()` directly
- C0.3 pipeline owns the `run_graph_traverse()` invocation; resolves adapter via `GraphTraversePolicy.graph_adapter_ref` → registry lookup
- Adapter must not write L4, emit answer text, or route
- `GraphTraverseInput.__post_init__` must pass before returning

**`apps_lic/integrations/c0_graph_adapter.py`**:
- `build_lic_graph_traverse_input(route_contract, hydrated_candidates) -> GraphTraverseInput`
- Node types: `contact`, `company`, `policy`
- Relations: `GOVERNED_BY`, `OBSERVED_IN`, `CONTRADICTS`, `OWNED_BY`, `REQUIRES`
- `max_hops=2`, `max_nodes=64`, `max_edges=128`
- Contradiction on; supersession off

**`apps_rg/integrations/c0_graph_adapter.py`**:
- `build_rg_graph_traverse_input(route_contract, hydrated_candidates) -> GraphTraverseInput`
- Node types: `jd_requirement`, `skill`, `resume_section`, `source_version`
- Relations: `DERIVED_FROM`, `IMPLEMENTS`, `CONTRADICTS`, `SOURCE_VERSION`, `EVIDENCE`
- `max_hops=1`, `max_nodes=32`, `max_edges=64`
- Contradiction on; supersession off

**`apps_research/integrations/c0_graph_adapter.py`**:
- `build_research_graph_traverse_input(route_contract, hydrated_candidates) -> GraphTraverseInput`
- Node types: `citation`, `source`, `claim`, `company_fact`
- Relations: `SOURCE_AUTHORITY`, `SOURCE_VERSION`, `CONTRADICTS`, `SUPERSEDES`, `SUPERSEDED_BY`, `EVIDENCE`, `DERIVED_FROM`
- `max_hops=2`, `max_nodes=64`, `max_edges=128`
- Contradiction on; supersession on
- Anchors seeded from `hydrated_candidates` with `confidence >= 0.7`

---

### W5.P0 — Embedding Model Conflict Fix (MUST PRECEDE W5.P1–P4)

**Edit** — `apps_research/config/domain_contract/cache_profile.company_brief.v1.yaml`:
```yaml
# BEFORE:
embedding_model: text-embedding-3-large
embedding_dimensions: 3072

# AFTER:
embedding_model: BAAI/bge-m3
embedding_dimensions: 1024
```

**Why first**: 3072-dim query vectors cannot match 1024-dim stored vectors; all similarity scores would be wrong. Option A (BAAI/bge-m3) matches all existing ingestion tooling, `SovereignChromaClient`, and the three new ingestion scripts.

---

### W5.P1 — `ChromaResearchStore` + Factory Gate

**New file** — `apps_research/engines/integration/chroma_research_store.py`:
- `ChromaResearchStore` backed by `SovereignChromaClient` (only `SovereignChromaClient` import in `apps_research/`)
- Interface: `add_research`, `query_similar`, `get_by_mode`
- Collection: `process_docs` (matching spine manifest)
- Embed: `BAAI/bge-m3` via `bge_runtime.py` singleton

**Edit** — `apps_research/engines/research_retrieval_engine.py`:
- `create_retrieval_engine(chromadb_path=None)` → `ChromaResearchStore(chromadb_path)` when `chromadb_path is not None`, else `InMemoryResearchStore` (test/dev)
- Remove `_mock_embed` from production path; it may remain inside `InMemoryResearchStore` for test isolation only

---

### W5 — Ingestion Pipelines (Source Docs → ChromaDB Collections)

> This wave is **non-blocking** for W1–W4 (code wiring works with empty collections). Collections must be populated before semantic cache can produce live hits in production.

| Component | Path | Notes |
|-----------|------|-------|
| ChromaDB persist root | `data/cache/chromadb/` | Via `canonical_persist_dir()` in `agentic_core/L4_state/config/chroma_paths.py` |
| BGE model | `BAAI/bge-m3` | 1024-dim, L2-normalized, cosine; singleton in `agentic_core/embeddings/bge_runtime.py` |
| Existing ingestion template | `tools/generate/ingestion/ingest_process_docs.py` | BAAI/bge-m3, cosine, `process_docs` collection — canonical template |

**`tools/ingestion/ingest_lic_intelligence.py`** — Collection: `lic_intelligence`; sources: `artifacts/apps_rg/runs/` company briefs + exec profiles; metadata: `company_id`, `executive_name`, `source_type`, `content_hash`; dedup by `content_hash`.

**`tools/ingestion/ingest_rg_docs.py`** — Collection: `rg_docs`; sources: `ops_scripts/apps_rg/jd_*.json` + `*_resume*.json` + `ResumeChunk` outputs; metadata: `company`, `role`, `level`, `section_type`, `content_hash`; dedup by `content_hash`.

**`tools/ingestion/ingest_research_artifacts.py`** — Collection: `process_docs` (adds to existing); sources: `artifacts/apps_rg/runs/*/company_research_*.json`; metadata: `company`, `run_id`, `task_class`, `section_type`, `source_type=research_artifact`; dedup by `content_hash`.

---

## W0 — Implementation Preflight Checklist

> **W0 status: ✅ DONE.** W0 preflight receipt emitted at `artifacts/chromadb_graphrag_remediation/w0_preflight_receipt.json`.

| # | Preflight Question | Why it matters |
|---|-------------------|----------------|
| PF-1 | What are the exact `semantic_cache` key names in all three live cache profiles? | Confirms `package_driven_l0_binding` reads the right key; catches any drift from `r1b_semantic_cache` |
| PF-2 | What are the exact `graph_traverse` key names in all three live route profiles? | Confirms binding reads `graph_expansion_allowed` (not `allowed`); catches key drift |
| PF-3 | Does `package_driven_l0_binding` currently read `semantic_cache` or `r1b_semantic_cache`? | Pin the exact live read path before the W2 GENERIC_INFRA_EDIT |
| PF-4 | Are any `graph_traverse` profile fields currently consumed by any binding? | Confirms W3 is net-new (no partial wiring that could conflict) |
| PF-5 | Can `RouteContract` carry a nested frozen `GraphTraversePolicy` dataclass without import cycles? | Confirms W3 dataclass shape is safe |
| PF-6 | Does C0.3 already have a config-driven adapter registry path, or must W4 introduce one? | Determines whether W4 must add the registry or merely register a new entry |
| PF-7 | Does `check_d2_semantic_cache()` return sufficient fields to populate all required `RETTerminalPacket` fields? | Guards against silent truncation on hit |
| PF-8 | Does `run_graph_traverse()` return sufficient fields to populate all required `FinalEvidenceContract` fields? | Guards against silent truncation on graph expand |
| PF-14 | **`apps_lic` semantic cache hard-bypass proof** — see detailed checklist below | Verifies `apps_lic` cannot execute R1B semantic cache lookup under any code path |

### PF-14 — apps_lic Semantic Cache Hard-Bypass (detailed)

Answer all 8 sub-questions explicitly before marking PASS. If any sub-question cannot be confirmed PASS, mark `BLOCKED_APPS_LIC_SEMANTIC_CACHE_NOT_BYPASSED`.

| Sub-question | Required answer | Notes |
|---|---|---|
| PF-14a | Is `apps_lic` present in any cache profile with `semantic_cache.enabled: true`? | Must be `false` (PASS) or absent |
| PF-14b | Is `apps_lic` present in any `route_evaluation_order` that includes `R1B_SEMANTIC_CACHE`? | If yes → must confirm PF-14c (WARN); if no → stronger guarantee |
| PF-14c | If `R1B_SEMANTIC_CACHE` appears in `apps_lic` `route_evaluation_order`, does `semantic_cache.enabled: false` force a hard bypass **before** `check_d2_semantic_cache()` is called? | Must be confirmed by static binding logic; convention-only is not sufficient |
| PF-14d | Does `package_driven_l0_binding` skip `check_d2_semantic_cache()` when `semantic_cache.enabled` is `false`? | Must be confirmed (PASS) |
| PF-14e | Can `apps_lic` ever emit `RETTerminalPacket` with `ret_type=SEMANTIC_CACHE_HIT`? | Must be impossible (PASS = `false`) |
| PF-14f | Can `apps_lic` still use ChromaDB for C0 evidence retrieval? | Must be `true` — bypass is semantic-cache-only, not all-Chroma |
| PF-14g | Can `apps_lic` still use C0.3 Graph RAG? | Must be `true` — same distinction |
| PF-14h | Does the bypass depend only on convention, or is it enforced by runtime binding logic? | Must be runtime-enforced; convention-only → BLOCKED |

**Blocker rules** — mark `BLOCKED_APPS_LIC_SEMANTIC_CACHE_NOT_BYPASSED` if ANY of:
- `apps_lic` cache profile has `semantic_cache.enabled: true`
- `apps_lic` code path can call `check_d2_semantic_cache()`
- `apps_lic` can emit `RETTerminalPacket` with `ret_type=SEMANTIC_CACHE_HIT`
- The bypass depends only on convention rather than enforced binding logic

**Warn rule** — emit `WARN_APPS_LIC_R1B_IN_ORDER` if:
- `apps_lic` `route_evaluation_order` includes `R1B_SEMANTIC_CACHE` even though `semantic_cache.enabled: false` correctly bypasses the lookup
- Recommendation in that case: **remove `R1B_SEMANTIC_CACHE` from `apps_lic` `route_evaluation_order`** unless the binding requires it for explicit disabled-route auditing

**Preferred `apps_lic` route profile shape**:
```yaml
route_evaluation_order:
  - R5_PRE_ROUTE_FALLBACK
  - R1A_EXACT_CACHE
  - R3_SIMPLE_GROUNDED_READ

semantic_cache:
  enabled: false
  reason: personalized_outreach_not_cacheable
```

**Required finding field in `w0_preflight_receipt.json`**:
```json
"apps_lic_semantic_cache_bypass": {
  "semantic_cache_enabled": false,
  "r1b_route_present": true,
  "check_d2_semantic_cache_called": false,
  "semantic_cache_ret_packet_possible": false,
  "c0_chroma_evidence_allowed": true,
  "c03_graph_rag_allowed": true,
  "bypass_reason": "personalized_outreach_not_cacheable",
  "status": "PASS"
}
```

> **Important distinction**: `apps_lic` must bypass semantic cache. `apps_lic` may still use ChromaDB for C0 evidence retrieval. `apps_lic` may still use C0.3 Graph RAG. `apps_lic` must not use ChromaDB semantic cache for outreach or answer reuse.

---

## Gap Register

| # | App | Gap | Evidence | Fix Wave | Severity |
|---|-----|-----|----------|----------|---------|
| G1 | `apps_lic` | Direct `SovereignChromaClient` import from `apps_lic/types/` | `lic_vector_memory_types.py:11` CONFIRMED | W1 | **P0 (HIGH)** |
| G2 | `apps_lic` | No C0.3 `GraphTraverseInput`; no contact/company/policy lineage traversal | No `GraphTraverseInput` construction in `apps_lic/` CONFIRMED | W4 | P1 (MEDIUM) |
| G3 | `apps_lic` | Semantic cache disabled by policy — personalized outreach not safely reusable | Design decision — confirmed correct | W2 (explicit disable) | Policy-correct (LOW) |
| G4 | `apps_rg` | `r1b_adapter.py` quarantined; `package_driven_l0_binding` R1B arm **never calls `check_d2_semantic_cache()`** — always misses | `r1b_adapter.py:12` raises `RuntimeError`; `package_driven_l0_binding` confirmed | W2 | P1 (HIGH) |
| G5 | `apps_rg` | No C0.3 `GraphTraverseInput`; no JD→skills or résumé provenance traversal | No `GraphTraverseInput` in `apps_rg/` CONFIRMED | W4 | P1 (MEDIUM) |
| G6 | `apps_research` | `InMemoryResearchStore` uses SHA-256 mock embeddings; `chromadb_path` parameter ignored | `research_retrieval_engine.py::_mock_embed` CONFIRMED | W5 | P1 (HIGH) |
| G7 | `apps_research` | R1B profile declared `enabled: true` but `check_d2_semantic_cache()` never called — always misses | `package_driven_l0_binding` always-miss CONFIRMED | W2 (same generic fix as G4) | P1 (HIGH) |
| G8 | `apps_research` | No C0.3 `GraphTraverseInput`; no citation lineage or contradiction scan | No `GraphTraverseInput` in `apps_research/` CONFIRMED | W4 | P1 (MEDIUM) |
| G9 | `apps_research` | Embedding model conflict: cache profile declares `text-embedding-3-large`/3072-dim; runtime uses `BAAI/bge-m3`/1024-dim — **blocks ingestion** | `cache_profile.company_brief.v1.yaml` CONFIRMED | W5.P0 | **P0 (HIGH — blocks ingestion)** |
| G10 | `apps_lic`, `apps_rg` | Route profiles missing `route_evaluation_order` and `graph_traverse` blocks required by `package_driven_l0_binding` | `apps_lic/route_profiles.yaml`, `apps_rg/route_profiles.yaml` CONFIRMED | W2+W3 | P0 (HIGH — blocks W2 generic wiring) |
| G11 | All apps | C0.3 adapter selection path unknown — may be hardcoded by `app_id` inside `agentic_core` or may not exist at all | Requires W0 preflight PF-6 to confirm | W4 (pre-condition) | MEDIUM (blocks DoD-10) |

---

## Non-Goals

- Any `agentic_core` edit beyond the **two labeled GENERIC_INFRA_EDITs** (`package_driven_l0_binding.py` + `route_contract.py`). If PF-6 reveals no adapter registry exists, W4 may need a third GENERIC_INFRA_EDIT to add one — this requires an explicit Author-Gate before W4 starts.
- App-specific branches or `app_id` checks inside `agentic_core`
- Unquarantining `apps_rg/cache/r1b_adapter.py`
- Full C0 `GovernedAppRunner` migration for `apps_lic` (separate plan)
- Graph RAG for `apps_qna`, `apps_rfp`, `apps_underwriting_ai`, `apps_architect`, `apps_repo_brief`, `apps_eval` (separate plan)
- `apps_qna` flat-index migration to ChromaDB (separate plan)
- `apps_shared` changes
- OpenAI embedding support in core (Option B — rejected; Option A chosen)

---

## Hardened Implementation Rules

### Semantic Cache
- R1B hit → `RETTerminalPacket` → Exit. Pipeline does not call C0, PA, L2, L3.
- Hit with `support_status=UNKNOWN` → fail closed (treat as miss).
- `apps_lic` R1B must remain disabled — personalized outreach is not safely reusable.
- `apps_rg/cache/r1b_adapter.py` must remain quarantined.

### C0 Embeddings
- Every embedded evidence item must carry: `source_id`, `source_type`, `source_version`, `source_uri_or_ref`, `chunk_digest`, `acl_status`, `freshness_status`, `authority_class`, `contradiction_status`, `allowed_prompt_slot=C0_EVIDENCE_DATA_ONLY`.
- C0 must preserve blocked, excluded, contradicted, and weak evidence — never silently drop.

### Graph RAG
- Graph nodes must be typed (`AnchorType`). Graph edges must be typed (`GraphRelationType`).
- Expansion bounded by: `max_hops`, `max_nodes`, `max_edges`, `allowed_relation_types`, ACL, freshness, support target.
- Contradictions and supersession explicit in `FinalEvidenceContract` — never hidden.
- Graph expansion failure → `WEAK_WITH_CAVEATS`, `CONFLICTED`, `EMPTY`, `BLOCKED`, or `UNKNOWN` — never fake `PASS`.
- `UNKNOWN` is never mapped to `PASS`. `NOT_APPLICABLE` requires a reason string.

---

## Definition of Done

| # | Criterion |
|---|-----------|
| DoD-1 | `apps_lic/types/lic_vector_memory_types.py` has zero `SovereignChromaClient` import at module level; `pyflakes` clean |
| DoD-2 | `package_driven_l0_binding` R1B arm calls `check_d2_semantic_cache()` and returns `RETTerminalPacket` on hit; `apps_rg` and `apps_research` both covered by generic path |
| DoD-3 | `create_retrieval_engine("/tmp/test")` returns `ChromaResearchStore`; `create_retrieval_engine(None)` returns `InMemoryResearchStore` |
| DoD-4 | All three `build_*_graph_traverse_input()` functions produce a `GraphTraverseInput` that passes `__post_init__` validation without raising |
| DoD-5 | `apps_research/config/domain_contract/cache_profile.company_brief.v1.yaml` has `embedding_model: BAAI/bge-m3` and `embedding_dimensions: 1024` |
| DoD-6 | `smoke_test`: `python -m apps_lic`, `python -m apps_rg --dry-run`, `python -m apps_research --dry-run` all exit 0 |
| DoD-7 | All new test files pass; zero regressions in `tests/_apps_contract/`; all 9 negative-control tests pass |
| DoD-8 | No new `SovereignChromaClient` imports in any `apps_*/types/` module |
| DoD-9 | `package_driven_l0_binding.py` contains no `app_id ==` string (static check) |
| DoD-10 | C0.3 adapter selection is registry/config-driven via `GraphTraversePolicy.graph_adapter_ref` → `ADAPTER_REGISTRY` lookup; no `app_id ==` branch inside `agentic_core` for adapter dispatch |

---

## Core Boundary Invariant

| Concern | Resolution |
|---------|------------|
| `agentic_core` edits beyond two labeled GENERIC_INFRA_EDITs | FORBIDDEN — spine law §5 |
| `apps_lic/types/` direct L4 import | Fixed by moving import to `apps_lic/integrations/chroma_delegate.py`; `agentic_core` untouched |
| R1B always-miss in L0 binding | Fixed by GENERIC_INFRA_EDIT to `package_driven_l0_binding.py`; reads namespace/threshold from app-owned cache profile; zero `app_id` checks |
| `RouteContract` graph policy fields | Fixed by GENERIC_INFRA_EDIT to `route_contract.py`; `GraphTraversePolicy` dataclass (11 fields) + single `graph_traverse_policy` field with `None` default |
| `InMemoryResearchStore` mock embed | Fixed entirely inside `apps_research/engines/`; `agentic_core` untouched |
| Embedding model conflict | Fixed by YAML edit to `apps_research/config/domain_contract/cache_profile.company_brief.v1.yaml`; `agentic_core` untouched |
| C0.3 invocation | Only C0.3 pipeline calls `run_graph_traverse()`; app adapters only build `GraphTraverseInput` |
| L0 graph traversal attempt | L0 maps profile config to `RouteContract` only; L0 MUST NOT call `run_graph_traverse()` |

---

## Verification-vs-Deferral

| Item | Verified in this plan | Deferred |
|------|----------------------|---------|
| P0 boundary violation closed | DoD-1 (pyflakes + test) | — |
| R1B live lookup (apps_rg) | DoD-2 (test gate-off + hit) | Real ChromaDB data population |
| R1B live lookup (apps_research) | DoD-2 (same generic path) | Real ChromaDB data population |
| ChromaResearchStore integration | DoD-3 (unit test) | Real BGE-M3 embedding at runtime |
| GraphTraverseInput validity | DoD-4 (dataclass __post_init__) | Real GraphAdapter wiring to ADG |
| Embedding model conflict closed | DoD-5 (profile audit test) | — |
| Zero regression | DoD-7 (full _apps_contract suite) | — |
| Negative controls | DoD-7 (9 tests required) | — |

---

## W6 — Required Tests (Full List)

### Boundary
- `test_no_types_layer_chroma_import` — no `apps_*/types` module imports `SovereignChromaClient`
- `test_chroma_delegate_only_import_site` — `apps_lic/integrations/chroma_delegate` is sole importer in apps_lic

### R1B
- `test_r1b_disabled_no_lookup` — when `enabled: false`, `check_d2_semantic_cache` never called
- `test_r1b_miss_continues_r3` — `check_d2_semantic_cache` returns `None` → route falls to R3
- `test_r1b_hit_emits_ret_packet` — hit returned → `RETTerminalPacket` returned from binding
- `test_r1b_hit_unknown_support_status_fails_closed` — hit with `support_status=UNKNOWN` → miss
- `test_r1b_hit_goes_to_exit_not_user` — `RETTerminalPacket` not unwrapped before Exit
- `test_no_app_id_branch_in_binding` — static check: `package_driven_l0_binding.py` contains no `app_id ==` string

### C0.3
- `test_l0_maps_graph_config_to_route_contract`
- `test_l0_does_not_call_run_graph_traverse` — L0 binding with `graph_expansion_allowed: true` in profile; mock `run_graph_traverse`; assert never called
- `test_c03_adapter_registry_driven` — C0.3 resolves adapter via `graph_adapter_ref` string → registry; no `app_id ==` branch present
- `test_c03_reads_route_contract_for_graph_input`
- `test_graph_traverse_input_validates` (all three apps)
- `test_adapter_does_not_call_run_graph_traverse` (all three apps)
- `test_acl_block_prevents_graph_expansion`
- `test_contradiction_represented_not_hidden`

### Negative Controls (required)
- `test_l0_direct_graph_traversal_attempt_fails`
- `test_c0_answer_attempt_fails`
- `test_types_direct_l4_import_fails`
- `test_semantic_cache_hit_without_compatibility_proof_fails`
- `test_graph_expansion_without_acl_proof_fails`
- `test_unknown_mapped_to_pass_fails`
- `test_not_applicable_without_reason_fails`
- `test_mock_embed_not_in_production_path`
- `test_cache_profile_embedding_model_1024`

### apps_lic Semantic Cache Bypass
- `test_apps_lic_semantic_cache_disabled_no_lookup` — `apps_lic` route profile has `semantic_cache.enabled: false`; binding must not call `check_d2_semantic_cache()` for `apps_lic` runs
- `test_apps_lic_semantic_cache_disabled_no_ret_hit` — `apps_lic` routing path must never produce `RETTerminalPacket` with `ret_type=SEMANTIC_CACHE_HIT`
- `test_apps_lic_can_still_use_c0_chroma_evidence` — `apps_lic` C0 evidence retrieval via `SovereignChromaClient` (through `chroma_delegate` shim) is unaffected by semantic cache bypass
- `test_apps_lic_can_still_use_c03_graph_rag` — `apps_lic` `build_lic_graph_traverse_input()` + `run_graph_traverse()` path is unaffected by semantic cache bypass
