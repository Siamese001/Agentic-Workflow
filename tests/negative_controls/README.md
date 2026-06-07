# Negative Control Library

Each gate must demonstrably **fail closed** on a known-bad input. This
directory holds one or more negative tests per gate, asserting that the
gate exits non-zero (or rejects the bad input via its documented contract)
when fed an input it must reject.

Covers W2 of plan
[`docs/archive/windsurf/legacy-tree/plans/assurance-p1-gates-ab4758.md`](../../docs/archive/windsurf/legacy-tree/plans/assurance-p1-gates-ab4758.md).

## Why a separate dir?

Unit tests prove a function returns the right value on good input.
Negative-control tests prove the **gate-level CLI** rejects bad input —
this is the assurance dimension #5 (fail-closed verification). They are
intentionally redundant with unit tests because they exercise the
gate-as-shipped, not the gate's internals.

## Layout

```
tests/negative_controls/
  README.md                          # this file
  __init__.py
  conftest.py                        # `run_gate` helper
  test_constitutional_negatives.py   # parametrized table — primary suite
```

## Adding a new negative test

Add a row to `_NEGATIVES` in `test_constitutional_negatives.py`::

    NegativeControl(
        gate="<repo-relative path to gate script>",
        case_id="<unique-slug>",
        stdin_payload=<dict | None>,    # None = no stdin
        args=<list[str]>,                # extra CLI args
        cwd_files=<dict[str, str] | None>,  # files to materialize in temp cwd
        expect_nonzero=True,
    )

The harness will execute the gate as a real subprocess against your fixture
and assert the documented fail-closed behavior.

## Running

```
python -m pytest tests/negative_controls/ -v
```

## Constitutional Tie-In

§4 — "CI enforces all of this." Every gate listed in `run_contract_gates.py`
should have at least one negative-control test here proving it actually
blocks bad input. A green run_contract_gates.py with no negative-control
suite is a "vacuous gate" — passes because nothing exercises its blocking
path.
