---
plan_id: apps-architect-deferred-scope-2-c9d4e2
plan_type: infra
parent_plan: apps-architect-deferred-scope-b8e3f1
grandparent_plan: apps-architect-pattern-hardening-d7e4f9
---

# apps_architect — Deferred Scope L2 (Deep Backlog)

Collects the 4 items that were out-of-scope even from the deferred plan `apps-architect-deferred-scope-b8e3f1` (Completed 2026-05-07). **Do not implement** — capture-only registration.

---

## Context

- **Situation** — `apps_architect` is now a fully hardened R3_grounded_read app: 28 Python modules, 18 tests, 12 deferred items implemented across 5 waves. The parent deferred plan closed all P1-P3 gaps.

- **Complication** — 4 items were explicitly excluded even from the deferred scope as too ambitious for the current architecture. These represent future research directions, not immediate hardening needs.

- **Question** — What long-horizon capabilities would elevate apps_architect from a repo-hardening engine to a fully autonomous architecture governance system?

- **Answer** — This L2 deferred plan captures the 4 excluded items as a deep backlog for future consideration. No implementation timeline.

---

## Deep Backlog Inventory

| ID | Item | Rationale for deferral | Est. Tokens |
|----|------|------------------------|-------------|
| DL-1 | Real-time enforcement with <100ms latency SLA | Requires event-streaming infra (Kafka/NATS), not poll-based | ~15K |
| DL-2 | Cross-organization pattern sharing | Requires auth federation, tenant isolation, pattern licensing | ~12K |
| DL-3 | ML-based pattern discovery | Requires training data pipeline, model versioning, human-in-the-loop validation | ~20K |
| DL-4 | Pattern rollback/undo mechanism | Requires pattern provenance DAG, inverse migrations, state snapshots | ~10K |

**Total: ~57K tokens across 4 deep-backlog items**

---

## Out Of Scope (even from L2 deferred)

- ❌ Fully autonomous enforcement (no human in the loop)
- ❌ Pattern marketplace / exchange
- ❌ Real-time cross-repo pattern synchronization

---

## Rules

1. **Do not implement** — capture-only
2. **All parent/grandparent plans must be Completed** before any DL item starts
3. **DL-1 requires infra provisioning** (event bus, not just code)
4. **DL-3 requires labeled training data** (not just model code)

---

## References

- Grandparent: `.cursor/plans/apps-architect-pattern-hardening-d7e4f9.md` (Completed)
- Parent: `.cursor/plans/apps-architect-deferred-scope-b8e3f1.md` (Completed)
- `apps_research/` — Canonical R3_grounded_read reference
- `.cursor/rules/adg-canonical-invariants.md` — ADG doctrine

---

DEFERRED_SCOPE: plan=apps-architect-deferred-scope-2-c9d4e2 parent=apps-architect-deferred-scope-b8e3f1 items=4 est_tokens=57K
