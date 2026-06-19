---
plan_id: shared-lane-skill-metric-skew-elimination-b4e8c1
plan_format: v2
plan_type: refactor
touches_agentic_core: false
touches_governance_ci: false
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
supersedes: []
---

# Shared Lane Skill And Metric Skew Elimination

Eliminate employer graph density skew from `executive_summary`, `headline`, and `competencies` without flattening the four employer graphs or deleting valid evidence. The graph remains the SSOT; shared lanes consume role-weighted, root-normalized slices of that graph.

> **plan_id discipline**: markers use `plan=shared-lane-skill-metric-skew-elimination-b4e8c1`.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: DONE
CURRENT_WAVE: W6
LAST_COMPLETED_WAVE: W6
LAST_UPDATED: 2026-06-12

---

## Context (SCQA)

- **Situation** - The four employer graphs are now company-scoped SSOTs for skills and metrics. Current counts are intentionally uneven: Unify has deep agentic roots, IBM has precise modernization/GTM roots, InsurTech has broad founder/CTO/insurance/AWS roots, and EY has dense actuarial/regulatory roots.
- **Complication** - Shared lanes traverse the full graph. If traversal uses raw eligible skill and metric rows, employers with more modeled rows get more selection opportunities. InsurTech currently has the highest unique skill count, while EY has the highest skills-per-root density. This can distort `executive_summary`, `headline`, and `competencies` before generation starts.
- **Question** - How do we remove selection skew without forcing artificial equal graph sizes or weakening the employer-specific evidence graph?
- **Answer** - Keep graph richness intact, but normalize shared-lane exposure. Introduce a deterministic shared-lane graph selection plan that scores employer roots by target-role relevance, caps skill and metric exposure by selected root, and emits diagnostics proving final selections came from role-weighted evidence rather than raw graph density.

---

## North Star

```text
Employer graphs may be as detailed as the truth supports.
Shared lanes may only consume capped, role-weighted evidence slices.

No employer wins because it has more skill rows.
No metric wins because its graph has more metric rows.
JD and briefing steer weighting only; they never create evidence.
```

---

## Status Tables

### Wave Progress

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1 | W1.1, W1.2 | Baseline skew audit | ~3K | Existing graph diagnostics expose employer/root/skill/metric mix | DONE | Current raw employer/root/skill/metric mix is emitted in `skew_diagnostics` |
| W2 | W2.1, W2.2 | Shared-lane selection contract | ~4K | Shared lanes can consume one common selected evidence contract | DONE | `selected_graph_evidence_plan` includes employer/root caps for skills and metrics |
| W3 | W3.1, W3.2, W3.3 | Role-weight and cap policy | ~5K | Role-profile caps can normalize exposure without graph flattening | DONE | Role-profile caps normalize exposure without equalizing graph sizes |
| W4 | W4.1, W4.2, W4.3 | Lane integration | ~5K | Shared-lane utilities can be reused by target lanes | DONE | `executive_summary`, `headline`, and `competencies` consume the same selection contract |
| W5 | W5.1, W5.2 | Validators and regression gates | ~4K | Regression tests can encode forbidden raw-density fallback behavior | DONE | Unit tests fail on raw skill-count dominance and selected root-cap leakage |
| W6 | W6.1, W6.2, W6.3 | Proof runs and closeout | ~4K | Target profiles cover the expected employer/root weighting modes | DONE | Target profiles prove employer/root/skill/metric mix matches expected weighting |

### Phase Progress

| Phase | Title | Status |
|---|---|---|
| W1.1 | Measure current raw graph density by employer, root, skill, and metric | DONE |
| W1.2 | Measure actual lane selections and expose skew diagnostics | DONE |
| W2.1 | Define `selected_graph_evidence_plan` schema | DONE |
| W2.2 | Define root-level skill and metric exposure fields | DONE |
| W3.1 | Add role-profile employer/root relevance scoring | DONE |
| W3.2 | Add per-root skill and metric caps | DONE |
| W3.3 | Add deterministic tie-breaks and audit rationales | DONE |
| W4.1 | Wire `executive_summary` to selected graph evidence | DONE |
| W4.2 | Wire `headline` to selected graph evidence | DONE |
| W4.3 | Wire `competencies` to selected graph evidence | DONE |
| W5.1 | Add skew guard tests for shared lanes | DONE |
| W5.2 | Add forbidden legacy fallback tests | DONE |
| W6.1 | Run AI partnerships / GTM profile proof | DONE |
| W6.2 | Run SVP agentic engineering profile proof | DONE |
| W6.3 | Run insurance IT strategy profile proof | DONE |

