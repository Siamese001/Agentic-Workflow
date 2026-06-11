---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\qwen3-32b-vllm-upgrade-d7a3f1.md'
original_relative_path: 'qwen3-32b-vllm-upgrade-d7a3f1.md'
source_sha256: c66667f83dd3a0ea0d806f97fc888b8584b554584c0109112b57b4451843d3e4
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: qwen3-32b-vllm-upgrade-d7a3f1
plan_type: infra
touches_agentic_core: false
touches_governance_ci: false
touches_cursor_rules: true
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
---

# Qwen3-32B-Instruct-AWQ — Local vLLM Upgrade (RTX 5090)

Upgrade the canonical `local-qwen-vllm` stack from **Qwen2.5-32B-Instruct-AWQ** to **Qwen3-32B-Instruct-AWQ** (dense AWQ) on the RTX 5090 Docker path, with regression proof on apps_rg generation lanes. **Not** a Chroma/BGE retrieval upgrade.

> **Priority:** Parked — execute when scheduled vLLM maintenance or exec-summary regen quality/cost triggers work.  
> **Notion status:** `Lower Priority`  
> **Supersedes nothing:** Qwen2.5-32B remains production until W3 proof passes.  
> **Related:** [qwen-vllm-topology.md](docs/architecture/qwen-vllm-topology.md), [local-llm-wsl2-gpu.mdc](.cursor/rules/local-llm-wsl2-gpu.mdc), [exec-summary-qwen-regen-token-budget-c4e8a1.md](exec-summary-qwen-regen-token-budget-c4e8a1.md) (completed)

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: TODO
CURRENT_WAVE: W0
LAST_COMPLETED_WAVE: NONE
LAST_UPDATED: 2026-05-26
NOTION_STATUS: Lower Priority
NOTION_PAGE_ID: 36c27693-f55c-8121-8712-c2bc55a50d72

---

## Context (SCQA)

- **Situation** — Production serves `Qwen/Qwen2.5-32B-Instruct-AWQ` via Docker `local-qwen-vllm` at `http://localhost:8000/v1`, `max-model-len=24576`, `awq_marlin`, `gpu_memory_utilization=0.92`. L0 SSOT: `QWEN_LOCAL_MODEL_ID` / `VLLM_MODEL_NAME`. apps_rg exec summary, section lanes, and `qwen_context_gateway` (ADR-045) route through this endpoint. Chroma C0 dense retrieval uses **BGE-M3** separately.
- **Complication** — Qwen3-32B offers better instruction-following and regen behavior, but Blackwell (SM_120) vLLM pins, token budgets, X2 gates, and judge baselines were tuned on 2.5-32B. Blind image bumps risk OOM, pydantic init failures, or silent quality regression.
- **Question** — How do we upgrade to Qwen3-32B AWQ with proof and a clean rollback path?
- **Answer** — Preflight vLLM+Qwen3 on 5090 → recreate container with pinned image → update env/docs/defaults → narrow contract proof (exec summary first) → optional fleet-wide lane sweep. MoE (Qwen3-30B-A3B) stays out of scope unless a follow-up plan is opened.

---

## Status Tables

### Wave Progress

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W0 | W0.1–W0.2 | Preflight: HF model, vLLM image pin, smoke load | ~8K | NOTION_TOKEN optional for W0 | 🔲 TODO | `/v1/models` lists Qwen3-32B-AWQ; no OOM at 24576 |
| W1 | W1.1–W1.2 | Container recreate + weight cache | ~12K | ~20 GB AWQ download | 🔲 TODO | `local-qwen-vllm` healthy; rollback doc in topology |
| W2 | W2.1–W2.2 | SSOT env + docs + rules | ~10K | No agentic_core unless env-only | 🔲 TODO | `VLLM_MODEL_NAME` + topology match container |
| W3 | W3.1–W3.2 | Regression: unit + exec_summary contract | ~15K | Live GPU for REAL_LLM slice | 🔲 TODO | Targeted pytest PASS; Brown/exec lane acceptable |
| W4 | W4.1 | Optional full lane sweep + ADR-045 note | ~8K | Deferred unless W3 clean | 🔲 TODO | Operator sign-off or explicit deferral |

