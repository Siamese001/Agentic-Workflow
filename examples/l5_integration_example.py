"""L5 High-Signal Unified Architecture - Integration Example

This example demonstrates the complete L5 architecture with both Resume and Outreach engines.
Shows silent execution, validation gates, adaptive recovery, and full artifact display.

Usage:
    python examples/l5_integration_example.py
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Any

from runtime.shared.integrity_gate_executor import create_integrity_gate_executor
from runtime.shared.adaptive_recovery_loop import create_adaptive_recovery_loop
from runtime.shared.execution_orchestrator import create_execution_orchestrator

from apps_rg.L2_execution.strategist_biowriter import create_strategist_biowriter, BioWriterConfig
from apps_rg.L2_execution.executive_title_composer import create_executive_title_composer, TitleComposerConfig

from apps_lic.L2_execution.route_classifier import create_route_classifier, RouteClassifierConfig
from apps_lic.L2_execution.message_body_composer import create_message_body_composer, MessageBodyConfig


def run_resume_generation_example():
    """
    Example: Resume Generation with L5 Architecture
    
    Demonstrates:
    - High temperature (0.6) for creative prose
    - Cryptographic validation gates
    - Adaptive recovery on failures
    - Silent execution mode
    """
    print("\n" + "="*80)
    print("RESUME GENERATION - L5 HIGH-SIGNAL ARCHITECTURE")
    print("="*80 + "\n")
    
    orchestrator = create_execution_orchestrator(
        output_dir=Path("./output/resume"),
        silent_mode=True
    )
    
    context = {
        'industry': 'FinTech',
        'seniority': 'Executive',
        'target_role': 'Chief Technology Officer'
    }
    
    run_sha = orchestrator.start_execution(context)
    orchestrator.record_decision("RESUME_GENERATION_STARTED", context)
    
    bullet_pool = [
        "Led digital transformation initiative resulting in 40% operational efficiency gain",
        "Architected cloud-native platform serving 2M+ daily active users",
        "Managed $15M technology budget with 98% on-time delivery rate",
        "Built and scaled engineering team from 12 to 85 members",
        "Implemented AI-driven fraud detection reducing losses by $3M annually"
    ]
    
    print("1. Generating Executive Summary (Strategist_BioWriter)...")
    bio_config = BioWriterConfig(temperature=0.6)
    biowriter = create_strategist_biowriter(config=bio_config)
    
    bio_result = biowriter.generate_summary(
        bullet_pool=bullet_pool,
        context=context
    )
    
    if bio_result.success:
        orchestrator.add_artifact(
            artifact_type="EXECUTIVE_SUMMARY",
            content=bio_result.summary,
            metadata={
                'word_count': bio_result.word_count,
                'attempts': bio_result.attempts,
                'temperature_adjustments': len(bio_result.temperature_log)
            }
        )
        print(f"   ✓ Generated in {bio_result.attempts} attempt(s)")
        print(f"   ✓ Word count: {bio_result.word_count}")
    else:
        print(f"   ✗ Failed after {bio_result.attempts} attempts")
        orchestrator.record_validation_failure(biowriter.gate_executor)
    
    orchestrator.record_temperature_adjustment(biowriter.recovery_loop)
    orchestrator.record_decision("BIO_GENERATION_COMPLETE", {'success': bio_result.success})
    
    print("\n2. Generating Headline (Executive_Title_Composer)...")
    title_config = TitleComposerConfig(temperature=0.5)
    title_composer = create_executive_title_composer(config=title_config)
    
    title_result = title_composer.generate_headline(context=context)
    
    if title_result.success:
        orchestrator.add_artifact(
            artifact_type="HEADLINE",
            content=title_result.headline,
            metadata={
                'segments': title_result.segments,
                'word_count': title_result.word_count,
                'char_count': title_result.char_count,
                'attempts': title_result.attempts
            }
        )
        print(f"   ✓ Generated in {title_result.attempts} attempt(s)")
        print(f"   ✓ Industry-first validated: {title_result.segments[0]}")
    else:
        print(f"   ✗ Failed after {title_result.attempts} attempts")
        orchestrator.record_validation_failure(title_composer.gate_executor)
    
    orchestrator.record_temperature_adjustment(title_composer.recovery_loop)
    orchestrator.record_decision("TITLE_GENERATION_COMPLETE", {'success': title_result.success})
    
    trace = orchestrator.complete_execution(
        success=bio_result.success and title_result.success
    )
    
    print(f"\n3. Execution Complete")
    print(f"   Run SHA: {trace.run_sha}")
    print(f"   Duration: {trace.end_time - trace.start_time:.2f}s")
    print(f"   Decisions: {len(trace.decision_path)}")
    print(f"   Temp Adjustments: {len(trace.temperature_log)}")
    print(f"   Validation Failures: {len(trace.validation_failures)}")
    
    print("\n" + orchestrator.display_all_artifacts())


def run_outreach_generation_example():
    """
    Example: LinkedIn Outreach with L5 Architecture
    
    Demonstrates:
    - Route classification with CXO precedence
    - Metric binding validation (LIC-QA-041)
    - Archetype-specific transitions
    - Premium gate enforcement
    """
    print("\n" + "="*80)
    print("OUTREACH GENERATION - L5 HIGH-SIGNAL ARCHITECTURE")
    print("="*80 + "\n")
    
    orchestrator = create_execution_orchestrator(
        output_dir=Path("./output/outreach"),
        silent_mode=True
    )
    
    profile = {
        'name': 'Jane Smith',
        'title': 'Chief Technology Officer',
        'company': 'Acme FinTech',
        'premium': True,
        'connection_degree': 3
    }
    
    run_sha = orchestrator.start_execution(profile)
    orchestrator.record_decision("OUTREACH_GENERATION_STARTED", profile)
    
    print("1. Classifying Route & Archetype (Route_Classifier)...")
    classifier = create_route_classifier()
    
    classification = classifier.classify(profile=profile)
    
    print(f"   ✓ Route: {classification.route.value}")
    print(f"   ✓ Archetype: {classification.archetype.value}")
    print(f"   ✓ Confidence: {classification.confidence:.2%}")
    
    orchestrator.add_artifact(
        artifact_type="CLASSIFICATION",
        content=f"Route: {classification.route.value}\nArchetype: {classification.archetype.value}",
        metadata={
            'route': classification.route.value,
            'archetype': classification.archetype.value,
            'confidence': classification.confidence
        }
    )
    
    orchestrator.record_decision("CLASSIFICATION_COMPLETE", {
        'route': classification.route.value,
        'archetype': classification.archetype.value
    })
    
    resume_evidence = {
        'EV001': "Led 30% revenue growth through strategic digital transformation initiatives",
        'EV002': "Managed $5M technology budget with 95% efficiency and on-time delivery",
        'EV003': "Built high-performing engineering team of 50+ across 3 continents"
    }
    
    print("\n2. Generating Message Body (Message_Body_Composer)...")
    composer = create_message_body_composer()
    
    message_context = {
        'company': profile['company'],
        'industry': 'FinTech',
        'role': 'CTO'
    }
    
    message_result = composer.generate_message_body(
        archetype=classification.archetype.value,
        resume_evidence=resume_evidence,
        context=message_context
    )
    
    if message_result.success:
        orchestrator.add_artifact(
            artifact_type="MESSAGE_BODY",
            content=message_result.body,
            metadata={
                'metrics_used': message_result.metrics_used,
                'evidence_bindings': message_result.evidence_bindings,
                'attempts': message_result.attempts
            }
        )
        print(f"   ✓ Generated in {message_result.attempts} attempt(s)")
        print(f"   ✓ Metrics bound: {len(message_result.evidence_bindings)}/{len(message_result.metrics_used)}")
    else:
        print(f"   ✗ Failed after {message_result.attempts} attempts")
        orchestrator.record_validation_failure(composer.gate_executor)
    
    orchestrator.record_temperature_adjustment(composer.recovery_loop)
    orchestrator.record_decision("MESSAGE_GENERATION_COMPLETE", {'success': message_result.success})
    
    trace = orchestrator.complete_execution(success=message_result.success)
    
    print(f"\n3. Execution Complete")
    print(f"   Run SHA: {trace.run_sha}")
    print(f"   Duration: {trace.end_time - trace.start_time:.2f}s")
    print(f"   Decisions: {len(trace.decision_path)}")
    print(f"   Temp Adjustments: {len(trace.temperature_log)}")
    print(f"   Validation Failures: {len(trace.validation_failures)}")
    
    print("\n" + orchestrator.display_all_artifacts())


def main():
    """Run both Resume and Outreach examples"""
    print("\n" + "█"*80)
    print("L5 HIGH-SIGNAL UNIFIED ARCHITECTURE - INTEGRATION EXAMPLES")
    print("█"*80)
    
    run_resume_generation_example()
    
    print("\n\n")
    
    run_outreach_generation_example()
    
    print("\n" + "█"*80)
    print("EXAMPLES COMPLETE")
    print("█"*80 + "\n")
    
    print("Key Features Demonstrated:")
    print("  ✓ High Temperature (0.5-0.6) for creative prose")
    print("  ✓ Cryptographic validation gates with signatures")
    print("  ✓ Adaptive recovery with temperature escalation")
    print("  ✓ Silent execution mode (no conversational filler)")
    print("  ✓ Full artifact display in output")
    print("  ✓ Complete audit trail in audit.json")
    print("\nAudit files saved to:")
    print("  - ./output/resume/audit_*.json")
    print("  - ./output/outreach/audit_*.json")


if __name__ == "__main__":
    main()
