# ADR-077 — C0 Retrieval Stack Boundary: L0 Dispatcher vs L_PG Knowledge Subsystem

**Status:** Accepted
**Date:** 2026-04-30
**Deciders:** L0 routing owner, L_PG knowledge plane owner, C0 architecture review
**Source plan:** `.claude/plans/c0-context-engine-wiring-fix-9e42a1.md`
**Related:** ADR (none directly — this is a boundary-clarification ADR)
**Author-Gate:** 2026-04-30 (architecture_choice, selected=adr_documenting_boundary_close_next_step, confidence=0.78)

---

## Context

The codebase carries two retrieval module trees that, on first inspection,
appear redundant:

- `agentic_core/L0_routing/c0_retrieval/` — 30 modules including
  `dispatcher.py`, `plan.py`, `gates.py`, `evidence_contract.py`,
  `final_contract.py`, plus a `c0_3_enhanced/` subpackage.
- `agentic_core/knowledge/retrieval/` — 25 modules including
  `retrieval_plan.py`, `hybrid_recall_stage.py`,
  `senior_librarian_reranker.py`, `evidence_contract_builder.py`, and
  several reranker / citation-adapter implementations.
- `agentic_core/knowledge/gates/` — 3 modules (the most notable being
  `preretrieval_gate.py`).

The original framing in
`.claude/plans/c0-context-engine-wiring-fix-9e42a1.md` and the
`NEXT_STEP` marker emitted on 2026-04-30 (page
`35227693-f55c-8133-933e-c0af5ebc6486`) treated these as **"two parallel
C0 implementations"** to be deduplicated. A subsequent ADG audit
(against snapshot `adg_indexed_04302026_1319.sqlite`) showed this
framing was **incorrect**.

## ADG-derived facts

The following facts come from direct SQLite queries against the latest
ADG snapshot (constitutional §22, §28). They are the authority over any
prose framing that disagrees.

### F1 — Module surfaces are sized differently and serve different layers

| Stack | Module count | Layer assignment | Production caller layers |
|---|---:|---|---|
| `agentic_core/L0_routing/c0_retrieval/*` | 30 | **L0** | L0, L1, L_APP, L_PG |
| `agentic_core/knowledge/retrieval/*` | 25 | **L_PG** | L2, L3, L_APP, L_PG, L_TOOLS |
| `agentic_core/knowledge/gates/*` | 3 | **L_PG** | L0 (since 2026-04-30 — see §F4) |

Both stacks have substantial production usage. Neither is dead code.

### F2 — Zero same-name module overlap

A basename-collision query across the two stacks yields exactly **one**
collision: both have an `__init__.py`. There are NO same-named functional
modules. `evidence_contract.py` (L0) and `evidence_contract_builder.py`
(L_PG) are not duplicates — different names, different APIs, different
consumer layers.

### F3 — Disjoint consumer surfaces

`L0/c0_retrieval/*` is consumed primarily by **the C0 dispatcher itself**
(internal cohesion via relative imports) plus a handful of L0/L1/L_APP
callers that drive request-time evidence retrieval.

`L_PG/knowledge/retrieval/*` is consumed by **upstream pipelines** —
`L3_orchestration.../context_compaction.py` for evidence binding,
`L2_execution/...` for evaluation flows, `L_APP` applications for
domain-specific retrieval, and `L_TOOLS` for build-time tooling.

The two stacks address **different problems at different layers**:

- **L0/c0_retrieval is a request-time orchestrator.** Its purpose is to
  coordinate a single C0 request through the documented 5-stage pipeline
  (C0.0 preflight → C0.0b ACL gate → C0.1 plan → C0.2-C0.5 fetch / graph
  / shape / contract). It owns the dispatcher state machine, the
  RouteContract → C0Result transformation, and the never-throw seal of
  the FinalEvidenceContract.

- **L_PG/knowledge/retrieval is a reusable knowledge subsystem.** It
  provides retrieval primitives (citation adapters for Anthropic /
  Qwen / dual-pass, hybrid recall implementations, reranker variants,
  evidence-contract builder) that are composed by *multiple* upstream
  callers, only one of which is the L0 C0 dispatcher.

### F4 — The dispatcher already calls into the subsystem (correct gravity)

As of 2026-04-30 (see same Author-Gate session as this ADR), the L0 C0
dispatcher imports `agentic_core.knowledge.gates.preretrieval_gate.check_access`
and invokes it as new pipeline stage **C0.0b** (post-preflight,
pre-plan). This is the correct architectural direction — higher layer
(L0) depending on lower layer (L_PG) — and validates that the two
stacks **compose**, they do not compete.

## Decision

