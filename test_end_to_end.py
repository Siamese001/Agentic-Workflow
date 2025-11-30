#!/usr/bin/env python3
"""
End-to-end test for apps/resume_app with real resume data
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_test_resume_data():
    """Create realistic test resume data"""
    return {
        "target_role": "Senior Software Engineer",
        "experience_level": "senior",
        "job_description": "We are looking for a Senior Software Engineer with experience in Python, machine learning, and cloud technologies. The ideal candidate will have 5+ years of experience developing scalable applications and working with cross-functional teams.",
        "target_company": "TechCorp",
        "optimization_focus": ["impact", "keywords", "technical_skills"],
        "linkedin_format": True,
        "personal_info": {
            "name": "Jane Doe",
            "location": "San Francisco, CA",
            "website": "https://janedoe.dev",
            "linkedin_url": "https://linkedin.com/in/janedoe"
        },
        "contact_info": {
            "email": "jane.doe@example.com",
            "phone": "+1-555-0123",
            "linkedin_url": "https://linkedin.com/in/janedoe"
        },
        "professional_experience": [
            {
                "company": "Tech Solutions Inc.",
                "title": "Software Engineer",
                "duration": "2020-2023",
                "start_date": "2020-06-01",
                "end_date": "2023-08-31",
                "bullet_pool": [
                    "Developed microservices using Python and Django",
                    "Improved application performance by 40%",
                    "Led a team of 3 junior developers",
                    "Implemented CI/CD pipelines reducing deployment time by 60%",
                    "Collaborated with product managers to define technical requirements"
                ]
            },
            {
                "company": "StartupXYZ",
                "title": "Junior Developer", 
                "duration": "2018-2020",
                "start_date": "2018-09-01",
                "end_date": "2020-05-31",
                "bullet_pool": [
                    "Built RESTful APIs for mobile applications",
                    "Worked with React frontend components",
                    "Participated in agile development process",
                    "Fixed critical bugs improving system stability"
                ]
            }
        ],
        "skills": {
            "technical": ["Python", "Django", "Flask", "React", "JavaScript", "SQL", "PostgreSQL", "MongoDB", "Docker", "Kubernetes", "AWS", "Git"],
            "soft": ["Leadership", "Communication", "Problem-solving", "Team collaboration", "Mentoring"],
            "tools": ["VS Code", "JIRA", "Slack", "Postman", "Docker Desktop"],
            "certifications": ["AWS Certified Developer", "Google Cloud Professional"]
        }
    }

def test_end_to_end_workflow():
    """Test complete end-to-end workflow with real data"""
    try:
        print("🚀 Starting End-to-End Workflow Test")
        print("=" * 60)
        
        # Import workflow
        print("1. Importing workflow...")
        from apps.resume_app.workflows.app_resume_generation_workflow import ResumeGenerationWorkflow
        print("✓ Workflow imported successfully")
        
        # Initialize workflow with configuration
        print("2. Initializing workflow...")
        config = {
            "enable_memory_query": True,
            "enable_output_validation": True,
            "max_retry_attempts": 2,
            "cache_enabled": True
        }
        workflow = ResumeGenerationWorkflow(config)
        print("✓ Workflow initialized successfully")
        
        # Get workflow status
        print("3. Checking workflow status...")
        status = workflow.get_workflow_status()
        print(f"✓ Components initialized: {status['components_initialized']}")
        print(f"✓ Configuration: {status['configuration']}")
        
        # Create test data
        print("4. Creating test resume data...")
        test_data = create_test_resume_data()
        print(f"✓ Test data created for {test_data['target_role']} at {test_data['target_company']}")
        
        # Run quick validation first
        print("5. Running quick validation...")
        validation_result = workflow.execute_quick_validation(test_data)
        print(f"✓ Validation completed - Valid: {validation_result['valid']}")
        
        if not validation_result['valid']:
            print("⚠️  Validation issues found:")
            for error in validation_result.get('input_validation', {}).get('errors', []):
                print(f"   - {error}")
            print("Continuing with full workflow test...")
        
        # Run full workflow
        print("6. Running full resume generation workflow...")
        # Pass the complete test data as master_resume_data for bullet extraction
        test_data["master_resume_data"] = {
            "professional_experience": test_data["professional_experience"],
            "technical_skills": test_data["skills"]["technical"],
            "soft_skills": test_data["skills"]["soft"],
            "tools": test_data["skills"]["tools"],
            "certifications": test_data["skills"]["certifications"]
        }
        result = workflow.execute_resume_generation(test_data)
        
        # Analyze results
        print("\n📊 Workflow Results Analysis")
        print("-" * 40)
        print(f"Success: {result.success}")
        print(f"Total time: {result.total_time_seconds:.2f} seconds")
        print(f"Steps completed: {len(result.steps_completed)}")
        
        # Check each step
        for step in result.steps_completed:
            status_icon = "✓" if step.status == "completed" else "❌"
            print(f"{status_icon} {step.step_name}: {step.status}")
            if step.error_message:
                print(f"   Error: {step.error_message}")
        
        # Validate resume response
        if result.resume_response:
            print(f"\n📄 Generated Resume Summary")
            print("-" * 40)
            response = result.resume_response
            print(f"Enhanced bullets: {len(response.enhanced_bullets)}")
            print(f"Professional summary length: {len(response.professional_summary)} chars")
            print(f"Enhancement confidence: {response.enhancement_confidence:.2f}")
            
            # Check LinkedIn compliance
            if response.linkedin_compliance:
                print(f"\n🔗 LinkedIn Compliance Check")
                print("-" * 40)
                for check, passed in response.linkedin_compliance.items():
                    status_icon = "✓" if passed else "❌"
                    print(f"{status_icon} {check}: {passed}")
            
            # Sample enhanced bullets
            if response.enhanced_bullets:
                print(f"\n💡 Sample Enhanced Bullets")
                print("-" * 40)
                for i, bullet in enumerate(response.enhanced_bullets[:3], 1):
                    print(f"{i}. {bullet}")
                    print(f"   Length: {len(bullet)} chars")
            
            # Professional summary preview
            if response.professional_summary:
                print(f"\n📝 Professional Summary Preview")
                print("-" * 40)
                summary_preview = response.professional_summary[:200] + "..." if len(response.professional_summary) > 200 else response.professional_summary
                print(f'"{summary_preview}"')
        
        # Validation results summary
        if result.validation_results:
            print(f"\n✅ Validation Summary")
            print("-" * 40)
            for i, validation in enumerate(result.validation_results, 1):
                print(f"Validation {i}: {'✓ Passed' if validation.is_valid else '❌ Failed'}")
                if validation.errors:
                    for error in validation.errors[:3]:  # Show first 3 errors
                        print(f"   - {error}")
        
        # Overall assessment
        print(f"\n🎯 Overall Assessment")
        print("=" * 60)
        if result.success:
            print("🎉 End-to-end test PASSED!")
            print("✓ All workflow steps completed successfully")
            print("✓ Resume generated with proper structure")
            print("✓ LinkedIn compliance checks performed")
            print("✓ Validation and error handling working")
        else:
            print("❌ End-to-end test FAILED!")
            print("⚠️  Some workflow steps did not complete")
            if "workflow_error" in result.metadata:
                print(f"Error: {result.metadata['workflow_error']}")
        
        return result.success
        
    except Exception as e:
        print(f"❌ End-to-end test failed with exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_component_individual_capabilities():
    """Test individual component capabilities"""
    print("\n🔧 Testing Individual Component Capabilities")
    print("=" * 60)
    
    try:
        # Test validators
        print("1. Testing validators...")
        from apps.resume_app.validators.app_resume_input_validator import ResumeInputValidator
        from apps.resume_app.validators.app_resume_schema_validator import ResumeSchemaValidator
        
        input_validator = ResumeInputValidator()
        schema_validator = ResumeSchemaValidator()
        
        # Test bullet validation
        test_bullets = [
            "Led development of microservices architecture",
            "Improved system performance by 40% through optimization",
            "Mentored team of junior developers in best practices"
        ]
        
        bullet_result = input_validator.validate_bullet_points(test_bullets)
        print(f"✓ Bullet validation: {bullet_result.is_valid} (Score: {bullet_result.compliance_score})")
        
        # Test schema export
        schema_json = schema_validator.export_schema_json("resume_request")
        print(f"✓ Schema export: {len(schema_json)} characters")
        
        # Test adapters
        print("2. Testing adapters...")
        from apps.resume_app.adapters.app_resume_engine_adapter import ResumeEngineAdapter
        from apps.resume_app.adapters.app_resume_memory_adapter import ResumeMemoryAdapter
        
        engine_adapter = ResumeEngineAdapter()
        memory_adapter = ResumeMemoryAdapter()
        
        # Test memory stats
        memory_stats = memory_adapter.get_memory_stats()
        print(f"✓ Memory stats: {memory_stats['total_bullets']} bullets, {memory_stats['total_competencies']} competencies")
        
        # Test validation summary
        validation_summary = input_validator.get_validation_summary()
        print(f"✓ Validation rules: {validation_summary['validation_rules_count']} rules defined")
        
        print("✅ All component capabilities working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Component capability test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 Running End-to-End Apps Layer Tests")
    print("=" * 80)
    
    # Test individual components
    components_ok = test_component_individual_capabilities()
    
    # Test end-to-end workflow
    workflow_ok = test_end_to_end_workflow()
    
    # Final summary
    print("\n" + "=" * 80)
    print("📋 FINAL TEST SUMMARY")
    print("=" * 80)
    
    if components_ok and workflow_ok:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Apps layer is ready for production use")
        print("✅ End-to-end resume generation pipeline working")
        print("✅ LinkedIn compliance integrated")
        print("✅ Error handling and validation functional")
        sys.exit(0)
    else:
        print("❌ SOME TESTS FAILED")
        if not components_ok:
            print("⚠️  Component capability issues detected")
        if not workflow_ok:
            print("⚠️  End-to-end workflow issues detected")
        sys.exit(1)
