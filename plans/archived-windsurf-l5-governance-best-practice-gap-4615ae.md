---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\l5-governance-best-practice-gap-4615ae.md'
original_relative_path: 'l5-governance-best-practice-gap-4615ae.md'
source_sha256: f141afd4a7963529dc3f6022f3713d0e643e2eda97bce49f88c834a35a9f17a5
recovered_status: LOST_RECOVERED
last_commit: '6477883502e'
last_commit_date: '2026-04-27 08:55:24 -0400'
created_date: '2026-04-24'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# L5 Governance & Safety Plane — Best-Practice Gap Analysis & Remediation Plan

**Plan ID**: `l5-governance-best-practice-gap-4615ae`
**Status**: Draft (research + plan only — no code edits)
**Tier**: T3 (architectural, cross-layer, governance plane)
**Source doc reviewed**: `docs/reference/00_L5_Policy_Plane/Governance & Safety v3.md` (v25 single-box triple-click)
**Research sources**: OpenAI (Practical Guide to Building Agents + Governed Agents Cookbook), Anthropic (Framework for Safe & Trustworthy Agents + Responsible Scaling Policy v3 + Claude Constitution), Google (Secure AI Framework / SAIF + Cloud CISO 2025 SAIF guidance + Agent Development Kit).

---

## 1. Current L5 Capability Inventory (from v3 doc)

| Capability | Where in v3 | Notes |
|---|---|---|
| Governance invocation triage (static / runtime / human re-entry) | G1 | Mode router |
| Authority context resolution (policy + structure + registry) | G2 | Single source of governing truth |
| Static structure enforcement (paths, layers, depth) | Static lane | Architectural invariants |
| AST classification kernel (type SSOT) | Static lane | Dual-tag conflict detect |
| Registry validation (agent identity, allowed_models, exec mode) | Static lane | Identity gate |
| Policy validation chokepoint (risk tier + tools/actions/plan check) | Runtime lane | Approve / reject / remediate |
| LLM gateway egress (provider resolution, prompt-injection detect, audit, replay envelope, fail-closed) | Runtime lane | Sole external-call path |
| Decision rail (REJECT / REMEDIATE / CERTIFY) | Decision rail | Terminal authority |
| Outputs: GovernanceResult, compliance_hash, audit_log, replay_envelope, capability_token, sandbox_envelope | Outputs block | Downstream contract |
| Invariant: learning signals cannot alter current certified run | Outputs block | Calibration isolation |

---

## 2. Vendor Best-Practice Distillation

### 2.1 OpenAI — *Practical Guide to Building Agents* + *Governed Agents Cookbook*

- **Layered defenses**: client-level universal guardrails + agent-level domain-specific guardrails, composed (not single-rail).
- **Named guardrail catalog**: PII, Secret Keys, Jailbreak, Prompt Injection, Moderation, NSFW, Off-Topic, Competitors, Hallucination, Keyword Filter, URL Filter, Custom Prompt Check.
- **Centralized policy-as-a-package**: versioned, distributable across agents; audited in one place.
- **Risk-proportionate controls**: low / moderate / high tiers with different approval, logging, HITL, and isolation requirements.
- **Registries as first-class governed resources**: Agent Registry, Tool Registry, Prompt Registry — each with owner, purpose, risk tier, eval status, scopes, lineage, rollback policy.
- **Eval-driven threshold tuning**: automated feedback loop using golden + adversarial datasets; tunable thresholds promoted via CI.
- **Red teaming in CI**: e.g., Promptfoo target script + red-team config + report → CI gate.
- **Tracing / observability with ZDR mode**: full trace by default, custom processors for compliance.
- **Shadow-AI discovery**: detect ungoverned agent activity; make governed path the path of least resistance.
- **Standards alignment**: NIST AI RMF, ISO/IEC 42001, sector overlays (HIPAA, SOX, GDPR).

### 2.2 Anthropic — *Safe & Trustworthy Agents Framework* + *RSP v3* + *Claude Constitution*

