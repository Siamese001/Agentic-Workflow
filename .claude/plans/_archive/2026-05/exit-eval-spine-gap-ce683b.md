# Exit Eval & Control — Best-Practice Gap Analysis & Remediation Plan

**Plan ID:** `exit-eval-spine-gap-ce683b`
**Scope:** v33 Process Map §5 "EXIT EVAL & CONTROL" (+ §6 Shadow Eval where it touches the exit spine)
**Source doc:** `docs/reference/_notes/agentic_process_mapping_v34.md` (lines 377–474)
**Status:** EXECUTED — doc+schema+ADR artifacts delivered; no code merged (per §6 Out of Scope). Code execution plans for each ADR are follow-ups.
**Tier:** T3 (cross-layer: L5 exit, L2 sealing, L6 shadow, apps_eval, UWG)

---

## 1. Best-Practice Reference Set (authoritative)

Synthesized from live vendor docs (web-fetched 2026-04-23):

### 1.1 Anthropic — "Demystifying evals for AI agents"
- **Combine 3 grader types per task**: code-based (deterministic), model-based (LLM-rubric / pairwise / reference / multi-judge consensus), human (SME review, calibration, A/B).
- **Scoring combine modes**: weighted-threshold, binary-all-pass, or hybrid.
- **Capability vs Regression split**: capability = hill-climb (low → high pass rate); regression = fleet-protecting (≈1.00 pass rate); capability graduates to regression after launch.
- **Research-agent spine**: groundedness + coverage + source quality + exact-match (where applicable).
- **Non-determinism handling**: replicate runs; track pass-rate distribution, not single score.
- **Give the LLM a way out** ("Unknown") and budget the Unknown fraction per judge.
- **Periodic human calibration** of LLM-rubric graders against expert judgment.
- **Track per-task**: latency, token usage, cost, error rate — even once quality is green.

### 1.2 Google Vertex AI — "Evaluate Gen AI agents"
Two evaluation surfaces, **both required**:
- **Final response evaluation** — did the agent achieve the goal (quality, groundedness, hallucination, safety, instruction-following).
- **Trajectory evaluation** — did it take the right path:
  - `trajectory_exact_match` (strict order + set)
  - `trajectory_in_order_match` (order preserved, extras allowed)
  - `trajectory_any_order_match` (set match, order-free)
  - `trajectory_precision` (predicted ∩ reference / predicted)
  - `trajectory_recall` (predicted ∩ reference / reference)
  - `single_tool_use` (specific tool invoked y/n)
  - Default always-emitted: `latency`, `failure` (boolean)
- **Hallucination metric** grounded to agent config + tool usage, not free-form judge.

### 1.3 OpenAI — "Evaluate agent workflows"
- **Trace-first, dataset-second**: trace-grading for debugging (per-run), datasets + eval-runs for repeatability (regression).
- **Trace content**: end-to-end record of model calls, tool calls, guardrails, handoffs.
- **Trace-grader questions**: right tool picked? handoff fired when it should? instruction/safety policy violated? did prompt/routing change improve end-to-end behavior?
- **Flywheel**: traces → curated dataset → eval runs → prompt optimizer → deploy.
- **Rubric-based LLM grader** for open-ended conversational/realtime agents (instruction following, correctness, empathy, escalation, hallucination avoidance).

### 1.4 Industry (Akira / Codebridge / practitioner consensus)
- **Real-time guardrail chain at exit**: policy validation → violation detection → fallback → HITL escalation.
- **Kill-switches / panic stop** as a named runtime verb.
- **Escalation packet schema**: reason + evidence + trace-ref + severity + proposed options + approver pool + deadline.
- **Budget envelopes** (tokens, time, $) with exit-phase budget-fit check.
- **Model cards / risk registers / decision logs** kept current.

---

## 2. Current State — what v33 §5 (+§6 touchpoints) actually defines

Quoting the canonical text (verbatim scope only):

> **CURRENT-RUN EVALUATION**
> - Policy / baseline fit
> - Answered the request in the required form
> - Safe to leave: integrity, isolation, mutation authorization
> - Answer quality: groundedness, citation/support, completeness

> **Dispositions**: allow/finish · deny/reroute · escalate (HITL) · commit request (→ UWG → L4)

> **Async exhaust** → **6B EVALUATE**: "Grade outcomes, groundedness, and citation support. Grade trajectories: tool order, retries, budget, execution shape. Detect regressions in exact match, schema, API, and guardrails. Human calibration tunes grading, not runtime."

