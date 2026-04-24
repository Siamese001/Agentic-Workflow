"""Unit tests for the pure-utility modules in ``agentic_core.L5_safety.eval_spine``.

Covers:
- tool_call_canonicalizer
- trajectory_metrics
- budget_envelope (check_fit pure path; policy-loading path via a tmp file)
- claim_extractor
- output_contract_validator
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from agentic_core.L5_safety.eval_spine import (
    budget_envelope,
    claim_extractor,
    output_contract_validator,
    tool_call_canonicalizer,
    trajectory_metrics,
)


# ---------- tool_call_canonicalizer ----------


class TestToolCallCanonicalizer:
    def test_args_hash_stable_across_key_order(self):
        h1 = tool_call_canonicalizer.args_hash({"b": 2, "a": 1})
        h2 = tool_call_canonicalizer.args_hash({"a": 1, "b": 2})
        assert h1 == h2

    def test_volatile_fields_stripped(self):
        h_with = tool_call_canonicalizer.args_hash(
            {"query": "x", "timestamp": "2026-04-23T00:00:00Z", "request_id": "r-1"}
        )
        h_without = tool_call_canonicalizer.args_hash({"query": "x"})
        assert h_with == h_without

    def test_canonicalize_tool_call_rejects_empty_tool(self):
        with pytest.raises(TypeError):
            tool_call_canonicalizer.canonicalize_tool_call("", {})

    def test_canonicalize_tool_call_shape(self):
        rec = tool_call_canonicalizer.canonicalize_tool_call("search", {"q": "x"})
        assert rec["tool"] == "search"
        assert len(rec["args_hash"]) == 64

    def test_nan_raises(self):
        with pytest.raises(ValueError):
            tool_call_canonicalizer.canonicalize_tool_call("x", {"v": float("nan")})


# ---------- trajectory_metrics ----------


class TestTrajectoryMetrics:
    @pytest.fixture
    def seq(self):
        return [
            {"tool": "a", "args_hash": "h1"},
            {"tool": "b", "args_hash": "h2"},
            {"tool": "c", "args_hash": "h3"},
        ]

    def test_exact_match(self, seq):
        assert trajectory_metrics.trajectory_exact_match(seq, seq) == 1
        assert trajectory_metrics.trajectory_exact_match(seq, list(reversed(seq))) == 0

    def test_in_order_match_allows_extras(self, seq):
        predicted = [
            {"tool": "a", "args_hash": "h1"},
            {"tool": "x", "args_hash": "hx"},
            {"tool": "b", "args_hash": "h2"},
            {"tool": "c", "args_hash": "h3"},
        ]
        assert trajectory_metrics.trajectory_in_order_match(predicted, seq) == 1

    def test_in_order_match_order_broken(self, seq):
        predicted = [seq[1], seq[0], seq[2]]
        assert trajectory_metrics.trajectory_in_order_match(predicted, seq) == 0

    def test_any_order_match(self, seq):
        predicted = list(reversed(seq))
        assert trajectory_metrics.trajectory_any_order_match(predicted, seq) == 1

    def test_precision_recall(self, seq):
        predicted = [seq[0], seq[1], {"tool": "x", "args_hash": "hx"}]
        assert trajectory_metrics.trajectory_precision(predicted, seq) == pytest.approx(
            2 / 3
        )
        assert trajectory_metrics.trajectory_recall(predicted, seq) == pytest.approx(
            2 / 3
        )

    def test_recall_empty_reference(self, seq):
        assert trajectory_metrics.trajectory_recall(seq, []) == 1.0

    def test_precision_empty_predicted(self, seq):
        assert trajectory_metrics.trajectory_precision([], seq) == 0.0

    def test_single_tool_use(self, seq):
        result = trajectory_metrics.single_tool_use(seq, "b")
        assert result == {"tool_name": "b", "present": True}
        assert trajectory_metrics.single_tool_use(seq, "z")["present"] is False

    def test_compute_all_without_reference(self, seq):
        out = trajectory_metrics.compute_all(seq, None)
        assert out["tool_call_count"] == 3
        assert out["exact_match"] is None
        assert out["precision"] is None

    def test_compute_all_with_reference_and_single(self, seq):
        out = trajectory_metrics.compute_all(
            seq, seq, single_tool_names=("a", "z")
        )
        assert out["exact_match"] == 1
        assert out["single_tool_use"]["a"]["present"] is True
        assert out["single_tool_use"]["z"]["present"] is False

    def test_invalid_record_shape(self):
        with pytest.raises(trajectory_metrics.TrajectoryRecordError):
            trajectory_metrics.trajectory_exact_match([{"tool": "x"}], [])


# ---------- budget_envelope ----------


class TestBudgetEnvelopeCheckFit:
    def test_all_within_envelope(self):
        env = budget_envelope.BudgetEnvelope(
            tokens_max=1000, latency_ms_max=10000, tool_calls_max=10, cost_usd_max=1.0
        )
        consumed = budget_envelope.BudgetConsumed(
            tokens=500, latency_ms=5000, tool_calls=2, cost_usd=0.25
        )
        fit = budget_envelope.check_fit(consumed, env)
        assert fit.budget_fit is True
        assert fit.severity_band == "info"

    def test_token_overrun(self):
        env = budget_envelope.BudgetEnvelope(tokens_max=100)
        consumed = budget_envelope.BudgetConsumed(tokens=250)
        fit = budget_envelope.check_fit(consumed, env)
        assert fit.budget_fit is False
        assert fit.per_axis["tokens"] is False
        assert fit.severity_band in {"high", "critical"}

    def test_unbounded_axis(self):
        env = budget_envelope.BudgetEnvelope(tokens_max=None)
        consumed = budget_envelope.BudgetConsumed(tokens=10_000)
        fit = budget_envelope.check_fit(consumed, env)
        assert fit.budget_fit is True

    def test_hard_cap_severity(self):
        env = budget_envelope.BudgetEnvelope(tokens_max=100)
        consumed = budget_envelope.BudgetConsumed(tokens=200)
        fit = budget_envelope.check_fit(consumed, env)
        assert fit.severity_band == "critical"


class TestBudgetEnvelopeResolve:
    @pytest.fixture
    def tmp_policy(self, tmp_path: Path) -> Path:
        policy = {
            "version": 1,
            "global_fallback": {
                "tokens_max": 100,
                "latency_ms_max": 1000,
                "tool_calls_max": 2,
                "cost_usd_max": 0.1,
            },
            "route_class_defaults": {
                "R2": {
                    "tokens_max": 4000,
                    "latency_ms_max": 10000,
                    "tool_calls_max": 8,
                    "cost_usd_max": 0.5,
                }
            },
            "tenants": {
                "acme": {
                    "defaults": {
                        "tokens_max": 2000,
                        "latency_ms_max": 5000,
                        "tool_calls_max": 4,
                        "cost_usd_max": 0.2,
                    },
                    "ceiling": {
                        "tokens_max": 10_000,
                        "latency_ms_max": 60_000,
                        "tool_calls_max": 64,
                        "cost_usd_max": 5.0,
                    },
                },
                "_default": {
                    "defaults": {
                        "tokens_max": 500,
                        "latency_ms_max": 2000,
                        "tool_calls_max": 2,
                        "cost_usd_max": 0.1,
                    },
                    "ceiling": {
                        "tokens_max": 10_000,
                        "latency_ms_max": 60_000,
                        "tool_calls_max": 64,
                        "cost_usd_max": 5.0,
                    },
                },
            },
        }
        import yaml  # type: ignore[import-untyped]

        path = tmp_path / "policy.yaml"
        path.write_text(yaml.safe_dump(policy), encoding="utf-8")
        return path

    def test_tenant_default(self, tmp_policy):
        env = budget_envelope.resolve_envelope(tenant="acme", policy_path=tmp_policy)
        assert env.tokens_max == 2000
        assert env.origin.startswith("tenant:")

    def test_route_fallback(self, tmp_policy):
        env = budget_envelope.resolve_envelope(
            tenant=None, route_class="R2", policy_path=tmp_policy
        )
        # "_default" tenant default applies before route fallback.
        assert env.tokens_max == 500

    def test_caller_clamped_by_ceiling(self, tmp_policy):
        caller = budget_envelope.BudgetEnvelope(tokens_max=999_999)
        env = budget_envelope.resolve_envelope(
            caller_envelope=caller, tenant="acme", policy_path=tmp_policy
        )
        assert env.tokens_max == 10_000  # clamped by acme ceiling

    def test_missing_policy(self, tmp_path: Path):
        with pytest.raises(budget_envelope.BudgetPolicyError):
            budget_envelope.resolve_envelope(policy_path=tmp_path / "nope.yaml")


# ---------- claim_extractor ----------


class TestClaimExtractor:
    def test_fully_supported_answer(self):
        report = claim_extractor.analyze(
            "The capital of France is Paris. Paris has the Eiffel Tower.",
            context_text="Paris is the capital of France. The Eiffel Tower stands in Paris.",
        )
        assert report.unsupported_claim_count == 0
        assert report.score_0_1 == pytest.approx(1.0)
        assert report.tool_grounded is True

    def test_tool_claim_without_ledger_is_unsupported(self):
        report = claim_extractor.analyze("I called the search tool and got 5 hits.")
        assert report.tool_grounded is False
        assert report.unsupported_claim_count >= 1

    def test_tool_claim_with_matching_ledger_is_supported(self):
        report = claim_extractor.analyze(
            "The search tool returned relevant results.",
            tool_calls=[{"tool": "search", "args_hash": "h"}],
        )
        assert report.tool_grounded is True

    def test_no_claims_scores_one(self):
        report = claim_extractor.analyze("")
        assert report.total_claim_count == 0
        assert report.score_0_1 == 1.0

    def test_questions_are_not_claims(self):
        report = claim_extractor.analyze("Who wrote this? Something.")
        assert report.total_claim_count == 1


# ---------- output_contract_validator ----------


class TestOutputContractValidator:
    def test_none_contract_passes(self):
        result = output_contract_validator.validate("anything", None)
        assert result.required_form_satisfied is True

    def test_unresolved_contract(self, tmp_path: Path):
        (tmp_path / "nothing").mkdir()
        result = output_contract_validator.validate(
            "x", "does_not_exist", contract_root=tmp_path
        )
        assert result.required_form_satisfied is False
        assert any("unresolved" in v for v in result.violations)

    def test_tool_result_envelope(self, tmp_path: Path):
        contract = {"kind": "tool_result_envelope", "envelope_version": 1}
        path = tmp_path / "env.json"
        path.write_text(json.dumps(contract), encoding="utf-8")

        good = {
            "success": True,
            "payload": {"x": 1},
            "reason": "ok",
            "schema_version": 1,
        }
        r_good = output_contract_validator.validate(
            good, "env", contract_root=tmp_path
        )
        assert r_good.required_form_satisfied is True

        bad = {"success": True, "payload": {}}
        r_bad = output_contract_validator.validate(bad, "env", contract_root=tmp_path)
        assert r_bad.required_form_satisfied is False
        assert any("missing_field" in v for v in r_bad.violations)

    def test_markdown_sections_ordered(self, tmp_path: Path):
        contract = {
            "kind": "markdown_sections",
            "required_sections": ["Intro", "Details", "Conclusion"],
        }
        path = tmp_path / "md.json"
        path.write_text(json.dumps(contract), encoding="utf-8")
        text_ok = "# Intro\n## Details\n## Conclusion\n"
        text_bad = "# Conclusion\n# Intro\n"
        good = output_contract_validator.validate(text_ok, "md", contract_root=tmp_path)
        bad = output_contract_validator.validate(text_bad, "md", contract_root=tmp_path)
        assert good.required_form_satisfied is True
        assert bad.required_form_satisfied is False

    def test_text_constraints(self, tmp_path: Path):
        contract = {
            "kind": "text_constraints",
            "max_chars": 10,
            "regex_denylist": [r"secret"],
        }
        (tmp_path / "tc.json").write_text(json.dumps(contract), encoding="utf-8")
        long_text = "a" * 20
        secret_text = "topsecret"
        r_long = output_contract_validator.validate(
            long_text, "tc", contract_root=tmp_path
        )
        r_secret = output_contract_validator.validate(
            secret_text, "tc", contract_root=tmp_path
        )
        assert r_long.required_form_satisfied is False
        assert r_secret.required_form_satisfied is False
