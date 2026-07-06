from __future__ import annotations

import json

import apps_rg.runtime.judges.executive_summary_x1d as subject


class _Response:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self) -> bytes:
        return json.dumps(self._payload).encode("utf-8")


def test_anthropic_x1d_caches_judge_system_not_candidate_prompt(
    monkeypatch,
    tmp_path,
) -> None:
    monkeypatch.setenv("APPS_RG_ANTHROPIC_PROMPT_CACHE", "1")
    monkeypatch.setattr(subject, "_judge_live_https_allowed_under_pytest", lambda: True)
    captured: dict[str, object] = {}

    def _urlopen(req, timeout):
        captured["timeout"] = timeout
        captured["body"] = json.loads(req.data.decode("utf-8"))
        return _Response(
            {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(
                            {
                                "score_scale": "0_to_5",
                                "score": 4.2,
                                "threshold": 4.0,
                                "pass": True,
                                "decisive_failure": False,
                                "findings": [],
                                "cited_sentence_indexes": [],
                                "remediation_suggestions": [],
                            },
                            separators=(",", ":"),
                        ),
                    }
                ],
                "stop_reason": "end_turn",
                "usage": {
                    "input_tokens": 100,
                    "output_tokens": 20,
                    "cache_creation_input_tokens": 60,
                    "cache_read_input_tokens": 120,
                },
            }
        )

    monkeypatch.setattr(subject.urllib.request, "urlopen", _urlopen)

    out = subject._call_anthropic(
        "test-key",
        "JUDGE PACKET\ncandidate_output: dynamic text\nclaim_ledger: []",
        "claude-sonnet-5",
        "input-hash",
        "anthropic_claude",
        artifact_base=tmp_path,
        packet_hash="packet-hash",
        canonical_contract_hash="contract-hash",
        section_id="executive_summary",
    )

    body = captured["body"]
    assert body["system"][0]["cache_control"] == {"type": "ephemeral"}
    assert "cache_control" not in str(body["messages"])
    assert "candidate_output" in body["messages"][0]["content"]
    assert out.provider_status == "MODEL_BACKED_PASS"
    assert out.proof_eligible_judge is False

    receipts = list(tmp_path.glob("x1d_anthropic_claude_anthropic_judge_cache_receipt_*.json"))
    assert receipts
    receipt = json.loads(receipts[0].read_text(encoding="utf-8"))
    assert receipt["cache_enabled"] is True
    assert receipt["cache_read_input_tokens"] == 120
    assert receipt["judge_contract_hash"] == "contract-hash"
    assert receipt["candidate_hash"]


def test_anthropic_x1d_cache_flag_off_uses_plain_system() -> None:
    system_prompt = subject.build_x1d_judge_system_prompt(compact=True)

    assert subject._anthropic_judge_system_for_payload(system_prompt) == system_prompt
