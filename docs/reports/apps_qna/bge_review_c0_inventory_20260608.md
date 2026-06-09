# apps_qna C0 Flat Index Inventory - BGE Review

Date: 2026-06-08
Branch: `codex/BGE-review`
Plan: `bge-review-apps-qna-c0-chroma-migration-f9a3b2`
Wave: W0 inventory and preservation

## Source Artifact

The current `apps_qna` C0 retrieval path reads a flat JSON index from:

`C:/AgenticEmbeddings/indexes/apps_qna_interview_cards`

Observed files:

| File | Size Bytes | SHA-256 |
|---|---:|---|
| `index.json` | 3,560,762 | `ec2439cfeaf3155cf7d7d4497317be5634c90c3994229e2ab17603961bda4671` |
| `manifest.json` | 321 | `28d0a0159f05d31f4227f834c3f2f2f9ba9c98d7d0f20a39df30cb38a25d89c7` |
| `meta.json` | 274 | `4b1ad88a7989843c7b9ef60afff322267ad75c52be31385d66f99e46b5dd1c36` |

Manifest values:

| Field | Value |
|---|---|
| `schema_version` | `1` |
| `embedder_id` | `BAAI/bge-m3` |
| `model_version` | `BAAI/bge-m3` |
| `dims` | `1024` |
| `vector_count` | `110` |
| `sha256_index` | `674edc4ce9a7c6c086881e5c6047a432abc40eaffbcf03717b6c6c1538b817e8` |
| `sha256_meta_canonical` | `d1b9de7e60c0e21ce9c59c670dda27016c9b2d9836d6d0b7b7d0677c11f54667` |

Index structure:

| Field | Value |
|---|---|
| `index_type` | `flat` |
| `distance_metric` | `cosine` |
| vectors observed | `110` |
| unique vector dimensions | `1024` |
| sample IDs | `runtime_root_junior`, `runtime_root_mid`, `runtime_root_senior`, `runtime_root_staff`, `runtime_root_principal` |

## Seed Pack

Seed pack directory:

`C:/AgenticEmbeddings/seed_packs/apps_qna_interview_cards/674edc4ce9a7c6c086881e5c6047a432abc40eaffbcf03717b6c6c1538b817e8`

Observed files:

| File | Size Bytes | SHA-256 |
|---|---:|---|
| `embeddings.f32` | 450,560 | `674edc4ce9a7c6c086881e5c6047a432abc40eaffbcf03717b6c6c1538b817e8` |
| `row_index.jsonl` | 44,292 | `89ea683914b5df17ff24f26234533519774dc28881e5bf8c3c3988bee442d395` |
| `seed_manifest.json` | 551 | `1ab2fd2b75ba8ad81999301b3e3e86873ad99a7a94df921f5004f138fe11654e` |

Preservation note: `manifest.json.sha256_index` matches `seed_packs/.../embeddings.f32`, not the raw `index.json` file hash. W1 migration must validate both the raw JSON and the seed-pack binary before ingesting.

## Target Confirmation

Parent plan `bge-review-apps-qna-cache-init-9a4c2e` is complete. The parent L4 semantic cache substrate is separate from the child C0 retrieval migration:

| Surface | Path | Collection |
|---|---|---|
| Parent L4 semantic cache | `artifacts/cache/l2/chroma` | `l2_semantic_cache` |
| Child C0 canonical retrieval target | `data/cache/chromadb` | `apps_qna_interview_cards` |

The child migration should populate the C0 canonical retrieval target without mutating `C:/AgenticEmbeddings`.

## W0 Recommendation

- Keep `C:/AgenticEmbeddings` intact through W1-W3.
- Treat the flat index as the rollback source until Chroma ingest, read-path migration, and CI gates all pass.
- Do not delete or compact `healing_contexts`; it is separate from `apps_qna_interview_cards`.
- Child W1 should build a deterministic ingest tool that reads the captured flat/seed artifacts and writes `apps_qna_interview_cards` into `data/cache/chromadb`.
