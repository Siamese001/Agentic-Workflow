---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\2026-05\\exec-summary-cli-gates-closeout-c7e4f2.md'
original_relative_path: '_archive\\2026-05\\exec-summary-cli-gates-closeout-c7e4f2.md'
source_sha256: f99754e1287aec13310c624a54e8dfc0288f8ad602c83fc52bbf224c520b5f34
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: exec-summary-cli-gates-closeout-c7e4f2
plan_type: refactor
touches_agentic_core: false
touches_governance_ci: false
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
---

# Executive Summary CLI Gates Closeout (SRFS + Targeting + vLLM Health)

Retrospective plan capturing all waves from the exec-summary SRFS bug-closeout and CLI hardening chat (2026-05-19–20). Default `python -m apps_rg --section executive_summary` must bind SRFS proof, reject stale/missing targeting, fast-fail mock provider, and require live Qwen vLLM Docker + HTTP health before dispatch.

> **Related plan:** [exec-summary-srfs-bug-closeout-a3f291.md](exec-summary-srfs-bug-closeout-a3f291.md) (narrower SRFS scope; absorbed here for chat closure).

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: DONE
CURRENT_WAVE: DONE
LAST_COMPLETED_WAVE: W6
LAST_UPDATED: 2026-05-20

---

## Context (SCQA)

- **Situation** — Default executive_summary CLI could masquerade as full proof (graph-only, DEFAULT_SSOT JD/briefing, mock provider hangs, no vLLM health gate).
- **Complication** — `exec_summary_20260520_000526` X3_BLOCK on invented metrics; post-fix runs still allowed placeholder targeting and silent mock/vLLM bypass under pytest `stub_only`.
- **Question** — How do we fail closed on inputs and infrastructure while proving SRFS-bound REAL_LLM ALLOW?
- **Answer** — apps_rg-only binding + targeting freshness + section_cli_preflight + regression tests; canonical proof run `exec_summary_20260520_105209` (X3_ALLOW).

---

## Status Tables

### Wave Progress

| Wave | Focus | Status | Tests Added | Files Changed |
|------|-------|--------|-------------|---------------|
| W1 | SRFS binding + regression tests | ✅ DONE | +6 contract/unit | proof_pool_resolver, srfs_binding, tests |
| W2 | Runtime SRFS proof + artifact inspection | ✅ DONE | subprocess/artifact | artifacts exec_summary real |
| W3 | Synthesis-only judge-safe (X3_ALLOW) | ✅ DONE | lane proof | exec_summary_srfs_judge_safe.py |
| W4 | JD/briefing mandatory + stale SSOT gate | ✅ DONE | +4 unit/contract | targeting_input_freshness.py, __main__.py |
| W5 | Mock fast-fail + vLLM health mandatory | ✅ DONE | +8 unit/contract | section_cli_preflight.py, section_cli_defaults.py |
| W6 | CLI proof demonstrations | ✅ DONE | manual commands | NONE (verification only) |

### Phase Progress

| Phase | Title | Status |
|-------|-------|--------|
| W1.1 | Default SRFS resolver + binding materialize | ✅ DONE |
| W1.2 | Regression tests (no graph-only masquerade) | ✅ DONE |
| W2.1 | REAL_LLM run + artifact inspection | ✅ DONE |
| W2.2 | Negative control (missing SRFS) | ✅ DONE |
| W3.1 | Judge-safe synthesis patches | ✅ DONE |
| W4.1 | Targeting freshness validator | ✅ DONE |
| W4.2 | Dry-run + exec_summary CLI gates | ✅ DONE |
| W5.1 | Reject `--provider mock` | ✅ DONE |
| W5.2 | Docker container + HTTP /v1/models preflight | ✅ DONE |
| W6.1 | Prove-it command matrix | ✅ DONE |

---

## Out Of Scope

- agentic_core edits
- All-section SRFS rollout
- Gate/rubric weakening
- Graph-only as acceptable proof
- Notion backlog wave execution (phase2 GTM graph waves)

---

## Wave 1 — SRFS binding and regression proof

WAVE_ID: W1
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: A

**Phases**:
- **W1.1** — Default executive_summary → active SRFS via `resolve_executive_summary_default_srfs_path` | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W1.2** — Contract tests: fail-closed without SRFS; SRFS vs GRAPH_ONLY rubric | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Acceptance** (met):
- `selected_role_fact_set_used=true`, `proof_pool_type=selected_role_fact_set`, `x2_srfs_gate_status=PASS`
- Judge packet uses `SRFS_GRADE_ONLY_RUBRIC` when SRFS active

**Commands**:
```bash
set PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
python -m pytest tests/_apps_contract/test_apps_rg_proof_pool_resolver_contract.py -k executive_summary -o addopts= -q
python -m pytest tests/_apps_contract/test_executive_summary_judge_packet_srfs_rubric.py -o addopts= -q
```

---

## Wave 2 — Runtime SRFS proof

WAVE_ID: W2
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: B

**Phases**:
- **W2.1** — REAL_LLM run with updated targeting (not DEFAULT_SSOT) | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W2.2** — Artifact inspection vs `exec_summary_20260520_000526` regression | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Canonical proof bundle:** [exec_summary_20260520_105209](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260520_105209)

**Key artifacts:** `section_metric_receipt.json`, `executive_summary_judge_packet.json`, `x2_gate_outputs.json`, `x3_disposition.json` → `X3_ALLOW`

---

## Wave 3 — Synthesis-only judge-safe (X3_ALLOW)

