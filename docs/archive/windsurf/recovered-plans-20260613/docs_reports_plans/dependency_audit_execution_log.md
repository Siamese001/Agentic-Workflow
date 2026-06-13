# Dependency Audit — Full Execution Log (v4, separate scans)

All commands executed verbatim. Outputs complete (not truncated).

---

## 1A. Runtime Scan

**Command:**
```bash
python ops_scripts/general/ast_import_audit.py --roots agentic_core apps_lic apps_rg apps_shared --emit-tag runtime --exclude-subdir scripts dashboards
```

**Exit code:** 0

**Full stdout:**
```
Scanning: roots=['agentic_core', 'apps_lic', 'apps_rg', 'apps_shared'] tag=runtime exclude-subdir=['dashboards', 'scripts']

Scan complete: tag=runtime
  Roots:            ['agentic_core', 'apps_lic', 'apps_rg', 'apps_shared']
  Exclude subdirs:  ['dashboards', 'scripts']
  Files scanned:    1583
  Dist packages:    53
  Phantom internal: 13
  Parse errors:     0

  Dist packages found:
    FlagEmbedding                  imports=[FlagEmbedding]  (1 conditional)
    GitPython                      imports=[git]  (2 conditional)
    PyPDF2                         imports=[PyPDF2]  (1 conditional)
    PyYAML                         imports=[yaml]  (1 hard, 2 excluded-hard, 3 conditional)
    aiofiles                       imports=[aiofiles]  (3 hard)
    anthropic                      imports=[anthropic]  (3 conditional)
    bandit                         imports=[bandit]  (1 conditional)
    beautifulsoup4                 imports=[bs4]  (1 excluded-hard)
    boto3                          imports=[boto3]  (1 conditional)
    chromadb                       imports=[chromadb]  (1 hard, 1 conditional)
    dash                           imports=[dash]  (1 excluded-hard)
    duckdb                         imports=[duckdb]  (1 hard)
    fastapi                        imports=[fastapi]  (1 excluded-hard, 1 conditional)
    google-genai                   imports=[google.genai]  (1 conditional)
    google-generativeai            imports=[google.generativeai]  (2 deferred, 2 conditional)
    jinja2                         imports=[jinja2]  (1 hard, 1 conditional)
    libcst                         imports=[libcst]  (3 hard)
    livereload                     imports=[livereload]  (1 excluded-hard)
    neo4j                          imports=[neo4j]  (1 conditional)
    networkx                       imports=[networkx]  (3 hard, 1 excluded-hard, 1 conditional)
    numpy                          imports=[numpy]  (9 hard, 1 excluded-hard)
    openai                         imports=[openai]  (1 deferred, 3 conditional)
    opentelemetry-api              imports=[opentelemetry]  (2 conditional)
    pandas                         imports=[pandas]  (1 excluded-hard, 1 conditional)
    pdf2image                      imports=[pdf2image]  (1 conditional)
    pdfplumber                     imports=[pdfplumber]  (1 conditional)
    pinecone                       imports=[pinecone]  (1 hard, 5 conditional)
    playwright                     imports=[playwright]  (1 excluded-hard, 4 conditional)
    plotly                         imports=[plotly]  (1 excluded-hard)
    psutil                         imports=[psutil]  (1 hard, 2 conditional)
    pydantic                       imports=[pydantic, pydantic_core]  (71 hard, 2 excluded-hard, 3 deferred, 1 conditional)
    pydantic-settings              imports=[pydantic_settings]  (1 hard)
    pypdf                          imports=[pypdf]  (1 conditional)
    pytesseract                    imports=[pytesseract]  (1 conditional)
    python-dotenv                  imports=[dotenv]  (1 hard, 4 conditional)
    pytz                           imports=[pytz]  (1 conditional)
    rank-bm25                      imports=[rank_bm25]  (2 hard)
    redis                          imports=[redis]  (4 hard, 5 conditional)
    requests                       imports=[requests]  (1 excluded-hard)
    rich                           imports=[rich]  (1 excluded-hard)
    scikit-learn                   imports=[sklearn]  (1 hard, 1 conditional)
    sentence-transformers          imports=[sentence_transformers]  (1 conditional)
    tabulate                       imports=[tabulate]  (1 excluded-hard)
    tenacity                       imports=[tenacity]  (1 hard, 1 deferred)
    tiktoken                       imports=[tiktoken]  (1 conditional)
    torch                          imports=[torch]  (1 deferred, 1 conditional)
    tqdm                           imports=[tqdm]  (1 hard)
    tree-sitter                    imports=[tree_sitter]  (1 conditional)
    tree-sitter-python             imports=[tree_sitter_python]  (1 conditional)
    uvicorn                        imports=[uvicorn]  (2 conditional)
    waitress                       imports=[waitress]  (1 excluded-hard)
    watchdog                       imports=[watchdog]  (1 hard, 3 conditional)
    websockets                     imports=[websockets]  (2 conditional)

  Written: docs\reports\plans\dependency_audit_scan_runtime.json
```

