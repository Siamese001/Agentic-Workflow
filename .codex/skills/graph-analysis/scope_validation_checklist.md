# Scope Validation Checklist

Run before any file edits in T2/T3 operations.

## Checklist

1. **Build graph** — ADG MCP query completed successfully
2. **Declare scope** — `## SCOPE_DECLARATION` written to evidence with exact files list
3. **Justify each file** — every file has a documented graph edge path showing why it is in blast radius
4. **Record baseline** — `git diff --name-only HEAD` confirms clean working directory
5. **No scope creep** — file list matches only what the dependency graph justifies

## After Each Edit Batch

- Run `git diff --name-only HEAD`
- Verify output matches declared scope exactly
- If unexpected files appear → invoke decontamination protocol (revert unexpected changes)

## Decontamination Protocol

If scope is violated (files outside declared set were changed):

1. STOP all further edits
2. `git diff --name-only HEAD` — identify contaminating files
3. `git checkout -- <contaminating_file>` for each unexpected file
4. Verify restoration: `git diff --name-only HEAD` matches declared scope
5. Document decontamination in evidence under `## SCOPE_DECONTAMINATION`
6. Update scope declaration if legitimate expansion is needed
