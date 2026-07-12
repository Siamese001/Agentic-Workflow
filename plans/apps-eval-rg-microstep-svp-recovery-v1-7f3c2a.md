# apps_eval / apps_rg microstep SVP recovery

Plan ID: `apps-eval-rg-microstep-svp-recovery-v1-7f3c2a`

## Objective

Implement the atomic apps_eval microstep contract and L6 grain-parity closure on a clean branch from current `main`, remove the accidental PR #536 bootstrap artifacts, validate the exact branch head, and merge only the verified implementation.

## Waves

1. Remove accidental bootstrap files from main lineage on this branch and establish current-source/test baseline.
2. Expand contracts and registries to atomic U0/L1/L0/C0/PA/L2/X2/X1D/X3/EXIT/UWG/L6/PACKAGE/REGRESSION rows.
3. Harden index-first artifact resolution, path containment, real content digests, and ambiguity handling.
4. Add semantic validators for global, per-lane, gate, judge, Exit, UWG, and governed L6 proof.
5. Remove planned-output self-proof and add post-emission package verification/sealing.
6. Add component/lane/gate/microstep regression outputs and trends.
7. Enforce post-boundary L6 observation and governed v40 release evidence without current-run authority.
8. Add CI, negative controls, run receipt, PR validation, and merge closeout.

## Non-negotiable authority split

- Exit emits exactly one current-run X3.
- UWG alone commits durable state.
- apps_eval grades proof and may supply audit evidence.
- L6 starts only after the sealed current-run boundary and cannot block, rescue, mutate, or emit current-run authority.

## Definition of done

- Full atomic contract and all required artifacts are implemented.
- Planned filenames cannot satisfy presence proof.
- Every required PASS row has an existing contained artifact and content digest.
- All 11 lanes emit complete required rows.
- apps_eval/L6 parity passes at the shared join grain.
- Governed v40 L6 closure is required for release-grade runs.
- Targeted, integration, negative-control, governance, compile, and diff checks pass on the exact remote head.
- Bootstrap files are absent from the final branch.
- PR diff is inspected before merge and merged using the expected head SHA.