---

## 1B. Dev Scan

**Command:**
```bash
python ops_scripts/general/ast_import_audit.py --roots tests --emit-tag dev
```

**Exit code:** 0

**Full stdout:**
```
Scanning: roots=['tests'] tag=dev exclude-subdir=[]

Scan complete: tag=dev
  Roots:            ['tests']
  Files scanned:    998
  Dist packages:    9
  Phantom internal: 6
  Parse errors:     0

  Dist packages found:
    PyYAML                         imports=[yaml]  (1 deferred)
    fastapi                        imports=[fastapi]  (2 hard)
    libcst                         imports=[libcst]  (2 hard)
    playwright                     imports=[playwright]  (2 hard, 1 deferred, 2 conditional)
    psutil                         imports=[psutil]  (1 conditional)
    pydantic                       imports=[pydantic]  (2 deferred, 1 conditional)
    pytest                         imports=[pytest]  (754 hard)
    python-dotenv                  imports=[dotenv]  (1 hard, 1 conditional)
    requests                       imports=[requests]  (1 hard)

  Written: docs\reports\plans\dependency_audit_scan_dev.json
```

---

## 1C. SDK Scan

**Command:**
```bash
python ops_scripts/general/ast_import_audit.py --roots data/sdks_mcps --emit-tag sdks
```

**Exit code:** 0

**Full stdout:**
```
Scanning: roots=['data/sdks_mcps'] tag=sdks exclude-subdir=[]

Scan complete: tag=sdks
  Roots:            ['data/sdks_mcps']
  Files scanned:    8
  Dist packages:    5
  Phantom internal: 1
  Parse errors:     0

  Dist packages found:
    anthropic                      imports=[anthropic]  (1 hard)
    backoff                        imports=[backoff]  (3 hard)
    google-cloud-aiplatform        imports=[vertexai]  (2 hard, 1 deferred)
    jsonschema                     imports=[jsonschema]  (1 hard)
    openai                         imports=[openai]  (1 hard)

  Written: docs\reports\plans\dependency_audit_scan_sdks.json
```

---

## 1D. Merge

**Command:**
```bash
python ops_scripts/general/ast_import_audit.py --merge
```

**Exit code:** 0

