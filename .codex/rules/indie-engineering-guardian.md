# Indie Engineering Guardian — Completion Floor

The detailed evidence, operating manual, enforcement map, and success metrics
are canonical at [`docs/governance/indie-engineering-guardian.md`](../../docs/governance/indie-engineering-guardian.md).
This always-on floor preserves its decisive requirements:

- Deliver one user objective, not activity, wave count, receipts, or partial
  progress. Keep the same branch/objective until it is complete or genuinely
  blocked; state the exact missing authority or dependency.
- Do not create or merge a PR for a partial, evidence-only, or unproven result.
  A completion claim needs the requested output, relevant fresh execution and
  tests, and the applicable review/authorization evidence.
- For `apps_rg`, a PASS or ready-for-review claim needs a fresh candidate-SHA
  run with all required sections, mandatory artifacts, final DOCX assembly and
  inspection, and no unresolved mandatory gate. Component tests alone do not
  prove product completion.
- Publication is separate from implementation: after merge, prove the feature
  tip is contained in `origin/main`, local and remote `main` converge, and run
  `codex_main_closeout.py` with governance health. Otherwise report
  `PUBLICATION_BLOCKED`, not PASS.
- Do not waive relevant failures as pre-existing, degraded, flaky, or
  environmental. Preserve fail-closed status and use the narrowest existing
  hook, CI gate, or verifier rather than adding overlapping governance prose.
