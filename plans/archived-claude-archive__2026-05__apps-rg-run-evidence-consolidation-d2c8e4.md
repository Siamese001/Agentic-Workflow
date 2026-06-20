---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\2026-05\\apps-rg-run-evidence-consolidation-d2c8e4.md'
original_relative_path: '_archive\\2026-05\\apps-rg-run-evidence-consolidation-d2c8e4.md'
source_sha256: 6edde1b4e67042b4c58c239b24dea9f37d5479a1b2da36ec2e987cf5cf9c139b
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: apps-rg-run-evidence-consolidation-d2c8e4
plan_type: governance
touches_agentic_core: false
touches_governance_ci: true
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
---

# apps_rg — Consolidate run evidence layout (runs + runtime_proofs + L7 audit)

Unify how operators discover **integrated R4 runs**, **per-lane seam proofs**, **rollup/assembly outputs**, and **L7 / audit JSON** under one correlation model and predictable subfolders — without breaking rollup eligibility or `render_run_summary.py` consumers.

> **plan_id** matches filename stem: `plan=apps-rg-run-evidence-consolidation-d2c8e4`.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: DONE
CURRENT_WAVE: W4-complete
LAST_COMPLETED_WAVE: W4
LAST_UPDATED: 2026-05-17

---

## Context (SCQA)

- **Situation** — Evidence lands in multiple roots: `artifacts/apps_rg/runs/<run_id>/` (integrated spine, L7 matrix, terminal packet per `pipeline_defaults.yaml`); `artifacts/apps_rg/runtime_proofs/<lane>/{real|mock}/<run_id>/` (lane dispatch per `runtime_proof_layout.py`); optional `APPS_RG_MODULAR_R4_SECTIONS_ROOT`; aggregates under `generated_lane_rollup/`, `final_resume_assembly/`, etc.
- **Complication** — Operators cannot tell which directory answers “outputs vs run logs vs L7 explainability” for a single logical run; `tools/apps_rg/render_run_summary.py` only indexes `artifacts/apps_rg/runs/`.
- **Question** — How do we consolidate **discovery** and **naming** so every run has a single correlation story without Big Bang path moves?
- **Answer** — Phased approach: operator map → standardized bundle subfolders + `RUN_BUNDLE_INDEX.json` → optional unified evidence root with links → align on-disk logs; keep legacy paths via compatibility layer until tests and pointers migrate.

---

## Current evidence map (baseline)

| Intent | Canonical path | Key artifacts |
|--------|------------------|---------------|
| Full integrated R4 / CLI | `artifacts/apps_rg/runs/<id>/` | `terminal_ret_packet.json`, `run_report.json`, `runtime_identity_envelope.json`, `r4_run_manifest.json`, `agentic_core_l7_route_family_coverage.json`, `agentic_core_how_trace.json`, resume outputs |
| Lane seam (exec summary, headline, …) | `artifacts/apps_rg/runtime_proofs/<lane>/{real\|mock}/<id>/` | `run_manifest.json`, `l2_output.json`, gate/judge/disposition JSON |
| Rollup / assembly | `artifacts/apps_rg/runtime_proofs/generated_lane_rollup/`, `final_resume_assembly/`, `locked_copy/`, `docx/` | manifests and aggregated outputs |

**Profile SSOT:** `config/profiles/apps_rg/pipeline_defaults.yaml` (`artifact_namespace`, `log_namespace`, `telemetry_prefix`). **W3.2:** Integrated `RUN_LINKS.json` carries `log_discovery` (`disk` \| `telemetry_only` \| `unavailable`); integrated `RUN_BUNDLE_INDEX.json` may include `log_root_path` when the `log_namespace` directory exists under the repo. **W4.1:** When `APPS_RG_MODULAR_R4_SECTIONS_ROOT` is set, `sections_root_manifest.json` must sit beside that resolved root (in-repo paths only); `RUN_LINKS.json` exposes `modular_sections_root` (`default` \| `env_manifest`).

---

## Status Tables

### Wave Progress

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1 | W1.1–W1.2 | Operator map + bundle index spec | ~12k | Notion + disk plan accepted | ✅ DONE | Contract in `apps_rg/runtime/run_bundle_index.py`; evidence map remains plan § table; W1.1 standalone doc deferred |
| W2 | W2.1–W2.2 | Implement index emission + subfolder layout (compat) | ~18k | Lane + integrated writers cooperate | ✅ DONE | `RUN_BUNDLE_INDEX.json` emitted from `canonical_dispatch`, `__main__`, `finalize_runtime_proof_run`; no subdir moves |
| W3 | W3.1–W3.2 | Correlation manifest + log discovery metadata | ~14k | No symlink evidence root required | ✅ DONE | `RUN_LINKS.json` + `log_discovery`; optional `log_root_path` on integrated index when disk tree exists |
| W4 | W4.1 | Env split policy + mandatory manifest for `APPS_RG_MODULAR_R4_SECTIONS_ROOT` | ~6k | CI/grep catches drift | ✅ DONE | `sections_root_manifest.json` + `RUN_LINKS.modular_sections_root`; outside-repo roots rejected |

### Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|-----------------|-------------|-------------|--------|
| W1.1 | Operator-facing map | `docs/` or `apps_rg/` short pointer doc (repo convention) | Choosing doc SSOT | ~2k | 🔄 PARTIAL (plan § map only) |
| W1.2 | `RUN_BUNDLE_INDEX` contract | `apps_rg/runtime/run_bundle_index.py` | Backward compatibility | ~3k | ✅ DONE |
| W2.1 | Emit index from integrated runner | `canonical_dispatch.py`, `__main__.py` | Flat vs nested paths | ~8k | ✅ DONE |
| W2.2 | Emit index from lane finalize | `runtime_proof_layout.py` | real/mock buckets | ~6k | ✅ DONE |
| W3.1 | Correlation manifest (`RUN_LINKS.json`) beside integrated runs | orchestrator emit + `apps_rg/runtime/run_correlation_links.py` | Single-hop discovery | ~5k | ✅ DONE |
| W3.2 | Log discovery in manifests (`log_discovery`, optional `log_root_path`) | `run_bundle_index.py`, `run_correlation_links.py` | File vs OTEL | ~5k | ✅ DONE |
| W4.1 | Modular sections root discipline | `runtime_proof_layout.py`, `sections_root_manifest.py`, `run_correlation_links.py`, Phase 1 emit | Third root confusion | ~4k | ✅ DONE |

---

## Out Of Scope

- Big-bang rename of `artifacts/apps_rg/runs/` ↔ `runtime_proofs/` without migration shims.
- Changing L7 certification semantics or Fort Knox bundles.
- Moving pytest temp roots (e.g. `.pytest_exec_sum_*`).

---

## Wave 1 — Discovery and contract

WAVE_ID: W1
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED

**Phases**:
- **W1.1** — Publish operator map (~2k) | PHASE_STATUS: PARTIAL (plan table SSOT; no separate doc file)
- **W1.2** — `RUN_BUNDLE_INDEX.json` fields + examples (~3k) | PHASE_STATUS: DONE

**Acceptance**:
- One-page table: where to look for integrated vs lane vs aggregate vs L7.
- Index JSON lists: `role`, `relative_path`, `content_type` for each known artifact class.

---

## Wave 2 — Writers emit index (compatibility-first)

WAVE_ID: W2
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED

**Phases**:
- **W2.1** — Integrated run dir: write index; optional `40_audit/` deferred (~8k) | PHASE_STATUS: DONE (index only; no physical subdirs)
- **W2.2** — `finalize_runtime_proof_run`: lane index (~6k) | PHASE_STATUS: DONE

**Acceptance**:
- `render_run_summary.py` still works with zero args on latest run (existing filenames).
- New runs include `RUN_BUNDLE_INDEX.json` at run root.

---

## Wave 3 — Unified evidence root and logs

WAVE_ID: W3
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED

**Phases**:
- **W3.1** — `artifacts/apps_rg/runs/<run_id>/RUN_LINKS.json` (repo-relative POSIX) pointing at integrated bundle index + optional lane/runtime-proof bundle indexes found via conservative path scan (~5k) — **DONE**
- **W3.2** — Manifest `log_discovery` + optional integrated `RUN_BUNDLE_INDEX.log_root_path` when `log_namespace` exists on disk; otherwise classify `telemetry_only` or `unavailable` — **DONE**

**Acceptance**:
- Single directory opens the full evidence graph for one operator “run.”
- Log files discoverable under a documented path or explicitly marked “telemetry-only.”

---

## Wave 4 — Modular sections root policy

WAVE_ID: W4
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED

**Phases**:
- **W4.1** — When `APPS_RG_MODULAR_R4_SECTIONS_ROOT` is set, require sibling `sections_root_manifest.json`; in-repo resolved path only; `RUN_LINKS` carries `modular_sections_root`; Phase 1 writer emits manifest before setting env (~4k) — **DONE**

**Acceptance**:
- No “silent third root” without a machine-readable manifest — **DONE** (unit coverage in `test_run_correlation_links.py`, `test_modular_resume_generation_phase1.py`).

---

## Gap Register

**GAP-1:** Windows symlink vs junction policy for evidence links — pick one supported approach for repo clones.