WAVE_ID: W3
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: C

**Phases**:
- **W3.1** — `exec_summary_srfs_judge_safe.py` only: S2 single-thread, S3 lifecycle, S4 fact-tight, S5 no meta-filler | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Outcome:** `exec_summary_20260520_105209` — X3_ALLOW, exit 0 (with updated JD/briefing + live vLLM).

---

## Wave 4 — JD/briefing mandatory + stale SSOT gate

WAVE_ID: W4
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: D

**Phases**:
- **W4.1** — `targeting_input_freshness.py` digest vs DEFAULT_SSOT | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W4.2** — Wire `__main__.py` + `canonical_dispatch` stale_targeting_inputs fault | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Files:** [targeting_input_freshness.py](apps_rg/runtime/targeting_input_freshness.py), [__main__.py](apps_rg/__main__.py), [canonical_dispatch.py](apps_rg/runtime/orchestration/canonical_dispatch.py), [ci-probe-briefing.txt](tests/_fixtures/ci-probe-briefing.txt)

**Override (tests only):** `APPS_RG_ALLOW_STALE_TARGETING_SSOT=1`

---

## Wave 5 — Mock fast-fail + vLLM health mandatory

WAVE_ID: W5
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: E

**Phases**:
- **W5.1** — Remove `mock` from `--provider`; reject at resolve with exit 2 | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W5.2** — `section_cli_preflight.py`: docker `local-qwen-vllm` running + HTTP `/v1/models`; honor `VLLM_BASE_URL` | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Files:** [section_cli_preflight.py](apps_rg/runtime/section_cli_preflight.py), [section_cli_defaults.py](apps_rg/runtime/section_cli_defaults.py)

**Skips:** `APPS_RG_QWEN_OFFLINE_CONTRACT_STUB=1`, `APPS_RG_SKIP_QWEN_VLLM_HEALTH=1` (not `APPS_RG_L2_PROVIDER_MODE=stub_only` — pytest conftest must not bypass section health)

**Tests:** 25/25 hardened slice passed (2026-05-20).

---

## Wave 6 — CLI proof demonstrations

WAVE_ID: W6
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: F

**Phases**:
- **W6.1** — Prove-it command matrix | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

| Command | Expected | Observed |
|---------|----------|----------|
| `python -m apps_rg --section executive_summary` | exit 2 missing inputs | exit 2 ~6.5s |
| `... --jd default_jd --manual-brief default_briefing` | exit 2 stale SSOT | exit 2 |
| `... ci-probe fixtures + VLLM_BASE_URL=127.0.0.1:9` | exit 2 health | exit 2 ~8s |
| `... ci-probe fixtures + live vLLM` | lane runs | exit 1 X3 not ALLOW (no waiver) |

---

## Definition of Done

DoD-1: Default CLI binds SRFS proof pool (not graph-only masquerade)
- Evidence: `test_executive_summary_default_resolves_active_srfs_binding` + `section_metric_receipt.json` on proof run
- Status: DONE

DoD-2: executive_summary CLI fail-closed on missing/stale targeting
- Evidence: `python -m apps_rg --section executive_summary` → exit 2; stale DEFAULT_SSOT → exit 2
- Status: DONE

DoD-3: Section lanes reject mock provider and require vLLM health for live qwen_vllm
- Evidence: `--provider mock` → exit 2; bad `VLLM_BASE_URL` → exit 2; pytest 25/25
- Status: DONE

DoD-4: REAL_LLM SRFS proof run achieves X3_ALLOW
- Evidence: [exec_summary_20260520_105209/x3_disposition.json](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260520_105209/x3_disposition.json)
- Status: DONE

DoD-5: Plan registered on disk + Notion Completed
- Evidence: this file + Notion Plans row `exec-summary-cli-gates-closeout-c7e4f2`
- Status: DONE

---

## Verification vs Deferral

| Item | Status | Notes |
|------|--------|-------|
| SRFS binding | DONE | apps_rg only |
| X3_ALLOW proof | DONE | 105209 bundle |
| Targeting gates | DONE | freshness module |
| vLLM health gate | DONE | section_cli_preflight |
| Full R4 product path | DEFERRED | section lanes only |
| Updated production JD/briefing files | DEFERRED | operator supplies per run |

---

## Marker Log (chat closure)

```
WAVE_COMPLETE: plan=exec-summary-cli-gates-closeout-c7e4f2 wave=1 note="+6 tests, 4 files, scope=srfs-binding"
WAVE_COMPLETE: plan=exec-summary-cli-gates-closeout-c7e4f2 wave=2 note="artifact proof, 1 bundle, scope=runtime-srfs"
WAVE_COMPLETE: plan=exec-summary-cli-gates-closeout-c7e4f2 wave=3 note="synthesis-only, 1 file, scope=x3-allow"
WAVE_COMPLETE: plan=exec-summary-cli-gates-closeout-c7e4f2 wave=4 note="+4 tests, 5 files, scope=targeting-freshness"
WAVE_COMPLETE: plan=exec-summary-cli-gates-closeout-c7e4f2 wave=5 note="+8 tests, 3 files, scope=cli-preflight"
WAVE_COMPLETE: plan=exec-summary-cli-gates-closeout-c7e4f2 wave=6 note="manual proof, 0 files, scope=prove-it"
PLAN_COMPLETE: plan=exec-summary-cli-gates-closeout-c7e4f2 note="All waves DONE; SRFS X3_ALLOW + CLI gates proven"
```
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
