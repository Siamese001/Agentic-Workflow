========================================================================================================================================================================================
[ ABOVE GOVERNANCE & SAFETY CONTEXT | governed packet enters from routing/orchestration (Patron arriving with a reading list) ]
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
INVARIANT: no execution, mutation, or external call proceeds without L5 certification (Head Librarian's Stamp) against active policy + structure + registry + principal chain
ADDITIONAL INVARIANT (v4): every certification carries an identity chain (principal → agent → tool/connector) and a scoped, TTL-bounded capability_token
========================================================================================================================================================================================
                                                                    │
                                                               [ walks in ]
                                                                    ▼
========================================================================================================================================================================================
[ GOVERNANCE & SAFETY | L5 ENFORCEMENT PLANE | v4 (v3 preserved verbatim + gap-driven additions from OAI / Anthropic / SAIF) ]
========================================================================================================================================================================================

┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ G1: GOVERNANCE INVOCATION | Front Desk Triage  [v3 preserved + v4 additions]                                                                                                 │
├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ - receive request for governance review (Patron submits reading request)                                                                                                     │
│ - identify mode: STATIC_CHECK | RUNTIME_CHECK | HUMAN_REENTRY                                                                                                                │
│ - route into appropriate enforcement lane                                                                                                                                    │
│ [V4+] assign risk_tier_band = { LOW | MODERATE | HIGH } (see risk_tier_bands.md)            ──► drives chokepoint depth, HITL requirement, logging detail [G-03]            │
│ [V4+] shadow_discovery_probe: detect bypass attempts before triage exits                                                                                   [G-17]            │
│ [OUT: governance mode + review request + risk_tier_band (Patron Slip, tiered)]                                                                                               │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                                    │
                                                              [ hands slip ]
                                                                    ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ G2: AUTHORITY CONTEXT RESOLUTION | The Master Charter Desk  [v3 preserved + v4 expansions]                                                                                   │
├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ - resolve active policy set (versioned package; each rule tagged hard_constraint: true|false)                                                         [G-10, G-15]          │
│ - resolve structure blueprint (Stack Map)                                                                                                                                    │
│ - resolve registry constraints — FOUR sibling registries                                                                                                          [G-12]     │
│     • Agent Registry         (identity, allowed_models, execution_mode, registry_digest)                                                                                     │
│     • Tool Registry          (auth scopes, data access, approval authority, risk tier)                                                                                       │
│     • Prompt Registry        (version, lineage, rollback policy, exemplar eligibility)                                                                                       │
│     • MCP Connector Registry (enterprise allowlist, one-time vs permanent grant, data sensitivity)                                                                           │
│ - [V4+] Data Authority Resolution — supply-chain digest + RAG-source vetting fingerprint                                                                          [G-13]     │
│ - [V4+] Identity Propagation — bind principal chain: { invoking_user, agent_id, parent_agent_id?, delegation_depth, scope }                                       [G-04]     │
│ [INVARIANT: downstream enforcement uses resolved authority only; ad-hoc rules forbidden; hard_constraint rules are not remediable]                                           │
│ [OUT: governed validation context + principal_chain + data_digest (Stamped Reference Folder, v4)]                                                                            │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                                    │
                                                              [ enters wing ]
                                                                    ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ DUAL ENFORCEMENT RAILS (CO-LOCATED, LOGICALLY ISOLATED)                                                                                                                      │
├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                                                                                              │
│  ── STATIC LANE (PREVENTION | Floor Plan + Dewey Decimal + Authorized Patron Registry) ──────────────────────────────────────────────────────────────────────────────────── │
│   ┌──────────────────────────────┐          ┌──────────────────────────────┐          ┌──────────────────────────────┐                                                       │
│   │ STRUCTURE ENFORCEMENT        │[ maps to]│ CLASSIFICATION KERNEL        │[ tags to]│ REGISTRY VALIDATION (x4)     │                                                       │
│   │ - path / territory / layers  │───→→───→ │ - AST type classification    │───→→───→ │ - Agent / Tool / Prompt /    │                                                       │
│   │ - depth + placement rules    │          │ - dual-tag conflict detect   │          │   MCP Connector registries   │                                                       │
│   │ - cross-domain violations    │          │                              │          │ - registry_digest match      │                                                       │
│   │ [no structural drift]        │          │ [type SSOT]                  │          │ [identity + capability gate] │                                                       │
│   └──────────────┬───────────────┘          └──────────────┬───────────────┘          └──────────────┬───────────────┘                                                       │
│                  │                                         │                                         │                                                                       │
│                  └─────────────────────────────────────────┴─────────────────────────────────────────┘                                                                       │
│                                                                    │                                                                                                         │
│                                                              [ drops down ]                                                                                                  │
│                                                                    ▼                                                                                                         │
│                                                                                                                                                                              │
│  ── RUNTIME LANE (CONTAINMENT | Layered Guardrails + Handoff Validation + Restricted Section + Interlibrary Loan Exit) ─────────────────────────────────────────────────    │
│                                                                                                                                                                              │
│     ┌──────────────────────────────────────────────────────────┐                                                                                                             │
│     │ [V4+] CLIENT-LEVEL UNIVERSAL GUARDRAIL BANK               │  [G-02]                                                                                                    │
│     │ (runs for every call, regardless of agent)                │                                                                                                            │
│     │ - Moderation | Secret Keys | URL Filter | Jailbreak       │                                                                                                            │
│     │ - Prompt Injection Detection | NSFW | Custom Prompt Check │                                                                                                            │
│     └─────────────────────────┬────────────────────────────────┘                                                                                                              │
│                               ▼                                                                                                                                              │
│     ┌──────────────────────────────────────────────────────────┐                                                                                                             │
│     │ [V4+] AGENT-LEVEL DOMAIN GUARDRAIL BANK                   │  [G-01]                                                                                                    │
│     │ (bound to agent spec; domain-specific)                    │                                                                                                            │
│     │ - Contains PII | Hallucination Detection | Off-Topic      │                                                                                                            │
│     │ - Competitors | Keyword Filter | Domain Constraints       │                                                                                                            │
│     │ see: guardrail_families.md                                │                                                                                                            │
│     └─────────────────────────┬────────────────────────────────┘                                                                                                              │
│                               ▼                                                                                                                                              │
│     ┌──────────────────────────────────────────────────────────┐                                                                                                             │
│     │ [V4+] HANDOFF VALIDATION (A2A)                            │  [G-05]                                                                                                    │
│     │ - specialist → specialist transfer check                  │                                                                                                            │
│     │ - handoff_description present + registry match            │                                                                                                            │
│     │ - principal_chain propagated; delegation_depth <= max     │                                                                                                            │
│     │ [denies cross-agent context bleed]                        │                                                                                                            │
│     └─────────────────────────┬────────────────────────────────┘                                                                                                              │
│                               ▼                                                                                                                                              │
│     ┌──────────────────────────────────────────────────────────┐                                                                                                             │
│     │ [V4+] CONTEXT BOUNDARY ENFORCEMENT                        │  [G-09]                                                                                                    │
│     │ - cross-task / cross-principal info-bleed detector        │                                                                                                            │
│     │ - context scope tag attached to capability_token          │                                                                                                            │
│     └─────────────────────────┬────────────────────────────────┘                                                                                                              │
│                               ▼                                                                                                                                              │
│     ┌──────────────────────────────────────────────────────────┐                                                                                                             │
│     │ POLICY VALIDATION CHOKEPOINT (risk-tier-proportionate)    │  [G-03, G-14]                                                                                              │
│     │ - risk_tier_band drives depth:                            │                                                                                                            │
│     │     LOW      → fast-track, minimal log                    │                                                                                                            │
│     │     MODERATE → standard guardrails + audit                │                                                                                                            │
│     │     HIGH     → enhanced log + HITL + isolated sandbox     │                                                                                                            │
│     │ - validate tools / actions / plan                         │                                                                                                            │
│     │ - approve / reject / remediate (REMEDIATE forbidden on    │                                                                                                            │
│     │   hard_constraint breaches)                               │                                                                                                            │
│     │ [hard stop on violation]                                  │                                                                                                            │
│     └─────────────────────────┬────────────────────────────────┘                                                                                                              │
│                               ▼                                                                                                                                              │
│     ┌──────────────────────────────────────────────────────────┐                                                                                                             │
│     │ LLM GATEWAY (SOVEREIGN EGRESS) — v4 expanded              │                                                                                                            │
│     │ - symbolic → provider resolution                          │                                                                                                            │
│     │ - [v3] INGRESS INSPECTION: prompt injection detection     │                                                                                                            │
│     │ - [V4+] EGRESS INSPECTION (bidirectional AI firewall):    │  [G-08]                                                                                                    │
│     │     • PII leak / Secret leak / URL filter                 │                                                                                                            │
│     │     • Hallucination / groundedness check                  │                                                                                                            │
│     │     • Sensitive-data classifier                           │                                                                                                            │
│     │ - [V4+] OPTIONAL GUARD-MODEL REVIEW on HIGH-risk          │  [G-20]                                                                                                    │
│     │ - audit log + replay envelope                             │                                                                                                            │
│     │ - fail-closed (no silent fallback)                        │                                                                                                            │
│     │ [only path to external models/archives]                   │                                                                                                            │
│     └─────────────────────────┬────────────────────────────────┘                                                                                                              │
│                               ▼                                                                                                                                              │
│                                                                                                                                                                              │
├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ DECISION RAIL (EXPLICIT, TERMINAL AUTHORITY | The Head Librarian's Desk)                                                                                                     │
├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│         ┌───────────────────────┬────────────────────────┬────────────────────────┐                                                                                          │
│         │ REJECT                │ REMEDIATE              │ CERTIFY                │                                                                                          │
│         │ (Revoke Card)         │ (Suggest Edits)        │ (Stamp of Approval)    │                                                                                          │
│         ├───────────────────────┼────────────────────────┼────────────────────────┤                                                                                          │
│         │ - stop execution      │ - sanitize / adjust    │ - attach compliance    │                                                                                          │
│         │ - return upstream     │ - re-enter L5          │   + standards fp [G-16]│                                                                                          │
│         │                       │ - FORBIDDEN on         │ - bind capability_token│                                                                                          │
│         │                       │   hard_constraint [G-15│   { scope, ttl,        │  [G-06, G-07, G-19]                                                                       │
│         │                       │                        │     single_use,        │                                                                                          │
│         │                       │                        │     principal_chain,   │                                                                                          │
│         │                       │                        │     connector_allowlist│                                                                                          │
│         │                       │                        │     plan_digest,       │                                                                                          │
│         │                       │                        │     permission_ladder }│                                                                                          │
│         │                       │                        │ - bind sandbox_envelope│                                                                                          │
│         │                       │                        │ - emit audit record +  │                                                                                          │
│         │                       │                        │   replay_envelope      │  [G-18]                                                                                   │
│         └───────────────┬───────┴───────────────┬────────┴───────────────┬────────┘                                                                                          │
│                         │                       │                        │                                                                                                   │
│                    [ tears up ]           [ hands back ]       [ stamps approved ]                                                                                           │
│                         ▼                       ▼                        ▼                                                                                                   │
│                 [ FAIL / RETURN ]        [ RE-VALIDATE LOOP ]      [ GOVERNED EXECUTION CONTINUES ]                                                                          │
│                                                                                                                                                                              │
│ [INVARIANT: every human modification, plan change, tool call, or LLM request must traverse this rail before gaining execution authority]                                     │
│ [V4 INVARIANT: REMEDIATE is forbidden when the breached rule is tagged hard_constraint: true — REJECT is the only exit]                                                      │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                                    │
                                                              [ walks out ]
                                                                    ▼
========================================================================================================================================================================================
[ OUT-OF-BAND PLANES (v4) | feed policy versions; NEVER alter current certified run ]
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
┌────────────────────────────────────────┐  ┌────────────────────────────────────────┐  ┌────────────────────────────────────────┐
│ CALIBRATION PLANE                       │  │ ASSURANCE PLANE                         │  │ AUDIT / FORENSIC PLANE                 │
│ (Golden + adversarial corpus;           │  │ (Continuous red-team + threat intel;    │  │ (replay_envelope verifier;             │
│  threshold tuning with promotion gate)  │  │  Promptfoo-style CI; misalignment evals)│  │  retention + independent reconstruction)│
│ [G-10]                                  │  │ [G-11]                                  │  │ [G-18]                                  │
└─────────────────────┬──────────────────┘  └─────────────────────┬──────────────────┘  └─────────────────────┬──────────────────┘
                      └────────────────────────────┬───────────────┴─────────────────────────────┬───────────┘
                                                   ▼                                             ▼
                                      [ policy version bump ]                           [ forensic replay / compliance attestation ]
                                      (enters G2 on next packet; never retroactive)
========================================================================================================================================================================================
[ BELOW GOVERNANCE & SAFETY CONTEXT | certified outputs propagate to execution / exit / observability (Patron leaves with stamped books) ]
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
OUTPUTS = GovernanceResult
       | compliance_hash (+ standards_fingerprint: NIST_AI_RMF | ISO_42001 | CoSAI_baselines | sector overlays)
       | audit_log
       | replay_envelope (schema-versioned; see capability_token.schema.md + replay_envelope spec)
       | capability_token (v4: scope, ttl, single_use, principal_chain, connector_allowlist, plan_digest, permission_ladder)
       | sandbox_envelope

INVARIANT = learning signals may inform future thresholds but cannot alter the current certified run
V4 INVARIANT = every out-of-band plane feeds policy_version_next; current run is immutable post-CERTIFY
========================================================================================================================================================================================

Cross-references:
  - docs/reference/00_L5_Policy_Plane/Governance & Safety v3.md   (v3, preserved)
  - docs/reference/00_L5_Policy_Plane/guardrail_families.md       (P3 / G-01, G-02, G-08)
  - docs/reference/00_L5_Policy_Plane/risk_tier_bands.md          (P5 / G-03, G-14)
  - docs/reference/00_L5_Policy_Plane/capability_token.schema.md  (P2 / G-06, G-07, G-09, G-19)
  - docs/contracts/identity_propagation.md                        (P4 / G-04, G-05)
  - docs/reference/00_L5_Policy_Plane/calibration_assurance_planes.md (P6 / G-10, G-11, G-18)
  - docs/architecture/adr/ADR-049-l5-v4-governance-plane.md       (P7)
  - .windsurf/plans/l5-governance-best-practice-gap-4615ae.md     (parent plan)
