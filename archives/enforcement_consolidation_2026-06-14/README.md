# Archive — Enforcement Surface Consolidation (2026-06-14)

Provenance: plan [enforcement-surface-consolidation-d8b3f6](../../plans/enforcement-surface-consolidation-d8b3f6.md), Wave **W2** (S1 Author-Gate machinery retirement).

These artifacts were **retired, not deleted** — the Author-Gate packet/marker/ledger/queue pipeline is
superseded by native `AskUserQuestion` (CLAUDE.md §Author-Gate + constitutional §6; ADR-093,
`claude-native-supersession-9d3f7a`). The invariant ("stop & ask on ambiguity") is preserved; only the
emulation machinery is moved here. Reversible: `git mv` back if ever needed.

## skills/
- `author-gate-packet-builder/` — emitted the retired `AUTHOR_GATE_PACKET:` block.
- `author-gate-ui-renderer/` — rendered the retired packet card.

No live code imports these; the active `ask-user-question-recommendation` skill is the native successor.
Verified non-breaking: the active `check_enriched_choice_ui_invariants.py` gate still exits 0 (it
classifies `author-gate-*` paths by string match and skips missing files).

## ci/
Gates classified **ORPHANED** (referenced by no registry / pre-commit / workflow / test) by
`tools/governance/classify_gate_wiring.py` → `docs/reports/governance/gate_wiring_classification.json`:
- `check_ag_queue_drain_freshness.py`
- `check_ag_queue_seed_markers.py`
- `check_enriched_choice_ui_invariants_ast.py`  (the active `check_enriched_choice_ui_invariants.py` remains)

## Deliberately KEPT (NOT archived) — discovered coupling, awaiting W2-followup decision
- `.claude/governance/scripts/author_gate_ledger_integrity.py` — still imported by the **active, kept**
  `refactor-decision-memory` skill (`lookup_refactor_decisions.py`: `from author_gate_ledger_integrity
  import GENESIS_PREV_HASH, …`). Must decouple `refactor-decision-memory` → native file memory before
  archiving this helper.
- The remaining ~15 AG governance scripts, the 2 TEST_ONLY gates
  (`check_author_gate_pipeline_freshness.py`, `check_author_gate_v2_completeness.py` — archive with
  their tests), the orphaned decision-ledger gates (ledger-adjacent to the kept skill), and
  `.github/workflows/author-gate-gates.yml` — all await the W2-followup decision so they move in
  lockstep with their consumers.
