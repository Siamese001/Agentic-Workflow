from __future__ import annotations

import json
import urllib.request

import apps_rg.runtime.judges.bullet_pool_claude_selector as subject
import apps_rg.runtime.judges.executive_summary_x1d as x1d


class _Response:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self) -> bytes:
        return json.dumps(self._payload).encode("utf-8")


def test_anthropic_pool_selector_caches_system_but_not_candidate_pool(
    monkeypatch,
    tmp_path,
) -> None:
    monkeypatch.setenv("APPS_RG_ANTHROPIC_PROMPT_CACHE", "1")
    monkeypatch.setattr(x1d, "_judge_live_https_allowed_under_pytest", lambda: True)
    captured: dict[str, object] = {}

    def _urlopen(req, timeout):
        captured["timeout"] = timeout
        captured["body"] = json.loads(req.data.decode("utf-8"))
        return _Response(
            {
                "content": [
                    {
                        "type": "text",
                        "text": '{"selections":[],"pool_summary":{"ok":true}}',
                    }
                ],
                "usage": {
                    "input_tokens": 100,
                    "output_tokens": 12,
                    "cache_creation_input_tokens": 50,
                    "cache_read_input_tokens": 150,
                },
            }
        )

    monkeypatch.setattr(urllib.request, "urlopen", _urlopen)

    judge_output, parsed = subject._call_anthropic_pool_selector(
        api_key="test-key",
        prompt="SELECTION_SCHEMA stable\n\nCANDIDATE POOL\npath_index=0 bullet text",
        model="claude-sonnet-5",
        input_hash="input-hash",
        model_source="unit",
        artifact_dir=tmp_path,
    )

    body = captured["body"]
    assert body["system"][0]["cache_control"] == {"type": "ephemeral"}
    assert "cache_control" not in str(body["messages"])
    assert "CANDIDATE POOL" in body["messages"][0]["content"]
    assert parsed == {"selections": [], "pool_summary": {"ok": True}}
    assert judge_output.provider_status == "MODEL_BACKED_PASS"

    receipt = json.loads((tmp_path / "bullet_pool_selector_cache_receipt.json").read_text(encoding="utf-8"))
    assert receipt["cache_enabled"] is True
    assert receipt["cache_read_input_tokens"] == 150
    assert receipt["candidate_pool_hash"]


def test_anthropic_pool_selector_cache_flag_off_uses_plain_system() -> None:
    assert subject._selector_system_for_anthropic() == subject.POOL_SELECTOR_SYSTEM_PROMPT
