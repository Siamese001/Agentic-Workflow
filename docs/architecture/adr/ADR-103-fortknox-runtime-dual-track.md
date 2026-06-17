# ADR-103: Fort Knox certification vs runtime proof (dual-track)

**Status:** Accepted (2026-05-25)  
**Plan:** `fortknox-runtime-dual-track-b7c4e2`

## Context

Fort Knox (`compile_requirement_signoff.py` + `verify_final_requirement_signoff_bundle.py`) provides tamper-evident **RTC-REQ** signoff from atomic assertions. Separately, engineers produce **runtime seam proof** (command logs, pytest, artifacts under `docs/reports/` and `artifacts/apps_rg/runtime_proofs/`).

Passing Fort Knox does **not** imply a live provider seam ran correctly.

## Decision

Maintain **two explicit tracks**:

| Track | Role | Authority | Typical artifacts |
|-------|------|-----------|-------------------|
| **Certification** | Notary for requirement signoff | Compiler + verifier only | `artifacts/certification/final_requirement_signoff_report.json` |
| **Runtime** | Live or contract proof that a seam executed | Command output + tests + receipts | `docs/reports/**`, `artifacts/apps_rg/runtime_proofs/**` |

Agents and CI must never substitute one for the other.

## CI posture (W1)

| Gate | Default posture | Notes |
|------|-----------------|-------|
| `verify_final_requirement_signoff_bundle.py` | **fail-closed** on certification PRs | Pair with compiler regen |
| `check_fortknox_*` advisory cluster | **advisory** unless branch policy tightens | See `ops_scripts/ci/run_contract_gates.py` ordering |
| Runtime seam rules | **001-runtime-seam-execution** | PASS requires command + test evidence |

## Consequences

- New RTC-REQ assertions stay emitter-allowlisted (`tools/cert/*`); runtime paths do not emit assertions.
- Runtime manifests use `docs/reports/runtime_cert/README.md` template.
- Fort Knox skill and `AGENTS.md` link here instead of duplicating rule text.

## Retirement path (ADR-091 alignment, W4)

Fort Knox remains the **certification notary** until explicit retirement triggers fire. This is not an implementation of in-toto/Sigstore in-repo — it documents when the dual-track model allows shrinking Fort Knox scope.

| Trigger | Action |
|---------|--------|
| **T1** — Runtime seam receipts cover ≥90% of RTC-REQ rows that claim live behavior | Move those RTC-REQ assertions to runtime-emitter allowlist only after Author-Gate; shrink Fort Knox rows to notary-only controls |
| **T2** — `trust_level` stable at `FINAL_SIGNED_CERTIFICATION` for 30 days + mutation runner green | Enable `POSITIVE_CONTROL_STRICT=1` in CI (ADR-091 deferred) |
| **T3** — Signer identity ADR landed (ADR-091 P5: cosign keyless vs GPG) | Promote envelope from `UNSIGNED_BLOCKED` to signed proof tier |
| **T4** — ADR-091 superseded by external attestation (in-toto predicate per release) | Archive `check_fortknox_*` to advisory; compiler becomes export-only |

Until **T1–T4**, do not delete Fort Knox gates or hand-edit compiler output. Runtime track PASS does not satisfy T1 alone — requires mapped RTC-REQ coverage audit (`tools/cert/` assertion ledger review).

## References

- ADR-091 Fort Knox certification discipline
- `.claude/skills/fortknox-evidence/SKILL.md`
- `.claude/rules/001-cursor-runtime-seam-execution.mdc`
