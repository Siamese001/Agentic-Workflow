# apps_repo_brief Deprecation and Deletion

**Plan ID:** `apps-repo-brief-deprecation-deletion-b7c4e1`
**Status:** Completed
**Created:** 2026-06-13
**Owner:** Codex
**Plan File:** `.claude/plans/apps-repo-brief-deprecation-deletion-b7c4e1.md`

---

## Context (SCQA)

**Situation:** `apps_repo_brief` remains listed as an active app in core registries, app inventory, L7 evidence tooling, README, governance scripts, and tests.

**Complication:** The package is partially broken (`apps_repo_brief.reasoning` imports a missing `ExecOrchestrator`), but active tests and registries still assert that it exists. Deleting only the directory would leave stale active contracts.

**Question:** How do we deprecate and delete `apps_repo_brief` without leaving active registry, test, or certification references behind?

**Answer:** First retire active registrations and tests that expect the app, then hard-delete the package, then verify that remaining references are limited to historical plans, archived docs, or generated reports.

---

## Status Tables

### Wave Progress

| Wave | Focus | Status | Verification |
|---|---|---|---|
| 1 | Plan registration and scope record | COMPLETED | Plan file exists; Notion plan row created |
| 2 | Active registry and tooling deprecation | COMPLETED | Active registries, docs, scanners, and L7 evidence tooling updated |
| 3 | Test contract retirement | COMPLETED | Package-specific unit and contract tests removed or updated |
| 4 | Package hard delete | COMPLETED | `apps_repo_brief/` absent; import spec resolves to `None` |
| 5 | Final verification and report | COMPLETED | Targeted pytest, scanners, compile, and residual search completed |

---

## Evidence

ADG MCP was not exposed in this Codex session.

`DEGRADED_FALLBACK: reason=adg_sqlite MCP unavailable in Codex; backend=sqlite; snapshot=artifacts/adg/adg_indexed_06132026_0847.sqlite`

Read-only findings:

- ADG fallback found `apps_repo_brief` package nodes but no external import consumers via `edges.source_file`.
- Literal active references exist in README, core path constants, structure blueprint SSOT, agent taxonomy, L7 evidence tooling, test-surface checks, cross-app allowlists, and tests.
- `import apps_repo_brief` works.
- `import apps_repo_brief.reasoning` fails because `apps_repo_brief.reasoning.ExecOrchestrator` is missing.
- No current runtime/output artifact directories were found for `apps_repo_brief`.

Completion evidence:

- Deleted `apps_repo_brief/`, `tests/apps_repo_brief/`, `tests/unit/apps_repo_brief/`, and the app-specific contract tests under `tests/_apps_contract/`.
- Removed active `apps_repo_brief` registrations from app inventory, path constants, structure blueprint SSOT, agent taxonomy, README, cross-app allowlist, L7 evidence tooling, leakage scanners, test-surface checks, and related tests.
- Residual active-reference search returned no matches outside historical plans, archived docs, reports, artifacts, and this plan.
- `importlib.util.find_spec("apps_repo_brief")` returned `None`.
- Compile check passed for changed Python surfaces.
- Focused pytest passed: `57 passed, 3 warnings in 0.28s`.
- App test-surface parity passed: `TSP1 test surface parity: OK — all 9 apps have canonical surfaces`.
- Core leakage scan completed in advisory mode with existing unrelated violations and no `apps_repo_brief` literal.

---

## Scope

In scope:

- Remove `apps_repo_brief` from active app registries and active documentation.
- Retire app-specific tests that assert the package exists or works.
- Remove package code and app-specific test scaffolds.
- Keep historical plans, archived docs, and generated historical reports unless an active gate reads them.

Out of scope:

- Rebuilding `apps_repo_brief`.
- Reintroducing `apps_exec`.
- Editing historical memorial plan imports.
- Broad cleanup of unrelated dirty worktree changes.

---

## Waves

### Wave 1: Registration

1. Create this plan file under `.claude/plans/`.
2. Register the plan in Notion Plans if the connector schema permits it in Codex.
3. Continue only within the approved deletion scope.

### Wave 2: Active Registry and Tooling Deprecation

1. Remove `apps_repo_brief` from active app lists in core and governance scripts.
2. Remove `apps_repo_brief` from app inventory and public README.
3. Remove `apps_repo_brief` from L7 app evidence collection lists.
4. Remove now-obsolete cross-app allowlist entries.
5. Remove or neutralize tools that import `apps_repo_brief` directly.

### Wave 3: Test Contract Retirement

1. Delete app-specific contract tests for `apps_repo_brief`.
2. Delete package-specific unit/integration scaffolds.
3. Update registry and parity tests to expect one fewer active app where required.
4. Add or preserve a narrow absence check only if useful.

### Wave 4: Package Hard Delete

1. Delete `apps_repo_brief/`.
2. Remove empty package-specific test directories if any remain.
3. Confirm no runtime artifact directories need archival.

### Wave 5: Verification

Run targeted checks:

1. `rg -n "apps_repo_brief|repo_brief" -g "!plans/**" -g "!docs/archive/**" -g "!docs/reports/**" -g "!artifacts/**"`
2. Unit tests for changed registry/tooling surfaces.
3. App test-surface parity check.
4. Core leakage scan if reachable.
5. ADG/gate verification if available in the current environment.

---

## Risks

- Some generated or historical reports mention `apps_repo_brief`; these should not block deletion unless active gates consume them.
- `agentic_core` files contain app-name registries that already violate the ideal core-agnostic rule; deletion should reduce, not expand, those literals.
- Existing unrelated worktree changes must not be reverted.
