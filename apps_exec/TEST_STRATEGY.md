# TEST STRATEGY — apps_exec: Executive Brief Generator

## Philosophy

All tests are deterministic. No LLM calls. No network I/O. No filesystem side effects
except where tests explicitly use `tmp_path` fixtures. Every test asserts on concrete
values — never on "output is non-empty unless I'm okay with empty."

---

## Test Layers

### Layer 1: Unit Tests (`tests/unit/apps_exec/test_exec_pipeline.py`)

| Test Class                    | Coverage Target                                           |
|-------------------------------|-----------------------------------------------------------|
| `TestExecAgentSpecs`          | Config loading, persona validation, empty personas raises |
| `TestIngestionEngine`         | Missing dirs, file discovery, oversized skip, total_chars |
| `TestCapabilityExtractionEngine`| Known patterns, deduplication, empty corpus           |
| `TestBriefAssemblyEngine`     | Sections per persona, non-empty bodies, why_this_matters |
| `TestStyleGateValidator`      | Clean pass, buzzword detection, empty body block         |
| `TestExecOrchestrator`        | Dry-run status, sections in dry-run, trace propagation   |
| `TestRunSummary`              | `to_dict()` completeness                                 |

### Layer 2: Integration Smoke Test (future)

```bash
python -m apps_exec --audience recruiter --dry-run
# Assert: exit code 0, JSON output status=dry_run
```

### Layer 3: Acceptance Test Matrix

| Scenario                              | Expected Outcome                           |
|---------------------------------------|--------------------------------------------|
| `--audience recruiter --dry-run`      | Status `DRY_RUN`, 0 artifacts, >0 sections |
| `--audience cto`                      | Status `COMPLETE`, `.md` written           |
| Section with absolute claim "always"  | Gate BLOCK, exit 1                         |
| `--audience board --json-output`      | JSON printed, `status` key present         |

---

## Run Commands

```bash
# Unit tests only
pytest tests/unit/apps_exec/ -v

# With coverage
pytest tests/unit/apps_exec/ --cov=apps_exec --cov-report=term-missing

# Specific test
pytest tests/unit/apps_exec/test_exec_pipeline.py::TestStyleGateValidator -v
```

---

## Coverage Targets

| Module                              | Target Coverage |
|-------------------------------------|-----------------|
| `config/agent_spec_config.py`       | 90%             |
| `engines/ingestion_engine.py`       | 85%             |
| `engines/capability_extraction_engine.py` | 80%       |
| `engines/brief_assembly_engine.py`  | 85%             |
| `validators/style_gate_validator.py`| 90%             |
| `reasoning/ExecOrchestrator.py`     | 80%             |

---

## Forbidden Test Patterns

- **No mocking the filesystem** except via `tmp_path` pytest fixture.
- **No mocking the `StyleGateValidator`** — always use real validation.
- **No asserting `len(output) > 0`** as sole assertion — assert specific fields.
- **No `assert True`** placeholder tests.
- **No tests that depend on wall-clock time** — all timestamps are fixed or not tested.

---

## Regression Test Requirement

For every BLOCK gate violation discovered, a regression test must be added.
Test must demonstrate the specific input that causes the violation.
Test must verify the violation's `rule_id` is present in the gate result.

---

## CI Gate

Tests must pass with exit code 0 before any PR touching `apps_exec/` is merged.
Coverage below 80% on `validators/style_gate_validator.py` → CI blocks.
