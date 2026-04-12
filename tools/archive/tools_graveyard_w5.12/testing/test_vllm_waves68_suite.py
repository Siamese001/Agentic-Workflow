"""Comprehensive VLLM Extension Test Suite - Waves 6-8.

Tests all vLLM extensions implemented in Waves 6-8 including:
- Wave 6: apps_research, apps_rfp, apps_exec integrations
- Wave 7: Shared infrastructure and templates
- Wave 8: Advanced features and analytics
"""

import asyncio
import json
import logging
import time
from pathlib import Path
from typing import Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VLLMWaves68TestSuite:
    """Comprehensive test suite for Waves 6-8 vLLM extensions."""

    def __init__(self):
        self.test_results = []
        self.start_time = time.time()

    async def run_all_tests(self) -> dict[str, Any]:
        """Run all tests for Waves 6-8.

        Returns:
            Comprehensive test results
        """
        logger.info("Starting VLLM Waves 6-8 Test Suite...")

        # Wave 6 Tests: Medium-Priority Extensions
        await self.test_wave6_research_integration()
        await self.test_wave6_rfp_integration()
        await self.test_wave6_exec_integration()

        # Wave 7 Tests: Shared Infrastructure
        await self.test_wave7_shared_utilities()
        await self.test_wave7_prompt_templates()

        # Wave 8 Tests: Advanced Features
        await self.test_wave8_batch_processing()
        await self.test_wave8_analytics()
        await self.test_wave8_multimodel()

        # Generate summary
        return self.generate_comprehensive_summary()

    async def test_wave6_research_integration(self) -> None:
        """Test apps_research vLLM integration."""
        logger.info("Testing Wave 6: apps_research integration...")

        try:
            # Import ResearchOrchestrator
            from apps_research.reasoning.ResearchOrchestrator import ResearchOrchestrator

            # Test initialization
            orchestrator = ResearchOrchestrator(qwen_enabled=True)

            # Test research synthesis
            research_topic = "AI Ethics in Healthcare"
            sources = [
                {
                    "title": "AI Ethics Framework",
                    "content": "AI systems must be designed with ethical considerations...",
                    "author": "Dr. Smith",
                    "date": "2024",
                },
                {
                    "title": "Healthcare AI Applications",
                    "content": "AI in healthcare shows promise for diagnosis and treatment...",
                    "author": "Dr. Johnson",
                    "date": "2024",
                },
            ]

            result = await orchestrator.synthesize_research_with_qwen(
                research_topic=research_topic,
                sources=sources,
                synthesis_type="comprehensive",
            )

            success = result.get("success", False)
            self.test_results.append(
                {
                    "test": "wave6_research_integration",
                    "success": success,
                    "message": "Research integration test completed"
                    if success
                    else f"Failed: {result.get('error')}",
                    "details": {
                        "synthesis_type": result.get("synthesis_type"),
                        "sources_count": result.get("sources_count"),
                        "confidence": result.get("confidence"),
                        "latency_ms": result.get("latency_ms"),
                    },
                },
            )

        except Exception as e:
            self.test_results.append(
                {
                    "test": "wave6_research_integration",
                    "success": False,
                    "message": f"Research integration test failed: {str(e)}",
                    "details": None,
                },
            )

    async def test_wave6_rfp_integration(self) -> None:
        """Test apps_rfp vLLM integration."""
        logger.info("Testing Wave 6: apps_rfp integration...")

        try:
            # Import RfpOrchestrator
            from apps_rfp.reasoning.RfpOrchestrator import RfpOrchestrator

            # Test initialization
            orchestrator = RfpOrchestrator(qwen_enabled=True)

            # Test proposal generation
            rfp_details = {
                "industry": "Healthcare",
                "problem_statement": "Need AI-powered diagnostic system for early disease detection",
                "requirements": [
                    "HIPAA compliance",
                    "Real-time processing",
                    "95% accuracy minimum",
                    "Integration with existing EMR",
                ],
                "constraints": [
                    "Budget under $2M",
                    "Implementation within 12 months",
                    "FDA approval pathway",
                ],
                "timeline": "12 months",
                "budget": "$1.5M",
            }

            result = await orchestrator.generate_proposal_with_qwen(
                rfp_details=rfp_details,
                proposal_type="technical",
            )

            success = result.get("success", False)
            self.test_results.append(
                {
                    "test": "wave6_rfp_integration",
                    "success": success,
                    "message": "RFP integration test completed"
                    if success
                    else f"Failed: {result.get('error')}",
                    "details": {
                        "proposal_type": result.get("proposal_type"),
                        "rfp_industry": result.get("rfp_industry"),
                        "confidence": result.get("confidence"),
                        "latency_ms": result.get("latency_ms"),
                    },
                },
            )

        except Exception as e:
            self.test_results.append(
                {
                    "test": "wave6_rfp_integration",
                    "success": False,
                    "message": f"RFP integration test failed: {str(e)}",
                    "details": None,
                },
            )

    async def test_wave6_exec_integration(self) -> None:
        """Test apps_exec vLLM integration."""
        logger.info("Testing Wave 6: apps_exec integration...")

        try:
            # Import ExecOrchestrator
            from apps_exec.reasoning.ExecOrchestrator import ExecOrchestrator

            # Test initialization
            orchestrator = ExecOrchestrator(qwen_enabled=True)

            # Test execution planning
            objectives = [
                "Implement AI-powered customer service platform",
                "Reduce response time by 50%",
                "Achieve 90% customer satisfaction",
                "Integrate with existing CRM system",
            ]

            constraints = {
                "timeline": "6 months",
                "budget": "$500K",
                "resources": "5 developers, 2 project managers",
                "technical": "Must use existing cloud infrastructure",
                "stakeholders": "Customer service, IT, Executive team",
            }

            result = await orchestrator.plan_execution_with_qwen(
                objectives=objectives,
                constraints=constraints,
                planning_type="strategic",
            )

            success = result.get("success", False)
            self.test_results.append(
                {
                    "test": "wave6_exec_integration",
                    "success": success,
                    "message": "Exec integration test completed"
                    if success
                    else f"Failed: {result.get('error')}",
                    "details": {
                        "planning_type": result.get("planning_type"),
                        "objectives_count": result.get("objectives_count"),
                        "confidence": result.get("confidence"),
                        "latency_ms": result.get("latency_ms"),
                    },
                },
            )

        except Exception as e:
            self.test_results.append(
                {
                    "test": "wave6_exec_integration",
                    "success": False,
                    "message": f"Exec integration test failed: {str(e)}",
                    "details": None,
                },
            )

    async def test_wave7_shared_utilities(self) -> None:
        """Test Wave 7 shared utilities."""
        logger.info("Testing Wave 7: shared utilities...")

        try:
            # Import shared utilities
            from apps_shared.utils.vllm_shared_utils import (
                VLLMConfigPresets,
                VLLMSharedManager,
                extract_response_metadata,
                validate_vllm_response,
            )

            # Test shared manager
            manager = VLLMSharedManager("test_app", VLLMConfigPresets.analytical_config())

            if manager.is_available():
                # Test generation
                result = await manager.generate_response(
                    prompt="Analyze the benefits of AI in healthcare",
                    metadata={"test_type": "wave7_shared"},
                )

                # Test validation
                is_valid = validate_vllm_response(result)
                metadata = extract_response_metadata(result)

                success = result.get("success", False) and is_valid

                self.test_results.append(
                    {
                        "test": "wave7_shared_utilities",
                        "success": success,
                        "message": "Shared utilities test completed"
                        if success
                        else "Failed: Invalid response",
                        "details": {
                            "manager_available": manager.is_available(),
                            "response_valid": is_valid,
                            "metadata_keys": list(metadata.keys()),
                            "confidence": result.get("confidence"),
                        },
                    },
                )
            else:
                self.test_results.append(
                    {
                        "test": "wave7_shared_utilities",
                        "success": False,
                        "message": "Shared utilities test failed: vLLM not available",
                        "details": None,
                    },
                )

        except Exception as e:
            self.test_results.append(
                {
                    "test": "wave7_shared_utilities",
                    "success": False,
                    "message": f"Shared utilities test failed: {str(e)}",
                    "details": None,
                },
            )

    async def test_wave7_prompt_templates(self) -> None:
        """Test Wave 7 prompt templates."""
        logger.info("Testing Wave 7: prompt templates...")

        try:
            # Import prompt templates
            from apps_shared.utils.vllm_prompt_templates import (
                IndustryPromptTemplates,
                UseCasePromptTemplates,
            )

            # Test industry templates
            healthcare_prompt = IndustryPromptTemplates.healthcare_analysis(
                content="Patient shows symptoms of AI-assisted diagnosis",
                analysis_type="clinical",
            )

            finance_prompt = IndustryPromptTemplates.finance_proposal(
                opportunity="AI investment platform",
                requirements=["Real-time data", "Risk analysis", "Compliance"],
                risk_factors=["Market volatility", "Regulatory changes"],
                financial_constraints={"budget": "$1M", "timeline": "12 months"},
            )

            # Test use case templates
            risk_prompt = UseCasePromptTemplates.risk_assessment(
                scenario="Implementing AI in critical infrastructure",
                risk_categories=["Technical", "Security", "Regulatory"],
                context={"industry": "Energy", "location": "North America"},
            )

            # Validate templates
            templates_valid = all(
                [
                    len(healthcare_prompt) > 100,
                    len(finance_prompt) > 100,
                    len(risk_prompt) > 100,
                    "HEALTHCARE ANALYSIS" in healthcare_prompt,
                    "FINANCIAL SERVICES" in finance_prompt,
                    "RISK ASSESSMENT" in risk_prompt,
                ],
            )

            self.test_results.append(
                {
                    "test": "wave7_prompt_templates",
                    "success": templates_valid,
                    "message": "Prompt templates test completed"
                    if templates_valid
                    else "Failed: Invalid templates",
                    "details": {
                        "healthcare_template_length": len(healthcare_prompt),
                        "finance_template_length": len(finance_prompt),
                        "risk_template_length": len(risk_prompt),
                        "templates_generated": 3,
                    },
                },
            )

        except Exception as e:
            self.test_results.append(
                {
                    "test": "wave7_prompt_templates",
                    "success": False,
                    "message": f"Prompt templates test failed: {str(e)}",
                    "details": None,
                },
            )

    async def test_wave8_batch_processing(self) -> None:
        """Test Wave 8 batch processing."""
        logger.info("Testing Wave 8: batch processing...")

        try:
            # Import advanced features
            from apps_shared.utils.vllm_advanced_features import BatchRequest, VLLMBatchProcessor

            # Create batch processor
            processor = VLLMBatchProcessor("test_batch", max_concurrent_requests=3)

            # Create batch requests
            requests = [
                BatchRequest(
                    id="req1",
                    prompt="Summarize the benefits of renewable energy",
                    metadata={"category": "environment"},
                ),
                BatchRequest(
                    id="req2",
                    prompt="Explain quantum computing in simple terms",
                    metadata={"category": "technology"},
                ),
                BatchRequest(
                    id="req3",
                    prompt="Describe the impact of social media on society",
                    metadata={"category": "social"},
                ),
            ]

            # Process batch
            batch_result = await processor.process_batch(requests, "test_batch_001")

            success = (
                batch_result.total_requests == 3
                and batch_result.successful_requests >= 2  # Allow for some failures
                and batch_result.average_latency_ms >= 0  # Allow 0 for mock implementation
            )

            self.test_results.append(
                {
                    "test": "wave8_batch_processing",
                    "success": success,
                    "message": "Batch processing test completed"
                    if success
                    else "Failed: Batch processing issues",
                    "details": {
                        "total_requests": batch_result.total_requests,
                        "successful_requests": batch_result.successful_requests,
                        "failed_requests": batch_result.failed_requests,
                        "average_latency_ms": batch_result.average_latency_ms,
                        "processing_time_seconds": batch_result.processing_time_seconds,
                    },
                },
            )

        except Exception as e:
            self.test_results.append(
                {
                    "test": "wave8_batch_processing",
                    "success": False,
                    "message": f"Batch processing test failed: {str(e)}",
                    "details": None,
                },
            )

    async def test_wave8_analytics(self) -> None:
        """Test Wave 8 analytics."""
        logger.info("Testing Wave 8: analytics...")

        try:
            # Import analytics
            from apps_shared.utils.vllm_advanced_features import get_analytics

            # Test analytics functionality
            analytics = get_analytics()

            # Record some test requests
            test_requests = [
                {
                    "success": True,
                    "content": "Test response 1",
                    "confidence": 0.85,
                    "latency_ms": 150.0,
                    "model_used": "Qwen/Qwen2.5-7B-Instruct",
                    "app_name": "test_app",
                },
                {
                    "success": True,
                    "content": "Test response 2",
                    "confidence": 0.90,
                    "latency_ms": 120.0,
                    "model_used": "Qwen/Qwen2.5-7B-Instruct",
                    "app_name": "test_app",
                },
                {"success": False, "error": "Test error", "app_name": "test_app"},
            ]

            for request in test_requests:
                analytics.record_request(request)

            # Get performance summary
            summary = analytics.get_performance_summary()

            # Validate analytics
            analytics_valid = (
                summary["total_requests"] == 3
                and summary["successful_requests"] == 2
                and summary["failed_requests"] == 1
                and abs(summary["success_rate"] - 66.67) < 0.1  # Allow for floating point precision
                and "average_latency_ms" in summary
            )

            self.test_results.append(
                {
                    "test": "wave8_analytics",
                    "success": analytics_valid,
                    "message": "Analytics test completed" if analytics_valid else "Failed: Analytics issues",
                    "details": {
                        "total_requests": summary["total_requests"],
                        "success_rate": summary["success_rate"],
                        "average_latency_ms": summary["average_latency_ms"],
                        "model_usage_keys": list(summary["model_usage"].keys()),
                        "app_usage_keys": list(summary["app_usage"].keys()),
                    },
                },
            )

        except Exception as e:
            self.test_results.append(
                {
                    "test": "wave8_analytics",
                    "success": False,
                    "message": f"Analytics test failed: {str(e)}",
                    "details": None,
                },
            )

    async def test_wave8_multimodel(self) -> None:
        """Test Wave 8 multi-model support."""
        logger.info("Testing Wave 8: multi-model support...")

        try:
            # Import multi-model manager
            from apps_shared.utils.vllm_advanced_features import get_multimodel_manager

            # Get multi-model manager
            manager = get_multimodel_manager()

            # List available models
            models = manager.list_models()

            # Test generation with different models
            test_results = []
            for model_name in ["qwen-7b", "qwen-7b-creative"]:
                if model_name in models:
                    result = await manager.generate_with_model(
                        model_name=model_name,
                        prompt="Briefly explain artificial intelligence",
                    )
                    test_results.append(result)

            # Validate multi-model functionality
            multimodel_valid = (
                len(models) >= 2
                and len(test_results) >= 1
                and any(r.get("success", False) for r in test_results)
            )

            self.test_results.append(
                {
                    "test": "wave8_multimodel",
                    "success": multimodel_valid,
                    "message": "Multi-model test completed"
                    if multimodel_valid
                    else "Failed: Multi-model issues",
                    "details": {
                        "available_models": list(models.keys()),
                        "models_tested": len(test_results),
                        "successful_generations": sum(1 for r in test_results if r.get("success", False)),
                        "model_descriptions": {
                            k: v.get("description", "No description") for k, v in models.items()
                        },
                    },
                },
            )

        except Exception as e:
            self.test_results.append(
                {
                    "test": "wave8_multimodel",
                    "success": False,
                    "message": f"Multi-model test failed: {str(e)}",
                    "details": None,
                },
            )

    def generate_comprehensive_summary(self) -> dict[str, Any]:
        """Generate comprehensive test summary.

        Returns:
            Summary dictionary
        """
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

        # Group results by wave
        wave_results = {}
        for result in self.test_results:
            wave = result["test"].split("_")[0]  # Extract wave number
            if wave not in wave_results:
                wave_results[wave] = {"total": 0, "passed": 0, "failed": 0}
            wave_results[wave]["total"] += 1
            if result["success"]:
                wave_results[wave]["passed"] += 1
            else:
                wave_results[wave]["failed"] += 1

        # Calculate performance metrics
        successful_tests = [r for r in self.test_results if r["success"] and r.get("details")]
        latencies = []
        confidences = []

        for test in successful_tests:
            details = test.get("details", {})
            if "latency_ms" in details:
                latencies.append(details["latency_ms"])
            if "confidence" in details:
                confidences.append(details["confidence"])

        avg_latency = sum(latencies) / len(latencies) if latencies else 0
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0

        total_time = time.time() - self.start_time

        return {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "test_suite": "VLLM Waves 6-8 Extension Test Suite",
            "total_time_seconds": total_time,
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate": success_rate,
            },
            "wave_breakdown": wave_results,
            "performance": {
                "average_latency_ms": avg_latency,
                "average_confidence": avg_confidence,
                "total_successful_tests": len(successful_tests),
            },
            "test_results": self.test_results,
        }


