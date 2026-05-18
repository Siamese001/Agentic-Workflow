# apps_rg whole-run R1B lookup — W9

**Wave:** W9 only  
**Status:** PASS

## Summary

W9 wires **whole-run** cache preflight so apps_rg consults W7/W8 `HistoricalIntentRecord` vectors at `ROLE_TARGET_RUN` grain **after R1A** and **before** normal generation. Hits emit an apps_rg-local terminal cache-return packet for Exit review; misses and inadmissible candidates fall through unchanged.

## Preflight order

1. **R1A_EXACT_CACHE** — `check_r1a_cache` in `apps_rg/__main__.py::_run_with_args`
2. **R1B_SEMANTIC_ROLE_TARGET_RUN** — `execute_whole_run_r1b_preflight`
3. **NORMAL_GENERATION** — `run_integrated_r4_deterministic_pipeline`

Documented in `apps_rg/config/domain_contract/cache_profiles.yaml` → `whole_run_cache_preflight.route_order`.

## R1B lookup behavior

| Property | Value |
|----------|--------|
| Lookup anchor | `HistoricalIntentRecord.request_intent_vector` |
| Grain | `ROLE_TARGET_RUN` only |
| Child chunks | Loaded for **compatibility inspection** only; never independent lookup keys |
| C0 | **Not consulted** (`c0_fact_vectors_consulted: false`) |
| Profile/digest mismatch | Miss / inadmissible — no degraded hit |
| Exit | `exit_bypassed: false`; `exit_review_required: true` on hit |

## Modules

| File | Role |
|------|------|
| `apps_rg/cache/r1b_whole_run_preflight.py` | W9 preflight orchestration + terminal packet |
| `apps_rg/cache/r1b_retrieval.py` | Intent-vector search + compatibility report (profile hashes) |
| `apps_rg/cache/r1b_adapter.py` | `check_r1b_for_apps_rg` → whole-run preflight |
| `apps_rg/__main__.py` | R1A → R1B → pipeline; writes `r1b_whole_run_preflight_hit.json` on hit |

## Hit receipt

On R1B hit, `runs_dir/r1b_whole_run_preflight_hit.json` contains:

- `terminal_packet` (`apps_rg.R1BCacheReturnPacket`)
- `child_chunk_inspection` (chunks inspected, `used_as_lookup_key: false`)
- `compatibility_report` per candidate

## Fixtures

`artifacts/apps_rg/r1b_semantic_cache/w9_fixtures/`:

- `accepted_r1b_hit.json`
- `semantic_miss_fallthrough.json`
- `inadmissible_profile_mismatch.json`
- `fallthrough_to_generation.json`
- `child_chunks_inspected_not_independently_retrieved.json`
- `r1b_vs_c0_separation.json`

Regenerate: `python tools/apps_rg/emit_r1b_w9_fixtures.py`

## Commands (2026-05-18)

```text
python -m compileall apps_rg -q  → exit 0
python tools/apps_rg/emit_r1b_w9_fixtures.py → exit 0
pytest tests/unit/apps_rg -k "r1b and (lookup or retrieval or adapter or compatibility)" -q → 12 passed
pytest tests/_apps_contract -k "apps_rg and r1b and (lookup or retrieval or preflight or cache)" -q → 21 passed (2 unrelated core failures in broad filter)
git diff HEAD -- agentic_core → empty
```

## Non-claims

- **W6 section-cache preflight** not complete (whole-run only in W9).
- **UWG durable persistence** not solved.
- Production `dispatch_apps_rg_run` path may need explicit W9 hook if not routed through `_run_with_args`.
