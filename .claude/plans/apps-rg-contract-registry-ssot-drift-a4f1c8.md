---
plan_type: apps_rg_contract_refactor
slug: apps-rg-contract-registry-ssot-drift-a4f1c8
status: Complete
ai_summary: "Kill apps_rg registry drift: derive lane/judge/gate/proof-source registries from one SSOT + coverage gate."
dod_exempt: false
supersedes: []
---

# apps_rg Contract/Registry SSOT Drift — Generalize the Anti-Drift Fix

## Supersedes
| Predecessor slug | Reason |
|---|---|
| _None — net-new plan._ | |

## Relationship to `prompt-gate-ssot-consolidation-e7c9a2`
That plan fixes **prompt ↔ X2 numeric** drift (section counts/budgets/schema; W0 done, W1–W4 pending).
This plan fixes the **non-numeric contract/registry** drift the ADG audit surfaced (lane taxonomy, judge
roster, gate-ID parity, proof-source string, fact-namespace stamping) and adds the **registry-coverage
gate** that is the non-numeric analog of that plan's W4 numeric-equality gate. To avoid double-tracking:
**D4 (numeric hardcodes) and the role-lane parity-lie cleanup stay in `e7c9a2` W2/W5**; this plan owns
the registry-derivation + coverage layer and only references them.

## Context (SCQA)

- **Situation.** apps_rg generates 11 lanes through a U0→L1→L0→C0→L2→X1D→X2→X3 spine. The recently-fixed
  prompt drift was one instance of a **general pattern**: a logical contract is authored in several
  independent places with no programmatic binding, and the copies silently diverge.
- **Complication (audited via ADG snapshot `06082026_1212`, layer `L_APP`).** The same pattern recurs
  across **five more contract families**, three already failing live:
  1. **Lane taxonomy** — canonical `GENERATED_LANES` (11) exists, but 3 downstream registries omit the 4
     role lanes (insurtech/ey) → live `KeyError` in `lane_x2_x1d_spec`, failing adversarial + lockstep tests.
  2. **Judge roster** — two stale 3-provider lists (`anthropic_claude` included) survive the 2026-06-08
     recalibration and still feed the CI/proof harness default, diagnostics, and the transport proof-keys.
  3. **Gate-ID advertise↔emit parity** — role lanes advertise gates they never emit (parity lies).
  4. **Numeric constants** — mostly *clean* (product_shape_ssot imports from rigor; 6→8 done) — residual
     hardcodes only → owned by `e7c9a2` W2.
  5. **Proof-source / fact-namespace** — `"augmented_skills_graph"` re-typed in 6+ files; insurtech/ey
     lanes have **no bullet-ID stamping** (unify/ibm do) → they cannot namespace facts.
- **Question.** How do we make these registries *structurally unable* to diverge from their SSOT?
- **Answer.** For each family: (1) name **one canonical SSOT**, (2) make every consumer **derive from it**
  (import, not re-type), (3) add a **registry-coverage gate** that fails CI when any registry ≠ its SSOT
  (lane set, judge panel, advertised⊆emitted, proof-source literal). Fix the live blockers first.

## Status Tables

### Wave Progress
| Wave | Phase IDs | Focus | Est. Tokens | Status | Success Criteria |
|---|---|---|---|---|---|
| W0 | P0 | **Lane taxonomy (D1)** — the live `KeyError`/test blocker | ~110k | ✅ Complete | `_LANE_MODULE_IMPORT`, alignment-matrix JSON, `LANE_RUBRIC_MODULES` all cover the 4 role lanes (derived from `GENERATED_LANES`); `lane_x2_x1d_spec`/lockstep/adversarial tests green for insurtech/ey |
| W1 | P1 | **Judge roster (D2)** — finish the recalibration propagation | ~70k | ✅ Complete | No judge constant contains `anthropic_claude`; harness default + transport proof-keys + diagnostics derive from the recalibrated panels |
| W2 | P2 | **Proof-source + namespace (D5)** | ~90k | ✅ Complete | `PROOF_SOURCE_AUGMENTED_SKILLS_GRAPH` imported everywhere (0 re-typed); insurtech/ey bullet-ID stamping exists; alias map computed once |
| W3 | P3 | **Gate-ID parity (D3)** — role-lane lies + advertise-subset contract | ~70k | ✅ Complete | Role lanes emit (or stop advertising) the style/discipline gates; unify/ibm "lies" verified (helper-registered vs real) |
| W4 | P4 | **Registry-coverage gate (D6)** — the durable fix | ~80k | ✅ Complete | New CI gate fails on any registry ≠ SSOT; wired into the 3 existing audits + CI |

