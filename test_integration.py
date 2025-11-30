#!/usr/bin/env python3
"""
Integration test for apps/resume_app components
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_workflow_integration():
    """Test basic workflow integration"""
    try:
        print("Testing workflow import...")
        from apps.resume_app.workflows.app_resume_generation_workflow import ResumeGenerationWorkflow
        print("✓ Workflow import successful")
        
        # Test basic instantiation
        print("Testing workflow instantiation...")
        workflow = ResumeGenerationWorkflow()
        print("✓ Workflow instantiation successful")
        
        # Test status method
        print("Testing workflow status...")
        status = workflow.get_workflow_status()
        print("✓ Workflow status method successful")
        print(f"Components initialized: {status['components_initialized']}")
        
        # Test quick validation with minimal data
        print("Testing quick validation...")
        test_data = {
            'target_role': 'Software Engineer',
            'experience_level': 'mid',
            'personal_info': {'name': 'John Doe'}
        }
        
        validation_result = workflow.execute_quick_validation(test_data)
        print("✓ Quick validation successful")
        print(f"Validation result: {validation_result['valid']}")
        
        if validation_result['valid']:
            print("✅ Integration test passed!")
        else:
            print("⚠️  Validation failed but integration works")
            print(f"Errors: {validation_result.get('input_validation', {}).get('errors', [])}")
        
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_individual_components():
    """Test individual component imports"""
    components = [
        ("ResumeEngineAdapter", "apps.resume_app.adapters.app_resume_engine_adapter"),
        ("ResumeMemoryAdapter", "apps.resume_app.adapters.app_resume_memory_adapter"),
        ("ResumeInputValidator", "apps.resume_app.validators.app_resume_input_validator"),
        ("ResumeSchemaValidator", "apps.resume_app.validators.app_resume_schema_validator"),
    ]
    
    for name, module_path in components:
        try:
            print(f"Testing {name} import...")
            module = __import__(module_path, fromlist=[name])
            component = getattr(module, name)
            print(f"✓ {name} import successful")
        except Exception as e:
            print(f"❌ {name} import failed: {str(e)}")
            return False
    
    return True

if __name__ == "__main__":
    print("🧪 Running Apps Integration Tests")
    print("=" * 50)
    
    # Test individual components
    print("\n1. Testing Individual Components")
    components_ok = test_individual_components()
    
    # Test workflow integration
    print("\n2. Testing Workflow Integration")
    workflow_ok = test_workflow_integration()
    
    # Summary
    print("\n" + "=" * 50)
    if components_ok and workflow_ok:
        print("🎉 All integration tests passed!")
        sys.exit(0)
    else:
        print("❌ Some integration tests failed")
        sys.exit(1)
