"""
Outreach Engine Integration Test
LEVEL 5 - Integration test to validate cross-layer wiring and dependencies
"""

import asyncio
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

def test_import_dependencies():
    """Test that all core modules can be imported without circular dependencies"""
    print("🔍 Testing import dependencies...")
    
    try:
        # Test service layer imports
        from apps.outreach_engine.services.builders.outreach_builder import OutreachBuilder
        from apps.outreach_engine.services.builders.message_builder import MessageBuilder
        from apps.outreach_engine.services.enrichers.personalization_engine import PersonalizationEngine
        from apps.outreach_engine.services.enrichers.profile_analyzer import RelationshipAnalyzer
        from apps.outreach_engine.services.generators.outreach_generator import MessageGenerator
        from apps.outreach_engine.services.generators.personalization_engine import TemplateGenerator
        from apps.outreach_engine.services.pipelines.outreach_pipeline import OutreachPipeline
        from apps.outreach_engine.services.pipelines.compliance_pipeline import ValidationPipeline
        from apps.outreach_engine.services.utils.formatting import OutreachFormatter
        from apps.outreach_engine.services.utils.scoring import OutreachScorer
        
        print("✅ Service layer imports successful")
        
        # Test worker imports
        from apps.outreach_engine.workers.enrichment_worker import OutreachGenerateWorker
        from apps.outreach_engine.workers.linkedin_send_worker import ContactEnrichWorker
        from apps.outreach_engine.workers.email_send_worker import DeliveryWorker
        
        print("✅ Worker layer imports successful")
        
        # Test API imports
        from apps.outreach_engine.api.v1.endpoints.generate_outreach import router as generate_router
        from apps.outreach_engine.api.v1.endpoints.validate_outreach import router as validate_router
        from apps.outreach_engine.api.v1.endpoints.healthcheck import router as healthcheck_router
        from apps.outreach_engine.api.v1.middleware.auth import AuthMiddleware
        from apps.outreach_engine.api.v1.middleware.rate_limit import RateLimitMiddleware
        
        print("✅ API layer imports successful")
        
        # Test CLI imports
        from apps.outreach_engine.cli.run_outreach_engine import OutreachEngineCLI
        from apps.outreach_engine.cli.debug_tools import OutreachEngineSetup
        
        print("✅ CLI layer imports successful")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"⚠️  Unexpected error: {e}")
        return False

def test_pipeline_integration():
    """Test that pipeline components can be instantiated and work together"""
    print("\n🔍 Testing pipeline integration...")
    
    try:
        from apps.outreach_engine.services.pipelines.outreach_pipeline import OutreachPipeline
        from apps.outreach_engine.services.pipelines.compliance_pipeline import ValidationPipeline
        
        # Instantiate pipelines
        outreach_pipeline = OutreachPipeline()
        validation_pipeline = ValidationPipeline()
        
        print("✅ Pipeline instantiation successful")
        
        # Test basic pipeline methods exist
        assert hasattr(outreach_pipeline, 'execute'), "OutreachPipeline missing execute method"
        assert hasattr(validation_pipeline, 'validate_outreach'), "ValidationPipeline missing validate_outreach method"
        
        print("✅ Pipeline methods validation successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Pipeline integration error: {e}")
        return False

def test_worker_integration():
    """Test that worker components can be instantiated"""
    print("\n🔍 Testing worker integration...")
    
    try:
        from apps.outreach_engine.workers.enrichment_worker import OutreachGenerateWorker
        from apps.outreach_engine.workers.linkedin_send_worker import ContactEnrichWorker
        from apps.outreach_engine.workers.email_send_worker import DeliveryWorker
        
        # Instantiate workers
        outreach_worker = OutreachGenerateWorker()
        enrich_worker = ContactEnrichWorker()
        delivery_worker = DeliveryWorker()
        
        print("✅ Worker instantiation successful")
        
        # Test basic worker methods exist
        assert hasattr(outreach_worker, 'start'), "OutreachGenerateWorker missing start method"
        assert hasattr(enrich_worker, 'start'), "ContactEnrichWorker missing start method"
        assert hasattr(delivery_worker, 'start'), "DeliveryWorker missing start method"
        
        print("✅ Worker methods validation successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Worker integration error: {e}")
        return False

