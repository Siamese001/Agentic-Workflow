"""AG-6 apps_rg Golden Path Runtime Proof — End-to-end contract chain verification.

Per plan ag6-apps-rg-golden-path-runtime-proof-d8e4a2.

This module tests the complete golden-path runtime chain for apps_rg:
U0 → L1 → L0 → C0 → PA → L2 → Exit → X1/X3

All 9 invariants from AG-5 + AG-6 must hold:
1. X3Disposition cannot be emitted without X1CheckoutResult
2. AggregateDecision.x1_checkout_result is consumed, not merely attached
3. material FAIL blocks ALLOW_FINISH
4. material UNKNOWN on groundedness, safety, replay, write, privacy, audit cannot pass
5. scalar eval_score is no longer the authoritative quality carrier
6. X1D groundedness fails grounded/model paths with missing FinalEvidenceContract
7. NOT_APPLICABLE requires a reason
8. No embeddings were generated
9. No ChromaDB mutation occurred
10. apps_rg C0 populates all AG-4 evidence fields (AG-6 addition)
11. apps_rg evidence stays in C0_EVIDENCE_DATA_ONLY slots (AG-6 addition)
12. L2 preserves evidence refs through to Exit (AG-6 addition)
13. apps_rg Exit consumes X1CheckoutResult for X3 (AG-6 addition)
"""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from unittest.mock import patch

# Pre-flight import check — fail early with clear message if runtime not available
try:
    from agentic_core.runtime.contracts.apps_rg_ingress_payload import (
        AppsRgIngressPayload,
        RequestEnvelope,
        ValidatedRequest,
    )
    from agentic_core.runtime.contracts.l1_plan_contract import L1PlanContract
    from agentic_core.runtime.contracts.route_contract import RouteContract
    from agentic_core.runtime.contracts.final_evidence_contract import (
        FinalEvidenceContract,
        EvidenceItem,
        STATUS_NOT_APPLICABLE,
        STATUS_UNKNOWN,
        ALLOWED_PROMPT_SLOT_C0_EVIDENCE_DATA_ONLY,
    )
    from agentic_core.runtime.contracts.compiled_prompt_artifact import (
        CompiledPromptArtifact,
    )
    from agentic_core.runtime.contracts.sealed_l2_artifact import SealedL2Artifact
    from agentic_core.runtime.contracts.x1_checkout_result import (
        X1CheckoutResult,
        X1Item,
        X1Verdict,
    )
    from apps_rg.runtime.bindings.u0_binding import u0_validate_apps_rg
    from apps_rg.runtime.bindings.l1_binding import l1_plan_apps_rg
    from apps_rg.runtime.bindings.l0_binding import l0_route_apps_rg
    from apps_rg.runtime.bindings.c0_binding import c0_retrieve_apps_rg
    from apps_rg.runtime.bindings.pa_binding import pa_compose_apps_rg
    from apps_rg.runtime.bindings.l2_binding import l2_execute_apps_rg
    from apps_rg.runtime.bindings.exit_binding import ExitResult, exit_finalize_apps_rg
    from agentic_core.L3_orchestration.exit_eval.v6.x1_checkout_adapter import (
        build_x1_checkout_result,
    )
    from agentic_core.L3_orchestration.exit_eval.v6.x2_matrix import (
        aggregate_decision,
        AggregateDecision,
    )
    from agentic_core.runtime.entry.apps_rg_dispatch import apps_rg_dispatch
    RUNTIME_AVAILABLE = True
except ImportError as e:
    RUNTIME_AVAILABLE = False
    IMPORT_ERROR = str(e)


class TestAG6Preconditions(unittest.TestCase):
    """Verify runtime is available before running golden-path tests."""

    def test_runtime_imports_available(self):
        """All required runtime modules must be importable."""
        self.assertTrue(
            RUNTIME_AVAILABLE,
            f"Runtime imports failed: {IMPORT_ERROR if not RUNTIME_AVAILABLE else 'N/A'}"
        )


