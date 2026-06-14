# Archive — Enforcement Surface Consolidation (2026-06-14)

Provenance: plan [enforcement-surface-consolidation-d8b3f6](../../plans/enforcement-surface-consolidation-d8b3f6.md), Wave **W2** (S1 Author-Gate machinery retirement).

Retired (not deleted) machinery from the superseded Author-Gate pipeline — superseded by native
`AskUserQuestion` (CLAUDE.md §Author-Gate + constitutional §6; ADR-093, `claude-native-supersession-9d3f7a`).
Invariant preserved; reversible via `git mv`.

## ci/ — 3 classifier-proven-orphan gates
Classified **ORPHANED** (referenced by no registry / pre-commit / workflow / test) by
`tools/governance/classify_gate_wiring.py` → `docs/reports/governance/gate_wiring_classification.json`:
- `check_ag_queue_drain_freshness.py`
- `check_ag_queue_seed_markers.py`
- `check_enriched_choice_ui_invariants_ast.py`  (the active `check_enriched_choice_ui_invariants.py` remains)

Verified non-breaking: `run_contract_gates.py` parses; the 3 are referenced nowhere; CI green after removal.

## NOT archived — discovered live coupling (deferred to a single lockstep S1 pass)
The 2 AG **skills** (`author-gate-packet-builder`, `author-gate-ui-renderer`) were briefly archived
here, then **REVERTED** — CI on PR #336 + the Codex review (P1) correctly flagged that they are
imported by **live** consumers:
- `tools/author_gate/render_template.py` (loads `packet_template.md`),
- `tools/governance_legacy/author_gate_prepare_ask.py` (loads `emit_packet.py` / `render_card.py`),
- `ops_scripts/ci/author_gate/check_ask_user_question_packet_freshness.py` (gate),
- `tests/unit/tools/meta_learning/test_author_gate_meta_learning_e2e.py`, `tests/unit/author_gate_hardening/test_author_gate_hardening.py`.

Also KEPT: `.claude/governance/scripts/author_gate_ledger_integrity.py` (imported by the active,
kept `refactor-decision-memory` skill). **The full S1 bundle** — the 2 skills + `tools/author_gate/*`
+ `tools/governance_legacy/author_gate_prepare_ask` + the `author_gate/` gates + their 2 tests +
`author_gate_ledger_integrity` + the `refactor-decision-memory` decouple — must retire together in
**one lockstep pass**.

**Lesson (CI + Codex caught it):** the AG machinery has more live consumers than the W0 coupling map
enumerated. Verify importers (`grep -rl`) before any archival — surfacing a name in a reference scan
is not enough; confirm it is not a live import.
