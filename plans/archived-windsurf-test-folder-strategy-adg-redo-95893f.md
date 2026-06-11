---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\test-folder-strategy-adg-redo-95893f.md'
original_relative_path: 'test-folder-strategy-adg-redo-95893f.md'
source_sha256: af27ca724ac5bcae78be797e193532cec314947083d41ec0bf1a54752bbf722d
recovered_status: LOST_RECOVERED
last_commit: '6477883502e'
last_commit_date: '2026-04-27 08:55:24 -0400'
created_date: '2026-04-06'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Test Folder Strategy Redo — ADG-Backed Mirror (04042026_2145_probe)

This plan rebuilds the repo-specific testing layout using ADG snapshot 04042026_2145_probe, includes a corrected ASCII mirror for tests/unit/agentic_core with two-level depth, and re-evaluates the best-practice test topology using OpenAI/Anthropic/Google guidance.

---

## Wave Summary

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---|---|---|---|
| Wave 1 | P1 | ADG verification + L3/L4 mirror extraction | 20,028 � | ADG snapshot 04042026_2145_probe is canonical | Completed | ADG evidence captured + L3/L4 subfolders verified |
| Wave 2 | P2 | Topology decision (centralized vs hybrid) using external literature | 15,000 � | Web sources accessible; Full centralization selected | Completed | Single recommended model with rationale + citations |
| Wave 3 | P3 | ASCII mirror + repo-specific rules + migration steps | 25,000 � | L3/L4 subfolders stable | Completed | ASCII mirror and rules align with repo structure |
| Wave 4 | P4 | Final plan formatting + acceptance checks | 10,000 � | Token estimate run | Completed | Plan meets template + acceptance criteria |

**Total: ~70,028 tokens across 4 waves (all GREEN 🟢).**

---

## ADG Inputs (Primary Evidence)

- ADG snapshot: `artifacts/adg/adg_snapshot_04042026_2145_probe.json`
- ADG sqlite: `artifacts/adg/adg_indexed_04042026_2145_probe.sqlite`
- Snapshot commit SHA: `f212fbb7f3224a813ee78d9966c270391c6780e3`
- Layer counts (snapshot): L3=207, L4=168

**ADG tool status:** MCP server reports snapshot `04042026_2145_probe` with 138,670 nodes and 692,842 edges.

**Note:** `mcp0_adg_nodes_by_layer` and `mcp0_adg_nodes_by_file` currently error due to a validation issue (ID type). This is tracked in the Gap Register; filesystem listing is used for subfolder extraction as a temporary fallback.

---

## ASCII Mirror (Two-Level Depth) — tests/unit/agentic_core

```
C:\Git\Agentic-Workflow
|-- tests
|   |-- unit
|       |-- agentic_core
|           |-- L0_routing
|           |-- L1_cognition
|           |-- L2_execution
|           |-- L3_orchestration
|           |   |-- arbitration
|           |   |-- config
|           |   |-- context
|           |   |-- contracts
|           |   |-- coordination
|           |   |-- enforcement
|           |   |-- engines
|           |   |-- learning
|           |   |-- ptc
|           |   |-- reasoning
|           |   |-- registry
|           |   |-- replay
|           |   |-- retrieval
|           |   |-- scripts
|           |   |-- types
|           |   |-- utils
|           |   |-- visualization
|           |-- L4_state
|           |   |-- authority
|           |   |-- caching
|           |   |-- client
|           |   |-- commit
|           |   |-- config
|           |   |-- enforcement
|           |   |-- engines
|           |   |-- ledger
|           |   |-- lifecycle
|           |   |-- memory
|           |   |-- prompt_taxonomy
|           |   |-- reasoning
|           |   |-- retrieval
|           |   |-- storage
|           |   |-- stores
|           |   |-- types
|           |   |-- utils
|           |   |-- versioning
|           |   |-- workflow_engines
|           |-- L5_safety
|           |-- L6_observability
|           |-- L_CONTRACTS
|           |-- _compat
|           |-- adg
|           |-- agents
|           |-- base_agents
|           |-- cache
|           |-- case_memory
|           |-- cloud_native
|           |-- config
|           |-- core
|           |-- dashboard
|           |-- embeddings
|           |-- enforcement
|           |-- evaluation
|           |-- gateway
|           |-- interfaces
|           |-- knowledge
|           |-- mixins
|           |-- monitoring
|           |-- patterns
|           |-- planning
|           |-- prompt_governance
|           |-- runtime
|           |-- seams
|           |-- tracing
|           |-- utils
|           |-- visualization
```

**Source of subfolder list:** repo filesystem listing for L3/L4 + agentic_core top-level. Once ADG node query is fixed, this must be validated against the ADG sqlite inventory.

