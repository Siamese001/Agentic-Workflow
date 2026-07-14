# C0.3 human-review instructions

This directory is one isolated reviewer-cohort distribution. Review only the
files listed in its `reviewer_manifest.v1.json`, and verify the included
`SHA256SUMS` before review. Never request or accept the full packet, the source
bundle, files under `sealed_internal/`, or a sibling proof, retrieval, or W9
reviewer distribution. Those materials contain system ranks, selections,
scores, mappings, or cross-lane text that would break blinding.

Proof, retrieval, and W9 review must use separate human cohorts. A reviewer who
has opened one cohort distribution is ineligible to review either of the other
cohort distributions for this packet. Do not publish any cohort distribution in
a reviewer-accessible pull request, repository, issue, or shared artifact; use
the controlled handoff channel designated by the evaluation owner.

This directory contains exactly one item data file and its matching rubric.
Return records conforming to `human_review.v1.schema.json`:

- `claim_items.jsonl` → `proof_label_rubric.v1.yaml`
- `retrieval_queries.jsonl` → `retrieval_label_rubric.v1.yaml`
- `w9_blind_pairs.jsonl` → `w9_resume_coach_rubric.v1.yaml`, when included

Every item requires exactly two independent human reviews from distinct
reviewer identities and label batches. Reviewers must not share labels before
submitting. `UNKNOWN` is not a completed label. W9 reviewers must be qualified
resume coaches whose `qualification_ref` uses `resume-coach://`. Preserve the
opaque item IDs exactly; never try to recover case, claim-unit, system-selection,
rank, or sibling-cohort linkage.

For each retrieval query, review every candidate in the supplied shuffled list.
That list is the complete allocator-bounded finite universe, not a system top-K
sample. Return exactly one final candidate label per `candidate_blind_id`;
missing, duplicate, or additional IDs invalidate the review.

Set `reviewer_identity_ref` to the evaluation owner's verified, stable
`human-reviewer://` roster reference. `reviewer_id_hash` must equal lowercase
SHA-256 over the exact UTF-8 bytes of that reference. For a human adjudicator,
bind `adjudicator_id_hash` to `adjudicator_identity_ref` the same way. The
included seal tool fills a missing bound hash and rejects a conflicting one.

After primary review, create one record per item conforming to
`adjudication.v1.schema.json`. Exact agreement may use
`deterministic_consensus`; disagreements require an independent human
adjudicator (and W9 adjudicators require the same resume-coach qualification).

Return only the file applicable to this directory plus `adjudications.jsonl`:

- `claim_reviews.jsonl`
- `retrieval_reviews.jsonl`
- `w9_reviews.jsonl` when W9 pairs are present
- `adjudications.jsonl`

Every returned row needs a canonical `record_digest`. Draft each JSONL without
that field (or with a stale value), then run:

```text
python seal_records.py seal draft.jsonl --out claim_reviews.jsonl
python seal_records.py validate claim_reviews.jsonl
```

Repeat with the exact applicable return filename. `seal_records.py` is
standalone, uses only Python's standard library, and never reads sealed packet
mappings. The digest is SHA-256 over canonical compact JSON with sorted keys,
excluding `record_digest` itself.

Do not add system scores, ranks, selections, predictions, verdicts, other
reviews, or variant identities to reviewer payloads. Return review JSONL files
separately; do not alter the frozen packet or its checksums.