---

## Target Design

### Contract

Create one shared-lane evidence contract:

```text
selected_graph_evidence_plan
```

Required fields:

```text
section_id
target_role_profile
role_family_key
graph_weight_profile
selected_employer_roots
employer_root_weights
skill_caps_by_root
metric_caps_by_root
selected_nodes
selected_edges
selected_skills
selected_metrics
selected_employer_lanes
excluded_due_to_root_cap
excluded_due_to_metric_cap
allowed_graph_evidence_ids
selection_rationale
skew_diagnostics
```

### Selection Flow

```text
JD / briefing / target title
-> infer target_role_profile
-> score employer roots by role relevance
-> allocate root caps for skills and metrics
-> rank skills and metrics inside each selected root
-> select capped evidence
-> generate only from selected graph evidence
```

### Key Rule

```text
Normalize exposure, not graph content.
```

Valid graph richness remains untouched. The shared lanes receive only a capped slice.

---

## Cap Policy

### Do Not Use

Do not use raw global ranking alone:

```text
all eligible graph skills
-> sort by score
-> take top N
```

This preserves raw-count lottery bias.

### Use

Use root-normalized ranking:

```text
eligible roots
-> score roots by role profile
-> allocate root caps
-> select top skills and metrics within each root
```

Initial cap bands:

| Root Weight | Shared-Lane Skill Cap | Shared-Lane Metric Cap |
|---|---:|---:|
| Primary | 4-6 | 2-3 |
| Secondary | 2-4 | 1-2 |
| Tertiary | 1-2 | 0-1 |
| Context only | 0-1 | 0 |

The caps are per selected employer/root, not per employer graph total.

---

## Role Profiles

### SVP Agentic Engineering

Expected weighting:

| Employer | Expected Role |
|---|---|
| Unify | Primary |
| IBM | Secondary modernization/platform proof |
| InsurTech | Tertiary regulated cloud/operator proof |
| EY | Context-only risk/regulatory proof |

### AI Partnerships / GTM

Expected weighting:

| Employer | Expected Role |
|---|---|
| Unify | Primary AI platform commercialization and partner co-sell |
| IBM | Primary/secondary AWS alliance, pre-sales, offering management |
| InsurTech | Tertiary founder-led cloud GTM |
| EY | Context-only |

### Insurance IT Strategy / Brown & Brown Style

Expected weighting:

| Employer | Expected Role |
|---|---|
| InsurTech | Primary insurance cloud/platform/operator proof |
| EY | Secondary insurance/regulatory/risk proof |
| IBM | Secondary modernization, AWS, enterprise delivery proof |
| Unify | Tertiary AI/platform innovation proof |

---

## Lane Behavior

### `executive_summary`

New behavior:

```text
role profile
-> selected_graph_evidence_plan
-> 6-10 highest-signal graph evidence items
-> employer/root mix recorded before generation
```

Guardrail:

```text
No candidate-fact/SRFS allocation may determine evidence authority.
No employer may exceed configured root-cap share unless explicitly justified by role profile.
```

### `headline`

New behavior:

```text
role profile
-> selected 2-4 positioning roots
-> compact positioning evidence
```

Guardrail:

```text
Do not attach all headline bundles by default.
Headline must use selected positioning roots only.
```

### `competencies`

New behavior:

```text
role profile
-> selected skill roots
-> capped skills per root
-> capped metrics per root when metric-bearing competencies are allowed
```

Guardrail:

```text
Competencies cannot select skills only because one employer graph has more skill IDs.
```

---

## Validators

Add deterministic validators:

| Validator | Failure Condition |
|---|---|
| `shared_lane_raw_density_dominance` | Selected employer share materially exceeds role weight because of raw skill/metric count |
| `shared_lane_root_cap_violation` | Selected skills or metrics exceed cap for a root |
| `shared_lane_unselected_root_evidence_leakage` | Generated text cites graph evidence outside selected roots |
| `shared_lane_metric_cap_violation` | Metric-bearing evidence exceeds selected metric caps |
| `shared_lane_role_profile_variance` | Employer/root mix materially diverges from expected profile without rationale |
| `shared_lane_jd_as_proof_violation` | JD/briefing creates or substitutes graph evidence |

