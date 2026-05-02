---
trigger: model_decision
description: Use when considering `python -c "..."` invocations via run_command — quote-hazard patterns hang pwsh forever. Deterministic enforcement via `pre_run_gate.py` `_check_python_dash_c_quote_hazard`; this rule is the advisory detail with recovery patterns.
---

# `python -c "..."` Quote-Hazard Ban — Prevent pwsh Heredoc Hangs

> ⛔ **Never invoke `python -c "..."` in `run_command` when the body contains
> escaped double-quotes (`\"`), literal triple-quotes (`"""`), or escaped
> triple-quotes (`\"\"\"`).** On Windows / pwsh, the outer double-quoted
> string is parsed by the shell BEFORE Python sees it. These sequences
> confuse pwsh's tokenizer, leave the outer string unterminated, and the
> shell waits for the user to finish typing — Cascade's turn hangs forever.

## Failure Precedent (2026-04-26)

A regex one-liner of the form:

```
python -c "import re; pat = r\"\"\"class (Test\w+).*?:\s*(?:\"\"\"([^\"]+)\"\"\")?\"\"\"; ..."
```

…hung indefinitely. Root cause: pwsh interpreted `\"\"\"` as
`end-quote + start-quote + escape`, leaving the outer `"..."` open. The
secondary risk (regex backtracking on a 29 KB file) was real but secondary —
the shell-quoting failure was the actual hang.

## Forbidden Patterns

| Pattern | Why it hangs |
|---|---|
| `python -c "...\"\"\"..."` | Escaped triple-quote — pwsh tokenizer confusion |
| `python -c "...\"...\""` | Any escaped double-quote inside outer `"..."` |
| `python -c "...""""..."` | Literal triple-quote inside outer `"..."` |
| `python3 -c "..."` / `python.exe -c "..."` | Same — variant names of the same exec |
| `cd ... && python -c "...\"..."` | Same — chained after a separator |

## Required Recovery Patterns

When tempted to write `python -c "..."` with embedded quotes, do **one** of:

1. **Use `grep_search` / `read_file`** — no shell quoting involved at all.
   The original 2026-04-26 task ("find `class Test*:` with docstring") was a
   pure search, perfectly served by `grep_search`.
2. **Write a temp `.py` file**, then run `python tmp.py` — single-arg
   invocation, no quoting hazard. Delete the temp file when done.
3. **Use `mcp_python_repl` / native `run_code`** if available — sidesteps
   the shell entirely.
4. **Single-quote the outer body** — `python -c 'print("hi")'` — and avoid
   single-quote escapes inside.
5. **Base64-encode the body**:
   ```
   python -c "import base64,sys;exec(base64.b64decode('cHJpbnQoMSk='))"
   ```
   No double-quotes inside the body → no pwsh confusion.

## Enforcement

- **Advisory tier** (this rule, always_on) — shapes Cascade's command authoring
- **Deterministic tier** — `.windsurf/scripts/pre_run_gate.py`
  `_check_python_dash_c_quote_hazard()` blocks at exec time (exit 2)
- **Test coverage** —
  `tests/unit/ops_scripts/hooks/windsurf/test_pre_run_gate.py::TestCheckCommandPythonDashCQuoteHazard`
  (12 cases: blocks all hazardous variants, allows safe `-c` usage)

## Constitutional Tie-In

Sibling to constitutional **§0** (no PowerShell), **§14** (subprocess
timeout), and **§26** (no interactive pagers in `run_command`). Same root
concern: shell-pipeline behaviors that hang Cascade's turn forever, where
no Python-level `timeout=` can rescue it because the shell itself — not the
Python process — is the blocking entity.
