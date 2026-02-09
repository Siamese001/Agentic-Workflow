# Known Failing / Skipped Tests — Consolidation Audit

**Date**: 2026-02-09
**Branch**: `v5.1-agentic-core-heal-complete`
**Pre-consolidation SHA**: `ccaed1df6`

## Summary

All skipped tests documented below were **already failing before consolidation**.
Evidence: each test was either `pytest.mark.skip`-ed in a prior commit or
references modules that were removed/relocated during the LCD refactor (not the
consolidation itself).

## Skipped Tests (pytest.mark.skip)

| File | Skip Count | Root Cause | Pre-Consolidation? |
|------|-----------|------------|---------------------|
| `tests/unit/core/test_sovereign_seal_state.py` | 10 | Missing `SovereignSealState` infrastructure | Yes — LCD refactor |
| `tests/misc/test_meta_learning.py` | 7 | Missing Redis/Pinecone integration deps | Yes — Phase 2.1 |
| `tests/unit/agentic_core/L5_safety/runtime/test_process_guard.py` | 3 | Missing `ProcessGuard` runtime | Yes — Phase 3 |
| `tests/guardian/test_import_safety.py` | 1 | Import chain validation | Yes |
| `tests/integration/agentic_core/test_inspector_agents_runtime.py` | 1 | Inspector agent infra | Yes |
| `tests/unit/agentic_core/agents/test_red_sentinel_agent.py` | 1 | Missing `RedSentinelAgent` | Yes — LCD refactor |
| `tests/unit/agentic_core/core/test_pascal_sovereign_replacements.py` | 1 | PSF assertion rot | Yes — Phase 2b |

## Quarantined Tests

49 tests are formally quarantined under `tests/_quarantine/` with manifest at
`tests/_quarantine/QUARANTINE_MANIFEST.json`. Categories:

- **infra_required**: 20 (dashboard HTML artifacts)
- **missing_module**: 11 (LCD refactor relocations)
- **missing_dep**: 7 (redis, fastapi)
- **runtime_error**: 7 (assertion rot, infra issues)
- **assertion_rot**: 4 (execute_ssot API changes)

## Ownership & Deadlines

| Category | Owner | Deadline |
|----------|-------|----------|
| LCD import path fixes | Core team | Sprint +1 |
| Redis/Pinecone deps | Infra team | Sprint +2 |
| Dashboard HTML generation | CI team | Sprint +1 |
| Assertion rot (execute_ssot) | Core team | Sprint +1 |

## Policy

Per constitutional rule §30 (No Silent Masking):
- No `pytest.mark.skip` without quarantine entry
- No `xfail` without regression deadline
- Quarantine ceiling must not increase without explicit commit rationale
