"""
Debug test to isolate generation workflow issues
Tests the generation workflow directly without controller
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from apps.resume_app.workflows.app_resume_generation_workflow import ResumeGenerationWorkflow

def test_generation_workflow_direct():
    """Test generation workflow directly to isolate issues"""
    print("🔧 Testing Generation Workflow Directly...")
    
    config = {
        "enable_memory_query": False,  # Disable to isolate issues
        "enable_output_validation": False,
        "max_retry_attempts": 1
    }
    
    workflow = ResumeGenerationWorkflow(config)
    
    # Minimal test data
    request_data = {
        "target_role": "Software Engineer",
        "experience_level": "mid",
        "job_description": "Software Engineer role",
        "personal_info": {
            "name": "John Doe",
            "email": "john.doe@email.com",
            "phone": "+1-555-0123",
            "linkedin_url": "https://linkedin.com/in/johndoe"
        },
        "professional_experience": [
            {
                "company": "Tech Corp",
                "title": "Engineer",
                "bullet_pool": ["Developed features", "Fixed bugs"]
            }
        ],
        "skills": {
            "technical": ["Python", "JavaScript"]
        }
    }
    
    print(f"📝 Request data: {request_data}")
    
    try:
        result = workflow.execute_resume_generation(request_data)
        print(f"✅ Workflow result: success={result.success}")
        print(f"📊 Metadata: {result.metadata}")
        
        if not result.success:
            print(f"❌ Workflow failed: {result.metadata.get('workflow_error', 'Unknown')}")
            if 'full_traceback' in result.metadata:
                print(f"🔍 Full traceback:\n{result.metadata['full_traceback']}")
        
        return result
        
    except Exception as e:
        print(f"💥 Exception in test: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def test_engine_adapter_direct():
    """Test engine adapter directly"""
    print("🔧 Testing Engine Adapter Directly...")
    
    from apps.resume_app.adapters.app_resume_engine_adapter import ResumeEngineAdapter, ResumeGenerationRequest
    
    adapter = ResumeEngineAdapter()
    
    # Create generation request
    generation_request = ResumeGenerationRequest(
        target_role="Software Engineer",
        experience_level="mid",
        job_description="Software Engineer role",
        master_resume_data={
            "professional_experience": [
                {
                    "company": "Tech Corp",
                    "title": "Engineer",
                    "bullet_pool": ["Developed features", "Fixed bugs"]
                }
            ]
        }
    )
    
    try:
        print(f"📝 Generation request created")
        response = adapter.generate_enhanced_resume(generation_request)
        print(f"✅ Engine adapter response: {response}")
        return response
        
    except Exception as e:
        print(f"💥 Exception in engine adapter: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Run debug tests"""
    print("🚀 Starting Debug Tests for Generation Workflow")
    print("=" * 60)
    
    # Test 1: Engine adapter directly
    print("\n1️⃣ Testing Engine Adapter Directly:")
    engine_result = test_engine_adapter_direct()
    
    # Test 2: Generation workflow directly  
    print("\n2️⃣ Testing Generation Workflow Directly:")
    workflow_result = test_generation_workflow_direct()
    
    print("\n" + "=" * 60)
    print("🔍 Debug Test Summary:")
    print(f"Engine Adapter: {'✅ Success' if engine_result else '❌ Failed'}")
    print(f"Generation Workflow: {'✅ Success' if workflow_result and workflow_result.success else '❌ Failed'}")
    
    if workflow_result and not workflow_result.success:
        print(f"Workflow Error: {workflow_result.metadata.get('workflow_error', 'Unknown')}")

if __name__ == "__main__":
    main()
