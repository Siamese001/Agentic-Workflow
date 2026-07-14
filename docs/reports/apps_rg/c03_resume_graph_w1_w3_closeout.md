# apps_rg C0.3 Resume Graph Hardening — W1-W3 Closeout

- **Plan:** `apps-rg-c03-resume-graph-hardening-9f3c2a`
- **Branch:** `agent/apps-rg-c03-resume-graph-w1-w6`
- **Base:** `origin/main@3ada93fc2c780fe548e723d68e7e5e5bdf8b21c7`
- **Scope:** W1 contract consolidation, W2 hard authority/fail-closed boundary, W3 actual bounded traversal and exhaustive terminal decisions
- **agentic_core edits:** none
- **Implementation commit:** `07cb833099`
- **Status:** `PASS`

## Implemented surfaces

1. `apps_rg/runtime/c0/c03_resume_graph_contracts.py`
   - pre-target authority contract;
   - terminal candidate-decision schema;
   - replayable traversal events and conservation receipt;
   - canonical section-plan validation and stable digest.
2. `apps_rg/runtime/sections/graph_role_episode_selector.py`
   - authority walk before JD/role scoring;
   - full bounded sibling enumeration;
   - deterministic skill/metric ranking before caps;
   - terminal decisions for roots, skills, metrics, and source facts;
   - no source-order slice or metric second-pass reuse.
3. `apps_rg/runtime/c0/c03_sqlite_graph_selection.py`
   - lazy context import closes the W0 circular-import baseline;
   - hard pre-target authority gates;
   - explicit current-run usage scope;
   - exhaustive candidate ledger and replayable direct-path events.
4. `apps_rg/runtime/c0/c03_graph_expansion.py`
   - direct binding from a frozen selected graph plan, role-episode root graph, or SQLite-ranked direct path;
   - canonical surface/ledger alias remapping;
   - broad fact-link and label/tag proof fallback removed;
   - proof-eligible missing frontier fails closed.

## Baseline blocker dispositions

| W0 blocker | W1 disposition |
|---|---|
| SQLite materializer circular import | Closed in `apps_rg` by lazy importing `ensure_c03_graph_sqlite` inside the public selector. |
| App-authority literal in `agentic_core/L0_routing/__init__.py` | Pre-existing current-main violation; explicitly out of scope because this plan forbids `agentic_core` edits. |
| Strict Codex readiness nonzero in GitHub-hosted runner | Environment-only transport/profile limitation; no authority or product gate weakened. |
| ADG current snapshot | Current-main direct receipt records zero open P0 fixes; tracked debt remains visible. |
| Aggregation boundary | Unchanged: aggregation consumes C0.3 receipts and does not traverse or rerank. |

## Verification

| Check | Result |
|---|---|
| W1-W3 authority/SQLite/traversal focused tests | **14 passed** |
| W1-W5/X3 refreshed-base focused suite | **50 passed** |
| Evidence-authority boundary suite | **6 passed** |
| C0.3 graph hardening validator | **PASS** |
| Python compilation | **PASS** |
| `agentic_core` production diff | **None** |

The local primary runtime did not ship optional `openai` or `chromadb` packages. The focused SQLite test used import-only temporary stubs for those unused optional modules; the tested path used the real generated SQLite projection and repository graph data. Branch CI with the repository dependency install remains the authoritative non-stub verification.
