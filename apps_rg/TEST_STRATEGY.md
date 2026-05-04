# apps_rg — Test Strategy

## Test pyramid

| Tier | Scope | Location |
|---|---|---|
| **Unit** | engines/, reasoning/, validators/enforcement/ | `tests/unit/apps_rg/` |
| **Enforcement** | Hardened*Strategy wrappers | `tests/unit/apps_rg/enforcement/` |
| **Contract** | ATS coverage, anti-overfitting invariants | `tests/_apps_contract/` |
| **Integration** | Full HOP pipeline with mocked executor | `tests/integration/apps_rg/` |
| **Proof** | apps_e2e runtime proof (SIGNED_OFF) | `tests/_apps_contract/test_app_domain_e2e_proof.py` |
| **Governance** | ADG contract + xfail invariants | `tests/governance/` |

## Coverage targets

- **engines/**: ≥80% line coverage
- **validators/enforcement/**: 100% branch coverage on every `Hardened*Strategy.execute()` path
- **Anti-overfitting**: every diversity constraint has a negative-control test

## Running

```bash
pytest tests/unit/apps_rg/ -q
pytest tests/unit/apps_rg/enforcement/ -q
pytest tests/governance/ -k apps_rg
```

## Governance

- `test_bootstrap_runtime_does_not_noop_replay_key` (xfail, strict) — locks in the replay-key remediation target. After plan `apps-rg-governed-runtime-b8d4f1.md` Wave 7 P7.2, this test flips to pass.
- Post-ADR-082, the test reads `apps_rg/bootstrap_runtime.py` (compat shim with full content copy). When the shim is retired 2026-05-17, update the test to read `apps_rg/services/runtime/bootstrap.py`.

## Mocking

- `agentic_core` — `install_runtime_shims()` auto-stubs when absent
- Anthropic executor — mocked via `pytest` fixture returning canned completions
- ATS scoring — deterministic local implementation; no external API

## CI gates

- `T7r` — ADR-082 taxonomy
- `T7` — all-requirements
- apps_e2e gates (evidence assertions, runtime proof)

## References

- `TECHNICAL_SPEC.md`
- ADR-082