- **Read-only by default**; explicit human approval before any state mutation.
- **Persistent permission grants** for routine trusted operations (capability scoping by repeatability + trust).
- **Real-time visible plan / to-do list**: humans can interrupt and redirect mid-execution.
- **Value-alignment evaluation**: agentic-misalignment red-team scenarios pre-deployment.
- **Prompt-injection classifier ensemble** + ongoing Threat Intelligence monitoring loop.
- **Cross-context / cross-task information compartmentalization** (privacy across long-horizon agents).
- **One-time vs permanent connector grants** (capability TTL semantics) at MCP layer.
- **Enterprise admin allowlist** for which MCP connectors users can attach.
- **Capability-tier graded safeguards (RSP / ASL)**: safeguards scale with detected model/agent capability; thresholds + risk reports + external review.
- **Hard constraints** (constitutional rules) that cannot be overridden by ad-hoc reasoning.

### 2.3 Google — *SAIF* + *Cloud CISO 2025 guidance* + *ADK safety*

- **Risk Map across 4 components**: Data, Infrastructure, Model, Application.
- **Three operating principles**:
  1. **Data is the new perimeter** — sanitize the supply chain (training data, RAG sources, KB ingestion); differential privacy; automated PII discovery.
  2. **Prompts are code** — versioned, governed, lineage-tracked, change-controlled.
  3. **Agentic AI requires identity propagation** — no broad service accounts; propagate end-user identity through every backend tool, MCP call, and A2A hop.
- **AI firewall (Model Armor pattern)**: dedicated input + output inspection layer in front of the model; sensitive-data leak detection on egress.
- **Guard-model pattern**: a second model (e.g., Gemini-as-guard) reviews high-risk outputs.
- **Identity-propagation control set**: front-end auth → identity propagation → MCP auth → A2A auth → cloud IAM.
- **Assurance controls**: continuous red teaming + vulnerability management as first-class controls (not optional).
- **Governance + Application + Data + Model + Infrastructure controls** as five distinct families.
- **CoSAI alignment** (industry coalition / shared baselines).

---

## 3. Gap Register (v3 doc vs distilled best practice)

Gaps are graded by **impact** (architectural reach) × **fan-in** (how many runtime paths intersect). Each carries a proposed L5 surface placement.