---

## Acceptance Criteria

- `executive_summary`, `headline`, and `competencies` all emit `selected_graph_evidence_plan`.
- Shared lanes no longer select from raw full-graph skill/metric pools without employer/root caps.
- InsurTech skill count no longer increases selection probability except through role relevance.
- EY dense bundles no longer increase selection probability except through role relevance.
- Unify agentic depth dominates only for agentic/AI-platform roles, not insurance IT strategy roles.
- IBM remains zero agentic-AI aligned and contributes only modernization, AWS, GTM, BI, customer success, and offering evidence.
- Every selected skill and metric has a root, employer lane, support level, and graph evidence ID.
- Every excluded high-scoring item records whether it was excluded by root cap, metric cap, section eligibility, or role irrelevance.
- Tests fail if a shared lane falls back to SRFS/candidate-fact authority as the primary proof contract.

---

## Out Of Scope

- Forcing all employer graphs to the same number of skills or metrics.
- Deleting valid employer evidence solely to equalize counts.
- Adding new claims or metrics not already present in graph SSOT.
- Refactoring employer-specific bullet/narrative lanes except where shared-lane utilities are reused.
- Changing final resume copy by hand to mask selection problems.

---

## Implementation Notes

- Start with diagnostics before changing selection. The first proof must show current skew.
- Use employer roots, not employer totals, as the cap unit. One employer can contribute multiple roots when the role truly calls for them.
- Metrics need separate caps from skills because metric density can skew executive summary and headline even when skill caps are correct.
- Keep tie-breaks deterministic: role score, support level, metric presence, section eligibility, then stable graph ID.
- Preserve rich employer graphs. The contract controls consumption, not truth.

---

## Closeout Evidence

Implemented:

- Shared-lane selector now traverses all four employer graphs for `executive_summary`, `headline`, and `competencies`.
- Selection emits `selected_graph_evidence_plan` with `target_role_profile`, employer/root weights, skill caps, metric caps, selected nodes/edges/skills/metrics, exclusions, and skew diagnostics.
- Prompt evidence packs for `headline` and `competencies` filter to selected role-profile families instead of attaching all bundles by default.
- Resolver metadata exposes `selected_graph_evidence_plan` before headline and competency bundle attachment.

Proof run summary for `competencies`:

| Profile | Selected Skill Mix | Selected Metric Mix |
|---|---|---|
| AI Partnerships / GTM | Unify 15, IBM 13, InsurTech 2, EY 1 | Unify 6, IBM 6, InsurTech 1, EY 0 |
| SVP Agentic Engineering | Unify 16, IBM 6, InsurTech 2, EY 1 | Unify 8, IBM 2, InsurTech 1, EY 0 |
| Insurance IT Strategy | InsurTech 15, EY 6, IBM 3, Unify 4 | InsurTech 6, EY 2, IBM 1, Unify 2 |

Verification:

```text
python -m py_compile apps_rg/runtime/sections/graph_role_episode_selector.py apps_rg/runtime/proof_pool_resolver.py apps_rg/runtime/sections/headline_positioning_evidence.py apps_rg/runtime/sections/competency_capability_evidence.py tests/unit/apps_rg/test_shared_lane_skew_elimination.py
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -p pytest_timeout tests/unit/apps_rg/test_shared_lane_skew_elimination.py -q
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -p pytest_timeout tests/unit/apps_rg/test_selected_role_fact_set_retirement_guard.py -q
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -p pytest_timeout tests/unit/apps_rg/test_competencies_capability_bundle_wiring.py -q
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -p pytest_timeout tests/unit/apps_rg/test_remaining_resume_rigor_finish.py::test_headline_positioning_bundles_validate_and_cover_families tests/unit/apps_rg/test_remaining_resume_rigor_finish.py::test_headline_config_enables_graph_only_in_bundle_mode tests/unit/apps_rg/test_remaining_resume_rigor_finish.py::test_competencies_anchor_injection_covers_uncovered_family tests/unit/apps_rg/test_remaining_resume_rigor_finish.py::test_competencies_anchor_injection_no_fabrication_without_allowed_fact -q
```
