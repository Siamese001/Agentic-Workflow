---
plan_id: apps-lic-completeness-graph-grounding-ssot-e7b2c4
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

# apps_lic Completeness — Grounding Graph + Reasoning/Model SSOT (vs apps_rg model)

First-principles review of apps_lic measured against apps_rg's (assumed-complete) model, then a prioritized plan to close the gaps. apps_lic is smaller/flatter than apps_rg (no multi-section synthesis, no DOCX; "lanes" = 5 message-types x 4 recipient-classes), but its grounded-content backbone is stubbed and its model/reasoning SSOT carries the exact drift classes that cost apps_rg.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: IN_PROGRESS
CURRENT_WAVE: W5
LAST_COMPLETED_WAVE: W4
LAST_UPDATED: 2026-06-15

---

## Context (SCQA)

- **Situation** — apps_lic ("Lifecycle Intelligence & Communication") is the LinkedIn-outreach follow-up to apps_rg: the same candidate sends short, grounded, compliant messages to recruiters / Senior TA / execs / C-level at a target company. Generation runs on local Qwen vLLM (Qwen2.5-32B-AWQ, fail-closed via APPS_LIC_REQUIRE_QWEN_VLLM=1); X1D judging is intended on Claude Sonnet 4.6. 9 waves since the W0 freeze (2026-06-08) built the reasoning/judge spine (SC-0..SC-3, reasoning_intensity policy, X2 gates, X1D, Exit dispositions, repair loop).
- **Complication** — Two problem classes remain: (1) the grounded-content backbone is a STUB — C0.3 sender proof graph returns empty (c0_graph_adapter), C0 evidence is inline-payload-only, and apps_lic re-derives a weaker version of apps_rg's candidate proof (flat candidate_skills, per-run achievement whitelisting) with no shared SSOT; (2) the model/reasoning SSOT carries apps_rg-class drift — X1D provider points at the superseded qwen_vllm_x1d judge while the canonical/frozen judge is Claude Sonnet 4.6; the frozen "2 judge passes for C-level" is unimplemented; "X2 deterministic gates" are actually LLM judges; the generator model has no YAML SSOT (env-pin chain || default).
- **Question** — How do we make apps_lic *complete* (grounded, recipient-fit, auditable, all lanes passing) without repeating apps_rg's model/orchestration mistakes?
- **Answer** — Reconcile the model/reasoning SSOT first (cheap, prevents the drift class), then infuse apps_rg's grounded candidate proof graph + fact ledger as the C0.3 backbone, re-weight per recipient, and prove completeness with a 5x4 eval lane matrix.

---

## Status Tables

### Wave Progress

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1 | W1.1, W1.2 | Model/reasoning SSOT reconciliation (apps_rg-lessons wave) | ~25K | no agentic_core edit | DONE | one X1D model SSOT; YAML generator SSOT; X2/X1D reclassified; C-level 2-pass wired |
| W2 | W2.1, W2.2 | C0.3 proof graph -> apps_rg-shared candidate SSOT (graph-skills infusion) | ~40K | none — core registry already generic (no edit) | DONE | LicGraphAdapter live; approved proof IDs+lineage into HOP3/HOP5; provenance in envelope |
| W3 | W3.1 | Recipient-fit weighting over the graph | ~20K | W2 done | DONE | proof re-weighted per recipient_class x message_type x trigger; flat candidate_skills removed |
| W4 | W4.1, W4.2 | Eval lane matrix (5x4) + batch aggregation | ~30K | judges from W1 | DONE | 20-cell matrix pass/fail report; per-recipient batch (no all-or-nothing) |
| W5 | W5.1 | C0 recipient-evidence readiness (chroma/ingestion/JD gate) | ~25K | chroma_delegate present | TODO | C0 owns vector readiness (missing/stale/blocked/ready); JD gate enforced |
| W6 | W6.1 | Pipeline SSOT + briefing reuse + ops hardening | ~15K | W2 done | TODO | shared apps_rg<->apps_lic proof SSOT; briefing.txt reuse verified; disposition/label accuracy |

### Phase Progress

