# X1D LLM Judge Provider Configuration

`apps_rg/config/provider_profiles.yaml` is the only SSOT for apps_rg X1D judge
model selection and judge runtime limits. This document intentionally does not
duplicate model IDs, model override env vars, retry counts, token budgets, or
fallback instructions.

Runtime code resolves judge models through
`apps_rg.runtime.judges.section_judge_profile.resolve_section_proof_judge_model`.
Credentials and provider endpoints may still come from environment variables,
but environment variables must not select judge models or LLM runtime policy.

If a configured provider model is unavailable, the run blocks and records the
provider error in artifacts. It does not switch to another model.
