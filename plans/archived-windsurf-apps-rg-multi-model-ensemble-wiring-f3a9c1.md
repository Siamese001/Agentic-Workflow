---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\apps-rg-multi-model-ensemble-wiring-f3a9c1.md'
original_relative_path: 'apps-rg-multi-model-ensemble-wiring-f3a9c1.md'
source_sha256: a04c9ad6793597b0b9131efd082f0f999e9f3b00a27fc9857a7b35eb31506f0c
recovered_status: SURVIVED_IN_CURRENT
last_commit: '153652b9eb3'
last_commit_date: '2026-06-07 06:37:48 -0400'
created_date: '2026-05-11'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: apps-rg-multi-model-ensemble-wiring-f3a9c1
status: In Progress
owner: Cursor Agent
created_at: "2026-05-11"
dod_exempt: false
---

# apps_rg Multi-Model Ensemble Wiring

**Goal**: Wire the full 4-provider ensemble (Qwen local + Anthropic + OpenAI + Gemini) into the
`apps_rg` managed-workflow pipeline so that generation nodes produce multi-model candidates,
the judge jury selects the winner, and all API keys from `.env` are correctly consumed.

**Parent plan**: `apps-rg-zip-based-full-spine-runtime-restoration-a3f7e2` (RB13 deferred external providers)

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Status |
|------|-----------|-------|-------------|--------|
| W1 | P1.1–P1.3 | Provider registry: model_id env-var resolution + `provider_vendor` field | ~800 | ⬜ TODO |
| W2 | P2.1–P2.3 | Workflow manifest: multi-provider candidate_count + generator_profile lists | ~600 | ⬜ TODO |
| W3 | P3.1–P3.2 | L2 binding: ensemble loop over provider list per node | ~900 | ⬜ TODO |
| W4 | P4.1–P4.2 | Smoke verify: dry-run + live end-to-end with all 4 providers | ~400 | ⬜ TODO |

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| P1.1 | `ProviderProfile` vendor field | `provider_types.py` | Frozen dataclass — add `vendor` field | ~200 | ⬜ |
| P1.2 | Registry parses `provider_vendor` | `provider_registry.py` | Must pass through from YAML | ~150 | ⬜ |
| P1.3 | Profile model_id env-var resolution | `provider_registry.py` + `model_registry.py` | Profiles currently hardcode model strings; should read env vars | ~300 | ⬜ |
| P2.1 | Manifest: ensemble generator_profiles list | `workflow_manifest.resume_generation.v1.yaml` | All generation nodes point at single root profile; need per-provider list | ~300 | ⬜ |
| P2.2 | Manifest: candidate_count reflects provider count | `workflow_manifest.resume_generation.v1.yaml` | candidate_count must match len(generator_profiles) | ~100 | ⬜ |
| P2.3 | `.env.example` — apps_rg provider vars declared | `.env.example` | `VLLM_MAX_MODEL_LEN`, `APPS_RG_ENSEMBLE_PROVIDERS` not declared | ~100 | ⬜ |
| P3.1 | L2 binding: per-node provider loop | `agentic_core/L2_execution/apps_rg_l2_binding.py` | Currently invokes single provider; need ensemble loop | ~600 | ⬜ |
| P3.2 | Gateway: model_id from env not hardcode | `provider_gateway.py` | `_invoke_anthropic`/`_invoke_openai_compat` use `profile.model_id` directly; env-var override path needed | ~200 | ⬜ |
| P4.1 | Dry-run smoke: all 4 profiles resolve | `check_apps_rg_dryrun.py` + manual | `APPS_RG_L2_FORCE_STUB=1` — confirm 4 profiles load without error | ~150 | ⬜ |
| P4.2 | Live smoke: Brown & Brown run, 4 candidates | Manual run + artifact inspection | Requires all 3 API keys in `.env` + Qwen Docker running | ~200 | ⬜ |

---

## Gap Register (what's missing today)

| # | Gap | Root cause | Fixed in |
|---|-----|-----------|---------|
| G1 | `ProviderProfile` has no `vendor` field | `provider_types.py` frozen dataclass never extended | P1.1 |
| G2 | `provider_registry.py` drops `provider_vendor` from YAML | `_parse_profile` only maps known fields | P1.2 |
| G3 | Profile `model_id` is hardcoded string in YAML | Should be resolved from `OPENAI_MODEL` / `ANTHROPIC_MODEL` / `GEMINI_PRO_MODEL` env vars via `model_registry.py` | P1.3 |
| G4 | Workflow manifest nodes use single `pvp::apps_rg::resume_generation::v1` profile | Root profile ref doesn't enumerate per-provider profiles | P2.1–P2.2 |
| G5 | L2 binding calls one provider per node | No ensemble loop over provider list | P3.1 |
| G6 | Gateway model_id uses profile YAML value, not env override | `_invoke_anthropic`/`_invoke_openai_compat` don't re-read env vars | P3.2 |
| G7 | `.env.example` missing `APPS_RG_ENSEMBLE_PROVIDERS` | New opt-in flag not declared | P2.3 |

