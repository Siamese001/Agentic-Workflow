# ADR-083 — apps_rg Prompt Assembly Ownership Boundary

**Status**: Accepted  
**Date**: 2026-05-09  
**Deciders**: Agentic-Workflow maintainers  
**Plan**: `apps-rg-spine-hardening-deferred-wave-2f8b1d` W2 P2.1  
**Parent plan**: `apps-rg-spine-hardening-7e3b9c` (Completed 2026-05-09)

---

## Context

The `apps-rg-spine-hardening-7e3b9c` plan (W1–W6) established prompt injection defenses for `apps_rg`: airlock pipeline (U0/C0/Tool/HITL), PA boundary receipts, OTEL spans, and an AST-based anti-bypass scanner (`PA-RG1`). During execution the W1 ADG sweep and the W1 carry-forward audit (plan `apps-rg-spine-hardening-deferred-wave-2f8b1d` W1) surfaced that `apps_rg` uses **two distinct PA paths** with different ownership models that must be explicitly ratified.

### The Two PA Paths

**Path A — Governed Substrate (main execution)**  
`GovernedRgRun` → `GovernedAppRunner` → L1 → L0 → C0 → L2 → L5 → L6.  
Prompt assembly is owned by `agentic_core/prompt_governance/` via the shared PA pipeline (`pa0_boundary` → `pa7_dispatch_states`). Provider calls route exclusively through `SovereignLLMGateway`. No direct SDK construction in this path.

**Path B — Narrative HOPs (post-processing)**  
`narrative_pass.py` → `hops/_llm_client.py` → direct SDK (Anthropic/OpenAI/Gemini/Qwen-vLLM).  
Prompt assembly is owned locally by `apps_rg/prompt_assembly/pa_local.py` via `capture_prompt_bom()`. The module docstring explicitly states: *"Direct SDK calls match the apps_rg architecture's layer-gravity rule"* and registers `NEXT_STEP-1` (wire `SovereignLLMGateway` into ensemble + judge live).  
Every provider call in this path is preceded by `capture_prompt_bom()` which emits a `PABoundaryReceipt` with `status=PA_BOM_RESOLVED`.

### Shared PA Surface

`agentic_core/prompt_governance/` contains 45+ files including the canonical PA pipeline (`pa0_boundary.py` through `pa7_dispatch_states.py`). `agentic_core/L0_routing/reasoning/assembly_stage.py` is a hotspot that composes prompts feeding into this pipeline. Both surfaces are in scope for the `PA-RG1` scanner per D14.

---

## Decision

### D1 — Two-path PA model is ratified

Both Path A (governed substrate) and Path B (narrative HOPs with BOM receipts) are **accepted** as the current `apps_rg` PA ownership model. Neither path is a violation:

- Path A satisfies the full PA contract via `SovereignLLMGateway`.
- Path B satisfies the PA audit contract via `capture_prompt_bom()` + `PABoundaryReceipt`. The CONDITIONAL_V1 classification (direct SDK calls in `hops/_llm_client.py`) is formally acknowledged and tracked via `NEXT_STEP-1`.

### D2 — PA boundary ownership by surface

| Surface | Owner | Path | Scanner status |
|---|---|---|---|
| `agentic_core/prompt_governance/` | `agentic_core` PA pipeline | Path A | Scan target (D14) |
| `agentic_core/L0_routing/reasoning/assembly_stage.py` | `agentic_core` L0 routing | Path A | Scan target (D14) |
| `apps_rg/prompt_assembly/` | `apps_rg` local PA | Both | Allowlisted in scanner |
| `apps_rg/integrations/llm_client.py` | Sanctioned shim (guardian exemption) | Path B | Allowlisted in scanner |
| `apps_rg/integrations/hops/_llm_client.py` | Narrative pipeline (CONDITIONAL_V1) | Path B | CONDITIONAL_V1 baselined; NEXT_STEP-1 registered |
| `apps_rg/airlocks/` | Injection defense | Both | Out of scanner scope (defense layer) |

### D3 — NEXT_STEP-1 trajectory

`hops/_llm_client.py` direct SDK calls MUST be migrated to `SovereignLLMGateway` when the narrative pipeline is production-governed. That migration is tracked as `NEXT_STEP-1` in the module docstring and as item D15 (gate promotion) in the wave plan. The `PA-RG1` scanner allowlist will register `hops/_llm_client.py` as `CONDITIONAL_V1_BASELINED` until the migration completes.

### D4 — Scanner expansion scope (D14)

The `PA-RG1` scanner (`check_apps_rg_pa_boundary.py`) is expanded to scan:
- `agentic_core/prompt_governance/` — 45 files, all sub-paths
- `agentic_core/L0_routing/reasoning/assembly_stage.py` — single file

The expanded scanner uses a **separate allowlist** for the `agentic_core` surface to avoid false-positives from the canonical PA pipeline itself (which legitimately constructs provider message arrays inside `pa6_provider_rendering.py`).

---

## Consequences

### Positive
- PA boundary ownership is documented and machine-enforceable via scanner.
- CONDITIONAL_V1 sites are baselined rather than silently ignored.
- Scanner expansion closes the gap where `prompt_governance/` violations would be invisible.
- Two-path model is explicit: future contributors know which path applies and why.

### Negative / Risks
- Scanner expansion to `agentic_core/prompt_governance/` may surface false-positives in `pa6_provider_rendering.py` (legitimate provider message array construction). Mitigated by the `agentic_core`-specific allowlist (D4).
- Path B → Path A migration (`NEXT_STEP-1`) is deferred. Until migration, `hops/_llm_client.py` remains a CONDITIONAL_V1 site with no automated fix.

### Neutral
- No behavior change in this ADR — this is a ratification of existing code structure.
- Scanner gate remains advisory (`PA-RG1`) until 30-day clean baseline is established (D15, plan W4).

---

## Alternatives Considered

**Alt A — Reject Path B entirely; require SovereignLLMGateway now.**  
Rejected: narrative pipeline is end-user-facing, not runtime-governed (per module docstring decision lock D6). Forcing SovereignLLMGateway before the gateway supports the narrative HOP call pattern would break live functionality.

**Alt B — Do not expand scanner to `agentic_core/prompt_governance/`.**  
Rejected: the shared PA surface is the highest-value scan target (L0, high fan-in, SAFETY_GATEKEEPER archetype). Leaving it unscanned defeats the purpose of D14.

---

## References

- Plan: `.codex/plans/apps-rg-spine-hardening-deferred-wave-2f8b1d.md` W2 P2.1
- Parent plan: `.codex/plans/apps-rg-spine-hardening-7e3b9c.md` (Completed)
- W1 findings: `docs/reports/apps_rg/w1_carry_forward_findings_20260509.md`
- Scanner: `ops_scripts/ci/check_apps_rg_pa_boundary.py`
- PA boundary receipt: `apps_rg/prompt_assembly/_pa_boundary.py`
- PA local BOM: `apps_rg/prompt_assembly/pa_local.py`
- Narrative LLM client: `apps_rg/integrations/hops/_llm_client.py` (CONDITIONAL_V1)
- Shared PA pipeline: `agentic_core/prompt_governance/prompt_assembly/pa0_boundary.py` → `pa7_dispatch_states.py`
- ADR-034: wiring CI gate plane and UWG allowlist (scanner registration pattern)
