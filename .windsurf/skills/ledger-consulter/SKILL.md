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

## Per-Ledger Skills

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

## References

- Registry: `tools/ledgers/schema_registry.py`
- Reader API: `tools/ledgers/consulter.py`
- Writer API: `tools/ledgers/writer.py`
- Base DDL: `.windsurf/schemas/ledger_base.schema.sql`
- Decision-ledger precedent: `.windsurf/skills/refactor-decision-memory/SKILL.md`
