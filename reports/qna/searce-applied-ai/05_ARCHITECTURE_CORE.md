# 05 Agentic Architecture Core


<!-- card-meta
card_id: 05_ARCHITECTURE_CORE
card_type: skill
priority: should
paste_order: 5
load_strategy: primary
-->

## LIVE VERBAL-FIRST OVERWRITE

These cards are optimized for live interview readout.

### Always-on output rules
- Use **short clauses** and a natural spoken cadence.
- Prefer **bullets** for architecture, governance, STAR, RCA, and technical answers.
- Limit live answers to **4 to 5 top-level bullets** unless Amit explicitly asks for depth.
- Use sub-bullets only when they make the answer easier to read under pressure.
- Use **bold** for words that should carry weight.
- Use *italics* for softer emphasis, contrast, or pacing.
- Do not over-format.
- Avoid forced summary endings such as polished "that is the difference between" lines.
- End on the practical implication or final control point.

### First-person credibility
Use lightly and naturally:
- "What I have seen in my agentic work..."
- "What I have learned building agentic workflows..."
- "My bias is to design the failure mode first..."

### Tight routing rule
- Architecture stays architecture-first.
- Governance stays risk/control-first.
- Do not drift into STAR, DGS, ROI, or 90-day plan unless asked.

### Inline citation discipline
- Every claim about Searce that came from research must carry a `[S#]` tag resolved in card 19 (Source Register).
- Personal experience (STAR, RCA) needs no citation.
- If you cannot cite a research claim, downgrade the framing to "my read is" or drop it.

### Preferred reliability-chain phrasing
When a reliability chain is useful, use these clusters instead of a long control inventory:
- **trusted data and semantic grounding**
- **validated execution and model lifecycle**
- **governed action and policy gates**
- **observability, audit, and regression evals**



## Purpose
Primary card for **Route 4 — Architecture concept**. When the question is "how would you build", this card drives the answer.


## Answer shape
1. Business workflow first.
2. Data and semantic layer.
3. Agent / orchestration layer.
4. Governance and eval layer.
5. Product and scale layer.

## Spine for an architecture answer

- Start with the **business decision** the system serves at Searce.
- Name the **trusted data contract** (semantic layer, governed catalog, lineage trace).
- Explain the **agent or orchestration layer** — what it plans, what it executes, what it does not touch.
- Name the **control point** (gate, eval, registry, approval checkpoint, audit log).
- Translate uncertainty honestly. Stop on the practical implication.

## Reliability chain (use as clusters, not full inventory)
- **trusted data and semantic grounding**
- **validated execution and model lifecycle**
- **governed action and policy gates**
- **observability, audit, and regression evals**

## Architecture content

### Six-layer agentic_core (L0..L6) with enforced gravity
- L0 routing → L1 cognition → L2 execution → L3 orchestration → L4 storage → L5 safety → L6 observability
- Dependency rules enforced at pre-commit; hard CI gate prevents reverse-gravity imports
- Mirrors Ram's 'Architectures Over Models' thesis: structure THEN models, not the inverse


### ADG (AST Dependency Graph) — Graph RAG applied to code
- SQLite canonical + Redis hot projection + MCP read-only gateway (source-of-truth hierarchy invariant)
- Materialized views: mv_graph_reverse_dependency_hotspots, mv_chokepoint_bridges, mv_critical_path_blast_radius, mv_hotspot_centrality
- Pre-built P-views: v_p0_apps_direct_infra, v_p0_write_bypass_uwg, v_p1_mis_layered_infra (architectural concern classification)
- Same mental model as Graph RAG: nodes + edges + multi-hop traversals for blast-radius, refactoring, and reachability queries


### 13+ MCP servers in production (Ram's zero-trust standard)
- adg_sqlite, memory, vector_db, otel_mcp, redis, GitKraken, notion, tavily, context7, deepwiki, pytest_mcp, task_manager, io.windsurf/mcp-playwright
- Each MCP: input validation, error contract, audit trail to JSONL ledger, fail-closed pre-execution gates
- MCP serialization rule (constitutional §25): one MCP call per response — derived from observed Anthropic SDK race
- Direct SQLite fallback supersedes grep when MCP unavailable (constitutional §28)


### Layered Memory Design — exactly Ram's architecture
- Short-term: in-session context (Cascade IDE working set, OTEL trace span buffer)
- Long-term episodic: EpisodicEvent entities (significant one-time events)
- Long-term semantic: ArchitecturalInvariant + ProjectContext (durable facts)
- Long-term procedural: ProceduralPattern (debugging recipes, fix playbooks)
- Eviction policy: mem_cleanup_stale at 30 days, with protected-type allowlist


### Multi-Agent A2A — apps_* engines as specialized agents
- 8+ apps_* engines: apps_rg, apps_research, apps_exec, apps_qna, apps_eval, apps_lic, apps_rfp, apps_underwriting_ai
- Shared L0 routing + UWG write gateway + L5 safety plane = production A2A protocol
- Each engine = specialized capability with typed contracts; coordination via L3 orchestration


### AI Gateway with FinOps — production multi-tier routing
- L0 NamespaceBandit (Thompson sampling) routes to namespace by EU score
- L2 Cascade tier: HIGH/MEDIUM/LOW/HITL — provider routing across deterministic/qwen/gemini_flash/gemini_pro/hitl
- Wilson CI + z + uplift + min-N gates on every promotion (L6/promo router)
- Brier-score calibration; ceiling-band enforcement; reroute caps to prevent runaway cost



## What this card does NOT do
- Does not turn into a STAR story unless asked.
- Does not collapse into governance — that is Route 5.
- Does not name vendor stack unless the question requires it.

## Cross-exam fallback
If the interviewer pushes deeper, hand off to **16_CROSS_EXAM.md** — name the artifact, gate, or metric and stop.
