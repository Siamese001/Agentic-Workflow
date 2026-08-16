# Apps_qna — App Customization Rules

> `apps_qna` owns Interview Q&A customization. Follow the shared [App Agent Contract](../apps_shared/APP_AGENT_CONTRACT.md) for ownership, core boundaries, U0 package structure, checklist, and related authority.

## Local ingress

- Ingress contract: `contracts/`, `config/domain_contract/`
- Schemas: `schemas/`
- App tests: `tests/unit/apps_qna/`, `tests/_apps_contract/`

## Core Bindings Status

`apps_qna` currently has **no temporary bindings** in `agentic_core/`. All customization happens through:
- `apps_qna/u0_intake.py` — U0-level intake (app-owned)
- `apps_qna/l0_router.py` — L0 routing (app-owned)
- `apps_qna/l1_planner.py` — L1 planning (app-owned)
- `apps_qna/cert/fec_producer.py` — FEC production (app-owned)

This is the **target state** — app logic stays in `apps_qna/`, core provides generic enforcement.
