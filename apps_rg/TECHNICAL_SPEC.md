# apps_rg — Technical Spec

## Purpose

Governed resume-generation application. Ingests a candidate profile + target-job description and produces an ATS-optimized, anti-overfitted résumé via a multi-hop HOP pipeline with hardened enforcement strategies.

## Architecture

### HOP pipeline

1. **Achievement extraction** — parse source profile
2. **Prioritization** — `AchievementPrioritizerEngine` scores per target JD
3. **ATS coverage** — `ats_coverage` module validates keyword hit-rate
4. **Anti-overfitting** — diversity + novelty constraints
5. **Assembly** — `HopProposalAssemblyEngine` produces draft
6. **Hardened enforcement** — `validators/enforcement/HardenedanthropicexecutorStrategy` (and siblings) veto-check output
7. **Emission** — renderer + evidence packet

### Folder layout (post-ADR-082)

```
apps_rg/
├── config/
│   └── schemas/           # moved from apps_rg/schemas/
├── engines/               # 52 engine modules
├── integrations/
│   └── hops/              # per-HOP integration glue
├── outputs/
├── reasoning/
├── services/
│   └── runtime/
│       └── bootstrap.py   # moved from apps_rg/bootstrap_runtime.py
├── types/
├── validators/
│   └── enforcement/       # moved from apps_rg/enforcement/
├── utils/
├── tools/                 # developer utilities (33 items)
├── tests/                 # app-local tests
└── spine_manifest.yaml
```

`ops_scripts/apps_rg/` holds ops-class scripts (formerly `apps_rg/scripts/`, 77 items; per-script triage deferred).

## Runtime bootstrap

`apps_rg/__init__.py` calls `install_runtime_shims()` at import time:
1. Pydantic v1/v2 compat patches (`BaseModel.model_dump`, `field_validator`, etc.)
2. agentic_core shim synthesis when `agentic_core` is absent (standalone install)
3. Lifecycle-trace SSOT resolution for emit functions

A compat copy at `apps_rg/bootstrap_runtime.py` (shim) preserves the governance xfail test path until 2026-05-17.

## Hardened executor strategies

`validators/enforcement/` hosts `Hardened*Strategy.py` classes (grandfathered CamelCase). Each wraps an executor call with:
- pre-call auth check
- post-call output validation
- provenance tagging
- failure-mode categorization

## Contracts

- **Input**: profile + JD + target-role config
- **Output**: assembled résumé + evidence packet + ATS-coverage report

## Invariants

1. No JD-specific content leaks into resumé beyond validated anchors
2. Every executor call goes through a `Hardened*Strategy` wrapper
3. Replay keys emitted for every spine step (governance xfail tracks remediation gap)

## References

- ADR-082 — folder taxonomy
- Plan `.windsurf/plans/apps-rg-governed-runtime-b8d4f1.md` — runtime hardening
