# apps_shared — Test Strategy

## Test pyramid

| Tier | Scope | Location |
|---|---|---|
| **Unit** | Pure helpers, types, utils | `tests/unit/apps_shared/` |
| **Facade contract** | PEP 562 lazy import, boundary-leak invariants | `tests/unit/apps_shared/adapters/test_w3_boundary_facades.py` |
| **Enforcement** | Hardened*Strategy behavior | `tests/unit/apps_shared/enforcement/` |
| **Proof harness** | AppRunEvidencePacket, bypass validator, negative controls | `tests/unit/apps_shared/proof/` |
| **Contract** | Cross-app envelope emitters, L0 emit schemas | `tests/unit/apps_shared/contracts/` |
| **Integration** | Governed-app-runner full path | `tests/unit/apps_shared/integrations/` |

## Coverage targets

- `validators/enforcement/`: 100% branch coverage on every `Hardened*Strategy`
- `validators/proof/`: ≥85% line coverage; every scenario runner exercised
- `integrations/adapters/`: 100% lazy-resolution path + AttributeError path
- `reasoning/orchestration/`: 100% of HopPipelineExecutor state transitions

## Boundary-leak invariants (W3, locked in)

The W3 test suite (`test_w3_boundary_facades.py`) enforces:
1. `apps_eval/` has NO direct `system_learning` or `apps_rg` imports
2. `apps_lic/` has NO direct `system_learning` imports
3. Facades use PEP 562 `__getattr__` (no eager upstream imports at module load)
4. Unknown attributes raise `AttributeError`, not `ImportError`

## Running

```bash
pytest tests/unit/apps_shared/ -q
pytest tests/unit/apps_shared/adapters/ -q      # boundary contract
pytest tests/unit/apps_shared/enforcement/ -q   # strategy behavior
pytest tests/unit/apps_shared/proof/ -q         # proof harness
```

## CI gates

- `T7r` — ADR-082 taxonomy (this app is the largest consumer)
- Boundary-leak tests run on every `apps_eval`/`apps_lic` PR
- Proof-harness tests gate every apps_e2e certification run

## References

- `TECHNICAL_SPEC.md`
- ADR-082 — folder taxonomy
- `.windsurf/plans/apps-runtime-first-principles-e6ba58.md` — boundary facades
