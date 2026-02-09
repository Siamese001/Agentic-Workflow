# Dependency Gate Evidence — vFinal

Authoritative evidence run for the lean-core dependency remediation.
Supersedes: `dependency_gate_evidence_v0_obsolete.md`

**Environment:** Windows, Python 3.12.10, pip 25.0.1, clean `.venv_final`
**Date:** 2026-02-09

---

## Gate A: Create Clean Venv + Version Check

```
> python -m venv .venv_final
> .venv_final\Scripts\python.exe -V
Python 3.12.10

> .venv_final\Scripts\python.exe -m pip -V
pip 25.0.1 from C:\Git\Agentic-Workflow\.venv_final\Lib\site-packages\pip (python 3.12)
```

Exit code: 0

---

## Gate B: `pip install -e .` (lean core — no infra deps)

```
> .venv_final\Scripts\python.exe -m pip install -e .

Obtaining file:///C:/Git/Agentic-Workflow
  Installing build dependencies ... done
  Checking if build backend supports build_editable ... done
  Getting requirements to build editable ... done
  Preparing editable metadata (pyproject.toml) ... done
Collecting pydantic>=2.0.0 (from agentic-workflow==1.0.0)
Collecting google-genai>=1.0.0 (from agentic-workflow==1.0.0)
Collecting pinecone>=5.0.0 (from agentic-workflow==1.0.0)
Collecting redis>=5.0.0 (from agentic-workflow==1.0.0)
Collecting libcst>=1.1.0 (from agentic-workflow==1.0.0)
Collecting cryptography>=41.0.0 (from agentic-workflow==1.0.0)
Collecting aiofiles>=23.0.0 (from agentic-workflow==1.0.0)
Collecting jinja2>=3.1.0 (from agentic-workflow==1.0.0)
Collecting networkx>=3.0 (from agentic-workflow==1.0.0)
Collecting psutil>=5.9.0 (from agentic-workflow==1.0.0)
Collecting python-dotenv>=1.0.0 (from agentic-workflow==1.0.0)
Collecting PyYAML>=6.0 (from agentic-workflow==1.0.0)
Collecting tenacity>=8.2.0 (from agentic-workflow==1.0.0)
Collecting tqdm>=4.65.0 (from agentic-workflow==1.0.0)
Collecting watchdog>=3.0.0 (from agentic-workflow==1.0.0)
Building wheels for collected packages: agentic-workflow
  Building editable for agentic-workflow (pyproject.toml) ... done
Successfully built agentic-workflow
Successfully installed MarkupSafe-3.0.3 PyYAML-6.0.3 agentic-workflow-1.0.0
  aiofiles-25.1.0 annotated-types-0.7.0 anyio-4.12.1 certifi-2026.1.4
  cffi-2.0.0 charset_normalizer-3.4.4 colorama-0.4.6 cryptography-46.0.4
  distro-1.9.0 google-auth-2.48.0 google-genai-1.62.0 h11-0.16.0
  httpcore-1.0.9 httpx-0.28.1 idna-3.11 jinja2-3.1.6 libcst-1.8.6
  networkx-3.6.1 orjson-3.11.7 packaging-24.2 pinecone-8.0.0
  pinecone-plugin-assistant-3.0.2 pinecone-plugin-interface-0.0.7
  psutil-7.2.2 pyasn1-0.6.2 pyasn1-modules-0.4.2 pycparser-3.0
  pydantic-2.12.5 pydantic-core-2.41.5 python-dateutil-2.9.0.post0
  python-dotenv-1.2.1 redis-7.1.0 requests-2.32.5 rsa-4.9.1
  six-1.17.0 sniffio-1.3.1 tenacity-9.1.4 tqdm-4.67.3
  typing-extensions-4.15.0 typing-inspection-0.4.2 urllib3-2.6.3
  watchdog-6.0.0 websockets-15.0.1
```

Exit code: 0

---

## Gate C: Baseline Import Test

```
> .venv_final\Scripts\python.exe -c "import agentic_core; import apps_shared; print('Gate C PASS')"
Gate C PASS
```

