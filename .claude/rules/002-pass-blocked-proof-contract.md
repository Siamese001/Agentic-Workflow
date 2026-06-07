
# PASS / PARTIAL / FAIL / BLOCKED Proof Contract

## PASS is expensive

Mark PASS only when all are true:

- The requested scoped seam was patched or verified.
- Exact command output is available.
- Relevant tests/gates were run and passed.
- Any generated artifact path is listed.
- No provider, model, judge, registry, schema, or runtime path was mocked unless the user explicitly asked for mock-only proof.

## PARTIAL is honest progress

Use PARTIAL when some work completed, but one or more proof requirements are missing. Name the missing proof directly.

## FAIL is a real failure

Use FAIL when the command/test/gate ran and failed. Include the failing command and smallest safe next patch.

## BLOCKED is not failure theater

Use BLOCKED when execution cannot proceed due to missing provider/model/API key, unavailable service, permission boundary, policy stop, missing file, or ambiguous destructive target.

## Receipt hyperlinks

In chat responses and on-disk `*_receipt.md` / manifest JSON, list every repo path in `FILES_CHANGED`, `ARTIFACTS`, and `REPORTS_GENERATED` as a markdown link `[basename](forward/slash/path)`. Manifests SHOULD include parallel `*_links` entries (`path` + `markdown`) — see `ops_scripts/apps_rg/l6_benchmarks/receipt_links.py`.

## Forbidden status behavior

- No PASS because the plan was updated.
- No PASS because a marker was emitted.
- No PASS with skipped tests unless explicitly scoped as documentation-only.
- No burying failed global gates as “pre-existing” without status impact.
- No deferred-scope label for a blocker that affects the requested seam.
- No “should pass” language. Either it passed, failed, is partial, or is blocked.
