---
name: agentic-workflow-verification
description: Use when verifying Codex primary-execution changes in C:/Git/Agentic-Workflow-FRESH. Runs repo-owned verification gates only.
---

# Agentic-Workflow Verification Adapter

This repo-owned skill keeps Agentic-Workflow verification in `C:\Git`, not under
a user-profile Codex home.

## Required Checks

For Codex governance, automation, hooks, skills, or publication hardening, run:

```bash
python scripts/governance/verify_codex_enforcement_home.py --json
python scripts/governance/verify_codex_primary.py
```

For publication closeout, also run:

```bash
python scripts/governance/codex_readiness.py --git-publication --require-single-main-worktree --json
python scripts/governance/verify_single_main_worktree.py --root C:\Git\Agentic-Workflow-FRESH --expected-path C:\Git\Agentic-Workflow-FRESH --fetch --json
```

For substantial runs, validate the JSON receipt:

```bash
python scripts/governance/verify_codex_run_receipt.py <receipt.json>
```

Pytest plugin autoload stays enabled for this repo. Do not set
`PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` for ad-hoc runs.
