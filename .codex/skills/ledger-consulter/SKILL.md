---
name: ledger-consulter
description: Base template for consulting a single intelligence ledger before acting. This skill itself is not auto-invoked; per-ledger consulting skills inherit this contract. STATUS — template only: of the per-ledger skills below, exactly ONE is built (`ledger-consulter-ask-user-question`); the rest are PLANNED, not on disk. See `.codex/plans/intelligence-ledgers-ten-a7c3e2.md` for the rollout.
trigger: manual
---

# Ledger-Consulter Template

> ⚠️ **STATUS — TEMPLATE + 1 REFERENCE IMPLEMENTATION (reconciled 2026-06-14).**
> This file is the inheritance contract for per-ledger consulting skills. The "Per-Ledger
> Skills" table below is the **planned roster** — it is NOT a list of files that exist.
>
> | Reality on disk | Count |
> |---|---|
> | Built reference implementations | **1** — [`ledger-consulter-ask-user-question`](../ledger-consulter-ask-user-question/SKILL.md) (note: keyed on the `ask_user_question` ledger, which is NOT in the roster table below) |
> | Planned / not yet authored | the roster rows below |
>
> Prior versions of this file and `closed-loop-router-enforcement.md` cited three different
> counts (10 / 12 / 24) for the same roster. The roster table below is the single source of
> truth for *intended* coverage; do not infer that any row is a callable skill until a folder
> `.codex/skills/<row-skill-name>/` actually exists. Per repo doctrine (`apps-rg-execution-bias`
> "subtraction before addition"), build a per-ledger skill **only when a concrete task needs it**,
> using the contract below — do not bulk-generate the roster.

## Purpose

Surface precedent from a given intelligence ledger (`artifacts/ledgers/<name>.sqlite`) so the current decision is biased by prior outcomes. Analogous to `refactor-decision-memory` but parameterized over any of the nine ledgers.

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

## Planned Per-Ledger Skills (roster — author on demand, not pre-built)

> These 24 rows are the **intended** roster. None exist on disk yet (the one built skill,
> `ledger-consulter-ask-user-question`, covers a ledger not listed here). Treat this as a
> backlog of skills to stamp from the contract above when a task actually needs the precedent.

| Ledger | Skill (PLANNED) | Auto-invoke trigger (indicative) |
|---|---|---|
| `tool_routing` | `ledger-consulter-tool-routing` | Any retrieval-class tool dispatch |
| `refactor_outcome` | `ledger-consulter-refactor-outcome` | Wave planning, refactor-scope Author-Gate |
| `prompt_classifier` | `ledger-consulter-prompt-classifier` | T2/T3 tier prediction |
| `mcp_invocation` | `ledger-consulter-mcp-invocation` | Before mcp* call where latency matters |
| `hotspot_defect` | `ledger-consulter-hotspot-defect` | Hotspot-first refactoring gate |
| `deferred_scope_calibration` | `ledger-consulter-deferred-scope-calibration` | DEFERRED_SCOPE marker emission |
| `guardian_exemption` | `ledger-consulter-guardian-exemption` | Any `# guardian: allow-*` addition |
| `progress_eta` | `ledger-consulter-progress-eta` | ProgressReporter init with new operation |
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
- Base DDL: `.codex/schemas/ledger_base.schema.sql`
- Decision-ledger precedent: `.codex/skills/refactor-decision-memory/SKILL.md`