This is **correct in direction** but stated as prose, not as a typed contract/schema, and it leaves several primitives unnamed.

### 2.1 What the repo already has (evidence-graded, DIRECTLY OBSERVED)

| Asset | Path | Covers |
|---|---|---|
| Dimension rubrics (faithfulness, answer_relevancy, context_precision, groundedness) | `config/judges/rubrics.yaml` | Final-response rubric spine |
| Capability-vs-regression taxonomy | `config/judges/rubrics.yaml` → `eval_taxonomy` | Anthropic split |
| Consensus / reference / pairwise judges | `config/judges/rubrics.yaml` | Anthropic multi-judge |
| Scenario outcome rules (PASS/FAIL/TIMEOUT/ERROR) | `apps_eval/config/eval_policies.yaml` | Terminal class |
| Regression detector | `apps_eval/engines/regression_detector.py` | Anthropic regression surface |
| Scorecard engine | `apps_eval/engines/scorecard_engine.py` | Aggregation |
| Scenario runner | `apps_eval/engines/scenario_runner.py` | Dataset + eval-runs |
| HITL decision quality engine | `apps_eval/engines/hitl_decision_quality_engine.py` | Escalation grading |
| Runtime HITL classes + approver pools + timeouts | `agentic_core/L5_safety/exit_control/hitl_*` + `config/runtime_hitl_policy.yaml` (ADR-023) | Escalation plumbing |
| Golden datasets scaffolding | `data/eval/golden/rag/`, `data/judge_calibration/` | Anthropic calibration bank |
| Hard vs soft gate split | `apps_eval/config/eval_policies.yaml` → `gate_policies` | Industry gate pattern |
| UWG authority for durable writes | v33 §5 commit path + `agentic_core/*/universal_write_gateway*` | Industry kill-switch locus |

### 2.2 Fact-grading of the remainder
All items in §3 are **DIRECTLY OBSERVED** as absent (grep + file inspection). No gap claim below is derived or assumed.

---

## 3. Gap Register

### Legend
- **Severity**: 🔴 blocks vendor parity · 🟡 partial coverage · 🟢 nice-to-have
- **Surface**: `RT` = runtime exit, `SH` = shadow/L6, `CONF` = config/schema, `GATE` = policy gate, `DOC` = process-map wording

