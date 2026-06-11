---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\06_shadow_eval_v6_requirements_matrix.md'
original_relative_path: '06_shadow_eval_v6_requirements_matrix.md'
source_sha256: 100fe62de525a9f58e1b201bc3a6e1602bec75767e28948beaf7bfd36587c244
recovered_status: LOST_RECOVERED
last_commit: 'dba31608679'
last_commit_date: '2026-04-26 21:01:43 -0400'
created_date: '2026-04-26'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# L6 Shadow-Eval Requirements Matrix — SUPERSEDED 2026-04-26

> ⚠️ **This file has been superseded.** The canonical SSOT is now co-located with doctrine at:
>
> **`docs/reference/06_L6_Shadow_Evaluation_System_Learning/v6_coverage_matrix.md`**
>
> This redirect mirrors the L5 precedent at `00A_L5_Governance_Safety/v5_coverage_matrix.md`.

## Why this file was rewritten

The prior matrix at this path covered only 9 of the 13 doctrine files in the
`06_L6_Shadow_Evaluation_System_Learning/` folder and **did not** flag four genuine implementation gaps. A
re-ingest on 2026-04-26 of all 13 doctrine files produced the new comprehensive matrix.

## Coverage delta vs. the prior matrix

The new matrix covers everything the old one did, **plus**:

1. **Full coverage of `06_Shadow_Evaluation_System_Learning_exec.md` (v5 normative file)** —
   - 6 RFC-2119 invariants (§1.1 Observer Law, §1.2 Eval-Before-Learning firewall, §1.3 Rubric integrity,
     §1.4 UWG Sole Ink Path, §1.5 No-Partial-Bypass, §1.6 Future-run only)
   - 11 KPIs with green/yellow/red tri-band thresholds
   - 14-row v4-step → module reference table

2. **Full coverage of `06.9_L6_Memory_Promotion_Interface.md`** —
   - `MemoryPromotionCandidate` (16 fields) — **NOT IMPLEMENTED**
   - `MemoryPromotionProposal` (9 fields) — **NOT IMPLEMENTED**
   - 4 doctrine rules and 5 named tests — **NOT IMPLEMENTED**

3. **Honest gap callouts** — four explicit ⚠️ gaps:

| Gap | Severity | Summary |
|---|:---:|---|
| **G1** | HIGH | `06.9` Memory Promotion Interface: 2 contracts + 5 named tests not implemented |
| **G2** | HIGH | v5 KPI tri-band semantics absent from impl `KPI_BOARD`; 3 v5 KPIs entirely missing (`replay_divergence_localization_pct`, `exemplar_hit_rate_pct`, `saturation_watch_pct`) |
| **G3** | MEDIUM | Trajectory flag taxonomy partial: doctrine §06.3 lists 14 detection conditions; impl emits 3. 12 detectors absent (route_thrash, tool_misuse, tool_overreach, hidden_scope_growth, unbounded_loop, skipped_C0_grounding, skipped_prompt_validation, premature_answer, stale_cache_reuse, excessive_model_escalation, non_replayable_behavior, unnecessary_HITL, missing_HITL) |
| **G4** | MEDIUM | Governance drift category population partial: `GovernanceRegressionRecord` has 15 typed fields; runtime populates only 4. 11 typed-but-never-populated fields require additional baselines |

4. **Doctrine-corpus inventory** — explicit listing of all 13 files with sizes, generations, and the
   confirmation that 06.2/06.3/06.7 each have two filename variants whose bodies are content-identical.

## Coverage rollup at a glance

| Category | Items | % |
|---|---:|---:|
| ✅ Enforced (runtime + tests) | ~453 | ~87% |
| 📦 Modeled (typed contract, partial population) | ~29 | ~6% |
| 🔁 Delegated to sibling/external | ~2 | <1% |
| ⚪ Doc-only / architectural | ~13 | ~2% |
| ⚠️ **GAP** (deferred, explicit) | ~25 | ~5% |
| **Total doctrine items** | **~522** | 100% |

Test surface: **301/301 passing**, **99.58% line+branch coverage** of `agentic_core/L6_observability/shadow_eval/`.

## Action items

The new matrix carries an Action Items section estimating ~18 hours of focused engineering to close G1–G4.
Each gap is **deferred, not silently absent**.

---

**For the full line-by-line evidence trail of every doctrine requirement, read:**
**`docs/reference/06_L6_Shadow_Evaluation_System_Learning/v6_coverage_matrix.md`**
