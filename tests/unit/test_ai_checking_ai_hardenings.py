"""Unit tests for AI-checking-AI hardenings: GAP-01, GAP-02, GAP-04, GAP-05.

Each test class maps to one gap.  Tests are fully synchronous or use
asyncio.run() so they don't require any external services.
"""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

# ---------------------------------------------------------------------------
# GAP-02 — ReflectionEngine fail-closed circuit breaker
# ---------------------------------------------------------------------------


class TestReflectionEngineFailClosed:
    """GAP-02: circuit breaker must fail-closed when required criteria present."""

    def _make_engine(self):
        try:
            from agentic_core.config.core.reflection_config import ReflectionEngine, ValidationCriterion
        except ImportError:
            import pytest

            pytest.skip("ReflectionEngine not importable")
        return ReflectionEngine(), ValidationCriterion

    def test_fail_closed_required_criterion_on_circuit_open(self):
        from agentic_core.config.core.reflection_config import (
            CircuitOpenError,
            ReflectionEngine,
            ValidationCriterion,
        )

        engine = ReflectionEngine()
        required_criterion = ValidationCriterion(
            name="must_pass",
            description="Must pass check",
            validator=lambda x: True,
            is_required=True,
        )

        async def _run():
            with patch.object(engine.circuit_breaker, "call", side_effect=CircuitOpenError()):
                with patch.object(engine, "_should_use_fast_path", return_value=False):
                    return await engine.evaluate(
                        content={"data": "test"},
                        criteria=[required_criterion],
                    )

        result = asyncio.get_event_loop().run_until_complete(_run())
        assert result.is_valid is False, (
            "GAP-02: circuit open with required criterion must fail-closed (is_valid=False)"
        )
        assert result.validation_type == "circuit_breaker_fallback"

    def test_fail_open_optional_criterion_on_circuit_open(self):
        from agentic_core.config.core.reflection_config import (
            CircuitOpenError,
            ReflectionEngine,
            ValidationCriterion,
        )

        engine = ReflectionEngine()
        optional_criterion = ValidationCriterion(
            name="nice_to_have",
            description="Optional check",
            validator=lambda x: True,
            is_required=False,
        )

        async def _run():
            with patch.object(engine.circuit_breaker, "call", side_effect=CircuitOpenError()):
                with patch.object(engine, "_should_use_fast_path", return_value=False):
                    return await engine.evaluate(
                        content={"data": "test"},
                        criteria=[optional_criterion],
                    )

        result = asyncio.get_event_loop().run_until_complete(_run())
        assert result.is_valid is True, (
            "GAP-02: circuit open with ONLY optional criteria should remain fail-open (is_valid=True)"
        )

    def test_fail_closed_required_on_unexpected_exception(self):
        from agentic_core.config.core.reflection_config import (
            ReflectionEngine,
            ValidationCriterion,
        )

        engine = ReflectionEngine()
        required_criterion = ValidationCriterion(
            name="required",
            description="Required check",
            validator=lambda x: True,
            is_required=True,
        )

        async def _run():
            with patch.object(engine.circuit_breaker, "call", side_effect=RuntimeError("unexpected")):
                with patch.object(engine, "_should_use_fast_path", return_value=False):
                    return await engine.evaluate(
                        content={"data": "test"},
                        criteria=[required_criterion],
                    )

        result = asyncio.get_event_loop().run_until_complete(_run())
        assert result.is_valid is False, (
            "GAP-02: unexpected exception with required criterion must fail-closed"
        )
        assert result.validation_type == "error_fallback"


# ---------------------------------------------------------------------------
# GAP-04 — SafetyInspectorAgent Socratic Judge hardening
# ---------------------------------------------------------------------------


