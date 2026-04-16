# Wave C Handoff Contract

**Version**: 2.0 · **Status**: Active (Wave B COMPLETE) · **Date**: 2026-04-16  
**Precondition**: Wave B complete (B7 final audit). This contract defines the boundary conditions Wave C must satisfy.  
**Scope**: What Wave C may do, what it must not change, and what it must prove.

---

## 1. Inherited Topology (DO NOT CHANGE)

Wave C inherits the Wave B3 three-collection topology exactly. No collection renames, splits, or merges.

| Collection | Lane | Source type | Normative use |
|------------|------|-------------|---------------|
| `ext_authority` | A: target_state_authority, B: supporting_guidance | External curated | ✅ Allowed — `invalid_for_normative_use=False` |
| `repo_evidence` | C: repo_canonical, D: repo_implementation | Internal repo | ❌ Excluded — `invalid_for_normative_use=True` |
| `ext_raw` | E: unvetted_web | Unvetted scraped | ❌ Excluded — `invalid_for_normative_use=True` |

**Anti-drift rule (non-negotiable)**: Target-state guidance MUST be sourced from `ext_authority` only. `repo_evidence` defines current state. `ext_raw` is never normative.

---

## 2. Allowed Target-State Sources (Wave C)

**Updated for B7**: Five of the original six B5R gap topics (hybrid retrieval, reranking, parent-child expansion, abstain/refine, embedding model selection) were closed by B6.x source additions. **Normative requirements spec (TS-20)** was confirmed as repo_evidence Lane C scope and is excluded from ext_authority. **F25-int** (confidence-scored healing dispatch routing) is out of ext_authority scope by adjudication.

Wave C may extend `ext_authority` only for advisory gaps not already closed. **No source additions are permitted for topics already ADEQUATE at B7.**

### Permitted additions (advisory gaps only)

| Gap topic | Suggested source candidates | Constraint |
|-----------|-----------------------------|------------|
| F02: Ingress auth / quota / schema (advisory) | OpenAI platform auth docs, agentic ingress patterns cookbook | Must be https://; advisory only — not a B7 hard gate |

### Permitted repo_evidence additions (Lane C, Wave C current-state work)

| Gap topic | Disposition | Constraint |
|-----------|-------------|------------|
| TS-20: Normative requirements spec | Add internal policy doc to `repo_evidence` Lane C | `invalid_for_normative_use=True`; no https:// URL |
| F25-int: Confidence-scored healing dispatch routing | Add internal architecture decision to `repo_evidence` Lane C | Documents the project-internal tier architecture only; no ext_authority addition permitted |

### Forbidden additions

- Sources already in `ext_authority` (C9: no duplicate URLs)
- Sources not reachable via `https://`
- Unvetted scrapes (→ `ext_raw` only, if at all)
- Internal repo documents (→ `repo_evidence` only)
- **New ext_authority sources for F25-int, TS-03, TS-04, TS-07, TS-09, TS-19** — these are CLOSED at B7; do not add further sources
- **Any source framed as closing F25 healing dispatch routing** — this query is retired; the concept is grounded via F25-ext

---

## 3. Allowed Current-State Sources

`repo_evidence` may be extended with additional internal repo documents that satisfy:
- `invalid_for_normative_use = True`
- `source_url` is a repo-relative path (no `https://`)
- `source_band` is `repo_canonical` (Lane C) or `repo_implementation` (Lane D)

Current-state queries (`architecture`, `internal_arch`, `repo_gap`, `implementation`) route to `repo_evidence`. This routing MUST NOT change.

---

## 4. Route Purity Contract (Immutable)

These routing rules are frozen. Wave C must not modify `query_router.py` domain-to-collection mappings without a documented route purity violation as justification.

```python
# FROZEN — do not change without route purity blocker evidence
_domain_to_collection = {
    "policy":        "ext_authority",    # normative — external only
    "best_practice": "ext_authority",    # normative — external only
    "tool_contracts":"ext_authority",    # normative — external only
    "architecture":  "repo_evidence",    # internal arch — repo only
    "code":          "code_chunks",      # implementation
}

# Architecture domain prefilter — frozen
_get_arch_prefilter("architecture") → {"source_band": "repo_canonical"}
```

**evidence_shaper.py** `allowed_collections` default = `ext_authority` — frozen.

---

## 5. Metadata Contract (Immutable)

The Wave B final metadata contract (`docs/requirements/wave_b_metadata_contract.md`) is frozen. Wave C must not add or remove mandatory fields. Any new chunk ingested into any Wave B collection must satisfy all 14 required fields.

**Required fields** (all collections):
`source_collection`, `source_band`, `authority_tier`, `normative_scope`, `invalid_for_normative_use`, `source_type`, `topic_bucket`, `doc_family`, `source_url`, `heading_path`, `collapse_group`, `title`, `chunk_index`, `canonical_digest`

---

## 6. Wave B Freeze Gates Wave C Must Not Regress

When Wave C adds sources and rebuilds collections, all 11 Wave B freeze gates must continue to pass.

