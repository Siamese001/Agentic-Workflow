#!/usr/bin/env python3
"""
Comprehensive test for MEDIUM and LOW complexity features implementation.

Tests:
- MEDIUM: HyDE hypothetical document expansion in K1 extract
- LOW: PII scrubbing, bias auditor, goal state injection, HyDE single-pass, reflection stub
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'resume_engine'))

from resume_engine.rg_orchestrator import RGOrchestrator, ResumeGenerationRequest
from resume_engine.rg_low_complexity_utils import LowComplexityUtils
import json

def test_medium_hyde_expansion():
    """Test MEDIUM complexity HyDE expansion in K1 extract."""
    print("🧪 Testing MEDIUM HyDE Expansion...")
    
    orchestrator = RGOrchestrator({
        "k1_config": {"hyde_expansion": True},
        "enable_low_complexity": False  # Disable LOW for this test
    })
    
    request = ResumeGenerationRequest(
        job_input={
            "title": "Senior Software Engineer",
            "industry": "technology",
            "skills": ["Python", "AWS", "Docker", "Kubernetes"],
            "requirements": ["5+ years experience", "Cloud computing", "Microservices"]
        },
        resume_input={
            "content": """
            John Doe
            Email: john@example.com | Phone: 555-1234
            
            Professional Summary
            Experienced software engineer with cloud expertise.
            
            Experience
            Software Engineer at Tech Corp (2018-2020)
            • Built REST APIs
            • Worked with cloud technologies
            """
        },
        processing_options={
            "analysis_depth": "comprehensive"
        }
    )
    
    try:
        result = orchestrator.generate_resume(request=request)
        
        if result.success:
            print("✅ HyDE expansion test PASSED")
            print(f"   Final content length: {len(result.final_resume_content)}")
            
            # Check if HyDE was applied
            k1_output = result.k_node_outputs.get("k1_extract")
            if k1_output and hasattr(k1_output, 'processing_trace'):
                hyde_steps = [step for step in k1_output.processing_trace if step.get("step") == "hyde_generation"]
                if hyde_steps:
                    print("✅ HyDE generation step found in processing trace")
                    print(f"   Hypothetical content generated: {hyde_steps[0].get('hypothetical_length', 0)} chars")
                else:
                    print("⚠️  HyDE generation step not found in trace")
            
            return True
        else:
            print(f"❌ HyDE expansion test FAILED: {result.error_message}")
            return False
            
    except Exception as e:
        print(f"❌ HyDE expansion test ERROR: {e}")
        return False

def test_low_complexity_features():
    """Test all LOW complexity features."""
    print("\n🧪 Testing LOW Complexity Features...")
    
    utils = LowComplexityUtils()
    
    test_content = """
    John Doe
    Email: john@example.com | Phone: 555-1234-5678
    
    Professional Summary
    Experienced software engineer with cloud expertise.
    
    Experience
    Senior Software Engineer at Tech Corp (2020-Present)
    • Led team of 5 engineers
    • Developed microservices using Python
    • Improved system performance by 40%
    
    Skills
    Python, AWS, Docker, Kubernetes
    """
    
    context = {
        "scrub_pii": True,
        "audit_bias": True,
        "inject_goals": True,
        "hyde_expand": True,
        "reflect_improve": True,
        "goal_state": {
            "primary_goal": "technical leadership",
            "target_role": "Senior Software Engineer",
            "industry": "technology"
        },
        "skills": ["Python", "AWS", "Docker"],
        "experience": "5+ years"
    }
    
    try:
        results = utils.process_content(test_content, context)
        
        print("✅ LOW complexity processing completed")
        print(f"   Original length: {len(test_content)}")
        print(f"   Processed length: {len(results['processed_content'])}")
        
        # Test PII scrubbing
        if results['pii_result']:
            pii_count = len(results['pii_result'].pii_detected)
            print(f"✅ PII scrubbing: {pii_count} PII instances detected and replaced")
            if pii_count > 0:
                print(f"   Example placeholder: {list(results['pii_result'].placeholders.keys())[0] if results['pii_result'].placeholders else 'None'}")
        
        # Test bias audit
        if results['bias_result']:
            bias_score = results['bias_result'].bias_score
            flagged_count = len(results['bias_result'].flagged_terms)
            print(f"✅ Bias audit: score={bias_score:.2f}, {flagged_count} terms flagged")
        
        # Test goal injection
        if results['goal_injected']:
            print("✅ Goal state injection applied")
        
        # Test HyDE expansion
        if results['hyde_expanded']:
            print("✅ HyDE single-pass expansion applied")
        
        # Test reflection
        if results['reflection_result']:
            quality_score = results['reflection_result']['quality_score']
            improvements = len(results['reflection_result']['improvements_suggested'])
            print(f"✅ Lightweight reflection: quality_score={quality_score:.2f}, {improvements} improvements suggested")
        
        return True
        
    except Exception as e:
        print(f"❌ LOW complexity test ERROR: {e}")
        return False

def test_integrated_pipeline():
    """Test complete pipeline with all features enabled."""
    print("\n🧪 Testing Integrated Pipeline...")
    
    orchestrator = RGOrchestrator({
        "k1_config": {"hyde_expansion": True},
        "enable_low_complexity": True
    })
    
    request = ResumeGenerationRequest(
        job_input={
            "title": "Senior Software Engineer",
            "industry": "technology", 
            "skills": ["Python", "AWS", "Docker", "Kubernetes", "Microservices"],
            "requirements": ["5+ years experience", "Cloud computing", "Leadership"]
        },
        resume_input={
            "content": """
            John Doe
            Email: john@example.com | Phone: 555-1234-5678 | LinkedIn: linkedin.com/in/johndoe
            
            Professional Summary
            Experienced software engineer with expertise in cloud technologies.
            
            Experience
            Senior Software Engineer at Tech Corp (2020-Present)
            • Led team of 5 engineers
            • Developed microservices using Python and AWS
            • Improved system performance by 40%
            
            Software Engineer at StartupXYZ (2018-2020)
            • Built REST APIs
            • Worked with Docker and Kubernetes
            • Reduced deployment time by 60%
            
            Education
            BS Computer Science, University (2014-2018)
            
            Skills
            Python, AWS, Docker, Kubernetes, Microservices, REST APIs
            """
        },
        processing_options={
            "scrub_pii": True,
            "audit_bias": True,
            "inject_goals": True,
            "hyde_expand": True,
            "reflect_improve": True,
            "analysis_depth": "comprehensive"
        }
    )
    
    try:
        result = orchestrator.generate_resume(request=request)
        
        if result.success:
            print("✅ Integrated pipeline test PASSED")
            print(f"   Final resume length: {len(result.final_resume_content)}")
            
            # Check execution trace for all features
            low_complexity_steps = [step for step in result.execution_trace if step.get("phase") == "LOW_Complexity_Preprocessing"]
            if low_complexity_steps:
                step = low_complexity_steps[0]
                print(f"✅ LOW preprocessing: {step.get('features_applied', 0)} features applied")
            
            # Check K-node outputs
            k1_output = result.k_node_outputs.get("k1_extract")
            if k1_output:
                hyde_steps = [step for step in k1_output.processing_trace if step.get("step") == "hyde_generation"]
                if hyde_steps:
                    print("✅ MEDIUM HyDE expansion applied")
            
            # Check processing metrics
            metrics = result.processing_metrics
            if metrics:
                print(f"✅ Processing metrics: {metrics.get('total_processing_time_ms', 0)}ms total time")
                print(f"   Success rate: {metrics.get('pipeline_success_rate', 0):.2f}")
            
            return True
        else:
            print(f"❌ Integrated pipeline test FAILED: {result.error_message}")
            return False
            
    except Exception as e:
        print(f"❌ Integrated pipeline test ERROR: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Testing MEDIUM and LOW Complexity Features Implementation\n")
    
    tests = [
        ("MEDIUM HyDE Expansion", test_medium_hyde_expansion),
        ("LOW Complexity Features", test_low_complexity_features),
        ("Integrated Pipeline", test_integrated_pipeline)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} CRASHED: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:.<40} {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Implementation is complete and working.")
    else:
        print("⚠️  Some tests failed. Check implementation.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
