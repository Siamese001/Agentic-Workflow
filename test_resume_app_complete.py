"""
Comprehensive End-to-End Test for Complete Resume App Pipeline
Tests research workflow, controller, and serializer integration
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from typing import Dict, Any
import json
from datetime import datetime

# Import resume app components
from apps.resume_app.workflows.app_resume_research_workflow import (
    ResumeResearchWorkflow, ResearchResult
)
from apps.resume_app.controllers.app_resume_controller import (
    ResumeController, ResumeRequest, ResearchRequest
)
from apps.resume_app.serializers.app_resume_output_serializer import (
    ResumeOutputSerializer, ResumeOutputFormat
)


def test_research_workflow():
    """Test the resume research workflow"""
    print("🔍 Testing Resume Research Workflow...")
    
    config = {
        "enable_memory_storage": True,
        "max_keywords_extracted": 20,
        "enable_thematic_analysis": True
    }
    
    workflow = ResumeResearchWorkflow(config)
    
    # Test job description
    job_description = """
    Senior Software Engineer position at TechCorp requiring Python, Django, AWS experience.
    Looking for 5+ years of experience in full-stack development, microservices architecture,
    and team leadership. Must have experience with Agile methodologies and CI/CD pipelines.
    """
    
    result = workflow.execute_job_research(
        job_description=job_description,
        target_role="Senior Software Engineer",
        company_info="TechCorp - Technology company"
    )
    
    assert result.success, f"Research workflow failed: {result.metadata.get('error', 'Unknown')}"
    assert result.job_analysis is not None, "Job analysis should not be None"
    assert result.job_analysis.target_role == "Senior Software Engineer", "Target role mismatch"
    assert len(result.job_analysis.required_skills) > 0, "No required skills extracted"
    assert result.job_analysis.experience_level == "senior", "Experience level not detected correctly"
    assert len(result.keyword_rankings) > 0, "No keywords extracted"
    assert len(result.recommendations) > 0, "No recommendations generated"
    
    print(f"✓ Research workflow passed - Found {len(result.job_analysis.required_skills)} skills")
    return result


def test_resume_controller():
    """Test the resume controller with research integration"""
    print("🎮 Testing Resume Controller...")
    
    config = {
        "enable_research_by_default": True,
        "strict_linkedin_compliance": True,
        "max_processing_time": 300
    }
    
    controller = ResumeController(config)
    
    # Create test resume request
    request = ResumeRequest(
        target_role="Senior Software Engineer",
        experience_level="senior",
        job_description="Senior Software Engineer at TechCorp requiring Python, Django, AWS experience.",
        target_company="TechCorp",
        personal_info={
            "name": "John Doe",
            "email": "john.doe@email.com",
            "phone": "+1-555-0123",
            "linkedin_url": "https://linkedin.com/in/johndoe"
        },
        professional_experience=[
            {
                "company": "Previous Company",
                "title": "Software Engineer",
                "duration": "3 years",
                "bullet_pool": [
                    "Developed microservices using Python and Django",
                    "Improved application performance by 40%",
                    "Led a team of 3 junior developers",
                    "Implemented CI/CD pipelines",
                    "Managed cloud infrastructure on AWS"
                ]
            }
        ],
        skills={
            "technical": ["Python", "Django", "AWS", "Docker", "PostgreSQL"],
            "soft": ["Leadership", "Communication", "Problem Solving"]
        },
        education=[
            {
                "degree": "Bachelor of Science in Computer Science",
                "university": "State University",
                "year": "2018"
            }
        ],
        enable_research=True,
        linkedin_compliance=True
    )
    
    response = controller.generate_resume(request)
    
    assert response.success, f"Resume generation failed: {response.error_message}"
    assert response.resume_data is not None, "Resume data should not be None"
    assert response.linkedin_compliance_score > 90, f"LinkedIn compliance score too low: {response.linkedin_compliance_score}"
    assert response.processing_time_seconds > 0, "Processing time should be positive"
    
    # Check research integration
    if response.research_results:
        assert response.research_results.success, "Research should succeed"
        assert response.research_results.job_analysis is not None, "Job analysis should be present"
    
    print(f"✓ Controller passed - Compliance score: {response.linkedin_compliance_score:.1f}")
    return response


def test_research_only():
    """Test research-only functionality"""
    print("🔬 Testing Research-Only Functionality...")
    
    controller = ResumeController()
    
    research_request = ResearchRequest(
        job_description="Data Scientist position requiring Python, Machine Learning, SQL experience.",
        target_role="Data Scientist",
        company_info="DataCorp - Analytics company",
        include_thematic_analysis=True,
        max_keywords=30
    )
    
    response = controller.research_job(research_request)
    
    assert response.success, f"Research failed: {response.error_message}"
    assert response.research_result is not None, "Research result should not be None"
    assert response.processing_time_seconds > 0, "Processing time should be positive"
    
    research = response.research_result
    assert research.success, "Research should succeed"
    assert len(research.keyword_rankings) > 0, "Keywords should be extracted"
    assert len(research.competitive_insights) > 0, "Competitive insights should be generated"
    
    print(f"✓ Research-only passed - {len(research.keyword_rankings)} keywords extracted")
    return response


def test_output_serializer():
    """Test the output serializer with different formats"""
    print("📄 Testing Output Serializer...")
    
    # Use the controller response from previous test
    controller = ResumeController()
    request = ResumeRequest(
        target_role="Software Engineer",
        experience_level="mid",
        job_description="Software Engineer role requiring Python and web development.",
        personal_info={
            "name": "Jane Smith",
            "email": "jane.smith@email.com",
            "phone": "+1-555-0456",
            "linkedin_url": "https://linkedin.com/in/janesmith"
        },
        professional_experience=[
            {
                "company": "Tech Company",
                "title": "Software Engineer", 
                "bullet_pool": ["Developed web applications", "Improved performance by 25%"]
            }
        ],
        enable_research=False
    )
    
    controller_response = controller.generate_resume(request)
    
    serializer = ResumeOutputSerializer()
    
    # Test JSON format
    json_format = ResumeOutputFormat(format_type="json", linkedin_optimized=True)
    json_result = serializer.serialize_resume_response(controller_response, json_format)
    
    assert json_result.format_type == "json", "JSON format type mismatch"
    assert json_result.content is not None, "JSON content should not be None"
    assert json_result.linkedin_compliance["compliance_score"] > 0, "Should have compliance score"
    
    # Test Markdown format
    md_format = ResumeOutputFormat(format_type="markdown", include_metadata=True)
    md_result = serializer.serialize_resume_response(controller_response, md_format)
    
    assert md_result.format_type == "markdown", "Markdown format type mismatch"
    assert isinstance(md_result.content, str), "Markdown content should be string"
    assert "# Professional Summary" in md_result.content, "Should contain summary header"
    
    # Test HTML format
    html_format = ResumeOutputFormat(format_type="html")
    html_result = serializer.serialize_resume_response(controller_response, html_format)
    
    assert html_result.format_type == "html", "HTML format type mismatch"
    assert "<html>" in html_result.content, "Should contain HTML tags"
    
    print("✓ Serializer passed - All formats working correctly")
    return serializer


def test_linkedin_compliance():
    """Test LinkedIn compliance enforcement"""
    print("✅ Testing LinkedIn Compliance Enforcement...")
    
    controller = ResumeController({"strict_linkedin_compliance": True})
    
    # Test compliant resume
    compliant_request = ResumeRequest(
        target_role="Software Engineer",
        experience_level="mid",
        personal_info={
            "name": "Test User",
            "email": "test@example.com",
            "phone": "+1-555-0000",
            "linkedin_url": "https://linkedin.com/in/testuser"
        },
        professional_experience=[
            {
                "company": "Tech Corp",
                "title": "Engineer",
                "bullet_pool": ["Developed features", "Fixed bugs", "Wrote tests"]  # 3 bullets (<= 5)
            }
        ]
    )
    
    compliant_response = controller.generate_resume(compliant_request)
    assert compliant_response.success, "Compliant resume should pass"
    
    # Test non-compliant resume (too many bullets)
    non_compliant_request = ResumeRequest(
        target_role="Software Engineer", 
        experience_level="mid",
        personal_info={
            "name": "Test User",
            "email": "test@example.com",
            "phone": "+1-555-0000",
            "linkedin_url": "https://linkedin.com/in/testuser"
        },
        professional_experience=[
            {
                "company": "Tech Corp",
                "title": "Engineer",
                "bullet_pool": [
                    "Bullet 1", "Bullet 2", "Bullet 3", "Bullet 4", 
                    "Bullet 5", "Bullet 6", "Bullet 7", "Bullet 8", "Bullet 9"  # 9 bullets (> 5)
                ]
            }
        ]
    )
    
    non_compliant_response = controller.generate_resume(non_compliant_request)
    assert not non_compliant_response.success, "Non-compliant resume should fail"
    assert "bullet" in non_compliant_response.error_message.lower(), "Should mention bullet error"
    
    print("✓ LinkedIn compliance enforcement working correctly")
    return True


def test_integration():
    """Test complete integration: Research -> Controller -> Serializer"""
    print("🔗 Testing Complete Integration...")
    
    # Step 1: Research
    research_workflow = ResumeResearchWorkflow()
    research_result = research_workflow.execute_job_research(
        job_description="Senior Python Developer with Django and AWS experience needed",
        target_role="Senior Python Developer"
    )
    
    assert research_result.success, "Research should succeed"
    
    # Step 2: Controller with research insights
    controller = ResumeController()
    resume_request = ResumeRequest(
        target_role="Senior Python Developer",
        experience_level="senior",
        job_description="Senior Python Developer with Django and AWS experience needed",
        personal_info={
            "name": "Integration User",
            "email": "integration@example.com",
            "phone": "+1-555-9999",
            "linkedin_url": "https://linkedin.com/in/integrationuser"
        },
        professional_experience=[
            {
                "company": "Previous Company",
                "title": "Python Developer",
                "bullet_pool": ["Built web apps", "Optimized performance"]
            }
        ],
        enable_research=True
    )
    
    controller_response = controller.generate_resume(resume_request)
    
    if not controller_response.success:
        print(f"❌ Controller failed: {controller_response.error_message}")
        print(f"🔍 Validation errors: {controller_response.validation_results}")
    
    assert controller_response.success, "Controller should succeed"
    assert controller_response.research_results is not None, "Should have research results"
    
    # Step 3: Serializer
    serializer = ResumeOutputSerializer()
    json_format = ResumeOutputFormat(format_type="json", include_provenance=True)
    final_output = serializer.serialize_resume_response(controller_response, json_format)
    
    assert final_output.format_type == "json", "Final output should be JSON"
    assert final_output.provenance, "Should include provenance when requested"
    assert final_output.linkedin_compliance["compliance_score"] > 0, "Should have compliance info"
    
    print("✓ Complete integration test passed")
    return final_output


def main():
    """Run all comprehensive tests"""
    print("🚀 Starting Comprehensive Resume App Pipeline Tests")
    print("=" * 60)
    
    try:
        # Test individual components
        research_result = test_research_workflow()
        controller_response = test_resume_controller()
        research_response = test_research_only()
        serializer = test_output_serializer()
        compliance_result = test_linkedin_compliance()
        integration_result = test_integration()
        
        print("\n" + "=" * 60)
        print("🎉 ALL TESTS PASSED!")
        print("=" * 60)
        
        # Summary
        print("📊 Test Summary:")
        print(f"✓ Research Workflow: {len(research_result.keyword_rankings)} keywords extracted")
        print(f"✓ Controller: Compliance score {controller_response.linkedin_compliance_score:.1f}")
        print(f"✓ Research-Only: {len(research_response.research_result.competitive_insights)} insights")
        print(f"✓ Serializer: {len(serializer.get_supported_formats())} formats supported")
        print(f"✓ LinkedIn Compliance: Enforcement working")
        print(f"✓ Integration: End-to-end pipeline functional")
        
        print("\n🎯 Resume App Reference Pattern: PRODUCTION READY")
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