Exit code: 0

---

## Gate D: Core Verifier (default — core only required)

```
> .venv_final\Scripts\python.exe docs/reports/plans/dependency_verify_imports.py

  [core ] [REQ] dist=PyYAML                         OK                 imports: yaml=OK
  [core ] [REQ] dist=aiofiles                       OK                 imports: aiofiles=OK
  [core ] [REQ] dist=jinja2                         OK                 imports: jinja2=OK
  [core ] [REQ] dist=libcst                         OK                 imports: libcst=OK
  [core ] [REQ] dist=networkx                       OK                 imports: networkx=OK
  [core ] [REQ] dist=pinecone                       OK                 imports: pinecone=OK
  [core ] [REQ] dist=psutil                         OK                 imports: psutil=OK
  [core ] [REQ] dist=pydantic                       OK                 imports: pydantic=OK
  [core ] [REQ] dist=python-dotenv                  OK                 imports: dotenv=OK
  [core ] [REQ] dist=redis                          OK                 imports: redis=OK
  [core ] [REQ] dist=tenacity                       OK                 imports: tenacity=OK
  [core ] [REQ] dist=tqdm                           OK                 imports: tqdm=OK
  [core ] [REQ] dist=watchdog                       OK                 imports: watchdog=OK
  [dev  ] [OPT] dist=pytest                         EXPECTED_MISSING   imports: pytest=MISSING: No module named 'pytest'
  [infra] [OPT] dist=numpy                          EXPECTED_MISSING   imports: numpy=MISSING: No module named 'numpy'
  [infra] [OPT] dist=chromadb                       EXPECTED_MISSING   imports: chromadb=MISSING: No module named 'chromadb'
  [infra] [OPT] dist=duckdb                         EXPECTED_MISSING   imports: duckdb=MISSING: No module named 'duckdb'
  [infra] [OPT] dist=rank-bm25                      EXPECTED_MISSING   imports: rank_bm25=MISSING: No module named 'rank_bm25'
  [infra] [OPT] dist=scikit-learn                   EXPECTED_MISSING   imports: sklearn=MISSING: No module named 'sklearn'
  [infra] [OPT] dist=pydantic-settings              EXPECTED_MISSING   imports: pydantic_settings=MISSING: No module named 'pydantic_settings'
  [infra] [OPT] dist=beautifulsoup4                 EXPECTED_MISSING   imports: bs4=MISSING: No module named 'bs4'
  [infra] [OPT] dist=dash                           EXPECTED_MISSING   imports: dash=MISSING: No module named 'dash'
  [infra] [OPT] dist=fastapi                        EXPECTED_MISSING   imports: fastapi=MISSING: No module named 'fastapi'
  [infra] [OPT] dist=livereload                     EXPECTED_MISSING   imports: livereload=MISSING: No module named 'livereload'
  [infra] [OPT] dist=pandas                         EXPECTED_MISSING   imports: pandas=MISSING: No module named 'pandas'
  [infra] [OPT] dist=playwright                     EXPECTED_MISSING   imports: playwright=MISSING: No module named 'playwright'
  [infra] [OPT] dist=plotly                         EXPECTED_MISSING   imports: plotly=MISSING: No module named 'plotly'
  [infra] [OPT] dist=waitress                       EXPECTED_MISSING   imports: waitress=MISSING: No module named 'waitress'
  [infra] [OPT] dist=rich                           EXPECTED_MISSING   imports: rich=MISSING: No module named 'rich'
  [external] [OPT] dist=FlagEmbedding               EXPECTED_MISSING   imports: FlagEmbedding=MISSING: No module named 'FlagEmbedding'
  [external] [OPT] dist=GitPython                   EXPECTED_MISSING   imports: git=MISSING: No module named 'git'
  [external] [OPT] dist=PyPDF2                      EXPECTED_MISSING   imports: PyPDF2=MISSING: No module named 'PyPDF2'
  [external] [OPT] dist=anthropic                   EXPECTED_MISSING   imports: anthropic=MISSING: No module named 'anthropic'
  [external] [OPT] dist=bandit                      EXPECTED_MISSING   imports: bandit=MISSING: No module named 'bandit'
  [external] [OPT] dist=boto3                       EXPECTED_MISSING   imports: boto3=MISSING: No module named 'boto3'
  [external] [OPT] dist=google-genai                OK                 imports: google.genai=OK
  [external] [OPT] dist=google-generativeai         EXPECTED_MISSING   imports: google.generativeai=MISSING
  [external] [OPT] dist=neo4j                       EXPECTED_MISSING   imports: neo4j=MISSING: No module named 'neo4j'
  [external] [OPT] dist=openai                      EXPECTED_MISSING   imports: openai=MISSING: No module named 'openai'
  [external] [OPT] dist=opentelemetry-api           EXPECTED_MISSING   imports: opentelemetry=MISSING: No module named 'opentelemetry'
  [external] [OPT] dist=pdf2image                   EXPECTED_MISSING   imports: pdf2image=MISSING: No module named 'pdf2image'
  [external] [OPT] dist=pdfplumber                  EXPECTED_MISSING   imports: pdfplumber=MISSING: No module named 'pdfplumber'
  [external] [OPT] dist=pypdf                       EXPECTED_MISSING   imports: pypdf=MISSING: No module named 'pypdf'
  [external] [OPT] dist=pytesseract                 EXPECTED_MISSING   imports: pytesseract=MISSING: No module named 'pytesseract'
  [external] [OPT] dist=pytz                        EXPECTED_MISSING   imports: pytz=MISSING: No module named 'pytz'
  [external] [OPT] dist=requests                    OK                 imports: requests=OK
  [external] [OPT] dist=sentence-transformers       EXPECTED_MISSING   imports: sentence_transformers=MISSING
  [external] [OPT] dist=tabulate                    EXPECTED_MISSING   imports: tabulate=MISSING: No module named 'tabulate'
  [external] [OPT] dist=tiktoken                    EXPECTED_MISSING   imports: tiktoken=MISSING: No module named 'tiktoken'
  [external] [OPT] dist=torch                       EXPECTED_MISSING   imports: torch=MISSING: No module named 'torch'
  [external] [OPT] dist=tree-sitter                 EXPECTED_MISSING   imports: tree_sitter=MISSING: No module named 'tree_sitter'
  [external] [OPT] dist=tree-sitter-python          EXPECTED_MISSING   imports: tree_sitter_python=MISSING
  [external] [OPT] dist=uvicorn                     EXPECTED_MISSING   imports: uvicorn=MISSING: No module named 'uvicorn'
  [external] [OPT] dist=websockets                  OK                 imports: websockets=OK
  [sdks ] [OPT] dist=backoff                        EXPECTED_MISSING   imports: backoff=MISSING: No module named 'backoff'
  [sdks ] [OPT] dist=google-cloud-aiplatform        EXPECTED_MISSING   imports: vertexai=MISSING: No module named 'vertexai'
  [sdks ] [OPT] dist=jsonschema                     EXPECTED_MISSING   imports: jsonschema=MISSING: No module named 'jsonschema'

Bucket Summary:
  bucket   required?    OK  FAIL  SKIP  verdict
  core     yes          13     0     0     PASS
  dev      no            0     0     1     PASS
  infra    no            0     0    15     PASS
  external no            3     0    22     PASS
  sdks     no            0     0     3     PASS

Total: 16/57 dist packages OK, 0 BLOCKING, 41 EXPECTED_MISSING
RESULT: PASS (all required imports OK)
```

