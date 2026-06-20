# `apps_underwriting_ai` — Reference Implementation for AgentSpec

> **Plan**: `.codex/plans/apps-underwriting-ai-first-principles-refactor-4b1c8e.md` (W1.2)
> **Reference**: `requirements/contracts/REQ-CROSS-APP-AGENTSPEC-001.contract.yaml`
> **Instance**: `apps_underwriting_ai/config/specs/agent_spec.underwriting_decisioning.v1.0.0.yaml`

## Why This App is the Reference Implementation

Phase B comparative audit ranked the seven `apps_*` apps by severity (heaviness × tone risk × runtime cost). The result:

| Rank | App | Severity |
|---|---|---|
| 1 | apps_lic | HIGH |
| 2 | apps_rg | HIGH |
| 3 | apps_exec | MEDIUM |
| 4 | apps_eval | MEDIUM |
| 5 | apps_rfp | MEDIUM-LOW |
| 6 | apps_research | LOW |
| **7** | **apps_underwriting_ai** | **LOW (reference impl)** |

`apps_underwriting_ai` got many things right by accident of domain. Underwriting forces structural discipline: regulators, auditors, and risk committees won't accept "the model decided" as a reason. The shape that emerged is the shape that should propagate across the fleet — adjusted for legitimate per-app variations.

## What This App Got Right

### 1. YAML-First Domain Rules

```
apps_underwriting_ai/config/
├── covenant_templates.yaml        # rule_set kind
├── industry_risk_weights.yaml     # rule_set kind
├── policy_exception_rules.yaml    # policy + rule_set
├── product_rules.yaml             # rule_set kind
├── prohibited_features.yaml       # policy (veto authority)
├── underwriting_required_docs.yaml  # policy (must-haves)
└── underwriting_thresholds.yaml   # policy (numeric thresholds)
```

Seven YAML files. Each is a **structured**, **declarative**, **versioned** rule set. None is a Python module that imports state and decides logic via class hierarchies.

In the AgentSpec, all seven are bound as `domain_rules.rule_set_refs`:

```yaml
domain_rules:
  rule_set_refs:
    - apps_underwriting_ai/config/covenant_templates.yaml
    - apps_underwriting_ai/config/industry_risk_weights.yaml
    - apps_underwriting_ai/config/policy_exception_rules.yaml
    - apps_underwriting_ai/config/product_rules.yaml
    - apps_underwriting_ai/config/prohibited_features.yaml
    - apps_underwriting_ai/config/underwriting_required_docs.yaml
    - apps_underwriting_ai/config/underwriting_thresholds.yaml
```

These are `EvidencePacket.kind=rule_set` with `authority_label=authoritative` per `REQ-CROSS-APP-EVIDENCE-PACKET-001`. They carry **veto authority**: a violation of `prohibited_features` forces `verdict=reject` regardless of aggregate score.

### 2. Single Orchestrator (`decision_packet_assembler`)

Every other app in the fleet has 3–5 orchestrators. `apps_underwriting_ai` has one. The orchestrator's job is structural assembly, not decision-making — decisions emerge from the rule sets.

This maps cleanly to `agency.tier=WORKFLOW`. No tool-loop. No autonomous planning. The orchestrator is a deterministic pipeline:

```
ingest -> reconcile -> derive_features -> hypothesize_risk -> recommend -> assemble
```

### 3. Zero Tone Surface

```yaml
response_contract:
  tone_bounds:
    register: technical
    max_persona_tokens: 0   # zero — packets are structural
    forbidden:
      - flattery
      - fake_intimacy
      - mimicry_of_user_phrasing
      - inflated_certainty
      - decorative_apology
      - hedging_filler
    voice_profile_ref: null
```

Decision packets do not have a voice. They have a schema. This eliminates the entire class of contrivance failures (mimicry, forced warmth, flattery) that other apps must defend against.

### 4. `human_escalation_selector` is Correctly Positioned

`apps_underwriting_ai/reasoning/human_escalation_selector.py` is a recommender, not a decider. It selects which exceptions need human review and emits a recommendation; it does not approve or reject the loan itself. This is the `ReleaseRecommendation` pattern in miniature.

