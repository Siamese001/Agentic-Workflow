# ADR-038 — Eval Trial Isolation Contract

- Status: Accepted (implemented)
- Date: 2026-04-23
- Deciders: cascade (author), humans-in-loop pending
- Related: ADR-028 (eval/SL publisher boundary), ADR-032 (LLM-judge hardening), ADR-036 (runtime trace grader), ADR-037 (trajectory metrics)
- Impact Layers: L6 (Observer), L5 (Safety plane), system_learning pipeline

Current-state note (2026-06-15): implemented via isolated eval fixtures in `tests/eval/conftest.py`, the eval harness workflow, and per-trial workdir/cache/network controls.

## Context

Anthropic's eval guidance (step 4 of the roadmap in *Demystifying evals for
AI agents*) observes that "correlated failures" and "artificial inflation"
arise when eval trials share environment state — leftover files, cached
data, git history, or resource exhaustion. In this repo, the capability and
regression suites land via `tools/eval/run_capability_regression.py`
(W1.2); without an explicit trial-isolation contract, pytest fixture state
and artifact directories can bleed across trials and silently move scores.

## Decision

Every eval trial MUST execute in an isolated workspace with the following
contract:

1. **Clean working directory per trial.** `tests/eval/conftest.py` provides
   a `per_trial_workdir` fixture that yields a unique `tmp_path` subtree
   for each trial and asserts empty-on-entry.
2. **No shared mutable fixtures across trials.** Any fixture used by an
   eval trial MUST be declared `scope="function"`. Module/session scope is
   forbidden inside `tests/eval/`.
3. **Artifact directory is trial-local.** Eval trials must write to
   `tmp_path / "artifacts"` — never to the repo-level `artifacts/eval/`.
   The runner aggregates results from trial outputs post-run.
4. **Env-var whitelist.** The conftest wipes env vars not on an explicit
   whitelist at trial start so production secrets cannot influence an eval
   score.
5. **No network by default.** Eval trials run with a monkey-patched DNS
   resolver that fails any outbound resolution unless the trial is
   explicitly marked `@pytest.mark.eval_network`.

## Consequences

- Positive: eliminates one class of hard-to-reproduce eval flake; makes
  "why did this score move?" answerable from the trial log alone.
- Negative: trials that legitimately depend on cached artifacts must
  explicitly opt in via `@pytest.mark.eval_cache_allowed`, which is more
  verbose than today.
- Neutral: aligns with Anthropic and Google Cloud best practice; no
  behavior change for non-eval tests.

## Implementation

- New file: `tests/eval/conftest.py` (W4.2).
- New fixture: `per_trial_workdir`.
- New marker: `eval_network` (must be added to `pytest.ini` addopts).
- CI gate: extend `.github/workflows/eval-harness.yml` to assert the
  conftest is present and non-empty before running the suite.

## Alternatives Considered

- **Rely on `tmp_path` alone** — rejected because it does not guard env
  vars or network access.
- **Run each trial in a container** — rejected for W4.2 scope; adds CI
  cost and Windows-host complexity. Reconsider when capability suites
  cross 1000 trials.