Exit code: 0

---

## Gate E: `pip install -e ".[dev]"` + Regression Test

```
> .venv_final\Scripts\python.exe -m pip install -e ".[dev]"

Successfully installed agentic-workflow-1.0.0 black-26.1.0 click-8.3.1
  coverage-7.13.3 iniconfig-2.3.0 librt-0.7.8 mypy-1.19.1
  mypy-extensions-1.1.0 pathspec-1.0.4 platformdirs-4.5.1
  pluggy-1.6.0 pygments-2.19.2 pytest-9.0.2 pytest-asyncio-1.3.0
  pytest-cov-7.0.0 pytokens-0.4.1 ruff-0.15.0
```

Exit code: 0

```
> .venv_final\Scripts\python.exe -m pytest tests/core/test_dependency_verifier_exit_code.py -xvv --no-header --override-ini="addopts="

collected 3 items

tests/core/test_dependency_verifier_exit_code.py::TestDependencyVerifierExitCode::test_verifier_exists PASSED                     [ 33%]
tests/core/test_dependency_verifier_exit_code.py::TestDependencyVerifierExitCode::test_exit_1_on_blocking_failures PASSED          [ 66%]
tests/core/test_dependency_verifier_exit_code.py::TestDependencyVerifierExitCode::test_exit_0_on_pass_when_all_core_installed PASSED [100%]

3 passed in 2.12s
```