| Phase | Title | Status |
|-------|-------|--------|
| W1.1 | X1D provider single-source + YAML generator SSOT | DONE |
| W1.2 | X2/X1D reclassification + C-level 2-pass + candidate-count sync | DONE |
| W2.1 | Wire LicGraphAdapter to augmented_skills_graph + fact ledger | DONE |
| W2.2 | Approved-proof selection into HOP3/HOP5 + provenance into envelope | DONE |
| W3.1 | Recipient-fit weighting | DONE |
| W4.1 | 5x4 eval lane matrix | DONE |
| W4.2 | Batch aggregation (per-recipient, no all-or-nothing) | DONE |
| W5.1 | C0 recipient-evidence readiness | TODO |
| W6.1 | Pipeline SSOT + briefing + ops | TODO |

---

## Per-Lane Reasoning Parameter Matrix (current, audited)

Derived from `apps_lic/policy/reasoning_intensity.py` (`select_reasoning_policy`). Risk tier is derived from payload signals, NOT a fixed per-recipient table — but the recipient class drives the triggers (executive/C-level => strict).

| Tier (trigger) | SC | reasoning | gen candidates | X2 "gates" (LLM-backed today) | X1D judges | repair passes | est. LLM calls / lane |
|---|---|---|---|---|---|---|---|
| R0_MINIMAL (explicit R0, no triggers) | SC-0 | R0 | 1 | schema_no_send (1) | none (x1d disabled) | 0 | ~1 (Qwen gen) |
| R1_STANDARD (default; no risk triggers) | SC-1 | R1 | 1 | schema_no_send + linkedin_tone (2) | linkedin_originality (1) | 1 | ~2-4 |
| R2_DELIBERATE (named contact/company, role-specific) | SC-2 | R2 | 2 | schema + tone + candidate_selection (3) | linkedin_originality (1) | 1 | ~4-6 |
| R3_STRICT (executive/C-level, sensitive/relationship, metric claim, send requested) | SC-3 | R3 | 3 | evidence_support + tone + safety_no_fabrication (3) | linkedin_originality (1) | 2 | ~6-10 |

Provider per call (audited): generation = **Qwen vLLM**; X1D = **CONTRADICTORY** (policy/`lic_x1d_llm_judge` say `qwen_vllm_x1d`; canonical adapter `x1d_claude_judge_adapter` = Claude Sonnet 4.6). Output budgets small (HOP5 max_tokens=500, HOP6=300) -> 24576 ctx ample, no truncation risk.

---

## apps_rg-Issue Checklist Applied to apps_lic

| apps_rg failure encountered | apps_lic status | Wave |
|---|---|---|
| Model SSOT / import-time env-pin drift (config != runtime) | PRESENT — X1D provider contradiction (qwen_vllm_x1d vs Claude); generator from env-chain `APPS_LIC_QWEN_MODEL`||`APPS_LIC_TARGET_MODEL`||`QWEN_VLLM_MODEL`||default, no YAML SSOT; audit ~/env/.env autoload pin | W1 |
| X2 (deterministic) vs X1D (semantic) discipline | VIOLATED — evidence/safety/selection LLM judges labeled "x2_deterministic_gates" | W1 |
| Frozen design rule unimplemented (declared-intent-without-consumer) | PRESENT — "2 judge passes for C-level" not wired (x1d_max_attempts=1 all tiers); two X1D impls (one superseded) | W1 |
| Numeric/config drift between paired surfaces | PRESENT — policy max_candidates (1/2/3) vs HOP5GenerationAgent default n_candidates=3 | W1 |
| Stale Qwen-era token/context budget (exec_summary truncation) | NOT AN ISSUE — outputs <=500 tok, ctx ample (smaller scope confirmed) | n/a (verify only) |
| Ungrounded content / fact provenance attrition | PRESENT — C0.3 stub + inline-only C0; no candidate proof SSOT; evidence-support gate fail-closes by construction | W2/W5 |
| All-or-nothing aggregation (final11 shipped zero) | LIKELY-OK — touch_scheduler is per-recipient; VERIFY a campaign of 20 does not fail-all on one block | W4 |
| Judge quorum=1 fragility on high-stakes | PRESENT — single X1D judge even at SC-3/C-level; couples to the 2-pass gap | W1 |
| Provider concurrency rate-limit | NOT AN ISSUE — local Qwen gen (no external limit); ~20-40 Claude judge calls for 20 sends, within limits | n/a |
| Parallel-lane serial _ENV_OVERLAY_LOCK | LOW — per-recipient processing, no section-root env overlay; verify campaign concurrency | W4 |
| Stale artifact labels (BLOCKED defaults mislead) | VERIFY — dispositions reflect real verdicts, not stale defaults | W6 |