### Phase-Level Summary
| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| P0 | Lane taxonomy derivation | `section_x2_x1d_contract.py`, `x2_x1d_alignment_matrix.json`, `graph_skills_x1d_rubric_contract.py`, (+ role-lane x1d rubric/judge) | role lanes half-wired; new judge modules may be needed | ~110k | ✅ |
| P1 | Judge roster propagation | `section_judge_policy.py`, `executive_summary_x2.py`, `x1d_judge_policy.py`, `x1d_lane_judge_diagnostics.py`, `x1d_judge_transport_contract.py` | two parallel stale 3-lists + 3 consumers | ~70k | ✅ |
| P2 | Proof-source + namespace | `proof_pool_resolver.py`, `proof_pool_source_fact_validation.py`, `competencies_graph_skills_proof_pool.py`, `product_evidence_authority.py`, `canonical_section_evidence_set.py` | 6+ re-typed literals; missing role-lane stamping | ~90k | ✅ |
| P3 | Gate-ID parity | `section_product_shape_ssot.py`, `role_episode_lane.py`, `section_x2_x1d_contract.py` | advertise-subset semantics; helper-registration false positives | ~70k | ✅ |
| P4 | Coverage gate | `ops_scripts/ci/check_apps_rg_registry_coverage.py` (new), the 3 existing audits | must not flag intentional advertise-subset | ~80k | ✅ |

## The Drift Inventory (ADG-grounded evidence)

> Snapshot `adg_indexed_06082026_1212.sqlite`; all targets layer `L_APP`. `section_judge_policy.py`=node 3907,
> `section_x2_x1d_contract.py`=4012, `section_product_shape_ssot.py`=4006.

### D1 — Lane taxonomy fan-out (HIGH · partly LIVE)
- **Canonical SSOT:** `GENERATED_LANES` (11 lanes) — `apps_rg/runtime/internal/generated_lane_rollup.py:97-109`.
- **Lagging registries (omit insurtech_bullets, insurtech_narrative, ey_bullets, ey_narrative):**
  - `_LANE_MODULE_IMPORT` (7) — `section_x2_x1d_contract.py:31-39`.
  - `x2_x1d_alignment_matrix.json` (7 generated + 3 locked) — `artifacts/apps_rg/prompt_authority/x2_x1d_alignment_matrix.json`.
  - `LANE_RUBRIC_MODULES` (7) — `graph_skills_x1d_rubric_contract.py:91-99` (and no `*_x1d` judge module exists for the role lanes).
- **In sync (have all 11 / 4 role lanes):** `section_judge_policy` (`_SECTION_POLICIES`), `section_product_shape_ssot` (`_SECTION_BUILDERS`), `section_execution_plan` (`BULLET_LANES`/`NARRATIVE_LANES`), `role_episode_lane` (`_ROLE_LANES`).
- **Live symptom:** `lane_x2_x1d_spec(section_id)` (`section_x2_x1d_contract.py:99-107`) passes the `GENERATED_LANES` membership check, then raises `KeyError: alignment matrix missing x1d_judge_profile_ref for <role lane>`. This is the root cause of `test_executive_summary_x2_x1d_adversarial` (insurtech/ey + cascaded executive_summary) and `test_section_prompt_judge_lockstep` failures.
- **Fix:** make the 3 lagging registries derive from `GENERATED_LANES`; supply a role-lane x1d rubric/judge profile (shared `role_episode_x1d` is acceptable — one profile, 4 lanes) so `LANE_RUBRIC_MODULES` + the alignment matrix cover them. `final_aggregate` is intentionally absent from `GENERATED_LANES` — confirm and document, do not add.

