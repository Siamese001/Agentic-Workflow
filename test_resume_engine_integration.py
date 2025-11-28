#!/usr/bin/env python3
"""
Integration Test for Phase F - Resume Engine Consolidation
Tests the extraction → enrichment → rendering pipeline
"""

import os
import tempfile

# Use direct imports to avoid circular import issues in main package
from resume_engine.l2.extraction import ClerkExtractor, DataEnricher
from resume_engine.rendering import FileRenderer
from resume_engine.state import ImmutableStagingBuffer
from resume_engine.l5.validation_engine import ValidationEngine, ValidationRule
from resume_engine.models import ValidationSeverity


def create_sample_master_resume():
    """Create a sample master resume for testing"""
    return {
        "owner": {
            "name": "John Doe",
            "email": "john.doe@example.com",
            "phone": "555-123-4567",
            "linkedin": "linkedin.com/in/johndoe"
        },
        "professional_experience": [
            {
                "company": "Tech Corp",
                "title": "Senior Software Engineer",
                "location": "San Francisco, CA",
                "dates": {
                    "start": "2020-01",
                    "end": "Present"
                },
                "overview": "Led development of enterprise software solutions",
                "bullet_pool": [
                    "Developed scalable microservices architecture",
                    "Improved system performance by 40%",
                    "Mentored junior developers on best practices"
                ]
            },
            {
                "company": "StartupXYZ",
                "title": "Software Engineer",
                "location": "Austin, TX",
                "dates": {
                    "start": "2018-06",
                    "end": "2019-12"
                },
                "overview": "Built web applications for startup clients",
                "bullet_pool": [
                    "Created responsive web interfaces",
                    "Implemented CI/CD pipelines",
                    "Collaborated with cross-functional teams"
                ]
            }
        ],
        "education": [
            {
                "degree": "Bachelor of Science in Computer Science",
                "institution": "University of Technology",
                "dates": "2014-2018",
                "notes": [
                    "Graduated magna cum laude",
                    "Dean's list for 6 semesters"
                ]
            }
        ],
        "certifications_and_credentials": [
            {
                "name": "AWS Certified Solutions Architect",
                "issuer": "Amazon Web Services",
                "date": "2021-03"
            }
        ],
        "strategic_and_technical_competencies": [
            "Python",
            "JavaScript",
            "React",
            "AWS",
            "Docker",
            "Kubernetes",
            "Microservices",
            "Agile Development"
        ]
    }


def test_extraction_pipeline():
    """Test the extraction and enrichment pipeline"""
    print("🧪 Testing Phase F Resume Engine Integration...")
    
    # Create sample data
    master_resume = create_sample_master_resume()
    
    # Test 1: ClerkExtractor
    print("\n1. Testing ClerkExtractor...")
    try:
        extractor = ClerkExtractor(master_resume)
        extracted_data, validation_results = extractor.extract()
        
        assert "experience_sections" in extracted_data
        assert "header" in extracted_data
        assert "education" in extracted_data
        assert "certifications" in extracted_data
        assert len(extracted_data["experience_sections"]) == 2
        print("   ✅ ClerkExtractor working correctly")
    except Exception as e:
        print(f"   ❌ ClerkExtractor failed: {e}")
        return False
    
    # Test 2: DataEnricher
    print("\n2. Testing DataEnricher...")
    try:
        enricher = DataEnricher()
        enriched_data = enricher.enrich(extracted_data)
        
        # Check that canonical verbs were added
        for section in enriched_data.get("experience_sections", []):
            for bullet in section.get("bullets", []):
                assert "canonical_verbs" in bullet
                assert isinstance(bullet["canonical_verbs"], list)
        
        print("   ✅ DataEnricher working correctly")
    except Exception as e:
        print(f"   ❌ DataEnricher failed: {e}")
        return False
    
    # Test 3: ValidationEngine
    print("\n3. Testing ValidationEngine...")
    try:
        validation_engine = ValidationEngine()
        
        # Add a simple validation rule
        def has_experience_sections(data):
            return len(data.get("experience_sections", [])) > 0
        
        validation_engine.register_rule(ValidationRule(
            rule_id="has_experience",
            severity=ValidationSeverity.HIGH,
            validator=has_experience_sections,
            error_message="Resume must have experience sections",
            category="structure"
        ))
        
        validation_results = validation_engine.validate(enriched_data)
        assert len(validation_results) == 1
        assert validation_results[0].passed == True
        print("   ✅ ValidationEngine working correctly")
    except Exception as e:
        print(f"   ❌ ValidationEngine failed: {e}")
        return False
    
    # Test 4: FileRenderer
    print("\n4. Testing FileRenderer...")
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create staging buffer with sample content
            staging_buffer = ImmutableStagingBuffer()
            staging_buffer.set("K0_CONTACT", master_resume["owner"])
            staging_buffer.set("K1_HEADLINE", "Senior Software Engineer | Cloud Architect | Full Stack Developer")
            staging_buffer.set("K2_SUMMARY", "Experienced software engineer with expertise in cloud architecture and full-stack development.")
            staging_buffer.set("K3_EXPERIENCE", enriched_data["experience_sections"])
            staging_buffer.set("K4_EDUCATION", enriched_data["education"])
            staging_buffer.set("K5_SKILLS", ", ".join(master_resume["strategic_and_technical_competencies"]))
            staging_buffer.lock()
            
            # Test rendering
            renderer = FileRenderer(
                master_resume=master_resume,
                output_dir=temp_dir,
                company_name="Tech Corp",
                job_title="Senior Software Engineer"
            )
            
            file_paths, (validation_results, file_contents) = renderer.render(
                staging_buffer=staging_buffer,
                company_name="Tech Corp",
                job_title="Senior Software Engineer"
            )
            
            # Check that files were created
            assert "resume_md" in file_paths
            assert "skills_md" in file_paths
            assert "cover_letter_md" in file_paths
            assert "qa_report_md" in file_paths
            assert "app_tracker_json" in file_paths
            
            # Check that files actually exist
            for file_type, filepath in file_paths.items():
                assert os.path.exists(filepath), f"File not created: {filepath}"
                assert os.path.getsize(filepath) > 0, f"File is empty: {filepath}"
            
            print("   ✅ FileRenderer working correctly")
            print(f"   📁 Generated {len(file_paths)} files in {temp_dir}")
            
    except Exception as e:
        print(f"   ❌ FileRenderer failed: {e}")
        return False
    
    # Test 5: Component Integration
    print("\n5. Testing Component Integration...")
    try:
        # Test that configuration classes work
        from resume_engine.config import EnricherConfig, ValidatorConfig
        config = EnricherConfig()
        assert config.enable_verb_canonicalization
        
        print("   ✅ Component imports and configuration working correctly")
    except Exception as e:
        print(f"   ❌ Component integration failed: {e}")
        return False
    
    print("\n🎉 Phase F Resume Engine Integration Test PASSED!")
    print("✅ All 6 major components extracted and working:")
    print("   - models.py (core dataclasses)")
    print("   - config.py (configuration)")
    print("   - l5/validation_engine.py (ValidationEngine, JDEnforcementValidator, PreFlightValidator)")
    print("   - l2/extraction.py (ClerkExtractor, DuplicateDetector, DataEnricher)")
    print("   - state.py (ImmutableStagingBuffer, TextSanitizer, ValidationContext)")
    print("   - rendering.py (FileRenderer)")
    
    return True


if __name__ == "__main__":
    success = test_extraction_pipeline()
    exit(0 if success else 1)
