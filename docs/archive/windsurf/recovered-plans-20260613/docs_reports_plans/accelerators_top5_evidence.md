# Top-5 Accelerator Implementation — Evidence Artifact

**Status:** ✅ RESOLVED
**Timestamp:** 2026-03-14
**Tests:** 145 passed, 0 failed, 0 skipped

---

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## SCOPE

### Files Created
| File | Purpose |
|------|---------|
| `tools/adg/adg_test_selector.py` | #5 — ADG-backed test selection via `covers` edges |
| `tools/adg/adg_stale_guard.py` | #2 — ADG staleness guard (ingest timestamp vs git) |
| `tools/adg/adg_type_check.py` | #4 — Incremental type checking (blast radius + mypy) |
| `tools/adg/adg_antipattern_fixer.py` | #1 — Guardian comment format auto-fixer |
| `tests/adg/test_adg_test_selector.py` | Tests for #5 (34 tests) |
| `tests/adg/test_adg_stale_guard.py` | Tests for #2 (22 tests) |
| `tests/adg/test_adg_type_check.py` | Tests for #4 (27 tests) |
| `tests/adg/test_adg_search_enhancements.py` | Tests for #3 (24 tests) |
| `tests/adg/test_adg_antipattern_fixer.py` | Tests for #1 (38 tests) |

### Files Modified
| File | Change |
|------|--------|
| `tools/adg/adg_redis_query.py` | #3 — Added `layer`/`entity_type` filter params to `search_nodes()`; updated CLI with `--layer`/`--entity-type` flags; made `term` optional (default `""` = all nodes) |

---

## DEPENDENCY_GRAPH

```
tools/adg/adg_test_selector.py
  └─ imports: tools.adg.adg_redis_query.ADGRedisClient
  └─ queries: adg:nodes:by_file:<path>, adg:edge:in:<nid>:covers, adg:node:<tnid>

tools/adg/adg_stale_guard.py
  └─ imports: tools.adg.adg_redis_query.ADGRedisClient
  └─ reads: adg:meta.ingested_at
  └─ calls: git log (subprocess, no shell=True)

tools/adg/adg_type_check.py
  └─ imports: tools.adg.adg_redis_query.ADGRedisClient
  └─ queries: adg:nodes:by_file:<path>, adg:edge:in:<nid>:imports, adg:node:<nid>
  └─ calls: mypy via subprocess (no shell=True)

tools/adg/adg_antipattern_fixer.py
  └─ NO ADG dependency — pure regex on Python source
  └─ calls: git diff (subprocess, no shell=True) for --from-diff mode

tools/adg/adg_redis_query.py (enhanced)
  └─ search_nodes() — new layer/entity_type filter params
```

---

## ROBUSTNESS_MATRIX

| Accelerator | Success | Empty Input | Not in ADG | Redis Down | Determinism |
|-------------|---------|-------------|------------|------------|-------------|
| #5 Test Selector | ✅ covers→paths | ✅ [] | ✅ [] (no error) | ✅ raises | ✅ |
| #2 Stale Guard | ✅ fresh/stale | ✅ 0 commits=fresh | ✅ raises on missing key | ✅ raises | ✅ |
| #4 Type Checker | ✅ blast+mypy | ✅ [] | ✅ file returned as-is | ✅ raises | ✅ |
| #3 Search | ✅ substring match | ✅ all nodes | ✅ [] | ✅ propagates | ✅ |
| #1 Fixer | ✅ fixes all forms | ✅ no changes | N/A (no ADG) | N/A | ✅ idempotent |

---

## FAILURE_CAPTURE

All accelerators are **fail-closed**:

- **Redis unavailable** → `redis.ConnectionError` propagates immediately, no fallback
- **ADG not loaded** → `RuntimeError("ADG Redis cache is not loaded")` from `ping()`
- **`ingested_at` missing** → `RuntimeError` with regen instructions
- **git command failure** → `RuntimeError` with stderr message
- **git timeout** → `RuntimeError("timed out")`
- **mypy not installed** → `RuntimeError("mypy not found")`
- **mypy timeout** → `RuntimeError("timed out after 120s")`
- **file not readable** → `OSError` propagates (no silent swallowing)

**NO grep fallbacks. NO filesystem search fallbacks. NO silent except swallowing.**

---

## CANONICAL FORMS ENFORCED

### Guardian Comment (#1 Fixer)
Canonical: `# guardian: allow-<type> -- <justification>`

Auto-corrected forms:
| Input | Fixed To |
|-------|----------|
| `# guardian allow-magic-config -- r` | `# guardian: allow-magic-config -- r` |
| `# guardian: allow-magic-config: r` | `# guardian: allow-magic-config -- r` |
| `# Guardian: allow-magic-config -- r` | `# guardian: allow-magic-config -- r` |
| `# guardian: allow_magic_config -- r` | `# guardian: allow-magic-config -- r` |
| `# guardian: allowMagicConfig -- r` | `# guardian: allow-magic-config -- r` |

Supported types: `magic-config`, `silent-swallower`, `global-mutation`, `bare-except`, `os-path`, `string-path-concat`

---

## CLI REFERENCE

```bash
# #5 — Select tests covering changed files
python tools/adg/adg_test_selector.py --from-diff --show-gaps
python tools/adg/adg_test_selector.py --from-diff --pytest-args | xargs pytest

# #2 — Check if ADG is stale before querying
python tools/adg/adg_stale_guard.py --json
python tools/adg/adg_stale_guard.py --files   # list what changed

# #4 — Type-check only the blast radius of changed files
python tools/adg/adg_type_check.py --from-diff --depth 1
python tools/adg/adg_type_check.py --from-diff --dry-run   # show scope only

# #3 — Filtered node search
python tools/adg/adg_redis_query.py search-nodes Agent --layer L3
python tools/adg/adg_redis_query.py search-nodes "" --entity-type class --layer L2

# #1 — Fix all guardian comment violations in changed files
python tools/adg/adg_antipattern_fixer.py --from-diff --check-only
python tools/adg/adg_antipattern_fixer.py --from-diff
```

---

## TEST EVIDENCE

```
pytest tests/adg/test_adg_test_selector.py
      tests/adg/test_adg_stale_guard.py
      tests/adg/test_adg_type_check.py
      tests/adg/test_adg_search_enhancements.py
      tests/adg/test_adg_antipattern_fixer.py
      -v

145 passed in 0.22s
```

All tests:
- No mocks for internal logic — only Redis (external service) and subprocess mocked
- No randomness, no time-dependency — fully deterministic
- Fail-closed: Redis error tests verify propagation, not swallowing
- Idempotent: `fix_source` applied twice → 0 changes on second pass
- Edge cases: empty input, file not in ADG, cycle detection (depth guard), boundary timestamps

## Rules

1. Follow all constitutional rules and guidelines
2. Maintain compliance with established standards
3. Document all changes and decisions
4. Validate all implementations before completion

---

## Success Criteria

- [ ] All objectives completed successfully
- [ ] Validation tests pass
- [ ] Documentation updated
- [ ] Stakeholder approval received

---

