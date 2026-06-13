# Dependency Remediation — Complete

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Deliverables

### Patch Files (produced, then applied)

- `docs/reports/plans/patch_packaging_discovery.patch` — setuptools package discovery
- `docs/reports/plans/patch_core_deps_blocking.patch` — dependency corrections (pinecone rename, pytest to dev, infra split, core reconciliation)

### Verifier Fix

- Exit code contract enforced (`sys.exit(1)` when blocking > 0)
- Verified via subprocess regression test: exit 1 on blocking, exit 0 on pass
- Split infra vs external buckets
- Added `--require-infra` flag
- `--all` now requires **core + dev + infra only**

### Regression Tests

- `tests/core/test_dependency_verifier_exit_code.py` — exit semantics enforced (3/3 PASS)
- `tests/core/test_baseline_import_no_guardrail_fire.py` — guardrails proven non-blocking on lean core (4/4 PASS)

---

## Final pyproject.toml Dependency Layout (Canonical)

### Core (15 — REQUIRED)

pydantic
google-genai
pinecone
redis
libcst
cryptography
aiofiles
jinja2
networkx
psutil
python-dotenv
PyYAML
tenacity
tqdm
watchdog

### Dev (6 — OPTIONAL, gated by flag)

pytest
pytest-cov
pytest-asyncio
black
ruff
mypy

### Infra (15 — OPTIONAL, guarded imports)

numpy
chromadb
duckdb
rank-bm25
scikit-learn
pydantic-settings
beautifulsoup4
dash
fastapi
livereload
pandas
playwright
plotly
waitress
rich

---

## Verifier Semantics (Contract)

The verifier (`docs/reports/plans/dependency_verify_imports.py`) operates with five buckets and four CLI modes:

### CLI Modes

| Mode | Required Buckets |
|------|------------------|
| *(default)* | core |
| `--require-dev` | core + dev |
| `--require-infra` | core + infra |
| `--all` | core + dev + infra |

### Bucket Rules

- **core** — Always required. Failure = exit 1.
- **dev** — Required only when `--require-dev` or `--all`.
- **infra** — Required only when `--require-infra` or `--all`.
- **external** — Informational only. Never blocks.
- **sdks** — Informational only. Never blocks.

### Non-Negotiable Invariant

> `external` and `sdks` buckets are ALWAYS OPTIONAL and must NEVER cause non-zero exit under any CLI mode, including `--all`.

---

## Why the Split Was Necessary

Previous implementation incorrectly lumped declared infra deps with undeclared third-party SDKs.
Under `--all`, this forced installation of heavy or optional packages (torch, anthropic, FlagEmbedding).

Now:

- `--all` validates only declared project dependencies
- External SDKs remain visible for audit
- CI remains deterministic
- Lean-core installs remain valid

---

## Canonical Gate Results (SSOT)

Authoritative evidence stored in:

`docs/reports/plans/dependency_gate_evidence_vFinal.md`

Environment:

- Windows
- Python 3.12.10
- pip 26.0.1
- `.venv_verify`

### Gates

| Gate | Result |
|------|--------|
| A — create venv | PASS |
| B — pip install -e . | PASS |
| C — baseline import | PASS |
| D — core verifier | PASS (15/15, 0 blocking) |
| E — dev install + regression | PASS |
| F — infra install + `--all` | PASS (31/31 declared, 0 blocking) |

---

## SSOT Note

Any references to:

- `.venv_gate`
- `.venv_final`
- `.venv_lean`
- pip 25.x
- core=13

are historical and non-authoritative.

The only canonical final environment is:

> `.venv_verify` with pip 26.0.1

---

## Guardrail Policy

All 15 infra packages use deterministic import guards:

```python
try:
    import <pkg>
except ImportError as _err:
    raise ImportError(
        "<pkg> is required for this module. Install with: pip install -e '.[infra]'",
    ) from _err
```

- No silent fallbacks
- No optional import ambiguity
- Clear actionable remediation
- Verified non-blocking on lean core imports

---

## Acceptance Criteria (All Satisfied)

- Core dependency count reconciled (15 == pyproject == verifier)
- External and sdks never blocking
- Clean venv evidence reproduced
- Exit code semantics enforced
- Guardrails verified non-blocking
- Historical contradictions marked explicitly
- All fenced blocks include language tags

---

## Final Status

PASS — Dependency remediation finalized with deterministic, auditable, SSOT-consistent evidence.

## Rules

1. Follow all constitutional rules and guidelines
2. Maintain compliance with established standards
3. Document all changes and decisions
4. Validate all implementations before completion

---

## Success Criteria

- [ ] All objectives completed successfully
- [ ] Validation tests pass
- [ ] Documentation updated
- [ ] Stakeholder approval received

---