### Phase Progress

| Phase | Title | Status |
|-------|-------|--------|
| W0.1 | Confirm HF id + AWQ variant (`Qwen/Qwen3-32B-Instruct-AWQ` or community mirror) | 🔲 TODO |
| W0.2 | Trial container on pinned vLLM (Blackwell: `awq_marlin`, `TRITON_ATTN` if needed) | 🔲 TODO |
| W1.1 | Stop/rm/recreate `local-qwen-vllm` with Qwen3 args | 🔲 TODO |
| W1.2 | Verify `nvidia-smi` + `curl /v1/models` + single chat completion | 🔲 TODO |
| W2.1 | Update `docs/architecture/qwen-vllm-topology.md`, `local-llm-wsl2-gpu.mdc` | 🔲 TODO |
| W2.2 | Document env overrides (`VLLM_MODEL_NAME`, served-model-name parity) | 🔲 TODO |
| W3.1 | `tests/unit/agentic_core/L0_routing/config/test_max_model_len_ssot.py` + qwen strict diagnostic | 🔲 TODO |
| W3.2 | apps_rg exec_summary contract / Brown slice (budget + regen invariants) | 🔲 TODO |
| W4.1 | Other section lanes + optional contextualize ingest spot-check | 🔲 TODO |

---

## Out Of Scope

- **Qwen3-30B MoE** (A3B) — separate plan if throughput is the goal
- **Chroma / BGE / fact_vectors re-index** — retrieval unchanged unless follow-up ADR-045 bulk ingest
- **72B or multi-GPU** — does not fit 32 GB single 5090
- **Cloud judge provider changes** — local model swap only
- **Prompt/rubric/X2 threshold changes** to “make Qwen3 pass” — fix transport/config first; policy changes need separate authorization

---

## Resume triggers (Lower Priority)

Execute this plan when **any** of:

1. Scheduled **vLLM Docker image / container rebuild** already planned
2. Exec-summary **regen burn** or proof-binding failures persist after token-budget work (c4e8a1)
3. Operator explicitly promotes plan to **In Progress**

---

## Wave 0 — Preflight & risk matrix

WAVE_ID: W0
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: A

**Phases**:
- **W0.1** — Confirm model card, AWQ repo id, license, approximate VRAM at Q4 AWQ + KV @ 24576 | ~4K | PHASE_STATUS: TODO
- **W0.2** — Ephemeral trial container (do not delete prod until W1): load model, `awq_marlin`, probe max context | ~4K | PHASE_STATUS: TODO

**Acceptance**:
- Trial completes one chat completion without OOM
- Document pinned vLLM image tag/digest (avoid unproven `latest` on Blackwell)
- Rollback command block copied into topology §0

**Blackwell checklist** (from [rtx5090_vllm_qwen_optimization_research_20260424.md](docs/reports/retrieval_baseline/rtx5090_vllm_qwen_optimization_research_20260424.md)):
- `--quantization awq_marlin` (not `awq`)
- Consider `--attention-backend TRITON_ATTN` if FA/SM_120 issues
- `VLLM_USE_V1=1` per engine requirements for pinned image

---

## Wave 1 — Container & weights

WAVE_ID: W1
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: B

**Phases**:
- **W1.1** — Production cutover: recreate `local-qwen-vllm` with Qwen3 model id (keep `max-model-len`, `gpu-memory-utilization` unless W0 proves adjustment) | ~6K
- **W1.2** — Health + minimal generation smoke | ~6K

**Target container args** (adjust after W0):

```text
--model Qwen/Qwen3-32B-Instruct-AWQ
--served-model-name Qwen/Qwen3-32B-Instruct-AWQ
--quantization awq_marlin
--dtype auto
--max-model-len 24576
--gpu-memory-utilization 0.92
--host 0.0.0.0
--port 8000
```

**Rollback** — recreate with Qwen2.5-32B-Instruct-AWQ args (preserve topology §0 block).

---

## Wave 2 — SSOT & documentation

WAVE_ID: W2
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: C

