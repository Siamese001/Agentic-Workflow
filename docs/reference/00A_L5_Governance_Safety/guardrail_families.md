========================================================================================================================
MECE ALIGNMENT FULL OVERWRITE HEADER
Canonical folder: 00A_L5_Governance_Safety
Canonical file: guardrail_families.md
Overwrite mode: full-file, no-overlap, implementation-grade, source-refreshed
Source refreshed from: guardrail_families.md
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

# L5 Guardrail Families — Taxonomy & Activation Matrix

**Scope**: Defines the named guardrail families that compose the v4 Runtime Lane's **Client-Level Universal Bank** and **Agent-Level Domain Bank**, plus the **Egress Inspection** stage in the LLM Gateway.

**Covers gaps**: G-01 (named catalog), G-02 (layered client+agent), G-08 (egress output-side).

**Sources**:
- OpenAI *Governed Agents Cookbook* → `default_spec_registry` guardrail list
- Anthropic *Framework for Safe & Trustworthy Agents* → prompt-injection classifier ensemble + threat-intel loop
- Google *SAIF* + *Model Armor* → bidirectional AI firewall (input + output)
- Internal: `apps_shared/enforcement/*` existing strategy classes

---

## 1. Family Catalog

Each family is an atomic, independently-evaluable guardrail with a scored verdict and optional remediation.

| # | Family | Purpose | Stage(s) | Source |
|---|---|---|---|---|
| F-01 | **Moderation** | CSAM / violence / hate / self-harm classifier | Ingress, Egress | OAI, SAIF |
| F-02 | **Secret Keys** | Detect API keys, tokens, credentials in prompt or output | Ingress, Egress | OAI, SAIF |
| F-03 | **Contains PII** | Detect and optionally redact PII (names, SSN, financial) | Ingress, Egress | OAI, SAIF |
| F-04 | **Jailbreak** | Known-jailbreak pattern classifier (DAN, role-play escape, etc.) | Ingress | OAI, Anthropic |
| F-05 | **Prompt Injection Detection** | Indirect injection from retrieved context / tool output | Ingress, Tool-output ingress | Anthropic, SAIF |
| F-06 | **NSFW Text** | Sexual content classifier | Ingress, Egress | OAI |
| F-07 | **URL Filter** | Allow/denylist URLs in output; phishing-domain detector | Egress | OAI, SAIF |
| F-08 | **Hallucination Detection** | Groundedness / citation-verification check vs. retrieved context | Egress | OAI, ADR-041 |
| F-09 | **Off-Topic Prompts** | Domain-boundary enforcement for specialist agents | Ingress | OAI |
| F-10 | **Competitors** | Mentions of disallowed competitor entities | Egress | OAI |
| F-11 | **Keyword Filter** | Configurable allow/denylist substrings | Ingress, Egress | OAI |
| F-12 | **Custom Prompt Check** | Domain-specific policy rule (LLM-as-judge or regex) | Ingress, Egress | OAI |
| F-13 | **Sensitive-Data Classifier** | Output-side inspection for confidential / regulated data classes | Egress | SAIF Model Armor |
| F-14 | **Guard-Model Review** | Second-model adjudication on HIGH-risk egress | Egress (HIGH tier only) | SAIF Gemini-as-guard |
| F-15 | **Handoff Validity** | A2A transfer check: handoff_description + registry match | Handoff Validation sub-lane | OAI handoffs, Anthropic |
| F-16 | **Context Bleed Detector** | Cross-task / cross-principal information-leak check | Context Boundary Enforcement | Anthropic |
| F-17 | **Supply-Chain Digest** | RAG source / KB fingerprint vs. Data Authority Resolution | Pre-ingress (via G2) | SAIF data perimeter |
| F-18 | **Threat-Intel Signature** | Known-malicious-prompt signature match from monitoring loop | Ingress | Anthropic TI |

---

## 2. Bank Assignment

### 2.1 Client-Level Universal Bank (fires for every request)

Universal, low-false-positive, cheap-to-evaluate families. Runs before any agent-specific logic.

- F-01 Moderation
- F-02 Secret Keys
- F-04 Jailbreak
- F-05 Prompt Injection Detection
- F-06 NSFW Text
- F-07 URL Filter (egress leg)
- F-11 Keyword Filter (universal denylist only)
- F-18 Threat-Intel Signature

### 2.2 Agent-Level Domain Bank (bound to agent spec)

Domain-specific, may be expensive, configurable per agent via Prompt Registry + Agent Registry metadata.

