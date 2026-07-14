# C0.3 human-evaluation packet

This package builds the frozen, blinded input packet required to complete the
human portion of resume-graph W6 and W9. It never creates human labels and it
does not make the informational executive-positioning judge release-authoritative.
The full packet is a controlled internal artifact, not a reviewer distribution.

The builder consumes six completed source cases declared in
`target_cases.v1.yaml`. Every source case must contain the 47 frozen allocation
claims across all eleven lanes. The first two slots in each of seven
independently ranked sections carry a bounded retrieval frontier, for 282 claim
items and 84 retrieval queries overall. Every query carries all candidates in
the allocator-bounded finite universe (at most 64), deterministically shuffled
with rank and selection hidden. Human relevance labels therefore cover the
entire denominator used for Recall@1/3/5/10 and nDCG; a system-selected top-K
pool can never grade itself. The sealed mapping preserves every original rank
and the selected candidate, with exact candidate conservation.
When W9 is requested, every case must also carry baseline and hardened
whole-resume text.

The builder emits separate self-contained reviewer-cohort roots:

- `reviewer_proof/claim_items.jsonl`
- `reviewer_retrieval/retrieval_queries.jsonl`
- `reviewer_w9/w9_blind_pairs.jsonl` only when W9 is explicitly ready

Each root has its own `reviewer_manifest.v1.json`, `SHA256SUMS`, instructions,
one applicable rubric, schemas, and digest tool. Send a reviewer only the files
listed by one cohort manifest. Proof and retrieval reviewers must be disjoint;
W9 later uses a third cohort. Reviewer-visible IDs are opaque and lane-specific,
reviewer records omit case/claim-unit join keys, and the retrieval objective is
independent of the selected claim text.

Never publish the full packet, source bundle, `sealed_internal/`, or any cohort
distribution in a reviewer-accessible pull request, repository, issue, or shared
artifact. Keep them in controlled storage and hand off each cohort archive
separately. Code review may contain only implementation, schemas, digest
receipts, and non-sensitive aggregate counts. Files below `sealed_internal/`
contain identity or variant mappings and must never be distributed. Reviewer
payloads omit ranks, selections, raw/model scores, system verdicts, and other
reviewers' labels.

The public target manifest intentionally contains no retrieval-split labels.
During controlled packet construction, the secret blinding nonce drives a
domain-separated HMAC assignment with exactly one calibration and one holdout
case per target profile. Only sealed mappings carry those assignments; the
controller manifest carries an opaque commitment. No reviewer cohort receives
retrieval/proof split assignments or the proof-split salt. Proof calibration
uses a separate deterministic `proof_split`, grouped by an immutable
binding-only `proof_split_group_digest`. Paraphrases grounded in the same
skill/fact/metric path therefore cannot cross calibration and holdout. The
separate claim-plus-binding `proof_identity_digest` remains the unit for
claim-level deduplication and metric math. The sealed export emits both fields
and keeps `split` as a `proof_split` compatibility alias.

Freeze the six real allocator cases from a clean checkout, then build and
validate the unlabeled W6 packet:

```bash
python -m apps_rg.evals.c03_human_eval freeze-source \
  --source-commit-sha "$(git rev-parse HEAD)" \
  --out /path/to/source_bundle.v1.json \
  --receipt-out /controlled/receipts/source_freeze_receipt.v1.json
python -m apps_rg.evals.c03_human_eval readiness \
  --source-bundle /path/to/source_bundle.v1.json \
  --freeze-receipt /controlled/receipts/source_freeze_receipt.v1.json \
  --expected-freeze-receipt-digest "$TRUSTED_FREEZE_RECEIPT_DIGEST" \
  --blinding-nonce-file /controlled/secrets/c03_blinding_nonce.hex
python -m apps_rg.evals.c03_human_eval build \
  --source-bundle /path/to/source_bundle.v1.json \
  --freeze-receipt /controlled/receipts/source_freeze_receipt.v1.json \
  --expected-freeze-receipt-digest "$TRUSTED_FREEZE_RECEIPT_DIGEST" \
  --blinding-nonce-file /controlled/secrets/c03_blinding_nonce.hex \
  --out /path/to/c03_resume_graph_v1
python -m apps_rg.evals.c03_human_eval validate \
  --packet /path/to/c03_resume_graph_v1 \
  --phase prelabel \
  --expected-freeze-receipt-digest "$TRUSTED_FREEZE_RECEIPT_DIGEST"
python -m apps_rg.evals.c03_human_eval seal-prelabel \
  --packet /path/to/c03_resume_graph_v1 \
  --receipt-out /controlled/receipts/c03_prelabel_packet_receipt.v1.json \
  --expected-freeze-receipt-digest "$TRUSTED_FREEZE_RECEIPT_DIGEST"
```

