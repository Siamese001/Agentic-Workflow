# apps_rg — Threat Model

## Scope

`apps_rg` ingests **externally-sourced user content** (candidate profiles, job descriptions, company briefs, CLI args, interactive-wizard input) and produces generated text via an LLM-backed HOP pipeline. This creates an attack surface distinct from pure-compute apps.

## Two prompt-injection concepts (definitive)

| Concept | What it is | Where defended | Threat IDs below |
|---|---|---|---|
| **Instructional prompt injection** (governed composition) | Insertion of: goal, success criteria, task mode, scope, efficiency constraints, evidence binding, reasoning controls, safety rails, output schema, error format, minimality rules. | PA Prompt Assembly (apps_rg local PA + agentic_core mixin corpus). Defense is **correctness of composition**, not detection. | covered by §3.1–§3.4 of `PROMPT_BOUNDARY_CONTRACT.md` |
| **Prompt injection defense** (boundary protection) | Detection / fencing / neutralization / quarantine / rejection of untrusted content trying to override system / developer / policy / route / tool / provider / model / schema / output-format / sandbox / write-authority / HITL controls. | PA airlock layer (U0 / C0 / tool-model / human-reentry) + `agentic_core/prompt_governance/security/`. | T1, T2 (revised), T7 (new) |

*Instructional injection is a governed composition pattern. Prompt injection defense is a boundary protection pattern. They are related but not the same.*

See `apps_rg/PROMPT_BOUNDARY_CONTRACT.md` for the slot authority map (S0 – R0), airlock invariants, and receipt contract.

## Assets

| Asset | Sensitivity | Integrity requirement |
|---|---|---|
| Candidate profile (PII) | High | Must not leak into shared caches or other runs |
| Job description (public or private) | Medium | Provenance must be preserved in evidence packet |
| Generated résumé | Medium | Must be reproducible from inputs + evidence |
| Replay keys | High | Must not be `_noop`-silenced (governance xfail tracks) |
| Executor auth credentials | Critical | Scoped; never logged in full |

## Threat actors

1. **Malicious input author** — crafts profile/JD with prompt injection
2. **Compromised executor** — Anthropic / vLLM gateway returns adversarial completion
3. **Insider with code access** — inserts logic that bypasses hardened strategies
4. **Dependency confusion** — upstream package hijack (agentic_core, apps_shared)

## Threats and mitigations

### T1 — Prompt injection via profile / JD / company brief / CLI args

- **Threat:** untrusted content (résumé, JD, brief, `--manual-brief`, `--target-*`, wizard input) attempting to override S0 / D0 / I0 / R0 authority slots, change provider/model, exfiltrate credentials, or alter output schema.
- **Mitigation:** PA airlock layer applied at slot composition — U0 user-text airlock + C0 evidence airlock (per `PROMPT_BOUNDARY_CONTRACT.md` §3). Each airlock emits a typed receipt and refuses `UNKNOWN` as PASS. `_assert_artifact_matches_company` (`apps_rg/__main__.py:110-149`) is an orthogonal cross-company contamination guard, **not** a substitute for the airlock.
- **Residual risk:** novel injection patterns may slip through — mitigated by HOP-4 fact-check + HOP-5 bullet diversity gate + W6 anti-bypass scanner.
- **Status (W1):** airlocks declared in `PROMPT_BOUNDARY_CONTRACT.md` are wired in W4 of plan `apps-rg-spine-hardening-7e3b9c`.

### T2 — Executor output contamination

- **Threat:** Anthropic / vLLM / OpenAI / Vertex returns adversarial completion that attempts to widen authority, modify route, change tool, alter schema, grant write permission, bypass HITL, or commit durable state.
- **Mitigation:** PA tool/model output airlock (`PROMPT_BOUNDARY_CONTRACT.md` §3.3) — model output is **data/proposal only**; downstream HOP-4 fact-check + HOP-5 bullet diversity gate + R0 schema binding + Runtime Gates emit live `GateVerdict` records before Exit consumes the sealed artifact.
- **Residual risk:** strategy must be kept in sync with LLM behavioral drift — calibration cadence in `/author-gate-calibration-report`.
- **Note on dormant scaffold:** four `Hardened*ExecutorStrategy.py` files exist under `enforcement/`, `reasoning/`, `validators/enforcement/`, and `engines/hardened_gemini_executor.py`. Per W1 ADG audit (`docs/reports/apps_rg/spine_boundary_findings_20260509_055000.md` §4B) **these have zero module fan-in and are NOT part of the active runtime path**. The active executor surface is `apps_rg/integrations/llm_client.py` (sanctioned `infrastructure.sdks_mcps` shim) consumed by the canonical L2 step adapters in `apps_rg/l2_recipe/steps.py`. Dormant cleanup is tracked separately.

### T3 — PII leakage across runs

- **Mitigation**: No candidate profile data persists in shared caches (`GlobalcacheStrategy` partitions by run-id). Evidence packets are per-run with deterministic hash.
- **Residual risk**: Log aggregation may capture PII — addressed by log-redaction middleware (tracked in plan `apps-rg-governed-runtime-b8d4f1.md`).

### T4 — Replay-key silencing

