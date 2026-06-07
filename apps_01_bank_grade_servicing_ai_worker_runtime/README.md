# Bank-Grade Servicing AI Worker — Fee-Adjustment Review

A reference implementation of an **agentic control plane** for bank servicing. One
LLM-backed worker *proposes*; a deterministic control plane *disposes*; only a write
gate can *persist*. Built around a single use case — **Complaint-Sensitive Fee
Adjustment Review** — in production-pattern depth.

> **What this is:** a working reference implementation / prototype with synthetic
> data and a local model. No real customer data, no external services, no
> system-of-record integration. The *pattern* is production-grade; this is a
> reference build, not a deployed system.

## The thesis

> **The model proposes; the deterministic control plane disposes. The agent is the
> least-trusted component in the system.**

This maps directly onto model risk management (**SR 11-7**): the LLM is "a model"
under MRM, and the deterministic gates are the **controls** around it. The model
gets a *voice*, never *authority*.

## What's actually real

| Capability | Where | Proof |
|---|---|---|
| One **live model decision** | `agent.py` → local Qwen2.5-32B (vLLM) | record-replay fixtures; deterministic + hermetic tests |
| **Honest gates** — Exit derives the disposition from evidence, not the model's word, not a hardcoded branch | `engine.py` `_derive_initial_exit` | tests: a wrong or UNKNOWN model can't approve |
| **Gated durable write** — the only write path | `ledger.py` `commit_run` | refuses without a UWG-approved commit (`WriteGateError`) |
| **Eval suite** incl. prompt-injection | `eval_suite.py` | 7/7; injection caught by **both** model and gate |

## Architecture (v40 spine)

`U0` validate → `L1` frame ambiguity → `L0` deterministic route → `C0` evidence
custody → `PA` prompt/data boundary → **`L2` bounded model worker** → `L2.E4`
same-authority schema repair → **`Exit` one X3** → `HITL` (Exit escalation) →
**`UWG` write validation** → `L4` archive (after UWG only) → `L6` post-run learning.

> **Write law:** *L2 executes and seals. If a state change is possible, L2 emits only
> an inert `proposed_state_diff`. Exit decides whether that becomes a CommitRequest.
> UWG validates and commits. L4 stores.*
>
> **HITL is an Exit disposition, not a model action. UNKNOWN is never PASS.**

## The three scenarios (one workflow)

| Scenario | Situation | Terminal path |
|---|---|---|
| **A — Clean** | Eligible fee, no complaint, no prior adjustment | `X3C` → UWG → L4 write |
| **B — Complaint-sensitive** (hero) | Strong evidence, but complaint posture → human review | `X3B` → reviewer → re-clearance → `X3C` → UWG → L4 |
| **C — Conflicted** | Prior note vs. ledger disagree | `X3E_SAFE_ABSTAIN` (no write) |

`D`/`E` are adversarial **prompt-injection** eval cases (not shown in the UI).

## How to run

```bash
pip install -r requirements.txt

streamlit run app.py                 # the case walkthrough UI
python -m src.runtime.eval_suite     # the eval table (offline, replay)
python -m pytest tests -q            # 41 tests, fully offline/deterministic
```

The model decisions are served from recorded fixtures by default (no network). To
record/refresh them against the live local Qwen endpoint:

```bash
# requires the local vLLM container serving Qwen2.5-32B at QWEN_BASE_URL
QWEN_LIVE=1 python scripts/record_fixtures.py
```

## Local model

Local **Qwen2.5-32B-Instruct-AWQ** via vLLM (OpenAI-compatible, `localhost:8000`,
`max_model_len=24576`). Prompts are ~1k tokens (the worker sees a curated evidence
packet, never the firehose), so the context window is ~4× larger than needed.
On-prem inference means no customer data leaves the environment.

## Layout

```
app.py                 Streamlit case-walkthrough UI over the engine
scripts/record_fixtures.py   record live Qwen fixtures for replay
src/runtime/
  contracts.py         RunTrace, StageReceipt, GateVerdict, ExitDisposition, ...
  scenarios.py         the workflow's scenarios (A/B/C) + injection evals (D/E)
  agent.py             the ONE model call — bounded L2 worker, record-replay, fail-closed
  checks.py            deterministic evidence custody, Exit checks, UWG checks
  engine.py            deterministic stage-by-stage runner; gates are authoritative
  ledger.py            UWG-gated durable SQLite write (the only write path)
  eval_suite.py        golden-set eval runner + rates
  stages.py            per-stage metadata for the UI
tests/                 41 deterministic tests (engine, gate authority, ledger, eval)
```

## Disclaimer

Reference implementation with synthetic data and a local model. Not a deployed
production system, not connected to any system of record, not an autonomous refund
bot, not a customer-facing agent.
