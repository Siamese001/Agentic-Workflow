---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\2026-05\\apps-underwriting-ai-activation-e8a3c5.md'
original_relative_path: '_archive\\2026-05\\apps-underwriting-ai-activation-e8a3c5.md'
source_sha256: b8e26d66ad9a70cee8d2ead980f95c9b7b69a3d6e8bdc6960e3489b872841eed
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# apps_underwriting_ai Activation — e8a3c5

> Closes P5.1 from the burndown plan `qwen-rollout-followup-burndown-d2a4f8`.
> Activates the LLM-bearing decision-explainability surface in
> `apps_underwriting_ai`. Compliance posture: deterministic verdict path
> remains the legally-binding mechanism; Qwen-judge enriches the
> human-readable `rationale` field only.

## Status

- **Plan**: `apps-underwriting-ai-activation-e8a3c5`
- **Created**: 2026-05-02
- **Owner**: Cursor Agent
- **Predecessor**: `qwen-rollout-followup-burndown-d2a4f8` P5.1
- **Status**: Completed (2026-05-02 session 2 — W3 sub-waves shipped, W4 retired as phantom scope)

## Compliance Posture (NON-NEGOTIABLE FLOOR)

For a regulated underwriting domain, the legally-binding verdict path
MUST be deterministic. This plan does NOT delegate the verdict
(`APPROVE` / `REFER` / `INSUFFICIENT_EVIDENCE` / etc.) to the LLM. The
LLM is wired ONLY to the human-readable `rationale` field on
`DecisionPacket`. Specifically:

- `DecisionPacketAssembler.assemble()` continues to compute the verdict
  via the existing deterministic heuristic (skeleton today; richer
  actuarial logic in future).
- After verdict is decided, a Qwen-first cascade attempts to GENERATE
  a richer rationale paragraph contextualized to the evidence refs +
  feature summary + reconciliation state. Any failure (preflight, SDK,
  gateway, empty response, content-policy guard) falls through to the
  pre-existing template rationale.
- `gate_violations`, `evidence_refs`, `feature_summary`, `verdict` are
  NEVER touched by the LLM. They are deterministic outputs.
- Future hardening (W3): pair Qwen with frontier-API second-judge on
  the high-risk subset (REFER / DENY verdicts) when production traffic
  begins. Gated on Wilson-CI agreement metrics across 4-week rolling
  window — same pattern as predecessor W4 P4.4.

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1 | P1.1–P1.3 | Decision-rationale Qwen-first wiring (LLM-bearing surface only) | ~3k | DecisionPacketAssembler.assemble() is the only LLM call site this wave | DONE | Live-smoke evidence: Qwen-32B produced 245-char grounded APPROVE rationale; 11/11 contract tests green; deterministic verdict path unchanged. Commits `73fd7ad165` + `e1c0a74cd2`. |
| W2 | P2.1 | Rubric YAML at `apps_underwriting_ai/policy/rubrics/judge_underwriting_decision.yaml` | ~1k | Rubric-location policy from predecessor W1 P1.5 (app owns its HOP-specific rubrics) | DONE | YAML readable; `rubric_id = underwriting_decision_rationale_v1`; wired through `RubricWiringService`. Shipped as part of W1. |
| W3 | P3.1–P3.4 | Frontier-API second-judge pairing (activated 2026-05-02 session 2) | ~5k | Existing primitives reused: `wilson_interval` / `promotion_decision` from `agentic_core/L6_observability/promotion_gates.py`; OpenAI-compatible SDK against `FRONTIER_API_BASE_URL`+`FRONTIER_API_KEY` (Anthropic/Gemini proxies, vLLM, etc.) | DONE | Pairing adapter + Wilson-CI agreement tracker + wire-in + tests shipped. Dormant by default (`APPS_UW_FRONTIER_PAIRING_ENABLED=1` to arm). Verdict path untouched; all existing tests green. |
| W4 | P4.1 | Full HOP pipeline activation — RETIRED AS PHANTOM SCOPE | 0 | Scope description (`profile_analysis / research / sender_grounding / routing / validation / qa_report / integration`) was inherited copy-paste from `apps_lic`; `apps_underwriting_ai` has 5 HOP engines (`hop_initialize_evidence`, `hop_collect_evidence`, `hop_reconcile_documents`, `hop_derive_features`, `hop_assemble_decision`) which are thin substrate-adapters already delegating to real implementations (`EvidenceRegisterEngine`, `DocumentReconciliationEngine`, `FeatureDerivationEngine`, `DecisionPacketAssembler`). What remains "skeleton" is actuarial richness inside `DeterministicRiskScorer` — out of scope per `SVP_ENGINEERING_REVIEW.md` SME-cliff boundary, requires jurisdictional SME. | RETIRED | Ground-truth verified 2026-05-02: no placeholder HOP engines exist. Follow-on plan `apps-underwriting-feature-complete-aa79a7` (Completed 2026-05-02) already shipped parsers/validators/services/tools/rubric-wiring/tests. Actuarial-model gap is captured elsewhere; deferred pending SME. |

### W3 Sub-Waves (detail)

