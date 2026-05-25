> **Superseded 2026-05-24:** apps_lic requires full rebaseline against [apps-rg-spine-only-unification-d8f4a2.md](apps-rg-spine-only-unification-d8f4a2.md). Notion Plans rows retired; do not execute pre-rebaseline scope.

---
plan_id: apps-lic-spine-product-convergence-b7e4a2
plan_type: refactor
status: Superseded (pending apps_lic rebaseline)
parent_plan: apps-lic-u0-boundary-alignment-4f1d9c
authored_at: 2026-05-20
dod_exempt: false
---

# apps_lic Spine Product Convergence

Converge `apps_lic` production entry on the **AG-8 golden spine** (U0→L1→L0→C0→PA→L3 managed→L2 HOP→Exit), retire the **`R4_SINGLE_ACTION` CLI shortcut**, migrate bindings to **`apps_lic/runtime/bindings/`**, and add an **`outreach_message` proof lane** (exec-summary artifact pattern only — not résumé section logic).

> **Governance:** [agentic-core-static-apps-customization](.cursor/plans/_archive/2026-05/apps-rg-golden-state-section-generation-a4f9e1.md) · Boundary law: [apps-lic-u0-boundary-alignment-4f1d9c](.windsurf/plans/apps-lic-u0-boundary-alignment-4f1d9c.md) · AG-8 baseline: [apps-lic-ag8-golden-template-adoption-f3c2e1](.cursor/plans/_archive/2026-05/apps-lic-ag8-golden-template-adoption-f3c2e1.md) (W0–W10 ✅)

---

## Context (SCQA)

- **Situation** — AG-8 wired the contract chain (`test_ag8_apps_lic_golden_path.py`, CI gate). L0 profile defines **R4 / R3R4 / R5** with **L3 managed workflow** and **`apps_research`** when briefing is missing. `apps_rg` exec summary proves a **section proof sandwich** (evidence → PA → L2 → X2 → X1D → X3) but is **not** the integrated spine.
- **Complication** — Production CLI uses [`integrated_r4_lic_pipeline_run.py`](../agentic_core/runtime/entrypoints/integrated_r4_lic_pipeline_run.py) (`R4_SINGLE_ACTION`, C0 bypass, generic `check_route_gates`, static L2 DAG). Ten bindings remain in `agentic_core`. HOP5 does not consume spine `CompiledPromptArtifact`. Two mental models: **contract spine** vs **R4 shortcut**.
- **Question** — How does `apps_lic` reach one product path that matches L0 routing (R1A policy, R3R4+research, managed L3) without a full rewrite?
- **Answer** — Five waves: baseline → bindings migration → canonical dispatch + CLI → HOP/PA convergence → proof lane + CI closeout.

---

## Target Architecture

```text
U0 (ingress + reflection + runtime_customization_package)
  → L1 (L1PlanContract from app_payload)
  → L0 (R4_MANAGED_DRAFT | R3R4_MANAGED_RESEARCH_THEN_DRAFT | R5_FALLBACK)
  → [R1A support-only cache; R1B bypass final drafts per profile]
  → C0 (inline FEC when grounding_required)
  → PA (CompiledPromptArtifact when model_generation_required)
  → L3 (managed_workflow; R3R4 → AppsResearchBridge → manifest)
  → L2 (HopPipelineExecutor / 9 HOP — single bounded packet)
  → Exit (one X3) → [optional outreach_message proof lane artifacts]
```

**Not the template:** `apps_rg` executive_summary lane (SRFS, claim ledger, section-only qwen slice).

**Borrow from exec summary:** artifact layout under `artifacts/apps_lic/runtime_proofs/outreach_message/`.

---

## Hard Laws

| Law | Rule |
|-----|------|
| BL-1 | No new app-specific logic in `agentic_core` except ≤30-line re-export shims |
| BL-2 | U0 is the only spine entry; no L1/L0/L2 bypass without validated package |
| BL-3 | Exit emits exactly one X3; apps_lic never emits X3 directly |
| BL-4 | `apps_research` only via `AppsResearchBridge` on R3R4; support-only |
| BL-5 | R1A/R1B: final outreach drafts bypass cache per [`final_draft_cache_policy.outreach_message.v1.json`](../apps_lic/config/domain_contract/final_draft_cache_policy.outreach_message.v1.json) |
| BL-6 | Do not weaken AG-8 tests or apps_rg golden-path receipts |
| BL-7 | UNKNOWN is never PASS; production proof requires command output |

---

## apps_rg Exec Summary vs apps_lic Target (reference)