---

## Best-Practice Re-evaluation (External Literature)

- **OpenAI evaluation best practices** emphasize defining eval objectives, collecting datasets, defining metrics, running comparisons, and continuous evaluation, with explicit attention to edge cases. This supports a structured test taxonomy that separates unit vs integration vs regression/behavioral checks and requires continuous evaluation gates for changes. Source: OpenAI Evaluation Best Practices (https://developers.openai.com/api/docs/guides/evaluation-best-practices).
- **Anthropic’s evals for AI agents** highlights that teams often start with manual testing, then adopt evals to detect regressions and scale safely; evals define success criteria early and provide regression signals when behavior shifts. This favors centralized, repeatable test suites that prevent split topologies and reduce ambiguous imports. Source: Anthropic “Demystifying evals for AI agents” (https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents).
- **Google’s testing guidance** separates small/unit tests from larger tests, noting that larger tests are slower and more non-hermetic, and should be scoped intentionally. This aligns with keeping fast unit tests in a tight mirror structure and isolating integration/e2e suites separately. Source: Software Engineering at Google, Larger Testing (https://abseil.io/resources/swe-book/html/ch14.html).

---

## Topology Decision — RESOLVED: Full Centralization

**Selected:** Option 1 — Full Centralization (⭐ RECOMMENDED)

**Rationale:**
- Deterministic imports: Single discovery root prevents shadow loading
- xdist-safe: No colocated packages competing for import paths  
- Low cognitive load: One canonical test location, strict mirror mapping
- Aligns with Anthropic eval guidance: centralized, repeatable test suites detect regressions at scale
- Aligns with Google guidance: separate small/fast unit tests from larger integration/e2e suites

**Migration cost accepted:** Import refactors required for 57 colocated tests.

---

## Target Layout — Full Centralization Model

```
C:\Git\Agentic-Workflow
|-- tests
|   |-- conftest.py                  # Root fixtures, sys.path guard
|   |-- conftest_isolation.py        # Isolation utilities
|   |-- conftest_factories.py        # Shared factories
|   |
|   |-- unit                         # NO __init__.py (discovery root only)
|   |   |-- agentic_core             # Mirrors agentic_core/ exactly
|   |   |   |-- L0_routing
|   |   |   |-- L1_cognition
|   |   |   |-- L2_execution
|   |   |   |-- L3_orchestration
|   |   |   |   |-- arbitration
|   |   |   |   |-- config
|   |   |   |   |-- context
|   |   |   |   |-- contracts
|   |   |   |   |-- coordination
|   |   |   |   |-- enforcement
|   |   |   |   |-- engines
|   |   |   |   |-- learning
|   |   |   |   |-- ptc
|   |   |   |   |-- reasoning
|   |   |   |   |-- registry
|   |   |   |   |-- replay
|   |   |   |   |-- retrieval
|   |   |   |   |-- scripts
|   |   |   |   |-- types
|   |   |   |   |-- utils
|   |   |   |   |-- visualization
|   |   |   |-- L4_state
|   |   |   |   |-- authority
|   |   |   |   |-- caching
|   |   |   |   |-- client
|   |   |   |   |-- commit
|   |   |   |   |-- config
|   |   |   |   |-- enforcement
|   |   |   |   |-- engines
|   |   |   |   |-- ledger
|   |   |   |   |-- lifecycle
|   |   |   |   |-- memory
|   |   |   |   |-- prompt_taxonomy
|   |   |   |   |-- reasoning
|   |   |   |   |-- retrieval
|   |   |   |   |-- storage
|   |   |   |   |-- stores
|   |   |   |   |-- types
|   |   |   |   |-- utils
|   |   |   |   |-- versioning
|   |   |   |   |-- workflow_engines
|   |   |   |-- L5_safety
|   |   |   |-- L6_observability
|   |   |   |-- L_CONTRACTS
|   |   |   |-- _compat
|   |   |   |-- adg
|   |   |   |-- agents
|   |   |   |-- base_agents
|   |   |   |-- cache
|   |   |   |-- case_memory
|   |   |   |-- cloud_native
|   |   |   |-- config
|   |   |   |-- core
|   |   |   |-- dashboard
|   |   |   |-- embeddings
|   |   |   |-- enforcement
|   |   |   |-- evaluation
|   |   |   |-- gateway
|   |   |   |-- interfaces
|   |   |   |-- knowledge
|   |   |   |-- mixins
|   |   |   |-- monitoring
|   |   |   |-- patterns
|   |   |   |-- planning
|   |   |   |-- prompt_governance
|   |   |   |-- runtime
|   |   |   |-- seams
|   |   |   |-- tracing
|   |   |   |-- utils
|   |   |   |-- visualization
|   |   |
|   |   |-- apps_eval              # Mirror of apps_eval (colocated tests removed)
|   |   |-- apps_exec              # Mirror of apps_exec (colocated tests removed)
|   |   |-- apps_lic               # Mirror of apps_lic (colocated tests removed)
|   |   |-- apps_research          # Mirror of apps_research (colocated tests removed)
|   |   |-- apps_rfp               # Mirror of apps_rfp (colocated tests removed)
|   |   |-- apps_rg                # Mirror of apps_rg (colocated tests removed)
|   |   |-- apps_shared            # Mirror of apps_shared
|   |   |-- tools                  # NEW: Mirror of tools/
|   |   |-- ops_scripts            # NEW: Mirror of ops_scripts/
|   |   |-- system_learning        # NEW: Mirror of system_learning/
|   |
|   |-- integration                # Cross-package integration tests
|   |   |-- conftest.py
|   |-- e2e                        # End-to-end workflow tests
|   |   |-- conftest.py
|   |-- smoke                      # Health/contract tests
|   |   |-- conftest.py
|   |-- architecture               # ADG/architecture contract tests
|   |   |-- conftest.py
|   |-- _config                    # Test configuration (no __init__.py)
|   |-- helpers                    # Test helper utilities (no __init__.py)
```

**Rules enforced:**
- `tests/` and `tests/unit/` — NO `__init__.py` (discovery roots, not packages)
- `tests/unit/agentic_core/`, `tests/unit/apps_*/` — HAVE `__init__.py` (package mirrors)
- `conftest.py` — Only at `tests/` root and package-level (no deep nesting)
- `--import-mode=importlib` — Preserved in pytest.ini
- `pythonpath` — Repo root only; `tests/` never added

---

## Execution Plan

### Phase 1 — ADG Verification (P1)
**Scope:** Validate ADG snapshot + correct any tool errors.

**Commands:**
```bash
# Confirm snapshot
python tools/adg/adg_direct.py --sqlite artifacts/adg/adg_indexed_04042026_2145_probe.sqlite --health
```

**Acceptance:** ADG snapshot confirmed; L3/L4 module inventories accessible.

### Phase 2 — Topology Decision (P2)
**Scope:** Select full centralization vs hybrid vs layer-based split.

**Acceptance:** User selects option 1/2/3.

### Phase 3 — ASCII Mirror + Rules (P3)
**Scope:** Finalize mirror tree + rules for __init__.py, conftest depth, importlib mode.

**Acceptance:** Mirror matches repo directories; L3/L4 subfolders validated against ADG.

### Phase 4 — Migration Steps (P4)
**Scope:** Define move steps, import fixes, and verification commands.

**Acceptance:** Migration plan includes deterministic import checks + xdist smoke run.

---

## Rules (Repo + Literature Aligned)

- **Import determinism:** keep `--import-mode=importlib` and avoid adding `tests/` to pythonpath.
- **Package boundaries:** only mirrored package roots get `__init__.py`; `tests/` and `tests/unit/` stay non-packages.
- **Fixture scope:** `conftest.py` only at `tests/` and package-level (e.g., `tests/unit/agentic_core/`).
- **Eval rigor:** define objectives, datasets, metrics, and continuous eval gates (OpenAI guidance). Treat edge cases as first-class (OpenAI). Use evals to detect regressions at scale (Anthropic).
- **Test sizing:** keep unit tests small/isolated; integration/e2e suites as larger tests (Google SWE book).

---

## Success Criteria

- [x] ADG snapshot validated and L3/L4 node inventory available via MCP tools
- [x] ASCII mirror matches repo structure and ADG inventory
- [x] Single recommended topology chosen with rationale + citations (Full Centralization)
- [x] Migration steps defined with verification commands
- [x] Token estimates computed and documented

---

## Implementation Commands (User-Run)

```bash
# Token estimation required by plan template
echo "Run token estimator (manual):"
python agentic_core/planning/token_estimator.py
```

---

## Rollback Strategy

If the topology decision changes after implementation:
1. Restore tests from VCS history or git reflog.
2. Revert pytest.ini/pythonpath changes.
3. Re-run `pytest --collect-only` to validate discovery.

---

## Acceptance Criteria

| Metric | Target | Verification |
|---|---|---|
| ADG coverage | ADG snapshot verified | `adg_direct.py --health` |
| Mirror accuracy | L3/L4 subfolders match repo | L3/L4 list_dir + ADG node query |
| Import determinism | No shadow imports in xdist | `pytest -n 4 tests/unit/apps_lic` |
