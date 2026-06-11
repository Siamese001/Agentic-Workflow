---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\apps-rg-stub-gap-closure-f4b2e1.md'
original_relative_path: 'apps-rg-stub-gap-closure-f4b2e1.md'
source_sha256: 15363776d551bafdd6b98a4614a0dc55a806582375e45e2604e6a51fe96b60d9
recovered_status: SURVIVED_IN_CURRENT
last_commit: '153652b9eb3'
last_commit_date: '2026-06-07 06:37:48 -0400'
created_date: '2026-05-11'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: apps-rg-stub-gap-closure-v2
plan_slug: apps-rg-stub-gap-closure-f4b2e1
plan_type: gap-closure
status: NOT_STARTED
active_authority: true
parent_plan: apps-rg-zip-based-full-spine-runtime-restoration-a3f7e2
created: "2026-05-11"
revised: "2026-05-11"
created_for: apps_rg
review_source: "Notion page 35d27693-f55c-8102-aee5-d0e3c68a273a"
---

# apps_rg Stub Gap Closure Plan (Governance-Corrected)

Identifies stubs found in the completed `apps-rg-zip-based-full-spine-runtime-restoration-a3f7e2`
plan and defines the closure roadmap. **Scope is strictly `apps_rg/` config and entrypoint only.**

## Governance Constraint (non-negotiable)

The entire RB1–RB16 architecture rests on one invariant:

> **`agentic_core/` is app-agnostic. apps_rg feeds U0. Core enforces contracts.**

Any stub inside `agentic_core/` is **intentional generic infrastructure** — it is correct-by-design
and is upgraded as a cross-app concern, not as an apps_rg fix. This plan **must not touch
`agentic_core/`** or it breaks governance for all other `apps_*`.

---

## Full Stub Inventory With Governance Classification

> Evidence collected 2026-05-11 via grep scan.

| # | Stub ID | File | In Scope? | Governance Ruling |
|---|---------|------|-----------|-------------------|
| S-01 | `executive_positioning_judge` quarantined | `apps_rg/engines/judges/__init__.py` | ✅ YES | Judge implementation belongs in **core** (`agentic_core/runtime/judges/`); apps_rg wires via profile ref in config only. Quarantine is correct — apps_rg must not own runtime authority. |
| S-02 | `role_alignment_hybrid_v1` `is_stub=True` | `apps_rg/config/domain_contract/grader_roster.yaml` | ✅ YES — config only | Update roster to point to real `LLM_AS_JUDGE` profile ref. Core gateway already handles it. No `agentic_core/` changes. |
| S-03 | `specificity_hybrid_v1` `is_stub=True` | `apps_rg/config/domain_contract/grader_roster.yaml` | ✅ YES — config only | Same as S-02. |
| S-04 | `_invoke_stub_judge` SHA-256 fake score | `agentic_core/runtime/judges/llm_judge_gateway.py` | ❌ OUT OF SCOPE | Correct-by-design. Activated only when app config sets `is_stub=True` on a profile. Fix = apps_rg config (S-02/S-03), not core code. |
| S-05 | `_invoke_deterministic_judge` hardcoded 0.85 | `agentic_core/runtime/judges/llm_judge_gateway.py` | ❌ OUT OF SCOPE | Core placeholder from RB13. Upgrade is a **cross-app core task** (benefits all apps). Not apps_rg-specific. Tracked separately. |
| S-06 | `_invoke_stub` provider gateway | `agentic_core/runtime/providers/provider_gateway.py` | ❌ OUT OF SCOPE | Intentional CI/dry-run path. Activated only via `APPS_RG_L2_FORCE_STUB=1`. Correct behavior. |
| S-07 | `llm_judge_stub` provider profile | `apps_rg/config/provider_profiles.yaml` | ✅ YES — audit only | Verify this profile is never referenced from production grader roster. Read-only audit; no code change. |
| S-08 | `executive_positioning_judge_stub` profile | `apps_rg/config/provider_profiles.yaml` | ✅ YES — config | Update profile once core judge implementation exists. Depends on S-01 core work. |
| S-09 | Guarded activation profile null fields | `apps_rg/config/domain_contract/activation_profile.resume_generation.guarded.v1.json` | ✅ YES — config only | Fill the null template fields. Pure config, no code. |
| S-10 | UWG `del tenant_id` no-op | `agentic_core/L3_orchestration/exit_eval/v6/uwg.py` | ❌ OUT OF SCOPE | Docstring explicitly says "Production swaps these for real backends without changing the sub-flow." Cross-app core concern. |
| S-11 | `prove_requirements` phases 2–8 | `agentic_core/runtime/prove_requirements/__init__.py` | ❌ OUT OF SCOPE | Core certification infrastructure. Separate cert plan. |
| S-12 | `stub_pending_*` exit path | `apps_rg/__main__.py` | ✅ YES — cleanup | Safe to remove if no live code path returns `stub_pending_`. Audit + remove. |
| S-13 | `decisive_reason = "stub_executor"` fallback | `agentic_core/L3_orchestration/managed_workflow_runner.py` | ❌ OUT OF SCOPE | Defensive guard in core L3 runner. Correct behavior — cross-app concern. |
| S-14 | `DeterministicGradeResult(is_stub=True)` fallback | `agentic_core/evaluation/judges/deterministic_graders.py` | ❌ OUT OF SCOPE | Fail-closed fallback (returns score=0.0) when no grader registered. Correct-by-design. apps_rg registers graders via roster config. |

