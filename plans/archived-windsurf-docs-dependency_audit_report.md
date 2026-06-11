---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\dependency_audit_report.md'
original_relative_path: 'dependency_audit_report.md'
source_sha256: c634ab27935c442fb17083a5f8869cf73aca642e34519e30ec8ddfe754beaea7
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-02-08'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Dependency Audit Report (v4 — separate scans)

**Generated**: 2026-02-09T03:42:13.423459+00:00
**Scans merged**: dev, runtime, sdks
**Dist packages**: 57
**Buckets**: core=19, dev=1, infra=34, sdks=3
**Phantom/stale internal**: 17

## Bucket Assignment Rule

1. DEV-TOOL dist packages → `dev` (always)
2. Packages appearing ONLY in the `sdks` tagged scan → `sdks`
3. Packages with ≥1 top-level hard import in the `runtime` tagged scan (after `--exclude-subdir` filtering) → `core`
4. Everything else → `infra`

### Repo Shipping Contract

The following directories are **not shipped** as part of the runtime package and are excluded from core classification:

- `tests/` — test suite (dev-only)
- `ops_scripts/` — operational tooling (dev-only)
- `data/` — sample data and SDK wrappers (not shipped)
- `*/scripts/` subdirs within runtime roots — utility/maintenance scripts (invoked manually, not imported at runtime)
- `*/dashboards/` subdirs within runtime roots — observability dashboards (deployed separately)

This contract MUST be enforced via packaging (`[project.packages]` or `find:` directives in setup) and CI. If any excluded path becomes shipped, re-run the runtime scan without that exclusion.

## Core Runtime (required — `pip install -e .`)

| dist package | import name(s) | RT hard | RT excl | RT defer | RT cond | Dev | version |
|---|---|---|---|---|---|---|---|
| PyYAML | yaml | 1 | 2 | 0 | 3 | 1 | >=6.0 |
| aiofiles | aiofiles | 3 | 0 | 0 | 0 | 0 | >=23.0.0 |
| chromadb | chromadb | 1 | 0 | 0 | 1 | 0 | >=0.4.0 |
| duckdb | duckdb | 1 | 0 | 0 | 0 | 0 | >=0.9.0 |
| jinja2 | jinja2 | 1 | 0 | 0 | 1 | 0 | >=3.1.0 |
| libcst | libcst | 3 | 0 | 0 | 0 | 2 | >=1.1.0 |
| networkx | networkx | 3 | 1 | 0 | 1 | 0 | >=3.0 |
| numpy | numpy | 9 | 1 | 0 | 0 | 0 | >=1.24.0 |
| pinecone | pinecone | 1 | 0 | 0 | 5 | 0 | >=5.0.0 |
| psutil | psutil | 1 | 0 | 0 | 2 | 1 | >=5.9.0 |
| pydantic | pydantic, pydantic_core | 71 | 2 | 3 | 1 | 3 | >=2.0.0 |
| pydantic-settings | pydantic_settings | 1 | 0 | 0 | 0 | 0 | >=2.0.0 |
| python-dotenv | dotenv | 1 | 0 | 0 | 4 | 2 | >=1.0.0 |
| rank-bm25 | rank_bm25 | 2 | 0 | 0 | 0 | 0 | >=0.2.0 |
| redis | redis | 4 | 0 | 0 | 5 | 0 | >=5.0.0 |
| scikit-learn | sklearn | 1 | 0 | 0 | 1 | 0 | >=1.3.0 |
| tenacity | tenacity | 1 | 0 | 1 | 0 | 0 | >=8.2.0 |
| tqdm | tqdm | 1 | 0 | 0 | 0 | 0 | >=4.65.0 |
| watchdog | watchdog | 1 | 0 | 0 | 3 | 0 | >=3.0.0 |

## Dev/Test Tooling (`pip install -e '.[dev]'`)

| dist package | import name(s) | RT hard | RT excl | RT defer | RT cond | Dev | version |
|---|---|---|---|---|---|---|---|
| pytest | pytest | 0 | 0 | 0 | 0 | 754 | >=7.4.0 |

## Optional Integrations (`pip install -e '.[infra]'`)

