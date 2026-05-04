# apps_lic — Test Strategy

## Test pyramid

| Tier | Scope | Location | Targets |
|---|---|---|---|
| **Unit** | Pure logic, no I/O | `tests/unit/apps_lic/` | Engines, planners, policy tables, decision router, judges |
| **Contract** | HOP I/O contracts | `tests/_apps_contract/apps_lic/` | HOP inputs/outputs match schema |
| **Integration** | Governed-run end-to-end with mocked spine | `tests/integration/apps_lic/` | HOP1..HOP8 full chain |
| **Proof/e2e** | Evidence-packet shape + apps_e2e runtime proof | `tests/_apps_contract/test_app_domain_e2e_proof.py` | SIGNED_OFF proof produced |
| **Governance** | ADG contract tests, xfail invariants | `tests/governance/` | Engine tree = HOP1..HOP8 |

## Coverage targets

- **Unit**: ≥85% line coverage on `engines/`, `reasoning/`, `validators/policy/`
- **Contract**: 100% of HOP I/O schemas exercised
- **Integration**: at least one happy path + one policy-gate-reject per HOP4 branch

## Mocking discipline

- L0 (routing) and L3 (orchestration) mocked via `agentic_core` spine test doubles
- External APIs (LinkedIn, email senders) mocked with fixture envelope
- Persistence tested against in-memory SQLite (`:memory:`)

## Key fixtures

- `tests/unit/apps_lic/conftest.py` — policy-table loader, rubric seeding
- `tests/_apps_contract/apps_lic/fixtures.py` — canonical profile, sender, context

## Running

```bash
pytest tests/unit/apps_lic/ -q
pytest tests/_apps_contract/apps_lic/ -q
pytest tests/governance/ -q -k apps_lic
```

## CI gates

- `T7e` — apps_lic-specific contract gate (see `.github/workflows/all-requirements-gate.yml`)
- `T7r` — apps folder taxonomy (ADR-082)
- Governance xfails: zero strict-xfail regressions permitted.

## References

- ADR-082 — folder taxonomy
- `TECHNICAL_SPEC.md` — architecture spec