---

## Corrected In-Scope Stubs (apps_rg/ only)

| # | Stub | File | Action |
|---|------|------|--------|
| S-01 | `executive_positioning_judge` QUARANTINED | `apps_rg/config/domain_contract/judge_profile.resume_generation.v1.json`, `apps_rg/config/provider_profiles.yaml` | Author judge implementation in **`agentic_core/runtime/judges/resume_judges/executive_positioning.py`** (core owns execution). Wire apps_rg to it via `provider_profile_ref` in config only. |
| S-02 | `role_alignment_hybrid_v1` `is_stub=True` | `apps_rg/config/domain_contract/grader_roster.yaml` | Change `ensemble_or_consensus_graders` entry to reference a real `LLM_AS_JUDGE` profile (not `llm_judge_stub`). |
| S-03 | `specificity_hybrid_v1` `is_stub=True` | `apps_rg/config/domain_contract/grader_roster.yaml` | Same as S-02. |
| S-07 | `llm_judge_stub` profile audit | `apps_rg/config/provider_profiles.yaml` | Confirm profile is not referenced from production roster paths. Advisory audit only. |
| S-09 | Guarded activation profile null fields | `apps_rg/config/domain_contract/activation_profile.resume_generation.guarded.v1.json` | Fill null fields per template instructions. |
| S-12 | `stub_pending_*` exit path | `apps_rg/__main__.py` | Audit + remove dead branch if confirmed unreachable. |

**Out-of-scope stubs (S-04, S-05, S-06, S-08, S-10, S-11, S-13, S-14):** Correct-by-design core
infrastructure or cross-app concerns. Tracked in a separate core-upgrade backlog item, not here.

---

## Gap Analysis Summary (corrected)

| Category | In-Scope Stubs | Risk | Notes |
|----------|---------------|------|-------|
| **Judge config** (S-02, S-03) | 2 | HIGH — G22 hybrid dims return stub scores | Fix is roster YAML only |
| **Judge implementation** (S-01) | 1 | MEDIUM — informational_only so no hard fail | Core impl + apps_rg config ref |
| **Activation profile** (S-09) | 1 | MEDIUM — template incomplete | Config fill |
| **Provider audit** (S-07) | 1 | LOW — audit only | No code change |
| **Entrypoint cleanup** (S-12) | 1 | LOW — dead code | Remove dead branch |

---

## Wave Structure (corrected)

| Wave | Focus | Stubs | Files Changed | Status |
|------|-------|-------|---------------|--------|
| W-J1 | Wire hybrid grader roster to real LLM profiles | S-02, S-03 | `apps_rg/config/domain_contract/grader_roster.yaml`, `apps_rg/config/provider_profiles.yaml` | Not Started |
| W-J2 | Author executive_positioning judge in core + wire apps_rg config | S-01, S-07, S-08 | `agentic_core/runtime/judges/resume_judges/executive_positioning.py` (NEW core file), `apps_rg/config/domain_contract/judge_profile.resume_generation.v1.json`, `apps_rg/config/provider_profiles.yaml` | Not Started |
| W-A1 | Complete guarded activation profile | S-09 | `apps_rg/config/domain_contract/activation_profile.resume_generation.guarded.v1.json` | Not Started |
| W-P2 | Remove stub_pending_ dead branch | S-12 | `apps_rg/__main__.py` | Not Started |