| # | Gap | Source(s) | Severity | Proposed L5 Placement |
|---|---|---|:---:|---|
| G-01 | **Named guardrail catalog absent** — Policy Validation Chokepoint is a single black box; no enumerated families (PII / Secrets / Jailbreak / Moderation / NSFW / Off-Topic / Competitors / Hallucination / URL / Keyword / Custom). | OAI, SAIF | **High** | Decompose Runtime Lane chokepoint into a guardrail bank with explicit families. |
| G-02 | **No layered guardrails (client + agent level)** — single rail vs. composed defenses. | OAI | **High** | Add a pre-chokepoint "client-level universal" rail above the existing chokepoint. |
| G-03 | **No risk-tier-proportionate enforcement** — uniform path; no low/moderate/high lane differentiation. | OAI, SAIF, Anthropic RSP | **High** | Risk-tier band selector at G1 → drives chokepoint depth + HITL + logging. |
| G-04 | **End-user identity propagation missing** — registry validates *agent* identity but not propagation of the *invoking principal* through MCP / A2A / backend tools. | SAIF (critical) | **Critical** | Add Identity Propagation rail to G2; bind principal into capability_token. |
| G-05 | **No A2A / multi-agent governance** — handoff between specialists is undefined; no cross-agent context-bleed control. | OAI handoffs, Anthropic, SAIF A2A | **High** | New "Handoff Validation" sub-lane between agents on the runtime path. |
| G-06 | **No graduated permission model** — read-only-by-default with explicit-mutation approval pattern absent. | Anthropic | **High** | Add permission ladder (read / suggest / mutate / external-side-effect) inside CERTIFY. |
| G-07 | **Capability token has no TTL / one-time-vs-permanent semantics** — single binary stamp. | Anthropic, SAIF | **Medium** | Extend capability_token schema: scope, ttl, single_use, principal, connector_allowlist. |
| G-08 | **Output-side / egress guardrails under-specified** — LLM Gateway mentions injection detection (input) but no output-side PII / secret-leak / hallucination / URL / sensitive-data inspection. | SAIF Model Armor, OAI | **Critical** | Add Egress Inspection sub-stage inside LLM Gateway (mirrored input/output). |
| G-09 | **Cross-context / long-horizon privacy compartmentalization missing** — agents can carry sensitive context across tasks/principals. | Anthropic | **High** | Add "Context Boundary Enforcement" stamp tied to capability_token scope. |
| G-10 | **No eval-driven threshold calibration loop** — invariant says learning cannot alter current run, but no specified calibration cadence / golden + adversarial corpus / promotion gate. | OAI, SAIF Assurance | **Medium** | Define out-of-band Calibration Plane feeding policy version bumps. |
| G-11 | **No continuous red-team / adversarial assurance gate** — Threat Intelligence + Promptfoo-style adversarial suites are not part of the L5 promotion contract. | OAI, Anthropic, SAIF | **High** | Add Assurance Gate as precondition for activating a new policy version. |
| G-12 | **Registries are incomplete** — only agent identity; missing Tool Registry, Prompt Registry, MCP Connector Registry. | OAI, Anthropic MCP directory | **High** | Expand "Authorized Patron List" → 4 sibling registries. |
| G-13 | **Data perimeter / supply-chain sanitization not in scope** — RAG ingestion, KB sources, training data are governed elsewhere or nowhere. | SAIF (perimeter principle) | **High** | Add explicit pre-L5 "Data Authority Resolution" hook that L5 trusts but verifies (digest match). |
| G-14 | **Capability-tier graded safeguards absent** — safeguards do not scale with detected blast radius / capability tier. | Anthropic RSP | **Medium** | Bind safeguard tier to risk-tier band (G-03) + capability_token scope. |
| G-15 | **Hard-constraint vs negotiable-policy split not modelled** — chokepoint treats all rules uniformly. | Anthropic Constitution | **Medium** | Tag policies with `hard_constraint: bool`; REMEDIATE forbidden on hard breaches. |
| G-16 | **External standards alignment hooks missing** — no NIST AI RMF / ISO 42001 / CoSAI mapping in compliance_hash payload. | OAI, SAIF/CoSAI | **Low** | Extend compliance_hash to carry standards-alignment fingerprint. |
| G-17 | **Shadow AI / bypass detection not covered** — L5 governs only requests that arrive; no discovery of agents bypassing it. | OAI | **Medium** | Out-of-plane Shadow Discovery probe feeding G1 + Audit. |
| G-18 | **Replay envelope downstream contract under-specified** — emitted but no spec for retention / independent re-verification / forensic reconstruction. | OAI ZDR, SAIF Assurance | **Medium** | Define replay_envelope schema + independent verifier in Audit Plane. |
| G-19 | **Plan / intent transparency surface absent** — Anthropic's "real-time visible to-do" pattern not represented; humans cannot inspect agent plan mid-flight. | Anthropic | **Medium** | Surface plan_digest in capability_token + live plan stream to HITL exit-control. |
| G-20 | **Guard-model pattern absent** — no "second model reviews high-risk output" stage. | SAIF Gemini-as-guard, OAI Hallucination guardrail | **Medium** | Optional Guard-Model substage of Egress Inspection (G-08). |

---

## 4. Proposed Target Architecture (v4 sketch — descriptive only)

