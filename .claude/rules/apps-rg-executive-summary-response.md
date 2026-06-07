
# Executive Summary — Default Response Shape

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