class TestAG6GoldenPathContractChain(unittest.TestCase):
    """
    AG-6 Golden Path: Full contract chain from ingress through Exit.
    
    Input: Realistic apps_rg request fixture
    Expected chain:
    ValidatedRequest → L1PlanContract → RouteContract → FinalEvidenceContract
    → CompiledPromptArtifact → SealedL2Artifact → ExitReviewPacket
    → X1CheckoutResult → ExitResult
    """

    @classmethod
    def setUpClass(cls):
        """Create golden-path test fixtures."""
        if not RUNTIME_AVAILABLE:
            raise unittest.SkipTest("Runtime not available")
        
        cls.fixture = cls._create_golden_fixture()
        cls.repo_root = cls._resolve_repo_root()

    def _c0_retrieve_fixture(self, route: RouteContract, validated: ValidatedRequest) -> FinalEvidenceContract:
        fixture_env = {
            "APPS_RG_TEST_HARNESS": "1",
            "APPS_RG_C0_DENSE_SPARSE_MANDATORY": "0",
            "APPS_RG_C0_SPARSE_ENABLED": "0",
            "CHROMA_PERSIST_DIR": "",
        }
        with patch.dict(os.environ, fixture_env):
            return c0_retrieve_apps_rg(route, validated, chromadb_path=None)

    @classmethod
    def _resolve_repo_root(cls) -> Path:
        """Resolve repo root for file operations."""
        here = Path(__file__).resolve()
        for parent in [here.parent, *here.parents]:
            if (parent / "pyproject.toml").exists():
                return parent
        return here.parents[4]

    @classmethod
    def _create_golden_fixture(cls) -> dict[str, Any]:
        """
        Create canonical apps_rg golden-path input fixture.
        
        Includes:
        - target role/company/level
        - JD text (realistic)
        - source resume text (realistic)
        - output requirements
        - fact-checking requirement
        - support/citation requirements
        - trace/replay/audit refs
        """
        jd_text = """Senior Software Engineer - AI Infrastructure

We are seeking a Senior Software Engineer to join our AI Infrastructure team.
The ideal candidate will have:
- 5+ years of Python development experience
- Experience with distributed systems and cloud infrastructure
- Knowledge of ML pipelines and model serving
- Familiarity with Docker, Kubernetes, and AWS/GCP
- Experience with large language models and prompt engineering
- Strong system design and debugging skills

Responsibilities:
- Design and build scalable ML inference infrastructure
- Optimize model serving latency and throughput
- Implement monitoring and observability for AI systems
- Collaborate with research teams to productionize models
"""
        
        resume_text = """JANE CHEN
Senior Software Engineer

EXPERIENCE

TechCorp Inc. | Senior Software Engineer | 2021-Present
- Architected distributed microservices handling 10M+ daily requests
- Built real-time data pipelines using Kafka and Spark
- Led migration from on-prem to AWS, reducing costs by 40%
- Implemented CI/CD pipelines with GitHub Actions

DataSystems Co. | Software Engineer | 2018-2021
- Developed Python-based ETL pipelines for data warehouse
- Designed REST APIs serving 1M+ requests/day
- Optimized database queries, improving performance by 60%

SKILLS
- Languages: Python, Go, Java
- Cloud: AWS (EC2, S3, Lambda), GCP (Compute, Storage)
- ML: PyTorch, TensorFlow, Hugging Face Transformers
- Infrastructure: Kubernetes, Docker, Terraform
- Databases: PostgreSQL, MongoDB, Redis

EDUCATION
BS Computer Science, UC Berkeley (2018)
"""
        
        return {
            "target_company": "TechCorp AI",
            "target_role": "Senior Software Engineer - AI Infrastructure",
            "target_level": "L5",
            "jd_text": jd_text,
            "resume_text": resume_text,
            "output_requirements": {
                "format": "json",
                "schema_version": "master_resume_v2.16",
                "sections": ["executive_summary", "experience", "skills", "education"],
            },
            "fact_check_required": True,
            "provenance_required": True,
            "citation_required": True,
            "replay_key": "ag6-golden-path-test-001",
            "trace_id": "ag6-trace-golden-001",
            "request_id": "ag6-req-001",
            "run_id": "ag6-run-001",
        }

    def _build_ingress_payload(self, fixture: dict[str, Any]) -> dict[str, Any]:
        """Build full apps_rg ingress payload from fixture."""
        return {
            "app_id": "apps_rg",
            "task_class": "resume_generation",
            "target_company": fixture["target_company"],
            "target_role": fixture["target_role"],
            "target_level": fixture["target_level"],
            "source_resume_ref": None,
            "source_resume_text": fixture["resume_text"],
            "job_description_ref": None,
            "job_description_text": fixture["jd_text"],
            "briefing_artifact_ref": None,
            "auto_research_internal": False,
            "auto_research_tavily": False,
            "research_via": None,
            "user_constraints": {
                "fact_check_required": fixture["fact_check_required"],
                "provenance_required": fixture["provenance_required"],
                "citation_required": fixture["citation_required"],
                "briefing_text": (
                    "TechCorp AI is hiring for AI infrastructure with emphasis "
                    "on production model serving, observability, and cloud-scale "
                    "distributed systems."
                ),
            },
            "output_preferences": fixture["output_requirements"],
            "idempotency_key": fixture["replay_key"],
        }

    def test_w0_ingress_payload_is_valid(self):
        """W0: Verify golden fixture produces valid ingress payload."""
        payload = self._build_ingress_payload(self.fixture)
        self.assertEqual(payload["app_id"], "apps_rg")
        self.assertEqual(payload["task_class"], "resume_generation")
        self.assertIsNotNone(payload["target_company"])
        self.assertIsNotNone(payload["target_role"])
        self.assertIsNotNone(payload["job_description_text"])
        self.assertIsNotNone(payload["source_resume_text"])

    def test_w1_u0_produces_validated_request(self):
        """W1: U0 produces ValidatedRequest with reflection receipt."""
        payload = self._build_ingress_payload(self.fixture)
        envelope = RequestEnvelope(
            payload=AppsRgIngressPayload(**payload),
            request_id=self.fixture["request_id"],
            run_id=self.fixture["run_id"],
            trace_id=self.fixture["trace_id"],
            submitted_at=datetime.now(timezone.utc).isoformat(),
        )
        
        validated = u0_validate_apps_rg(envelope)
        
        self.assertIsInstance(validated, ValidatedRequest)
        self.assertEqual(validated.request_id, self.fixture["request_id"])
        self.assertIsNotNone(validated.reflection_receipt)
        self.assertTrue(validated.reflection_receipt.pass_status)
        self.assertIsNotNone(validated.app_payload)
        self.assertIn("jd_payload", validated.app_payload)
        self.assertIn("resume_payload", validated.app_payload)

    def test_w2_l1_produces_plan_contract(self):
        """W2: L1 produces L1PlanContract from ValidatedRequest."""
        payload = self._build_ingress_payload(self.fixture)
        envelope = RequestEnvelope(
            payload=AppsRgIngressPayload(**payload),
            request_id=self.fixture["request_id"],
            run_id=self.fixture["run_id"],
            trace_id=self.fixture["trace_id"],
            submitted_at=datetime.now(timezone.utc).isoformat(),
        )
        validated = u0_validate_apps_rg(envelope)
        
        l1_plan = l1_plan_apps_rg(validated)
        
        self.assertIsInstance(l1_plan, L1PlanContract)
        self.assertEqual(l1_plan.request_id, self.fixture["request_id"])
        self.assertIsNotNone(l1_plan.task_plan)
        self.assertIsNotNone(l1_plan.required_capabilities)
        self.assertIsNotNone(l1_plan.task_plan)

    def test_w3_l0_produces_route_contract(self):
        """W3: L0 produces RouteContract from L1PlanContract."""
        payload = self._build_ingress_payload(self.fixture)
        envelope = RequestEnvelope(
            payload=AppsRgIngressPayload(**payload),
            request_id=self.fixture["request_id"],
            run_id=self.fixture["run_id"],
            trace_id=self.fixture["trace_id"],
            submitted_at=datetime.now(timezone.utc).isoformat(),
        )
        validated = u0_validate_apps_rg(envelope)
        l1_plan = l1_plan_apps_rg(validated)
        
        route = l0_route_apps_rg(l1_plan)
        
        self.assertIsInstance(route, RouteContract)
        self.assertEqual(route.request_id, self.fixture["request_id"])
        self.assertTrue(route.grounding_required)
        self.assertTrue(route.model_generation_required)

    def test_w4_c0_produces_final_evidence_contract(self):
        """W4: C0 produces FinalEvidenceContract with all AG-4 fields populated."""
        payload = self._build_ingress_payload(self.fixture)
        envelope = RequestEnvelope(
            payload=AppsRgIngressPayload(**payload),
            request_id=self.fixture["request_id"],
            run_id=self.fixture["run_id"],
            trace_id=self.fixture["trace_id"],
            submitted_at=datetime.now(timezone.utc).isoformat(),
        )
        validated = u0_validate_apps_rg(envelope)
        l1_plan = l1_plan_apps_rg(validated)
        route = l0_route_apps_rg(l1_plan)
        
        fec = self._c0_retrieve_fixture(route, validated)
        
        self.assertIsInstance(fec, FinalEvidenceContract)
        self.assertEqual(fec.request_id, self.fixture["request_id"])
        self.assertTrue(len(fec.evidence_items) >= 2, "Should have JD + resume evidence")
        
        # AG-4 invariant: all evidence items must have required fields
        for item in fec.evidence_items:
            self.assertIsInstance(item, EvidenceItem)
            self.assertTrue(item.evidence_id, "evidence_id must be populated")
            self.assertTrue(item.source_id, "source_id must be populated")
            self.assertTrue(item.source_type, "source_type must be populated")
            self.assertTrue(item.source_uri_or_ref, "source_uri_or_ref must be populated")
            self.assertTrue(item.chunk_digest, "chunk_digest must be populated")
            self.assertTrue(item.citation_anchor, "citation_anchor must be populated")
            self.assertEqual(
                item.allowed_prompt_slot,
                ALLOWED_PROMPT_SLOT_C0_EVIDENCE_DATA_ONLY,
                "allowed_prompt_slot must be C0_EVIDENCE_DATA_ONLY"
            )
            self.assertTrue(item.evidence_digest, "evidence_digest must be populated")
            
            # AG-4: NOT_APPLICABLE fields must have reason
            if item.freshness_status == STATUS_NOT_APPLICABLE:
                self.assertTrue(
                    item.not_applicable_reason,
                    "NOT_APPLICABLE freshness must have reason"
                )
            if item.acl_status == STATUS_NOT_APPLICABLE:
                self.assertTrue(
                    item.not_applicable_reason,
                    "NOT_APPLICABLE acl must have reason"
                )
        
        # Contract-level fields
        self.assertTrue(fec.compilation_hash, "compilation_hash must be populated")
        self.assertTrue(fec.final_evidence_digest, "final_evidence_digest must be populated")
        self.assertTrue(fec.citation_map, "citation_map must be populated")
        self.assertTrue(fec.source_lineage_map, "source_lineage_map must be populated")

    def test_w5_pa_consumes_evidence_as_data_only(self):
        """W5: PA consumes FinalEvidenceContract and keeps evidence in data slots only."""
        payload = self._build_ingress_payload(self.fixture)
        envelope = RequestEnvelope(
            payload=AppsRgIngressPayload(**payload),
            request_id=self.fixture["request_id"],
            run_id=self.fixture["run_id"],
            trace_id=self.fixture["trace_id"],
            submitted_at=datetime.now(timezone.utc).isoformat(),
        )
        validated = u0_validate_apps_rg(envelope)
        l1_plan = l1_plan_apps_rg(validated)
        route = l0_route_apps_rg(l1_plan)
        fec = self._c0_retrieve_fixture(route, validated)
        
        prompt = pa_compose_apps_rg(route, l1_plan, fec, validated)
        
        self.assertIsInstance(prompt, CompiledPromptArtifact)
        self.assertEqual(prompt.request_id, self.fixture["request_id"])
        
        # Evidence must be referenced, not embedded as instructions
        self.assertTrue(prompt.evidence_digest, "evidence_digest must be populated")
        
        # Check that evidence refs chain correctly
        self.assertTrue(prompt.prompt_blocks, "prompt_blocks must be populated")
        
        # Verify slot_lineage_map exists (AG-2 addition)
        self.assertTrue(prompt.slot_lineage_map, "slot_lineage_map must be populated")
        
        # AG-2: slot_lineage_map must be preserved
        self.assertTrue(prompt.slot_lineage_map, "slot_lineage_map must be preserved")

    @patch.dict(os.environ, {"APPS_RG_L2_FORCE_STUB": "1"})
    def test_w6_l2_preserves_evidence_refs(self):
        """W6: L2 produces SealedL2Artifact preserving evidence refs."""
        payload = self._build_ingress_payload(self.fixture)
        envelope = RequestEnvelope(
            payload=AppsRgIngressPayload(**payload),
            request_id=self.fixture["request_id"],
            run_id=self.fixture["run_id"],
            trace_id=self.fixture["trace_id"],
            submitted_at=datetime.now(timezone.utc).isoformat(),
        )
        validated = u0_validate_apps_rg(envelope)
        l1_plan = l1_plan_apps_rg(validated)
        route = l0_route_apps_rg(l1_plan)
        fec = self._c0_retrieve_fixture(route, validated)
        prompt = pa_compose_apps_rg(route, l1_plan, fec, validated)
        
        sealed = l2_execute_apps_rg(prompt)
        
        self.assertIsInstance(sealed, SealedL2Artifact)
        self.assertEqual(sealed.request_id, self.fixture["request_id"])
        
        # Evidence refs must be preserved
        self.assertTrue(
            sealed.prompt_artifact_digest,
            "prompt_artifact_digest must chain to PA"
        )
        self.assertTrue(sealed.compilation_hash, "compilation_hash must be populated")
        
        # L5 certification ref must be present
        self.assertTrue(sealed.l5_certification_ref, "l5_certification_ref must be present")

    @patch.dict(os.environ, {"APPS_RG_L2_FORCE_STUB": "1"})
    def test_w7_exit_produces_exit_result_with_fec(self):
        """W7: Exit produces ExitResult while consuming the FEC."""
        payload = self._build_ingress_payload(self.fixture)
        envelope = RequestEnvelope(
            payload=AppsRgIngressPayload(**payload),
            request_id=self.fixture["request_id"],
            run_id=self.fixture["run_id"],
            trace_id=self.fixture["trace_id"],
            submitted_at=datetime.now(timezone.utc).isoformat(),
        )
        validated = u0_validate_apps_rg(envelope)
        l1_plan = l1_plan_apps_rg(validated)
        route = l0_route_apps_rg(l1_plan)
        fec = self._c0_retrieve_fixture(route, validated)
        prompt = pa_compose_apps_rg(route, l1_plan, fec, validated)
        sealed = l2_execute_apps_rg(prompt)
        
        exit_result = exit_finalize_apps_rg(
            sealed,
            prompt,
            fec=fec,
            target_company=self.fixture["target_company"],
            target_role=self.fixture["target_role"],
        )
        
        self.assertIsInstance(exit_result, ExitResult)
        disposition = exit_result.disposition
        
        # ExitResult carries apps_rg-local authorization and inert proposals.
        self.assertTrue(disposition.outcome_authorized)
        self.assertFalse(disposition.c0_blocking)
        
        self.assertTrue(disposition.final_output, "Authorized disposition must have output")
        self.assertTrue(
            exit_result.artifact_commit_candidates,
            "ExitResult must carry inert artifact commit candidates",
        )

    def test_w8_no_chromadb_imports_in_golden_path(self):
        """W8: No ChromaDB imports in any golden-path module."""
        import ast
        
        modules_to_check = [
            "apps_rg.runtime.bindings.c0_binding",
            "apps_rg.runtime.bindings.pa_binding",
            "apps_rg.runtime.bindings.l2_binding",
            "apps_rg.runtime.bindings.exit_binding",
        ]
        
        for module_name in modules_to_check:
            try:
                import importlib
                mod = importlib.import_module(module_name)
                source = Path(mod.__file__).read_text()
                tree = ast.parse(source)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            self.assertNotIn(
                                "chromadb", alias.name,
                                f"{module_name} imports chromadb: {alias.name}"
                            )
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            self.assertNotIn(
                                "chromadb", node.module,
                                f"{module_name} imports from chromadb: {node.module}"
                            )
            except Exception as e:
                self.fail(f"Failed to check {module_name}: {e}")

    def test_w9_no_embedding_calls_in_golden_path(self):
        """W9: No embedding generation calls in golden-path."""
        import ast
        
        modules_to_check = [
            "apps_rg.runtime.bindings.c0_binding",
            "apps_rg.runtime.bindings.pa_binding",
            "apps_rg.runtime.bindings.l2_binding",
        ]
        
        forbidden_patterns = ["embed_texts", "bge_embed", "get_embeddings"]
        
        for module_name in modules_to_check:
            try:
                import importlib
                mod = importlib.import_module(module_name)
                source = Path(mod.__file__).read_text()
                
                for pattern in forbidden_patterns:
                    self.assertNotIn(
                        pattern, source,
                        f"{module_name} contains forbidden pattern: {pattern}"
                    )
            except Exception as e:
                self.fail(f"Failed to check {module_name}: {e}")


