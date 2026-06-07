
# Cursor Runtime Seam Execution Contract

Cursor must behave like a bounded L2 executor, not a project manager.

## Default execution shape

For implementation or verification work, use this shape unless the user explicitly asks for broader planning:

1. Identify one narrow runtime seam.
2. Name immutable constraints before editing.
3. Patch the smallest necessary files.
4. Run the exact command that exercises the seam.
5. Run the narrowest relevant test or gate.
6. Report evidence with PASS, PARTIAL, FAIL, or BLOCKED.

## Scope containment

- Prefer one file or one seam. Avoid multi-wave execution unless the user explicitly asks for it.
- Do not create a plan when a direct patch plus command proof is possible.
- Do not create new frameworks, registries, adapters, prompts, or broad abstractions unless the seam cannot be proven without them.
- Do not convert blockers into deferred scope. A blocker remains BLOCKED until a command proves otherwise.
- Do not ask for confirmation when the next step is deterministic and already inside the user’s requested scope.

## Runtime proof over receipts

- A narrative receipt is not proof.
- A marker is not proof.
- A Notion/status update is not proof.
- A sidecar dry run is not production runtime proof.
- A passing unit test is useful, but the runtime seam still needs the command that exercises the actual path when available.

## Cursor response floor for repo work

Every repo-work response must include:

```text
STATUS: PASS | PARTIAL | FAIL | BLOCKED
FILES_CHANGED:
- [basename](repo/relative/path)
COMMANDS_RUN:
- command -> result
TESTS_GATES:
- command -> result
ARTIFACTS:
- [basename](repo/relative/path) or NONE
REPORTS_GENERATED: (when applicable)
- [basename](repo/relative/path)
NOTES:
- one or two important caveats only
```

**Receipt hyperlinks (required):** In chat responses and companion `*_receipt.md` / manifest JSON, every repo path in `FILES_CHANGED`, `ARTIFACTS`, and `REPORTS_GENERATED` MUST be a markdown link `[label](path)` using forward slashes (e.g. `[human_benchmark_plan.md](artifacts/apps_rg/plans/human_benchmark_plan.md)`). JSON manifests SHOULD also include parallel `*_links` objects via `ops_scripts/apps_rg/l6_benchmarks/receipt_links.py` (`path` + `markdown` fields).
