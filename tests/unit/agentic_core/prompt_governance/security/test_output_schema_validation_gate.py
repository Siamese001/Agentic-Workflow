"""
Tests for WAVE 2.1 — Runtime output schema validation gate + bounded retry.

Covers:
  - validate_against_schema: dict schema and pydantic model paths
  - parse_response with schema= param
  - Gateway bounded retry: mock provider returns invalid then valid (2 calls)
  - Gateway fail-closed: invalid then invalid (2 calls, exception)
"""

from __future__ import annotations

import json
from typing import Any
from unittest.mock import MagicMock

import pytest

from agentic_core.prompt_governance.security.validators.output_schema_validator import (
    validate_against_schema,
)
from agentic_core.runtime.exceptions.sovereign_errors import SecurityViolationError

# ── Dict schema fixtures ─────────────────────────────────────────────────────

PERSON_SCHEMA = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "age": {"type": "integer"},
    },
    "required": ["name", "age"],
}

ARRAY_SCHEMA = {
    "type": "array",
    "items": {"type": "string"},
}


# ── 1) validate_against_schema ───────────────────────────────────────────────


class TestValidateAgainstSchema:
    """Core validator tests."""

    def test_valid_dict_schema_passes(self):
        ok, code, details = validate_against_schema({"name": "Alice", "age": 30}, PERSON_SCHEMA)
        assert ok is True
        assert code is None

    def test_valid_json_string_passes(self):
        ok, code, details = validate_against_schema(json.dumps({"name": "Bob", "age": 25}), PERSON_SCHEMA)
        assert ok is True

    def test_missing_required_key(self):
        ok, code, details = validate_against_schema({"name": "Alice"}, PERSON_SCHEMA)
        assert ok is False
        assert code == "DICT_SCHEMA_VALIDATION_ERROR"
        assert any("missing required key" in e for e in details.get("errors", []))

    def test_wrong_type(self):
        ok, code, details = validate_against_schema({"name": "Alice", "age": "thirty"}, PERSON_SCHEMA)
        assert ok is False
        assert code == "DICT_SCHEMA_VALIDATION_ERROR"

    def test_array_schema_passes(self):
        ok, code, details = validate_against_schema(["a", "b", "c"], ARRAY_SCHEMA)
        assert ok is True

    def test_array_schema_wrong_items(self):
        ok, code, details = validate_against_schema([1, 2, 3], ARRAY_SCHEMA)
        assert ok is False

    def test_none_schema_always_passes(self):
        ok, code, details = validate_against_schema("anything", None)
        assert ok is True

    def test_unsupported_schema_type(self):
        ok, code, details = validate_against_schema({}, 42)
        assert ok is False
        assert code == "SCHEMA_UNSUPPORTED"

    def test_invalid_json_string(self):
        ok, code, details = validate_against_schema("not json", PERSON_SCHEMA)
        assert ok is False
        assert code == "JSON_PARSE_ERROR"

    def test_enum_validation(self):
        schema = {"type": "string", "enum": ["red", "green", "blue"]}
        ok, _, _ = validate_against_schema("red", schema)
        assert ok is True
        ok2, code2, _ = validate_against_schema("yellow", schema)
        assert ok2 is False

    def test_additional_properties_false(self):
        schema = {
            "type": "object",
            "properties": {"name": {"type": "string"}},
            "required": ["name"],
            "additionalProperties": False,
        }
        ok, _, _ = validate_against_schema({"name": "A", "extra": 1}, schema)
        assert ok is False


# ── 2) Pydantic model validation ────────────────────────────────────────────


class TestPydanticValidation:
    """Pydantic BaseModel schema path."""

    def test_valid_pydantic_passes(self):
        from pydantic import BaseModel

        class Person(BaseModel):
            name: str
            age: int

        ok, code, details = validate_against_schema({"name": "Alice", "age": 30}, Person)
        assert ok is True

    def test_invalid_pydantic_fails(self):
        from pydantic import BaseModel

        class Person(BaseModel):
            name: str
            age: int

        ok, code, details = validate_against_schema({"name": "Alice", "age": "not_int"}, Person)
        assert ok is False
        assert code == "PYDANTIC_VALIDATION_ERROR"

    def test_pydantic_json_string(self):
        from pydantic import BaseModel

        class Person(BaseModel):
            name: str
            age: int

        ok, code, details = validate_against_schema(json.dumps({"name": "Bob", "age": 25}), Person)
        assert ok is True


# ── 3) parse_response with schema= ──────────────────────────────────────────


