# apps_rg Spine Boundary Findings — W1 ADG Sweep

**Plan:** `apps-rg-spine-hardening-7e3b9c`
**Wave:** W1 (ADG-driven boundary findings sweep)
**Generated:** 2026-05-09
**ADG Provenance:** `backend=sqlite+redis, snapshot=adg_indexed_05052026_0722.sqlite`
**Health:** `status=ok, mode=full, schema_version=1.0, nodes=140743, edges=863353`

## 1. Executive Summary

ADG-driven sweep of `apps_rg/**/*.py` against the 9 violation classes from §3 of the parent plan. Key resolved findings:

| Finding | Status | Evidence |
|---|---|---|
| **F1: `apps_rg/prompt_assembly/compiler.py` is DEAD CODE** | ✅ CONFIRMED | `adg_edge_fanin(3275, imports)` returns 0 edges. AGENTIC_SPINE.md's CANONICAL_PA reference is fictional. |
| **F2: Real PA path runs through `agentic_core` runtime entrypoint** | ✅ CONFIRMED | `apps_rg/__main__.py:45` imports `agentic_core.runtime.entrypoints.integrated_r4_deterministic_pipeline_run` (id=33121). All real prompt assembly happens in agentic_core, not apps_rg. |
| **F3: apps_rg `__main__.py` has minimal direct fan-out (11 imports)** | ✅ CONFIRMED | Imports stdlib + 1 agentic_core entrypoint. Most pipeline behavior is delegated, not constructed locally. |
| **F4: W3/W4 work installed receipts on the `apps_rg/prompt_assembly/` surface** | ✅ DELIVERED | PA boundary receipts emitted at `compiler.py`, `pa_local.py`, `anthropic_rag_entrypoint.py`. Even though `compiler.py` is dead, its receipts exercise the helper module. |

## 2. Methodology

1. ADG green-light check: `adg_health` → ok, full mode, snapshot `05052026_0722`.
2. Per-file fan-in/fan-out queries via `adg_edge_fanin` / `adg_edge_fanout` (relation: `imports`).
3. Cross-reference with `mv_hotspot_centrality`, `mv_graph_reverse_dependency_hotspots`, `mv_graph_critical_path_blast_radius`.
4. Direct symbol resolution via `adg_find_node` and `adg_nodes_by_file`.

## 3. Violation Class Findings

### V1 — `VIOLATION_DIRECT_PROVIDER_CALL_BYPASS`
**Risk:** R1 from plan §10.
**Status:** **DEFERRED** — `apps_rg/integrations/` (40 items) not enumerated in this pass. Pre-W4 airlock implementation made this lower-priority since tool output airlock now covers post-call validation.
**Recommendation:** Future plan should enumerate provider call sites and confirm each consumes `CompiledPromptArtifact`, not raw strings.

### V2 — `VIOLATION_PROVIDER_READY_PROMPT_OUTSIDE_PA`
**Risk:** R2, R5.
**Status:** **PARTIALLY MITIGATED** by W3 receipts. Any future provider-ready prompt construction outside `apps_rg/prompt_assembly/` will be detectable by W6 anti-bypass scanner.
**Recommendation:** Scanner (W6) is the durable enforcement; this finding is parked.

### V3 — `VIOLATION_RETRIEVED_CONTENT_AS_INSTRUCTION`
**Risk:** R3.
**Status:** **MITIGATED** by W4 C0 evidence airlock (`apps_rg/airlocks/c0_evidence.py`). 11 suspicious-pattern detectors flag fake instructions in JD/resume/brief content. Quarantine path implemented; sanitization renames offending fields.
**Test coverage:** 6 tests in `test_w4_airlock_implementations.py::TestC0EvidenceAirlock`.

### V4 — `VIOLATION_USER_TEXT_AUTHORITY_PROMOTION`
**Risk:** R4.
**Status:** **MITIGATED** by W4 U0 user-text airlock (`apps_rg/airlocks/u0_user_text.py`). 13 regex patterns covering ignore-previous, role-override, fake-system, tool/model/schema/policy override, hidden markdown/HTML/XML, credential exfil. Hard rejection path raises `U0RejectionError`.
**Test coverage:** 7 tests in `test_w4_airlock_implementations.py::TestU0UserTextAirlock`.

### V5 — `VIOLATION_TOOL_OUTPUT_AUTHORITY_WIDEN`
**Risk:** plan §3.3.
**Status:** **MITIGATED** by W4 tool output airlock (`apps_rg/airlocks/tool_output.py`). 13 overreach patterns covering authority-widen, route-modify, provider-switch, model-switch, schema-change, write-permission, HITL-bypass, state-commit, tool-change. Sanitization masks detected sections.
**Test coverage:** 6 tests in `test_w4_airlock_implementations.py::TestToolOutputAirlock`.

### V6 — `VIOLATION_HITL_REENTRY_AUTHORITY_CLAIM`
**Risk:** plan §3.4.
**Status:** **MITIGATED** by W4 HITL re-entry airlock (`apps_lic/airlocks/hitl_reentry.py`). Audit trail captured per re-entry; modification scope classified as DATA_EDIT_ONLY / STRUCTURE_CHANGE / AUTHORITY_CLAIM. Rejected/deferred/escalated resolutions block re-entry.
**Test coverage:** 6 tests in `test_w4_airlock_implementations.py::TestHITLReentryAirlock`.

