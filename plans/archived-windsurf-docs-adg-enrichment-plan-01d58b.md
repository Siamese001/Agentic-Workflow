---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\adg-enrichment-plan-01d58b.md'
original_relative_path: 'adg-enrichment-plan-01d58b.md'
source_sha256: 6a25d7232e4b2bb34e076a02e616d8dffb689b5bd9145b2833a6c292ba0c6ce4
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-03-12'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# ADG Enrichment Plan

Enrich the ADG builder/scanner to produce a richer catalog — more first-class node types, more precise edge/relation types, and closed gaps between what `schema.py` declares and what the scanner actually extracts — so that every subsequent ADG rebuild produces a more complete and queryable graph.

**ADG basis:** schema_version 4.0.0 — 76,809 nodes, 209,559 edges (Mar 12 2026)
**Scope:** Changes to `schema.py`, `static_scanner.py`, `builder.py`, and layer mapping only. No analyzer consumers, no violation detection, no CI wiring.

---

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## What the New ADG Data Reveals

Three categories of enrichment gap, all diagnosed directly from `adg_indexed_03122026.sqlite`:

### Gap A — Schema-declared entity types with zero nodes

The schema defines 21 entity types. Only **2 are materialized** (`module`, `symbol`). The scanner never creates first-class nodes for:

| Entity Type | What it represents | Current workaround |
|---|---|---|
| `layer` | L0–L6, L_APP, L_SL etc. as nodes | Layer is a string field only |
| `gateway` | `SovereignLLMGateway`, `UniversalWriteGateway` | Only referenced as symbols |
| `provider` | `openai`, `anthropic`, `httpx` | Only referenced as symbols |
| `datastore` | filesystem, DB, vector store endpoints | No nodes at all |
| `agent` | Agent classes (reasoning layer) | No nodes at all |
| `tool` | MCP tool call targets | No nodes at all |
| `side_effect_endpoint` | Write targets of `writes_to` edges | No nodes at all |
| `prompt_slot` | S0/D0/I0/C0/U0 prompt slots | No nodes at all |

**Impact:** Analyzers querying "what agents call this gateway?" cannot use node-level queries — they must infer from edge patterns. First-class nodes enable direct graph traversal.

### Gap B — Edge kinds in DB not mapped to `RelationType`

The scanner produces **rich edge kinds** but maps them all onto coarse `RelationType` values, losing specificity:

| DB `edge_kind` | Count | Current `relation_type` | Problem |
|---|---|---|---|
| `reads_env` | 769 | `reads_from` | Env reads and config reads merged |
| `reads_policy_state` | 990 | `reads_from` | Policy reads and env reads merged |
| `reads_secret` | 66 | `reads_from` | Security-sensitive reads invisible |
| `dynamic_exec` | 489 | `invokes_provider` | Dynamic `eval`/`exec` conflated with LLM calls |
| `composition` | 676 | `instantiates` | Composition (field ownership) conflated with any instantiation |
| `unresolved` | 1,783 | `implements` | Unresolved inheritance conflated with concrete implementations |
| `external` | 106 | `implements` | External base classes (e.g. `ABC`) conflated with in-repo implements |

**Impact:** Queries like "which modules read secrets?" or "which modules use dynamic exec?" require scanning all `reads_from` / `invokes_provider` edges and filtering by `edge_kind` — an extra join. Proper `RelationType` values make these direct.

### Gap C — Schema-declared relation types with zero edges (scanner never extracts them)

| Relation Type | What it should represent | Why zero |
|---|---|---|
| `belongs_to_layer` | Module → Layer node edge | Layer nodes don't exist (Gap A) |
| `in_cycle` | Modules in import cycles | Scanner detects cycles but emits nothing |
| `re_exports` | Module re-exporting another module's symbols | Not extracted |
| `invokes_tool` | Module calling a tool endpoint | `dynamic_exec` edges never classified as tool calls |
| `bypasses_uwg` | Write that bypasses UWG | Never extracted; only implied by absence of `writes_through` |
| `produces` / `consumes` | Data flow between modules | Not extracted |

### Gap D — L_UNKNOWN modules (layer mapping holes)

7 `agentic_core` subdirectories are unmapped in `LAYER_PREFIXES`:

| Path | Correct Layer |
|---|---|
| `agentic_core/_compat/` | `L_SHARED` (compatibility shims) |
| `agentic_core/embeddings/` | `L_SHARED` (shared embedding infrastructure) |
| `agentic_core/enforcement/` | `L_SHARED` (cross-layer enforcement contracts) |