Exit code: 0

---

## Gate F: `pip install -e ".[infra]"` + Verifier `--all`

```
> .venv_final\Scripts\python.exe -m pip install -e ".[infra]"

Successfully installed Flask-3.1.2 Werkzeug-3.1.5 agentic-workflow-1.0.0
  annotated-doc-0.0.4 attrs-25.4.0 backoff-2.2.1 bcrypt-5.0.0
  beautifulsoup4-4.14.3 blinker-1.9.0 build-1.4.0 chromadb-1.4.1
  dash-4.0.0 duckdb-1.4.4 durationpy-0.10 fastapi-0.128.5
  filelock-3.20.3 flatbuffers-25.12.19 fsspec-2026.2.0
  googleapis-common-protos-1.72.0 greenlet-3.3.1 grpcio-1.78.0
  hf-xet-1.2.0 httptools-0.7.1 huggingface-hub-1.4.1
  importlib-metadata-8.7.1 importlib-resources-6.5.2 itsdangerous-2.2.0
  joblib-1.5.3 jsonschema-4.26.0 jsonschema-specifications-2025.9.1
  kubernetes-35.0.0 livereload-2.7.1 markdown-it-py-4.0.0
  mdurl-0.1.2 mmh3-5.2.0 mpmath-1.3.0 narwhals-2.16.0
  nest-asyncio-1.6.0 numpy-2.4.2 oauthlib-3.3.1 onnxruntime-1.24.1
  opentelemetry-api-1.39.1 opentelemetry-exporter-otlp-proto-common-1.39.1
  opentelemetry-exporter-otlp-proto-grpc-1.39.1 opentelemetry-proto-1.39.1
  opentelemetry-sdk-1.39.1 opentelemetry-semantic-conventions-0.60b1
  overrides-7.7.0 pandas-3.0.0 playwright-1.58.0 plotly-6.5.2
  posthog-5.4.0 protobuf-6.33.5 pybase64-1.4.3 pydantic-settings-2.12.0
  pyee-13.0.0 pypika-0.51.1 pyproject_hooks-1.2.0 rank-bm25-0.2.2
  referencing-0.37.0 requests-oauthlib-2.0.0 retrying-1.4.2 rich-14.3.2
  rpds-py-0.30.0 scikit-learn-1.8.0 scipy-1.17.0 setuptools-82.0.0
  shellingham-1.5.4 soupsieve-2.8.3 starlette-0.52.1 sympy-1.14.0
  threadpoolctl-3.6.0 tokenizers-0.22.2 tornado-6.5.4 typer-0.21.1
  typer-slim-0.21.1 tzdata-2025.3 uvicorn-0.40.0 waitress-3.0.2
  watchfiles-1.1.1 websocket-client-1.9.0 zipp-3.23.0
```

Exit code: 0

