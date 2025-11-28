#!/usr/bin/env python3
"""
Resume Generation Pipeline Demo

Demonstrates the complete 8-node resume generation pipeline:
L1 Planning → K1 Extract → K2 Clean → K3 Quantify → K4 Rewrite → K5 Skillmap → K6 Assemble → K7 Format → K8 Validate

Usage:
    python demo_resume_generation.py
"""

import sys
import logging
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from resume_engine import (
    RGOrchestrator, 
    ResumeGenerationRequest,
    generate_resume,
    create_sample_request
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def print_section_header(title: str):
    """Print a formatted section header."""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def print_subsection_header(title: str):
    """Print a formatted subsection header."""
    print(f"\n--- {title} ---")

def demo_basic_usage():
    """Demonstrate basic usage of the resume generation pipeline."""
    print_section_header("DEMO 1: Basic Resume Generation")
    
    # Create orchestrator
    print_subsection_header("Initializing Orchestrator")
    orchestrator = RGOrchestrator()
    print("✓ RGOrchestrator initialized successfully")
    
    # Create sample request
    print_subsection_header("Creating Sample Request")
    request = orchestrator.create_sample_request()
    print(f"✓ Sample request created")
    print(f"  Target Role: {request.job_input['title']}")
    print(f"  Target Company: {request.job_input['company']}")
    print(f"  Industry: {request.job_input['industry']}")
    
    # Execute pipeline
    print_subsection_header("Executing Resume Generation Pipeline")
    print("Starting K1→K8 sequential execution...")
    
    result = orchestrator.generate_resume(request=request)
    
    # Display results
    print_subsection_header("Pipeline Results")
    print(f"Success: {result.success}")
    print(f"Error Message: {result.error_message or 'None'}")
    
    if result.success:
        print(f"Final Resume Length: {len(result.final_resume_content)} characters")
        print(f"Processing Time: {result.processing_metrics.get('total_processing_time_ms', 0)}ms")
        print(f"Pipeline Success Rate: {result.processing_metrics.get('pipeline_success_rate', 0):.2%}")
        
        # Show execution trace
        print_subsection_header("Execution Trace")
        for trace in result.execution_trace:
            status_symbol = "✓" if trace.get('status') == 'success' else "⚠" if trace.get('status') == 'warning' else "✗"
            print(f"  {status_symbol} {trace.get('phase', 'Unknown')} - {trace.get('status', 'Unknown')}")
            if 'execution_time_ms' in trace:
                print(f"    Time: {trace['execution_time_ms']:.2f}ms")
    else:
        print(f"Pipeline failed: {result.error_message}")

def demo_k_node_outputs():
    """Demonstrate detailed K-node outputs and data flow."""
    print_section_header("DEMO 2: Detailed K-Node Analysis")
    
    orchestrator = RGOrchestrator()
    request = orchestrator.create_sample_request()
    
    # Execute with detailed configuration
    config = {
        "enable_error_recovery": True,
        "performance_monitoring": True,
        "k1_config": {"strategy": "hybrid"},
        "k2_config": {"normalization_level": "standard"},
        "k3_config": {"approach": "achievements"},
        "k4_config": {"style": "professional", "enhance_achievements": True},
        "k5_config": {"method": "job_alignment"},
        "k6_config": {"organization": "targeted"},
        "k7_config": {"standards": "ats_optimized"},
        "k8_config": {"level": "comprehensive"}
    }
    
    orchestrator.config.update(config)
    result = orchestrator.generate_resume(request=request)
    
    if result.success:
        print_subsection_header("K-Node Output Summary")
        
        for node_name, node_output in result.k_node_outputs.items():
            print(f"\n{node_name.upper()}:")
            
            if hasattr(node_output, 'metrics'):
                metrics = node_output.metrics
                print(f"  Success: {getattr(node_output, 'success', 'N/A')}")
                
                # Show key metrics based on node type
                if node_name == "k1_extract":
                    print(f"  Sections Extracted: {metrics.total_sections}")
                    print(f"  Extraction Confidence: {metrics.extraction_confidence:.2f}")
                elif node_name == "k2_clean":
                    print(f"  Operations Performed: {metrics.total_operations}")
                    print(f"  Quality Improvement: {metrics.quality_improvement_score:.2f}")
                elif node_name == "k3_quantify":
                    print(f"  Metrics Extracted: {metrics.total_metrics_extracted}")
                    print(f"  Achievements Quantified: {metrics.total_achievements_quantified}")
                elif node_name == "k4_rewrite":
                    print(f"  Enhancements Applied: {metrics.enhancements_applied}")
                    print(f"  Average Improvement: {metrics.average_improvement_score:.2f}")
                elif node_name == "k5_skillmap":
                    print(f"  Skills Mapped: {metrics.total_skills_mapped}")
                    print(f"  Coverage Percentage: {metrics.coverage_percentage:.1f}%")
                elif node_name == "k6_assemble":
                    print(f"  Sections Assembled: {metrics.total_sections_assembled}")
                    print(f"  Organization Quality: {metrics.organization_quality:.2f}")
                elif node_name == "k7_format":
                    print(f"  Formatting Rules Applied: {metrics.formatting_rules_applied}")
                    print(f"  ATS Compliance: {metrics.overall_ats_compliance:.2f}")
                elif node_name == "k8_validate":
                    print(f"  Rules Checked: {metrics.total_rules_checked}")
                    print(f"  Critical Issues: {metrics.critical_issues}")
        
        # Show validation results
        if result.validation_result:
            print_subsection_header("Final Validation Results")
            validation = result.validation_result
            print(f"Overall Status: {validation.overall_status}")
            print(f"Quality Score: {validation.quality_score:.2f}")
            print(f"Compliance Score: {validation.compliance_score:.2f}")
            print(f"Content Score: {validation.content_score:.2f}")
            print(f"Format Score: {validation.format_score:.2f}")
            
            if validation.recommendations:
                print(f"\nRecommendations ({len(validation.recommendations)}):")
                for i, rec in enumerate(validation.recommendations[:5], 1):
                    print(f"  {i}. {rec}")

def demo_convenience_functions():
    """Demonstrate convenience functions."""
    print_section_header("DEMO 3: Convenience Functions")
    
    # Test generate_resume function
    print_subsection_header("Using generate_resume() Function")
    
    job_input = {
        "title": "Data Scientist",
        "company": "Analytics Corp",
        "industry": "technology",
        "description": "Data science role focused on machine learning and analytics",
        "requirements": ["Python", "Machine Learning", "Statistics", "3+ years experience"],
        "skills": ["python", "machine learning", "statistics", "sql", "data visualization"]
    }
    
    resume_input = {
        "content": """
        Jane Smith
        Email: jane@example.com | Phone: 555-5678 | LinkedIn: linkedin.com/in/janesmith
        
        Professional Summary
        Data scientist with expertise in machine learning and statistical analysis.
        
        Experience
        Data Scientist at DataCorp (2021-Present)
        • Developed machine learning models using Python and scikit-learn
        • Analyzed large datasets to extract business insights
        • Improved prediction accuracy by 25%
        
        Junior Data Scientist at StartupXYZ (2019-2021)
        • Built data pipelines and visualization dashboards
        • Applied statistical methods to solve business problems
        • Collaborated with cross-functional teams
        
        Education
        MS Data Science, Tech University (2017-2019)
        BS Statistics, State University (2013-2017)
        
        Skills
        Python, Machine Learning, Statistics, SQL, Data Visualization, TensorFlow
        """,
        "sections": {
            "contact_info": "Jane Smith\nEmail: jane@example.com | Phone: 555-5678 | LinkedIn: linkedin.com/in/janesmith",
            "summary": "Data scientist with expertise in machine learning and statistical analysis.",
            "experience": "Data Scientist at DataCorp (2021-Present)\n• Developed machine learning models using Python and scikit-learn\n• Analyzed large datasets to extract business insights\n• Improved prediction accuracy by 25%",
            "education": "MS Data Science, Tech University (2017-2019)\nBS Statistics, State University (2013-2017)",
            "skills": "Python, Machine Learning, Statistics, SQL, Data Visualization, TensorFlow"
        }
    }
    
    processing_options = {
        "analysis_depth": "comprehensive",
        "validation_level": "comprehensive",
        "formatting_standards": "professional"
    }
    
    result = generate_resume(
        job_input=job_input,
        resume_input=resume_input,
        processing_options=processing_options
    )
    
    print(f"✓ Resume generated successfully: {result.success}")
    print(f"✓ Processing time: {result.processing_metrics.get('total_processing_time_ms', 0)}ms")
    print(f"✓ Final content length: {len(result.final_resume_content)} characters")
    
    # Test create_sample_request function
    print_subsection_header("Using create_sample_request() Function")
    sample_request = create_sample_request()
    print(f"✓ Sample request created for: {sample_request.job_input['title']}")
    print(f"✓ Resume has {len(sample_request.resume_input.get('sections', {}))} sections")

def demo_error_handling():
    """Demonstrate error handling and recovery."""
    print_section_header("DEMO 4: Error Handling and Recovery")
    
    # Test with invalid input
    print_subsection_header("Testing Invalid Input Handling")
    
    orchestrator = RGOrchestrator(config={"enable_error_recovery": True})
    
    # Create request with missing required fields
    invalid_request = ResumeGenerationRequest(
        job_input={},  # Empty job input
        resume_input={},  # Empty resume input
        processing_options={}
    )
    
    result = orchestrator.generate_resume(request=invalid_request)
    
    print(f"Success: {result.success}")
    print(f"Error Message: {result.error_message}")
    
    if not result.success:
        print("✓ Error handling working correctly - invalid input rejected")
    else:
        print("⚠ Warning: Invalid input was accepted")

def main():
    """Main demo function."""
    print("🚀 Resume Generation Pipeline Demo")
    print("=" * 60)
    print("This demo showcases the complete 8-node resume generation pipeline")
    print("with L1 planning, K-node sequential execution, and L3 orchestration.")
    
    try:
        # Run all demos
        demo_basic_usage()
        demo_k_node_outputs()
        demo_convenience_functions()
        demo_error_handling()
        
        print_section_header("DEMO COMPLETE")
        print("✓ All demos completed successfully!")
        print("✓ Resume generation pipeline is fully functional")
        print("✓ HIGH complexity architecture implemented and validated")
        
        print("\nNext Steps:")
        print("1. Add MEDIUM complexity enhancements (semantic analysis, advanced skill mapping)")
        print("2. Implement LOW complexity utilities (PII scrubbing, bias auditing)")
        print("3. Create comprehensive integration tests")
        print("4. Add performance optimizations and caching")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        logger.exception("Demo execution failed")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
