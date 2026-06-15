# Old L5 Agent Wave 4 Archive Gate

Plan: `old-l5-agent-retirement-a94f6c`
Date: 2026-06-15
Source manifest: `docs/reports/agent_deprecation/old_l5_agent_retirement_manifest_20260615.json`

## Gate Result

W4 physical archive/delete is blocked.

Manifest value:

```text
eligible_for_physical_archive_as_of_2026_06_15 = 0
```

The already-authorized deletion cohort has an earliest archive-eligible date of 2026-07-23. The remaining unclassified and large-facade cohorts do not yet have replacement proof, zero-live-consumer proof, or per-file deletion authorization.

## Actions Taken

- No `git rm` was performed.
- No candidate file was moved to an archive path.
- W1 migrated selected active references away from already-authorized shims.
- W2/W3 recorded deprecation and split-plan evidence for future deletion waves.

## Required Before W4 Can Proceed

1. Current date is on or after the relevant archive-eligible date.
2. Focused literal scan shows zero active live consumers for the candidate.
3. ADG or fallback SQLite evidence shows zero live import consumers, or remaining consumers are explicitly historical/generated and excluded.
4. Replacement surface is documented where behavior is still needed.
5. Physical archive path is listed in the candidate file metadata or the deletion receipt.

## Next Eligible Queue

The 2026-07-23 queue includes the 21 `COOLING_WINDOW_AUTHORIZED` candidates listed in `old_l5_agent_wave2_authorization_20260615.md`. W4 should be rerun on or after 2026-07-23, after refreshing consumer evidence.