---

## Out Of Scope

- The 6/16 "send to 20" itself — it can ship on the current path; this plan is the post-send quality completeness investment.
- apps_rg lane work (owned by other sessions).
- agentic_core engine changes beyond the minimal C0.3 graph-traverse wiring receipt (W2).

---

## Wave 1 — Model/Reasoning SSOT Reconciliation

WAVE_ID: W1
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: A

**Phases**:
- **W1.1** — X1D provider single-source + YAML generator SSOT | ~12K | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W1.2** — X2/X1D reclassification + C-level 2-pass + candidate-count sync | ~13K | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Acceptance**:
- Decide X1D model (recommend Claude Sonnet 4.6 per the frozen W0 contract = independent judge != generator); make `reasoning_intensity.x1d_provider_profile`, the judge adapter, and `lic_x1d_llm_judge` consistent; delete/deprecate the superseded impl.
- Generator + judge models resolved from a single YAML SSOT (e.g. `apps_lic/config/domain_contract/model_profiles.yaml`); env vars become documented overrides, not the source of truth; ~/env/.env autoload audited for a hidden Qwen pin.
- "X2 deterministic gates" reclassified: deterministic checks (schema, length, JD-presence, no-send regex, injection) stay X2; LLM judgments (evidence-support, safety, tone, originality, selection) move to X1D.
- C-level / executive recipients get 2 independent X1D judge passes (implement the frozen rule); max_candidates (policy) and HOP5 n_candidates synced per tier.

---

## Wave 2 — C0.3 Proof Graph -> apps_rg-Shared Candidate SSOT

WAVE_ID: W2
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED (discovery: core C0.3 registry already generic; zero agentic_core edits)
CHECKPOINT: B

**Authorization**: NOT_REQUIRED (superseded by discovery) — the core C0.3 adapter registry (`resolve_graph_adapter`) is a generic dotted-path resolver; apps_lic wires via its own `graph_adapter_ref` with ZERO agentic_core edits, so no migration receipt is needed.

**Phases**:
- **W2.1** — Wire LicGraphAdapter to apps_rg `augmented_skills_graph` + candidate fact ledger | ~20K | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W2.2** — Approved-proof selection into HOP3/HOP5 + provenance into OutboundEnvelope | ~20K | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Acceptance**:
- `c0_graph_adapter.LicGraphAdapter` returns real approved proof-points (IDs + source lineage + permission), not empty neighbors.
- HOP3 sender-grounding + HOP5 bullet generation source from the graph; every outbound proof claim carries provenance; evidence-support gate now passes on grounded lanes (no longer fail-closed by construction).

---

## Wave 3 — Recipient-Fit Weighting

WAVE_ID: W3
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: C

**Phases**:
- **W3.1** — Weight proof-points per recipient_class x message_type x company_trigger | ~20K | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Acceptance**:
- Recruiter/Senior-TA surface role/req-fit proof; exec/C-level surface business-outcome/insight proof. Flat `candidate_skills: list[str]` in competitor_recon replaced by graph-weighted selection.
- Status: DONE (W3; apps_rg role_family_weights drive recipient_fit_weight() + graph_weighted_skill_ids(); graph_recipient_fit signal in _score_proof preserves exec commercialization>agentic ordering; competitor_recon candidate_skills now derive from graph_weighted_candidate_skills(); test_w3_recipient_fit_weighting.py).

---

## Wave 4 — Eval Lane Matrix (5x4) + Batch Aggregation

WAVE_ID: W4
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: D

**Phases**:
- **W4.1** — 5x4 message-type x recipient-class eval matrix (the apps_rg "11/11" analog) | ~18K | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W4.2** — Per-recipient batch aggregation (no all-or-nothing) | ~12K | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Acceptance**:
- A single matrix report shows each of the 20 cells pass/fail at target quality (response-rate proxy + judge verdicts); single gap-backlog discipline (no scattered plans).
- A 20-recipient campaign emits drafts for all clearable recipients even if some block (verified, not assumed).

