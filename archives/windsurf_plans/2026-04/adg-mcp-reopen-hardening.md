---
plan_id: adg-mcp-reopen-hardening
plan_type: infra
---

# ADG MCP Reopen Hardening

Harden the `adg_reopen_connections` path against silent logging overrides, reopen-during-close races, and idempotency bugs that caused W1-series issues.

Scaffold — populated by downstream work under `C1` of `notion-schema-refactor-cleanup-9f2e4a`.

---

## Evidence Sources

| Source | Why | Status |
|---|---|---|
| Wave/Phase rows W1.1, W1.2, W2.1, W2.2 (4 P2 backlog rows) | dependents that required this plan to exist | ✅ captured in Notion |
| `agentic_core/adg/runtime_adg.py` (or equivalent) | the code site to harden | 🔲 |

---

## Wave Structure

| Wave | Metric | Scope | Checkpoint | Tokens |
|------|--------|-------|------------|---------|
| W1 | F1 — fix `logging.basicConfig` override silencing ADG MCP logs | adg_sqlite server | A | 2,000 🟢 |
| W1 | F2 — bounded-timeout wrapper around service.reopen() | adg_sqlite server | A | 2,000 🟢 |
| W2 | F4 — make `adg_reopen_connections` truly idempotent | adg_sqlite server | B | 2,000 🟢 |
| W2 | F5 — reopen-during-close race guard | adg_sqlite server | B | 2,000 🟢 |

**Total: 8,000 tokens across 2 waves, all GREEN.**

---

## Phase-Level Summary

| Phase ID | Title | Scope | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| W1.1 | F1 logging.basicConfig override fix | adg_sqlite logger setup | ADG MCP log silence | ~2k | 🔲 TODO |
| W1.2 | F2 bounded-timeout wrapper | adg_sqlite service layer | hang on reopen | ~2k | 🔲 TODO |
| W2.1 | F4 idempotent reopen | adg_sqlite connection pool | double-open | ~2k | 🔲 TODO |
| W2.2 | F5 close/reopen race guard | adg_sqlite connection pool | corruption risk | ~2k | 🔲 TODO |

---

## Execution Plan

Each phase: diagnose → minimal upstream fix → regression test. Details filled in on execution start.

---

## Success Criteria

- [ ] All 4 F* items reach Done in Wave/Phase
- [ ] Regression tests land under `tests/unit/adg/`
- [ ] `adg_health` returns green post-patch under stress