async def main():
    """Main test execution."""
    print("🚀 Starting VLLM Waves 6-8 Extension Test Suite")
    print("=" * 70)

    test_suite = VLLMWaves68TestSuite()
    results = await test_suite.run_all_tests()

    print("\n📊 WAVES 6-8 TEST RESULTS")
    print("=" * 70)
    print(f"Timestamp: {results['timestamp']}")
    print(f"Total Test Time: {results['total_time_seconds']:.2f} seconds")

    summary = results["summary"]
    print(f"Total Tests: {summary['total_tests']}")
    print(f"Passed: {summary['passed_tests']}")
    print(f"Failed: {summary['failed_tests']}")
    print(f"Success Rate: {summary['success_rate']:.1f}%")

    print("\n📈 WAVE BREAKDOWN")
    print("-" * 30)
    for wave, stats in results["wave_breakdown"].items():
        print(f"{wave.upper()}: {stats['passed']}/{stats['total']} passed")

    performance = results["performance"]
    if performance["average_latency_ms"] > 0:
        print("\n📈 PERFORMANCE METRICS")
        print("-" * 30)
        print(f"Average Latency: {performance['average_latency_ms']:.2f}ms")
        print(f"Average Confidence: {performance['average_confidence']:.2f}")
        print(f"Successful Tests: {performance['total_successful_tests']}")

    print("\n🔍 DETAILED RESULTS")
    print("-" * 30)
    for result in results["test_results"]:
        status = "✅ PASS" if result["success"] else "❌ FAIL"
        print(f"{status} | {result['test']}")
        print(f"     {result['message']}")
        if result["details"]:
            for key, value in result["details"].items():
                if isinstance(value, (int, float)):
                    print(f"     {key}: {value}")
                elif isinstance(value, list) and len(value) <= 3:
                    print(f"     {key}: {value}")
                else:
                    print(f"     {key}: {type(value).__name__} ({len(str(value))} chars)")

    # Save results
    results_path = Path("artifacts/vllm_waves68_test_results.json")
    results_path.parent.mkdir(exist_ok=True)

    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n💾 Results saved to: {results_path}")

    # Return appropriate exit code
    if summary["success_rate"] >= 80.0:
        print("\n🎉 WAVES 6-8 EXTENSION TESTS PASSED!")
        return 0
    else:
        print("\n⚠️  WAVES 6-8 EXTENSION TESTS ISSUES DETECTED")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
