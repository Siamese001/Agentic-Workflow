# Dependency Audit — Full Execution Log (vFinal)

## SSOT Status

**Canonical Final Environment**

- Windows
- Python 3.12.10
- pip 26.0.1
- Clean venv: `.venv_verify`

All FINAL gate results in this document originate from `.venv_verify`.

Any references to:
- `.venv_gate`
- `.venv_final`
- `.venv_lean`
- pip 25.x
- core=13

are explicitly marked HISTORICAL and are non-authoritative.

---

# PHASE 4 — CANONICAL REGENERATION (.venv_verify)

---

## Gate A — pip Version

```text
> .venv_verify\Scripts\python.exe -m pip -V
pip 26.0.1 from C:\Git\Agentic-Workflow\.venv_verify\Lib\site-packages\pip (python 3.12)
```

Exit code: 0

---

## Gate B — Lean Core Install

```text
> .venv_verify\Scripts\pip.exe install -e .

Successfully installed 46 packages
```

Exit code: 0

---

## Gate C — Baseline Import Surface

```text
> .venv_verify\Scripts\python.exe -c "import agentic_core; import apps_shared; print('Gate C PASS')"
Gate C PASS
```

Exit code: 0

---

## Gate D — Verifier (Default: core required)

```text
> .venv_verify\Scripts\python.exe docs/reports/plans/dependency_verify_imports.py

[core ] [REQ] dist=PyYAML              OK
[core ] [REQ] dist=aiofiles            OK
[core ] [REQ] dist=cryptography        OK
[core ] [REQ] dist=google-genai        OK
[core ] [REQ] dist=jinja2              OK
[core ] [REQ] dist=libcst              OK
[core ] [REQ] dist=networkx            OK
[core ] [REQ] dist=pinecone            OK
[core ] [REQ] dist=psutil              OK
[core ] [REQ] dist=pydantic            OK
[core ] [REQ] dist=python-dotenv       OK
[core ] [REQ] dist=redis               OK
[core ] [REQ] dist=tenacity            OK
[core ] [REQ] dist=tqdm                OK
[core ] [REQ] dist=watchdog            OK

Bucket Summary:
  bucket   required?    OK  FAIL  SKIP  verdict
  core     yes          15     0     0     PASS
  dev      no            0     0     1     PASS
  infra    no            0     0    15     PASS
  external no            2     0    22     PASS
  sdks     no            0     0     3     PASS

RESULT: PASS (all required imports OK)
```

Exit code: 0

---

## Gate E — Dev Install + Regression Tests

```text
> .venv_verify\Scripts\pip.exe install -e ".[dev]"

Successfully installed pytest pytest-cov pytest-asyncio black ruff mypy
```

```text
> .venv_verify\Scripts\pytest.exe tests/core/test_dependency_verifier_exit_code.py
3 passed in 2.17s
```

```text
> .venv_verify\Scripts\pytest.exe tests/core/test_baseline_import_no_guardrail_fire.py
4 passed in 0.02s
```

Exit code: 0

---

## Gate F — Infra Install + Verifier --all

```text
> .venv_verify\Scripts\pip.exe install -e ".[infra]"

Successfully installed numpy chromadb duckdb rank-bm25 scikit-learn pydantic-settings beautifulsoup4 dash fastapi livereload pandas playwright plotly waitress rich
```

```text
> .venv_verify\Scripts\python.exe docs/reports/plans/dependency_verify_imports.py --all
```

```text
Bucket Summary:
  bucket   required?    OK  FAIL  SKIP  verdict
  core     yes          15     0     0     PASS
  dev      yes           1     0     0     PASS
  infra    yes          15     0     0     PASS
  external no            4     0    20     PASS
  sdks     no            2     0     1     PASS

RESULT: PASS (all required imports OK)
```

Exit code: 0

---

# HISTORICAL SECTIONS (Retained for Traceability Only)

---

## HISTORICAL — .venv_final (Obsolete)

> This environment predates final SSOT reconciliation.
> Uses pip 25.x and earlier core counts.
> Not authoritative.

Legacy output retained for audit trail only.

---

## HISTORICAL — .venv_lean (Supporting Only)

> Used to validate guardrail non-fire behavior.
> Not a canonical final environment.

```text
> .venv_lean\Scripts\pytest.exe tests/core/test_baseline_import_no_guardrail_fire.py
4 passed
```

Exit code: 0

---

# Verifier Semantics Confirmation

- `core` required in all modes
- `dev` required under `--require-dev` or `--all`
- `infra` required under `--require-infra` or `--all`
- `external` NEVER blocking
- `sdks` NEVER blocking

Invariant:

> external and sdks buckets are informational only and must never cause non-zero exit.

---

# Final Canonical State

- core = 15
- dev = 6
- infra = 15
- external = informational only
- sdks = informational only
- pip = 26.0.1
- Environment = `.venv_verify`
- All gates exit 0

---

# Final Status

PASS — Deterministic SSOT evidence complete and normalized.

## Findings

[Document key findings from the investigation]

---

## Evidence

[Provide evidence supporting the findings]

---

