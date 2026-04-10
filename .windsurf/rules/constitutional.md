---
trigger: always_on
---
# Constitutional Floor

> ⛔ These constraints apply to every task, every tier, every session. No exceptions.

## Hard Constraints

0. **No PowerShell.** Use `subprocess.run(argv, shell=False, timeout=30)`.
1. **No test skipping.** No `pytest.mark.skip`, no `xfail` without `strict=True`.
2. **No editing while exploring.** All five repair gates must pass before any edit.
3. **No agent deletion without authorization.** Requires AGENT-DELETION-AUTHORIZED marker, 90-day deprecation, zero references.
4. **CI enforces all of this.** `python ops_scripts/ci/run_contract_gates.py`
5. **ADG before T2/T3 work.** Ingest `artifacts/adg/adg_indexed_<timestamp>.sqlite` before any query or edit. Regenerate: `python tools/generate_full_adg.py`.
6. **HITL for ambiguous decisions.** Score candidates 0.00–1.00, filter at 0.72, apply dominance rule (≥0.85, gap ≥0.12 → surface alone). See `hitl-enforcement.md`.
7. **RCA auto-closure.** Execute corrective actions immediately. Never leave RCA unresolved.
8. **Guardian exemptions require HITL.** Format: `# guardian: allow-<type> -- <specific justification>`. Generic words forbidden. Gate: `guardian_exemption_gate.py`.
9. **SVP Engineering persona for T3 architecture.** Prioritize: operational simplicity, dependency hygiene, archival over deletion, ADRs, zero-regression.
10. **Zero-loss refactor.** After removing boilerplate, check for hollow files. Gate: `zero_loss_refactor_verifier.py`.
11. **Terminal process lifecycle.** All `run_command`/subprocess calls must terminate when query completes. Gate: `check_terminal_cleanup.py`.
12. **No imports from `archives/` in production.** CI gate: `check_no_archives_imports.py`.
13. **MCP green light before T2/T3.** Check Redis hot cache first (`adg_redis_ingest.py --check`). Fallback: `mcp1_adg_health`. Both red = BLOCKED.
14. **Subprocess timeout required.** `subprocess.run(argv, shell=False, timeout=30)`. No exceptions.
15. **Precise exception handling.** Catch specific types. Bare `except:` FORBIDDEN. `except Exception` without guardian comment FORBIDDEN.

## Tier Classification

| Tier | Scope | ADG Requirement |
|------|-------|----------------|
| **T0 — Question** | No code changes | ADG cache optional |
| **T1 — Trivial** | ≤1 file, ≤20 lines | Scoped tests only |
| **T2 — Scoped** | 2–5 files, single layer | Query ADG blast radius |
| **T3 — Architectural** | >5 files or cross-layer | Full ADG protocol mandatory |

ADG graph is the **primary** analysis primitive. `grep_search` for dependency analysis is FORBIDDEN.

## Quick Gates

- Plan SSOT: `.windsurf/plans/<name>-<6hex>.md` — never `docs/reports/plans/` for plans
- All Python file I/O: `encoding="utf-8"`
- `grep_search` permitted only to confirm literals, never for dependency tracing

## Extended Doctrine (model_decision rules)

Full protocol details live in focused rules — loaded on demand, not always_on:
- `adg-repair-discipline.md` — ADG repair loop and fail-closed recovery
- `anti-pattern-hitl-gate.md` — anti-pattern HITL approval gate
- `hitl-enforcement.md` — full HITL decision pipeline and option shapes
- `sequential-thinking-enforcement.md` — T2/T3 structured reasoning protocol
- `global_rules.md` — subprocess, exception, MCP SSOT policy details
- `adg-test-accelerator-enforcement.md` — ADG-driven test scope selection