> **The L0/c0_retrieval and L_PG/knowledge/retrieval stacks are NOT duplicates.
> They serve different consumer surfaces at different layers. Both remain
> canonical at their respective layers. The L0 dispatcher MAY call into the
> L_PG subsystem for reusable primitives — this is the correct gravity
> direction and is the pattern adopted by stage C0.0b.**

### What this ADR rejects

- ❌ Archiving `L_PG/knowledge/retrieval/*` — would break 5 distinct
  production caller layers (L2, L3, L_APP, L_PG, L_TOOLS).
- ❌ Archiving `L0/c0_retrieval/*` — would break the C0 dispatcher
  pipeline that this ADR confirms is canonical.
- ❌ Creating a "merged" canonical retrieval package — there is nothing
  to merge; the modules have different names and different APIs.
- ❌ Treating the file count (30 + 25) as evidence of duplication —
  large file counts at different layers are evidence of a **layered
  architecture**, not duplication. Constitutional §22 (graph-layer
  primitives drive refactoring decisions) makes ADG name-collision
  evidence the dispositive test, not LOC counts.

### What this ADR accepts

- ✅ Both stacks remain in the codebase, at their respective layers.
- ✅ The L0 dispatcher continues to import L_PG primitives where useful
  (currently: `preretrieval_gate.check_access` at stage C0.0b).
- ✅ Future module additions to either stack are evaluated against
  their stack's purpose (request-time orchestration vs reusable
  knowledge primitive), not against the count in the other stack.

### Future overlap-claim contract

Any future plan or NEXT_STEP that proposes deduplicating these stacks
**MUST** cite ADG name-collision evidence — specifically, a query
returning ≥1 same-basename module shared between the two trees AND
≥1 caller layer that imports BOTH modules. Without that evidence, the
plan is unfounded under ADR-077 and constitutional §22.

The query for that evidence (canonical SSOT):

```sql
-- ADG name-collision query (constitutional §28: direct SQLite, the
-- canonical fallback when MCP serialization §25 forbids a 2nd MCP call)
SELECT a.resolved_path AS l0_module, b.resolved_path AS lpg_module
FROM nodes a
JOIN nodes b ON SUBSTR(a.resolved_path, INSTR(a.resolved_path, '/c0_retrieval/') + 14)
              = SUBSTR(b.resolved_path, INSTR(b.resolved_path, '/retrieval/') + 11)
WHERE a.entity_type = 'module'
  AND a.resolved_path LIKE 'agentic_core/L0_routing/c0_retrieval/%'
  AND b.entity_type = 'module'
  AND b.resolved_path LIKE 'agentic_core/knowledge/retrieval/%'
  AND a.resolved_path != b.resolved_path;
```

Today this query returns **0 rows** (the only collision is `__init__.py`,
which is a Python package marker not a functional module). When it
returns ≥1 functional collision, that is the trigger for re-opening the
dedup question.

## Consequences

### Positive

- The NEXT_STEP item "Dedup L_PG retrieval vs L0 c0_retrieval stacks"
  (Notion page `35227693-f55c-8133-933e-c0af5ebc6486`) is closed with
  the architecturally honest answer.
- Future contributors see the boundary documented and stop attempting
  to "simplify" by collapsing distinct subsystems.
- The L0 → L_PG gravity pattern (from C0.0b stage wiring) is now a
  documented precedent — other dispatcher stages may follow the same
  pattern when they need reusable knowledge primitives.

### Negative

- The codebase still has 30 + 25 retrieval-related modules. If anyone
  judges code health by raw file count, this ADR will look like a
  punt. The architectural answer (different consumer surfaces at
  different layers) is correct regardless.

### Neutral

- This ADR creates no enforcement gate. Constitutional §22 already
  requires ADG-evidence-driven refactoring decisions; the name-collision
  query in this ADR is the specific test for the C0 retrieval stacks.

## References

- Author-Gate decision capture (2026-04-30): refactor_scope ⇒
  finish_two_items_introduced_this_chat ⇒ Item 2 ⇒ architecture_choice
  ⇒ selected=adr_documenting_boundary_close_next_step
- Plan: `.claude/plans/c0-context-engine-wiring-fix-9e42a1.md`
- ADG snapshot: `artifacts/adg/adg_indexed_04302026_1319.sqlite`
- Constitutional §22 (ADG graph layer is primary for refactoring)
- Constitutional §28 (SQLite-direct fallback supersedes grep)
- Sibling stage wiring: `agentic_core/L0_routing/c0_retrieval/dispatcher.py`
  C0.0b stage (commit `0a14e94b63`)
- Manifest entry: `config/canonical_pipelines.yaml` C01_acl_gate
  (status=active as of 2026-04-30)
