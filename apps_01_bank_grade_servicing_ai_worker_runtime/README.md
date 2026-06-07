# Fee-Adjustment Mechanics Lab

A **private mechanics lab**, not an interview demo. It runs **one**
production-believable bank-grade AI worker workflow end to end so you can study the
mechanics, see who holds authority at each point, see what is forbidden, inspect the
receipt each stage emits, replay the trace, and explain the run from memory.

> **Framing:** fictional internal analyst-assist / case-review workbench for a
> regional bank. No real customer data, no external services, no production or
> institutional claims.

## What it does

It simulates **Complaint-Sensitive Fee Adjustment Review**: a servicing analyst
reviews a customer fee-adjustment request (monthly maintenance, service, or
card-related fee). The runtime assembles evidence, identifies complaint
sensitivity, generates a bounded recommendation, prepares an inert
`proposed_state_diff` when eligible, escalates to human review when required, and
routes any eligible write through a durable write gate.

Every screen reads from the **same RunTrace**. Every stage emits a receipt. Every
action updates the trace deterministically. There are no placeholder screens and no
interview-coaching UI — the lab asks **you** to explain the mechanics.

## How to run

```bash
# from this directory
pip install -r requirements.txt
streamlit run app.py
```

The deterministic engine has **no dependencies** and can be exercised directly:

```bash
python -c "from src.runtime import run_workflow; t=run_workflow('A'); print(t.final_exit)"
python -m pytest tests -q
```

## The three fee-adjustment scenarios

| Scenario | Situation | Terminal path |
|----------|-----------|---------------|
| **A — Clean Fee Adjustment** | Eligible service fee, no prior adjustment, no complaint, evidence PASS | Exit `X3C_COMMIT_REQUEST_TO_UWG` → UWG → L4 archive |
| **B — Complaint-Sensitive** | Evidence mostly strong, but complaint posture requires human review | Exit `X3B_ESCALATE_HITL` → reviewer decision → re-clearance → `X3C` → UWG → L4 (if approved) |
| **C — Conflicted Prior Adjustment** | Prior note says adjustment granted; ledger does not confirm; evidence CONFLICTED | Exit `X3E_SAFE_ABSTAIN` (no UWG, no L4) |

## v40 write law (verbatim)

> **L2 executes and seals. If a state change is possible, L2 emits only an inert
> proposed_state_diff. Exit decides whether that becomes a CommitRequest. UWG
> validates and commits. L4 stores.**

- **HITL rule** — *HITL is an Exit disposition, not a model action.*
- **Learning rule** — *L6 learns only after the current run boundary.*

## v40 layer map

`U0` validate → `L1` frame ambiguity → `L0` deterministic route → `C0` evidence
custody → `PA` prompt/data boundary → `L2` bounded execution → `L2.E4`
same-authority schema repair only → `Exit` one X3 → `HITL` Exit escalation path →
`UWG` write validation → `L4` archive after UWG only → `L6` post-run learning after
boundary only. `L5` is cross-cutting certification; `00C` are the runtime gates.

**Runtime gate verdicts:** `PASS` · `STOP` · `ESCALATE` · `ABSTAIN` · `REROUTE` ·
`UNKNOWN`. **Hard rule: UNKNOWN is never PASS.**

## Layout

```
app.py                 Streamlit UI (15 screens) over the engine
src/runtime/
  contracts.py         RunTrace, StageReceipt, GateVerdict, ExitDisposition, ...
  scenarios.py         the three deterministic scenarios + evidence packets
  stages.py            per-stage teaching metadata + explain-back prompts
  engine.py            deterministic stage-by-stage runner (the mechanics)
tests/                 deterministic acceptance tests
```

## Disclaimer

Fictional demo for personal understanding. No real customer data. No external
services. No production release claim. No system-of-record writer. Not an
autonomous refund bot and not a customer-facing agent.