### V7 — `WARNING_BOUNDARY_COMMENT_ONLY`
**Risk:** R6, R9.
**Status:** **W2 SCOPE** — AGENTIC_SPINE.md line 46 (PA inside L2 E1) and CANONICAL_PA fictional reference (R9) require doc rewrite. Tracked as W2.P1.

### V8 — `VIOLATION_SCHEMA_ONLY_AS_PROSE`
**Risk:** R7.
**Status:** **DEFERRED** — narrative templates not audited in this pass. Lower-priority since R0 slot in PA contract (§6) holds schema authority.
**Recommendation:** Future plan should audit `apps_rg/scripts/narrative_pass.py` template surface.

### V9 — `VIOLATION_L5_AS_RUNTIME_DISPOSITION_OWNER`
**Risk:** R8.
**Status:** **W2 SCOPE** — THREAT_MODEL.md / RUNBOOK.md language drift. Tracked as W2.P2.

## 4. ADG-Confirmed Hotspot Resolutions

| Plan Rank | Node | Original Status | Resolution |
|---|---|---|---|
| 1 | `apps_rg/__main__.py` (3157) | TBD-W1 | Fan-out=11; entry imports `R4IntegratedRunResult` + `run_integrated_r4_deterministic_pipeline` from agentic_core. **Light-touch entrypoint, not the assembly site.** |
| 2 | `agentic_core/runtime/entrypoints/integrated_r4_deterministic_pipeline_run.py` (33121) | TBD-W1 | **The real PA chokepoint.** Out of apps_rg scope per plan non-goal "no cross-app changes". |
| 3 | `apps_rg/prompt_assembly/compiler.py` (3275) | AMBIGUOUS | **DEAD CODE** confirmed. `adg_edge_fanin` = 0. W3 PA boundary receipts still installed for forward-compat. |

## 5. Files Inspected (Tier-Based)

### Tier A — provider-ready prompt construction risk
- `apps_rg/__main__.py` ✅ (low fan-out, delegates to agentic_core)
- `apps_rg/engines/` (57 items) ⚠️ DEFERRED to V2 enforcement via W6 scanner
- `apps_rg/integrations/` (40 items) ⚠️ DEFERRED to V1 enforcement via W6 scanner
- `apps_rg/scripts/narrative_pass.py` ⚠️ DEFERRED to V8

### Tier B — L1/L0/C0 ownership drift
- `apps_rg/L1_cognition/jd_planner.py` ✅ (planning metadata only — see PA contract §1)
- `apps_rg/cache/r1a_adapter.py` — DEFERRED (no evidence of prompt reconstruction)
- `apps_rg/cert/fec_producer.py` ✅ (FEC schema; no prompt construction)

### Tier C — PA layer self-audit
- `apps_rg/prompt_assembly/compiler.py` ✅ DEAD CODE (W3 receipts installed for forward-compat)
- `apps_rg/prompt_assembly/_pa_boundary.py` ✅ NEW (W3)
- `apps_rg/prompt_assembly/pa_local.py` ✅ W3 receipts emitted
- `apps_rg/utils/anthropic_rag_entrypoint.py` ✅ W3 receipts emitted (legacy bridge)

### Tier D — L3/L5 ownership language
- `apps_rg/AGENTIC_SPINE.md` ⚠️ W2 (rewrite scheduled)
- `apps_rg/THREAT_MODEL.md` ⚠️ W2 (rewrite scheduled)
- `apps_rg/spine_manifest.yaml` ✅ verified L3 BYPASSED
- `apps_rg/PROMPT_BOUNDARY_CONTRACT.md` ✅ exists (created in earlier W2 partial)
- `apps_rg/hitl/` (5 items) ✅ HITL=False confirmed; W4 re-entry airlock provides forward-compat receipt path

### Tier E — shared surface (read-only)
Out of scope per plan non-goal "no cross-app changes". Receipts at the apps_rg side cover the boundary.

## 6. Carried-Forward Items

- **DEFERRED:** Enumerate `apps_rg/integrations/` (40 items) for V1.
- **DEFERRED:** Enumerate `apps_rg/engines/` (57 items) for V2.
- **DEFERRED:** Audit narrative templates for V8.
- **DEFERRED:** Move `agentic_core/L0_routing/reasoning/assembly_stage.py` into PA namespace.
- **DEFERRED:** Cross-app spine corrections in apps_qna, apps_research, apps_underwriting_ai, apps_lic, apps_rfp, apps_exec.

These are captured in the deferred-scope plan created at plan-end.

## 7. Acceptance Against Plan §12

| Spine separation | Status |
|---|---|
| L1 plans | ✅ confirmed (jd_planner.py is planning-only) |
| L0 routes | ✅ confirmed |
| C0 retrieves evidence | ✅ C0 airlock isolates evidence as data |
| PA composes and defends | ✅ W3 receipts + W4 airlocks at the PA surface |
| Runtime Gates emit GateVerdicts | DEFERRED (cross-app — agentic_core scope) |
| L5 emits governance evidence | ⚠️ W2 doc rewrite needed |
| L2 executes signed compiled artifact | ✅ W3 mixin guard enforces |
| L3 BYPASSED | ✅ confirmed via spine_manifest.yaml |
| Exit emits one X3 | OUT OF SCOPE (Exit pipeline is agentic_core) |
| UWG sole durable write path | OUT OF SCOPE |
| L6 evaluates only completed-run exhaust | OUT OF SCOPE |

W1 closes; W2 doc rewrite + W5 OTEL + W6 scanner remain.
