---
status: Archived
do_not_execute: true
memorialized: true
source_surface: docs_reports_plans
source_key: docs-reports
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\docs\\reports\\plans\\rca-h5-system-learning-confidence-engine.md'
original_relative_path: 'rca-h5-system-learning-confidence-engine.md'
source_sha256: 80466b1decf000f3f545004e48f8e88c05cf1319f0674a1c558228ef4e3235cc
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# RCA — H5: `system_learning/confidence/engine.py` Is a 6th Confidence Surface

**Plan reference:** `.windsurf/plans/routing-followups-7a2c91.md` (Phase F3.4)
**Parent gap:** `.windsurf/plans/routing-unification-qwen-abe735.md` §6 H5
**Status:** RCA only — parent plan §9 NON-GOAL; code change requires dedicated plan
**Date:** 2026-04-21

---

## 1. Observed State

File: `@c:\Git\Agentic-Workflow\system_learning\confidence\engine.py:1-20`

Duplicates the healing `ConfidenceScore` type and threshold:

```python
# Line 6:
CONFIDENCE_THRESHOLD = 0.8

# Lines 9-14:
class ConfidenceScore:
    """Placeholder confidence score type for test compatibility."""
    def __init__(self, value=0.0, level="LOW"):
        self.value = value
        self.level = level

# Lines 17-19:
def calculate_confidence():
    """Placeholder calculate confidence function for test compatibility."""
    return 0.0
```

The comment "Placeholder ... for test compatibility" indicates this is a **shim surface**, not an authoritative implementation. But it coexists with 5 other confidence surfaces documented in the parent plan analysis:

1. `agentic_core.L2_execution.healers.confidence_scorer.ConfidenceScore` (Wave 2 canonical)
2. `ops_scripts.dev_tools.L0_routing_scripts._ssot_types.ConfidenceScore` (Wave 3 deprecated)
3. `tools/routing/calibrate_thresholds.py` (Wave 6 — uses confidence values, no class)
4. `heal_classifier/HealClassifierModel` (ML-side, shadow mode)
5. `consensus_validator.MAJORITY_THRESHOLD = 0.66` (consensus, not heal — H4)
6. **This file: `system_learning/confidence/engine.py`** — 6th surface

## 2. Why This Is a Parent Plan NON-GOAL

Parent plan §9 explicitly states:

> Not touching `consensus_validator.py` (H4) or `system_learning/confidence/engine.py` (H5)

Reason: `system_learning/` is the meta-learning subsystem — it learns **about** healing outcomes to improve future policies. Unifying the L2 healer's runtime `ConfidenceScore` with the meta-learning engine's historical confidence type risks:

- Coupling runtime hot path to offline analysis types
- Breaking the layered tenant boundary (L2 healer should not import from `system_learning/`)
- Cross-contaminating ML training with runtime decision logic

## 3. Observed Evidence of Shim Status

The file header comment and the `"""Placeholder ... for test compatibility."""` docstrings strongly suggest these symbols exist **only** to satisfy legacy test imports. Real logic likely lives below line 22 (not inspected in this RCA).

An ADG fan-in query (deferred to plan execution) should confirm:
- Who imports `system_learning.confidence.engine.ConfidenceScore`?
- Is it test-only, or does it leak into production hot path?

If test-only: collapse the shim with aliases to `L2_execution.healers.confidence_scorer.ConfidenceScore`.
If production usage: separate parent plan required — see §4.

## 4. Recommended Fix (dedicated plan required)

A **meta-learning confidence audit plan** would:

1. **ADG fan-in scan** — `adg_edge_fanin(tgt_id=<system_learning.confidence.engine.ConfidenceScore>)` to enumerate consumers
2. **Classify consumers** — test-only vs production path
3. **Decide: shim-alias vs full unify** — guided by consumer analysis
4. **Preserve L2↔system_learning separation** — do not introduce cross-layer dependency
5. **Document decision as ADR** — what the 6 surfaces mean and why unification is scoped as it is

Estimated size: 10k tokens. Separate parent plan required per §9.

## 5. Next Action

**Do not execute** without explicit authorization to waive parent plan §9 non-goal. Open `.windsurf/plans/meta-learning-confidence-audit-<hash>.md` when scheduled; link this RCA from §1 of that plan.

## 6. Provenance

ADG Provenance: backend=sqlite (direct file read; fan-in query deferred to execution plan)
Constitutional compliance: §9 respected — no code changes proposed here; parent plan non-goal preserved.