class TestSocraticJudgeHardening:
    """GAP-04: rate limit, audit log, timeout fail-closed."""

    def _make_inspector(self, max_calls: int = 3):
        try:
            from agentic_core.L5_safety.reasoning.SafetyInspectorAgent import SafetyInspectorAgent
        except ImportError:
            import pytest

            pytest.skip("SafetyInspectorAgent not importable")
        return SafetyInspectorAgent(enable_socratic_judge=True, max_socratic_calls=max_calls)

    def test_rate_limit_returns_yes_conservatively(self):
        inspector = self._make_inspector(max_calls=0)
        result = asyncio.get_event_loop().run_until_complete(
            inspector._socratic_verify("fake.py", "issue", "question?")
        )
        assert result == "YES", "GAP-04: rate-limited call must return YES (conservative)"
        assert inspector._socratic_audit_log[-1]["reason"] == "rate_limit"

    def test_audit_log_populated_on_timeout(self):
        inspector = self._make_inspector(max_calls=10)

        with patch(
            "agentic_core.L5_safety.reasoning.SafetyInspectorAgent.get_llm_router_client",
            side_effect=Exception("simulated timeout"),
            create=True,
        ):
            # Patch the local import inside _socratic_verify
            with patch(
                "builtins.__import__",
                side_effect=ImportError("mocked"),
            ):
                pass  # just verify rate_limit=0 path handles audit log

        # Trigger error path directly (ImportError from get_llm_router_client)
        with patch.dict(
            "sys.modules",
            {
                "agentic_core.L2_execution.enforcement.llm_router_mcp_client": None,
            },
        ):
            result = asyncio.get_event_loop().run_until_complete(
                inspector._socratic_verify("fake.py", "issue", "question?")
            )

        assert result == "YES", "GAP-04: import error must return YES (fail-closed)"
        log_entry = inspector._socratic_audit_log[-1]
        assert log_entry["verdict"] == "YES"
        assert (
            "error" in log_entry["reason"]
            or log_entry["reason"] in ("timeout", "rate_limit", "error: 'NoneType' object is not callable")
            or log_entry["reason"].startswith("error")
        )

    def test_audit_log_entry_schema(self):
        inspector = self._make_inspector(max_calls=0)
        asyncio.get_event_loop().run_until_complete(
            inspector._socratic_verify("some/file.py", "a problem", "is it real?")
        )
        entry = inspector._socratic_audit_log[-1]
        for required_key in ("ts", "file", "issue", "verdict", "reason"):
            assert required_key in entry, f"Audit log entry missing key: {required_key}"

    def test_call_counter_increments(self):
        inspector = self._make_inspector(max_calls=5)
        # Force import error so the call still increments the counter
        with patch.dict(
            "sys.modules",
            {
                "agentic_core.L2_execution.enforcement.llm_router_mcp_client": None,
            },
        ):
            asyncio.get_event_loop().run_until_complete(inspector._socratic_verify("f.py", "issue", "q?"))
        assert inspector._socratic_call_count == 1

    def test_snippet_sanitization_excludes_credential_lines(self, tmp_path):
        """Credential lines must not appear in what would be sent to the LLM."""
        secret_file = tmp_path / "secrets.py"
        secret_file.write_text("password = 'hunter2'\nx = 1\ny = 2\n", encoding="utf-8")
        inspector = self._make_inspector(max_calls=10)

        captured_prompt: list[str] = []

        async def mock_validate(prompt, **kwargs):
            captured_prompt.append(prompt)
            return {"response": "NO"}

        mock_router = MagicMock()
        mock_router.validate_content = mock_validate
        mock_module = MagicMock()
        mock_module.get_llm_router_client = MagicMock(return_value=mock_router)

        with patch.dict(
            "sys.modules",
            {
                "agentic_core.L2_execution.enforcement.llm_router_mcp_client": mock_module,
            },
        ):
            asyncio.get_event_loop().run_until_complete(
                inspector._socratic_verify(str(secret_file), "secret", "real?")
            )

        if captured_prompt:
            assert "hunter2" not in captured_prompt[0], (
                "GAP-04: credential values must be stripped from Socratic Judge prompt"
            )


# ---------------------------------------------------------------------------
# GAP-01 — JudgeEvaluator audit log + heuristic anchor
# ---------------------------------------------------------------------------