### D2 — Judge roster recalibration loose ends (HIGH · partly LIVE)
- **Canonical SSOT:** the recalibrated panels — `_DUAL_JUDGE_PANEL=("gemini_pro","openai_chatgpt")`, `_SINGLE_JUDGE_PANEL=("gemini_pro",)` and `get_section_judge_policy(...).required_judge_providers` (`section_judge_policy.py:57-58`).
- **Stale shadows (both still include `anthropic_claude`, the dropped self-judge):**
  - `REQUIRED_JUDGE_PROVIDER_KEYS = ("gemini_pro","openai_chatgpt","anthropic_claude")` — `section_judge_policy.py:26-30` (sits directly above the recalibration comment at :53-56 that says anthropic_claude was dropped). Consumed by `PROOF_JUDGE_PROVIDER_KEYS` — `x1d_judge_transport_contract.py:38,42`.
  - `REQUIRED_JUDGE_PROVIDERS = ["gemini_pro","openai_chatgpt","anthropic_claude"]` — `executive_summary_x2.py:384`. Consumed by the **CI/proof harness default** `APPS_RG_E2E_DEFAULT_X1D_JUDGES` (`x1d_judge_policy.py:20,23,78`) and the **diagnostics rollup** (`x1d_lane_judge_diagnostics.py:13,251`); also imported by `competencies_x2.py:16`, `ibm_bullets_x2.py:15`, `unify_bullets_x2.py:16`.
- **What W0-A already fixed:** the *gate evaluation* (`x2_x1d_required_judges_present`) now derives per-lane via `required_judges_for_section()`. **It did NOT fix the harness default / diagnostics / transport proof-keys** — those still demand 3 judges incl. anthropic_claude.
- **Fix:** make both legacy constants derive from the panels (e.g. `REQUIRED_JUDGE_PROVIDER_KEYS = _DUAL_JUDGE_PANEL`; harness default = union of policy panels = `(gemini_pro, openai_chatgpt)`); drop the dead `executive_summary_x2.REQUIRED_JUDGE_PROVIDERS` or alias it to the policy. Verify each importer (`competencies_x2`, bullets) no longer needs the 3-list.