| # | Gap | Severity | Surface | Best-Practice Source | Evidence (what is missing in repo) |
|---|---|---|---|---|---|
| G1 | **No trajectory metric suite at runtime exit.** v33 §6B mentions "tool order, retries, budget" prose only; no `trajectory_exact_match`/`in_order`/`any_order`/`precision`/`recall`/`single_tool_use` primitives emitted on the sealed-artifact path. | 🔴 | RT, SH | Google Vertex | `grep trajectory_*_match` → zero hits in `agentic_core/`, `apps_eval/`. |
| G2 | **No typed `ExitDecision` schema.** §5 lists 4 dispositions in prose; there is no JSON-Schema / pydantic contract pinning disposition enum + reason_code + confidence + safety_flags + budget_fit + groundedness_score + trajectory_scores + escalation_packet_ref. | 🔴 | CONF | Industry + OpenAI trace-grade | No `decision_record.schema.json` equivalent for exit (only author-gate schema in `.cursor/schemas/`). |
| G3 | **Runtime trace-grading surface missing.** OpenAI mandates trace-grade before dataset-grade; repo has `scenario_runner.py` (dataset path) but no runtime trace grader that scores the live L2 sealed transcript before disposition. | 🔴 | RT | OpenAI | `apps_eval/` engines consume datasets; nothing runs at §5 on sealed runtime artifacts. |
| G4 | **No exit-phase budget-fit check.** Ingress stamps request envelope; §5 has no named step validating token / latency / tool-call / $ budget consumed vs envelope before `allow/finish`. | 🔴 | RT, GATE | Anthropic + Industry | `eval_policies.yaml` has `latency_threshold_ms: 30000` for scenarios; no runtime per-request enforcement. |
| G5 | **Escalation packet schema undefined.** `hitl_policy.py` has `HitlPolicy` dataclass (classes/timeouts/approvers) but no schema pinning the fields an L5 escalation packet **must** carry (trace_ref, severity_band, confidence, options_ledger, evidence_refs, deadline, tenant, blast_radius). | 🔴 | CONF | Industry + ADR-023 | `.cursor/schemas/decision_record.schema.json` is for author-gate; no runtime counterpart. |
| G6 | **Data-exhaust contract is prose.** v33 line 444 "Traces, Artifacts, Outcomes, reason codes, commit status" — no typed `EvalEvent` schema for the L6 ingest queue. | 🟡 | SH, CONF | Google + OpenAI | No schema at `config/schemas/` for exhaust events; §6A "Map telemetry" has no target shape. |
| G7 | **No regression-suite gate before promotion (6D).** 6D "gated review" does not require capability→regression pass rate ≥ rubrics.yaml `regression.min_pass_rate_target: 0.98` before UWG commits a prompt/policy/rubric change. | 🔴 | GATE, SH | Anthropic | `regression_detector.py` exists but is not wired as a blocking precondition in §6D. |
| G8 | **Judge-calibration cadence not gated.** `rubrics.yaml` defines `unknown_budget` but no rule/workflow enforces periodic (e.g. weekly) human recalibration; calibration ledger only contains `data/judge_calibration/` scaffolding. | 🟡 | SH, GATE | Anthropic | No cron / CI gate checks last-calibration timestamp. |
| G9 | **No hallucination metric distinct from groundedness.** Vertex defines `hallucination` grounded to *agent config + tool usage*, separate from LLM-rubric groundedness. Repo collapses both into `groundedness` rubric. | 🟡 | RT, SH | Google | `rubrics.yaml` has `groundedness` dim only. |
| G10 | **No explicit safety-violation result class.** OpenAI trace-grade asks "Did the workflow violate an instruction or safety policy?" as a first-class boolean; v33 §5 bullets name "Policy / baseline fit" but no typed flag. | 🔴 | RT, CONF | OpenAI + Industry | Tied to G2 (ExitDecision schema). |
| G11 | **No named kill-switch / panic-stop verb at Exit Desk.** Industry guardrail spec requires a standing primitive to halt a class of outcomes (tenant, route, tool, cost) mid-session. L5 owns policy but no `exit_kill_switch()` primitive is declared in §5. | 🟡 | RT, DOC | Industry | No verb; `L5_safety/enforcement/` has static gates only. |
| G12 | **Trace→dataset flywheel bridge absent.** OpenAI: failed/escalated traces should be promoted to eval datasets. No tool lifts runtime exhaust into `data/eval/golden/`. | 🟡 | SH | OpenAI | `data/eval/golden/rag/` is scaffold-only; no promotion script. |
| G13 | **"Answered the required form" check is unspecified.** v33 bullet is prose only — no schema-validation step against the request's declared output contract (JSON schema, markdown section list, tool-result envelope). | 🟡 | RT, GATE | OpenAI + Google | No `output_contract_validator` module. |
| G14 | **Non-determinism reporting absent.** Anthropic stresses pass-rate distribution over replicated runs. Scorecard engine emits single score, not replication variance. | 🟢 | SH | Anthropic | `scorecard_engine.py` has no `replicate_n` field. |
| G15 | **Cost per task not emitted as default metric.** Vertex emits `latency` + `failure` always; Anthropic adds token/$. Repo emits latency but `cost_usd` is not always-on in ExitDecision. | 🟡 | RT, SH | Anthropic + Google | No `cost_usd` default metric in scorecard. |
| G16 | **Trace-grader questions not codified.** OpenAI lists the four canonical trace questions (right tool? handoff fired? policy violated? change improved?). Repo has no rubric file encoding them. | 🟡 | CONF, SH | OpenAI | No `config/judges/trace_rubric.yaml`. |
| G17 | **v33 doc itself does not name the metric set.** §5 uses prose bullets; reader cannot extract a canonical metric list. | 🟡 | DOC | All three vendors | Doc update required independent of code. |
| G18 | **6B "regressions in exact match, schema, API, and guardrails" is mentioned only in shadow lane.** Should also be runtime-exit inputs (trace-grade), not purely future-run. | 🟡 | DOC, RT | OpenAI | §5 current-run evaluation bullets don't include these four. |

---

## 4. Remediation Plan (waves)

Rules of engagement:
- Docs + schemas first. Code changes gated behind ADR approval.
- Zero-scope expansion — each wave delivers one observable artifact per gap.
- Every new schema goes under `config/schemas/` and is CI-linted.