These 7 modules currently carry `layer = L_UNKNOWN` — any layer-sensitive query over them returns wrong results.

### Gap E — All nodes have `confidence = 0.0`

Every node in the DB has `confidence = 0.0`. The schema supports confidence scoring but the builder never writes a non-zero value. A node derived from a concrete `import` statement should have higher confidence than one inferred from a string pattern match.

---

## Re-Engineered Scope: What This Plan Covers

| # | Enrichment | ADG layer touched | Phase |
|---|---|---|---|
| E1 | Materialize first-class nodes: `layer`, `gateway`, `provider`, `datastore` | `schema.py` + `builder.py` | P1 |
| E2 | Promote `reads_env`, `reads_policy_state`, `reads_secret` to distinct `RelationType` values | `schema.py` + `static_scanner.py` | P1 |
| E3 | Promote `dynamic_exec` to `invokes_dynamic` relation type; separate from `invokes_provider` | `schema.py` + `static_scanner.py` | P1 |
| E4 | Fix L_UNKNOWN: add 3 missing `LAYER_PREFIXES` entries | `schema.py` | P1 |
| E5 | Extract `belongs_to_layer` edges (Module → Layer node) | `static_scanner.py` + `builder.py` | P2 |
| E6 | Extract `in_cycle` edges for detected import cycles | `static_scanner.py` | P2 |
| E7 | Materialize `agent`, `tool`, `side_effect_endpoint` nodes from existing symbol evidence | `builder.py` | P2 |
| E8 | Promote `composition` to `composes` relation type; separate from `instantiates` | `schema.py` + `static_scanner.py` | P2 |
| E9 | Promote `unresolved` and `external` implements to distinct subtypes | `schema.py` + `static_scanner.py` | P2 |
| E10 | Write non-zero confidence scores based on evidence strength | `builder.py` | P3 |
| E11 | Extract `bypasses_uwg` edges explicitly (write with no `writes_through` path) | `static_scanner.py` | P3 |
| E12 | Materialize `prompt_slot` nodes from `GovernedPayload` field analysis | `static_scanner.py` + `builder.py` | P3 |

**Out of scope (this plan):** Analyzers that read the enriched graph, violation detection, CI gates, Hybrid ADG runtime edges.

---

## Phase 1 — Schema Corrections + Quick Wins

### E1: Materialize layer, gateway, provider, datastore nodes

**File: `agentic_core/adg/schema.py`** — no change needed (types already declared)

**File: `agentic_core/adg/artifact/builder.py`** (~60 LOC)

In `build_adg_artifact()` or equivalent post-scan assembly function, add a materialization pass:

```python
# Layer nodes — one per LAYER_PREFIXES value
for layer_label in set(LAYER_PREFIXES.values()):
    artifact.add_node(canonical_name("Layer", layer_label), entity_type="layer", layer=layer_label)

# Gateway nodes — from GATEWAY_ALLOWLIST
for gw_name, gw_path in GATEWAY_ALLOWLIST.items():
    artifact.add_node(canonical_name("Gateway", gw_name), entity_type="gateway", layer=module_path_to_layer(gw_path))

# Provider nodes — from PROVIDER_SDK_SYMBOLS
for sdk in PROVIDER_SDK_SYMBOLS:
    artifact.add_node(canonical_name("Provider", sdk), entity_type="provider", layer="L_EXTERNAL")

# Datastore/side_effect_endpoint nodes — from WRITE_SIDE_EFFECT_SYMBOLS
for sym in WRITE_SIDE_EFFECT_SYMBOLS:
    artifact.add_node(canonical_name("SideEffectEndpoint", sym), entity_type="side_effect_endpoint", layer="L_EXTERNAL")
```

**Expected node additions:** ~15 layer nodes, ~3 gateway nodes, ~10 provider nodes, ~15 side_effect_endpoint nodes.

---

### E2: Promote `reads_env`, `reads_policy_state`, `reads_secret` to distinct RelationTypes

**File: `agentic_core/adg/schema.py`** (~10 LOC)

Add to `RelationType`:
```python
"reads_env",           # module reads os.environ / os.getenv
"reads_secret",        # module reads secrets.token_* or secret store
"reads_policy_state",  # module reads policy hash / policy guard state
```

**File: `agentic_core/adg/extraction/static_scanner.py`** (~20 LOC)

