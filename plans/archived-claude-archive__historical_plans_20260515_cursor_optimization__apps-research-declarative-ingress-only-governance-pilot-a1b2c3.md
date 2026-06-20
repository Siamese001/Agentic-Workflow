---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\historical_plans_20260515_cursor_optimization\\apps-research-declarative-ingress-only-governance-pilot-a1b2c3.md'
original_relative_path: '_archive\\historical_plans_20260515_cursor_optimization\\apps-research-declarative-ingress-only-governance-pilot-a1b2c3.md'
source_sha256: d0e008c82705cd5f31fe85a23773c3b8aa35d22d28dab8b0f5ef2690329feb4d
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# apps_research — Declarative Ingress-Only Governance (DS-4 Pilot)

**Slug:** `apps-research-declarative-ingress-only-governance-pilot-a1b2c3`
**Status:** ⛔ **DEFERRED / PILOT ONLY** (DS-4 activation)
**Tier:** T3 — cross-layer, multi-file, architectural, governance
**Parent:** `apps-rg-declarative-ingress-deferred-scope-a9f2e3` (DS-4)
**Priority:** P1 (highest risk among sibling apps per ADG analysis)
**Created:** 2026-05-09

---

## ⛔ PILOT SCOPE ONLY

This plan is a **PILOT IMPLEMENTATION** for DS-4 (Sibling App Governance Replication).
It covers only `apps_research` — the highest-risk sibling app per ADG hotspot analysis.

The remaining 7 apps are **NOT in scope** for this pilot:
- `apps_underwriting_ai` (P2)
- `apps_lic` (P3)
- `apps_qna` (P4)
- `apps_rfp` (P5)
- `apps_architect` (P6)
- `apps_eval` (P7)
- `apps_repo_brief` (P8)

---

## §1. apps_research Risk Analysis (ADG Hotspot)

**Current Runtime Authority in apps_research:**

| Component | Runtime Type | Risk | Current Implementation |
|-----------|-------------|------|----------------------|
| `company_brief_engine.py` | L2 executor (direct Qwen vLLM call) | **CRITICAL** | Calls `requests.post()` to local vLLM endpoint |
| `engines/base_research_engine.py` | L1-L2 hybrid | HIGH | Orchestrates research flow |
| `airlocks/research_query.py` | C0 retrieval wrapper | MEDIUM | Currently inert stub |

**ADG Violations Identified:**

```
apps_research/engines/company_brief_engine.py
  → flows_to: Qwen vLLM direct (bypasses SovereignLLMGateway)
  → emits_side_effect: HTTP POST to localhost:8000
  → layer: L2_execution (misplaced in apps_*)
```

---

## §2. Governance Transformation

**Target State (Declarative Ingress-Only):**

| Aspect | Current | Target |
|--------|---------|--------|
| Entry | `python -m apps_research` | `python -m apps_research` (unchanged) |
| Input | CLI args + interactive | CLI + `ResearchIngressPayload` |
| Processing | `company_brief_engine.py` (local) | Submit to `AppIngressRunner` |
| Execution | Direct vLLM call | Core L2 `SovereignLLMGateway` |
| Output | Print/JSON file | Exit-approved `ResearchOutputContract` |

**Files to Quarantine (Runtime Authority):**

```
apps_research/engines/company_brief_engine.py → QUARANTINE
apps_research/engines/base_research_engine.py → QUARANTINE
apps_research/integrations/llm_client.py → QUARANTINE (if exists)
apps_research/adapters/*.py → QUARANTINE (any runtime adapters)
```

**New Declarative Profiles:**

```yaml
# apps_research/profiles/research_planning_profile.yaml
schema_version: "1.0"
research_depth: "standard"  # or "deep", "quick"
company_sources: ["tavily", "manual_brief"]
output_format: "structured_brief"
```

---

## §3. Wave Structure (Pilot)

| Wave | Phase | Focus | Est. Tokens |
|------|-------|-------|-------------|
| W1 | P1-P2 | ADG baseline + quarantine scope | ~3k |
| W2 | P1-P3 | Authority contracts (ResearchIngressPayload, etc.) | ~4k |
| W3 | P1-P4 | Declarative profiles (YAML pack) | ~2k |
| W4 | P1-P4 | Quarantine runtime files | ~4k |
| W5 | P1-P3 | Ingress-only __main__.py rewrite | ~3k |
| W6 | P1-P3 | Core consumption (SovereignLLMGateway wiring) | ~5k |
| W7 | P1-P2 | L7 auditability | ~2k |
| W8 | P1-P4 | CI gates + mutation guards | ~4k |
| W9 | P1-P2 | Evidence bundle | ~2k |

**Total:** ~29k tokens (pilot scope: 1 app only)

---

## §4. Activation Requirements

Before this pilot can proceed:

1. ✅ **W8 gates PASS** on parent `apps_rg` (verified)
2. ⬜ **AG-10 decision** for pilot authorization (score ≥0.85, gap ≥0.12)
3. ⬜ **ADG preflight** run for `apps_research` specifically
4. ⬜ **User explicit authorization** for P1 app pilot
5. ⬜ **CI gate extension** for `apps_research` forbidden patterns

---

## §5. Non-Goals (Explicitly Out of Pilot Scope)

| Item | Reason | Future Work |
|------|--------|-------------|
| Other 7 apps | Pilot scope limited to 1 app | Separate plans per app |
| Real vLLM removal | Deferred to core wiring | DS-1 Gemini pattern |
| C0 FEC producer | Separate BLOCKER #4 plan | `apps_qna` pattern |
| Multi-step research workflow | Requires DS-2 L3 MANAGED_WORKFLOW | Post-pilot |
| Cross-app research (research → rg) | Requires both apps governed | Post both pilots |

---

## §6. Implementation Status

**Current Status:** ⛔ **NOT STARTED** — awaiting activation

**Next Action:** User authorization + AG-10 decision to proceed with W1

**Estimated Completion:** 3-4 sessions (29k tokens)

---

## §7. Parent Plan Linkage

This plan is **child of** `apps-rg-declarative-ingress-deferred-scope-a9f2e3` (DS-4).
When this pilot completes:
- DS-4 item "Sibling app governance replication" updates to "1 of 8 complete"
- Remaining 7 apps remain deferred with updated priority list

---

**Plan File:** `.windsurf/plans/apps-research-declarative-ingress-only-governance-pilot-a1b2c3.md`
**Notion Registration:** PENDING (registered on activation)
