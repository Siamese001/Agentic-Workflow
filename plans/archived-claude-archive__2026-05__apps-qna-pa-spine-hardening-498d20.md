---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\2026-05\\apps-qna-pa-spine-hardening-498d20.md'
original_relative_path: '_archive\\2026-05\\apps-qna-pa-spine-hardening-498d20.md'
source_sha256: 68213ed146fbda82aacd04fdf1081ee155d1872a2c73338208bbf35cb09fd302
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# apps_qna PA Spine Hardening (T3)

**Slug:** `apps-qna-pa-spine-hardening-498d20`
**Status:** In Progress
**Tier:** T3
**Parent plan:** `apps-rg-spine-hardening-deferred-wave-2f8b1d` W5 P5.1
**Pattern source:** `apps-rg-spine-hardening-7e3b9c` (parent pattern)
**Authored:** 2026-05-09

> Apply the apps_rg W1-W4 spine hardening pattern to apps_qna: PA boundary audit,
> scanner coverage, airlocks, OTEL spans, and contract tests. Pattern-setter child plan for W5.

---

## ADG Provenance

```
ADG Provenance: backend=sqlite+redis, snapshot=adg_indexed_05052026_0722.sqlite
Health: status=ok, mode=full, schema_version=1.0
Nodes: 140743, Edges: 863353
```

## 1. Goal

Establish the same 4 spine-hardening invariants for apps_qna that apps_rg achieved in W1-W4:

1. **PA boundary enforced**: no direct provider construction outside sanctioned shim
2. **Scanner coverage**: `check_apps_rg_pa_boundary.py` extended to scan `apps_qna/` (or dedicated scanner)
3. **Airlocks**: airlock gate functions for the two apps_qna routes (`build_time_compiler` + `R4_SINGLE_ACTION`)
4. **Contract tests**: suite verifying all of the above, matching the `test_w6_pa_boundary_scanner.py` pattern

## 2. Non-Goals

- No changes to apps_qna prompt assembly logic or card templates
- No LLM judge implementations (separate plan)
- No relocation of modules (W3 parent plan is already deferred)
- No C0 FEC producer binding (separate plan)
- No cross-app integration changes

## 3. ADG_HOTSPOT_REPORT

> apps_qna is `L_UNKNOWN` in the ADG (leaf app, expected). Impact ranked by PA-boundary risk.

| Rank | File | Fan-In (imports) | Archetype | Surface | Impact | Notes |
|---|---|---|---|---|---|---|
| 1 | `apps_qna/integrations/provider_adapter.py` | ADG not resolved | **ORCHESTRATOR** | Execution + Egress | HIGH | 35 Anthropic/OpenAI matches — primary provider bridge |
| 2 | `apps_qna/engines/dispatch/provider_dispatch.py` | ADG not resolved | **ORCHESTRATOR** | Execution | HIGH | 27 matches — engine-level LLM dispatch |
| 3 | `apps_qna/integrations/intent_classifier.py` | ADG not resolved | **CENTRAL_DEPENDENCY** | Execution | MEDIUM | 17 matches — classifier calls LLM |
| 4 | `apps_qna/engines/judges/interview_card_quality_judge.py` | ADG not resolved | **SAFETY_GATEKEEPER** | Security | MEDIUM | 16 matches — LLM judge |
| 5 | `apps_qna/integrations/llm_client.py` | 0 (leaf) | **CENTRAL_DEPENDENCY** | Execution | LOW (SANCTIONED) | Sanctioned shim → `infrastructure/sdks_mcps`; NOT a violation |

**Key difference from apps_rg:** `apps_qna/integrations/llm_client.py` is a **sanctioned shim** (routes through `infrastructure/sdks_mcps`). Files importing from it are not violations. Files that construct `Anthropic()`/`OpenAI()` directly (bypassing the shim) ARE violations.

## 4. ADG_GRAPH_LAYER_EVIDENCE

