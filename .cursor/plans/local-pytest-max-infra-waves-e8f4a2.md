---
plan_id: local-pytest-max-infra-waves-e8f4a2
plan_type: operations
---

# Local pytest — wave plan to maximize Ryzen + keep GPU path predictable

Run the test suite in **ordered waves** so AMD Ryzen parallelism is used efficiently, **serial** and shared-state tests are not corrupted by xdist, and the RTX 5090 either stays **out of the critical path** (typical pytest) or is **explicitly scheduled** when tests touch CUDA/torch/embeddings.

---

## Context (SCQA)

- **Situation** — Repo has two pytest entry shapes: `pytest.ini` for IDE-friendly defaults (no xdist in `addopts`), and `[tool.pytest.ini_options]` in `pyproject.toml` for **CI-style** runs (`-n 24 --dist=worksteal`, coverage). Local max-throughput runs should **opt in** to xdist explicitly.
- **Complication** — Oversubscribing **BLAS/OpenMP** inside each xdist worker collapses throughput. Tests marked `serial` must not run under xdist. Long GPU inference stacks (e.g. vLLM Docker) can compete for **RAM/PCIe** during large parallel pytest.
- **Question** — What wave sequence maximizes wall-clock signal without invalid results?
- **Answer** — Preflight thread caps → fast parallel slice → CI-parity xdist → optional dist-mode tuning → **serial-only** finale → optional JUnit merge for pass %.

---

## Infra assumptions (edit if different)

| Resource | Assumed | Plan behavior |
|----------|---------|----------------|
| CPU | AMD Ryzen (repo CI notes **9950X3D**; `-n 24` in `pyproject.toml`) | Default worker target **24** with `--dist worksteal` |
| GPU | RTX 5090 | Not used by most unit tests; **pause** heavy GPU services if RAM pressure |
| OS | Windows + optional WSL/Docker for vLLM | vLLM optional stop/start in Wave 1 |

---

## Evidence sources

| Source | Why |
|--------|-----|
| `pytest.ini` | Local defaults; documents `pytest -p xdist -n auto --dist=worksteal` |
| `pyproject.toml` `[tool.pytest.ini_options]` | CI addopts: `-n 24 --dist=worksteal`, coverage |
| Markers in `pytest.ini` | `slow`, `serial`, `integration`, etc. |

---

## Wave Structure

| Wave | Metric | Scope | Checkpoint | Tokens |
|------|--------|-------|------------|--------|
| Wave 1 | Preflight + env caps | Thread env, optional GPU/RAM relief | Env set; services noted | ~2K |
| Wave 2 | Fast parallel (breadth) | xdist, exclude slow, minimal reporting | Green path + rough pass % | ~4K |
| Wave 3 | CI-parity parallel | Match `pyproject` worker count + `worksteal` | Same pass bar as CI (coverage policy applies) | ~8K |
| Wave 4 | Dist-mode alternates (optional) | Fixture-heavy: `loadscope` / file-heavy: `loadfile` | Improved stability or time vs W3 | ~4K |
| Wave 5 | Serial + shared state | No xdist; `serial` marker / Redis-sensitive | Serial bucket green | ~3K |
| Wave 6 | Report merge (optional) | JUnit XML or scripted summary | pass/total % artifact | ~2K |

**Total: ~6 waves, ~23K tokens, GREEN**

---

## Out of scope

- Changing global `pytest.ini` / `pyproject.toml` defaults (this plan is **execution** only).
- Relaxing gates or skipping tests to “go green.”
- Notion Plans DB row (optional follow-up via `tools.notion.plan_creation_helper` if you track plans there).

---

## Global preflight (apply before Wave 2+)

**PowerShell (session):**

```powershell
$env:OMP_NUM_THREADS = "1"
$env:MKL_NUM_THREADS = "1"
$env:OPENBLAS_NUM_THREADS = "1"
$env:NUMEXPR_NUM_THREADS = "1"
```

Optional: stop GPU-heavy Docker only if you see **host RAM** or **PCIe** contention during Wave 3, e.g. `docker stop local-qwen-vllm` (see `.cursor/rules/local-llm-wsl2-gpu.mdc`). Start again after pytest if you need the endpoint.