> **W-J2 note**: The judge implementation file lands in `agentic_core/runtime/judges/resume_judges/`
> because core owns execution. apps_rg contributes only the config profile ref pointing at it.
> This is consistent with the RB1–RB16 U0 feed model — apps_rg config → core enforcement.

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| W-J1.P1 | Update grader roster hybrid entries to real LLM profiles | `apps_rg/config/domain_contract/grader_roster.yaml`, `apps_rg/config/provider_profiles.yaml` | Replace `provider_profile_ref: llm_judge_stub` with `local_qwen_generator`; remove `is_stub` flag from ensemble entries | ~1k | Not Started |
| W-J1.P2 | Add tests confirming hybrid graders no longer return stub scores | `tests/_apps_contract/` | New test asserting score != stub hash pattern when real provider available | ~2k | Not Started |
| W-J2.P1 | Author `executive_positioning` judge in core | `agentic_core/runtime/judges/resume_judges/executive_positioning.py` (NEW) | LLM-as-judge; rubric from `apps_rg/config/eval_rubrics.yaml#executive_positioning`; `informational_only=True` by default; provider `local_qwen_generator` | ~4k | Not Started |
| W-J2.P2 | Wire apps_rg config to core judge | `apps_rg/config/domain_contract/judge_profile.resume_generation.v1.json`, `apps_rg/config/provider_profiles.yaml` | Update `grader_status` from `stub` → `active`; remove `stub_quarantined` profile; point `judge_implementation_ref` at new core module | ~1k | Not Started |
| W-A1.P1 | Fill guarded activation profile null fields | `apps_rg/config/domain_contract/activation_profile.resume_generation.guarded.v1.json` | Fill `null` fields per template; leave `provider_mode: stub_only` unchanged (correct for guarded) | ~1k | Not Started |
| W-P2.P1 | Remove stub_pending_ branch from __main__ | `apps_rg/__main__.py` | Confirm no live path returns `stub_pending_`; remove dead branch | ~1k | Not Started |

---

## Definition of Done

| # | Criterion | Verification |
|---|-----------|-------------|
| DoD-1 | `role_alignment_hybrid_v1` and `specificity_hybrid_v1` roster entries reference `local_qwen_generator`, not `llm_judge_stub` | `grep llm_judge_stub apps_rg/config/domain_contract/grader_roster.yaml` returns 0 hits |
| DoD-2 | `executive_positioning` judge exists in core and is importable | `python -c "from agentic_core.runtime.judges.resume_judges.executive_positioning import ExecutivePositioningJudge"` exits 0 |
| DoD-3 | apps_rg config profile points at core judge (no quarantine RuntimeError) | `python -m apps_rg --dry-run` exits 0; no RuntimeError in output |
| DoD-4 | Guarded activation profile has no null fields | `python -c "import json; d=json.load(open('apps_rg/config/domain_contract/activation_profile.resume_generation.guarded.v1.json')); assert None not in d.values()"` exits 0 |
| DoD-5 | `stub_pending_*` branch removed from `__main__.py` | `grep stub_pending apps_rg/__main__.py` returns 0 hits |

### Verification-vs-Deferral

| Item | Verify in this plan | Defer |
|------|--------------------|----|
| executive_positioning Qwen 32B live call | W-J2 smoke DoD-3 | Full calibration to separate judge-calibration plan |
| Core deterministic grader upgrade (S-05 hardcoded 0.85) | No — out of scope | Separate cross-app core-upgrade plan |
| UWG tenant ACL real backend (S-10) | No — out of scope | Separate core L3 upgrade plan |
| Guarded activation → live_allowed promotion | No — guarded stays `stub_only` by design | Separate production-activation approval wave |

---

## Hard Invariants

- `agentic_core/` changes in this plan are limited to **one new file** (`resume_judges/executive_positioning.py`) which is generic judge infrastructure, not apps_rg-specific logic.
- apps_rg contributes **config only** — no runtime authority, no provider calls from `apps_rg/`.
- `executive_positioning` judge remains `informational_only=True` unless explicit Author-Gate policy change.
- `UNKNOWN` is never `PASS`. If the judge cannot score, it abstains; the gate treats abstain as informational (not a hard block) for this dimension only.

---

## Scope Boundaries

- **In scope**: S-01, S-02, S-03, S-07 (audit), S-09, S-12 — all `apps_rg/` config/entrypoint plus one new core judge file (W-J2.P1).
- **Out of scope**: S-04, S-05, S-06, S-08, S-10, S-11, S-13, S-14 — all correct-by-design core stubs.
- **Do not** touch `agentic_core/runtime/judges/llm_judge_gateway.py` — the hardcoded 0.85 is a cross-app core concern.
- **Do not** touch `agentic_core/L3_orchestration/exit_eval/v6/uwg.py` — tenant ACL is a cross-app core upgrade.
- **Do not** touch any other `apps_*`.
- **Do not** unquarantine `apps_rg/engines/judges/` — the quarantine is correct.