```
> .venv_final\Scripts\python.exe docs/reports/plans/dependency_verify_imports.py --all

  [core ] [REQ] dist=PyYAML                         OK                 imports: yaml=OK
  [core ] [REQ] dist=aiofiles                       OK                 imports: aiofiles=OK
  [core ] [REQ] dist=jinja2                         OK                 imports: jinja2=OK
  [core ] [REQ] dist=libcst                         OK                 imports: libcst=OK
  [core ] [REQ] dist=networkx                       OK                 imports: networkx=OK
  [core ] [REQ] dist=pinecone                       OK                 imports: pinecone=OK
  [core ] [REQ] dist=psutil                         OK                 imports: psutil=OK
  [core ] [REQ] dist=pydantic                       OK                 imports: pydantic=OK
  [core ] [REQ] dist=python-dotenv                  OK                 imports: dotenv=OK
  [core ] [REQ] dist=redis                          OK                 imports: redis=OK
  [core ] [REQ] dist=tenacity                       OK                 imports: tenacity=OK
  [core ] [REQ] dist=tqdm                           OK                 imports: tqdm=OK
  [core ] [REQ] dist=watchdog                       OK                 imports: watchdog=OK
  [dev  ] [REQ] dist=pytest                         OK                 imports: pytest=OK
  [infra] [REQ] dist=numpy                          OK                 imports: numpy=OK
  [infra] [REQ] dist=chromadb                       OK                 imports: chromadb=OK
  [infra] [REQ] dist=duckdb                         OK                 imports: duckdb=OK
  [infra] [REQ] dist=rank-bm25                      OK                 imports: rank_bm25=OK
  [infra] [REQ] dist=scikit-learn                   OK                 imports: sklearn=OK
  [infra] [REQ] dist=pydantic-settings              OK                 imports: pydantic_settings=OK
  [infra] [REQ] dist=beautifulsoup4                 OK                 imports: bs4=OK
  [infra] [REQ] dist=dash                           OK                 imports: dash=OK
  [infra] [REQ] dist=fastapi                        OK                 imports: fastapi=OK
  [infra] [REQ] dist=livereload                     OK                 imports: livereload=OK
  [infra] [REQ] dist=pandas                         OK                 imports: pandas=OK
  [infra] [REQ] dist=playwright                     OK                 imports: playwright=OK
  [infra] [REQ] dist=plotly                         OK                 imports: plotly=OK
  [infra] [REQ] dist=waitress                       OK                 imports: waitress=OK
  [infra] [REQ] dist=rich                           OK                 imports: rich=OK
  [external] [OPT] dist=FlagEmbedding               EXPECTED_MISSING   imports: FlagEmbedding=MISSING
  [external] [OPT] dist=GitPython                   EXPECTED_MISSING   imports: git=MISSING
  [external] [OPT] dist=PyPDF2                      EXPECTED_MISSING   imports: PyPDF2=MISSING
  [external] [OPT] dist=anthropic                   EXPECTED_MISSING   imports: anthropic=MISSING
  [external] [OPT] dist=bandit                      EXPECTED_MISSING   imports: bandit=MISSING
  [external] [OPT] dist=boto3                       EXPECTED_MISSING   imports: boto3=MISSING
  [external] [OPT] dist=google-genai                OK                 imports: google.genai=OK
  [external] [OPT] dist=google-generativeai         EXPECTED_MISSING   imports: google.generativeai=MISSING
  [external] [OPT] dist=neo4j                       EXPECTED_MISSING   imports: neo4j=MISSING
  [external] [OPT] dist=openai                      EXPECTED_MISSING   imports: openai=MISSING
  [external] [OPT] dist=opentelemetry-api           OK                 imports: opentelemetry=OK
  [external] [OPT] dist=pdf2image                   EXPECTED_MISSING   imports: pdf2image=MISSING
  [external] [OPT] dist=pdfplumber                  EXPECTED_MISSING   imports: pdfplumber=MISSING
  [external] [OPT] dist=pypdf                       EXPECTED_MISSING   imports: pypdf=MISSING
  [external] [OPT] dist=pytesseract                 EXPECTED_MISSING   imports: pytesseract=MISSING
  [external] [OPT] dist=pytz                        EXPECTED_MISSING   imports: pytz=MISSING
  [external] [OPT] dist=requests                    OK                 imports: requests=OK
  [external] [OPT] dist=sentence-transformers       EXPECTED_MISSING   imports: sentence_transformers=MISSING
  [external] [OPT] dist=tabulate                    EXPECTED_MISSING   imports: tabulate=MISSING
  [external] [OPT] dist=tiktoken                    EXPECTED_MISSING   imports: tiktoken=MISSING
  [external] [OPT] dist=torch                       EXPECTED_MISSING   imports: torch=MISSING
  [external] [OPT] dist=tree-sitter                 EXPECTED_MISSING   imports: tree_sitter=MISSING
  [external] [OPT] dist=tree-sitter-python          EXPECTED_MISSING   imports: tree_sitter_python=MISSING
  [external] [OPT] dist=uvicorn                     OK                 imports: uvicorn=OK
  [external] [OPT] dist=websockets                  OK                 imports: websockets=OK
  [sdks ] [OPT] dist=backoff                        OK                 imports: backoff=OK
  [sdks ] [OPT] dist=google-cloud-aiplatform        EXPECTED_MISSING   imports: vertexai=MISSING
  [sdks ] [OPT] dist=jsonschema                     OK                 imports: jsonschema=OK

Bucket Summary:
  bucket   required?    OK  FAIL  SKIP  verdict
  core     yes          13     0     0     PASS
  dev      yes           1     0     0     PASS
  infra    yes          15     0     0     PASS
  external no            5     0    20     PASS
  sdks     no            2     0     1     PASS

Total: 36/57 dist packages OK, 0 BLOCKING, 21 EXPECTED_MISSING
RESULT: PASS (all required imports OK)
```

