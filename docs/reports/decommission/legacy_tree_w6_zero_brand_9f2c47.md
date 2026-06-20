# Legacy Tree W6 Zero-Brand Verification

Date: 2026-06-08
Plan: `legacy-windsurf-tree-decommission-9f2c47`
Branch: `codex/ide-archive-decommission-plans`

## Result

W6 verified that the deleted legacy trees are absent, repointed active stale hook-name references to
the current `post_agent_*` surface, and reduced active deleted-tree residuals to intentional
compatibility or historical references.

## Physical Tree Checks

Commands:

```text
git ls-files .cursor .windsurf .codex/governance/scripts/_legacy_windsurf .codex/governance/scripts/_legacy_cursor
python -c "from pathlib import Path; ..."
```

Result:

```text
git ls-files: no tracked entries
cursor_exists=False
windsurf_exists=False
legacy_windsurf_exists=False
legacy_cursor_exists=False
```

Deletion/readiness gates:

```text
python ops_scripts/ci/check_no_cursor_refs.py
python ops_scripts/ci/check_windsurf_deletion_readiness.py
```

Result:

```text
[no-cursor-refs] OK - .cursor/ decommissioned; no active path use
check_windsurf_deletion_readiness.py: deletion_safe=true, blockers=[]
```

## Active Surface Cleanup

Updated active governance documentation/config and debug helpers from stale legacy names to current
names:

- `post_cursor_agent_*` references in active `.codex/templates`, `.codex/skills`, and
  `.codex/rules` now point to `post_agent_*`.
- `post_cascade` trigger prose in active config/tools now uses post-agent wording.
- Active debug helpers no longer import or glob the deleted `_legacy_windsurf` tree.
- `check_hook_consolidation.py` now exposes `--max-post-agent` and retains
  `--max-post-cursor-agent` only as a compatibility alias.

## Residual Allowlist

Targeted active scan:

```text
rg -n "post_cursor_agent|post-cursor-agent|Post-Cursor-Agent|post_cascade|_legacy_windsurf|_legacy_cursor" \
  .codex/templates .codex/skills .codex/rules .codex/governance/scripts \
  config/notion_databases.yaml AGENTS.md tools/priority/validate_deferred_scope_marker.py \
  tools/plan_lifecycle/plan_lifecycle_manager.py tools/debug ops_scripts/ci
```

Only one active hit remains:

- `ops_scripts/ci/check_hook_consolidation.py`: `--max-post-cursor-agent` retained as a
  backwards-compatible CLI alias for `--max-post-agent`.

Broader non-archive scan still finds:

- historical docs and ADRs that describe the old hook/tree state,
- maintenance migration tools that are explicitly denylisted/allowlisted as historical migration
  helpers,
- compatibility tests whose purpose is to guard legacy input handling.

## Handoff

No tracked `.cursor/` directory remains in this worktree, and no physical `.cursor/` directory is
present on disk. The parent `cursor-windsurf-codeium-decommission-dec0de` plan can treat `.cursor/`
physical removal as already satisfied for this branch; this W6 did not duplicate any additional
`.cursor` deletion work.

## Broad Gate Note

`python ops_scripts/ci/run_contract_gates.py` was attempted during W6 closeout and failed on an
unrelated infrastructure import:

```text
apps_lic/engines/x1d_claude_judge_adapter.py:277: import anthropic
```

That file is not touched by W6 and is not different between this branch and `origin/main`; blame points
to `df521109c0` from earlier on 2026-06-08. W6 treated this as a pre-existing broad-gate blocker,
not as legacy-tree scope.
