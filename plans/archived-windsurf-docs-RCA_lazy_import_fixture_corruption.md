---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\RCA_lazy_import_fixture_corruption.md'
original_relative_path: 'RCA_lazy_import_fixture_corruption.md'
source_sha256: ae848dc1cea3dc1a61c91b153aae98b02f8569d76d255acfff4b52d535ed1998
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-03-31'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# RCA: Lazy Import Fixture Corruption

**Status: RESOLVED**
**Date: 2026-03-31**
**Severity: P0 — blocked all pre-commit hooks and CI pipelines**

## Summary

An automated "lazy import" converter corrupted 43+ test and source files across the repository, introducing syntax errors and runtime NameErrors that blocked the entire pre-commit suite and CI pipelines.

## Root Cause

A script intended to convert eager `from agentic_core.X import Y` statements into pytest session-scoped fixtures produced three categories of defects:

### Defect 1: Stray Closing Parentheses (17 files)
The converter left orphan `)` lines between fixture blocks and test code, causing `SyntaxError: unmatched ')'`.

### Defect 2: Invalid `as` Alias Syntax in Fixture Dicts (4 files)
The converter emitted `"ToolCall as PTCToolCall": ToolCall as PTCToolCall` inside `type('_Import', ...)` dict literals — `X as Y` is not valid Python outside `import` statements.

### Defect 3: Unconsumed Fixtures (26 files)
The converter created `@pytest.fixture(scope="session")` wrappers but **never updated the test bodies** to consume them as parameters. Tests still referenced imported names at module level where they are undefined, causing `NameError` at runtime.

### Defect 4: Broken `except` Indentation (2 files)
A separate "guardian" annotation tool corrupted `try/except ImportError` blocks by indenting `except ImportError:` inside the `try` body, causing `IndentationError`.

### Defect 5: Born-Corrupted Files (3 files)
`test_graphrag_e2e.py`, `test_lifecycle_contracts.py`, and `tools/adg/accelerators/__main__.py` were so heavily corrupted they had no clean git history to restore from and required full manual rewrites.

## Impact

- **Pre-commit hooks**: 100% blocked — `py_compile` check failed on every commit
- **CI pipelines**: All GitHub Actions workflows failed at syntax validation step
- **Test suite**: pytest collection failed with hundreds of import/syntax errors
- **Developer velocity**: Zero — no code could be committed

## Fix Applied

| Category | Files | Fix |
|----------|-------|-----|
| Stray `)` | 17 | Surgically removed orphan parens between fixture blocks and code |
| `as` alias bug | 4 | Regex replacement: `"X as Y": X as Y` → `"Y": Y` |
| Unconsumed fixtures | 26 | Replaced `type('_Import', ...)` fixtures with `try/except ImportError` direct imports |
| Broken `except` indent | 2 | Fixed indentation of `except ImportError:` blocks |
| Born-corrupted | 3 | Full manual rewrites with correct syntax and fixture patterns |
| `__future__` import order | 1 | Moved `from __future__ import annotations` before fixture block |
| Escape sequence warning | 1 | Changed `"def \w+"` to `r"def \w+"` |

## Verification

```
Full repo scan (excl archives) — 0 syntax errors
26/26 lazy fixture files: py_compile OK
17/17 stray paren files: py_compile OK
```

## Prevention

1. **Never run automated import converters without a rollback checkpoint**
2. **Always verify `py_compile` on every modified file before committing**
3. **The `type('_Import', ...)` fixture pattern is an anti-pattern** — if collection-time imports fail, use `try/except ImportError` at module level instead
4. **CI syntax gate** (`test_suite.yml` step 1) catches these — ensure it runs on all PRs
