---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\dependency_gate_evidence_v0_obsolete.md'
original_relative_path: 'dependency_gate_evidence_v0_obsolete.md'
source_sha256: ab3e0cb5f2f3dd8ab76200c5be1a3499064cd5918b78d7f77b48ba8f9f0cf312
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-02-25'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# OBSOLETE — Superseded by dependency_gate_evidence_vFinal.md

This file contains intermediate gate results from an earlier run and is no longer authoritative.
Canonical evidence: `docs/reports/plans/dependency_gate_evidence_vFinal.md`

---

# Dependency Gate Evidence — Clean Venv Run (OBSOLETE)

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Gate Results Summary

**Environment:** Python 3.12.10, pip 25.0.1, clean venv `.venv_gate`

### Gate A: Python/Pip Version ✅ PASS
```
Python 3.12.10
pip 25.0.1 from C:\Git\Agentic-Workflow\.venv_gate\Lib\site-packages\pip (python 3.12)
```

### Gate B: pip install -e . ✅ PASS
```
Successfully installed agentic-workflow-1.0.0 [+ 48 dependencies]
```

### Gate C: Import Test ✅ PASS
```bash
python -c "import agentic_core; import apps_shared"
```
**Exit code:** 0
**Output:** `Gate C PASS: Import successful`

### Gate D: Core Verifier ❌ FAIL — 13 BLOCKING
```bash
python docs/reports/plans/dependency_verify_imports.py
```
**Exit code:** 0
**Bucket Summary:**
```
bucket   required?    OK  FAIL  SKIP  verdict
core     yes           6    13     0    BLOCK
dev      no            1     0     0     PASS
infra    no            3     0    31     PASS
sdks     no            0     0     3     PASS

Total: 10/57 dist packages OK, 13 BLOCKING, 34 EXPECTED_MISSING
RESULT: FAIL (13 blocking failures)
```

**13 BLOCKING failures:**
1. aiofiles — MISSING
2. chromadb — MISSING
3. duckdb — MISSING
4. jinja2 — MISSING
5. networkx — MISSING
6. numpy — MISSING
7. psutil — MISSING
8. pydantic-settings — MISSING
9. python-dotenv — MISSING
10. rank-bm25 — MISSING
11. scikit-learn — MISSING
12. tqdm — MISSING
13. watchdog — MISSING

---

## Root Cause Analysis

### Current HEAD pyproject.toml declares 9 core deps:
```toml
dependencies = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "pytest-asyncio>=0.21.0",
    "pydantic>=2.0.0",
    "google-genai>=1.0.0",
    "pinecone>=5.0.0",
    "redis>=5.0.0",
    "libcst>=1.1.0",
    "cryptography>=41.0.0",
]
```

### Runtime scan shows 53 dist packages with imports:

**Hard imports (28 packages):**
- aiofiles (3 hard)
- beautifulsoup4 (1 hard)
- chromadb (1 hard)
- dash (1 hard)
- duckdb (1 hard)
- fastapi (1 hard, 1 conditional)
- jinja2 (1 hard, 1 conditional)
- libcst (3 hard)
- livereload (1 hard)
- networkx (4 hard, 1 conditional)
- numpy (9 hard)
- pandas (1 hard, 1 conditional)
- pinecone (1 hard, 4 conditional)
- playwright (1 hard, 4 conditional)
- plotly (1 hard)
- psutil (1 hard, 2 conditional)
- pydantic (64 hard, 1 deferred)
- pydantic-settings (1 hard)
- python-dotenv (1 hard, 4 conditional)
- PyYAML (3 hard, 3 conditional)
- rank-bm25 (2 hard)
- redis (4 hard, 5 conditional)
- requests (1 hard)
- rich (1 hard)
- scikit-learn (1 hard, 1 conditional)
- tabulate (1 hard)
- tenacity (1 hard)
- tqdm (1 hard)
- waitress (1 hard)
- watchdog (1 hard, 3 conditional)

**Conditional/deferred imports (25 packages):**
- FlagEmbedding, GitPython, PyPDF2, anthropic, bandit, boto3, google-genai, google-generativeai, neo4j, openai, opentelemetry-api, pdf2image, pdfplumber, pypdf, pytesseract, pytz, sentence-transformers, tiktoken, torch, tree-sitter, tree-sitter-python, uvicorn, websockets

---

## Packaging Policy Options

### Option 1: Heavy Core (28 deps)
**Keep all hard-import packages as core dependencies.**