**Phases**:
- **W2.1** — Update topology, local-llm rule VRAM table footnote, `qwen_context_gateway.py` module docstring if default id changes | ~5K
- **W2.2** — Operator env table: `VLLM_MODEL_NAME`, `VLLM_MAX_MODEL_LEN`, `VLLM_BASE_URL`, served name must match `/v1/models` | ~5K

**Acceptance**:
- `agentic_core/L0_routing/config/model_registry.py` default env docs align (file edit only if changing documented default string in comments — prefer env override)
- `qwen_strict_diagnostic.py` passes `ok` against new served name

---

## Wave 3 — Regression proof

WAVE_ID: W3
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: D

**Phases**:
- **W3.1** — Unit: max_model_len SSOT, vllm serving profile types, strict diagnostic | ~6K
- **W3.2** — Contract: exec_summary regen SSOT tests + one REAL_LLM Brown or harness lane if operator approves GPU time | ~9K

**Manifest** (baseline from prior qwen work):
- `docs/reports/apps_rg/qwen_vllm_reliability_w5_test_manifest.json` (refresh if image pin changes)

**Acceptance**:
- No regression in `budgeted_qwen_regen_call` invariants (I1–I8 from c4e8a1)
- Exec summary artifacts: call plan + transport receipts sane
- Explicit FAIL if regen acceptance rate drops without documented cause

---

## Wave 4 — Fleet sweep (optional)

WAVE_ID: W4
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: E

**Phases**:
- **W4.1** — unify_narrative, competencies, IBM lanes spot-check; ADR-045 contextualize sample (10 chunks) | ~8K

**Defer** entire W4 unless W3 PASS and operator requests breadth.

---

## Gap Register

**GAP-1: Exact HF model id**
- Official `Qwen/Qwen3-32B-Instruct-AWQ` availability vs QuantTrio/community AWQ — resolve in W0.1

**GAP-2: vLLM version vs Qwen3**
- Qwen3 native support requires minimum vLLM; may conflict with Blackwell pin — W0.2 decides image tag

**GAP-3: MoE confusion**
- Operators may expect retrieval lift — document in closeout: BGE/Chroma unchanged

---

## Definition of Done

DoD-1: `local-qwen-vllm` serves Qwen3-32B-Instruct-AWQ at `http://localhost:8000/v1` with `max-model-len` matching `VLLM_MAX_MODEL_LEN=24576`
- Evidence: `curl http://localhost:8000/v1/models` JSON + `qwen_strict_diagnostic` → `ok`
- Status: TODO

DoD-2: Topology and local-llm rule document Qwen3 args and rollback
- Evidence: diff in `docs/architecture/qwen-vllm-topology.md`, `.cursor/rules/local-llm-wsl2-gpu.mdc`
- Status: TODO

DoD-3: Targeted pytest slice PASS (no skipped gates)
- Evidence: `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/unit/agentic_core/L0_routing/config/test_max_model_len_ssot.py tests/_apps_contract/test_exec_summary_regen_qwen_dispatch_ssot.py -q`
- Status: TODO

DoD-4: Exec-summary REAL_LLM proof or documented deferral with reason
- Evidence: Brown/harness artifact path in `docs/reports/apps_rg/` OR `DEFERRED_SCOPE` marker with operator ack
- Status: TODO

DoD-5: Closeout receipt + Notion `Completed`
- Evidence: `docs/reports/retrieval_baseline/qwen3_32b_vllm_upgrade_closeout_receipt.md` + `PLAN_COMPLETE` marker
- Status: TODO

### Verification vs deferral

| Item | Verify now | Defer |
|------|------------|-------|
| Container load + health | W1 | — |
| Full all-lane REAL_LLM matrix | — | W4 unless promoted |
| Chroma re-index | — | Separate plan |
| MoE trial | — | Separate plan |

---

## Marker Quick Reference

```
PLAN_CREATED: slug=qwen3-32b-vllm-upgrade-d7a3f1 path=.cursor/plans/qwen3-32b-vllm-upgrade-d7a3f1.md status=Lower Priority
WAVE_COMPLETE: plan=qwen3-32b-vllm-upgrade-d7a3f1 wave=<N> note="<evidence>"
PLAN_COMPLETE: plan=qwen3-32b-vllm-upgrade-d7a3f1 note="<outcome>"
```
