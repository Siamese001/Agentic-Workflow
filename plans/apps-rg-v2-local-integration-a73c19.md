# Apps RG V2 Local Integration

## Objective

Create `C:\Git\apps_rg_v2` as the local independent repository that consolidates
the apps-rg standalone workstream while retaining source provenance.

## Approved deviation

The prior standalone and source-refreeze plans prohibit target creation at
`C:\Git\apps_rg`. The user approved a new local target at
`C:\Git\apps_rg_v2` and approved an independent-repository transplant rather
than a monorepo history merge.

## Scope

Wave 1 imports the source-refreeze branch's app-owned sources and relevant
supporting assets into the target, plus the standalone worktree's Wave 1
closure tooling. `agentic_core/**` remains in the source repository and is not
copied. The target records the exact source branch, commit, and local-dirty
state used for this import.

## Wave 1 Validation

1. The target is a Git repository on `main` with one import commit.
2. The import contains the declared app-owned paths and standalone tooling.
3. The import contains no `agentic_core/**` path.
4. A provenance record identifies the source branch, SHA, and dirty files.

## Deferred

Making the imported repository independently installable, reconciling
unresolved source imports, and parity certification remain later waves. The
source-refreeze branch remains unmerged into the Agentic Workflow main branch.
