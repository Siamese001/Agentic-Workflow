# Architecture Decision Records

**Status:** Active index
**Last reconciled:** 2026-06-15

This directory is the filesystem source of truth for formal architecture
decision records. The retired Notion ADR Registry is not a write target.
Historical `.windsurf/` and `.cursor/` links inside older ADRs are evidence
pointers only unless a current `.codex/` rule, gate, test, runtime/config
surface, or root plan still references them.

ADRs are rationale and provenance records, not executable policy. Active
enforcement lives in gates, tests, hooks, `.codex` rules/skills, configs, and
runtime code. Treat an ADR as current only when it has a live binding to one of
those surfaces; otherwise treat it as historical context pending review.

## Current Rules

- New ADRs use `ADR-template.md`.
- New plans referenced by ADRs live under `plans/<slug>-<6hex>.md`.
- Current governance rules and skills live under `.codex/rules/` and `.codex/skills/`.
- Do not add Notion ADR Registry write steps. The registry was archived; ADR files are canonical.
- Do not reuse an ADR number until the duplicate-number cleanup below is resolved.
- Use `python ops_scripts/ci/inventory_adr_liveness.py --json` to classify
  ADRs as live-bound, historical, noncanonical, or unbound-review.
- Use `python ops_scripts/ci/check_adr_hygiene.py --advisory` to report new ADR
  namespace drift without blocking on known cleanup debt.

## Reconciliation Summary

The 2026-06-15 pass found 122 active ADR-like files, excluding this README and the reusable ADR template:

| Location | Count | Notes |
|---|---:|---|
| `docs/architecture/adr/` | 109 | Canonical ADR directory |
| `docs/adr/` | 9 | Active ADR-like records outside the canonical directory |
| `docs/architecture/*_adr.md` | 4 | Standalone architecture ADRs |

## Duplicate Number Groups

These groups need a deliberate renumber, supersession, or archive pass. They were not renamed in the 2026-06-15 cleanup because renumbering requires cross-reference migration.

| Number | Files |
|---|---|
| ADR-023 | `ADR-023-review-request.md`; `ADR-023-runtime-hitl-exit-control.md` |
| ADR-038 | `ADR-038-budget-envelope.md`; `ADR-038-eval-trial-isolation.md` |
| ADR-042 | `adr-0042-skills-consolidation.md`; `ADR-042-exit-kill-switch.md` |
| ADR-043 | `adr-0043-structural-agentic-checks.md`; `ADR-043-l1-plan-contract-v2.md` |
| ADR-051 | `ADR-051-l5-v5-governance-plane.md`; `ADR-051-sc1-structural-block-remediation.md` |
| ADR-061 | `ADR-061-apps-rg-route-family-r3-to-r4-correction.md`; `ADR-061-retrieval-golden-set-ragas-eval.md` |
| ADR-079 | `ADR-079-adg-pipeline-three-bucket-opt-in.md`; `ADR-079-l2-agent-graph-layer-contract.md` |
| ADR-081 | `docs/adr/ADR-081-apps-e2e-spine-cert-wireup.md`; `ADR-081-adg-ci-unified-enforcement-planes.md`; `ADR-081-canonical-hop-pipeline-substrate.md` |
| ADR-082 | `docs/adr/ADR-082-multi-provider-judge-panel-harness.md`; `ADR-082-apps-folder-taxonomy.md` |
| ADR-085 | `docs/adr/ADR-085-same-authority-incremental-regen.md`; `ADR-085-l6-observability-dependency-hygiene.md` |
| ADR-086 | `docs/adr/ADR-086-judge-directed-regen-apps-orchestrator.md`; `ADR-086-l6-eval-surface-consolidation.md` |
| ADR-088 | `ADR-088-l6-category-a-shared-permanent-exception.md`; `ADR-088-product-spine-function-truth.md` |
| ADR-093 | `ADR-093-author-gate-native-ask-user-question.md`; `ADR-093-fortknox-wave1-zero-yield-honest-audit.md` |
| ADR-094 | `ADR-094-mcp-serialization-sentinel-retirement.md`; `ADR-094-sr-markers-native-plan-mode.md` |
| ADR-095 | `ADR-095-l6-observability-dependency-hygiene.md`; `ADR-095-mcp-shadow-disable-filesystem-task-manager.md`; `ADR-095-memory-native-file-memory.md` |
| ADR-096 | `ADR-096-deferred-scope-native-spawn-task.md`; `ADR-096-l6-universally-importable.md` |
| ADR-097 | `ADR-097-canonical-adapters-redis-chromadb-sqlite3.md`; `ADR-097-mcp-serialization-and-cleanup.md` |
| ADR-100 | `ADR-100-enforcement-surface-consolidation.md`; `ADR-100-l5-cert-ref-emit-chain-threading.md`; `ADR-100-spine-envelope-pattern.md` |

## Explicit Open Or Successor Scope

No active ADR-like file is missing a status line after the 2026-06-15 reconciliation. Vague stale `Proposed` statuses were either promoted with local implementation evidence or replaced with explicit open-scope labels.

The records below are the remaining items that still need a dedicated follow-up plan, owner approval, or supersession pass.

| File | Current status |
|---|---|
| `docs/adr/semantic_cache_threshold_recalibration.md` | PROPOSED_NOT_APPLIED; pending approval is intentional safety enforcement |

## ADR-Like Non-Canonical Artifact

`docs/adr/gate-promotion/AG-PURITY-advisory-to-strict.md` is an ADR-like gate-promotion note, but it is not currently numbered as an ADR. It now has a standard status line for inventory purposes; leave it outside numeric ADR cleanup unless a future governance pass promotes it to a formal ADR.