**Full stdout:**
```
Merging scan inventories...
  Loaded: dependency_audit_scan_dev.json (tag=dev, 9 dists)
  Loaded: dependency_audit_scan_runtime.json (tag=runtime, 53 dists)
  Loaded: dependency_audit_scan_sdks.json (tag=sdks, 5 dists)

Merge complete:
  Scans merged:     ['dev', 'runtime', 'sdks']
  Dist packages:    57
  Buckets:          core=19 dev=1 infra=34 sdks=3
  Phantom internal: 17

  Packages by bucket:
    [core] (19): PyYAML, aiofiles, chromadb, duckdb, jinja2, libcst, networkx, numpy, pinecone, psutil, pydantic, pydantic-settings, python-dotenv, rank-bm25, redis, scikit-learn, tenacity, tqdm, watchdog
    [dev] (1): pytest
    [infra] (34): FlagEmbedding, GitPython, PyPDF2, anthropic, bandit, beautifulsoup4, boto3, dash, fastapi, google-genai, google-generativeai, livereload, neo4j, openai, opentelemetry-api, pandas, pdf2image, pdfplumber, playwright, plotly, pypdf, pytesseract, pytz, requests, rich, sentence-transformers, tabulate, tiktoken, torch, tree-sitter, tree-sitter-python, uvicorn, waitress, websockets
    [sdks] (3): backoff, google-cloud-aiplatform, jsonschema

  Artifacts:
    docs\reports\plans\dependency_audit_merged.json
    docs\reports\plans\dependency_audit_report.md
    docs\reports\plans\dependency_audit_pyproject_diff.patch
    docs\reports\plans\dependency_verify_imports.py
```

---

## 2A. Verifier — default (core only required)

**Command:**
```bash
python docs/reports/plans/dependency_verify_imports.py
```

**Exit code:** 1

