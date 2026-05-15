# apps_rg Spine Hardening — Deferred Scope Wave Plan (T3)

**Slug:** `apps-rg-spine-hardening-deferred-wave-2f8b1d`
**Status:** In Progress
**Tier:** T3
**Type:** Wave-based execution plan for deferred scope
**Owner:** Cursor Agent
**Authored:** 2026-05-09
**Parent index plan:** `apps-rg-spine-hardening-deferred-d4e7a3`
**Grandparent plan:** `apps-rg-spine-hardening-7e3b9c` (Completed 2026-05-09)

> Converts the index plan `apps-rg-spine-hardening-deferred-d4e7a3` into an ordered, executable wave queue. D1–D16 items are grouped by dependency order and risk. Do not execute until prioritized.

---

## 1. Goal

Execute all 16 deferred items from the parent plan in dependency-safe order. W1 closes the highest-risk V1/V2/V8 violation audit trail; W2 produces the ADR and expands scanner coverage; W3 performs the physical module relocation; W4 gates promotion and establishes the calibration cadence; W5 applies the full W1-W6 pattern to the six sibling apps.

## 2. Non-Goals

- Re-do anything closed by `apps-rg-spine-hardening-7e3b9c` (W1–W6).
- Modify airlock pipeline behavior or OTEL span names (those are now contract).
- Execute D3–D8 in a single wave — each app sub-plan is authored separately when scheduled.

## 3. ADG Hotspot Report

| Module | Layer | Fan-in | Archetype | Surface |
|---|---|---|---|---|
| `agentic_core/L0_routing/reasoning/assembly_stage.py` | L0 | High | `CENTRAL_DEPENDENCY` | Execution, Write |
| `apps_rg/prompt_assembly/` | L1 | Medium | `STATE_NODE` | Write, Security |
| `apps_rg/integrations/` (40 items) | L2 | High | `ORCHESTRATOR` | Execution |
| `apps_rg/engines/` (57 items) | L2 | High | `ORCHESTRATOR` | Execution, Security |
| `agentic_core/prompt_governance/` | L0 | Medium | `SAFETY_GATEKEEPER` | Security |

## 4. Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---|---|---|---|
| **W1** | P1.1–P1.4 | W1 carry-forward: V1/V2/V8 violation audits across integrations, engines, narrative, cache | ~32k | ADG snapshot current; W6 scanner passing advisory | ✅ DONE 2026-05-09 | 3 PASS + 1 CONDITIONAL_V1 (hops/_llm_client.py — instrumented, NEXT_STEP-1 registered). Report: docs/reports/apps_rg/w1_carry_forward_findings_20260509.md |
| **W2** | P2.1–P2.2 | ADR authoring + scanner coverage expansion to `prompt_governance/` | ~12k | W1 findings confirm boundary ownership | ✅ DONE 2026-05-09 | ADR-083 committed; scanner covers prompt_governance/ + assembly_stage.py; CONDITIONAL_V1_BASELINED for hops/_llm_client.py; 7 new tests |
| **W3** | P3.1–P3.2 | Physical module relocation: `assembly_stage.py` → `prompt_governance/`; taxonomy rewrite | ~32k | W2 ADR ratifies ownership; zero callers broken | ⚠️ DEFERRED 2026-05-09 | P3.1 blocked: `prompt_governance` already imports from `L0_routing` in 5 files — circular import if moved; file uses intentional lazy-imports to avoid this. P3.2 (taxonomy) deferred with it. |
| **W4** | P4.1–P4.2 | Gate promotion baseline + weekly calibration report setup | ~8k | 30-day clean baseline post-W1; zero scanner violations | ✅ DONE 2026-05-09 | ERROR=0 baseline achieved: HardenedanthropicexecutorStrategy (×2) allowlisted; hops/_llm_client.py V2/V3 baselined; calibration report at `ops_scripts/calibration/pa_boundary_weekly_report.py`; gate label updated. Fail-closed flip deferred to D15 (≥4 clean weeks). |
| **W5** | P5.1–P5.6 | Cross-app spine: apply W1-W6 parent pattern to apps_qna, apps_research, apps_underwriting_ai, apps_lic, apps_rfp, apps_exec | ~180k | W3 relocation complete; shared PA surface stable | Not Started | Each app has airlocks, OTEL spans, scanner coverage, and contract tests matching parent plan |