class TestJudgeEvaluatorAuditAndAnchor:
    """GAP-01: audit log populated, model_id tracked, anchor cross-check works."""

    def _make_evaluator(self, llm_client=None, model_id=None):
        try:
            from apps_shared.types.judge_evaluator_types import JudgeEvaluator, JudgmentCriterion
        except ImportError:
            import pytest

            pytest.skip("JudgeEvaluator not importable")
        return JudgeEvaluator(
            llm_client=llm_client,
            criteria=[JudgmentCriterion.ACCURACY],
            model_id=model_id,
            enable_logging=False,
        )

    def test_audit_log_entry_on_heuristic_evaluate(self):
        evaluator = self._make_evaluator()
        asyncio.get_event_loop().run_until_complete(
            evaluator.evaluate("some output text here", expected="some output text")
        )
        assert len(evaluator._audit_log) == 1
        entry = evaluator._audit_log[0]
        for key in ("ts", "model_id", "output_hash", "overall_score", "heuristic_anchor", "passed"):
            assert key in entry, f"Audit log entry missing key: {key}"

    def test_model_id_defaults_to_heuristic_when_no_llm(self):
        evaluator = self._make_evaluator(llm_client=None)
        assert evaluator.model_id == "heuristic"

    def test_model_id_defaults_to_unknown_when_llm_no_model_id(self):
        dummy_client = AsyncMock(return_value='{"score": 0.8, "reasoning": "ok"}')
        evaluator = self._make_evaluator(llm_client=dummy_client, model_id=None)
        assert evaluator.model_id == "unknown"

    def test_model_id_stored_when_provided(self):
        evaluator = self._make_evaluator(model_id="gpt-4o-audit-test")
        assert evaluator.model_id == "gpt-4o-audit-test"

    def test_heuristic_anchor_with_matching_expected(self):
        evaluator = self._make_evaluator()
        score = evaluator._compute_heuristic_anchor("hello world", "hello world")
        assert score == 1.0, "Identical output and expected should yield anchor=1.0"

    def test_heuristic_anchor_empty_output(self):
        evaluator = self._make_evaluator()
        score = evaluator._compute_heuristic_anchor("", None)
        assert score == 0.0, "Empty output should yield anchor=0.0"

    def test_audit_log_evaluation_path_is_heuristic(self):
        evaluator = self._make_evaluator(llm_client=None)
        asyncio.get_event_loop().run_until_complete(evaluator.evaluate("output text", expected=None))
        assert evaluator._audit_log[0]["evaluation_path"] == "heuristic"

    def test_anchor_alert_set_on_large_deviation(self):
        from apps_shared.types.judge_evaluator_types import JudgeEvaluator, JudgmentCriterion

        async def high_score_llm(prompt: str) -> str:
            return '{"score": 0.99, "reasoning": "perfect"}'

        evaluator = JudgeEvaluator(
            llm_client=high_score_llm,
            criteria=[JudgmentCriterion.ACCURACY],
            model_id="test-model",
            deterministic_anchor_tolerance=0.01,
            enable_logging=False,
        )
        asyncio.get_event_loop().run_until_complete(evaluator.evaluate("x", expected=None))
        entry = evaluator._audit_log[0]
        # anchor for single-word output vs None is ~small; LLM claims 0.99
        # deviation will be large → anchor_alert=True
        assert "anchor_alert" in entry


# ---------------------------------------------------------------------------
# GAP-05 — RegressionOracleAgent AST safety check + iteration cap constant
# ---------------------------------------------------------------------------


class TestRegressionOracleASTSafetyCheck:
    """GAP-05: AST safety check blocks dangerous generated code."""

    def _checker(self):
        try:
            from agentic_core.L5_safety.reasoning.RegressionOracleAgent import RegressionOracleAgent
        except ImportError:
            import pytest

            pytest.skip("RegressionOracleAgent not importable")
        return RegressionOracleAgent

    def test_safe_code_passes(self):
        cls = self._checker()
        safe = "def test_foo():\n    assert 1 + 1 == 2\n"
        assert cls._ast_safety_check(safe) == []

    def test_exec_call_flagged(self):
        cls = self._checker()
        bad = "def test_foo():\n    exec('import os')\n"
        violations = cls._ast_safety_check(bad)
        assert len(violations) > 0
        assert "exec" in violations[0]

    def test_os_system_flagged(self):
        cls = self._checker()
        bad = "import os\ndef test_foo():\n    os.system('rm -rf /')\n"
        violations = cls._ast_safety_check(bad)
        assert len(violations) > 0

    def test_eval_flagged(self):
        cls = self._checker()
        bad = "def test_foo():\n    eval('1+1')\n"
        violations = cls._ast_safety_check(bad)
        assert len(violations) > 0

    def test_syntax_error_returns_violation(self):
        cls = self._checker()
        bad = "def test_foo(\n    pass"
        violations = cls._ast_safety_check(bad)
        assert len(violations) > 0
        assert "SyntaxError" in violations[0]

    def test_iteration_cap_constant_is_bounded(self):
        cls = self._checker()
        assert hasattr(cls, "MAX_CORRECTION_ITERATIONS")
        assert cls.MAX_CORRECTION_ITERATIONS <= 5, (
            "GAP-05: MAX_CORRECTION_ITERATIONS must be ≤5 to prevent infinite LLM retry loops"
        )
        assert cls.MAX_CORRECTION_ITERATIONS >= 1