| Gate | Invariant |
|------|-----------|
| G1 | ext_authority: invalid_for_normative_use=False on ALL chunks |
| G2 | ext_authority: source_url starts with https:// on ALL chunks |
| G3 | ext_authority: all required fields present on ALL chunks |
| G4 | repo_evidence: invalid_for_normative_use=True on ALL chunks |
| G5 | repo_evidence: no https:// source_url on ANY chunk |
| G6 | repo_evidence: all required fields present on ALL chunks |
| G7 | ext_raw: invalid_for_normative_use=True on ALL chunks |
| G8 | ext_raw: no URL overlap with ext_authority |
| G9 | ext_authority retrieval strength ≥ 75% (B7 result: ≥95% — must not regress below 75%) |
| G10 | 0 non-ext_authority chunks in target-state audit results |
| G11 | 0 ext_raw chunks in target-state audit results |

**G9 passes at B7 (≥95%).** Wave C must not regress G9 below 75%. Wave C may not reopen closed topics (TS-03, TS-04, TS-07, TS-09, TS-19, F25-int) by adding further sources.

---

## 7. External-Only Target-State Baseline (B7 Final)

The `docs/requirements/wave_b_target_state_registry.md` (v2.0) defines the B7 external-only target-state baseline. Wave C extends it; Wave C must not remove or contradict any entry in the registry.

**Grounded topics at B7 (≥19/20 original queries + 2 new = ≥21/22)**:
- Orchestrator-workers pattern (STRONG, dist@1=0.349)
- MCP tool definition and registration (STRONG, dist@1=0.277)
- FastMCP server pattern (STRONG, dist@1=0.347)
- Agent handoffs (STRONG, dist@1=0.335)
- Single vs multi-agent architecture (STRONG, dist@1=0.329)
- Evidence shaping (ADEQUATE, dist@1=0.445)
- Agentic architecture patterns (ADEQUATE, dist@1=0.417)
- Safety guardrails (ADEQUATE, dist@1=0.456)
- Evaluator-optimizer pattern (ADEQUATE, dist@1=0.429)
- Routing principles (ADEQUATE, dist@1=0.473)
- Chunking strategy (ADEQUATE, dist@1=0.500)
- Metadata provenance (ADEQUATE, dist@1=0.498)
- Context engineering (ADEQUATE, dist@1=0.421)
- Contextual retrieval (ADEQUATE, dist@1=0.500)
- Hybrid retrieval / BM25+dense (ADEQUATE — closed by B6.x P3/P9)
- Cross-encoder reranking (ADEQUATE — closed by B6.x P4)
- Parent-child chunk expansion (ADEQUATE — closed by B6.x P5/P9)
- Abstain / refine signals (ADEQUATE — closed by B6.x P6/P11)
- Embedding model selection (ADEQUATE — closed by B6.x P7)
- **F25-ext: Tiered escalation / HITL / durable execution** (ADEQUATE advisory — grounded by running_agents.md HITL section)
- LLM response caching / exact cache (ADEQUATE — closed by B6 P1)
- Semantic/vector caching (ADEQUATE — closed by B6 P2)

**Out-of-scope for ext_authority (Wave C must route these to repo_evidence Lane C)**:
- TS-20: Normative requirements spec — project-specific; repo_evidence Lane C
- F25-int: Confidence-scored healing dispatch routing — project-internal; repo_evidence Lane C

**G9 Wave C target**: G9 PASSES at B7 (≥95%). Wave C must not regress below 75%.

---

## 8. Gap Analysis Rules for Wave C

Wave C gap analysis MUST follow these rules:

1. **External target-state gap**: `ext_authority` retrieval returns dist@1 > 0.50 for a topic AND answer_support fails → gap is confirmed; add external source.
2. **Internal current-state gap**: `repo_evidence` retrieval returns dist@1 > 0.50 for an internal topic → gap is in repo docs, not ext_authority.
3. **No cross-lane gap filling**: Do not fill an external target-state gap with `repo_evidence` chunks, and do not fill an internal architecture gap with `ext_authority` chunks.
4. **Minimum evidence standard**: A new source must return dist@1 < 0.45 for the gap query to be accepted as closing the gap.

---

## 9. What Wave C Must NOT Do

- Modify the 3-collection topology (no new collections, no renames)
- Change `invalid_for_normative_use` values on existing chunks
- Add internal repo documents to `ext_authority`
- Add web scrapes to `ext_authority` (scrapes → `ext_raw` only)
- Modify `query_router.py` routing without a documented route-purity blocker
- Modify `evidence_shaper.py` normative filter logic without a documented blocker
- Start any retrieval path redesign (query intent detection, hybrid fusion, reranking pipeline)
- Delete or archive any Wave B collection without full migration evidence
- Add new ext_authority sources targeting F25-int or the retired F25 healing dispatch query
- Reopen the F25 adjudication (this reclassification is final per wave_b_b7_final_audit.md §3)
- Add ext_authority sources for topics already ADEQUATE at B7 (TS-03, TS-04, TS-07, TS-09, TS-19)

---

## 10. Wave C Entry Criteria

Wave C may begin. All entry criteria are satisfied as of 2026-04-16:

- [x] This handoff contract is acknowledged by the implementing party
- [x] `docs/reports/wave_b_closeout.md` is in final COMPLETE state (v2.0, 2026-04-16)
- [x] All 11 Wave B freeze gates pass (see `docs/reports/wave_b_b7_freeze_gates.md`)
- [ ] A Wave C plan is drafted in `.windsurf/plans/` with source additions justified per §2 (Wave C work item)