The scanner already classifies these edge kinds (evidence: 769 `reads_env`, 990 `reads_policy_state`, 66 `reads_secret` edges in DB with correct `edge_kind`). The only change is to emit the matching `relation_type` instead of the coarse `reads_from`:

```python
_EDGE_KIND_TO_RELATION: dict[str, str] = {
    ...
    "reads_env":          "reads_env",
    "reads_secret":       "reads_secret",
    "reads_policy_state": "reads_policy_state",
}
```

**Impact:** 1,825 edges get more specific relation types. `reads_from` retains only true config/settings reads (previously 62,639 — bulk are correct, ~1,825 were miscategorized).

---

### E3: Promote `dynamic_exec` to `invokes_dynamic`

**File: `agentic_core/adg/schema.py`** (~5 LOC)

Add to `RelationType`:
```python
"invokes_dynamic",  # module uses eval/exec/__import__/importlib at runtime
```

**File: `agentic_core/adg/extraction/static_scanner.py`** (~5 LOC)

Change emission for `dynamic_exec` edge_kind: set `relation_type = "invokes_dynamic"` instead of `"invokes_provider"`.

**Impact:** 489 edges currently in `invokes_provider` (502 total) are `dynamic_exec` — these are `eval`/`exec`/`__import__` calls, **not** LLM provider calls. Separating them makes `invokes_provider` a clean LLM-only signal. `invokes_provider` count drops from 502 to ~13 genuine LLM calls.

> **Note:** This is a significant correction — the current `invokes_provider` count of 502 is highly inflated by dynamic exec conflation. After this fix, `invokes_provider` will more accurately represent actual LLM SDK calls.

---

### E4: Fix L_UNKNOWN layer mapping

**File: `agentic_core/adg/schema.py`** (~6 LOC)

Add to `LAYER_PREFIXES`:
```python
"agentic_core/_compat":    "L_SHARED",   # compatibility shims
"agentic_core/embeddings": "L_SHARED",   # shared embedding infrastructure
"agentic_core/enforcement":"L_SHARED",   # cross-layer enforcement contracts
```

**Impact:** 7 modules move from `L_UNKNOWN` to `L_SHARED`. All layer-sensitive queries over these modules now return correct results.

---

**Phase 1 totals:** ~4 files, ~100 LOC, ~1,840 edge reclassifications, ~43 new first-class nodes materialized, 7 L_UNKNOWN modules resolved.

---

## Phase 2 — Structural Graph Enrichment

### E5: Extract `belongs_to_layer` edges

Depends on E1 (layer nodes must exist before edges can point to them).

**File: `agentic_core/adg/extraction/static_scanner.py`** (~30 LOC)

After each module is scanned, emit:
```python
RelationRecord(
    from_name=module_adg_name,
    relation_type="belongs_to_layer",
    to_name=canonical_name("Layer", layer_label),
    edge_kind="layer_membership",
    ...
)
```

Add `"layer_membership"` to `EdgeKind` in `schema.py`.

**Impact:** ~5,902 new `belongs_to_layer` edges (one per repo module). Enables direct graph traversal: "give me all L0 modules" becomes a 1-hop edge query rather than a string-prefix filter on `adg_name`.

---

### E6: Extract `in_cycle` edges

The scanner already detects import cycles (evidence: `in_cycle` is in `RelationType` but has 0 edges — the detection exists but emission is missing).

**File: `agentic_core/adg/extraction/static_scanner.py`** (~40 LOC)

