# ADR-049: L5 v4 Governance & Safety Plane — Gap-Driven Expansion

- **Status**: Accepted
- **Decision Date**: 2026-04-24
- **Deciders**: Repo operator (ratified 2026-04-24 via 4-question Author-Gate sequence)
- **Impact Layers**: L5 (primary), L3 (capability_token consumer), L2 (tool authorization), L4 (memory/context compartmentalization), L6 (audit/forensic emission)
- **Supersedes**: (extends) `docs/reference/00_L5_Policy_Plane/Governance & Safety v3.md`
- **Parent plan**: `.windsurf/plans/l5-governance-best-practice-gap-4615ae.md`

---

## 1. Context

The v3 L5 Governance & Safety doc (v25 single-box triple-click) is architecturally sound but predates recent authoritative agent-governance guidance from OpenAI (*Practical Guide to Building Agents*, *Governed Agents Cookbook*), Anthropic (*Framework for Safe & Trustworthy Agents*, *RSP v3*, *Claude Constitution*), and Google (*Secure AI Framework* + *Cloud CISO 2025 SAIF guidance*).

Twenty gaps were identified (§3 of parent plan), spanning:
- Layered + named guardrail catalog (OAI)
- Risk-tier-proportionate enforcement (OAI, SAIF, Anthropic RSP)
- End-user identity propagation (SAIF — critical)
- A2A handoff governance (OAI, SAIF)
- Graduated permission model + capability TTL (Anthropic)
- Output-side / egress inspection AI firewall (SAIF Model Armor — critical)
- Cross-context privacy compartmentalization (Anthropic)
- Calibration + Assurance + Audit/Forensic out-of-band planes (all three vendors)
- Four sibling registries: Agent / Tool / Prompt / MCP Connector (OAI)
- Data-perimeter / supply-chain sanitization (SAIF)
- Standards alignment fingerprint (NIST AI RMF, ISO/IEC 42001, CoSAI)

---

## 2. Decision

Adopt **L5 v4** as the next governance plane specification, authored as a net-additive expansion of v3. Key decisions:

1. **v3 invariants are preserved verbatim.** v4 sits beside v3, not replacing it on disk. Invariants are upgraded (not reversed) with two v4-specific additions: (a) every CERTIFY carries a principal chain, and (b) out-of-band planes feed `policy_version_next`, never the current run.

2. **Twenty gaps mapped onto a descriptive v4 architecture** (see `Governance & Safety v4.md` §4 diagram): risk-tier bands at G1, four sibling registries + Data Authority Resolution + Identity Propagation at G2, layered guardrail banks + Handoff Validation + Context Boundary Enforcement in Runtime Lane, bidirectional AI firewall in LLM Gateway, upgraded capability_token in CERTIFY, and three out-of-band planes (Calibration / Assurance / Audit/Forensic).

3. **Capability token schema v4** (`capability_token.schema.md`): adds `principal_chain`, `risk_tier_band`, `permission_ladder_entry`, `ttl_seconds` + `single_use`, `connector_allowlist` + `tool_allowlist`, `plan_digest` + `plan_stream_endpoint`, `standards_fingerprint`. Permission ladder rungs: read / suggest / mutate / external.

4. **Identity propagation is the critical path** (`docs/contracts/identity_propagation.md`): every action attributable to a specific `invoking_user`, ban on broad service accounts, chain appended-only on A2A handoff, delegation_depth capped by risk tier.

5. **Hard-constraint tagging**: every policy rule carries `hard_constraint: bool`. REMEDIATE is forbidden on hard-constraint breaches — REJECT is the only exit. CSAM moderation, secret-key detection, jailbreak, prompt injection, supply-chain digest, and threat-intel signatures default to `hard_constraint: true`.

6. **Incremental adoption** (vs big-bang cutover): each of the 20 gaps becomes its own implementation plan spawned via `DEFERRED_SCOPE` markers in this wave. v3 remains authoritative at runtime until per-gap plans land their implementations and ratchet the spec from v3 → v4 family by family.

---

## 3. Consequences

### Positive
- Closes two **critical** gaps (G-04 identity propagation, G-08 egress inspection) that SAIF/OpenAI both mark as table-stakes for production agent governance.
- Aligns with NIST AI RMF, ISO/IEC 42001, CoSAI baselines via `standards_fingerprint` in `compliance_hash`.
- Makes `capability_token` the single verifiable artifact carrying everything L5 exit-control (ADR-023) needs to gate any action.
- Establishes three out-of-band planes so policy evolution is explicit, gated, and attestable — instead of drifting implicitly.
- Does not break existing v3 consumers; v4 is net-additive.

