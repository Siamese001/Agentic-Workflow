# THREAT MODEL — apps_lic

> **Threat-model methodology:** STRIDE per hop boundary; HITL-aware.
> **Scope:** apps_lic (LinkedIn / Lead Intelligence & Composition) only.
> **Last reviewed:** 2026-04-29
> **Owner:** see `CODEOWNERS`

## Why This App Needs a Threat Model

apps_lic composes outbound messages on behalf of the user (LinkedIn-style outreach). The threat surface is:

1. **Outbound impersonation risk** — messages sent in user's voice; if the model produces something the user wouldn't approve, the user owns the consequence.
2. **Recipient PII handling** — recipient names, profiles, sometimes inferred attributes. Fair-use boundaries apply.
3. **Replay & determinism** — every composed message must be replayable for audit, especially if a recipient complains.

These are different from `apps_underwriting_ai` threats (regulated decisioning) — but no less real for an SVP+ panel asking "how does your sender-tooling avoid generating a regrettable message?"

## Asset Inventory

| Asset | Class | Sensitivity | Where it lives |
|---|---|---|---|
| Recipient profile data | **PII-Standard** (3rd party) | Medium — fair-use bounded | Knowledge base; cached briefly during hop chain |
| Sender voice profile (the user's own writing style) | **User config** | Medium — modeled-from-user | `apps_lic/config/voice_profile.json` |
| Composed message body | **Outbound artifact** | High — represents the user externally | Rendered output; must be replayable |
| Hop chain telemetry | **Operational** | Low | OTEL spans (no recipient PII) |
| Determinism digest | **Audit signal** | High — integrity foundation | Per-run digest in evidence trail |
| Knowledge base entries | **Mixed** (some PII) | Medium | `apps_shared/data/sender_knowledge_base.json` and adapters |

## Trust Boundaries

```
[ Sender (user) request ]
       │  (authenticated)
       ▼
[ Archetype indicator ] — input shape detection      ← Boundary A
       │
       ▼
[ Knowledge-base lookup ] — recipient/sender data    ← Boundary B (PII enters)
       │
       ▼
[ Voice-profile match ] — sender style retrieval     ← Boundary C
       │
       ▼
[ Message-body composer ] — LLM-driven                ← Boundary D (LLM processes PII)
       │
       ▼
[ Validator chain ] — multiple gate stages           ← Boundary E (HITL escape hatch)
       │
       ▼
[ Determinism digest emit ] — audit envelope          ← Boundary F
       │
       ▼
[ Outbound delivery ]                                 ← out of scope
```

## STRIDE Analysis (per boundary)

### Boundary A: Sender Request

| Threat | Description | Control |
|---|---|---|
| **Spoofing** | Attacker submits as a different sender | Authentication at ingress; sender-identity propagated through hop chain |
| **EOP** | Sender requests a message exceeding their permitted scope (volume, target audience) | Per-sender quota in `retry_policy_config.py` (volumetric); composition policy in `apps_lic/config/lic_policies.yaml` |

### Boundary B: PII Enters

| Threat | Description | Control |
|---|---|---|
| **Info disclosure** | Recipient PII leaked to logs / telemetry | OTEL spans MUST exclude recipient name, email, profile URL — use opaque IDs only. CI gate (TODO) — `check_pii_in_lic_telemetry.py` |
| **Tampering** | KB entry altered between lookup and composition | KB entries hashed at lookup; hash propagated through hop chain |
| **Repudiation** | Sender later claims a recipient was never targeted | KB lookup logged in evidence trail with KB version |

### Boundary D: LLM Processes PII (HIGHEST RISK)

| Threat | Description | Control |
|---|---|---|
| **Info disclosure** | LLM regurgitates recipient PII in unintended ways | Composer prompt template restricts what the LLM can mention; validator chain (Boundary E) audits the output |
| **Tampering** | Prompt injection from KB content (recipient profile contains crafted text) | Input sanitization at Boundary B; prompt template uses structured fields, not free-form concatenation |
| **EOP** | LLM produces content the sender did not authorize (off-policy claim, off-scope offer) | Validator chain checks for forbidden topics; HITL escalation if uncertain |

**Architectural note:** message-body composer is the **highest-risk hop** in apps_lic. Almost every threat concentrates here.

### Boundary E: Validator Chain + HITL

| Threat | Description | Control |
|---|---|---|
| **EOP** | Message bypasses validator chain (e.g., admin override) | No admin override exists; HITL is the only escape hatch and it routes to a human, not back to auto-send |
| **Tampering** | Validator config tweaked to permit otherwise-rejected content | Config changes require Author-Gate (constitutional §6); CI gate enforces this on validator-rule files |

### Boundary F: Determinism Digest

| Threat | Description | Control |
|---|---|---|
| **Repudiation** | Sender later claims they didn't compose a particular message | Determinism digest + replay capability + evidence trail prove origin |
| **Tampering** | Digest replaced post-emission | Digest signed; signature verified before delivery |

## Composition Policy (what the LLM is permitted to claim)

apps_lic enforces a content policy at the validator stage:

| Allowed | Restricted | Forbidden |
|---|---|---|
| Sender's documented capabilities | Pricing claims (require explicit sender confirmation) | Claims about recipient's protected attributes |
| Sender's documented experience | Forward-looking commitments (require disclaimers) | Manipulative urgency / scarcity tactics |
| Public information about recipient | Inferred attributes about recipient | Personal information not in the KB |
| References to mutual connections (if in KB) | Claims of mutual familiarity not in data | Fabricated context |

## Known Gaps & Mitigations

| Gap | Severity | Mitigation Plan |
|---|---|---|
| Prompt-injection corpus not exercised | High | NEXT_STEP — wire `ops_scripts/assurance/red_team_runner.py` to lic fixtures |
| Per-recipient PII redaction in OTEL spans not yet enforced via CI | High | NEXT_STEP — `check_pii_in_lic_telemetry.py` |
| No content-policy version-pinning per outbound message | Medium | Track in DEFERRED_SCOPE; tie to determinism digest |
| HITL handoff has no SLA on human turnaround | Medium | Document in HITL operator runbook (when written) |

## Why This Document Matters for the SVP+ Narrative

The strongest portfolio narrative for apps_lic is: "I built an outbound composition system with a hop registry, per-stage SLOs, content policy enforced at the validator boundary, HITL fallback, and full determinism replay — to mitigate the regrettable-message risk." This threat model is the architecture spec for that claim.

## Threat-Model Review Cadence

- Reviewed quarterly by app owner.
- Triggered review on: composer prompt change, validator rule change, new policy class, security incident.
