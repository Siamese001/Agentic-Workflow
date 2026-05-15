========================================================================================================================
MECE ALIGNMENT FULL OVERWRITE HEADER
Canonical folder: 00A_L5_Governance_Safety
Canonical file: risk_tier_bands.md
Overwrite mode: full-file, no-overlap, implementation-grade, source-refreshed
Source refreshed from: risk_tier_bands.md
Owner summary: Cross-cutting L5 governance and certification evidence plane. Owns authority, policy, registry, capability, origin-trust, egress, HITL re-clearance, replay/audit certification evidence. Does not own live GateVerdict dispositions or durable write admission.

GLOBAL NO-OVERLAP LAW
- 00A L5 owns governance certification evidence, not live runtime dispositions and not durable write admission.
- 00B L4/UWG owns durable system-of-record state and durable write admission, not planning, routing, retrieval, execution, Exit disposition, or L6 learning mechanics.
- 00C Runtime Gates owns G01-G29 current-run GateVerdict law, not final Exit X3 aggregation and not L5 certification evidence.
- 00X owns traceability and no-loss mapping only.
- 01 Intake owns request envelope validation and identity/session/tenant baseline only.
- 02 L1 owns advisory interpretation and planning only.
- 03 L0/L3 owns deterministic route selection and optional workflow orchestration only.
- C0 owns retrieval/evidence contracts only.
- PA owns prompt packet construction only.
- 04 L2 owns bounded execution and sealing only.
- 05 Exit owns current-run checkout aggregation and exactly one X3 disposition only.
- 06 L6 owns completed-run evaluation, RCA, and future-run learning proposals only.
- 99 owns proof harnesses only; it does not own runtime behavior.

REFERENCE POINTERS
- Cross-cutting governance/certification evidence: 00A_L5_Governance_Safety/
- Durable state and Universal Write Gateway: 00B_L4_State_Archive_and_UWG/
- Current-run reusable gate mesh: 00C_Runtime_Gates_Current_Run_Mesh/
- Traceability and zero-loss proof: 00X_Requirements_Traceability_and_No_Loss_Map.md
- End-to-end runtime proof harness: 99_End_to_End_Runtime_Proof_and_Acceptance/
========================================================================================================================

# L5 Risk-Tier Bands — Proportionate Enforcement Matrix

**Scope**: Defines the `risk_tier_band` enum assigned at G1 Invocation Triage that drives chokepoint depth, HITL requirement, logging detail, sandbox isolation, and guardrail activation throughout the v4 Runtime Lane.

**Covers gaps**: G-03 (risk-proportionate enforcement), G-14 (capability-tier graded safeguards).

**Sources**:
- OpenAI *Governed Agents Cookbook* → low/moderate/high tiered controls
- Anthropic *RSP v3* → capability-tier graded safeguards (ASL-2/3/4 pattern)
- Google *SAIF* → risk-proportionate application controls

---

## 1. Relationship to Existing Constitutional Tier

The constitutional `T0 / T1 / T2 / T3` classification governs **developer-loop task scope** (how many files change, cross-layer-ness). The L5 `risk_tier_band` governs **runtime request blast radius** at execution time. They are orthogonal:

| Example | Constitutional Tier | L5 risk_tier_band |
|---|---|---|
| Cursor Agent reads a file to answer a question | T0 | LOW |
| Agent cancels a subscription via external API | T1 (if scripted) | HIGH |
| Multi-file architectural refactor | T3 | LOW (no runtime blast) |
| Agent writes to `apps_*/data/*` with PII | T2 | HIGH |

**Rule of thumb**: T0–T3 classifies the *authoring task*; LOW/MODERATE/HIGH classifies the *runtime action*.

(Open question from parent plan §10.2: user to decide whether to reuse T-tiers or keep parallel — this doc keeps parallel and maps across.)

---

## 2. Band Definitions

### 2.1 LOW

