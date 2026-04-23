---
trigger: always_on
---

> **Cascade always-on discipline:** Keep this file lean and invariant-focused. Put durable boundaries, routing cues, and non-negotiable standards here. Move long procedures, examples, templates, and execution playbooks into skills or workflows.
>
> **Cascade retrieval discipline:** When this rule affects research or synthesis, prefer local-first retrieval, exact or structural matches before broad semantic search, and evidence or quote extraction before final synthesis on high-risk tasks.
>
> **Cascade enforcement split:** Advisory guidance lives here, but deterministic blocking, fail-closed checks, and audit capture belong in hooks and scripts rather than prompt prose.

# Constitutional Floor

> ⛔ These constraints apply to every task, every tier, every session. No exceptions.

## Hard Constraints

### Tool Prefix Stability

Server IDs in `.windsurf/mcp_config.json` are stable. Live tool prefixes such as `mcp0_`, `mcp1_`, and `mcp2_` can shift whenever server order changes. In rule text, prefer stable server IDs plus bare tool names, then resolve the live prefix from the active tool list.

0. **No PowerShell.** Use `subprocess.run(argv, shell=False, timeout=30)`.
1. **No test skipping.** No `pytest.mark.skip`, no `xfail` without `strict=True`.
2. **No editing while exploring.** All five repair gates must pass before any edit.
3. **No agent deletion without authorization.** Requires AGENT-DELETION-AUTHORIZED marker, 90-day deprecation, zero references.
4. **CI enforces all of this.** `python ops_scripts/ci/run_contract_gates.py`
5. **ADG before T2/T3 work.** Ingest `artifacts/adg/adg_indexed_<timestamp>.sqlite` before any query or edit. Regenerate: `python tools/generate_full_adg.py`.
6. **Author-Gate for ambiguous decisions.** Score candidates 0.00–1.00, filter at 0.72, apply dominance rule (≥0.85, gap ≥0.12 → surface alone). See `author-gate-enforcement.md`.
7. **RCA auto-closure.** Execute corrective actions immediately. Never leave RCA unresolved.
8. **Guardian exemptions require Author-Gate.** Format: `# guardian: allow-<type> -- <specific justification>`. Generic words forbidden. Gate: `guardian_exemption_gate.py`.
9. **SVP Engineering persona for T3 architecture.** Prioritize: operational simplicity, dependency hygiene, archival over deletion, ADRs, zero-regression.
10. **Zero-loss refactor.** After removing boilerplate, check for hollow files. Gate: `zero_loss_refactor_verifier.py`.
11. **Terminal process lifecycle.** All `run_command`/subprocess calls must terminate when query completes. Gate: `check_terminal_cleanup.py`.
12. **No imports from `archives/` in production.** CI gate: `check_no_archives_imports.py`.
13. **MCP green light before T2/T3.** Check Redis hot cache first (`adg_redis_ingest.py --check`). Fallback: `adg_health`. Both red = BLOCKED.
14. **Subprocess timeout required.** `subprocess.run(argv, shell=False, timeout=30)`. No exceptions.
15. **Precise exception handling.** Catch specific types. Bare `except:` FORBIDDEN. `except Exception` without guardian comment FORBIDDEN.
16. **Query progress bar mandatory.** All operations >5s, loops >10 lines, or heavy-named functions (`scan_*`, `build_*`, `query_*`, etc.) >12 lines MUST display a colored progress bar. CI gate: `check_query_progress_bar.py`. See `query-progress-bar.md`.
17. **Memory lifecycle mandatory.** At the start of every conversation, call `mem_recall_session_start` to load persistent project context. After significant architecture decisions, Author-Gate resolutions, or new patterns, write to memory via `create_entities`/`add_observations`. See AGENTS.md Memory Lifecycle section.
18. **No hidden scope expansion.** Do not quietly widen scope. If the task grows, state it in the working packet and keep the change bounded.
19. **Mode separation is mandatory.** Separate `analyze` (inspect, no edits), `plan` (sequence, no edits), `edit` (make the change), and `verify` (prove the change). Do not blur these modes.
20. **Fact grading is mandatory.** Classify claims as **DIRECTLY OBSERVED**, **DERIVED**, or **UNRESOLVED**. Do not present unresolved items as facts.
21. **Zero-loss overwrite discipline.** When overwriting a rule, skill, or workflow: preserve useful constraints, remove redundancy, clarify triggers, preserve references relied on by scripts, and do not silently delete operational intent.
22. **ADG graph layer is primary for refactoring.** Materialized views (`mv_*`), semantic edges (`flows_to`, `emits_side_effect`, `resolves_callsite`, `controls_flow`, `reads_from`, `writes_to`), and pre-built P-views (`v_p0_*`, `v_p1_*`, `v_p2_*`, `v_p3_*`) MUST drive T2/T3 refactoring plans — not just raw `edges`/`violations` tables. Plans missing the `## ADG_GRAPH_LAYER_EVIDENCE` section are invalid. Gate: `check_graph_layer_evidence.py`. See `adg-graph-layer-enforcement.md`.
23. **ADG canonical invariants (doctrinal floor).** (a) Source-of-truth hierarchy: **SQLite=truth, Redis=hot projection, MCP=read-only gateway** — no divergence allowed. (b) **ADG wins conflicts**: if graph facts disagree with text search / intuition, the graph is authoritative. (c) Hotspot reports MUST classify every row with one of 4 archetypes (`CENTRAL_DEPENDENCY`, `ORCHESTRATOR`, `STATE_NODE`, `SAFETY_GATEKEEPER`), cross-reference the 5 ADG Surfaces (Execution/Write/Security/State/Observability), and trace the full Zero-Loss Propagation Pipeline. (d) Layer criticality: L0/L5 ×2.0, L3/L4 ×1.75, L1/L2 ×1.0, L6 ×0.75. (e) Static ADG (`adg_sqlite`) and Runtime ADG (`otel_mcp`) are distinct — do not conflate. (f) Prefer ADG node/edge queries over hardcoded path/layer strings. See `adg-canonical-invariants.md`.
24. **Deferred-scope capture mandatory.** Every deferred scope item MUST be captured with a `DEFERRED_SCOPE:` marker line in the Cascade response that introduces it (plain text, before any Notion `API-post-page`). Post-hook `post_cascade_deferred_scope_capture.py` auto-scores priority (P1..P5) and auto-posts to Wave/Phase Convergence DB. Priority is deterministic — never hand-assign `[Pn]`. Pre-session hook surfaces unresolved pendings; recovery script retries failed posts. Pre-commit gate `check_deferred_scope_markers.py` blocks plan-file commits with prose deferred-scope language without matching markers. See `deferred-scope-capture.md`.
25. **MCP serialization mandatory.** MCP tool calls (`mcp*_` prefix) MUST be issued one per response, with no sibling tool calls of any kind in the same `<function_calls>` block. Concurrent MCP dispatches hit a known upstream race in the Anthropic MCP client transport (`anthropics/claude-agent-sdk-typescript#41`) that causes the user-visible hang/cancel pattern. Prefer direct on-disk reads (SQLite, filesystem) over MCP round-trips when equivalent data is local. Advisory layer: `mcp-serialization.md`. Deterministic layer: `post_cascade_mcp_serialization_audit.py` → `artifacts/windsurf/mcp_serialization_violations.jsonl`. Auto-retires when upstream race is fixed.

