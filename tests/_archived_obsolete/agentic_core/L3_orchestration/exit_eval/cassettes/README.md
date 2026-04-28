# Judge Adapter Cassettes

Recorded HTTP responses for the Anthropic and OpenAI judge adapters,
used by `test_judges_vcr.py` to exercise the full
`AnthropicJudge.judge()` / `OpenAIJudge.judge()` paths offline — no API
keys, no network.

## Why a tiny home-grown cassette format and not `vcrpy`?

- The judges call `urllib.request.urlopen` directly (zero-dep policy).
- `vcrpy` requires either `requests` or `urllib3` interception plus
  pickle-format cassettes; we want plain JSON that an SVP can audit
  in 60 seconds.
- The replay shim is ~30 lines (`_replay_urlopen`). Trade three lines
  of saved code in tests for one fewer transitive dependency.

## Cassette schema

```json
{
  "_meta": {
    "description": "...",
    "recorded_at": "2026-04-24T22:00:00Z",
    "endpoint": "https://api.anthropic.com/v1/messages",
    "model": "claude-3-5-sonnet-latest"
  },
  "expected_request": {
    "method": "POST",
    "headers_required": ["x-api-key", "anthropic-version", "content-type"]
  },
  "response_status": 200,
  "response_body": {<provider-specific body>}
}
```

- `_meta.endpoint` MUST match the request URL.
- `expected_request.headers_required` is a list of header names that
  MUST be present on the request (case-insensitive). We do not capture
  the secret values themselves.
- `response_status` — HTTP status code. `200` returns the body to
  the adapter; non-2xx raises `urllib.error.HTTPError`.
- `response_body` — provider's JSON shape, *exactly* what the real
  API returned, with PII stripped.

## How to record a new cassette

1. Run a one-off live call (with `--judge anthropic` or `--judge openai`)
   inside a debugger; capture the `response.read()` bytes.
2. Hand-redact any PII or org IDs.
3. Drop the JSON file in this directory.
4. Reference it by filename from `test_judges_vcr.py`.

## Replay invariants

- The replay shim does NOT compare request bodies — judges sometimes
  vary prompt formatting across runs and we accept that. It DOES
  enforce required headers so a regression that drops auth surfaces.
- The shim raises `urllib.error.HTTPError` for non-2xx statuses to
  match the live adapter's error surface, not a custom exception.
