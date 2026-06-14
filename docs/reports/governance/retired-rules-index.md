# Retired Rules Index — Zero-Loss Redirect Map

> Created by plan [enforcement-surface-consolidation-d8b3f6](../../../plans/enforcement-surface-consolidation-d8b3f6.md), Wave **W3.1**.
> Single canonical record of where each retired `.claude/rules/*.md` redirect stub's signal now lives.
> Preserves the redirect map (constitutional §21 zero-loss) so the stub files can be deleted in **W3.2**
> without losing any pointer.
>
> **Location note:** kept under `docs/reports/governance/` (governance evidence), **not** `.claude/rules/`,
> because the rules-validation gates (`check_rule_frontmatter_schema.py`, `check_rules_filesystem_integrity.py`,
> `check_rule_cross_references.py`) `glob("*.md")` over the rules dir and would reject a non-rule index file.
>
> Rationale: each listed file was already a pure-redirect/inactive stub (its real content had already moved
> to the canonical target). They were nonetheless loaded as project instructions every session. Deleting
> them reduces always-on context for **zero** signal loss — the canonical target is authoritative, and
> constitutional §-citations are number-based (not filename-based), so they survive.

## Redirect map (stub → canonical home)

| Retired stub (`.claude/rules/`) | Canonical home for its signal | Superseded by |
|---|---|---|
| `003-author-gate-hitl.md` | `CLAUDE.md` §Author-Gate + `constitutional.md` §6 | native `AskUserQuestion` (ADR-093, W1) |
| `author-gate-enforcement.md` | `CLAUDE.md` §Author-Gate + `constitutional.md` §6 | native `AskUserQuestion` (ADR-093, W1) |
| `author-gate-decision-points.md` | `CLAUDE.md` §Author-Gate + `constitutional.md` §6 | native `AskUserQuestion` (ADR-093, W1) |
| `author-gate-queue-drain.md` | `CLAUDE.md` §Author-Gate + `constitutional.md` §6 / §35 (retired slot) | native `AskUserQuestion` (ADR-093, W1) |
| `author-gate-svp-calibration.md` | `CLAUDE.md` §Author-Gate + `constitutional.md` §6 | native `AskUserQuestion` (ADR-093, W1) |
| `anti-pattern-author-gate.md` | `approval-exception-policy.md` + `CLAUDE.md` §Author-Gate | native `AskUserQuestion` (ADR-093, W1) |
| `next-step-capture.md` | `constitutional.md` §24 | native `spawn_task` (ADR-096, W4) |
| `deferred-scope-capture.md` | `constitutional.md` §24 + `scope-containment.md` | native `spawn_task` (ADR-096, W4) |
| `mcp-serialization.md` | `pre_mcp_gate.py` (Notion-token + GitKraken checks retained) | native parallel MCP (ADR-097, W5) |
| `adg-graph-layer-enforcement.md` | `adg-analysis-procedures.md` §1/§3 + `adg-canonical-invariants.md` | W3.P2 ADG consolidation |
| `adg-hotspot-enforcement.md` | `adg-analysis-procedures.md` §2 + `adg-canonical-invariants.md` §4 | W3.P2 ADG consolidation |
| `adg-repair-discipline.md` | `adg-analysis-procedures.md` §5 | W3.P2 ADG consolidation |
| `adg-test-accelerator-enforcement.md` | `adg-analysis-procedures.md` §6 — **glob trigger** (`**/test_*_adg.py`, `tools/adg/**`) re-homed to that file's frontmatter | W3.P2 ADG consolidation |
| `adg-p7-analyst-artifacts.md` | `adg-analysis-procedures.md` §4 | W3.P2 ADG consolidation |
| `wave-completion-discipline.md` | `plan-governance` skill §3 (via `plan-lifecycle-procedures.md`) | W3.P3 plan/wave consolidation |
| `notion-backlog-plan-linkage.md` | `plan-governance` skill §5 | W3.P3 plan/wave consolidation |
| `notion-plan-identity-verification.md` | `plan-governance` skill §4 | W3.P3 plan/wave consolidation |
| `plan-registration-enforcement.md` | `plan-governance` skill §1 + `plan-location.md` + `constitutional.md` §36 | W2 governance dedupe |
| `plan-lifecycle-procedures.md` | `plan-governance` skill (Tier-2 procedural SSOT) | (redirect file) |
| `global_rules.md` | `000-agentic-core-operating-contract.md` · `001-runtime-seam-execution.md` · `002-pass-blocked-proof-contract.md` | (intentionally inactive pointer) |

## W3.2 inbound-reference surgery (must accompany deletion — keeps CI green)

Repoint these **live** inbound filename references (mapped by W3.1 `detect_stubs.py`) to the canonical
home above (or to this index) before/with deleting the stubs:

| Active file citing a stub | Stubs it references |
|---|---|
| `CLAUDE.md` (Specialized-rules index + "Deprecated rules" note) | nearly all of the above |
| `constitutional.md` (Extended Doctrine repoint line) | `adg-repair-discipline`, `adg-hotspot-enforcement`, `adg-graph-layer-enforcement`, `adg-test-accelerator-enforcement`, `anti-pattern-author-gate`, `author-gate-enforcement`, `deferred-scope-capture`, `plan-registration-enforcement` |
| `approval-exception-policy.md` | `author-gate-enforcement`, `author-gate-svp-calibration`, `anti-pattern-author-gate` |
| `refactor-decision-memory.md` | `author-gate-enforcement`, `author-gate-decision-points` |
| `scope-containment.md` | `next-step-capture`, `deferred-scope-capture` |
| `memory-management.md` | `adg-repair-discipline` |
| `memory-notion-writeback.md` | `deferred-scope-capture` |
| `intelligence-ledger-family.md` | `author-gate-enforcement` |
| `fortknox-certification-discipline.md` | `author-gate-decision-points` |
| `pre_prompt_classifier.py` | `adg-graph-layer-enforcement`, `adg-hotspot-enforcement` (this script is itself slated for S2/W6 retirement) |

> `.py` references from the orphaned AG audit scripts (`post_agent_author_gate_*`, `post_agent_deferred_scope_capture`, `post_agent_next_step_capture`) need no fix — those scripts retire with their subsystem.