- F-03 Contains PII
- F-08 Hallucination Detection
- F-09 Off-Topic Prompts
- F-10 Competitors
- F-11 Keyword Filter (agent-specific lists)
- F-12 Custom Prompt Check

### 2.3 Egress Inspection (LLM Gateway — bidirectional AI firewall)

Mirror of ingress, applied to model output before it leaves the gateway.

- F-01 Moderation (output)
- F-02 Secret Keys (leak detection)
- F-03 Contains PII (leak detection)
- F-06 NSFW Text (output)
- F-07 URL Filter (output)
- F-08 Hallucination Detection
- F-10 Competitors
- F-13 Sensitive-Data Classifier
- F-14 Guard-Model Review *(HIGH risk tier only)*

### 2.4 Handoff + Context sub-lanes

- F-15 Handoff Validity → Handoff Validation sub-lane
- F-16 Context Bleed Detector → Context Boundary Enforcement sub-lane
- F-17 Supply-Chain Digest → consumed at G2 Data Authority Resolution

---

## 3. Risk-Tier Activation Matrix

Activation by `risk_tier_band` (see `risk_tier_bands.md`). ✔ = mandatory, ✓ = optional/configurable, — = skipped.

| Family | LOW | MODERATE | HIGH |
|---|:---:|:---:|:---:|
| F-01 Moderation | ✔ | ✔ | ✔ |
| F-02 Secret Keys | ✔ | ✔ | ✔ |
| F-03 Contains PII | ✓ | ✔ | ✔ |
| F-04 Jailbreak | ✔ | ✔ | ✔ |
| F-05 Prompt Injection | ✔ | ✔ | ✔ |
| F-06 NSFW | ✓ | ✔ | ✔ |
| F-07 URL Filter | ✓ | ✔ | ✔ |
| F-08 Hallucination | — | ✓ | ✔ |
| F-09 Off-Topic | ✓ | ✔ | ✔ |
| F-10 Competitors | — | ✓ | ✔ |
| F-11 Keyword Filter | ✓ | ✔ | ✔ |
| F-12 Custom Prompt Check | ✓ | ✔ | ✔ |
| F-13 Sensitive-Data | — | ✓ | ✔ |
| F-14 Guard-Model Review | — | — | ✔ |
| F-15 Handoff Validity | ✔ | ✔ | ✔ |
| F-16 Context Bleed | ✓ | ✔ | ✔ |
| F-17 Supply-Chain Digest | ✔ | ✔ | ✔ |
| F-18 Threat-Intel Signature | ✔ | ✔ | ✔ |

---

## 4. Family Record Schema (descriptive)

```
GuardrailFamilyRecord:
  id: F-NN
  name: str
  stage: enum{ INGRESS | EGRESS | HANDOFF | CONTEXT | SUPPLY_CHAIN }
  bank: enum{ CLIENT_UNIVERSAL | AGENT_DOMAIN | EGRESS_INSPECTION }
  evaluator_kind: enum{ REGEX | CLASSIFIER | LLM_JUDGE | GUARD_MODEL | DIGEST_MATCH }
  risk_tier_activation: { LOW: bool, MODERATE: bool, HIGH: bool }
  hard_constraint: bool              # if true, REMEDIATE forbidden on breach
  remediable_when_false: bool        # may re-enter L5 with sanitized input
  owner: str                         # policy owner (Agent Registry link)
  eval_dataset_ref: str              # Calibration Plane corpus pointer
  version: semver
  threshold: float                   # promoted via Calibration Plane
```

---

## 5. Implementation Notes (descriptive — not yet wired)

- Existing `apps_shared/enforcement/*Strategy.py` classes are the closest structural match; many map 1:1 to families (e.g., `AdaptiveretrievalgateStrategy` ↔ F-05, `CircuitbreakerStrategy` ↔ fail-closed semantics).
- Each family's `threshold` is frozen at CERTIFY time and carried in `compliance_hash`; Calibration Plane promotions produce a new policy version only (§V4 Invariant).
- `hard_constraint: true` flagged families: F-01 (Moderation CSAM class), F-02 (Secret Keys), F-04 (Jailbreak), F-05 (Prompt Injection), F-17 (Supply-Chain Digest), F-18 (Threat-Intel Signature). REMEDIATE path is forbidden on breach.

---

## 6. Out of Scope

- Implementation classes / code (spawned by per-gap plans via P8 backlog).
- Specific threshold values (owned by Calibration Plane `config/judges/`).
- Vendor-specific classifier bindings (deferred to `apps_shared/enforcement/`).
