---
name: ledger-consulter
description: Base template for consulting a single intelligence ledger before acting. This skill itself is not auto-invoked; the ten per-ledger consulting skills (ledger-consulter-tool-routing, ledger-consulter-refactor-outcome, etc.) inherit this contract. See `.windsurf/plans/intelligence-ledgers-ten-a7c3e2.md` for the full rollout.
trigger: manual
---

# Ledger-Consulter Template

## Purpose

Surface precedent from a given intelligence ledger (`artifacts/ledgers/<name>.sqlite`) so the current decision is biased by prior outcomes. Analogous to `refactor-decision-memory` but parameterized over any of the ten ledgers.

## Contract

Every per-ledger consulting skill MUST:

1. State its ledger name (matching `tools.ledgers.schema_registry.LEDGER_REGISTRY[*].name`).
2. Declare the trigger features that mean "consult me now" (observable query or context signals).
3. Show the minimal code snippet to query the ledger:

   ```python
   from tools.ledgers import LedgerConsulter
   verdict = LedgerConsulter("<ledger_name>").lookup(
       query_text="<current intent summary>",
       filters={"event_kind": "<specific-kind>"},
       limit=5,
   )
   ```

4. Map verdict strength → action:

   | `verdict.strength` | Required behavior |
   |---|---|
   | `strong` | Bias current decision toward precedent. Note alignment in packet/plan. |
   | `suggestive` | Surface precedent in the Author-Gate packet or plan body but do not auto-bias. |
   | `none` | State explicitly: "Precedent: ledger had no match (novel case)." |

5. Record the consultation itself as a ledger event (meta-row) so W5.2 coverage audit can verify the skill actually ran.

## Invocation Rules

- Consulting skills are **read-only**. They never mutate the ledger they query.
- They run **before** the action whose precedent they surface — not after.
- They add at most 500 tokens of precedent text to the prompt context. Top-3 matches only.
- If `verdict.fts_available == False`, fall back to LIKE search and note reduced confidence.

## Per-Ledger Skills (24 Total)

| Ledger | Skill | Auto-invoke trigger (indicative) |
|---|---|---|
| `tool_routing` | `ledger-consulter-tool-routing` | Any retrieval-class tool dispatch |
| `refactor_outcome` | `ledger-consulter-refactor-outcome` | Wave planning, refactor-scope Author-Gate |
| `prompt_classifier` | `ledger-consulter-prompt-classifier` | T2/T3 tier prediction |
| `mcp_invocation` | `ledger-consulter-mcp-invocation` | Before mcp* call where latency matters |
| `hotspot_defect` | `ledger-consulter-hotspot-defect` | Hotspot-first refactoring gate |
| `deferred_scope_calibration` | `ledger-consulter-deferred-scope-calibration` | DEFERRED_SCOPE marker emission |
| `guardian_exemption` | `ledger-consulter-guardian-exemption` | Any `# guardian: allow-*` addition |
| `progress_eta` | `ledger-consulter-progress-eta` | ProgressReporter init with new operation |
| `memory_recall` | `ledger-consulter-memory-recall` | Session start (weighting recall list) |
| `test_selection` | `ledger-consulter-test-selection` | `/adg-test-triage-gate` invocation |
| `apps_qna_pack_lifecycle` | `ledger-consulter-apps-qna-pack-lifecycle` | apps_qna pack build / lint / route decisions |
| `eval_harness_outcome` | `ledger-consulter-eval-harness-outcome` | AppSpecificEvaluator run completion |
| `router_l0_agentic` | `ledger-consulter-router-l0-agentic` | AgenticRouter dispatch logic changes |
| `router_l0_bandit` | `ledger-consulter-router-l0-bandit` | NamespaceBandit policy / admissibility changes |
| `router_l0_ensemble` | `ledger-consulter-router-l0-ensemble` | EnsembleRouter weights / MetaLearner changes |
| `router_l0_path` | `ledger-consulter-router-l0-path` | PathRouter abstain threshold / A/B/C/D rules |
| `router_l1_c0` | `ledger-consulter-router-l1-c0` | RetrievalRouter intent / SLO / downgrade changes |
| `router_l2_cascade` | `ledger-consulter-router-l2-cascade` | HealingRouter tier / provider selection |
| `router_l3_reroute` | `ledger-consulter-router-l3-reroute` | RerouteCeiling threshold / max_reroutes |
| `router_l3_sovereign_mcp` | `ledger-consulter-router-l3-sovereign-mcp` | SovereignMcpRouter key_id / dispatch logic |
| `router_l4_uwg` | `ledger-consulter-router-l4-uwg` | DurableWriteGateway commit policy changes |
| `router_l5_hitl` | `ledger-consulter-router-l5-hitl` | HITLApprovalGate verdict handling / escalation |
| `router_l6_promo` | `ledger-consulter-router-l6-promo` | PromotionGate min_n_each_arm / z / Wilson CI |
| `router_l6_regret` | `ledger-consulter-router-l6-regret` | RegretLedger record / top-offender attribution |

## References

- Registry: `tools/ledgers/schema_registry.py`
- Reader API: `tools/ledgers/consulter.py`
- Writer API: `tools/ledgers/writer.py`
- Base DDL: `.windsurf/schemas/ledger_base.schema.sql`
- Decision-ledger precedent: `.windsurf/skills/refactor-decision-memory/SKILL.md`