```
G1 Invocation Triage
   └─ + risk_tier_band(low|moderate|high)              [G-03]
   └─ + shadow_discovery_probe                          [G-17]

G2 Authority Context Resolution
   ├─ Policy Set (versioned package + hard_constraint tags)  [G-10, G-15]
   ├─ Structure Blueprint
   ├─ Registries (4): Agent, Tool, Prompt, MCP Connector     [G-12]
   ├─ Data Authority Resolution (digest + supply-chain)      [G-13]
   └─ Identity Propagation (principal + scope chain)         [G-04]

STATIC LANE  (unchanged in spirit; gains registry expansion)

RUNTIME LANE
   ├─ Client-Level Universal Guardrail Bank                  [G-02]
   ├─ Agent-Level Domain Guardrail Bank (named families)     [G-01]
   ├─ Handoff Validation (A2A)                               [G-05]
   ├─ Context Boundary Enforcement                           [G-09]
   ├─ Policy Validation Chokepoint (risk-tier-proportionate) [G-03, G-14]
   └─ LLM Gateway
        ├─ Ingress Inspection (existing prompt-injection)
        ├─ Egress Inspection (PII/secret/hallucination/URL)  [G-08]
        └─ Optional Guard-Model review                       [G-20]

DECISION RAIL
   ├─ REJECT
   ├─ REMEDIATE  (forbidden on hard_constraint breach)       [G-15]
   └─ CERTIFY
        ├─ capability_token (scope, ttl, single_use,
        │   principal, connector_allowlist, plan_digest)     [G-06, G-07, G-19]
        ├─ sandbox_envelope
        ├─ compliance_hash (+ standards fingerprint)         [G-16]
        └─ replay_envelope (schema + verifier contract)      [G-18]

OUT-OF-BAND PLANES (feed policy versions, never current run)
   ├─ Calibration Plane (golden + adversarial eval loop)     [G-10]
   ├─ Assurance Plane (continuous red-team + threat intel)   [G-11]
   └─ Audit / Forensic Plane (replay verifier, retention)    [G-18]
```

---

## 5. Phase-Level Summary

| Phase ID | Title | Scope (artifacts) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| P1 | Authoring v4 doc skeleton | New `Governance & Safety v4.md` next to v3, preserving v3 invariants verbatim, adding gap-driven boxes | None — pure doc work | 6,000 | Todo |
| P2 | Capability token schema spec | `docs/reference/00_L5_Policy_Plane/capability_token.schema.md` (scope, ttl, single_use, principal, connector_allowlist, plan_digest) | Cross-cuts L3 exit-control + L5 cert | 4,500 | Todo |
| P3 | Guardrail family taxonomy | `docs/reference/00_L5_Policy_Plane/guardrail_families.md` mapping each family → input/output stage, risk-tier activation | Need to reconcile with existing `apps_shared/enforcement/*` | 5,000 | Todo |
| P4 | Identity propagation contract | `docs/contracts/identity_propagation.md` covering principal chain through MCP + A2A | Touches every tool wrapper; spec only in this plan | 4,000 | Todo |
| P5 | Risk-tier policy band spec | `docs/reference/00_L5_Policy_Plane/risk_tier_bands.md` with low/moderate/high HITL + logging + isolation matrix | Must align with existing constitutional Tier table | 3,500 | Todo |
| P6 | Calibration + Assurance planes spec | `docs/reference/00_L5_Policy_Plane/calibration_assurance_planes.md` (cadence, datasets, promotion gate, red-team CI hook) | Will reference existing `apps_eval/`, `tools/calibration/`, `config/judges/` | 5,000 | Todo |
| P7 | ADR(s) for v4 adoption | `docs/architecture/adr/ADR-NNN-l5-v4-governance-plane.md` + Notion ADR Registry row | Decision: adopt incrementally vs big-bang | 3,000 | Todo |
| P8 | Gap-to-implementation backlog | DEFERRED_SCOPE markers per gap → Wave/Phase Convergence rows with computed P-bands | Each gap becomes a tracked phase | 2,000 | Todo |

**Total est.**: ~33,000 tokens (documentation + ADRs only, no code).

---

## 6. Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---|---|---|---|
| W1 | P1, P3, P5 | Author v4 skeleton + guardrail taxonomy + risk-tier bands | 14,500 | v3 invariants stay verbatim; net-add only | Todo 🟢 | v4 doc ASCII renders; all v3 invariants preserved; gaps G-01/02/03 explicitly addressed |
| W2 | P2, P4 | Capability token + identity propagation specs | 8,500 | Schemas are descriptive Markdown, not code | Todo 🟢 | Both schemas reviewable; cover G-04, G-06, G-07, G-09 |
| W3 | P6 | Calibration + Assurance plane specs | 5,000 | Reuses existing eval infra terminology | Todo 🟢 | G-10, G-11, G-18 covered; cadence + promotion gate defined |
| W4 | P7, P8 | ADR + backlog capture | 5,000 | Notion writeback works | Todo 🟢 | ADR posted to ADR Registry; one Wave/Phase row per remaining gap with P-band |