**Full stdout:**
```
  [core ] [REQ] dist=PyYAML                         OK                 imports: yaml=OK
  [core ] [REQ] dist=aiofiles                       OK                 imports: aiofiles=OK
  [core ] [REQ] dist=chromadb                       FAIL               imports: chromadb=MISSING: No module named 'chromadb'
  [core ] [REQ] dist=duckdb                         FAIL               imports: duckdb=MISSING: No module named 'duckdb'
  [core ] [REQ] dist=jinja2                         OK                 imports: jinja2=OK
  [core ] [REQ] dist=libcst                         OK                 imports: libcst=OK
  [core ] [REQ] dist=networkx                       OK                 imports: networkx=OK
  [core ] [REQ] dist=numpy                          FAIL               imports: numpy=MISSING: No module named 'numpy'
  [core ] [REQ] dist=pinecone                       OK                 imports: pinecone=OK
  [core ] [REQ] dist=psutil                         OK                 imports: psutil=OK
  [core ] [REQ] dist=pydantic                       OK                 imports: pydantic=OK
  [core ] [REQ] dist=pydantic-settings              FAIL               imports: pydantic_settings=MISSING: No module named 'pydantic_settings'
  [core ] [REQ] dist=python-dotenv                  OK                 imports: dotenv=OK
  [core ] [REQ] dist=rank-bm25                      FAIL               imports: rank_bm25=MISSING: No module named 'rank_bm25'
  [core ] [REQ] dist=redis                          OK                 imports: redis=OK
  [core ] [REQ] dist=scikit-learn                   FAIL               imports: sklearn=MISSING: No module named 'sklearn'
  [core ] [REQ] dist=tenacity                       OK                 imports: tenacity=OK
  [core ] [REQ] dist=tqdm                           OK                 imports: tqdm=OK
  [core ] [REQ] dist=watchdog                       OK                 imports: watchdog=OK
  [dev  ] [OPT] dist=pytest                         OK                 imports: pytest=OK
  [infra] [OPT] dist=FlagEmbedding                  EXPECTED_MISSING   imports: FlagEmbedding=MISSING: No module named 'FlagEmbedding'
  [infra] [OPT] dist=GitPython                      EXPECTED_MISSING   imports: git=MISSING: No module named 'git'
  [infra] [OPT] dist=PyPDF2                         EXPECTED_MISSING   imports: PyPDF2=MISSING: No module named 'PyPDF2'
  [infra] [OPT] dist=anthropic                      OK                 imports: anthropic=OK
  [infra] [OPT] dist=bandit                         EXPECTED_MISSING   imports: bandit=MISSING: No module named 'bandit'
  [infra] [OPT] dist=beautifulsoup4                 OK                 imports: bs4=OK
  [infra] [OPT] dist=boto3                          EXPECTED_MISSING   imports: boto3=MISSING: No module named 'boto3'
  [infra] [OPT] dist=dash                           EXPECTED_MISSING   imports: dash=MISSING: No module named 'dash'
  [infra] [OPT] dist=fastapi                        OK                 imports: fastapi=OK
  [infra] [OPT] dist=google-genai                   OK                 imports: google.genai=OK
  [infra] [OPT] dist=google-generativeai            EXPECTED_MISSING   imports: google.generativeai=MISSING: No module named 'google.generativeai'
  [infra] [OPT] dist=livereload                     EXPECTED_MISSING   imports: livereload=MISSING: No module named 'livereload'
  [infra] [OPT] dist=neo4j                          EXPECTED_MISSING   imports: neo4j=MISSING: No module named 'neo4j'
  [infra] [OPT] dist=openai                         OK                 imports: openai=OK
  [infra] [OPT] dist=opentelemetry-api              EXPECTED_MISSING   imports: opentelemetry=MISSING: No module named 'opentelemetry'
  [infra] [OPT] dist=pandas                         EXPECTED_MISSING   imports: pandas=MISSING: No module named 'pandas'
  [infra] [OPT] dist=pdf2image                      EXPECTED_MISSING   imports: pdf2image=MISSING: No module named 'pdf2image'
  [infra] [OPT] dist=pdfplumber                     EXPECTED_MISSING   imports: pdfplumber=MISSING: No module named 'pdfplumber'
  [infra] [OPT] dist=playwright                     EXPECTED_MISSING   imports: playwright=MISSING: No module named 'playwright'
  [infra] [OPT] dist=plotly                         EXPECTED_MISSING   imports: plotly=MISSING: No module named 'plotly'
  [infra] [OPT] dist=pypdf                          EXPECTED_MISSING   imports: pypdf=MISSING: No module named 'pypdf'
  [infra] [OPT] dist=pytesseract                    EXPECTED_MISSING   imports: pytesseract=MISSING: No module named 'pytesseract'
  [infra] [OPT] dist=pytz                           EXPECTED_MISSING   imports: pytz=MISSING: No module named 'pytz'
  [infra] [OPT] dist=requests                       OK                 imports: requests=OK
  [infra] [OPT] dist=rich                           OK                 imports: rich=OK
  [infra] [OPT] dist=sentence-transformers          EXPECTED_MISSING   imports: sentence_transformers=MISSING: No module named 'sentence_transformers'
  [infra] [OPT] dist=tabulate                       OK                 imports: tabulate=OK
  [infra] [OPT] dist=tiktoken                       EXPECTED_MISSING   imports: tiktoken=MISSING: No module named 'tiktoken'
  [infra] [OPT] dist=torch                          EXPECTED_MISSING   imports: torch=MISSING: No module named 'torch'
  [infra] [OPT] dist=tree-sitter                    EXPECTED_MISSING   imports: tree_sitter=MISSING: No module named 'tree_sitter'
  [infra] [OPT] dist=tree-sitter-python             EXPECTED_MISSING   imports: tree_sitter_python=MISSING: No module named 'tree_sitter_python'
  [infra] [OPT] dist=uvicorn                        EXPECTED_MISSING   imports: uvicorn=MISSING: No module named 'uvicorn'
  [infra] [OPT] dist=waitress                       EXPECTED_MISSING   imports: waitress=MISSING: No module named 'waitress'
  [infra] [OPT] dist=websockets                     OK                 imports: websockets=OK
  [sdks ] [OPT] dist=backoff                        OK                 imports: backoff=OK
  [sdks ] [OPT] dist=google-cloud-aiplatform        OK                 imports: vertexai=OK
  [sdks ] [OPT] dist=jsonschema                     OK                 imports: jsonschema=OK

Bucket Summary:
  bucket   required?    OK  FAIL  SKIP  verdict
  core     yes          13     6     0    BLOCK
  dev      no            1     0     0     PASS
  infra    no            9     0    25     PASS
  sdks     no            3     0     0     PASS

Total: 26/57 dist packages OK, 6 BLOCKING, 25 EXPECTED_MISSING
RESULT: FAIL (6 blocking failures)
```

