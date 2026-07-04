# ProceduralPattern:AppsResearchAppsRgHandoffEnvelopeInvariant

INVARIANT: apps_research may pass a targeting brief to apps_rg only through an apps_research-owned handoff envelope with external_openai generation metadata, model-backed X2 judge proof, and X3 ALLOW authorization.

scope: `apps_research/integrations/apps_rg_handoff.py`, `apps_research/engines/company_brief_engine.py`, `apps_rg/integrations/apps_research_bridge.py`, `apps_rg/integrations/managed_research_delegation.py`, `apps_rg/prerequisites/briefing_validator.py`, and row 0 rendering in `apps_rg/runtime/mandatory_run_outputs.py`.

enforcement: `tests/unit/apps_research/test_targeting_brief_grounding_failclosed.py`, `tests/unit/apps_research/test_cli_apps_rg_targeting_brief.py`, `tests/unit/apps_rg/test_apps_research_bridge_contract_gate.py`, `tests/unit/apps_rg/test_pre_dispatch_preflight.py`, and `tests/unit/apps_rg/test_mandatory_run_outputs.py`.

violation_examples: emitting `handoff_eligible=True` from deterministic sidecar scoring alone; treating `confidence_score` from `research_bridge_response.json` as X2; setting X3 ALLOW when the X2 receipt lacks score, threshold, judge provider/model, `model_backed=True`, or `MODEL_BACKED_*` provider status.

canonical_pattern: generate the brief with `external_openai` / `gpt-5.4-mini-2026-03-17`, run the X2 LLM judge with `gemini_pro` / `gemini-3.1-pro-preview`, write `apps_research_briefing_envelope.json` beside the delegated briefing, and let apps_rg render X2/X3 from that envelope.

doctrine_ref: `memory/codex/apps_rg_x1d_model_ssot_lockdown.md`; discovered: 2026-07-04, validated: 2026-07-04.
