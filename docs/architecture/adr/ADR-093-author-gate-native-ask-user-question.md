# ADR-093 — Author-Gate superseded by native AskUserQuestion

- **Status:** Accepted
- **Date:** 2026-06-07
- **Plan:** [claude-native-supersession-9d3f7a](../../../plans/claude-native-supersession-9d3f7a.md) (Wave W1)
- **Supersedes:** the bespoke Author-Gate harness-HITL pipeline

## Context

The Author-Gate developer-loop HITL was built when the agent harness (legacy editor/legacy IDE era) had **no
native structured-choice tool**. To make the model "stop and ask before an ambiguous edit," the repo
hand-built a pipeline: a packet-builder skill → ui-renderer skill → `AUTHOR_GATE_PACKET:` marker →
`DECISION_CAPTURED:` marker → SQLite decision ledger → Notion mirror → an append-only queue with
seed/drain markers, all policed by **9 CI assurance gates**, **4 pre-commit hooks**, **~16 governance
scripts**, **6 rule files**, and constitutional **§6/§30/§35**.

Claude Code ships a native **`AskUserQuestion`** tool that renders clickable, described options with a
recommended choice — exactly what the pipeline emulated.

## Decision

Retire the emulation; keep the invariant.

- **Invariant kept** (AGENTS.md § Author-Gate + constitutional §6): stop and ask via `AskUserQuestion`
  when ≥2 plausible approaches have different blast radius and no unambiguous directive; mark the
  recommended option; don't fire for typos / single-path fixes / explicit instructions.
- **Retired:** the packet/render/marker/queue/ledger pipeline.
  - `run_contract_gates.py`: 9 Author-Gate CI gates removed.
  - `.pre-commit-config.yaml`: T6d, T6d2, T7e, T7t removed.
  - `after_agent_governance_dispatch.py`: 8 AG audit scripts dropped from the Stop chain (non-AG
    audits retained).
  - `.codex/hooks.json`: `pre_user_prompt_author_gate_reminder` hook removed.
  - Constitutional **§30** (capture health) and **§35** (queue drain) marked RETIRED; slots kept for
    stable numbering (§-citations are load-bearing across rules).
  - 6 rule files reduced to deprecation stubs pointing at the native flow.
  - Skills `author-gate-packet-builder` and `author-gate-ui-renderer` moved to
    `archives/claude_native_supersession_2026-06-07/skills/`.
- **Deferred to W5 cleanup:** physically archiving the now-dormant governance scripts
  (`pre_author_gate.py`, `_author_gate_queue.py`, `post_*_author_gate_*.py`, etc.) and the dormant
  `ops_scripts/ci/author_gate/` gate scripts, after a zero-import verification. They are uncalled as
  of this wave (no invocation path remains).

## Consequences

- **Positive:** ~12 fewer gates to keep green; 8 fewer subprocesses per Stop; no marker grammar to
  emit or audit; decisions surface through a real clickable UI instead of prose-rendered markdown.
- **Precedent:** historical refactor-decision precedent now lives in file memory (the
  `refactor-decision-memory` skill is dormant, swept in W5) rather than a bespoke SQLite ledger.
- **Reversibility:** all removed scripts/skills are archived or dormant-on-disk; gate entries are
  re-addable from git history. No data destroyed.

## Verification

`run_contract_gates.py`, the dispatch hook, and `hooks.json` parse cleanly; `.pre-commit-config.yaml`
is valid YAML; constitutional §6 reads native and §30/§35 read RETIRED.