After the import graph is built, run a cycle detection pass (Tarjan's SCC or nx `simple_cycles`) and emit:
```python
# For each cycle member pair A → B where A imports B and B (transitively) imports A:
RelationRecord(from_name=A, relation_type="in_cycle", to_name=B, edge_kind="cycle", ...)
```

**Impact:** Import cycles are currently invisible in the graph. Cycle membership becomes queryable.

---

### E7: Materialize `agent` and `tool` nodes

**File: `agentic_core/adg/artifact/builder.py`** (~50 LOC)

Scan the existing symbol nodes for known agent/tool naming patterns and promote them:

```python
# Agent nodes: classes ending in "Agent" in apps_* or agentic_core/*/reasoning/
# Tool nodes: classes/functions matching MCP tool call patterns or *_tool.py modules
```

Patterns from existing ADG data:
- **Agent:** `ADG::Symbol::*Agent` where parent module is in `L_APP` or `L_SHARED`
- **Tool:** modules in `tools/` directory + classes registered in `mcp_tool_call` patterns

**Impact:** Promotes inferred symbols to typed nodes. Enables "find all agent nodes that invokes_provider without routes_through" — currently requires string matching on symbol names.

---

### E8: Promote `composition` to `composes` RelationType

**File: `agentic_core/adg/schema.py`** (~5 LOC)

Add to `RelationType`:
```python
"composes",  # class field holds an instance of another class (composition relationship)
```

**File: `agentic_core/adg/extraction/static_scanner.py`** (~5 LOC)

Change `composition` edge_kind emission: set `relation_type = "composes"` instead of `"instantiates"`.

**Impact:** 676 composition edges separated from 700 `instantiates` edges. Enables clean distinction between "class creates a temporary instance" vs "class owns an instance as a field".

---

### E9: Separate `unresolved` and `external` implements subtypes

**File: `agentic_core/adg/schema.py`** (~10 LOC)

Add to `RelationType`:
```python
"implements_external",  # inherits from an external (non-repo) base class (e.g. ABC, BaseModel)
"implements_unresolved", # inherits from a class that could not be resolved in the repo
```

**File: `agentic_core/adg/extraction/static_scanner.py`** (~10 LOC)

Change `unresolved` and `external` edge_kind emissions to use the new relation types.

**Impact:** 1,783 `unresolved` + 106 `external` edges separated from 1,889 real `implements` edges. `implements` becomes a clean "concrete in-repo inheritance" signal.

---

**Phase 2 totals:** ~3 files, ~140 LOC, ~5,902 new `belongs_to_layer` edges, cycle edges for all detected cycles, 2,565 edge reclassifications.

---

## Phase 3 — Advanced Extraction

### E10: Non-zero confidence scores

**File: `agentic_core/adg/artifact/builder.py`** (~40 LOC)

All 76,809 nodes currently have `confidence = 0.0`. Add evidence-based scoring:

| Evidence | Confidence |
|---|---|
| Module exists on disk, `__init__.py` present | 1.0 |
| Module exists on disk, no `__init__.py` | 0.9 |
| Symbol extracted from concrete AST `def`/`class` | 0.9 |
| Symbol inferred from import alias | 0.7 |
| Symbol from `external_module` (no source) | 0.5 |
| `unresolved_import` | 0.3 |
| Inferred from string pattern | 0.4 |

**Impact:** Confidence becomes a filterable dimension. Queries can exclude low-confidence nodes (e.g. `confidence < 0.5`) to get a cleaner subgraph.

---

### E11: Extract `bypasses_uwg` edges explicitly

Currently the UWG bypass gap is only detectable by the *absence* of a `writes_through` edge — there is no positive assertion in the graph that a module bypasses UWG.

**File: `agentic_core/adg/extraction/static_scanner.py`** (~50 LOC)

In the write-side-effect extraction pass, after emitting `writes_to` edges, check whether the same module also has a `writes_through` edge to `UWG_CANONICAL_SYMBOL`. If not, also emit:

```python
RelationRecord(
    from_name=module_adg_name,
    relation_type="bypasses_uwg",
    to_name=UWG_CANONICAL_SYMBOL,
    edge_kind="uwg_bypass",
    ...
)
```

**Impact:** `bypasses_uwg` becomes a direct, queryable edge. Currently requires a two-query join (all `writes_to` sources minus all `writes_through` sources). The bypass count of 1,172 modules becomes directly queryable with `SELECT COUNT(*) FROM edges WHERE relation_type='bypasses_uwg'`.

---

### E12: Materialize `prompt_slot` nodes

**File: `agentic_core/adg/extraction/static_scanner.py`** (~60 LOC)

Scan for `GovernedPayload` class definitions and field accesses matching `PROMPT_FIELD_TO_SLOT` (`s0_system`, `d0_injections`, `i0_instructional`, `c0_context`, `u0_user_prompt`). For each slot field found, emit a `prompt_slot` node and `generates_prompt` / `consumes_prompt` edges from the accessing module.

**Impact:** The 5 prompt slot types become queryable nodes. Currently `generates_prompt` has 215 edges but no slot granularity — you can't ask "which modules write to the S0 system slot?" without string-scanning symbol names.

---

**Phase 3 totals:** ~2 files, ~150 LOC, ~1,172 new `bypasses_uwg` edges, confidence on all 76k nodes, prompt slot nodes.

---

## File Change Summary

| File | Changes | Phase | LOC est. |
|---|---|---|---|
| `agentic_core/adg/schema.py` | Add `RelationType`: `reads_env`, `reads_secret`, `reads_policy_state`, `invokes_dynamic`, `composes`, `implements_external`, `implements_unresolved`; Add `EdgeKind`: `layer_membership`; Add `LAYER_PREFIXES` entries for `_compat`, `embeddings`, `enforcement` | P1+P2 | ~50 |
| `agentic_core/adg/extraction/static_scanner.py` | Remap `edge_kind → relation_type` for 5 edge kinds; add `belongs_to_layer` emission; add `in_cycle` pass; add `bypasses_uwg` emission; add prompt slot extraction | P1+P2+P3 | ~200 |
| `agentic_core/adg/artifact/builder.py` | Materialize layer/gateway/provider/side_effect_endpoint nodes; materialize agent/tool nodes from symbol patterns; add confidence scoring | P1+P2+P3 | ~150 |

**Total: ~400 LOC across 3 files.**

---

## Expected ADG After Rebuild

| Metric | Current | After enrichment |
|---|---|---|
| `L_UNKNOWN` modules | 7 | 0 |
| Entity types with nodes | 2 | ~9 |
| `invokes_provider` (LLM calls only) | 502 (inflated by dynamic_exec) | ~13 (clean) |
| `invokes_dynamic` | 0 | ~489 |
| `reads_env` edges | 0 (merged into reads_from) | ~769 |
| `reads_secret` edges | 0 (merged into reads_from) | ~66 |
| `reads_policy_state` edges | 0 (merged into reads_from) | ~990 |
| `belongs_to_layer` edges | 0 | ~5,902 |
| `bypasses_uwg` edges | 0 | ~1,172 |
| `composes` edges | 0 (merged into instantiates) | ~676 |
| `implements` (clean in-repo) | 1,889 (polluted) | ~0 resolved, ~1,783 properly typed |
| `confidence = 0.0` | 100% of nodes | 0% — all nodes have evidence-based score |
| First-class layer nodes | 0 | ~15 |
| First-class gateway nodes | 0 | ~3 |
| First-class provider nodes | 0 | ~10 |
| Prompt slot nodes | 0 | ~5 |

---

## Acceptance Criteria

### Phase 1 complete when (next ADG rebuild):
- `SELECT COUNT(*) FROM nodes WHERE entity_type='layer'` > 0
- `SELECT COUNT(*) FROM edges WHERE relation_type='reads_env'` = ~769
- `SELECT COUNT(*) FROM edges WHERE relation_type='invokes_dynamic'` = ~489
- `SELECT COUNT(*) FROM nodes WHERE layer='L_UNKNOWN'` = 0

### Phase 2 complete when:
- `SELECT COUNT(*) FROM edges WHERE relation_type='belongs_to_layer'` = ~5,902
- `SELECT COUNT(*) FROM edges WHERE relation_type='in_cycle'` > 0
- `SELECT COUNT(*) FROM edges WHERE relation_type='composes'` = ~676
- `SELECT COUNT(*) FROM edges WHERE relation_type='implements'` = clean in-repo count only

### Phase 3 complete when:
- `SELECT COUNT(*) FROM edges WHERE relation_type='bypasses_uwg'` = ~1,172
- `SELECT MIN(confidence) FROM nodes` > 0.0
- `SELECT COUNT(*) FROM nodes WHERE entity_type='prompt_slot'` = 5

---

## What This Unlocks for Future Analyzers

Once this plan is implemented and the ADG is rebuilt, the downstream analyzer layer gains:

| Current limitation | After enrichment |
|---|---|
| "Which modules bypass UWG?" requires two-query join | Direct: `WHERE relation_type='bypasses_uwg'` |
| "Which modules read secrets?" requires `edge_kind` filter | Direct: `WHERE relation_type='reads_secret'` |
| "Which LLM callers are ungoverned?" polluted by dynamic_exec | Clean: `invokes_provider` is LLM-only |
| "Are there import cycles?" — invisible | Direct: `WHERE relation_type='in_cycle'` |
| "What layer does module X belong to?" requires string parsing | Direct: 1-hop `belongs_to_layer` traversal |
| "Confidence filter" for high-signal subgraphs | `WHERE confidence >= 0.9` |

---

## Phase 4 — Analyzer-Enabling Enrichments

Querying the current ADG against each named analyzer reveals **6 additional data quality and structural gaps** that specifically block `layer_authority`, `prompt_governance`, `mutation_authority`, and `seam_enforcement` analyzers. These are distinct from Phase 1–3 enrichments — they fix data that is **present but wrong or unqueryable**.

### What the data shows per analyzer

| Analyzer | Blocking gap in current ADG |
|---|---|
| `layer_authority` | `violates` edges encode rule only as string `"L0->L5"` in `symbol` field — no structured `rule_id` column; cannot group violations by rule type without string parsing |
| `prompt_governance` | 49 `PromptSlot` nodes exist but have `entity_type=symbol` not `entity_type=prompt_slot` — type-based queries return 0; `invokes_provider` has 228 ungoverned callers but 97% of its 502 edges are not LLM calls (dynamic exec noise) |
| `mutation_authority` | `writes_to` contains false positives: `asyncio.run` (113), `copy.deepcopy` (61), `assert_no_persistent_write` (103) — these inflate the bypass count; `dead_imports` top entry is `__future__.annotations` (4,228 edges) — these are never "dead" (always used by type checker) |
| `seam_enforcement` | `routes_through` points to `symbol` nodes (`ADG::Symbol::SovereignLLMGateway`) not typed `gateway` nodes; 12 real seam modules in `L0_routing/seams/` have `entity_type=module` with no `is_seam` flag — seam_enforcement cannot identify seams without name-pattern matching |

---

### E13: Add `rule_id` column to edge table — enables `layer_authority` analyzer

**What's wrong:** `violates` edges store the rule as `symbol = "L0->L5"` (a string). There is no structured field. An analyzer grouping violations by rule type must do `WHERE symbol LIKE 'L0->%'` — fragile string parsing.

**File: `agentic_core/adg/artifact/builder.py`** + **`agentic_core/adg/extraction/graph_persister.py`** (~40 LOC)

Add `rule_id TEXT` column to the edges table schema. Populate it during `violates` edge emission:

```python
# When emitting a violates edge:
rule_id = f"LAYER_GRAVITY:{src_layer}->{dst_layer}"  # e.g. "LAYER_GRAVITY:L0->L5"
# Other rule_id namespaces for future use:
# "UWG_BYPASS:{module}"
# "SEAM_BYPASS:{module}"
# "PROMPT_UNGOVERNED:{module}"
```

Add `rule_id` to `EdgeKind` metadata in `schema.py`:
```python
# Structured rule_id prefixes (stored in edge.rule_id column)
RULE_ID_PREFIXES: dict[str, str] = {
    "LAYER_GRAVITY":    "Layer gravity violation (upward import)",
    "UWG_BYPASS":       "Write bypasses UniversalWriteGateway",
    "SEAM_BYPASS":      "Provider call bypasses architectural seam",
    "PROMPT_UNGOVERNED":"LLM invocation without governed prompt",
}
```

**Impact:** `layer_authority` analyzer can do `GROUP BY rule_id` to get exact violation counts per rule. All `violates` edges get structured rule IDs. Also usable by `seam_enforcement` and `mutation_authority` for their own violations.

---

### E14: Fix `PromptSlot` node `entity_type` — enables `prompt_governance` analyzer

**What's wrong:** 49 `PromptSlot` nodes (`ADG::PromptSlot::S0::...`, `ADG::PromptSlot::C0::...` etc.) are in the DB with `entity_type = "symbol"`. A query `WHERE entity_type = 'prompt_slot'` returns 0 rows.

**File: `agentic_core/adg/extraction/static_scanner.py`** or **`builder.py`** (~15 LOC)

When emitting a node with `adg_name` matching `ADG::PromptSlot::*`, set `entity_type = "prompt_slot"` not `"symbol"`.

**Impact:** `prompt_governance` analyzer can do `SELECT * FROM nodes WHERE entity_type='prompt_slot'` to enumerate all governed prompt slots. Currently unreachable by type. The 215 `generates_prompt` edges pointing to these nodes become properly typed graph entries.

---

### E15: Purge `writes_to` false positives — enables `mutation_authority` analyzer

**What's wrong:** The `WRITE_SIDE_EFFECT_SYMBOLS` set in `schema.py` is too broad. It captures symbols that are **not** persistent writes:

| False positive symbol | Count | Why it's wrong |
|---|---|---|
| `asyncio.run` | 113 | Event loop runner, no persistence |
| `copy.deepcopy` | 61 | In-memory copy, no persistence |
| `assert_no_persistent_write` | 103 | A test assertion *about* writes — not a write |
| `run` / `_run` / `_call` | 159 combined | Generic method names, not file/db writes |

These inflate the "1,172 module bypass gap" with modules that never actually write anything.

**File: `agentic_core/adg/schema.py`** (~15 LOC)

Remove from `WRITE_SIDE_EFFECT_SYMBOLS`:
```python
# Remove — not persistent writes:
"asyncio.run",      # not in current set but captured via suffix matching — add explicit exclusion
"copy.deepcopy",    # in-memory only
```

Add an explicit **exclusion list** checked during edge emission:
```python
WRITE_SIDE_EFFECT_EXCLUSIONS: frozenset[str] = frozenset({
    "asyncio.run",
    "copy.deepcopy",
    "assert_no_persistent_write",
    "deepcopy",
    "copy",
})
```

**File: `agentic_core/adg/extraction/static_scanner.py`** (~10 LOC)

Before emitting a `writes_to` edge, check `symbol not in WRITE_SIDE_EFFECT_EXCLUSIONS`.

**Impact:** `writes_to` false positive count drops by ~330+ edges. Bypass gap count becomes accurate. `mutation_authority` analyzer reports credible, not inflated, violations.

---

### E16: Exclude `__future__.annotations` from `dead_imports` — data quality fix

**What's wrong:** `from __future__ import annotations` is the top dead import target with **4,228 edges**. It is never "dead" — it is used at parse time by the type checker and intentionally not referenced at runtime. The ADG scanner incorrectly classifies it as dead.

**File: `agentic_core/adg/extraction/static_scanner.py`** (~5 LOC)

Add to the dead import exclusion set:
```python
_DEAD_IMPORT_EXCLUSIONS: frozenset[str] = frozenset({
    "__future__.annotations",   # always used by type checker
    "__future__.generator_stop",
    "__future__.unicode_literals",
    # ... other __future__ features
})
```

**Impact:** `dead_imports` drops from 6,274 to ~2,046 (removing the 4,228 `__future__.annotations` false positives). The remaining dead imports are genuine unused symbols — a clean signal for any dead-code analyzer.

---

### E17: Rename `influences` to `decorated_by` — semantic correctness

**What's wrong:** All 17,544 `influences` edges have `edge_kind = "decorator"`. The `symbol` values are `lru_cache`, `property`, `dataclass`, `contextmanager`, `functools.wraps` — these are **decorator applications**, not generic "influences". The word "influences" is ambiguous and misleads any analyzer reading the graph.

**File: `agentic_core/adg/schema.py`** (~5 LOC)

Add to `RelationType`:
```python
"decorated_by",  # module/class/function is decorated by the target symbol
```

Keep `influences` as a deprecated alias (do not remove — backward compat) but emit `decorated_by` for all new decorator edges.

**File: `agentic_core/adg/extraction/static_scanner.py`** (~5 LOC)

Change decorator edge emission: `relation_type = "decorated_by"` instead of `"influences"`.

**Impact:** 17,544 decorator edges become semantically precise. An analyzer can now ask "which enforcement modules use `@lru_cache`?" or "which classes are `@dataclass`?" without guessing what `influences` means. `influences` count → 0 (deprecated), `decorated_by` → 17,544.

---

### E18: Promote seam modules to `entity_type=seam` — enables `seam_enforcement` analyzer

**What's wrong:** The 12 real seam modules in `agentic_core/L0_routing/seams/` have `entity_type = "module"` — identical to every other module. `routes_through` edges point to `ADG::Symbol::SovereignLLMGateway` (a `symbol` node), not to a typed seam node. The `seam_enforcement` analyzer cannot identify seam modules without string-matching `adg_name LIKE '%/seams/%'`.

**File: `agentic_core/adg/schema.py`** (~5 LOC)

Add to `EntityType`:
```python
"seam",  # architectural seam module — routes calls through a gateway
```

Add seam path patterns:
```python
SEAM_MODULE_PATTERNS: tuple[str, ...] = (
    "agentic_core/L0_routing/seams/",
    "agentic_core/seams/",
)
```

**File: `agentic_core/adg/artifact/builder.py`** (~20 LOC)

During module node creation, check if the module path matches any `SEAM_MODULE_PATTERNS`. If yes, set `entity_type = "seam"` instead of `"module"`.

Also promote `SovereignLLMGateway` symbol node to a `gateway` node (ties back to E1) so `routes_through` edges connect `module → gateway` rather than `module → symbol`.

**Impact:** `SELECT * FROM nodes WHERE entity_type='seam'` returns exactly the 12 architectural seam modules. `seam_enforcement` analyzer can identify seam modules with a direct type query. `routes_through` edges connect to typed gateway nodes — the full seam routing path becomes graph-traversable.

---

### Phase 4 File Change Summary

| File | Changes | LOC est. |
|---|---|---|
| `agentic_core/adg/schema.py` | Add `rule_id` prefix constants; add `WRITE_SIDE_EFFECT_EXCLUSIONS`; add `SEAM_MODULE_PATTERNS`; add `EntityType`: `seam`; add `RelationType`: `decorated_by` | ~45 |
| `agentic_core/adg/extraction/static_scanner.py` | Exclude false-positive writes; exclude `__future__` dead imports; rename `influences` → `decorated_by`; set `entity_type=seam` for seam paths | ~35 |
| `agentic_core/adg/artifact/builder.py` | Fix `PromptSlot` entity_type; populate `rule_id` on `violates` edges; promote seam modules; point `routes_through` to gateway nodes | ~50 |
| `agentic_core/adg/extraction/graph_persister.py` | Add `rule_id TEXT` column to edges table DDL | ~10 |

**Phase 4 total: ~140 LOC across 4 files.**

### Phase 4 Acceptance Criteria

- `SELECT COUNT(*) FROM nodes WHERE entity_type='prompt_slot'` = 49 (not 0)
- `SELECT COUNT(*) FROM nodes WHERE entity_type='seam'` = 12
- `SELECT COUNT(*) FROM edges WHERE relation_type='decorated_by'` = ~17,544
- `SELECT COUNT(*) FROM edges WHERE relation_type='influences'` = 0
- `SELECT COUNT(*) FROM edges WHERE symbol='asyncio.run' AND relation_type='writes_to'` = 0
- `SELECT COUNT(*) FROM edges WHERE relation_type='dead_imports' AND dst_id IN (SELECT id FROM nodes WHERE adg_name LIKE '%__future__.annotations%')` = 0
- `SELECT COUNT(*) FROM edges WHERE relation_type='violates' AND (rule_id IS NULL OR rule_id = '')` = 0
- `routes_through` DST nodes have `entity_type='gateway'` not `entity_type='symbol'`

---

## Revised File Change Summary (All Phases)

| File | Phases | Total LOC est. |
|---|---|---|
| `agentic_core/adg/schema.py` | P1+P2+P4 | ~95 |
| `agentic_core/adg/extraction/static_scanner.py` | P1+P2+P3+P4 | ~235 |
| `agentic_core/adg/artifact/builder.py` | P1+P2+P3+P4 | ~200 |
| `agentic_core/adg/extraction/graph_persister.py` | P4 | ~10 |

**Grand total: ~540 LOC across 4 files.**

---

## Revised Expected ADG After Full Rebuild

| Metric | Current | After all phases |
|---|---|---|
| `L_UNKNOWN` modules | 7 | **0** |
| Entity types with nodes | 2 (`module`, `symbol`) | **~11** (+ `layer`, `gateway`, `provider`, `side_effect_endpoint`, `agent`, `tool`, `seam`, `prompt_slot`, `scan_run`) |
| `invokes_provider` | 502 (97% dynamic-exec noise) | **~13** (clean LLM-only) |
| `invokes_dynamic` | 0 | **~489** |
| `decorated_by` | 0 (`influences` was misleading) | **~17,544** |
| `influences` | 17,544 (misleading) | **0** (deprecated) |
| `reads_env` | 0 (merged into reads_from) | **~769** |
| `reads_secret` | 0 (merged into reads_from) | **~66** |
| `reads_policy_state` | 0 (merged into reads_from) | **~990** |
| `dead_imports` | 6,274 (4,228 are false positives) | **~2,046** (genuine only) |
| `writes_to` false positives | ~330 | **0** |
| `bypasses_uwg` | 0 | **~1,172** (accurate after false-positive cleanup) |
| `belongs_to_layer` | 0 | **~5,902** |
| `in_cycle` | 0 | **> 0** |
| `rule_id` on `violates` edges | empty | **all 224 populated** |
| `PromptSlot` node entity_type | `symbol` (wrong) | **`prompt_slot`** |
| Seam modules entity_type | `module` (generic) | **`seam`** |
| `confidence = 0.0` | 100% | **0%** |

## Rules

1. Follow all constitutional rules and guidelines
2. Maintain compliance with established standards
3. Document all changes and decisions
4. Validate all implementations before completion

---

## Success Criteria

- [ ] All objectives completed successfully
- [ ] Validation tests pass
- [ ] Documentation updated
- [ ] Stakeholder approval received

---