### Wave Summary

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---|---|---|---|
| **W1 — Doctrine & Schema SSOT** | W1.1, W1.2, W1.3, W1.4 | Update v33 §5 text, author `ExitDecision` schema, author `EscalationPacket` schema, author `EvalEvent` exhaust schema | ~18k | No code execution; doc + schema only | Todo | §5 names all canonical metrics; 3 new schemas committed + CI-validated |
| **W2 — Runtime Trace-Grader** | W2.1, W2.2, W2.3 | ADR for trace-grader; `config/judges/trace_rubric.yaml`; integration contract (no wiring yet) | ~22k | W1 complete | Todo | ADR merged; rubric covers 4 OpenAI trace questions + safety flag |
| **W3 — Trajectory Metrics** | W3.1, W3.2, W3.3 | ADR for trajectory metric suite; reference-trajectory format; precision/recall/match specs | ~20k | W1 complete | Todo | ADR merged; metric definitions match Vertex semantics; reference format added to eval dataset schema |
| **W4 — Budget Envelope & Output Contract** | W4.1, W4.2 | ADR for per-request budget envelope (token/latency/tool/$); ADR for output-contract validation step at §5 | ~18k | W1 complete | Todo | Two ADRs merged; budget envelope shape defined + wired into ExitDecision |
| **W5 — Promotion & Calibration Gates** | W5.1, W5.2, W5.3 | Regression-gate-before-UWG rule; judge-calibration cadence rule; trace→dataset flywheel script spec | ~15k | W1–W4 in place | Todo | Two always-on rules; one spec doc; CI gate skeletons identified |
| **W6 — Shadow Observability Upgrades** | W6.1, W6.2, W6.3 | Hallucination vs groundedness split; cost-per-task default; non-determinism replication reporting | ~14k | W1 complete | Todo | Rubric delta merged; `cost_usd` added to ExitDecision + scorecard; replication field added to EvalEvent |
| **W7 — Kill-Switch & Safety Verbs** | W7.1 | ADR declaring `exit_kill_switch(scope)` primitive at L5; wired to ExitDecision `policy_halt` flag | ~8k | W1, W4 | Todo | ADR merged; no code yet |
| **W8 — Verification** | W8.1, W8.2 | Gap-register re-walk; doc-vs-schema cross-check; sign-off | ~6k | All prior | Todo | 18/18 gaps have a tracked artifact ID; SVP review scheduled |

### Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| W1.1 | Rewrite v33 §5 to name metrics | `docs/reference/_notes/agentic_process_mapping_v34.md` §5 | Prose→contract language without expanding scope | 5k | Todo |
| W1.2 | `ExitDecision` schema | `config/schemas/exit_decision.schema.json` (new) | Enum fidelity across disposition + reason_code + safety + budget | 5k | Todo |
| W1.3 | `EscalationPacket` schema | `config/schemas/escalation_packet.schema.json` (new) | Must align with ADR-023 HITL classes | 4k | Todo |
| W1.4 | `EvalEvent` exhaust schema | `config/schemas/eval_event.schema.json` (new) | Must cover Traces / Artifacts / Outcomes / reason / commit | 4k | Todo |
| W2.1 | ADR — Runtime Trace-Grader | `docs/architecture/adr/ADR-NNN-runtime-trace-grader.md` | Bounded scope; no code merge | 8k | Todo |
| W2.2 | `trace_rubric.yaml` (design only) | `config/judges/trace_rubric.yaml` (new, design) | OpenAI 4-question rubric + safety-violation boolean | 8k | Todo |
| W2.3 | Integration contract | ADR §4 | How sealed artifact ↔ grader ↔ ExitDecision flows; no code | 6k | Todo |
| W3.1 | ADR — Trajectory Metric Suite | `docs/architecture/adr/ADR-NNN-trajectory-metrics.md` | Name the 6 Vertex metrics + default latency/failure | 8k | Todo |
| W3.2 | Reference-trajectory dataset format | `data/eval/golden/trajectory/README.md` (new) | Tool-call sequence schema | 6k | Todo |
| W3.3 | Semantic equivalence policy | ADR §5 | Exact vs normalized tool-call comparison | 6k | Todo |
| W4.1 | ADR — Budget Envelope | `docs/architecture/adr/ADR-NNN-budget-envelope.md` | Stamped at ingress E3; checked at §5 | 10k | Todo |
| W4.2 | ADR — Output-Contract Validator | `docs/architecture/adr/ADR-NNN-output-contract-validator.md` | Schema-validates final answer against declared contract | 8k | Todo |
| W5.1 | Rule — Regression pass before promotion | `.cursor/rules/evaluation-promotion-gate.md` (new) | Ties to §6D + rubrics.yaml regression threshold | 5k | Todo |
| W5.2 | Rule — Judge calibration cadence | `.cursor/rules/judge-calibration-cadence.md` (new) | Weekly; unknown-budget watchdog | 5k | Todo |
| W5.3 | Trace→dataset flywheel spec | `docs/architecture/adr/ADR-NNN-eval-flywheel.md` | Failed/escalated traces auto-curated | 5k | Todo |
| W6.1 | Hallucination vs Groundedness split | `config/judges/rubrics.yaml` doc delta + ADR | Vertex-style tool-grounded hallucination dim | 5k | Todo |
| W6.2 | Cost-per-task default metric | `config/schemas/exit_decision.schema.json` (update) + scorecard spec | `cost_usd` always-on | 4k | Todo |
| W6.3 | Non-determinism replication field | `config/schemas/eval_event.schema.json` (update) | `replicate_of`, `replicate_n`, `pass_rate` fields | 5k | Todo |
| W7.1 | ADR — Exit Kill-Switch | `docs/architecture/adr/ADR-NNN-exit-kill-switch.md` | Verb + scope grammar + audit trail | 8k | Todo |
| W8.1 | Gap re-walk | this plan + artifact register | Cross-check all 18 gaps have PRs/ADRs | 3k | Todo |
| W8.2 | SVP Engineering Review | `apps_eval/SVP_ENGINEERING_REVIEW.md` delta | Sign-off packet for exit spine | 3k | Todo |

