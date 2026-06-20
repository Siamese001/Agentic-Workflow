---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\historical_plans_20260515_cursor_optimization\\dom007-fec-producers-followup-e9f3c1.md'
original_relative_path: '_archive\\historical_plans_20260515_cursor_optimization\\dom007-fec-producers-followup-e9f3c1.md'
source_sha256: 556f219348c62808786f624194aeda58d2a00134c64085d6366a9b0bb6ff3d83
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# DOM-007 FEC Producer Wiring · W4 Follow-up

**Slug:** `dom007-fec-producers-followup-e9f3c1`
**Status:** Completed (2026-05-03)
**Parent:** `apps-runtime-domain-enforcement-a7e9d4` (W4 deferred-scope items)
**Decision link:** Author-Gate `dec_19dedd3f565173b7f` (heuristic_split, captured 2026-05-03)

## AI Summary

Closes the 3 remaining DOM-007 (`c0_fec_bound`) FAILs surfaced by the W3.P1
APPS-DOM evidence emitter. apps_eval, apps_lic, and apps_rg each carry
rubric dimensions with `evidence_required: true` but ship no FEC producer
under `apps_<x>/cert/`. Without a producer, ExitReviewPacket.final_evidence_contract is `{}` for these
apps and the compiler cannot mark `apps_*` 100% signed off. This plan
ships 3 producers following the proven pattern from the 5 prior apps
(apps_qna, apps_underwriting_ai, apps_exec, apps_research, apps_rfp —
BLOCKER #4 closed 2026-05-03). After W4 of this plan completes, DOM-007
goes 5/8 PASS → 8/8 PASS, and the parent plan can advance to W5
(FEC presence + empty-judge-roster + OTEL field gates) without a stuck
DOM-007 row.

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---|---|---|---|
| W1 | W1.P1 | apps_eval FEC producer + cert init + tests | ~10k | apps_eval rubric stable; producer emits grader_calibration / taxonomy_correctness / no_self_contradiction provenance | Draft | DOM-007 row for apps_eval flips PASS in W3.P1 emitter |
| W2 | W2.P1 | apps_lic FEC producer + cert init + tests | ~10k | Mirror apps_qna pattern; LIC-specific source_ladder = profile_data / outreach_template / compliance_check | Draft | DOM-007 row for apps_lic flips PASS |
| W3 | W3.P1 | apps_rg FEC producer + cert init + tests | ~10k | Mirror apps_qna pattern; RG-specific source_ladder = jd_evidence / role_evidence / repo_signals | Draft | DOM-007 row for apps_rg flips PASS |
| W4 | W4.P1 | Verification + parent-plan unblock | ~3k | Re-run `tools/cert/apps_e2e/emit_apps_domain_enforcement_assertions.py`; confirm PASS=40 / FAIL=0 / NOT_VERIFIED=64 | Draft | All 3 DOM-007 deferrals closed; parent plan can advance to W5 |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| W1.P1 | apps_eval FEC producer | `apps_eval/cert/__init__.py` (new), `apps_eval/cert/fec_producer.py` (new), `apps_eval/__main__.py` (modify — resolve_fec call), `tests/_apps_contract/test_apps_eval_fec_producer.py` (new, 7 tests) | apps_eval rubric has 3 evidence_required dims (grader_calibration hybrid/0.25, taxonomy_correctness deterministic/0.20, no_self_contradiction deterministic/0.15). Producer must surface grader-calibration provenance — distinct from grounded-app pattern. | ~10k | Draft |
| W2.P1 | apps_lic FEC producer | `apps_lic/cert/__init__.py` (new), `apps_lic/cert/fec_producer.py` (new), `apps_lic/__main__.py` (modify), `tests/_apps_contract/test_apps_lic_fec_producer.py` (new, 7 tests) | apps_lic rubric has 4 evidence_required dims (audience_fit, personalization_integrity, compliance, brevity_and_channel_fit). Producer surfaces profile_data + outreach_template + compliance_check. Drafted plan apps-lic-c0-fec-producer-wiring exists from prior session — adopt or supersede. | ~10k | Draft |
| W3.P1 | apps_rg FEC producer | `apps_rg/cert/__init__.py` (new), `apps_rg/cert/fec_producer.py` (new), `apps_rg/__main__.py` (modify), `tests/_apps_contract/test_apps_rg_fec_producer.py` (new, 7 tests) | apps_rg rubric has 5 evidence_required dims (factual_grounding, role_alignment, executive_positioning, specificity, +1). Producer surfaces jd_evidence + role_evidence + repo_signals. Drafted plan apps-rg-c0-fec-producer-wiring exists — adopt or supersede. | ~10k | Draft |
| W4.P1 | Verification | `tools/cert/apps_e2e/emit_apps_domain_enforcement_assertions.py` (run, no edit) | Confirm DOM-007 → 8/8 PASS; capture `tests/_apps_contract` count delta; emit DECISION_OUTCOME marker for parent plan W4 closure. | ~3k | Draft |

## ADG_GRAPH_LAYER_EVIDENCE

Constitutional §22 requires graph-layer primitives drive T2/T3 plans. This is a T2 (3 apps × 4 files each = 12 files, single-layer = apps_*, no cross-layer). Graph-layer evidence:

- **MV `mv_dependency_cone_risk`** — confirms `apps_qna/cert/fec_producer.py` (the reference pattern) has zero downstream consumers outside its own app cone. The new producers will inherit the same isolation property; blast radius bounded to one app each.
- **MV `mv_chokepoint_bridges`** — `apps_shared/cert/exit_eval_hook.py` is the chokepoint that consumes registered producers. New registrations land via side-effect import in `apps_<x>/cert/__init__.py`; chokepoint MV invariants (single-import, no upward dep) preserved.
- **Semantic edge `flows_to`** — confirms producer → ExitReviewPacket.final_evidence_contract is the only flow path. No other consumer reads the FEC contract; producers do not bind to anything else.
- **P-view `v_p2_fec_producer_present`** (auto-discovered via apps_<x>/cert/ presence) — currently 5/8 apps registered; this plan flips count to 8/8.

## ADG_HOTSPOT_REPORT

| File | Layer | Fan-in | Hotspot Rank | Archetype | Surfaces | Impact |
|---|---|---|---|---|---|---|
| `apps_shared/cert/exit_eval_hook.py` | apps_shared | 5 (existing producers) → 8 (after) | n/a (chokepoint) | CENTRAL_DEPENDENCY | Execution, Observability | low — additive only; no behavior change |
| `apps_eval/__main__.py` | apps_eval | 1 (apps_eval entry) | n/a (leaf) | ORCHESTRATOR | Execution | low — single new resolve_fec call |
| `apps_lic/__main__.py` | apps_lic | 1 | n/a | ORCHESTRATOR | Execution | low |
| `apps_rg/__main__.py` | apps_rg | 1 | n/a | ORCHESTRATOR | Execution | low |

No L0/L5 boundary crossing. No safety-gatekeeper modification. All edits land in apps_* layer (apps doctrine layer, lower than L1 cognition). Layer multiplier 1.0; impact bounded.

## Files In Scope

- `apps_eval/cert/__init__.py` (new)
- `apps_eval/cert/fec_producer.py` (new)
- `apps_eval/__main__.py` (modify — single resolve_fec hook)
- `apps_lic/cert/__init__.py` (new)
- `apps_lic/cert/fec_producer.py` (new)
- `apps_lic/__main__.py` (modify)
- `apps_rg/cert/__init__.py` (new)
- `apps_rg/cert/fec_producer.py` (new)
- `apps_rg/__main__.py` (modify)
- `tests/_apps_contract/test_apps_eval_fec_producer.py` (new)
- `tests/_apps_contract/test_apps_lic_fec_producer.py` (new)
- `tests/_apps_contract/test_apps_rg_fec_producer.py` (new)

12 files. T2 plan.

## Producer Pattern (canonical, copied from apps_qna/apps_rfp)

```python
# apps_<x>/cert/fec_producer.py
from __future__ import annotations
from typing import Any

def produce_fec(run_context: dict[str, Any]) -> dict[str, Any]:
    sources = _resolve_sources(run_context)
    return {
        "schema_version": "1.0",
        "producer": "apps_<x>",
        "grounded": bool(sources),
        "retrieval_sources": sources,
        "template_ids": run_context.get("template_ids", []),
        "route_id": run_context.get("route_id"),
        "evidence_sufficiency": _grade_sufficiency(sources, run_context),
    }

def _resolve_sources(run_context):
    # App-specific source ladder; degrades to [] when run_context lacks keys
    ...

def _grade_sufficiency(sources, run_context):
    if not sources: return "insufficient"
    if len(sources) >= run_context.get("min_sources", 1): return "sufficient"
    return "partial"
```

```python
# apps_<x>/cert/__init__.py
from apps_shared.cert.fec_registry import register_producer
from apps_<x>.cert.fec_producer import produce_fec

register_producer("apps_<x>", produce_fec)
```

```python
# apps_<x>/__main__.py — add at exit-packet construction site:
import apps_<x>.cert  # noqa: F401 -- side-effect register
from apps_shared.cert.fec_registry import resolve_fec
exit_packet.final_evidence_contract = resolve_fec("apps_<x>", run_context)
```

## Test Pattern (canonical, mirrors prior 5 producers)

7 tests per producer (see memory `d367a9bc` test invariant):

1. `test_register_idempotent` — calling register_producer twice no-ops
2. `test_produce_fec_returns_schema_v1` — returns dict with `schema_version: "1.0"`
3. `test_grounded_false_when_no_sources` — empty run_context → `grounded: False`
4. `test_grounded_true_when_sources_present` — populated source ladder → `grounded: True`
5. `test_evidence_sufficiency_ladder` — sufficient/partial/insufficient transitions
6. `test_route_id_propagated` — run_context.route_id flows through
7. `test_resolve_fec_via_registry` — clear_registry + register_producer + resolve_fec returns producer output (per memory invariant: NEVER rely on import side-effect after clear_registry — call register_producer explicitly)

## Non-Goals

- No changes to existing 5 producers (apps_qna, apps_underwriting_ai, apps_exec, apps_research, apps_rfp).
- No changes to `apps_shared/cert/fec_registry.py` (chokepoint stable).
- No new judge implementations (out of scope; tracked in DEFERRED_SCOPE markers from W4 of parent plan).
- No exit-hook adoption rework (apps_exec, apps_research already deferred to other plans per memory).

## Gap Register

| Gap | Owner | Resolution |
|---|---|---|
| apps_eval producer pattern differs from grounded-app pattern (it grades grader-calibration, not retrieval-grounded output) | W1.P1 | Producer surfaces `grader_calibration_score`, `taxonomy_match_count`, `contradiction_check_status` instead of `retrieval_sources` |
| Drafted plans `apps-lic-c0-fec-producer-wiring` and `apps-rg-c0-fec-producer-wiring` may exist from prior sessions | W2.P1 / W3.P1 | Open them at wave start; supersede if drafts; mark Retired if duplicates |
| Test invariant: clear_registry must be followed by explicit register_producer call | All test phases | Use the canonical pattern from memory `d367a9bc`; never rely on sys.modules-cached import |

## Verification Plan (W4.P1)

1. Run `python tools/cert/apps_e2e/emit_apps_domain_enforcement_assertions.py`
2. Confirm output: `Emitted 104 APPS-DOM assertions: PASS=40 FAIL=0 NOT_VERIFIED=64`
3. Confirm DOM-007 row breakdown: `APPS-DOM-007    PASS= 8  FAIL= 0  NV= 0`
4. Run `pytest tests/_apps_contract/test_apps_eval_fec_producer.py tests/_apps_contract/test_apps_lic_fec_producer.py tests/_apps_contract/test_apps_rg_fec_producer.py -v` — all 21 tests green
5. Emit `DECISION_OUTCOME: decision_id=dec_19dedd3f565173b7f, execution_completed=1, tests_passed=1, regression_found=0, rollback_required=0, promote_to_pattern=1`

## AG_QUEUE_SEED

```
AG_QUEUE_SEED: plan=dom007-fec-producers-followup-e9f3c1 id=ag-w4-followup-superseded-drafts depends_on= title=Decide whether to supersede or open prior drafted plans (apps-lic-c0-fec-producer-wiring, apps-rg-c0-fec-producer-wiring)
```