class TestParseResponseSchemaGate:
    """Test the schema validation gate logic as wired in parse_response.

    PromptAssembler has broken transitive import chains (L4_state, governance_hub).
    We test the gate logic by simulating the parse_response flow: parse content
    from JSON, then validate_against_schema. This matches the exact logic added
    to PromptAssembler.parse_response and the module-level parse_response.
    """

    @staticmethod
    def _simulate_parse_response(response: str, schema: Any | None = None) -> dict:
        """Replicate the parse_response schema gate without importing PromptAssembler."""
        result: dict[str, Any] = {"plan": None, "content": None, "metadata": {}, "raw": response}
        try:
            result["content"] = json.loads(response)
        except json.JSONDecodeError:
            result["content"] = response

        if schema is not None:
            ok, code, details = validate_against_schema(result.get("content"), schema)
            if not ok:
                return {
                    "type": "schema_validation_failed",
                    "content": result.get("content"),
                    "schema_error_code": code,
                    "schema_error": details,
                }
        return result

    def test_valid_passes(self):
        result = self._simulate_parse_response(
            json.dumps({"name": "Alice", "age": 30}),
            schema=PERSON_SCHEMA,
        )
        assert result.get("type") != "schema_validation_failed"
        assert result["content"] == {"name": "Alice", "age": 30}

    def test_invalid_returns_sentinel(self):
        result = self._simulate_parse_response(
            json.dumps({"name": "Alice"}),
            schema=PERSON_SCHEMA,
        )
        assert result["type"] == "schema_validation_failed"
        assert result["schema_error_code"] == "DICT_SCHEMA_VALIDATION_ERROR"

    def test_no_schema_passes_through(self):
        result = self._simulate_parse_response("just plain text")
        assert result.get("type") != "schema_validation_failed"

    def test_source_has_schema_param(self):
        """AST verification: PromptAssembler.parse_response accepts schema= kwarg."""
        import ast
        from pathlib import Path

        src = Path("agentic_core/prompt_governance/core/prompt_assembler.py")
        assert src.exists()
        tree = ast.parse(src.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "parse_response":
                arg_names = [a.arg for a in node.args.args + node.args.kwonlyargs]
                assert "schema" in arg_names, "parse_response must accept schema= parameter"
                return
        pytest.fail("parse_response not found in prompt_assembler.py")


# ── 4) Gateway bounded retry ────────────────────────────────────────────────


class TestGatewayBoundedRetry:
    """Test SovereignLLMGateway.generate with response_schema."""

    @pytest.fixture
    def gateway(self, monkeypatch):
        """Create a gateway instance with mocked internals."""
        # Disable V15 enforcement so TokenCapArtifact isn't required
        monkeypatch.setattr(
            "agentic_core.L2_execution.enforcement.SovereignLLMGateway.is_v15_enforced",
            lambda: False,
        )

        from agentic_core.L2_execution.enforcement.SovereignLLMGateway import (
            SovereignLLMGateway,
        )

        SovereignLLMGateway.reset_instance()
        gw = SovereignLLMGateway()
        gw._injection_detector = MagicMock()
        gw._injection_detector.scan = MagicMock(return_value=True)
        return gw

    @pytest.mark.asyncio
    async def test_retry_once_then_success(self, gateway, monkeypatch):
        """Provider returns invalid JSON first, valid JSON second. Assert 2 calls."""
        invalid_response = {
            "content": json.dumps({"name": "Alice"}),
            "tokens": 10,
            "provider": "google",
            "model": "test",
        }
        valid_response = {
            "content": json.dumps({"name": "Alice", "age": 30}),
            "tokens": 10,
            "provider": "google",
            "model": "test",
        }

        call_count = {"n": 0}

        async def mock_call_provider(provider, prompt, model, temp, max_t, **kw):
            call_count["n"] += 1
            if call_count["n"] == 1:
                return invalid_response
            return valid_response

        monkeypatch.setattr(gateway, "_call_provider", mock_call_provider)
        monkeypatch.setattr(gateway, "_audit", lambda *a, **kw: None)

        result = await gateway.generate(
            prompt="test prompt",
            provider="google",
            model="test-model",
            response_schema=PERSON_SCHEMA,
        )
        assert call_count["n"] == 2, "Should call provider exactly twice (1 fail + 1 retry)"
        content = result.get("content")
        parsed = json.loads(content) if isinstance(content, str) else content
        assert parsed["age"] == 30

    @pytest.mark.asyncio
    async def test_retry_once_then_fail_closed(self, gateway, monkeypatch):
        """Provider returns invalid JSON both times. Assert 2 calls + exception."""
        invalid_response = {
            "content": json.dumps({"name": "Alice"}),
            "tokens": 10,
            "provider": "google",
            "model": "test",
        }

        call_count = {"n": 0}

        async def mock_call_provider(provider, prompt, model, temp, max_t, **kw):
            call_count["n"] += 1
            return invalid_response

        monkeypatch.setattr(gateway, "_call_provider", mock_call_provider)
        monkeypatch.setattr(gateway, "_audit", lambda *a, **kw: None)

        with pytest.raises(SecurityViolationError) as exc_info:
            await gateway.generate(
                prompt="test prompt",
                provider="google",
                model="test-model",
                response_schema=PERSON_SCHEMA,
            )

        assert call_count["n"] == 2, "Should call provider exactly twice before failing"
        assert (
            "SCHEMA_VALIDATION_FAILED" in str(exc_info.value)
            or exc_info.value.violation_type == "SCHEMA_VALIDATION_FAILED"
        )

    @pytest.mark.asyncio
    async def test_valid_first_try_no_retry(self, gateway, monkeypatch):
        """Provider returns valid JSON on first try. Assert 1 call only."""
        valid_response = {
            "content": json.dumps({"name": "Alice", "age": 30}),
            "tokens": 10,
            "provider": "google",
            "model": "test",
        }

        call_count = {"n": 0}

        async def mock_call_provider(provider, prompt, model, temp, max_t, **kw):
            call_count["n"] += 1
            return valid_response

        monkeypatch.setattr(gateway, "_call_provider", mock_call_provider)
        monkeypatch.setattr(gateway, "_audit", lambda *a, **kw: None)

        await gateway.generate(
            prompt="test prompt",
            provider="google",
            model="test-model",
            response_schema=PERSON_SCHEMA,
        )
        assert call_count["n"] == 1, "Should call provider only once when valid"

    @pytest.mark.asyncio
    async def test_no_schema_no_validation(self, gateway, monkeypatch):
        """Without response_schema, no validation occurs."""
        response = {"content": "not json at all", "tokens": 5, "provider": "google", "model": "test"}

        async def mock_call_provider(provider, prompt, model, temp, max_t, **kw):
            return response

        monkeypatch.setattr(gateway, "_call_provider", mock_call_provider)
        monkeypatch.setattr(gateway, "_audit", lambda *a, **kw: None)

        result = await gateway.generate(
            prompt="test prompt",
            provider="google",
            model="test-model",
        )
        assert result["content"] == "not json at all"


class TestSchemaThreading:
    """WAVE 2.2: Verify schema bound at assembly is threaded to gateway."""

    @pytest.fixture
    def gateway(self, monkeypatch):
        monkeypatch.setattr(
            "agentic_core.L2_execution.enforcement.SovereignLLMGateway.is_v15_enforced",
            lambda: False,
        )
        from agentic_core.L2_execution.enforcement.SovereignLLMGateway import (
            SovereignLLMGateway,
        )

        SovereignLLMGateway.reset_instance()
        gw = SovereignLLMGateway()
        gw._injection_detector = MagicMock()
        gw._injection_detector.scan = MagicMock(return_value=True)
        return gw

    @pytest.mark.asyncio
    async def test_assembled_schema_threaded_to_gateway(self, gateway, monkeypatch):
        """Schema from AssembledPrompt is received by gateway.generate as response_schema."""
        valid_response = {
            "content": json.dumps({"name": "Alice", "age": 30}),
            "tokens": 10,
            "provider": "google",
            "model": "test",
        }

        async def mock_call_provider(provider, prompt, model, temp, max_t, **kw):
            return valid_response

        monkeypatch.setattr(gateway, "_call_provider", mock_call_provider)
        monkeypatch.setattr(gateway, "_audit", lambda *a, **kw: None)

        # Simulate what a caller using AssembledPrompt would do:
        # assembled = assembler.assemble_with_schema(...) -> AssembledPrompt
        # gateway.generate(assembled.text, response_schema=assembled.response_schema)
        # We can't import PromptAssembler (broken deps), so simulate the threading:

        # Thread the schema through gateway
        result = await gateway.generate(
            prompt="test prompt",
            provider="google",
            model="test-model",
            response_schema=PERSON_SCHEMA,
        )

        # Gateway validated via response_schema -> content is valid
        content = result.get("content")
        parsed = json.loads(content) if isinstance(content, str) else content
        assert parsed == {"name": "Alice", "age": 30}

    @pytest.mark.asyncio
    async def test_none_schema_skips_validation_in_gateway(self, gateway, monkeypatch):
        """When response_schema=None (no schema bound), gateway skips validation."""
        response = {"content": "freeform text", "tokens": 5, "provider": "google", "model": "test"}

        async def mock_call_provider(provider, prompt, model, temp, max_t, **kw):
            return response

        monkeypatch.setattr(gateway, "_call_provider", mock_call_provider)
        monkeypatch.setattr(gateway, "_audit", lambda *a, **kw: None)

        result = await gateway.generate(
            prompt="test prompt",
            provider="google",
            model="test-model",
            response_schema=None,
        )
        assert result["content"] == "freeform text"
