data/
│
├── raw/                               # L1 ingestion – untouched source files
│   ├── transcripts/
│   │   ├── 2025_Q1_call.pkl
│   │   ├── 2025_Q2_call.pkl
│   │   └── …
│   ├── web_scrapes/
│   │   ├── yahoo_finance/
│   │   ├── sec_filings/
│   │   └── …
│   ├── uploads/
│   │   ├── manual_user_docs/
│   │   └── …
│   └── external_sources/
│       ├── hf_downloads/
│       └── …
│
├── interim/                           # L2 transformation – chunked, cleaned, structured
│   ├── chunked/
│   │   ├── amd/
│   │   ├── nvda/
│   │   └── …
│   ├── semantic_embeddings/
│   │   ├── text-embedding-3-small/
│   │   └── text-embedding-3-large/
│   ├── temporal_events/
│   │   ├── raw_events/
│   │   ├── validated_events/
│   │   └── …
│   └── extraction_outputs/
│       ├── statements/
│       ├── triplets/
│       └── entities/
│
├── processed/                         # L3 orchestration – finalized, canonical datasets
│   ├── canonical_entities/
│   │   ├── organizations.json
│   │   ├── people.json
│   │   └── products.json
│   ├── knowledge_graph/
│   │   ├── graph_edges.parquet
│   │   ├── graph_nodes.parquet
│   │   └── neo4j_export/
│   ├── temporal_kg/
│   │   ├── events_clean.parquet
│   │   └── invalidations.parquet
│   ├── retrieval_indexes/
│   │   ├── bm25/
│   │   ├── dense/
│   │   ├── hybrid/
│   │   └── rr_fusion/
│   └── model_ready/
│       ├── train_dataset/
│       ├── eval_dataset/
│       └── …
│
├── reference/                         # L4 state: static lookup tables and dictionaries
│   ├── predicate_definitions.yaml
│   ├── entity_type_ontology.yaml
│   ├── temporal_labeling_rules.yaml
│   ├── schema_mappings/
│   └── glossaries/
│
└── logs/                              # L5 safety + observability
    ├── ingestion/
    ├── extraction/
    ├── invalidation/
    ├── retrieval/
    └── errors/


### Directory Structure

```plaintext
├── agentic_core.md
├── apps.md
├── config.md
├── data.md
├── observability.md
├── prompt_governance.md
├── runtime.md
├── schemas.md
├── scripts.md
├── tests.md
└── update_markdown_trees.py
```
