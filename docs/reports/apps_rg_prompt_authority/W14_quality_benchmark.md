# W14 — Section quality benchmark (design + scaffold only)

**Cursor plan (execution SSOT):** `.cursor/plans/apps-rg-w14-quality-benchmark-f1a9b3.md` — Notion Plans **Slug** matches; row **Status** starts **Not Started** when registered.

## Purpose

Define how to **evaluate resume section quality offline** for generated lanes, without:

- asserting X1D judges as **runtime release** gates,
- running full human scoring in this wave,
- performing large benchmark builds or calibration execution,
- mutating **L6** on the current run (L6 is **future-run learning only**; no current-run mutation).

## Governance boundaries

| Layer | Role in W14 |
|-------|-------------|
| **X2** | Deterministic correctness remains authoritative at runtime (schema, ledger, forbidden inline tags, JD-not-proof, etc.). |
| **X1D** | Soft quality signal only (voice, fit, clarity). **X1D does not approve runtime release.** |
| **Human labels** | Gold / preference labels **calibrate** judges **offline**; labels are not shipped as runtime gates in this design. |
| **L6** | Consumes completed-run packages for **offline** analysis and learning; **no durable write from L2/L3/tools/Exit during the active run** per spine law. |

## Dimensions (scoring rubric axes)

Evaluators (human or offline judge) score each sample on:

1. **Factual support** — claims trace to allowed evidence / ledger (complements X2, does not replace it).
2. **JD fit** — alignment to stated role requirements (soft).
3. **Executive presence** — senior tone appropriate to level (soft).
4. **Concision** — length discipline vs spec (soft).
5. **Specificity** — concrete outcomes vs generic filler (soft).
6. **Seniority signal** — scope/scale language credible for role (soft).
7. **Unsupported claim risk** — likelihood of over-claim vs sources (risk proxy; X2 remains hard gate where coded).
8. **Resume usefulness** — would a hiring manager act on this section (holistic).

## Artifact layout

Scaffold under `apps_rg/evals/section_quality_benchmark/`:

- `README.md` — operator instructions, no fabricated scores.
- `*.schema.json` — JSON Schema for **label rows** (optional fields, comment fields); **no pre-filled numeric scores**.

## Execution phases (future)

1. **Freeze** — prompt_hash / section contract ID / model version per row.
2. **Label** — human or trusted offline model; store separately from runtime gates.
3. **Calibrate** — map X1D dimensions to human agreement; adjust rubrics **offline**.
4. **Report** — correlation tables, error buckets; do not weaken X2.

## Status

**PASS** (design + minimal scaffold only; no benchmark scores created).
