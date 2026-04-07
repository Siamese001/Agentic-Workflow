# Refactor Accelerator — Design Spec (W3.3)

**Status**: Accepted — MVP implementation in W3.4
**Consumes**: ADG SQLite, git log, ruff/pylint output, pytest results

---

## Purpose

The Refactor Accelerator (RA) answers: **"Which files should I refactor next, in what order, and what tests will be affected?"**

It is a read-only analysis tool — it does not modify code. It produces a ranked candidate list with blast radius, test surface, and migration order.

---

## Inputs

| Input | Source | Purpose |
|-------|--------|---------|
| ADG SQLite | `artifacts/adg/adg_indexed_<ts>.sqlite` | Structural topology (fan-in, fan-out, layer, violations) |
| git log | `git log --numstat` | Change frequency per file (churn score) |
| Ruff/Pylint output | `ruff check --output-format=json` | Lint violation count per file |
| pytest results | `artifacts/adg/test_surface_coverage_<ts>.json` | Test coverage edges (covers relation) |

---

## Outputs

### 1. Ranked Candidate List
Every file scored on 4 dimensions, composite score used for ranking:

| Dimension | Formula | Weight |
|-----------|---------|--------|
| **Fan-in** | `direct_fan_in / max_fan_in` | 0.30 — high fan-in = high blast radius |
| **Churn** | `commit_count_90d / max_churn` | 0.25 — frequently changed = high ROI |
| **Violations** | `violation_count / max_violations` | 0.25 — violations = refactor urgency |
| **Lint debt** | `lint_count / max_lint` | 0.20 — lint debt = code quality signal |

Composite: `score = 0.30*fan_in + 0.25*churn + 0.25*violations + 0.20*lint`

### 2. Blast Radius per Candidate
For each top-N candidate: list of modules reachable via `imports`/`calls` fan-in traversal (depth ≤ 3).

### 3. Impacted Tests
For each candidate: test files linked via `covers` relation in ADG.

### 4. Migration Order
Topological sort of candidates using ADG dependency edges — refactor leaves before roots to minimize cascading breakage.

---

## Output Format

```json
{
  "generated_at": "04072026_1900",
  "sqlite_used": "adg_indexed_04072026_1729.sqlite",
  "candidates": [
    {
      "rank": 1,
      "file": "agentic_core/L0_routing/router.py",
      "layer": "L0",
      "score": 0.847,
      "dimensions": {
        "fan_in": 142,
        "churn_90d": 23,
        "violations": 4,
        "lint_count": 17
      },
      "blast_radius": {
        "depth_1": ["agentic_core/L1_planning/planner.py"],
        "total_affected": 38
      },
      "impacted_tests": [
        "tests/unit/test_router.py",
        "tests/integration/test_routing_flow.py"
      ],
      "migration_order": 3
    }
  ],
  "migration_sequence": ["file_A.py", "file_B.py", "file_C.py"]
}
```

---

## CLI Interface

```
python tools/adg/refactor_accelerator.py
python tools/adg/refactor_accelerator.py --top 20
python tools/adg/refactor_accelerator.py --layer L0
python tools/adg/refactor_accelerator.py --mode candidates   # default
python tools/adg/refactor_accelerator.py --mode blast-radius --target agentic_core/L0_routing/router.py
python tools/adg/refactor_accelerator.py --mode migration-order
python tools/adg/refactor_accelerator.py --json              # machine-readable output
python tools/adg/refactor_accelerator.py --sqlite <path>     # explicit SQLite path
```

---

## Scoring Calibration

Weights are tunable via `tools/adg/ra_config.json` (created on first run with defaults).

Fan-in dominates (0.30) because high-centrality modules cause the most downstream breakage — refactoring them yields the highest architectural ROI.

Churn (0.25) identifies files actively being changed — concurrent refactoring reduces merge conflicts.

---

## Constraints

- **Read-only** — RA never modifies code. Output only.
- **ADG-first** — All structural data from SQLite. No grep/text fallback.
- **Offline** — No external API calls.
- **Fast** — Full scan ≤ 10 seconds on 80K node graph.
- **Idempotent** — Same inputs → same output.

---

## Non-Goals

- Automated code transformation (out of scope — RA only ranks)
- Test generation (out of scope — tests are a human concern)
- Merge conflict detection (git responsibility)
- CI integration (Wave 4 concern)
