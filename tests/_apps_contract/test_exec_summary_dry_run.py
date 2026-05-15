"""
Tests for executive summary dry-run harness — THREE-PROVIDER LLM JUDGE EDITION.

Validates:
1. All three judge rows exist (Gemini Pro, OpenAI ChatGPT, Anthropic Claude)
2. Console output shows all three providers
3. Missing provider config produces BLOCKED_PROVIDER_UNAVAILABLE with exact error
4. Mocked judge cannot produce X3_ALLOW
5. Blocked judge cannot produce X3_ALLOW
6. X3_ALLOW requires all three judges MODEL_BACKED
7. X3_BLOCK if any X2 gate fails
8. X3_BLOCK if any judge has decisive_failure=true
9. X3_REVIEW_JUDGE_PROVIDER_BLOCKED if X2 passes but one or more judges are blocked
10. L6 package records all three judge refs and remains offline_only=true, promotion_allowed=false
11. No registry/v1/core changes
12. Qwen temperature in valid range 0.35-0.55, default 0.45
13. Qwen provider_request.json artifact exists
14. New X2 gates: temperature_in_profile, first_person_zero, target_company_as_experience_zero
15. Product quality depends on X2 gates
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
ARTIFACTS_DIR = REPO_ROOT / "artifacts" / "apps_rg" / "runtime_proofs" / "executive_summary"
HARNESS_MODULE = "apps_rg.runtime.dry_run.executive_summary_demo"


class TestThreeProviderLLMJudges:
    """Test 1-3: Three-provider LLM judges with BLOCKED/MOCKED states."""
    
    @pytest.fixture(autouse=True)
    def run_harness_with_judges(self):
        """Run harness with --x1d-judges flag to enable LLM judges."""
        subprocess.run(
            [sys.executable, "-m", HARNESS_MODULE, "--provider", "qwen_vllm", 
             "--x1d-judges", "gemini_pro,openai_chatgpt,anthropic_claude"],
            capture_output=True,
            cwd=REPO_ROOT,
        )
    
    def test_all_three_judge_rows_exist(self):
        """Test 1: x1d_llm_judge_outputs.json contains all three providers."""
        path = ARTIFACTS_DIR / "x1d_llm_judge_outputs.json"
        assert path.exists(), "x1d_llm_judge_outputs.json should exist"
        
        data = json.loads(path.read_text())
        assert len(data) == 3, f"Expected 3 judges, got {len(data)}"
        
        provider_keys = {j["provider_key"] for j in data}
        expected = {"gemini_pro", "openai_chatgpt", "anthropic_claude"}
        assert provider_keys == expected, f"Missing providers: {expected - provider_keys}"
    
    def test_console_shows_three_providers(self):
        """Test 2: Console output shows Gemini Pro, OpenAI ChatGPT, Anthropic Claude."""
        result = subprocess.run(
            [sys.executable, "-m", HARNESS_MODULE, "--provider", "qwen_vllm",
             "--x1d-judges", "gemini_pro,openai_chatgpt,anthropic_claude"],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        stdout = result.stdout
        
        # Check for three-provider evaluation header
        assert "X1D_LLM_JUDGE_OUTPUTS" in stdout
        assert "THREE-PROVIDER EVALUATION" in stdout
        
        # Check for all three provider names
        assert "Gemini Pro" in stdout
        assert "OpenAI ChatGPT" in stdout or "OpenAI" in stdout
        assert "Anthropic Claude" in stdout or "Anthropic" in stdout
    
    def test_missing_gemini_config_blocked(self):
        """Test 3a: Missing Gemini config produces BLOCKED_PROVIDER_UNAVAILABLE."""
        path = ARTIFACTS_DIR / "x1d_llm_judge_outputs.json"
        data = json.loads(path.read_text())
        
        gemini_judge = next((j for j in data if j["provider_key"] == "gemini_pro"), None)
        assert gemini_judge is not None
        
        if not gemini_judge["provider_available"]:
            assert gemini_judge["evaluator_mode"] == "BLOCKED_PROVIDER_UNAVAILABLE"
            assert gemini_judge["exact_provider_error"] is not None
            assert "GEMINI_API_KEY" in gemini_judge["exact_provider_error"] or "not set" in gemini_judge["exact_provider_error"]
    
    def test_missing_openai_config_blocked(self):
        """Test 3b: Missing OpenAI config produces BLOCKED_PROVIDER_UNAVAILABLE."""
        path = ARTIFACTS_DIR / "x1d_llm_judge_outputs.json"
        data = json.loads(path.read_text())
        
        openai_judge = next((j for j in data if j["provider_key"] == "openai_chatgpt"), None)
        assert openai_judge is not None
        
        if not openai_judge["provider_available"]:
            assert openai_judge["evaluator_mode"] == "BLOCKED_PROVIDER_UNAVAILABLE"
            assert openai_judge["exact_provider_error"] is not None
            assert "OPENAI_API_KEY" in openai_judge["exact_provider_error"] or "not set" in openai_judge["exact_provider_error"]
    
    def test_missing_anthropic_config_blocked(self):
        """Test 3c: Missing Anthropic config produces BLOCKED_PROVIDER_UNAVAILABLE."""
        path = ARTIFACTS_DIR / "x1d_llm_judge_outputs.json"
        data = json.loads(path.read_text())
        
        anthropic_judge = next((j for j in data if j["provider_key"] == "anthropic_claude"), None)
        assert anthropic_judge is not None
        
        if not anthropic_judge["provider_available"]:
            assert anthropic_judge["evaluator_mode"] == "BLOCKED_PROVIDER_UNAVAILABLE"
            assert anthropic_judge["exact_provider_error"] is not None
            assert "ANTHROPIC_API_KEY" in anthropic_judge["exact_provider_error"] or "not set" in anthropic_judge["exact_provider_error"]


class TestQwenTemperature:
    """Test 12-13: Qwen temperature validation and artifact."""
    
    @pytest.fixture(autouse=True)
    def run_harness_with_judges(self):
        """Run harness with --x1d-judges flag."""
        subprocess.run(
            [sys.executable, "-m", HARNESS_MODULE, "--provider", "qwen_vllm",
             "--x1d-judges", "gemini_pro,openai_chatgpt,anthropic_claude"],
            capture_output=True,
            cwd=REPO_ROOT,
        )
    
    def test_qwen_temperature_in_valid_range(self):
        """Test 12a: Qwen temperature is within 0.35-0.55 range."""
        path = ARTIFACTS_DIR / "real_l2_generation_result.json"
        assert path.exists(), "real_l2_generation_result.json should exist"
        
        data = json.loads(path.read_text())
        temp = data.get("temperature", 0.7)
        
        assert 0.35 <= temp <= 0.55, f"Temperature {temp} outside valid range 0.35-0.55"
    
    def test_qwen_temperature_is_0_45(self):
        """Test 12b: Qwen temperature is exactly 0.45 (default)."""
        path = ARTIFACTS_DIR / "real_l2_generation_result.json"
        data = json.loads(path.read_text())
        temp = data.get("temperature", 0.7)
        
        assert temp == 0.45, f"Expected temperature 0.45, got {temp}"
    
    def test_qwen_provider_request_artifact_exists(self):
        """Test 13: x1d_provider_request_qwen_vllm.json exists with correct data."""
        path = ARTIFACTS_DIR / "x1d_provider_request_qwen_vllm.json"
        assert path.exists(), "x1d_provider_request_qwen_vllm.json should exist"
        
        data = json.loads(path.read_text())
        assert data["provider_key"] == "qwen_vllm"
        assert data["model_name"] == "Qwen/Qwen2.5-32B-Instruct-AWQ"
        assert 0.35 <= data["temperature"] <= 0.55
        assert "request_payload" in data


class TestNewX2Gates:
    """Test 14: New X2 gates for temperature, first-person, and target company."""
    
    @pytest.fixture(autouse=True)
    def run_harness_with_judges(self):
        """Run harness with --x1d-judges flag."""
        subprocess.run(
            [sys.executable, "-m", HARNESS_MODULE, "--provider", "qwen_vllm",
             "--x1d-judges", "gemini_pro,openai_chatgpt,anthropic_claude"],
            capture_output=True,
            cwd=REPO_ROOT,
        )
    
    def test_x2_temperature_in_profile_gate_exists(self):
        """Test 14a: x2_temperature_in_profile gate exists."""
        path = ARTIFACTS_DIR / "x2_gate_outputs.json"
        assert path.exists()
        
        data = json.loads(path.read_text())
        gate_ids = {g["gate_id"] for g in data}
        
        assert "x2_temperature_in_profile" in gate_ids
        
        # Find the gate and check it passes with temp 0.45
        temp_gate = next((g for g in data if g["gate_id"] == "x2_temperature_in_profile"), None)
        assert temp_gate is not None
        assert temp_gate["pass"] is True
    
    def test_x2_first_person_zero_gate_exists(self):
        """Test 14b: x2_first_person_zero gate exists."""
        path = ARTIFACTS_DIR / "x2_gate_outputs.json"
        data = json.loads(path.read_text())
        gate_ids = {g["gate_id"] for g in data}
        
        assert "x2_first_person_zero" in gate_ids
    
    def test_x2_target_company_zero_gate_exists(self):
        """Test 14c: x2_target_company_as_experience_zero gate exists."""
        path = ARTIFACTS_DIR / "x2_gate_outputs.json"
        data = json.loads(path.read_text())
        gate_ids = {g["gate_id"] for g in data}
        
        assert "x2_target_company_as_experience_zero" in gate_ids


class TestProductQualityDependsOnX2:
    """Test 15: Product quality status depends on X2 gates."""
    
    @pytest.fixture(autouse=True)
    def run_harness_with_judges(self):
        """Run harness with --x1d-judges flag."""
        subprocess.run(
            [sys.executable, "-m", HARNESS_MODULE, "--provider", "qwen_vllm",
             "--x1d-judges", "gemini_pro,openai_chatgpt,anthropic_claude"],
            capture_output=True,
            cwd=REPO_ROOT,
        )
    
    def test_product_quality_not_pass_if_x2_fails(self):
        """Test 15a: Product quality cannot be PASS if any X2 gate fails."""
        x3_path = ARTIFACTS_DIR / "x3_disposition.json"
        assert x3_path.exists()
        
        x3_data = json.loads(x3_path.read_text())
        
        # If any X2 gate failed, product_quality should not be PASS
        if not x3_data.get("all_x2_passed", True):
            assert x3_data.get("product_quality_status") != "PASS", \
                "Product quality should not be PASS when X2 gates fail"
    
    def test_x3_disposition_shows_product_quality(self):
        """Test 15b: X3 disposition includes product_quality_status."""
        x3_path = ARTIFACTS_DIR / "x3_disposition.json"
        x3_data = json.loads(x3_path.read_text())
        
        assert "product_quality_status" in x3_data
        assert x3_data["product_quality_status"] in ["PASS", "PARTIAL", "FAIL", "BLOCKED"]


class TestX3DispositionWithLLMJudges:
    """Test 4-10: X3 disposition logic with three-provider judges."""
    
    @pytest.fixture(autouse=True)
    def run_harness_with_judges(self):
        """Run harness with --x1d-judges flag."""
        subprocess.run(
            [sys.executable, "-m", HARNESS_MODULE, "--provider", "qwen_vllm",
             "--x1d-judges", "gemini_pro,openai_chatgpt,anthropic_claude"],
            capture_output=True,
            cwd=REPO_ROOT,
        )
    
    def test_mocked_judge_cannot_produce_x3_allow(self):
        """Test 4: If any judge is MOCKED, X3 cannot be X3_ALLOW."""
        x3_path = ARTIFACTS_DIR / "x3_disposition.json"
        assert x3_path.exists()
        
        x3_data = json.loads(x3_path.read_text())
        
        # Check for mocked judges in llm_judge_refs
        llm_refs = x3_data.get("llm_judge_refs", [])
        has_mocked = any(j.get("evaluator_mode") == "MOCKED" for j in llm_refs)
        
        if has_mocked:
            assert x3_data["x3_code"] != "X3_ALLOW", \
                "MOCKED judges cannot produce X3_ALLOW"
    
    def test_blocked_judge_cannot_produce_x3_allow(self):
        """Test 5: If any judge is BLOCKED_PROVIDER_UNAVAILABLE, X3 cannot be X3_ALLOW."""
        x3_path = ARTIFACTS_DIR / "x3_disposition.json"
        assert x3_path.exists()
        
        x3_data = json.loads(x3_path.read_text())
        
        llm_refs = x3_data.get("llm_judge_refs", [])
        has_blocked = any(j.get("evaluator_mode") == "BLOCKED_PROVIDER_UNAVAILABLE" for j in llm_refs)
        
        if has_blocked:
            assert x3_data["x3_code"] != "X3_ALLOW", \
                "BLOCKED_PROVIDER_UNAVAILABLE judges cannot produce X3_ALLOW"
    
    def test_x3_allow_requires_all_model_backed(self):
        """Test 6: X3_ALLOW requires all three judges MODEL_BACKED."""
        x3_path = ARTIFACTS_DIR / "x3_disposition.json"
        assert x3_path.exists()
        
        x3_data = json.loads(x3_path.read_text())
        
        if x3_data["x3_code"] == "X3_ALLOW":
            llm_refs = x3_data.get("llm_judge_refs", [])
            assert len(llm_refs) == 3, "X3_ALLOW requires exactly 3 judges"
            
            all_model_backed = all(j.get("evaluator_mode") == "MODEL_BACKED" for j in llm_refs)
            assert all_model_backed, "X3_ALLOW requires all judges MODEL_BACKED"
    
    def test_x3_block_if_x2_fails(self):
        """Test 7: X3_BLOCK if any X2 gate fails."""
        x3_path = ARTIFACTS_DIR / "x3_disposition.json"
        assert x3_path.exists()
        
        x3_data = json.loads(x3_path.read_text())
        
        if not x3_data["all_x2_passed"]:
            assert x3_data["x3_code"] == "X3_BLOCK", \
                "X2 failure must produce X3_BLOCK"
    
    def test_x3_block_if_judge_decisive_failure(self):
        """Test 8: X3_BLOCK if any judge has decisive_failure=true."""
        x3_path = ARTIFACTS_DIR / "x3_disposition.json"
        assert x3_path.exists()
        
        x3_data = json.loads(x3_path.read_text())
        
        llm_refs = x3_data.get("llm_judge_refs", [])
        has_decisive_failure = any(j.get("decisive_failure") for j in llm_refs)
        
        if has_decisive_failure:
            assert x3_data["x3_code"] == "X3_BLOCK", \
                "Decisive judge failure must produce X3_BLOCK"

    def test_x3_soft_fail_when_judge_below_threshold_not_decisive(self):
        """Soft MODEL_BACKED_FAIL without decisive_failure => X3_REVIEW_JUDGE_SOFT_FAIL."""
        from apps_rg.runtime.exit.executive_summary_x3 import aggregate_x3

        x3 = aggregate_x3(
            resume_display_text="Enterprise AI platform leader who delivered outcomes.",
            claim_ledger=[{"claim_text": "c", "source_fact_ids": ["bul_unify_001"]}],
            x2_gates=[{"gate_id": "x2_schema_valid", "pass": True}],
            x1d_judges=[
                {
                    "provider_key": "gemini_pro",
                    "evaluator_mode": "MODEL_BACKED",
                    "provider_status": "MODEL_BACKED_PASS",
                    "pass": True,
                    "decisive_failure": False,
                    "normalized_score": 1.0,
                    "normalized_threshold": 0.8,
                },
                {
                    "provider_key": "openai_chatgpt",
                    "evaluator_mode": "MODEL_BACKED",
                    "provider_status": "MODEL_BACKED_PASS",
                    "pass": True,
                    "decisive_failure": False,
                    "normalized_score": 0.92,
                    "normalized_threshold": 0.8,
                },
                {
                    "provider_key": "anthropic_claude",
                    "evaluator_mode": "MODEL_BACKED",
                    "provider_status": "MODEL_BACKED_FAIL",
                    "pass": False,
                    "decisive_failure": False,
                    "normalized_score": 0.72,
                    "normalized_threshold": 0.8,
                },
            ],
            runtime_generation_status="REAL_LLM",
            product_quality_status="PASS",
        )
        assert x3.x3_code == "X3_REVIEW_JUDGE_SOFT_FAIL"
        assert x3.soft_failed_judges == ["anthropic_claude"]
        assert x3.proceed_to_runtime is False
        assert x3.pass_ is False

    def test_x3_allow_impossible_with_any_model_backed_fail(self):
        from apps_rg.runtime.exit.executive_summary_x3 import aggregate_x3

        x3 = aggregate_x3(
            resume_display_text="text",
            claim_ledger=[{"claim_text": "c", "source_fact_ids": ["bul_unify_001"]}],
            x2_gates=[{"gate_id": "x2_schema_valid", "pass": True}],
            x1d_judges=[
                {
                    "provider_key": "anthropic_claude",
                    "evaluator_mode": "MODEL_BACKED",
                    "provider_status": "MODEL_BACKED_FAIL",
                    "pass": False,
                    "decisive_failure": False,
                }
            ],
            runtime_generation_status="REAL_LLM",
            product_quality_status="PASS",
        )
        assert x3.x3_code != "X3_ALLOW"
    
    def test_x3_review_judge_provider_blocked(self):
        """Test 9: X3_REVIEW_JUDGE_PROVIDER_BLOCKED if X2 passes but judges blocked."""
        x3_path = ARTIFACTS_DIR / "x3_disposition.json"
        assert x3_path.exists()
        
        x3_data = json.loads(x3_path.read_text())
        
        llm_refs = x3_data.get("llm_judge_refs", [])
        has_blocked = any(j.get("evaluator_mode") == "BLOCKED_PROVIDER_UNAVAILABLE" for j in llm_refs)
        
        if x3_data["all_x2_passed"] and has_blocked and x3_data["x3_code"] != "X3_BLOCK":
            # If X2 passes but judges are blocked, should be REVIEW_JUDGE_PROVIDER_BLOCKED
            assert x3_data["x3_code"] == "X3_REVIEW_JUDGE_PROVIDER_BLOCKED", \
                "X2 pass + blocked judges should produce X3_REVIEW_JUDGE_PROVIDER_BLOCKED"


class TestL6ShadowWithLLMJudges:
    """Test 10: L6 shadow package with LLM judges."""
    
    @pytest.fixture(autouse=True)
    def run_harness_with_judges(self):
        """Run harness with --x1d-judges flag."""
        subprocess.run(
            [sys.executable, "-m", HARNESS_MODULE, "--provider", "qwen_vllm",
             "--x1d-judges", "gemini_pro,openai_chatgpt,anthropic_claude"],
            capture_output=True,
            cwd=REPO_ROOT,
        )
    
    def test_l6_records_all_three_judge_refs(self):
        """Test 10a: L6 package records all three judge refs."""
        l6_path = ARTIFACTS_DIR / "l6_shadow_eval_package.json"
        assert l6_path.exists()
        
        l6_data = json.loads(l6_path.read_text())
        judge_refs = l6_data.get("x1d_judge_refs", [])
        
        # Should have at least 3 refs (legacy + LLM judges)
        assert len(judge_refs) >= 3, f"Expected at least 3 judge refs, got {len(judge_refs)}"
    
    def test_l6_offline_only_true(self):
        """Test 10b: L6 package has offline_only=true."""
        l6_path = ARTIFACTS_DIR / "l6_shadow_eval_package.json"
        l6_data = json.loads(l6_path.read_text())
        assert l6_data.get("offline_only") is True
    
    def test_l6_promotion_allowed_false(self):
        """Test 10c: L6 package has promotion_allowed=false."""
        l6_path = ARTIFACTS_DIR / "l6_shadow_eval_package.json"
        l6_data = json.loads(l6_path.read_text())
        assert l6_data.get("promotion_allowed") is False
    
    def test_l6_learning_mutation_performed_false(self):
        """Test 10d: L6 package has learning_mutation_performed=false."""
        l6_path = ARTIFACTS_DIR / "l6_shadow_eval_package.json"
        l6_data = json.loads(l6_path.read_text())
        assert l6_data.get("learning_mutation_performed") is False


class TestNoCoreChanges:
    """Test 11: No registry/v1/core changes."""
    
    def test_no_agentic_core_imports(self):
        """Harness does not import from agentic_core."""
        harness_path = REPO_ROOT / "apps_rg" / "runtime" / "dry_run" / "executive_summary_demo.py"
        harness_code = harness_path.read_text()
        
        assert "from agentic_core" not in harness_code
        assert "import agentic_core" not in harness_code


class TestProviderArtifacts:
    """Test provider request/response artifacts are written."""
    
    @pytest.fixture(autouse=True)
    def run_harness_with_judges(self):
        """Run harness with --x1d-judges flag."""
        subprocess.run(
            [sys.executable, "-m", HARNESS_MODULE, "--provider", "qwen_vllm",
             "--x1d-judges", "gemini_pro,openai_chatgpt,anthropic_claude"],
            capture_output=True,
            cwd=REPO_ROOT,
        )
    
    def test_gemini_request_artifact_exists(self):
        """x1d_provider_request_gemini_pro.json exists."""
        path = ARTIFACTS_DIR / "x1d_provider_request_gemini_pro.json"
        assert path.exists()
        
        data = json.loads(path.read_text())
        assert data["provider_key"] == "gemini_pro"
        assert "input_hash" in data
    
    def test_openai_request_artifact_exists(self):
        """x1d_provider_request_openai_chatgpt.json exists."""
        path = ARTIFACTS_DIR / "x1d_provider_request_openai_chatgpt.json"
        assert path.exists()
        
        data = json.loads(path.read_text())
        assert data["provider_key"] == "openai_chatgpt"
        assert "input_hash" in data
    
    def test_anthropic_request_artifact_exists(self):
        """x1d_provider_request_anthropic_claude.json exists."""
        path = ARTIFACTS_DIR / "x1d_provider_request_anthropic_claude.json"
        assert path.exists()
        
        data = json.loads(path.read_text())
        assert data["provider_key"] == "anthropic_claude"
        assert "input_hash" in data
    
    def test_provider_response_artifacts_exist(self):
        """Provider response artifacts exist for blocked/unavailable providers."""
        # Response artifacts should exist even for blocked providers
        for provider in ["gemini_pro", "openai_chatgpt", "anthropic_claude"]:
            path = ARTIFACTS_DIR / f"x1d_provider_response_{provider}.json"
            assert path.exists(), f"Response artifact for {provider} should exist"


class TestJudgeRubricFields:
    """Test judge output contains all required rubric fields."""
    
    @pytest.fixture(autouse=True)
    def run_harness_with_judges(self):
        """Run harness with --x1d-judges flag."""
        subprocess.run(
            [sys.executable, "-m", HARNESS_MODULE, "--provider", "qwen_vllm",
             "--x1d-judges", "gemini_pro,openai_chatgpt,anthropic_claude"],
            capture_output=True,
            cwd=REPO_ROOT,
        )
    
    def test_judge_has_all_required_fields(self):
        """Each judge has all required fields."""
        path = ARTIFACTS_DIR / "x1d_llm_judge_outputs.json"
        data = json.loads(path.read_text())
        
        required_fields = [
            "judge_id", "provider_name", "provider_key", "evaluator_mode",
            "model_name", "provider_available", "exact_provider_error",
            "rubric_version", "input_hash", "output_hash",
            "score", "threshold", "pass", "decisive_failure",
            "findings", "cited_sentence_indexes", "remediation_suggestions"
        ]
        
        for judge in data:
            for field in required_fields:
                assert field in judge, f"Missing field '{field}' in judge {judge.get('judge_id', 'unknown')}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