### 5. Hard Floors on Safety AND Evidence Grounding

Most apps' rubrics have a hard floor on `safety_authority`. Underwriting goes further — `evidence_grounding` is also hard-floor (4):

```yaml
min_release_thresholds:
  evidence_grounding: 4.0      # underwriting demands grounded claims
  safety: 4.0                  # hard floor
```

A decision packet that scores high on most dimensions but can't ground a numeric claim is rejected. Period.

### 6. Tight Anti-Overfit Profile

```yaml
anti_overfit_profile:
  mimicry_max: 0.30                # tighter than fleet default 0.55
  repeated_user_phrase_max: 0      # zero — packets are structural
  forced_warmth_threshold: 0.05    # near zero
  fake_history_tolerance: 0.0
  certainty_calibration_required: true
```

These thresholds make sense for underwriting because the surface is structural. Other apps need looser thresholds because their domains involve some legitimate phrasing reuse — but underwriting demonstrates the **floor**: tighter is always available when the domain permits.

## What Other Apps Should Adopt (Adjusted for Domain)

Not every app should become underwriting. But every app should ask: which of these patterns can I adopt without sacrificing legitimate domain expressivity?

| Pattern | Adopt as-is? | Per-app adaptation |
|---|---|---|
| YAML-first domain rules | Yes — for structured constraints | Add app-specific rule YAMLs to `domain_rules.rule_set_refs` |
| Single orchestrator | Where possible | Justified multi-orchestrator goes through `MULTI_AGENT` ADR (see `apps_rfp`) |
| Zero tone surface | No — only if domain warrants it | Most apps need bounded tone (`apps_lic` outreach, `apps_exec` brief) |
| Hard floor on evidence_grounding | Yes — where claims are factual | Apps with creative output may use 3.0 instead of 4.0 |
| Tight anti-overfit | Adjust per domain | `apps_lic` outreach is the canary; underwriting is the strict floor |

## What Other Apps Should NOT Adopt Verbatim

- **Zero persona tokens** — `apps_lic` and `apps_exec` need bounded persona for outreach and exec briefs.
- **No tool calls** — `apps_research` and `apps_lic` legitimately need retrieval tools.
- **`agency.tier=WORKFLOW`** — `apps_rfp` is justified MULTI_AGENT; `apps_research` and `apps_lic` are justified SINGLE_AGENT.

The point is not uniformity. The point is that **`apps_underwriting_ai`'s structural shape demonstrates how far the AgentSpec contract can go when the domain doesn't push back** — and that shape is the floor every other app's spec is measured against.

## Action: How to Apply This to Your App

When authoring a new `agent_spec.<purpose>.v1.0.0.yaml`:

1. **Start from `apps_underwriting_ai`'s spec** — copy the YAML file as a template.
2. **Justify each loosening** in a comment:
   - "tone_bounds.max_persona_tokens: 256 — outreach requires bounded voice (canary)"
   - "agency.tier: SINGLE_AGENT — research synthesis benefits from a bounded agent loop"
   - "anti_overfit_profile.repeated_user_phrase_max: 1 — RFP boilerplate reuse is legitimate"
3. **Add domain-specific rule YAMLs** to `domain_rules.rule_set_refs` when you have structured constraints (and most apps do — they're just hidden in code today).
4. **Validate** with `python ops_scripts/ci/check_cross_app_contract_schema.py`.

## References

- AgentSpec instance: `apps_underwriting_ai/config/specs/agent_spec.underwriting_decisioning.v1.0.0.yaml`
- Cross-app contract: `requirements/contracts/REQ-CROSS-APP-AGENTSPEC-001.contract.yaml`
- Evidence packet kinds: `requirements/contracts/REQ-CROSS-APP-EVIDENCE-PACKET-001.contract.yaml`
- Phase B audit findings (conversation 2026-04-29)
- ADG hotspot report: `docs/reports/adg/apps_underwriting_ai_hotspots_<ts>.md`