### Negative / cost
- ~20 per-gap implementation plans to schedule (captured via `DEFERRED_SCOPE` backlog).
- Capability token becomes heavier; serialization and verification cost grows. Mitigation: verify-fast path for LOW band; full path for HIGH.
- Identity propagation requires touching every tool wrapper / MCP client; blast radius spans L2/L3/L4.
- Red-team CI and assurance plane are net-new ops obligations.

### Risks
- **Adoption friction** if developers perceive v4 as a compliance burden rather than a safety enabler (OAI finding: *"Governance enables adoption"* — framing matters).
- **Drift risk** if some gaps are implemented and others shelved — intermediate state must remain internally consistent. Mitigation: each per-gap plan explicitly states its pre/post invariants.
- **Open questions** in parent plan §10 still need ratification before W1 implementations start (adoption strategy, tier vocabulary, propagation depth in single-operator context, calibration plane location).

---

## 4. Alternatives Considered

| Alt | Why rejected |
|---|---|
| Monolithic v3 → v4 cutover with retroactive re-certification | Too large a blast radius; violates incremental adoption rule from constitutional §SVP; no clean rollback. |
| Leave v3 as-is and rely on vendor-side guardrails only | Fails SAIF identity-propagation requirement; leaves egress inspection gap; no out-of-band calibration. |
| Adopt SAIF controls only (skip OAI / Anthropic additions) | Loses named guardrail catalog, permission ladder, A2A handoff governance. |
| Wait for industry standard (CoSAI baselines v1.0) | Available now vs. waiting; v4 explicitly tags standards_fingerprint so future alignment is incremental. |

---

## 5. Implementation

This ADR authorizes the **spec artifacts** in W1-W3 of the parent plan:

- `docs/reference/00_L5_Policy_Plane/Governance & Safety v4.md`
- `docs/reference/00_L5_Policy_Plane/guardrail_families.md`
- `docs/reference/00_L5_Policy_Plane/risk_tier_bands.md`
- `docs/reference/00_L5_Policy_Plane/capability_token.schema.md`
- `docs/reference/00_L5_Policy_Plane/calibration_assurance_planes.md`
- `docs/contracts/identity_propagation.md`

Implementation of each of the 20 gaps is **explicitly deferred** — see §6.

---

## 6. Deferred Scope

Each gap is a stand-alone implementation plan, captured as a `DEFERRED_SCOPE` marker in the response that posted this ADR. Scorer will assign P-bands; critical gaps (G-04, G-08) will score P1 by the deterministic layer × fan-in × surface formula.

---

## 7. Ratified Decisions (2026-04-24)

Four open questions resolved via Author-Gate sequence. All four captured in the Author-Gate Decision Ledger.

| # | Question | Decision | Confidence | Principle |
|---|---|---|---:|---|
| 7.1 | Adoption strategy | **Incremental gap-by-gap** (v3 stays authoritative until per-gap ratchet) | 0.91 | Incremental over big-bang (SVP §9) |
| 7.2 | Risk-tier vocabulary | **Parallel** to T0–T3 with mapping table in `risk_tier_bands.md §1` | 0.86 | Orthogonal axes preserved |
| 7.3 | Identity propagation depth | **Full `principal_chain` now**, `invoking_user` env-seeded in single-operator mode | 0.88 | Deployment-invariant identity |
| 7.4 | Planes location | **Fold into existing infra as roles** (apps_eval/, tools/calibration/, ops_scripts/, L6_observability); new net-adds only | 0.84 | Reuse over duplication |

**Implementation consequences**:
- Pull order for per-gap plans: P1-band first → **G-04 (identity propagation)**, then **G-08 (egress inspection)**.
- v4 spec docs already reflect all four decisions — no further spec edits required from ratification.
- Each gap implementation plan MUST respect Q3: full `principal_chain` schema plumbed through every new code path (no deferred invoker slot).

---

## 8. References

- OpenAI *A Practical Guide to Building Agents* + *Building Governed AI Agents Cookbook*
- Anthropic *Our Framework for Developing Safe and Trustworthy Agents* + *Responsible Scaling Policy v3* + *Claude Constitution*
- Google *Secure AI Framework* (saif.google) + *Cloud CISO Perspectives: Practical guidance on building with SAIF* (2026-04)
- NIST AI RMF, ISO/IEC 42001, Coalition for Secure AI (CoSAI)
- v3: `docs/reference/00_L5_Policy_Plane/Governance & Safety v3.md`
- ADR-023 (Runtime HITL exit-control)
- ADR-044 (Request intake envelope hardening)
- ADR-041 (Hallucination / groundedness split)
- ADR-042 (Exit kill switch)
