# SVP Documentation Gate Hardening

Plan ID: `svp-docs-gate-hardening-7c4e2a`

Status: **APPROVED — implementation in progress**

## Objective

Turn the weekly SVP documentation automation from a prompt-only review into a replayable, deterministic governance path. Preserve one authority for publication: the existing PR-only main publisher.

## Scope

1. Convert the weekly automation to audit-only.
2. Add a separately invoked, approval-bound manual documentation refresh.
3. Implement deterministic X2 checks and one X3 disposition.
4. Add versioned X1D, X2, X3, and run receipt schemas.
5. Add a versioned reviewer-packet and claim-evidence manifest.
6. Correct stale architecture-proof summary output and reviewer-facing status documents.
7. Add focused unit tests and GitHub Actions validation.

## Authority model

```text
weekly audit -> X2 pre -> X1D -> X3 PLAN_ONLY/NOOP/BLOCK/ESCALATE_HUMAN
approved manual refresh -> X2 pre -> edit -> X2 post -> X1D -> X3 ALLOW_TO_PR/BLOCK
ALLOW_TO_PR -> on-demand-pr-main-publisher -> GitHub PR -> CI -> merge
```

The SVP documentation automations do not merge or push directly to `main`.

## Acceptance criteria

- Weekly automation is read-only and cannot emit `ALLOW_TO_PR`.
- Manual editing requires a machine-readable approval receipt.
- X2 gates emit explicit PASS, WARN, FAIL, or NOT_APPLICABLE results.
- X3 emits exactly one allowed disposition.
- Receipt schemas are checked in and validated.
- App classification and counts are derived from `APP_REGISTRY`.
- Architecture proof output contains no hard-coded five-governed/two-exception narrative.
- Active reviewer documents contain no stale 36-check or all-seven-governed claims.
- PR publication remains delegated to `on-demand-pr-main-publisher`.

## Verification

```bash
python scripts/governance/verify_codex_primary.py
python scripts/governance/verify_codex_enforcement_home.py --json
python scripts/governance/svp_docs_review.py --mode audit --phase pre --json
python ops_scripts/ci/run_architecture_proof.py --suite S1
pytest -q tests/unit/scripts/governance/test_svp_docs_review.py
pytest -q tests/unit/scripts/governance/test_verify_codex_enforcement_home.py
git diff --check
```