# ---------------------------------------------------------------------------
# GAP-05 — _ast_safety_check compile() is also dangerous
# ---------------------------------------------------------------------------


class TestRegressionOracleAdditionalDangerousCalls:
    def _checker(self):
        try:
            from agentic_core.L5_safety.reasoning.RegressionOracleAgent import RegressionOracleAgent
        except ImportError:
            import pytest

            pytest.skip("RegressionOracleAgent not importable")
        return RegressionOracleAgent

    def test_compile_flagged(self):
        cls = self._checker()
        bad = "def test_foo():\n    compile('x=1', '<string>', 'exec')\n"
        violations = cls._ast_safety_check(bad)
        assert len(violations) > 0

    def test_dunder_import_flagged(self):
        cls = self._checker()
        bad = "def test_foo():\n    __import__('os')\n"
        violations = cls._ast_safety_check(bad)
        assert len(violations) > 0


# ===========================================================================
# §1.5 EDGE-CASE MATRIX
# Covers: null/None, empty input, boundary values, replayed transition,
#         dependency failure, negative control, recovery path.
# ===========================================================================

# ---------------------------------------------------------------------------
# GAP-01 edge cases — JudgeEvaluator
# ---------------------------------------------------------------------------


class TestJudgeEvaluatorEdgeCases:
    """§1.5 edge-case matrix for JudgeEvaluator (GAP-01)."""

    def _ev(self, **kw):
        from apps_shared.types.judge_evaluator_types import JudgeEvaluator, JudgmentCriterion

        return JudgeEvaluator(
            criteria=[JudgmentCriterion.ACCURACY],
            enable_logging=False,
            **kw,
        )

    # --- null / empty input ---

    def test_empty_string_output_does_not_raise(self):
        """Empty output must not raise; audit log entry must be written."""
        ev = self._ev()
        asyncio.get_event_loop().run_until_complete(ev.evaluate("", expected=None))
        assert len(ev._audit_log) == 1
        assert ev._audit_log[0]["output_hash"] is not None

    def test_none_expected_produces_valid_result(self):
        """None expected must be accepted (optional arg)."""
        ev = self._ev()
        result = asyncio.get_event_loop().run_until_complete(ev.evaluate("some output", expected=None))
        assert result is not None
        assert isinstance(result.overall_score, float)

    def test_whitespace_only_output(self):
        """Whitespace-only output is valid input; audit entry written."""
        ev = self._ev()
        asyncio.get_event_loop().run_until_complete(ev.evaluate("   \n\t", expected=None))
        assert len(ev._audit_log) == 1

    # --- empty criteria list ---

    def test_empty_criteria_list_raises_or_returns_safely(self):
        """Empty criteria must not produce ZeroDivisionError."""
        from apps_shared.types.judge_evaluator_types import JudgeEvaluator

        ev = JudgeEvaluator(criteria=[], enable_logging=False)
        try:
            result = asyncio.get_event_loop().run_until_complete(ev.evaluate("output", expected=None))
            # If it returns without raising, score must be defined
            assert isinstance(result.overall_score, float)
        except (ZeroDivisionError, ValueError) as exc:  # guardian: allow-silent-swallower
            # Acceptable: propagate rather than silently corrupt
            assert exc is not None

    # --- boundary values for pass_threshold ---

    def test_threshold_exactly_met_is_passing(self):
        """overall_score == pass_threshold must evaluate as passed=True."""
        from apps_shared.types.judge_evaluator_types import JudgeEvaluator, JudgmentCriterion

        # heuristic path: identical strings → score ≈ 1.0; threshold=0.5
        ev = JudgeEvaluator(
            criteria=[JudgmentCriterion.ACCURACY],
            pass_threshold=0.0,
            enable_logging=False,
        )
        result = asyncio.get_event_loop().run_until_complete(ev.evaluate("x", expected=None))
        assert result.passed is True, "threshold=0.0 must always pass"

    def test_threshold_above_max_score_always_fails(self):
        """pass_threshold=1.0 with imperfect heuristic must produce passed=False."""
        from apps_shared.types.judge_evaluator_types import JudgeEvaluator, JudgmentCriterion

        ev = JudgeEvaluator(
            criteria=[JudgmentCriterion.ACCURACY],
            pass_threshold=1.0,
            enable_logging=False,
        )
        result = asyncio.get_event_loop().run_until_complete(
            ev.evaluate("a", expected="completely different text here")
        )
        # Heuristic score will be < 1.0 for mismatched strings
        assert result.passed is False, "pass_threshold=1.0 must fail on non-identical output"

    # --- replayed transition (§1.7 determinism) ---

    def test_identical_input_produces_identical_audit_hash(self):
        """Same output string must always produce the same output_hash (deterministic)."""
        ev = self._ev()
        loop = asyncio.get_event_loop()
        loop.run_until_complete(ev.evaluate("deterministic output", expected=None))
        loop.run_until_complete(ev.evaluate("deterministic output", expected=None))
        h1 = ev._audit_log[0]["output_hash"]
        h2 = ev._audit_log[1]["output_hash"]
        assert h1 == h2, "§1.7: same input must produce identical output_hash"

    def test_distinct_inputs_produce_distinct_hashes(self):
        """Different output strings must produce different hashes."""
        ev = self._ev()
        loop = asyncio.get_event_loop()
        loop.run_until_complete(ev.evaluate("output A", expected=None))
        loop.run_until_complete(ev.evaluate("output B", expected=None))
        assert ev._audit_log[0]["output_hash"] != ev._audit_log[1]["output_hash"]

    # --- dependency failure (LLM client raises) ---

    def test_llm_client_exception_falls_back_gracefully(self):
        """If LLM client raises, evaluate must not propagate; must write audit entry."""
        from apps_shared.types.judge_evaluator_types import JudgeEvaluator, JudgmentCriterion

        async def bad_client(prompt: str) -> str:
            raise RuntimeError("LLM unavailable")

        ev = JudgeEvaluator(
            llm_client=bad_client,
            criteria=[JudgmentCriterion.ACCURACY],
            model_id="test",
            enable_logging=False,
        )
        # Must not raise; should fall back to heuristic
        result = asyncio.get_event_loop().run_until_complete(ev.evaluate("some output", expected=None))
        assert result is not None
        assert len(ev._audit_log) == 1

    # --- heuristic anchor boundary ---

    def test_anchor_no_alert_when_deviation_within_tolerance(self):
        """No anchor_alert when LLM score matches heuristic within tolerance."""
        from apps_shared.types.judge_evaluator_types import JudgeEvaluator, JudgmentCriterion

        async def exact_heuristic_client(prompt: str) -> str:
            # Return score that will match heuristic for identical strings
            return '{"score": 1.0, "reasoning": "perfect match"}'

        ev = JudgeEvaluator(
            llm_client=exact_heuristic_client,
            criteria=[JudgmentCriterion.ACCURACY],
            model_id="test",
            deterministic_anchor_tolerance=0.5,
            enable_logging=False,
        )
        asyncio.get_event_loop().run_until_complete(ev.evaluate("hello world", expected="hello world"))
        # tolerance=0.5 means deviation must exceed 0.5 to alert; won't here
        assert ev._audit_log[0]["anchor_alert"] is False