| Dimension | apps_rg exec summary | apps_lic target |
|-----------|---------------------|-----------------|
| Spine | Lane slice only | Full spine |
| L0 | N/A | R4 \| R3R4 \| R5 |
| L3 / research | N/A | Managed + `apps_research` on R3R4 |
| C0 | Proof pool / C03 shim | `c0_retrieve_apps_lic` (inline FEC) |
| PA | Section compile | `pa_compose_apps_lic` |
| L2 | Direct qwen slice | 9× HOP via `l2_execute_apps_lic` |
| R1B | Whole-run (apps_rg product) | Bypass final draft; not wired for LIC |

---

## Wave Structure

| Wave | Focus | Status |
|------|-------|--------|
| W0 | Baseline + gap receipt | ✅ Completed |
| W1 | `apps_lic/runtime/bindings/` migration | ✅ Completed |
| W2 | Canonical dispatch + CLI spine entry | ✅ Completed |
| W3 | R3R4 / `apps_research` + L0 routing on CLI | ✅ Completed |
| W4 | HOP ↔ PA/C0 consumption | ✅ Completed |
| W5 | `outreach_message` proof lane + CI + closeout | ✅ Completed |
| R-W1 | Release blocker: `EvidenceShaper` + evidence translation | ✅ Completed (2026-05-20) |
| R-W2 | Release blocker: R3R4 fail-closed | ✅ Completed (2026-05-20) |
| R-W3 | Release blocker: live R3R4 proof (no mock) | ✅ Completed (2026-05-20) |

**Release eligibility:** `RELEASE_ELIGIBLE` — see [release_eligibility_verification_receipt.md](../docs/reports/apps_lic/release_eligibility_verification_receipt.md) and [r3r4_release_blocker_waves_closeout_receipt.md](../docs/reports/apps_lic/r3r4_release_blocker_waves_closeout_receipt.md).

---

## W0 — Baseline Verification

**Goal:** Prove AG-8 green before edits; document CLI vs contract gap.

**Commands:**

```bash
python -m pytest tests/_apps_contract/test_ag8_apps_lic_golden_path.py -q
python ops_scripts/ci/check_apps_lic_golden_path_runtime.py --fail-closed
python -m pytest tests/apps_lic/test_w3_apps_lic_u0.py tests/apps_lic/test_w5_apps_lic_c0_pa.py -q
```

**Produce:**

- `artifacts/apps_lic/spine_convergence/w0_baseline_gap.json` — fields:
  - `cli_path`: `integrated_r4_lic_pipeline` / `R4_SINGLE_ACTION`
  - `contract_path`: AG-8 binding chain
  - `bindings_in_core`: list of 10 shim files
  - `u0_blocker`: Bundle-C envelope vs raw JSON (from `__main__.py` comment)

**Acceptance:** All three command groups exit 0. Gap JSON committed.

---

## W1 — App-Owned Bindings (`apps_lic/runtime/bindings/`)

**Goal:** Mirror [`apps_rg/runtime/bindings/`](../apps_rg/runtime/bindings/); reduce each core `apps_lic_*_binding.py` to re-export shim.

| Move from `agentic_core` | To `apps_lic/runtime/bindings/` |
|--------------------------|----------------------------------|
| `runtime/entry/u0_apps_lic_binding.py` + `runtime/u0/apps_lic_u0_adapter.py` | `u0_binding.py` (adapter + validate) |
| `L0_routing/apps_lic_l0_binding.py` | `l0_binding.py` |
| `L1_cognition/apps_lic_l1_binding.py` | `l1_binding.py` |
| `runtime/c0/apps_lic_c0_binding.py` | `c0_binding.py` |
| `prompt_governance/apps_lic_pa_binding.py` | `pa_binding.py` |
| `L2_execution/apps_lic_l2_binding.py` | `l2_binding.py` |
| `L3_orchestration/apps_lic_l3_binding.py` | `l3_binding.py` |
| `runtime/exit/apps_lic_exit_binding.py` | `exit_binding.py` |
| `L6_observability/promotion/apps_lic_promo_binding.py` | `l6_binding.py` |

**Also:**

- Update [`profile_builder_adapter.py`](../apps_lic/runtime/profile_builder_adapter.py) imports to app-owned paths.
- Fix G-06: core L2 must not `from apps_lic.config.hop_pipeline import REGISTRY` — registry loaded via app binding only.

**Tests:**

```bash
python -m pytest tests/_apps_contract/test_ag8_apps_lic_golden_path.py -q
python -m pytest tests/apps_lic/test_w4_apps_lic_l1_l0.py tests/apps_lic/test_w5_apps_lic_c0_pa.py -q
```

**Acceptance:** Each core shim ≤30 lines, docstring contains `re-export shim`. AG-8 tests pass. No new `from apps_lic` in non-shim core files (except allowlist in boundary plan).