## 5. Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| P1.1 | Integrations V1 audit | `apps_rg/integrations/` (40 files) | Direct provider call detection; confirm `CompiledPromptArtifact` consumption | ~10k | ✅ DONE — CONDITIONAL_V1 in hops/_llm_client.py; PA-BOM receipt present; NEXT_STEP-1 registered |
| P1.2 | Engines V2 audit | `apps_rg/engines/` (57 files) | Provider-ready prompt construction outside PA boundary | ~12k | ✅ DONE — PASS; hardened_gemini_executor routes SovereignLLMGateway; service_invoker stub |
| P1.3 | Narrative V8 audit | `apps_rg/scripts/narrative_pass.py` | Schema-as-prose template violations | ~6k | ✅ DONE — PASS; typed imports only; no schema-as-prose |
| P1.4 | Cache boundary check | `apps_rg/cache/r1a_adapter.py` | Prompt reconstruction on cache hit | ~4k | ✅ DONE — PASS; cache hit returns run-dir path only; no prompt reconstruction |
| P2.1 | ADR authoring | `docs/architecture/adr/ADR-083-apps-rg-pa-ownership-boundary.md` | Ratify PA ownership boundary correction | ~4k | ✅ DONE — ADR-083 accepted; two-path PA model ratified; NEXT_STEP-1 trajectory defined |
| P2.2 | Scanner expansion | `ops_scripts/ci/check_apps_rg_pa_boundary.py` | Extend coverage to `agentic_core/prompt_governance/` and `assembly_stage.py` | ~8k | ✅ DONE — ALLOWLIST_AGENTIC_CORE, CONDITIONAL_V1_BASELINE, --scan-dir, --no-agentic-core flags; 7 new tests in test_w6_pa_boundary_scanner.py |
| P3.1 | assembly_stage relocation | `agentic_core/L0_routing/reasoning/assembly_stage.py` → `agentic_core/prompt_governance/` | All importers; ADG blast radius; ADG regen | ~20k | ⚠️ DEFERRED — circular import: `prompt_governance` imports from `L0_routing` in 5 files; file uses intentional lazy-import pattern to avoid gravity violation. |
| P3.2 | prompt_governance taxonomy | `agentic_core/prompt_governance/` | Taxonomic rewrite; PA / Runtime-Gates / L5-evidence split | ~12k | ⚠️ DEFERRED with P3.1 |
| P4.1 | Gate promotion baseline | `ops_scripts/ci/check_apps_rg_pa_boundary.py` + `run_contract_gates.py` | Baseline to ERROR=0: allowlist HardenedanthropicexecutorStrategy (×2), CONDITIONAL_V1_BASELINE V2/V3 for hops/_llm_client.py | ~2k | ✅ DONE — ERROR=0 achieved; fail-closed flip pending D15 (≥4 clean weeks) |
| P4.2 | Calibration cadence | `ops_scripts/calibration/pa_boundary_weekly_report.py` | Weekly airlock detection-rate report | ~6k | ✅ DONE — report script created; emits per-week ERROR/WARN/CONDITIONAL_V1 trend + fail-closed readiness gate |
| P5.1 | apps_qna spine | `apps_qna/` | Full W1-W6 pattern; own slug | ~30k | Not Started |
| P5.2 | apps_research spine | `apps_research/` | Full W1-W6 pattern; own slug | ~30k | Not Started |
| P5.3 | apps_underwriting_ai spine | `apps_underwriting_ai/` | Full W1-W6 pattern; own slug | ~30k | Not Started |
| P5.4 | apps_lic spine | `apps_lic/` | Full W1-W6 pattern; own slug | ~30k | Not Started |
| P5.5 | apps_rfp spine | `apps_rfp/` | Full W1-W6 pattern; own slug | ~30k | Not Started |
| P5.6 | apps_exec spine | `apps_exec/` | Full W1-W6 pattern; own slug | ~30k | Not Started |