- Read-only, no external side effects, no PII/regulated data, no state mutation
- Internal productivity, non-sensitive synthesis, code-reading, docs Q&A
- Examples: reading files, ADG queries, local test runs, internal summarization

### 2.2 MODERATE

- State mutation inside trusted surface (repo files, local caches, KB ingest)
- Customer-facing output without regulated data
- Reversible external calls (idempotent reads from APIs)
- Examples: creating/editing files, writing to memory graph, querying Notion read-only, calling LLM provider

### 2.3 HIGH

- Irreversible external side effects (cancellations, payments, emails sent, deployments, external writes)
- PII / financial / regulated data in request or response
- Tool use against production systems
- Any operation touching `data_is_new_perimeter` sensitive sources (SAIF)
- Examples: external HTTP POST/DELETE, production deploy, sending notifications, writing billing data

---

## 3. Band Controls Matrix

| Control | LOW | MODERATE | HIGH |
|---|:---:|:---:|:---:|
| **Client-level guardrail bank** | ✔ | ✔ | ✔ |
| **Agent-level guardrail bank** | ✓ (subset) | ✔ | ✔ |
| **Egress inspection** | ✓ (cheap only) | ✔ | ✔ (full) |
| **Guard-model review (F-14)** | — | — | ✔ |
| **HITL required (v30 step [5])** | — | — | ✔ (or explicit persistent grant) |
| **Audit log detail** | summary | full | full + structured trace |
| **Replay envelope retention** | short | standard | extended + forensic index |
| **Sandbox isolation** | process | process + fs scope | process + fs + network egress allowlist |
| **Capability token TTL max** | 1h | 15m | 5m single-use |
| **Capability token `single_use`** | false | configurable | ✔ true |
| **Permission ladder entry point** | read/suggest | suggest/mutate | mutate/external (explicit grant only) |
| **Connector allowlist width** | default | narrowed | strict (per-tool grant) |
| **Delegation depth max (A2A)** | 3 | 2 | 1 |
| **Calibration cadence feeds** | weekly | daily | continuous |
| **Red-team assurance gate** | quarterly | monthly | pre-deploy + weekly |

---

## 4. Band Assignment Algorithm (descriptive)

```
def assign_risk_tier_band(request, context) -> Band:
    # Hard-coded HIGH triggers (any one → HIGH)
    if request.involves_external_side_effect(): return HIGH
    if request.touches_pii_or_regulated(): return HIGH
    if request.targets_production_system(): return HIGH
    if request.irreversible_mutation(): return HIGH

    # MODERATE triggers
    if request.mutates_repo_state(): return MODERATE
    if request.calls_external_llm_provider(): return MODERATE
    if request.writes_local_persistent_state(): return MODERATE

    # Default
    return LOW
```

Implementation is out of scope for this plan; the algorithm is authored here as the contract.

---

## 5. Band → Capability Token Binding

The band materializes on the `capability_token` (see `capability_token.schema.md`):

```
capability_token:
  risk_tier_band: LOW | MODERATE | HIGH
  ttl_seconds: <band-derived cap>
  single_use: <band-derived>
  permission_ladder_entry: read|suggest|mutate|external
  ...
```

Downstream execution (L3 orchestration, L2 execution, L5 exit-control) MUST honor the band's controls. Violating the matrix post-CERTIFY is a structural violation.

---

## 6. Hard Constraints

Irrespective of band:

- REMEDIATE is forbidden on any `hard_constraint: true` guardrail breach (see `guardrail_families.md` §4).
- HIGH band requires either HITL approval or a pre-existing persistent grant tied to `principal_chain`.
- Band cannot be downgraded after G1 — upgrade-only during the request lifecycle.

---

## 7. Out of Scope

- Specific TTL values per band (owned by Calibration Plane; this doc only fixes the *relative ordering* LOW > MODERATE > HIGH in restrictiveness).
- Implementation of `assign_risk_tier_band` — spawned by per-gap plan.
- Vendor-specific isolation tech (sandbox, network ACLs).
