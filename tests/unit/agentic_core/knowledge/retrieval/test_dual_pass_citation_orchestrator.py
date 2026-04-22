"""Unit tests for dual_pass_citation_orchestrator."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pytest

from agentic_core.knowledge.retrieval.dual_pass_citation_orchestrator import (
    STATUS_ABSTAIN,
    STATUS_JSON_NOT_REQUESTED,
    STATUS_JSON_PARSE_FAILED,
    STATUS_NO_GATEWAY,
    STATUS_OK,
    STATUS_PASS1_FAILED,
    STATUS_PASS2_FAILED,
    DualPassCitationOrchestrator,
    DualPassResult,
)
from agentic_core.knowledge.retrieval.evidence_contract_builder import (
    VerifiedChunk,
)
from agentic_core.knowledge.retrieval.prompt_envelope import (
    AssemblyStatusCode,
    PromptAssemblyStatus,
    PromptEnvelope,
)


def _chunk(chunk_id: str = "c0", content: str = "body", is_must_use: bool = True) -> VerifiedChunk:
    return VerifiedChunk(
        chunk_id=chunk_id,
        content=content,
        source_id=f"src-{chunk_id}",
        citation_anchor=f"[{chunk_id}]",
        support_score=0.9,
        is_must_use=is_must_use,
    )


def _envelope(
    chunks: list[VerifiedChunk] | None = None,
    abstain: bool = False,
    task_spec: str = "",
) -> PromptEnvelope:
    return PromptEnvelope(
        envelope_id="env",
        trace_id="trace",
        query_id="q",
        verified_chunks=tuple(chunks or []),
        cited_spans=(),
        coverage_score=0.8,
        gaps=(),
        contradiction_status="none",
        abstain_recommended=abstain,
        next_action_hint="proceed",
        task_spec=task_spec,
        system_blocks=(),
        replay_key="rk",
        policy_hash="ph",
        plan_id="plan",
        assembly_status=PromptAssemblyStatus(status=AssemblyStatusCode.READY),
    )


def _mk_pass1_response(
    text: str = "Grounded answer.",
    citations: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    return {
        "content": [
            {
                "type": "text",
                "text": text,
                "citations": citations or [],
            }
        ]
    }


# ---------------------------------------------------------------------------
# Abstain / offline short-circuits
# ---------------------------------------------------------------------------


def test_abstain_envelope_returns_status_abstain():
    orch = DualPassCitationOrchestrator(pass1_fn=lambda p: None)
    env = _envelope([], abstain=True)
    result = orch.execute(env, query="q")
    assert result.status == STATUS_ABSTAIN
    assert result.answer_text == ""
    assert result.citations == ()
    assert result.structured_output is None


def test_no_pass1_fn_returns_status_no_gateway():
    orch = DualPassCitationOrchestrator(pass1_fn=None)
    env = _envelope([_chunk()])
    result = orch.execute(env, query="q")
    assert result.status == STATUS_NO_GATEWAY
    assert "offline" in result.reason


# ---------------------------------------------------------------------------
# Pass 1 only (no JSON schema)
# ---------------------------------------------------------------------------


def test_pass1_only_returns_status_json_not_requested():
    captured_payloads: list[dict[str, Any]] = []

    def pass1(payload: dict[str, Any]) -> Any:
        captured_payloads.append(payload)
        return _mk_pass1_response(
            text="Widget retries fail after 3 attempts.",
            citations=[
                {
                    "type": "char_location",
                    "cited_text": "fail after 3",
                    "document_index": 0,
                }
            ],
        )

    orch = DualPassCitationOrchestrator(pass1_fn=pass1)
    env = _envelope([_chunk(chunk_id="widget-policy")])
    result = orch.execute(env, query="When do widget retries fail?")

    assert result.status == STATUS_JSON_NOT_REQUESTED
    assert result.answer_text == "Widget retries fail after 3 attempts."
    assert len(result.citations) == 1
    assert result.citations[0].doc_id == "widget-policy"
    assert result.structured_output is None
    assert result.citation_coverage == 1.0
    # Pass 1 received a structured payload from build_messages_payload
    assert "messages" in captured_payloads[0]


def test_pass1_failure_status_pass1_failed():
    def pass1(_payload: dict[str, Any]) -> Any:
        raise RuntimeError("simulated upstream failure")

    orch = DualPassCitationOrchestrator(pass1_fn=pass1)
    env = _envelope([_chunk()])
    result = orch.execute(env, query="q")
    assert result.status == STATUS_PASS1_FAILED
    assert "simulated upstream failure" in result.reason


def test_citation_coverage_computed_against_must_use_only():
    def pass1(_p):
        # Only cite chunk 0; chunk 1 is must-use but uncited; chunk 2 optional
        return _mk_pass1_response(
            text=".",
            citations=[
                {"type": "char_location", "cited_text": "x", "document_index": 0}
            ],
        )

    orch = DualPassCitationOrchestrator(pass1_fn=pass1)
    env = _envelope(
        [
            _chunk("c0", is_must_use=True),
            _chunk("c1", is_must_use=True),
            _chunk("c2", is_must_use=False),
        ]
    )
    result = orch.execute(env, query="q")
    # 1 of 2 must-use chunks covered
    assert result.citation_coverage == pytest.approx(0.5)


# ---------------------------------------------------------------------------
# Pass 2 (JSON shape)
# ---------------------------------------------------------------------------


def test_full_two_pass_ok_with_json_shape():
    pass1_response = _mk_pass1_response(
        text="BM25 is a lexical retrieval algorithm.",
        citations=[
            {"type": "char_location", "cited_text": "BM25", "document_index": 0}
        ],
    )

    def pass1(_payload):
        return pass1_response

    captured_pass2_prompt: list[str] = []

    def pass2(prompt: str) -> str:
        captured_pass2_prompt.append(prompt)
        return '{"algorithm": "BM25", "category": "lexical"}'

    orch = DualPassCitationOrchestrator(pass1_fn=pass1, pass2_fn=pass2)
    env = _envelope([_chunk("bm25-intro")])
    schema = {"type": "object", "required": ["algorithm", "category"]}
    result = orch.execute(env, query="What is BM25?", json_schema=schema)

    assert result.status == STATUS_OK
    assert result.structured_output == {"algorithm": "BM25", "category": "lexical"}
    assert result.answer_text == "BM25 is a lexical retrieval algorithm."
    assert result.pass2_raw_text == '{"algorithm": "BM25", "category": "lexical"}'
    # Pass 2 prompt references the answer AND embeds schema
    assert "BM25 is a lexical retrieval algorithm." in captured_pass2_prompt[0]
    assert '"required"' in captured_pass2_prompt[0]


def test_pass2_extracts_json_from_fenced_code_block():
    def pass1(_p):
        return _mk_pass1_response(text="Answer.")

    def pass2(_p):
        return "Here is your JSON:\n```json\n{\"x\": 1}\n```\nThanks."

    orch = DualPassCitationOrchestrator(pass1_fn=pass1, pass2_fn=pass2)
    env = _envelope([_chunk()])
    result = orch.execute(env, query="q", json_schema={"type": "object"})
    assert result.status == STATUS_OK
    assert result.structured_output == {"x": 1}


def test_pass2_extracts_json_from_prose_with_outermost_braces():
    def pass1(_p):
        return _mk_pass1_response(text="Answer.")

    def pass2(_p):
        return 'The JSON is: {"key": "value", "n": 42} as requested.'

    orch = DualPassCitationOrchestrator(pass1_fn=pass1, pass2_fn=pass2)
    env = _envelope([_chunk()])
    result = orch.execute(env, query="q", json_schema={"type": "object"})
    assert result.status == STATUS_OK
    assert result.structured_output == {"key": "value", "n": 42}


def test_pass2_unparseable_json_returns_status_json_parse_failed():
    def pass1(_p):
        return _mk_pass1_response(text="Answer.")

    def pass2(_p):
        return "This response has no JSON at all."

    orch = DualPassCitationOrchestrator(pass1_fn=pass1, pass2_fn=pass2)
    env = _envelope([_chunk()])
    result = orch.execute(env, query="q", json_schema={"type": "object"})
    assert result.status == STATUS_JSON_PARSE_FAILED
    assert result.structured_output is None
    # Pass 1 data is still preserved
    assert result.answer_text == "Answer."
    assert result.pass2_raw_text == "This response has no JSON at all."


def test_pass2_failure_preserves_pass1_data():
    def pass1(_p):
        return _mk_pass1_response(
            text="Answer.",
            citations=[{"type": "char_location", "cited_text": "x", "document_index": 0}],
        )

    def pass2(_p):
        raise RuntimeError("pass 2 timeout")

    orch = DualPassCitationOrchestrator(pass1_fn=pass1, pass2_fn=pass2)
    env = _envelope([_chunk("c0")])
    result = orch.execute(env, query="q", json_schema={"type": "object"})
    assert result.status == STATUS_PASS2_FAILED
    # Grounded answer + citations still returned
    assert result.answer_text == "Answer."
    assert len(result.citations) == 1
    assert "pass 2 timeout" in result.reason


def test_json_requested_without_pass2_fn_returns_status_pass2_failed():
    def pass1(_p):
        return _mk_pass1_response(text="Answer.")

    orch = DualPassCitationOrchestrator(pass1_fn=pass1, pass2_fn=None)
    env = _envelope([_chunk()])
    result = orch.execute(env, query="q", json_schema={"type": "object"})
    assert result.status == STATUS_PASS2_FAILED
    assert "pass2_fn not provided" in result.reason


# ---------------------------------------------------------------------------
# Pass 1 payload shape (integration with P1.2 + P2.1)
# ---------------------------------------------------------------------------


def test_pass1_payload_has_messages_and_cache_structure():
    captured: list[dict[str, Any]] = []

    def pass1(payload):
        captured.append(payload)
        return _mk_pass1_response(text=".")

    orch = DualPassCitationOrchestrator(pass1_fn=pass1)
    chunks = [_chunk(f"c{i}", content="x" * 100) for i in range(5)]
    env = _envelope(chunks, task_spec="Answer from documents.")
    orch.execute(env, query="how does it work?")

    payload = captured[0]
    assert "messages" in payload
    assert payload["messages"][0]["role"] == "user"
    # content is a list of blocks (may be 1 or 2 depending on cache boundary)
    assert isinstance(payload["messages"][0]["content"], list)


# ---------------------------------------------------------------------------
# Result dataclass contract
# ---------------------------------------------------------------------------


def test_result_is_frozen_dataclass():
    r = DualPassResult(
        answer_text="x",
        citations=(),
        structured_output=None,
        citation_coverage=0.0,
        status=STATUS_OK,
    )
    with pytest.raises((AttributeError, TypeError)):
        r.answer_text = "mutated"  # type: ignore[misc]


def test_result_citations_is_tuple_not_list():
    def pass1(_p):
        return _mk_pass1_response(text=".")

    orch = DualPassCitationOrchestrator(pass1_fn=pass1)
    env = _envelope([_chunk()])
    result = orch.execute(env, query="q")
    assert isinstance(result.citations, tuple)