**GAP-2:** Whether L7 JSON is duplicated into `40_audit/` or only indexed (avoid drift).

---

## Definition of Done

| DoD | Verification | Deferred? |
|-----|----------------|-----------|
| DoD-1 | Operator map committed; path table matches code SSOT (`pipeline_defaults.yaml`, `runtime_proof_layout.py`) | No |
| DoD-2 | Sample run produces `RUN_BUNDLE_INDEX.json` under both `runs/` and a lane `runtime_proofs/.../` path | No |
| DoD-3 | `python tools/apps_rg/render_run_summary.py <run_dir>` exits 0 on a fresh integrated run dir | No |
| DoD-4 | Pinned smoke dirs expose valid `RUN_BUNDLE_INDEX.json` (+ integrated `RUN_LINKS.json`); gate RG-SMOKE-BUNDLE | No |
| DoD-5 | Notion Plans row exists with `Exists On Disk=true`, `Plan File Path` = `.cursor/plans/apps-rg-run-evidence-consolidation-d2c8e4.md` | No |

**DoD rows (detail)**

- DoD-1: Primary functional outcome — consolidation plan executed through W1–W2 minimum; evidence discoverable.
- Evidence: plan § Current evidence map + `apps_rg/runtime/run_bundle_index.py`.
- Status: DONE (W1.1 standalone markdown doc explicitly out of scope for this pass)

- DoD-2: Smoke-run — index files under both trees.
- Evidence: `artifacts/apps_rg/runs/_proof_smoke_integrated/RUN_BUNDLE_INDEX.json`, `_proof_smoke_integrated/RUN_LINKS.json`, `artifacts/apps_rg/runtime_proofs/headline/mock/_proof_smoke_lane/RUN_BUNDLE_INDEX.json` (smoke emission).
- Status: DONE

- DoD-3: Tests — `tests/unit/apps_rg/test_run_bundle_index.py` + subprocess `render_run_summary`.
- Evidence: `pytest tests/unit/apps_rg/test_run_bundle_index.py tests/unit/apps_rg/test_run_correlation_links.py -q --tb=short` exit 0; `render_run_summary` on `_proof_smoke_integrated`.
- Status: DONE

- DoD-4: Smoke bundle guard — validates schema for pinned `_proof_*` dirs only (skipped when dirs absent via gate exit 0).
- Evidence: `ops_scripts/ci/check_apps_rg_smoke_bundle_indexes.py` (**RG-SMOKE-BUNDLE**, wired in `run_contract_gates.py`); unit smoke `tests/unit/apps_rg/test_apps_rg_smoke_bundle_indexes.py`; `pytest … -q --tb=short` (without `-p pytest_timeout`) exit 0.
- Status: DONE

- DoD-5: Notion + disk parity per AGENTS.md auto-routing.
- Evidence: Plans DB row + on-disk plan file (created earlier in session).
- Status: DONE (pre-existing)

---

## Verification vs Deferral

| Item | In charter | Deferred to |
|------|------------|---------------|
| Full physical merge of `runs` + `runtime_proofs` | No | Future plan after index stable |
| CI gate for pinned smoke bundles (`RUN_BUNDLE_INDEX` + integrated `RUN_LINKS`) | Yes | ✅ `RG-SMOKE-BUNDLE` in `run_contract_gates.py` (advisory; roots may be absent on fresh clones) |
| OTEL-only log strategy | Clarified in W3 | N/A |

---

## Marker Quick Reference

```
WAVE_START: plan=apps-rg-run-evidence-consolidation-d2c8e4 wave=<N>
WAVE_COMPLETE: plan=apps-rg-run-evidence-consolidation-d2c8e4 wave=<N> note="<summary>"
PLAN_COMPLETE: plan=apps-rg-run-evidence-consolidation-d2c8e4 note="<final outcome>"
```

**Executed:**

```
PLAN_COMPLETE: plan=apps-rg-run-evidence-consolidation-d2c8e4 note="W1-W4 delivered; RG-SMOKE-BUNDLE + smoke RUN_LINKS with modular_sections_root default; pytest + render_run_summary PASS"
```

---

## W1–W2 execution markers (manual)

```
WAVE_COMPLETE: plan=apps-rg-run-evidence-consolidation-d2c8e4 wave=1 note="RUN_BUNDLE_INDEX contract in apps_rg/runtime/run_bundle_index.py; evidence map = plan § Current evidence map"
WAVE_COMPLETE: plan=apps-rg-run-evidence-consolidation-d2c8e4 wave=2 note="+6 unit tests test_run_bundle_index.py; emit wired canonical_dispatch+__main__+finalize_runtime_proof_run; render_run_summary smoke exit 0"
```