---

## Wave 5 — C0 Recipient-Evidence Readiness

WAVE_ID: W5
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: E

**Phases**:
- **W5.1** — Wire chroma_delegate into canonical C0; readiness states + JD gate + governed ingestion | ~25K | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Acceptance**:
- C0 owns public-evidence retrieval with missing/stale/blocked/conflicted/ready states; JD facts gate role-specific recruiter/Senior-TA messages (position_name + requisition_number).

---

## Wave 6 — Pipeline SSOT + Briefing + Ops Hardening

WAVE_ID: W6
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: F

**Phases**:
- **W6.1** — Shared proof SSOT + briefing reuse + disposition/label/ops verification | ~15K | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Acceptance**:
- One versioned candidate-proof SSOT shared by apps_rg + apps_lic (resume and outreach cannot drift).
- Briefing reuse documented + verified: apps_lic consumes apps_rg's briefing.txt via `--manual-brief <path>` (HOP2 research) — confirm format compatibility.
- Operational: the send requires Qwen vLLM up (fail-closed) — runbook note; dispositions reflect real verdicts (no stale BLOCKED defaults).

---

## Definition of Done

DoD-1: Single model SSOT — generator + X1D judge each resolve from one YAML source; X1D provider contradiction gone.
- Evidence: `grep qwen_vllm_x1d apps_lic` shows no live contradiction; model_profiles.yaml is the source; tests pin resolution.
- Status: DONE (W1.1; model_profiles.yaml + resolver; reasoning_intensity x1d_provider_profile=claude_sonnet_4_6_x1d; test_model_profiles_ssot.py)

DoD-2: Grounded proof — LicGraphAdapter returns real approved proof-points; every outbound claim has provenance.
- Evidence: an E2E run emits an OutboundEnvelope with proof IDs + lineage; evidence-support gate passes on a grounded lane.
- Status: DONE (W2; apps_rg_proof_bridge SSOT projection; LicGraphAdapter live over apps_rg graph; per-proof apps_rg_provenance grounded in packet + PA envelope; gate passes on grounded lane; test_w2_apps_rg_proof_bridge.py). NOTE: HOP5 prompt-level provenance weave is light — envelope carries it; deeper weave is W3.

DoD-3: 5x4 eval matrix green — all 20 message-type x recipient-class cells pass at target quality.
- Evidence: matrix report artifact under `artifacts/apps_lic/`; per-recipient batch ships partial on mixed verdicts.
- Status: PARTIAL (W4; tools/apps_lic/eval_lane_matrix.py renders the 5x4 matrix + JSON; 12/20 lanes READY at target quality with grounded apps_rg provenance; the 8 referral_ask/follow_up lanes are INPUT-gated (need per-campaign referral/prior-thread context), NOT quality-gated; per-cell independence proven — no all-or-nothing; test_w4_eval_lane_matrix.py. REMAINING for full 20/20: provide referral/prior-thread context + live X1D judge-verdict augmentation (offline harness uses proof/gate quality proxy)).

DoD-4: apps_rg-issue checklist closed — X2/X1D reclassified, C-level 2-pass wired, candidate-count synced, env-pin audited, no all-or-nothing.
- Evidence: the checklist table above all resolved; targeted tests.
- Status: DONE (W1.2; X2/X1D reclassified, C-level x1d_max_attempts=2, candidate-count synced, Qwen X1D judge deleted, env-pin documented as override; test_reasoning_intensity_policy.py + test_aig_target_category_e2e.py)

DoD-5: Briefing reuse + ops — apps_lic runs from apps_rg's briefing.txt via `--manual-brief`; runbook documents the Qwen-up dependency.
- Evidence: a real run with the shared briefing path; RUNBOOK updated.
- Status: TODO

DoD-6: Zero regression — `python -m pytest tests/unit/apps_lic tests/apps_lic` green; contract gates pass.
- Status: TODO

---

## Supersedes

_None — net-new plan._

---

## Marker Quick Reference

```
WAVE_COMPLETE: plan=apps-lic-completeness-graph-grounding-ssot-e7b2c4 wave=<N> note="+N tests, N files, scope=<summary>"
PLAN_COMPLETE: plan=apps-lic-completeness-graph-grounding-ssot-e7b2c4 note="<final outcome>"
```