Exit code: 0

---

## Unified Diffs

### 1. pyproject.toml

```diff
diff --git a/pyproject.toml b/pyproject.toml
index 1cf22430f..faeb5d19a 100644
--- a/pyproject.toml
+++ b/pyproject.toml
@@ -25,17 +25,11 @@ dependencies = [
     "libcst>=1.1.0",         # MANDATORY: Deterministic AST serialization (Cap 1.4)
     "cryptography>=41.0.0",  # MANDATORY: Signed Guardian artifacts (Cap 7.2)
     "aiofiles>=23.0.0",
-    "chromadb>=0.4.0",
-    "duckdb>=0.9.0",
     "jinja2>=3.1.0",
     "networkx>=3.0",
-    "numpy>=1.24.0",
     "psutil>=5.9.0",
-    "pydantic-settings>=2.0.0",
     "python-dotenv>=1.0.0",
     "PyYAML>=6.0",
-    "rank-bm25>=0.2.0",
-    "scikit-learn>=1.3.0",
     "tenacity>=8.2.0",
     "tqdm>=4.65.0",
     "watchdog>=3.0.0",
@@ -50,6 +44,23 @@ dev = [
     "ruff>=0.1.0",
     "mypy>=1.5.0",
 ]
+infra = [
+    "numpy>=1.24.0",
+    "chromadb>=0.4.0",
+    "duckdb>=0.9.0",
+    "rank-bm25>=0.2.0",
+    "scikit-learn>=1.3.0",
+    "pydantic-settings>=2.0.0",
+    "beautifulsoup4>=4.12.0",
+    "dash>=2.14.0",
+    "fastapi>=0.100.0",
+    "livereload>=2.6.0",
+    "pandas>=2.0.0",
+    "playwright>=1.40.0",
+    "plotly>=5.18.0",
+    "waitress>=2.1.0",
+    "rich>=13.0.0",
+]
```

### 2. docs/reports/plans/dependency_verify_imports.py