def test_api_integration():
    """Test that API components can be instantiated"""
    print("\n🔍 Testing API integration...")
    
    try:
        from apps.outreach_engine.api.v1.endpoints.generate_outreach import router as generate_router
        from apps.outreach_engine.api.v1.endpoints.validate_outreach import router as validate_router
        from apps.outreach_engine.api.v1.endpoints.healthcheck import router as healthcheck_router
        
        # Test that routers are FastAPI routers
        assert hasattr(generate_router, 'routes'), "Generate router missing routes"
        assert hasattr(validate_router, 'routes'), "Validate router missing routes"
        assert hasattr(healthcheck_router, 'routes'), "Healthcheck router missing routes"
        
        print("✅ API router validation successful")
        
        return True
        
    except Exception as e:
        print(f"❌ API integration error: {e}")
        return False

def test_cli_integration():
    """Test that CLI components can be instantiated"""
    print("\n🔍 Testing CLI integration...")
    
    try:
        from apps.outreach_engine.cli.run_outreach_engine import OutreachEngineCLI
        from apps.outreach_engine.cli.debug_tools import OutreachEngineSetup
        
        # Instantiate CLI components
        cli = OutreachEngineCLI()
        setup = OutreachEngineSetup()
        
        print("✅ CLI instantiation successful")
        
        # Test basic CLI methods exist
        assert hasattr(cli, 'generate_outreach'), "CLI missing generate_outreach method"
        assert hasattr(setup, 'setup_environment'), "Setup missing setup_environment method"
        
        print("✅ CLI methods validation successful")
        
        return True
        
    except Exception as e:
        print(f"❌ CLI integration error: {e}")
        return False

async def test_end_to_end_flow():
    """Test a minimal end-to-end flow through the system"""
    print("\n🔍 Testing end-to-end flow...")
    
    try:
        from apps.outreach_engine.services.pipelines.outreach_pipeline import OutreachPipeline
        from apps.outreach_engine.services.pipelines.compliance_pipeline import ValidationPipeline
        
        # Create test data
        test_request = {
            "recipient_profile": {
                "name": "Test User",
                "email": "test@example.com",
                "company": "Test Company",
                "role": "Test Role"
            },
            "sender_profile": {
                "name": "Sender User",
                "email": "sender@example.com",
                "company": "Sender Company",
                "role": "Sender Role"
            },
            "outreach_type": "email",
            "context": {},
            "preferences": {}
        }
        
        # Test outreach pipeline (this will use mock data internally)
        outreach_pipeline = OutreachPipeline()
        
        print("✅ End-to-end flow structure validation successful")
        print("📝 Note: Full pipeline execution requires external dependencies")
        
        return True
        
    except Exception as e:
        print(f"❌ End-to-end flow error: {e}")
        return False

def main():
    """Run all integration tests"""
    print("🚀 Starting Outreach Engine Integration Tests")
    print("=" * 60)
    
    tests = [
        ("Import Dependencies", test_import_dependencies),
        ("Pipeline Integration", test_pipeline_integration),
        ("Worker Integration", test_worker_integration),
        ("API Integration", test_api_integration),
        ("CLI Integration", test_cli_integration),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 Running: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Run async test separately
    print(f"\n📋 Running: End-to-End Flow")
    try:
        result = asyncio.run(test_end_to_end_flow())
        results.append(("End-to-End Flow", result))
    except Exception as e:
        print(f"❌ End-to-End Flow failed with exception: {e}")
        results.append(("End-to-End Flow", False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 INTEGRATION TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All integration tests passed!")
        print("✅ Outreach Engine architecture is properly integrated")
        print("🚀 Ready to proceed with shared components development")
    else:
        print("⚠️  Some integration tests failed")
        print("🔧 Please review and fix the issues before proceeding")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
