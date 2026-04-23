# Gemini Best Practices (2026)

**Status:** Reference for plan `prompt-reception-followups-a7b3c4`, phase RH8B.1.
**Canonical entry point:** `infrastructure.sdks_mcps.gemini_client.GeminiClient`.

## Native request shape

The Gemini SDK (`google.generativeai`) takes three key inputs on `generate_content`:

| Field | Purpose | Our mapping |
|---|---|---|
| `system_instruction` | High-authority preamble. Applied to every turn. | Concatenation of S0 + I0 + D0 + C0 + M0 + H0 slot content |
| `contents` | Turn-by-turn dialogue. Roles are `user` and `model` (not `assistant`). | E0 exemplars as leading user/model turns, followed by the U0 user turn |
| `generation_config` | Temperature, max_output_tokens, top_p, etc. | Forwarded as kwargs on `GeminiClient.send(...)` |

## Authority-slot projection (RH2B.3 → RH8B.1)

`GeminiClient.project(prompt_messages)` implements this map deterministically:

```text
S0 ─┐
I0 ─┤
D0 ─┼──► system_instruction  (join with "\n\n")
C0 ─┤
M0 ─┤
H0 ─┘

E0 (parsed USER:/ASSISTANT:) ──► leading user/model turns in contents[]
U0                            ──► final {"role": "user", "parts": [U0]} in contents[]
```

When `PromptMessages` carries only the flat-string fallback (synthetic
`SYSTEM` / `USER` keys, e.g. from pre-W6 assembly paths), the projection
degrades gracefully: `SYSTEM` goes to `system_instruction` and `USER` to a
single user turn.

## Role vocabulary

Gemini uses `user` and `model`. Our IR and exemplar parser use the common
`user` / `assistant` vocabulary; the client translates `assistant` → `model`
in projection. Do **not** send `"role": "assistant"` to the Gemini SDK — it
will be rejected.

## Credentials

`GeminiClient.from_env()` delegates to
`infrastructure.sdks_mcps.create_gemini_model`, which reads
`GEMINI_API_KEY` (preferred) or `GOOGLE_API_KEY`. There is no project-level
Vertex auth path in this client; use `create_vertex_client` for the
Vertex-on-GCP service-account variant.

## Testing

`GeminiClient` accepts a `model_factory` in its constructor so unit tests
substitute a mock. The existing
`tests/unit/infrastructure/sdks_mcps/test_gemini_client.py` suite
demonstrates:

- Projection determinism (11 cases).
- Lazy + cached model construction (one factory call across N sends).
- Enum → string finish-reason coercion for telemetry.
- `generation_config` forwarding.
- `system_instruction=None` when the IR has no system slots.

## Deferred (not in RH8B.1)

- Live end-to-end smoke test against Vertex AI. The plan names this as a
  success criterion; gating it requires CI-available Gemini credentials
  which are not yet provisioned. Captured as deferred scope.
- Streaming responses (`generate_content_stream`). Current client is
  request/response only.
- Tool-use / function-calling projection. The `allowed_tools_schema` on
  `CompiledPromptArtifact` does not yet translate to Gemini's tool-use
  request shape.