## Quick Non-Negotiables

- No PowerShell.
- No shell=True.
- No silent scope growth.
- No graph questions answered by grep when ADG is healthy.
- No completion claims without verification.
- No new anti-pattern without approval.
- No long opaque work without progress.
- No deferred scope without a `DEFERRED_SCOPE:` marker.
- No MCP tool call batched with any other tool call in the same response.

## Tier Classification

| Tier | Scope | ADG Requirement |
|------|-------|----------------|
| **T0 — Question** | No code changes | ADG cache optional |
| **T1 — Trivial** | ≤1 file, ≤20 lines | Scoped tests only |
| **T2 — Scoped** | 2–5 files, single layer | Query ADG blast radius |
| **T3 — Architectural** | >5 files or cross-layer | Full ADG protocol mandatory |

ADG graph is the **primary** analysis primitive. `grep_search` for dependency analysis is FORBIDDEN.

### ADG-First Retrieval-Tool Decision Tree (§3.2 OpenDev pattern)

**STOP before every `grep_search` call. Check these observable query features:**

```
IF query contains "import", "from X import", "who imports" → ADG fanin
IF query targets a function/class/constant name in *.py   → ADG fanin
IF query asks "what does X depend on"                      → ADG fanout
IF query mentions "blast radius", "impact", "consumers"    → ADG fanin
IF query mentions "references", "who uses", "who calls"    → ADG fanin
IF query searches for an ALL_CAPS symbol name              → ADG fanin
IF query asks about architectural layers (L0-L6)           → ADG nodes_by_layer
ELSE (TODOs, FIXMEs, literal strings, non-Python content)  → grep_search OK
```