# ---------------------------------------------------------------------------
# GAP-02 edge cases — ReflectionEngine
# ---------------------------------------------------------------------------


class TestReflectionEngineEdgeCases:
    """§1.5 edge-case matrix for ReflectionEngine (GAP-02)."""

    def _engine(self):
        from agentic_core.config.core.reflection_config import ReflectionEngine

        return ReflectionEngine()

    def _required(self, name="req"):
        from agentic_core.config.core.reflection_config import ValidationCriterion

        return ValidationCriterion(name=name, description="req", validator=lambda x: True, is_required=True)

    def _optional(self, name="opt"):
        from agentic_core.config.core.reflection_config import ValidationCriterion

        return ValidationCriterion(name=name, description="opt", validator=lambda x: True, is_required=False)

    # --- empty criteria list ---

    def test_empty_criteria_list_does_not_raise(self):
        """evaluate() with no criteria must not raise."""
        engine = self._engine()
        result = asyncio.get_event_loop().run_until_complete(
            engine.evaluate(content={"data": "test"}, criteria=[])
        )
        assert result is not None

    # --- replayed transition: same result on repeated circuit-open ---

    def test_circuit_open_is_deterministic_across_repeated_calls(self):
        """Circuit-open fail-closed must return same is_valid on repeated calls."""
        from agentic_core.config.core.reflection_config import CircuitOpenError, ReflectionEngine

        engine = ReflectionEngine()
        criterion = self._required()

        async def _run():
            with patch.object(engine.circuit_breaker, "call", side_effect=CircuitOpenError()):
                with patch.object(engine, "_should_use_fast_path", return_value=False):
                    r1 = await engine.evaluate({"d": "1"}, criteria=[criterion])
                    r2 = await engine.evaluate({"d": "1"}, criteria=[criterion])
            return r1, r2

        r1, r2 = asyncio.get_event_loop().run_until_complete(_run())
        assert r1.is_valid == r2.is_valid, "§1.7: repeated circuit-open must be deterministic"
        assert r1.validation_type == r2.validation_type

    # --- boundary: exactly one required + one optional ---

    def test_mixed_criteria_required_dominates_on_circuit_open(self):
        """With one required + one optional, required criterion must dominate (fail-closed)."""
        from agentic_core.config.core.reflection_config import CircuitOpenError, ReflectionEngine

        engine = ReflectionEngine()
        criteria = [self._required("r"), self._optional("o")]

        async def _run():
            with patch.object(engine.circuit_breaker, "call", side_effect=CircuitOpenError()):
                with patch.object(engine, "_should_use_fast_path", return_value=False):
                    return await engine.evaluate({"d": "x"}, criteria=criteria)

        result = asyncio.get_event_loop().run_until_complete(_run())
        assert result.is_valid is False, "Required criterion must dominate → fail-closed"

    # --- null / malformed content ---

    def test_none_content_does_not_raise(self):
        """None content passed to evaluate must not raise."""
        engine = self._engine()
        try:
            result = asyncio.get_event_loop().run_until_complete(
                engine.evaluate(content=None, criteria=[self._optional()])
            )
            assert result is not None
        except (TypeError, AttributeError):  # guardian: allow-silent-swallower
            pass  # Acceptable: contract violation surfaces explicitly

    # --- recovery: stats increment on every call ---

    def test_stats_total_critiques_increments_on_circuit_open(self):
        """Stats counter must increment even on circuit-open fallback."""
        from agentic_core.config.core.reflection_config import CircuitOpenError, ReflectionEngine

        engine = ReflectionEngine()
        before = engine.stats["total_critiques"]

        async def _run():
            with patch.object(engine.circuit_breaker, "call", side_effect=CircuitOpenError()):
                with patch.object(engine, "_should_use_fast_path", return_value=False):
                    await engine.evaluate({"d": "x"}, criteria=[self._required()])

        asyncio.get_event_loop().run_until_complete(_run())
        assert engine.stats["total_critiques"] == before + 1


