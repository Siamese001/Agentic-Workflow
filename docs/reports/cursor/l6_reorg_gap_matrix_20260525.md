# L6 Reorganization — Gap Matrix (Baseline)

**Date:** 2026-05-25  
**Plan:** [l6-repo-reorganization-mental-model-c4e8f2.md](../../.cursor/plans/l6-repo-reorganization-mental-model-c4e8f2.md)  
**SSOT:** [L6_mental_model.md](../../reference/_notes/L6_mental_model.md)

---

## Executive Summary

The repo already **declares** L6 correctly via in-tree markers and `LAYER.md`, but **physical layout**, **ADG tagging**, and **passive/active boundaries** still drift from the mental model. Reorganization should be **governance-first** (W1), then **docs/markers** (W2), then **optional structure** (W3–W4), and **rename last** (W5).

---

## Two-Surface Inventory

| Surface | Path | Module count (approx) | Mental-model match |
|---------|------|----------------------:|--------------------|
| Passive | `agentic_core/L6_observability/` | ~119 files | **Partial** — extra `promotion/`, root-level promotion modules |
| Active | `system_learning/` | ~302 files | **Partial** — correct root location (documented drift); 8 dirs without chapter `__init__.py` |

**Alias:** `agentic_core/L6_system_learning` re-exports `system_learning` (W2 of non-invasive plan — landed).

---

## Gap Table

| ID | Gap | Evidence | Target wave |
|----|-----|----------|-------------|
| G1 | 292 ADG modules untagged `layer=L6` | Resolved W1 fail-closed — see [l6_w1_gate_receipt_20260525.json](l6_w1_gate_receipt_20260525.json) | **W1 DONE** |
| G2 | 2 observer-law violations | TYPE_CHECKING scope fix in observer-law gate (W1) | **W1 DONE** |
| G3 | 8 subpackages missing `__l6_chapter__` | `adg`, `config`, `ml_integration`, `monitoring`, `policy`, `runtime`, `state`, `telemetry` | **W2 DONE** |
| G4 | `engines/` is cross-chapter flat bucket | `__l6_chapter__` empty on `engines/__init__.py` | W3 or doc-only map |
| G5 | `L6_observability/promotion/` not in mental model | Mapped W4 — defer move D1; see [l6_w4_passive_drift_20260525.md](l6_w4_passive_drift_20260525.md) | **W4 DONE** (deferred) |
| G6 | Eval overlap passive vs active | Three-surface map in W4 §3; consolidation deferred D2 | **W4 DONE** (deferred) |
| G7 | Doc folder name lag | Renamed to `06_L6_Observability_and_System_Learning/` | **W2 DONE** |
| G8 | Physical rename not done | Resolved W5 — canonical `agentic_core/L6_system_learning/` | **W5 DONE** (2026-05-25) |
| G0 | W3+W5 unconstrained (plan defect) | Risk of double-reorg | **W0.2 hard gate** (fixed in plan) |

---

## Chapter Marker Audit (`system_learning/`)

| Package | `__l6_chapter__` | Mental-model chapter |
|---------|------------------|----------------------|
| adapters | 06.1 | 06.1 Ingest |
| ports | 06.1 | 06.1 |
| buses | (empty) | 06.1 |
| raw | 06.1 | 06.1 |
| runtime_adg | (empty) | 06.1 |
| **adg** | **missing init** | 06.1 |
| **telemetry** | **missing init** | 06.1 |
| invariants | 06.2 | 06.2 Observer |
| enforcement | 06.2 | 06.2 |
| constraints | 06.2 | 06.2 |
| validators | 06.2 | 06.2 |
| **policy** | **missing init** | 06.2 |
| engines | (empty) | 06.3 / 06.6 / 06.7 / 06.8 (split) |
| rubrics | (empty) | 06.3 |
| correlation | 06.3 | 06.3 |
| fingerprinting | 06.3 | 06.3 |
| golden | 06.4 | 06.4 Calibration |
| provenance | 06.4 | 06.4 |
| meta_learning | 06.5 | 06.5 Fusion |
| embedding | 06.5 | 06.5 |
| **ml_integration** | **missing init** | 06.5 |
| confidence | (empty) | 06.5 |
| arbitration | 06.5 | 06.5 |
| pipelines | 06.6 | 06.6 Proposals |
| output | 06.6 | 06.6 |
| scripts | 06.7 | 06.7 Promotion |
| **state** | **missing init** | 06.7 |
| **monitoring** | **missing init** | 06.8 KPIs |
| snapshots | 06.8 | 06.8 |
| memory | 06.9 | 06.9 Memory |
| stores | 06.9 | 06.9 |
| types, logs, runtime, config | cross-cutting | per mental model |

---

## Passive Surface Drift (`L6_observability/`)

**In mental model:** `runtime_trace`, `semconv`, `execution`, `reasoning`, `shadow_eval`, `enforcement`, `types`, `utils`

**On disk but not in tree:**

- `promotion/` — promotion consumer semantics; likely belongs under active 06.7 or documented handoff
- Root modules: `promotion_gates.py`, `flywheel_promoter.py`, `otel_runtime_ingest.py`, etc. — classify in W4

---

## Recommended Execution Order (hardened 2026-05-25)

**W0.2 is a hard architecture gate** — must select exactly one path before W3 or W5:

| Path | W3 chapter wrappers | W5 physical rename |
|------|--------------------|--------------------|
| `PATH_KEEP_ROOT` | Allowed (with non-cosmetic proof) | **Out of scope** for this plan |
| `PATH_RENAME_CANONICAL` | **Skipped** | Required after W1 fail-closed + W5 preflight |

1. **W0** — Baseline + W0.2 path lock (Author-Gate)
2. **W1** — ADG + observer law fail-closed
3. **W2** — Docs + markers (path-agnostic)
4. **W3 OR W5** — mutually exclusive per W0.2 (never both without zero-loss migration)
5. **W4** — Passive drift map
6. **W6** — Optional gravity after canonical root stable

Plan detail: [l6-repo-reorganization-mental-model-c4e8f2.md](../../.cursor/plans/l6-repo-reorganization-mental-model-c4e8f2.md) § Single-Root Architecture Invariant + § PATH-AWARE CERTIFICATION RULE.

**Stale-cert risk (GAP-0b):** Under `PATH_RENAME_CANONICAL`, W1 pre-rename passes are provisional; final proof = W1.5 after W5.3 + stale-cert `rg` gate.

**W0.2 locked (2026-05-25):** `PATH_RENAME_CANONICAL` — sibling `L6_observability` + `L6_system_learning`; W3 removed. Receipt: [l6_w0_architecture_decision_20260525.md](l6_w0_architecture_decision_20260525.md).

---

## Child Plans

- [l6-alignment-deferred-scope-c5e8a7.md](../../../.cursor/plans/_archive/2026-05/l6-alignment-deferred-scope-c5e8a7.md) — D1/D2/D3/D5
- [l6-folder-rename-doctrinal-alignment-a8c4e2.md](../../../.cursor/plans/_archive/2026-05/l6-folder-rename-doctrinal-alignment-a8c4e2.md) — W5 body
- [l6-gravity-hybrid-7c4e2a.md](../../../.cursor/plans/_archive/2026-05/l6-gravity-hybrid-7c4e2a.md) — W6 optional
