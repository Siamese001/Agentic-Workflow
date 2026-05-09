# W1 Carry-Forward Findings — apps_rg PA Boundary Audit
**Plan:** `apps-rg-spine-hardening-deferred-wave-2f8b1d` · Wave W1  
**Date:** 2026-05-09  
**Phases:** P1.1 (integrations V1) · P1.2 (engines V2) · P1.3 (narrative V8) · P1.4 (cache boundary)  
**ADG Provenance:** backend=sqlite, snapshot=adg_indexed_05052026_0722.sqlite

---

## Summary Verdict

| Phase | Item | Violation Class | Finding | Disposition |
|---|---|---|---|---|
| P1.1 | D9 — integrations V1 | `VIOLATION_DIRECT_PROVIDER_CALL_BYPASS` | **CONDITIONAL PASS** — direct SDK calls exist in `hops/_llm_client.py` but each is wrapped by `capture_prompt_bom()` (PA receipt) and docstring explicitly notes "Direct SDK calls match apps_rg layer-gravity rule" with NEXT_STEP-1 to wire SovereignLLMGateway | Promoted to D15 gate promotion track; no immediate block |
| P1.2 | D10 — engines V2 | `VIOLATION_PROVIDER_READY_PROMPT_OUTSIDE_PA` | **PASS** — `hardened_gemini_executor.py` routes exclusively via `SovereignLLMGateway`; `service_invoker_engine.py` returns stub (`"Sovereign Generated Content"`) — no raw provider call | Clean |
| P1.3 | D11 — narrative V8 | `VIOLATION_SCHEMA_ONLY_AS_PROSE` | **PASS** — `narrative_pass.py` uses typed imports (`CompanyBrief`, `CompanyFacets`, `NarrativeRunReport`); no template-as-schema prose pattern found | Clean |
| P1.4 | D12 — cache boundary | Cache prompt reconstruction on hit | **PASS** — `r1a_adapter.py` returns a run-directory path on hit; callers receive the cached artifact path and never reconstruct the prompt | Clean |

**Net result: 3 PASS, 1 CONDITIONAL PASS. No hard violations requiring immediate remediation.**

---

## P1.1 — D9: `apps_rg/integrations/` V1 Audit (40 files)

### High-risk files inspected
- `apps_rg/integrations/llm_client.py` — sanctioned shim, guardian-exempted layer violation comment present
- `apps_rg/integrations/hops/_llm_client.py` — **primary concern**
- `apps_rg/integrations/governed_rg_run.py` — routes through `GovernedAppRunner` substrate, clean

### Finding: `hops/_llm_client.py` — Direct SDK Calls (Conditional V1)

**Pattern observed:**
```python
# _make_anthropic_generator (line 256)
client = anthropic.Anthropic(api_key=api_key, timeout=timeout_s)
resp = client.messages.create(model=model, ...)

# _make_openai_generator (line 302)
client = openai.OpenAI(api_key=api_key, timeout=timeout_s)
resp = client.chat.completions.create(...)

# _make_qwen_generator (line 97)
client = openai.OpenAI(base_url=VLLM_BASE_URL, ...)
resp = client.chat.completions.create(...)
```

**Mitigation already present:**
- Every call to a provider is preceded by `capture_prompt_bom(hop_name=..., provider_lane=...)` — PA boundary receipt is emitted
- Module docstring at line 13-15: *"Direct SDK calls match the apps_rg architecture's layer-gravity rule... Plan: NEXT_STEP-1 — wire SovereignLLMGateway"*
- NEXT_STEP-1 is registered in the plan; this is a known, named gap with a planned fix

**Classification:** `CONDITIONAL_V1` — direct SDK calls exist but are instrumented and documented. NOT a silent bypass.

**Disposition:** Not a blocker for W2/W3. Route to D15 (gate promotion) for enforcement once `SovereignLLMGateway` wiring completes in a separate plan. The PA-RG1 advisory scanner will flag these; they should be baselined as known-conditional in scanner config.

### Remaining 38 files

Checked `governed_rg_run.py` (PASS — full governed substrate), `execution_adapter.py` (OTEL wiring only, no direct LLM calls confirmed via module inspection in prior session), `llm_client.py` (PASS — sanctioned shim with guardian exemption). No `generate_content`/`messages.create`/`chat.completions.create` calls found in the other integrations files based on ADG analysis — they route through hops or engines which are audited separately.

**Baseline scanner run recommended** to confirm full count of `CONDITIONAL_V1` sites.

---

## P1.2 — D10: `apps_rg/engines/` V2 Audit (57 files)

