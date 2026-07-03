---
name: agentic-workflow-governance
description: Use when working in C:/Git/Agentic-Workflow-FRESH as Codex. Treat repo-owned Codex files under .codex as the only Agentic-Workflow enforcement home.
---

# Agentic-Workflow Governance Adapter

This repo-owned skill is a bootstrap pointer for Codex sessions in
`C:\Git\Agentic-Workflow-FRESH`. It must stay versioned in this repository, not
under a user-profile Codex home.

## Canonical Sources

For this repo, follow:

- `AGENTS.md`
- `docs/codex-primary-execution.md`
- `.codex/rules/plan-first-enforcement.md`
- `.codex/skills/structured-reasoning/SKILL.md`
- `.codex/skills/mcp-integration/SKILL.md`
- `.codex/hooks.json`
- `scripts/governance/verify_codex_primary.py`
- `scripts/governance/verify_codex_enforcement_home.py`

## Enforcement Home

Agentic-Workflow Codex enforcement artifacts belong under:

- `.codex/automations/`
- `.codex/skills/`
- `.codex/hooks/`
- `.codex/rules/`
- `.codex/governance/`
- `scripts/governance/`

Repo-specific automation or skill files under `C:\Users\amita\.codex` are
invalid for this repository. Run:

```bash
python scripts/governance/verify_codex_enforcement_home.py --json
```

## Triage

- T0/T1: answer or edit directly when the scope is one small file or a direct question.
- T2/T3: present a plan before edits and use `structured-reasoning` for decomposition.

Before long Codex-primary runs, use:

```bash
python scripts/governance/codex_readiness.py --json
```

For publication closeout, use:

```bash
python scripts/governance/codex_readiness.py --git-publication --require-publication-closeout --json
python scripts/governance/codex_main_closeout.py --check --fetch --json --publication-only
```

For strict workspace topology hygiene, use:

```bash
python scripts/governance/verify_single_main_worktree.py --root C:\Git\Agentic-Workflow-FRESH --expected-path C:\Git\Agentic-Workflow-FRESH --fetch --json
```