`freeze-source` refuses a dirty checkout or a source SHA different from `HEAD`.
It emits a receipt binding the exact source bytes and canonical content to the
source commit, target manifest, graph digest, and policy digest. Record its
`source_freeze_receipt_digest` in the evaluation owner's trusted approval
channel; do not derive the expected value from the packet being validated.
Official `readiness`, `build`, `validate`, and `export` fail closed without that
caller-supplied pin. In-memory/fabricated fixtures are explicitly test-only and
can never receive official `PASS`.
Before distributing anything for review, pin `packet_manifest.json` through
`seal-prelabel` and preserve its SHA-256 in the evaluation owner's out-of-band
approval channel. Completed validation and export require that pre-review pin;
a post-label packet cannot choose a different split salt or manifest and
authorize itself.
The blinding nonce file must be owner-only (mode `0600` or stricter), must not be
a symlink, and must contain exactly 64 lowercase hex characters from a
cryptographically secure 256-bit secret. Never pass the nonce as a CLI value,
commit it, publish it, or distribute it to reviewers. The packet exposes only a
one-way commitment in controlled top-level metadata; reviewer pseudonyms and
candidate order use domain-separated HMAC-SHA-256. Add `--require-w9` to `build`
and validation only after all six real baseline and hardened resume pairs exist.

Validate returned human labels and adjudications:

```bash
python -m apps_rg.evals.c03_human_eval validate \
  --packet /path/to/c03_resume_graph_v1 \
  --phase completed \
  --labels-dir /path/to/returned_labels \
  --expected-freeze-receipt-digest "$TRUSTED_FREEZE_RECEIPT_DIGEST" \
  --expected-prelabel-manifest-sha256 "$TRUSTED_PRELABEL_MANIFEST_SHA256" \
  --human-review-authority-receipt /controlled/receipts/human_review_authority.v1.json \
  --expected-human-review-authority-receipt-sha256 "$TRUSTED_HUMAN_AUTHORITY_SHA256"
```

Reviewer returns are named `claim_reviews.jsonl`, `retrieval_reviews.jsonl`,
optional `w9_reviews.jsonl`, and `adjudications.jsonl`. The included standalone
`seal_records.py` in each cohort root fills and verifies their canonical
`record_digest` values without accessing sealed mappings.

Completed validation requires two distinct human reviewers for every claim,
retrieval query, and W9 pair, plus one adjudication receipt per item. Synthetic,
model, agent, judge, bot, or automated reviewer identities are rejected.
`UNKNOWN` is never accepted as a completed label or a passing result.
The owner-only human-review authority receipt is an additional external trust
root: it binds the prelabel packet, cohort manifests, approved roster,
assignments, qualifications, issuer, and approval. Reviewer identity strings or
self-authored label files alone can never establish official authority.
Every retrieval review and adjudication must label every blinded candidate in
the declared finite universe. Missing, duplicate, or extra candidate labels
fail validation, so official provenance can never coexist with partial-pool
Recall@10 evidence.

The identity-grouped proof holdout and case-grouped retrieval holdout are W6
offline evaluation partitions. They do not execute or promote the separate
release-only holdout, which remains gated by `APPS_EVAL_RELEASE_GATE`.