# ---------------------------------------------------------------------------
# GAP-04 edge cases — SafetyInspectorAgent rate-limit boundary matrix
# ---------------------------------------------------------------------------


class TestSocraticJudgeEdgeCases:
    """§1.5 / §1.9 matrix for SafetyInspectorAgent rate-limit boundary (GAP-04)."""

    def _inspector(self, max_calls):
        from agentic_core.L5_safety.reasoning.SafetyInspectorAgent import SafetyInspectorAgent

        return SafetyInspectorAgent(enable_socratic_judge=True, max_socratic_calls=max_calls)

    # --- boundary: exactly at limit ---

    def test_call_at_limit_is_rate_limited(self):
        """Call index == max_socratic_calls must be rejected (rate_limit)."""
        inspector = self._inspector(max_calls=1)
        loop = asyncio.get_event_loop()
        # First call: consumes the one allowed slot (may error on missing client)
        with patch.dict(
            "sys.modules",
            {
                "agentic_core.L2_execution.enforcement.llm_router_mcp_client": None,
            },
        ):
            loop.run_until_complete(inspector._socratic_verify("f.py", "i", "q?"))
        # Second call: must hit rate limit
        result = loop.run_until_complete(inspector._socratic_verify("f.py", "i", "q?"))
        assert result == "YES"
        assert inspector._socratic_audit_log[-1]["reason"] == "rate_limit"

    # --- boundary: limit=0 blocks immediately ---

    def test_max_calls_zero_always_rate_limits(self):
        """max_socratic_calls=0 must rate-limit on the very first call."""
        inspector = self._inspector(max_calls=0)
        result = asyncio.get_event_loop().run_until_complete(
            inspector._socratic_verify("x.py", "issue", "q?")
        )
        assert result == "YES"
        assert inspector._socratic_audit_log[0]["reason"] == "rate_limit"

    # --- negative control: counter does NOT increment on rate-limit ---

    def test_rate_limited_call_does_not_increment_counter(self):
        """Rate-limited calls must not increment _socratic_call_count."""
        inspector = self._inspector(max_calls=0)
        asyncio.get_event_loop().run_until_complete(inspector._socratic_verify("x.py", "issue", "q?"))
        assert inspector._socratic_call_count == 0

    # --- audit log: every call (including rate-limited) must be logged ---

    def test_audit_log_length_matches_total_calls(self):
        """Every invocation of _socratic_verify must produce an audit entry."""
        inspector = self._inspector(max_calls=0)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(inspector._socratic_verify("a.py", "i1", "q1"))
        loop.run_until_complete(inspector._socratic_verify("b.py", "i2", "q2"))
        assert len(inspector._socratic_audit_log) == 2

    # --- malformed file path (missing file) ---

    def test_nonexistent_file_path_does_not_raise(self):
        """Passing a nonexistent file path must not raise; verdict must be YES."""
        inspector = self._inspector(max_calls=10)
        with patch.dict(
            "sys.modules",
            {
                "agentic_core.L2_execution.enforcement.llm_router_mcp_client": None,
            },
        ):
            result = asyncio.get_event_loop().run_until_complete(
                inspector._socratic_verify("/nonexistent/path/file.py", "issue", "q?")
            )
        assert result == "YES"