| MV / Evidence | Finding |
|---|---|
| `mv_hotspot_centrality` | apps_qna files not in global top-20 (leaf app, expected) |
| `adg_nodes_by_file(apps_qna/__main__.py)` | fan-in=0 (entrypoint, correct) |
| `adg_edge_fanout(__main__.py, imports)` | 13 edges — imports `apps_shared.spine_emission`, `maybe_invoke_exit_eval`, `apps_shared.cert.resolve_fec` — spine already wired |
| Grep scan | 4 files with direct SDK matches; `llm_client.py` is sanctioned shim; need W1 audit to confirm |

## 5. Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---|---|---|---|
| **W1** | P1.1–P1.3 | V1/V2/V8 violation audit across integrations, engines/dispatch, judges | ~16k | ADG snapshot current; PA scanner available | ✅ DONE | 5 files classified: 1 SANCTIONED (llm_client.py), 1 PASS (provider_adapter early read), 4 CONDITIONAL_V1 |
| **W2** | P2.1 | PA scanner coverage extension to `apps_qna/` | ~6k | W1 audit complete | ✅ DONE | Scanner covers apps_qna/; ERROR=0; allowlist + 4 CONDITIONAL_V1 baseline entries; `--no-apps-qna` flag |
| **W3** | P3.1–P3.2 | Airlocks + OTEL spans for build_time_compiler and R4_SINGLE_ACTION routes | ~12k | W2 scanner clean | ✅ DONE | `apps_qna/airlocks/` with `template_input.py`, `user_question.py`, `_otel_spans.py`, `__init__.py` |
| **W4** | P4.1 | Contract tests + calibration | ~6k | W3 airlocks in place | ✅ DONE | 16 contract tests passing; scanner ERROR=0 WARN=27 (all CONDITIONAL_V1 baselined) |

## 6. Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| P1.1 | Integrations V1/V2 audit | `apps_qna/integrations/` (21 files) | Direct SDK construction vs shim import; confirm `llm_client.py` sanctioned | ~6k | ✅ DONE |
| P1.2 | Engines dispatch V2 audit | `apps_qna/engines/dispatch/provider_dispatch.py` | Provider-ready prompt construction outside PA | ~5k | ✅ DONE |
| P1.3 | Judges V8 audit | `apps_qna/engines/judges/` | LLM judge direct SDK calls | ~5k | ✅ DONE |
| P2.1 | Scanner coverage extension | `ops_scripts/ci/check_apps_rg_pa_boundary.py` | Add `apps_qna/` scan scope; allowlist shim | ~6k | ✅ DONE |
| P3.1 | Airlock gate functions | `apps_qna/airlocks/` (new) | Two routes: build_time_compiler (no-LLM) + R4_SINGLE_ACTION (LLM) | ~8k | ✅ DONE |
| P3.2 | OTEL spans | `apps_qna/airlocks/_otel_spans.py` | Span helper with `apps_qna.airlocks` tracer namespace | ~4k | ✅ DONE |
| P4.1 | Contract tests | `tests/_apps_contract/test_apps_qna_pa_spine.py` | 16 tests covering scanner allowlist, airlocks, OTEL | ~6k | ✅ DONE |

## 7. Dependency Graph

```
W1 (integrations + engines + judges audit)
 └─► W2 (scanner coverage extension)
      └─► W3 (airlocks + OTEL)
           └─► W4 (contract tests)
```

## 8. Key Files

| File | Role | Action |
|---|---|---|
| `apps_qna/integrations/llm_client.py` | Sanctioned shim | Add to `ALLOWLIST_FILES` in scanner |
| `apps_qna/integrations/provider_adapter.py` | Primary provider bridge | W1 audit: confirm routes through shim |
| `apps_qna/engines/dispatch/provider_dispatch.py` | Engine dispatch | W1 audit: confirm routes through shim |
| `apps_qna/integrations/intent_classifier.py` | Classifier | W1 audit: confirm routes through shim |
| `apps_qna/engines/judges/interview_card_quality_judge.py` | LLM judge | W1 audit: shim or direct? |
| `apps_qna/airlocks/` (new) | Airlock gates | W3: create matching apps_lic pattern |
| `tests/_apps_contract/test_apps_qna_pa_spine.py` (new) | Contract tests | W4 |
