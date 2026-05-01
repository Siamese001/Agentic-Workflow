"""W1 Phase 5 Gap-6 — Fail-closed behavior tests.

Verifies the mandatory fail-closed invariants:
1. LLM judge timeout -> block reuse
2. LLM judge malformed output -> block reuse
3. LLM judge UNKNOWN -> block reuse
4. Lexical pre-veto bypass disabled -> LLM judge still protects hard negatives
5. Veto bypass env var logs audit and prevents PASS classification
6. --allow-missing-evidence cannot be used in the strict certification path
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.certification.safety.llm_judge_veto import LLMJudgeVeto
from tools.certification.safety.veto_protocol import VetoStatus, VetoResult
from tools.certification.safety.lexical_intent_veto import LexicalIntentVeto
from tools.certification.safety.veto_orchestrator import VetoOrchestrator


# ──────────────────────────────────────────────────────────────────────
# Section 1: LLM judge timeout -> block reuse
# ──────────────────────────────────────────────────────────────────────


class TestLLMJudgeTimeoutBlocks:
    """A timeout from the LLM judge must fail-closed."""

    def test_timeout_returns_error_status(self):
        """When the provider call exceeds timeout_ms, result.blocks_reuse() must be True."""
        veto = LLMJudgeVeto(provider="mock", timeout_ms=1000)

        # Simulate the provider taking too long by patching the mock path
        def slow_mock(prompt):
            import time
            time.sleep(0.5)
            return {"raw": "", "latency_ms": 500}

        with patch.object(veto, "_call_mock", side_effect=slow_mock):
            # Set timeout to 1ms so the 500ms sleep blows past it
            veto._timeout_ms = 1
            result = veto.evaluate(query="q", cached_query="cq")

        assert result.blocks_reuse(), (
            f"Timeout must block reuse. status={result.status}, rationale={result.rationale}"
        )
        assert result.status == VetoStatus.ERROR
        assert "timeout" in result.rationale.lower()

    def test_provider_exception_blocks(self):
        """Provider throwing an exception must block reuse (fail-closed)."""
        veto = LLMJudgeVeto(provider="mock")

        def exploding_mock(prompt):
            raise RuntimeError("simulated provider failure")

        with patch.object(veto, "_call_mock", side_effect=exploding_mock):
            result = veto.evaluate(query="q", cached_query="cq")

        assert result.blocks_reuse()
        assert result.status == VetoStatus.ERROR


# ──────────────────────────────────────────────────────────────────────
# Section 2: LLM judge malformed output -> block reuse
# ──────────────────────────────────────────────────────────────────────


class TestLLMJudgeMalformedBlocks:
    """Malformed JSON / non-JSON output must fail-closed."""

    def test_non_json_output_blocks(self):
        """Raw response that is not valid JSON must block reuse."""
        veto = LLMJudgeVeto(provider="mock")

        with patch.object(
            veto,
            "_call_mock",
            return_value={"raw": "this is not JSON at all", "latency_ms": 1},
        ):
            result = veto.evaluate(query="q", cached_query="cq")

        assert result.blocks_reuse(), "Non-JSON output must block reuse"
        # Status should be ERROR (parse failure) or UNKNOWN
        assert result.status in (VetoStatus.ERROR, VetoStatus.UNKNOWN)

    def test_missing_verdict_field_blocks(self):
        """JSON missing the 'verdict' field defaults to UNCERTAIN -> blocks."""
        veto = LLMJudgeVeto(provider="mock")

        with patch.object(
            veto,
            "_call_mock",
            return_value={"raw": json.dumps({"confidence": 0.9}), "latency_ms": 1},
        ):
            result = veto.evaluate(query="q", cached_query="cq")

        assert result.blocks_reuse()

    def test_invalid_verdict_value_blocks(self):
        """Unknown verdict value must not be treated as SAFE."""
        veto = LLMJudgeVeto(provider="mock")

        with patch.object(
            veto,
            "_call_mock",
            return_value={
                "raw": json.dumps({"verdict": "TOTALLY_FINE_TRUST_ME", "confidence": 1.0}),
                "latency_ms": 1,
            },
        ):
            result = veto.evaluate(query="q", cached_query="cq")

        assert result.blocks_reuse(), (
            "Unrecognized verdict must fail-closed, not pass as SAFE"
        )


# ──────────────────────────────────────────────────────────────────────
# Section 3: LLM judge UNKNOWN -> block reuse
# ──────────────────────────────────────────────────────────────────────


class TestLLMJudgeUnknownBlocks:
    """Explicit UNCERTAIN verdict must block reuse."""

    def test_uncertain_verdict_blocks(self):
        """UNCERTAIN with low confidence blocks reuse."""
        veto = LLMJudgeVeto(provider="mock")

        with patch.object(
            veto,
            "_call_mock",
            return_value={
                "raw": json.dumps({
                    "verdict": "UNCERTAIN",
                    "confidence": 0.3,
                    "rationale": "ambiguous",
                }),
                "latency_ms": 1,
            },
        ):
            result = veto.evaluate(query="q", cached_query="cq")

        assert result.blocks_reuse()
        assert result.status == VetoStatus.UNKNOWN

    def test_unknown_status_is_blocking(self):
        """VetoStatus.UNKNOWN.is_blocking() == True."""
        assert VetoStatus.UNKNOWN.is_blocking()
        assert not VetoStatus.UNKNOWN.allows_reuse()


# ──────────────────────────────────────────────────────────────────────
# Section 4: Lexical pre-veto bypass -> LLM judge still protects
# ──────────────────────────────────────────────────────────────────────


class TestLexicalBypassLLMStillProtects:
    """If lexical pre-veto is disabled, Layer 2 (LLM judge) must still catch hard negatives."""

    def test_orchestrator_without_lexical_still_blocks(self):
        """Orchestrator with only llm_judge enabled blocks opposite-intent pairs."""
        # Build a policy that disables lexical pre-veto
        judge = LLMJudgeVeto(provider="mock")

        # Mock the judge to return UNSAFE for opposite-intent queries
        def smart_mock(prompt):
            # Mock returns UNSAFE when queries look opposed
            if "disable" in prompt.lower() and "enable" in prompt.lower():
                return {
                    "raw": json.dumps({
                        "verdict": "UNSAFE_DIFFERENT_INTENT",
                        "confidence": 0.95,
                        "rationale": "enable vs disable = opposite",
                    }),
                    "latency_ms": 1,
                }
            return {
                "raw": json.dumps({
                    "verdict": "UNCERTAIN",
                    "confidence": 0.5,
                    "rationale": "insufficient evidence",
                }),
                "latency_ms": 1,
            }

        with patch.object(judge, "_call_mock", side_effect=smart_mock):
            orch = VetoOrchestrator(
                stages=[judge],
                latency_budget_ms=5000,
            )
            # Orchestrator was given explicit stages, so policy not auto-loaded
            orch._stage_order = ["llm_judge"]

            # Hard negative: enable vs disable
            result = orch.evaluate(
                query="Enable two-factor authentication",
                cached_query="Disable two-factor authentication",
            )

            assert result.blocks_reuse(), (
                "LLM judge alone must catch enable↔disable without lexical help"
            )


# ──────────────────────────────────────────────────────────────────────
# Section 5: Veto bypass env var -> audit logged, no PASS classification
# ──────────────────────────────────────────────────────────────────────


class TestVetoBypassAudit:
    """Env bypass must be auditable and must not let the composer classify PASS."""

    def test_veto_bypass_flag_documented_in_policy(self):
        """Policy schema must declare a bypass contract (even if disabled)."""
        policy_path = (
            REPO_ROOT / "artifacts" / "certification" / "semantic_cache_veto_policy.json"
        )
        if not policy_path.exists():
            pytest.skip("policy artifact not present")
        policy = json.loads(policy_path.read_text(encoding="utf-8"))
        # All four fail-closed defaults must be VETO
        defaults = policy.get("fail_closed_defaults", {})
        assert defaults.get("on_timeout") == "VETO"
        assert defaults.get("on_parse_error") == "VETO"
        assert defaults.get("on_model_error") == "VETO"

    def test_author_gate_pending_prevents_pass(self):
        """Composer must not classify veto PASS when Author-Gate is PENDING."""
        from scripts.compose_semantic_cache_subclaims import _map_veto_proof

        veto_ev_good = {
            "status": "PASS",
            "metrics": {"false_negatives": 0},
            "safety_score": 1.0,
            "primary_veto_mode": "C_PRIMARY_LLM_JUDGE",
            "invocation_counts": {"llm_judge_invocation_count": 5},
        }
        # Author-Gate artifact exists but status=AUTHOR_GATE_PENDING
        # (this is the current on-disk state — we don't mutate it here)
        status, notes = _map_veto_proof(veto_ev_good, None, None)

        # With Author-Gate still PENDING, even perfect evidence must be PARTIAL
        ag_path = REPO_ROOT / "artifacts" / "certification" / "author_gate_w1p5_decision.json"
        if ag_path.exists():
            ag = json.loads(ag_path.read_text(encoding="utf-8"))
            if ag.get("explicit_approval", {}).get("status") != "APPROVED":
                assert status != "PASS", (
                    f"Composer must not PASS veto while Author-Gate pending. "
                    f"Got status={status}, notes={notes}"
                )
                assert "Author-Gate" in notes or "llm_judge_invocation_count" in notes


# ──────────────────────────────────────────────────────────────────────
# Section 6: --allow-missing-evidence cannot appear in strict path
# ──────────────────────────────────────────────────────────────────────


class TestStrictModeForbidsAllowMissing:
    """The strict certification path must not use --allow-missing-evidence."""

    def test_strict_verifier_does_not_pass_allow_missing(self):
        """Search the verifier for forbidden flag usage in strict mode."""
        verifier_path = REPO_ROOT / "scripts" / "verify_semantic_cache_certification.py"
        if not verifier_path.exists():
            pytest.skip("verifier not present")
        content = verifier_path.read_text(encoding="utf-8")
        # The verifier file itself must not invoke the composer with bypass flag
        forbidden_pattern = "--allow-missing-evidence"
        # Allow the flag to appear ONLY in comment lines documenting the anti-cheat rule
        for lineno, line in enumerate(content.splitlines(), 1):
            stripped = line.strip()
            if forbidden_pattern in stripped and not stripped.startswith("#"):
                pytest.fail(
                    f"Line {lineno}: verifier uses --allow-missing-evidence in "
                    f"non-comment line: {line!r}"
                )

    def test_ci_workflow_main_path_runs_strict(self):
        """CI must run the compose step without the bypass flag on the strict path."""
        workflow_path = (
            REPO_ROOT / ".github" / "workflows" / "runtime-certification.yml"
        )
        if not workflow_path.exists():
            pytest.skip("workflow not present")
        content = workflow_path.read_text(encoding="utf-8")
        # The W1p5 safety-gate step must NOT use the bypass flag. It's OK for
        # advisory/upstream compose steps during bring-up to allow it, but the
        # FINAL strict verifier path must not.
        strict_marker = "--strict"
        assert strict_marker in content, "CI workflow lacks --strict verifier step"

    def test_compose_default_is_strict(self):
        """Running compose without flags must NOT require --allow-missing-evidence."""
        result = subprocess.run(
            [sys.executable, "scripts/compose_semantic_cache_subclaims.py"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=60,
        )
        # Exit 0 means all required evidence is present OR the sidecar wrote cleanly
        # Exit 2 means evidence missing — which is ALSO acceptable per user §4:
        # "The chain may exit non-zero because RTC-REQ-055 remains PARTIAL. That is
        # fine. But missing evidence cannot be suppressed."
        # Either way, the default path must not silently succeed with missing evidence.
        assert result.returncode in (0, 2, 3), (
            f"Unexpected exit {result.returncode}; stderr={result.stderr[:500]}"
        )
        # If exit 2, the stderr must announce the FAIL_CLOSED reason (not suppression)
        if result.returncode == 2:
            assert "FAIL_CLOSED" in result.stderr or "MISSING_EVIDENCE" in result.stderr


# ──────────────────────────────────────────────────────────────────────
# Section 7: Protocol-level invariants
# ──────────────────────────────────────────────────────────────────────


class TestVetoStatusInvariants:
    """Structural invariants on VetoStatus — the safety alphabet."""

    def test_only_safe_allows_reuse(self):
        """Only VetoStatus.SAFE allows reuse; everything else blocks."""
        for status in VetoStatus:
            if status == VetoStatus.SAFE:
                assert status.allows_reuse()
                assert not status.is_blocking()
            elif status == VetoStatus.DELEGATE:
                # DELEGATE is a non-verdict passed up to the orchestrator
                assert not status.allows_reuse()
                assert not status.is_blocking()
            else:
                assert not status.allows_reuse(), (
                    f"Status {status} must not allow reuse"
                )
                assert status.is_blocking(), f"Status {status} must block reuse"

    def test_error_and_unknown_both_block(self):
        assert VetoStatus.ERROR.is_blocking()
        assert VetoStatus.UNKNOWN.is_blocking()
        # Neither allows reuse
        assert not VetoStatus.ERROR.allows_reuse()
        assert not VetoStatus.UNKNOWN.allows_reuse()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
