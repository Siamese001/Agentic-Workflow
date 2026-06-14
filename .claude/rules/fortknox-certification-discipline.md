
<!-- Converted from `.claude/rules/fortknox-certification-discipline.md`. Original Cursor trigger: `model_decision`. -->

# DEPRECATED — Fort Knox certification arm decommissioned (2026-06-14)

> ⛔ Retired with constitutional **§32**. The bottom-up requirements-certification methodology
> (`RTC-REQ-*` evidence assertions → `compile_requirement_signoff.py` → Merkle/signature signoff,
> hostile verifier, mutation-rejection, positive-control canary) was abandoned: the
> `certification/evidence_assertions.jsonl` input no longer exists, the canonical contract-gate
> runner never invoked it, and nothing has been produced since early May 2026.

## What to do instead

The one durable principle — **certification/completion claims emerge only from a compiler or command,
never from hand-edited prose; no green theater** — is enforced by constitutional **§37**
(RCA-on-runtime-failure; no PASS over a failing body) and **`002-pass-blocked-proof-contract`**
(PASS is expensive; a marker is not proof). Apply those.

## Decommissioned with this rule (governance + enforcement arm)

- Constitutional §32 → RETIRED stub.
- Pre-commit gates T7s.1–.4 (`check_fortknox_*`, `check_apps_fortknox_signed_proof`) — removed.
- Hooks `pre_write_fortknox_guard.py` + `post_agent_fortknox_integrity_audit.py` — removed
  (the latter unwired from `post_agent_dispatch.py`).
- GitHub workflow `fortknox-nightly.yml` — already retired upstream (solo-workflow CI trim, 2026-06-14).
- Skill `fortknox-evidence` — flagged RETIRED (kept for historical reference).

## Deferred (separate teardown — NOT done here)

The runtime *machinery* is left in place; removing `agentic_core/` runtime needs its own boundary
audit and the apps_e2e tests are constitutionally protected:

- `agentic_core/L7_auditability/**`, `tools/cert/**`, `tools/certification/**`
- `tests/unit/apps_e2e/**`, `ops_scripts/ci/check_fortknox_*.py`, `verify_final_requirement_signoff_bundle.py`
- `.github/workflows/apps-fortknox-keyless-sign.yml` (W9 keyless signer — coupled to `test_w9_keyless_signature.py`)
- `config/certification/schemas/**`, and the frozen `artifacts/certification/**` historical bundle.