---

## 2B. Verifier — --require-dev

**Command:**
```bash
python docs/reports/plans/dependency_verify_imports.py --require-dev
```

**Exit code:** 1

**Bucket summary (full stdout identical to 2A except):**
```
Bucket Summary:
  bucket   required?    OK  FAIL  SKIP  verdict
  core     yes          13     6     0    BLOCK
  dev      yes           1     0     0     PASS
  infra    no            9     0    25     PASS
  sdks     no            3     0     0     PASS

Total: 26/57 dist packages OK, 6 BLOCKING, 25 EXPECTED_MISSING
RESULT: FAIL (6 blocking failures)
```

---

## 2C. Verifier — --all

**Command:**
```bash
python docs/reports/plans/dependency_verify_imports.py --all
```

**Exit code:** 1

**Bucket summary (full stdout identical to 2A except infra rows show FAIL instead of EXPECTED_MISSING):**
```
Bucket Summary:
  bucket   required?    OK  FAIL  SKIP  verdict
  core     yes          13     6     0    BLOCK
  dev      yes           1     0     0     PASS
  infra    yes           9    25     0    BLOCK
  sdks     yes           3     0     0     PASS

Total: 26/57 dist packages OK, 31 BLOCKING, 0 EXPECTED_MISSING
RESULT: FAIL (31 blocking failures)
```

---

## 3. Google Namespace Evidence (AST-derived from scan JSON)

**Command:**
```bash
python -c "import json; d=json.loads(open('docs/reports/plans/dependency_audit_scan_runtime.json').read()); ds=d['dist_summary']; g1=ds.get('google-genai',{}); g2=ds.get('google-generativeai',{}); print('=== google-genai ==='); print('import_names:', g1.get('import_names')); print('hard_files:', g1.get('hard_files')); print('excluded_hard_files:', g1.get('excluded_hard_files')); print('deferred_files:', g1.get('deferred_files')); print('conditional_files:', g1.get('conditional_files')); print(); print('=== google-generativeai ==='); print('import_names:', g2.get('import_names')); print('hard_files:', g2.get('hard_files')); print('excluded_hard_files:', g2.get('excluded_hard_files')); print('deferred_files:', g2.get('deferred_files')); print('conditional_files:', g2.get('conditional_files')); print(); print('=== bare google in dist_summary? ==='); print('google' in ds)"
```

**Exit code:** 0

**Full stdout:**
```
=== google-genai ===
import_names: ['google.genai']
hard_files: []
excluded_hard_files: []
deferred_files: []
conditional_files: ['apps_shared/types/hardened_gemini_executor_types.py']

=== google-generativeai ===
import_names: ['google.generativeai']
hard_files: []
excluded_hard_files: []
deferred_files: ['agentic_core/L2_execution/reasoning/EmbeddingSovereignAgent.py', 'apps_rg/tools/ResumeGenerator.py']
conditional_files: ['agentic_core/L2_execution/enforcement/SovereignLLMGateway.py', 'apps_shared/utils/providers_google_genai_client.py']

=== bare google in dist_summary? ===
False
```

**Verifier confirmation:** Bare `google` does NOT appear as a tested target. The verifier tests:
- `dist=google-genai` → `imports: google.genai=OK`
- `dist=google-generativeai` → `imports: google.generativeai=MISSING`

---

## Summary

**6 BLOCKING core failures:**
1. chromadb
2. duckdb
3. numpy
4. pydantic-settings
5. rank-bm25
6. scikit-learn

**Bucket totals:** core=19, dev=1, infra=34, sdks=3 (57 total)

**pyproject.toml:** NOT MODIFIED (zero diff against HEAD)

## Findings

[Document key findings from the investigation]

---

## Evidence

[Provide evidence supporting the findings]

---