**Deferred to enabling plans (if blocked):** taxonomy registry API, HITL protocol injection, L4 touch-state schema move — per [apps-lic-u0-boundary-alignment-4f1d9c](.windsurf/plans/apps-lic-u0-boundary-alignment-4f1d9c.md) §Generic Interface Dependency Order.

---

## W2 — Canonical Dispatch + U0 Bridge

**Goal:** Single app-owned orchestrator; fix U0 signature mismatch (`Bundle-C-apps_lic-u0-signature-mismatch`).

**Create:**

- `apps_lic/runtime/dispatch/canonical_dispatch.py` — sequences:
  - `u0_validate` → `l1_plan` → `l0_route` → `c0_retrieve` (if `grounding_required`) → `pa_compose` (if `model_generation_required`) → `l3_orchestrate` (if `l3_required`) → `l2_execute` → `exit_finalize`
- `apps_lic/runtime/dispatch/spine_run_result.py` — typed result (run_id, route_family, x3, artifact_dir, `terminal_r5`)

**U0 bridge (pick one, document in receipt):**

| Option | Approach |
|--------|----------|
| A (preferred) | `__main__` builds `AppsLicIngressContractV1` dict → `apps_lic_u0_adapt` → `ValidatedRequest` |
| B | Extend shim so `AppIngressRunner` + envelope path both land on same adapter |

**Retire as default:** `run_integrated_r4_lic_pipeline` from [`__main__.py`](../apps_lic/__main__.py) — keep module for harness-only with `APPS_LIC_ALLOW_LEGACY_R4=1` env guard until W5.

**Update:** [`config/profiles/apps_lic/pipeline_defaults.yaml`](../config/profiles/apps_lic/pipeline_defaults.yaml) — `route_constants` must reflect L0 families, not `R4_SINGLE_ACTION`.

**Acceptance:**

```bash
python -m apps_lic --recipient-class executive --channel email --outreach-mode cold --manual-brief apps_lic/scripts/truist_pascal_brief.json
# Expect route_family R4_MANAGED_DRAFT in manifest; no c0_bypass-only receipt as sole grounding proof
```

---

## W3 — L0 Routing + R3R4 + apps_research on Product Path

**Goal:** CLI `auto` briefing and missing brief trigger **R3R4** and [`managed_workflow_dispatcher.py`](../apps_lic/integrations/managed_workflow_dispatcher.py).

**Wire:**

1. After L0, if `route_family == R3R4_MANAGED_RESEARCH_THEN_DRAFT`:
   - Build `RequestForBriefing` from `ValidatedRequest.app_payload`
   - Call `ManagedWorkflowDispatcher` → `AppsResearchBridge.fetch`
   - On success: merge `PreloadedOutreachContextManifest` into context for L3/L2
   - On failure: R5 terminal → Exit (existing reason codes)
2. If `manual_brief` / fresh context: `R4_MANAGED_DRAFT` — skip bridge
3. L3 binding must emit `L3StepContract` before L2 (already in AG-8 tests — ensure dispatch calls it)

**Tests:**

```bash
python -m pytest tests/apps_lic/test_w4_research_bridge.py tests/_apps_contract/test_ag8_apps_lic_golden_path.py -k "r3r4 or research or route" -q
```

**Acceptance:** Integration test with mocked `AppsResearchBridge` proves R3R4 path; live research test optional (`BLOCKED` without provider).

---

## W4 — HOP ↔ Spine PA/C0 Convergence

**Goal:** Close split where PA/FEC are proven but HOP5 uses local templates only.

**Choose one (Author-Gate at implementation if both remain viable):**

| ID | Approach | Trade-off |
|----|----------|-----------|
| H1 | HOP5 reads `CompiledPromptArtifact.messages` + FEC evidence bundle when present | Single prompt authority; more HOP churn |
| H2 | PA remains receipt-only; add `outreach_message_compose.py` called from L2 pre-HOP | Smaller HOP change; duplicate compose surface |

**Minimum for W4 done:**

- L2 context passes full FEC + PA ref (not digest-only) into HOP entry
- HOP2 `research_engine` does not duplicate spine C0 when FEC already populated (guard flag)
- Document in `apps_lic/runtime/RUNBOOK.md` which path owns generation authority

**Tests:**

```bash
python -m pytest tests/_apps_contract/test_ag8_apps_lic_golden_path.py -k "l2 or pa or c0" -q
python -m pytest tests/apps_lic/test_w6_e2e_pipeline.py -q
```

---

## W5 — Outreach Proof Lane + CI + Legacy Retirement

**Goal:** Exec-summary-style **proof artifacts** without copying résumé gates.

**Create:**

- `apps_lic/runtime/lanes/outreach_message_lane.py` — post-spine wrapper:
  - Writes `artifacts/apps_lic/runtime_proofs/outreach_message/<run_id>/`
  - `evidence_package_index.json`, `compiled_prompt_trace.json`, `x2_gate_outputs.json`, `judge_packet.json`, `x3_disposition.json`
