---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\2026-05\\phase-b-blocker-burndown-a8c4f1.md'
original_relative_path: '_archive\\2026-05\\phase-b-blocker-burndown-a8c4f1.md'
source_sha256: c29dbb40fb0ec9c64fb2d62cd5c581e3e14b77b164f9744ce11325c383daedbb
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Phase B P0 Gate Blocker Burndown

Source snapshot: `adg_indexed_04232026_1820.sqlite`
Runner artifact: `artifacts/ci_gates/p0_runner_full_2026-04-23T222214_995698+0000.json`
Status date: 2026-04-23

## Baseline (post Wave-1/Wave-2 layer violation cleanup)

| Gate | Violations | Severity | Character |
|---|---:|---|---|
| `write_sovereignty` | 1864 | CRITICAL | Non-UWG write paths across production code |
| `authority_boundary` | 612 | HIGH | Cross-layer import breaches (e.g. L6→L0) |
| `capability_egress` | 492 | HIGH | L0 actions without egress gate |
| `critical_path_integrity` | 64 | HIGH | Whole layers (L_APP, L5, L_SHARED) disconnected from runtime spine |
| `infra_wiring` | 2 | LOW | Direct vendor SDK imports outside sanctioned adapters |
| **TOTAL** | **3034** | | |

## Wave Structure

| Wave | Focus | Approach | Est. Tokens | Status |
|---|---|---|---:|---|
| W1 | `infra_wiring` (2) | Allow-list the 2 new sanctioned adapters | 2k | in-progress |
| W2 | `authority_boundary` L6 imports (top offender subset) | Fix `L6_observability/__init__.py` re-exports; remove illegal L6→L0 imports | 20k | todo |
| W3 | `critical_path_integrity` (64) | MV/spine configuration — likely allow-list of non-runtime layers (L_APP, L_SHARED, L_OPS, L_TOOLS, L_PG) | 15k | todo |
| W4 | `capability_egress` (492) | Classify L0 modules: non-action (allow-list) vs needs egress gate (wire through provider) | 40k | todo |
| W5 | `write_sovereignty` (1864) | Systemic — route through UWG, or expand adapter whitelist where legitimate | 80k+ | todo |

## Wave Sequencing Rationale

1. **Smallest first (W1)** — proves the gate interaction and establishes rhythm.
2. **Next-smallest structural (W3 spine gaps)** — likely a one-line allow-list for non-runtime layers; high-count but low-effort.
3. **Authority boundary (W2)** — concentrated in re-export shims; fixable by collapsing the shim.
4. **Egress (W4)** — requires per-module classification; mid-effort.
5. **Write sovereignty (W5)** — largest, deferred; may require a separate plan.

## Phase-Level Summary

| Phase | Title | Scope | Pain Points | Est. Tokens | Status |
|---|---|---|---|---:|---|
| W1.1 | infra_wiring allow-list | `ops_scripts/ci/infra_wiring_scan.py` (SANCTIONED_ADAPTER_FILES) | Governance: are both files legitimate adapters? | 2k | in-progress |
| W2.1 | L6 obs re-export audit | `agentic_core/L6_observability/__init__.py` | How many distinct illegal imports? | 20k | todo |
| W3.1 | Spine MV allow-list | `tools/generate/materialized_views/*spine*` | Where does the spine definition live? | 15k | todo |
| W4.1 | L0 egress classification | `agentic_core/L0_routing/*` | 30+ modules, each needs provider wiring or non-action marker | 40k | todo |
| W5.1 | UWG write path audit | repo-wide | Systemic architecture change | 80k | todo |

## Success Criteria (per wave)

- W1: `infra_wiring` gate returns `passed` with 0 violations
- W2: `authority_boundary` reduced ≥ 50%
- W3: `critical_path_integrity` returns `passed` OR reduced to runtime-layer-only gaps
- W4: `capability_egress` reduced ≥ 50%
- W5: `write_sovereignty` reduced ≥ 30% (explicit stretch; may span multiple plans)

## Verification Loop

Each wave ends with `python tools/generate_full_adg.py` and examination of the new runner artifact under `artifacts/ci_gates/p0_runner_full_<ts>.json`.

## Deferred Scope

DEFERRED_SCOPE: plan=phase-b-blocker-burndown-a8c4f1 wave=W5 phase=W5.1 layer=L2 fan_in=100 surface=Write coverage_gap_pct=100.0 est_tokens=80000 reason=write_sovereignty UWG bypass systemic refactor