| Sub-Wave | Focus | Files | Status |
|----------|-------|-------|--------|
| W3.1 | Frontier-rationale judge adapter | `apps_underwriting_ai/services/frontier_rationale_judge.py` (NEW) | DONE |
| W3.2 | Rolling Wilson-CI agreement tracker (reuses `promotion_gates.wilson_interval`) | `apps_underwriting_ai/services/rationale_agreement_tracker.py` (NEW) | DONE |
| W3.3 | Wire pairing into `DecisionPacketAssembler._enrich_rationale_via_qwen` (post-Qwen-accept, fail-soft, verdict floor preserved) | `apps_underwriting_ai/engines/decision_packet_assembler.py` (EDIT) | DONE |
| W3.4 | Contract tests for pairing path (disabled default / unavailable fail-soft / agreement sample / disagreement sample / determinism floor) | `apps_underwriting_ai/tests/test_frontier_pairing.py` (NEW), conftest extension | DONE |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| P1.1 | Rubric YAML authoring | `apps_underwriting_ai/policy/rubrics/judge_underwriting_decision.yaml` (NEW) + parent dirs | Deciding rubric content for a regulated-domain explainability judge — bias toward narrow scope (rationale clarity, factual grounding in evidence_refs, no fabrication of feature values) | 1k | DONE |
| P1.2 | Wire Qwen-first cascade in DecisionPacketAssembler.assemble() | `apps_underwriting_ai/engines/decision_packet_assembler.py` | Sync openai.OpenAI cascade matching W2/W3/W5/burndown-P1.1 pattern; preserve frozen DecisionPacket immutability by deciding verdict + rationale before construction | 2k | DONE |
| P1.3 | Live smoke verification | inline Python test against real Qwen-32B | Confirm verdict path deterministic; rationale enriched only on Qwen accept | 1k | DONE |
| P3.1 | Frontier adapter (W3.1) | `services/frontier_rationale_judge.py` | OpenAI-compatible SDK against configurable base_url; fail-soft on every failure path; returns `None` unless pairing enabled + frontier available + response passes same guards as Qwen path | 1.5k | DONE |
| P3.2 | Agreement tracker (W3.2) | `services/rationale_agreement_tracker.py` | Jaccard overlap on significant tokens (lowercased, len≥5, stopword-filtered) as agreement heuristic; durable JSONL at `artifacts/apps_underwriting_ai/rationale_agreement.jsonl`; Wilson lower-bound watchdog via existing `wilson_interval`; 4-week rolling window; disagree threshold = lower_bound < 0.85 on n≥30 | 2k | DONE |
| P3.3 | Wire-in (W3.3) | `engines/decision_packet_assembler.py` | Runs AFTER Qwen accepts; verdict already fixed upstream; pairing is telemetry-only, never mutates `text`; marker emitted on disagree | 1k | DONE |
| P3.4 | Tests (W3.4) | `tests/test_frontier_pairing.py`, `tests/conftest.py` | ~10 tests; autouse conftest disables pairing during contract suite to preserve W1 determinism floor | 0.5k | DONE |
| P4.1 | Full HOP pipeline activation | RETIRED as phantom | See W4 row — scope description was inherited from `apps_lic`; no matching placeholder engines exist in `apps_underwriting_ai` | 0 | RETIRED |

## ADG_HOTSPOT_REPORT

Single-file edit to `decision_packet_assembler.py` plus one new YAML.
The decision_packet_assembler is a downstream consumer (low fan-out).
No layer crossings, no new ADG hotspot.

## ADG_GRAPH_LAYER_EVIDENCE

`apps_underwriting_ai/engines/hop_assemble_decision_engine.py` already
calls `DecisionPacketAssembler.assemble()` — the substrate edge from
HOP5 to the assembler is in place. This wave inserts a Qwen call
INSIDE the assembler before `DecisionPacket(...)` construction; no
new edges, no fan-in or fan-out change.

## Decision Log

- **2026-05-02 18:13 UTC** — Plan created. Compliance-posture floor
  set: LLM touches `rationale` only; verdict path stays deterministic.
  Future-hardening trigger (frontier pairing) deferred to passive.
  Full-app activation (7 placeholder engines) explicitly out of
  scope — separate workstream.
- **2026-05-02 session 2** — Author-Gate selected Option 1
  (build W3 + close plan honestly). Ground-truth validation
  revealed W4 as phantom scope: the "7 placeholder HOP engines"
  description was inherited copy-paste from `apps_lic`, and
  `apps_underwriting_ai`'s 5 HOP engines are already
  substrate-adapters delegating to real implementations. The
  follow-on `apps-underwriting-feature-complete-aa79a7` plan
  (Completed 2026-05-02) already shipped parsers / validators /
  services / tools / rubric-wiring / tests. Actuarial-model
  richness is out of scope per SVP_ENGINEERING_REVIEW SME-cliff.
  W4 retired; W3 broken into sub-waves W3.1–W3.4 and shipped.
  Existing Wilson-CI + consensus-judge + provider-registry
  primitives in `agentic_core` reused (no duplication).

## Burndown Order

1. **P1.1 + P1.2 + P1.3** (session 1) — rubric + cascade wiring + live smoke. DONE.
2. **P2.1** — folded into P1.1 (rubric file authored as part of W1). DONE.
3. **P3.1 – P3.4** (session 2) — frontier pairing adapter + tracker + wire-in + tests. DONE.
4. **P4.1** — RETIRED (phantom scope).

## Plan Closure (2026-05-02 session 2)

All in-scope work DONE. W4 retired on ground-truth evidence
(no matching placeholder engines; follow-on feature-complete
plan already shipped). Notion row flipped Live → Completed.
