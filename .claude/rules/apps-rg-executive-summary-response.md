
# Executive Summary — Default Response Shape

> **General principle (always-on):** the business-first/technical-kept standard — lead with the outcome in plain English, keep precise terms but gloss each on first use — applies to **all** explanatory prose now, not just apps_rg (SSOT: `CLAUDE.md` § Explanation style). The **post-turn `STATUS` floor / `### ⬛ Turn Receipt`** is the sole carve-out (evidence, never simplified). This file is the **stricter apps_rg instance** of that principle for the `executive_summary` deliverable (the exact-3-sentence / ~12-year-old shape below).

> **Precedence (canonical SSOT — `001-runtime-seam-execution.md` § Canonical post-turn output):** this layman-lead shape is a **simplify / translate** standard for *how the §37 Outcome frame's RCA + next-step content reads* for this deliverable (plain English first, jargon later). It layers on the response floor / Outcome frame; it never replaces them. (For the artifact-derived evidence table, see the sibling `apps-rg-post-run-summary.md`.)

After every `python -m apps_rg --section executive_summary` run (or when explaining one), use this order:

## 1. Layman lead (required — exactly 3 sentences)

- Reading level: ~12 years old. Short sentences. No gate IDs, no digests, no file paths.
- Cover: (a) did the run finish and save outputs, (b) targeting parity in plain terms (writer and grader saw the same briefing slice), (c) pass/fail in human terms and the main reason if not certified.
- Do **not** use jargon: X3, X2, digest, U0, parity_match — say "writer," "grader," "shortened notes," "checklist," "approved / not approved."

## 2. Technical detail (below the lead)

- Artifact dir as markdown link.
- Small table: parity, generation/judge briefing chars, X3 code, judges pass/soft-fail, exit code.
- Optional proof-contract block (`STATUS`, `ARTIFACTS`, etc.) when repo-work rules apply.
- Renderer output or row-level gates only when the user needs depth — never instead of the 3-sentence lead.

## Forbidden

- Starting with `X3_BLOCK`, digest hashes, or a gate failure list.
- Skipping the layman block because "the user is technical."
- More than 3 sentences in the layman block (move extra context to Technical detail).

## SSOT

Operator examples: [executive_summary_operator_guide.md](docs/apps_rg/executive_summary_operator_guide.md) § Default run summary.