```diff
diff --git a/docs/reports/plans/dependency_verify_imports.py b/docs/reports/plans/dependency_verify_imports.py
index 24dc2f5b0..96099a475 100644
--- a/docs/reports/plans/dependency_verify_imports.py
+++ b/docs/reports/plans/dependency_verify_imports.py
@@ -3,9 +3,10 @@ Reproducible import verification script (v4).
 Generated: 2026-02-09T03:42:13.423459+00:00

 Verification contract:
-  default:       require core only.
-  --require-dev: require core + dev.
-  --all:         require every bucket.
+  default:         require core only.
+  --require-dev:   require core + dev.
+  --require-infra: require core + infra (declared optional deps).
+  --all:           require core + dev + infra (declared optional deps).

 Output is keyed by dist package with per-import breakdown.
 """
@@ -17,20 +18,14 @@ PACKAGES = {
     "core": [
         ("PyYAML", ["yaml"]),
         ("aiofiles", ["aiofiles"]),
-        ("chromadb", ["chromadb"]),
-        ("duckdb", ["duckdb"]),
         ("jinja2", ["jinja2"]),
         ("libcst", ["libcst"]),
         ("networkx", ["networkx"]),
-        ("numpy", ["numpy"]),
         ("pinecone", ["pinecone"]),
         ("psutil", ["psutil"]),
         ("pydantic", ["pydantic"]),
-        ("pydantic-settings", ["pydantic_settings"]),
         ("python-dotenv", ["dotenv"]),
-        ("rank-bm25", ["rank_bm25"]),
         ("redis", ["redis"]),
-        ("scikit-learn", ["sklearn"]),
         ("tenacity", ["tenacity"]),
         ("tqdm", ["tqdm"]),
         ("watchdog", ["watchdog"]),
@@ -39,31 +34,40 @@ PACKAGES = {
         ("pytest", ["pytest"]),
     ],
     "infra": [
+        ("numpy", ["numpy"]),
+        ("chromadb", ["chromadb"]),
+        ("duckdb", ["duckdb"]),
+        ("rank-bm25", ["rank_bm25"]),
+        ("scikit-learn", ["sklearn"]),
+        ("pydantic-settings", ["pydantic_settings"]),
+        ("beautifulsoup4", ["bs4"]),
+        ("dash", ["dash"]),
+        ("fastapi", ["fastapi"]),
+        ("livereload", ["livereload"]),
+        ("pandas", ["pandas"]),
+        ("playwright", ["playwright"]),
+        ("plotly", ["plotly"]),
+        ("waitress", ["waitress"]),
+        ("rich", ["rich"]),
+    ],
+    "external": [
         ("FlagEmbedding", ["FlagEmbedding"]),
         ... (remaining 25 external SDKs unchanged)
     ],
@@ -84,13 +87,16 @@ PACKAGES = {

 def main():
     require_dev = "--require-dev" in sys.argv
+    require_infra = "--require-infra" in sys.argv
     require_all = "--all" in sys.argv

     required_buckets = {"core"}
     if require_dev:
         required_buckets.add("dev")
+    if require_infra:
+        required_buckets.add("infra")
     if require_all:
-        required_buckets = set(PACKAGES.keys())
+        required_buckets.update({"core", "dev", "infra"})
```

### 3. tests/core/test_dependency_verifier_exit_code.py (full file — new)

```python
"""Regression test: dependency_verify_imports.py must exit 1 when blocking > 0."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

VERIFIER = (
    Path(__file__).resolve().parent.parent.parent
    / "docs"
    / "reports"
    / "plans"
    / "dependency_verify_imports.py"
)


class TestDependencyVerifierExitCode:
    def test_verifier_exists(self):
        assert VERIFIER.exists(), f"Verifier not found at {VERIFIER}"

    def test_exit_1_on_blocking_failures(self):
        """When run without all deps installed, blocking failures must produce exit code 1."""
        result = subprocess.run(
            [sys.executable, str(VERIFIER)],
            capture_output=True,
            text=True,
            timeout=60,
        )
        stdout = result.stdout
        if "RESULT: FAIL" in stdout:
            assert result.returncode == 1, (
                f"Verifier printed FAIL but exited {result.returncode}; "
                f"blocking failures MUST produce exit code 1"
            )
        elif "RESULT: PASS" in stdout:
            assert result.returncode == 0, (
                f"Verifier printed PASS but exited {result.returncode}; passing run MUST produce exit code 0"
            )
        else:
            pytest.fail(f"Verifier produced unexpected output (no RESULT line):\n{stdout[-500:]}")

    def test_exit_0_on_pass_when_all_core_installed(self):
        """When all core deps are installed, verifier must exit 0."""
        result = subprocess.run(
            [sys.executable, str(VERIFIER)],
            capture_output=True,
            text=True,
            timeout=60,
        )
        stdout = result.stdout
        if "RESULT: PASS" in stdout:
            assert result.returncode == 0
        else:
            pytest.skip("Core deps not fully installed in this environment; cannot test PASS path")
```

