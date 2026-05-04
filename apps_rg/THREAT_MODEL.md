# apps_rg — Threat Model

## Scope

`apps_rg` ingests **externally-sourced user content** (candidate profiles, job descriptions) and produces generated text via an LLM-backed HOP pipeline. This creates an attack surface distinct from pure-compute apps.

## Assets

| Asset | Sensitivity | Integrity requirement |
|---|---|---|
| Candidate profile (PII) | High | Must not leak into shared caches or other runs |
| Job description (public or private) | Medium | Provenance must be preserved in evidence packet |
| Generated résumé | Medium | Must be reproducible from inputs + evidence |
| Replay keys | High | Must not be `_noop`-silenced (governance xfail tracks) |
| Executor auth credentials | Critical | Scoped; never logged in full |

## Threat actors

1. **Malicious input author** — crafts profile/JD with prompt injection
2. **Compromised executor** — Anthropic / vLLM gateway returns adversarial completion
3. **Insider with code access** — inserts logic that bypasses hardened strategies
4. **Dependency confusion** — upstream package hijack (agentic_core, apps_shared)

## Threats and mitigations

### T1 — Prompt injection via profile/JD

- **Mitigation**: Every input passes through `validators/` before reaching the HOP chain. `anti_overfitting` module enforces constraints that reject content matching injection signatures.
- **Residual risk**: Novel injection patterns may slip through — mitigated by rubric-based QA (HOP6).

### T2 — Executor output contamination

- **Mitigation**: Every executor call is wrapped by a `Hardened*Strategy` (validators/enforcement/). Output validation checks for schema compliance, length bounds, banned tokens.
- **Residual risk**: Strategy must be kept in sync with LLM behavioral drift — calibration cadence in `/author-gate-calibration-report`.

### T3 — PII leakage across runs

- **Mitigation**: No candidate profile data persists in shared caches (`GlobalcacheStrategy` partitions by run-id). Evidence packets are per-run with deterministic hash.
- **Residual risk**: Log aggregation may capture PII — addressed by log-redaction middleware (tracked in plan `apps-rg-governed-runtime-b8d4f1.md`).

### T4 — Replay-key silencing

- **Known gap**: `bootstrap_runtime.py` currently contains `emit_replay_key = _noop`. This silences replay receipts in production, breaking non-repudiation.
- **Tracked as**: governance xfail `tests/governance/test_no_lifecycle_noop_shims_in_production.py`
- **Remediation**: plan `apps-rg-governed-runtime-b8d4f1.md` Wave 7 P7.2

### T5 — Dependency confusion

- **Mitigation**: All dependencies pinned in `uv.lock`. CI gate rejects unpinned versions.
- **Residual risk**: Transitive dependency updates — mitigated by lockfile refresh cadence.

### T6 — Direct executor bypass

- **Mitigation**: Architectural invariant — `apps_rg/engines/` must invoke `apps_shared/validators/enforcement/Hardened*Strategy`. ADG contract tests verify no direct `anthropic.Client(...)` calls in producer code.

## Trust boundaries

```
USER INPUT ──[validators/]──> HOP1..HOP6 ──[Hardened*Strategy]──> EXECUTOR
                 ↓                              ↓                      ↓
           schema check              provenance stamp          scoped auth
```

Each `──>` is a trust boundary. Evidence packet records crossings.

## Non-goals

- Side-channel attacks on the inference provider
- Physical security of the infrastructure
- Supply-chain attacks on the Python interpreter itself

## References

- ADR-028 — publisher-boundary doctrine
- `tools/cert/` — certification evidence
- `tests/governance/` — invariant lock-in tests
- `TECHNICAL_SPEC.md` — architecture spec