| Observable Feature | FORBIDDEN | REQUIRED |
|---|---|---|
| Query contains `from X import` or `import X` | `grep_search("from X import")` | `adg_nodes_by_file` → `adg_edge_fanin` |
| Query targets a function name `Y(` | `grep_search("Y(")` | `adg_edge_fanin(tgt_id=<Y_node>, relation_type="calls")` |
| Query targets a class name `class Y` | `grep_search("class Y")` | `adg_node(node_id=<Y>)` → `adg_edge_fanin` |
| Query asks outgoing deps of file Z | `grep_search("import", SearchPath=Z)` | `adg_edge_fanout(src_id=<Z_node>, relation_type="imports")` |
| Query mentions blast radius / impact | `grep_search("A", Includes=["*.py"])` | `adg_edge_fanin(tgt_id=<A_node>)` |
| Query targets ALL_CAPS constant | `grep_search("CONSTANT_NAME")` | `adg_edge_fanin(tgt_id=<const_node>)` |
| Literal text / TODO / non-code | `grep_search` ✅ ALLOWED | — |

**Why grep fails at dependency analysis**: false positives (comments, dead code), false negatives (re-exports, aliases), no transitive closure, no layer awareness, context window pollution (70-80% of tokens wasted per OpenDev §3.1).

**Degraded fallback rule**: Before using `grep_search` for any graph query, call `adg_health`. Fallback allowed only when health is red AND response contains `DEGRADED_FALLBACK: reason=<...>`. Silent fallback (no health check, no reason code) = `severity: critical` in `adg_first_violations.jsonl`.

Enforcement chain (4 layers):
1. `graph-analysis` skill auto-invokes → loads `tool_routing_decision_tree.md` at maximum recency
2. `pre_prompt_classifier.py` step 0 in SR_MANDATE (T2/T3 prompts)
3. This always_on rule (system prompt — fades after ~15 tool calls per OpenDev §2.3.4)
4. `post_cascade_adg_audit.py` retroactive detection → `artifacts/windsurf/adg_first_violations.jsonl`

## Quick Gates

- Plan SSOT: `.windsurf/plans/<name>-<6hex>.md` — never `docs/reports/plans/` for plans
- All Python file I/O: `encoding="utf-8"`
- `grep_search` permitted only to confirm literals, never for dependency tracing

## Extended Doctrine (model_decision rules)

Full protocol details live in focused rules — loaded on demand, not always_on:
- `adg-repair-discipline.md` — ADG repair loop and fail-closed recovery
- `anti-pattern-author-gate.md` — anti-pattern Author-Gate approval gate
- `author-gate-enforcement.md` — full Author-Gate decision pipeline and option shapes
- `sequential-thinking-enforcement.md` — T2/T3 structured reasoning protocol
- `global_rules.md` — subprocess, exception, MCP SSOT policy details
- `adg-test-accelerator-enforcement.md` — ADG-driven test scope selection
- `memory-management.md` — memory graph maintenance, purge sync, health thresholds
- `adg-hotspot-enforcement.md` — mandatory hotspot report before any refactoring
- `adg-graph-layer-enforcement.md` — MVs + semantic edges + P-views are PRIMARY for refactoring decisions
- `deferred-scope-capture.md` — DEFERRED_SCOPE marker contract, auto-scoring, auto-post + session-start recovery
