# W9 Boundary Repair — Quarantine Notice

## Status: BOUNDARY CLOSED (as of W2R — 2026-05-11)

Plan: `apps-research-w9-judge-boundary-closure-c21951`

---

## A. Governance Boundary

`apps_research` is **ingress-only** for judge execution. Judge execution authority is
**core-only** (`agentic_core/evaluation/judges/`).

Apps_research judge files must NOT contain:
- Local scoring or heuristic logic
- Provider calls or model invocations
- Routing, retrieval, or prompt assembly
- Execution authority, write authority, or learning authority
- Literal `def evaluate(` definitions
- Literal `def grade(` definitions

All executable judge logic must live in `agentic_core/evaluation/judges/`.
Apps own config only: rubrics, profiles, thresholds, and grader rosters.

---

## B. What W1 Fixed

**File:** `agentic_core/evaluation/judges/llm_judge_gateway.py`

**Fix:** Renamed `LLMJudgeMode` → `LLMGatewayMode` (1-line rename).

**Impact:** This NameError blocked collection of all W9 boundary tests. After W1, the
W9 boundary test suite collected and ran successfully.

---

## C. What W2 Fixed

**Files:** All 9 `apps_research/engines/judges/*.py` files (excluding `__init__.py`).

**Fix:** Removed callable `def evaluate(` and `def grade(` definitions from all judge
files. Each file was reduced to a boundary stub: constants (`IS_STUB=True`,
`IS_CALIBRATED`, `GRADER_ID`) and a metadata-only class. No scoring logic remains.

**Boundary rule enforced:**
No literal `def evaluate(` or `def grade(` may appear in any file under
`apps_research/engines/judges/*.py`.

**Files stubbed by W2:**
- `base.py` — removed `ABC` base class and `@abstractmethod evaluate()`
- `briefing_injection_judge.py` — `IS_STUB=True`, no callable logic
- `cache_compatibility_judge.py` — `IS_STUB=True`, no callable logic
- `citation_quality_judge.py` — `IS_STUB=True`, no callable logic
- `claim_support_judge.py` — `IS_STUB=True`, no callable logic
- `contradiction_resolution_judge.py` — `IS_STUB=True`, no callable logic
- `downstream_relevance_judge.py` — `IS_STUB=True`, no callable logic
- `source_authority_judge.py` — `IS_STUB=True`, no callable logic

**Note:** `coverage_depth_judge.py` was also stubbed in W2 (`IS_STUB=True`, no `grade`).
This caused 6 spine alignment regressions in `TestCoverageDepthJudge`, which were repaired
by W2R without test edits (see Section D).

---

## D. What W2R Fixed

**File:** `apps_research/engines/judges/coverage_depth_judge.py` (special case)

**Problem:** `TestCoverageDepthJudge` spine alignment tests (authored by plan
`apps-research-deferred-scope-2-f3a9c1` DS-D) assert:
- `IS_STUB is False` — the judge is live and calibrated
- `grade` is importable and callable
- `grade(dim, run_ctx)` returns correct scores for full/empty/FORENSIC coverage inputs

These assertions are incompatible with a hollow `IS_STUB=True` stub, but the W9
boundary test forbids any literal `def grade(` inside `apps_research`.

**Solution:** The run_context coverage-depth scoring implementation was added to core:

```
agentic_core/evaluation/judges/deterministic_graders.py
```

as `grade_coverage_depth_run_context`. The `coverage_depth_judge.py` file was then
rewritten as a **core-backed compatibility facade**:

```python
from agentic_core.evaluation.judges.deterministic_graders import (
    grade_coverage_depth_run_context as grade,
)
IS_STUB: bool = False  # core-backed, not a hollow stub
```

**Key invariants:**
- No `def grade(` literal in `coverage_depth_judge.py` (import alias, not definition)
- No local scoring logic in `apps_research`
- `IS_STUB=False` is acceptable only because execution delegates entirely to core
- Tests were not modified

---

## E. Verified Test State

After W1, W2, and W2R — verified 2026-05-11:

| Suite | Command | Result |
|---|---|---|
| W9 boundary | `pytest tests/_apps_contract/test_w9_boundary_judge_execution.py -q` | **25/25 passed** |
| Spine alignment | `pytest tests/_apps_contract/test_apps_research_spine_alignment.py -q` | **110/110 passed** |

**Tests were not modified** at any point during W1, W2, or W2R.

Raw boundary scan (no `def evaluate(` or `def grade(` in judge files):
```
python -c "from pathlib import Path; ..."  →  [] exit 0
```

---

## F. Future Maintainer Rules

1. **Do not add `def evaluate(` to any file under `apps_research/engines/judges/`.**
2. **Do not add `def grade(` to any file under `apps_research/engines/judges/`.**
3. Do not move scoring logic back into `apps_research`.
4. If a legacy app-level import is required, expose a core-backed alias or facade only
   (no local execution logic). Pattern: `from agentic_core... import <symbol> as grade`.
5. If new judge behavior is needed, implement it in `agentic_core/evaluation/judges/`,
   then expose only compatibility references in `apps_research` if required.
6. `coverage_depth_judge.py` is a compatibility facade. Its `grade` symbol must always
   resolve to a core-owned callable in `deterministic_graders.py`. Any scoring changes
   must be made in `grade_coverage_depth_run_context` in core, not in `apps_research`.
7. Any durable learning or grader promotion must follow the L6 future-run proposal →
   UWG → L4 path. Never direct `apps_research` mutation.

---

## G. File Status Reference

| File | Type | IS_STUB | Callable grade? | Notes |
|---|---|---|---|---|
| `base.py` | Infrastructure | — | No | ABC removed; metadata/dataclass only |
| `briefing_injection_judge.py` | Boundary stub | `True` | No | W9 closed |
| `cache_compatibility_judge.py` | Boundary stub | `True` | No | W9 closed |
| `citation_quality_judge.py` | Boundary stub | `True` | No | W9 closed |
| `claim_support_judge.py` | Boundary stub | `True` | No | W9 closed |
| `contradiction_resolution_judge.py` | Boundary stub | `True` | No | W9 closed |
| `coverage_depth_judge.py` | **Core-backed facade** | `False` | Yes (core alias) | `grade = grade_coverage_depth_run_context` from `deterministic_graders.py` |
| `downstream_relevance_judge.py` | Boundary stub | `True` | No | W9 closed |
| `source_authority_judge.py` | Boundary stub | `True` | No | W9 closed |

---

## H. Core Infrastructure (Canonical Execution Location)

| File | Purpose |
|---|---|
| `agentic_core/evaluation/judges/deterministic_graders.py` | Core-owned deterministic graders including `grade_coverage_depth_run_context` |
| `agentic_core/evaluation/judges/llm_judge_gateway.py` | Core-owned LLM gateway (PROFILE_ONLY, fixed W1) |
| `agentic_core/evaluation/judges/gate_evidence_mapper.py` | Core-owned gate mapping |

---

Date closed: 2026-05-11
Waves: W1 (NameError fix) · W2 (stub closure) · W2R (coverage_depth core-backed facade)
Receipts:
- `artifacts/apps_research/w9_judge_boundary_closure/w1_nameerror_fix_receipt.json`
- `artifacts/apps_research/w9_judge_boundary_closure/w2_judge_stub_receipt.json`
- `artifacts/apps_research/w9_judge_boundary_closure/w2r_regression_repair_receipt.json`
- `artifacts/apps_research/w9_judge_boundary_closure/w3_quarantine_notice_receipt.json`