---

## Wave 1 — Provider Registry Plumbing

### P1.1 — Add `vendor` field to `ProviderProfile`

File: `agentic_core/runtime/providers/provider_types.py`

Add optional `vendor: str = ""` to the frozen `ProviderProfile` dataclass. This is the field
`_infer_vendor()` in the gateway currently tries to read via `getattr`. Making it explicit
removes the fragile string-match fallback.

### P1.2 — Registry passes `provider_vendor` through

File: `agentic_core/runtime/providers/provider_registry.py`

In `_parse_profile`, read `data.get("provider_vendor", "")` and pass it as `vendor=` when
constructing `ProviderProfile`.

### P1.3 — Model ID resolved from env vars at registry load time

File: `agentic_core/runtime/providers/provider_registry.py`

After reading `model_id` from YAML, resolve through `model_registry.py` env-var constants:

| YAML `model_id` | Resolved from |
|-----------------|---------------|
| `"claude-sonnet-4-6"` | `ANTHROPIC_MODEL` env var (default `claude-sonnet-4-6`) |
| `"gpt-5.5"` | `OPENAI_MODEL` env var (default `gpt-5.5`) |
| `"gemini-3.1-pro-preview"` | `GEMINI_PRO_MODEL` env var (default `gemini-3.1-pro-preview`) |
| `"Qwen/Qwen2.5-32B-Instruct-AWQ"` | `VLLM_MODEL_NAME` env var (default as-is) |

The YAML value acts as a fallback default if the env var is unset, exactly matching the
`os.getenv("OPENAI_MODEL", "gpt-5.5")` pattern in `model_registry.py`.

---

## Wave 2 — Workflow Manifest: Ensemble Nodes

### P2.1 — Generation nodes list all 4 provider profiles

File: `apps_rg/config/workflow_manifest.resume_generation.v1.yaml`

Change `generator_profile` on generation-tier nodes (`professional_summary`, `experience_block`,
`header_block`, `skills_block`) from a single string to a list:

```yaml
generator_profiles:
  - "pvp::apps_rg::local_qwen_generator"
  - "pvp::apps_rg::anthropic_claude_generator"
  - "pvp::apps_rg::openai_gpt_generator"
  - "pvp::apps_rg::google_gemini_generator"
```

Lower-stakes nodes (`education_block`, `certifications_block`, `final_render`) stay single-provider
(Qwen only) since they are deterministic / passthrough — no ensemble benefit.

Opt-in env override: `APPS_RG_ENSEMBLE_PROVIDERS` (comma-separated profile short-keys) lets
operators restrict the ensemble without redeploying YAML. Empty = all 4.

### P2.2 — `candidate_count` tracks provider count

For ensemble nodes: `candidate_count: 4` (one per provider). For single-provider nodes: unchanged.

### P2.3 — `.env.example` new vars

```
APPS_RG_ENSEMBLE_PROVIDERS=   # comma-separated short keys; empty = all registered
OPENAI_BASE_URL=              # optional base URL override for OpenAI-compat calls
GEMINI_BASE_URL=              # optional override; default = Google compat endpoint
```

---

## Wave 3 — L2 Binding: Ensemble Loop

### P3.1 — Per-node provider loop

File: `agentic_core/L2_execution/apps_rg_l2_binding.py`

Current shape (single call):
```python
response = gateway.invoke(ProviderRequest(provider_profile=primary_profile, ...))
```

New shape (ensemble):
```python
candidates = []
for profile_ref in node.generator_profiles:
    profile = registry.get_profile(profile_ref)
    resp = gateway.invoke(ProviderRequest(provider_profile=profile, ...))
    if resp.success:
        candidates.append(resp)
# Pass candidates to judge_jury_runner for winner selection
```

Fail-soft: if a provider fails, log and continue — a single failing provider must NOT abort
the node. Minimum 1 successful candidate required; else escalate to HITL.

### P3.2 — Gateway model_id env-var override at invocation time

File: `agentic_core/runtime/providers/provider_gateway.py`

In `_invoke_anthropic` and `_invoke_openai_compat`, resolve model_id at call time via
`model_registry` constants rather than using `profile.model_id` directly:

```python
from agentic_core.L0_routing.config.model_registry import (
    ANTHROPIC_MODEL_ID, OPENAI_MODEL_ID, GEMINI_PRO_MODEL_ID,
)
# Use ANTHROPIC_MODEL_ID (which already reads ANTHROPIC_MODEL env var)
# instead of profile.model_id (which is the YAML string)
```

This ensures `ANTHROPIC_MODEL=claude-opus-4-5` in `.env` overrides the YAML default without
requiring a YAML edit.

---

## Wave 4 — Smoke Verification

### P4.1 — Dry-run: all profiles load

```powershell
$env:APPS_RG_L2_FORCE_STUB=1
python -m apps_rg --dry-run `
  --target-company "Test" `
  --target-role "Test" `
  --source-resume "C:\Users\amita\Documents\Resumes\SVP Engineering Resume_Ayer.pdf" `
  --jd "ops_scripts/apps_rg/jd_brown_brown_svp_it_strategy.txt"
```

Expected: exit 0, artifact JSON contains `provider_profiles_loaded: 7` (4 generators + 2 stubs + 1 deterministic), `stub_mode: true`.

### P4.2 — Live run: Brown & Brown, 4-provider ensemble

```powershell
python -m apps_rg `
  --target-company "Brown & Brown" `
  --target-role "SVP IT Strategy & Innovation" `
  --source-resume "C:\Users\amita\Documents\Resumes\SVP Engineering Resume_Ayer.pdf" `
  --jd "ops_scripts/apps_rg/jd_brown_brown_svp_it_strategy.txt" `
  --manual-brief "C:\Users\amita\Documents\Brown & Brown\Brown & Brown - Resume Prep SVP IT.pdf"
```

Expected artifact contains:
- `ensemble_candidates: 4` (or fewer if a provider fails — min 1)
- `providers_used: [local_qwen_generator, anthropic_claude_generator, openai_gpt_generator, google_gemini_generator]`
- `winner_provider: <one of the four>`
- `stub_mode: false`

---

## Definition of Done

| # | Criterion | Verification |
|---|-----------|-------------|
| DoD-1 | All 4 provider profiles load from YAML with correct `vendor` field | `registry.list_profiles(ProviderKind.EXTERNAL_API)` returns 3 entries |
| DoD-2 | Dry-run exits 0 with stub responses from all 4 profiles | `APPS_RG_L2_FORCE_STUB=1 python -m apps_rg --dry-run ...` exits 0 |
| DoD-3 | Live run produces ≥1 candidate per generation node | `generated_resume.json` contains `ensemble_candidates ≥ 1`, `stub_mode: false` |
| DoD-4 | Model IDs respect env-var overrides (`ANTHROPIC_MODEL`, `OPENAI_MODEL`, `GEMINI_PRO_MODEL`) | Set each to a known alias; confirm `model_used` in receipt matches |
| DoD-5 | Single provider failure does not abort run | Mock one provider to timeout; confirm run still exits 0 with 3 candidates |

### Verification-vs-Deferral

| Item | Verified this plan | Deferred |
|------|-------------------|----------|
| All 4 provider profiles resolve | ✅ | — |
| Env-var model_id override | ✅ | — |
| Ensemble winner selection via judge jury | ⬜ | Judge jury implementation is existing RB13 stub; wired but not upgraded here |
| Per-provider cost tracking | ⬜ | Deferred — `TokenUsage` populated with heuristic; real usage from response metadata is future work |
| Gemini function-calling / structured output mode | ⬜ | Using plain chat completions; native Gemini structured output deferred |

---

## Files in Scope

| File | Change |
|------|--------|
| `agentic_core/runtime/providers/provider_types.py` | Add `vendor: str = ""` to `ProviderProfile` |
| `agentic_core/runtime/providers/provider_registry.py` | Parse `provider_vendor`; env-var model_id resolution |
| `agentic_core/runtime/providers/provider_gateway.py` | Model ID resolved from `model_registry` constants |
| `agentic_core/L2_execution/apps_rg_l2_binding.py` | Ensemble loop over `generator_profiles` list |
| `apps_rg/config/workflow_manifest.resume_generation.v1.yaml` | `generator_profiles` list on ensemble nodes; `candidate_count: 4` |
| `.env.example` | Declare `APPS_RG_ENSEMBLE_PROVIDERS`, `OPENAI_BASE_URL`, `GEMINI_BASE_URL` |

---

## Non-Goals

- Adding new LLM providers beyond the 4 already registered
- Upgrading judge jury from stub to real LLM judge (separate plan)
- Cost accounting / budget enforcement across providers
- Gemini native structured output / function calling
- Rate-limit handling / retry logic beyond fail-soft