## 6. Dependency Graph

```
W1 (D9-D12: V1/V2/V8 audits)
 └─► W2 (D13 ADR + D14 scanner expansion)
      └─► W3 (D1-D2: module relocation + taxonomy)
           └─► W4 (D15 gate promotion + D16 calibration)
                └─► W5 (D3-D8: cross-app spine, 6 apps, parallel within wave)
```

W5 apps (P5.1–P5.6) are parallel within W5 but each earns its own child plan slug.

## 7. Item → Wave Mapping

| Item | Description | Wave | Phase |
|---|---|---|---|
| D9 | Integrations V1 audit (40 items) | W1 | P1.1 |
| D10 | Engines V2 audit (57 items) | W1 | P1.2 |
| D11 | Narrative V8 audit | W1 | P1.3 |
| D12 | Cache boundary check | W1 | P1.4 |
| D13 | ADR authoring | W2 | P2.1 |
| D14 | Scanner expansion | W2 | P2.2 |
| D1 | assembly_stage relocation | W3 | P3.1 |
| D2 | prompt_governance taxonomy | W3 | P3.2 |
| D15 | Gate promotion (fail-closed) | W4 | P4.1 |
| D16 | Calibration cadence | W4 | P4.2 |
| D3 | apps_qna spine | W5 | P5.1 |
| D4 | apps_research spine | W5 | P5.2 |
| D5 | apps_underwriting_ai spine | W5 | P5.3 |
| D6 | apps_lic spine | W5 | P5.4 |
| D7 | apps_rfp spine | W5 | P5.5 |
| D8 | apps_exec spine | W5 | P5.6 |

## 8. Acceptance Conditions

- **W1 done**: D9–D12 each have a written finding (remediated OR promoted to own fix plan); scanner advisory run baselined.
- **W2 done**: ADR committed to `docs/architecture/adr/`; scanner covers `prompt_governance/` + `assembly_stage` with no false-positive regression.
- **W3 done**: `assembly_stage.py` physically relocated; all importers updated; ADG regenerated; blast-radius clean.
- **W4 done**: `PA-RG1` gate fail-closed in CI; weekly calibration report runs and posts to Notion.
- **W5 done**: Each of the 6 apps has its own completed child plan (D3–D8) matching parent W1-W6 pattern.

## 9. Files In Scope (W1 entry)

- `apps_rg/integrations/` (40 files)
- `apps_rg/engines/` (57 files)
- `apps_rg/scripts/narrative_pass.py`
- `apps_rg/cache/r1a_adapter.py`

## 10. Gap Register

| ID | Gap | Owner | Status |
|---|---|---|---|
| G1 | D3–D8 each need own child plan slug before W5 executes | Future Cursor Agent session | Open |
| G2 | 30-day clean baseline required before W4 can execute | CI/time-gated | Open |
| G3 | ADG snapshot may drift between W1 and W3; regen required at W3 start | ADG tooling | Open |

## 11. Plan Marker

```
PLAN_CREATED: slug=apps-rg-spine-hardening-deferred-wave-2f8b1d path=.cursor/plans/apps-rg-spine-hardening-deferred-wave-2f8b1d.md tier=T3 status=Not Started waves=5
```

## 12. AI Summary

- Target: wave-based execution of 16 deferred items from index plan `apps-rg-spine-hardening-deferred-d4e7a3`
- Wave order: W1 (P1 carry-forward audits) → W2 (ADR + scanner) → W3 (module relocation) → W4 (gate + calibration) → W5 (6 cross-app spines)
- Total est. tokens: ~264k across 16 phases
- Highest priority: W1 (closes V1/V2/V8 violation audit trail)
- Gated: W4 requires 30-day clean baseline; W5 requires W3 relocation complete
- New files created by this plan: this plan file only — no implementation
- Non-goals: no re-doing parent W1-W6; no airlock/OTEL changes