- **Known gap**: `bootstrap_runtime.py` currently contains `emit_replay_key = _noop`. This silences replay receipts in production, breaking non-repudiation.
- **Tracked as**: governance xfail `tests/governance/test_no_lifecycle_noop_shims_in_production.py`
- **Remediation**: plan `apps-rg-governed-runtime-b8d4f1.md` Wave 7 P7.2

### T5 — Dependency confusion

- **Mitigation**: All dependencies pinned in `uv.lock`. CI gate rejects unpinned versions.
- **Residual risk**: Transitive dependency updates — mitigated by lockfile refresh cadence.

### T6 — Direct executor bypass

- **Threat:** producer code (engines / scripts / utils) calls a provider SDK directly with raw prompt strings, bypassing PA composition and the airlock layer.
- **Mitigation:** Architectural invariant — every model-backed step must consume a `PA_L2_HANDOFF_READY` `AppsRgCompiledPromptArtifact` (apps_rg local PA) **or** a `PromptEnvelope`-derived `AnthropicRagPayload` (legacy PA bridge per `AGENTIC_SPINE.md > Dual PA Topology`). `_PAGuard` (`apps_rg/l2_recipe/steps.py:27-104`) fail-closes when the artifact is missing. The W6 anti-bypass scanner (`ops_scripts/ci/check_apps_rg_pa_boundary.py`, plan `apps-rg-spine-hardening-7e3b9c`) enforces this at CI time.
- **Active LLM call path:** `l2_recipe/steps.py` → `apps_rg/scripts/generate_resume.py` → `apps_rg/engines/resume_orchestrator_engine.py` → `apps_rg/integrations/llm_client.py` (sanctioned `infrastructure.sdks_mcps` shim). The narrative-pipeline path uses the LEGACY PA bridge with `pa_local.capture_prompt_bom` instrumentation.

### T7 — User text or retrieved content promoted to authority slot

- **Threat:** untrusted U0 / C0 content lands in S0 / D0 / I0 / R0 slots (or H0 widens scope), granting attacker control over policy, route, tool, model, schema, capability, sandbox, or write authority.
- **Mitigation:** PA slot authority model (`PROMPT_BOUNDARY_CONTRACT.md` §2) — S0 / D0 / I0 / R0 outrank E0 / C0 / U0 / H0 by construction. Slot composition emits `slot_authority_map` and `slot_lineage_map` receipts per crossing. Mandatory authority that cannot fit token budget fails closed with `PA_BUDGET_OVERFLOW`; PA never silently drops mandatory slots.
- **Status (W1):** receipts declared in `PROMPT_BOUNDARY_CONTRACT.md` §5 are wired in W3/W5 of plan `apps-rg-spine-hardening-7e3b9c`.

## Trust boundaries (canonical runtime path)

```
USER (CLI / wizard / file inputs)
  │
  ▼  U0 INTAKE — request envelope; raw content labeled as user intent (not authority)
  │
  ▼  L1 PLAN — task_spec / query_spec; no provider-ready prompts
  │
  ▼  L0 ROUTE — RouteContract only; no PromptBOM / no CompiledPromptArtifact
  │
  ▼  C0 — N/A for apps_rg (preloaded inputs; grounding_required=false)
  │
  ▼  PA PROMPT ASSEMBLY ◄── airlocks (U0 user-text · C0 evidence · tool/model · HITL re-entry)
  │     • S0 / D0 / I0 / R0 = HIGHEST authority
  │     • E0 / C0 / U0 / H0 = data-only, cannot override authority slots
  │     • emits: prompt_boundary_receipt, slot_authority_map, slot_lineage_map,
  │              assembly_security_pass_receipt, compiled_prompt_artifact_receipt
  │
  ▼  RUNTIME GATES + L5 EVIDENCE — Runtime Gates emit live GateVerdicts;
  │     L5 emits certification evidence (authority / policy / origin-trust /
  │     registry / sandbox / egress / replay-audit). UNKNOWN is never PASS.
  │
  ▼  L2 EXECUTE — _PAGuard (apps_rg/l2_recipe/steps.py:27-104) fail-closed:
  │     no model call without PA_L2_HANDOFF_READY artifact.
  │     Active provider surface: apps_rg/integrations/llm_client.py
  │     (sanctioned infrastructure.sdks_mcps shim).
  │
  ▼  EXIT — exactly one X3 disposition (X3A / X3C / X3D / X3E)
  │
  ▼  UWG / L4 — only when durable write cleared (apps_rg: cache commit only)
  │
  ▼  L6 SHADOW EVAL — completed-run exhaust only; cannot rescue current run
```

Each `▼` is a trust boundary. Receipts declared in `PROMPT_BOUNDARY_CONTRACT.md` §5 record crossings; OTEL spans wrap each.

**Excluded from this diagram:** the four dormant `Hardened*ExecutorStrategy.py` scaffolds (zero module fan-in per W1 ADG audit) are **NOT** part of the active runtime path. They retain provider-message construction patterns from earlier eras and are tracked for separate cleanup; do not treat them as the live defense layer.

## Non-goals

- Side-channel attacks on the inference provider
- Physical security of the infrastructure
- Supply-chain attacks on the Python interpreter itself

## References

- ADR-028 — publisher-boundary doctrine
- `tools/cert/` — certification evidence
- `tests/governance/` — invariant lock-in tests
- `TECHNICAL_SPEC.md` — architecture spec
