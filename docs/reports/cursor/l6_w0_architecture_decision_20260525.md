# L6 W0.2 Architecture Decision Receipt

**Date:** 2026-05-25  
**Plan:** [l6-repo-reorganization-mental-model-c4e8f2.md](../../.cursor/plans/l6-repo-reorganization-mental-model-c4e8f2.md)

---

## Decision

```
DECISION_CAPTURED: type=architecture_choice, repo_area=system_learning, selected=PATH_RENAME_CANONICAL, outcome=executed, authorized_by=user, confidence=0.74
```

**Rationale (user-confirmed purist layout):** Two **sibling** surfaces under `agentic_core/` — passive `L6_observability/` unchanged; active `system_learning/` → `agentic_core/L6_system_learning/` via `git mv`. **Not** nested under a renamed `L6_shadow_learning`. Doctrinal docs umbrella → `06_L6_Observability_and_System_Learning/`.

---

## Locked target layout

```text
agentic_core/
├── L6_observability/          # passive — keep name
│   runtime_trace | semconv | execution | reasoning
│   shadow_eval | enforcement | types | utils
└── L6_system_learning/       # active — git mv from repo root (W5)
    adapters | engines | meta_learning | …  (06.1–06.9)

docs/reference/
└── 06_L6_Observability_and_System_Learning/   # W2 doc rename
```

---

## Wave enablement

| Wave | Status after W0.2 |
|------|-------------------|
| W1 | **ALLOWED** — pre-rename; `proof_phase=pre_rename`, provisional |
| W2 | **ALLOWED** — path-conditional; no final canonical claims for root `system_learning/` |
| W3 | **REMOVED** from this plan |
| W4 | **ALLOWED** |
| W5 | **ALLOWED** after W1 fail-closed + W5.0 preflight + Author-Gate |
| W6 | After W5.3 final cert |

---

## Single-root invariant (post-W5.3)

| Role | Path |
|------|------|
| Canonical active root | `agentic_core/L6_system_learning/` |
| Canonical passive root | `agentic_core/L6_observability/` |
| Root `system_learning/` | **Removed** (temporary shim only during W5.1–W5.2) |
| `agentic_core.L6_system_learning` | Canonical import path after W5.3 |

---

## Baseline evidence (W0.1)

- [l6_reorg_gap_matrix_20260525.md](l6_reorg_gap_matrix_20260525.md)
- [l6_import_blast_radius_baseline_20260525.md](l6_import_blast_radius_baseline_20260525.md) — 329 files, 732 import lines

---

## Next wave

**W1** — ADG `__layer__` SSOT + observer-law remediation + fail-closed promotion (Author-Gate required per plan § Authorization Law). Final governance certification for this path is **W1.5 after W5.3**, not W1 alone.
