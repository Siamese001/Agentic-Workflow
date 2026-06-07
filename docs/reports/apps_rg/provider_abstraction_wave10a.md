# apps_rg Provider Abstraction Wave 10A

## Scope

Wave 10A creates an apps_rg-local provider abstraction without changing production defaults:

- `qwen_vllm` remains the default provider profile.
- External providers are selectable for Wave 10B parity work.
- `external_default` is present as a target profile but is not the default.
- Section CLI/runtime generation remains on the existing Qwen transport paths.

## Delivered

- `apps_rg/runtime/providers/provider_gateway.py`
  - `ProviderProfile`
  - `ModelProvider`
  - `ProviderGateway`
  - provider profile resolution and YAML loading
- `apps_rg/runtime/providers/qwen_vllm_provider.py`
  - `QwenVLLMProvider` wrapper around existing `call_qwen_vllm`
- `apps_rg/runtime/providers/external_provider.py`
  - injectable external provider wrapper
  - fail-closed credentials/transport behavior
- `apps_rg/config/provider_profiles.yaml`
  - Qwen default profile
  - external OpenAI/Claude/default profiles for parity staging

## Guardrails

- No default switch to `external_default`.
- No Qwen quarantine.
- No section generation path rewrite.
- External profiles require credentials and a configured transport before model-backed execution.

## Follow-Up

Wave 10B must validate provider parity across all seven sections before Wave 10C can change defaults.