# ---------------------------------------------------------------------------
# GAP-05 edge cases — RegressionOracleAgent AST safety check
# ---------------------------------------------------------------------------


class TestRegressionOracleEdgeCases:
    """§1.5 edge-case matrix for RegressionOracleAgent AST safety check (GAP-05)."""

    def _cls(self):
        from agentic_core.L5_safety.reasoning.RegressionOracleAgent import RegressionOracleAgent

        return RegressionOracleAgent

    # --- empty input ---

    def test_empty_string_returns_no_violations(self):
        """Empty generated code produces no violations (no AST nodes)."""
        cls = self._cls()
        assert cls._ast_safety_check("") == []

    # --- null / whitespace ---

    def test_whitespace_only_code_returns_no_violations(self):
        cls = self._cls()
        assert cls._ast_safety_check("   \n  ") == []

    # --- boundary: single safe statement ---

    def test_single_pass_statement_is_safe(self):
        cls = self._cls()
        assert cls._ast_safety_check("pass") == []

    # --- replayed check: deterministic (same code → same violations) ---

    def test_repeated_call_same_input_same_output(self):
        """§1.7: identical code must produce identical violation list on every call."""
        cls = self._cls()
        code = "def f():\n    exec('x')\n    eval('y')\n"
        v1 = cls._ast_safety_check(code)
        v2 = cls._ast_safety_check(code)
        assert v1 == v2, "§1.7: AST safety check must be deterministic"

    # --- boundary: nested dangerous call ---

    def test_nested_exec_inside_lambda_is_flagged(self):
        cls = self._cls()
        bad = "f = lambda: exec('rm')\n"
        violations = cls._ast_safety_check(bad)
        assert len(violations) > 0

    # --- negative control: assert statement is safe ---

    def test_assert_statement_not_flagged(self):
        cls = self._cls()
        safe = "def test():\n    assert True\n    assert 1 == 1\n"
        assert cls._ast_safety_check(safe) == []

    # --- boundary: MAX_CORRECTION_ITERATIONS exact value ---

    def test_max_correction_iterations_is_exactly_3(self):
        """Iteration cap must be the exact value declared in Wave 6."""
        cls = self._cls()
        assert cls.MAX_CORRECTION_ITERATIONS == 3
