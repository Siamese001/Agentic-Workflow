# CI Gate Coverage Audit - Archived

This audit is superseded by `.github/workflow-config.yaml` and the current
three-check branch-protection topology:

- `workflow-reference-check`
- `contract-summary`
- `smoke-summary`

The historical five-workflow Tier 0 / Tier 1 snapshot is retained only as
pre-consolidation evidence. It is not the active CI contract.

## Status

- `ARCHIVED`
- `SUPERSEDED_BY: .github/workflow-config.yaml`

## Historical Reference

The previous static audit covered five Tier 0 / Tier 1 workflows and
verified that they existed on disk, used the canonical trigger shape,
pinned Python 3.12, and invoked only their intended verifier command.
That snapshot is intentionally stale now that CI has been consolidated.
