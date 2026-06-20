---
plan_id: searxng-primary-search-a4f7c9
plan_format: v2
plan_type: refactor
touches_agentic_core: false
touches_governance_ci: false
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
supersedes: []
---

# SearXNG Primary Search Refactor

Make SearXNG the primary `apps_research` web-search provider while preserving offline behavior and compatibility wrappers for existing Tavily-shaped imports.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: DONE
CURRENT_WAVE: W3
LAST_COMPLETED_WAVE: W3
LAST_UPDATED: 2026-06-19

---

## Context (SCQA)

- **Situation** - `apps_research` currently routes live web retrieval through a Tavily-named adapter and has tests, docs, and SLO language keyed to `TAVILY_API_KEY`.
- **Complication** - SearXNG is the desired primary provider and uses a self-hosted HTTP `/search` API, not a Python SDK or vendor key.
- **Question** - How do we make SearXNG the primary runtime search provider without breaking existing retrieval consumers or offline tests?
- **Answer** - Introduce a provider-neutral retrieval seam backed by SearXNG, keep Tavily aliases only as compatibility shims, update docs/tests/env guidance, and verify the app-layer blast radius.

---

## Status Tables

### Wave Progress

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1 | W1.1, W1.2 | Branch/worktree isolation and plan artifact | ~2K | Existing dirty primary checkout must stay untouched except plan file | DONE | Worktree exists and plan file is tracked candidate |
| W2 | W2.1, W2.2, W2.3 | SearXNG adapter and runtime rewiring | ~8K | SearXNG JSON format is enabled on the configured instance | DONE | Runtime consumers call provider-neutral retrieval and Tavily SDK/direct client is removed from active path |
| W3 | W3.1, W3.2 | Tests, docs, PR draft | ~6K | Live SearXNG tests are opt-in by env | DONE | Scoped tests pass, docs describe config, PR is drafted |

### Phase Progress

| Phase | Title | Status |
|-------|-------|--------|
| W1.1 | Create isolated worktree branch | DONE |
| W1.2 | Create plan file | DONE |
| W2.1 | Add provider-neutral SearXNG retrieval adapter | DONE |
| W2.2 | Rewire app consumers away from active Tavily dependency | DONE |
| W2.3 | Preserve compatibility imports where needed | DONE |
| W3.1 | Update tests and docs | DONE |
| W3.2 | Verify, commit, push, draft PR | DONE |

---

## Out Of Scope

- Hosting or provisioning a SearXNG instance.
- Refactoring dormant MCP registry/governance references to Tavily.
- Removing historical plan/archive mentions of Tavily.
- Changing `agentic_core` contracts or apps_rg ingress field names.

---

## Wave 1 - Isolation And Plan

WAVE_ID: W1
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: USER_APPROVED
CHECKPOINT: A

**Authorization**: USER_APPROVED - User approved implementation after plan gate.

**Phases**:
- **W1.1** - Create isolated worktree branch | ~1K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W1.2** - Create disk plan file | ~1K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Acceptance**:
- Worktree folder basename exactly matches branch name.
- Primary checkout receives only this plan file during planning/setup.

---

## Wave 2 - Runtime Refactor

WAVE_ID: W2
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: USER_APPROVED
CHECKPOINT: B

**Phases**:
- **W2.1** - Add SearXNG-backed provider-neutral retrieval module | ~3K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W2.2** - Rewire `CompanyBriefEngine`, `RoleProfileEngine`, and reranker typing | ~3K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W2.3** - Keep `tavily_retrieval.py` as a compatibility wrapper only | ~2K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Acceptance**:
- Active retrieval path reads `SEARXNG_BASE_URL`.
- Empty query, missing config, HTTP failure, malformed result, and disabled JSON output fail explicitly or degrade through existing app behavior.
- No active runtime path imports the Tavily SDK or `tools.retrieval.tavily_client`.

---

## Wave 3 - Verification And PR

WAVE_ID: W3
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: USER_APPROVED
CHECKPOINT: C

**Phases**:
- **W3.1** - Update offline/live tests, env example, SLO/RUNBOOK wording | ~3K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W3.2** - Run scoped verification, commit, push, and draft PR | ~3K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Acceptance**:
- Scoped pytest selectors pass or failures are documented with RCA.
- Branch is pushed.
- PR draft contains implementation summary, verification output, and SearXNG configuration notes.

---

## Execution Details

### W2.1 - SearXNG Retrieval Adapter
**Scope**: Create a provider-neutral app-layer retrieval module using `requests.get` with bounded timeout and SearXNG `/search` JSON normalization.

**Commands**:
```bash
pytest tests/apps_research/integrations/test_search_retrieval.py
```

### W2.2 - Runtime Rewiring
**Scope**: Update active app consumers to import provider-neutral retrieval.

**Commands**:
```bash
pytest tests/apps_research/engines/test_company_brief_engine.py tests/apps_research/engines/test_role_profile_engine.py
```

### W3.2 - Verification
**Scope**: Run scoped integration/unit tests, readiness, git diff review, commit, push, and draft PR.

**Commands**:
```bash
pytest tests/apps_research/integrations/test_search_retrieval.py tests/apps_research/integrations/test_reranker_adapter.py tests/apps_research/engines/test_company_brief_engine.py tests/apps_research/engines/test_role_profile_engine.py
pytest tests/unit/apps_research/engines/test_company_brief_engine.py
python scripts/governance/codex_readiness.py --json
```

---

## Gap Register

**GAP-1: Live SearXNG instance availability**
- Details: The repo can validate adapter behavior with mocked HTTP responses, but live retrieval requires an operator-provided SearXNG instance with JSON output enabled.
- Impact: Live E2E remains opt-in and skipped without `SEARXNG_BASE_URL`.

**GAP-2: Historical Tavily names in contracts**
- Details: Some core/app ingress fields and historical docs use `auto_research_tavily`.
- Impact: They remain compatibility names in this plan to avoid changing `agentic_core` or apps_rg API contracts.

---

## Definition of Done

DoD-1: SearXNG primary retrieval adapter exists and is tested.
- Evidence: `pytest tests/apps_research/integrations/test_search_retrieval.py`
- Status: DONE

DoD-2: Active app runtime no longer imports Tavily SDK/direct client.
- Evidence: `rg -n "from tavily|import tavily|tools\\.retrieval\\.tavily_client" apps_research tests`
- Status: DONE

DoD-3: Existing app-layer retrieval consumers still pass scoped tests.
- Evidence: `pytest tests/apps_research/integrations/test_reranker_adapter.py tests/apps_research/engines/test_company_brief_engine.py tests/apps_research/engines/test_role_profile_engine.py`
- Status: DONE

DoD-4: Offline behavior remains green when live provider env is absent.
- Evidence: `pytest tests/unit/apps_research/engines/test_company_brief_engine.py`
- Status: DONE

DoD-5: PR is drafted with verification evidence and SearXNG configuration notes.
- Evidence: GitHub draft PR URL
- Status: DONE

---

## Scope Expansion Authorization

| Decision | When | Continues? |
|---|---|---|
| ACCEPTED | In-charter app-layer provider seam changes | Yes |
| DEFERRED | Dormant MCP/governance Tavily wording cleanup | Yes |
| SPLIT_TO_NEW_PLAN | Core contract renames or apps_rg API flag renames | Yes |
| REJECTED | Historical archive literal cleanup | Yes |

---

## Supersedes

_None - net-new plan._