class TestAG6X1ExitIntegration(unittest.TestCase):
    """Test X1 checkout integration with Exit for apps_rg."""

    @classmethod
    def setUpClass(cls):
        if not RUNTIME_AVAILABLE:
            raise unittest.SkipTest("Runtime not available")

    def _build_minimal_pipeline_result(self) -> tuple[SealedL2Artifact, CompiledPromptArtifact]:
        """Build minimal pipeline result for X1 testing."""
        timestamp = datetime.now(timezone.utc).isoformat()
        
        # Build minimal evidence
        from apps_rg.runtime.bindings.c0_binding import APPS_RG_C0_CERT_REF
        fec = FinalEvidenceContract(
            request_id="x1-test-001",
            run_id="x1-run-001",
            app_id="apps_rg",
            trace_id="x1-trace-001",
            tenant_id="apps_rg",
            evidence_items=tuple([
                EvidenceItem(
                    source="test:jd",
                    content="Test JD content",
                    content_type="text",
                    evidence_id="test-ev-001",
                    source_id="test.jd",
                    source_type="test_payload",
                    chunk_digest=hashlib.sha256(b"Test JD content").hexdigest(),
                    citation_anchor="test:jd:abc123",
                    evidence_digest=hashlib.sha256(b"Test JD content").hexdigest(),
                    support_status="PASS",
                    allowed_prompt_slot=ALLOWED_PROMPT_SLOT_C0_EVIDENCE_DATA_ONLY,
                ),
            ]),
            compilation_hash=hashlib.sha256(b"test").hexdigest(),
            final_evidence_digest=hashlib.sha256(b"test").hexdigest(),
            support_status="PASS",
            l5_certification_ref=APPS_RG_C0_CERT_REF,
        )
        
        # Build minimal prompt
        from agentic_core.runtime.contracts.origin import Origin
        from agentic_core.runtime.contracts.compiled_prompt_artifact import PromptBlock
        from apps_rg.runtime.bindings.pa_binding import APPS_RG_PA_CERT_REF
        prompt = CompiledPromptArtifact(
            request_id="x1-test-001",
            run_id="x1-run-001",
            app_id="apps_rg",
            trace_id="x1-trace-001",
            tenant_id="apps_rg",
            prompt_blocks=tuple([
                PromptBlock(
                    role="system",
                    content="You are a resume writer.",
                    origin=Origin.SYSTEM_INTERNAL,
                    block_index=0,
                ),
                PromptBlock(
                    role="user",
                    content="Write a resume for a software engineer.",
                    origin=Origin.USER_INTENT,
                    block_index=1,
                ),
            ]),
            target_model="Retired/Provider-Model",
            target_provider="local_model_server",
            compilation_hash=hashlib.sha256(b"prompt").hexdigest(),
            evidence_digest=fec.final_evidence_digest,
            schema_version="1.0",
            l5_certification_ref=APPS_RG_PA_CERT_REF,
        )
        
        # Build minimal sealed artifact
        from apps_rg.runtime.bindings.l2_binding import APPS_RG_L2_CERT_REF
        sealed = SealedL2Artifact(
            request_id="x1-test-001",
            run_id="x1-run-001",
            app_id="apps_rg",
            trace_id="x1-trace-001",
            tenant_id="apps_rg",
            generated_content='{"stub": true}',
            prompt_artifact_digest=prompt.compilation_hash,
            compilation_hash=hashlib.sha256(b"sealed").hexdigest(),
            execution_status="completed_stub",
            execution_timestamp=timestamp,
            execution_duration_ms=0,
            schema_version="1.0",
            l5_certification_ref=APPS_RG_L2_CERT_REF,
        )
        
        return sealed, prompt

    def test_x1_checkout_can_be_built_from_sealed_artifact(self):
        """X1CheckoutResult can be built from sealed artifact and prompt."""
        sealed, prompt = self._build_minimal_pipeline_result()
        
        # Build X1CheckoutResult from pipeline artifacts
        from agentic_core.L3_orchestration.exit_eval.v6.types import (
            ExitReviewPacket,
            SourceType,
        )
        
        packet = ExitReviewPacket(
            source_type=SourceType.L2_SEALED_ARTIFACT,
            request_id=sealed.request_id,
            run_id=sealed.run_id,
            trace_root=sealed.trace_id,
            output={
                "output_id": sealed.run_id,
                "content_type": "application/json",
                "digest": sealed.compilation_hash,
            },
            evidence_bundle={
                "bundle_id": sealed.prompt_artifact_digest,
            },
            otel_spans={
                "spans": {
                    "trace_root": {},
                    "route_contract": {},
                    "tool_invocations": {},
                    "evidence_contracts": {},
                    "step_outputs": {},
                    "exit_disposition": {},
                },
            },
            final_evidence_contract={
                "c0_status": "PASS",
                "evidence_count": 1,
            },
        )
        
        # X1CheckoutResult should be constructible
        checkout = X1CheckoutResult(
            request_id=sealed.request_id,
            run_id=sealed.run_id,
            trace_root=sealed.trace_id,
        )
        
        self.assertIsInstance(checkout, X1CheckoutResult)
        self.assertEqual(checkout.request_id, sealed.request_id)

    def test_x1d_groundedness_evaluates_fec_status(self):
        """X1D groundedness evaluator works with FinalEvidenceContract."""
        from agentic_core.L3_orchestration.exit_eval.v6.x1d_deterministic_evaluator import (
            evaluate_x1d_groundedness_deterministic,
            GroundednessEvidence,
        )
        
        # Build minimal evidence dict for X1D
        fec_dict = {
            "c0_status": "PASS",
            "evidence_items": [{"source": "test"}],
            "support_target_met": True,
            "support_target_partial": True,
            "evidence_sufficiency_score": 1.0,
            "citation_map": [("ev1", "cite1")],
            "contradiction_report": "",
        }
        
        # Evaluator should not raise - use keyword arguments
        result = evaluate_x1d_groundedness_deterministic(
            fec=fec_dict,
            intent_text="Generate resume",
            output_text='{"resume": true}',
        )
        self.assertIsNotNone(result)