- Optional CLI: `python -m apps_lic --proof-lane` (or always emit when `APPS_LIC_EMIT_PROOF=1`)

**CI:**

- Extend or add `ops_scripts/ci/check_apps_lic_spine_product_path.py`:
  - CLI must not default to `R4_SINGLE_ACTION`
  - `l0_route_apps_lic` invoked on product path
  - C0 bypass not sole grounding for non-dry outreach runs
- Register in `ops_scripts/ci/run_contract_gates.py`

**Legacy retirement:**

| Surface | Action |
|---------|--------|
| `integrated_r4_lic_pipeline_run.py` | Harness-only + deprecation header; or move to `apps_lic/runtime/legacy/` |
| `lic_l2_step_adapters` static DAG | Keep for cert smoke only; document vs HOP path |
| `tools/run_workflow_lic.py` | Already retired — verify no new imports |

**Closeout artifact:**

- `docs/reports/apps_lic/spine_product_convergence_closeout_receipt.md`

**Acceptance:**

```bash
python ops_scripts/ci/check_apps_lic_golden_path_runtime.py --fail-closed
python ops_scripts/ci/check_apps_lic_spine_product_path.py --fail-closed
python -m pytest tests/_apps_contract/test_ag8_apps_lic_golden_path.py -q
```

---

## Out of Scope

- Full rewrite of HOP agents or deletion of sequence/HITL infrastructure
- Wiring R1B semantic cache for LIC final drafts (explicitly bypassed)
- Copying `apps_rg` SRFS, skills graph materialization, or section-modular CLI
- `agentic_core` generic engine changes except approved enabling-plan interfaces
- Real LLM-judge calibration / production `apps_research` live runs (proof may mock bridge)

---

## Definition of Done

| # | Criterion | Verification |
|---|-----------|--------------|
| D1 | `python -m apps_lic` runs W2 dispatch (not default R4 shortcut) | CLI manifest shows `route_family` from L0 profile |
| D2 | Manual brief → R4; no brief + research auth → R3R4 calls bridge (mocked test) | W3 tests + artifact refs |
| D3 | All 10 bindings live under `apps_lic/runtime/bindings/` | Tree exists; core shims ≤30 lines |
| D4 | AG-8 + C0/PA tests pass | pytest + CI gate exit 0 |
| D5 | HOP generation uses spine PA/FEC per W4 decision | Code path + test assertion |
| D6 | Proof lane emits standard artifact bundle | Path under `artifacts/apps_lic/runtime_proofs/outreach_message/` |
| D7 | Closeout receipt with honest PASS/PARTIAL/BLOCKED | `docs/reports/apps_lic/spine_product_convergence_closeout_receipt.md` |

---

## Risk Register

| Risk | Mitigation |
|------|------------|
| U0 envelope vs raw JSON blocker | W2 option A — CLI emits contract dict |
| Dual L2 paths (static DAG vs HOP) | W5 document; cert flag for legacy only |
| Core enabling-plan dependencies | Gate W1/W4 on taxonomy/HITL stubs if needed |
| Live `apps_research` unavailable | Mock bridge in W3; mark live proof BLOCKED |

---

## Suggested Execution Order

1. W0 (half day) — no code
2. W1 (2–3 days) — bindings only, tests green
3. W2 (1–2 days) — CLI on spine
4. W3 (1–2 days) — R3R4 product path
5. W4 (2–4 days) — HOP/PA (largest uncertainty)
6. W5 (1 day) — proof lane + CI + receipt

**First PR slice:** W0 + W1 (boundary parity, zero behavior change to routing).

**Second PR slice:** W2 + W3 (product path users care about).

**Third PR slice:** W4 + W5 (quality + proof + legacy flags).
---

## ADG_GRAPH_LAYER_EVIDENCE

Preflight scope (Constitutional §22) — MV-driven blast radius before edits:

| MV | Use |
|----|-----|
| `mv_fanin_top` | inbound dependency rank for scoped seam |
| `mv_fanout_top` | outbound consumer rank |
| `mv_blast_radius` | change-impact envelope |
| `mv_chokepoint_score` | sequencing / coupling risk |

Semantic edges: `flows_to`, `reads_from`, `writes_to` · P-view: `v_p0_wave_plan`

---

## ADG_HOTSPOT_REPORT

| Rank | Node | Archetype | Surface | Rationale |
|------|------|-----------|---------|-----------|
| 1 | scoped seam | CENTRAL_DEPENDENCY | Execution Surface | primary edit locus |
| 2 | gate / boundary | SAFETY_GATEKEEPER | Security Surface | fail-closed enforcement |