**Pros:**
- Guarantees `pip install -e .` works for all baseline imports
- No code changes required
- No risk of breaking existing functionality

**Cons:**
- Large install size (~500MB+ with numpy, chromadb, scikit-learn, etc.)
- Includes specialized backends (chromadb, duckdb) not needed for basic usage
- Includes UI/dashboard deps (dash, plotly, livereload) not needed for library usage

**Core deps (28):**
```toml
dependencies = [
    "pydantic>=2.0.0",
    "python-dotenv>=1.0.0",
    "PyYAML>=6.0",
    "networkx>=3.0",
    "jinja2>=3.1.0",
    "libcst>=1.1.0",
    "tenacity>=8.2.0",
    "aiofiles>=23.0.0",
    "psutil>=5.9.0",
    "watchdog>=3.0.0",
    "tqdm>=4.65.0",
    "redis>=5.0.0",
    "pinecone>=5.0.0",
    "numpy>=1.24.0",
    "chromadb>=0.4.0",
    "duckdb>=0.9.0",
    "rank-bm25>=0.2.0",
    "scikit-learn>=1.3.0",
    "pydantic-settings>=2.0.0",
    "beautifulsoup4>=4.12.0",
    "dash>=2.14.0",
    "fastapi>=0.100.0",
    "livereload>=2.6.0",
    "pandas>=2.0.0",
    "playwright>=1.40.0",
    "plotly>=5.18.0",
    "requests>=2.28.0",
    "rich>=13.0.0",
    "tabulate>=0.9.0",
    "waitress>=2.1.0",
]
```

### Option 2: Lean Core (13 deps) + Guardrails
**Move 15 specialized packages to infra extras, implement import guardrails.**

**Packages to move to infra (15):**
1. numpy (9 hard) — embeddings, caching, agents
2. chromadb (1 hard) — vector cache backend
3. duckdb (1 hard) — trace event storage
4. rank-bm25 (2 hard) — BM25 retrieval
5. scikit-learn (1 hard) — TF-IDF validation
6. pydantic-settings (1 hard) — Settings class (unused)
7. beautifulsoup4 (1 hard) — HTML parsing
8. dash (1 hard) — dashboard UI
9. fastapi (1 hard) — web server
10. livereload (1 hard) — dev server
11. pandas (1 hard) — data processing
12. playwright (1 hard) — browser automation
13. plotly (1 hard) — visualization
14. waitress (1 hard) — WSGI server
15. rich (1 hard) — terminal formatting

**Core deps (13):**
```toml
dependencies = [
    "pydantic>=2.0.0",
    "python-dotenv>=1.0.0",
    "PyYAML>=6.0",
    "networkx>=3.0",
    "jinja2>=3.1.0",
    "libcst>=1.1.0",
    "tenacity>=8.2.0",
    "aiofiles>=23.0.0",
    "psutil>=5.9.0",
    "watchdog>=3.0.0",
    "tqdm>=4.65.0",
    "redis>=5.0.0",
    "pinecone>=5.0.0",
    "requests>=2.28.0",
    "tabulate>=0.9.0",
]
```

**Guardrail strategy:**
- Defer imports to function scope with try/except ImportError
- Raise actionable error: "Install with: pip install -e '.[infra]'"
- Update type hints to use `from __future__ import annotations` or `Any`

**Estimated effort:** 2- for complete implementation + testing
**Estimated benefit:** ~400MB smaller core install, clearer separation of concerns

---

## Recommendation

**Proceed with Option 2 (Lean Core)** for the following reasons:

1. **Baseline usability:** 13 core deps cover all essential library functionality
2. **Specialized backends:** chromadb, duckdb, rank-bm25 are optional backends, not required for basic usage
3. **UI/dashboard deps:** dash, plotly, livereload are development/visualization tools, not library runtime
4. **Clear separation:** Core = library essentials, Infra = specialized backends + UI tools
5. **Smaller footprint:** ~100MB core vs ~500MB+ with all hard imports

**Next steps:**
1. Implement guardrails for 15 packages (deferred imports + actionable errors)
2. Update pyproject.toml with 13 core + 15 infra
3. Re-run clean venv gates to verify 0 BLOCKING
4. Provide minimal, reviewable diffs grouped logically

## Violation

[Describe the violation or issue that triggered this RCA]

---

## Corrective Actions

[List the corrective actions taken to resolve the issue]

---

