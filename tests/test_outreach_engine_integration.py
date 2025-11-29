#!/usr/bin/env python3
"""
Integration Tests for Outreach Engine - Phase F LIC Capability Integration
Tests all 13 capability modules working together without deprecated hop-based logic
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from typing import Dict, Any
from outreach_engine import (
    # Core models
    Route, Archetype, ValidationResult, ValidationSeverity,
    
    # Main engines
    RoutingEngine, OutreachConfig, RAGPipelineV75, InsightsEngine,
    CTAEngine, ToneEngine, ConstraintEngine, ValidationEngine,
    TemplateEngine, KNodeAssemblyEngine, SeniorityEngine,
    
    # Schemas
    SenderProfile, RecipientProfile, JobDescription, MessageSchema
)

def load_lic_capabilities() -> Dict[str, Any]:
    """Load LIC capabilities from reconstructed_capabilities.py"""
    try:
        sys.path.append(os.path.join(os.path.dirname(__file__), 'LIC_capabilities'))
        from reconstructed_capabilities import LIC_CAPABILITIES
        return LIC_CAPABILITIES
    except ImportError as e:
        print(f"Warning: Could not load LIC capabilities: {e}")
        # Return minimal test configuration
        return {
            "routing_rules": {
                "CONNECTION_REQ": {
                    "conditions": {"connection_status": "not_connected"},
                    "constraints": {"char_limit": 300, "word_range": [50, 100]}
                }
            },
            "parameter_presets": {
                "context_manager": {"max_tokens": 8000},
                "adaptive_temperature_controller": {"base_temperatures": {"EXECUTIVE": 0.7}},
                "tool_call_budget": {"minimum": 0, "maximum": 20}
            },
            "scenario_rules": {
                "rag_pipeline_v75": {
                    "stage_0_hyde": {"enabled": True},
                    "stage_1_hybrid_recall": {"web_search_calls": 6},
                    "stage_2_cross_encoder_reranking": {"threshold": 0.75}
                }
            },
            "insight_patterns": {
                "signal_quality_scorer": {"source_weights": {"web": 1.0}},
                "claim_confidence_scorer": {"per_claim_minimum": 0.8}
            },
            "cta_patterns": {
                "archetype_specific": {"EXECUTIVE": {"example": "Would you be open to a brief chat?"}},
                "date_window_engine": {"business_day_rules": {"window_size_days": 2}}
            },
            "tone_rules": {
                "archetype_tone_mappings": {"EXECUTIVE": {"message_tone": "professional"}}
            },
            "constraints": {
                "content_cleanliness": {"forbidden_verbs": ["spearheaded"], "max_violations": 1},
                "ascii_hygiene": {"replacements": {"\\u2019": "'"}},
                "structural_validation": {"word_count_tolerance": 0.1}
            },
            "message_templates": {
                "greeting_templates": {"CONNECTION_REQ": {"template": "Hi {first_name},"}},
                "cta_templates": {"CONNECTION_REQ": {"template": "Would you be open to a call?"}},
                "signature_templates": {"standard": {"template": "Best regards,\n{name}"}}
            },
            "seniority_rules": {
                "recipient_classifier_taxonomy": {
                    "types": ["EXECUTIVE", "C_LEVEL", "SENIOR_TA", "RECRUITER"]
                }
            }
        }

def test_core_imports():
    """Test that all core modules can be imported"""
    print("Testing core imports...")
    
    try:
        from outreach_engine.models import Route, Archetype, ValidationResult
        from outreach_engine.routing import RoutingEngine
        from outreach_engine.config import OutreachConfig
        from outreach_engine.rag import RAGPipelineV75
        from outreach_engine.insights import InsightsEngine
        from outreach_engine.cta import CTAEngine
        from outreach_engine.tone import ToneEngine
        from outreach_engine.constraints import ConstraintEngine
        from outreach_engine.validation import ValidationEngine
        from outreach_engine.templates import TemplateEngine
        from outreach_engine.assembly import KNodeAssemblyEngine
        from outreach_engine.seniority import SeniorityEngine
        from outreach_engine.schemas import SenderProfile, RecipientProfile, MessageSchema
        
        print("✓ All core modules imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_engine_initialization():
    """Test that all engines can be initialized with LIC capabilities"""
    print("Testing engine initialization...")
    
    lic_capabilities = load_lic_capabilities()
    
    try:
        # Initialize all engines
        routing_engine = RoutingEngine(lic_capabilities.get("routing_rules", {}))
        config_engine = OutreachConfig(lic_capabilities)
        rag_engine = RAGPipelineV75(lic_capabilities)
        insights_engine = InsightsEngine(lic_capabilities)
        cta_engine = CTAEngine(lic_capabilities)
        tone_engine = ToneEngine(lic_capabilities)
        constraint_engine = ConstraintEngine(lic_capabilities)
        validation_engine = ValidationEngine(lic_capabilities)
        template_engine = TemplateEngine(lic_capabilities)
        assembly_engine = KNodeAssemblyEngine(lic_capabilities)
        seniority_engine = SeniorityEngine(lic_capabilities)
        
        print("✓ All engines initialized successfully")
        return True, {
            "routing_engine": routing_engine,
            "config_engine": config_engine,
            "rag_engine": rag_engine,
            "insights_engine": insights_engine,
            "cta_engine": cta_engine,
            "tone_engine": tone_engine,
            "constraint_engine": constraint_engine,
            "validation_engine": validation_engine,
            "template_engine": template_engine,
            "assembly_engine": assembly_engine,
            "seniority_engine": seniority_engine
        }
    except Exception as e:
        print(f"✗ Engine initialization error: {e}")
        return False, {}

def test_routing_workflow():
    """Test routing workflow"""
    print("Testing routing workflow...")
    
    lic_capabilities = load_lic_capabilities()
    routing_engine = RoutingEngine(lic_capabilities.get("routing_rules", {}))
    
    # Test data
    recipient_profile = {
        "name": "John Smith",
        "title": "Engineering Manager",
        "company": "Tech Corp",
        "connection_status": "not_connected"
    }
    
    sender_profile = {
        "name": "Jane Doe",
        "title": "Senior Software Engineer",
        "company": "Startup Inc"
    }
    
    try:
        # Test route determination
        route = routing_engine.determine_route(recipient_profile, [])
        print(f"✓ Route determined: {route.value}")
        
        # Test message context creation
        context = routing_engine.create_message_context(sender_profile, recipient_profile)
        print(f"✓ Message context created with route: {context.route.value}, archetype: {context.archetype.value}")
        
        return True
    except Exception as e:
        print(f"✗ Routing workflow error: {e}")
        return False

def test_seniority_classification():
    """Test seniority classification"""
    print("Testing seniority classification...")
    
    lic_capabilities = load_lic_capabilities()
    seniority_engine = SeniorityEngine(lic_capabilities)
    
    # Test recipients
    test_recipients = [
        {"name": "CEO", "title": "Chief Executive Officer", "company": "Big Corp"},
        {"name": "Director", "title": "Director of Engineering", "company": "Tech Co"},
        {"name": "Engineer", "title": "Senior Software Engineer", "company": "Startup"},
        {"name": "Recruiter", "title": "Technical Recruiter", "company": "Hiring Inc"}
    ]
    
    try:
        for recipient in test_recipients:
            classification, analysis, validations = seniority_engine.analyze_recipient_seniority(recipient)
            print(f"✓ {recipient['title']} -> {classification.recipient_type} (confidence: {classification.confidence:.2f})")
        
        return True
    except Exception as e:
        print(f"✗ Seniority classification error: {e}")
        return False

def test_template_generation():
    """Test template generation"""
    print("Testing template generation...")
    
    lic_capabilities = load_lic_capabilities()
    template_engine = TemplateEngine(lic_capabilities)
    
    try:
        # Test component assembly
        components = template_engine.assemble_template_components(
            route=Route.CONNECTION_REQ,
            archetype=Archetype.EXECUTIVE,
            sender_profile={"name": "Jane Doe"},
            recipient_profile={"name": "John Smith"},
            context={"topic": "engineering opportunities"}
        )
        
        print(f"✓ Greeting: {components['greeting']}")
        print(f"✓ CTA: {components['cta']}")
        print(f"✓ Signature: {components['signature']}")
        
        return True
    except Exception as e:
        print(f"✗ Template generation error: {e}")
        return False

def test_constraint_validation():
    """Test constraint validation"""
    print("Testing constraint validation...")
    
    lic_capabilities = load_lic_capabilities()
    constraint_engine = ConstraintEngine(lic_capabilities)
    
    # Test route constraints
    from outreach_engine.models import RouteConstraints
    constraints = RouteConstraints(
        char_limit=300,
        word_range=[50, 100],
        signature_format="standard",
        subject_line_enabled=False,
        attachments_enabled=False,
        cta_format="standard",
        cta_max_words=20,
        greeting_format="Hi {first_name},"
    )
    
    test_messages = [
        "This is a clean message without forbidden verbs.",
        "I spearheaded the initiative to improve processes."  # Contains forbidden verb
    ]
    
    try:
        for i, message in enumerate(test_messages):
            validations = constraint_engine.validate_message(message, constraints)
            failed_count = sum(1 for v in validations if not v.passed)
            print(f"✓ Message {i+1}: {len(validations)} validations, {failed_count} failed")
        
        return True
    except Exception as e:
        print(f"✗ Constraint validation error: {e}")
        return False

def test_rag_pipeline():
    """Test RAG pipeline"""
    print("Testing RAG pipeline...")
    
    lic_capabilities = load_lic_capabilities()
    rag_engine = RAGPipelineV75(lic_capabilities)
    
    # Test data
    recipient_profile = {
        "name": "John Smith",
        "title": "Engineering Manager",
        "company": "Tech Corp",
        "about": "Short about section"
    }
    
    sender_profile = {
        "name": "Jane Doe",
        "current_company": "Startup Inc"
    }
    
    try:
        rag_result, validations = rag_engine.execute_rag_pipeline(
            recipient_profile=recipient_profile,
            sender_profile=sender_profile,
            route="CONNECTION_REQ"
        )
        
        print(f"✓ RAG pipeline executed: {len(rag_result.evidence)} evidence items")
        print(f"✓ Confidence score: {rag_result.confidence_score:.3f}")
        print(f"✓ Processing time: {rag_result.processing_time_ms}ms")
        
        return True
    except Exception as e:
        print(f"✗ RAG pipeline error: {e}")
        return False

def test_end_to_end_workflow():
    """Test complete end-to-end workflow"""
    print("Testing end-to-end workflow...")
    
    lic_capabilities = load_lic_capabilities()
    
    # Initialize all engines
    try:
        routing_engine = RoutingEngine(lic_capabilities.get("routing_rules", {}))
        seniority_engine = SeniorityEngine(lic_capabilities)
        template_engine = TemplateEngine(lic_capabilities)
        constraint_engine = ConstraintEngine(lic_capabilities)
        assembly_engine = KNodeAssemblyEngine(lic_capabilities)
        
        # Test data
        sender_profile = {
            "name": "Jane Doe",
            "title": "Senior Software Engineer", 
            "company": "Startup Inc",
            "current_company": "Startup Inc"
        }
        
        recipient_profile = {
            "name": "John Smith",
            "title": "Engineering Manager",
            "company": "Tech Corp",
            "connection_status": "not_connected"
        }
        
        # Step 1: Seniority classification
        classification, analysis, seniority_validations = seniority_engine.analyze_recipient_seniority(recipient_profile)
        
        # Step 2: Route determination
        route = routing_engine.determine_route(recipient_profile, [])
        
        # Step 3: Template generation
        components = template_engine.assemble_template_components(
            route=route,
            archetype=Archetype(classification.recipient_type),
            sender_profile=sender_profile,
            recipient_profile=recipient_profile,
            context={}
        )
        
        # Step 4: Message assembly
        assembly, assembly_validations = assembly_engine.execute_k_node_assembly(
            route=route,
            archetype=Archetype(classification.recipient_type),
            components=components,
            sender_profile=sender_profile,
            recipient_profile=recipient_profile
        )
        
        # Step 5: Final validation
        formatted_message = assembly_engine.message_assembler.format_assembled_message(assembly, route)
        
        print(f"✓ End-to-end workflow completed")
        print(f"✓ Route: {route.value}")
        print(f"✓ Archetype: {classification.recipient_type}")
        print(f"✓ Message length: {len(formatted_message)} characters")
        
        return True
        
    except Exception as e:
        print(f"✗ End-to-end workflow error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all integration tests"""
    print("=" * 60)
    print("OUTREACH ENGINE INTEGRATION TESTS")
    print("Phase F: LIC Capability Integration")
    print("=" * 60)
    
    tests = [
        ("Core Imports", test_core_imports),
        ("Engine Initialization", test_engine_initialization),
        ("Routing Workflow", test_routing_workflow),
        ("Seniority Classification", test_seniority_classification),
        ("Template Generation", test_template_generation),
        ("Constraint Validation", test_constraint_validation),
        ("RAG Pipeline", test_rag_pipeline),
        ("End-to-End Workflow", test_end_to_end_workflow)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            result = test_func()
            if isinstance(result, tuple):
                success, _ = result
            else:
                success = result
            
            if success:
                passed += 1
                print(f"✓ {test_name} PASSED")
            else:
                print(f"✗ {test_name} FAILED")
        except Exception as e:
            print(f"✗ {test_name} ERROR: {e}")
    
    print("\n" + "=" * 60)
    print(f"TEST RESULTS: {passed}/{total} tests passed")
    print("=" * 60)
    
    if passed == total:
        print("🎉 ALL INTEGRATION TESTS PASSED!")
        print("Outreach Engine is ready for use.")
    else:
        print("⚠️  Some tests failed. Please review the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