Token estimates are documentation-only and conservative; no code budget.

---

## 7. ADG Hotspot Report

Not applicable in the strict sense — this plan does **not** edit code in this iteration. ADG hotspot analysis becomes mandatory at the *implementation* plans spawned by P8 (each gap → its own plan with full ADG_HOTSPOT_REPORT and ADG_GRAPH_LAYER_EVIDENCE sections per constitutional §22).

For situational context only: the L5 plane currently surfaces in `agentic_core/L5_safety/` (per ADR-023 runtime HITL exit-control reference). Implementation waves spawned by this plan will need fan-in queries against:
- L5 enforcement entry points (chokepoint, gateway)
- `apps_shared/enforcement/*` strategy classes
- L3 orchestration → L5 invocation edges
- L6 observability ← L5 audit emission edges

These are deferred to the per-gap implementation plans.

## 8. ADG Graph Layer Evidence

Same caveat as §7 — this is a **specification + planning** artifact, not a refactoring plan. The constitutional §22 requirement for `ADG_GRAPH_LAYER_EVIDENCE` (≥3 MVs + semantic edges + P-views) attaches to the per-gap implementation plans created in P8, not to this gap-analysis plan.

When P8 spawns implementation plans (e.g., "L5 v4 Egress Inspection wiring"), each MUST include:
- ≥3 materialized views (e.g., `mv_dependency_cone_risk` for L5 entry points, `mv_hotspot_centrality` for chokepoint, `mv_path_criticality_rollup` for gateway)
- Semantic edges: `controls_flow` (chokepoint → tool dispatch), `emits_side_effect` (gateway → external provider), `flows_to` (capability_token → execution)
- P-view cross-reference: `v_p0_write_bypass_uwg` (any state mutation that bypasses CERTIFY = P0)

---

## 9. Out of Scope for This Plan

- All code edits (per user instruction "no code edits yet").
- Implementation of any gap remediation — those become individual plans spawned by P8 with full ADG protocol.
- Changes to v3 doc content (v4 sits beside it).
- Changes to constitutional rules or `.windsurf/rules/*` (downstream of v4 adoption ADR).

---

## 10. Open Questions for User

1. **Adoption strategy** — incremental v3 → v4 (one gap per wave) vs draft-v4-then-cutover? (Author-Gate decision needed before P7 ADR.)
2. **Risk-tier vocabulary** — reuse existing constitutional T0/T1/T2/T3 tiering, or introduce a parallel L5 risk-tier (low/moderate/high) that maps onto it? (Affects G-03 / P5.)
3. **Identity propagation scope** — is end-user principal even meaningful in this single-operator workspace, or should propagation only model agent-chain principals? (Affects G-04 / P4 depth.)
4. **Calibration plane location** — fold into existing `apps_eval/` + `tools/calibration/`, or define as a new top-level plane? (Affects G-10 / P6.)

---

## 11. References

- v3 doc: `docs/reference/00_L5_Policy_Plane/Governance & Safety v3.md`
- OpenAI: *A Practical Guide to Building Agents* (PDF) + *Building Governed AI Agents Cookbook* (`developers.openai.com/cookbook/.../agentic_governance_cookbook`)
- Anthropic: *Our Framework for Developing Safe and Trustworthy Agents* (`anthropic.com/news/our-framework-for-developing-safe-and-trustworthy-agents`) + *Responsible Scaling Policy v3* + *Claude Constitution*
- Google: *Secure AI Framework* (`saif.google`) + *Cloud CISO Perspectives: Practical guidance on building with SAIF* + *SAIF Cloud Paper 2025*
- Industry: NIST AI RMF, ISO/IEC 42001, Coalition for Secure AI (CoSAI)