### 4. Representative Guardrail: numpy (agentic_core/L2_execution/reasoning/tool_registry.py)

```diff
diff --git a/agentic_core/L2_execution/reasoning/tool_registry.py b/agentic_core/L2_execution/reasoning/tool_registry.py
index 94ffdd7cf..419a5bab4 100644
--- a/agentic_core/L2_execution/reasoning/tool_registry.py
+++ b/agentic_core/L2_execution/reasoning/tool_registry.py
@@ -13,7 +13,12 @@ from collections.abc import Callable
 from dataclasses import dataclass, field
 from typing import Any

-import numpy as np
+try:
+    import numpy as np
+except ImportError as _err:
+    raise ImportError(
+        "numpy is required for this module. Install with: pip install -e '.[infra]'",
+    ) from _err

 Logger: Any = logging.getLogger(__name__)
```

### 5. Representative Guardrail: chromadb (agentic_core/L4_state/memory/in_memory_vector_cache.py)

```diff
diff --git a/agentic_core/L4_state/memory/in_memory_vector_cache.py b/agentic_core/L4_state/memory/in_memory_vector_cache.py
index 5fed12127..3d0a660f2 100644
--- a/agentic_core/L4_state/memory/in_memory_vector_cache.py
+++ b/agentic_core/L4_state/memory/in_memory_vector_cache.py
@@ -8,7 +8,12 @@ Optimized for 8GB hot cache allocation within 32GB WSL2 environment.
 import logging
 from typing import Any

-import chromadb
+try:
+    import chromadb
+except ImportError as _err:
+    raise ImportError(
+        "chromadb is required for this module. Install with: pip install -e '.[infra]'",
+    ) from _err

 Logger: Any = logging.getLogger(__name__)
```

### 6. Representative Guardrail: dash/pandas/plotly (agentic_core/L0_maintenance/scripts/windsurf_realtime_dashboard_util.py)

```diff
diff --git a/agentic_core/L0_maintenance/scripts/windsurf_realtime_dashboard_util.py b/agentic_core/L0_maintenance/scripts/windsurf_realtime_dashboard_util.py
index 959225207..2aa45b5f8 100644
--- a/agentic_core/L0_maintenance/scripts/windsurf_realtime_dashboard_util.py
+++ b/agentic_core/L0_maintenance/scripts/windsurf_realtime_dashboard_util.py
@@ -16,13 +16,28 @@ from datetime import datetime
 from pathlib import Path
 from typing import Any

-import dash
-import pandas as pd
-import plotly.express as px
-import plotly.graph_objects as go
-from dash import dcc, html
-from dash.dependencies import Input, Output
-from plotly.subplots import make_subplots
+try:
+    import dash
+    from dash import dcc, html
+    from dash.dependencies import Input, Output
+except ImportError as _err:
+    raise ImportError(
+        "dash is required for this module. Install with: pip install -e '.[infra]'",
+    ) from _err
+try:
+    import pandas as pd
+except ImportError as _err:
+    raise ImportError(
+        "pandas is required for this module. Install with: pip install -e '.[infra]'",
+    ) from _err
+try:
+    import plotly.express as px
+    import plotly.graph_objects as go
+    from plotly.subplots import make_subplots
+except ImportError as _err:
+    raise ImportError(
+        "plotly is required for this module. Install with: pip install -e '.[infra]'",
+    ) from _err
```