---

## Execution plan

### Wave 1 — Preflight + service posture

| Step | Action | Done when |
|------|--------|-----------|
| 1.1 | Set thread caps (commands above) | `$env:OMP_NUM_THREADS -eq '1'` |
| 1.2 | Choose repo root: `cd C:\Git\Agentic-Workflow-FRESH` | `pytest --version` works |
| 1.3 | Decide vLLM/container posture for the run | Document in run notes (up/down) |

---

### Wave 2 — Fast parallel slice (max throughput, low noise)

**Intent:** Maximum Ryzen utilization for a **representative** pass without paying coverage cost.

```powershell
cd C:\Git\Agentic-Workflow-FRESH
pytest -p xdist -n logical --dist=worksteal -m "not slow" --tb=no -q
```

**Checkpoint:** Final line shows pass/fail counts; use as early health signal.

---

### Wave 3 — CI-parity parallel (authoritative local gate)

**Intent:** Same parallelism class as CI (`-n 24 --dist=worksteal`) with coverage options from `pyproject.toml`.

Run from repo root **explicitly merging** ini (pytest reads both `pytest.ini` and `pyproject` — if your environment loads CI addopts via `-c` or `python -m pytest`, prefer **one** SSOT to avoid duplicate flags). Pragmatic approach:

```powershell
cd C:\Git\Agentic-Workflow-FRESH
python -m pytest --cov=agentic_core --cov-branch --cov-report=term-missing --cov-report=html:reports/coverage_html -ra -v -n 24 --dist=worksteal --timeout=180
```

Adjust `-n 24` down if **RAM** pressure or **disk** thrash (watch Task Manager).

**Checkpoint:** Exit code 0; coverage gate satisfied if you keep `--cov-fail-under=100` from CI (add if you need strict parity).

---

### Wave 4 — Alternate `--dist` modes (only if Wave 3 shows fixture/file isolation pain)

Per `pyproject.toml` comments:

| Mode | When | Command fragment |
|------|------|------------------|
| `loadscope` | Fixture-heavy suites | `--dist loadscope -n 18` |
| `loadfile` | File-level isolation wins | `--dist loadfile -n 20` |

Example rerun for a **directory** that flaked under `worksteal`:

```powershell
pytest -p xdist -n 18 --dist=loadscope -v tests\unit\some_hot_area
```

**Checkpoint:** Flaky setup errors reduced vs Wave 3 for that scope.

---

### Wave 5 — Serial and non-xdist-safe tests

**Intent:** Validate `@pytest.mark.serial` and any shared Redis/global state tests.

```powershell
pytest -n 0 -m serial -v
```

If collection excludes non-marked serial behaviors, use targeted paths from your last failure list instead of broad `-m serial`.

**Checkpoint:** Serial bucket passes independently of xdist.

---

### Wave 6 — Pass/fail % artifact (optional)

**Intent:** Deterministic totals for spreadsheets/CI comparison.

```powershell
pytest -p xdist -n logical --dist=worksteal --junitxml=artifacts\pytest\junit-max-infra.xml --tb=no
```

**Checkpoint:** `artifacts\pytest\junit-max-infra.xml` exists; compute `passed/(passed+failed+errors)` with your XML tool of choice.

---

## Gap register

| Gap ID | Risk | Mitigation |
|--------|------|------------|
| GAP-1 | Duplicate `addopts` / conflicting `-n` | Prefer explicit CLI for Wave 3; avoid nesting config files without checking merged args |
| GAP-2 | xdist + BLAS without thread caps | Always Wave 1 env vars |
| GAP-3 | IDE Test Explorer spawning many workers | Use terminal runs for this plan; keep IDE discovery separate |

---

## Definition of done

- Waves 1–3 completed once per “full audit” cycle; Waves 4–6 as needed.
- Serial wave (5) green before declaring shared-state safe.
- Optional JUnit path recorded if you need pass %.

---

## Notion / plan hygiene (optional)

If you track plans in Notion Plans DB, create/update the row with **Plan File Path** = `.cursor/plans/local-pytest-max-infra-waves-e8f4a2.md` using `tools.notion.plan_creation_helper.create_plan_in_notion` (filesystem remains SSOT).