| dist package | import name(s) | RT hard | RT excl | RT defer | RT cond | Dev | version |
|---|---|---|---|---|---|---|---|
| FlagEmbedding | FlagEmbedding | 0 | 0 | 0 | 1 | 0 | >=1.0.0 |
| GitPython | git | 0 | 0 | 0 | 2 | 0 | >=3.1.0 |
| PyPDF2 | PyPDF2 | 0 | 0 | 0 | 1 | 0 | >=3.0.0 |
| anthropic | anthropic | 0 | 0 | 0 | 3 | 0 | >=0.20.0 |
| bandit | bandit | 0 | 0 | 0 | 1 | 0 | >=1.7.0 |
| beautifulsoup4 | bs4 | 0 | 1 | 0 | 0 | 0 | >=4.12.0 |
| boto3 | boto3 | 0 | 0 | 0 | 1 | 0 | >=1.28.0 |
| dash | dash | 0 | 1 | 0 | 0 | 0 | >=2.14.0 |
| fastapi | fastapi | 0 | 1 | 0 | 1 | 2 | >=0.100.0 |
| google-genai | google.genai | 0 | 0 | 0 | 1 | 0 | >=1.0.0 |
| google-generativeai | google.generativeai | 0 | 0 | 2 | 2 | 0 | >=0.3.0 |
| livereload | livereload | 0 | 1 | 0 | 0 | 0 | >=2.6.0 |
| neo4j | neo4j | 0 | 0 | 0 | 1 | 0 | >=5.0.0 |
| openai | openai | 0 | 0 | 1 | 3 | 0 | >=1.0.0 |
| opentelemetry-api | opentelemetry | 0 | 0 | 0 | 2 | 0 | >=1.20.0 |
| pandas | pandas | 0 | 1 | 0 | 1 | 0 | >=2.0.0 |
| pdf2image | pdf2image | 0 | 0 | 0 | 1 | 0 | >=1.16.0 |
| pdfplumber | pdfplumber | 0 | 0 | 0 | 1 | 0 | >=0.10.0 |
| playwright | playwright | 0 | 1 | 0 | 4 | 4 | >=1.40.0 |
| plotly | plotly | 0 | 1 | 0 | 0 | 0 | >=5.18.0 |
| pypdf | pypdf | 0 | 0 | 0 | 1 | 0 | >=3.0.0 |
| pytesseract | pytesseract | 0 | 0 | 0 | 1 | 0 | >=0.3.10 |
| pytz | pytz | 0 | 0 | 0 | 1 | 0 | >=2023.3 |
| requests | requests | 0 | 1 | 0 | 0 | 1 | >=2.28.0 |
| rich | rich | 0 | 1 | 0 | 0 | 0 | >=13.0.0 |
| sentence-transformers | sentence_transformers | 0 | 0 | 0 | 1 | 0 | >=2.2.0 |
| tabulate | tabulate | 0 | 1 | 0 | 0 | 0 | >=0.9.0 |
| tiktoken | tiktoken | 0 | 0 | 0 | 1 | 0 | >=0.5.0 |
| torch | torch | 0 | 0 | 1 | 1 | 0 | >=2.0.0 |
| tree-sitter | tree_sitter | 0 | 0 | 0 | 1 | 0 | >=0.20.0 |
| tree-sitter-python | tree_sitter_python | 0 | 0 | 0 | 1 | 0 | >=0.20.0 |
| uvicorn | uvicorn | 0 | 0 | 0 | 2 | 0 | >=0.23.0 |
| waitress | waitress | 0 | 1 | 0 | 0 | 0 | >=2.1.0 |
| websockets | websockets | 0 | 0 | 0 | 2 | 0 | >=11.0.0 |

## SDK Samples (`pip install -e '.[sdks]'`)

| dist package | import name(s) | RT hard | RT excl | RT defer | RT cond | Dev | version |
|---|---|---|---|---|---|---|---|
| backoff | backoff | 0 | 0 | 0 | 0 | 0 | >=2.2.0 |
| google-cloud-aiplatform | vertexai | 0 | 0 | 0 | 0 | 0 | >=1.38.0 |
| jsonschema | jsonschema | 0 | 0 | 0 | 0 | 0 | >=4.20.0 |

## Phantom/Stale Internal Imports

| import name | file count |
|---|---|
| ManifestGuardian | 1 |
| agent_validation | 1 |
| batch_embeddings | 1 |
| canon_validator_agentic_v2 | 1 |
| config | 1 |
| dashboard_ssot_definitions | 1 |
| execute_ssot | 1 |
| mcp0_git_add_or_commit | 1 |
| mcp0_git_status | 1 |
| mcp_time_client | 1 |
| repo_builder | 1 |
| runtime | 4 |
| scripts | 2 |
| services | 7 |
| shared | 2 |
| territory_ssot_definitions | 1 |
| titanium_rag_pipeline | 1 |

## Findings

[Document key findings from the investigation]

---

## Evidence

[Provide evidence supporting the findings]

---