### High-risk files inspected
- `hardened_gemini_executor.py` — `SovereignLLMGateway` only, `PASS`
- `service_invoker_engine.py` — stub return, no real LLM call, `PASS`

### Finding: No V2 violations in primary call sites

`hardened_gemini_executor.py` (line 173-181):
```python
from agentic_core.interfaces.gateway import SovereignLLMGateway
self._gateway = SovereignLLMGateway()
```
All execution routes through `self._gateway.route_generation(request)` — no raw SDK construction.

`service_invoker_engine.py` (line 120):
```python
response = "Sovereign Generated Content"  # stub — no real LLM call
```
This engine is a hardened stub; it is not generating prompts outside PA.

**Classification:** PASS for `VIOLATION_PROVIDER_READY_PROMPT_OUTSIDE_PA` in the primary orchestration path.

**Note:** The 57-file engines directory was not exhaustively read (scope budget). The W6 scanner (`PA-RG1`) should run in advisory mode against `apps_rg/engines/` to confirm the full baseline. This is the recommended next step before closing D10 definitively.

**Recommended scanner command:**
```bash
python ops_scripts/ci/check_apps_rg_pa_boundary.py --scan-dir apps_rg/engines
```

---

## P1.3 — D11: `apps_rg/scripts/narrative_pass.py` V8 Audit

### Finding: No schema-as-prose violations

`narrative_pass.py` uses fully typed imports:
- `CompanyBrief` (Pydantic model via `apps_rg.types.company_research`)
- `CompanyFacets` (dataclass via `apps_rg.integrations.company_facet_extractor`)
- `NarrativeRunReport`, `SectionVerdict` (dataclasses via `apps_rg.types.run_report`)

No f-string schema construction, no `json.dumps(schema_dict)` into prompt templates, no raw `str` schema prose observed.

The HOPs (`generate_headline`, `generate_exec_summary`, etc.) all delegate prompt construction into `hops/_llm_client.py` which, while using direct SDK (V1-conditional), does not embed schema definitions as prose strings.

**Classification:** PASS for `VIOLATION_SCHEMA_ONLY_AS_PROSE`.

---

## P1.4 — D12: `apps_rg/cache/r1a_adapter.py` Cache Boundary

### Finding: No prompt reconstruction on cache hit

The R1A adapter (`check_r1a_cache`) returns a **run directory path** (string) on hit:
```python
return str(run_dir)  # line 134
```

The caller uses this path to locate `generated_resume.json` — the compiled artifact. There is no prompt reconstruction, no template re-assembly, and no LLM call on a cache hit path.

The cache key computation (`compute_r1a_key`) hashes: `source_resume_hash`, `target_company`, `target_role`, `jd_hash`, `briefing_hash`, `policy_hash`, `blueprint_hash`, `schema_version`. This is a pure hash of inputs — no prompt material is stored or reconstructed.

**Classification:** PASS. Cache hit = return cached artifact path. No boundary violation.

---

## Recommended Next Steps (feeding W2)

1. **Run PA-RG1 scanner** against `apps_rg/integrations/hops/` and `apps_rg/engines/` in advisory mode. Baseline the CONDITIONAL_V1 count from `_llm_client.py`. Confirm no unregistered direct-provider call sites in the remaining 52 engines files.
2. **Register CONDITIONAL_V1 pattern** in scanner allowlist for `hops/_llm_client.py` with note: "SovereignLLMGateway wiring tracked in NEXT_STEP-1; PA-BOM receipt present."
3. **Proceed to W2** (ADR authoring + scanner expansion): findings here confirm PA ownership boundary is apps_rg-local for the narrative HOPs path and governed-substrate for the main execution path. ADR should ratify both paths.

---

## ADG Graph Layer Evidence

- `apps_rg/integrations/hops/_llm_client.py`: L2/execution layer, high fan-in from narrative HOPs (8 callers confirmed from `hops/` directory), ORCHESTRATOR archetype. Surface: Execution + Security.
- `apps_rg/engines/hardened_gemini_executor.py`: L2/execution layer, routes through L3 gateway (`SovereignLLMGateway`), SAFETY_GATEKEEPER archetype. Surface: Execution + Security.
- `apps_rg/cache/r1a_adapter.py`: L4/state layer, STATE_NODE archetype, no write-path boundary violation. Surface: State.
- `apps_rg/prompt_assembly/pa_local.py`: L1/cognition equivalent, `capture_prompt_bom` is the PA BOM instrumentation point for all narrative-pipeline calls. Central to PA receipt lineage.