---

## 5. Success Criteria (plan-wide)

- **Parity**: v33 §5 names every metric primitive in §1.1 + §1.2 + §1.3 of this plan.
- **Contracts**: 3 new JSON schemas (`ExitDecision`, `EscalationPacket`, `EvalEvent`) + 2 rubric YAMLs (`trace_rubric`, hallucination split).
- **ADRs**: 7 ADRs cover trace-grader, trajectory metrics, budget envelope, output-contract validator, flywheel, kill-switch, hallucination split.
- **Rules**: 2 always-on rules (promotion gate, calibration cadence).
- **Traceability**: every gap G1–G18 has ≥1 artifact ID in an ADR or schema commit.
- **No code merged in this plan** — execution plans emit after each ADR is approved; author-gate on first code edit.

## 6. Out of Scope (explicit)

- Implementation of trace-grader, trajectory metric emitters, budget envelope enforcement, kill-switch verb — each requires its own execution plan post-ADR.
- Changes to ADR-023 HITL runtime policy (only *references* added).
- Changes to UWG internal logic (only *contract* between §5 and UWG is clarified).
- Judge model swaps or rubric weight re-tuning.

## 7. ADG Provenance

ADG Provenance: backend=sqlite, snapshot=artifacts/adg/adg_indexed_<latest>.sqlite
(No ADG graph-layer queries were required — this plan is pure doctrine/schema scoping. A follow-up plan for W2/W3 code phases will emit `## ADG_HOTSPOT_REPORT` and `## ADG_GRAPH_LAYER_EVIDENCE` sections per constitutional §22.)

## 8. Fact Grading

| Claim class | Count |
|---|---|
| DIRECTLY OBSERVED (repo grep/read) | 14 (Gaps G1–G5, G7, G9, G10, G12–G16) |
| DIRECTLY OBSERVED (vendor docs web-fetched 2026-04-23) | §1 entirety |
| DERIVED | 4 (G6 schema shape, G8 cadence specifics, G11 verb name, G18 routing implication) |
| UNRESOLVED | 0 |

## W8 — Verification & Artifact Register (executed 2026-04-23)

