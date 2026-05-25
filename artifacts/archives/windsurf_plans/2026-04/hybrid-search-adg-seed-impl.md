---
plan_id: hybrid-search-adg-seed-impl
plan_type: refactor
---

# HybridSearchEngine `adg_seed` Implementation

Implement the missing `adg_seed` method on HybridSearchEngine (referenced by E.F1.1 P1 row, impact 404.5).

---

## Evidence Sources

| Source | Why | Status |
|---|---|---|
| Wave/Phase row `E.F1.1` (P1, impact 404.5) | concrete consumer failure | ✅ captured |
| `agentic_core/.../HybridSearchEngine.py` | the class missing the method | 🔲 confirm path on execution |
| `hybrid-search-adg-seed-rerank-c58e21.md` | parent plan covering the design | ✅ |

---

## Wave Structure

| Wave | Metric | Scope | Checkpoint | Tokens |
|------|--------|-------|------------|---------|
| W1 | Implement `adg_seed` | HybridSearchEngine | A | 3,000 🟢 |

---

## Phase-Level Summary

| Phase ID | Title | Scope | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| W1.1 | Add `adg_seed` method wired through to ADG retrieval path | HybridSearchEngine + adapter | AttributeError at runtime | ~3k | 🔲 TODO |

---

## Notes

Scaffold — the design already exists in `hybrid-search-adg-seed-rerank-c58e21`. This plan is the implementation-side counterpart. Consider merging the two rather than creating a separate file; if merged, update the Backlog row's Plan relation and archive this stub.

## Success Criteria

- [ ] E.F1.1 Backlog row transitions to Done
- [ ] `adg_seed` covered by a unit test that exercises the ADG path