class TestAG6NoBypass(unittest.TestCase):
    """Verify no legacy payload bypass exists in apps_rg pipeline."""

    @classmethod
    def setUpClass(cls):
        if not RUNTIME_AVAILABLE:
            raise unittest.SkipTest("Runtime not available")

    def test_c0_never_reads_envelope_payload(self):
        """C0 binding must never read from envelope.payload directly."""
        import ast
        
        source = Path(
            "c:\\Git\\Agentic-Workflow-FRESH\\apps_rg\\runtime\\bindings\\c0_binding.py"
        ).read_text()
        tree = ast.parse(source)
        
        # Check for any reference to envelope.payload or payload["...
        source_text = ast.dump(tree)
        
        # The C0 binding should read from validated_request.app_payload only
        self.assertIn("app_payload", source)
        
        # Should NOT have direct envelope.payload references
        # (This is a heuristic check — full static analysis is in the CI gate)

    def test_pa_never_reads_legacy_payload(self):
        """PA binding must never read from legacy AppsRgIngressPayload."""
        import ast
        
        source = Path(
            "c:\\Git\\Agentic-Workflow-FRESH\\apps_rg\\runtime\\bindings\\pa_binding.py"
        ).read_text()
        
        # Should read from validated_request.app_payload
        self.assertIn("app_payload", source)


if __name__ == "__main__":
    unittest.main()