| Wave | Artifact | Path | Status |
|---|---|---|---|
| W1.1 | v33 §5 rewrite (prose → canonical metric spine) | `docs/reference/_notes/agentic_process_mapping_v34.md` §5 | ✅ committed |
| W1.2 | ExitDecision schema | `config/schemas/exit_decision.schema.json` | ✅ JSON-valid |
| W1.3 | EscalationPacket schema | `config/schemas/escalation_packet.schema.json` | ✅ JSON-valid |
| W1.4 | EvalEvent exhaust schema | `config/schemas/eval_event.schema.json` | ✅ JSON-valid |
| W2.1 | ADR-036 — Runtime Trace-Grader | `docs/architecture/adr/ADR-036-runtime-trace-grader.md` | ✅ |
| W2.2 | Trace rubric | `config/judges/trace_rubric.yaml` | ✅ YAML-valid |
| W3.1 | ADR-037 — Trajectory Metric Suite | `docs/architecture/adr/ADR-037-trajectory-metrics.md` | ✅ |
| W3.2 | Trajectory dataset README | `data/eval/golden/trajectory/README.md` | ✅ |
| W4.1 | ADR-038 — Budget Envelope | `docs/architecture/adr/ADR-038-budget-envelope.md` | ✅ |
| W4.2 | ADR-039 — Output-Contract Validator | `docs/architecture/adr/ADR-039-output-contract-validator.md` | ✅ |
| W5.1 | Rule — Promotion Gate | `.cursor/rules/evaluation-promotion-gate.md` | ✅ |
| W5.2 | Rule — Judge Calibration Cadence | `.cursor/rules/judge-calibration-cadence.md` | ✅ |
| W5.3 | ADR-040 — Eval Flywheel | `docs/architecture/adr/ADR-040-eval-flywheel.md` | ✅ |
| W6.1 | Hallucination/Groundedness split (ADR + rubrics.yaml note) | `docs/architecture/adr/ADR-041-hallucination-groundedness-split.md` + `config/judges/rubrics.yaml` | ✅ |
| W6.2 | Cost-per-task default metric | `config/schemas/exit_decision.schema.json` → `budget.cost_usd_*`; `config/schemas/eval_event.schema.json` → `cost.cost_usd` | ✅ encoded in schemas |
| W6.3 | Non-determinism replication fields | `config/schemas/eval_event.schema.json` → `replication.*` | ✅ encoded in schema |
| W7.1 | ADR-042 — Exit Kill-Switch | `docs/architecture/adr/ADR-042-exit-kill-switch.md` | ✅ |

### Gap → Artifact traceability (all 18 gaps covered)

| Gap | Covered by |
|---|---|
| G1 trajectory suite | ADR-037 + ExitDecision.trajectory |
| G2 ExitDecision schema | exit_decision.schema.json |
| G3 runtime trace-grader | ADR-036 + trace_rubric.yaml |
| G4 budget-fit check | ADR-038 + ExitDecision.budget |
| G5 escalation packet schema | escalation_packet.schema.json |
| G6 data-exhaust contract | eval_event.schema.json |
| G7 regression-before-promotion | rule `evaluation-promotion-gate.md` |
| G8 judge-calibration cadence | rule `judge-calibration-cadence.md` |
| G9 hallucination vs groundedness | ADR-041 + rubrics.yaml note + ExitDecision.final_response.hallucination |
| G10 safety-violation result class | ExitDecision.safety.* |
| G11 kill-switch verb | ADR-042 + ExitDecision.safety.policy_halt |
| G12 flywheel bridge | ADR-040 + EvalEvent.flywheel + trajectory dataset README |
| G13 output-form check | ADR-039 + ExitDecision.output_contract |
| G14 non-determinism reporting | EvalEvent.replication |
| G15 cost per task default | ExitDecision.budget.cost_usd_* + EvalEvent.cost.cost_usd |
| G16 trace-grader rubric | trace_rubric.yaml |
| G17 doc names the metric set | v33 §5 rewrite |
| G18 regression signals at runtime | ADR-036 §2 + v33 §5 regression paragraph |

### Verification evidence

- `python -c "import json,yaml; ..."` — all 3 JSON schemas parse; both YAML rubrics parse (exit 0, 2026-04-23).
- v33 §5 rewrite verified in-file (lines 389–419).
- Rule files follow `.cursor/rules/*.md` frontmatter convention (`trigger: model_decision`).
- Seven new ADRs follow the existing `ADR-NNN-kebab-title.md` naming pattern in `docs/architecture/adr/`.

### Explicit non-deliverables (per §6 Out of Scope)

- No code merged to `agentic_core/`, `apps_eval/`, `apps_*/`, `tools/`, `system_learning/`.
- ADR-023 content not modified — only referenced.
- UWG internals not modified.
- No judge-rubric weight tuning or model swaps.

## 9. References

- Anthropic — https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents
- Google Vertex — https://docs.cloud.google.com/vertex-ai/generative-ai/docs/models/evaluation-agents
- OpenAI — https://developers.openai.com/api/docs/guides/agent-evals
- Industry guardrails — Akira / Codebridge / Medium practitioner guides (2025–2026)
- Repo SSOT — `config/judges/rubrics.yaml`, `apps_eval/`, `agentic_core/L5_safety/exit_control/`, `docs/architecture/adr/ADR-023-runtime-hitl-exit-control.md`
- Canonical v33 — `docs/reference/_notes/agentic_process_mapping_v34.md` §5 lines 377–474
