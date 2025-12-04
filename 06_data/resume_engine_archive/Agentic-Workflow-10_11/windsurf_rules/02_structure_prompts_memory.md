# /windsurf_rules/02_structure_prompts_memory.md
## Import Graph, Prompt Schema, Memory & Context Rules (Condensed)

### 1. Import Graph Invariants
Forbidden:
- L1→L2
- L1→cognitive_agents
- L2→L3 internals
- L4→providers
- Providers→RAG/orchestration
- No upward-layer imports.
- No circular imports.

### 2. Prompt Schema Rules
- Declare placeholders explicitly.
- No unused or hallucinated macros.
- Validate substitution completeness.
- Prompts must be versioned, governed, and schema-bound.

### 3. Memory & Resource Requirements
- Bounded lists, caches, and stores.
- All caches must have eviction policies.
- No unbounded embeddings or histories.
- No orphaned async tasks.

### 4. Context Engineering Requirements
- Only relevant, safety-approved context may be injected.
- RAG results must be deterministic under same inputs.
- No infinite scroll accumulation; context must be curated.

### 5. Drafting & RAG Agent Boundaries
- Draft Planner = L1  
- Draft Executor = L2  
- Critic = L1  
- Fix Agent = L1  
- Integrated only through L3 DAG.
- High-signal rules apply (no fluff, persona alignment, metric injection).
