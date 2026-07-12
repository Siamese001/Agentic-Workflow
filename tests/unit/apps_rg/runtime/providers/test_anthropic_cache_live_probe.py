from __future__ import annotations

import json

from apps_rg.runtime.providers.anthropic_cache_live_probe import run_live_cache_probe


class _Response:
    def __init__(self, payload: dict) -> None:
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self) -> bytes:
        return json.dumps(self.payload).encode("utf-8")


def test_live_probe_requires_second_call_cache_read_and_output_parity() -> None:
    responses = iter(
        [
            {
                "content": [{"type": "text", "text": "CACHE_PROBE_OK"}],
                "usage": {
                    "input_tokens": 4,
                    "output_tokens": 2,
                    "cache_creation_input_tokens": 2200,
                    "cache_read_input_tokens": 0,
                    "cache_creation": {"ephemeral_5m_input_tokens": 2200},
                },
            },
            {
                "content": [{"type": "text", "text": "CACHE_PROBE_OK"}],
                "usage": {
                    "input_tokens": 4,
                    "output_tokens": 2,
                    "cache_creation_input_tokens": 0,
                    "cache_read_input_tokens": 2200,
                },
            },
        ]
    )
    captured = []

    def opener(request, timeout):
        captured.append(json.loads(request.data.decode("utf-8")))
        return _Response(next(responses))

    receipt = run_live_cache_probe(api_key="test-key", opener=opener, input_usd_per_million=2.0)

    assert receipt["status"] == "PASS"
    assert receipt["pass"] is True
    assert receipt["outputs_equal"] is True
    assert receipt["second_call_cache_read_input_tokens"] == 2200
    assert receipt["second_call_estimated_input_token_savings"] > 0
    assert len(captured) == 2
    assert captured[0]["system"][0]["cache_control"] == {"type": "ephemeral"}
    assert captured[0]["system"] == captured[1]["system"]


def test_live_probe_blocks_when_second_call_does_not_read_cache() -> None:
    payloads = iter(
        [
            {
                "content": [{"type": "text", "text": "CACHE_PROBE_OK"}],
                "usage": {"input_tokens": 4, "output_tokens": 2, "cache_creation_input_tokens": 2200},
            },
            {
                "content": [{"type": "text", "text": "CACHE_PROBE_OK"}],
                "usage": {"input_tokens": 4, "output_tokens": 2, "cache_creation_input_tokens": 2200},
            },
        ]
    )

    receipt = run_live_cache_probe(
        api_key="test-key",
        opener=lambda *_args, **_kwargs: _Response(next(payloads)),
    )

    assert receipt["status"] == "BLOCKED"
    assert "second_call_has_no_cache_read_tokens" in receipt["promotion_reasons"]