### D3 — Gate-ID advertise↔emit parity (MEDIUM)
- **Confirmed lie (role lanes):** `_role_bullets_shape` advertises `style_gate_ids=("x2_no_first_person","x2_no_em_dash")` + `x2_{lane}_bullet_single_thought` + `x2_{lane}_bullet_no_embedded_newline` (`section_product_shape_ssot.py:521-531`); `role_episode_lane._x2_gates` does not emit them. `_role_narrative_shape` similarly (:543+).
- **VERIFY (likely false positive):** unify/ibm bullet/narrative "advertised-not-emitted" gates are probably registered via helpers (`register_bullet_line_discipline_x2_gates` / `register_narrative_mechanical_x2_gates`) the static scan didn't trace — confirm before changing anything (prior `x2_severity` work already routes `x2_no_em_dash`/`x2_no_first_person` as WARN for these lanes, implying they ARE emitted).
- **By design (document, don't "fix"):** validators emit 20-60 gates; shape blocks advertise only the ~10 critical ones. The advertise set is intentionally a **subset** — the parity contract is `advertised ⊆ emitted`, not `==`.
- **Fix:** for role lanes, emit the advertised style/discipline gates (preferred — they're real quality guards) OR stop advertising them; encode the `advertised ⊆ emitted` contract so the coverage gate (D6) enforces it. `compile_hints` still say `qwen_pool_paths=` — relabel (Qwen removed).

### D4 — Numeric constant hardcodes (LOW · no live divergence) → owned by `e7c9a2` W2
- product_shape_ssot is already a sound numeric SSOT (imports `EXEC_SUMMARY_*` from `executive_summary_x2`, category counts from `competencies_rigor`); values agree everywhere and the 6→8 migration is clean.
- Residual hardcode/dup only: `unify_narrative_x2.py:483` (`<=58 and <=360` literals), `role_episode_lane.py:65-66` (re-declared `NARRATIVE_MAX_WORDS/CHARS`). **No fix here — tracked by `e7c9a2` W2.**

### D5 — Proof-source string + fact-namespace stamping (MEDIUM/HIGH for role lanes)
- **Proof-source literal:** canonical `PROOF_SOURCE_AUGMENTED_SKILLS_GRAPH="augmented_skills_graph"` — `proof_pool_resolver.py:62`. Re-typed (not imported) in `proof_pool_source_fact_validation.py:33`, `competencies_graph_skills_proof_pool.py:178,181,229,292`, and a dead private `_PROOF_SOURCE_AUGMENTED_SKILLS_GRAPH` — `product_evidence_authority.py:23`.
- **Fact-namespace stamping:** `_stamp_unify_canonical_bullet_ids` / `_stamp_ibm_canonical_bullet_ids` exist (`proof_pool_resolver.py`); **no insurtech/ey equivalents** even though validators forbid/expect `bul_insurtech_`/`bul_ey_` prefixes → role lanes can't namespace facts (would fail `detect_id_namespace_split_without_alias`). Ties to D1 (completing role lanes).
- **Alias map:** `id_alias_map` rebuilt in 3 places (`canonical_section_evidence_set.py`, `canonical_evidence_x2.py`, `proof_pool_source_fact_validation.py`) instead of computed once and passed.
- **Fix:** export+import the proof-source constant (0 re-typed); add role-lane stamping (or a generic per-lane stamper keyed off the lane prefix); compute the alias map once in the resolver and carry it on the pool.

### D6 — No registry-coverage / derivation gate (the durable fix)
- The three existing audits (`section_prompt_drift_audit`, `section_prompt_judge_alignment`, `section_x2_x1d_contract`) check presence/dimensions/gate-ID-sets but **never assert a registry equals its SSOT**. Same blind spot that let the prompt numbers drift.
- **Fix:** add `ops_scripts/ci/check_apps_rg_registry_coverage.py` asserting: (a) every lane registry == `GENERATED_LANES`; (b) no judge constant contains `anthropic_claude` and harness/transport keys == policy panels; (c) per lane, advertised gate IDs ⊆ emitted; (d) `"augmented_skills_graph"` appears only via the imported constant. Wire into CI + the existing audit suite.

## ADG_GRAPH_LAYER_EVIDENCE
- **Snapshot:** `adg_indexed_06082026_1212.sqlite` (182,313 nodes / 1,072,457 edges); `adg_health` = `ok`, sqlite healthy, projection fresh.
- **Modules confirmed (layer L_APP):** `section_judge_policy` (node 3907) exports `all_canonical_section_policies`, `normalize_section_id`, `REQUIRED_JUDGE_PROVIDER_KEYS`; `section_x2_x1d_contract` (4012) exports `all_lane_x2_x1d_specs`, `lane_x2_x1d_spec`, `audit_lane_x2_x1d_drift`, `extract_runtime_x2_gate_ids`; `section_product_shape_ssot` (4006) exports the numeric constants + `RETIRED_*_X2_GATE_IDS` + per-lane shape builders.
- **Surfaces intersected (per ADG 5-surface map):** **Security/guardrail** (X2 gate parity, judge roster), **Write/Evidence** (proof-pool/FEC namespace), **Observability** (diagnostics/transport judge keys). Archetype: these registries are `CENTRAL_DEPENDENCY` nodes (fan-out to every lane) — a wrong row poisons all consumers, which is why drift here is high-blast-radius.
- **Derivation note:** import-edge fan-in for the policy/contract modules is not materialized at symbol level in this snapshot (L_APP), so consumer mapping above was confirmed by content reads, not edge walks — recorded as DERIVED, not graph-observed.

## Definition of Done
| # | Criterion | Verification |
|---|---|---|
| 1 | Lane registries all cover the 11 `GENERATED_LANES` | `lane_x2_x1d_spec("insurtech_bullets"/"ey_*")` returns a spec (no KeyError); `test_executive_summary_x2_x1d_adversarial` + `test_section_prompt_judge_lockstep` green |
| 2 | No judge constant contains `anthropic_claude` | grep audit = 0 hits in roster/key constants; harness default == policy panels |
| 3 | Proof-source literal imported, not re-typed | grep: `"augmented_skills_graph"` literal appears only at its definition; all others import the constant |
| 4 | insurtech/ey can namespace facts | role-lane stamping present; `detect_id_namespace_split_without_alias` passes for a role-lane fixture |
| 5 | Registry-coverage gate green + fails on injected drift | `check_apps_rg_registry_coverage.py` passes; flipping one registry red makes it fail |
| 6 | Smoke: app still runs | `python -m apps_rg --section executive_summary` (or a role-lane lane) exits 0 with no new X3_BLOCK from registry drift |

## Safety / Invariants
- Never weaken a gate or judge requirement to "match" — reconcile toward the *correct* contract (drop
  `anthropic_claude` because the recalibration dropped it; cover role lanes because they generate), then
  bind consumers to the SSOT.
- Role-lane wiring (D1/D5) must not silently lower proof rigor for insurtech/ey — they get the same
  X2↔X1D contract as unify/ibm, just sourced from the shared role profile.
- The coverage gate (D6) is the durable guarantee — without it, registry drift returns.
- Stay in `apps_rg`; no `agentic_core` edits (no core boundary receipt needed).
